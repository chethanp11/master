from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict

from .slices import FilterSpec


class DrilldownState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_card_id: str
    applied_filters: List[FilterSpec]


class InteractionState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active_filters: List[FilterSpec]
    drilldowns: List[DrilldownState]
