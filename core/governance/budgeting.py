from __future__ import annotations

# ==============================
# Budget Resolver + Consumption
# ==============================

from typing import Dict, Optional, Tuple

from core.contracts.budget_schema import Budget, BudgetPolicy, BudgetState, LatencyBucket

_LATENCY_ORDER = {"LOW": 0, "MED": 1, "HIGH": 2}


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


def consume_budget(
    *,
    budget: Budget,
    state: BudgetState,
    kind: str,
    amount: int = 1,
    cost_units: int = 0,
    latency_bucket: Optional[LatencyBucket] = None,
) -> Tuple[bool, str, BudgetState]:
    updated = state.model_copy()
    violations = list(updated.violations)

    if latency_bucket:
        if _LATENCY_ORDER[latency_bucket] > _LATENCY_ORDER[updated.latency_bucket_observed]:
            updated.latency_bucket_observed = latency_bucket
        if _LATENCY_ORDER[updated.latency_bucket_observed] > _LATENCY_ORDER[budget.max_latency_bucket]:
            violations.append("latency_bucket_exceeded")

    if kind == "pass":
        updated.passes_used += amount
        if updated.passes_used > budget.max_passes:
            violations.append("max_passes_exceeded")
    elif kind == "tool":
        updated.tool_calls_used += amount
        if updated.tool_calls_used > budget.max_tool_calls:
            violations.append("max_tool_calls_exceeded")
    elif kind == "parallel":
        updated.parallel_calls_used += amount
        if updated.parallel_calls_used > budget.max_parallel_calls:
            violations.append("max_parallel_calls_exceeded")

    updated.cost_units_used += cost_units
    if updated.cost_units_used > budget.max_total_cost_units:
        violations.append("max_total_cost_units_exceeded")

    updated.violations = violations

    if violations:
        if budget.on_exceed == "DEGRADE":
            degraded = _apply_degrade(budget, budget.degrade_to)
            return _recheck(degraded, updated, kind, amount, cost_units, latency_bucket)
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
) -> Tuple[bool, str, BudgetState]:
    state = state.model_copy(update={"violations": []})
    return consume_budget(
        budget=budget,
        state=state,
        kind=kind,
        amount=amount,
        cost_units=cost_units,
        latency_bucket=latency_bucket,
    )
