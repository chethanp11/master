
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DecisionSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: str
    title: str
    intent: str
    narrative: str
    claim_strength: str
    visuals: Optional[List[Dict[str, Any]]] = None
    evidence_refs: Optional[List[Dict[str, Any]]] = None
    rejected_alternatives: Optional[List[str]] = None
