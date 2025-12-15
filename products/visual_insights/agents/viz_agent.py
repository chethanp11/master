from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from products.visual_insights.contracts.plan import CardSpec

ChartType = Literal["line", "bar", "stacked_bar", "scatter", "table"]


class VizInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card: CardSpec
    has_time: bool
    has_category: bool
    has_x_numeric: bool
    has_y_numeric: bool


class VizOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preferred_chart: ChartType
    rationale: str


def choose_viz(payload: VizInput) -> VizOutput:
    if payload.has_time and payload.has_y_numeric:
        return VizOutput(
            preferred_chart="line",
            rationale="time data with a numeric measure favors a line chart",
        )
    if payload.has_x_numeric and payload.has_y_numeric:
        return VizOutput(
            preferred_chart="scatter",
            rationale="numeric x and y support a scatter chart",
        )
    if payload.has_category and payload.has_y_numeric:
        return VizOutput(
            preferred_chart="bar",
            rationale="categorical breakdown with numeric data uses a bar chart",
        )
    return VizOutput(
        preferred_chart="table",
        rationale="fallback to table when other heuristics do not match",
    )
