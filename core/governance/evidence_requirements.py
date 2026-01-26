# ==============================
# Evidence Requirements Module
# ==============================
"""
Evidence Requirements Validation (IMP-051).

GOV-EVID-001...005: Evidence requirement model and validation.
GOV-EVID-CONF-001...005: Evidence confidence propagation.
GOV-EVID-TRACE-001...005: Evidence trace events.

This module provides:
- EvidenceRequirement: Model for required evidence per decision type
- EvidenceValidator: Validates decisions have required evidence
- Evidence confidence propagation functions
- Missing evidence detection and reporting
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4


# ==============================
# Error Codes
# ==============================
EVIDENCE_MISSING = "EVIDENCE_MISSING"
EVIDENCE_INSUFFICIENT_CONFIDENCE = "EVIDENCE_INSUFFICIENT_CONFIDENCE"
EVIDENCE_REQUIREMENT_VIOLATED = "EVIDENCE_REQUIREMENT_VIOLATED"


# ==============================
# Evidence Type Enum
# ==============================
class EvidenceType(str, Enum):
    """
    Types of evidence that can be required.
    
    GOV-EVID-001: Evidence types for decision validation.
    """
    DATA_RETRIEVAL = "data_retrieval"  # Evidence from data sources
    USER_INPUT = "user_input"  # Evidence from user confirmation
    TOOL_RESULT = "tool_result"  # Evidence from tool execution
    EXTERNAL_API = "external_api"  # Evidence from external API
    COMPUTED = "computed"  # Evidence from computation/analysis
    CONTEXTUAL = "contextual"  # Evidence from context pack
    ASSUMED = "assumed"  # Assumed evidence (lower confidence)


# ==============================
# Evidence Requirement Model (GOV-EVID-001...005)
# ==============================
@dataclass(frozen=True)
class EvidenceRequirement:
    """
    Requirement for evidence to support a decision.
    
    GOV-EVID-002: Each requirement specifies type, minimum confidence, and description.
    """
    
    requirement_id: str
    evidence_type: EvidenceType
    description: str
    min_confidence: float = 0.7
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_satisfied_by(
        self,
        evidence_confidence: float,
        evidence_type: EvidenceType,
    ) -> bool:
        """
        Check if this requirement is satisfied by given evidence.
        
        Args:
            evidence_confidence: Confidence of the evidence (0.0-1.0)
            evidence_type: Type of the evidence
            
        Returns:
            True if requirement is satisfied
        """
        if evidence_type != self.evidence_type:
            return False
        return evidence_confidence >= self.min_confidence
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload."""
        return {
            "requirement_id": self.requirement_id,
            "evidence_type": self.evidence_type.value,
            "description": self.description,
            "min_confidence": self.min_confidence,
            "required": self.required,
        }


@dataclass(frozen=True)
class EvidenceItem:
    """
    A piece of evidence supporting a decision.
    
    GOV-EVID-003: Evidence items have type, confidence, and source reference.
    """
    
    evidence_id: str
    evidence_type: EvidenceType
    source_ref: str
    confidence: float
    description: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload."""
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type.value,
            "source_ref": self.source_ref,
            "confidence": self.confidence,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
        }


# ==============================
# Validation Result Types
# ==============================
@dataclass(frozen=True)
class EvidenceValidationResult:
    """
    Result of evidence validation for a decision.
    
    GOV-EVID-004: Validation result includes satisfied/missing requirements.
    """
    
    is_valid: bool
    satisfied_requirements: List[str]
    missing_requirements: List[str]
    insufficient_confidence: List[str]
    aggregated_confidence: float
    validation_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    error_code: Optional[str] = None
    
    @property
    def has_missing_evidence(self) -> bool:
        """Check if any required evidence is missing."""
        return len(self.missing_requirements) > 0
    
    @property
    def has_low_confidence_evidence(self) -> bool:
        """Check if any evidence has insufficient confidence."""
        return len(self.insufficient_confidence) > 0
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload."""
        return {
            "is_valid": self.is_valid,
            "satisfied_count": len(self.satisfied_requirements),
            "missing_count": len(self.missing_requirements),
            "insufficient_confidence_count": len(self.insufficient_confidence),
            "aggregated_confidence": self.aggregated_confidence,
            "error_code": self.error_code,
            "timestamp": self.validation_timestamp.isoformat(),
        }


# ==============================
# Evidence Validator (GOV-EVID-CONF-001...005)
# ==============================
class EvidenceValidator:
    """
    Validator for evidence requirements.
    
    GOV-EVID-005: Validator checks all requirements are satisfied.
    """
    
    def __init__(
        self,
        *,
        emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        confidence_floor: float = 0.5,
    ) -> None:
        """
        Initialize evidence validator.
        
        Args:
            emit_event_fn: Optional function to emit trace events.
            confidence_floor: Minimum confidence floor (default: 0.5).
        """
        self._emit_event_fn = emit_event_fn
        self._confidence_floor = confidence_floor
    
    def validate_decision_has_evidence(
        self,
        decision_id: str,
        requirements: List[EvidenceRequirement],
        evidence: List[EvidenceItem],
    ) -> EvidenceValidationResult:
        """
        Validate that a decision has all required evidence.
        
        GOV-EVID-CONF-001: Validates decision has sufficient evidence.
        
        Args:
            decision_id: ID of the decision being validated.
            requirements: List of evidence requirements.
            evidence: List of evidence items provided.
            
        Returns:
            EvidenceValidationResult with validation details.
        """
        satisfied: List[str] = []
        missing: List[str] = []
        insufficient: List[str] = []
        
        # Create evidence lookup by type
        evidence_by_type: Dict[EvidenceType, List[EvidenceItem]] = {}
        for item in evidence:
            if item.evidence_type not in evidence_by_type:
                evidence_by_type[item.evidence_type] = []
            evidence_by_type[item.evidence_type].append(item)
        
        # Check each requirement
        for req in requirements:
            matching_evidence = evidence_by_type.get(req.evidence_type, [])
            
            if not matching_evidence:
                if req.required:
                    missing.append(req.requirement_id)
                continue
            
            # Find best matching evidence
            best_confidence = max(e.confidence for e in matching_evidence)
            
            if best_confidence >= req.min_confidence:
                satisfied.append(req.requirement_id)
            else:
                insufficient.append(req.requirement_id)
        
        # Compute aggregated confidence
        if evidence:
            agg_confidence = self.propagate_evidence_confidence(evidence)
        else:
            agg_confidence = 0.0
        
        # Determine validity
        is_valid = len(missing) == 0 and len(insufficient) == 0
        error_code = None
        if missing:
            error_code = EVIDENCE_MISSING
        elif insufficient:
            error_code = EVIDENCE_INSUFFICIENT_CONFIDENCE
        
        result = EvidenceValidationResult(
            is_valid=is_valid,
            satisfied_requirements=satisfied,
            missing_requirements=missing,
            insufficient_confidence=insufficient,
            aggregated_confidence=agg_confidence,
            error_code=error_code,
        )
        
        # GOV-EVID-TRACE-001: Emit validation completed event
        if self._emit_event_fn:
            self._emit_event_fn(
                "evidence_validation_completed",
                {
                    "decision_id": decision_id,
                    **result.to_trace_payload(),
                },
            )
        
        return result
    
    def propagate_evidence_confidence(
        self,
        evidence: List[EvidenceItem],
        weights: Optional[Dict[EvidenceType, float]] = None,
    ) -> float:
        """
        Propagate confidence from multiple evidence items.
        
        GOV-EVID-CONF-002: Weighted aggregation of evidence confidence.
        
        Args:
            evidence: List of evidence items.
            weights: Optional weights per evidence type.
            
        Returns:
            Aggregated confidence score (0.0-1.0).
        """
        if not evidence:
            return 0.0
        
        # Default weights (higher for direct evidence)
        default_weights: Dict[EvidenceType, float] = {
            EvidenceType.DATA_RETRIEVAL: 1.0,
            EvidenceType.USER_INPUT: 1.0,
            EvidenceType.TOOL_RESULT: 0.9,
            EvidenceType.EXTERNAL_API: 0.8,
            EvidenceType.COMPUTED: 0.7,
            EvidenceType.CONTEXTUAL: 0.6,
            EvidenceType.ASSUMED: 0.3,
        }
        
        weights = weights or default_weights
        
        # Weighted product formula
        total_weight = 0.0
        weighted_sum = 0.0
        
        for item in evidence:
            weight = weights.get(item.evidence_type, 0.5)
            weighted_sum += item.confidence * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Average weighted by type importance
        result = weighted_sum / total_weight
        
        # Apply floor
        return max(result, self._confidence_floor) if result > 0 else 0.0
    
    def check_missing_evidence(
        self,
        decision_id: str,
        decision_type: str,
        requirements: List[EvidenceRequirement],
        evidence: List[EvidenceItem],
    ) -> List[EvidenceRequirement]:
        """
        Check for missing evidence and emit trace event if found.
        
        GOV-EVID-CONF-003: Detects and reports missing evidence.
        
        Args:
            decision_id: ID of the decision.
            decision_type: Type of decision being made.
            requirements: Required evidence.
            evidence: Provided evidence.
            
        Returns:
            List of missing EvidenceRequirements.
        """
        evidence_types_present = {e.evidence_type for e in evidence}
        
        missing: List[EvidenceRequirement] = []
        for req in requirements:
            if req.required and req.evidence_type not in evidence_types_present:
                missing.append(req)
        
        # GOV-EVID-TRACE-002: Emit missing evidence event if any found
        if missing and self._emit_event_fn:
            self._emit_event_fn(
                "missing_evidence_detected",
                {
                    "decision_id": decision_id,
                    "decision_type": decision_type,
                    "missing_count": len(missing),
                    "missing_types": [m.evidence_type.value for m in missing],
                    "missing_descriptions": [m.description for m in missing],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        
        return missing
    
    def get_evidence_for_requirement(
        self,
        requirement: EvidenceRequirement,
        evidence: List[EvidenceItem],
    ) -> List[EvidenceItem]:
        """
        Get all evidence items that could satisfy a requirement.
        
        GOV-EVID-CONF-004: Match evidence to requirements.
        
        Args:
            requirement: The requirement to match.
            evidence: Available evidence items.
            
        Returns:
            List of matching evidence items.
        """
        return [
            e for e in evidence
            if e.evidence_type == requirement.evidence_type
        ]
    
    def compute_decision_confidence(
        self,
        requirements: List[EvidenceRequirement],
        evidence: List[EvidenceItem],
    ) -> float:
        """
        Compute overall decision confidence based on evidence.
        
        GOV-EVID-CONF-005: Overall confidence from evidence coverage.
        
        Args:
            requirements: Required evidence.
            evidence: Provided evidence.
            
        Returns:
            Decision confidence (0.0-1.0).
        """
        if not requirements:
            # No requirements means no constraint
            if evidence:
                return self.propagate_evidence_confidence(evidence)
            return 1.0
        
        # Count satisfied vs total required
        required_count = len([r for r in requirements if r.required])
        if required_count == 0:
            return self.propagate_evidence_confidence(evidence)
        
        satisfied_count = 0
        for req in requirements:
            if not req.required:
                continue
            matching = self.get_evidence_for_requirement(req, evidence)
            if matching and max(e.confidence for e in matching) >= req.min_confidence:
                satisfied_count += 1
        
        # Coverage ratio * evidence confidence
        coverage = satisfied_count / required_count
        evidence_confidence = self.propagate_evidence_confidence(evidence)
        
        return coverage * evidence_confidence


# ==============================
# Helper Functions
# ==============================
def create_evidence_requirement(
    evidence_type: EvidenceType,
    description: str,
    min_confidence: float = 0.7,
    required: bool = True,
) -> EvidenceRequirement:
    """
    Factory function to create an evidence requirement.
    
    Args:
        evidence_type: Type of evidence required.
        description: Description of what evidence is needed.
        min_confidence: Minimum confidence threshold.
        required: Whether this requirement is mandatory.
        
    Returns:
        New EvidenceRequirement instance.
    """
    return EvidenceRequirement(
        requirement_id=str(uuid4())[:8],
        evidence_type=evidence_type,
        description=description,
        min_confidence=min_confidence,
        required=required,
    )


def create_evidence_item(
    evidence_type: EvidenceType,
    source_ref: str,
    confidence: float,
    description: str = "",
) -> EvidenceItem:
    """
    Factory function to create an evidence item.
    
    Args:
        evidence_type: Type of evidence.
        source_ref: Reference to evidence source.
        confidence: Confidence score (0.0-1.0).
        description: Optional description.
        
    Returns:
        New EvidenceItem instance.
    """
    return EvidenceItem(
        evidence_id=str(uuid4())[:8],
        evidence_type=evidence_type,
        source_ref=source_ref,
        confidence=min(1.0, max(0.0, confidence)),  # Clamp to 0-1
        description=description,
    )


# ==============================
# Standard Requirement Sets
# ==============================
def get_high_risk_requirements() -> List[EvidenceRequirement]:
    """
    Get standard requirements for high-risk decisions.
    
    High-risk decisions require multiple evidence types.
    """
    return [
        create_evidence_requirement(
            EvidenceType.DATA_RETRIEVAL,
            "Data from authoritative source required",
            min_confidence=0.8,
        ),
        create_evidence_requirement(
            EvidenceType.USER_INPUT,
            "User confirmation required",
            min_confidence=0.9,
        ),
    ]


def get_standard_requirements() -> List[EvidenceRequirement]:
    """
    Get standard requirements for normal decisions.
    """
    return [
        create_evidence_requirement(
            EvidenceType.DATA_RETRIEVAL,
            "Supporting data required",
            min_confidence=0.7,
        ),
    ]


def get_low_risk_requirements() -> List[EvidenceRequirement]:
    """
    Get requirements for low-risk decisions.
    
    Low-risk decisions have relaxed requirements.
    """
    return [
        create_evidence_requirement(
            EvidenceType.CONTEXTUAL,
            "Contextual evidence sufficient",
            min_confidence=0.5,
            required=False,
        ),
    ]
