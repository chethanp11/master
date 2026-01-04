
from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.ade.tools.build_chart_spec import ChartType


class RecommendChartInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str
    has_time: bool = False
    has_category: bool = False
    has_x_numeric: bool = False
    has_y_numeric: bool = True
    wants_composition: bool = False


class RecommendChartOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_type: ChartType
    rationale: str
    purpose: str = "evidence_rendering"
    caveats: List[str] = []
    optional: bool = True


def recommend_chart(payload: RecommendChartInput) -> RecommendChartOutput:
    caveats: List[str] = ["heuristic_only", "does_not_influence_analysis"]
    if payload.has_time and payload.has_y_numeric:
        chart_type: ChartType = "line"
        rationale = "time series + numeric target -> line chart"
    elif payload.has_x_numeric and payload.has_y_numeric:
        chart_type = "scatter"
        rationale = "numeric x and y -> scatter"
    elif payload.wants_composition and payload.has_category:
        chart_type = "stacked_bar"
        rationale = "composition request with category -> stacked bar"
    elif payload.has_category and payload.has_y_numeric:
        chart_type = "bar"
        rationale = "categorical breakdown with numeric measure -> bar"
    else:
        chart_type = "table"
        rationale = "fallback to table when chart heuristics do not match"

    return RecommendChartOutput(
        chart_type=chart_type,
        rationale=rationale,
        caveats=caveats,
    )


class RecommendChartTool(BaseTool):
    name = "recommend_chart"
    description = "Recommends a chart type based on basic data heuristics."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = RecommendChartInput.model_validate(params or {})
            output = recommend_chart(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> RecommendChartTool:
    return RecommendChartTool()
