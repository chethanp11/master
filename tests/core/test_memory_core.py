# ==============================
# Tests: Memory (SQLite Backend)
# ==============================
from __future__ import annotations

from pathlib import Path

import pytest

from core.memory.sqlite_backend import SQLiteMemoryBackend


def test_sqlite_backend_creates_schema_and_writes_run(tmp_path: Path) -> None:
    db_path = tmp_path / "mem.sqlite"
    backend = SQLiteMemoryBackend(sqlite_path=str(db_path))
    backend.ensure_schema()

    run_id = "r1"
    backend.create_run(run_id=run_id, product="sandbox", flow="hello_world", payload={"a": 1})
    backend.update_run_status(run_id=run_id, status="RUNNING")

    run = backend.get_run(run_id=run_id)
    assert run is not None
    assert run["run_id"] == "r1"
    assert run["product"] == "sandbox"
    assert run["flow"] == "hello_world"


def test_sqlite_backend_approvals_roundtrip(tmp_path: Path) -> None:
    db_path = tmp_path / "mem2.sqlite"
    backend = SQLiteMemoryBackend(sqlite_path=str(db_path))
    backend.ensure_schema()

    run_id = "r2"
    backend.create_run(run_id=run_id, product="sandbox", flow="hello_world", payload={})

    approval_id = backend.create_approval(run_id=run_id, step_id="approval", title="Approve", message="ok?", form={})
    pending = backend.list_pending_approvals(product=None)
    assert any(a["approval_id"] == approval_id for a in pending)

    backend.resolve_approval(approval_id=approval_id, decision={"approved": True, "notes": "ok"})
    pending2 = backend.list_pending_approvals(product=None)
    assert not any(a["approval_id"] == approval_id for a in pending2)