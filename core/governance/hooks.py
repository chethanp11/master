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
from typing import Any, Dict, Optional

from core.config.schema import Settings
from core.contracts.flow_schema import AutonomyLevel
from core.governance.policies import PolicyDecision, PolicyEngine
from core.governance.security import SecurityRedactor
from core.orchestrator.context import RunContext, StepContext


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
        return self._decision(
            allowed=True,
            reason="ok",
            details={"step_id": self._step_id(step_ctx), "step_type": step_ctx.step.type.value},
            scrubbed={"step": self.redactor.sanitize(step_ctx.step.model_dump())},
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
        return self._decision(decision.allow, decision.reason, decision.details, scrubbed)

    def before_model_call(
        self,
        *,
        model_name: str,
        purpose: Optional[str],
        messages: Dict[str, Any],
        max_tokens: Optional[int],
        ctx: StepContext,
    ) -> HookDecision:
        decision = self.engine.evaluate_model_use(model_name=model_name, step_ctx=ctx)
        limit = self.settings.policies.model_max_tokens
        if limit is not None and max_tokens is not None and max_tokens > limit:
            decision = PolicyDecision(
                allow=False,
                reason="model_token_limit_exceeded",
                details={"model": model_name, "requested": max_tokens, "limit": limit},
            )
        scrubbed = {
            "model": model_name,
            "purpose": purpose or "",
            "messages": self.redactor.sanitize(messages),
            "max_tokens": max_tokens,
            "run_id": self._run_id(ctx.run),
            "product": self._product(ctx.run),
        }
        return self._decision(decision.allow, decision.reason, decision.details, scrubbed)

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

    @classmethod
    def noop(cls) -> "GovernanceHooks":
        """
        Helper used by orchestrator tests – returns a hooks instance with default Settings.
        """
        return cls(settings=Settings())
