from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", "storage", "secrets", "tests"}


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def _read_imports(path: Path) -> List[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imports: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _find_offenses(
    files: Sequence[Path],
    *,
    forbidden_prefixes: Sequence[str],
    allow_prefixes: Sequence[str] = (),
    allow_modules: Sequence[str] = (),
) -> List[Tuple[Path, str]]:
    offenses: List[Tuple[Path, str]] = []
    for path in files:
        for module in _read_imports(path):
            if module in allow_modules or any(module.startswith(prefix) for prefix in allow_prefixes):
                continue
            if any(module.startswith(prefix) for prefix in forbidden_prefixes):
                offenses.append((path, module))
    return offenses


def _format_offenses(label: str, offenses: List[Tuple[Path, str]]) -> str:
    lines = [f"{label} import violations:"]
    for path, module in sorted(offenses, key=lambda item: (str(item[0]), item[1])):
        lines.append(f"- {path}: {module}")
    return "\n".join(lines)


def test_products_do_not_import_forbidden_core_modules() -> None:
    products_root = REPO_ROOT / "products"
    files = list(_iter_python_files(products_root))
    offenses = _find_offenses(
        files,
        forbidden_prefixes=(
            "core.models",
            "core.memory",
            "core.orchestrator",
            "core.agents.llm_reasoner",
        ),
        allow_modules=("core.orchestrator.context",),
    )
    assert not offenses, _format_offenses("Products", offenses)


def test_tools_do_not_import_agents_or_models() -> None:
    tool_roots = [REPO_ROOT / "core" / "tools", REPO_ROOT / "products"]
    files: List[Path] = []
    for root in tool_roots:
        if not root.exists():
            continue
        for path in _iter_python_files(root):
            if "tools" in path.parts:
                files.append(path)
    offenses = _find_offenses(
        files,
        forbidden_prefixes=("core.agents", "core.models"),
    )
    assert not offenses, _format_offenses("Tools", offenses)


def test_agents_do_not_import_memory_backends_or_tool_executor() -> None:
    agent_roots = [REPO_ROOT / "core" / "agents", REPO_ROOT / "products"]
    files: List[Path] = []
    for root in agent_roots:
        if not root.exists():
            continue
        for path in _iter_python_files(root):
            if "agents" in path.parts:
                files.append(path)
    offenses = _find_offenses(
        files,
        forbidden_prefixes=(
            "core.memory.sqlite_backend",
            "core.memory.in_memory",
            "core.tools.executor",
        ),
    )
    assert not offenses, _format_offenses("Agents", offenses)


def test_ui_does_not_import_core_runtime_layers() -> None:
    ui_root = REPO_ROOT / "gateway" / "ui"
    files = list(_iter_python_files(ui_root))
    offenses = _find_offenses(
        files,
        forbidden_prefixes=(
            "core.orchestrator",
            "core.memory",
            "core.models",
            "core.tools",
            "core.governance",
            "core.agents",
        ),
        allow_prefixes=("core.config", "core.contracts"),
    )
    assert not offenses, _format_offenses("UI", offenses)
