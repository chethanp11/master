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



import json
import time
from datetime import datetime
from typing import Any, Dict, Optional, List, Tuple

from core.contracts.context_pack_schema import EvidenceItem, EvidenceSource
from core.contracts.run_schema import ArtifactRef
from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.governance.hooks import GovernanceHooks, HookDecision
from core.governance.security import SecurityRedactor
from core.orchestrator.context import StepContext
from core.tools.backends.local_backend import LocalToolBackend
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
            else:
                # Remote and MCP backends removed in v1 simplification
                err = ToolError(
                    code=ToolErrorCode.UNKNOWN,
                    message=f"Unknown or unsupported backend_mode: {self.backend_mode}. Only 'local' is supported.",
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
        normalized = self._normalize_result(result, tool_name=tool_name)
        enriched = self._attach_evidence(normalized, tool_name=tool_name, params=params, ctx=ctx)

        # Emit trace/log event (sanitized)
        safe_result = self._safe_tool_result(enriched)
        produced_evidence = _evidence_metadata(enriched.evidence)
        self._emit(
            ctx,
            kind="tool.executed",
            payload={
                "tool": tool_name,
                "params": safe_params,
                "result": safe_result,
                "produced_evidence": produced_evidence,
                "latency_ms": elapsed_ms,
                "backend": self.backend_mode,
            },
        )

        # Always return envelope
        meta = enriched.meta or self._meta(tool_name)
        updated_meta = meta.model_copy(update={"latency_ms": elapsed_ms, "backend": self.backend_mode})
        return enriched.model_copy(update={"meta": updated_meta})

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

    def _normalize_result(self, result: Any, *, tool_name: str) -> ToolResult:
        if isinstance(result, ToolResult):
            return result
        meta = self._meta(tool_name)
        if isinstance(result, dict):
            return ToolResult(ok=True, data=result, error=None, meta=meta)
        if isinstance(result, ArtifactRef):
            return ToolResult(ok=True, data={"artifact": result.model_dump(mode="json")}, error=None, meta=meta)
        if result is None:
            return ToolResult(ok=True, data={}, error=None, meta=meta)
        return ToolResult(ok=True, data={"value": result}, error=None, meta=meta)

    def _attach_evidence(
        self,
        result: ToolResult,
        *,
        tool_name: str,
        params: Dict[str, Any],
        ctx: StepContext,
    ) -> ToolResult:
        if result.evidence:
            return result
        if result.error and result.error.code == ToolErrorCode.PERMISSION_DENIED:
            return result
        safe_params = self.redactor.sanitize(params)
        payload = result.data if result.ok else {"error": result.error.model_dump(mode="json") if result.error else {}}
        summary = _summarize_payload(payload)
        confidence = 0.8 if result.ok else 0.5
        evidence_id = f"{tool_name}-{result.meta.request_id}"
        content_ref, artifacts = _store_evidence_artifact(
            ctx=ctx,
            tool_name=tool_name,
            evidence_id=evidence_id,
            payload=payload,
        )
        evidence = EvidenceItem(
            id=evidence_id,
            type="text",
            source=EvidenceSource(tool=tool_name, uri=content_ref.uri, ref=content_ref.key),
            timestamp=datetime.utcnow(),
            confidence=confidence,
            content_ref=content_ref,
            summary=summary,
            provenance=safe_params,
        )
        return result.model_copy(update={"evidence": [evidence], "artifacts": artifacts})


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


def _store_evidence_artifact(
    *,
    ctx: StepContext,
    tool_name: str,
    evidence_id: str,
    payload: Dict[str, Any],
) -> Tuple[ArtifactRef, Dict[str, ArtifactRef]]:
    key = f"tool.{tool_name}.evidence.{evidence_id}"
    uri = f"memory://{key}"
    ref = ArtifactRef(key=key, kind="json", uri=uri, meta={"tool": tool_name})
    ctx.run.artifacts[key] = payload
    return ref, {key: ref}


def _summarize_payload(payload: Any, *, limit: int = 300) -> str:
    if isinstance(payload, str):
        text = payload
    else:
        try:
            text = json.dumps(payload, ensure_ascii=True, sort_keys=True)
        except Exception:
            text = str(payload)
    text = text.strip()
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text or "tool_output"


def _evidence_metadata(items: List[EvidenceItem]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        out.append({"id": item.id, "type": item.type, "source": item.source.model_dump(mode="json")})
    return out
