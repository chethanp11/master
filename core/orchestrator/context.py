# ==============================
# Orchestrator Context
# ==============================
"""
RunContext and StepContext for orchestrator execution.

Principles:
- Context is the in-memory working set for a run.
- Context is NOT persistence. Persistence happens via core/memory/* only.
- Context provides:
    - metadata (safe, non-secret)
    - artifacts (references + inline working objects)
    - trace hook placeholder (emit events via tracing pipeline elsewhere)

Intended usage:
- Orchestrator constructs RunContext at run start (or resume)
- Each step receives a StepContext derived from RunContext
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.flow_schema import FlowDef, StepDef
from core.contracts.run_schema import ArtifactRef, RunRecord
from core.orchestrator.state import RunStatus, StepStatus

# ==============================
# Trace Hook Types
# ==============================
TraceHook = Callable[[str, Dict[str, Any]], None]
# TraceHook signature:
#   trace(event_type: str, payload: dict) -> None
# Implementations live in core/logging/tracing.py later.


# ==============================
# Artifact Store
# ==============================
class ArtifactStore(BaseModel):
    """
    In-memory artifact bag for a run.

    Stores:
    - inline: arbitrary python objects for in-run use (NOT persisted)
    - refs: ArtifactRef objects that point to persisted artifacts (persisted by memory backend)
    """
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    inline: Dict[str, Any] = Field(default_factory=dict, description="In-run, in-memory objects (not persisted).")
    refs: Dict[str, ArtifactRef] = Field(default_factory=dict, description="Artifact references persisted elsewhere.")

    def put_inline(self, key: str, value: Any) -> None:
        self.inline[key] = value

    def get_inline(self, key: str, default: Any = None) -> Any:
        return self.inline.get(key, default)

    def put_ref(self, key: str, ref: ArtifactRef) -> None:
        self.refs[key] = ref

    def get_ref(self, key: str) -> Optional[ArtifactRef]:
        return self.refs.get(key)


# ==============================
# Run Context
# ==============================
class RunContext(BaseModel):
    """
    Execution context for a run.

    Notes:
    - run_record is a snapshot reference for the current run state (persist via memory backend).
    - metadata is mutable and should remain sanitized (no secrets).
    - artifacts stores in-run objects and persisted references.
    - trace is a callable hook; if unset, calls should be no-ops.
    """
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    run_record: RunRecord = Field(..., description="Current run record snapshot.")
    flow: FlowDef = Field(..., description="Loaded and validated flow definition.")

    status: RunStatus = Field(default=RunStatus.RUNNING, description="Current run status.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Context creation time (UTC).")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="Mutable metadata (sanitized).")
    artifacts: ArtifactStore = Field(default_factory=ArtifactStore, description="Artifact store for the run.")

    trace: Optional[TraceHook] = Field(default=None, description="Trace emitter hook (optional).")

    def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Emit a trace event through the configured hook (no-op if unset)."""
        if self.trace is None:
            return
        self.trace(event_type, payload)

    @property
    def run_id(self) -> str:
        return self.run_record.run_id

    @property
    def product(self) -> str:
        return self.run_record.product

    @property
    def flow_id(self) -> str:
        return self.run_record.flow_id


# ==============================
# Step Context
# ==============================
class StepContext(BaseModel):
    """
    Execution context for a single step.

    Derived from RunContext and includes the StepDef being executed.
    """
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    run: RunContext = Field(..., description="Parent run context.")
    step: StepDef = Field(..., description="Step definition.")
    status: StepStatus = Field(default=StepStatus.NOT_STARTED, description="Current step status.")
    attempt: int = Field(default=0, ge=0, le=100, description="Attempt counter for retries.")

    def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Emit a step-scoped trace event."""
        merged = {"step_id": self.step.id, **payload}
        self.run.emit(event_type, merged)