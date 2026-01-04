
from __future__ import annotations

from statistics import mean, median
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, validator

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.ade.contracts.card import InsightCard, KeyMetric
from products.ade.contracts.citations import CitationRef
from products.ade.contracts.slices import DataSlice

ChartType = Literal["line", "bar", "stacked_bar", "scatter", "table"]


class AssembleInsightCardInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_id: str
    title: str
    chart_type: ChartType
    chart_spec: Dict[str, object]
    narrative: str
    key_metrics: List[KeyMetric]
    data_slice: Optional[DataSlice] = None
    citations: List[CitationRef]
    assumptions: List[str] = Field(default_factory=list)
    anomaly_summary: Optional[str] = None
    anomalies: Optional[List[Dict[str, Any]]] = None
    primary_metric: Optional[str] = None

    @validator("citations")
    def must_have_citations(cls, value: List[CitationRef]) -> List[CitationRef]:
        if not value:
            raise ValueError("at least one citation is required")
        return value


class AssembleInsightCardOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card: InsightCard


def assemble_insight_card(payload: AssembleInsightCardInput) -> AssembleInsightCardOutput:
    key_metrics = list(payload.key_metrics)
    extra_metric = _build_primary_metric(payload.chart_spec, payload.primary_metric)
    if extra_metric:
        key_metrics.append(extra_metric)
    card = InsightCard(
        card_id=payload.card_id,
        title=payload.title,
        chart_type=payload.chart_type,
        chart_spec=payload.chart_spec,
        key_metrics=key_metrics,
        narrative=payload.narrative,
        data_slice=payload.data_slice,
        citations=payload.citations,
        assumptions=payload.assumptions,
        anomaly_summary=payload.anomaly_summary,
        anomalies=payload.anomalies,
    )
    return AssembleInsightCardOutput(card=card)


class AssembleInsightCardTool(BaseTool):
    name = "assemble_insight_card"
    description = "Assembles an InsightCard from validated inputs."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = AssembleInsightCardInput.model_validate(params or {})
            output = assemble_insight_card(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> AssembleInsightCardTool:
    return AssembleInsightCardTool()


def _build_primary_metric(chart_spec: Dict[str, object], metric: Optional[str]) -> Optional[KeyMetric]:
    if not metric:
        return None
    if not isinstance(chart_spec, dict):
        return None
    data = chart_spec.get("data")
    if not isinstance(data, dict):
        return None
    columns = data.get("columns")
    rows = data.get("rows")
    if not isinstance(columns, list) or not isinstance(rows, list):
        return None
    encoding = chart_spec.get("encoding")
    y_field = None
    if isinstance(encoding, dict):
        y_field = (encoding.get("y") or {}).get("field")
    if not y_field or y_field not in columns:
        return None
    y_idx = columns.index(y_field)
    values = []
    for row in rows:
        if y_idx >= len(row):
            continue
        value = _to_float(row[y_idx])
        if value is None:
            continue
        values.append(value)
    if not values:
        return None
    metric_key = metric.lower()
    if metric_key == "sum":
        result = sum(values)
    elif metric_key == "mean":
        result = mean(values)
    elif metric_key == "median":
        result = median(values)
    elif metric_key == "min":
        result = min(values)
    elif metric_key == "max":
        result = max(values)
    else:
        return None
    name = f"{metric_key}_{y_field}"
    return KeyMetric(name=name, value=round(result, 4))


def _to_float(value: Any) -> Optional[float]:
    # TODO: Keep local conversion to avoid cross-tool coupling; consolidate if a shared util is introduced.
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None
