# ==============================
# Tool Registry
# ==============================
"""
Global tool registry.

Design:
- Registry stores name -> tool factory or instance
- Products can register their tools during boot (gateway startup, or product loader)
- Resolution is by string name used in StepDef.tool
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from core.tools.base import BaseTool


ToolFactory = Callable[[], BaseTool]


@dataclass(frozen=True)
class ToolRegistration:
    name: str
    factory: ToolFactory
    meta: Dict[str, Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolRegistration] = {}

    def register(
        self,
        *,
        name: str,
        factory: ToolFactory,
        meta: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> None:
        norm = _norm(name)
        if not overwrite and norm in self._tools:
            raise ValueError(f"Tool already registered: {name}")
        self._tools[norm] = ToolRegistration(name=norm, factory=factory, meta=meta or {})

    def resolve(self, name: str) -> BaseTool:
        norm = _norm(name)
        reg = self._tools.get(norm)
        if reg is None:
            raise KeyError(f"Unknown tool: {name}")
        return reg.factory()

    def has(self, name: str) -> bool:
        return _norm(name) in self._tools

    def list(self) -> Dict[str, Dict[str, Any]]:
        return {k: {"name": v.name, "meta": v.meta} for k, v in self._tools.items()}


def _norm(name: str) -> str:
    return name.strip().lower().replace(" ", "_")