from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from products.visual_insights.agents.insight_builder import BuilderInput, BuilderOutput, build_insight
from products.visual_insights.agents.viz_agent import VizInput, VizOutput, choose_viz
from products.visual_insights.contracts.card import InsightCard, KeyMetric
from products.visual_insights.contracts.citations import CitationRef, CsvCitation
from products.visual_insights.contracts.plan import CardSpec
from products.visual_insights.contracts.refs import DatasetRef
from products.visual_insights.flows.steps.evidence_step import EvidenceOutput

STEP_NAME = "render"


class RenderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: List[CardSpec]
    computed_metrics: Dict[str, Dict[str, float]]
    evidence: Dict[str, EvidenceOutput]
    dataset_refs: List[DatasetRef]


class RenderOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: List[InsightCard]


def _build_citation(dataset_refs: List[DatasetRef]) -> CitationRef:
    if dataset_refs:
        dataset = dataset_refs[0]
        columns = list(dataset.schema.keys())
        return CitationRef(
            type="csv",
            csv=CsvCitation(dataset_id=dataset.dataset_id, columns=columns, filters=[]),
            pdf=None,
        )
    return CitationRef(type="csv", csv=CsvCitation(dataset_id="unknown", columns=["value"], filters=[]), pdf=None)


def run_step(inputs: RenderInput, ctx: Dict[str, str]) -> RenderOutput:
    """
    Builds InsightCards calling builder and viz agents with placeholders.
    """
    results: List[InsightCard] = []
    citation = _build_citation(inputs.dataset_refs)
    for card in inputs.cards:
        evidence_entry = inputs.evidence.get(card.card_id)
        builder_input = BuilderInput(
            card=card,
            computed_metrics=inputs.computed_metrics.get(card.card_id, {}),
            evidence_summary=evidence_entry.notes if evidence_entry else [],
        )
        builder_output = build_insight(builder_input)
        viz_input = VizInput(
            card=card,
            has_time=True,
            has_category=False,
            has_x_numeric=False,
            has_y_numeric=True,
        )
        viz_output = choose_viz(viz_input)
        results.append(
            InsightCard(
                card_id=card.card_id,
                title=builder_output.title,
                chart_type=viz_output.preferred_chart,
                chart_spec={"type": viz_output.preferred_chart},
                key_metrics=[
                    KeyMetric(name=name, value=inputs.computed_metrics.get(card.card_id, {}).get(name, 0))
                    for name in builder_output.key_metric_names
                ],
                narrative=builder_output.narrative_template,
                data_slice=None,
                citations=[citation],
                assumptions=builder_output.assumptions,
            )
        )
    return RenderOutput(cards=results)
