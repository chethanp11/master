# ==============================
# MCP Backend (Stub)
# ==============================
"""
MCP backend adapter surface (minimal).

v1:
- Defines list_tools() and call_tool()
- Disabled by default (executor must opt-in via config)
- Not implemented; returns clear error envelopes
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.contracts.tool_schema import ToolError, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool


class MCPBackend:
    name: str = "mcp"

    def __init__(self, *, server_name: Optional[str] = None) -> None:
        self.server_name = server_name

    def list_tools(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("MCPBackend.list_tools not implemented in v1.")

    def call_tool(self, *, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("MCPBackend.call_tool not implemented in v1.")

    def run(self, tool: BaseTool, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        err = ToolError(
            code="MCP_BACKEND_NOT_IMPLEMENTED",
            message="MCP backend is disabled/not implemented in v1.",
            details={"server": self.server_name, "tool": getattr(tool, 'name', tool.__class__.__name__)},
        )
        return ToolResult(ok=False, data=None, error=err, meta={"backend": self.name})