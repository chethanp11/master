# ==============================
# Integration: Session Isolation
# ==============================
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict

import pytest

from core.config.loader import load_settings
from core.memory.router import MemoryRouter
from core.memory.sqlite_backend import SQLiteBackend
from core.memory.tracing import Tracer
from core.orchestrator.engine import OrchestratorEngine


@pytest.mark.integration
def test_concurrent_runs_isolated(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    sqlite_path = tmp_path / "api.sqlite"
    storage_dir = tmp_path / "storage"
    env = {
        "MASTER__APP__PATHS__REPO_ROOT": repo_root.as_posix(),
        "MASTER__APP__PATHS__STORAGE_DIR": storage_dir.as_posix(),
        "MASTER__SECRETS__MEMORY_DB_PATH": sqlite_path.as_posix(),
    }
    settings = load_settings(repo_root=str(repo_root), env=env)
    backend = SQLiteBackend(db_path=sqlite_path.as_posix())
    backend.ensure_schema()
    memory = MemoryRouter(backend, repo_root=None)
    tracer = Tracer.from_settings(settings=settings, memory=memory)

    payloads = [{"keyword": "alpha"}, {"keyword": "beta"}]

    def _start_run(payload: Dict[str, str]) -> str:
        engine = OrchestratorEngine.from_settings(settings=settings, memory=memory, tracer=tracer)
        result = engine.run_flow(product="hello_world", flow="hello_world", payload=payload)
        assert result.ok is True
        return result.data["run_id"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        run_ids = list(executor.map(_start_run, payloads))

    assert len(set(run_ids)) == 2

    for payload, run_id in zip(payloads, run_ids):
        bundle = memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.input == payload
