# ==============================
# Guardrail Validations
# ==============================
from __future__ import annotations

import pathlib
import re
from typing import List


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", "storage", "secrets", "tests", "scripts"}


def _iter_python_files() -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    for path in REPO_ROOT.rglob("*.py"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _find_offenses(pattern: str, files: List[pathlib.Path], *, allow: List[pathlib.Path]) -> List[pathlib.Path]:
    offenders: List[pathlib.Path] = []
    for path in files:
        if any(path == allowed or allowed in path.parents for allowed in allow):
            continue
        if re.search(pattern, _read(path)):
            offenders.append(path)
    return offenders


def test_no_os_environ_outside_loader() -> None:
    files = _iter_python_files()
    permitted = [REPO_ROOT / "core" / "config" / "loader.py"]
    pattern = r"os\.environ"
    offenders = _find_offenses(pattern, files, allow=permitted)
    assert not offenders, f"os.environ reads only allowed in core/config/loader.py, found in: {offenders}"


def test_model_router_is_only_provider_entrypoint() -> None:
    files = _iter_python_files()
    permitted = [
        REPO_ROOT / "core" / "models" / "router.py",
        REPO_ROOT / "core" / "models" / "providers",
    ]
    pattern = r"\bcore\.models\b"
    offenders = _find_offenses(pattern, files, allow=permitted)
    assert not offenders, (
        "Direct model/provider imports are only permitted under core/models/router.py "
        f"or core/models/providers/*, found in: {offenders}"
    )


def test_tool_executor_is_centralized() -> None:
    files = _iter_python_files()
    allowed = {
        REPO_ROOT / "core" / "orchestrator" / "engine.py",
        REPO_ROOT / "core" / "orchestrator" / "step_executor.py",
        REPO_ROOT / "tests" / "core" / "test_tools_core.py",
        REPO_ROOT / "core" / "tools" / "executor.py",
    }
    pattern = r"ToolExecutor"
    offenders = _find_offenses(pattern, files, allow=list(allowed))
    assert not offenders, (
        "Only orchestrator/engine, orchestrator/step_executor, and test_tools_core should reference ToolExecutor directly. "
        f"Offenders: {offenders}"
    )


def test_sqlite_imports_constrained_to_persistence_modules() -> None:
    files = _iter_python_files()
    allowed = {
        REPO_ROOT / "core" / "memory" / "sqlite_backend.py",
        REPO_ROOT / "core" / "knowledge" / "vector_store.py",
    }
    pattern = r"\bsqlite3\b"
    offenders = _find_offenses(pattern, files, allow=list(allowed))
    assert not offenders, (
        "Direct sqlite3 usage must be contained within persistence helpers. Offending files: {offenders}"
    )
