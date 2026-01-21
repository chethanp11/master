"""Evidence schemas for ADE.

TS-SCHEMA-EVITEM-001: EvidenceItem includes confidence field.
TS-SCHEMA-EVITEM-002: EvidenceItem includes values field.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItemBase(BaseModel):
    """Base evidence item with common fields.

    TS-SCHEMA-EVITEM-001: confidence field with 0.0-1.0 range.
    TS-SCHEMA-EVITEM-002: values field for evidence data.
    """

    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    kind: str
    tool_step_id: str
    dataset_id: str
    created_at_iso: str
    inputs_hash: str
    # TS-SCHEMA-EVITEM-001: Confidence score for this evidence item
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    # TS-SCHEMA-EVITEM-002: Extracted values from evidence
    values: Dict[str, Any] = Field(default_factory=dict)
    # TS-SCHEMA-CTX-004: Columns referenced by this evidence
    columns: List[str] = Field(default_factory=list)


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
