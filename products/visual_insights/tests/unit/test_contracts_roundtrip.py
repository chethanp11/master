from __future__ import annotations

from typing import List

from products.visual_insights.contracts.card import InsightCard, KeyMetric
from products.visual_insights.contracts.citations import CitationRef
from products.visual_insights.contracts.io import RunResponse, UploadRequest
from products.visual_insights.contracts.modes import InsightMode
from products.visual_insights.contracts.plan import InsightPlan, PlanStep, CardSpec
from products.visual_insights.contracts.refs import FileRef


def _roundtrip(model, data):
    dump = model.model_dump()
    return model.__class__.model_validate(dump)


def test_upload_request_roundtrip():
    upload = UploadRequest(
        files=[FileRef(file_id="f1", file_type="csv", name="dataset.csv")],
        mode=InsightMode.summarize_dataset,
        prompt="Explain metrics",
    )
    new = _roundtrip(upload, {})
    assert new.files[0].name == "dataset.csv"
    assert new.mode == InsightMode.summarize_dataset


def test_insight_plan_roundtrip():
    plan = InsightPlan(
        mode=InsightMode.answer_question,
        steps=[PlanStep(step_id="plan", description="Plan insight", required_tools=["detect_anomalies"])],
        cards=[CardSpec(card_id="c1", intent="answer", preferred_chart="line")],
    )
    new = _roundtrip(plan, {})
    assert new.mode == InsightMode.answer_question
    assert new.cards[0].preferred_chart == "line"


def test_run_response_roundtrip():
    card = InsightCard(
        card_id="c1",
        title="Insights",
        chart_type="table",
        chart_spec={"type": "table"},
        key_metrics=[KeyMetric(name="m1", value=42)],
        narrative="Story",
        data_slice=None,
        citations=[CitationRef(type="csv", csv=None, pdf=None)],
        assumptions=["assumption"],
    )
    resp = RunResponse(run_id="run1", session_id="session1", cards=[card])
    new = _roundtrip(resp, {})
    assert new.run_id == "run1"
    assert new.cards[0].title == "Insights"
