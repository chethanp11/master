# ==============================
# IMP-051: Evidence Requirements Tests
# ==============================
"""
Tests for Evidence Requirements Validation.

Tech Specs: GOV-EVID-001..005, GOV-EVID-CONF-001..005, GOV-EVID-TRACE-001..005
- GOV-EVID-001: Evidence types for decision validation
- GOV-EVID-002: Requirement specifies type, min confidence, description
- GOV-EVID-003: Evidence items have type, confidence, source reference
- GOV-EVID-004: Validation result includes satisfied/missing requirements
- GOV-EVID-005: Validator checks all requirements are satisfied
- GOV-EVID-CONF-001: Validates decision has sufficient evidence
- GOV-EVID-CONF-002: Weighted aggregation of evidence confidence
- GOV-EVID-CONF-003: Detects and reports missing evidence
- GOV-EVID-CONF-004: Match evidence to requirements
- GOV-EVID-CONF-005: Overall confidence from evidence coverage
- GOV-EVID-TRACE-001: evidence_validation_completed event
- GOV-EVID-TRACE-002: missing_evidence_detected event
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List

from core.governance.evidence_requirements import (
    EvidenceType,
    EvidenceRequirement,
    EvidenceItem,
    EvidenceValidationResult,
    EvidenceValidator,
    create_evidence_requirement,
    create_evidence_item,
    get_high_risk_requirements,
    get_standard_requirements,
    get_low_risk_requirements,
    EVIDENCE_MISSING,
    EVIDENCE_INSUFFICIENT_CONFIDENCE,
    EVIDENCE_REQUIREMENT_VIOLATED,
)
from core.memory.tracing import TraceEventType


# ==============================
# EvidenceType Tests
# ==============================
class TestEvidenceType:
    """Tests for EvidenceType enum."""
    
    def test_all_evidence_types_exist(self):
        """All required evidence types exist."""
        assert EvidenceType.DATA_RETRIEVAL.value == "data_retrieval"
        assert EvidenceType.USER_INPUT.value == "user_input"
        assert EvidenceType.TOOL_RESULT.value == "tool_result"
        assert EvidenceType.EXTERNAL_API.value == "external_api"
        assert EvidenceType.COMPUTED.value == "computed"
        assert EvidenceType.CONTEXTUAL.value == "contextual"
        assert EvidenceType.ASSUMED.value == "assumed"
    
    def test_evidence_types_are_string_enum(self):
        """Evidence types inherit from str."""
        assert isinstance(EvidenceType.DATA_RETRIEVAL, str)


# ==============================
# EvidenceRequirement Tests
# ==============================
class TestEvidenceRequirement:
    """Tests for EvidenceRequirement dataclass."""
    
    def test_requirement_creation(self):
        """Requirement stores all fields."""
        req = EvidenceRequirement(
            requirement_id="req-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            description="Need data evidence",
            min_confidence=0.8,
            required=True,
        )
        
        assert req.requirement_id == "req-001"
        assert req.evidence_type == EvidenceType.DATA_RETRIEVAL
        assert req.description == "Need data evidence"
        assert req.min_confidence == 0.8
        assert req.required is True
    
    def test_requirement_immutable(self):
        """Requirement is frozen/immutable."""
        req = EvidenceRequirement(
            requirement_id="req-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            description="Test",
        )
        
        with pytest.raises(Exception):
            req.min_confidence = 0.5  # type: ignore
    
    def test_requirement_defaults(self):
        """Requirement has sensible defaults."""
        req = EvidenceRequirement(
            requirement_id="req-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            description="Test",
        )
        
        assert req.min_confidence == 0.7
        assert req.required is True
        assert req.metadata == {}
    
    def test_is_satisfied_by_matching_evidence(self):
        """is_satisfied_by returns True for matching evidence."""
        req = EvidenceRequirement(
            requirement_id="req-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            description="Test",
            min_confidence=0.7,
        )
        
        assert req.is_satisfied_by(0.8, EvidenceType.DATA_RETRIEVAL) is True
        assert req.is_satisfied_by(0.7, EvidenceType.DATA_RETRIEVAL) is True
    
    def test_is_satisfied_by_low_confidence(self):
        """is_satisfied_by returns False for low confidence."""
        req = EvidenceRequirement(
            requirement_id="req-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            description="Test",
            min_confidence=0.7,
        )
        
        assert req.is_satisfied_by(0.6, EvidenceType.DATA_RETRIEVAL) is False
    
    def test_is_satisfied_by_wrong_type(self):
        """is_satisfied_by returns False for wrong evidence type."""
        req = EvidenceRequirement(
            requirement_id="req-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            description="Test",
        )
        
        assert req.is_satisfied_by(0.9, EvidenceType.USER_INPUT) is False
    
    def test_to_trace_payload(self):
        """to_trace_payload includes all fields."""
        req = EvidenceRequirement(
            requirement_id="req-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            description="Test",
            min_confidence=0.8,
            required=True,
        )
        
        payload = req.to_trace_payload()
        
        assert payload["requirement_id"] == "req-001"
        assert payload["evidence_type"] == "data_retrieval"
        assert payload["min_confidence"] == 0.8
        assert payload["required"] is True


# ==============================
# EvidenceItem Tests
# ==============================
class TestEvidenceItem:
    """Tests for EvidenceItem dataclass."""
    
    def test_evidence_item_creation(self):
        """EvidenceItem stores all fields."""
        item = EvidenceItem(
            evidence_id="ev-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            source_ref="tool:get_data",
            confidence=0.85,
            description="Retrieved data",
        )
        
        assert item.evidence_id == "ev-001"
        assert item.evidence_type == EvidenceType.DATA_RETRIEVAL
        assert item.source_ref == "tool:get_data"
        assert item.confidence == 0.85
        assert item.description == "Retrieved data"
    
    def test_evidence_item_immutable(self):
        """EvidenceItem is frozen/immutable."""
        item = EvidenceItem(
            evidence_id="ev-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            source_ref="test",
            confidence=0.8,
        )
        
        with pytest.raises(Exception):
            item.confidence = 0.5  # type: ignore
    
    def test_evidence_item_has_timestamp(self):
        """EvidenceItem has automatic timestamp."""
        item = EvidenceItem(
            evidence_id="ev-001",
            evidence_type=EvidenceType.DATA_RETRIEVAL,
            source_ref="test",
            confidence=0.8,
        )
        
        assert isinstance(item.timestamp, datetime)
    
    def test_to_trace_payload(self):
        """to_trace_payload includes all fields."""
        item = EvidenceItem(
            evidence_id="ev-001",
            evidence_type=EvidenceType.USER_INPUT,
            source_ref="user:confirm",
            confidence=0.95,
            description="User confirmed",
        )
        
        payload = item.to_trace_payload()
        
        assert payload["evidence_id"] == "ev-001"
        assert payload["evidence_type"] == "user_input"
        assert payload["source_ref"] == "user:confirm"
        assert payload["confidence"] == 0.95


# ==============================
# EvidenceValidationResult Tests
# ==============================
class TestEvidenceValidationResult:
    """Tests for EvidenceValidationResult dataclass."""
    
    def test_valid_result(self):
        """Valid result has correct properties."""
        result = EvidenceValidationResult(
            is_valid=True,
            satisfied_requirements=["req-001", "req-002"],
            missing_requirements=[],
            insufficient_confidence=[],
            aggregated_confidence=0.9,
        )
        
        assert result.is_valid is True
        assert result.has_missing_evidence is False
        assert result.has_low_confidence_evidence is False
    
    def test_invalid_with_missing(self):
        """Invalid result with missing requirements."""
        result = EvidenceValidationResult(
            is_valid=False,
            satisfied_requirements=["req-001"],
            missing_requirements=["req-002"],
            insufficient_confidence=[],
            aggregated_confidence=0.5,
            error_code=EVIDENCE_MISSING,
        )
        
        assert result.is_valid is False
        assert result.has_missing_evidence is True
        assert result.error_code == EVIDENCE_MISSING
    
    def test_invalid_with_low_confidence(self):
        """Invalid result with insufficient confidence."""
        result = EvidenceValidationResult(
            is_valid=False,
            satisfied_requirements=["req-001"],
            missing_requirements=[],
            insufficient_confidence=["req-002"],
            aggregated_confidence=0.4,
            error_code=EVIDENCE_INSUFFICIENT_CONFIDENCE,
        )
        
        assert result.is_valid is False
        assert result.has_low_confidence_evidence is True


# ==============================
# EvidenceValidator Tests
# ==============================
class TestEvidenceValidator:
    """Tests for EvidenceValidator class."""
    
    def test_validate_all_satisfied(self):
        """Validation passes when all requirements satisfied."""
        validator = EvidenceValidator()
        
        requirements = [
            EvidenceRequirement(
                requirement_id="req-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                description="Need data",
                min_confidence=0.7,
            ),
        ]
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="tool:data",
                confidence=0.8,
            ),
        ]
        
        result = validator.validate_decision_has_evidence(
            "decision-001",
            requirements,
            evidence,
        )
        
        assert result.is_valid is True
        assert "req-001" in result.satisfied_requirements
    
    def test_validate_missing_evidence(self):
        """Validation fails when required evidence is missing."""
        validator = EvidenceValidator()
        
        requirements = [
            EvidenceRequirement(
                requirement_id="req-001",
                evidence_type=EvidenceType.USER_INPUT,
                description="Need user confirmation",
            ),
        ]
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="tool:data",
                confidence=0.9,
            ),
        ]
        
        result = validator.validate_decision_has_evidence(
            "decision-001",
            requirements,
            evidence,
        )
        
        assert result.is_valid is False
        assert "req-001" in result.missing_requirements
        assert result.error_code == EVIDENCE_MISSING
    
    def test_validate_insufficient_confidence(self):
        """Validation fails when evidence confidence is too low."""
        validator = EvidenceValidator()
        
        requirements = [
            EvidenceRequirement(
                requirement_id="req-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                description="Need data",
                min_confidence=0.8,
            ),
        ]
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="tool:data",
                confidence=0.6,  # Below required 0.8
            ),
        ]
        
        result = validator.validate_decision_has_evidence(
            "decision-001",
            requirements,
            evidence,
        )
        
        assert result.is_valid is False
        assert "req-001" in result.insufficient_confidence
        assert result.error_code == EVIDENCE_INSUFFICIENT_CONFIDENCE
    
    def test_validate_emits_event(self):
        """Validation emits trace event."""
        events: List[Dict[str, Any]] = []
        
        def emit(event_type: str, payload: Dict[str, Any]) -> None:
            events.append({"type": event_type, "payload": payload})
        
        validator = EvidenceValidator(emit_event_fn=emit)
        
        requirements = [
            EvidenceRequirement(
                requirement_id="req-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                description="Need data",
            ),
        ]
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="tool:data",
                confidence=0.8,
            ),
        ]
        
        validator.validate_decision_has_evidence(
            "decision-001",
            requirements,
            evidence,
        )
        
        assert len(events) >= 1
        assert events[0]["type"] == "evidence_validation_completed"
        assert events[0]["payload"]["decision_id"] == "decision-001"


class TestPropagateEvidenceConfidence:
    """Tests for evidence confidence propagation."""
    
    def test_propagate_empty_evidence(self):
        """Empty evidence list returns 0."""
        validator = EvidenceValidator()
        result = validator.propagate_evidence_confidence([])
        assert result == 0.0
    
    def test_propagate_single_evidence(self):
        """Single evidence returns weighted confidence."""
        validator = EvidenceValidator()
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="test",
                confidence=0.9,
            ),
        ]
        
        result = validator.propagate_evidence_confidence(evidence)
        assert result == 0.9  # Single item, full weight
    
    def test_propagate_multiple_evidence(self):
        """Multiple evidence aggregates correctly."""
        validator = EvidenceValidator()
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="test",
                confidence=0.8,
            ),
            EvidenceItem(
                evidence_id="ev-002",
                evidence_type=EvidenceType.USER_INPUT,
                source_ref="test",
                confidence=0.9,
            ),
        ]
        
        result = validator.propagate_evidence_confidence(evidence)
        assert 0.8 <= result <= 0.9  # Should be weighted average
    
    def test_assumed_evidence_lower_weight(self):
        """Assumed evidence has lower weight than direct evidence."""
        validator = EvidenceValidator()
        
        data_only = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="test",
                confidence=0.8,
            ),
        ]
        
        assumed_only = [
            EvidenceItem(
                evidence_id="ev-002",
                evidence_type=EvidenceType.ASSUMED,
                source_ref="test",
                confidence=0.8,
            ),
        ]
        
        data_result = validator.propagate_evidence_confidence(data_only)
        assumed_result = validator.propagate_evidence_confidence(assumed_only)
        
        # Assumed should have lower effective confidence
        assert assumed_result <= data_result


class TestCheckMissingEvidence:
    """Tests for missing evidence detection."""
    
    def test_no_missing_evidence(self):
        """Returns empty list when all evidence present."""
        validator = EvidenceValidator()
        
        requirements = [
            EvidenceRequirement(
                requirement_id="req-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                description="Test",
            ),
        ]
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="test",
                confidence=0.8,
            ),
        ]
        
        missing = validator.check_missing_evidence(
            "decision-001",
            "test_decision",
            requirements,
            evidence,
        )
        
        assert len(missing) == 0
    
    def test_detects_missing_evidence(self):
        """Detects missing required evidence."""
        validator = EvidenceValidator()
        
        requirements = [
            EvidenceRequirement(
                requirement_id="req-001",
                evidence_type=EvidenceType.USER_INPUT,
                description="Need confirmation",
            ),
        ]
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="test",
                confidence=0.8,
            ),
        ]
        
        missing = validator.check_missing_evidence(
            "decision-001",
            "test_decision",
            requirements,
            evidence,
        )
        
        assert len(missing) == 1
        assert missing[0].requirement_id == "req-001"
    
    def test_emits_missing_evidence_event(self):
        """Emits trace event when evidence is missing."""
        events: List[Dict[str, Any]] = []
        
        def emit(event_type: str, payload: Dict[str, Any]) -> None:
            events.append({"type": event_type, "payload": payload})
        
        validator = EvidenceValidator(emit_event_fn=emit)
        
        requirements = [
            EvidenceRequirement(
                requirement_id="req-001",
                evidence_type=EvidenceType.USER_INPUT,
                description="Need confirmation",
            ),
        ]
        
        validator.check_missing_evidence(
            "decision-001",
            "test_decision",
            requirements,
            [],  # No evidence
        )
        
        assert len(events) == 1
        assert events[0]["type"] == "missing_evidence_detected"
        assert events[0]["payload"]["decision_id"] == "decision-001"
        assert events[0]["payload"]["missing_count"] == 1


class TestComputeDecisionConfidence:
    """Tests for decision confidence computation."""
    
    def test_full_coverage_high_confidence(self):
        """Full requirement coverage gives high confidence."""
        validator = EvidenceValidator()
        
        requirements = [
            EvidenceRequirement(
                requirement_id="req-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                description="Test",
                min_confidence=0.7,
            ),
        ]
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="test",
                confidence=0.9,
            ),
        ]
        
        result = validator.compute_decision_confidence(requirements, evidence)
        
        assert result >= 0.8  # High coverage * high confidence
    
    def test_no_coverage_zero_confidence(self):
        """No coverage gives zero confidence."""
        validator = EvidenceValidator()
        
        requirements = [
            EvidenceRequirement(
                requirement_id="req-001",
                evidence_type=EvidenceType.USER_INPUT,
                description="Test",
            ),
        ]
        
        evidence = [
            EvidenceItem(
                evidence_id="ev-001",
                evidence_type=EvidenceType.DATA_RETRIEVAL,
                source_ref="test",
                confidence=0.9,
            ),
        ]
        
        result = validator.compute_decision_confidence(requirements, evidence)
        
        assert result == 0.0  # Zero coverage


# ==============================
# Helper Function Tests
# ==============================
class TestHelperFunctions:
    """Tests for helper/factory functions."""
    
    def test_create_evidence_requirement(self):
        """Factory creates requirement with UUID."""
        req = create_evidence_requirement(
            EvidenceType.DATA_RETRIEVAL,
            "Test description",
            min_confidence=0.8,
        )
        
        assert len(req.requirement_id) == 8  # UUID prefix
        assert req.evidence_type == EvidenceType.DATA_RETRIEVAL
        assert req.description == "Test description"
        assert req.min_confidence == 0.8
    
    def test_create_evidence_item(self):
        """Factory creates item with UUID."""
        item = create_evidence_item(
            EvidenceType.USER_INPUT,
            "user:confirm",
            0.95,
            "User confirmed",
        )
        
        assert len(item.evidence_id) == 8  # UUID prefix
        assert item.evidence_type == EvidenceType.USER_INPUT
        assert item.confidence == 0.95
    
    def test_create_evidence_item_clamps_confidence(self):
        """Factory clamps confidence to 0-1 range."""
        item_high = create_evidence_item(
            EvidenceType.DATA_RETRIEVAL,
            "test",
            1.5,  # Too high
        )
        item_low = create_evidence_item(
            EvidenceType.DATA_RETRIEVAL,
            "test",
            -0.5,  # Too low
        )
        
        assert item_high.confidence == 1.0
        assert item_low.confidence == 0.0


class TestStandardRequirementSets:
    """Tests for standard requirement sets."""
    
    def test_high_risk_requirements(self):
        """High-risk requirements are strict."""
        reqs = get_high_risk_requirements()
        
        assert len(reqs) >= 2
        assert all(r.required for r in reqs)
        assert any(r.evidence_type == EvidenceType.USER_INPUT for r in reqs)
    
    def test_standard_requirements(self):
        """Standard requirements are moderate."""
        reqs = get_standard_requirements()
        
        assert len(reqs) >= 1
        assert all(r.required for r in reqs)
    
    def test_low_risk_requirements(self):
        """Low-risk requirements are relaxed."""
        reqs = get_low_risk_requirements()
        
        assert len(reqs) >= 1
        # Low risk has optional requirements
        assert any(not r.required for r in reqs)


# ==============================
# Trace Event Type Tests
# ==============================
class TestTraceEventTypes:
    """Tests for trace event type registration."""
    
    def test_evidence_validation_completed_event_exists(self):
        """EVIDENCE_VALIDATION_COMPLETED trace event type exists."""
        assert hasattr(TraceEventType, "EVIDENCE_VALIDATION_COMPLETED")
        assert TraceEventType.EVIDENCE_VALIDATION_COMPLETED.value == "evidence_validation_completed"
    
    def test_missing_evidence_detected_event_exists(self):
        """MISSING_EVIDENCE_DETECTED trace event type exists."""
        assert hasattr(TraceEventType, "MISSING_EVIDENCE_DETECTED")
        assert TraceEventType.MISSING_EVIDENCE_DETECTED.value == "missing_evidence_detected"


# ==============================
# Error Code Tests
# ==============================
class TestErrorCodes:
    """Tests for error code constants."""
    
    def test_evidence_missing_code(self):
        """EVIDENCE_MISSING error code exists."""
        assert EVIDENCE_MISSING == "EVIDENCE_MISSING"
    
    def test_evidence_insufficient_confidence_code(self):
        """EVIDENCE_INSUFFICIENT_CONFIDENCE error code exists."""
        assert EVIDENCE_INSUFFICIENT_CONFIDENCE == "EVIDENCE_INSUFFICIENT_CONFIDENCE"
    
    def test_evidence_requirement_violated_code(self):
        """EVIDENCE_REQUIREMENT_VIOLATED error code exists."""
        assert EVIDENCE_REQUIREMENT_VIOLATED == "EVIDENCE_REQUIREMENT_VIOLATED"
