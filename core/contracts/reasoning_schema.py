# ==============================
# Reasoning Purpose Contract
# ==============================
"""
Reasoning purposes and lifecycle phases for LLM usage in master/.

This is a stable contract used across routing, governance, and tracing.

IMP-009: Added ReasoningPhase and phase output schemas.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


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
