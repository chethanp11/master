from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from products.visual_insights.contracts.modes import InsightMode
from products.visual_insights.contracts.plan import CardSpec, InsightPlan, PlanStep
from products.visual_insights.contracts.refs import DatasetRef, DocRef


class PlannerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: InsightMode
    prompt: Optional[str]
    available_datasets: List[DatasetRef]
    available_docs: List[DocRef]


class PlannerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan: InsightPlan
    notes: List[str]


def _make_card(card_id: str, intent: str, chart: Optional[str] = None) -> CardSpec:
    return CardSpec(card_id=card_id, intent=intent, preferred_chart=chart)


def _build_steps(mode: InsightMode) -> List[PlanStep]:
    base = [
        PlanStep(step_id="collect-data", description="collect relevant datasets and docs", required_tools=["driver_analysis"]),
        PlanStep(step_id="plan-insights", description="plan insight cards and evidence", required_tools=["recommend_chart"]),
        PlanStep(step_id="build-cards", description="assemble insight cards with narratives", required_tools=["assemble_insight_card"]),
    ]
    if mode == InsightMode.anomalies_and_drivers:
        base.append(
            PlanStep(
                step_id="analyze-drivers",
                description="identify anomalies and driver contributions",
                required_tools=["detect_anomalies", "driver_analysis"],
            )
        )
    return base


def plan_insights(payload: PlannerInput) -> PlannerOutput:
    mode = payload.mode
    cards: List[CardSpec] = []
    notes: List[str] = []

    if mode == InsightMode.summarize_dataset:
        intents = [
            "overall trend summary",
            "top categories",
            "distribution overview",
            "percentile spread",
        ]
        cards = [_make_card(f"summarize-{i}", intent) for i, intent in enumerate(intents, start=1)]
        notes.append("summary path uses broad descriptive cards")
    elif mode == InsightMode.answer_question:
        prompt = payload.prompt or "answer focused insight"
        cards = [_make_card("answer-1", f"respond to: {prompt}")]
        notes.append("created insight tailored to prompt")
    else:
        cards = [
            _make_card("anomaly-1", "anomaly detection summary"),
            _make_card("driver-1", "driver contribution breakdown"),
        ]
        notes.append("paired anomaly detection with driver story")

    plan = InsightPlan(mode=mode, steps=_build_steps(mode), cards=cards)
    return PlannerOutput(plan=plan, notes=notes)
