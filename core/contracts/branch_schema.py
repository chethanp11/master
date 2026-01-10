from __future__ import annotations

# ==============================
# Branching Contracts
# ==============================
"""
Deterministic condition expressions for branching.
"""

from typing import List, Optional, Union
from typing_extensions import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ConditionOp = Literal["==", "!=", ">", ">=", "<", "<=", "in", "contains", "exists"]
ConditionScalar = Union[str, int, float, bool, None]
ConditionValue = Union[ConditionScalar, List[ConditionScalar]]

_MAX_CONDITION_NODES = 20


class ConditionExpr(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: Optional[str] = None
    op: Optional[ConditionOp] = None
    value: Optional[ConditionValue] = None
    all: Optional[List["ConditionExpr"]] = Field(default=None)
    any: Optional[List["ConditionExpr"]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_shape(self) -> "ConditionExpr":
        has_path = self.path is not None or self.op is not None
        has_group = self.all is not None or self.any is not None
        if has_path and has_group:
            raise ValueError("condition cannot mix path/op with all/any")
        if not has_path and not has_group:
            raise ValueError("condition must include path/op or all/any")
        if has_path:
            if not self.path or not self.op:
                raise ValueError("condition path and op are required")
            if self.op == "exists":
                return self
            if self.value is None:
                raise ValueError("condition value is required for op")
        if self.all is not None and not self.all:
            raise ValueError("all must contain at least one condition")
        if self.any is not None and not self.any:
            raise ValueError("any must contain at least one condition")
        if self._count_nodes() > _MAX_CONDITION_NODES:
            raise ValueError("condition too complex")
        return self

    def _count_nodes(self) -> int:
        if self.all:
            return 1 + sum(child._count_nodes() for child in self.all)
        if self.any:
            return 1 + sum(child._count_nodes() for child in self.any)
        return 1


ConditionExpr.model_rebuild()
