# ==============================
# Memory Router
# ==============================
"""
Memory router provides a single interface used by orchestrator + tracer.

v1:
- Delegates all operations to a chosen backend (sqlite or in-memory).
- Keeps room for future multi-store routing (short/long/episodic) without changing callers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from core.contracts.run_schema import RunRecord, StepRecord, TraceEvent
from core.config.schema import Settings
from core.memory.base import ApprovalRecord, MemoryBackend, RunBundle
from core.memory.sqlite_backend import SQLiteBackend


class MemoryRouter(MemoryBackend):
    def __init__(self, backend: MemoryBackend) -> None:
        self.backend = backend

    def create_run(self, run: RunRecord) -> None:
        self.backend.create_run(run)

    def update_run_status(self, run_id: str, status: str, *, summary: Optional[Dict[str, Any]] = None) -> None:
        self.backend.update_run_status(run_id, status, summary=summary)

    def add_step(self, step: StepRecord) -> None:
        self.backend.add_step(step)

    def update_step(self, run_id: str, step_id: str, patch: Dict[str, Any]) -> None:
        self.backend.update_step(run_id, step_id, patch)

    def add_event(self, event: TraceEvent) -> None:
        self.backend.add_event(event)

    def append_trace_event(self, event: TraceEvent) -> None:
        self.backend.append_trace_event(event)

    def create_approval(self, approval: ApprovalRecord) -> None:
        self.backend.create_approval(approval)

    def resolve_approval(
        self,
        approval_id: str,
        *,
        decision: str,
        resolved_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        self.backend.resolve_approval(approval_id, decision=decision, resolved_by=resolved_by, comment=comment)

    def get_run(self, run_id: str) -> Optional[RunBundle]:
        return self.backend.get_run(run_id)

    def list_runs(self, *, limit: int = 50, offset: int = 0) -> List[RunRecord]:
        return self.backend.list_runs(limit=limit, offset=offset)

    def list_pending_approvals(self, *, limit: int = 50, offset: int = 0) -> List[ApprovalRecord]:
        return self.backend.list_pending_approvals(limit=limit, offset=offset)

    def ensure_schema(self) -> None:
        self.backend.ensure_schema()

    def get_schema_version(self) -> int:
        return self.backend.get_schema_version()

    @classmethod
    def from_settings(cls, settings: Settings) -> "MemoryRouter":
        """
        Instantiate router using repo settings.
        """
        repo_root = settings.repo_root_path()

        def _resolve(path_str: str) -> Path:
            path = Path(path_str)
            return path if path.is_absolute() else (repo_root / path)

        storage_dir = _resolve(settings.app.paths.storage_dir)
        memory_dir = storage_dir / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)

        db_path = settings.secrets.memory_db_path
        db_file = _resolve(db_path) if db_path else (memory_dir / "master.sqlite")
        db_file.parent.mkdir(parents=True, exist_ok=True)

        backend = SQLiteBackend(db_path=str(db_file))
        backend.ensure_schema()
        return cls(backend)
