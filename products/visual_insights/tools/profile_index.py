from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from products.visual_insights.contracts.refs import DatasetRef, DocRef


class ProfileIndexInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_refs: List[DatasetRef]
    doc_refs: List[DocRef]


class ProfileIndexOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_profiles: List[Dict[str, str]]
    pdf_index_refs: List[Dict[str, str]]


def profile_index(payload: ProfileIndexInput) -> ProfileIndexOutput:
    return ProfileIndexOutput(dataset_profiles=[], pdf_index_refs=[])


class ProfileIndexTool(BaseTool):
    name = "profile_index"
    description = "Profiles datasets and returns index references (stub in v1)."
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            payload = ProfileIndexInput.model_validate(params or {})
            output = profile_index(payload)
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> ProfileIndexTool:
    return ProfileIndexTool()
