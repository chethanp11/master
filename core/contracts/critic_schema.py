from __future__ import annotations

# ==============================
# Critic Contracts
# ==============================
"""
Bounded critic/evaluator output contracts.
"""

from typing import List, Optional
from typing_extensions import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


EvidenceType = Literal["table", "doc", "text"]
CriticNextAction = Literal["NONE", "USER_INPUT", "HITL", "FETCH_MORE_EVIDENCE"]


class MissingEvidenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_type: EvidenceType
    description: str
    suggested_sources: Optional[List[str]] = None


class CriticOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    completeness_score: float = Field(ge=0.0, le=1.0)
    inconsistency_flags: List[str] = Field(default_factory=list)
    missing_evidence_requests: List[MissingEvidenceRequest] = Field(default_factory=list)
    confidence_adjustment: float = Field(ge=-1.0, le=1.0)
    recommended_next_action: CriticNextAction
    notes: Optional[str] = None

    @field_validator("notes")
    @classmethod
    def _limit_notes(cls, value: Optional[str]) -> Optional[str]:
        if value and len(value) > 300:
            raise ValueError("notes too long")
        return value


class CriticFailure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str
    details: dict = Field(default_factory=dict)


class CriticResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    output: Optional[CriticOutput] = None
    error: Optional[CriticFailure] = None
