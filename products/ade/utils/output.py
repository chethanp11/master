"""Output file utilities for ADE.

TS-IO-OUT-007: Ensure output directories exist before writes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def ensure_output_dir(output_path: str | Path, *, create_parents: bool = True) -> Path:
    """Ensure the output directory exists, creating it if necessary.

    TS-IO-OUT-007: Output directories are created automatically before writes.

    Args:
        output_path: Path to the output file or directory.
        create_parents: If True, create parent directories too.

    Returns:
        Path object for the output directory.

    Raises:
        OSError: If directory cannot be created.
    """
    path = Path(output_path)

    # If this looks like a file path (has extension), get parent directory
    if path.suffix:
        directory = path.parent
    else:
        directory = path

    directory.mkdir(parents=create_parents, exist_ok=True)
    return directory


def get_output_path(base_dir: str | Path, filename: str, *, ensure_exists: bool = True) -> Path:
    """Get a path in the output directory, optionally ensuring it exists.

    Args:
        base_dir: Base output directory.
        filename: Output filename.
        ensure_exists: If True, create the directory if it doesn't exist.

    Returns:
        Full path to the output file.
    """
    base = Path(base_dir)
    if ensure_exists:
        ensure_output_dir(base)
    return base / filename


def default_output_dir() -> Path:
    """Get the default output directory for ADE.

    Returns:
        Default output directory path (storage/output).
    """
    return Path("storage/output")
