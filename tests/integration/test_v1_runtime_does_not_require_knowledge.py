from __future__ import annotations

import importlib
import sys
from pathlib import Path


def _import(module_name: str) -> None:
    importlib.import_module(module_name)


def _knowledge_modules(loaded: set[str]) -> set[str]:
    return {
        name
        for name in loaded
        if name == "core.knowledge" or name.startswith("core.knowledge.")
    }


def test_v1_runtime_imports_do_not_require_knowledge(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    storage_dir = tmp_path / "storage"

    monkeypatch.setenv("MASTER__APP__PATHS__REPO_ROOT", repo_root.as_posix())
    monkeypatch.setenv("MASTER__APP__PATHS__STORAGE_DIR", storage_dir.as_posix())

    before_modules = set(sys.modules)

    _import("gateway.api.http_app")
    _import("gateway.ui.platform_app")

    new_modules = set(sys.modules) - before_modules
    knowledge_loaded = _knowledge_modules(new_modules)

    assert not knowledge_loaded, f"Unexpected knowledge modules loaded: {sorted(knowledge_loaded)}"
    assert not (storage_dir / "vectors").exists(), "Vector store initialized during import"
