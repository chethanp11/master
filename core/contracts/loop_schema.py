from __future__ import annotations

# ==============================
# Loop Contracts
# ==============================
"""
Contracts for bounded, deterministic loops.
"""

from typing import Any, Dict, List, Optional, Union
from typing_extensions import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


_MAX_STOP_NODES = 20


class ConfidenceThreshold(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["confidence_threshold"]
    path: str
    op: Literal[">=", ">", "<", "<="] = ">="
    value: float


class NoMissingEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["no_missing_evidence"]
    path: str
    op: Literal["empty"] = "empty"


class StopConditionGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["all", "any"]
    conditions: List["StopConditionExpr"]

    @model_validator(mode="after")
    def _validate_group(self) -> "StopConditionGroup":
        if not self.conditions:
            raise ValueError("stop condition group must include at least one condition")
        if self._count_nodes() > _MAX_STOP_NODES:
            raise ValueError("stop condition too complex")
        return self

    def _count_nodes(self) -> int:
        return 1 + sum(_count_stop_nodes(cond) for cond in self.conditions)


StopConditionExpr = Annotated[
    Union[ConfidenceThreshold, NoMissingEvidence, StopConditionGroup],
    Field(discriminator="kind"),
]


class LoopState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    iters_used: int = 0
    terminated: bool = False
    termination_reason: str = ""
    last_evaluated_condition: Optional[Dict[str, Any]] = None
    started_at: Optional[int] = None
    ended_at: Optional[int] = None


def _count_stop_nodes(condition: StopConditionExpr) -> int:
    if isinstance(condition, StopConditionGroup):
        return condition._count_nodes()
    return 1


StopConditionGroup.model_rebuild()
