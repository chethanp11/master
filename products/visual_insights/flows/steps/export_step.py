from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from products.visual_insights.contracts.card import InsightCard

STEP_NAME = "export"


class ExportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: List[InsightCard]
    export_requested: bool


class ExportOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_ref: Optional[Dict[str, str]]


def run_step(inputs: ExportInput, ctx: Dict[str, str]) -> ExportOutput:
    """
    Placeholder for export step. Export tools would be triggered if requested.
    """
    return ExportOutput(export_ref=None)
