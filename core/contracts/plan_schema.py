# ==============================
# Plan Proposal Contracts
# ==============================
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PlanStep(BaseModel):
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
    steps: List[PlanStep]
    required_tools: List[str] = Field(default_factory=list)
    approvals: List[PlanApproval] = Field(default_factory=list)
    estimated_cost: EstimatedCost
