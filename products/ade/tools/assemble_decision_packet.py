
from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.tools.base import BaseTool, tool
from products.ade.schemas.decision_packet import DecisionPacket
from products.ade.schemas.decision_section import DecisionSection
from products.ade.utils.versioning import build_version_metadata


class AssembleDecisionPacketInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sections: List[DecisionSection]
    confidence_level: str
    assumptions: List[str]
    limitations: List[str]
    question: str = ""
    decision_summary: str = ""
    trace_refs: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_narrative: str = ""
    stop_reason: str = "sufficient"


class AssembleDecisionPacketOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_packet: DecisionPacket


def assemble_decision_packet(payload: AssembleDecisionPacketInput) -> AssembleDecisionPacketOutput:
    packet = DecisionPacket(
        question=payload.question,
        decision_summary=payload.decision_summary,
        confidence_level=payload.confidence_level,
        assumptions=payload.assumptions,
        limitations=payload.limitations,
        sections=payload.sections,
        trace_refs=payload.trace_refs,
        reasoning_narrative=payload.reasoning_narrative or None,
        stop_reason=payload.stop_reason,
    )
    return AssembleDecisionPacketOutput(decision_packet=packet)


@tool(
    name="assemble_decision_packet",
    description="Assembles a deterministic DecisionPacket from provided sections and metadata.",
    capabilities=["decision_assembly", "packet_generation", "report_packaging"],
    read_only=True,
    side_effect=False,
    sensitivity_class="MED",
    cost_hint="LOW",
)
class AssembleDecisionPacketTool(BaseTool):
    name = "assemble_decision_packet"
    description = "Assembles a deterministic DecisionPacket from provided sections."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: Any) -> ToolResult:
        try:
            payload = AssembleDecisionPacketInput.model_validate(params or {})
            output = assemble_decision_packet(payload)
            artifacts = getattr(ctx, "run", None).artifacts if getattr(ctx, "run", None) else {}
            data_reader = artifacts.get("tool.data_reader.output", {}) if isinstance(artifacts, dict) else {}
            dataset_id = ""
            run_payload = getattr(getattr(ctx, "run", None), "payload", {}) or {}
            if isinstance(run_payload, dict):
                dataset_id = str(run_payload.get("dataset") or "")
            version_metadata = build_version_metadata(
                flow_id=str(getattr(getattr(ctx, "run", None), "flow", "")),
                dataset_id=dataset_id,
                columns=list(data_reader.get("columns") or []),
                rows=list(data_reader.get("rows") or []),
                input_payload=params or {},
            )
            packet = output.decision_packet.model_copy(update={"version_metadata": version_metadata})
            output = output.model_copy(update={"decision_packet": packet})
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> AssembleDecisionPacketTool:
    return AssembleDecisionPacketTool()
