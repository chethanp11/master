from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    headline: str
    value: str
    context: str
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)


class VisualSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["line", "heatmap", "bar"]
    title: str
    data: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)


class AnomalyRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int
    expense: str
    period: str
    value: float
    baseline: float
    delta: float
    delta_pct: Optional[float] = None
    reason: str


class Appendix(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confidence: str
    downgrade_reasons: List[str] = Field(default_factory=list)
    trace_refs: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class BusinessReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    generated_at_iso: str
    dataset_id: str
    row_count: int
    period_labels: List[str]
    series_count: int
    executive_summary: List[str]
    key_findings: List[Finding]
    visuals: List[VisualSpec]
    anomalies: List[AnomalyRow]
    recommendations: List[str]
    appendix: Appendix
