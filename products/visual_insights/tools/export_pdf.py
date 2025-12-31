from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.visual_insights.contracts.card import InsightCard


class ExportPdfInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: List[InsightCard]
    export_requested: bool


class ExportPdfOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_ref: Optional[Dict[str, str]]


def export_pdf(payload: ExportPdfInput, *, run_id: str) -> ExportPdfOutput:
    if not payload.export_requested:
        return ExportPdfOutput(export_ref=None)
    return ExportPdfOutput(export_ref={"run_id": run_id, "uri": f"storage/exports/{run_id}.pdf"})


class ExportPdfTool(BaseTool):
    name = "export_pdf"
    description = "Exports insight cards to a PDF artifact (stub in v1)."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = ExportPdfInput.model_validate(params or {})
            output = export_pdf(payload, run_id=ctx.run_id)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> ExportPdfTool:
    return ExportPdfTool()
