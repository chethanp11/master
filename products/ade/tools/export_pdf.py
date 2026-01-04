
from __future__ import annotations

import base64
import json
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.ade.contracts.card import InsightCard
from products.ade.tools.export_rendering import _build_html_bytes, _build_stub_payload, _render_cards_pdf


class ExportPdfInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: List[InsightCard]
    export_requested: bool
    output_format: str = "both"


class ExportPdfOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output_files: List[Dict[str, Any]]


def export_pdf(payload: ExportPdfInput) -> ExportPdfOutput:
    if not payload.export_requested:
        return ExportPdfOutput(output_files=[])

    stub_payload = _build_stub_payload(payload.cards)
    stub_bytes = json.dumps(stub_payload, indent=2, ensure_ascii=False).encode("utf-8")
    output_files = [
        {
            "name": "ade_stub.json",
            "content_type": "application/json",
            "content_base64": base64.b64encode(stub_bytes).decode("ascii"),
        },
    ]
    format_value = (payload.output_format or "both").strip().lower()
    if format_value in {"html", "both"}:
        html_bytes = _build_html_bytes(stub_payload)
        output_files.append(
            {
                "name": "ade.html",
                "content_type": "text/html",
                "role": "interactive",
                "content_base64": base64.b64encode(html_bytes).decode("ascii"),
            }
        )
    if format_value in {"pdf", "both"}:
        pdf_bytes = _render_cards_pdf(payload.cards)
        output_files.append(
            {
                "name": "ade.pdf",
                "content_type": "application/pdf",
                "content_base64": base64.b64encode(pdf_bytes).decode("ascii"),
            }
        )
    return ExportPdfOutput(
        output_files=output_files,
    )


class ExportPdfTool(BaseTool):
    name = "export_pdf"
    description = "Exports insight cards to a PDF artifact."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = ExportPdfInput.model_validate(params or {})
            output = export_pdf(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> ExportPdfTool:
    return ExportPdfTool()
