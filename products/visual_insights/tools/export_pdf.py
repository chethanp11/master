from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, ConfigDict

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.visual_insights.contracts.card import InsightCard
from core.logging.observability import ObservabilityWriter


class ExportPdfInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: List[InsightCard]
    export_requested: bool


class ExportPdfOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_ref: Optional[Dict[str, str]]


def _render_cards_pdf(cards: List[InsightCard], output_path: Path) -> None:
    pages: List[Image.Image] = []
    for card in cards:
        img = Image.new("RGB", (1240, 1754), "white")
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        y = 40
        draw.text((40, y), f"{card.title}", fill="black", font=font)
        y += 40
        draw.text((40, y), f"Chart type: {card.chart_type}", fill="black", font=font)
        y += 40
        draw.text((40, y), f"Narrative: {card.narrative}", fill="black", font=font)
        y += 60
        if card.key_metrics:
            draw.text((40, y), "Key metrics:", fill="black", font=font)
            y += 30
            for metric in card.key_metrics:
                draw.text((60, y), f"- {metric.name}: {metric.value}", fill="black", font=font)
                y += 24
        pages.append(img)

    if not pages:
        pages = [Image.new("RGB", (1240, 1754), "white")]
    pages[0].save(output_path, save_all=True, append_images=pages[1:])


def export_pdf(payload: ExportPdfInput, *, run_id: str, repo_root: Path) -> ExportPdfOutput:
    if not payload.export_requested:
        return ExportPdfOutput(export_ref=None)

    writer = ObservabilityWriter(repo_root=repo_root)
    output_path = writer.output_path(product="visual_insights", run_id=run_id, name="visualization.pdf")
    _render_cards_pdf(payload.cards, output_path)
    return ExportPdfOutput(export_ref={"run_id": run_id, "uri": str(output_path)})


class ExportPdfTool(BaseTool):
    name = "export_pdf"
    description = "Exports insight cards to a PDF artifact."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = ExportPdfInput.model_validate(params or {})
            repo_root = Path(__file__).resolve().parents[3]
            output = export_pdf(payload, run_id=ctx.run_id, repo_root=repo_root)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> ExportPdfTool:
    return ExportPdfTool()
