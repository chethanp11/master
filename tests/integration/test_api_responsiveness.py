from __future__ import annotations

# ==============================
# Integration: API Responsiveness
# ==============================

from pathlib import Path
import threading
import time

import pytest
from fastapi.testclient import TestClient

from core.contracts.run_schema import RunOperationResult
from core.agents.registry import AgentRegistry
from core.tools.registry import ToolRegistry
from gateway.api.http_app import create_app
import gateway.api.deps as deps


def _reset_deps() -> None:
    for dep in (
        deps.get_engine,
        deps.get_settings,
        deps.get_memory_router,
        deps.get_tracer,
        deps.get_product_catalog,
    ):
        cache_clear = getattr(dep, "cache_clear", None)
        if callable(cache_clear):
            cache_clear()


class _SlowEngine:
    def __init__(self, *, started: threading.Event, finished: threading.Event, delay_seconds: float) -> None:
        self._started = started
        self._finished = finished
        self._delay = delay_seconds

    def run_flow(self, *, product: str, flow: str, payload: dict, requested_by: str | None = None) -> RunOperationResult:
        self._started.set()
        time.sleep(self._delay)
        self._finished.set()
        return RunOperationResult.success({"run_id": "slow_run", "status": "PENDING_HUMAN"})


@pytest.mark.integration
def test_health_responsive_during_slow_run(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    sqlite_path = tmp_path / "api.sqlite"
    storage_dir = tmp_path / "storage"
    monkeypatch.setenv("MASTER__APP__PATHS__REPO_ROOT", repo_root.as_posix())
    monkeypatch.setenv("MASTER__APP__PATHS__STORAGE_DIR", storage_dir.as_posix())
    monkeypatch.setenv("MASTER__SECRETS__MEMORY_DB_PATH", sqlite_path.as_posix())

    started = threading.Event()
    finished = threading.Event()
    slow_engine = _SlowEngine(started=started, finished=finished, delay_seconds=0.6)

    _reset_deps()
    AgentRegistry.clear()
    ToolRegistry.clear()
    app = create_app()
    app.dependency_overrides[deps.get_engine] = lambda: slow_engine
    client = TestClient(app)

    def _run_request() -> None:
        resp = client.post("/api/run/hello_world/hello_world", json={"payload": {"keyword": "slow"}})
        body = resp.json()
        assert body["ok"] is True

    run_thread = threading.Thread(target=_run_request)
    run_thread.start()

    assert started.wait(timeout=2.0)

    start = time.monotonic()
    health = client.get("/health")
    elapsed = time.monotonic() - start

    assert health.status_code == 200
    assert elapsed < 0.3
    assert not finished.is_set()

    run_thread.join(timeout=2.0)
    assert finished.is_set()
    client.close()
