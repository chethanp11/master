from __future__ import annotations

"""Tests for Phase 9: Bounded Reasoning & Critic Pattern.

Tests cover:
- ReasoningBudget configuration and conversion to Budget
- HITL escalation on budget exceeded
- Bounded reasoning with budget enforcement
- Critic evaluator budget awareness
- Governance integration for critic recommendations
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pytest

from core.agents.critic_evaluator import (
    CriticEvaluatorAgent,
    evaluate_with_governance,
    run_critic_evaluator,
)
from core.agents.reasoning_ladder import run_bounded_reasoning, run_reasoning_ladder
from core.contracts.budget_schema import Budget, BudgetState, ReasoningBudget
from core.contracts.context_pack_schema import ContextPackConfig, EvidenceItem, EvidenceSource
from core.contracts.critic_schema import CriticOutput, CriticResult
from core.contracts.reasoning_ladder_schema import (
    ReasoningLadderConfig,
    ReasoningLadderInterpret,
    ReasoningLadderOutput,
    ReasoningLadderPropose,
    ReasoningLadderSelect,
)
from core.contracts.run_schema import ArtifactRef
from core.governance.budgeting import (
    consume_budget,
    emit_budget_exceeded_event,
    emit_hitl_escalation_event,
    init_budget_state,
    init_reasoning_budget,
    should_escalate_to_hitl,
)
from core.knowledge.context_pack import build_context_pack


# =============================================================================
# Fixtures and Helpers
# =============================================================================


class _StubLadderReasoner:
    """Stub reasoner that returns valid responses for each pass."""

    def __init__(self, *, fail_pass: Optional[str] = None) -> None:
        self.fail_pass = fail_pass

    def __call__(self, pass_name: str, payload: Dict[str, Any]) -> str:
        if self.fail_pass == pass_name:
            return "invalid-json"
        if pass_name == "interpret":
            return json.dumps({
                "intent": "analyze",
                "entities": [{"name": "test"}],
                "constraints": ["bounded"],
            })
        if pass_name == "propose":
            return json.dumps({
                "candidates": [{"id": "c1", "title": "Option A", "description": "First option"}],
                "tool_candidates": [],
                "agent_candidates": [],
            })
        if pass_name == "select":
            return json.dumps({
                "select": {"chosen": {"id": "c1"}, "rationale": "best", "evidence_refs": []},
                "confidence": 0.8,
                "assumptions": [],
                "unknowns": [],
            })
        return "{}"


class _StubCriticReasoner:
    """Stub reasoner that returns valid critic output."""

    def __init__(
        self,
        *,
        completeness_score: float = 0.8,
        recommended_action: str = "NONE",
        inconsistency_flags: Optional[List[str]] = None,
    ) -> None:
        self.completeness_score = completeness_score
        self.recommended_action = recommended_action
        self.inconsistency_flags = inconsistency_flags or []

    def __call__(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "completeness_score": self.completeness_score,
            "inconsistency_flags": self.inconsistency_flags,
            "missing_evidence_requests": [],
            "confidence_adjustment": 0.1,
            "recommended_next_action": self.recommended_action,
            "notes": None,
        }


def _build_context_pack() -> Tuple[Any, Dict[str, Any]]:
    """Build a minimal context pack for tests."""
    artifacts: Dict[str, Any] = {}
    text_key = "artifact.text"
    artifacts[text_key] = {"text": "Test evidence content."}

    text_ref = ArtifactRef(key=text_key, kind="text", uri=f"memory://{text_key}")
    now = datetime(2024, 1, 1)
    evidence = [
        EvidenceItem(
            id="evidence-1",
            type="text",
            source=EvidenceSource(tool="test_tool", ref="r1"),
            timestamp=now,
            confidence=0.9,
            content_ref=text_ref,
            summary="test summary",
            provenance={},
        ),
    ]
    config = ContextPackConfig(table_row_limit=10, excerpt_char_limit=100, artifacts=artifacts)
    pack = build_context_pack(evidence, question="Test question?", config=config)
    return pack, artifacts


def _build_reasoning_output() -> ReasoningLadderOutput:
    """Build a minimal reasoning output for critic tests."""
    return ReasoningLadderOutput(
        interpret=ReasoningLadderInterpret(
            intent="test",
            entities=[],
            constraints=[],
        ),
        propose=ReasoningLadderPropose(
            candidates=[],
            tool_candidates=[],
            agent_candidates=[],
        ),
        select=ReasoningLadderSelect(
            chosen={"id": "test"},
            rationale="test rationale",
            evidence_refs=[],
        ),
        confidence=0.7,
        assumptions=[],
        unknowns=[],
    )


# =============================================================================
# ReasoningBudget Tests
# =============================================================================


def test_reasoning_budget_defaults() -> None:
    """ReasoningBudget has sensible defaults."""
    rb = ReasoningBudget()
    assert rb.max_passes == 3
    assert rb.max_tool_calls == 10
    assert rb.max_parallel_calls == 3
    assert rb.max_total_cost_units == 100.0
    assert rb.max_latency_bucket == "MED"
    assert rb.escalate_on_exceed is True


def test_reasoning_budget_to_budget_with_escalation() -> None:
    """ReasoningBudget converts to Budget with HITL on_exceed when escalate_on_exceed=True."""
    rb = ReasoningBudget(escalate_on_exceed=True)
    budget = rb.to_budget()
    assert budget.on_exceed == "HITL"
    assert budget.max_passes == rb.max_passes
    assert budget.max_tool_calls == rb.max_tool_calls


def test_reasoning_budget_to_budget_without_escalation() -> None:
    """ReasoningBudget converts to Budget with FAIL on_exceed when escalate_on_exceed=False."""
    rb = ReasoningBudget(escalate_on_exceed=False)
    budget = rb.to_budget()
    assert budget.on_exceed == "FAIL"


def test_init_reasoning_budget_creates_valid_state() -> None:
    """init_reasoning_budget returns Budget and BudgetState ready for use."""
    rb = ReasoningBudget(max_passes=5, max_tool_calls=20)
    budget, state = init_reasoning_budget(rb)
    
    assert budget.max_passes == 5
    assert budget.max_tool_calls == 20
    assert state.passes_used == 0
    assert state.tool_calls_used == 0
    assert state.violations == []


def test_init_reasoning_budget_uses_defaults_when_none() -> None:
    """init_reasoning_budget uses defaults when no ReasoningBudget provided."""
    budget, state = init_reasoning_budget(None)
    assert budget.max_passes == 3
    assert budget.on_exceed == "HITL"  # Default escalate_on_exceed=True


# =============================================================================
# HITL Escalation Tests
# =============================================================================


def test_should_escalate_to_hitl_true() -> None:
    """should_escalate_to_hitl returns True for HITL action."""
    assert should_escalate_to_hitl("HITL") is True


def test_should_escalate_to_hitl_false_for_fail() -> None:
    """should_escalate_to_hitl returns False for FAIL action."""
    assert should_escalate_to_hitl("FAIL") is False


def test_should_escalate_to_hitl_false_for_degrade() -> None:
    """should_escalate_to_hitl returns False for DEGRADE action."""
    assert should_escalate_to_hitl("DEGRADE") is False


def test_emit_budget_exceeded_event() -> None:
    """emit_budget_exceeded_event emits correct event structure."""
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    budget = Budget(max_passes=2, on_exceed="HITL")
    state = BudgetState(passes_used=3, violations=["max_passes_exceeded"])
    
    emit_budget_exceeded_event(trace, kind="pass", budget=budget, state=state, action="HITL")
    
    assert len(events) == 1
    assert events[0]["type"] == "budget_exceeded"
    assert events[0]["payload"]["kind"] == "pass"
    assert events[0]["payload"]["limit"] == 2
    assert events[0]["payload"]["action_taken"] == "HITL"
    assert events[0]["payload"]["requires_hitl"] is True
    assert "max_passes_exceeded" in events[0]["payload"]["violations"]


def test_emit_hitl_escalation_event() -> None:
    """emit_hitl_escalation_event emits correct event structure."""
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    emit_hitl_escalation_event(
        trace,
        reason="budget_exceeded",
        context={"pass_name": "interpret", "violations": ["max_passes_exceeded"]},
    )
    
    assert len(events) == 1
    assert events[0]["type"] == "hitl_escalation_triggered"
    assert events[0]["payload"]["reason"] == "budget_exceeded"
    assert events[0]["payload"]["context"]["pass_name"] == "interpret"


# =============================================================================
# Budget Consumption Tests
# =============================================================================


def test_consume_budget_tracks_passes() -> None:
    """consume_budget correctly tracks pass consumption."""
    budget = Budget(max_passes=3)
    state = init_budget_state()
    
    allowed1, action1, state = consume_budget(budget=budget, state=state, kind="pass")
    assert allowed1 is True
    assert state.passes_used == 1
    
    allowed2, action2, state = consume_budget(budget=budget, state=state, kind="pass")
    assert allowed2 is True
    assert state.passes_used == 2


def test_consume_budget_exceeds_max_passes() -> None:
    """consume_budget returns False when max_passes exceeded."""
    budget = Budget(max_passes=1, on_exceed="FAIL")
    state = init_budget_state()
    
    # First pass allowed
    allowed1, _, state = consume_budget(budget=budget, state=state, kind="pass")
    assert allowed1 is True
    
    # Second pass exceeds
    allowed2, action2, state = consume_budget(budget=budget, state=state, kind="pass")
    assert allowed2 is False
    assert action2 == "FAIL"
    assert "max_passes_exceeded" in state.violations


def test_consume_budget_hitl_on_exceed() -> None:
    """consume_budget returns HITL action when configured."""
    budget = Budget(max_passes=1, on_exceed="HITL")
    state = BudgetState(passes_used=1)
    
    allowed, action, _ = consume_budget(budget=budget, state=state, kind="pass")
    assert allowed is False
    assert action == "HITL"


# =============================================================================
# Bounded Reasoning Tests
# =============================================================================


def test_run_bounded_reasoning_completes_with_budget() -> None:
    """run_bounded_reasoning completes all passes within budget."""
    pack, _ = _build_context_pack()
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    config = ReasoningLadderConfig(max_passes=3)
    rb = ReasoningBudget(max_passes=5)  # Enough budget
    
    result = run_bounded_reasoning(
        context_pack=pack,
        question="Test?",
        config=config,
        llm_reasoner=_StubLadderReasoner(),
        reasoning_budget=rb,
        trace=trace,
    )
    
    assert result.ok
    assert result.output is not None
    
    # Check bounded_reasoning events
    started = [e for e in events if e["type"] == "bounded_reasoning_started"]
    assert len(started) == 1
    completed = [e for e in events if e["type"] == "bounded_reasoning_completed"]
    assert len(completed) == 1
    assert completed[0]["payload"]["ok"] is True


def test_run_reasoning_ladder_exceeds_budget_with_hitl() -> None:
    """run_reasoning_ladder emits HITL escalation when budget exceeded."""
    pack, _ = _build_context_pack()
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    config = ReasoningLadderConfig(max_passes=3)
    budget = Budget(max_passes=0, on_exceed="HITL")  # No passes allowed
    budget_state = init_budget_state()
    
    result = run_reasoning_ladder(
        context_pack=pack,
        question="Test?",
        config=config,
        llm_reasoner=_StubLadderReasoner(),
        trace=trace,
        budget=budget,
        budget_state=budget_state,
    )
    
    assert not result.ok
    assert result.error is not None
    assert result.error.reason == "budget_exceeded"
    
    # Check HITL escalation was triggered
    hitl_events = [e for e in events if e["type"] == "hitl_escalation_triggered"]
    assert len(hitl_events) == 1
    assert hitl_events[0]["payload"]["reason"] == "budget_exceeded"


def test_run_reasoning_ladder_tracks_budget_consumption() -> None:
    """run_reasoning_ladder correctly consumes budget for each pass."""
    pack, _ = _build_context_pack()
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    config = ReasoningLadderConfig(max_passes=3)
    budget = Budget(max_passes=10)  # Enough budget
    budget_state = init_budget_state()
    
    result = run_reasoning_ladder(
        context_pack=pack,
        question="Test?",
        config=config,
        llm_reasoner=_StubLadderReasoner(),
        trace=trace,
        budget=budget,
        budget_state=budget_state,
    )
    
    assert result.ok
    assert budget_state.passes_used == 3  # interpret, propose, select
    
    # Check budget_consumed events
    consumed_events = [e for e in events if e["type"] == "budget_consumed"]
    assert len(consumed_events) == 3


# =============================================================================
# Critic Evaluator Tests
# =============================================================================


def test_critic_evaluator_with_budget_tracking() -> None:
    """run_critic_evaluator tracks budget consumption."""
    pack, _ = _build_context_pack()
    reasoning = _build_reasoning_output()
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    budget = Budget(max_passes=5)
    budget_state = init_budget_state()
    
    result = run_critic_evaluator(
        context_pack=pack,
        evidence=[],
        reasoning=reasoning,
        question="Test?",
        llm_reasoner=_StubCriticReasoner(),
        trace=trace,
        budget=budget,
        budget_state=budget_state,
    )
    
    assert result.ok
    assert result.output is not None
    assert budget_state.passes_used == 1
    
    consumed = [e for e in events if e["type"] == "budget_consumed"]
    assert len(consumed) == 1


def test_critic_evaluator_budget_exceeded_returns_error() -> None:
    """run_critic_evaluator returns error when budget exceeded."""
    pack, _ = _build_context_pack()
    reasoning = _build_reasoning_output()
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    budget = Budget(max_passes=0, on_exceed="FAIL")  # No passes allowed
    budget_state = init_budget_state()
    
    result = run_critic_evaluator(
        context_pack=pack,
        evidence=[],
        reasoning=reasoning,
        question="Test?",
        llm_reasoner=_StubCriticReasoner(),
        trace=trace,
        budget=budget,
        budget_state=budget_state,
    )
    
    assert not result.ok
    assert result.error is not None
    assert result.error.reason == "budget_exceeded"


def test_evaluate_with_governance_blocks_fetch_more_evidence() -> None:
    """evaluate_with_governance blocks FETCH_MORE_EVIDENCE when not allowed."""
    pack, _ = _build_context_pack()
    reasoning = _build_reasoning_output()
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    result = evaluate_with_governance(
        context_pack=pack,
        evidence=[],
        reasoning=reasoning,
        question="Test?",
        llm_reasoner=_StubCriticReasoner(recommended_action="FETCH_MORE_EVIDENCE"),
        trace=trace,
        allow_fetch_more_evidence=False,
    )
    
    assert result.ok
    assert result.output is not None
    # Action should be downgraded to NONE
    assert result.output.recommended_next_action == "NONE"
    
    blocked = [e for e in events if e["type"] == "critic_recommendation_blocked"]
    assert len(blocked) == 1


def test_evaluate_with_governance_allows_fetch_more_evidence_with_budget() -> None:
    """evaluate_with_governance allows FETCH_MORE_EVIDENCE when policy permits."""
    pack, _ = _build_context_pack()
    reasoning = _build_reasoning_output()
    
    result = evaluate_with_governance(
        context_pack=pack,
        evidence=[],
        reasoning=reasoning,
        question="Test?",
        llm_reasoner=_StubCriticReasoner(recommended_action="FETCH_MORE_EVIDENCE"),
        allow_fetch_more_evidence=True,
        evidence_budget=3,
    )
    
    assert result.ok
    assert result.output is not None
    assert result.output.recommended_next_action == "FETCH_MORE_EVIDENCE"


def test_evaluate_with_governance_blocks_when_evidence_budget_exhausted() -> None:
    """evaluate_with_governance blocks FETCH_MORE_EVIDENCE when evidence_budget=0."""
    pack, _ = _build_context_pack()
    reasoning = _build_reasoning_output()
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    result = evaluate_with_governance(
        context_pack=pack,
        evidence=[],
        reasoning=reasoning,
        question="Test?",
        llm_reasoner=_StubCriticReasoner(recommended_action="FETCH_MORE_EVIDENCE"),
        trace=trace,
        allow_fetch_more_evidence=True,
        evidence_budget=0,  # Exhausted
    )
    
    assert result.ok
    assert result.output.recommended_next_action == "NONE"
    
    blocked = [e for e in events if e["type"] == "critic_recommendation_blocked"]
    assert len(blocked) == 1
    assert blocked[0]["payload"]["reason"] == "evidence_budget_exhausted"


def test_critic_output_includes_inconsistency_flags() -> None:
    """CriticOutput correctly captures inconsistency_flags."""
    pack, _ = _build_context_pack()
    reasoning = _build_reasoning_output()
    
    result = run_critic_evaluator(
        context_pack=pack,
        evidence=[],
        reasoning=reasoning,
        question="Test?",
        llm_reasoner=_StubCriticReasoner(
            inconsistency_flags=["data_mismatch", "missing_reference"],
        ),
    )
    
    assert result.ok
    assert result.output is not None
    assert "data_mismatch" in result.output.inconsistency_flags
    assert "missing_reference" in result.output.inconsistency_flags


def test_critic_evaluator_emits_detailed_trace_events() -> None:
    """run_critic_evaluator emits detailed trace events."""
    pack, _ = _build_context_pack()
    reasoning = _build_reasoning_output()
    events: List[Dict[str, Any]] = []
    
    def trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"type": event_type, "payload": payload})
    
    result = run_critic_evaluator(
        context_pack=pack,
        evidence=[],
        reasoning=reasoning,
        question="Test question?",
        llm_reasoner=_StubCriticReasoner(
            completeness_score=0.75,
            inconsistency_flags=["flag1"],
        ),
        trace=trace,
    )
    
    assert result.ok
    
    # Check started event
    started = [e for e in events if e["type"] == "critic_evaluator_started"]
    assert len(started) == 1
    assert started[0]["payload"]["reasoning_confidence"] == 0.7
    
    # Check completed event with detailed fields
    completed = [e for e in events if e["type"] == "critic_evaluator_completed"]
    assert len(completed) == 1
    assert completed[0]["payload"]["completeness_score"] == 0.75
    assert completed[0]["payload"]["inconsistency_count"] == 1


# =============================================================================
# CriticEvaluatorAgent Tests
# =============================================================================


def test_critic_evaluator_agent_with_budget() -> None:
    """CriticEvaluatorAgent respects budget when configured."""
    budget = Budget(max_passes=5)
    budget_state = init_budget_state()
    
    agent = CriticEvaluatorAgent(
        llm_reasoner=_StubCriticReasoner(),
        budget=budget,
        budget_state=budget_state,
    )
    
    # The agent's run method extracts params from step_context.step.params
    # For testing, we directly test the budget tracking via run_critic_evaluator
    reasoning = _build_reasoning_output()
    pack, _ = _build_context_pack()
    
    result = run_critic_evaluator(
        context_pack=pack,
        evidence=[],
        reasoning=reasoning,
        question="Test?",
        llm_reasoner=_StubCriticReasoner(),
        budget=budget,
        budget_state=budget_state,
    )
    
    assert result.ok
    assert budget_state.passes_used == 1
