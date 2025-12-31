# ==============================
# Hello World Tool: echo_tool
# ==============================
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field

from core.tools.base import BaseTool
from core.contracts.tool_schema import ToolResult, ToolError, ToolMeta, ToolErrorCode
from core.orchestrator.context import StepContext


class EchoParams(BaseModel):
    message: str = Field(default="")


class EchoTool(BaseTool):
    """
    Deterministic tool that returns whatever message it receives.
    """

    name: str = "echo_tool"
    description: str = "Returns the provided message."
    risk: str = "read_only"

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        try:
            p = EchoParams.model_validate(params or {})
            timestamp = datetime.now(timezone.utc).isoformat()
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(
                ok=True,
                data={
                    "echo": p.message,
                    "timestamp": timestamp,
                },
                error=None,
                meta=meta,
            )
        except Exception as exc:
            err = ToolError(code=ToolErrorCode.INVALID_INPUT, message=str(exc))
            meta = ToolMeta(tool_name=self.name, backend="local")
            return ToolResult(ok=False, data=None, error=err, meta=meta)


def build() -> EchoTool:
    return EchoTool()
