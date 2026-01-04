# ==============================
# Tool Registry
# ==============================
"""
Global tool registry.

    Design:
    - Registry stores name -> tool factory (no shared instances)
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
    """
    Global tool registry (class-level for simplicity).
    """

    _tools: Dict[str, ToolRegistration] = {}

    @classmethod
    def clear(cls) -> None:
        cls._tools.clear()

    @classmethod
    def register(
        cls,
        name: str,
        factory: ToolFactory | BaseTool,
        *,
        meta: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> None:
        norm = _norm(name)
        if not overwrite and norm in cls._tools:
            raise ValueError(f"Tool already registered: {name}")

        if isinstance(factory, BaseTool):
            raise ValueError("ToolRegistry.register requires a factory to avoid shared state across runs.")
        actual_factory = factory

        cls._tools[norm] = ToolRegistration(name=norm, factory=actual_factory, meta=meta or {})

    @classmethod
    def resolve(cls, name: str) -> BaseTool:
        norm = _norm(name)
        reg = cls._tools.get(norm)
        if reg is None:
            raise KeyError(f"Unknown tool: {name}")
        return reg.factory()

    @classmethod
    def has(cls, name: str) -> bool:
        return _norm(name) in cls._tools

    @classmethod
    def list(cls) -> Dict[str, Dict[str, Any]]:
        return {k: {"name": v.name, "meta": v.meta} for k, v in cls._tools.items()}


def _norm(name: str) -> str:
    return name.strip().lower().replace(" ", "_")
