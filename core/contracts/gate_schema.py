"""
Gate Rejection Artifacts Schema (IMP-050)

GOV-GATE-REJ-001...010: Gate rejection artifacts for audit and traceability.

This module provides:
- GateRejectionArtifact: Structured artifact for gate rejection events
- GateRejectionSeverity: Severity classification of rejections
- Factory functions for artifact creation
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Severity Enum
# ============================================================================


class GateRejectionSeverity(str, Enum):
    """
    Severity level of gate rejection.
    
    GOV-GATE-REJ-002: Rejections MUST have severity classification.
    """
    LOW = "LOW"           # Minor issue, may be auto-recoverable
    MEDIUM = "MEDIUM"     # Requires attention, may need user input
    HIGH = "HIGH"         # Critical issue, blocks execution
    CRITICAL = "CRITICAL" # Security or safety concern


# ============================================================================
# Gate Rejection Artifact
# ============================================================================


class GateRejectionArtifact(BaseModel):
    """
    Structured artifact for gate rejection events.
    
    GOV-GATE-REJ-001...010: Full traceability for gate rejections.
    
    Attributes:
        rejection_id: Unique identifier for this rejection event
        gate_name: Name of the gate that rejected
        rejection_reason: Primary reason for rejection
        severity: Severity classification
        gate_inputs: Copy of inputs provided to the gate
        timestamp: When the rejection occurred
        run_id: Associated run ID
        step_id: Optional associated step ID
        recommendations: Suggested actions to resolve
        errors: List of specific error messages
        metadata: Additional context
    """
    
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    # Core identification
    rejection_id: str = Field(
        default_factory=lambda: f"rej-{uuid4().hex[:12]}",
        description="Unique identifier for this rejection event",
        min_length=1,
    )
    
    gate_name: str = Field(
        ...,
        description="Name of the gate that rejected",
        min_length=1,
        max_length=100,
    )
    
    rejection_reason: str = Field(
        ...,
        description="Primary reason for rejection",
        max_length=500,
    )
    
    severity: GateRejectionSeverity = Field(
        default=GateRejectionSeverity.MEDIUM,
        description="Severity classification of the rejection",
    )
    
    # Context
    gate_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Copy of inputs provided to the gate (sanitized)",
    )
    
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the rejection occurred",
    )
    
    run_id: str = Field(
        ...,
        description="Associated run ID",
        min_length=1,
    )
    
    step_id: Optional[str] = Field(
        default=None,
        description="Optional associated step ID",
    )
    
    product: Optional[str] = Field(
        default=None,
        description="Product context for the rejection",
    )
    
    flow: Optional[str] = Field(
        default=None,
        description="Flow context for the rejection",
    )
    
    # Resolution guidance
    recommendations: List[str] = Field(
        default_factory=list,
        description="Suggested actions to resolve the rejection",
        max_length=10,
    )
    
    errors: List[str] = Field(
        default_factory=list,
        description="List of specific error messages",
        max_length=50,
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context and details",
    )
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload format."""
        return {
            "rejection_id": self.rejection_id,
            "gate_name": self.gate_name,
            "rejection_reason": self.rejection_reason,
            "severity": self.severity.value,
            "run_id": self.run_id,
            "step_id": self.step_id,
            "product": self.product,
            "flow": self.flow,
            "recommendation_count": len(self.recommendations),
            "error_count": len(self.errors),
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_persistence_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return self.model_dump(mode="json")


# ============================================================================
# Factory Functions
# ============================================================================


def create_rejection_artifact(
    gate_name: str,
    rejection_reason: str,
    run_id: str,
    *,
    severity: GateRejectionSeverity = GateRejectionSeverity.MEDIUM,
    gate_inputs: Optional[Dict[str, Any]] = None,
    step_id: Optional[str] = None,
    product: Optional[str] = None,
    flow: Optional[str] = None,
    recommendations: Optional[List[str]] = None,
    errors: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> GateRejectionArtifact:
    """
    Factory function to create a GateRejectionArtifact.
    
    GOV-GATE-REJ-003: Factory ensures all required fields populated.
    
    Args:
        gate_name: Name of the rejecting gate.
        rejection_reason: Primary rejection reason.
        run_id: Associated run ID.
        severity: Rejection severity (default: MEDIUM).
        gate_inputs: Inputs provided to the gate.
        step_id: Optional step ID.
        product: Optional product context.
        flow: Optional flow context.
        recommendations: Suggested resolution actions.
        errors: Specific error messages.
        metadata: Additional context.
        
    Returns:
        Configured GateRejectionArtifact.
    """
    return GateRejectionArtifact(
        gate_name=gate_name,
        rejection_reason=rejection_reason,
        run_id=run_id,
        severity=severity,
        gate_inputs=gate_inputs or {},
        step_id=step_id,
        product=product,
        flow=flow,
        recommendations=recommendations or [],
        errors=errors or [],
        metadata=metadata or {},
    )


def create_confidence_rejection(
    run_id: str,
    actual_confidence: float,
    threshold: float,
    *,
    step_id: Optional[str] = None,
    product: Optional[str] = None,
    flow: Optional[str] = None,
    failing_entities: Optional[List[str]] = None,
) -> GateRejectionArtifact:
    """
    Create rejection artifact for confidence gate failure.
    
    Args:
        run_id: Associated run ID.
        actual_confidence: The actual confidence score.
        threshold: The required threshold.
        step_id: Optional step ID.
        product: Optional product context.
        flow: Optional flow context.
        failing_entities: Entities that failed confidence check.
        
    Returns:
        GateRejectionArtifact for confidence rejection.
    """
    errors = [f"Confidence {actual_confidence:.2f} below threshold {threshold:.2f}"]
    if failing_entities:
        for entity in failing_entities:
            errors.append(f"Entity '{entity}' below threshold")
    
    return GateRejectionArtifact(
        gate_name="confidence",
        rejection_reason="Low confidence score",
        run_id=run_id,
        severity=GateRejectionSeverity.MEDIUM,
        gate_inputs={
            "actual_confidence": actual_confidence,
            "threshold": threshold,
            "failing_entities": failing_entities or [],
        },
        step_id=step_id,
        product=product,
        flow=flow,
        recommendations=[
            "Request clarification from user",
            "Gather additional context",
            "Consider lowering threshold if appropriate",
        ],
        errors=errors,
    )


def create_sufficiency_rejection(
    run_id: str,
    blocking_gaps: List[str],
    *,
    step_id: Optional[str] = None,
    product: Optional[str] = None,
    flow: Optional[str] = None,
    blocking_unknowns: Optional[List[str]] = None,
) -> GateRejectionArtifact:
    """
    Create rejection artifact for sufficiency gate failure.
    
    Args:
        run_id: Associated run ID.
        blocking_gaps: List of blocking gap descriptions.
        step_id: Optional step ID.
        product: Optional product context.
        flow: Optional flow context.
        blocking_unknowns: Optional blocking unknown questions.
        
    Returns:
        GateRejectionArtifact for sufficiency rejection.
    """
    errors = [f"Blocking gap: {gap}" for gap in blocking_gaps]
    if blocking_unknowns:
        errors.extend(f"Blocking unknown: {u}" for u in blocking_unknowns)
    
    return GateRejectionArtifact(
        gate_name="intent_sufficiency",
        rejection_reason=f"{len(blocking_gaps)} blocking gap(s) prevent execution",
        run_id=run_id,
        severity=GateRejectionSeverity.HIGH,
        gate_inputs={
            "blocking_gap_count": len(blocking_gaps),
            "blocking_gaps": blocking_gaps,
            "blocking_unknowns": blocking_unknowns or [],
        },
        step_id=step_id,
        product=product,
        flow=flow,
        recommendations=[
            "Gather required information for blocking gaps",
            "Request user input for unknowns",
        ],
        errors=errors,
    )


def create_semantic_rejection(
    run_id: str,
    failures: List[str],
    *,
    envelope_complete: bool = True,
    confidence_passed: bool = True,
    sufficiency_passed: bool = True,
    step_id: Optional[str] = None,
    product: Optional[str] = None,
    flow: Optional[str] = None,
) -> GateRejectionArtifact:
    """
    Create rejection artifact for semantic gate failure.
    
    Args:
        run_id: Associated run ID.
        failures: List of failure reasons.
        envelope_complete: Whether envelope was complete.
        confidence_passed: Whether confidence check passed.
        sufficiency_passed: Whether sufficiency check passed.
        step_id: Optional step ID.
        product: Optional product context.
        flow: Optional flow context.
        
    Returns:
        GateRejectionArtifact for semantic gate rejection.
    """
    # Determine primary reason
    if not envelope_complete:
        reason = "Incomplete semantic envelope"
    elif not confidence_passed:
        reason = "Low confidence"
    elif not sufficiency_passed:
        reason = "Insufficient intent understanding"
    else:
        reason = "Semantic validation failed"
    
    recommendations = []
    if not envelope_complete:
        recommendations.append("Ensure all required envelope fields are populated")
    if not confidence_passed:
        recommendations.append("Request clarification for low-confidence interpretation")
    if not sufficiency_passed:
        recommendations.append("Resolve blocking gaps before proceeding")
    
    return GateRejectionArtifact(
        gate_name="semantic",
        rejection_reason=reason,
        run_id=run_id,
        severity=GateRejectionSeverity.MEDIUM,
        gate_inputs={
            "envelope_complete": envelope_complete,
            "confidence_passed": confidence_passed,
            "sufficiency_passed": sufficiency_passed,
        },
        step_id=step_id,
        product=product,
        flow=flow,
        recommendations=recommendations,
        errors=failures,
    )


# ============================================================================
# Artifact Store Protocol
# ============================================================================


class GateRejectionStore:
    """
    In-memory store for gate rejection artifacts.
    
    GOV-GATE-REJ-008: Artifacts MUST be retrievable by rejection_id.
    
    Note: This is a simple in-memory implementation. Production should
    use a persistent backend via MemoryBackend interface.
    """
    
    def __init__(self) -> None:
        self._artifacts: Dict[str, GateRejectionArtifact] = {}
    
    def store(self, artifact: GateRejectionArtifact) -> str:
        """
        Store a rejection artifact.
        
        Args:
            artifact: The artifact to store.
            
        Returns:
            The rejection_id of the stored artifact.
        """
        self._artifacts[artifact.rejection_id] = artifact
        return artifact.rejection_id
    
    def get(self, rejection_id: str) -> Optional[GateRejectionArtifact]:
        """
        Retrieve an artifact by ID.
        
        Args:
            rejection_id: The rejection ID to look up.
            
        Returns:
            The artifact if found, None otherwise.
        """
        return self._artifacts.get(rejection_id)
    
    def get_by_run(self, run_id: str) -> List[GateRejectionArtifact]:
        """
        Get all artifacts for a run.
        
        Args:
            run_id: The run ID to filter by.
            
        Returns:
            List of artifacts for the run.
        """
        return [a for a in self._artifacts.values() if a.run_id == run_id]
    
    def get_by_gate(self, gate_name: str) -> List[GateRejectionArtifact]:
        """
        Get all artifacts for a specific gate.
        
        Args:
            gate_name: The gate name to filter by.
            
        Returns:
            List of artifacts for the gate.
        """
        return [a for a in self._artifacts.values() if a.gate_name == gate_name]
    
    def clear(self) -> None:
        """Clear all stored artifacts."""
        self._artifacts.clear()
    
    def count(self) -> int:
        """Get count of stored artifacts."""
        return len(self._artifacts)
