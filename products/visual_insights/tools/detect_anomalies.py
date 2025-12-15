from __future__ import annotations

from statistics import mean, pstdev
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field, validator


class Point(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts: str
    value: float


class DetectAnomaliesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    series: List[Point]
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


def detect_anomalies(payload: DetectAnomaliesInput) -> DetectAnomaliesOutput:
    if len(payload.series) < payload.min_points:
        return DetectAnomaliesOutput(anomalies=[], summary="series too short")
    values = [pt.value for pt in payload.series]
    stddev = pstdev(values)
    if stddev == 0:
        return DetectAnomaliesOutput(anomalies=[], summary="no variance")
    m = mean(values)
    anomalies = []
    for pt in payload.series:
        z = (pt.value - m) / stddev
        if abs(z) >= payload.z_threshold:
            anomalies.append(Anomaly(ts=pt.ts, value=pt.value, zscore=z))
    anomalies.sort(key=lambda a: (-abs(a.zscore), a.ts))
    summary = f"found {len(anomalies)} anomalies"
    return DetectAnomaliesOutput(anomalies=anomalies, summary=summary)
