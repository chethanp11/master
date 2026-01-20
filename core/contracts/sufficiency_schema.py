# ==============================
# Sufficiency State Schema (IMP-016)
# ==============================
"""
SufficiencyState and related models for tracking reasoning completeness.

Tech Spec IDs: INT-SUFF-001, INT-SUFF-002, INT-SUFF-003, INT-SUFF-004, INT-SUFF-005
BRD ID: BRD-AUTO-029

This module provides:
- Fact: Verified evidence with confidence
- Unknown: Unresolved question blocking or non-blocking
- Assumption: Assumed fact with confidence
- Gap: Missing information with priority
- SufficiencyState: Aggregate state tracking what is known/unknown
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==============================
# Priority Enum
# ==============================
class Priority(str, Enum):
    """Priority level for gaps and unknowns."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Importance(str, Enum):
    """Importance level for unknowns."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ==============================
# Fact Model
# ==============================
class Fact(BaseModel):
    """
    Verified evidence that has been confirmed.
    
    INT-SUFF-002: Facts represent verified evidence with confidence.
    """
    
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique fact identifier.",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Human-readable description of the fact.",
    )
    evidence_ref: Optional[str] = Field(
        default=None,
        description="Reference to supporting evidence item.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in this fact (0.0-1.0).",
    )


# ==============================
# Unknown Model
# ==============================
class Unknown(BaseModel):
    """
    Unresolved question that may or may not block progress.
    
    INT-SUFF-003: Unknowns represent unresolved questions.
    """
    
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique unknown identifier.",
    )
    question: str = Field(
        ...,
        min_length=1,
        description="The unresolved question.",
    )
    importance: Importance = Field(
        default=Importance.MEDIUM,
        description="How important is answering this question.",
    )
    blocking: bool = Field(
        default=False,
        description="Whether this unknown blocks progress.",
    )


# ==============================
# Assumption Model
# ==============================
class Assumption(BaseModel):
    """
    Assumed fact that has not been verified.
    
    INT-SUFF-004: Assumptions have confidence and optional evidence ref.
    """
    
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique assumption identifier.",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Human-readable description of the assumption.",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in this assumption (0.0-1.0).",
    )
    evidence_ref: Optional[str] = Field(
        default=None,
        description="Reference to supporting evidence item (if any).",
    )


# ==============================
# Gap Model
# ==============================
class Gap(BaseModel):
    """
    Missing information that needs to be gathered.
    
    INT-SUFF-005: Gaps represent missing information with priority.
    """
    
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique gap identifier.",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Description of what information is missing.",
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Priority of filling this gap.",
    )
    blocking: bool = Field(
        default=False,
        description="Whether this gap blocks progress.",
    )


# ==============================
# Sufficiency State Model
# ==============================
class SufficiencyState(BaseModel):
    """
    Aggregate state tracking what is known, unknown, assumed, and missing.
    
    INT-SUFF-001: SufficiencyState is maintained per run.
    INT-SUFF-002: Contains facts (verified evidence).
    INT-SUFF-003: Contains unknowns (unresolved questions).
    INT-SUFF-004: Contains assumptions (with confidence).
    INT-SUFF-005: Contains gaps (missing information).
    """
    
    model_config = ConfigDict(extra="forbid")
    
    run_id: str = Field(
        ...,
        description="Run ID this state belongs to.",
    )
    facts: List[Fact] = Field(
        default_factory=list,
        description="Verified evidence items.",
    )
    unknowns: List[Unknown] = Field(
        default_factory=list,
        description="Unresolved questions.",
    )
    assumptions: List[Assumption] = Field(
        default_factory=list,
        description="Assumed facts (not verified).",
    )
    gaps: List[Gap] = Field(
        default_factory=list,
        description="Missing information.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of last update.",
    )
    
    def is_sufficient(self) -> bool:
        """
        Check if state is sufficient to proceed.
        
        Returns True if there are no gaps, or all gaps are non-blocking.
        
        Returns:
            True if sufficient, False otherwise.
        """
        if not self.gaps:
            return True
        return all(not gap.blocking for gap in self.gaps)
    
    def has_blocking_unknowns(self) -> bool:
        """
        Check if there are any blocking unknowns.
        
        Returns:
            True if any unknown is blocking.
        """
        return any(unknown.blocking for unknown in self.unknowns)
    
    def get_blocking_gaps(self) -> List[Gap]:
        """
        Get list of blocking gaps.
        
        Returns:
            List of gaps where blocking is True.
        """
        return [gap for gap in self.gaps if gap.blocking]
    
    def get_blocking_unknowns(self) -> List[Unknown]:
        """
        Get list of blocking unknowns.
        
        Returns:
            List of unknowns where blocking is True.
        """
        return [unknown for unknown in self.unknowns if unknown.blocking]
    
    def add_fact(self, fact: Fact) -> None:
        """Add a fact to the state."""
        self.facts.append(fact)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_unknown(self, unknown: Unknown) -> None:
        """Add an unknown to the state."""
        self.unknowns.append(unknown)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_assumption(self, assumption: Assumption) -> None:
        """Add an assumption to the state."""
        self.assumptions.append(assumption)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_gap(self, gap: Gap) -> None:
        """Add a gap to the state."""
        self.gaps.append(gap)
        self.updated_at = datetime.now(timezone.utc)
    
    def resolve_unknown(self, unknown_id: str) -> bool:
        """
        Remove an unknown by ID.
        
        Args:
            unknown_id: ID of unknown to remove.
            
        Returns:
            True if removed, False if not found.
        """
        original_len = len(self.unknowns)
        self.unknowns = [u for u in self.unknowns if u.id != unknown_id]
        if len(self.unknowns) < original_len:
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def resolve_gap(self, gap_id: str) -> bool:
        """
        Remove a gap by ID.
        
        Args:
            gap_id: ID of gap to remove.
            
        Returns:
            True if removed, False if not found.
        """
        original_len = len(self.gaps)
        self.gaps = [g for g in self.gaps if g.id != gap_id]
        if len(self.gaps) < original_len:
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def to_summary(self) -> dict:
        """
        Generate a summary of the sufficiency state.
        
        Returns:
            Dictionary with counts and blocking status.
        """
        return {
            "fact_count": len(self.facts),
            "unknown_count": len(self.unknowns),
            "assumption_count": len(self.assumptions),
            "gap_count": len(self.gaps),
            "blocking_gap_count": len(self.get_blocking_gaps()),
            "blocking_unknown_count": len(self.get_blocking_unknowns()),
            "is_sufficient": self.is_sufficient(),
        }
