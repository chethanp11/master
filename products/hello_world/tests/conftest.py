# ==============================
# Hello World Product Test Configuration
# ==============================
"""
products/hello_world/tests/conftest.py

Shared fixtures for hello_world product tests.
These fixtures provide consistent access to product paths
and test data across all hello_world test modules.
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def hello_world_product_path() -> Path:
    """Return the path to the hello_world product root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def hello_world_flows_path() -> Path:
    """Return the path to hello_world flows directory."""
    return Path(__file__).parent.parent / "flows"


@pytest.fixture
def hello_world_staging_path(tmp_path: Path) -> Generator[Path, None, None]:
    """Create and return a temporary staging directory for test inputs."""
    staging = tmp_path / "staging" / "input"
    staging.mkdir(parents=True, exist_ok=True)
    yield staging
