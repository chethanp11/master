from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from products.visual_insights.contracts.plan import CardSpec


class BuilderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card: CardSpec
    computed_metrics: Dict[str, Any]
    evidence_summary: List[str]


class BuilderOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    narrative_template: str
    key_metric_names: List[str]
    assumptions: List[str]


def build_insight(payload: BuilderInput) -> BuilderOutput:
    intent = payload.card.intent.strip()
    title = intent.capitalize()
    metrics = list(payload.computed_metrics.keys())
    metric_placeholders = ", ".join(metrics[:2]) if metrics else "key metrics"
    template = (
        f"This insight shows {metric_placeholders} for {payload.card.intent}, "
        "highlighting trends within the evidence."
    )
    assumptions = payload.evidence_summary or ["derived from provided datasets"]
    return BuilderOutput(
        title=title,
        narrative_template=template,
        key_metric_names=metrics,
        assumptions=assumptions,
    )
