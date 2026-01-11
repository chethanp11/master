from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.tools.base import BaseTool
from products.ade.schemas.evidence import EvidenceBundle, EvidenceItem


class AssembleEvidenceBundleInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    intent: str
    selections: Dict[str, Any] = Field(default_factory=dict)
    items: List[Any] = Field(default_factory=list)


class AssembleEvidenceBundleOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_bundle: EvidenceBundle


_EVIDENCE_ADAPTER = TypeAdapter(EvidenceItem)


def _flatten_items(items: List[Any]) -> List[EvidenceItem]:
    flattened: List[EvidenceItem] = []
    for item in items:
        if isinstance(item, list):
            flattened.extend(_flatten_items(item))
            continue
        if isinstance(item, dict):
            flattened.append(_EVIDENCE_ADAPTER.validate_python(item))
    return flattened


def assemble_evidence_bundle(payload: AssembleEvidenceBundleInput, ctx: Any) -> AssembleEvidenceBundleOutput:
    items = _flatten_items(payload.items)
    summary_stats: Dict[str, Any] = {"total_items": len(items)}
    kind_counts: Dict[str, int] = {}
    for item in items:
        kind_counts[item.kind] = kind_counts.get(item.kind, 0) + 1
    summary_stats["by_kind"] = kind_counts

    bundle = EvidenceBundle(
        run_id=ctx.run.run_id,
        product=ctx.run.product,
        flow=ctx.run.flow,
        dataset_id=payload.dataset_id,
        intent=payload.intent,
        selections=payload.selections,
        items=items,
        summary_stats=summary_stats,
    )
    return AssembleEvidenceBundleOutput(evidence_bundle=bundle)


class AssembleEvidenceBundleTool(BaseTool):
    name = "assemble_evidence_bundle"
    description = "Aggregates evidence items into a single evidence bundle."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: Any) -> ToolResult:
        try:
            payload = AssembleEvidenceBundleInput.model_validate(params or {})
            output = assemble_evidence_bundle(payload, ctx)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> AssembleEvidenceBundleTool:
    return AssembleEvidenceBundleTool()
