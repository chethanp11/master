"""Tests for output utilities.

IMP-023: TS-IO-OUT-007 output directory creation tests.
"""

import tempfile
from pathlib import Path

import pytest

from products.ade.utils.output import (
    ensure_output_dir,
    get_output_path,
    default_output_dir,
)


class TestEnsureOutputDir:
    """Tests for ensure_output_dir function."""

    def test_creates_directory(self):
        """Test that directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "staging" / "output"
            assert not new_dir.exists()

            result = ensure_output_dir(new_dir)

            assert result.exists()
            assert result.is_dir()
            assert result == new_dir

    def test_creates_parent_directories(self):
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = Path(tmpdir) / "a" / "b" / "c" / "d"
            assert not nested.exists()

            result = ensure_output_dir(nested)

            assert result.exists()

    def test_file_path_creates_parent(self):
        """Test that file path creates parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "output" / "report.html"
            parent = file_path.parent

            result = ensure_output_dir(file_path)

            assert result == parent
            assert parent.exists()
            assert parent.is_dir()

    def test_existing_directory_no_error(self):
        """Test that existing directory causes no error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            existing = Path(tmpdir)
            assert existing.exists()

            result = ensure_output_dir(existing)

            assert result.exists()


class TestGetOutputPath:
    """Tests for get_output_path function."""

    def test_returns_full_path(self):
        """Test that full path is returned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "output"
            result = get_output_path(base, "report.html")

            assert result == base / "report.html"
            assert result.parent.exists()

    def test_creates_directory_when_ensure_exists(self):
        """Test directory creation with ensure_exists=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "new_output"
            assert not base.exists()

            result = get_output_path(base, "file.txt", ensure_exists=True)

            assert base.exists()
            assert result == base / "file.txt"

    def test_no_creation_when_ensure_exists_false(self):
        """Test no directory creation with ensure_exists=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "nonexistent"
            result = get_output_path(base, "file.txt", ensure_exists=False)

            assert not base.exists()
            assert result == base / "file.txt"


class TestDefaultOutputDir:
    """Tests for default_output_dir function."""

    def test_returns_path(self):
        """Test that Path is returned."""
        result = default_output_dir()
        assert isinstance(result, Path)

    def test_default_path(self):
        """Test default path value."""
        result = default_output_dir()
        assert str(result) == "storage/output"
