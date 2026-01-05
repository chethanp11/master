from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from core.config.schema import AppConfig, FeatureFlagsConfig, PathsConfig, Settings
from core.memory.base import MemoryBackendLoadError
from core.memory.router import MemoryRouter


def _build_settings(tmp_path: Path, *, enable_sqlite: bool) -> Settings:
    return Settings(
        app=AppConfig(
            paths=PathsConfig(
                repo_root=str(tmp_path),
                storage_dir="storage",
                observability_dir="observability",
            ),
            features=FeatureFlagsConfig(enable_sqlite_backend=enable_sqlite),
        )
    )


def test_memory_router_does_not_import_sqlite_backend_when_disabled(tmp_path: Path) -> None:
    sys.modules.pop("core.memory.sqlite_backend", None)
    settings = _build_settings(tmp_path, enable_sqlite=False)

    router = MemoryRouter.from_settings(settings)

    assert "core.memory.sqlite_backend" not in sys.modules
    assert router.backend.__class__.__name__ == "InMemoryBackend"


def test_memory_router_sqlite_missing_raises_typed_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _build_settings(tmp_path, enable_sqlite=True)

    def _raise(_: str):
        raise ImportError("sqlite unavailable")

    monkeypatch.setattr(importlib, "import_module", _raise)

    with pytest.raises(MemoryBackendLoadError) as excinfo:
        MemoryRouter.from_settings(settings)

    assert excinfo.value.code == "sqlite_backend_unavailable"
