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

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict

# ==============================
# Enums
# ==============================
class RunStatus(str, Enum):
    """Lifecycle status for a run."""
    RUNNING = "running"
    PENDING_HUMAN = "pending_human"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Lifecycle status for a step."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    SKIPPED = "skipped"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_HUMAN = "waiting_human"


class TraceLevel(str, Enum):
    """Severity level for trace events."""
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class ArtifactKind(str, Enum):
    """Artifact classification for stored outputs."""
    TEXT = "text"
    JSON = "json"
    FILE = "file"
    BLOB = "blob"


# ==============================
# Models
# ==============================
class ArtifactRef(BaseModel):
    """Reference to an artifact persisted by memory backend."""
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique artifact id.")
    kind: ArtifactKind = Field(..., description="Artifact kind.")
    uri: str = Field(..., description="Storage URI/path (implementation-defined).")
    sha256: Optional[str] = Field(default=None, description="Optional checksum.")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata (sanitized).")


class TraceEvent(BaseModel):
    """A single trace event emitted during a run."""
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event id.")
    run_id: str = Field(..., description="Associated run id.")
    step_id: Optional[str] = Field(default=None, description="Associated step id if applicable.")

    ts: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp (UTC).")
    level: TraceLevel = Field(default=TraceLevel.INFO, description="Event severity.")
    event_type: str = Field(..., description="Machine-readable event type (e.g., step_started, tool_called).")

    message: Optional[str] = Field(default=None, description="Human-readable message (sanitized).")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Structured payload (sanitized).")
    redacted: bool = Field(default=False, description="Whether payload/message were redacted.")


class StepRecord(BaseModel):
    """Persistent record of a single step execution."""
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(..., description="Associated run id.")
    step_id: str = Field(..., description="Step id from flow definition.")
    status: StepStatus = Field(default=StepStatus.NOT_STARTED, description="Current step status.")

    started_at: Optional[datetime] = Field(default=None, description="Step start timestamp (UTC).")
    ended_at: Optional[datetime] = Field(default=None, description="Step end timestamp (UTC).")

    attempt: int = Field(default=0, ge=0, le=100, description="Attempt counter for retries.")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Structured error (sanitized).")

    input_ref: Optional[ArtifactRef] = Field(default=None, description="Optional artifact ref for inputs.")
    output_ref: Optional[ArtifactRef] = Field(default=None, description="Optional artifact ref for outputs.")

    meta: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata (sanitized).")


class RunRecord(BaseModel):
    """Persistent record of a flow run."""
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique run id.")
    product: str = Field(..., description="Product name.")
    flow_id: str = Field(..., description="Flow id.")
    status: RunStatus = Field(default=RunStatus.RUNNING, description="Current run status.")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Run created timestamp (UTC).")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last updated timestamp (UTC).")

    current_step_id: Optional[str] = Field(default=None, description="Current step pointer for resume.")
    steps: List[StepRecord] = Field(default_factory=list, description="Step records (may be partial).")

    summary: Optional[str] = Field(default=None, description="Short summary for UI/status endpoints.")
    final_output_ref: Optional[ArtifactRef] = Field(default=None, description="Artifact ref to final output if any.")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata (sanitized).")

    def to_dict(self) -> Dict[str, Any]:
        """Stable serialization wrapper."""
        return self.model_dump(mode="python")