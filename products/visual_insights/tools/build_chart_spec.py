from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, validator

ChartType = Literal["line", "bar", "stacked_bar", "scatter", "table"]


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

    chart_type: ChartType
    title: str
    x: Optional[str] = None
    y: Optional[str] = None
    series: Optional[str] = None
    data: ChartData


class BuildChartSpecOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_spec: Dict[str, Any]
    summary: str


def build_chart_spec(payload: BuildChartSpecInput) -> BuildChartSpecOutput:
    columns = payload.data.columns
    spec: Dict[str, Any] = {
        "type": payload.chart_type,
        "title": payload.title,
        "data": {"columns": columns, "rows": payload.data.rows},
    }
    encoding: Dict[str, Dict[str, str]] = {}
    if payload.chart_type == "table":
        spec["encoding"] = encoding
    else:
        if payload.x is None or payload.x not in columns:
            raise ValueError("missing or unknown x field")
        if payload.y is None or payload.y not in columns:
            raise ValueError("missing or unknown y field")
        encoding["x"] = {"field": payload.x}
        encoding["y"] = {"field": payload.y}
        if payload.chart_type == "stacked_bar":
            if payload.series is None or payload.series not in columns:
                raise ValueError("missing or unknown series field")
            encoding["series"] = {"field": payload.series}
        spec["encoding"] = encoding
    summary = f"built spec for {payload.chart_type}"
    return BuildChartSpecOutput(chart_spec=spec, summary=summary)
