
from __future__ import annotations

import base64
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.ade.contracts.decision_packet import DecisionPacket


class RenderDecisionPacketInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    packet: DecisionPacket
    embed_assets: bool = True


class RenderDecisionPacketOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    html: str
    output_files: List[Dict[str, Any]] = Field(default_factory=list)


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _render_table(columns: List[str], rows: List[List[Any]]) -> str:
    if not columns or not rows:
        return "<div class=\"note\">Table data not inlined.</div>"
    head = "".join(f"<th>{_escape(str(col))}</th>" for col in columns)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{_escape(str(cell))}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    body = "".join(body_rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _render_visual(visual: Dict[str, Any]) -> str:
    chart_spec = visual.get("chart_spec") if isinstance(visual, dict) else None
    if isinstance(chart_spec, dict):
        title = _escape(str(chart_spec.get("title") or "Chart"))
        chart_type = _escape(str(chart_spec.get("type") or "unknown"))
        data = chart_spec.get("data") if isinstance(chart_spec.get("data"), dict) else {}
        columns = data.get("columns") if isinstance(data, dict) else []
        rows = data.get("rows") if isinstance(data, dict) else []
        table_html = _render_table(columns or [], rows or [])
        return (
            f"<div class=\"visual\">"
            f"<div class=\"visual-title\">{title}</div>"
            f"<div class=\"visual-meta\">Type: {chart_type}</div>"
            f"{table_html}"
            f"</div>"
        )
    table = visual.get("table") if isinstance(visual, dict) else None
    if isinstance(table, dict):
        columns = table.get("columns") or []
        rows = table.get("rows") or []
        return f"<div class=\"visual\">{_render_table(columns, rows)}</div>"
    return f"<pre class=\"visual-json\">{_escape(str(visual))}</pre>"


def _extract_user_inputs(trace_refs: List[Any]) -> Dict[str, Any]:
    for item in trace_refs:
        if isinstance(item, dict) and "user_inputs" in item:
            user_inputs = item.get("user_inputs")
            if isinstance(user_inputs, dict):
                return user_inputs
    return {}


def render_decision_packet_html(payload: RenderDecisionPacketInput) -> RenderDecisionPacketOutput:
    packet = payload.packet
    sections_html = []
    for section in packet.sections:
        visuals = section.visuals or []
        visuals_html = "".join(_render_visual(v) for v in visuals)
        evidence_refs = section.evidence_refs or []
        evidence_html = ""
        if evidence_refs:
            items = "".join(f"<li>{_escape(str(item))}</li>" for item in evidence_refs)
            evidence_html = f"<ul class=\"evidence\">{items}</ul>"
        rejected = section.rejected_alternatives or []
        rejected_html = ""
        if rejected:
            items = "".join(f"<li>{_escape(str(item))}</li>" for item in rejected)
            rejected_html = f"<ul class=\"rejected\">{items}</ul>"
        sections_html.append(
            "<section class=\"section\">"
            f"<h2>{_escape(section.title)}</h2>"
            f"<div class=\"section-meta\">{_escape(section.intent)} · "
            f"Claim strength: {_escape(section.claim_strength)}</div>"
            f"<p>{_escape(section.narrative)}</p>"
            f"{visuals_html}"
            f"{evidence_html}"
            f"{rejected_html}"
            "</section>"
        )
    limitations = "".join(f"<li>{_escape(item)}</li>" for item in packet.limitations)
    assumptions = "".join(f"<li>{_escape(item)}</li>" for item in packet.assumptions)
    trace_refs = "".join(f"<li>{_escape(str(item))}</li>" for item in packet.trace_refs)
    user_inputs = _extract_user_inputs(packet.trace_refs)
    user_inputs_html = ""
    if user_inputs:
        items = "".join(f"<li>{_escape(str(key))}: {_escape(str(value))}</li>" for key, value in user_inputs.items())
        user_inputs_html = f"<h2>Selections</h2><ul>{items}</ul>"
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_escape(packet.question or "Decision Packet")}</title>
  <style>
    body {{ font-family: "Helvetica Neue", Arial, sans-serif; margin: 24px; color: #1a1a1a; }}
    h1 {{ margin-bottom: 4px; }}
    h2 {{ margin: 16px 0 6px; }}
    .meta {{ color: #555; font-size: 0.95rem; margin-bottom: 12px; }}
    .summary {{ padding: 12px; border: 1px solid #e0e0e0; border-radius: 8px; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    .section {{ border-top: 1px solid #eee; padding-top: 12px; margin-top: 12px; }}
    .section-meta {{ color: #666; font-size: 0.9rem; }}
    .visual {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; margin: 10px 0; }}
    .visual-title {{ font-weight: 600; }}
    .visual-meta {{ color: #666; font-size: 0.85rem; margin-bottom: 6px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th, td {{ border: 1px solid #eee; padding: 6px 8px; text-align: left; }}
    th {{ background: #fafafa; }}
    ul {{ margin: 6px 0 12px 18px; }}
    .note {{ color: #777; font-size: 0.85rem; }}
    .visual-json {{ background: #f7f7f7; padding: 8px; border-radius: 6px; overflow: auto; }}
  </style>
</head>
<body>
  <h1>{_escape(packet.question or "Decision Packet")}</h1>
  <div class="meta">Confidence: {_escape(packet.confidence_level)}</div>
  <div class="summary">
    <strong>Decision summary</strong>
    <p>{_escape(packet.decision_summary)}</p>
  </div>
  <div class="grid">
    <div>
      {user_inputs_html}
      <h2>Assumptions</h2>
      <ul>{assumptions}</ul>
      <h2>Limitations</h2>
      <ul>{limitations}</ul>
    </div>
    <div>
      <h2>Trace References</h2>
      <ul>{trace_refs}</ul>
    </div>
  </div>
  {''.join(sections_html)}
</body>
</html>"""
    output_files: List[Dict[str, Any]] = []
    if payload.embed_assets:
        encoded = base64.b64encode(html.encode("utf-8")).decode("ascii")
        output_files.append(
            {
                "name": "decision_packet.html",
                "content_type": "text/html",
                "content_base64": encoded,
                "role": "supporting",
            }
        )
    return RenderDecisionPacketOutput(html=html, output_files=output_files)


class RenderDecisionPacketHtmlTool(BaseTool):
    name = "render_decision_packet_html"
    description = "Renders a DecisionPacket into a plain HTML summary."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = RenderDecisionPacketInput.model_validate(params or {})
            output = render_decision_packet_html(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> RenderDecisionPacketHtmlTool:
    return RenderDecisionPacketHtmlTool()
