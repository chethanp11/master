from __future__ import annotations

# ==============================
# Budget Resolver + Consumption
# ==============================
"""
Budget management for governance.

IMP-048: GOV-BUD-HARD-001...005 - Hard budget limits.
- No overdraft allowed
- Pre-check before consumption
- Trace events on limit reached and rejection
"""

from typing import Any, Callable, Dict, Final, Optional, Tuple

from core.contracts.budget_schema import Budget, BudgetPolicy, BudgetState, LatencyBucket, ReasoningBudget

_LATENCY_ORDER = {"LOW": 0, "MED": 1, "HIGH": 2}

# Type alias for trace emitter callbacks
TraceEmitter = Callable[[str, Dict[str, Any]], None]

# INT-DISC-030: Default estimated costs per tool (can be overridden)
_TOOL_COST_ESTIMATES: Dict[str, int] = {}


# ============================================================================
# Error Codes (IMP-048: GOV-BUD-HARD-001...005)
# ============================================================================

# Error code for hard budget limit exceeded
BUDGET_HARD_LIMIT_EXCEEDED: Final[str] = "budget_hard_limit_exceeded"

# Error code for budget operation rejected (pre-check failed)
BUDGET_OPERATION_REJECTED: Final[str] = "budget_operation_rejected"


def register_tool_cost(tool_name: str, cost_units: int) -> None:
    """
    INT-DISC-031: Register estimated cost for a tool.
    
    Args:
        tool_name: Tool name
        cost_units: Estimated cost in units
    """
    _TOOL_COST_ESTIMATES[tool_name.lower()] = cost_units


def estimated_cost_by_tool(tool_name: str) -> int:
    """
    INT-DISC-032: Get estimated cost for a tool.
    
    Args:
        tool_name: Tool name
        
    Returns:
        Estimated cost in units (default: 1)
    """
    return _TOOL_COST_ESTIMATES.get(tool_name.lower(), 1)


def can_afford_tool(
    tool_name: str,
    budget: Budget,
    state: BudgetState,
) -> bool:
    """
    INT-DISC-033: Check if budget can afford a tool call.
    
    Args:
        tool_name: Tool name to check
        budget: Budget limits
        state: Current budget state
        
    Returns:
        True if tool can be afforded
    """
    # Check tool call count
    if state.tool_calls_used >= budget.max_tool_calls:
        return False
    
    # Check cost units
    estimated_cost = estimated_cost_by_tool(tool_name)
    if state.cost_units_used + estimated_cost > budget.max_total_cost_units:
        return False
    
    return True


# ============================================================================
# Hard Budget Pre-Checks (IMP-048: GOV-BUD-HARD-001...005)
# ============================================================================

class BudgetPreCheckResult:
    """
    Result of budget pre-check operation.
    
    GOV-BUD-HARD-002: Pre-check before consumption.
    
    Attributes:
        can_proceed: True if operation can proceed
        reason: Human-readable explanation
        requested_amount: Amount requested
        remaining_budget: Remaining budget for this kind
        limit: The limit for this kind
        error_code: Error code if rejected
    """
    
    def __init__(
        self,
        *,
        can_proceed: bool,
        reason: str,
        requested_amount: int,
        remaining_budget: int,
        limit: int,
        error_code: Optional[str] = None,
    ):
        self.can_proceed = can_proceed
        self.reason = reason
        self.requested_amount = requested_amount
        self.remaining_budget = remaining_budget
        self.limit = limit
        self.error_code = error_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for trace events."""
        return {
            "can_proceed": self.can_proceed,
            "reason": self.reason,
            "requested_amount": self.requested_amount,
            "remaining_budget": self.remaining_budget,
            "limit": self.limit,
            "error_code": self.error_code,
        }


def can_consume_budget(
    *,
    budget: Budget,
    state: BudgetState,
    kind: str,
    amount: int = 1,
    cost_units: int = 0,
    emit_event_fn: Optional[TraceEmitter] = None,
) -> BudgetPreCheckResult:
    """
    Pre-check if budget consumption would succeed.
    
    GOV-BUD-HARD-002: Pre-check before consumption.
    GOV-BUD-HARD-003: Reject if would exceed (not post-hoc).
    
    Args:
        budget: Budget limits
        state: Current budget state
        kind: Type of consumption (pass, tool, parallel)
        amount: Amount to consume
        cost_units: Cost units for the operation
        emit_event_fn: Optional trace event emitter
        
    Returns:
        BudgetPreCheckResult with can_proceed flag and details
    """
    # Determine current usage and limits based on kind
    if kind == "pass":
        current = state.passes_used
        limit = budget.max_passes
        new_value = current + amount
    elif kind == "tool":
        current = state.tool_calls_used
        limit = budget.max_tool_calls
        new_value = current + amount
    elif kind == "parallel":
        current = state.parallel_calls_used
        limit = budget.max_parallel_calls
        new_value = current + amount
    else:
        # Unknown kind - reject with high limit to avoid issues
        return BudgetPreCheckResult(
            can_proceed=False,
            reason=f"Unknown budget kind: {kind}",
            requested_amount=amount,
            remaining_budget=0,
            limit=0,
            error_code=BUDGET_OPERATION_REJECTED,
        )
    
    remaining = limit - current
    
    # Check if at limit already
    if current >= limit:
        if emit_event_fn:
            emit_event_fn("budget_limit_reached", {
                "kind": kind,
                "current": current,
                "limit": limit,
                "requested_amount": amount,
            })
        return BudgetPreCheckResult(
            can_proceed=False,
            reason=f"Budget limit reached for {kind}: {current}/{limit}",
            requested_amount=amount,
            remaining_budget=0,
            limit=limit,
            error_code=BUDGET_HARD_LIMIT_EXCEEDED,
        )
    
    # Check if operation would exceed limit
    if new_value > limit:
        if emit_event_fn:
            emit_event_fn("budget_operation_rejected", {
                "kind": kind,
                "current": current,
                "limit": limit,
                "requested_amount": amount,
                "remaining_budget": remaining,
                "would_exceed_by": new_value - limit,
            })
        return BudgetPreCheckResult(
            can_proceed=False,
            reason=f"Operation would exceed {kind} limit: {new_value} > {limit}",
            requested_amount=amount,
            remaining_budget=remaining,
            limit=limit,
            error_code=BUDGET_OPERATION_REJECTED,
        )
    
    # Check cost units separately
    cost_remaining = budget.max_total_cost_units - state.cost_units_used
    if state.cost_units_used + cost_units > budget.max_total_cost_units:
        if emit_event_fn:
            emit_event_fn("budget_operation_rejected", {
                "kind": "cost_units",
                "current": state.cost_units_used,
                "limit": budget.max_total_cost_units,
                "requested_amount": cost_units,
                "remaining_budget": cost_remaining,
            })
        return BudgetPreCheckResult(
            can_proceed=False,
            reason=f"Cost units would exceed limit: {state.cost_units_used + cost_units} > {budget.max_total_cost_units}",
            requested_amount=cost_units,
            remaining_budget=cost_remaining,
            limit=budget.max_total_cost_units,
            error_code=BUDGET_OPERATION_REJECTED,
        )
    
    # All checks passed
    return BudgetPreCheckResult(
        can_proceed=True,
        reason="OK",
        requested_amount=amount,
        remaining_budget=remaining,
        limit=limit,
    )


def resolve_budget(
    policy: BudgetPolicy,
    *,
    sensitivity_class: str,
    flow_type: str,
) -> Budget:
    if flow_type in policy.overrides_by_flow_type:
        return policy.overrides_by_flow_type[flow_type]
    if sensitivity_class in policy.overrides_by_sensitivity:
        return policy.overrides_by_sensitivity[sensitivity_class]
    return policy.defaults


def init_budget_state() -> BudgetState:
    return BudgetState()


def init_reasoning_budget(
    reasoning_budget: Optional[ReasoningBudget] = None,
) -> Tuple[Budget, BudgetState]:
    """Initialize budget and state for bounded reasoning operations.
    
    Args:
        reasoning_budget: Optional ReasoningBudget config. If None, uses defaults.
        
    Returns:
        Tuple of (Budget, BudgetState) ready for reasoning passes.
    """
    if reasoning_budget is None:
        reasoning_budget = ReasoningBudget()
    return reasoning_budget.to_budget(), init_budget_state()


def consume_budget(
    *,
    budget: Budget,
    state: BudgetState,
    kind: str,
    amount: int = 1,
    cost_units: int = 0,
    latency_bucket: Optional[LatencyBucket] = None,
    allow_overdraft: bool = False,  # GOV-BUD-HARD-001: Always False - documented for clarity
    emit_event_fn: Optional[TraceEmitter] = None,
) -> Tuple[bool, str, BudgetState]:
    """
    Consume budget for an operation.
    
    GOV-BUD-HARD-001: No overdraft allowed (allow_overdraft is always ignored).
    GOV-BUD-HARD-003: Pre-check before consumption.
    
    Args:
        budget: Budget limits
        state: Current budget state
        kind: Type of consumption (pass, tool, parallel)
        amount: Amount to consume
        cost_units: Cost units for the operation
        latency_bucket: Optional latency bucket
        allow_overdraft: Ignored - always False per GOV-BUD-HARD-001
        emit_event_fn: Optional trace event emitter
        
    Returns:
        Tuple of (allowed, action, updated_state)
    """
    # GOV-BUD-HARD-001: Ignore allow_overdraft parameter - always enforce hard limits
    _ = allow_overdraft
    
    # GOV-BUD-HARD-003: Pre-check before consumption
    pre_check = can_consume_budget(
        budget=budget,
        state=state,
        kind=kind,
        amount=amount,
        cost_units=cost_units,
        emit_event_fn=emit_event_fn,
    )
    
    if not pre_check.can_proceed:
        # Return current state unchanged - no consumption occurred
        return False, pre_check.error_code or "REJECTED", state
    
    # Safe to proceed - update state
    updated = state.model_copy()
    violations = list(updated.violations)

    if latency_bucket:
        if _LATENCY_ORDER[latency_bucket] > _LATENCY_ORDER[updated.latency_bucket_observed]:
            updated.latency_bucket_observed = latency_bucket
        if _LATENCY_ORDER[updated.latency_bucket_observed] > _LATENCY_ORDER[budget.max_latency_bucket]:
            violations.append("latency_bucket_exceeded")

    if kind == "pass":
        updated.passes_used += amount
    elif kind == "tool":
        updated.tool_calls_used += amount
    elif kind == "parallel":
        updated.parallel_calls_used += amount

    updated.cost_units_used += cost_units
    updated.violations = violations

    # Post-consumption check for latency (can still trigger violations)
    if violations:
        if budget.on_exceed == "DEGRADE":
            if not budget.degrade_to:
                return False, "DEGRADE", updated
            degraded = _apply_degrade(budget, budget.degrade_to)
            if degraded.model_dump() == budget.model_dump():
                return False, "DEGRADE", updated
            return _recheck(degraded, updated, kind, amount, cost_units, latency_bucket, emit_event_fn)
        return False, budget.on_exceed, updated
    return True, "OK", updated


def _apply_degrade(budget: Budget, degrade_to: Optional[Dict[str, int]]) -> Budget:
    if not degrade_to:
        return budget
    data = budget.model_dump()
    for key in ("max_passes", "max_tool_calls", "max_parallel_calls", "max_total_cost_units"):
        if key in degrade_to:
            data[key] = min(int(data.get(key, 0)), int(degrade_to[key]))
    return Budget.model_validate(data)


def _recheck(
    budget: Budget,
    state: BudgetState,
    kind: str,
    amount: int,
    cost_units: int,
    latency_bucket: Optional[LatencyBucket],
    emit_event_fn: Optional[TraceEmitter] = None,
) -> Tuple[bool, str, BudgetState]:
    state = state.model_copy(update={"violations": []})
    return consume_budget(
        budget=budget,
        state=state,
        kind=kind,
        amount=amount,
        cost_units=cost_units,
        latency_bucket=latency_bucket,
        emit_event_fn=emit_event_fn,
    )


def should_escalate_to_hitl(action: str) -> bool:
    """Check if the budget exceed action requires HITL escalation.
    
    Args:
        action: The action string returned from consume_budget.
        
    Returns:
        True if HITL escalation is needed.
    """
    return action == "HITL"


def emit_budget_exceeded_event(
    trace: Optional[TraceEmitter],
    *,
    kind: str,
    budget: Budget,
    state: BudgetState,
    action: str,
) -> None:
    """Emit a budget_exceeded trace event with full context.
    
    Args:
        trace: Optional trace emitter callback.
        kind: The kind of budget consumption (pass, tool, parallel).
        budget: The budget limits.
        state: Current budget state with violations.
        action: The action taken (FAIL, HITL, DEGRADE).
    """
    if trace is None:
        return
    
    limit_map = {
        "pass": budget.max_passes,
        "tool": budget.max_tool_calls,
        "parallel": budget.max_parallel_calls,
    }
    
    trace(
        "budget_exceeded",
        {
            "kind": kind,
            "limit": limit_map.get(kind, 0),
            "state": state.model_dump(mode="json"),
            "action_taken": action,
            "violations": state.violations,
            "requires_hitl": should_escalate_to_hitl(action),
        },
    )


def emit_hitl_escalation_event(
    trace: Optional[TraceEmitter],
    *,
    reason: str,
    context: Dict[str, Any],
) -> None:
    """Emit HITL escalation event for governance tracking.
    
    Args:
        trace: Optional trace emitter callback.
        reason: The reason for HITL escalation.
        context: Additional context for the escalation.
    """
    if trace is None:
        return
    
    trace(
        "hitl_escalation_triggered",
        {
            "reason": reason,
            "context": context,
        },
    )
