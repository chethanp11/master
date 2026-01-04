# ==============================
# Tests: Agents must not import memory backends
# ==============================
from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List, Tuple


FORBIDDEN_PREFIXES = (
    "core.memory.sqlite_backend",
    "core.memory.observability_store",
    "core.memory.router",
)


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if path.is_file():
            yield path


def _check_file(path: Path) -> List[Tuple[str, str]]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    offenders: List[Tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if any(name.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
                    offenders.append((str(path), name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module and any(module.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
                offenders.append((str(path), module))
    return offenders


def test_agents_do_not_import_memory_backends() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    agent_roots = [
        repo_root / "core" / "agents",
        repo_root / "products",
    ]
    offenders: List[Tuple[str, str]] = []
    for root in agent_roots:
        if not root.exists():
            continue
        for path in _iter_python_files(root):
            if "agents" not in path.parts:
                continue
            offenders.extend(_check_file(path))
    if offenders:
        details = "\n".join(f"{path}: {module}" for path, module in offenders)
        raise AssertionError(f"Forbidden memory backend imports found in agent code:\n{details}")
