# ==============================
# Tests: Agent Output Guardrails
# ==============================
from __future__ import annotations

import pytest

from core.agents.base import BaseAgent
from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.agent_schema import AgentMeta, AgentResult, validate_agent_output_payload
from core.contracts.flow_schema import BackendType, StepDef, StepType
from core.governance.hooks import GovernanceHooks
from core.orchestrator.context import RunContext
from core.orchestrator.step_executor import StepExecutor


class _NoopToolExecutor:
    def execute(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("tool executor should not be called")


class _ControlAgent(BaseAgent):
    name = "control_agent"

    def __init__(self, payload):  # type: ignore[no-untyped-def]
        super().__init__()
        self._payload = payload

    def run(self, step_context):  # type: ignore[no-untyped-def]
        return AgentResult(ok=True, data=self._payload, error=None, meta=AgentMeta(agent_name=self.name))


def test_agent_output_schema_rejects_control_fields() -> None:
    with pytest.raises(ValueError):
        validate_agent_output_payload({"next_step": "s2"})

    with pytest.raises(ValueError):
        validate_agent_output_payload({"data": {"branch_hint": "s3"}})


def test_step_executor_blocks_agent_control_output() -> None:
    settings = Settings()
    governance = GovernanceHooks(settings=settings)
    step_executor = StepExecutor(tool_executor=_NoopToolExecutor(), governance=governance, agent_registry=AgentRegistry)

    AgentRegistry.clear()
    try:
        AgentRegistry.register("control_agent", lambda: _ControlAgent({"next_step": "s2"}))
        run_ctx = RunContext(run_id="run_1", product="test_product", flow="test_flow")
        step_def = StepDef(
            id="step_1",
            type=StepType.AGENT,
            agent="control_agent",
            backend=BackendType.LOCAL,
        )
        with pytest.raises(RuntimeError) as exc:
            step_executor.execute(run_ctx=run_ctx, step_def=step_def)
        assert "agent_output_control_fields" in str(exc.value)
        assert "agent.control_agent.output" not in run_ctx.artifacts
    finally:
        AgentRegistry.clear()
