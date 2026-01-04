
from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from products.ade.contracts.decision_section import DecisionSection


class DecisionPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    decision_summary: str
    confidence_level: str
    assumptions: List[str]
    limitations: List[str]
    sections: List[DecisionSection]
    trace_refs: List[Dict[str, Any]]
