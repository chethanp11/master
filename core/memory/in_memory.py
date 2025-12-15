# ==============================
# In-Memory Backend (Dev)
# ==============================
"""
In-memory backend for local dev/testing.

Not durable. Deterministic. No file I/O.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from core.contracts.run_schema import RunRecord, StepRecord, TraceEvent
from core.memory.base import ApprovalRecord, MemoryBackend, RunBundle


class InMemoryBackend(MemoryBackend):
    def __init__(self) -> None:
        self._runs: Dict[str, RunRecord] = {}
        self._steps: Dict[str, Dict[str, StepRecord]] = {}
        self._events: Dict[str, List[TraceEvent]] = {}
        self._approvals: Dict[str, ApprovalRecord] = {}

    def create_run(self, run: RunRecord) -> None:
        self._runs[run.run_id] = run
        self._steps.setdefault(run.run_id, {})
        self._events.setdefault(run.run_id, [])

    def update_run_status(self, run_id: str, status: str, *, summary: Optional[Dict[str, Any]] = None) -> None:
        run = self._runs.get(run_id)
        if run is None:
            return
        patch: Dict[str, Any] = {"status": status}
        if summary is not None:
            patch["summary"] = summary
        self._runs[run_id] = run.model_copy(update=patch)

    def add_step(self, step: StepRecord) -> None:
        self._steps.setdefault(step.run_id, {})
        self._steps[step.run_id][step.step_id] = step

    def update_step(self, run_id: str, step_id: str, patch: Dict[str, Any]) -> None:
        step = self._steps.get(run_id, {}).get(step_id)
        if step is None:
            return
        self._steps[run_id][step_id] = step.model_copy(update=patch)

    def add_event(self, event: TraceEvent) -> None:
        self._events.setdefault(event.run_id, [])
        self._events[event.run_id].append(event)

    def create_approval(self, approval: ApprovalRecord) -> None:
        self._approvals[approval.approval_id] = approval

    def resolve_approval(
        self,
        approval_id: str,
        *,
        decision: str,
        resolved_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
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
        run = self._runs.get(run_id)
        if run is None:
            return None
        steps = list(self._steps.get(run_id, {}).values())
        events = list(self._events.get(run_id, []))
        approvals = [a for a in self._approvals.values() if a.run_id == run_id]
        return RunBundle(run=run, steps=steps, events=events, approvals=approvals)

    def list_runs(self, *, limit: int = 50, offset: int = 0) -> List[RunRecord]:
        runs = list(self._runs.values())
        runs.sort(key=lambda r: r.started_at, reverse=True)
        return runs[offset : offset + limit]

    def list_pending_approvals(self, *, limit: int = 50, offset: int = 0) -> List[ApprovalRecord]:
        pending = [a for a in self._approvals.values() if a.status == "PENDING"]
        pending.sort(key=lambda a: a.requested_at, reverse=True)
        return pending[offset : offset + limit]

    def ensure_schema(self) -> None:
        # Nothing to create for in-memory backend
        return None

    def get_schema_version(self) -> int:
        return 0
