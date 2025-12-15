from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, validator

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
    )
    return AssembleInsightCardOutput(card=card)
