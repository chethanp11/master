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
from core.memory.observability_store import ObservabilityStore
from core.memory.sqlite_backend import SQLiteBackend


class MemoryRouter(MemoryBackend):
    def __init__(
        self,
        backend: MemoryBackend,
        *,
        repo_root: Optional[Path] = None,
        observability_root: Optional[Path] = None,
    ) -> None:
        self.backend = backend
        # Observability store is internal to the memory layer; keep call sites centralized here.
        self._observability = (
            ObservabilityStore(repo_root=repo_root, observability_root=observability_root)
            if repo_root
            else None
        )

    def create_run(self, run: RunRecord) -> None:
        self.backend.create_run(run)

    def update_run_status(self, run_id: str, status: str, *, summary: Optional[Dict[str, Any]] = None) -> None:
        self.backend.update_run_status(run_id, status, summary=summary)

    def update_run_output(self, run_id: str, *, output: Optional[Dict[str, Any]]) -> None:
        self.backend.update_run_output(run_id, output=output)

    def update_run_output(self, run_id: str, *, output: Optional[Dict[str, Any]]) -> None:
        self.backend.update_run_output(run_id, output=output)

    def add_step(self, step: StepRecord) -> None:
        self.backend.add_step(step)

    def update_step(self, run_id: str, step_id: str, patch: Dict[str, Any]) -> None:
        self.backend.update_step(run_id, step_id, patch)

    def add_event(self, event: TraceEvent) -> None:
        self.backend.add_event(event)

    def append_trace_event(self, event: TraceEvent) -> None:
        self.backend.append_trace_event(event)
        if self._observability is None:
            return
        self._observability.append_event(
            product=event.product,
            run_id=event.run_id,
            payload=event.model_dump(mode="json"),
        )

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

    def append_run_comment(
        self,
        *,
        product: str,
        run_id: str,
        comment: Optional[str],
        decision: Optional[str] = None,
        step_id: Optional[str] = None,
        ts: Optional[int] = None,
    ) -> None:
        if self._observability is None:
            return
        self._observability.append_comment(
            product=product,
            run_id=run_id,
            comment=comment or "",
            decision=decision,
            step_id=step_id,
            ts=ts,
        )

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

    def ensure_observability_dirs(self, *, product: str, run_id: str) -> None:
        if self._observability is None:
            return
        self._observability.ensure_dirs(product=product, run_id=run_id)

    def get_observability_dirs(self, *, product: str, run_id: str) -> Dict[str, Path]:
        if self._observability is None:
            return {}
        return self._observability.ensure_dirs(product=product, run_id=run_id)

    def clear_staging(self, *, product: str, clear_input: bool = True, clear_output: bool = True) -> None:
        if self._observability is None:
            return
        self._observability.clear_staging(product=product, clear_input=clear_input, clear_output=clear_output)

    def move_staged_inputs_to_run(self, *, product: str, run_id: str) -> None:
        if self._observability is None:
            return
        self._observability.move_staged_inputs_to_run(product=product, run_id=run_id)

    def capture_run_input(self, *, product: str, run_id: str, payload: Dict[str, Any]) -> None:
        if self._observability is None:
            return
        wrote = self._observability.write_input_payload(product=product, run_id=run_id, payload=payload)
        if not wrote:
            return
        self._observability.stage_attachments(product=product, run_id=run_id, payload=payload)

    def write_run_response(self, *, product: str, run_id: str, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self._observability is None:
            return None
        return self._observability.write_response(product=product, run_id=run_id, response=response)

    def write_output_files(self, *, product: str, run_id: str, files: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        if self._observability is None:
            return None
        return self._observability.write_output_files(product=product, run_id=run_id, files=files)

    def write_user_input_response(
        self,
        *,
        product: str,
        run_id: str,
        form_id: str,
        payload: Dict[str, Any],
    ) -> Optional[Path]:
        if self._observability is None:
            return None
        return self._observability.write_user_input_response(
            product=product,
            run_id=run_id,
            form_id=form_id,
            payload=payload,
        )

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
        observability_dir = _resolve(settings.app.paths.observability_dir)
        memory_dir = storage_dir / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)

        db_path = settings.secrets.memory_db_path
        db_file = _resolve(db_path) if db_path else (memory_dir / "master.sqlite")
        db_file.parent.mkdir(parents=True, exist_ok=True)

        backend = SQLiteBackend(db_path=str(db_file))
        backend.ensure_schema()
        return cls(backend, repo_root=repo_root, observability_root=observability_dir)
