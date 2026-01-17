from __future__ import annotations

import base64
import json
from string import Template
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.tools.base import BaseTool, tool
from products.ade.schemas.business_report import BusinessReport


class RenderBusinessReportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report: BusinessReport
    embed_assets: bool = True


class RenderBusinessReportOutput(BaseModel):
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


def _heatmap_stats(rows: List[List[Any]]) -> Tuple[float, float]:
    values: List[float] = []
    for row in rows:
        for cell in row[1:]:
            try:
                values.append(float(cell))
            except (TypeError, ValueError):
                continue
    if not values:
        return 0.0, 0.0
    return min(values), max(values)


def _heatmap_cell(value: Any, min_val: float, max_val: float) -> str:
    try:
        num = float(value)
    except (TypeError, ValueError):
        return "<td>-</td>"
    if max_val == min_val:
        intensity = 0.5
    else:
        intensity = (num - min_val) / (max_val - min_val)
    shade = int(255 - (intensity * 120))
    color = f"rgb({shade},{shade},{255})"
    return f"<td style=\"background:{color}\">{_escape(f'{num:,.1f}')}</td>"


def render_business_report_html(payload: RenderBusinessReportInput) -> RenderBusinessReportOutput:
    report = payload.report
    dataset_meta = (
        f"{report.series_count} series · {report.row_count} rows · "
        f"{len(report.period_labels)} periods · Generated {report.generated_at_iso}"
    )
    summary_items = "".join(f"<li>{_escape(item)}</li>" for item in report.executive_summary)
    recommendations = "".join(f"<li>{_escape(item)}</li>" for item in report.recommendations)

    findings_blocks = []
    for finding in report.key_findings:
        refs = "".join(f"<li>{_escape(str(ref))}</li>" for ref in finding.evidence_refs)
        refs_html = f"<ul class=\"refs\">{refs}</ul>" if refs else ""
        findings_blocks.append(
            f"<div class=\"card\"><h4>{_escape(finding.headline)}</h4>"
            f"<div class=\"value\">{_escape(finding.value)}</div>"
            f"<p>{_escape(finding.context)}</p>{refs_html}</div>"
        )
    findings_html = "".join(findings_blocks)
    what_changed_items = "".join(
        f"<li>{_escape(finding.headline)}: {_escape(finding.value)}</li>"
        for finding in report.key_findings[:3]
    )
    so_what_items = "".join(
        f"<li>{_escape(finding.context)}</li>"
        for finding in report.key_findings[:2]
        if finding.context
    )
    what_next_items = recommendations

    line_visual = next((v for v in report.visuals if v.kind == "line"), None)
    heatmap_visual = next((v for v in report.visuals if v.kind == "heatmap"), None)
    line_data = line_visual.data if line_visual else {}
    heatmap_data = heatmap_visual.data if heatmap_visual else {}

    heatmap_rows = heatmap_data.get("rows") if isinstance(heatmap_data.get("rows"), list) else []
    heatmap_columns = heatmap_data.get("columns") if isinstance(heatmap_data.get("columns"), list) else report.period_labels
    min_val, max_val = _heatmap_stats(heatmap_rows)

    heatmap_body = []
    for row in heatmap_rows:
        if not row:
            continue
        row_label = _escape(str(row[0]))
        cells = "".join(_heatmap_cell(cell, min_val, max_val) for cell in row[1:])
        heatmap_body.append(f"<tr><td class=\"row-label\">{row_label}</td>{cells}</tr>")
    heatmap_head = "".join(f"<th>{_escape(str(col))}</th>" for col in heatmap_columns)

    anomalies_rows = []
    for anomaly in report.anomalies:
        delta_pct = f"{anomaly.delta_pct:.1%}" if anomaly.delta_pct is not None else "-"
        anomalies_rows.append(
            "<tr>"
            f"<td>{anomaly.rank}</td>"
            f"<td>{_escape(anomaly.expense)}</td>"
            f"<td>{_escape(anomaly.period)}</td>"
            f"<td>{_escape(f'{anomaly.value:,.1f}')}</td>"
            f"<td>{_escape(f'{anomaly.baseline:,.1f}')}</td>"
            f"<td>{_escape(f'{anomaly.delta:,.1f}')}</td>"
            f"<td>{_escape(delta_pct)}</td>"
            f"<td>{_escape(anomaly.reason)}</td>"
            "</tr>"
        )
    anomalies_html = "".join(anomalies_rows) if anomalies_rows else "<tr><td colspan=\"8\">No anomalies detected.</td></tr>"

    downgrade = "".join(f"<li>{_escape(reason)}</li>" for reason in report.appendix.downgrade_reasons)
    assumptions = "".join(f"<li>{_escape(item)}</li>" for item in report.appendix.assumptions)
    limitations = "".join(f"<li>{_escape(item)}</li>" for item in report.appendix.limitations)
    trace_refs = "".join(f"<li>{_escape(str(item))}</li>" for item in report.appendix.trace_refs)

    confidence_explainer = ""
    if report.appendix.confidence.lower() == "low":
        missing = []
        if len(report.period_labels) < 6:
            missing.append("longer historical window")
        if report.series_count < 5:
            missing.append("broader series coverage")
        missing.append("validated anomaly labels")
        missing_text = ", ".join(missing)
        confidence_explainer = (
            "<div class=\"confidence-card\">"
            "<h4>Why confidence is low</h4>"
            f"<p>Missing: {missing_text}.</p>"
            "<p>Impact: interpret the findings as directional signals, not precise forecasts.</p>"
            "<p>Raise confidence: add more periods, validate outliers, and segment by key drivers.</p>"
            "</div>"
        )

    line_json = json.dumps(line_data)
    template = Template("""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$title</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    :root {{
      --ink: #1a1f2b;
      --muted: #5c6477;
      --border: #e2e6ef;
      --bg: #f6f8fb;
      --card: #ffffff;
      --accent: #1f4f99;
    }}
    body {{ font-family: "Source Sans 3", "Helvetica Neue", Arial, sans-serif; margin: 0; color: var(--ink); background: var(--bg); }}
    header {{ padding: 28px 36px 20px; background: var(--card); border-bottom: 1px solid var(--border); }}
    h1 {{ margin: 0 0 6px; font-size: 28px; }}
    .meta {{ color: var(--muted); font-size: 0.95rem; }}
    main {{ padding: 28px 36px 40px; max-width: 1200px; margin: 0 auto; }}
    section {{ margin-bottom: 28px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
    .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
    .value {{ font-size: 20px; font-weight: 600; color: var(--accent); margin: 6px 0; }}
    ul {{ padding-left: 18px; margin: 8px 0 0; }}
    .chart {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th, td {{ border: 1px solid var(--border); padding: 6px 8px; text-align: right; }}
    th {{ background: #f0f3f9; text-align: center; }}
    td.row-label {{ text-align: left; font-weight: 600; background: #f8f9fc; }}
    .confidence-card {{ background: #fff7e6; border: 1px solid #f5d7a1; border-radius: 10px; padding: 12px 16px; }}
    details {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px; }}
    summary {{ font-weight: 600; cursor: pointer; }}
    .refs {{ margin-top: 6px; color: var(--muted); }}
  </style>
</head>
<body>
  <header>
    <h1>$title</h1>
    <div class="meta">Dataset: $dataset_id · $dataset_meta</div>
    <div class="meta">Advisory findings only; human decision required before action.</div>
  </header>
  <main>
    <section class="card">
      <h2>Executive summary</h2>
      <ul>$summary_items</ul>
    </section>

    $confidence_explainer

    <section class="card">
      <h2>What changed?</h2>
      <ul>$what_changed_items</ul>
    </section>

    <section class="card">
      <h2>So what?</h2>
      <ul>$so_what_items</ul>
    </section>

    <section>
      <h2>Key findings</h2>
      <div class="grid">$findings_html</div>
    </section>

    <section class="chart">
      <h2>$line_title</h2>
      <div id="primary-chart" style="height: 420px;"></div>
    </section>

    <section class="chart">
      <h2>$heatmap_title</h2>
      <table>
        <thead>
          <tr><th>Expense</th>$heatmap_head</tr>
        </thead>
        <tbody>
          $heatmap_body
        </tbody>
      </table>
    </section>

    <section class="chart">
      <h2>Anomaly candidates</h2>
      <table>
        <thead>
          <tr>
            <th>#</th><th>Expense</th><th>Period</th><th>Value</th><th>Baseline</th><th>Delta</th><th>Delta %</th><th>Reason</th>
          </tr>
        </thead>
        <tbody>
          $anomalies_html
        </tbody>
      </table>
    </section>

    <section class="card">
      <h2>What next?</h2>
      <ul>$what_next_items</ul>
    </section>

    <details>
      <summary>Appendix (Technical)</summary>
      <p><strong>Confidence:</strong> $confidence</p>
      <h4>Downgrade reasons</h4>
      <ul>$downgrade</ul>
      <h4>Assumptions</h4>
      <ul>$assumptions</ul>
      <h4>Limitations</h4>
      <ul>$limitations</ul>
      <h4>Trace references</h4>
      <ul>$trace_refs</ul>
    </details>
  </main>

  <script>
    const chartData = $line_json;
    const periods = chartData.periods || [];
    const series = chartData.series || [];
    const traces = series.map(item => ({
      x: periods,
      y: item.values,
      name: item.name,
      mode: 'lines+markers'
    }));
    Plotly.newPlot('primary-chart', traces, {{
      margin: {{ t: 20, r: 20, l: 50, b: 40 }},
      legend: {{ orientation: 'h' }},
      xaxis: {{ title: 'Period' }},
      yaxis: {{ title: 'Value' }},
    }}, {{displayModeBar: false}});
  </script>
</body>
</html>""")
    html = template.safe_substitute(
        title=_escape(report.title),
        dataset_id=_escape(report.dataset_id),
        dataset_meta=_escape(dataset_meta),
        summary_items=summary_items,
        confidence_explainer=confidence_explainer,
        findings_html=findings_html,
        what_changed_items=what_changed_items,
        so_what_items=so_what_items or "<li>Key impacts summarized in findings.</li>",
        what_next_items=what_next_items,
        line_title=_escape(line_visual.title if line_visual else "Primary chart"),
        heatmap_title=_escape(heatmap_visual.title if heatmap_visual else "Heatmap"),
        heatmap_head=heatmap_head,
        heatmap_body="".join(heatmap_body),
        anomalies_html=anomalies_html,
        confidence=_escape(report.appendix.confidence),
        downgrade=downgrade,
        assumptions=assumptions,
        limitations=limitations,
        trace_refs=trace_refs,
        line_json=line_json,
    )

    output_files: List[Dict[str, Any]] = []
    if payload.embed_assets:
        encoded = base64.b64encode(html.encode("utf-8")).decode("ascii")
        output_files.append(
            {
                "name": "business_report.html",
                "content_type": "text/html",
                "content_base64": encoded,
                "role": "primary",
            }
        )
    return RenderBusinessReportOutput(html=html, output_files=output_files)


@tool(
    name="render_business_report_html",
    description="Renders a BusinessReport into an analyst-ready HTML report with charts and tables.",
    capabilities=["html_rendering", "report_visualization", "chart_generation"],
    read_only=True,
    side_effect=False,
    sensitivity_class="LOW",
    cost_hint="MED",
)
class RenderBusinessReportHtmlTool(BaseTool):
    name = "render_business_report_html"
    description = "Renders a BusinessReport into an analyst-ready HTML report."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: Any) -> ToolResult:
        try:
            payload = RenderBusinessReportInput.model_validate(params or {})
            output = render_business_report_html(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except ValidationError as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=f"validation_error: {exc.errors()}")
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> RenderBusinessReportHtmlTool:
    return RenderBusinessReportHtmlTool()
