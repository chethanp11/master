from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from products.visual_insights.agents.insight_planner import PlannerInput, PlannerOutput, plan_insights
from products.visual_insights.contracts.modes import InsightMode
from products.visual_insights.contracts.refs import DatasetRef, DocRef

STEP_NAME = "plan"


class PlanInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: InsightMode
    prompt: Optional[str]
    dataset_refs: List[DatasetRef]
    doc_refs: List[DocRef]


class PlanOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan: PlannerOutput


def run_step(inputs: PlanInput, ctx: Dict[str, str]) -> PlanOutput:
    agent_input = PlannerInput(
        mode=inputs.mode,
        prompt=inputs.prompt,
        available_datasets=inputs.dataset_refs,
        available_docs=inputs.doc_refs,
    )
    plan = plan_insights(agent_input)
    return PlanOutput(plan=plan)
