from __future__ import annotations

# ==============================
# Tests: Plan Proposal Schema
# ==============================

from core.contracts.plan_schema import EstimatedCost, PlanApproval, PlanProposal, PlanStep


def test_plan_proposal_schema_validates() -> None:
    plan = PlanProposal(
        schema_version="1.0",
        summary="Proposed execution plan",
        steps=[
            PlanStep(step_id="s1", description="Read input", step_type="tool", tool="data_reader"),
            PlanStep(step_id="s2", description="Summarize", step_type="agent", agent="llm_reasoner"),
        ],
        required_tools=["data_reader"],
        approvals=[PlanApproval(step_id="s2", reason="Review narrative")],
        estimated_cost=EstimatedCost(currency="USD", amount=0.12, tokens=1200),
    )
    payload = plan.model_dump(mode="json")
    assert payload["summary"] == "Proposed execution plan"
    assert payload["estimated_cost"]["currency"] == "USD"
