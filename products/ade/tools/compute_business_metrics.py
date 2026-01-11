from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.tools.base import BaseTool
from products.ade.schemas.evidence import DataQualityEvidence, OutlierEvidence, TrendEvidence, EvidenceItem
from products.ade.tools.evidence_utils import evidence_id, inputs_hash, now_iso


class BusinessMetricsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = ""
    columns: List[str]
    rows: List[List[Any]]
    metric_focus: str = "mean"
    chart_type: str = "line"
    include_hypothesis_checks: bool = True


class PeriodStat(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: str
    total: float
    mean: float


class Mover(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expense: str
    previous: float
    latest: float
    delta: float
    delta_pct: Optional[float] = None


class AnomalyCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expense: str
    period: str
    value: float
    baseline: float
    delta: float
    delta_pct: Optional[float] = None
    reason: str


class BusinessMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = ""
    row_count: int
    period_labels: List[str]
    series_count: int
    totals: List[PeriodStat]
    means: List[PeriodStat]
    top_movers_abs: List[Mover]
    top_movers_pct: List[Mover]
    anomalies: List[AnomalyCandidate]
    deduped_rows: List[List[Any]]
    evidence_items: List[EvidenceItem] = Field(default_factory=list)


def _coerce_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if text == "":
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _dedupe_rows(rows: List[List[Any]]) -> List[List[Any]]:
    seen: set[Tuple[Any, ...]] = set()
    deduped: List[List[Any]] = []
    for row in rows:
        key = tuple(row)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(list(row))
    return deduped


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = (len(sorted_vals) - 1) * p
    lower = int(idx)
    upper = min(lower + 1, len(sorted_vals) - 1)
    weight = idx - lower
    return sorted_vals[lower] * (1 - weight) + sorted_vals[upper] * weight


def compute_business_metrics(payload: BusinessMetricsInput) -> BusinessMetrics:
    columns = payload.columns or []
    deduped_rows = _dedupe_rows(payload.rows or [])
    period_labels = columns[1:] if len(columns) > 1 else []
    expense_idx = 0
    values_by_expense: Dict[str, List[Optional[float]]] = {}

    for row in deduped_rows:
        if not row:
            continue
        expense = str(row[expense_idx])
        if expense not in values_by_expense:
            values_by_expense[expense] = [0.0 for _ in period_labels]
        for idx, _period in enumerate(period_labels, start=1):
            if idx >= len(row):
                continue
            value = _coerce_number(row[idx])
            if value is None:
                continue
            values_by_expense[expense][idx - 1] += value

    series_count = len(values_by_expense)
    totals: List[PeriodStat] = []
    means: List[PeriodStat] = []
    for idx, period in enumerate(period_labels):
        values = []
        for series in values_by_expense.values():
            if idx < len(series):
                values.append(series[idx])
        total = float(sum(values)) if values else 0.0
        mean = float(total / len(values)) if values else 0.0
        totals.append(PeriodStat(period=period, total=total, mean=mean))
        means.append(PeriodStat(period=period, total=total, mean=mean))

    movers: List[Mover] = []
    if len(period_labels) >= 2:
        for expense, series in values_by_expense.items():
            prev = series[-2]
            latest = series[-1]
            delta = latest - prev
            delta_pct = None
            if prev != 0:
                delta_pct = delta / prev
            movers.append(
                Mover(
                    expense=expense,
                    previous=prev,
                    latest=latest,
                    delta=delta,
                    delta_pct=delta_pct,
                )
            )

    top_movers_abs = sorted(movers, key=lambda m: abs(m.delta), reverse=True)[:3]
    movers_with_pct = [m for m in movers if m.delta_pct is not None]
    top_movers_pct = sorted(movers_with_pct, key=lambda m: abs(m.delta_pct or 0.0), reverse=True)[:3]

    anomalies: List[AnomalyCandidate] = []
    deltas = [m.delta for m in movers]
    if deltas:
        q1 = _percentile(deltas, 0.25)
        q3 = _percentile(deltas, 0.75)
        iqr = q3 - q1
        upper = q3 + 1.5 * iqr
        lower = q1 - 1.5 * iqr
        for mover in movers:
            if mover.delta >= upper or mover.delta <= lower:
                anomalies.append(
                    AnomalyCandidate(
                        expense=mover.expense,
                        period=period_labels[-1],
                        value=mover.latest,
                        baseline=mover.previous,
                        delta=mover.delta,
                        delta_pct=mover.delta_pct,
                        reason="delta_iqr_outlier",
                    )
                )
    if not anomalies and movers:
        for mover in top_movers_abs[:3]:
            anomalies.append(
                AnomalyCandidate(
                    expense=mover.expense,
                    period=period_labels[-1] if period_labels else "latest",
                    value=mover.latest,
                    baseline=mover.previous,
                    delta=mover.delta,
                    delta_pct=mover.delta_pct,
                    reason="largest_delta",
                )
            )

    return BusinessMetrics(
        dataset_id=payload.dataset_id,
        row_count=len(deduped_rows),
        period_labels=period_labels,
        series_count=series_count,
        totals=totals,
        means=means,
        top_movers_abs=top_movers_abs,
        top_movers_pct=top_movers_pct,
        anomalies=anomalies,
        deduped_rows=deduped_rows,
    )


class ComputeBusinessMetricsTool(BaseTool):
    name = "compute_business_metrics"
    description = "Computes deterministic business metrics for ADE reports."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: Any) -> ToolResult:
        try:
            payload = BusinessMetricsInput.model_validate(params or {})
            output = compute_business_metrics(payload)
            input_hash = inputs_hash(payload.model_dump(mode="json"))
            duplicate_count = max(0, len(payload.rows) - len(output.deduped_rows))
            trend = TrendEvidence(
                evidence_id=evidence_id(kind="trend", tool_step_id=ctx.step_id, inputs_hash_value=input_hash),
                kind="trend",
                tool_step_id=ctx.step_id,
                dataset_id=payload.dataset_id,
                created_at_iso=now_iso(),
                inputs_hash=input_hash,
                period_labels=output.period_labels,
                totals=[{"period": item.period, "total": item.total} for item in output.totals],
                means=[{"period": item.period, "mean": item.mean} for item in output.means],
                top_movers_abs=[m.model_dump(mode="json") for m in output.top_movers_abs],
                top_movers_pct=[m.model_dump(mode="json") for m in output.top_movers_pct],
            )
            data_quality = DataQualityEvidence(
                evidence_id=evidence_id(kind="data_quality", tool_step_id=ctx.step_id, inputs_hash_value=input_hash),
                kind="data_quality",
                tool_step_id=ctx.step_id,
                dataset_id=payload.dataset_id,
                created_at_iso=now_iso(),
                inputs_hash=input_hash,
                row_count=len(payload.rows),
                deduped_row_count=len(output.deduped_rows),
                duplicate_count=duplicate_count,
            )
            outlier = OutlierEvidence(
                evidence_id=evidence_id(kind="outlier", tool_step_id=ctx.step_id, inputs_hash_value=input_hash),
                kind="outlier",
                tool_step_id=ctx.step_id,
                dataset_id=payload.dataset_id,
                created_at_iso=now_iso(),
                inputs_hash=input_hash,
                candidates=[item.model_dump(mode="json") for item in output.anomalies],
                method="iqr",
            )
            output = output.model_copy(update={"evidence_items": [trend, data_quality, outlier]})
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> ComputeBusinessMetricsTool:
    return ComputeBusinessMetricsTool()
