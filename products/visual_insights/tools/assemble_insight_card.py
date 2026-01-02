from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, validator

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.visual_insights.contracts.card import InsightCard, KeyMetric
from products.visual_insights.contracts.citations import CitationRef
from products.visual_insights.contracts.slices import DataSlice

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

    @validator("citations")
    def must_have_citations(cls, value: List[CitationRef]) -> List[CitationRef]:
        if not value:
            raise ValueError("at least one citation is required")
        return value


class AssembleInsightCardOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card: InsightCard


def assemble_insight_card(payload: AssembleInsightCardInput) -> AssembleInsightCardOutput:
    card = InsightCard(
        card_id=payload.card_id,
        title=payload.title,
        chart_type=payload.chart_type,
        chart_spec=payload.chart_spec,
        key_metrics=payload.key_metrics,
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
