# ==============================
# Tests: Orchestrator must not import products
# ==============================
from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List, Tuple


FORBIDDEN_PREFIXES = ("products.",)


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


def test_orchestrator_does_not_import_products() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    orchestrator_root = repo_root / "core" / "orchestrator"
    offenders: List[Tuple[str, str]] = []
    for path in _iter_python_files(orchestrator_root):
        offenders.extend(_check_file(path))
    if offenders:
        details = "\n".join(f"{path}: {module}" for path, module in offenders)
        raise AssertionError(f"Forbidden product imports found in core/orchestrator:\n{details}")
