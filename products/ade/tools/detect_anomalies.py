
from __future__ import annotations

from statistics import mean, pstdev
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, validator

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool


class Point(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts: str
    value: float


class DetectAnomaliesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    series: List[Point] = Field(default_factory=list)
    data: Optional["TableData"] = None
    method: Literal["zscore"] = "zscore"
    z_threshold: float = 3.0
    min_points: int = 8

    @validator("series")
    def must_have_points(cls, value: List[Point]) -> List[Point]:
        return value


class Anomaly(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts: str
    value: float
    zscore: float


class DetectAnomaliesOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    anomalies: List[Anomaly]
    summary: str


class TableData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: List[str]
    rows: List[List[Any]]


def detect_anomalies(payload: DetectAnomaliesInput) -> DetectAnomaliesOutput:
    series = payload.series
    if not series and payload.data is not None:
        return _detect_anomalies_from_table(payload.data, payload)
    if len(series) < payload.min_points:
        return DetectAnomaliesOutput(anomalies=[], summary="series too short")
    values = [pt.value for pt in series]
    stddev = pstdev(values)
    if stddev == 0:
        return DetectAnomaliesOutput(anomalies=[], summary="no variance")
    m = mean(values)
    anomalies = []
    for pt in series:
        z = (pt.value - m) / stddev
        if abs(z) >= payload.z_threshold:
            anomalies.append(Anomaly(ts=pt.ts, value=pt.value, zscore=z))
    anomalies.sort(key=lambda a: (-abs(a.zscore), a.ts))
    summary = f"found {len(anomalies)} anomalies"
    return DetectAnomaliesOutput(anomalies=anomalies, summary=summary)


class DetectAnomaliesTool(BaseTool):
    name = "detect_anomalies"
    description = "Detects anomalies in a time series using z-score heuristics."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = DetectAnomaliesInput.model_validate(params or {})
            output = detect_anomalies(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> DetectAnomaliesTool:
    return DetectAnomaliesTool()


def _derive_series_from_table(data: TableData) -> List[Point]:
    numeric_columns: List[int] = []
    for idx, _ in enumerate(data.columns):
        values = []
        for row in data.rows:
            if idx >= len(row):
                continue
            value = row[idx]
            if value is None:
                continue
            values.append(value)
        if values and all(_to_float(v) is not None for v in values):
            numeric_columns.append(idx)

    series: List[Point] = []
    for idx in numeric_columns:
        total = 0.0
        count = 0
        for row in data.rows:
            if idx >= len(row):
                continue
            value = _to_float(row[idx])
            if value is None:
                continue
            total += value
            count += 1
        if count == 0:
            continue
        series.append(Point(ts=str(data.columns[idx]), value=total))
    return series


def _detect_anomalies_from_table(data: TableData, payload: DetectAnomaliesInput) -> DetectAnomaliesOutput:
    columns = data.columns
    if not columns or not data.rows:
        return DetectAnomaliesOutput(anomalies=[], summary="no data")
    numeric_cols: List[int] = []
    for idx in range(len(columns)):
        col_values = []
        for row in data.rows:
            if idx >= len(row):
                continue
            value = _to_float(row[idx])
            if value is None:
                continue
            col_values.append(value)
        if col_values and len(col_values) == sum(1 for _ in col_values if _ is not None):
            numeric_cols.append(idx)

    label_idx = None
    if 0 in numeric_cols:
        numeric_cols = [idx for idx in numeric_cols if idx != 0]
    elif columns:
        label_idx = 0

    if not numeric_cols:
        return DetectAnomaliesOutput(anomalies=[], summary="no numeric columns")

    anomalies: List[Anomaly] = []
    for row in data.rows:
        label = None
        if label_idx is not None and label_idx < len(row):
            label = str(row[label_idx])
        points: List[Point] = []
        for idx in numeric_cols:
            if idx >= len(row):
                continue
            value = _to_float(row[idx])
            if value is None:
                continue
            ts = f"{label}:{columns[idx]}" if label is not None else str(columns[idx])
            points.append(Point(ts=ts, value=value))
        if len(points) < payload.min_points:
            continue
        values = [pt.value for pt in points]
        stddev = pstdev(values)
        if stddev == 0:
            continue
        m = mean(values)
        for pt in points:
            z = (pt.value - m) / stddev
            if abs(z) >= payload.z_threshold:
                anomalies.append(Anomaly(ts=pt.ts, value=pt.value, zscore=z))

    anomalies.sort(key=lambda a: (-abs(a.zscore), a.ts))
    if not anomalies:
        return DetectAnomaliesOutput(anomalies=[], summary="no anomalies found")
    top = anomalies[0]
    summary = f"found {len(anomalies)} anomalies (top: {top.ts}={top.value})"
    return DetectAnomaliesOutput(anomalies=anomalies, summary=summary)


def _to_float(value: Any) -> Optional[float]:
    # TODO: Keep local conversion to avoid cross-tool coupling; consolidate if a shared util is introduced.
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None
