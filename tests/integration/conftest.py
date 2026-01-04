# ==============================
# Integration fixtures
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def hello_world_test_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Shared env fixture for integration tests that rely on sqlite-backed memory.

    This fixture ensures we use deterministic sqlite paths (for runs, approvals, and
    ingestion) without duplicating environment overrides in every test.
    """
    repo_root = Path(__file__).resolve().parents[2]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "integration.sqlite"

    monkeypatch.setenv("MASTER__APP__PATHS__REPO_ROOT", repo_root.as_posix())
    monkeypatch.setenv("MASTER__APP__PATHS__STORAGE_DIR", storage_dir.as_posix())
    monkeypatch.setenv("MASTER__SECRETS__MEMORY_DB_PATH", sqlite_path.as_posix())

    return sqlite_path
