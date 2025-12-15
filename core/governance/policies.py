# ==============================
# Governance Policies
# ==============================
"""
Policy evaluation for tools, models, and autonomy.

Design:
- Simple allow/deny evaluation with per-product overrides.
- Uses Settings + context (RunContext/StepContext) for decisions.
- v1 focus: tool + model allow/deny and autonomy gating.

No persistence. No vendor calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.config.schema import Settings
from core.contracts.flow_schema import AutonomyLevel
from core.orchestrator.context import RunContext, StepContext


@dataclass(frozen=True)
class PolicyDecision:
    allow: bool
    reason: str
    details: Dict[str, Any]


def _merge_policy_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if isinstance(out.get(k), dict) and isinstance(v, dict):
            out[k] = _merge_policy_dict(out[k], v)  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


class PolicyEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _policy_for_product(self, product: str) -> Dict[str, Any]:
        base = self.settings.policies.model_dump()
        overrides = self.settings.policies.by_product.get(product, {}) if self.settings.policies.by_product else {}
        return _merge_policy_dict(base, overrides)

    # ------------------------------
    # Autonomy
    # ------------------------------

    def evaluate_autonomy(self, *, autonomy: AutonomyLevel, run_ctx: RunContext) -> PolicyDecision:
        pol = self._policy_for_product(run_ctx.product)
        if not pol.get("enforce", True):
            return PolicyDecision(True, "policies_disabled", {"autonomy": autonomy.value})

        if autonomy == AutonomyLevel.FULL_AUTO and not pol.get("allow_full_autonomy", False):
            return PolicyDecision(False, "full_autonomy_disabled", {"autonomy": autonomy.value})

        return PolicyDecision(True, "ok", {"autonomy": autonomy.value})

    # ------------------------------
    # Tools
    # ------------------------------

    def evaluate_tool_call(self, *, tool_name: str, step_ctx: StepContext) -> PolicyDecision:
        pol = self._policy_for_product(step_ctx.product)
        if not pol.get("enforce", True):
            return PolicyDecision(True, "policies_disabled", {"tool": tool_name})

        allowed = pol.get("allowed_tools") or []
        blocked = pol.get("blocked_tools") or []

        if tool_name in blocked:
            return PolicyDecision(False, "tool_blocked", {"tool": tool_name})

        # If allowed list is non-empty, tool must be in allowed
        if allowed and tool_name not in allowed:
            return PolicyDecision(False, "tool_not_in_allowlist", {"tool": tool_name})

        return PolicyDecision(True, "ok", {"tool": tool_name})

    # ------------------------------
    # Models
    # ------------------------------

    def evaluate_model_use(self, *, model_name: str, step_ctx: StepContext) -> PolicyDecision:
        pol = self._policy_for_product(step_ctx.product)
        if not pol.get("enforce", True):
            return PolicyDecision(True, "policies_disabled", {"model": model_name})

        allowed = pol.get("allowed_models") or []
        blocked = pol.get("blocked_models") or []

        if model_name in blocked:
            return PolicyDecision(False, "model_blocked", {"model": model_name})

        if allowed and model_name not in allowed:
            return PolicyDecision(False, "model_not_in_allowlist", {"model": model_name})

        return PolicyDecision(True, "ok", {"model": model_name})