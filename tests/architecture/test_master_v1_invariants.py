
from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", "storage", "secrets", "tests"}


def _iter_python_files(root: Path) -> List[Path]:
    paths: List[Path] = []
    if not root.exists():
        return paths
    for path in root.rglob("*.py"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        paths.append(path)
    return sorted(paths, key=lambda item: str(item))


def _read_imports(path: Path) -> List[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imports: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if not module:
                continue
            for alias in node.names:
                if alias.name == "*":
                    imports.append(module)
                else:
                    imports.append(f"{module}.{alias.name}")
    return imports


def _first_violation(
    files: Sequence[Path],
    *,
    forbidden_prefixes: Sequence[str],
    forbidden_modules: Sequence[str] = (),
    allow_prefixes: Sequence[str] = (),
) -> Optional[Tuple[Path, str]]:
    for path in files:
        for module in _read_imports(path):
            if any(module.startswith(prefix) for prefix in allow_prefixes):
                continue
            if module in forbidden_modules or any(module.startswith(prefix) for prefix in forbidden_prefixes):
                return path, module
    return None


def _format_violation(label: str, violation: Optional[Tuple[Path, str]]) -> str:
    if not violation:
        return f"{label} import violation"
    path, module = violation
    rel_path = path.relative_to(REPO_ROOT)
    return f"{label} import violation: {rel_path}: {module}"


def _iter_tool_files(repo_root: Path) -> Iterable[Path]:
    tool_roots = [repo_root / "core" / "tools", repo_root / "products"]
    for root in tool_roots:
        for path in _iter_python_files(root):
            if "tools" in path.parts:
                yield path


def _iter_agent_files(repo_root: Path) -> Iterable[Path]:
    agent_roots = [repo_root / "core" / "agents", repo_root / "products"]
    for root in agent_roots:
        for path in _iter_python_files(root):
            if "agents" in path.parts:
                yield path


def test_products_do_not_import_forbidden_core_modules() -> None:
    files = _iter_python_files(REPO_ROOT / "products")
    violation = _first_violation(
        files,
        forbidden_prefixes=(
            "core.models",
            "core.memory",
            "core.orchestrator",
            "core.agents.llm_reasoner",
        ),
    )
    assert not violation, _format_violation("Products", violation)


def test_tools_do_not_import_agents_or_models() -> None:
    files = list(_iter_tool_files(REPO_ROOT))
    violation = _first_violation(
        files,
        forbidden_prefixes=("core.agents", "core.models"),
    )
    assert not violation, _format_violation("Tools", violation)


def test_agents_do_not_import_memory_backends_or_tool_executor() -> None:
    files = list(_iter_agent_files(REPO_ROOT))
    violation = _first_violation(
        files,
        forbidden_prefixes=(
            "core.memory.in_memory",
            "core.memory.sqlite_backend",
            "core.tools.executor",
        ),
    )
    assert not violation, _format_violation("Agents", violation)


def test_ui_does_not_import_core_beyond_api_surface() -> None:
    files = _iter_python_files(REPO_ROOT / "gateway" / "ui")
    violation = _first_violation(
        files,
        forbidden_prefixes=("core.",),
        allow_prefixes=("core.config", "core.contracts"),
    )
    assert not violation, _format_violation("UI", violation)
