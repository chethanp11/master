from __future__ import annotations

# ==============================
# Action Plan Contracts
# ==============================
"""
Contracts for executable action plans.

This module consolidates:
- action_plan_schema.py (ActionPlan, PlanToolCall, PlanAgentCall, PlanStep union, PlanGateResult)
- plan_schema.py (PlanProposal, PlanProposalStep, PlanApproval, EstimatedCost)
"""

from typing import Any, Dict, List, Optional, Union
from typing_extensions import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


EvidenceType = Literal["table", "doc", "text"]


# ==============================
# Plan Proposal Models (from plan_schema)
# ==============================

class PlanProposalStep(BaseModel):
    """
    A step in a plan proposal (pre-execution phase).
    Note: Renamed from PlanStep to avoid conflict with PlanStep discriminated union.
    """
    model_config = ConfigDict(extra="forbid")

    step_id: str
    description: str
    step_type: str
    tool: Optional[str] = None
    agent: Optional[str] = None
    requires_approval: bool = False


class PlanApproval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    reason: str


class EstimatedCost(BaseModel):
    model_config = ConfigDict(extra="forbid")

    currency: str = "USD"
    amount: float = 0.0
    tokens: Optional[int] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class PlanProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    summary: str
    steps: List[PlanProposalStep]
    required_tools: List[str] = Field(default_factory=list)
    approvals: List[PlanApproval] = Field(default_factory=list)
    estimated_cost: EstimatedCost


# ==============================
# Action Plan Models (original action_plan_schema)
# ==============================

class RequiredInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str


class ExpectedEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_type: EvidenceType
    description: str


class PlanToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["tool"]
    tool_name: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    expected_evidence_types: List[EvidenceType] = Field(default_factory=list)
    read_only_expected: Optional[bool] = None


class PlanAgentCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["agent"]
    agent_name: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    expected_outputs: List[str] = Field(default_factory=list)


PlanStep = Annotated[Union[PlanToolCall, PlanAgentCall], Field(discriminator="kind")]


class ActionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    goal: str
    steps: List[PlanStep]
    required_inputs: List[RequiredInput] = Field(default_factory=list)
    expected_evidence: List[ExpectedEvidence] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class PlanRejection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: Dict[str, Any]
    reason: str


class PlanGateResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    status: Literal["APPROVED", "REJECTED", "TRUNCATED", "REQUIRES_HITL"]
    approved_steps: List[PlanStep] = Field(default_factory=list)
    rejected_steps: List[PlanRejection] = Field(default_factory=list)
    requires_hitl_for_steps: List[int] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)
    effective_budget: Optional[Dict[str, Any]] = None
    sensitivity: str = "LOW"


# ==============================
# Exports
# ==============================

__all__ = [
    # Plan Proposal (from plan_schema)
    "PlanProposalStep",
    "PlanApproval",
    "EstimatedCost",
    "PlanProposal",
    # Action Plan
    "EvidenceType",
    "RequiredInput",
    "ExpectedEvidence",
    "PlanToolCall",
    "PlanAgentCall",
    "PlanStep",
    "ActionPlan",
    "PlanRejection",
    "PlanGateResult",
]
