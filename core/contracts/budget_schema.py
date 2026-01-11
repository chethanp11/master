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
    """Execution budget for reasoning passes, tool calls, and cost tracking."""

    model_config = ConfigDict(extra="forbid")

    max_passes: int = Field(default=3, ge=0)
    max_tool_calls: int = Field(default=10, ge=0)
    max_parallel_calls: int = Field(default=5, ge=0)
    max_total_cost_units: int = Field(default=20, ge=0)
    max_latency_bucket: LatencyBucket = "HIGH"
    on_exceed: BudgetExceedAction = "FAIL"
    degrade_to: Optional[Dict[str, int]] = None


class ReasoningBudget(BaseModel):
    """Specialized budget for bounded multi-pass reasoning with HITL escalation."""

    model_config = ConfigDict(extra="forbid")

    max_passes: int = Field(default=3, ge=1)
    max_tool_calls: int = Field(default=10, ge=0)
    max_parallel_calls: int = Field(default=3, ge=0)
    max_total_cost_units: float = Field(default=100.0, ge=0.0)
    max_latency_bucket: LatencyBucket = "MED"
    escalate_on_exceed: bool = Field(
        default=True,
        description="Trigger HITL escalation when budget is exceeded",
    )

    def to_budget(self) -> Budget:
        """Convert to standard Budget with HITL escalation if enabled."""
        return Budget(
            max_passes=self.max_passes,
            max_tool_calls=self.max_tool_calls,
            max_parallel_calls=self.max_parallel_calls,
            max_total_cost_units=int(self.max_total_cost_units),
            max_latency_bucket=self.max_latency_bucket,
            on_exceed="HITL" if self.escalate_on_exceed else "FAIL",
            degrade_to=None,
        )


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
