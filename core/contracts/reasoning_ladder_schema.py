from __future__ import annotations

# ==============================
# Reasoning Ladder Contracts
# ==============================
"""
Contracts for the multi-pass Reasoning Ladder helper.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReasoningLadderInterpret(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)


class ReasoningLadderCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str


class ReasoningLadderToolCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str
    rationale: str
    required_inputs: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ReasoningLadderAgentCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent: str
    rationale: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ReasoningLadderPropose(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidates: List[ReasoningLadderCandidate] = Field(default_factory=list)
    tool_candidates: List[ReasoningLadderToolCandidate] = Field(default_factory=list)
    agent_candidates: List[ReasoningLadderAgentCandidate] = Field(default_factory=list)


class ReasoningLadderSelect(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chosen: Dict[str, Any]
    rationale: str
    evidence_refs: List[str] = Field(default_factory=list)


class ReasoningLadderSelectPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    select: ReasoningLadderSelect
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    assumptions: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)


class ReasoningLadderOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interpret: ReasoningLadderInterpret
    propose: ReasoningLadderPropose
    select: ReasoningLadderSelect
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    assumptions: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)


class ReasoningLadderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_passes: int = 3
    max_tool_candidates: int = 3
    max_agent_candidates: int = 3
    max_candidates: int = 5
    min_confidence_to_select: Optional[float] = None


class ReasoningLadderFailure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str
    failed_pass: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ReasoningLadderResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    output: Optional[ReasoningLadderOutput] = None
    error: Optional[ReasoningLadderFailure] = None
