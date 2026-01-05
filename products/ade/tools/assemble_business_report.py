from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.ade.contracts.decision_packet import DecisionPacket
from products.ade.schemas.business_report import (
    AnomalyRow,
    Appendix,
    BusinessReport,
    Finding,
    VisualSpec,
)
from products.ade.tools.compute_business_metrics import BusinessMetrics


class AssembleBusinessReportInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metrics: BusinessMetrics
    packet: DecisionPacket
    downgrade_reasons: List[str] = Field(default_factory=list)
    chart_type: str = "line"
    metric_focus: str = "mean"
    include_hypothesis_checks: bool = True


class AssembleBusinessReportOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report: BusinessReport


def _format_number(value: float) -> str:
    return f"{value:,.1f}" if abs(value) >= 1 else f"{value:,.3f}"


def _build_series(period_labels: List[str], rows: List[List[Any]]) -> List[Dict[str, Any]]:
    series: Dict[str, List[Optional[float]]] = {}
    for row in rows:
        if not row:
            continue
        expense = str(row[0])
        series.setdefault(expense, [None for _ in period_labels])
        for idx, _period in enumerate(period_labels, start=1):
            if idx >= len(row):
                continue
            value = row[idx]
            try:
                series[expense][idx - 1] = float(value)
            except (ValueError, TypeError):
                continue
    return [{"name": name, "values": values} for name, values in series.items()]


def assemble_business_report(payload: AssembleBusinessReportInput) -> AssembleBusinessReportOutput:
    metrics = payload.metrics
    packet = payload.packet
    now = datetime.now(tz=timezone.utc).isoformat()
    last_period = metrics.period_labels[-1] if metrics.period_labels else "latest"
    prev_period = metrics.period_labels[-2] if len(metrics.period_labels) >= 2 else "previous"

    top_abs = metrics.top_movers_abs[0] if metrics.top_movers_abs else None
    top_pct = metrics.top_movers_pct[0] if metrics.top_movers_pct else None
    total_latest = metrics.totals[-1].total if metrics.totals else 0.0
    total_prev = metrics.totals[-2].total if len(metrics.totals) >= 2 else 0.0
    total_delta = total_latest - total_prev

    exec_summary = [
        f"Dataset covers {metrics.series_count} expense series across {len(metrics.period_labels)} periods.",
        f"Overall total in {last_period} is {_format_number(total_latest)} "
        f"({('+' if total_delta >= 0 else '')}{_format_number(total_delta)} vs {prev_period}).",
    ]
    if top_abs:
        exec_summary.append(
            f"Top absolute mover: {top_abs.expense} "
            f"({('+' if top_abs.delta >= 0 else '')}{_format_number(top_abs.delta)})."
        )
    if top_pct and top_pct.delta_pct is not None:
        exec_summary.append(
            f"Top % mover: {top_pct.expense} "
            f"({('+' if top_pct.delta_pct >= 0 else '')}{top_pct.delta_pct:.1%})."
        )
    exec_summary.append(f"Anomaly candidates flagged: {len(metrics.anomalies)}.")
    exec_summary = exec_summary[:5]

    findings: List[Finding] = [
        Finding(
            headline=f"Total change from {prev_period} to {last_period}",
            value=f"{('+' if total_delta >= 0 else '')}{_format_number(total_delta)}",
            context=f"Total moved from {_format_number(total_prev)} to {_format_number(total_latest)}.",
            evidence_refs=[{"periods": [prev_period, last_period]}],
        )
    ]
    if metrics.totals:
        period_summaries = [
            f"{item.period}: total {_format_number(item.total)} / mean {_format_number(item.mean)}"
            for item in metrics.totals
        ]
        findings.append(
            Finding(
                headline="Trend summary by period",
                value=f"{len(metrics.totals)} periods summarized",
                context="; ".join(period_summaries),
                evidence_refs=[{"periods": [item.period for item in metrics.totals]}],
            )
        )
    if top_abs:
        findings.append(
            Finding(
                headline="Largest absolute mover",
                value=f"{top_abs.expense} ({('+' if top_abs.delta >= 0 else '')}{_format_number(top_abs.delta)})",
                context=f"Change measured between {prev_period} and {last_period}.",
                evidence_refs=[{"expense": top_abs.expense}],
            )
        )
    if top_pct and top_pct.delta_pct is not None:
        findings.append(
            Finding(
                headline="Largest percentage mover",
                value=f"{top_pct.expense} ({('+' if top_pct.delta_pct >= 0 else '')}{top_pct.delta_pct:.1%})",
                context=f"Percentage change between {prev_period} and {last_period}.",
                evidence_refs=[{"expense": top_pct.expense}],
            )
        )
    if metrics.anomalies:
        findings.append(
            Finding(
                headline="Anomaly candidates",
                value=f"{len(metrics.anomalies)} flagged",
                context="Outliers identified from period-over-period deltas.",
                evidence_refs=[{"period": last_period}],
            )
        )

    series = _build_series(metrics.period_labels, metrics.deduped_rows)
    visuals = [
        VisualSpec(
            kind="line",
            title="Primary trend overview",
            data={"periods": metrics.period_labels, "series": series},
            config={"metric_focus": payload.metric_focus, "chart_type": payload.chart_type},
        ),
        VisualSpec(
            kind="heatmap",
            title="Expense by period heatmap",
            data={"columns": metrics.period_labels, "rows": metrics.deduped_rows},
            config={},
        ),
    ]

    anomalies: List[AnomalyRow] = []
    for idx, item in enumerate(metrics.anomalies, start=1):
        anomalies.append(
            AnomalyRow(
                rank=idx,
                expense=item.expense,
                period=item.period,
                value=item.value,
                baseline=item.baseline,
                delta=item.delta,
                delta_pct=item.delta_pct,
                reason=item.reason,
            )
        )

    recommendations = [
        "Validate anomalous expenses with source system owners before downstream decisions.",
        "Confirm period definitions and align reporting cadence for trend stability.",
        "Collect additional periods or segments to raise statistical confidence.",
    ]

    report = BusinessReport(
        title=packet.question or "Business Report",
        generated_at_iso=now,
        dataset_id=metrics.dataset_id or "unknown",
        row_count=metrics.row_count,
        period_labels=metrics.period_labels,
        series_count=metrics.series_count,
        executive_summary=exec_summary,
        key_findings=findings,
        visuals=visuals,
        anomalies=anomalies,
        recommendations=recommendations,
        appendix=Appendix(
            confidence=packet.confidence_level,
            downgrade_reasons=payload.downgrade_reasons,
            trace_refs=[ref for ref in packet.trace_refs if isinstance(ref, dict)],
            assumptions=packet.assumptions,
            limitations=packet.limitations,
        ),
    )
    return AssembleBusinessReportOutput(report=report)


class AssembleBusinessReportTool(BaseTool):
    name = "assemble_business_report"
    description = "Assembles a business-ready report from ADE metrics and decision packet."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = AssembleBusinessReportInput.model_validate(params or {})
            output = assemble_business_report(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> AssembleBusinessReportTool:
    return AssembleBusinessReportTool()
