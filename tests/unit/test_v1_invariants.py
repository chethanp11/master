# ==============================
# Tests: V1 Invariants (Consolidated)
# ==============================
from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from tests.unit import test_agents_no_memory_backend_imports as agent_mem_guard
from tests.unit import test_architecture_guardrails as product_guard
from tests.unit import test_orchestrator_no_product_imports as orchestrator_guard
from tests.unit import test_tool_no_llm_imports as tool_llm_guard


_EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", "storage", "secrets", "tests"}


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if not path.is_file():
            continue
        if any(part in _EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def _format_report(sections: Dict[str, List[str]]) -> str:
    lines: List[str] = ["V1 invariant violations:"]
    for section, items in sections.items():
        if not items:
            continue
        lines.append(f"\n== {section} ==")
        lines.extend(f"- {item}" for item in sorted(items))
    return "\n".join(lines)


def _dedupe_sections(sections: Dict[str, List[str]]) -> Dict[str, List[str]]:
    seen = set()
    out: Dict[str, List[str]] = {}
    for section, items in sections.items():
        filtered: List[str] = []
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            filtered.append(item)
        out[section] = filtered
    return out


def _scan_openai_imports(repo_root: Path) -> List[str]:
    offenders: List[str] = []
    providers_root = repo_root / "core" / "models" / "providers"
    for path in _iter_python_files(repo_root):
        if providers_root in path.parents:
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("openai"):
                        offenders.append(f"{path}: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("openai"):
                    offenders.append(f"{path}: {module}")
    return offenders


def _scan_products_boundary(repo_root: Path) -> List[str]:
    offenders: List[str] = []
    products_root = repo_root / "products"
    for path in product_guard._iter_python_files(products_root):
        offenders.extend(f"{p}: {m}" for p, m in product_guard._check_file(path))
    return offenders


def _scan_tools_boundary(repo_root: Path) -> List[str]:
    offenders: List[str] = []
    tool_roots = [repo_root / "core" / "tools", repo_root / "products"]
    for root in tool_roots:
        if not root.exists():
            continue
        for path in tool_llm_guard._iter_python_files(root):
            if "tools" not in path.parts:
                continue
            offenders.extend(f"{p}: {m}" for p, m in tool_llm_guard._check_file(path))
    return offenders


def _scan_agents_boundary(repo_root: Path) -> List[str]:
    offenders: List[str] = []
    agent_roots = [repo_root / "core" / "agents", repo_root / "products"]
    for root in agent_roots:
        if not root.exists():
            continue
        for path in agent_mem_guard._iter_python_files(root):
            if "agents" not in path.parts:
                continue
            offenders.extend(f"{p}: {m}" for p, m in agent_mem_guard._check_file(path))
    return offenders


def _scan_orchestrator_boundary(repo_root: Path) -> List[str]:
    offenders: List[str] = []
    orchestrator_root = repo_root / "core" / "orchestrator"
    for path in orchestrator_guard._iter_python_files(orchestrator_root):
        offenders.extend(f"{p}: {m}" for p, m in orchestrator_guard._check_file(path))
    return offenders


def test_v1_invariants() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    sections = _dedupe_sections(
        {
        "Imports boundary checks (products)": _scan_products_boundary(repo_root),
        "Imports boundary checks (tools)": _scan_tools_boundary(repo_root),
        "Imports boundary checks (agents)": _scan_agents_boundary(repo_root),
        "Imports boundary checks (orchestrator)": _scan_orchestrator_boundary(repo_root),
        "Forbidden vendor SDK usage outside core/models/providers": _scan_openai_imports(repo_root),
        "Forbidden persistence outside core/memory (agents/products)": _scan_agents_boundary(repo_root),
        }
    )
    violations = [item for items in sections.values() for item in items]
    if violations:
        raise AssertionError(_format_report(sections))
