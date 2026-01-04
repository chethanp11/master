
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, validator

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool

ChartType = Literal["line", "bar", "stacked_bar", "scatter", "table"]
ChartInputType = Literal["auto", "line", "bar", "stacked_bar", "scatter", "table"]


class ChartData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: List[str]
    rows: List[List[Any]]

    @validator("rows", each_item=True)
    def row_matches_columns(cls, row: List[Any], values: Dict[str, Any]) -> List[Any]:
        columns = values.get("columns") or []
        if len(row) != len(columns):
            raise ValueError("row length must match columns")
        return row


class BuildChartSpecInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_type: ChartInputType
    fallback_chart_type: Optional[ChartType] = None
    title: str
    x: Optional[str] = None
    y: Optional[str] = None
    series: Optional[str] = None
    data: ChartData
    evidence_ref: Optional[Dict[str, Any]] = None


class BuildChartSpecOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_spec: Dict[str, Any]
    summary: str
    purpose: str = "evidence_rendering"
    caveats: List[str] = []
    optional: bool = True


def build_chart_spec(payload: BuildChartSpecInput) -> BuildChartSpecOutput:
    columns = payload.data.columns
    chart_type: ChartType = payload.fallback_chart_type or "bar"
    if payload.chart_type != "auto":
        chart_type = payload.chart_type  # type: ignore[assignment]
    caveats: List[str] = ["charts_optional", "does_not_influence_analysis"]
    evidence_ref = payload.evidence_ref
    if evidence_ref is None:
        caveats.append("missing_evidence_ref")
        evidence_ref = {"columns": columns}
    spec: Dict[str, Any] = {
        "type": chart_type,
        "title": payload.title,
        "data": {"columns": columns},
        "data_ref": evidence_ref,
    }
    encoding: Dict[str, Dict[str, str]] = {}
    if chart_type == "table":
        spec["encoding"] = encoding
    else:
        if payload.x is None or payload.x not in columns:
            raise ValueError("missing or unknown x field")
        if payload.y is None or payload.y not in columns:
            raise ValueError("missing or unknown y field")
        encoding["x"] = {"field": payload.x}
        encoding["y"] = {"field": payload.y}
        if chart_type == "stacked_bar":
            if payload.series is None or payload.series not in columns:
                raise ValueError("missing or unknown series field")
            encoding["series"] = {"field": payload.series}
        spec["encoding"] = encoding
    summary = f"built spec for {chart_type}"
    return BuildChartSpecOutput(
        chart_spec=spec,
        summary=summary,
        caveats=caveats,
    )


class BuildChartSpecTool(BaseTool):
    name = "build_chart_spec"
    description = "Builds a chart specification from structured inputs."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = BuildChartSpecInput.model_validate(params or {})
            output = build_chart_spec(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> BuildChartSpecTool:
    return BuildChartSpecTool()
