# ==============================
# Tool Contracts
# ==============================
"""
Tool contracts for master/.

These models define the stable envelope and metadata for tool execution across the platform.
No core module should invent its own tool result shape — use ToolEnvelope.

Intended usage:
- Tool implementations return ToolEnvelope
- Tool executor emits trace events using ToolMeta + ToolError + ToolEnvelope
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict, model_validator

# ==============================
# Typing
# ==============================
T = TypeVar("T")


# ==============================
# Enums
# ==============================
class ToolRisk(str, Enum):
    """Risk classification for governance checks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    DESTRUCTIVE = "destructive"


class ToolErrorCode(str, Enum):
    """Standard error codes for tool failures."""
    INVALID_INPUT = "invalid_input"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    BACKEND_ERROR = "backend_error"
    CONTRACT_VIOLATION = "contract_violation"
    UNKNOWN = "unknown"
    TEMPORARY = "TEMPORARY"


# ==============================
# Models
# ==============================
class ToolMeta(BaseModel):
    """Metadata describing a tool call and its execution context."""
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(..., description="Registered tool name.")
    backend: str = Field(..., description="Execution backend (local|remote|mcp).")
    request_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique id for this tool call.")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Tool call start timestamp (UTC).")
    ended_at: Optional[datetime] = Field(default=None, description="Tool call end timestamp (UTC).")

    latency_ms: Optional[int] = Field(default=None, description="Measured latency in milliseconds.")
    cost_estimate: Optional[float] = Field(default=None, description="Approx cost estimate for this tool call.")

    tags: Dict[str, str] = Field(default_factory=dict, description="Arbitrary tags (product, flow, step, etc.).")
    redacted: bool = Field(default=False, description="Whether inputs/outputs were redacted/sanitized.")


class ToolError(BaseModel):
    """Structured error for tool failures. Errors are data, not control flow."""
    model_config = ConfigDict(extra="forbid")

    code: ToolErrorCode = Field(..., description="Standard tool error code.")
    message: str = Field(..., description="Human readable message.")
    recoverable: bool = Field(default=False, description="Whether retrying might succeed.")
    details: Dict[str, Any] = Field(default_factory=dict, description="Optional structured details (sanitized).")


class ToolEnvelope(BaseModel, Generic[T]):
    """
    Standard envelope for tool results.

    Pattern:
      ok: bool
      data: T | None
      error: ToolError | None
      meta: ToolMeta
    """
    model_config = ConfigDict(extra="forbid")

    ok: bool = Field(..., description="True if tool succeeded.")
    data: Optional[T] = Field(default=None, description="Tool output payload.")
    error: Optional[ToolError] = Field(default=None, description="Tool error if ok=False.")
    meta: ToolMeta = Field(..., description="Tool execution metadata.")

    @model_validator(mode="after")
    def _enforce_error_contract(self) -> "ToolEnvelope[T]":
        if self.ok and self.error is not None:
            raise ValueError("Tool error must be None when ok=True")
        if not self.ok and self.error is None:
            raise ValueError("Tool error is required when ok=False")
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Stable serialization wrapper."""
        return self.model_dump(mode="python")


class ToolResult(ToolEnvelope[Dict[str, Any]]):
    """Concrete envelope used throughout the platform (dict payload)."""

    @classmethod
    def ok(cls, data: Optional[Dict[str, Any]] = None, meta: Optional[ToolMeta] = None) -> "ToolResult":
        return cls(ok=True, data=data or {}, error=None, meta=meta or ToolMeta(tool_name="unknown", backend="local"))

    @classmethod
    def fail(cls, *, error: ToolError, meta: ToolMeta) -> "ToolResult":
        return cls(ok=False, data=None, error=error, meta=meta)


class ToolSpec(BaseModel):
    """
    Tool specification used for registration and discovery.

    This is not the runtime result; it is metadata about a tool and its contract.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Unique tool name in registry.")
    description: str = Field(..., description="Short description of what the tool does.")
    risk: ToolRisk = Field(default=ToolRisk.LOW, description="Governance risk classification.")
    version: str = Field(default="v1", description="Tool semantic version label.")

    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON-schema-like description of inputs.")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON-schema-like description of outputs.")

    idempotent: bool = Field(default=True, description="Whether repeated calls are safe.")
    side_effects: bool = Field(default=False, description="Whether tool causes external side effects.")

    allowed_backends: List[str] = Field(default_factory=lambda: ["local"], description="Allowed execution backends.")

    def to_dict(self) -> Dict[str, Any]:
        """Stable serialization wrapper."""
        return self.model_dump(mode="python")
