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

from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.governance.hooks import GovernanceHooks, HookDecision
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
            meta = self._meta(tool_name)
            err = ToolError(code=ToolErrorCode.NOT_FOUND, message=str(e), details={"tool": tool_name})
            return ToolResult(ok=False, data=None, error=err, meta=meta)

        safe_params = self.redactor.sanitize(params)

        if self.hooks is not None:
            decision = self.hooks.before_tool_call(tool_name=tool_name, params=params, ctx=ctx)
            if not decision.allowed:
                return self._deny(ctx, decision, tool_name)
        else:
            decision = None  # type: ignore[assignment]

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
                        code=ToolErrorCode.PERMISSION_DENIED,
                        message="MCP backend is disabled. Set configs to enable_mcp=true to use it.",
                        details={"tool": tool_name},
                    )
                    meta = self._meta(tool_name).model_copy(update={"backend": "mcp"})
                    result = ToolResult(ok=False, data=None, error=err, meta=meta)
                else:
                    result = self._mcp.run(tool=tool, params=params, ctx=ctx)
            else:
                err = ToolError(
                    code=ToolErrorCode.UNKNOWN,
                    message=f"Unknown tool backend_mode: {self.backend_mode}",
                    details={"backend_mode": self.backend_mode},
                )
                result = ToolResult(ok=False, data=None, error=err, meta=self._meta(tool_name))
        except Exception as e:
            err = ToolError(
                code=ToolErrorCode.BACKEND_ERROR,
                message="Tool execution failed.",
                details={"tool": tool_name, "exc": repr(e)},
            )
            result = ToolResult(ok=False, data=None, error=err, meta=self._meta(tool_name))

        elapsed_ms = int((time.time() - started) * 1000)

        # Emit trace/log event (sanitized)
        safe_result = self._safe_tool_result(result)
        self._emit(
            ctx,
            kind="tool.executed",
            payload={
                "tool": tool_name,
                "params": safe_params,
                "result": safe_result,
                "latency_ms": elapsed_ms,
                "backend": self.backend_mode,
            },
        )

        # Always return envelope
        meta = result.meta or self._meta(tool_name)
        updated_meta = meta.model_copy(update={"latency_ms": elapsed_ms, "backend": self.backend_mode})
        return result.model_copy(update={"meta": updated_meta})

    def _deny(self, ctx: StepContext, decision: HookDecision, tool_name: str) -> ToolResult:
        err = ToolError(
            code=ToolErrorCode.PERMISSION_DENIED,
            message=decision.reason or "Blocked by governance",
            details=decision.details,
        )
        payload = decision.to_payload()
        payload["tool"] = tool_name
        self._emit(ctx, kind="governance.decision", payload=payload)
        return ToolResult(ok=False, data=None, error=err, meta=self._meta(tool_name))

    def _emit(self, ctx: StepContext, *, kind: str, payload: Dict[str, Any]) -> None:
        ctx.emit(kind, self.redactor.sanitize(payload))

    def _safe_tool_result(self, result: ToolResult) -> Dict[str, Any]:
        """
        Avoid leaking sensitive data in trace/log channels.
        Keep structure stable for observability.
        """
        data = result.model_dump()
        redacted = self.redactor.redact_dict(data)
        return _strip_large_fields(redacted)

    def _meta(self, tool_name: str) -> ToolMeta:
        return ToolMeta(tool_name=tool_name, backend=self.backend_mode)


def _strip_large_fields(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, val in value.items():
            if key in {"content_base64", "file_bytes", "bytes"}:
                continue
            if isinstance(val, dict) and key == "output_files":
                cleaned[key] = _strip_large_fields(val)
            else:
                cleaned[key] = _strip_large_fields(val)
        return cleaned
    if isinstance(value, list):
        return [_strip_large_fields(item) for item in value]
    return value
