# ==============================
# Formatters
# ==============================
"""
Small human-friendly formatters for UI/CLI.

No I/O. No persistence.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def compact_kv(d: Dict[str, Any], *, keys: Optional[List[str]] = None, max_len: int = 300) -> str:
    use = d if keys is None else {k: d.get(k) for k in keys}
    parts = []
    for k, v in use.items():
        s = f"{k}={_short(v, max_len=max_len)}"
        parts.append(s)
    return " ".join(parts)


def _short(x: Any, *, max_len: int) -> str:
    s = str(x)
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."