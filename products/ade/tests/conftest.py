# ==============================
# ADE Product Test Configuration
# ==============================
"""
products/ade/tests/conftest.py

Shared fixtures for ADE product tests.
These fixtures provide consistent access to product paths
and test data across all ADE test modules.
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def ade_product_path() -> Path:
    """Return the path to the ADE product root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def ade_test_data_path() -> Path:
    """Return the path to ADE test data directory."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def ade_flows_path() -> Path:
    """Return the path to ADE flows directory."""
    return Path(__file__).parent.parent / "flows"


@pytest.fixture
def ade_staging_path(tmp_path: Path) -> Generator[Path, None, None]:
    """Create and return a temporary staging directory for test uploads."""
    staging = tmp_path / "staging" / "input"
    staging.mkdir(parents=True, exist_ok=True)
    yield staging


@pytest.fixture
def sample_csv_data() -> str:
    """Return sample CSV data for testing."""
    rows = [
        "Expense,H22024,H2025,H2026",
        "Marketing,100,120,140",
        "Engineering,200,220,180",
        "Sales,150,160,170",
    ]
    return "\n".join(rows)


@pytest.fixture
def sample_csv_file(ade_staging_path: Path, sample_csv_data: str) -> Path:
    """Create a sample CSV file in the staging directory."""
    csv_path = ade_staging_path / "sample.csv"
    csv_path.write_text(sample_csv_data, encoding="utf-8")
    return csv_path
