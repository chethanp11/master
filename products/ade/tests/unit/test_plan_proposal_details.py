from core.contracts.flow_schema import StepDef, StepType
from core.orchestrator.context import RunContext, StepContext
from products.ade.agents.plan_proposal_agent import PlanProposalAgent


def test_plan_proposal_includes_objective_and_evidence() -> None:
    run = RunContext(
        run_id="run_1",
        product="ade",
        flow="ade_v1",
        payload={},
        artifacts={
            "agent.plan_agent.output": {
                "chart_type": "line",
                "metric": "amount_inr",
                "dataset_id": "sample.csv",
                "tool_flags": {"detect_anomalies": True},
            }
        },
    )
    step = StepDef(id="plan_proposal", type=StepType.PLAN_PROPOSAL, agent="plan_proposal_agent")
    ctx = StepContext(run=run, step=step, step_id="plan_proposal", type="plan_proposal")

    agent = PlanProposalAgent()
    result = agent.run(ctx)
    assert result.ok
    payload = result.data or {}
    details = payload.get("estimated_cost", {}).get("details", {})
    assert "objective" in details
    assert details.get("expected_evidence")
