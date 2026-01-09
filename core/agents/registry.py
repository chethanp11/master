# ==============================
# Agent Registry
# ==============================
"""
Global agent registry.

    Design:
    - Registry stores name -> agent factory (no shared instances)
- Products can register their agents during boot (gateway startup, or product loader)
- Resolution is by string name used in StepDef.agent
"""

from __future__ import annotations



from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Iterable

from core.agents.base import BaseAgent
from core.contracts.descriptors_schema import AgentDescriptor, CostHint
from core.agents.llm_reasoner import (
    build as build_llm_reasoner,
    build_explanation_reasoner,
    build_insight_reasoner,
    build_prioritization_reasoner,
)


AgentFactory = Callable[[], BaseAgent]


@dataclass(frozen=True)
class AgentRegistration:
    name: str
    factory: AgentFactory
    meta: Dict[str, Any]
    descriptor: AgentDescriptor


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
        global _CORE_REGISTERED
        _CORE_REGISTERED = False

    @classmethod
    def register(
        cls,
        name: str,
        factory: AgentFactory | BaseAgent,
        *,
        meta: Optional[Dict[str, Any]] = None,
        descriptor: Optional[AgentDescriptor | Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> None:
        norm = _norm(name)
        if not overwrite and norm in cls._agents:
            raise ValueError(f"Agent already registered: {name}")

        if isinstance(factory, BaseAgent):
            raise ValueError("AgentRegistry.register requires a factory to avoid shared state across runs.")
        actual_factory = factory

        resolved_descriptor = cls._coerce_descriptor(norm, actual_factory, meta or {}, descriptor)
        cls._agents[norm] = AgentRegistration(
            name=norm,
            factory=actual_factory,
            meta=meta or {},
            descriptor=resolved_descriptor,
        )

    @classmethod
    def resolve(cls, name: str) -> BaseAgent:
        _register_core_agents()
        norm = _norm(name)
        reg = cls._agents.get(norm)
        if reg is None:
            raise KeyError(f"Unknown agent: {name}")
        return reg.factory()

    @classmethod
    def has(cls, name: str) -> bool:
        _register_core_agents()
        return _norm(name) in cls._agents

    @classmethod
    def list(cls) -> Dict[str, Dict[str, Any]]:
        _register_core_agents()
        return {k: {"name": v.name, "meta": v.meta} for k, v in cls._agents.items()}

    @classmethod
    def get_descriptor(cls, name: str) -> AgentDescriptor:
        _register_core_agents()
        norm = _norm(name)
        reg = cls._agents.get(norm)
        if reg is None:
            raise KeyError(f"Unknown agent: {name}")
        return reg.descriptor

    @classmethod
    def list_descriptors(cls) -> Iterable[AgentDescriptor]:
        _register_core_agents()
        return [reg.descriptor for reg in cls._agents.values()]

    @classmethod
    def _coerce_descriptor(
        cls,
        name: str,
        factory: AgentFactory,
        meta: Dict[str, Any],
        descriptor: Optional[AgentDescriptor | Dict[str, Any]],
    ) -> AgentDescriptor:
        if isinstance(descriptor, AgentDescriptor):
            return descriptor
        if isinstance(descriptor, dict):
            return AgentDescriptor.model_validate(descriptor)

        description = ""
        try:
            agent = factory()
            description = getattr(agent, "description", "") or ""
        except Exception:
            agent = None  # type: ignore[assignment]

        purposes = list(meta.get("purposes") or [])
        tags = list(meta.get("tags") or [])
        allowed_step_types = list(meta.get("allowed_step_types") or ["agent", "plan_proposal"])
        cost_hint = meta.get("cost_hint") or CostHint.UNKNOWN

        return AgentDescriptor(
            name=name,
            purposes=purposes,
            tags=tags,
            input_schema_ref=meta.get("input_schema_ref"),
            output_schema_ref=meta.get("output_schema_ref"),
            cost_hint=CostHint(str(cost_hint)) if not isinstance(cost_hint, CostHint) else cost_hint,
            allowed_step_types=allowed_step_types,
        )


def _norm(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


_CORE_REGISTERED = False


def _register_core_agents() -> None:
    global _CORE_REGISTERED
    if _CORE_REGISTERED:
        return
    for factory in (
        build_llm_reasoner,
        build_insight_reasoner,
        build_prioritization_reasoner,
        build_explanation_reasoner,
    ):
        name = _norm(factory().name)
        if name not in AgentRegistry._agents:
            AgentRegistry.register(name, factory)
    _CORE_REGISTERED = True
