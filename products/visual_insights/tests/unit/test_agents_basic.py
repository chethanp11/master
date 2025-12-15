import pytest

from products.visual_insights.agents.evidence_agent import (
    EvidenceInput,
    EvidenceOutput,
    determine_evidence,
)
from products.visual_insights.agents.insight_builder import BuilderInput, BuilderOutput, build_insight
from products.visual_insights.agents.insight_planner import (
    PlannerInput,
    PlannerOutput,
    plan_insights,
)
from products.visual_insights.agents.viz_agent import VizInput, VizOutput, choose_viz
from products.visual_insights.contracts.modes import InsightMode
from products.visual_insights.contracts.plan import CardSpec
from products.visual_insights.contracts.refs import DatasetRef, DocRef


def _sample_dataset() -> DatasetRef:
    return DatasetRef(dataset_id="ds_1", schema={"revenue": "float", "region": "str"}, row_count=1200)


def _sample_doc() -> DocRef:
    return DocRef(doc_id="doc_1", page_count=5)


def test_insight_planner_returns_plan():
    payload = PlannerInput(
        mode=InsightMode.summarize_dataset,
        prompt=None,
        available_datasets=[_sample_dataset()],
        available_docs=[_sample_doc()],
    )
    output = plan_insights(payload)
    assert isinstance(output, PlannerOutput)
    assert output.plan.mode == InsightMode.summarize_dataset
    assert output.plan.cards
    assert all(card.card_id and card.intent for card in output.plan.cards)
    assert output.plan.steps


def test_evidence_agent_handles_trend_intent():
    card = CardSpec(card_id="card_trend", intent="trend analysis", preferred_chart="line")
    payload = EvidenceInput(card=card, datasets=[_sample_dataset()], docs=[_sample_doc()])
    output = determine_evidence(payload)
    assert isinstance(output, EvidenceOutput)
    assert isinstance(output.required_csv_columns, list)
    assert isinstance(output.requires_pdf, bool)
    assert output.notes


def test_insight_builder_produces_template():
    card = CardSpec(card_id="card_build", intent="trend by region", preferred_chart="line")
    payload = BuilderInput(
        card=card,
        computed_metrics={"revenue": 100.0, "change_pct": -5},
        evidence_summary=["evidence note"],
    )
    output = build_insight(payload)
    assert isinstance(output, BuilderOutput)
    assert output.title
    assert "highlighting" in output.narrative_template
    assert isinstance(output.key_metric_names, list)
    assert isinstance(output.assumptions, list)


def test_viz_agent_prefers_allowed_chart():
    card = CardSpec(card_id="card_viz", intent="distribution", preferred_chart=None)
    payload = VizInput(
        card=card,
        has_time=True,
        has_category=False,
        has_x_numeric=False,
        has_y_numeric=True,
    )
    output = choose_viz(payload)
    assert isinstance(output, VizOutput)
    assert output.preferred_chart in {"line", "bar", "stacked_bar", "scatter", "table"}
    assert output.rationale


@pytest.mark.parametrize(
    "input_args",
    [
        {"has_time": True, "has_category": False, "has_x_numeric": False, "has_y_numeric": True},
        {"has_time": False, "has_category": True, "has_x_numeric": False, "has_y_numeric": True},
        {"has_time": False, "has_category": False, "has_x_numeric": True, "has_y_numeric": True},
        {"has_time": False, "has_category": False, "has_x_numeric": False, "has_y_numeric": False},
    ],
)
def test_viz_agent_respects_guardrails(input_args):
    card = CardSpec(card_id="card_guard", intent="guarded intent", preferred_chart=None)
    payload = VizInput(card=card, **input_args)
    output = choose_viz(payload)
    assert output.preferred_chart in {"line", "bar", "stacked_bar", "scatter", "table"}
