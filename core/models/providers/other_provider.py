# ==============================
# Other Provider (Stub)
# ==============================
"""
Placeholder provider adapter.

Purpose:
- Useful to prove that the router/provider boundaries are real.
- If selected, it returns a structured error response.

v1:
- No real vendor integration.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OtherRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(...)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OtherResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool = Field(default=False)
    model: str = Field(...)
    content: str = Field(default="")
    error: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)


class OtherProvider:
    def __init__(self, *, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

    def complete(self, request: OtherRequest) -> OtherResponse:
        return OtherResponse(
            ok=False,
            model=request.model,
            content="",
            error={
                "code": "PROVIDER_NOT_CONFIGURED",
                "message": "OtherProvider is a stub in v1. Configure a real provider adapter under core/models/providers/.",
            },
            meta={"provider": "other", "stub": True},
        )