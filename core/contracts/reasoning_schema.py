# ==============================
# Reasoning Purpose Contract
# ==============================
"""
Reasoning purposes and lifecycle phases for LLM usage in master/.

This is a stable contract used across routing, governance, and tracing.

IMP-009: Added ReasoningPhase and phase output schemas.
IMP-034: Added ReasoningContract with mandatory phases and critique waiver.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReasoningPurpose(str, Enum):
    INSIGHT = "INSIGHT"
    PRIORITIZATION = "PRIORITIZATION"
    EXPLANATION = "EXPLANATION"
    UNCERTAINTY = "UNCERTAINTY"


# ==============================
# Reasoning Phase Enum (IMP-009)
# ==============================
class ReasoningPhase(str, Enum):
    """
    Phases of the reasoning lifecycle.
    
    ORC-REASON-001: Reasoning proceeds through 4 phases.
    """
    INTERPRET = "interpret"
    PROPOSE = "propose"
    CRITIQUE = "critique"
    RECOMMEND = "recommend"


# ==============================
# Phase Output Schemas (IMP-009)
# ==============================
class InterpretOutput(BaseModel):
    """
    Output from the INTERPRET phase.
    
    ORC-REASON-003: Each phase produces typed output artifact.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique output identifier.",
    )
    user_intent: str = Field(
        ...,
        min_length=1,
        description="Interpreted user intent.",
    )
    entities: List[str] = Field(
        default_factory=list,
        description="Extracted entities.",
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Identified constraints.",
    )
    ambiguities: List[str] = Field(
        default_factory=list,
        description="Identified ambiguities requiring clarification.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in interpretation.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class ProposeOutput(BaseModel):
    """
    Output from the PROPOSE phase.
    
    ORC-REASON-003: Each phase produces typed output artifact.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique output identifier.",
    )
    proposed_actions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of proposed actions.",
    )
    hypotheses: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Generated hypotheses.",
    )
    rationale: str = Field(
        default="",
        description="Rationale for proposals.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in proposals.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class CritiqueOutput(BaseModel):
    """
    Output from the CRITIQUE phase.
    
    ORC-REASON-003: Each phase produces typed output artifact.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique output identifier.",
    )
    issues_found: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Issues identified in proposals.",
    )
    improvements: List[str] = Field(
        default_factory=list,
        description="Suggested improvements.",
    )
    risk_assessment: Dict[str, Any] = Field(
        default_factory=dict,
        description="Risk assessment of proposals.",
    )
    verdict: str = Field(
        default="",
        description="Overall verdict (approve/reject/revise).",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in critique.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class RecommendOutput(BaseModel):
    """
    Output from the RECOMMEND phase.
    
    ORC-REASON-003: Each phase produces typed output artifact.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique output identifier.",
    )
    recommendation: str = Field(
        ...,
        min_length=1,
        description="Final recommendation.",
    )
    selected_action: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Selected action to execute.",
    )
    justification: str = Field(
        default="",
        description="Justification for recommendation.",
    )
    alternatives_considered: List[str] = Field(
        default_factory=list,
        description="Alternatives that were considered.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in recommendation.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


# ==============================
# Reasoning Contract (IMP-034)
# ==============================

# Error codes for contract violations
REASONING_CONTRACT_VIOLATION = "REASONING_CONTRACT_VIOLATION"
CRITIQUE_WAIVER_INVALID = "CRITIQUE_WAIVER_INVALID"
MANDATORY_PHASE_MISSING = "MANDATORY_PHASE_MISSING"


class ReasoningContractError(Exception):
    """Raised when a reasoning contract violation occurs."""
    
    def __init__(self, message: str, error_code: str = REASONING_CONTRACT_VIOLATION):
        self.error_code = error_code
        super().__init__(message)


class ReasoningContract(BaseModel):
    """
    Reasoning contract defining mandatory phases and critique waiver.
    
    ORC-REASON-CONTRACT-001: INTERPRET and PROPOSE are always mandatory.
    ORC-REASON-CONTRACT-002: CRITIQUE can be waived with documented reason.
    ORC-REASON-CONTRACT-003: RECOMMEND phase requires prior CRITIQUE (unless waived).
    
    Example:
        >>> contract = ReasoningContract(critique_waiver=True, waiver_reason="Low-risk query")
        >>> contract.mandatory_phases  # [INTERPRET, PROPOSE]
    """
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    critique_waiver: bool = Field(
        default=False,
        description="Whether CRITIQUE phase is waived for this flow.",
    )
    waiver_reason: str = Field(
        default="",
        description="Required explanation when critique_waiver is True.",
    )
    
    @model_validator(mode="after")
    def _validate_waiver(self) -> "ReasoningContract":
        """Validate that waiver_reason is provided when critique is waived."""
        if self.critique_waiver and not self.waiver_reason.strip():
            raise ValueError(
                "waiver_reason is required when critique_waiver is True"
            )
        return self
    
    @property
    def mandatory_phases(self) -> List[ReasoningPhase]:
        """
        Get mandatory phases for this contract.
        
        ORC-REASON-CONTRACT-001: INTERPRET and PROPOSE are always mandatory.
        """
        return [ReasoningPhase.INTERPRET, ReasoningPhase.PROPOSE]
    
    @property
    def optional_phases(self) -> List[ReasoningPhase]:
        """
        Get optional phases for this contract.
        
        Returns CRITIQUE if not waived, empty otherwise.
        """
        if self.critique_waiver:
            return []
        return [ReasoningPhase.CRITIQUE]
    
    @property
    def all_required_phases(self) -> List[ReasoningPhase]:
        """
        Get all phases required by this contract.
        
        Includes mandatory + optional (if not waived).
        """
        return self.mandatory_phases + self.optional_phases
    
    def validate_phases_present(self, phases: List[ReasoningPhase]) -> bool:
        """
        Validate that all required phases are present.
        
        Args:
            phases: List of phases to validate.
        
        Returns:
            True if all required phases are present.
        
        Raises:
            ReasoningContractError: If mandatory phases are missing.
        """
        phase_set = set(phases)
        
        # Check mandatory phases
        for phase in self.mandatory_phases:
            if phase not in phase_set:
                raise ReasoningContractError(
                    f"Mandatory phase '{phase.value}' is missing from flow",
                    error_code=MANDATORY_PHASE_MISSING,
                )
        
        # Check optional phases (if not waived)
        for phase in self.optional_phases:
            if phase not in phase_set:
                raise ReasoningContractError(
                    f"Required phase '{phase.value}' is missing (critique not waived)",
                    error_code=REASONING_CONTRACT_VIOLATION,
                )
        
        return True
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload."""
        return {
            "mandatory_phases": [p.value for p in self.mandatory_phases],
            "critique_waiver": self.critique_waiver,
            "waiver_reason": self.waiver_reason if self.critique_waiver else None,
            "all_required_phases": [p.value for p in self.all_required_phases],
        }


def get_default_reasoning_contract() -> ReasoningContract:
    """
    Get the default reasoning contract.
    
    Default requires all phases including CRITIQUE.
    """
    return ReasoningContract(critique_waiver=False)


def create_waived_contract(waiver_reason: str) -> ReasoningContract:
    """
    Create a reasoning contract with critique waived.
    
    Args:
        waiver_reason: Required explanation for waiving critique.
    
    Returns:
        ReasoningContract with critique waived.
    
    Raises:
        ValueError: If waiver_reason is empty.
    """
    return ReasoningContract(critique_waiver=True, waiver_reason=waiver_reason)
