# ==============================
# Governance Policies
# ==============================
"""
Policy evaluation for tools, models, and autonomy.

Design:
- Simple allow/deny evaluation with per-product overrides.
- Uses Settings + context (RunContext/StepContext) for decisions.
- v1 focus: tool + model allow/deny and autonomy gating.
- IMP-047: No bypass functionality - policies always enforced.

No persistence. No vendor calls.
"""

from __future__ import annotations



from dataclasses import dataclass
from typing import Any, Callable, Dict, Final, Optional

from core.config.schema import Settings
from core.contracts.flow_schema import AutonomyLevel
from core.orchestrator.context import RunContext, StepContext


# ============================================================================
# Policy Enforcement Error Codes (IMP-047: GOV-POL-BLOCK-001...005)
# ============================================================================

# Error code for immediate policy violations
POLICY_VIOLATION_IMMEDIATE: Final[str] = "policy_violation_immediate"

# Error code for bypass attempt detection
POLICY_BYPASS_ATTEMPTED: Final[str] = "policy_bypass_attempted"


@dataclass(frozen=True)
class PolicyDecision:
    allow: bool
    reason: str
    details: Dict[str, Any]
    
    # IMP-047: Track if this was a bypass attempt
    bypass_attempted: bool = False


# ============================================================================
# Policy Bypass Detection (IMP-047: GOV-POL-NOBYPASS-001...005)
# ============================================================================

class PolicyBypassAttemptError(Exception):
    """
    Exception raised when a policy bypass is attempted.
    
    GOV-POL-NOBYPASS-001: No bypass configuration allowed.
    """
    
    def __init__(self, message: str, context: Dict[str, Any] | None = None):
        super().__init__(message)
        self.context = context or {}


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
    """
    Policy engine for evaluating governance policies.
    
    IMP-047: GOV-POL-NOBYPASS-001...005 - No bypass functionality.
    IMP-047: GOV-POL-BLOCK-001...005 - Block immediately on violations.
    
    Attributes:
        settings: Application settings
        emit_event_fn: Optional callback to emit trace events
        
    Note:
        The 'enforce' configuration option is deprecated and ignored.
        Policies are always enforced - there is no bypass mechanism.
    """
    
    def __init__(
        self, 
        settings: Settings,
        *,
        emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        self.settings = settings
        self._emit_event = emit_event_fn
        self._bypass_attempt_count = 0

    def _policy_for_product(self, product: str) -> Dict[str, Any]:
        base = self.settings.policies.model_dump()
        overrides = self.settings.policies.by_product.get(product, {}) if self.settings.policies.by_product else {}
        merged = _merge_policy_dict(base, overrides)
        
        # IMP-047: Detect and block any bypass configuration
        if not merged.get("enforce", True):
            self._handle_bypass_attempt(product, "enforce=false detected")
            # Force enforcement - remove bypass option
            merged["enforce"] = True
        
        return merged
    
    def _handle_bypass_attempt(self, product: str, reason: str) -> None:
        """
        Handle a detected policy bypass attempt.
        
        GOV-POL-NOBYPASS-001: Log and block bypass attempts.
        """
        self._bypass_attempt_count += 1
        context = {
            "product": product,
            "reason": reason,
            "attempt_count": self._bypass_attempt_count,
        }
        
        if self._emit_event:
            self._emit_event("policy_bypass_blocked", context)
    
    def _handle_violation(
        self, 
        reason: str, 
        details: Dict[str, Any],
    ) -> PolicyDecision:
        """
        Handle a policy violation - block immediately.
        
        GOV-POL-BLOCK-001...005: Block immediately on violations.
        """
        if self._emit_event:
            self._emit_event("policy_violation_blocked", {
                "reason": reason,
                "details": details,
            })
        
        return PolicyDecision(
            allow=False,
            reason=reason,
            details={**details, "error_code": POLICY_VIOLATION_IMMEDIATE},
        )

    # ------------------------------
    # Bypass Attempt Counter
    # ------------------------------
    
    @property
    def bypass_attempt_count(self) -> int:
        """Number of bypass attempts detected."""
        return self._bypass_attempt_count

    # ------------------------------
    # Autonomy
    # ------------------------------

    def evaluate_autonomy(self, *, autonomy: AutonomyLevel, run_ctx: RunContext) -> PolicyDecision:
        pol = self._policy_for_product(run_ctx.product)
        # IMP-047: Removed enforce=false check - policies always enforced

        if autonomy == AutonomyLevel.FULL_AUTO and not pol.get("allow_full_autonomy", False):
            return self._handle_violation(
                "full_autonomy_disabled", 
                {"autonomy": autonomy.value},
            )

        return PolicyDecision(True, "ok", {"autonomy": autonomy.value})

    # ------------------------------
    # Tools
    # ------------------------------

    def evaluate_tool_call(self, *, tool_name: str, step_ctx: StepContext) -> PolicyDecision:
        product = self._product_from_ctx(step_ctx)
        pol = self._policy_for_product(product)
        norm_tool = _norm(tool_name)
        # IMP-047: Removed enforce=false check - policies always enforced

        allowed = [_norm(t) for t in (pol.get("allowed_tools") or [])]
        blocked = {_norm(t) for t in (pol.get("blocked_tools") or [])}

        if norm_tool in blocked:
            return self._handle_violation(
                "tool_blocked", 
                {"tool": tool_name, "product": product},
            )

        if allowed and norm_tool not in allowed:
            return self._handle_violation(
                "tool_not_in_allowlist", 
                {"tool": tool_name, "product": product},
            )

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
        # IMP-047: Removed enforce=false check - policies always enforced

        allowed = [_norm(m) for m in (pol.get("allowed_models") or [])]
        blocked = {_norm(m) for m in (pol.get("blocked_models") or [])}

        if norm_model in blocked:
            return self._handle_violation(
                "model_blocked", 
                {"model": model_name, "product": product},
            )

        if allowed and norm_model not in allowed:
            return self._handle_violation(
                "model_not_in_allowlist", 
                {"model": model_name, "product": product},
            )

        return PolicyDecision(True, "ok", {"model": model_name, "product": product})

    @staticmethod
    def _product_from_ctx(step_ctx: StepContext) -> str:
        run = getattr(step_ctx, "run", None)
        run_record = getattr(run, "run_record", None)
        return getattr(run_record, "product", getattr(step_ctx, "product", "unknown_product"))
