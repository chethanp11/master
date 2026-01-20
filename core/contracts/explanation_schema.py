# ==============================
# Explanation Schema
# ==============================
"""
Pydantic models for Explanation Artifacts.

IMP-026: MEM-EXPLAIN-ART-001, MEM-EXPLAIN-ART-002, MEM-EXPLAIN-ART-003
BRD: BRD-OPS-060

Provides:
- ExplanationArtifactModel: Complete explanation for a run
- ReasoningStepModel: Individual reasoning step
- EvidenceRefModel: Reference to evidence used
- DecisionPointModel: Decision made during reasoning
- TerminalOutcomeSection: Terminal outcome with reason and explanation
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from core.contracts.run_schema import OutcomeReason


# ==============================
# Evidence Reference Model
# ==============================

class EvidenceRefModel(BaseModel):
    """
    Reference to a piece of evidence used in reasoning.
    
    MEM-EXPLAIN-ART-002: Evidence references within reasoning steps.
    """
    evidence_id: str = Field(..., description="Unique evidence identifier")
    source_tool: str = Field(..., description="Tool that produced this evidence")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence in evidence")
    summary: Optional[str] = Field(default=None, description="Brief summary of evidence")
    
    model_config = {"extra": "forbid"}


# ==============================
# Decision Point Model
# ==============================

class DecisionPointModel(BaseModel):
    """
    A decision point in the reasoning chain.
    
    MEM-EXPLAIN-ART-002: Decision tracking with evidence.
    """
    decision_id: str = Field(..., description="Unique decision identifier")
    step_id: Optional[str] = Field(default=None, description="Associated step ID")
    phase: str = Field(default="", description="Reasoning phase")
    decision_type: str = Field(default="", description="Type of decision")
    description: str = Field(default="", description="Human-readable description")
    evidence_refs: List[EvidenceRefModel] = Field(default_factory=list, description="Evidence used")
    source_tools: List[str] = Field(default_factory=list, description="Tools consulted")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Decision confidence")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {"extra": "forbid"}


# ==============================
# Reasoning Step Model
# ==============================

class ReasoningStepModel(BaseModel):
    """
    A step in the reasoning chain.
    
    MEM-EXPLAIN-ART-001: Reasoning steps with required fields.
    """
    step_id: str = Field(..., description="Unique step identifier")
    phase: str = Field(..., description="Reasoning phase (retrieval, reasoning, validation, etc.)")
    input_summary: str = Field(default="", description="Summary of input to this step")
    output_summary: str = Field(default="", description="Summary of output from this step")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Step confidence")
    evidence_refs: List[EvidenceRefModel] = Field(default_factory=list, description="Evidence used")
    decisions: List[DecisionPointModel] = Field(default_factory=list, description="Decisions made")
    duration_ms: Optional[int] = Field(default=None, ge=0, description="Step duration in ms")
    
    model_config = {"extra": "forbid"}


# ==============================
# Confidence Point Model
# ==============================

class ConfidencePointModel(BaseModel):
    """
    A point in the confidence evolution timeline.
    
    MEM-EXPLAIN-ART-002: Confidence evolution tracking.
    """
    phase: str = Field(..., description="Phase where confidence was recorded")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence value")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: Optional[str] = Field(default=None, description="Reason for confidence level")
    
    model_config = {"extra": "forbid"}


# ==============================
# Terminal Outcome Section
# ==============================

class TerminalOutcomeSection(BaseModel):
    """
    Terminal outcome section for explanation artifact.
    
    MEM-EXPLAIN-ART-003: Terminal outcome with reason and explanation.
    """
    outcome: str = Field(..., description="Terminal outcome value")
    outcome_reason: OutcomeReason = Field(..., description="Typed reason for outcome")
    outcome_explanation: str = Field(default="", description="Human-readable explanation")
    
    model_config = {"extra": "forbid"}


# ==============================
# Explanation Artifact Model
# ==============================

class ExplanationArtifactModel(BaseModel):
    """
    Complete explanation artifact for a run.
    
    MEM-EXPLAIN-ART-001: ExplanationArtifact includes run_id, created_at, reasoning_steps.
    MEM-EXPLAIN-ART-002: Each reasoning_step has required fields.
    MEM-EXPLAIN-ART-003: Explanation includes terminal_outcome with reason and explanation.
    """
    run_id: str = Field(..., description="Run ID this explanation is for")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this explanation was created"
    )
    reasoning_steps: List[ReasoningStepModel] = Field(
        default_factory=list,
        description="Ordered list of reasoning steps"
    )
    evidence_used: List[EvidenceRefModel] = Field(
        default_factory=list,
        description="All evidence referenced during reasoning"
    )
    decisions_made: List[DecisionPointModel] = Field(
        default_factory=list,
        description="All decisions made during reasoning"
    )
    confidence_evolution: List[ConfidencePointModel] = Field(
        default_factory=list,
        description="Confidence changes over time"
    )
    terminal_outcome: Optional[TerminalOutcomeSection] = Field(
        default=None,
        description="Terminal outcome section"
    )
    
    model_config = {"extra": "forbid"}
    
    def get_decision_chain(self) -> List[DecisionPointModel]:
        """
        Get chronological list of all decisions.
        
        Returns:
            List of decisions sorted by timestamp
        """
        all_decisions: List[DecisionPointModel] = list(self.decisions_made)
        for step in self.reasoning_steps:
            all_decisions.extend(step.decisions)
        return sorted(all_decisions, key=lambda d: d.timestamp)
    
    def trace_evidence_to_decisions(self, evidence_id: str) -> List[DecisionPointModel]:
        """
        Find all decisions that used a specific piece of evidence.
        
        Args:
            evidence_id: The evidence ID to trace
            
        Returns:
            List of decisions that reference this evidence
        """
        result: List[DecisionPointModel] = []
        for decision in self.get_decision_chain():
            for ref in decision.evidence_refs:
                if ref.evidence_id == evidence_id:
                    result.append(decision)
                    break
        return result
    
    def get_confidence_tuples(self) -> List[tuple[str, float]]:
        """Get confidence evolution as list of (phase, confidence) tuples."""
        return [(c.phase, c.confidence) for c in self.confidence_evolution]


# ==============================
# Conversion Functions
# ==============================

def dataclass_to_pydantic_evidence(evidence_dict: Dict[str, Any]) -> EvidenceRefModel:
    """
    Convert evidence dict (from dataclass) to Pydantic model.
    
    Args:
        evidence_dict: Dict from EvidenceRef.to_dict()
        
    Returns:
        EvidenceRefModel
    """
    return EvidenceRefModel(
        evidence_id=evidence_dict["evidence_id"],
        source_tool=evidence_dict["source_tool"],
        confidence=evidence_dict.get("confidence", 0.5),
        summary=evidence_dict.get("summary"),
    )


def dataclass_to_pydantic_decision(decision_dict: Dict[str, Any]) -> DecisionPointModel:
    """
    Convert decision dict (from dataclass) to Pydantic model.
    
    Args:
        decision_dict: Dict from DecisionPoint.to_dict()
        
    Returns:
        DecisionPointModel
    """
    evidence_refs = [
        dataclass_to_pydantic_evidence(e) 
        for e in decision_dict.get("evidence_refs", [])
    ]
    timestamp = decision_dict.get("timestamp")
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)
    elif timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    return DecisionPointModel(
        decision_id=decision_dict["decision_id"],
        step_id=decision_dict.get("step_id"),
        phase=decision_dict.get("phase", ""),
        decision_type=decision_dict.get("decision_type", ""),
        description=decision_dict.get("description", ""),
        evidence_refs=evidence_refs,
        source_tools=decision_dict.get("source_tools", []),
        confidence=decision_dict.get("confidence", 0.5),
        timestamp=timestamp,
    )


def dataclass_to_pydantic_step(step_dict: Dict[str, Any]) -> ReasoningStepModel:
    """
    Convert reasoning step dict (from dataclass) to Pydantic model.
    
    Args:
        step_dict: Dict from ReasoningStep.to_dict()
        
    Returns:
        ReasoningStepModel
    """
    evidence_refs = [
        dataclass_to_pydantic_evidence(e) 
        for e in step_dict.get("evidence_refs", [])
    ]
    decisions = [
        dataclass_to_pydantic_decision(d) 
        for d in step_dict.get("decisions", [])
    ]
    
    return ReasoningStepModel(
        step_id=step_dict["step_id"],
        phase=step_dict["phase"],
        input_summary=step_dict.get("input_summary", ""),
        output_summary=step_dict.get("output_summary", ""),
        confidence=step_dict.get("confidence", 0.5),
        evidence_refs=evidence_refs,
        decisions=decisions,
        duration_ms=step_dict.get("duration_ms"),
    )


def dataclass_to_pydantic_artifact(artifact_dict: Dict[str, Any]) -> ExplanationArtifactModel:
    """
    Convert full artifact dict to Pydantic model.
    
    Args:
        artifact_dict: Dict from ExplanationArtifact.to_dict()
        
    Returns:
        ExplanationArtifactModel
    """
    reasoning_steps = [
        dataclass_to_pydantic_step(s) 
        for s in artifact_dict.get("reasoning_chain", [])
    ]
    evidence_used = [
        dataclass_to_pydantic_evidence(e) 
        for e in artifact_dict.get("evidence_used", [])
    ]
    decisions_made = [
        dataclass_to_pydantic_decision(d) 
        for d in artifact_dict.get("decisions_made", [])
    ]
    confidence_evolution = []
    for c in artifact_dict.get("confidence_evolution", []):
        timestamp = c.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now(timezone.utc)
        confidence_evolution.append(ConfidencePointModel(
            phase=c["phase"],
            confidence=c["confidence"],
            timestamp=timestamp,
            reason=c.get("reason"),
        ))
    
    created_at = artifact_dict.get("created_at")
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    elif created_at is None:
        created_at = datetime.now(timezone.utc)
    
    terminal_outcome = None
    if artifact_dict.get("terminal_outcome") or artifact_dict.get("outcome_reason"):
        terminal_outcome = TerminalOutcomeSection(
            outcome=artifact_dict.get("terminal_outcome", ""),
            outcome_reason=OutcomeReason(artifact_dict.get("outcome_reason", "SUCCESS")),
            outcome_explanation=artifact_dict.get("outcome_explanation", ""),
        )
    
    return ExplanationArtifactModel(
        run_id=artifact_dict["run_id"],
        created_at=created_at,
        reasoning_steps=reasoning_steps,
        evidence_used=evidence_used,
        decisions_made=decisions_made,
        confidence_evolution=confidence_evolution,
        terminal_outcome=terminal_outcome,
    )
