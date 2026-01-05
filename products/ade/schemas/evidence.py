from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItemBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    kind: str
    tool_step_id: str
    dataset_id: str
    created_at_iso: str
    inputs_hash: str


class TrendEvidence(EvidenceItemBase):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["trend"]
    period_labels: List[str]
    totals: List[Dict[str, Any]] = Field(default_factory=list)
    means: List[Dict[str, Any]] = Field(default_factory=list)
    top_movers_abs: List[Dict[str, Any]] = Field(default_factory=list)
    top_movers_pct: List[Dict[str, Any]] = Field(default_factory=list)


class OutlierEvidence(EvidenceItemBase):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["outlier"]
    candidates: List[Dict[str, Any]] = Field(default_factory=list)
    method: str = "iqr"


class DataQualityEvidence(EvidenceItemBase):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["data_quality"]
    row_count: int
    deduped_row_count: int
    duplicate_count: int


class HypothesisEvidence(EvidenceItemBase):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["hypothesis"]
    hypothesis_name: str
    status: str
    reasoning: str


EvidenceItem = Union[TrendEvidence, OutlierEvidence, DataQualityEvidence, HypothesisEvidence]


class EvidenceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    product: str
    flow: str
    dataset_id: str
    intent: str
    selections: Dict[str, Any] = Field(default_factory=dict)
    items: List[EvidenceItem] = Field(default_factory=list)
    summary_stats: Dict[str, Any] = Field(default_factory=dict)
