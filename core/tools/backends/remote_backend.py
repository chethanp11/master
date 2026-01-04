# ==============================
# Remote Tool Backend (Stub)
# ==============================
"""
Remote backend is a placeholder for calling tools hosted remotely (HTTP/gRPC).

v1:
- Provide clean interface
- Disabled by default
- Raises NotImplementedError with clear guidance
"""

from __future__ import annotations



from typing import Any, Dict, Optional

from core.contracts.tool_schema import ToolError, ToolResult
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool


class RemoteToolBackend:
    name: str = "remote_agent"

    def __init__(self, *, endpoint: Optional[str] = None) -> None:
        self.endpoint = endpoint

    def run(self, tool: BaseTool, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        err = ToolError(
            code="REMOTE_BACKEND_NOT_IMPLEMENTED",
            message="RemoteToolBackend is not implemented in v1. Use local backend or implement HTTP/gRPC adapter.",
            details={"endpoint": self.endpoint, "tool": getattr(tool, "name", tool.__class__.__name__)},
        )
        return ToolResult(ok=False, data=None, error=err, meta={"backend": self.name})
