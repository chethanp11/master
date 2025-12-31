from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool


class SegmentRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment: str
    before: float
    after: float


class DriverAnalysisInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rows: List[SegmentRow]
    top_k: int = Field(default=5, ge=1)
    min_total_change: float = 0.0


class Driver(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment: str
    delta: float
    contribution_pct: float


class DriverAnalysisOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_before: float
    total_after: float
    total_delta: float
    drivers: List[Driver]
    summary: str


def driver_analysis(payload: DriverAnalysisInput) -> DriverAnalysisOutput:
    total_before = sum(row.before for row in payload.rows)
    total_after = sum(row.after for row in payload.rows)
    total_delta = total_after - total_before
    if abs(total_delta) <= payload.min_total_change or not payload.rows:
        return DriverAnalysisOutput(
            total_before=total_before,
            total_after=total_after,
            total_delta=total_delta,
            drivers=[],
            summary="no significant change",
        )

    drivers = []
    for row in payload.rows:
        delta = row.after - row.before
        contribution_pct = (
            round((delta / total_delta) * 100, 2) if total_delta != 0 else 0.0
        )
        drivers.append(Driver(segment=row.segment, delta=delta, contribution_pct=contribution_pct))

    drivers.sort(key=lambda d: (-abs(d.delta), d.segment))
    drivers = drivers[: payload.top_k]
    summary = f"derived {len(drivers)} drivers"
    return DriverAnalysisOutput(
        total_before=total_before,
        total_after=total_after,
        total_delta=total_delta,
        drivers=drivers,
        summary=summary,
    )


class DriverAnalysisTool(BaseTool):
    name = "driver_analysis"
    description = "Computes driver contributions for before/after segments."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = DriverAnalysisInput.model_validate(params or {})
            output = driver_analysis(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> DriverAnalysisTool:
    return DriverAnalysisTool()
