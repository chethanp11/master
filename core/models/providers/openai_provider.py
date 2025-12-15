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
- Read API keys from core/config/loader.py injected config (never from os.environ here).
- Add retry, timeouts, and structured error mapping to AgentError/ToolError envelopes.
"""

from __future__ import annotations

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
        # v1 stub: no external calls
        # Return deterministic placeholder so downstream code can be tested.
        content = _stub_summarize(request.messages)
        return OpenAIResponse(
            ok=True,
            model=request.model,
            content=content,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            meta={"provider": "openai", "stub": True},
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