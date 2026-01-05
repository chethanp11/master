
from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, ConfigDict


class FilterSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: str
    op: Literal["=", "!=", ">", ">=", "<", "<=", "in"]
    value: Any


class GroupBySpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: List[str]


class TimeWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: Optional[str] = None
    end: Optional[str] = None


class DataSlice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filters: List[FilterSpec]
    group_by: Optional[GroupBySpec] = None
    time_window: Optional[TimeWindow] = None
