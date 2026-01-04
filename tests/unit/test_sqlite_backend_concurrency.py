
from __future__ import annotations

import threading

from core.contracts.run_schema import RunRecord
from core.memory.sqlite_backend import SQLiteBackend


def test_sqlite_backend_concurrent_writes(tmp_path) -> None:
    db_path = tmp_path / "runs.sqlite3"
    backend = SQLiteBackend(db_path=str(db_path), initialize=True)

    thread_count = 6
    runs_per_thread = 10
    total_runs = thread_count * runs_per_thread
    barrier = threading.Barrier(thread_count)
    errors = []
    lock = threading.Lock()

    def worker(thread_id: int) -> None:
        try:
            barrier.wait()
            for idx in range(runs_per_thread):
                run = RunRecord(
                    run_id=f"run-{thread_id}-{idx}",
                    product="demo",
                    flow="flow",
                    autonomy_level="semi_auto",
                )
                backend.create_run(run)
        except Exception as exc:  # pragma: no cover - failure path
            with lock:
                errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(thread_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors, f"Concurrent writes raised errors: {errors}"

    runs = backend.list_runs(limit=total_runs + 5)
    run_ids = {run.run_id for run in runs}
    expected_ids = {f"run-{thread_id}-{idx}" for thread_id in range(thread_count) for idx in range(runs_per_thread)}
    assert run_ids == expected_ids


def test_sqlite_backend_uses_wal(tmp_path) -> None:
    db_path = tmp_path / "wal.sqlite3"
    backend = SQLiteBackend(db_path=str(db_path), initialize=True)
    con = backend._connect()
    try:
        journal_mode = con.execute("PRAGMA journal_mode;").fetchone()[0]
        busy_timeout = con.execute("PRAGMA busy_timeout;").fetchone()[0]
        assert str(journal_mode).lower() == "wal"
        assert int(busy_timeout) > 0
    finally:
        con.close()
