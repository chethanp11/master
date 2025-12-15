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


def _norm(value: str) -> str:
    return value.strip().lower()


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
        product = self._product_from_ctx(step_ctx)
        pol = self._policy_for_product(product)
        norm_tool = _norm(tool_name)
        if not pol.get("enforce", True):
            return PolicyDecision(True, "policies_disabled", {"tool": tool_name, "product": product})

        allowed = [_norm(t) for t in (pol.get("allowed_tools") or [])]
        blocked = {_norm(t) for t in (pol.get("blocked_tools") or [])}

        if norm_tool in blocked:
            return PolicyDecision(False, "tool_blocked", {"tool": tool_name, "product": product})

        if allowed and norm_tool not in allowed:
            return PolicyDecision(False, "tool_not_in_allowlist", {"tool": tool_name, "product": product})

        return PolicyDecision(True, "ok", {"tool": tool_name, "product": product})

    # ------------------------------
    # Models
    # ------------------------------

    def evaluate_model_use(self, *, model_name: str, step_ctx: StepContext) -> PolicyDecision:
        product = self._product_from_ctx(step_ctx)
        return self.evaluate_model_selection(product=product, model_name=model_name)

    def evaluate_model_selection(self, *, product: str, model_name: str) -> PolicyDecision:
        pol = self._policy_for_product(product)
        norm_model = _norm(model_name)
        if not pol.get("enforce", True):
            return PolicyDecision(True, "policies_disabled", {"model": model_name, "product": product})

        allowed = [_norm(m) for m in (pol.get("allowed_models") or [])]
        blocked = {_norm(m) for m in (pol.get("blocked_models") or [])}

        if norm_model in blocked:
            return PolicyDecision(False, "model_blocked", {"model": model_name, "product": product})

        if allowed and norm_model not in allowed:
            return PolicyDecision(False, "model_not_in_allowlist", {"model": model_name, "product": product})

        return PolicyDecision(True, "ok", {"model": model_name, "product": product})

    @staticmethod
    def _product_from_ctx(step_ctx: StepContext) -> str:
        run = getattr(step_ctx, "run", None)
        run_record = getattr(run, "run_record", None)
        return getattr(run_record, "product", getattr(step_ctx, "product", "unknown_product"))
