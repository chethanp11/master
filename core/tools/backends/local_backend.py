# ==============================
# Local Tool Backend
# ==============================
"""
Local backend executes in-process Python tool implementations.

Rules:
- No persistence here.
- No direct logging of sensitive fields; executor handles redaction + tracing.
"""

from __future__ import annotations



from typing import Any, Dict

from core.contracts.tool_schema import ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool


class LocalToolBackend:
    name: str = "local"

    def run(self, tool: BaseTool, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        return tool.run(params=params, ctx=ctx)
