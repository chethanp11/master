# ==============================
# Tests: Agents (Base + Registry + Minimal Agent Run)
# ==============================
from __future__ import annotations

from typing import Any, Dict, Optional

from core.agents.base import BaseAgent
from core.agents.registry import AgentRegistry
from core.contracts.agent_schema import AgentMeta, AgentResult
from core.orchestrator.context import RunContext
from core.orchestrator.state import RunStatus
from core.contracts.flow_schema import AutonomyLevel


class _EchoAgent(BaseAgent):
    def __init__(self, name: str = "echo_agent") -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def run(self, step_ctx: Any) -> AgentResult:
        # Minimal agent that echoes payload + prior artifacts
        message = None
        try:
            message = step_ctx.run.payload.get("keyword")  # type: ignore[attr-defined]
        except Exception:
            message = None

        data = {
            "echo": message,
            "artifact_keys": sorted(list(getattr(step_ctx.run, "artifacts", {}).keys())),
        }
        return AgentResult(ok=True, data=data, error=None, meta=AgentMeta(agent_name=self.name))


def test_agent_registry_register_and_resolve() -> None:
    AgentRegistry.clear()
    a = _EchoAgent()
    AgentRegistry.register(a.name, a)
    resolved = AgentRegistry.resolve(a.name)
    assert resolved is not None
    assert resolved.name == "echo_agent"


def test_agent_registry_duplicate_registration_raises() -> None:
    AgentRegistry.clear()
    a = _EchoAgent("dup_agent")
    AgentRegistry.register(a.name, a)
    try:
        AgentRegistry.register(a.name, a)
        assert False, "Expected duplicate registration to raise"
    except ValueError:
        assert True


def test_agent_run_returns_agent_result() -> None:
    AgentRegistry.clear()
    a = _EchoAgent()
    AgentRegistry.register(a.name, a)

    run = RunContext(
        run_id="r1",
        product="hello_world",
        flow="hello_world",
        status=RunStatus.RUNNING,
        payload={"keyword": "hi"},
        artifacts={"k1": {"v": 1}},
        meta={},
    )
    step = run.new_step(step_id="s_agent", step_type="agent", backend="local", target=a.name)

    resolved = AgentRegistry.resolve("echo_agent")
    assert resolved is not None

    res = resolved.run(step)
    assert res.ok is True
    assert res.data is not None
    assert res.data["echo"] == "hi"
    assert "k1" in res.data["artifact_keys"]
