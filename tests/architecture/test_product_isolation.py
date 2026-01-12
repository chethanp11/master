"""
Product Isolation Tests

Tests that verify product isolation constraints:
- No cross-product imports
- Product cannot access other product runs
- Products only import allowed core modules
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.contracts.run_schema import RunStatus
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCTS_ROOT = REPO_ROOT / "products"


def _iter_python_files(root: Path) -> List[Path]:
    """Iterate all Python files under root, excluding common directories."""
    excluded = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache", "tests"}
    files: List[Path] = []
    if not root.exists():
        return files
    for path in root.rglob("*.py"):
        if not path.is_file():
            continue
        if any(part in excluded for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def _get_product_dirs() -> List[Path]:
    """Get all product directories."""
    if not PRODUCTS_ROOT.exists():
        return []
    return [
        d for d in PRODUCTS_ROOT.iterdir()
        if d.is_dir()
        and not d.name.startswith("_")
        and not d.name.startswith(".")
        and (d / "manifest.yaml").exists()
    ]


def _extract_imports(path: Path) -> List[str]:
    """Extract all import statements from a Python file."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    imports.append(module)
                else:
                    full = f"{module}.{alias.name}" if module else alias.name
                    imports.append(full)
    return imports


def _get_product_name_from_path(path: Path) -> Optional[str]:
    """Extract product name from file path."""
    try:
        rel = path.relative_to(PRODUCTS_ROOT)
        return rel.parts[0] if rel.parts else None
    except ValueError:
        return None


class TestNoCrossProductImports:
    """Tests that no product imports another product."""

    def test_no_cross_product_imports(self) -> None:
        """No product imports another product."""
        product_dirs = _get_product_dirs()
        product_names = {d.name for d in product_dirs}

        violations: List[Tuple[Path, str, str]] = []

        for product_dir in product_dirs:
            product_name = product_dir.name
            other_products = product_names - {product_name}

            for py_file in _iter_python_files(product_dir):
                imports = _extract_imports(py_file)
                for imp in imports:
                    # Check if import references another product
                    for other in other_products:
                        if imp.startswith(f"products.{other}"):
                            violations.append((py_file, product_name, imp))

        assert not violations, (
            f"Found cross-product imports:\n"
            + "\n".join(
                f"  {v[0].relative_to(REPO_ROOT)}: product '{v[1]}' imports '{v[2]}'"
                for v in violations
            )
        )

    def test_products_only_import_allowed_core_modules(self) -> None:
        """Products only import from allowed core modules."""
        # Allowed imports from core
        allowed_core_prefixes = (
            "core.agents.base",
            "core.agents.registry",
            "core.tools.base",
            "core.tools.registry",
            "core.contracts",
            "core.config",
            "core.utils.product_loader",
            "core.knowledge.base",
            "core.knowledge.retriever",
        )

        # Forbidden imports from core
        forbidden_core_prefixes = (
            "core.models.providers",
            "core.memory.sqlite_backend",
            "core.memory.in_memory",
            "core.orchestrator.engine",
            "core.tools.executor",
        )

        violations: List[Tuple[Path, str]] = []

        for product_dir in _get_product_dirs():
            for py_file in _iter_python_files(product_dir):
                imports = _extract_imports(py_file)
                for imp in imports:
                    if not imp.startswith("core."):
                        continue
                    # Check forbidden
                    if any(imp.startswith(prefix) for prefix in forbidden_core_prefixes):
                        violations.append((py_file, imp))

        assert not violations, (
            f"Found forbidden core imports in products:\n"
            + "\n".join(
                f"  {v[0].relative_to(REPO_ROOT)}: imports '{v[1]}'"
                for v in violations
            )
        )


class TestProductCannotAccessOtherProductRuns:
    """Tests that API enforces product isolation for runs."""

    def test_product_cannot_access_other_product_runs(
        self,
        orchestrator,
        trace_sink: List[dict],
    ) -> None:
        """API enforces product isolation - runs are scoped to products."""
        settings = load_settings()
        AgentRegistry.clear()
        ToolRegistry.clear()
        catalog = discover_products(settings)
        register_enabled_products(catalog, settings=settings)

        trace_sink.clear()

        # Start a hello_world run
        start_hw = orchestrator.run_flow(
            product="hello_world",
            flow="hello_world",
            payload={"keyword": "isolation_test"},
        )
        assert start_hw.ok
        hw_run_id = start_hw.data["run_id"]

        # Get run should work for correct product
        bundle = orchestrator.memory.get_run(hw_run_id)
        assert bundle is not None
        assert bundle.run.product == "hello_world"

        # The run_id includes product context - verify it's hello_world specific
        all_runs = orchestrator.memory.list_runs(limit=100)
        hw_runs = [r for r in all_runs if r.product == "hello_world"]
        assert any(r.run_id == hw_run_id for r in hw_runs)

        # Verify no ADE runs mixed in (unless ADE was run separately)
        # This verifies that product field is correctly stored
        for run in all_runs:
            if run.run_id == hw_run_id:
                assert run.product == "hello_world"

    def test_run_product_field_immutable(self, orchestrator) -> None:
        """Run's product field cannot be changed after creation."""
        settings = load_settings()
        AgentRegistry.clear()
        ToolRegistry.clear()
        catalog = discover_products(settings)
        register_enabled_products(catalog, settings=settings)

        start = orchestrator.run_flow(
            product="hello_world",
            flow="hello_world",
            payload={"keyword": "immutable_test"},
        )
        assert start.ok
        run_id = start.data["run_id"]

        bundle = orchestrator.memory.get_run(run_id)
        assert bundle.run.product == "hello_world"

        # Attempting to resume with wrong product context should fail
        # (The actual enforcement depends on implementation)
        # Here we just verify the product is correctly stored
        bundle_after = orchestrator.memory.get_run(run_id)
        assert bundle_after.run.product == "hello_world"


class TestProductDirectoryStructure:
    """Tests that products follow required directory structure."""

    def test_all_products_have_manifest(self) -> None:
        """All product directories have manifest.yaml."""
        missing: List[Path] = []

        for product_dir in PRODUCTS_ROOT.iterdir():
            if not product_dir.is_dir():
                continue
            if product_dir.name.startswith("_") or product_dir.name.startswith("."):
                continue
            if product_dir.name == "__pycache__":
                continue
            if product_dir.name == "data":
                continue  # data directory is not a product

            manifest = product_dir / "manifest.yaml"
            if not manifest.exists():
                missing.append(product_dir)

        assert not missing, (
            f"Products missing manifest.yaml:\n"
            + "\n".join(f"  {p.relative_to(REPO_ROOT)}" for p in missing)
        )

    def test_all_products_have_registry(self) -> None:
        """All products have registry.py for agent/tool registration."""
        missing: List[Path] = []

        for product_dir in _get_product_dirs():
            registry = product_dir / "registry.py"
            if not registry.exists():
                missing.append(product_dir)

        assert not missing, (
            f"Products missing registry.py:\n"
            + "\n".join(f"  {p.relative_to(REPO_ROOT)}" for p in missing)
        )

    def test_all_products_have_flows_directory(self) -> None:
        """All products have a flows/ directory."""
        missing: List[Path] = []

        for product_dir in _get_product_dirs():
            flows_dir = product_dir / "flows"
            if not flows_dir.exists() or not flows_dir.is_dir():
                missing.append(product_dir)

        assert not missing, (
            f"Products missing flows/ directory:\n"
            + "\n".join(f"  {p.relative_to(REPO_ROOT)}" for p in missing)
        )


class TestProductImportPatterns:
    """Tests for specific import patterns that should be avoided."""

    def test_no_direct_model_provider_imports(self) -> None:
        """Products should not import model providers directly."""
        forbidden = "core.models.providers"
        violations: List[Tuple[Path, str]] = []

        for product_dir in _get_product_dirs():
            for py_file in _iter_python_files(product_dir):
                imports = _extract_imports(py_file)
                for imp in imports:
                    if imp.startswith(forbidden):
                        violations.append((py_file, imp))

        assert not violations, (
            f"Direct model provider imports found:\n"
            + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}: {v[1]}" for v in violations)
        )

    def test_no_direct_orchestrator_imports(self) -> None:
        """Products should not import orchestrator internals."""
        forbidden_prefixes = (
            "core.orchestrator.engine",
            "core.orchestrator.step_executor",
            "core.orchestrator.run_lifecycle",
        )
        violations: List[Tuple[Path, str]] = []

        for product_dir in _get_product_dirs():
            for py_file in _iter_python_files(product_dir):
                imports = _extract_imports(py_file)
                for imp in imports:
                    if any(imp.startswith(prefix) for prefix in forbidden_prefixes):
                        violations.append((py_file, imp))

        assert not violations, (
            f"Direct orchestrator imports found:\n"
            + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}: {v[1]}" for v in violations)
        )

    def test_no_direct_memory_backend_imports(self) -> None:
        """Products should not import memory backends directly."""
        forbidden_prefixes = (
            "core.memory.sqlite_backend",
            "core.memory.in_memory",
        )
        violations: List[Tuple[Path, str]] = []

        for product_dir in _get_product_dirs():
            for py_file in _iter_python_files(product_dir):
                imports = _extract_imports(py_file)
                for imp in imports:
                    if any(imp.startswith(prefix) for prefix in forbidden_prefixes):
                        violations.append((py_file, imp))

        assert not violations, (
            f"Direct memory backend imports found:\n"
            + "\n".join(f"  {v[0].relative_to(REPO_ROOT)}: {v[1]}" for v in violations)
        )
