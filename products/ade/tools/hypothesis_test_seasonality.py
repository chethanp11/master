
from __future__ import annotations

from math import sqrt
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.ade.tools.detect_anomalies import Point
from products.ade.tools.hypothesis_test_data_outage import HypothesisTestOutput
from products.ade.schemas.evidence import HypothesisEvidence, EvidenceItem
from products.ade.tools.evidence_utils import evidence_id, inputs_hash, now_iso


class SeasonalityInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = ""
    series: List[Point] = Field(default_factory=list)
    period: int = 7
    min_points: int = 12
    strength_threshold: float = 0.2
    enabled: bool = True


def _seasonal_strength(values: List[float], period: int) -> float:
    buckets: Dict[int, List[float]] = {}
    for idx, value in enumerate(values):
        bucket = idx % period
        buckets.setdefault(bucket, []).append(value)
    means = [sum(v) / len(v) for v in buckets.values() if v]
    if not means:
        return 0.0
    overall = sum(means) / len(means)
    if overall == 0:
        return 0.0
    variance = sum((m - overall) ** 2 for m in means) / len(means)
    return sqrt(variance) / abs(overall)


def hypothesis_test_seasonality(payload: SeasonalityInput) -> HypothesisTestOutput:
    hypothesis_name = "seasonality"
    if not payload.enabled:
        return HypothesisTestOutput(
            hypothesis_name=hypothesis_name,
            status="skipped",
            reasoning="skipped_by_user_preference",
        )
    series = payload.series
    if payload.period <= 1 or payload.min_points <= 0:
        return HypothesisTestOutput(
            hypothesis_name=hypothesis_name,
            status="rejected",
            reasoning="invalid_parameters",
        )
    if len(series) < payload.min_points:
        return HypothesisTestOutput(
            hypothesis_name=hypothesis_name,
            status="rejected",
            reasoning="insufficient_points",
        )
    values = [pt.value for pt in series]
    strength = _seasonal_strength(values, payload.period)
    if strength >= payload.strength_threshold:
        return HypothesisTestOutput(
            hypothesis_name=hypothesis_name,
            status="plausible",
            reasoning=f"seasonal_strength_{strength:.2f}_meets_threshold",
        )
    return HypothesisTestOutput(
        hypothesis_name=hypothesis_name,
        status="rejected",
        reasoning=f"seasonal_strength_{strength:.2f}_below_threshold",
    )


class HypothesisTestSeasonalityTool(BaseTool):
    name = "hypothesis_test_seasonality"
    description = "Tests whether the series shows seasonality signals."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = SeasonalityInput.model_validate(params or {})
            output = hypothesis_test_seasonality(payload)
            input_hash = inputs_hash(payload.model_dump(mode="json"))
            evidence = HypothesisEvidence(
                evidence_id=evidence_id(kind="hypothesis", tool_step_id=ctx.step_id, inputs_hash_value=input_hash),
                kind="hypothesis",
                tool_step_id=ctx.step_id,
                dataset_id=payload.dataset_id,
                created_at_iso=now_iso(),
                inputs_hash=input_hash,
                hypothesis_name=output.hypothesis_name,
                status=output.status,
                reasoning=output.reasoning,
            )
            output = output.model_copy(update={"evidence_items": [evidence]})
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> HypothesisTestSeasonalityTool:
    return HypothesisTestSeasonalityTool()
