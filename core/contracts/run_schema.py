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

from __future__ import annotations


# ==============================
# Imports
# ==============================

import time
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional
from uuid import uuid4

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from core.contracts.semantic_schema import SemanticEnvelope

# ==============================
# Enums
# ==============================
class RunStatus(str, Enum):
    """Lifecycle status for a run."""

    RUNNING = "RUNNING"
    PENDING_HUMAN = "PENDING_HUMAN"
    PENDING_USER_INPUT = "PENDING_USER_INPUT"
    PAUSED_WAITING_FOR_USER = "PAUSED_WAITING_FOR_USER"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StepStatus(str, Enum):
    """Lifecycle status for a step."""

    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    PENDING_HUMAN = "PENDING_HUMAN"
    PENDING_USER_INPUT = "PENDING_USER_INPUT"
    PAUSED_WAITING_FOR_USER = "PAUSED_WAITING_FOR_USER"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# ==============================
# Terminal Outcome Enums (IMP-012)
# ==============================
class TerminalOutcome(str, Enum):
    """
    Explicit terminal outcome classification for a run.
    
    ORC-TERM-001..005: Every run must end in exactly one terminal outcome.
    """
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"
    PAUSED_INDEFINITE = "PAUSED_INDEFINITE"


class OutcomeReason(str, Enum):
    """
    Reason for terminal outcome.
    
    ORC-TERM-002: Each outcome has a typed reason enum.
    """
    SUCCESS = "SUCCESS"
    USER_ABORT = "USER_ABORT"
    GOVERNANCE_BLOCK = "GOVERNANCE_BLOCK"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    MAX_ITERATIONS = "MAX_ITERATIONS"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    UNRECOVERABLE_ERROR = "UNRECOVERABLE_ERROR"


class AbortSource(str, Enum):
    """
    Source of an abort action.
    
    ORC-TERM-ART-003: Aborted outcome includes abort source.
    """
    USER = "USER"
    SYSTEM = "SYSTEM"
    GOVERNANCE = "GOVERNANCE"


# ==============================
# Version Tracking (IMP-027)
# ==============================

class Versions(BaseModel):
    """
    Version tracking for reproducibility.
    
    IMP-027: MEM-REPRO-001, MEM-REPRO-002, MEM-REPRO-003
    BRD: BRD-OPS-061
    
    Captures all version information needed to reproduce a run.
    """
    model_config = ConfigDict(extra="forbid")
    
    platform_version: str = Field(
        default="1.0.0",
        description="MASTER platform version."
    )
    flow_version: str = Field(
        default="unknown",
        description="Flow file version or hash."
    )
    python_version: str = Field(
        default="unknown",
        description="Python runtime version."
    )
    models: Dict[str, str] = Field(
        default_factory=dict,
        description="Model versions (model name → version/checkpoint)."
    )
    
    @classmethod
    def capture(
        cls,
        *,
        platform_version: str = "1.0.0",
        flow_version: str = "unknown",
        models: Optional[Dict[str, str]] = None,
    ) -> "Versions":
        """
        Capture current versions.
        
        Args:
            platform_version: Platform version string
            flow_version: Flow file version or hash
            models: Optional model versions dict
            
        Returns:
            Versions instance with captured information
        """
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        return cls(
            platform_version=platform_version,
            flow_version=flow_version,
            python_version=python_version,
            models=models or {},
        )


# ==============================
# Terminal Outcome Artifacts (IMP-013)
# ==============================
class CompletedArtifact(BaseModel):
    """
    Artifact for COMPLETED terminal outcome.
    
    ORC-TERM-ART-001: COMPLETED outcome includes final output artifact.
    """
    model_config = ConfigDict(extra="forbid")
    
    final_output: Dict[str, Any] = Field(
        ...,
        description="Final output produced by the run.",
    )
    output_summary: Optional[str] = Field(
        default=None,
        description="Human-readable summary of the output.",
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Completion metrics (duration, steps executed, etc.).",
    )


class FailedArtifact(BaseModel):
    """
    Artifact for FAILED terminal outcome.
    
    ORC-TERM-ART-002: FAILED outcome includes error artifact with required fields.
    """
    model_config = ConfigDict(extra="forbid")
    
    error_code: str = Field(
        ...,
        description="Machine-readable error code.",
    )
    error_message: str = Field(
        ...,
        description="Human-readable error message.",
    )
    stack_trace: Optional[str] = Field(
        default=None,
        description="Optional stack trace for debugging.",
    )
    failed_step_id: Optional[str] = Field(
        default=None,
        description="ID of the step that caused the failure.",
    )
    recovery_attempted: bool = Field(
        default=False,
        description="Whether recovery was attempted before failing.",
    )


class AbortedArtifact(BaseModel):
    """
    Artifact for ABORTED terminal outcome.
    
    ORC-TERM-ART-003: ABORTED outcome includes abort reason and source.
    """
    model_config = ConfigDict(extra="forbid")
    
    abort_reason: str = Field(
        ...,
        description="Reason for the abort.",
    )
    abort_source: AbortSource = Field(
        ...,
        description="Source of the abort (user/system/governance).",
    )
    aborted_at_step_id: Optional[str] = Field(
        default=None,
        description="ID of the step that was running when abort occurred.",
    )
    partial_output: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Any partial output produced before abort.",
    )


class CancelledArtifact(BaseModel):
    """
    Artifact for CANCELLED terminal outcome.
    
    ORC-TERM-ART-004: CANCELLED outcome includes cancellation details.
    """
    model_config = ConfigDict(extra="forbid")
    
    cancel_reason: Optional[str] = Field(
        default=None,
        description="Reason for cancellation.",
    )
    cancelled_by: Optional[str] = Field(
        default=None,
        description="Entity that initiated cancellation.",
    )
    cancelled_at_step_id: Optional[str] = Field(
        default=None,
        description="ID of the step that was running when cancelled.",
    )


class PausedIndefiniteArtifact(BaseModel):
    """
    Artifact for PAUSED_INDEFINITE terminal outcome.
    
    Captures state for runs paused indefinitely (e.g., awaiting external input).
    """
    model_config = ConfigDict(extra="forbid")
    
    pause_reason: str = Field(
        ...,
        description="Reason for indefinite pause.",
    )
    paused_at_step_id: Optional[str] = Field(
        default=None,
        description="ID of the step where pause occurred.",
    )
    resumable: bool = Field(
        default=True,
        description="Whether the run can be resumed.",
    )
    resume_instructions: Optional[str] = Field(
        default=None,
        description="Instructions for resuming the run.",
    )


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
    semantic_envelope: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Semantic interpretation result (SemanticEnvelope serialized).",
    )
    # Terminal outcome fields (IMP-012: ORC-TERM-001..005)
    terminal_outcome: Optional[TerminalOutcome] = Field(
        default=None,
        description="Explicit terminal outcome classification.",
    )
    outcome_reason: Optional[OutcomeReason] = Field(
        default=None,
        description="Reason for terminal outcome.",
    )
    outcome_explanation: Optional[str] = Field(
        default=None,
        description="Human-readable explanation for terminal outcome.",
    )
    # Terminal artifact (IMP-013: ORC-TERM-ART-001..004)
    terminal_artifact: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Serialized terminal artifact (CompletedArtifact, FailedArtifact, AbortedArtifact, etc.).",
    )
    # Version tracking (IMP-027: MEM-REPRO-001..003)
    versions: Optional[Versions] = Field(
        default=None,
        description="Version information for reproducibility.",
    )
    # Input hashing (IMP-028: MEM-REPRO-010..012)
    input_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of canonical JSON input for reproducibility.",
    )
    # Output hashing (IMP-029: MEM-REPRO-020..021)
    output_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of canonical JSON output for reproducibility.",
    )


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
