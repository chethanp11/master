"""
Unit tests for IMP-049: Semantic Gate Implementation.

Tests:
- GOV-GATE-SEM-001: SemanticGate class exists
- GOV-GATE-SEM-002: Envelope completeness validated
- GOV-GATE-SEM-003: Confidence threshold validated
- GOV-GATE-SEM-004: Intent sufficiency validated
- GOV-GATE-SEM-005: SemanticGateResult has all fields
- GOV-GATE-SEM-006: Gate evaluation via GateContext
- GOV-GATE-SEM-007: Trace events emitted
- GOV-GATE-SEM-008: Combined validation logic
"""

import pytest
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

from core.governance.semantic_gate import (
    SemanticGate,
    SemanticGateResult,
    create_semantic_gate,
)
from core.governance.gates import GateContext
from core.contracts.semantic_schema import SemanticEnvelope, Entity, Ambiguity
from core.contracts.sufficiency_schema import (
    SufficiencyState,
    Gap,
    Unknown,
    Priority,
    Importance,
)
from core.memory.tracing import TraceEventType


# ==============================
# Fixtures
# ==============================

def create_envelope(
    confidence: float = 0.8,
    raw_input: str = "test input",
    entities: Optional[List[Entity]] = None,
    ambiguities: Optional[List[Ambiguity]] = None,
) -> SemanticEnvelope:
    """Create a SemanticEnvelope for testing."""
    return SemanticEnvelope(
        raw_input=raw_input,
        normalized_input=raw_input,
        product_id="test_product",
        intent_type="query",
        entities=entities or [],
        confidence=confidence,
        ambiguities=ambiguities or [],
    )


def create_entity(name: str, confidence: float = 0.8) -> Entity:
    """Create an Entity with specified confidence."""
    return Entity(
        name=name,
        type="test_type",
        value="test_value",
        confidence=confidence,
    )


def create_ambiguity(
    ambiguity_id: str,
    blocking: bool = False,
    resolved: bool = False,
) -> Ambiguity:
    """Create an Ambiguity for testing."""
    return Ambiguity(
        ambiguity_id=ambiguity_id,
        description="Test ambiguity",
        options=["option1", "option2"],
        is_blocking=blocking,
        resolution_method="manual" if resolved else None,
        selected_option="option1" if resolved else None,
    )


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
# GOV-GATE-SEM-001: Gate class exists
# ==============================

class TestSemanticGateExists:
    """Test that SemanticGate class exists and has correct interface."""
    
    def test_gate_class_exists(self):
        """SemanticGate class exists."""
        gate = SemanticGate()
        assert gate is not None
    
    def test_gate_has_name(self):
        """Gate has correct name."""
        gate = SemanticGate()
        assert gate.name == "semantic"
    
    def test_gate_has_validate_method(self):
        """Gate has validate method."""
        gate = SemanticGate()
        assert hasattr(gate, 'validate')
    
    def test_gate_has_evaluate_method(self):
        """Gate has evaluate method (from BaseGate)."""
        gate = SemanticGate()
        assert hasattr(gate, 'evaluate')
    
    def test_factory_function_works(self):
        """create_semantic_gate factory function works."""
        gate = create_semantic_gate(confidence_threshold=0.8)
        assert gate._default_confidence_threshold == 0.8


# ==============================
# GOV-GATE-SEM-002: Envelope completeness
# ==============================

class TestEnvelopeCompleteness:
    """Test envelope completeness validation."""
    
    def test_complete_envelope_passes(self):
        """Complete envelope passes validation."""
        gate = SemanticGate()
        envelope = create_envelope()
        
        complete, errors = gate.validate_envelope_completeness(envelope)
        
        assert complete is True
        assert errors == []
    
    def test_empty_raw_input_fails(self):
        """Empty raw_input fails validation."""
        gate = SemanticGate()
        envelope = create_envelope(raw_input="")
        
        complete, errors = gate.validate_envelope_completeness(envelope)
        
        assert complete is False
        assert any("raw_input" in e for e in errors)
    
    def test_blocking_unresolved_ambiguity_fails(self):
        """Blocking unresolved ambiguity fails validation."""
        gate = SemanticGate()
        ambiguities = [create_ambiguity("amb1", blocking=True, resolved=False)]
        envelope = create_envelope(ambiguities=ambiguities)
        
        complete, errors = gate.validate_envelope_completeness(envelope)
        
        assert complete is False
        assert any("ambiguities" in e for e in errors)
    
    def test_resolved_blocking_ambiguity_passes(self):
        """Resolved blocking ambiguity passes validation."""
        gate = SemanticGate()
        ambiguities = [create_ambiguity("amb1", blocking=True, resolved=True)]
        envelope = create_envelope(ambiguities=ambiguities)
        
        complete, errors = gate.validate_envelope_completeness(envelope)
        
        assert complete is True


# ==============================
# GOV-GATE-SEM-003: Confidence threshold
# ==============================

class TestConfidenceThreshold:
    """Test confidence threshold validation."""
    
    def test_high_confidence_passes(self):
        """High confidence passes threshold."""
        gate = SemanticGate()
        envelope = create_envelope(confidence=0.9)
        
        passed, errors = gate.validate_confidence_threshold(
            envelope, 
            threshold=0.7,
        )
        
        assert passed is True
        assert errors == []
    
    def test_low_confidence_fails(self):
        """Low confidence fails threshold."""
        gate = SemanticGate()
        envelope = create_envelope(confidence=0.5)
        
        passed, errors = gate.validate_confidence_threshold(
            envelope, 
            threshold=0.7,
        )
        
        assert passed is False
        assert any("Confidence" in e for e in errors)
    
    def test_low_entity_confidence_fails(self):
        """Low entity confidence fails threshold."""
        gate = SemanticGate()
        entities = [create_entity("low_entity", confidence=0.3)]
        envelope = create_envelope(confidence=0.9, entities=entities)
        
        passed, errors = gate.validate_confidence_threshold(
            envelope, 
            threshold=0.7,
            entity_threshold=0.5,
        )
        
        assert passed is False
        assert any("low_entity" in e for e in errors)
    
    def test_custom_thresholds_respected(self):
        """Custom thresholds are respected."""
        gate = SemanticGate()
        envelope = create_envelope(confidence=0.85)
        
        # Should fail at 0.9 threshold
        passed1, _ = gate.validate_confidence_threshold(
            envelope, 
            threshold=0.9,
        )
        
        # Should pass at 0.8 threshold
        passed2, _ = gate.validate_confidence_threshold(
            envelope, 
            threshold=0.8,
        )
        
        assert passed1 is False
        assert passed2 is True


# ==============================
# GOV-GATE-SEM-004: Intent sufficiency
# ==============================

class TestIntentSufficiency:
    """Test intent sufficiency validation."""
    
    def test_no_gaps_passes(self):
        """No gaps passes sufficiency check."""
        gate = SemanticGate()
        envelope = create_envelope()
        state = create_state(gaps=[])
        
        passed, errors = gate.validate_intent_sufficiency(envelope, state)
        
        assert passed is True
        assert errors == []
    
    def test_blocking_gap_fails(self):
        """Blocking gap fails sufficiency check."""
        gate = SemanticGate()
        envelope = create_envelope()
        gaps = [create_gap("Critical info missing", blocking=True)]
        state = create_state(gaps=gaps)
        
        passed, errors = gate.validate_intent_sufficiency(envelope, state)
        
        assert passed is False
        assert any("Critical info missing" in e for e in errors)
    
    def test_blocking_unknown_fails(self):
        """Blocking unknown fails sufficiency check."""
        gate = SemanticGate()
        envelope = create_envelope()
        unknowns = [create_unknown("What is X?", blocking=True)]
        state = create_state(unknowns=unknowns)
        
        passed, errors = gate.validate_intent_sufficiency(envelope, state)
        
        assert passed is False
        assert any("What is X?" in e for e in errors)
    
    def test_non_blocking_gaps_pass(self):
        """Non-blocking gaps pass sufficiency check."""
        gate = SemanticGate()
        envelope = create_envelope()
        gaps = [create_gap("Minor gap", blocking=False)]
        state = create_state(gaps=gaps)
        
        passed, errors = gate.validate_intent_sufficiency(envelope, state)
        
        assert passed is True


# ==============================
# GOV-GATE-SEM-005: Result structure
# ==============================

class TestSemanticGateResult:
    """Test SemanticGateResult structure."""
    
    def test_result_has_all_fields(self):
        """SemanticGateResult has all required fields."""
        result = SemanticGateResult(
            proceed=True,
            envelope_complete=True,
            confidence_passed=True,
            sufficiency_passed=True,
            failures=[],
        )
        
        assert hasattr(result, 'proceed')
        assert hasattr(result, 'envelope_complete')
        assert hasattr(result, 'confidence_passed')
        assert hasattr(result, 'sufficiency_passed')
        assert hasattr(result, 'failures')
        assert hasattr(result, 'details')
    
    def test_result_is_frozen(self):
        """SemanticGateResult is immutable."""
        result = SemanticGateResult(
            proceed=True,
            envelope_complete=True,
            confidence_passed=True,
            sufficiency_passed=True,
            failures=[],
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            result.proceed = False  # type: ignore
    
    def test_to_trace_payload(self):
        """to_trace_payload returns correct structure."""
        result = SemanticGateResult(
            proceed=True,
            envelope_complete=True,
            confidence_passed=True,
            sufficiency_passed=True,
            failures=[],
            details={"test_key": "test_value"},
        )
        
        payload = result.to_trace_payload()
        
        assert payload["proceed"] is True
        assert payload["envelope_complete"] is True
        assert payload["decision"] == "proceed"
        assert payload["test_key"] == "test_value"
    
    def test_to_trace_payload_on_failure(self):
        """to_trace_payload shows rejection correctly."""
        result = SemanticGateResult(
            proceed=False,
            envelope_complete=True,
            confidence_passed=False,
            sufficiency_passed=True,
            failures=["Low confidence"],
        )
        
        payload = result.to_trace_payload()
        
        assert payload["proceed"] is False
        assert payload["decision"] == "rejected"
        assert payload["failure_count"] == 1


# ==============================
# GOV-GATE-SEM-006: Gate evaluation
# ==============================

class TestGateEvaluation:
    """Test gate evaluation via GateContext."""
    
    def test_evaluate_with_valid_envelope(self):
        """Evaluate returns success for valid envelope."""
        gate = SemanticGate()
        envelope = create_envelope(confidence=0.9)
        context = GateContext(extra={"envelope": envelope})
        
        result = gate.evaluate(context)
        
        assert result.allowed is True
        assert result.gate_name == "semantic"
    
    def test_evaluate_with_low_confidence(self):
        """Evaluate returns failure for low confidence."""
        gate = SemanticGate(default_confidence_threshold=0.9)
        envelope = create_envelope(confidence=0.5)
        context = GateContext(extra={"envelope": envelope})
        
        result = gate.evaluate(context)
        
        assert result.allowed is False
        assert result.reason == "semantic_gate_rejected"
    
    def test_evaluate_without_envelope_fails(self):
        """Evaluate fails when no envelope provided."""
        gate = SemanticGate()
        context = GateContext(extra={})
        
        result = gate.evaluate(context)
        
        assert result.allowed is False
        assert "no_envelope" in result.reason
    
    def test_evaluate_with_sufficiency_state(self):
        """Evaluate checks sufficiency when state provided."""
        gate = SemanticGate()
        envelope = create_envelope(confidence=0.9)
        gaps = [create_gap("Blocking", blocking=True)]
        state = create_state(gaps=gaps)
        context = GateContext(extra={
            "envelope": envelope,
            "sufficiency_state": state,
        })
        
        result = gate.evaluate(context)
        
        assert result.allowed is False


# ==============================
# GOV-GATE-SEM-007: Trace events
# ==============================

class TestTraceEvents:
    """Test trace event emission."""
    
    def test_emit_evaluated_event(self):
        """Gate emits semantic_gate_evaluated event."""
        events = []
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append((event_type, payload))
        
        gate = SemanticGate(emit_event_fn=capture_event)
        envelope = create_envelope()
        
        gate.validate(envelope)
        
        event_types = [e[0] for e in events]
        assert "semantic_gate_evaluated" in event_types
    
    def test_emit_rejected_event_on_failure(self):
        """Gate emits semantic_gate_rejected event when rejected."""
        events = []
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append((event_type, payload))
        
        gate = SemanticGate(
            default_confidence_threshold=0.9,
            emit_event_fn=capture_event,
        )
        envelope = create_envelope(confidence=0.5)
        
        gate.validate(envelope)
        
        event_types = [e[0] for e in events]
        assert "semantic_gate_rejected" in event_types
    
    def test_trace_event_types_exist(self):
        """Trace event types exist in TraceEventType enum."""
        assert hasattr(TraceEventType, 'SEMANTIC_GATE_EVALUATED')
        assert hasattr(TraceEventType, 'SEMANTIC_GATE_REJECTED')
        assert TraceEventType.SEMANTIC_GATE_EVALUATED.value == "semantic_gate_evaluated"
        assert TraceEventType.SEMANTIC_GATE_REJECTED.value == "semantic_gate_rejected"


# ==============================
# GOV-GATE-SEM-008: Combined validation
# ==============================

class TestCombinedValidation:
    """Test combined validation logic."""
    
    def test_all_pass_proceeds(self):
        """All validations passing results in proceed."""
        gate = SemanticGate()
        envelope = create_envelope(confidence=0.9)
        state = create_state()
        
        result = gate.validate(envelope, state)
        
        assert result.proceed is True
        assert result.envelope_complete is True
        assert result.confidence_passed is True
        assert result.sufficiency_passed is True
        assert result.failures == []
    
    def test_any_failure_rejects(self):
        """Any validation failure results in rejection."""
        gate = SemanticGate()
        envelope = create_envelope(confidence=0.5)  # Low confidence
        
        result = gate.validate(envelope, confidence_threshold=0.9)
        
        assert result.proceed is False
        assert result.confidence_passed is False
        assert len(result.failures) > 0
    
    def test_multiple_failures_collected(self):
        """Multiple failures are collected."""
        gate = SemanticGate()
        envelope = create_envelope(
            confidence=0.5, 
            raw_input="",  # Empty input
        )
        
        result = gate.validate(envelope, confidence_threshold=0.9)
        
        assert result.proceed is False
        assert result.envelope_complete is False
        assert result.confidence_passed is False
        assert len(result.failures) >= 2
    
    def test_sufficiency_skipped_when_no_state(self):
        """Sufficiency check skipped when no state provided."""
        gate = SemanticGate()
        envelope = create_envelope()
        
        result = gate.validate(envelope, sufficiency_state=None)
        
        assert result.sufficiency_passed is True
        assert result.details.get("sufficiency_skipped") is True
    
    def test_details_include_thresholds(self):
        """Result details include threshold values."""
        gate = SemanticGate()
        envelope = create_envelope()
        
        result = gate.validate(
            envelope, 
            confidence_threshold=0.8,
            entity_threshold=0.6,
        )
        
        assert result.details["confidence_threshold"] == 0.8
        assert result.details["entity_threshold"] == 0.6
        assert result.details["actual_confidence"] == envelope.confidence
