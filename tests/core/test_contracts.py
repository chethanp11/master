# ==============================
# Tests: Core Contracts
# ==============================
from __future__ import annotations

from typing import Any, Dict

import pytest
from pydantic import ValidationError

from core.contracts.agent_schema import AgentError, AgentMeta, AgentResult
from core.contracts.flow_schema import AutonomyLevel, FlowDef, StepDef, StepType
from core.contracts.run_schema import ArtifactRef, RunRecord, StepRecord, TraceEvent
from core.contracts.tool_schema import ToolError, ToolMeta, ToolResult


def test_tool_result_envelope_ok() -> None:
    r = ToolResult(ok=True, data={"x": 1}, error=None, meta=ToolMeta(tool_name="t", backend="local"))
    assert r.ok is True
    assert r.data == {"x": 1}
    assert r.error is None
    assert r.meta.tool_name == "t"


def test_tool_result_requires_error_when_not_ok() -> None:
    with pytest.raises(ValidationError):
        ToolResult(ok=False, data=None, error=None, meta=ToolMeta(tool_name="t", backend="local"))


def test_agent_result_envelope_ok() -> None:
    r = AgentResult(ok=True, data={"y": 2}, error=None, meta=AgentMeta(agent_name="a"))
    assert r.ok is True
    assert r.data == {"y": 2}
    assert r.error is None


def test_agent_result_requires_error_when_not_ok() -> None:
    with pytest.raises(ValidationError):
        AgentResult(ok=False, data=None, error=None, meta=AgentMeta(agent_name="a"))


def test_flow_def_and_steps_validate() -> None:
    f = FlowDef(
        name="hello",
        version="1.0.0",
        autonomy_level=AutonomyLevel.suggest_only,
        steps=[
            StepDef(id="s1", type=StepType.tool, tool="echo_tool", backend="local"),
            StepDef(id="s2", type=StepType.human_approval, title="Approve", message="ok?"),
            StepDef(id="s3", type=StepType.agent, agent="simple_agent", backend="local"),
        ],
    )
    assert f.name == "hello"
    assert f.steps[0].type == StepType.tool


def test_step_def_requires_tool_or_agent() -> None:
    with pytest.raises(ValidationError):
        StepDef(id="bad", type=StepType.tool, backend="local")

    with pytest.raises(ValidationError):
        StepDef(id="bad2", type=StepType.agent, backend="local")


def test_run_models_validate_minimal() -> None:
    run = RunRecord(run_id="r1", product="sandbox", flow="hello_world", status="RUNNING")
    step = StepRecord(run_id="r1", step_id="s1", status="RUNNING")
    event = TraceEvent(run_id="r1", step_id="s1", product="sandbox", flow="hello_world", event_type="test", payload={"a": 1})
    art = ArtifactRef(key="k", kind="json", uri="memory://k")
    assert run.run_id == "r1"
    assert step.step_id == "s1"
    assert event.payload["a"] == 1
    assert art.key == "k"
