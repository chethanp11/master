"""
Unit tests for IMP-035: Intent Sufficiency Gate.

Tests:
- ORC-SUFF-GATE-001: IntentSufficiencyGate class exists
- ORC-SUFF-GATE-002: Gate checks gaps.count == 0 or all gaps non-blocking
- ORC-SUFF-GATE-003: Gate evaluated before tool selection
- ORC-SUFF-GATE-004: Blocking gaps prevent execution
- ORC-SUFF-GATE-005: Non-blocking gaps allow execution
- ORC-SUFF-GATE-006: Trace events emitted
- ORC-SUFF-GATE-007: Decision converts to trace payload
- ORC-SUFF-GATE-008: Extended check with unknowns
"""

import pytest
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

from core.governance.gates import (
    IntentSufficiencyGate,
    SufficiencyGateDecision,
    GateContext,
)
from core.contracts.sufficiency_schema import (
    SufficiencyState,
    Gap,
    Unknown,
    Fact,
    Priority,
    Importance,
)
from core.memory.tracing import TraceEventType


# ==============================
# Fixtures
# ==============================

def create_gap(description: str, blocking: bool = False) -> Gap:
    """Create a Gap with specified blocking status."""
    return Gap(
        description=description,
        priority=Priority.MEDIUM,
        blocking=blocking,
    )


def create_unknown(question: str, blocking: bool = False) -> Unknown:
    """Create an Unknown with specified blocking status."""
    return Unknown(
        question=question,
        importance=Importance.MEDIUM,
        blocking=blocking,
    )


def create_state(
    run_id: str = "test-run",
    gaps: Optional[List[Gap]] = None,
    unknowns: Optional[List[Unknown]] = None,
) -> SufficiencyState:
    """Create a SufficiencyState for testing."""
    return SufficiencyState(
        run_id=run_id,
        gaps=gaps or [],
        unknowns=unknowns or [],
    )


# ==============================
# ORC-SUFF-GATE-001: Gate class exists
# ==============================

class TestIntentSufficiencyGateExists:
    """Test that IntentSufficiencyGate class exists and has correct interface."""
    
    def test_gate_class_exists(self):
        """IntentSufficiencyGate class exists."""
        gate = IntentSufficiencyGate()
        assert gate is not None
    
    def test_gate_has_name(self):
        """Gate has correct name."""
        gate = IntentSufficiencyGate()
        assert gate.name == "intent_sufficiency"
    
    def test_gate_has_check_sufficiency_method(self):
        """Gate has check_sufficiency method."""
        gate = IntentSufficiencyGate()
        assert hasattr(gate, 'check_sufficiency')
    
    def test_gate_has_evaluate_method(self):
        """Gate has evaluate method (from BaseGate)."""
        gate = IntentSufficiencyGate()
        assert hasattr(gate, 'evaluate')


# ==============================
# ORC-SUFF-GATE-002: Gap checking logic
# ==============================

class TestGapChecking:
    """Test that gate correctly checks gap count and blocking status."""
    
    def test_no_gaps_proceeds(self):
        """State with no gaps proceeds."""
        gate = IntentSufficiencyGate()
        state = create_state(gaps=[])
        
        decision = gate.check_sufficiency(state)
        
        assert decision.proceed is True
        assert decision.gap_count == 0
        assert decision.is_sufficient is True
    
    def test_non_blocking_gaps_proceed(self):
        """State with only non-blocking gaps proceeds."""
        gate = IntentSufficiencyGate()
        gaps = [
            create_gap("Non-blocking gap 1", blocking=False),
            create_gap("Non-blocking gap 2", blocking=False),
        ]
        state = create_state(gaps=gaps)
        
        decision = gate.check_sufficiency(state)
        
        assert decision.proceed is True
        assert decision.gap_count == 2
        assert decision.blocking_gap_count == 0
        assert decision.is_sufficient is True
    
    def test_blocking_gap_blocks(self):
        """State with blocking gap does not proceed."""
        gate = IntentSufficiencyGate()
        gaps = [
            create_gap("Blocking gap", blocking=True),
        ]
        state = create_state(gaps=gaps)
        
        decision = gate.check_sufficiency(state)
        
        assert decision.proceed is False
        assert decision.gap_count == 1
        assert decision.blocking_gap_count == 1
        assert decision.is_sufficient is False
    
    def test_mixed_gaps_blocks_on_blocking(self):
        """State with mixed gaps blocks on blocking ones."""
        gate = IntentSufficiencyGate()
        gaps = [
            create_gap("Non-blocking", blocking=False),
            create_gap("Blocking gap", blocking=True),
            create_gap("Another non-blocking", blocking=False),
        ]
        state = create_state(gaps=gaps)
        
        decision = gate.check_sufficiency(state)
        
        assert decision.proceed is False
        assert decision.gap_count == 3
        assert decision.blocking_gap_count == 1
        assert "Blocking gap" in decision.blocking_gaps


# ==============================
# ORC-SUFF-GATE-003: Gate evaluation interface
# ==============================

class TestGateEvaluation:
    """Test gate evaluation via GateContext."""
    
    def test_evaluate_with_sufficient_state(self):
        """Evaluate returns success for sufficient state."""
        gate = IntentSufficiencyGate()
        state = create_state(gaps=[])
        context = GateContext(extra={"sufficiency_state": state})
        
        result = gate.evaluate(context)
        
        assert result.allowed is True
        assert result.gate_name == "intent_sufficiency"
    
    def test_evaluate_with_blocking_gaps(self):
        """Evaluate returns failure for blocking gaps."""
        gate = IntentSufficiencyGate()
        gaps = [create_gap("Blocking", blocking=True)]
        state = create_state(gaps=gaps)
        context = GateContext(extra={"sufficiency_state": state})
        
        result = gate.evaluate(context)
        
        assert result.allowed is False
        assert result.reason == "sufficiency_gate_blocked"
        assert len(result.errors) > 0
    
    def test_evaluate_without_state_fails(self):
        """Evaluate fails when no sufficiency state provided."""
        gate = IntentSufficiencyGate()
        context = GateContext(extra={})
        
        result = gate.evaluate(context)
        
        assert result.allowed is False
        assert "no_sufficiency_state" in result.reason
    
    def test_evaluate_with_invalid_state_fails(self):
        """Evaluate fails when invalid state provided."""
        gate = IntentSufficiencyGate()
        context = GateContext(extra={"sufficiency_state": "not a state"})
        
        result = gate.evaluate(context)
        
        assert result.allowed is False
        assert "invalid_sufficiency_state" in result.reason


# ==============================
# ORC-SUFF-GATE-004: Blocking prevents execution
# ==============================

class TestBlockingPreventsExecution:
    """Test that blocking gaps prevent execution."""
    
    def test_single_blocking_gap_blocks(self):
        """Single blocking gap prevents execution."""
        gate = IntentSufficiencyGate()
        gaps = [create_gap("Critical missing info", blocking=True)]
        state = create_state(gaps=gaps)
        
        decision = gate.check_sufficiency(state)
        
        assert decision.proceed is False
        assert "Critical missing info" in decision.blocking_gaps
    
    def test_multiple_blocking_gaps_all_reported(self):
        """Multiple blocking gaps are all reported."""
        gate = IntentSufficiencyGate()
        gaps = [
            create_gap("Gap 1", blocking=True),
            create_gap("Gap 2", blocking=True),
            create_gap("Gap 3", blocking=True),
        ]
        state = create_state(gaps=gaps)
        
        decision = gate.check_sufficiency(state)
        
        assert decision.proceed is False
        assert decision.blocking_gap_count == 3
        assert len(decision.blocking_gaps) == 3
    
    def test_reason_mentions_gap_count(self):
        """Reason message mentions blocking gap count."""
        gate = IntentSufficiencyGate()
        gaps = [create_gap("Blocking", blocking=True)]
        state = create_state(gaps=gaps)
        
        decision = gate.check_sufficiency(state)
        
        assert "1 blocking gap" in decision.reason


# ==============================
# ORC-SUFF-GATE-005: Non-blocking allows execution
# ==============================

class TestNonBlockingAllowsExecution:
    """Test that non-blocking gaps allow execution."""
    
    def test_non_blocking_gaps_allow_proceed(self):
        """Non-blocking gaps still allow proceeding."""
        gate = IntentSufficiencyGate()
        gaps = [
            create_gap("Minor gap 1", blocking=False),
            create_gap("Minor gap 2", blocking=False),
        ]
        state = create_state(gaps=gaps)
        
        decision = gate.check_sufficiency(state)
        
        assert decision.proceed is True
        assert decision.gap_count == 2
        assert decision.blocking_gaps == []


# ==============================
# ORC-SUFF-GATE-006: Trace events emitted
# ==============================

class TestTraceEventEmission:
    """Test trace event emission."""
    
    def test_emit_evaluation_event(self):
        """Gate emits sufficiency_gate_evaluated event."""
        events = []
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append((event_type, payload))
        
        gate = IntentSufficiencyGate(emit_event_fn=capture_event)
        state = create_state(gaps=[])
        
        gate.check_sufficiency(state)
        
        event_types = [e[0] for e in events]
        assert "sufficiency_gate_evaluated" in event_types
    
    def test_emit_blocked_event_on_failure(self):
        """Gate emits sufficiency_gate_blocked event when blocked."""
        events = []
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append((event_type, payload))
        
        gate = IntentSufficiencyGate(emit_event_fn=capture_event)
        gaps = [create_gap("Blocking", blocking=True)]
        state = create_state(gaps=gaps)
        
        gate.check_sufficiency(state)
        
        event_types = [e[0] for e in events]
        assert "sufficiency_gate_blocked" in event_types
    
    def test_blocked_event_includes_gap_info(self):
        """Blocked event includes gap information."""
        events = []
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append((event_type, payload))
        
        gate = IntentSufficiencyGate(emit_event_fn=capture_event)
        gaps = [create_gap("My blocking gap", blocking=True)]
        state = create_state(gaps=gaps)
        
        gate.check_sufficiency(state)
        
        blocked_events = [e for e in events if e[0] == "sufficiency_gate_blocked"]
        assert len(blocked_events) == 1
        payload = blocked_events[0][1]
        assert payload["blocking_gap_count"] == 1
        assert "My blocking gap" in payload["blocking_gaps"]
    
    def test_trace_event_types_exist(self):
        """Trace event types exist in TraceEventType enum."""
        assert hasattr(TraceEventType, 'SUFFICIENCY_GATE_EVALUATED')
        assert hasattr(TraceEventType, 'SUFFICIENCY_GATE_BLOCKED')
        assert TraceEventType.SUFFICIENCY_GATE_EVALUATED.value == "sufficiency_gate_evaluated"
        assert TraceEventType.SUFFICIENCY_GATE_BLOCKED.value == "sufficiency_gate_blocked"


# ==============================
# ORC-SUFF-GATE-007: Decision to trace payload
# ==============================

class TestDecisionTracePayload:
    """Test SufficiencyGateDecision.to_trace_payload()."""
    
    def test_to_trace_payload_structure(self):
        """to_trace_payload returns expected structure."""
        decision = SufficiencyGateDecision(
            proceed=True,
            reason="All good",
            gap_count=0,
            blocking_gap_count=0,
            blocking_gaps=[],
            is_sufficient=True,
        )
        
        payload = decision.to_trace_payload()
        
        assert payload["proceed"] is True
        assert payload["reason"] == "All good"
        assert payload["gap_count"] == 0
        assert payload["blocking_gap_count"] == 0
        assert payload["blocking_gaps"] == []
        assert payload["is_sufficient"] is True
        assert payload["decision"] == "proceed"
    
    def test_to_trace_payload_on_block(self):
        """to_trace_payload shows blocked decision correctly."""
        decision = SufficiencyGateDecision(
            proceed=False,
            reason="Blocked by gaps",
            gap_count=2,
            blocking_gap_count=1,
            blocking_gaps=["Critical gap"],
            is_sufficient=False,
        )
        
        payload = decision.to_trace_payload()
        
        assert payload["proceed"] is False
        assert payload["decision"] == "blocked"
        assert payload["blocking_gaps"] == ["Critical gap"]
    
    def test_decision_is_frozen(self):
        """SufficiencyGateDecision is immutable."""
        decision = SufficiencyGateDecision(
            proceed=True,
            reason="test",
            gap_count=0,
            blocking_gap_count=0,
            blocking_gaps=[],
            is_sufficient=True,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            decision.proceed = False  # type: ignore


# ==============================
# ORC-SUFF-GATE-008: Extended check with unknowns
# ==============================

class TestExtendedCheckWithUnknowns:
    """Test check_sufficiency_with_unknowns method."""
    
    def test_without_unknowns_flag_ignores_blocking_unknowns(self):
        """Without flag, blocking unknowns are ignored."""
        gate = IntentSufficiencyGate()
        unknowns = [create_unknown("Blocking question", blocking=True)]
        state = create_state(unknowns=unknowns)
        
        decision = gate.check_sufficiency_with_unknowns(
            state, 
            include_blocking_unknowns=False,
        )
        
        assert decision.proceed is True
    
    def test_with_unknowns_flag_blocks_on_unknowns(self):
        """With flag, blocking unknowns cause blocking."""
        gate = IntentSufficiencyGate()
        unknowns = [create_unknown("Blocking question", blocking=True)]
        state = create_state(unknowns=unknowns)
        
        decision = gate.check_sufficiency_with_unknowns(
            state, 
            include_blocking_unknowns=True,
        )
        
        assert decision.proceed is False
        assert "Blocking question" in decision.blocking_gaps
    
    def test_non_blocking_unknowns_allow_proceed(self):
        """Non-blocking unknowns allow proceeding even with flag."""
        gate = IntentSufficiencyGate()
        unknowns = [create_unknown("Non-blocking question", blocking=False)]
        state = create_state(unknowns=unknowns)
        
        decision = gate.check_sufficiency_with_unknowns(
            state, 
            include_blocking_unknowns=True,
        )
        
        assert decision.proceed is True
    
    def test_combined_gaps_and_unknowns(self):
        """Blocking gaps and unknowns are combined."""
        gate = IntentSufficiencyGate()
        gaps = [create_gap("Blocking gap", blocking=True)]
        unknowns = [create_unknown("Blocking unknown", blocking=True)]
        state = create_state(gaps=gaps, unknowns=unknowns)
        
        decision = gate.check_sufficiency_with_unknowns(
            state, 
            include_blocking_unknowns=True,
        )
        
        assert decision.proceed is False
        assert "Blocking gap" in decision.blocking_gaps
        # Note: blocking_gaps includes both gaps and unknowns
