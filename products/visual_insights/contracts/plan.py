from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .modes import InsightMode


class PlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    description: str
    required_tools: List[str]


class CardSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_id: str
    intent: str
    preferred_chart: Optional[str] = None


class InsightPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: InsightMode
    steps: List[PlanStep]
    cards: List[CardSpec]
