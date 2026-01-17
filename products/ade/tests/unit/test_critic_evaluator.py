from core.contracts.flow_schema import StepDef, StepType
from core.orchestrator.context import RunContext, StepContext
from products.ade.agents.critic_evaluator import CriticEvaluatorAgent


def _build_context(artifacts: dict) -> StepContext:
    run = RunContext(run_id="run_1", product="ade", flow="ade_v1", payload={}, artifacts=artifacts)
    step = StepDef(id="critic_eval", type=StepType.AGENT, agent="critic_evaluator")
    return StepContext(run=run, step=step, step_id="critic_eval", type="agent")


def test_critic_evaluator_flags_gaps() -> None:
    ctx = _build_context(
        {
            "agent.sufficiency_evaluator.output": {
                "confidence_level": "high",
                "downgrade_reasons": ["insufficient_rows"],
            },
            "agent.plan_proposal_agent.output": {"steps": []},
        }
    )
    agent = CriticEvaluatorAgent()
    result = agent.run(ctx)
    assert result.ok
    payload = result.data or {}
    assert payload["stage"] == "critique"
    assert "insufficient_rows" in payload["evidence_gaps"]
    assert "missing_plan_steps" in payload["evidence_gaps"]
    assert payload["downgrade_reason"] == "critique_evidence_gap"
    assert payload["blocking_required"] is True
