
from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.ade.tools.detect_anomalies import Point


class DataOutageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    series: List[Point] = Field(default_factory=list)
    recent_window: int = 5
    outage_threshold: float = 0.6


class HypothesisTestOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hypothesis_name: str
    status: str
    reasoning: str


def hypothesis_test_data_outage(payload: DataOutageInput) -> HypothesisTestOutput:
    hypothesis_name = "data_outage"
    series = payload.series
    if payload.recent_window <= 0 or payload.outage_threshold <= 0:
        return HypothesisTestOutput(
            hypothesis_name=hypothesis_name,
            status="rejected",
            reasoning="invalid_parameters",
        )
    if len(series) < payload.recent_window:
        return HypothesisTestOutput(
            hypothesis_name=hypothesis_name,
            status="rejected",
            reasoning="insufficient_recent_points",
        )
    recent = series[-payload.recent_window :]
    zero_count = sum(1 for pt in recent if pt.value == 0)
    ratio = zero_count / len(recent)
    if ratio >= payload.outage_threshold:
        return HypothesisTestOutput(
            hypothesis_name=hypothesis_name,
            status="plausible",
            reasoning=f"zero_ratio_{ratio:.2f}_meets_threshold",
        )
    return HypothesisTestOutput(
        hypothesis_name=hypothesis_name,
        status="rejected",
        reasoning=f"zero_ratio_{ratio:.2f}_below_threshold",
    )


class HypothesisTestDataOutageTool(BaseTool):
    name = "hypothesis_test_data_outage"
    description = "Tests whether recent data indicates a potential outage."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = DataOutageInput.model_validate(params or {})
            output = hypothesis_test_data_outage(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> HypothesisTestDataOutageTool:
    return HypothesisTestDataOutageTool()
