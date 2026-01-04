from __future__ import annotations

from io import BytesIO
import base64
import json
from statistics import median
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, ConfigDict

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.visual_insights.contracts.card import InsightCard


class ExportPdfInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cards: List[InsightCard]
    export_requested: bool
    output_format: str = "both"


class ExportPdfOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output_files: List[Dict[str, Any]]


def _render_cards_pdf(cards: List[InsightCard]) -> bytes:
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
    buffer = BytesIO()
    pages[0].save(buffer, format="PDF", save_all=True, append_images=pages[1:])
    return buffer.getvalue()


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
        "cards": [_build_stub_card(card) for card in cards],
    }


def _build_stub_card(card: InsightCard) -> Dict[str, Any]:
    card_payload = card.model_dump(mode="json")
    card_payload.pop("anomaly_summary", None)
    card_payload.pop("anomalies", None)
    chart_spec = dict(card_payload.get("chart_spec") or {})
    columns, rows = _extract_chart_rows(chart_spec)
    label_idx = _label_index(chart_spec, columns)
    dataset_id = _dataset_id_from_card(card)

    insights = _build_insights(
        columns=columns,
        rows=rows,
        label_idx=label_idx,
        anomaly_summary=card.anomaly_summary,
        anomalies=card.anomalies,
    )
    card_payload["insights"] = insights
    card_payload["narrative"] = _build_narrative(insights)

    if _should_inline_rows(rows):
        card_payload["chart_spec"] = chart_spec
        return card_payload

    if rows is not None and columns is not None:
        chart_spec = dict(chart_spec)
        chart_spec["data"] = {"columns": columns}
        chart_spec["data_ref"] = {
            "dataset_id": dataset_id,
            "columns": columns,
            "filters": [],
        }
        card_payload["chart_spec"] = chart_spec
        card_payload["data_ref"] = {
            "dataset_id": dataset_id,
            "columns": columns,
            "filters": [],
        }
    return card_payload


def _extract_chart_rows(chart_spec: Dict[str, Any]) -> tuple[Optional[List[str]], Optional[List[List[Any]]]]:
    data = chart_spec.get("data")
    if not isinstance(data, dict):
        return None, None
    columns = data.get("columns")
    rows = data.get("rows")
    if not isinstance(columns, list) or not isinstance(rows, list):
        return None, None
    return [str(col) for col in columns], rows


def _label_index(chart_spec: Dict[str, Any], columns: Optional[List[str]]) -> Optional[int]:
    if not columns:
        return None
    encoding = chart_spec.get("encoding")
    if isinstance(encoding, dict):
        for key in ("x", "series"):
            field = (encoding.get(key) or {}).get("field")
            if field in columns:
                return columns.index(field)
    return 0 if columns else None


def _dataset_id_from_card(card: InsightCard) -> str:
    for citation in card.citations:
        if citation.type == "csv" and citation.csv is not None:
            return citation.csv.dataset_id
    return card.title


def _should_inline_rows(rows: Optional[List[List[Any]]]) -> bool:
    if rows is None:
        return True
    if len(rows) > 50:
        return False
    try:
        payload = json.dumps(rows, ensure_ascii=True).encode("utf-8")
        return len(payload) <= 64 * 1024
    except Exception:
        return False


def _build_insights(
    *,
    columns: Optional[List[str]],
    rows: Optional[List[List[Any]]],
    label_idx: Optional[int],
    anomaly_summary: Optional[str],
    anomalies: Optional[List[Dict[str, Any]]],
) -> Dict[str, Any]:
    anomaly_detection = _anomaly_detection_summary(anomaly_summary, anomalies)
    highlights: List[Dict[str, Any]] = []
    if columns and rows:
        highlights = _highlight_outliers(columns, rows, label_idx=label_idx)
    trend = {"majority_monotonic_increase": False}
    if columns and rows:
        trend["majority_monotonic_increase"] = _majority_monotonic_increase(columns, rows, label_idx=label_idx)
    return {
        "data_quality": {"anomaly_detection": anomaly_detection},
        "highlights": highlights,
        "trend": trend,
    }


def _anomaly_detection_summary(
    summary: Optional[str],
    anomalies: Optional[List[Dict[str, Any]]],
) -> Dict[str, Any]:
    normalized = (summary or "").strip().lower()
    anomalies_list = anomalies or []

    if normalized in {"series too short"}:
        return {
            "status": "INCONCLUSIVE",
            "reason": "series too short",
            "anomalies_count": None,
        }
    if normalized in {"no data", "no numeric columns"}:
        return {
            "status": "SKIPPED",
            "reason": summary or "no data",
            "anomalies_count": None,
        }
    if normalized == "":
        return {
            "status": "ERROR",
            "reason": "missing anomaly summary",
            "anomalies_count": None,
        }

    if normalized.startswith("found"):
        return {
            "status": "OK",
            "reason": summary or "ok",
            "anomalies_count": len(anomalies_list),
        }
    if normalized in {"no anomalies found", "no variance"}:
        return {
            "status": "OK",
            "reason": summary or "ok",
            "anomalies_count": 0,
        }

    return {
        "status": "OK",
        "reason": summary or "ok",
        "anomalies_count": len(anomalies_list),
    }


def _highlight_outliers(
    columns: List[str],
    rows: List[List[Any]],
    *,
    label_idx: Optional[int],
) -> List[Dict[str, Any]]:
    numeric_idxs: List[int] = []
    for idx in range(len(columns)):
        values = [_to_float(row[idx]) for row in rows if idx < len(row)]
        cleaned = [v for v in values if v is not None]
        if cleaned and len(cleaned) == len(values):
            numeric_idxs.append(idx)

    if label_idx is not None and label_idx in numeric_idxs:
        numeric_idxs = [idx for idx in numeric_idxs if idx != label_idx]

    highlights: List[Dict[str, Any]] = []
    for idx in numeric_idxs:
        col_name = columns[idx]
        values = []
        for row in rows:
            if idx >= len(row):
                continue
            value = _to_float(row[idx])
            if value is None:
                continue
            values.append(value)
        if not values:
            continue
        med = median(values)
        max_value = max(values)
        if max_value > med * 3:
            row_id = None
            for row in rows:
                if idx >= len(row):
                    continue
                value = _to_float(row[idx])
                if value == max_value:
                    if label_idx is not None and label_idx < len(row):
                        row_id = str(row[label_idx])
                    break
            highlights.append(
                {
                    "type": "outlier_candidate",
                    "column": col_name,
                    "value": max_value,
                    "row_id": row_id,
                    "median": med,
                }
            )
    return highlights


def _build_narrative(insights: Dict[str, Any]) -> str:
    data_quality = insights.get("data_quality") or {}
    anomaly = data_quality.get("anomaly_detection") or {}
    status = anomaly.get("status")
    reason = anomaly.get("reason")
    anomalies_count = anomaly.get("anomalies_count")

    parts: List[str] = []
    if status in {"INCONCLUSIVE", "SKIPPED"}:
        parts.append(f"Anomaly detection is {status.lower()} ({reason}).")
    elif status == "ERROR":
        parts.append(f"Anomaly detection failed ({reason}).")
    elif status == "OK":
        if anomalies_count == 0:
            parts.append("No anomalies were detected by the anomaly check.")
        elif isinstance(anomalies_count, int):
            parts.append(f"Anomaly check detected {anomalies_count} anomalies.")
    else:
        parts.append("Anomaly detection status is unavailable.")

    trend = insights.get("trend") or {}
    if trend.get("majority_monotonic_increase"):
        parts.append("Most series show a monotonic increase across numeric columns.")

    highlights = insights.get("highlights") or []
    if highlights:
        outlier_lines = []
        for highlight in highlights:
            if highlight.get("type") != "outlier_candidate":
                continue
            row_id = highlight.get("row_id")
            column = highlight.get("column")
            value = highlight.get("value")
            if row_id:
                outlier_lines.append(f"{row_id} has {column}={value}")
            else:
                outlier_lines.append(f"{column} has {value}")
        if outlier_lines:
            parts.append("Outlier candidates: " + "; ".join(outlier_lines) + ".")
    return " ".join(parts).strip()


def _majority_monotonic_increase(
    columns: List[str],
    rows: List[List[Any]],
    *,
    label_idx: Optional[int],
) -> bool:
    numeric_idxs: List[int] = []
    for idx in range(len(columns)):
        if label_idx is not None and idx == label_idx:
            continue
        values = [_to_float(row[idx]) for row in rows if idx < len(row)]
        cleaned = [v for v in values if v is not None]
        if cleaned and len(cleaned) == len(values):
            numeric_idxs.append(idx)
    if len(numeric_idxs) < 2:
        return False
    monotonic_rows = 0
    eligible_rows = 0
    for row in rows:
        series = []
        for idx in numeric_idxs:
            if idx >= len(row):
                break
            value = _to_float(row[idx])
            if value is None:
                series = []
                break
            series.append(value)
        if len(series) < 2:
            continue
        eligible_rows += 1
        if all(series[i] <= series[i + 1] for i in range(len(series) - 1)):
            monotonic_rows += 1
    if eligible_rows == 0:
        return False
    return monotonic_rows >= (eligible_rows / 2)


def _to_float(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def export_pdf(payload: ExportPdfInput) -> ExportPdfOutput:
    if not payload.export_requested:
        return ExportPdfOutput(output_files=[])

    stub_payload = _build_stub_payload(payload.cards)
    stub_bytes = json.dumps(stub_payload, indent=2, ensure_ascii=False).encode("utf-8")
    output_files = [
        {
            "name": "visualization_stub.json",
            "content_type": "application/json",
            "content_base64": base64.b64encode(stub_bytes).decode("ascii"),
        },
    ]
    format_value = (payload.output_format or "both").strip().lower()
    if format_value in {"html", "both"}:
        html_bytes = _build_html_bytes(stub_payload)
        output_files.append(
            {
                "name": "visualization.html",
                "content_type": "text/html",
                "role": "interactive",
                "content_base64": base64.b64encode(html_bytes).decode("ascii"),
            }
        )
    if format_value in {"pdf", "both"}:
        pdf_bytes = _render_cards_pdf(payload.cards)
        output_files.append(
            {
                "name": "visualization.pdf",
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


def _build_html_bytes(stub_payload: Dict[str, Any]) -> bytes:
    stub_json = json.dumps(stub_payload, ensure_ascii=False)
    stub_json = stub_json.replace("</", "<\\/")
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Visual Insights</title>
  <style>
    body { font-family: "Helvetica Neue", Arial, sans-serif; margin: 24px; color: #222; }
    .card { border: 1px solid #ddd; border-radius: 10px; padding: 16px; margin-bottom: 24px; }
    .card h2 { margin: 0 0 8px; }
    .meta { color: #666; font-size: 0.9rem; margin-bottom: 12px; }
    .layout { display: grid; grid-template-columns: 1fr; gap: 16px; }
    .chart { border: 1px solid #eee; padding: 8px; border-radius: 6px; }
    .metrics { display: flex; flex-wrap: wrap; gap: 12px; }
    .metric { background: #f7f7f7; padding: 8px 12px; border-radius: 6px; font-size: 0.9rem; }
    details { margin-top: 10px; }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th, td { border: 1px solid #eee; padding: 6px 8px; text-align: left; }
    th { cursor: pointer; background: #fafafa; position: sticky; top: 0; }
    .table-wrap { max-height: 240px; overflow: auto; border: 1px solid #eee; border-radius: 6px; }
    #tooltip { position: absolute; background: #333; color: #fff; padding: 6px 8px; border-radius: 4px; font-size: 0.8rem; pointer-events: none; opacity: 0; }
  </style>
</head>
<body>
  <h1>Visual Insights</h1>
  <div id="cards"></div>
  <div id="tooltip"></div>
  <script id="stub-data" type="application/json">__STUB_JSON__</script>
  <script>
    const stub = JSON.parse(document.getElementById('stub-data').textContent);
    const cards = Array.isArray(stub.cards) ? stub.cards : [];
    const container = document.getElementById('cards');
    const tooltip = document.getElementById('tooltip');

    function showTooltip(text, x, y) {
      tooltip.textContent = text;
      tooltip.style.left = (x + 12) + 'px';
      tooltip.style.top = (y + 12) + 'px';
      tooltip.style.opacity = 1;
    }
    function hideTooltip() {
      tooltip.style.opacity = 0;
    }

    function buildMetric(metric) {
      const el = document.createElement('div');
      el.className = 'metric';
      el.textContent = metric.name + ': ' + metric.value;
      return el;
    }

    function buildNarrative(card) {
      const details = document.createElement('details');
      details.open = true;
      const summary = document.createElement('summary');
      summary.textContent = 'Narrative';
      details.appendChild(summary);
      const p = document.createElement('p');
      p.textContent = card.narrative || '';
      details.appendChild(p);
      return details;
    }

    function buildCitations(card) {
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = 'Citations';
      details.appendChild(summary);
      const pre = document.createElement('pre');
      pre.textContent = JSON.stringify(card.citations || [], null, 2);
      details.appendChild(pre);
      return details;
    }

    function buildAssumptions(card) {
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = 'Assumptions';
      details.appendChild(summary);
      const ul = document.createElement('ul');
      (card.assumptions || []).forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        ul.appendChild(li);
      });
      details.appendChild(ul);
      return details;
    }

    function buildTable(card) {
      const data = card.chart_spec && card.chart_spec.data ? card.chart_spec.data : null;
      const columns = data && Array.isArray(data.columns) ? data.columns : [];
      const rows = data && Array.isArray(data.rows) ? data.rows.slice() : [];
      const wrap = document.createElement('div');
      wrap.className = 'table-wrap';
      if (!columns.length || !rows.length) {
        const note = document.createElement('div');
        note.textContent = 'Table data not inlined.';
        wrap.appendChild(note);
        return wrap;
      }
      const table = document.createElement('table');
      const thead = document.createElement('thead');
      const tr = document.createElement('tr');
      columns.forEach((col, idx) => {
        const th = document.createElement('th');
        th.textContent = col;
        th.addEventListener('click', () => {
          const numeric = rows.every(r => !isNaN(parseFloat(r[idx])));
          rows.sort((a, b) => {
            const av = a[idx];
            const bv = b[idx];
            if (numeric) {
              return parseFloat(av) - parseFloat(bv);
            }
            return String(av).localeCompare(String(bv));
          });
          renderBody();
        });
        tr.appendChild(th);
      });
      thead.appendChild(tr);
      table.appendChild(thead);
      const tbody = document.createElement('tbody');
      table.appendChild(tbody);
      function renderBody() {
        tbody.innerHTML = '';
        rows.forEach(row => {
          const tr = document.createElement('tr');
          columns.forEach((_, idx) => {
            const td = document.createElement('td');
            td.textContent = row[idx];
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
      }
      renderBody();
      wrap.appendChild(table);
      return wrap;
    }

    function buildChart(card) {
      const data = card.chart_spec && card.chart_spec.data ? card.chart_spec.data : null;
      const columns = data && Array.isArray(data.columns) ? data.columns : [];
      const rows = data && Array.isArray(data.rows) ? data.rows : [];
      const encoding = card.chart_spec && card.chart_spec.encoding ? card.chart_spec.encoding : {};
      if (!columns.length || !rows.length) {
        const empty = document.createElement('div');
        empty.textContent = 'Chart data not inlined.';
        return empty;
      }
      let xField = encoding.x && encoding.x.field ? encoding.x.field : columns[0];
      let yField = encoding.y && encoding.y.field ? encoding.y.field : columns.find(c => c !== xField) || columns[1];
      const xIdx = columns.indexOf(xField);
      const yIdx = columns.indexOf(yField);
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', '640');
      svg.setAttribute('height', '260');
      const maxVal = Math.max(...rows.map(r => parseFloat(r[yIdx]) || 0), 1);
      const barWidth = 640 / Math.max(rows.length, 1);
      rows.forEach((row, idx) => {
        const value = parseFloat(row[yIdx]) || 0;
        const height = (value / maxVal) * 220;
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', String(idx * barWidth + 2));
        rect.setAttribute('y', String(240 - height));
        rect.setAttribute('width', String(barWidth - 4));
        rect.setAttribute('height', String(height));
        rect.setAttribute('fill', '#4a90e2');
        rect.addEventListener('mousemove', (evt) => {
          const label = row[xIdx];
          showTooltip(label + ': ' + value, evt.clientX, evt.clientY);
        });
        rect.addEventListener('mouseleave', hideTooltip);
        svg.appendChild(rect);
      });
      return svg;
    }

    cards.forEach(card => {
      const wrapper = document.createElement('div');
      wrapper.className = 'card';
      const title = document.createElement('h2');
      title.textContent = card.title || 'Insight';
      wrapper.appendChild(title);
      const meta = document.createElement('div');
      meta.className = 'meta';
      meta.textContent = 'Chart type: ' + (card.chart_type || 'unknown');
      wrapper.appendChild(meta);

      const metrics = document.createElement('div');
      metrics.className = 'metrics';
      (card.key_metrics || []).forEach(metric => metrics.appendChild(buildMetric(metric)));
      wrapper.appendChild(metrics);

      const layout = document.createElement('div');
      layout.className = 'layout';
      const chartWrap = document.createElement('div');
      chartWrap.className = 'chart';
      chartWrap.appendChild(buildChart(card));
      layout.appendChild(chartWrap);
      layout.appendChild(buildTable(card));
      wrapper.appendChild(layout);
      wrapper.appendChild(buildNarrative(card));
      wrapper.appendChild(buildCitations(card));
      wrapper.appendChild(buildAssumptions(card));
      container.appendChild(wrapper);
    });
  </script>
</body>
</html>
"""
    html = html.replace("__STUB_JSON__", stub_json)
    return html.encode("utf-8")
