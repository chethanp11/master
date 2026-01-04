
# ==============================
# Template Rendering
# ==============================
"""
Shared template rendering helpers for orchestrator/agents.

Supports strict rendering for message templates and lenient rendering for tool params.
"""

from __future__ import annotations


# Public surface; keep deterministic and minimal.
__all__ = ["render_template", "render_messages", "render_params"]

import json
import re
from typing import Any, Dict, Iterable, List


_TOKEN_RE = re.compile(r"\{\{\s*([a-zA-Z_][\w\.]*)\s*\}\}")


def render_template(template: str, context: Dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        path = match.group(1)
        value = _resolve_path(context, path)
        return _stringify(value)

    missing = _missing_keys(template, context)
    if missing:
        raise KeyError(f"Missing placeholders: {', '.join(sorted(missing))}")
    return _TOKEN_RE.sub(replace, template)


def render_messages(messages: Iterable[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    rendered: List[Dict[str, Any]] = []
    for msg in messages:
        item = dict(msg)
        content = item.get("content")
        if isinstance(content, str):
            item["content"] = render_template(content, context)
        rendered.append(item)
    return rendered


def render_params(params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    def render(value: Any) -> Any:
        if isinstance(value, str):
            full_match = _TOKEN_RE.fullmatch(value)
            if full_match:
                try:
                    return _resolve_path(context, full_match.group(1))
                except KeyError:
                    return None

            def replace(match: re.Match[str]) -> str:
                try:
                    resolved = _resolve_path(context, match.group(1))
                except KeyError:
                    return ""
                return str(resolved) if resolved is not None else ""

            return _TOKEN_RE.sub(replace, value)
        if isinstance(value, dict):
            return {k: render(v) for k, v in value.items()}
        if isinstance(value, list):
            return [render(item) for item in value]
        return value

    return {k: render(v) for k, v in params.items()}


def _missing_keys(template: str, context: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    for match in _TOKEN_RE.finditer(template):
        path = match.group(1)
        try:
            _resolve_path(context, path)
        except KeyError:
            missing.append(path)
    return missing


def _resolve_path(context: Dict[str, Any], path: str) -> Any:
    parts = path.split(".")
    if not parts:
        raise KeyError(path)
    root = parts[0]
    if root not in context:
        raise KeyError(path)
    current: Any = context[root]
    remainder = parts[1:]
    if root == "artifacts":
        current, remainder = _resolve_dotted_key(current, remainder, path)
    for part in remainder:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
            except ValueError as exc:
                raise KeyError(path) from exc
            if idx < 0 or idx >= len(current):
                raise KeyError(path)
            current = current[idx]
        else:
            raise KeyError(path)
    return current


def _resolve_dotted_key(current: Any, remainder: List[str], path: str) -> tuple[Any, List[str]]:
    if not isinstance(current, dict) or not remainder:
        return current, remainder
    for split in range(len(remainder), 0, -1):
        key = ".".join(remainder[:split])
        if key in current:
            return current[key], remainder[split:]
    raise KeyError(path)


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=True, default=str)
    return str(value)
