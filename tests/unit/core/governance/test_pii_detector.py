"""
Tests for IMP-044: Enhanced PII Detection (GOV-SEC-PII-001..005).

Verifies:
- PIIDetector pattern-based detection
- PIIDetector NER-based detection
- PIIEntity and PIIMatch models
- Trace event emission
- Redaction functionality
"""

import pytest
from typing import Any, Dict, List

from core.governance.pii_detector import (
    PIIDetectionResult,
    PIIDetector,
    PIIEntity,
    PIIEntityType,
    PIIMatch,
    PIISensitivity,
    create_pii_detector,
)
from core.memory.tracing import TraceEventType


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def detector() -> PIIDetector:
    return PIIDetector()


@pytest.fixture
def sample_text_with_pii() -> str:
    return """
    Contact John Smith at john.smith@example.com or call 555-123-4567.
    His SSN is 123-45-6789 and credit card is 4532015112830366.
    Office address: 192.168.1.100
    """


# ============================================================================
# GOV-SEC-PII-001: PIIEntity Tests
# ============================================================================


class TestPIIEntity:
    """Test PIIEntity model."""
    
    def test_entity_has_required_fields(self):
        """GOV-SEC-PII-001: Entity has required fields."""
        entity = PIIEntity(
            entity_type=PIIEntityType.EMAIL,
            value="test@example.com",
            span=(0, 16),
            confidence=0.95,
        )
        
        assert entity.entity_type == PIIEntityType.EMAIL
        assert entity.value == "test@example.com"
        assert entity.span == (0, 16)
        assert entity.confidence == 0.95
    
    def test_entity_is_frozen(self):
        """GOV-SEC-PII-001: Entity is immutable."""
        entity = PIIEntity(
            entity_type=PIIEntityType.EMAIL,
            value="test@example.com",
            span=(0, 16),
            confidence=0.95,
        )
        
        with pytest.raises(Exception):
            entity.value = "other@example.com"
    
    def test_entity_to_dict_redacts_value(self):
        """GOV-SEC-PII-001: to_dict does not expose actual value."""
        entity = PIIEntity(
            entity_type=PIIEntityType.SSN,
            value="123-45-6789",
            span=(0, 11),
            confidence=0.90,
            sensitivity=PIISensitivity.HIGH,
        )
        
        data = entity.to_dict()
        assert "value" not in data
        assert data["length"] == 11  # Length only
        assert data["entity_type"] == "SSN"
        assert data["sensitivity"] == "HIGH"


class TestPIIMatch:
    """Test PIIMatch model."""
    
    def test_match_to_entity(self):
        """GOV-SEC-PII-001: Match converts to entity."""
        match = PIIMatch(
            pattern_name="email",
            value="test@example.com",
            span=(0, 16),
            entity_type=PIIEntityType.EMAIL,
        )
        
        entity = match.to_entity(confidence=0.95)
        
        assert entity.entity_type == PIIEntityType.EMAIL
        assert entity.value == "test@example.com"
        assert entity.confidence == 0.95


# ============================================================================
# GOV-SEC-PII-002: Pattern Detection Tests
# ============================================================================


class TestPatternDetection:
    """Test pattern-based PII detection."""
    
    def test_detect_email(self, detector: PIIDetector):
        """GOV-SEC-PII-002: Detect email addresses."""
        text = "Contact us at support@company.com for help."
        matches = detector.detect_patterns(text)
        
        assert len(matches) == 1
        assert matches[0].entity_type == PIIEntityType.EMAIL
        assert matches[0].value == "support@company.com"
    
    def test_detect_phone_us(self, detector: PIIDetector):
        """GOV-SEC-PII-002: Detect US phone numbers."""
        text = "Call us at (555) 123-4567 or 555.987.6543"
        matches = detector.detect_patterns(text)
        
        phone_matches = [m for m in matches if m.entity_type == PIIEntityType.PHONE]
        assert len(phone_matches) >= 1
    
    def test_detect_ssn(self, detector: PIIDetector):
        """GOV-SEC-PII-002: Detect SSN patterns."""
        text = "SSN: 123-45-6789"
        matches = detector.detect_patterns(text)
        
        ssn_matches = [m for m in matches if m.entity_type == PIIEntityType.SSN]
        assert len(ssn_matches) == 1
        assert "123-45-6789" in ssn_matches[0].value
    
    def test_detect_credit_card(self, detector: PIIDetector):
        """GOV-SEC-PII-002: Detect credit card numbers."""
        text = "Card: 4532015112830366"
        matches = detector.detect_patterns(text)
        
        cc_matches = [m for m in matches if m.entity_type == PIIEntityType.CREDIT_CARD]
        assert len(cc_matches) == 1
    
    def test_detect_ip_address(self, detector: PIIDetector):
        """GOV-SEC-PII-002: Detect IP addresses."""
        text = "Server IP: 192.168.1.100"
        matches = detector.detect_patterns(text)
        
        ip_matches = [m for m in matches if m.entity_type == PIIEntityType.IP_ADDRESS]
        assert len(ip_matches) == 1
        assert ip_matches[0].value == "192.168.1.100"
    
    def test_detect_multiple_patterns(self, detector: PIIDetector, sample_text_with_pii: str):
        """GOV-SEC-PII-002: Detect multiple PII types."""
        matches = detector.detect_patterns(sample_text_with_pii)
        
        entity_types = {m.entity_type for m in matches}
        # Should detect at least email, phone, SSN, and IP
        assert PIIEntityType.EMAIL in entity_types
        assert PIIEntityType.IP_ADDRESS in entity_types


# ============================================================================
# GOV-SEC-PII-003: NER Detection Tests
# ============================================================================


class TestNERDetection:
    """Test NER-based detection."""
    
    def test_detect_person_with_prefix(self, detector: PIIDetector):
        """GOV-SEC-PII-003: Detect person names with prefix."""
        text = "Meeting with Dr. John Smith tomorrow."
        entities = detector.detect_named_entities(text)
        
        person_entities = [e for e in entities if e.entity_type == PIIEntityType.PERSON]
        assert len(person_entities) >= 1
    
    def test_detect_organization(self, detector: PIIDetector):
        """GOV-SEC-PII-003: Detect organization names."""
        text = "Working with Acme Corp on the project."
        entities = detector.detect_named_entities(text)
        
        org_entities = [e for e in entities if e.entity_type == PIIEntityType.ORGANIZATION]
        assert len(org_entities) == 1
    
    def test_ner_entities_have_low_sensitivity(self, detector: PIIDetector):
        """GOV-SEC-PII-003: NER entities (names) have low sensitivity."""
        text = "Dr. Jane Doe is our contact."
        entities = detector.detect_named_entities(text)
        
        for entity in entities:
            if entity.entity_type == PIIEntityType.PERSON:
                assert entity.sensitivity == PIISensitivity.LOW


# ============================================================================
# GOV-SEC-PII-004: Full Detection Tests
# ============================================================================


class TestFullDetection:
    """Test combined detection."""
    
    def test_detect_combines_pattern_and_ner(self, detector: PIIDetector):
        """GOV-SEC-PII-004: detect() combines both methods."""
        text = "Email Dr. John Smith at john.smith@example.com"
        result = detector.detect(text)
        
        entity_types = {e.entity_type for e in result.entities}
        assert PIIEntityType.EMAIL in entity_types
    
    def test_detection_result_counts(self, detector: PIIDetector, sample_text_with_pii: str):
        """GOV-SEC-PII-004: Result has correct counts."""
        result = detector.detect(sample_text_with_pii)
        
        assert result.total_detected > 0
        assert len(result.entity_counts) > 0
        assert len(result.sensitivity_counts) > 0
    
    def test_detection_result_has_high_sensitivity(self, detector: PIIDetector):
        """GOV-SEC-PII-004: Result detects high sensitivity."""
        text = "SSN: 123-45-6789"
        result = detector.detect(text)
        
        assert result.has_high_sensitivity() is True
    
    def test_detection_empty_text(self, detector: PIIDetector):
        """GOV-SEC-PII-004: Empty text returns empty result."""
        result = detector.detect("")
        
        assert result.total_detected == 0
        assert len(result.entities) == 0


class TestPIIDetectionResult:
    """Test PIIDetectionResult model."""
    
    def test_result_entity_counts(self):
        """GOV-SEC-PII-004: Entity counts are correct."""
        entities = [
            PIIEntity(PIIEntityType.EMAIL, "a@b.com", (0, 7), 0.9),
            PIIEntity(PIIEntityType.EMAIL, "c@d.com", (10, 17), 0.9),
            PIIEntity(PIIEntityType.PHONE, "555-1234", (20, 28), 0.8),
        ]
        result = PIIDetectionResult(entities=entities)
        
        assert result.entity_counts["EMAIL"] == 2
        assert result.entity_counts["PHONE"] == 1
        assert result.total_detected == 3
    
    def test_result_sensitivity_counts(self):
        """GOV-SEC-PII-004: Sensitivity counts are correct."""
        entities = [
            PIIEntity(PIIEntityType.EMAIL, "a@b.com", (0, 7), 0.9, PIISensitivity.MEDIUM),
            PIIEntity(PIIEntityType.SSN, "123-45-6789", (10, 21), 0.9, PIISensitivity.HIGH),
        ]
        result = PIIDetectionResult(entities=entities)
        
        assert result.sensitivity_counts["MEDIUM"] == 1
        assert result.sensitivity_counts["HIGH"] == 1


# ============================================================================
# GOV-SEC-PII-005: Trace Event Tests
# ============================================================================


class TestTraceEvents:
    """Test trace event emission."""
    
    def test_pii_detected_event_emitted(self):
        """GOV-SEC-PII-005: pii_detected event emitted."""
        events: List[Dict[str, Any]] = []
        
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append({"type": event_type, "payload": payload})
        
        detector = PIIDetector(emit_event_fn=capture_event)
        detector.detect("Email: test@example.com")
        
        assert len(events) == 1
        assert events[0]["type"] == "pii_detected"
    
    def test_trace_payload_has_counts_not_values(self):
        """GOV-SEC-PII-005: Trace payload has counts, not values."""
        events: List[Dict[str, Any]] = []
        
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append(payload)
        
        detector = PIIDetector(emit_event_fn=capture_event)
        detector.detect("SSN: 123-45-6789 Email: test@test.com")
        
        payload = events[0]
        assert "total_detected" in payload
        assert "entity_counts" in payload
        assert "sensitivity_counts" in payload
        # Should NOT have actual PII values
        assert "123-45-6789" not in str(payload)
        assert "test@test.com" not in str(payload)
    
    def test_no_event_when_no_pii(self):
        """GOV-SEC-PII-005: No event when no PII detected."""
        events: List[Dict[str, Any]] = []
        
        def capture_event(event_type: str, payload: Dict[str, Any]):
            events.append({"type": event_type})
        
        detector = PIIDetector(emit_event_fn=capture_event)
        detector.detect("This text has no PII.")
        
        assert len(events) == 0
    
    def test_trace_event_type_exists(self):
        """GOV-SEC-PII-005: PII_DETECTED trace event type exists."""
        assert hasattr(TraceEventType, "PII_DETECTED")
        assert TraceEventType.PII_DETECTED.value == "pii_detected"


# ============================================================================
# Redaction Tests
# ============================================================================


class TestRedaction:
    """Test redaction functionality."""
    
    def test_redact_email(self, detector: PIIDetector):
        """Redact email addresses."""
        text = "Contact us at support@company.com"
        redacted = detector.redact(text)
        
        assert "[REDACTED:EMAIL]" in redacted
        assert "support@company.com" not in redacted
    
    def test_redact_multiple(self, detector: PIIDetector):
        """Redact multiple PII items."""
        text = "Email: a@b.com Phone: 555-123-4567"
        redacted = detector.redact(text)
        
        assert "[REDACTED:" in redacted
        assert "a@b.com" not in redacted
    
    def test_redact_preserves_non_pii(self, detector: PIIDetector):
        """Redaction preserves non-PII text."""
        text = "Please contact us at support@company.com for more info."
        redacted = detector.redact(text)
        
        assert "Please contact us at" in redacted
        assert "for more info." in redacted
    
    def test_redact_no_pii(self, detector: PIIDetector):
        """Redaction returns original when no PII."""
        text = "This is a normal sentence."
        redacted = detector.redact(text)
        
        assert redacted == text


# ============================================================================
# Configuration Tests
# ============================================================================


class TestConfiguration:
    """Test detector configuration."""
    
    def test_add_custom_pattern(self):
        """Add custom pattern to detector."""
        detector = PIIDetector()
        detector.add_pattern(
            name="custom_id",
            pattern=r"ID-[0-9]{6}",
            entity_type=PIIEntityType.CUSTOM,
            confidence=0.85,
        )
        
        assert "custom_id" in detector.get_pattern_names()
        
        # Should detect custom pattern
        text = "Your ID is ID-123456"
        matches = detector.detect_patterns(text)
        custom_matches = [m for m in matches if m.pattern_name == "custom_id"]
        assert len(custom_matches) == 1
    
    def test_invalid_pattern_raises_error(self):
        """Invalid pattern raises ValueError."""
        detector = PIIDetector()
        
        with pytest.raises(ValueError):
            detector.add_pattern(
                name="bad",
                pattern="[invalid(regex",
                entity_type=PIIEntityType.CUSTOM,
            )
    
    def test_min_confidence_filter(self):
        """Min confidence filters low-confidence patterns."""
        detector = PIIDetector(min_confidence=0.95)
        
        # Some patterns have confidence < 0.95, should be filtered
        text = "Driver license: A1234567"
        matches = detector.detect_patterns(text)
        
        # Driver license pattern has 0.60 confidence, should be filtered
        dl_matches = [m for m in matches if m.entity_type == PIIEntityType.DRIVER_LICENSE]
        assert len(dl_matches) == 0


# ============================================================================
# Factory Function Tests
# ============================================================================


class TestFactoryFunction:
    """Test factory function."""
    
    def test_create_pii_detector(self):
        """Factory creates valid detector."""
        detector = create_pii_detector(
            sensitivity_level="high",
            min_confidence=0.6,
        )
        
        assert isinstance(detector, PIIDetector)
    
    def test_factory_with_emit_fn(self):
        """Factory accepts emit function."""
        events = []
        
        detector = create_pii_detector(
            emit_event_fn=lambda t, p: events.append(t)
        )
        detector.detect("test@example.com")
        
        assert "pii_detected" in events
