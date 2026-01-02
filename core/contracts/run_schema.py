# ==============================
# Run Contracts
# ==============================
"""
Run contracts for master/.

These models define the stable representation of a run, step records, trace events,
and artifact references used for auditability and pause/resume.

Intended usage:
- Memory backend persists RunRecord + StepRecord + TraceEvent
- Orchestrator reads/writes RunRecord updates through memory backend
- Gateway API returns RunRecord summaries safely
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

# ==============================
# Enums
# ==============================
class RunStatus(str, Enum):
    """Lifecycle status for a run."""

    RUNNING = "RUNNING"
    PENDING_HUMAN = "PENDING_HUMAN"
    PENDING_USER_INPUT = "PENDING_USER_INPUT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StepStatus(str, Enum):
    """Lifecycle status for a step."""

    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    PENDING_HUMAN = "PENDING_HUMAN"
    PENDING_USER_INPUT = "PENDING_USER_INPUT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ArtifactRef(BaseModel):
    """Reference to an artifact persisted by memory backend."""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Artifact handle used by orchestrator.")
    kind: str = Field(..., description="Artifact kind (json, file, text, etc.).")
    uri: str = Field(..., description="Storage URI/path.")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata (sanitized).")


class TraceEvent(BaseModel):
    """A single trace event emitted during a run."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event id.")
    run_id: str = Field(..., description="Associated run id.")
    step_id: Optional[str] = Field(default=None, description="Associated step id if applicable.")
    product: str = Field(..., description="Product name.")
    flow: str = Field(..., description="Flow name.")
    kind: str = Field(
        default="event",
        validation_alias=AliasChoices("kind", "event_type"),
        serialization_alias="event_type",
        description="Machine-readable event type (e.g., step_started).",
    )
    ts: int = Field(default_factory=lambda: int(time.time()), description="Event timestamp (epoch seconds).")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured payload (sanitized).")
    redacted: bool = Field(default=False, description="Whether payload was redacted before persistence.")


class StepRecord(BaseModel):
    """Persistent record of a single step execution."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(..., description="Associated run id.")
    step_id: str = Field(..., description="Step id from flow definition.")
    step_index: int = Field(default=0, description="Zero-based index within the flow.")
    name: str = Field(default="", description="Human readable step name.")
    type: str = Field(default="tool", description="Step type (tool|agent|human_approval|subflow).")
    status: StepStatus = Field(default=StepStatus.NOT_STARTED, description="Current step status.")
    started_at: Optional[int] = Field(default=None, description="Step start timestamp (epoch seconds).")
    finished_at: Optional[int] = Field(default=None, description="Step finish timestamp (epoch seconds).")
    input: Optional[Dict[str, Any]] = Field(default=None, description="Step input payload.")
    output: Optional[Dict[str, Any]] = Field(default=None, description="Step output payload.")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Structured error (sanitized).")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata (backend, target, etc.).")


class RunRecord(BaseModel):
    """Persistent record of a flow run."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    run_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique run id.")
    product: str = Field(..., description="Product name.")
    flow: str = Field(
        ...,
        description="Flow id.",
        validation_alias=AliasChoices("flow", "flow_id"),
        serialization_alias="flow",
    )
    status: RunStatus = Field(default=RunStatus.RUNNING, description="Current run status.")
    autonomy_level: Optional[str] = Field(default=None, description="Flow autonomy level.")
    started_at: int = Field(default_factory=lambda: int(time.time()), description="Run start timestamp.")
    finished_at: Optional[int] = Field(default=None, description="Run finish timestamp.")
    input: Optional[Dict[str, Any]] = Field(default=None, description="Initial payload.")
    output: Optional[Dict[str, Any]] = Field(default=None, description="Final output payload.")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Summary metadata for UI/state.")


class RunOperationError(BaseModel):
    """Structured error for run operations exposed via engine/gateway."""

    code: str = Field(default="run_error")
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class RunOperationResult(BaseModel):
    """Envelope returned by orchestrator public methods (start/resume/get)."""

    model_config = ConfigDict(extra="forbid")

    ok: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[RunOperationError] = None

    @classmethod
    def success(cls, data: Dict[str, Any]) -> "RunOperationResult":
        return cls(ok=True, data=data, error=None)

    @classmethod
    def failure(cls, *, code: str, message: str, details: Optional[Dict[str, Any]] = None) -> "RunOperationResult":
        return cls(ok=False, data=None, error=RunOperationError(code=code, message=message, details=details or {}))
