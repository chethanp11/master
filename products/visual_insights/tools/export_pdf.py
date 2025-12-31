from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict, List, Optional, Tuple

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
    stub_ref: Optional[Dict[str, str]]


def _render_cards_pdf(cards: List[InsightCard], output_path: Path) -> None:
    pages: List[Image.Image] = []
    for card in cards:
        img = Image.new("RGB", (1240, 1754), "white")
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        y = 40
        draw.text((40, y), f"{card.title}", fill="black", font=font)
        y += 28
        draw.text((40, y), f"Chart type: {card.chart_type}", fill="black", font=font)
        y += 28
        draw.text((40, y), f"Narrative: {card.narrative}", fill="black", font=font)
        y += 40
        _render_chart(draw, card.chart_spec, (40, y, 1200, 900), font=font)
        y = 980
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


def _render_chart(
    draw: ImageDraw.ImageDraw,
    chart_spec: Dict[str, Any],
    box: Tuple[int, int, int, int],
    *,
    font: ImageFont.ImageFont,
) -> None:
    chart_type = chart_spec.get("type") if isinstance(chart_spec, dict) else None
    data = (chart_spec.get("data") if isinstance(chart_spec, dict) else None) or {}
    columns = data.get("columns") or []
    rows = data.get("rows") or []
    encoding = chart_spec.get("encoding") if isinstance(chart_spec, dict) else {}
    x_field = (encoding.get("x") or {}).get("field") if isinstance(encoding, dict) else None
    y_field = (encoding.get("y") or {}).get("field") if isinstance(encoding, dict) else None
    series_field = (encoding.get("series") or {}).get("field") if isinstance(encoding, dict) else None

    x0, y0, x1, y1 = box
    draw.rectangle(box, outline="#d0d0d0", width=1)
    if not columns or not rows:
        draw.text((x0 + 10, y0 + 10), "No chart data available.", fill="black", font=font)
        return

    if chart_type == "table" or not x_field or not y_field:
        _render_table(draw, columns, rows, box, font=font)
        return

    try:
        x_index = columns.index(x_field)
        y_index = columns.index(y_field)
    except ValueError:
        _render_table(draw, columns, rows, box, font=font)
        return

    plot_left = x0 + 50
    plot_top = y0 + 20
    plot_right = x1 - 20
    plot_bottom = y1 - 40
    draw.line((plot_left, plot_bottom, plot_right, plot_bottom), fill="black", width=1)
    draw.line((plot_left, plot_top, plot_left, plot_bottom), fill="black", width=1)

    if chart_type == "scatter":
        points = []
        for row in rows:
            if x_index >= len(row) or y_index >= len(row):
                continue
            x_val = row[x_index]
            y_val = row[y_index]
            if x_val is None or y_val is None:
                continue
            try:
                x_num = float(x_val)
                y_num = float(y_val)
            except (TypeError, ValueError):
                continue
            points.append((x_num, y_num))
        if not points:
            draw.text((x0 + 10, y0 + 10), "No numeric points for scatter.", fill="black", font=font)
            return
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        _plot_scatter(draw, points, xs, ys, plot_left, plot_top, plot_right, plot_bottom)
        return

    if chart_type == "stacked_bar" and series_field:
        _plot_stacked_bar(draw, columns, rows, x_field, y_field, series_field, plot_left, plot_top, plot_right, plot_bottom, font=font)
        return

    if chart_type in {"bar", "line"}:
        labels = []
        values = []
        for row in rows:
            if x_index >= len(row) or y_index >= len(row):
                continue
            label = row[x_index]
            value = row[y_index]
            if value is None:
                continue
            try:
                y_val = float(value)
            except (TypeError, ValueError):
                continue
            labels.append(str(label))
            values.append(y_val)
        if not values:
            draw.text((x0 + 10, y0 + 10), "No numeric values for chart.", fill="black", font=font)
            return
        if chart_type == "bar":
            _plot_bar(draw, labels, values, plot_left, plot_top, plot_right, plot_bottom)
        else:
            _plot_line(draw, labels, values, plot_left, plot_top, plot_right, plot_bottom)
        return

    _render_table(draw, columns, rows, box, font=font)


def _plot_bar(draw: ImageDraw.ImageDraw, labels: List[str], values: List[float], x0: int, y0: int, x1: int, y1: int) -> None:
    max_val = max(values) if values else 1
    if max_val == 0:
        max_val = 1
    width = x1 - x0
    height = y1 - y0
    bar_width = max(1, int(width / max(len(values), 1)))
    for idx, value in enumerate(values):
        x_left = x0 + idx * bar_width
        x_right = x_left + bar_width - 2
        bar_height = int((value / max_val) * height)
        y_top = y1 - bar_height
        draw.rectangle((x_left, y_top, x_right, y1), fill="#4a90e2", outline="#2f5d8a")


def _plot_line(draw: ImageDraw.ImageDraw, labels: List[str], values: List[float], x0: int, y0: int, x1: int, y1: int) -> None:
    max_val = max(values) if values else 1
    min_val = min(values) if values else 0
    if max_val == min_val:
        max_val += 1
    width = x1 - x0
    height = y1 - y0
    step = width / max(len(values) - 1, 1)
    points = []
    for idx, value in enumerate(values):
        x = x0 + idx * step
        y = y1 - ((value - min_val) / (max_val - min_val)) * height
        points.append((x, y))
    if len(points) >= 2:
        draw.line(points, fill="#4a90e2", width=2)
    for x, y in points:
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="#2f5d8a")


def _plot_scatter(draw: ImageDraw.ImageDraw, points: List[Tuple[float, float]], xs: List[float], ys: List[float], x0: int, y0: int, x1: int, y1: int) -> None:
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    if max_x == min_x:
        max_x += 1
    if max_y == min_y:
        max_y += 1
    width = x1 - x0
    height = y1 - y0
    for x_val, y_val in points:
        x = x0 + ((x_val - min_x) / (max_x - min_x)) * width
        y = y1 - ((y_val - min_y) / (max_y - min_y)) * height
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill="#4a90e2")


def _plot_stacked_bar(
    draw: ImageDraw.ImageDraw,
    columns: List[str],
    rows: List[List[Any]],
    x_field: str,
    y_field: str,
    series_field: str,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    *,
    font: ImageFont.ImageFont,
) -> None:
    try:
        x_idx = columns.index(x_field)
        y_idx = columns.index(y_field)
        s_idx = columns.index(series_field)
    except ValueError:
        _render_table(draw, columns, rows, (x0, y0, x1, y1), font=font)
        return

    grouped: Dict[str, Dict[str, float]] = {}
    series_names: List[str] = []
    for row in rows:
        if x_idx >= len(row) or y_idx >= len(row) or s_idx >= len(row):
            continue
        x_val = row[x_idx]
        s_val = row[s_idx]
        y_val = row[y_idx]
        if x_val is None or s_val is None or y_val is None:
            continue
        try:
            y_num = float(y_val)
        except (TypeError, ValueError):
            continue
        x_key = str(x_val)
        s_key = str(s_val)
        if s_key not in series_names:
            series_names.append(s_key)
        grouped.setdefault(x_key, {})[s_key] = grouped.get(x_key, {}).get(s_key, 0) + y_num

    categories = list(grouped.keys())
    if not categories:
        draw.text((x0 + 10, y0 + 10), "No data for stacked bar.", fill="black", font=font)
        return
    totals = [sum(grouped[c].values()) for c in categories]
    max_total = max(totals) if totals else 1
    if max_total == 0:
        max_total = 1
    width = x1 - x0
    height = y1 - y0
    bar_width = max(1, int(width / max(len(categories), 1)))
    palette = ["#4a90e2", "#50e3c2", "#f5a623", "#9013fe", "#b8e986"]
    for idx, category in enumerate(categories):
        x_left = x0 + idx * bar_width
        x_right = x_left + bar_width - 2
        y_cursor = y1
        for s_idx, s_name in enumerate(series_names):
            value = grouped.get(category, {}).get(s_name, 0)
            if value == 0:
                continue
            segment_height = int((value / max_total) * height)
            y_top = y_cursor - segment_height
            color = palette[s_idx % len(palette)]
            draw.rectangle((x_left, y_top, x_right, y_cursor), fill=color, outline="#2f5d8a")
            y_cursor = y_top


def _render_table(
    draw: ImageDraw.ImageDraw,
    columns: List[str],
    rows: List[List[Any]],
    box: Tuple[int, int, int, int],
    *,
    font: ImageFont.ImageFont,
) -> None:
    x0, y0, x1, y1 = box
    col_count = max(len(columns), 1)
    col_width = (x1 - x0) / col_count
    y = y0 + 10
    for idx, col in enumerate(columns):
        draw.text((x0 + idx * col_width + 4, y), str(col), fill="black", font=font)
    y += 20
    max_rows = min(len(rows), 12)
    for row_idx in range(max_rows):
        row = rows[row_idx]
        for col_idx in range(col_count):
            value = row[col_idx] if col_idx < len(row) else ""
            draw.text((x0 + col_idx * col_width + 4, y), str(value), fill="black", font=font)
        y += 18


def _build_stub_payload(cards: List[InsightCard]) -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "format": "visual_insights_stub",
        "cards": [card.model_dump(mode="json") for card in cards],
    }


def export_pdf(payload: ExportPdfInput, *, run_id: str, repo_root: Path) -> ExportPdfOutput:
    if not payload.export_requested:
        return ExportPdfOutput(export_ref=None, stub_ref=None)

    writer = ObservabilityWriter(repo_root=repo_root)
    output_path = writer.output_path(product="visual_insights", run_id=run_id, name="visualization.pdf")
    stub_path = writer.output_path(product="visual_insights", run_id=run_id, name="visualization_stub.json")
    stub_payload = _build_stub_payload(payload.cards)
    stub_path.write_text(json.dumps(stub_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    _render_cards_pdf(payload.cards, output_path)
    return ExportPdfOutput(
        export_ref={"run_id": run_id, "uri": str(output_path)},
        stub_ref={"run_id": run_id, "uri": str(stub_path)},
    )


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
