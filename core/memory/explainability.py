# ==============================
# Explainability Module
# ==============================
"""
Explainability support for MASTER platform.

IMP-025: MEM-EXPLAIN-001, MEM-EXPLAIN-002, MEM-EXPLAIN-003, MEM-EXPLAIN-004, MEM-EXPLAIN-005
IMP-026: MEM-EXPLAIN-ART-001, MEM-EXPLAIN-ART-002, MEM-EXPLAIN-ART-003

Provides:
- Decision point tracking with evidence chain
- Reasoning chain reconstruction from trace events
- Explanation artifact generation
- Confidence evolution tracking
- Pydantic model integration for validation/serialization

All explanations are generated from persisted trace events, 
ensuring full auditability and reproducibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4


# ==============================
# Evidence Reference
# ==============================

@dataclass
class EvidenceRef:
    """
    Reference to a piece of evidence used in reasoning.
    
    MEM-EXPLAIN-002: Evidence chain traceability.
    """
    evidence_id: str
    source_tool: str
    confidence: float = 0.5
    summary: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "evidence_id": self.evidence_id,
            "source_tool": self.source_tool,
            "confidence": self.confidence,
            "summary": self.summary,
        }


# ==============================
# Decision Point
# ==============================

@dataclass
class DecisionPoint:
    """
    A decision point in the reasoning chain.
    
    MEM-EXPLAIN-002: Each decision traceable through evidence chain.
    
    Represents a point where the system made a decision based on
    available evidence and reasoning.
    """
    decision_id: str = field(default_factory=lambda: str(uuid4()))
    step_id: Optional[str] = None
    phase: str = ""
    decision_type: str = ""  # e.g., "hypothesis_selection", "evidence_evaluation"
    description: str = ""
    evidence_refs: List[EvidenceRef] = field(default_factory=list)
    source_tools: List[str] = field(default_factory=list)
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "decision_id": self.decision_id,
            "step_id": self.step_id,
            "phase": self.phase,
            "decision_type": self.decision_type,
            "description": self.description,
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
            "source_tools": self.source_tools,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


# ==============================
# Reasoning Step
# ==============================

@dataclass
class ReasoningStep:
    """
    A step in the reasoning chain.
    
    MEM-EXPLAIN-003: Reasoning chains reconstructable from trace events.
    """
    step_id: str
    phase: str
    input_summary: str = ""
    output_summary: str = ""
    confidence: float = 0.5
    evidence_refs: List[EvidenceRef] = field(default_factory=list)
    decisions: List[DecisionPoint] = field(default_factory=list)
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "step_id": self.step_id,
            "phase": self.phase,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "confidence": self.confidence,
            "evidence_refs": [e.to_dict() for e in self.evidence_refs],
            "decisions": [d.to_dict() for d in self.decisions],
            "duration_ms": self.duration_ms,
        }


# ==============================
# Confidence Evolution
# ==============================

@dataclass
class ConfidencePoint:
    """
    A point in the confidence evolution timeline.
    
    MEM-EXPLAIN-005: Confidence evolution tracking.
    """
    phase: str
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reason: Optional[str] = None
    
    def to_tuple(self) -> Tuple[str, float]:
        """Convert to (phase, confidence) tuple."""
        return (self.phase, self.confidence)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "phase": self.phase,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
        }


# ==============================
# Explanation Artifact
# ==============================

@dataclass
class ExplanationArtifact:
    """
    Complete explanation artifact for a run.
    
    MEM-EXPLAIN-004: explain_run() API returns structured artifact.
    MEM-EXPLAIN-005: Includes required fields.
    """
    run_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reasoning_chain: List[ReasoningStep] = field(default_factory=list)
    evidence_used: List[EvidenceRef] = field(default_factory=list)
    decisions_made: List[DecisionPoint] = field(default_factory=list)
    confidence_evolution: List[ConfidencePoint] = field(default_factory=list)
    terminal_outcome: Optional[str] = None
    outcome_reason: Optional[str] = None
    outcome_explanation: Optional[str] = None
    
    def get_confidence_tuples(self) -> List[Tuple[str, float]]:
        """Get confidence evolution as list of (phase, confidence) tuples."""
        return [c.to_tuple() for c in self.confidence_evolution]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "run_id": self.run_id,
            "created_at": self.created_at.isoformat(),
            "reasoning_chain": [s.to_dict() for s in self.reasoning_chain],
            "evidence_used": [e.to_dict() for e in self.evidence_used],
            "decisions_made": [d.to_dict() for d in self.decisions_made],
            "confidence_evolution": [c.to_dict() for c in self.confidence_evolution],
            "terminal_outcome": self.terminal_outcome,
            "outcome_reason": self.outcome_reason,
            "outcome_explanation": self.outcome_explanation,
        }


# ==============================
# Explainability Functions
# ==============================

def create_decision_point(
    *,
    step_id: Optional[str] = None,
    phase: str = "",
    decision_type: str = "",
    description: str = "",
    evidence_refs: Optional[List[EvidenceRef]] = None,
    source_tools: Optional[List[str]] = None,
    confidence: float = 0.5,
) -> DecisionPoint:
    """
    Create a new decision point.
    
    Args:
        step_id: Associated step ID
        phase: Reasoning phase
        decision_type: Type of decision (e.g., "hypothesis_selection")
        description: Human-readable description
        evidence_refs: List of evidence references
        source_tools: List of source tool names
        confidence: Decision confidence
        
    Returns:
        DecisionPoint with unique decision_id
    """
    return DecisionPoint(
        step_id=step_id,
        phase=phase,
        decision_type=decision_type,
        description=description,
        evidence_refs=evidence_refs or [],
        source_tools=source_tools or [],
        confidence=confidence,
    )


def create_evidence_ref(
    *,
    evidence_id: str,
    source_tool: str,
    confidence: float = 0.5,
    summary: Optional[str] = None,
) -> EvidenceRef:
    """
    Create a new evidence reference.
    
    Args:
        evidence_id: Unique evidence identifier
        source_tool: Tool that produced this evidence
        confidence: Confidence in this evidence
        summary: Optional summary text
        
    Returns:
        EvidenceRef instance
    """
    return EvidenceRef(
        evidence_id=evidence_id,
        source_tool=source_tool,
        confidence=confidence,
        summary=summary,
    )


def explain_run(
    run_id: str,
    *,
    trace_events: Optional[List[Dict[str, Any]]] = None,
) -> ExplanationArtifact:
    """
    Generate explanation artifact for a run.
    
    MEM-EXPLAIN-004: explain_run(run_id) API returns structured artifact.
    
    This is a placeholder implementation that creates an empty artifact.
    Full implementation would reconstruct reasoning chain from trace events.
    
    Args:
        run_id: Run ID to explain
        trace_events: Optional list of trace events for reconstruction
        
    Returns:
        ExplanationArtifact with available information
    """
    artifact = ExplanationArtifact(run_id=run_id)
    
    if trace_events:
        # Reconstruct from trace events (placeholder - would parse events)
        for event in trace_events:
            event_type = event.get("event_type", "")
            payload = event.get("payload", {})
            
            # Extract confidence evolution
            if "confidence" in event_type.lower():
                phase = payload.get("phase", "unknown")
                confidence = payload.get("confidence", 0.5)
                artifact.confidence_evolution.append(
                    ConfidencePoint(phase=phase, confidence=confidence)
                )
            
            # Extract terminal outcome
            if "terminal_outcome" in event_type.lower():
                artifact.terminal_outcome = payload.get("terminal_outcome")
                artifact.outcome_reason = payload.get("outcome_reason")
                artifact.outcome_explanation = payload.get("outcome_explanation")
    
    return artifact


def get_decision_chain(decisions: List[DecisionPoint]) -> List[str]:
    """
    Get the chain of decision IDs in order.
    
    Args:
        decisions: List of decision points
        
    Returns:
        List of decision IDs in chronological order
    """
    sorted_decisions = sorted(decisions, key=lambda d: d.timestamp)
    return [d.decision_id for d in sorted_decisions]


def trace_evidence_to_decisions(
    evidence_id: str,
    decisions: List[DecisionPoint],
) -> List[DecisionPoint]:
    """
    Find all decisions that used a specific piece of evidence.
    
    MEM-EXPLAIN-002: Evidence chain traceability.
    
    Args:
        evidence_id: Evidence ID to trace
        decisions: List of all decisions
        
    Returns:
        List of decisions that reference this evidence
    """
    return [
        d for d in decisions
        if any(e.evidence_id == evidence_id for e in d.evidence_refs)
    ]


# ==============================
# Pydantic Model Integration
# ==============================

def to_pydantic_artifact(artifact: ExplanationArtifact) -> "ExplanationArtifactModel":
    """
    Convert dataclass-based ExplanationArtifact to Pydantic model.
    
    IMP-026: Integration with Pydantic models for validation/serialization.
    
    Args:
        artifact: Dataclass-based ExplanationArtifact
        
    Returns:
        ExplanationArtifactModel (Pydantic)
    """
    from core.contracts.explanation_schema import (
        dataclass_to_pydantic_artifact,
        ExplanationArtifactModel,
    )
    return dataclass_to_pydantic_artifact(artifact.to_dict())


def explain_run_pydantic(
    run_id: str,
    *,
    trace_events: Optional[List[Dict[str, Any]]] = None,
) -> "ExplanationArtifactModel":
    """
    Generate explanation artifact for a run (Pydantic version).
    
    IMP-026: MEM-EXPLAIN-ART-001 through MEM-EXPLAIN-ART-003.
    
    Args:
        run_id: Run ID to explain
        trace_events: Optional list of trace events for reconstruction
        
    Returns:
        ExplanationArtifactModel (Pydantic) with available information
    """
    artifact = explain_run(run_id, trace_events=trace_events)
    return to_pydantic_artifact(artifact)


__all__ = [
    # Dataclass types
    "EvidenceRef",
    "DecisionPoint",
    "ReasoningStep",
    "ConfidencePoint",
    "ExplanationArtifact",
    # Factory functions
    "create_decision_point",
    "create_evidence_ref",
    # Core APIs
    "explain_run",
    "explain_run_pydantic",
    "get_decision_chain",
    "trace_evidence_to_decisions",
    # Pydantic conversion
    "to_pydantic_artifact",
]
