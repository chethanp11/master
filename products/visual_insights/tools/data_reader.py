# Visual insights tool: simple data reader
from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field

from core.contracts.tool_schema import ToolResult, ToolError, ToolMeta
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool


class ReadParams(BaseModel):
    dataset: str = Field(..., description="Dataset to read")


class DataReaderTool(BaseTool):
    name = "data_reader"
    description = "Returns a stubbed summary for a dataset"
    risk = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            validated = ReadParams.model_validate(params or {})
            summary = f"Insights for {validated.dataset}: all metrics nominal."
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=True, data={"summary": summary}, error=None, meta=meta)
        except Exception as exc:
            err = ToolError(code="TOOL_ERROR", message=str(exc))
            return ToolResult(ok=False, data=None, error=err, meta=ToolMeta(tool_name=self.name, backend="local"))


def build() -> DataReaderTool:
    return DataReaderTool()
