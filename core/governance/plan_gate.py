from __future__ import annotations

# ==============================
# Action Plan Gating
# ==============================
"""
Deterministic gating for executable action plans.
"""

from typing import List, Optional, Tuple

from core.contracts.action_plan_schema import ActionPlan, PlanGateResult, PlanRejection, PlanStep, PlanToolCall, PlanAgentCall
from core.contracts.budget_schema import Budget
from core.governance.budgeting import consume_budget, init_budget_state
from core.tools.registry import ToolRegistry
from core.agents.registry import AgentRegistry


def gate_action_plan(
    plan: ActionPlan,
    *,
    allow_tools: Optional[List[str]] = None,
    allow_agents: Optional[List[str]] = None,
    budget: Optional[Budget] = None,
    sensitivity: str = "LOW",
) -> PlanGateResult:
    allow_tools_set = {name.strip().lower() for name in (allow_tools or [])}
    allow_agents_set = {name.strip().lower() for name in (allow_agents or [])}
    rejected: List[PlanRejection] = []
    approved: List[PlanStep] = []
    requires_hitl: List[int] = []
    reasons: List[str] = []

    if budget is None:
        budget_state = None
    else:
        budget_state = init_budget_state()

    for idx, step in enumerate(plan.steps):
        if isinstance(step, PlanToolCall):
            tool_name = step.tool_name
            if allow_tools_set and tool_name.strip().lower() not in allow_tools_set:
                rejected.append(PlanRejection(step=step.model_dump(mode="json"), reason="tool_not_allowed"))
                reasons.append("tool_not_allowed")
                return _reject(plan, rejected, reasons, budget, sensitivity)
            if not ToolRegistry.has(tool_name):
                rejected.append(PlanRejection(step=step.model_dump(mode="json"), reason="tool_not_registered"))
                reasons.append("tool_not_registered")
                return _reject(plan, rejected, reasons, budget, sensitivity)
            descriptor = ToolRegistry.get_descriptor(tool_name)
            if descriptor.side_effect:
                requires_hitl.append(idx)
            if budget and budget_state:
                allowed, action, updated = consume_budget(
                    budget=budget,
                    state=budget_state,
                    kind="tool",
                    amount=1,
                    cost_units=1,
                )
                budget_state = updated
                if not allowed:
                    reasons.append("budget_exceeded")
                    return _truncate_or_reject(plan, approved, rejected, requires_hitl, reasons, budget, sensitivity, action)
            approved.append(step)
        elif isinstance(step, PlanAgentCall):
            agent_name = step.agent_name
            if allow_agents_set and agent_name.strip().lower() not in allow_agents_set:
                rejected.append(PlanRejection(step=step.model_dump(mode="json"), reason="agent_not_allowed"))
                reasons.append("agent_not_allowed")
                return _reject(plan, rejected, reasons, budget, sensitivity)
            if not AgentRegistry.has(agent_name):
                rejected.append(PlanRejection(step=step.model_dump(mode="json"), reason="agent_not_registered"))
                reasons.append("agent_not_registered")
                return _reject(plan, rejected, reasons, budget, sensitivity)
            if budget and budget_state:
                allowed, action, updated = consume_budget(
                    budget=budget,
                    state=budget_state,
                    kind="pass",
                    amount=1,
                    cost_units=1,
                )
                budget_state = updated
                if not allowed:
                    reasons.append("budget_exceeded")
                    return _truncate_or_reject(plan, approved, rejected, requires_hitl, reasons, budget, sensitivity, action)
            approved.append(step)

    status = "REQUIRES_HITL" if requires_hitl else "APPROVED"
    return PlanGateResult(
        plan_id=plan.id,
        status=status,
        approved_steps=approved,
        rejected_steps=rejected,
        requires_hitl_for_steps=requires_hitl,
        reasons=sorted(set(reasons)),
        effective_budget=budget.model_dump(mode="json") if budget else None,
        sensitivity=sensitivity,
    )


def _truncate_or_reject(
    plan: ActionPlan,
    approved: List[PlanStep],
    rejected: List[PlanRejection],
    requires_hitl: List[int],
    reasons: List[str],
    budget: Optional[Budget],
    sensitivity: str,
    action: str,
) -> PlanGateResult:
    if action == "FAIL":
        return _reject(plan, rejected, reasons, budget, sensitivity)
    if not approved:
        return _reject(plan, rejected, reasons, budget, sensitivity)
    return PlanGateResult(
        plan_id=plan.id,
        status="TRUNCATED",
        approved_steps=approved,
        rejected_steps=rejected,
        requires_hitl_for_steps=requires_hitl,
        reasons=sorted(set(reasons)),
        effective_budget=budget.model_dump(mode="json") if budget else None,
        sensitivity=sensitivity,
    )


def _reject(
    plan: ActionPlan,
    rejected: List[PlanRejection],
    reasons: List[str],
    budget: Optional[Budget],
    sensitivity: str,
) -> PlanGateResult:
    return PlanGateResult(
        plan_id=plan.id,
        status="REJECTED",
        approved_steps=[],
        rejected_steps=rejected,
        requires_hitl_for_steps=[],
        reasons=sorted(set(reasons)) or ["rejected"],
        effective_budget=budget.model_dump(mode="json") if budget else None,
        sensitivity=sensitivity,
    )
