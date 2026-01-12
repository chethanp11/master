
from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.tools.base import BaseTool, tool
from products.ade.tools.detect_anomalies import Point
from products.ade.schemas.evidence import HypothesisEvidence, EvidenceItem
from products.ade.tools.evidence_utils import evidence_id, inputs_hash, now_iso


class DataOutageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = ""
    series: List[Point] = Field(default_factory=list)
    recent_window: int = 5
    outage_threshold: float = 0.6
    enabled: bool = True


class HypothesisTestOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hypothesis_name: str
    status: str
    reasoning: str
    evidence_items: List[EvidenceItem] = Field(default_factory=list)


def hypothesis_test_data_outage(payload: DataOutageInput) -> HypothesisTestOutput:
    hypothesis_name = "data_outage"
    if not payload.enabled:
        return HypothesisTestOutput(
            hypothesis_name=hypothesis_name,
            status="skipped",
            reasoning="skipped_by_user_preference",
        )
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


@tool(
    name="hypothesis_test_data_outage",
    description="Tests whether recent data indicates a potential outage or data quality issue.",
    capabilities=["hypothesis_testing", "outage_detection", "data_quality"],
    read_only=True,
    side_effect=False,
    sensitivity_class="MED",
    cost_hint="LOW",
)
class HypothesisTestDataOutageTool(BaseTool):
    name = "hypothesis_test_data_outage"
    description = "Tests whether recent data indicates a potential outage."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: Any) -> ToolResult:
        try:
            payload = DataOutageInput.model_validate(params or {})
            output = hypothesis_test_data_outage(payload)
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


def build() -> HypothesisTestDataOutageTool:
    return HypothesisTestDataOutageTool()
