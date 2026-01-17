from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class IntentFrame(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: str = "interpret"
    intent_summary: str
    inferred_entities: List[str] = Field(default_factory=list)
    inferred_metrics: List[str] = Field(default_factory=list)
    inferred_time_window: Optional[str] = None
    requested_outputs: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    confidence_label: str = "low"
    blocking_required: bool = False
    blocking_questions: List[str] = Field(default_factory=list)
    blocking_question: Optional[str] = None
