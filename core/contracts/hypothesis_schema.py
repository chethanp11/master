# ==============================
# Hypothesis Schema (IMP-014)
# ==============================
"""
Hypothesis and HypothesisSet models for reasoning hypothesis management.

Tech Spec IDs: INT-HYP-001, INT-HYP-002, INT-HYP-003, INT-HYP-004, INT-HYP-005
BRD ID: BRD-AUTO-028

This module provides:
- EvidenceRef: Reference to evidence supporting a hypothesis
- Hypothesis: Individual hypothesis with confidence and evidence
- HypothesisSet: Collection of hypotheses with freeze capability
- HypothesisSetFrozenError: Exception raised when modifying frozen set
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ==============================
# Exceptions
# ==============================
class HypothesisSetFrozenError(Exception):
    """
    Raised when attempting to modify a frozen HypothesisSet.
    
    INT-HYP-004: HypothesisSet is immutable once frozen.
    """
    
    def __init__(self, message: str = "Cannot modify frozen HypothesisSet") -> None:
        super().__init__(message)
        self.message = message


# ==============================
# Evidence Reference Model
# ==============================
class EvidenceRef(BaseModel):
    """
    Reference to evidence item supporting a hypothesis.
    
    INT-CP-EVI-001: Each EvidenceRef MUST include id, source_type, and confidence.
    INT-CP-EVI-002: Each EvidenceRef MAY include uri and tool_name.
    """
    
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(..., description="Evidence item identifier.")
    source_type: str = Field(..., description="Type of evidence source (table, doc, text, metric, etc.).")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this evidence (0.0-1.0).",
    )
    uri: Optional[str] = Field(default=None, description="Optional URI to evidence location.")
    tool_name: Optional[str] = Field(default=None, description="Tool that produced this evidence.")


# ==============================
# Hypothesis Model
# ==============================
class Hypothesis(BaseModel):
    """
    Individual hypothesis with confidence and supporting evidence.
    
    INT-HYP-001: Hypothesis MUST have id, description, confidence, evidence_refs.
    INT-HYP-002: Hypothesis confidence MUST be in range [0.0, 1.0].
    INT-HYP-003: Evidence refs limited to max 20 items.
    """
    
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique hypothesis identifier (UUID).",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Human-readable hypothesis description.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this hypothesis (0.0-1.0).",
    )
    evidence_refs: List[EvidenceRef] = Field(
        default_factory=list,
        description="Evidence supporting this hypothesis (max 20 items).",
    )
    
    @field_validator("evidence_refs")
    @classmethod
    def _validate_evidence_refs_limit(cls, value: List[EvidenceRef]) -> List[EvidenceRef]:
        """INT-HYP-003: Limit evidence refs to 20 items."""
        if len(value) > 20:
            raise ValueError("evidence_refs cannot exceed 20 items")
        return value


# ==============================
# Hypothesis Set Model
# ==============================
class HypothesisSet(BaseModel):
    """
    Collection of hypotheses with freeze capability for immutability.
    
    INT-HYP-001: HypothesisSet contains list of Hypothesis objects.
    INT-HYP-002: HypothesisSet has created_at timestamp and optional context_hash.
    INT-HYP-004: HypothesisSet is immutable once frozen.
    INT-HYP-005: All hypotheses retained in audit trail.
    """
    
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    hypotheses: List[Hypothesis] = Field(
        default_factory=list,
        description="List of hypotheses (max 10).",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when hypothesis set was created.",
    )
    context_hash: Optional[str] = Field(
        default=None,
        description="Hash of context used to generate these hypotheses.",
    )
    frozen: bool = Field(
        default=False,
        description="Whether this hypothesis set is frozen (immutable).",
    )
    
    @field_validator("hypotheses")
    @classmethod
    def _validate_hypotheses_limit(cls, value: List[Hypothesis]) -> List[Hypothesis]:
        """Limit hypotheses to 10 items per set."""
        if len(value) > 10:
            raise ValueError("hypotheses cannot exceed 10 items")
        return value
    
    def freeze(self) -> "HypothesisSet":
        """
        Freeze the hypothesis set, making it immutable.
        
        INT-HYP-004: Once frozen, no modifications are allowed.
        
        Returns:
            Self for method chaining.
            
        Raises:
            HypothesisSetFrozenError: If already frozen.
        """
        if self.frozen:
            raise HypothesisSetFrozenError("HypothesisSet is already frozen")
        # Use object.__setattr__ to bypass frozen check during freeze operation
        object.__setattr__(self, "frozen", True)
        return self
    
    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        """
        Add a hypothesis to the set.
        
        Args:
            hypothesis: Hypothesis to add.
            
        Raises:
            HypothesisSetFrozenError: If set is frozen.
            ValueError: If adding would exceed 10 hypotheses.
        """
        if self.frozen:
            raise HypothesisSetFrozenError("Cannot add hypothesis to frozen HypothesisSet")
        if len(self.hypotheses) >= 10:
            raise ValueError("Cannot add hypothesis: limit of 10 reached")
        self.hypotheses.append(hypothesis)
    
    def get_highest_confidence(self) -> Optional[Hypothesis]:
        """
        Get the hypothesis with highest confidence.
        
        Returns:
            Hypothesis with highest confidence, or None if empty.
        """
        if not self.hypotheses:
            return None
        return max(self.hypotheses, key=lambda h: h.confidence)
    
    def get_sorted_by_confidence(self) -> List[Hypothesis]:
        """
        Get hypotheses sorted by confidence (descending).
        
        Returns:
            List of hypotheses sorted by confidence.
        """
        return sorted(self.hypotheses, key=lambda h: h.confidence, reverse=True)
