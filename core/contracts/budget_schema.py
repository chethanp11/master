from __future__ import annotations

# ==============================
# Budget Contracts
# ==============================
"""
Reasoning and execution budgeting contracts.
"""

from typing import Dict, List, Optional
from typing_extensions import Literal

from pydantic import BaseModel, ConfigDict, Field


LatencyBucket = Literal["LOW", "MED", "HIGH"]
BudgetExceedAction = Literal["FAIL", "HITL", "DEGRADE"]


class Budget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_passes: int = Field(default=3, ge=0)
    max_tool_calls: int = Field(default=10, ge=0)
    max_parallel_calls: int = Field(default=5, ge=0)
    max_total_cost_units: int = Field(default=20, ge=0)
    max_latency_bucket: LatencyBucket = "HIGH"
    on_exceed: BudgetExceedAction = "FAIL"
    degrade_to: Optional[Dict[str, int]] = None


class BudgetState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passes_used: int = 0
    tool_calls_used: int = 0
    parallel_calls_used: int = 0
    cost_units_used: int = 0
    latency_bucket_observed: LatencyBucket = "LOW"
    violations: List[str] = Field(default_factory=list)


class BudgetPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    defaults: Budget
    overrides_by_sensitivity: Dict[str, Budget] = Field(default_factory=dict)
    overrides_by_flow_type: Dict[str, Budget] = Field(default_factory=dict)
