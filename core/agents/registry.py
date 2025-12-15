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
    def __init__(self) -> None:
        self._agents: Dict[str, AgentRegistration] = {}

    def register(
        self,
        *,
        name: str,
        factory: AgentFactory,
        meta: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> None:
        norm = _norm(name)
        if not overwrite and norm in self._agents:
            raise ValueError(f"Agent already registered: {name}")
        self._agents[norm] = AgentRegistration(name=norm, factory=factory, meta=meta or {})

    def resolve(self, name: str) -> BaseAgent:
        norm = _norm(name)
        reg = self._agents.get(norm)
        if reg is None:
            raise KeyError(f"Unknown agent: {name}")
        return reg.factory()

    def has(self, name: str) -> bool:
        return _norm(name) in self._agents

    def list(self) -> Dict[str, Dict[str, Any]]:
        return {k: {"name": v.name, "meta": v.meta} for k, v in self._agents.items()}


def _norm(name: str) -> str:
    return name.strip().lower().replace(" ", "_")