# ==============================
# Agent Registry
# ==============================
"""
Global agent registry.

Design:
- Registry stores name -> agent factory or instance
- Products can register their agents during boot (gateway startup, or product loader)
- Resolution is by string name used in StepDef.agent
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from core.agents.base import BaseAgent


AgentFactory = Callable[[], BaseAgent]


@dataclass(frozen=True)
class AgentRegistration:
    name: str
    factory: AgentFactory
    meta: Dict[str, Any]


class AgentRegistry:
    """
    Simple global registry used by orchestrator + products.

    The registry stores factories to ensure every resolution gets a fresh instance.
    Tests/products interact via classmethods to avoid passing registry handles around.
    """

    _agents: Dict[str, AgentRegistration] = {}

    @classmethod
    def clear(cls) -> None:
        cls._agents.clear()

    @classmethod
    def register(
        cls,
        name: str,
        factory: AgentFactory | BaseAgent,
        *,
        meta: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> None:
        norm = _norm(name)
        if not overwrite and norm in cls._agents:
            raise ValueError(f"Agent already registered: {name}")

        if isinstance(factory, BaseAgent):
            inst = factory

            def _factory(inst: BaseAgent = inst) -> BaseAgent:
                return inst

            actual_factory: AgentFactory = _factory
        else:
            actual_factory = factory

        cls._agents[norm] = AgentRegistration(name=norm, factory=actual_factory, meta=meta or {})

    @classmethod
    def resolve(cls, name: str) -> BaseAgent:
        norm = _norm(name)
        reg = cls._agents.get(norm)
        if reg is None:
            raise KeyError(f"Unknown agent: {name}")
        return reg.factory()

    @classmethod
    def has(cls, name: str) -> bool:
        return _norm(name) in cls._agents

    @classmethod
    def list(cls) -> Dict[str, Dict[str, Any]]:
        return {k: {"name": v.name, "meta": v.meta} for k, v in cls._agents.items()}


def _norm(name: str) -> str:
    return name.strip().lower().replace(" ", "_")
