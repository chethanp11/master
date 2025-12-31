from __future__ import annotations

from typing import Dict, List, Optional

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from products.visual_insights.contracts.card import InsightCard
from products.visual_insights.tools.export_pdf import ExportPdfInput, export_pdf

STEP_NAME = "export"


class ExportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: List[InsightCard]
    export_requested: bool


class ExportOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_ref: Optional[Dict[str, str]]
    stub_ref: Optional[Dict[str, str]]


def run_step(inputs: ExportInput, ctx: Dict[str, str]) -> ExportOutput:
    """
    Placeholder for export step. Export tools would be triggered if requested.
    """
    run_id = ctx.get("run_id", "run_visual_insights_v1")
    export_result = export_pdf(
        ExportPdfInput(cards=inputs.cards, export_requested=True),
        run_id=run_id,
        repo_root=Path(__file__).resolve().parents[4],
    )
    return ExportOutput(export_ref=export_result.export_ref, stub_ref=export_result.stub_ref)
