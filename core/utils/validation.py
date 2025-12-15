# ==============================
# Validation Helpers
# ==============================
"""
Reusable validators used across core (non-domain).

No side effects.
"""

from __future__ import annotations

import re
from typing import Optional


_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


def validate_slug(name: str, *, what: str = "name") -> None:
    """
    Enforce a safe slug: lowercase letters/numbers/_ and starts with a letter.
    """
    if not _NAME_RE.match(name):
        raise ValueError(f"Invalid {what}: '{name}'. Use lowercase letters/numbers/_; start with a letter; 2-64 chars.")


def require_non_empty(value: Optional[str], *, what: str) -> str:
    if value is None or not value.strip():
        raise ValueError(f"{what} must be provided.")
    return value.strip()