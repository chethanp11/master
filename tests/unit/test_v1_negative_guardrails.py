from __future__ import annotations

# ==============================
# Tests: V1 Negative Guardrails
# ==============================

import ast
from pathlib import Path
from typing import Iterable, List, Tuple


_EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", "storage", "secrets", "tests"}


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if not path.is_file():
            continue
        if any(part in _EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def _scan_agent_to_agent_calls(root: Path) -> List[str]:
    offenders: List[str] = []
    for path in _iter_python_files(root):
        if "agents" not in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "core.agents.registry":
                offenders.append(f"{path}: imports AgentRegistry")
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "resolve":
                    if isinstance(func.value, ast.Name) and func.value.id == "AgentRegistry":
                        offenders.append(f"{path}: AgentRegistry.resolve()")
    return offenders


def _scan_dynamic_flow_mutation(root: Path) -> List[str]:
    offenders: List[str] = []
    for path in _iter_python_files(root):
        if "orchestrator" not in path.parts and "products" not in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AugAssign)) and isinstance(node.target if isinstance(node, ast.AugAssign) else node.targets[0], ast.Attribute):
                target = node.target if isinstance(node, ast.AugAssign) else node.targets[0]
                if isinstance(target, ast.Attribute) and target.attr == "steps":
                    offenders.append(f"{path}: assigns to steps")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "steps":
                    if node.func.attr in {"append", "extend", "insert", "pop", "remove", "clear"}:
                        offenders.append(f"{path}: mutates steps via {node.func.attr}")
    return offenders


def _scan_autonomous_retries(root: Path) -> List[str]:
    offenders: List[str] = []
    for path in _iter_python_files(root):
        if not any(part in path.parts for part in ("agents", "tools", "products")):
            continue
        if path.name in {"step_executor.py", "error_policy.py"}:
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("tenacity"):
                        offenders.append(f"{path}: imports tenacity")
            if isinstance(node, ast.ImportFrom):
                if (node.module or "").startswith("tenacity"):
                    offenders.append(f"{path}: imports tenacity")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id in {"time", "asyncio"}:
                    if node.func.attr == "sleep":
                        offenders.append(f"{path}: sleep() usage")
    return offenders


def _scan_hidden_product_state(root: Path) -> List[str]:
    offenders: List[str] = []
    for path in _iter_python_files(root):
        if "products" not in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if not isinstance(target, ast.Name):
                        continue
                    name = target.id
                    if name.isupper():
                        continue
                    if isinstance(node.value, (ast.Dict, ast.List, ast.Set)):
                        offenders.append(f"{path}: mutable module state '{name}'")
                    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                        if node.value.func.id in {"dict", "list", "set"}:
                            offenders.append(f"{path}: mutable module state '{name}'")
    return offenders


def _scan_self_modifying_flows(root: Path) -> List[str]:
    offenders: List[str] = []
    for path in _iter_python_files(root):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {"write_text", "write_bytes"} and node.args:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "/flows/" in arg.value and arg.value.endswith((".yaml", ".yml")):
                            offenders.append(f"{path}: writes flow file {arg.value}")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
                if node.args:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "/flows/" in arg.value and arg.value.endswith((".yaml", ".yml")):
                            offenders.append(f"{path}: opens flow file {arg.value}")
    return offenders


def _fail_if(offenders: List[str], *, title: str) -> None:
    if offenders:
        details = "\n".join(sorted(offenders))
        raise AssertionError(f"{title}:\n{details}")


def test_no_agent_to_agent_calls() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    offenders = _scan_agent_to_agent_calls(repo_root)
    _fail_if(offenders, title="Agent-to-agent calls are forbidden")


def test_no_dynamic_flow_mutation() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    offenders = _scan_dynamic_flow_mutation(repo_root)
    _fail_if(offenders, title="Dynamic flow mutation is forbidden")


def test_no_autonomous_retries_without_policy() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    offenders = _scan_autonomous_retries(repo_root)
    _fail_if(offenders, title="Autonomous retries without policy are forbidden")


def test_no_hidden_state_inside_products() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    offenders = _scan_hidden_product_state(repo_root)
    _fail_if(offenders, title="Hidden mutable state inside products is forbidden")


def test_no_self_modifying_flows() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    offenders = _scan_self_modifying_flows(repo_root)
    _fail_if(offenders, title="Self-modifying flow files are forbidden")
