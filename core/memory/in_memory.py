# ==============================
# In-Memory Backend (Dev)
# ==============================
"""
In-memory backend for local dev/testing.

Not durable. Deterministic. No file I/O.
"""

from __future__ import annotations



import time
import threading
from typing import Any, Dict, List, Optional

from core.contracts.run_schema import RunRecord, StepRecord, TraceEvent
from core.memory.base import ApprovalRecord, MemoryBackend, RunBundle


class InMemoryBackend(MemoryBackend):
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: Dict[str, RunRecord] = {}
        self._steps: Dict[str, Dict[str, StepRecord]] = {}
        self._events: Dict[str, List[TraceEvent]] = {}
        self._approvals: Dict[str, ApprovalRecord] = {}
        self._sufficiency_states: Dict[str, Dict[str, Any]] = {}  # IMP-017
        self._context_packs: Dict[str, Dict[str, Any]] = {}  # IMP-021

    def create_run(self, run: RunRecord) -> None:
        with self._lock:
            self._runs[run.run_id] = run
            self._steps.setdefault(run.run_id, {})
            self._events.setdefault(run.run_id, [])

    def update_run_status(self, run_id: str, status: str, *, summary: Optional[Dict[str, Any]] = None) -> None:
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                return
            patch: Dict[str, Any] = {"status": status}
            if summary is not None:
                patch["summary"] = summary
            self._runs[run_id] = run.model_copy(update=patch)

    def update_run_output(self, run_id: str, *, output: Optional[Dict[str, Any]]) -> None:
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                return
            self._runs[run_id] = run.model_copy(update={"output": output})

    def update_run(self, run_id: str, patch: Dict[str, Any]) -> None:
        """Update arbitrary fields on a run record."""
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                return
            self._runs[run_id] = run.model_copy(update=patch)

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
        """
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                return
            update_data = {
                "terminal_outcome": terminal_outcome,
                "outcome_reason": outcome_reason,
                "outcome_explanation": outcome_explanation,
            }
            if terminal_artifact is not None:
                update_data["terminal_artifact"] = terminal_artifact
            self._runs[run_id] = run.model_copy(update=update_data)

    def add_step(self, step: StepRecord) -> None:
        with self._lock:
            self._steps.setdefault(step.run_id, {})
            self._steps[step.run_id][step.step_id] = step

    def update_step(self, run_id: str, step_id: str, patch: Dict[str, Any]) -> None:
        with self._lock:
            step = self._steps.get(run_id, {}).get(step_id)
            if step is None:
                return
            self._steps[run_id][step_id] = step.model_copy(update=patch)

    def add_event(self, event: TraceEvent) -> None:
        with self._lock:
            self._events.setdefault(event.run_id, [])
            self._events[event.run_id].append(event)

    def create_approval(self, approval: ApprovalRecord) -> None:
        with self._lock:
            self._approvals[approval.approval_id] = approval

    def resolve_approval(
        self,
        approval_id: str,
        *,
        decision: str,
        resolved_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        with self._lock:
            a = self._approvals.get(approval_id)
            if a is None:
                return
            now = int(time.time())
            status = "APPROVED" if decision.upper().startswith("APPROVE") else "REJECTED"
            self._approvals[approval_id] = a.model_copy(
                update={
                    "status": status,
                    "decision": decision,
                    "resolved_by": resolved_by,
                    "comment": comment,
                    "resolved_at": now,
                }
            )

    def get_run(self, run_id: str) -> Optional[RunBundle]:
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                return None
            steps = list(self._steps.get(run_id, {}).values())
            events = list(self._events.get(run_id, []))
            approvals = [a for a in self._approvals.values() if a.run_id == run_id]
            return RunBundle(run=run, steps=steps, events=events, approvals=approvals)

    def list_runs(self, *, limit: int = 50, offset: int = 0) -> List[RunRecord]:
        with self._lock:
            runs = list(self._runs.values())
            runs.sort(key=lambda r: r.started_at, reverse=True)
            return runs[offset : offset + limit]

    def list_pending_approvals(self, *, limit: int = 50, offset: int = 0) -> List[ApprovalRecord]:
        with self._lock:
            pending = [a for a in self._approvals.values() if a.status == "PENDING"]
            pending.sort(key=lambda a: a.requested_at, reverse=True)
            return pending[offset : offset + limit]

    # IMP-017: Sufficiency state persistence
    def persist_sufficiency_state(
        self,
        run_id: str,
        state: Dict[str, Any],
    ) -> None:
        """Persist sufficiency state for a run."""
        with self._lock:
            self._sufficiency_states[run_id] = state

    def restore_sufficiency_state(
        self,
        run_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Restore sufficiency state for a run."""
        with self._lock:
            return self._sufficiency_states.get(run_id)

    # IMP-021: ContextPack persistence
    def persist_context_pack(
        self,
        run_id: str,
        context_pack: Dict[str, Any],
    ) -> None:
        """Persist frozen ContextPack for a run."""
        with self._lock:
            self._context_packs[run_id] = context_pack

    def restore_context_pack(
        self,
        run_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Restore frozen ContextPack for a run."""
        with self._lock:
            return self._context_packs.get(run_id)

    def ensure_schema(self) -> None:
        # Nothing to create for in-memory backend
        return None

    def get_schema_version(self) -> int:
        return 0
