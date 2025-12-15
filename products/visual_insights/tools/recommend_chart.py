from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

ChartType = Literal["line", "bar", "stacked_bar", "scatter", "table"]


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


def recommend_chart(payload: RecommendChartInput) -> RecommendChartOutput:
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

    return RecommendChartOutput(chart_type=chart_type, rationale=rationale)
