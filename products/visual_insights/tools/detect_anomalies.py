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
        series = _derive_series_from_table(payload.data)
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


def _to_float(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None
