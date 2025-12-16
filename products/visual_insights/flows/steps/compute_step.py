from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, ConfigDict

from products.visual_insights.contracts.plan import InsightPlan
from products.visual_insights.contracts.refs import DatasetRef

STEP_NAME = "compute"
from products.visual_insights.contracts.refs import DatasetRef


class ComputeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan: InsightPlan
    dataset_refs: List[DatasetRef]


class ComputeOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    computed_metrics_per_card: Dict[str, Dict[str, float]]


def run_step(inputs: ComputeInput, ctx: Dict[str, str]) -> ComputeOutput:
    """
    Placeholder for computations and tool intents declared per plan step.
    """
    return ComputeOutput(computed_metrics_per_card={card.card_id: {} for card in inputs.plan.cards})
