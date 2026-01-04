# ==============================
# Tests: Core role agents
# ==============================
from __future__ import annotations

import json

from core.agents.llm_reasoner import (
    ExplanationReasoner,
    InsightReasoner,
    PrioritizationReasoner,
)
from core.agents.registry import AgentRegistry
from core.contracts.agent_schema import AgentMeta, AgentResult, AgentKind
from core.contracts.flow_schema import StepDef, StepType
from core.orchestrator.context import RunContext


def _make_step_ctx(agent_name: str, params: dict) -> "object":
    step_def = StepDef(id="step", type=StepType.AGENT, agent=agent_name, params=params)
    run_ctx = RunContext(run_id="run_1", product="demo", flow="demo", payload={})
    return run_ctx.new_step(step_def=step_def)


def _fake_llm_result(payload: dict) -> AgentResult:
    meta = AgentMeta(agent_name="llm_reasoner", kind=AgentKind.OTHER, tags={})
    return AgentResult(ok=True, data={"content": json.dumps(payload)}, error=None, meta=meta)


def test_registry_registers_core_role_agents() -> None:
    AgentRegistry.clear()
    assert AgentRegistry.has("insight_reasoner")
    assert AgentRegistry.has("prioritization_reasoner")
    assert AgentRegistry.has("explanation_reasoner")


def test_insight_reasoner_parses_output(monkeypatch) -> None:
    payload = {"summary": "ok", "highlights": ["a"], "risks": []}
    monkeypatch.setattr(
        "core.agents.llm_reasoner.LlmReasoner.run",
        lambda self, ctx: _fake_llm_result(payload),
    )
    agent = InsightReasoner()
    result = agent.run(_make_step_ctx(agent.name, {"prompt": "test"}))
    assert result.ok
    assert result.data["summary"] == "ok"


def test_prioritization_reasoner_parses_output(monkeypatch) -> None:
    payload = {"priorities": [{"item": "A", "priority": 1, "rationale": "top"}]}
    monkeypatch.setattr(
        "core.agents.llm_reasoner.LlmReasoner.run",
        lambda self, ctx: _fake_llm_result(payload),
    )
    agent = PrioritizationReasoner()
    result = agent.run(_make_step_ctx(agent.name, {"prompt": "test"}))
    assert result.ok
    assert result.data["priorities"][0]["item"] == "A"


def test_explanation_reasoner_parses_output(monkeypatch) -> None:
    payload = {"explanation": "because", "assumptions": [], "limitations": []}
    monkeypatch.setattr(
        "core.agents.llm_reasoner.LlmReasoner.run",
        lambda self, ctx: _fake_llm_result(payload),
    )
    agent = ExplanationReasoner()
    result = agent.run(_make_step_ctx(agent.name, {"prompt": "test"}))
    assert result.ok
    assert result.data["explanation"] == "because"
