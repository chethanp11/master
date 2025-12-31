from __future__ import annotations

##### Imports #####
from typing import Dict, List

from products.visual_insights.contracts.card import InsightCard
from products.visual_insights.contracts.io import RunResponse, UploadRequest
from products.visual_insights.contracts.modes import InsightMode
from products.visual_insights.flows.steps.compute_step import (
    ComputeInput,
    STEP_NAME as COMPUTE_STEP_NAME,
    run_step as compute_step,
)
from products.visual_insights.flows.steps.evidence_step import (
    EvidenceStepInput,
    STEP_NAME as EVIDENCE_STEP_NAME,
    run_step as evidence_step,
)
from products.visual_insights.flows.steps.export_step import (
    ExportInput,
    STEP_NAME as EXPORT_STEP_NAME,
    run_step as export_step,
)
from products.visual_insights.flows.steps.ingest_step import (
    IngestInput,
    STEP_NAME as INGEST_STEP_NAME,
    run_step as ingest_step,
)
from products.visual_insights.flows.steps.plan_step import (
    PlanInput,
    STEP_NAME as PLAN_STEP_NAME,
    run_step as plan_step,
)
from products.visual_insights.flows.steps.profile_index_step import (
    ProfileIndexInput,
    STEP_NAME as PROFILE_STEP_NAME,
    run_step as profile_index_step,
)
from products.visual_insights.flows.steps.render_step import (
    RenderInput,
    STEP_NAME as RENDER_STEP_NAME,
    run_step as render_step,
)


##### Trace metadata #####
STEP_TRACE_NAMES = [
    INGEST_STEP_NAME,
    PROFILE_STEP_NAME,
    PLAN_STEP_NAME,
    COMPUTE_STEP_NAME,
    EVIDENCE_STEP_NAME,
    RENDER_STEP_NAME,
    EXPORT_STEP_NAME,
]

ALLOWED_CHART_TYPES = {"line", "bar", "stacked_bar", "scatter", "table"}


##### Guardrails #####
def _validate_cards(cards: List[InsightCard]) -> None:
    for card in cards:
        if not card.citations:
            raise ValueError(f"card {card.card_id} missing citations")
        if card.chart_type not in ALLOWED_CHART_TYPES:
            raise ValueError(f"card {card.card_id} uses unsupported chart {card.chart_type}")


##### Flow entry #####
def run_visual_insights_v1(*, upload_request: UploadRequest, ctx: Dict[str, str]) -> RunResponse:
    run_id = ctx.get("run_id", "run_visual_insights_v1")
    session_id = ctx.get("session_id", "session_visual_insights_v1")

    trace_steps: List[str] = []

    def _with_trace(step_name: str, invoke):
        trace_steps.append(f"{step_name}:start")
        result = invoke()
        trace_steps.append(f"{step_name}:end")
        return result

    ingest_result = _with_trace(
        INGEST_STEP_NAME,
        lambda: ingest_step(IngestInput(request=upload_request), ctx),
    )
    _with_trace(
        PROFILE_STEP_NAME,
        lambda: profile_index_step(
            ProfileIndexInput(dataset_refs=ingest_result.dataset_refs, doc_refs=ingest_result.doc_refs),
            ctx,
        ),
    )
    mode_value = ctx.get("mode")
    mode = (
        mode_value
        if isinstance(mode_value, InsightMode)
        else InsightMode(mode_value or InsightMode.summarize_dataset)
    )
    plan_result = _with_trace(
        PLAN_STEP_NAME,
        lambda: plan_step(
            PlanInput(
                mode=mode,
                prompt=ctx.get("prompt"),
                dataset_refs=ingest_result.dataset_refs,
                doc_refs=ingest_result.doc_refs,
            ),
            ctx,
        ),
    )
    planner_output = plan_result.plan
    insight_plan = planner_output.plan
    compute_result = _with_trace(
        COMPUTE_STEP_NAME,
        lambda: compute_step(
            ComputeInput(plan=insight_plan, dataset_refs=ingest_result.dataset_refs),
            ctx,
        ),
    )
    evidence_result = _with_trace(
        EVIDENCE_STEP_NAME,
        lambda: evidence_step(
            EvidenceStepInput(
                cards=insight_plan.cards,
                dataset_refs=ingest_result.dataset_refs,
                doc_refs=ingest_result.doc_refs,
            ),
            ctx,
        ),
    )
    render_result = _with_trace(
        RENDER_STEP_NAME,
        lambda: render_step(
            RenderInput(
                cards=insight_plan.cards,
                computed_metrics=compute_result.computed_metrics_per_card,
                evidence=evidence_result.evidence_per_card,
                dataset_refs=ingest_result.dataset_refs,
            ),
            ctx,
        ),
    )
    export_result = _with_trace(
        EXPORT_STEP_NAME,
        lambda: export_step(
            ExportInput(cards=render_result.cards, export_requested=True),
            ctx,
        ),
    )

    _validate_cards(render_result.cards)
    return RunResponse(
        run_id=run_id,
        session_id=session_id,
        cards=render_result.cards,
        trace_steps=trace_steps,
    )
