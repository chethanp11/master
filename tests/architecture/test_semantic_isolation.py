from __future__ import annotations

import ast
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Iterable, List, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_ast(path: Path) -> ast.Module:
    source = path.read_text(encoding="utf-8")
    return ast.parse(source, filename=str(path))


def _iter_import_roots(tree: ast.AST) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                yield node.module.split(".")[0]


def _get_function_def(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == name:
                    return child
    raise AssertionError(f"Expected to find function {name}.")


def _find_semantic_adapter_modules(products_root: Path) -> List[Path]:
    candidates: List[Path] = []
    for path in products_root.rglob("semantic.py"):
        candidates.append(path)
    for path in products_root.rglob("semantic_adapter.py"):
        candidates.append(path)
    return sorted(set(candidates))


def _load_module_from_path(path: Path) -> object:
    module_name = f"semantic_adapter_{path.as_posix().replace('/', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load module from {path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _get_call_lines(func_def: ast.FunctionDef, attr_name: str) -> List[int]:
    lines: List[int] = []
    for node in ast.walk(func_def):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == attr_name:
                if hasattr(node, "lineno"):
                    lines.append(node.lineno)
    return sorted(lines)


def _get_emit_event_kinds(func_def: ast.FunctionDef) -> Set[str]:
    kinds: Set[str] = set()
    for node in ast.walk(func_def):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "_emit_event":
            continue
        for keyword in node.keywords:
            if keyword.arg == "kind" and isinstance(keyword.value, ast.Constant):
                if isinstance(keyword.value.value, str):
                    kinds.add(keyword.value.value)
    return kinds


def test_semantic_schema_no_external_deps() -> None:
    path = REPO_ROOT / "core" / "contracts" / "semantic_schema.py"
    tree = _load_ast(path)
    if hasattr(sys, "stdlib_module_names"):
        stdlib = set(sys.stdlib_module_names)
    else:
        stdlib = set(sys.builtin_module_names) | {"enum", "typing", "dataclasses"}
    allowed_external = {"pydantic", "core"}
    offenders: List[str] = []
    for root in _iter_import_roots(tree):
        if root in {"__future__"}:
            continue
        if root in stdlib or root in allowed_external:
            continue
        offenders.append(root)
    assert not offenders, f"semantic_schema.py has external deps: {sorted(set(offenders))}"


def test_normalization_no_io_operations() -> None:
    path = REPO_ROOT / "core" / "orchestrator" / "normalization.py"
    tree = _load_ast(path)
    forbidden_modules = {
        "aiohttp",
        "http",
        "io",
        "os",
        "pathlib",
        "requests",
        "shutil",
        "socket",
        "subprocess",
        "tempfile",
        "urllib",
    }
    import_offenses = [root for root in _iter_import_roots(tree) if root in forbidden_modules]
    banned_attrs = {
        "open",
        "read_text",
        "write_text",
        "read_bytes",
        "write_bytes",
        "mkdir",
        "rmdir",
        "unlink",
        "rglob",
        "glob",
    }
    call_offenses: List[Tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                call_offenses.append((node.lineno, "open"))
            elif isinstance(node.func, ast.Attribute) and node.func.attr in banned_attrs:
                call_offenses.append((node.lineno, node.func.attr))
    assert not import_offenses, f"Normalization imports IO modules: {import_offenses}"
    assert not call_offenses, f"Normalization performs IO calls: {call_offenses}"


def test_semantic_phase_before_step_execution() -> None:
    path = REPO_ROOT / "core" / "orchestrator" / "engine.py"
    tree = _load_ast(path)
    run_flow = _get_function_def(tree, "run_flow")
    semantic_lines = _get_call_lines(run_flow, "_run_semantic_interpretation")
    execute_lines = _get_call_lines(run_flow, "_execute_from_index")
    assert semantic_lines, "run_flow must call _run_semantic_interpretation."
    assert execute_lines, "run_flow must call _execute_from_index."
    assert semantic_lines[0] < execute_lines[0], (
        "_run_semantic_interpretation must occur before _execute_from_index."
    )


def test_adapters_implement_required_interface() -> None:
    products_root = REPO_ROOT / "products"
    adapter_paths = _find_semantic_adapter_modules(products_root)
    assert adapter_paths, "No semantic adapter modules found under products/."

    for path in adapter_paths:
        module = _load_module_from_path(path)
        factory = getattr(module, "create_semantic_adapter", None)
        assert callable(factory), f"{path} must export create_semantic_adapter."

        adapter = factory()
        assert hasattr(adapter, "interpret") and callable(adapter.interpret), (
            f"{path} adapter must implement interpret."
        )
        assert hasattr(adapter, "validate") and callable(adapter.validate), (
            f"{path} adapter must implement validate."
        )

        interpret_sig = inspect.signature(adapter.interpret)
        interpret_params = [
            p for p in interpret_sig.parameters.values() if p.name != "self"
        ]
        assert len(interpret_params) >= 2, (
            f"{path} interpret must accept (user_input, context)."
        )

        validate_sig = inspect.signature(adapter.validate)
        validate_params = [
            p for p in validate_sig.parameters.values() if p.name != "self"
        ]
        assert len(validate_params) >= 1, f"{path} validate must accept envelope."


def test_trace_events_emitted_for_semantic_operations() -> None:
    path = REPO_ROOT / "core" / "orchestrator" / "engine.py"
    tree = _load_ast(path)
    func_def = _get_function_def(tree, "_run_semantic_interpretation")
    kinds = _get_emit_event_kinds(func_def)
    required = {
        "semantic_interpretation_skipped",
        "semantic_interpretation_started",
        "semantic_interpretation_completed",
        "semantic_stop_issued",
        "semantic_interpretation_failed",
    }
    missing = required - kinds
    assert not missing, f"Missing semantic trace events: {sorted(missing)}"
