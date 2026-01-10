from __future__ import annotations

# ==============================
# Advisory Agent Contracts
# ==============================
"""
Structured outputs for advisory-only agents.
"""

from typing import Any, Dict, List, Optional
from typing_extensions import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.contracts.critic_schema import MissingEvidenceRequest
from core.contracts.question_schema import Question


_MAX_RECOMMENDATIONS = 10
_MAX_REJECTIONS = 10
_MAX_LIST = 10


class ToolRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    reason: str = Field(max_length=300)
    required_inputs: Optional[Dict[str, Any]] = None
    expected_evidence_types: List[str] = Field(default_factory=list, max_length=_MAX_LIST)
    confidence: float = Field(ge=0.0, le=1.0)


class ToolRejection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    reason: str = Field(max_length=300)


class ToolSelectorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommended_tools: List[ToolRecommendation] = Field(default_factory=list, max_length=_MAX_RECOMMENDATIONS)
    rejected_tools: List[ToolRejection] = Field(default_factory=list, max_length=_MAX_REJECTIONS)
    assumptions: List[str] = Field(default_factory=list, max_length=_MAX_LIST)
    unknowns: List[str] = Field(default_factory=list, max_length=_MAX_LIST)


class AgentRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_name: str
    reason: str = Field(max_length=300)
    confidence: float = Field(ge=0.0, le=1.0)


class AgentRejection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_name: str
    reason: str = Field(max_length=300)


class AgentSelectorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommended_agents: List[AgentRecommendation] = Field(default_factory=list, max_length=_MAX_RECOMMENDATIONS)
    rejected_agents: List[AgentRejection] = Field(default_factory=list, max_length=_MAX_REJECTIONS)
    assumptions: List[str] = Field(default_factory=list, max_length=_MAX_LIST)
    unknowns: List[str] = Field(default_factory=list, max_length=_MAX_LIST)


class GapFinderOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    missing_evidence: List[MissingEvidenceRequest] = Field(default_factory=list, max_length=_MAX_RECOMMENDATIONS)
    missing_fields: List[str] = Field(default_factory=list, max_length=_MAX_LIST)
    questions_for_user: List[Question] = Field(default_factory=list, max_length=_MAX_LIST)
    confidence: float = Field(ge=0.0, le=1.0)


class SummarizerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(max_length=1000)
    key_points: List[str] = Field(default_factory=list, max_length=_MAX_LIST)
    evidence_refs: List[str] = Field(default_factory=list, max_length=_MAX_LIST)


class RiskFactor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factor: str = Field(max_length=200)
    rationale: str = Field(max_length=500)
    evidence_refs: List[str] = Field(default_factory=list, max_length=_MAX_LIST)
    severity: Literal["LOW", "MED", "HIGH"]


class RiskExplainerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_factors: List[RiskFactor] = Field(default_factory=list, max_length=_MAX_RECOMMENDATIONS)
    mitigations: List[str] = Field(default_factory=list, max_length=_MAX_LIST)
    confidence: float = Field(ge=0.0, le=1.0)
    assumptions: List[str] = Field(default_factory=list, max_length=_MAX_LIST)
    unknowns: List[str] = Field(default_factory=list, max_length=_MAX_LIST)

    @field_validator("risk_factors")
    @classmethod
    def _risk_required(cls, value: List[RiskFactor]) -> List[RiskFactor]:
        if not value:
            raise ValueError("risk_factors required")
        return value
