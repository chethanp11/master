"""
Unit tests for IMP-032: Confidence Gate at Semantic Phase Exit.

Tests:
- ORC-SEM-CONF-GATE-001: Confidence gate invoked after semantic phase
- ORC-SEM-CONF-GATE-002: Gate returns ConfidenceGateDecision with structured fields
- ORC-SEM-CONF-GATE-003: Low confidence triggers proceed=False
- ORC-SEM-CONF-GATE-004: Entity confidence failures tracked
- ORC-SEM-CONF-GATE-005: Threshold configurable via settings
- ORC-SEM-CONF-GATE-006: bypass_allowed always False
- ORC-SEM-CONF-GATE-007: CONFIDENCE_GATE_EVALUATED trace event type exists
- ORC-SEM-CONF-GATE-008: Decision converts to trace payload
"""

import pytest
from typing import List, Optional

from core.governance.hooks import (
    check_semantic_confidence,
    check_semantic_confidence_legacy,
    ConfidenceGateDecision,
)
from core.contracts.semantic_schema import SemanticEnvelope, Entity
from core.config.schema import Settings
from core.memory.tracing import TraceEventType


# ==============================
# Fixtures
# ==============================

def create_envelope(
    confidence: float = 0.8,
    entities: Optional[List[Entity]] = None,
) -> SemanticEnvelope:
    """Create a SemanticEnvelope with specified confidence."""
    if entities is None:
        entities = []
    return SemanticEnvelope(
        raw_input="test input",
        normalized_input="test input",
        product_id="test_product",
        intent_type="query",
        intent="test_intent",
        entities=entities,
        confidence=confidence,
        ambiguities=[],
    )


def create_entity(name: str, confidence: float = 0.8) -> Entity:
    """Create an Entity with specified confidence."""
    return Entity(
        name=name,
        type="test_type",
        value="test_value",
        confidence=confidence,
    )


# ==============================
# ORC-SEM-CONF-GATE-001: Gate returns ConfidenceGateDecision
# ==============================

class TestConfidenceGateDecision:
    """Test that gate returns structured ConfidenceGateDecision."""
    
    def test_returns_confidence_gate_decision(self):
        """check_semantic_confidence returns ConfidenceGateDecision."""
        envelope = create_envelope(confidence=0.8)
        decision = check_semantic_confidence(envelope)
        assert isinstance(decision, ConfidenceGateDecision)
    
    def test_decision_has_all_required_fields(self):
        """ConfidenceGateDecision has all required fields."""
        envelope = create_envelope(confidence=0.8)
        decision = check_semantic_confidence(envelope)
        
        assert hasattr(decision, 'proceed')
        assert hasattr(decision, 'reason')
        assert hasattr(decision, 'effective_confidence')
        assert hasattr(decision, 'threshold')
        assert hasattr(decision, 'entity_threshold')
        assert hasattr(decision, 'failing_entities')
        assert hasattr(decision, 'bypass_allowed')
    
    def test_decision_is_frozen(self):
        """ConfidenceGateDecision is immutable."""
        decision = ConfidenceGateDecision(
            proceed=True,
            reason="test",
            effective_confidence=0.8,
            threshold=0.7,
            entity_threshold=0.5,
            failing_entities=[],
            bypass_allowed=False,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            decision.proceed = False  # type: ignore


# ==============================
# ORC-SEM-CONF-GATE-002: Proceed on high confidence
# ==============================

class TestConfidenceGateProceed:
    """Test that high confidence results in proceed=True."""
    
    def test_high_confidence_proceeds(self):
        """Envelope with confidence above threshold proceeds."""
        envelope = create_envelope(confidence=0.8)
        decision = check_semantic_confidence(envelope, threshold=0.7)
        
        assert decision.proceed is True
        assert decision.effective_confidence == 0.8
        assert decision.threshold == 0.7
    
    def test_exact_threshold_proceeds(self):
        """Envelope with confidence exactly at threshold proceeds."""
        envelope = create_envelope(confidence=0.7)
        decision = check_semantic_confidence(envelope, threshold=0.7)
        
        assert decision.proceed is True
    
    def test_default_threshold_is_0_7(self):
        """Default threshold is 0.7."""
        envelope = create_envelope(confidence=0.75)
        decision = check_semantic_confidence(envelope)
        
        assert decision.threshold == 0.7
        assert decision.proceed is True


# ==============================
# ORC-SEM-CONF-GATE-003: Low confidence triggers pause
# ==============================

class TestConfidenceGatePause:
    """Test that low confidence results in proceed=False."""
    
    def test_low_confidence_pauses(self):
        """Envelope with confidence below threshold pauses."""
        envelope = create_envelope(confidence=0.5)
        decision = check_semantic_confidence(envelope, threshold=0.7)
        
        assert decision.proceed is False
        assert "Low confidence" in decision.reason
        assert decision.effective_confidence == 0.5
        assert decision.threshold == 0.7
    
    def test_just_below_threshold_pauses(self):
        """Envelope with confidence just below threshold pauses."""
        envelope = create_envelope(confidence=0.69)
        decision = check_semantic_confidence(envelope, threshold=0.7)
        
        assert decision.proceed is False


# ==============================
# ORC-SEM-CONF-GATE-004: Entity confidence failures
# ==============================

class TestEntityConfidenceFailures:
    """Test entity-level confidence checking."""
    
    def test_low_entity_confidence_pauses(self):
        """Low entity confidence triggers pause."""
        entities = [
            create_entity("entity1", confidence=0.8),
            create_entity("entity2", confidence=0.3),
        ]
        envelope = create_envelope(confidence=0.8, entities=entities)
        decision = check_semantic_confidence(envelope, entity_threshold=0.5)
        
        assert decision.proceed is False
        assert "entity2" in decision.failing_entities
        assert "entity1" not in decision.failing_entities
    
    def test_multiple_failing_entities_tracked(self):
        """Multiple failing entities are all tracked."""
        entities = [
            create_entity("entity1", confidence=0.3),
            create_entity("entity2", confidence=0.4),
            create_entity("entity3", confidence=0.8),
        ]
        envelope = create_envelope(confidence=0.8, entities=entities)
        decision = check_semantic_confidence(envelope, entity_threshold=0.5)
        
        assert decision.proceed is False
        assert len(decision.failing_entities) == 2
        assert "entity1" in decision.failing_entities
        assert "entity2" in decision.failing_entities
    
    def test_default_entity_threshold_is_0_5(self):
        """Default entity threshold is 0.5."""
        entities = [create_entity("entity1", confidence=0.6)]
        envelope = create_envelope(confidence=0.8, entities=entities)
        decision = check_semantic_confidence(envelope)
        
        assert decision.entity_threshold == 0.5
        assert decision.proceed is True
    
    def test_high_entity_confidence_proceeds(self):
        """All entities above threshold proceeds."""
        entities = [
            create_entity("entity1", confidence=0.8),
            create_entity("entity2", confidence=0.9),
        ]
        envelope = create_envelope(confidence=0.8, entities=entities)
        decision = check_semantic_confidence(envelope, entity_threshold=0.5)
        
        assert decision.proceed is True
        assert decision.failing_entities == []


# ==============================
# ORC-SEM-CONF-GATE-005: Threshold from settings
# ==============================

class TestThresholdFromSettings:
    """Test threshold configuration via Settings."""
    
    def test_threshold_from_settings(self):
        """Threshold can be configured via Settings."""
        settings = Settings()
        settings.policies.semantic_confidence_threshold = 0.9
        
        envelope = create_envelope(confidence=0.85)
        decision = check_semantic_confidence(envelope, settings=settings)
        
        assert decision.threshold == 0.9
        assert decision.proceed is False
    
    def test_entity_threshold_from_settings(self):
        """Entity threshold can be configured via Settings."""
        settings = Settings()
        settings.policies.semantic_entity_confidence_threshold = 0.8
        
        entities = [create_entity("entity1", confidence=0.7)]
        envelope = create_envelope(confidence=0.9, entities=entities)
        decision = check_semantic_confidence(envelope, settings=settings)
        
        assert decision.entity_threshold == 0.8
        assert decision.proceed is False
    
    def test_explicit_threshold_overrides_settings(self):
        """Explicit threshold parameter overrides settings."""
        settings = Settings()
        settings.policies.semantic_confidence_threshold = 0.9
        
        envelope = create_envelope(confidence=0.75)
        decision = check_semantic_confidence(
            envelope, 
            threshold=0.7, 
            settings=settings,
        )
        
        assert decision.threshold == 0.7
        assert decision.proceed is True


# ==============================
# ORC-SEM-CONF-GATE-006: Bypass always False
# ==============================

class TestBypassAlwaysFalse:
    """Test that bypass_allowed is always False."""
    
    def test_bypass_allowed_always_false(self):
        """bypass_allowed is always False in decision."""
        envelope = create_envelope(confidence=0.8)
        decision = check_semantic_confidence(envelope)
        
        assert decision.bypass_allowed is False
    
    def test_bypass_parameter_ignored(self):
        """bypass_allowed parameter is ignored - gate cannot be bypassed."""
        envelope = create_envelope(confidence=0.8)
        
        # Even if True is passed, it should be False in the result
        decision = check_semantic_confidence(envelope, bypass_allowed=True)
        
        assert decision.bypass_allowed is False
    
    def test_low_confidence_cannot_be_bypassed(self):
        """Low confidence cannot be bypassed even with bypass_allowed=True."""
        envelope = create_envelope(confidence=0.5)
        decision = check_semantic_confidence(
            envelope, 
            threshold=0.7, 
            bypass_allowed=True,
        )
        
        assert decision.proceed is False
        assert decision.bypass_allowed is False


# ==============================
# ORC-SEM-CONF-GATE-007: Trace event type exists
# ==============================

class TestTraceEventType:
    """Test CONFIDENCE_GATE_EVALUATED trace event type."""
    
    def test_confidence_gate_evaluated_event_type_exists(self):
        """CONFIDENCE_GATE_EVALUATED trace event type exists."""
        assert hasattr(TraceEventType, 'CONFIDENCE_GATE_EVALUATED')
        assert TraceEventType.CONFIDENCE_GATE_EVALUATED.value == "confidence_gate_evaluated"


# ==============================
# ORC-SEM-CONF-GATE-008: Decision converts to trace payload
# ==============================

class TestTracePayloadConversion:
    """Test decision.to_trace_payload() conversion."""
    
    def test_to_trace_payload_structure(self):
        """to_trace_payload returns expected structure."""
        envelope = create_envelope(confidence=0.8)
        decision = check_semantic_confidence(envelope, threshold=0.7)
        
        payload = decision.to_trace_payload()
        
        assert payload["proceed"] is True
        assert payload["reason"] == "Confidence threshold passed"
        assert payload["effective_confidence"] == 0.8
        assert payload["threshold"] == 0.7
        assert payload["bypass_allowed"] is False
        assert payload["decision"] == "proceed"
    
    def test_to_trace_payload_on_pause(self):
        """to_trace_payload correctly shows pause decision."""
        envelope = create_envelope(confidence=0.5)
        decision = check_semantic_confidence(envelope, threshold=0.7)
        
        payload = decision.to_trace_payload()
        
        assert payload["proceed"] is False
        assert payload["decision"] == "pause"
    
    def test_to_trace_payload_includes_failing_entities(self):
        """to_trace_payload includes failing_entities."""
        entities = [create_entity("bad_entity", confidence=0.3)]
        envelope = create_envelope(confidence=0.8, entities=entities)
        decision = check_semantic_confidence(envelope, entity_threshold=0.5)
        
        payload = decision.to_trace_payload()
        
        assert "bad_entity" in payload["failing_entities"]


# ==============================
# Legacy compatibility
# ==============================

class TestLegacyCompatibility:
    """Test legacy tuple-based function still works."""
    
    def test_legacy_returns_tuple(self):
        """Legacy function returns (bool, Optional[str]) tuple."""
        envelope = create_envelope(confidence=0.8)
        result = check_semantic_confidence_legacy(envelope)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is True
        assert result[1] is None
    
    def test_legacy_low_confidence(self):
        """Legacy function returns reason on low confidence."""
        envelope = create_envelope(confidence=0.5)
        passed, reason = check_semantic_confidence_legacy(envelope, threshold=0.7)
        
        assert passed is False
        assert reason is not None
        assert "Low confidence" in reason
