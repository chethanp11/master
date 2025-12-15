# ==============================
# Agent Utilities (Pure Helpers)
# ==============================
"""
Common helpers for agents.

Rules:
- Pure utilities only. No vendor calls. No tool calls. No persistence.
- Safe parsing, coercion, prompt formatting helpers.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Union


def safe_json_loads(text: str, *, default: Optional[Any] = None) -> Any:
    """
    Best-effort JSON parse.
    Returns default on failure (default=None).
    """
    try:
        return json.loads(text)
    except Exception:
        return default


def coerce_str(x: Any, *, default: str = "") -> str:
    if x is None:
        return default
    try:
        return str(x)
    except Exception:
        return default


def coerce_int(x: Any, *, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def coerce_bool(x: Any, *, default: bool = False) -> bool:
    if isinstance(x, bool):
        return x
    if isinstance(x, str):
        v = x.strip().lower()
        if v in {"true", "1", "yes", "y"}:
            return True
        if v in {"false", "0", "no", "n"}:
            return False
    try:
        return bool(x)
    except Exception:
        return default


def format_prompt(template: str, variables: Dict[str, Any]) -> str:
    """
    Simple prompt formatter using {var} placeholders.
    Missing keys remain unchanged.
    """
    out = template
    for k, v in variables.items():
        out = out.replace("{" + k + "}", coerce_str(v))
    return out


def ensure_dict(x: Any) -> Dict[str, Any]:
    """
    Coerce input into a dict if possible; else return {}.
    """
    if isinstance(x, dict):
        return x
    return {}


def ensure_jsonable(x: Any) -> Union[Dict[str, Any], list, str, int, float, bool, None]:
    """
    Best-effort conversion into JSON-serializable structure.
    """
    try:
        json.dumps(x)
        return x  # type: ignore[return-value]
    except Exception:
        return coerce_str(x)