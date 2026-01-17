from core.contracts.flow_schema import StepDef, StepType
from core.orchestrator.context import RunContext, StepContext
from products.ade.agents.planning_agent import PlanningAgent


def test_planning_agent_replan_fields() -> None:
    run = RunContext(
        run_id="run_1",
        product="ade",
        flow="ade_v1",
        payload={"replan_comment": "Adjust chart type"},
        artifacts={},
    )
    step = StepDef(id="planning", type=StepType.AGENT, agent="planning_agent")
    ctx = StepContext(run=run, step=step, step_id="planning", type="agent")

    agent = PlanningAgent()
    result = agent.run(ctx)
    assert result.ok
    payload = result.data or {}
    assert payload.get("replan_change_summary")
    assert payload.get("replan_rationale")
