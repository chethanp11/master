
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


# ==============================
# Extended Architectural Invariants (Phase 16-17)
# ==============================


def _find_function_calls(path: Path, function_names: Sequence[str]) -> List[Tuple[str, int]]:
    """Find calls to specific functions in a file.

    Returns list of (function_name, line_number) tuples.
    """
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    calls: List[Tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Direct function call: func()
            if isinstance(node.func, ast.Name) and node.func.id in function_names:
                calls.append((node.func.id, node.lineno))
            # Attribute call: obj.func()
            elif isinstance(node.func, ast.Attribute) and node.func.attr in function_names:
                calls.append((node.func.attr, node.lineno))

    return calls


def _find_attribute_access(path: Path, attr_names: Sequence[str]) -> List[Tuple[str, int]]:
    """Find attribute accesses in a file.

    Returns list of (attr_name, line_number) tuples.
    """
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    accesses: List[Tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in attr_names:
            accesses.append((node.attr, node.lineno))

    return accesses


def _check_for_direct_tool_calls(files: Sequence[Path]) -> List[Tuple[Path, str, int]]:
    """Check if files make direct tool execution calls (bypassing executor).

    Returns list of (file, function_name, line) tuples.
    """
    # Tool execution should only go through ToolExecutor.execute()
    # Direct calls to tool.run() or tool.execute() are violations
    violations: List[Tuple[Path, str, int]] = []

    for path in files:
        # Skip executor itself
        if "executor" in path.name or "step_executor" in path.name:
            continue

        calls = _find_function_calls(path, ("run",))
        # Check if it's a tool.run() call by looking at context
        # This is a heuristic - we check if "tool" appears nearby
        try:
            source = path.read_text(encoding="utf-8")
            lines = source.split("\n")
            for func_name, line_no in calls:
                if line_no <= len(lines):
                    line = lines[line_no - 1]
                    # Check if this looks like a tool.run() call
                    if ".run(" in line and ("tool" in line.lower() or "Tool" in line):
                        # Further check: is this inside an executor?
                        if "executor" not in path.stem.lower():
                            # Check if this is a test file (allowed)
                            if "test" not in str(path):
                                violations.append((path, func_name, line_no))
        except (IOError, UnicodeDecodeError):
            continue

    return violations


def test_agents_never_call_tools_directly() -> None:
    """Agents must not call tools directly; they must request via step output."""
    agent_files = list(_iter_agent_files(REPO_ROOT))

    # Check for imports of tool executor
    for path in agent_files:
        imports = _read_imports(path)
        for imp in imports:
            if "tools.executor" in imp or "ToolExecutor" in imp:
                assert False, f"Agent {path.relative_to(REPO_ROOT)} imports ToolExecutor"

    # Check for direct tool.run() calls
    violations = _check_for_direct_tool_calls(agent_files)
    assert not violations, (
        "Agents calling tools directly:\n"
        + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}:{v[2]} - {v[1]}" for v in violations)
    )


def test_tools_never_call_llm_directly() -> None:
    """Tools must not call LLM providers directly; use llm_reasoner pattern."""
    tool_files = list(_iter_tool_files(REPO_ROOT))

    forbidden_imports = (
        "core.models.providers",
        "openai",
        "anthropic",
        "litellm",
    )

    violations: List[Tuple[Path, str]] = []

    for path in tool_files:
        # Skip provider files themselves
        if "providers" in path.parts:
            continue

        imports = _read_imports(path)
        for imp in imports:
            if any(imp.startswith(forbidden) for forbidden in forbidden_imports):
                violations.append((path, imp))

    assert not violations, (
        "Tools importing LLM providers directly:\n"
        + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}: {v[1]}" for v in violations)
    )


def test_no_env_reads_outside_config_loader() -> None:
    """Environment variables should only be read in config/loader.py."""
    allowed_files = {
        "loader.py",  # config loader
        "conftest.py",  # test fixtures
        "dotenv_loading.py",  # dotenv integration
    }

    env_access_patterns = ("environ", "getenv", "os.environ")

    violations: List[Tuple[Path, str, int]] = []

    # Check core and products (not tests)
    for root in [REPO_ROOT / "core", REPO_ROOT / "products", REPO_ROOT / "gateway"]:
        for path in _iter_python_files(root):
            if path.name in allowed_files:
                continue
            if "test" in path.name.lower():
                continue

            # Check for os.environ or os.getenv
            imports = _read_imports(path)
            has_os = any("os" in imp for imp in imports)
            if not has_os:
                continue

            accesses = _find_attribute_access(path, ("environ", "getenv"))
            for attr, line_no in accesses:
                violations.append((path, attr, line_no))

    assert not violations, (
        "Environment reads outside config loader:\n"
        + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}:{v[2]} - os.{v[1]}" for v in violations)
    )


def test_no_persistence_outside_memory() -> None:
    """Direct file/database writes should only happen in memory layer."""
    allowed_paths = {
        "memory",  # memory layer
        "observability_store",  # observability
        "tracing",  # tracing
    }

    # Patterns that indicate persistence operations
    persistence_patterns = ("sqlite3", "open(", ".write(", ".write_text(", "Path.write")

    violations: List[Tuple[Path, str, int]] = []

    # Check orchestrator and agents (they shouldn't persist directly)
    for root in [REPO_ROOT / "core" / "orchestrator", REPO_ROOT / "core" / "agents"]:
        for path in _iter_python_files(root):
            # Skip if in allowed paths
            if any(allowed in str(path) for allowed in allowed_paths):
                continue

            try:
                source = path.read_text(encoding="utf-8")
                lines = source.split("\n")

                for line_no, line in enumerate(lines, 1):
                    # Check for file writes
                    if ".write(" in line or ".write_text(" in line:
                        # Ignore string methods
                        if "StringIO" not in source[:source.find(line)] and "io.StringIO" not in source:
                            violations.append((path, "file write", line_no))

                    # Check for sqlite direct access
                    if "sqlite3" in line and "import" not in line:
                        violations.append((path, "sqlite3", line_no))

            except (IOError, UnicodeDecodeError):
                continue

    assert not violations, (
        "Persistence operations outside memory layer:\n"
        + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}:{v[2]} - {v[1]}" for v in violations)
    )


def test_no_direct_model_calls_outside_reasoner() -> None:
    """LLM calls should only go through llm_reasoner or model router."""
    allowed_files = {
        "llm_reasoner.py",
        "router.py",  # model router
    }
    allowed_dirs = {"providers", "models"}

    # LLM-related imports that indicate direct calls
    llm_imports = (
        "openai",
        "anthropic",
        "litellm",
    )

    violations: List[Tuple[Path, str]] = []

    for path in _iter_python_files(REPO_ROOT / "core"):
        # Skip allowed files and directories
        if path.name in allowed_files:
            continue
        if any(d in path.parts for d in allowed_dirs):
            continue

        imports = _read_imports(path)
        for imp in imports:
            if any(imp.startswith(llm) or imp == llm for llm in llm_imports):
                violations.append((path, imp))

    assert not violations, (
        "Direct LLM imports outside reasoner/router:\n"
        + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}: {v[1]}" for v in violations)
    )


def test_orchestrator_is_only_control_plane() -> None:
    """Orchestrator should not contain business logic - only control flow."""
    orchestrator_root = REPO_ROOT / "core" / "orchestrator"

    # Business logic imports that shouldn't be in orchestrator
    forbidden_imports = (
        "pandas",
        "numpy",
        "sklearn",
        "matplotlib",
    )

    violations: List[Tuple[Path, str]] = []

    for path in _iter_python_files(orchestrator_root):
        imports = _read_imports(path)
        for imp in imports:
            if any(imp.startswith(forbidden) for forbidden in forbidden_imports):
                violations.append((path, imp))

    assert not violations, (
        "Business logic imports in orchestrator:\n"
        + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}: {v[1]}" for v in violations)
    )


def test_gateway_does_not_bypass_orchestrator() -> None:
    """Gateway layer must use orchestrator for all run operations."""
    gateway_root = REPO_ROOT / "gateway"

    # Gateway should not import memory backends directly
    forbidden_imports = (
        "core.memory.in_memory",
        "core.memory.sqlite_backend",
        "core.tools.executor",
        "core.agents.llm_reasoner",
    )

    violations: List[Tuple[Path, str]] = []

    for path in _iter_python_files(gateway_root):
        # deps.py can import memory for initialization
        if path.name == "deps.py":
            continue

        imports = _read_imports(path)
        for imp in imports:
            if any(imp.startswith(forbidden) for forbidden in forbidden_imports):
                violations.append((path, imp))

    assert not violations, (
        "Gateway bypassing orchestrator:\n"
        + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}: {v[1]}" for v in violations)
    )
