from core.contracts.flow_schema import StepDef, StepType
from core.orchestrator.context import RunContext, StepContext
from products.ade.agents.dashboard_agent import DashboardAgent


def test_dashboard_agent_anomaly_interpretation() -> None:
    run = RunContext(
        run_id="run_1",
        product="ade",
        flow="ade_v1",
        payload={},
        artifacts={
            "tool.data_reader.output": {"summary": "Summary"},
            "tool.detect_anomalies.output": {"summary": "found 2 anomalies", "anomalies": [{}, {}]},
        },
    )
    step = StepDef(id="dashboard", type=StepType.AGENT, agent="dashboard_agent")
    ctx = StepContext(run=run, step=step, step_id="dashboard", type="agent")

    agent = DashboardAgent()
    result = agent.run(ctx)
    assert result.ok
    payload = result.data or {}
    assert payload["anomaly_count"] == 2
    assert "Detected 2 anomaly candidates" in payload["anomaly_interpretation"]
