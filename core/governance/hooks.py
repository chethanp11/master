# ==============================
# Governance Hooks
# ==============================
"""
Hook layer used by orchestrator/tools to enforce policies and emit structured decisions.

Hooks are intentionally thin:
- Evaluate allow/deny via PolicyEngine
- Redact payloads via SecurityRedactor
- Return a stable decision object for tracing

No persistence here. No logging here. Callers emit trace events.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Dict, Optional

from core.config.schema import Settings
from core.contracts.agent_schema import find_control_fields, validate_agent_output_payload
from core.contracts.reasoning_schema import ReasoningPurpose
from core.contracts.flow_schema import AutonomyLevel
from core.governance.policies import PolicyDecision, PolicyEngine
from core.governance.security import SecurityRedactor
from core.orchestrator.context import RunContext, StepContext

_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "dump system prompt",
    "reveal configuration",
)


@dataclass(frozen=True)
class HookDecision:
    allowed: bool
    reason: str
    details: Dict[str, Any]
    scrubbed: Dict[str, Any]

    def to_payload(self) -> Dict[str, Any]:
        payload = {"allowed": self.allowed, "reason": self.reason}
        payload.update(self.scrubbed)
        return payload


class GovernanceHooks:
    def __init__(
        self,
        *,
        settings: Settings,
        redactor: Optional[SecurityRedactor] = None,
    ) -> None:
        self.settings = settings
        self.engine = PolicyEngine(settings)
        patterns = settings.logging.redact_patterns if settings.logging.redact_patterns else None
        self.redactor = redactor or SecurityRedactor(patterns=patterns)

    # ------------------------------
    # Orchestrator hooks
    # ------------------------------

    def before_step(self, *, step_ctx: StepContext) -> HookDecision:
        step_payload = step_ctx.step.model_dump() if step_ctx.step is not None else {"id": self._step_id(step_ctx), "type": step_ctx.type}
        limit = self.settings.policies.max_steps
        if limit is not None:
            count = int(step_ctx.run.meta.get("steps_executed", 0))
            if count >= limit:
                return self._decision(
                    allowed=False,
                    reason="step_limit_exceeded",
                    details={"step_id": self._step_id(step_ctx), "requested": count + 1, "limit": limit},
                    scrubbed={"step": self.redactor.sanitize(step_payload)},
                )
        return self._decision(
            allowed=True,
            reason="ok",
            details={
                "step_id": self._step_id(step_ctx),
                "step_type": step_ctx.step.type.value if step_ctx.step is not None else step_ctx.type,
            },
            scrubbed={"step": self.redactor.sanitize(step_payload)},
        )

    def before_complete(self, *, run_ctx: RunContext, output: Dict[str, Any]) -> HookDecision:
        return self._decision(
            allowed=True,
            reason="ok",
            details={"run_id": self._run_id(run_ctx)},
            scrubbed={"output": self.redactor.sanitize(output)},
        )

    def check_autonomy(self, *, run_ctx: RunContext, autonomy: AutonomyLevel) -> HookDecision:
        decision = self.engine.evaluate_autonomy(autonomy=autonomy, run_ctx=run_ctx)
        return self._decision(
            allowed=decision.allow,
            reason=decision.reason,
            details=decision.details,
            scrubbed={"autonomy": autonomy.value},
        )

    # ------------------------------
    # Tool hooks (used by the executor layer)
    # ------------------------------

    def before_tool_call(self, *, tool_name: str, params: Dict[str, Any], ctx: StepContext) -> HookDecision:
        decision = self.engine.evaluate_tool_call(tool_name=tool_name, step_ctx=ctx)
        scrubbed = {
            "tool": tool_name,
            "params": self.redactor.sanitize(params),
            "run_id": self._run_id(ctx.run),
            "product": self._product(ctx.run),
        }
        limit = self.settings.policies.max_tool_calls
        if limit is not None:
            count = int(ctx.run.meta.get("tool_calls", 0))
            if count >= limit:
                decision = PolicyDecision(
                    allow=False,
                    reason="tool_call_limit_exceeded",
                    details={"tool": tool_name, "requested": count + 1, "limit": limit},
                )
            else:
                ctx.run.meta["tool_calls"] = count + 1
        return self._decision(decision.allow, decision.reason, decision.details, scrubbed)

    def before_model_call(
        self,
        *,
        model_name: str,
        purpose: ReasoningPurpose,
        messages: Dict[str, Any],
        max_tokens: Optional[int],
        ctx: StepContext,
    ) -> HookDecision:
        flattened = str(messages).lower()
        if any(pat in flattened for pat in _INJECTION_PATTERNS):
            return self._decision(
                allowed=False,
                reason="prompt_injection_detected",
                details={"patterns": [p for p in _INJECTION_PATTERNS if p in flattened]},
                scrubbed={
                    "model": model_name,
                    "purpose": purpose.value,
                    "run_id": self._run_id(ctx.run),
                    "product": self._product(ctx.run),
                },
            )
        decision = self.engine.evaluate_model_use(model_name=model_name, step_ctx=ctx)
        limit = self.settings.policies.model_max_tokens
        if limit is not None and max_tokens is not None and max_tokens > limit:
            decision = PolicyDecision(
                allow=False,
                reason="model_token_limit_exceeded",
                details={"model": model_name, "requested": max_tokens, "limit": limit},
            )
        run_limit = self.settings.policies.max_tokens_per_run
        if run_limit is not None:
            used = int(ctx.run.meta.get("tokens_used", 0))
            requested = int(max_tokens or 0)
            if used >= run_limit or (requested and used + requested > run_limit):
                decision = PolicyDecision(
                    allow=False,
                    reason="run_token_budget_exceeded",
                    details={"model": model_name, "used": used, "requested": requested, "limit": run_limit},
                )
        scrubbed = {
            "model": model_name,
            "purpose": purpose.value,
            "messages": self.redactor.sanitize(messages),
            "max_tokens": max_tokens,
            "tokens_used": int(ctx.run.meta.get("tokens_used", 0)),
            "run_id": self._run_id(ctx.run),
            "product": self._product(ctx.run),
        }
        return self._decision(decision.allow, decision.reason, decision.details, scrubbed)

    def before_user_input_response(
        self,
        *,
        request: Any,
        response: Any,
        ctx: StepContext,
    ) -> HookDecision:
        limit = self.settings.policies.max_payload_bytes
        payload = {"request": request, "response": response}
        if limit is not None and self._payload_size_bytes(response) > limit:
            return self._decision(
                allowed=False,
                reason="user_input_payload_limit_exceeded",
                details={"limit_bytes": limit},
                scrubbed={"payload": self.redactor.sanitize(payload), "run_id": self._run_id(ctx.run)},
            )
        return self._decision(
            allowed=True,
            reason="ok",
            details={"run_id": self._run_id(ctx.run)},
            scrubbed={"payload": self.redactor.sanitize(payload)},
        )

    def before_run_output(self, *, output: Dict[str, Any], run_ctx: RunContext) -> HookDecision:
        limit = self.settings.policies.max_payload_bytes
        if limit is not None and self._payload_size_bytes(output) > limit:
            return self._decision(
                allowed=False,
                reason="output_payload_limit_exceeded",
                details={"limit_bytes": limit},
                scrubbed={"output": self.redactor.sanitize(output), "run_id": self._run_id(run_ctx)},
            )
        return self._decision(
            allowed=True,
            reason="ok",
            details={"run_id": self._run_id(run_ctx)},
            scrubbed={"output": self.redactor.sanitize(output)},
        )

    def before_output_files(self, *, files: Any, run_ctx: RunContext) -> HookDecision:
        limit = self.settings.policies.max_payload_bytes
        if limit is not None and self._payload_size_bytes(files) > limit:
            return self._decision(
                allowed=False,
                reason="output_files_limit_exceeded",
                details={"limit_bytes": limit},
                scrubbed={"files": self.redactor.sanitize(files), "run_id": self._run_id(run_ctx)},
            )
        return self._decision(
            allowed=True,
            reason="ok",
            details={"run_id": self._run_id(run_ctx)},
            scrubbed={"files": self.redactor.sanitize(files)},
        )

    def validate_agent_output(self, *, agent_name: str, output: Dict[str, Any], ctx: StepContext) -> HookDecision:
        violations = find_control_fields(output)
        allowed = True
        reason = "ok"
        details: Dict[str, Any] = {"agent": agent_name}
        if violations:
            allowed = False
            reason = "agent_output_control_fields"
            details["violations"] = violations
        try:
            validate_agent_output_payload(output)
        except Exception as exc:
            allowed = False
            if reason == "ok":
                reason = "agent_output_invalid"
            details["error"] = str(exc)
        scrubbed = {
            "agent": agent_name,
            "output": self.redactor.sanitize(output),
            "violations": violations,
            "run_id": self._run_id(ctx.run),
            "product": self._product(ctx.run),
        }
        return self._decision(allowed, reason, details, scrubbed)

    def _decision(self, allowed: bool, reason: str, details: Dict[str, Any], scrubbed: Dict[str, Any]) -> HookDecision:
        return HookDecision(allowed=allowed, reason=reason, details=details, scrubbed=scrubbed)

    @staticmethod
    def _step_id(step_ctx: StepContext) -> str:
        return getattr(step_ctx.step, "id", "unknown_step")

    @staticmethod
    def _run_id(run_ctx: RunContext) -> str:
        record = getattr(run_ctx, "run_record", None)
        return getattr(record, "run_id", "unknown_run")

    @staticmethod
    def _product(run_ctx: RunContext) -> str:
        record = getattr(run_ctx, "run_record", None)
        return getattr(record, "product", "unknown_product")

    @staticmethod
    def _payload_size_bytes(payload: Any) -> int:
        try:
            raw = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
        except Exception:
            raw = str(payload)
        return len(raw.encode("utf-8"))

    @classmethod
    def noop(cls) -> "GovernanceHooks":
        """
        Helper used by orchestrator tests – returns a hooks instance with default Settings.
        """
        return cls(settings=Settings())
