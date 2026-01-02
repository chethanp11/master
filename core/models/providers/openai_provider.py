# ==============================
# OpenAI Provider (Stub)
# ==============================
"""
OpenAI provider adapter stub.

Important:
- This file does NOT make real network calls in v1.
- No environment reads here.
- In v1, this is a placeholder so the rest of the platform compiles and routes calls
  through a provider boundary.

Later:
- Wire this provider to the real OpenAI SDK.
- Read API keys from core/config/loader.py injected config (never from this module).
- Add retry, timeouts, and structured error mapping to AgentError/ToolError envelopes.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OpenAIRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(..., description="Model name (router sets this)")
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    temperature: float = Field(default=0.2)
    max_tokens: Optional[int] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OpenAIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool = Field(default=True)
    model: str = Field(...)
    content: str = Field(default="")
    usage: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[Dict[str, Any]] = Field(default=None)
    meta: Dict[str, Any] = Field(default_factory=dict)


class OpenAIProvider:
    """
    Provider boundary for OpenAI.

    config shape (example):
{
  "api_base": "...",
  "api_key_ref": "secrets/openai_api_key"   # resolved by config loader later
}
    """

    def __init__(self, *, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

    def complete(self, request: OpenAIRequest) -> OpenAIResponse:
        api_key = self.config.get("api_key")
        if not api_key:
            return OpenAIResponse(
                ok=False,
                model=request.model,
                content="",
                error={"code": "missing_api_key", "message": "OpenAI API key is not configured."},
                meta={"provider": "openai"},
            )

        api_base = self.config.get("api_base") or "https://api.openai.com/v1"
        endpoint = f"{api_base.rstrip('/')}/chat/completions"
        payload: Dict[str, Any] = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        org_id = self.config.get("org_id")
        if _should_send_org_header(org_id):
            headers["OpenAI-Organization"] = org_id
        body = json.dumps(payload).encode("utf-8")
        timeout = float(self.config.get("timeout_seconds") or 30.0)
        req = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")

        request_id = None
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                request_id = _extract_request_id(resp.headers)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            try:
                data = json.loads(raw)
            except Exception:
                data = {"error": {"message": "OpenAI HTTP error"}}
            status = getattr(exc, "code", None)
            request_id = _extract_request_id(exc.headers) if exc.headers else None
            body_snippet = _safe_body_snippet(raw)
            error_payload = dict(data.get("error", {}) or {})
            if not error_payload.get("message"):
                if body_snippet:
                    error_payload["message"] = f"OpenAI HTTP error: {body_snippet}"
                else:
                    error_payload["message"] = "OpenAI HTTP error"
            if body_snippet:
                error_payload["response_body"] = body_snippet
            return OpenAIResponse(
                ok=False,
                model=request.model,
                content="",
                error=_build_error(
                    error_payload,
                    status=status,
                    request_id=request_id,
                ),
                meta={"provider": "openai", "status": status},
            )
        except urllib.error.URLError as exc:
            return OpenAIResponse(
                ok=False,
                model=request.model,
                content="",
                error={"code": "network_error", "message": f"OpenAI network error: {exc.reason}"},
                meta={"provider": "openai"},
            )
        except TimeoutError:
            return OpenAIResponse(
                ok=False,
                model=request.model,
                content="",
                error={"code": "timeout", "message": "OpenAI request timed out"},
                meta={"provider": "openai"},
            )
        except Exception as exc:
            return OpenAIResponse(
                ok=False,
                model=request.model,
                content="",
                error={"code": "unknown", "message": f"OpenAI request failed: {exc}"},
                meta={"provider": "openai"},
            )

        try:
            choice = data["choices"][0]
            content = choice["message"]["content"]
        except Exception:
            content = ""
        usage = data.get("usage") or {}
        return OpenAIResponse(
            ok=True,
            model=request.model,
            content=content,
            usage=usage,
            meta={"provider": "openai", "request_id": request_id},
        )


def _stub_summarize(messages: List[Dict[str, Any]]) -> str:
    if not messages:
        return "OpenAIProvider stub: no messages provided."
    last = messages[-1]
    role = str(last.get("role", "user"))
    content = str(last.get("content", ""))
    content = content.strip()
    if len(content) > 400:
        content = content[:400] + "…"
    return f"OpenAIProvider stub ({role}): {content}"


def _build_error(raw_error: Dict[str, Any], *, status: Optional[int], request_id: Optional[str]) -> Dict[str, Any]:
    message = str(raw_error.get("message") or "OpenAI request failed")
    err_type = str(raw_error.get("type") or "")
    code = str(raw_error.get("code") or "")
    retryable = bool(status in {429, 500, 502, 503, 504})
    if status == 401:
        err_code = "auth_error"
    elif status == 429:
        err_code = "rate_limited"
    elif status in {400, 404, 422}:
        err_code = "invalid_request"
    elif status is None:
        err_code = "unknown"
    else:
        err_code = "http_error"
    return {
        "code": err_code,
        "message": message,
        "http_status": status,
        "request_id": request_id,
        "retryable": retryable,
        "type": err_type,
        "provider_code": code,
        "response_body": raw_error.get("response_body"),
    }


def _safe_body_snippet(raw: str, *, limit: int = 500) -> str:
    if not raw:
        return ""
    snippet = raw[:limit]
    if "sk-" in snippet:
        snippet = snippet.replace("sk-", "[REDACTED]-")
    return snippet


def _should_send_org_header(org_id: Any) -> bool:
    if not isinstance(org_id, str):
        return False
    value = org_id.strip()
    if not value:
        return False
    upper = value.upper()
    if "PUT_" in upper or "PLACEHOLDER" in upper or "YOUR_" in upper or "ORG_ID" in upper:
        return False
    return True


def _extract_request_id(headers: Any) -> Optional[str]:
    if headers is None:
        return None
    return headers.get("x-request-id") or headers.get("openai-request-id") or headers.get("request-id")
