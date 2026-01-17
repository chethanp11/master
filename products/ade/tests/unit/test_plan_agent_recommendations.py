from core.contracts.flow_schema import StepDef, StepType
from core.orchestrator.context import RunContext, StepContext
from products.ade.agents.plan_agent import PlanAgent


def test_plan_agent_tool_recommendations() -> None:
    run = RunContext(
        run_id="run_1",
        product="ade",
        flow="ade_v1",
        payload={},
        artifacts={
            "agent.intent_agent.output": {
                "intent_summary": "Summarize dataset",
                "inferred_entities": ["sample.csv"],
                "inferred_metrics": ["amount_inr"],
                "inferred_time_window": "last 30 days",
                "blocking_required": False,
            }
        },
    )
    step = StepDef(id="plan", type=StepType.AGENT, agent="plan_agent")
    ctx = StepContext(run=run, step=step, step_id="plan", type="agent")

    agent = PlanAgent()
    result = agent.run(ctx)
    assert result.ok
    payload = result.data or {}
    recommendations = payload.get("tool_recommendations") or []
    assert recommendations
    assert all(item.get("optional") is True for item in recommendations)
