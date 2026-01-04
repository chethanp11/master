
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict

from .citations import CitationRef
from .slices import DataSlice


class KeyMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    value: Union[float, int, str]


class InsightCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_id: str
    title: str
    chart_type: Literal["line", "bar", "stacked_bar", "scatter", "table"]
    chart_spec: Dict[str, Any]
    key_metrics: List[KeyMetric]
    narrative: str
    data_slice: Optional[DataSlice] = None
    citations: List[CitationRef]
    assumptions: List[str]
    anomaly_summary: Optional[str] = None
    anomalies: Optional[List[Dict[str, Any]]] = None
