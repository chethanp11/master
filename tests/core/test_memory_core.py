# ==============================
# Tests: Memory (SQLite Backend)
# ==============================
from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace

from core.memory.base import ApprovalRecord
from core.memory.sqlite_backend import SQLiteBackend
from scripts import migrate_memory


def _make_run(run_id: str, *, started_at: int) -> SimpleNamespace:
    return SimpleNamespace(
        run_id=run_id,
        product="sandbox",
        flow="hello_world",
        status="RUNNING",
        autonomy_level="manual",
        started_at=started_at,
        finished_at=None,
        input={"hello": "world"},
        output=None,
        summary={"current_step_index": 0},
    )


def _make_step(run_id: str, *, step_id: str, idx: int) -> SimpleNamespace:
    return SimpleNamespace(
        run_id=run_id,
        step_id=step_id,
        step_index=idx,
        name=f"step_{idx}",
        type="agent",
        status="RUNNING",
        started_at=int(time.time()),
        finished_at=None,
        input={"foo": "bar"},
        output=None,
        error=None,
        meta={"agent": "simple"},
    )


def _make_event(run_id: str, step_id: str) -> SimpleNamespace:
    return SimpleNamespace(
        kind="step_started",
        run_id=run_id,
        step_id=step_id,
        product="sandbox",
        flow="hello_world",
        ts=int(time.time()),
        payload={"ok": True},
    )


def test_sqlite_backend_schema_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "schema.sqlite"
    backend = SQLiteBackend(db_path=str(db_path))
    backend.ensure_schema()
    first = backend.get_schema_version()
    backend.ensure_schema()
    assert backend.get_schema_version() == first == 1


def test_sqlite_backend_run_step_event_and_approvals_roundtrip(tmp_path: Path) -> None:
    db_path = tmp_path / "mem.sqlite"
    backend = SQLiteBackend(db_path=str(db_path))
    backend.ensure_schema()

    run = _make_run("run_1", started_at=int(time.time()))
    backend.create_run(run)

    step = _make_step(run.run_id, step_id="step-1", idx=0)
    backend.add_step(step)
    backend.update_step(run.run_id, step.step_id, {"status": "COMPLETED", "output": {"ok": True}, "finished_at": int(time.time())})

    event = _make_event(run.run_id, step.step_id)
    backend.add_event(event)

    approval = ApprovalRecord(
        approval_id="ap_1",
        run_id=run.run_id,
        step_id=step.step_id,
        product="sandbox",
        flow="hello_world",
        status="PENDING",
        requested_by="tester",
        requested_at=int(time.time()),
        resolved_by=None,
        resolved_at=None,
        decision=None,
        comment=None,
        payload={"question": "ok?"},
    )
    backend.create_approval(approval)

    pending = backend.list_pending_approvals()
    assert any(a.approval_id == approval.approval_id for a in pending)

    backend.resolve_approval(approval.approval_id, decision="approved", resolved_by="tester", comment="looks good")
    assert not any(a.approval_id == approval.approval_id for a in backend.list_pending_approvals())

    bundle = backend.get_run(run.run_id)
    assert bundle is not None
    assert bundle.run.run_id == run.run_id
    assert bundle.steps and bundle.steps[0].step_id == step.step_id
    assert bundle.events and bundle.events[0].kind == event.kind
    assert bundle.approvals and bundle.approvals[0].status in {"APPROVED", "REJECTED"}

    runs = backend.list_runs(limit=10)
    assert runs and runs[0].run_id == run.run_id


def test_migrate_memory_script_smoke(tmp_path: Path) -> None:
    db_path = tmp_path / "cli.sqlite"
    code = migrate_memory.main(["--db-path", str(db_path), "--apply"])
    assert code == 0
    assert db_path.exists()
