
from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.ade.contracts.decision_packet import DecisionPacket
from products.ade.contracts.decision_section import DecisionSection


class AssembleDecisionPacketInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sections: List[DecisionSection]
    confidence_level: str
    assumptions: List[str]
    limitations: List[str]
    question: str = ""
    decision_summary: str = ""
    trace_refs: List[Dict[str, Any]] = Field(default_factory=list)


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
    )
    return AssembleDecisionPacketOutput(decision_packet=packet)


class AssembleDecisionPacketTool(BaseTool):
    name = "assemble_decision_packet"
    description = "Assembles a deterministic DecisionPacket from provided sections."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = AssembleDecisionPacketInput.model_validate(params or {})
            output = assemble_decision_packet(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> AssembleDecisionPacketTool:
    return AssembleDecisionPacketTool()
