# ==============================
# Agent Contracts
# ==============================
"""
Agent contracts for master/.

Agents are first-class reasoning units. They must return AgentEnvelope.
Agents do not execute tools directly. They may request tool actions via structured outputs.

Intended usage:
- Orchestrator invokes Agent.run(context) and expects AgentEnvelope
- Tracing uses AgentMeta + AgentError
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict, model_validator

# ==============================
# Typing
# ==============================
T = TypeVar("T")


# ==============================
# Enums
# ==============================
class AgentKind(str, Enum):
    """High-level category for agents."""
    PLANNER = "planner"
    EXECUTOR = "executor"
    CRITIC = "critic"
    ROUTER = "router"
    SUMMARIZER = "summarizer"
    VALIDATOR = "validator"
    OTHER = "other"


class AgentErrorCode(str, Enum):
    """Standard error codes for agent failures."""
    INVALID_INPUT = "invalid_input"
    POLICY_BLOCKED = "policy_blocked"
    MODEL_ERROR = "model_error"
    TIMEOUT = "timeout"
    CONTRACT_VIOLATION = "contract_violation"
    UNKNOWN = "unknown"


# ==============================
# Models
# ==============================
class AgentMeta(BaseModel):
    """Metadata describing an agent run."""
    model_config = ConfigDict(extra="forbid")

    agent_name: str = Field(..., description="Registered agent name.")
    kind: AgentKind = Field(default=AgentKind.OTHER, description="Agent category.")
    request_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique id for this agent call.")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Agent call start timestamp (UTC).")
    ended_at: Optional[datetime] = Field(default=None, description="Agent call end timestamp (UTC).")

    latency_ms: Optional[int] = Field(default=None, description="Measured latency in milliseconds.")
    token_estimate: Optional[int] = Field(default=None, description="Approx tokens used by agent/model calls.")
    cost_estimate: Optional[float] = Field(default=None, description="Approx cost estimate for this agent run.")

    tags: Dict[str, str] = Field(default_factory=dict, description="Arbitrary tags (product, flow, step, etc.).")
    redacted: bool = Field(default=False, description="Whether inputs/outputs were redacted/sanitized.")


class AgentError(BaseModel):
    """Structured error for agent failures. Errors are data, not control flow."""
    model_config = ConfigDict(extra="forbid")

    code: AgentErrorCode = Field(..., description="Standard agent error code.")
    message: str = Field(..., description="Human readable message.")
    recoverable: bool = Field(default=False, description="Whether retrying might succeed.")
    details: Dict[str, Any] = Field(default_factory=dict, description="Optional structured details (sanitized).")


class AgentEnvelope(BaseModel, Generic[T]):
    """
    Standard envelope for agent results.

    Pattern:
      ok: bool
      data: T | None
      error: AgentError | None
      meta: AgentMeta
    """
    model_config = ConfigDict(extra="forbid")

    ok: bool = Field(..., description="True if agent succeeded.")
    data: Optional[T] = Field(default=None, description="Agent output payload.")
    error: Optional[AgentError] = Field(default=None, description="Agent error if ok=False.")
    meta: AgentMeta = Field(..., description="Agent execution metadata.")

    @model_validator(mode="after")
    def _enforce_error_contract(self) -> "AgentEnvelope[T]":
        if self.ok and self.error is not None:
            raise ValueError("Agent error must be None when ok=True")
        if not self.ok and self.error is None:
            raise ValueError("Agent error is required when ok=False")
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Stable serialization wrapper."""
        return self.model_dump(mode="python")


# Backwards-compatible default envelope used across the platform.
AgentResult = AgentEnvelope[Dict[str, Any]]


class AgentSpec(BaseModel):
    """
    Agent specification used for registration and discovery.

    This is not the runtime result; it is metadata about an agent and its interface.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Unique agent name in registry.")
    kind: AgentKind = Field(default=AgentKind.OTHER, description="Agent category.")
    description: str = Field(..., description="Short description of responsibilities.")
    version: str = Field(default="v1", description="Agent semantic version label.")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON-schema-like description of inputs.")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON-schema-like description of outputs.")

    def to_dict(self) -> Dict[str, Any]:
        """Stable serialization wrapper."""
        return self.model_dump(mode="python")
