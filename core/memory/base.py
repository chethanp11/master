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


class MemoryBackendLoadError(Exception):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def as_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message}


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
    def update_run(self, run_id: str, patch: Dict[str, Any]) -> None:
        """Update arbitrary fields on a run record."""
        raise NotImplementedError

    def update_run_terminal_outcome(
        self,
        run_id: str,
        *,
        terminal_outcome: str,
        outcome_reason: str,
        outcome_explanation: str,
        terminal_artifact: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update terminal outcome fields on a run record.
        
        IMP-012 (ORC-TERM-001..005): Persist terminal outcome classification.
        IMP-013 (ORC-TERM-ART-001..004): Persist terminal artifact.
        
        Default implementation updates via generic patch mechanism.
        Concrete backends may override for optimized persistence.
        
        Args:
            run_id: Run ID
            terminal_outcome: Terminal outcome enum value
            outcome_reason: Outcome reason enum value
            outcome_explanation: Human-readable explanation
            terminal_artifact: Serialized terminal artifact (optional)
        """
        # Default: call update_run_status with terminal fields in summary
        # Concrete backends should override if they have direct field support
        pass

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

    # Sufficiency state persistence (IMP-017: INT-SUFF-LC-003..004)
    def persist_sufficiency_state(
        self,
        run_id: str,
        state: Dict[str, Any],
    ) -> None:
        """
        Persist sufficiency state for a run.
        
        IMP-017 (INT-SUFF-LC-003): Persist state after each reasoning pass.
        
        Args:
            run_id: Run ID
            state: Serialized SufficiencyState
        """
        pass

    def restore_sufficiency_state(
        self,
        run_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Restore sufficiency state for a run.
        
        IMP-017 (INT-SUFF-LC-004): State restorable from persistence.
        
        Args:
            run_id: Run ID
            
        Returns:
            Serialized SufficiencyState or None if not found.
        """
        return None

    # ContextPack persistence (IMP-021: INT-CP-FREEZE-LC-002)
    def persist_context_pack(
        self,
        run_id: str,
        context_pack: Dict[str, Any],
    ) -> None:
        """
        Persist frozen ContextPack for a run.
        
        IMP-021 (INT-CP-FREEZE-LC-002): Frozen ContextPack persisted for audit.
        
        Args:
            run_id: Run ID
            context_pack: Serialized frozen ContextPack
        """
        pass

    def restore_context_pack(
        self,
        run_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Restore frozen ContextPack for a run.
        
        IMP-021 (INT-CP-FREEZE-LC-002): Supports reproducibility for audit.
        
        Args:
            run_id: Run ID
            
        Returns:
            Serialized ContextPack or None if not found.
        """
        return None

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
