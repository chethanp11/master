# ==============================
# Tool Executor
# ==============================
"""
Central tool execution entrypoint.

Rules:
- ONLY place tools are invoked.
- Applies governance hooks (if available) before execution.
- Applies security redaction before emitting trace/log events.
- Never raises raw exceptions; always returns ToolResult envelope.

Execution routing:
- Default: local backend (runs python implementation)
- Optional: remote/mcp backends (disabled unless explicitly enabled by config)

Dependencies:
- ToolRegistry (resolve tool)
- Governance hooks (optional)
- Security redaction (optional)
- StepContext trace hook (optional)
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from core.contracts.run_schema import TraceEvent
from core.contracts.tool_schema import ToolError, ToolResult
from core.governance.hooks import GovernanceHooks
from core.governance.security import SecurityRedactor
from core.orchestrator.context import StepContext
from core.tools.backends.local_backend import LocalToolBackend
from core.tools.backends.mcp_backend import MCPBackend
from core.tools.backends.remote_backend import RemoteToolBackend
from core.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(
        self,
        *,
        registry: ToolRegistry,
        hooks: Optional[GovernanceHooks] = None,
        redactor: Optional[SecurityRedactor] = None,
        backend_mode: str = "local",
        backend_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.registry = registry
        self.hooks = hooks
        self.redactor = redactor or SecurityRedactor()
        self.backend_mode = backend_mode
        self.backend_config = backend_config or {}

        self._local = LocalToolBackend()
        self._remote = RemoteToolBackend(endpoint=self.backend_config.get("remote_endpoint"))
        self._mcp = MCPBackend(server_name=self.backend_config.get("mcp_server"))

    def execute(self, *, tool_name: str, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        started = time.time()

        # Resolve tool
        try:
            tool = self.registry.resolve(tool_name)
        except Exception as e:
            err = ToolError(code="TOOL_NOT_FOUND", message=str(e), details={"tool": tool_name})
            return ToolResult(ok=False, data=None, error=err, meta={"tool": tool_name})

        safe_params = self.redactor.redact_dict(params)

        # Governance: before_tool
        try:
            if self.hooks is not None:
                self.hooks.before_tool_call(tool_name=tool_name, params=params, ctx=ctx)
        except Exception as e:
            err = ToolError(code="TOOL_BLOCKED", message=str(e), details={"tool": tool_name})
            self._emit(ctx, kind="tool.blocked", tool=tool_name, payload={"params": safe_params, "error": err.model_dump()})
            return ToolResult(ok=False, data=None, error=err, meta={"tool": tool_name, "backend": self.backend_mode})

        # Execute
        try:
            if self.backend_mode == "local":
                result = self._local.run(tool=tool, params=params, ctx=ctx)
            elif self.backend_mode == "remote_agent":
                result = self._remote.run(tool=tool, params=params, ctx=ctx)
            elif self.backend_mode == "mcp":
                enabled = bool(self.backend_config.get("enable_mcp", False))
                if not enabled:
                    err = ToolError(
                        code="MCP_DISABLED",
                        message="MCP backend is disabled. Set configs to enable_mcp=true to use it.",
                        details={"tool": tool_name},
                    )
                    result = ToolResult(ok=False, data=None, error=err, meta={"tool": tool_name, "backend": "mcp"})
                else:
                    result = self._mcp.run(tool=tool, params=params, ctx=ctx)
            else:
                err = ToolError(
                    code="UNKNOWN_BACKEND",
                    message=f"Unknown tool backend_mode: {self.backend_mode}",
                    details={"backend_mode": self.backend_mode},
                )
                result = ToolResult(ok=False, data=None, error=err, meta={"tool": tool_name})
        except Exception as e:
            err = ToolError(code="TOOL_EXCEPTION", message="Tool execution failed.", details={"tool": tool_name, "exc": repr(e)})
            result = ToolResult(ok=False, data=None, error=err, meta={"tool": tool_name, "backend": self.backend_mode})

        elapsed_ms = int((time.time() - started) * 1000)

        # Emit trace/log event (sanitized)
        safe_result = self._safe_tool_result(result)
        self._emit(
            ctx,
            kind="tool.executed",
            tool=tool_name,
            payload={"params": safe_params, "result": safe_result, "latency_ms": elapsed_ms, "backend": self.backend_mode},
        )

        # Always return envelope
        meta = dict(result.meta or {})
        meta.update({"latency_ms": elapsed_ms, "backend": self.backend_mode, "tool": tool_name})
        return result.model_copy(update={"meta": meta})

    def _emit(self, ctx: StepContext, *, kind: str, tool: str, payload: Dict[str, Any]) -> None:
        if ctx.trace is None:
            return
        evt = TraceEvent(
            kind=kind,
            run_id=ctx.run_id,
            step_id=ctx.step_id,
            product=ctx.product,
            flow=ctx.flow,
            payload=self.redactor.redact_dict(payload),
        )
        ctx.trace(evt)

    def _safe_tool_result(self, result: ToolResult) -> Dict[str, Any]:
        """
        Avoid leaking sensitive data in trace/log channels.
        Keep structure stable for observability.
        """
        data = result.model_dump()
        return self.redactor.redact_dict(data)