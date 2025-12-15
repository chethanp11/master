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
class HookResult:
    allow: bool
    reason: str
    details: Dict[str, Any]
    scrubbed: Dict[str, Any]


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

    def before_step(self, *, step_ctx: StepContext) -> HookResult:
        # v1: no step-level enforcement beyond basic context redaction
        return HookResult(
            allow=True,
            reason="ok",
            details={"step_id": step_ctx.step_id, "step_type": step_ctx.step.type.value},
            scrubbed={"step": self.redactor.redact_dict(step_ctx.step.model_dump())},
        )

    def before_complete(self, *, run_ctx: RunContext, output: Dict[str, Any]) -> HookResult:
        return HookResult(
            allow=True,
            reason="ok",
            details={"run_id": run_ctx.run_id},
            scrubbed={"output": self.redactor.redact_dict(output)},
        )

    def check_autonomy(self, *, run_ctx: RunContext, autonomy: AutonomyLevel) -> HookResult:
        d: PolicyDecision = self.engine.evaluate_autonomy(autonomy=autonomy, run_ctx=run_ctx)
        return HookResult(
            allow=d.allow,
            reason=d.reason,
            details=d.details,
            scrubbed={"autonomy": autonomy.value},
        )

    # ------------------------------
    # Tool hooks (used by ToolExecutor)
    # ------------------------------

    def before_tool_call(self, *, tool_name: str, params: Dict[str, Any], ctx: StepContext) -> HookResult:
        d: PolicyDecision = self.engine.evaluate_tool_call(tool_name=tool_name, step_ctx=ctx)
        scrubbed = {"tool": tool_name, "params": self.redactor.redact_dict(params)}
        if not d.allow:
            return HookResult(False, d.reason, d.details, scrubbed)
        return HookResult(True, "ok", d.details, scrubbed)

    # Convenience for ToolExecutor: raise on deny (keeps executor code small)
    def before_tool_call_raise(self, *, tool_name: str, params: Dict[str, Any], ctx: StepContext) -> None:
        res = self.before_tool_call(tool_name=tool_name, params=params, ctx=ctx)
        if not res.allow:
            raise PermissionError(f"{res.reason}: {res.details}")