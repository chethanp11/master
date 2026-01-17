from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class ContextPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_profile: Dict[str, Any]
    coverage: Dict[str, Any]
    missingness: Dict[str, Any]
    data_quality_flags: List[str] = Field(default_factory=list)
    metric_availability: List[str] = Field(default_factory=list)
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)
