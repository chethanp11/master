from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PlanDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str
    rationale: str


class PlanSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_summary: str
    question_type: str
    dataset_id: Optional[str] = None
    metric: Optional[str] = None
    time_window: Optional[str] = None
    chart_type: str = "line"
    aggregation: str = "total"
    tool_flags: Dict[str, bool] = Field(default_factory=dict)
    decision_points: List[PlanDecision] = Field(default_factory=list)
