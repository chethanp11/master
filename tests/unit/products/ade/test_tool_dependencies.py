"""Tests for tool network dependency enforcement.

IMP-021: TS-TOOL-GEN-007 - No external network dependencies in tools.
"""

import ast
import os
from pathlib import Path
from typing import List, Set, Tuple

import pytest


# Network libraries that should not be imported in tool modules
FORBIDDEN_IMPORTS = {
    "requests",
    "urllib",
    "urllib.request",
    "urllib.urlopen",
    "urllib3",
    "httpx",
    "aiohttp",
    "http.client",
    "socket",
}

# Modules in tools directory that are allowed exceptions (e.g., base classes)
ALLOWED_EXCEPTIONS = {
    "__init__.py",
}


def _get_tool_files() -> List[Path]:
    """Get all Python files in the ADE tools directory."""
    tools_dir = Path(__file__).resolve().parents[4] / "products" / "ade" / "tools"
    if not tools_dir.exists():
        pytest.skip(f"Tools directory not found: {tools_dir}")
    return list(tools_dir.glob("*.py"))


def _extract_imports(file_path: Path) -> Set[str]:
    """Extract all import names from a Python file."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError:
        return set()

    imports: Set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])

    return imports


def _check_file_for_forbidden_imports(file_path: Path) -> List[Tuple[str, str]]:
    """Check a file for forbidden network imports.

    Returns:
        List of (filename, import_name) tuples for violations.
    """
    if file_path.name in ALLOWED_EXCEPTIONS:
        return []

    imports = _extract_imports(file_path)
    violations = []

    for imp in imports:
        if imp in FORBIDDEN_IMPORTS:
            violations.append((file_path.name, imp))

    return violations


class TestToolNetworkDependencies:
    """Tests for network dependency enforcement (TS-TOOL-GEN-007)."""

    def test_no_requests_import(self):
        """Test that tools don't import requests."""
        for file_path in _get_tool_files():
            imports = _extract_imports(file_path)
            assert "requests" not in imports, (
                f"Tool {file_path.name} imports 'requests' which is forbidden. "
                "Tools must not make external network calls."
            )

    def test_no_httpx_import(self):
        """Test that tools don't import httpx."""
        for file_path in _get_tool_files():
            imports = _extract_imports(file_path)
            assert "httpx" not in imports, (
                f"Tool {file_path.name} imports 'httpx' which is forbidden. "
                "Tools must not make external network calls."
            )

    def test_no_urllib_import(self):
        """Test that tools don't import urllib."""
        for file_path in _get_tool_files():
            imports = _extract_imports(file_path)
            assert "urllib" not in imports, (
                f"Tool {file_path.name} imports 'urllib' which is forbidden. "
                "Tools must not make external network calls."
            )

    def test_no_aiohttp_import(self):
        """Test that tools don't import aiohttp."""
        for file_path in _get_tool_files():
            imports = _extract_imports(file_path)
            assert "aiohttp" not in imports, (
                f"Tool {file_path.name} imports 'aiohttp' which is forbidden. "
                "Tools must not make external network calls."
            )

    def test_all_tools_clean(self):
        """Test that all tools pass network dependency check."""
        all_violations = []
        for file_path in _get_tool_files():
            violations = _check_file_for_forbidden_imports(file_path)
            all_violations.extend(violations)

        assert not all_violations, (
            f"Found forbidden network imports:\n"
            + "\n".join(f"  - {fname}: {imp}" for fname, imp in all_violations)
        )

    def test_tools_directory_exists(self):
        """Test that tools directory exists."""
        tools_dir = Path(__file__).resolve().parents[4] / "products" / "ade" / "tools"
        assert tools_dir.exists(), f"Tools directory not found: {tools_dir}"

    def test_has_tool_files(self):
        """Test that tool files exist."""
        files = _get_tool_files()
        assert len(files) > 0, "No tool files found"
