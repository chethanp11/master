# tests/unit/test_advisors_bounded.py
# ==============================
# Advisory Agents Bounded Behavior Tests
# ==============================
"""
Tests verifying advisory agents cannot execute tools and produce valid outputs.

Phase 13 invariants:
- Advisory agents cannot invoke ToolExecutor
- Advisory agents return structured, validated outputs
- Advisory agents cannot produce control-flow directives
"""

from __future__ import annotations

from typing import Any, Dict

import pytest

from core.agents.advisors import (
    AdvisoryAgent,
    ToolSelector,
    AgentSelector,
    GapFinder,
    Summarizer,
    RiskExplainer,
    build_tool_selector,
    build_agent_selector,
    build_gap_finder,
    build_summarizer,
    build_risk_explainer,
)
from core.contracts.flow_schema import StepDef, StepType
from core.orchestrator.context import RunContext


# ==============================
# Mock Reasoners
# ==============================


def _tool_selector_reasoner(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "recommended_tools": [
            {
                "tool_name": "test_tool",
                "reason": "Suitable for the task",
                "required_inputs": {"query": "string"},
                "expected_evidence_types": ["text"],
                "confidence": 0.85,
            }
        ],
        "rejected_tools": [
            {"tool_name": "wrong_tool", "reason": "Not applicable"}
        ],
        "assumptions": ["User wants text-based evidence"],
        "unknowns": ["Data freshness requirements"],
    }


def _agent_selector_reasoner(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "recommended_agents": [
            {"agent_name": "summarizer", "reason": "Can condense results", "confidence": 0.9}
        ],
        "rejected_agents": [],
        "assumptions": [],
        "unknowns": [],
    }


def _gap_finder_reasoner(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "missing_evidence": [],
        "missing_fields": ["customer_id"],
        "questions_for_user": [
            {"key": "customer_id", "prompt": "What is the customer ID?", "required": True}
        ],
        "confidence": 0.75,
    }


def _summarizer_reasoner(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "summary": "The analysis shows positive results across all metrics.",
        "key_points": ["Revenue increased 15%", "Customer satisfaction stable"],
        "evidence_refs": ["ev_001", "ev_002"],
    }


def _risk_explainer_reasoner(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "risk_factors": [
            {
                "factor": "Data staleness",
                "rationale": "Data is 30 days old which may not reflect current state",
                "evidence_refs": ["ev_001"],
                "severity": "MED",
            }
        ],
        "mitigations": ["Refresh data before finalizing decision"],
        "confidence": 0.7,
        "assumptions": ["Current data structure is stable"],
        "unknowns": ["Market volatility impact"],
    }


# ==============================
# Helper Functions
# ==============================


def _make_step_context(agent_name: str) -> Any:
    """Create a minimal step context for testing."""
    run_ctx = RunContext(
        run_id="test_run",
        product="test_product",
        flow="test_flow",
        payload={},
    )
    step_def = StepDef(
        id=f"test_{agent_name}",
        type=StepType.AGENT,
        agent=agent_name,
        params={"question": "Test question"},
    )
    return run_ctx.new_step(step_def)


# ==============================
# Base Class Tests
# ==============================


def test_advisory_agent_cannot_execute_tools() -> None:
    """Advisory agents have can_execute_tools=False enforced."""
    advisors = [
        ToolSelector(),
        AgentSelector(),
        GapFinder(),
        Summarizer(),
        RiskExplainer(),
    ]
    for advisor in advisors:
        assert advisor.can_execute_tools is False, f"{advisor.name} should not execute tools"
        assert advisor._can_execute_tools is False, f"{advisor.name}._can_execute_tools should be False"


def test_advisory_agent_base_class_enforces_no_tools() -> None:
    """AdvisoryAgent base class enforces no tool execution capability."""

    class TestAdvisor(AdvisoryAgent):
        name = "test_advisor"
        output_model = None  # type: ignore

        def _build_system_prompt(self) -> str:
            return "test"

    advisor = TestAdvisor()
    assert advisor.can_execute_tools is False
    assert advisor._can_execute_tools is False

    # Attempt to override should not work (property returns False)
    advisor._can_execute_tools = True  # type: ignore
    assert advisor.can_execute_tools is False  # Property still returns False


# ==============================
# Tool Selector Tests
# ==============================


def test_tool_selector_returns_structured_output() -> None:
    """ToolSelector returns valid ToolSelectorOutput."""
    advisor = ToolSelector(llm_reasoner=_tool_selector_reasoner)
    ctx = _make_step_context("tool_selector")

    result = advisor.run(ctx)

    assert result.ok is True
    assert result.data is not None
    assert "recommended_tools" in result.data
    assert "rejected_tools" in result.data
    assert len(result.data["recommended_tools"]) == 1
    assert result.data["recommended_tools"][0]["tool_name"] == "test_tool"


def test_tool_selector_factory() -> None:
    """build_tool_selector returns a ToolSelector instance."""
    advisor = build_tool_selector()
    assert isinstance(advisor, ToolSelector)
    assert advisor.name == "tool_selector"


# ==============================
# Agent Selector Tests
# ==============================


def test_agent_selector_returns_structured_output() -> None:
    """AgentSelector returns valid AgentSelectorOutput."""
    advisor = AgentSelector(llm_reasoner=_agent_selector_reasoner)
    ctx = _make_step_context("agent_selector")

    result = advisor.run(ctx)

    assert result.ok is True
    assert result.data is not None
    assert "recommended_agents" in result.data
    assert len(result.data["recommended_agents"]) == 1
    assert result.data["recommended_agents"][0]["agent_name"] == "summarizer"


def test_agent_selector_factory() -> None:
    """build_agent_selector returns an AgentSelector instance."""
    advisor = build_agent_selector()
    assert isinstance(advisor, AgentSelector)
    assert advisor.name == "agent_selector"


# ==============================
# Gap Finder Tests
# ==============================


def test_gap_finder_returns_structured_output() -> None:
    """GapFinder returns valid GapFinderOutput."""
    advisor = GapFinder(llm_reasoner=_gap_finder_reasoner)
    ctx = _make_step_context("gap_finder")

    result = advisor.run(ctx)

    assert result.ok is True
    assert result.data is not None
    assert "missing_fields" in result.data
    assert "questions_for_user" in result.data
    assert "confidence" in result.data
    assert "customer_id" in result.data["missing_fields"]


def test_gap_finder_factory() -> None:
    """build_gap_finder returns a GapFinder instance."""
    advisor = build_gap_finder()
    assert isinstance(advisor, GapFinder)
    assert advisor.name == "gap_finder"


# ==============================
# Summarizer Tests
# ==============================


def test_summarizer_returns_structured_output() -> None:
    """Summarizer returns valid SummarizerOutput."""
    advisor = Summarizer(llm_reasoner=_summarizer_reasoner)
    ctx = _make_step_context("summarizer")

    result = advisor.run(ctx)

    assert result.ok is True
    assert result.data is not None
    assert "summary" in result.data
    assert "key_points" in result.data
    assert "evidence_refs" in result.data
    assert len(result.data["key_points"]) == 2


def test_summarizer_factory() -> None:
    """build_summarizer returns a Summarizer instance."""
    advisor = build_summarizer()
    assert isinstance(advisor, Summarizer)
    assert advisor.name == "summarizer"


# ==============================
# Risk Explainer Tests
# ==============================


def test_risk_explainer_returns_structured_output() -> None:
    """RiskExplainer returns valid RiskExplainerOutput."""
    advisor = RiskExplainer(llm_reasoner=_risk_explainer_reasoner)
    ctx = _make_step_context("risk_explainer")

    result = advisor.run(ctx)

    assert result.ok is True
    assert result.data is not None
    assert "risk_factors" in result.data
    assert "mitigations" in result.data
    assert "confidence" in result.data
    assert len(result.data["risk_factors"]) == 1
    assert result.data["risk_factors"][0]["severity"] == "MED"


def test_risk_explainer_factory() -> None:
    """build_risk_explainer returns a RiskExplainer instance."""
    advisor = build_risk_explainer()
    assert isinstance(advisor, RiskExplainer)
    assert advisor.name == "risk_explainer"


# ==============================
# Error Handling Tests
# ==============================


def test_advisor_handles_invalid_reasoner_output() -> None:
    """Advisor returns error result when reasoner output is invalid."""

    def bad_reasoner(payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"invalid": "structure"}

    advisor = ToolSelector(llm_reasoner=bad_reasoner)
    ctx = _make_step_context("tool_selector")

    result = advisor.run(ctx)

    assert result.ok is False
    assert result.error is not None
    assert result.error.code.value == "invalid_input"


def test_advisor_handles_reasoner_exception() -> None:
    """Advisor returns error result when reasoner raises exception."""

    def failing_reasoner(payload: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("Reasoner failed")

    advisor = ToolSelector(llm_reasoner=failing_reasoner)
    ctx = _make_step_context("tool_selector")

    result = advisor.run(ctx)

    assert result.ok is False
    assert result.error is not None
    assert "Reasoner failed" in result.error.message


# ==============================
# Meta/Audit Tests
# ==============================


def test_advisor_result_includes_meta() -> None:
    """Advisor result includes proper metadata."""
    advisor = ToolSelector(llm_reasoner=_tool_selector_reasoner)
    ctx = _make_step_context("tool_selector")

    result = advisor.run(ctx)

    assert result.meta is not None
    assert result.meta.agent_name == "tool_selector"
    assert result.meta.kind.value == "router"


def test_all_advisors_have_distinct_names() -> None:
    """Each advisor has a unique name."""
    advisors = [
        ToolSelector(),
        AgentSelector(),
        GapFinder(),
        Summarizer(),
        RiskExplainer(),
    ]
    names = [a.name for a in advisors]
    assert len(names) == len(set(names)), "Advisor names must be unique"
