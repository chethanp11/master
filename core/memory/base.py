# ==============================
# Memory Backend Contracts
# ==============================
"""
Memory layer is the ONLY place where persistence is allowed.

This module defines:
- MemoryBackend interface used by orchestrator + tracing.
- Pydantic records for approvals and bundled run retrieval.

Rules:
- No vendor calls.
- No tool execution.
- Concrete persistence lives in sqlite_backend.py (or other backends).
"""

from __future__ import annotations



from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.run_schema import RunRecord, StepRecord, TraceEvent


class ApprovalRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approval_id: str = Field(...)
    run_id: str = Field(...)
    step_id: str = Field(...)
    product: str = Field(...)
    flow: str = Field(...)
    status: str = Field(default="PENDING")  # PENDING | APPROVED | REJECTED
    requested_by: Optional[str] = Field(default=None)
    requested_at: int = Field(...)
    resolved_by: Optional[str] = Field(default=None)
    resolved_at: Optional[int] = Field(default=None)
    decision: Optional[str] = Field(default=None)  # APPROVE/REJECT or custom
    comment: Optional[str] = Field(default=None)
    payload: Dict[str, Any] = Field(default_factory=dict)  # scrubbed payload for UI display


class RunBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run: RunRecord = Field(...)
    steps: List[StepRecord] = Field(default_factory=list)
    events: List[TraceEvent] = Field(default_factory=list)
    approvals: List[ApprovalRecord] = Field(default_factory=list)


class MemoryBackend(ABC):
    """
    Interface used by core.orchestrator and core.memory.Tracer.

    Minimal set of operations for v1:
    - runs + steps + events
    - HITL approvals
    """

    @abstractmethod
    def create_run(self, run: RunRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_run_status(self, run_id: str, status: str, *, summary: Optional[Dict[str, Any]] = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_run_output(self, run_id: str, *, output: Optional[Dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_step(self, step: StepRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_step(self, run_id: str, step_id: str, patch: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_event(self, event: TraceEvent) -> None:
        raise NotImplementedError

    # For tracing convenience (Tracer calls this)
    def append_trace_event(self, event: TraceEvent) -> None:
        self.add_event(event)

    @abstractmethod
    def create_approval(self, approval: ApprovalRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    def resolve_approval(
        self,
        approval_id: str,
        *,
        decision: str,
        resolved_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_run(self, run_id: str) -> Optional[RunBundle]:
        raise NotImplementedError

    @abstractmethod
    def list_runs(self, *, limit: int = 50, offset: int = 0) -> List[RunRecord]:
        raise NotImplementedError

    @abstractmethod
    def list_pending_approvals(self, *, limit: int = 50, offset: int = 0) -> List[ApprovalRecord]:
        raise NotImplementedError

    # Optional hooks for durable backends so tooling/migrations can introspect.
    def ensure_schema(self) -> None:
        """
        Ensure backing schema exists. In-memory backends can no-op.
        """
        return None

    def get_schema_version(self) -> int:
        """
        Return integer schema version if supported. Defaults to 0.
        """
        return 0
