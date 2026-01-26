# ==============================
# Agent Registry
# ==============================
"""
Global agent registry.

Design:
- Registry stores name -> agent factory (no shared instances)
- Products can register their agents during boot (gateway startup, or product loader)
- Resolution is by string name used in StepDef.agent
- Extends ComponentRegistry for unified registry pattern
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional

from pydantic import ValidationError

from core.agents.base import BaseAgent
from core.contracts.descriptors_schema import AgentDescriptor, CostHint
from core.utils.registry import ComponentRegistry


AgentFactory = Callable[[], BaseAgent]


# AGT-DISC-VAL-001: Descriptor validation error with field details
class DescriptorValidationError(Exception):
    """
    Raised when descriptor validation fails during registration.
    
    AGT-DISC-VAL-001: Validation errors must include descriptor name and field details.
    """

    def __init__(
        self,
        message: str,
        descriptor_name: str = "",
        field_errors: Optional[Dict[str, str]] = None,
    ) -> None:
        self.message = message
        self.descriptor_name = descriptor_name
        self.field_errors = field_errors or {}
        super().__init__(f"{message} (descriptor: {descriptor_name})")


@dataclass(frozen=True)
class AgentRegistration:
    """Registration record for an agent with descriptor."""
    
    name: str
    factory: AgentFactory
    meta: Dict[str, Any]
    descriptor: AgentDescriptor


class AgentRegistry(ComponentRegistry[BaseAgent]):
    """
    Global agent registry (class-level for simplicity).
    
    Extends ComponentRegistry with agent-specific descriptor support.
    The registry stores factories to ensure every resolution gets a fresh instance.
    Tests/products interact via classmethods to avoid passing registry handles around.
    """
    
    _component_type = "agent"
    _agents: Dict[str, AgentRegistration] = {}
    
    @classmethod
    def _get_components(cls) -> Dict[str, AgentRegistration]:
        return cls._agents
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered agents and reset core registration flag."""
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
        emit_event_fn: Optional[Callable[..., None]] = None,
    ) -> None:
        """
        Register an agent factory.
        
        AGT-DISC-VAL-001...006: Validates descriptor schema during registration.
        
        Args:
            name: The agent name (will be normalized)
            factory: A callable that returns a new agent instance
            meta: Optional metadata dict
            descriptor: Optional AgentDescriptor or dict to coerce
            overwrite: If True, allow overwriting existing registrations
            emit_event_fn: Optional function to emit trace events
            
        Raises:
            ValueError: If factory is an instance instead of callable
            ValueError: If name is already registered and overwrite=False
            DescriptorValidationError: If descriptor validation fails
        """
        norm = cls._normalize_name(name)
        if not overwrite and norm in cls._agents:
            raise ValueError(f"Agent already registered: {name}")
        
        if isinstance(factory, BaseAgent):
            raise ValueError(
                "AgentRegistry.register requires a factory to avoid shared state across runs."
            )
        actual_factory = factory
        
        # AGT-DISC-VAL-003...005: Validate descriptor during registration
        try:
            resolved_descriptor = cls._coerce_descriptor(
                norm, actual_factory, meta or {}, descriptor
            )
        except ValidationError as e:
            # Extract field errors from Pydantic validation error
            field_errors = {}
            for error in e.errors():
                loc = ".".join(str(x) for x in error.get("loc", []))
                field_errors[loc] = error.get("msg", "validation error")
            
            # AGT-DISC-VAL-006: Emit registration_failed trace event
            if emit_event_fn is not None:
                emit_event_fn(
                    kind="registration_failed",
                    payload={
                        "component_type": "agent",
                        "name": name,
                        "field_errors": field_errors,
                        "error_message": str(e),
                    },
                )
            
            raise DescriptorValidationError(
                "Agent descriptor validation failed",
                descriptor_name=name,
                field_errors=field_errors,
            ) from e
        
        cls._agents[norm] = AgentRegistration(
            name=norm,
            factory=actual_factory,
            meta=meta or {},
            descriptor=resolved_descriptor,
        )
    
    @classmethod
    def resolve(cls, name: str) -> BaseAgent:
        """Resolve an agent by name, returning a fresh instance."""
        _register_core_agents()
        norm = cls._normalize_name(name)
        reg = cls._agents.get(norm)
        if reg is None:
            raise KeyError(f"Unknown agent: {name}")
        return reg.factory()
    
    @classmethod
    def has(cls, name: str) -> bool:
        """Check if an agent is registered."""
        _register_core_agents()
        return cls._normalize_name(name) in cls._agents
    
    @classmethod
    def list(cls) -> Dict[str, Dict[str, Any]]:
        """Return a dict of registered agents with their metadata."""
        _register_core_agents()
        return {k: {"name": v.name, "meta": v.meta} for k, v in cls._agents.items()}
    
    @classmethod
    def list_registered(cls) -> list[str]:
        """Return a list of all registered agent names."""
        _register_core_agents()
        return list(cls._agents.keys())
    
    @classmethod
    def get_factory(cls, name: str) -> AgentFactory:
        """Get the factory function for an agent."""
        _register_core_agents()
        norm = cls._normalize_name(name)
        reg = cls._agents.get(norm)
        if reg is None:
            raise KeyError(f"Unknown agent: {name}")
        return reg.factory
    
    @classmethod
    def get_descriptor(cls, name: str) -> AgentDescriptor:
        """Get the descriptor for an agent."""
        _register_core_agents()
        norm = cls._normalize_name(name)
        reg = cls._agents.get(norm)
        if reg is None:
            raise KeyError(f"Unknown agent: {name}")
        return reg.descriptor
    
    @classmethod
    def list_descriptors(cls) -> Iterable[AgentDescriptor]:
        """Return all agent descriptors."""
        _register_core_agents()
        return [reg.descriptor for reg in cls._agents.values()]
    
    @classmethod
    def get_all_descriptors(cls) -> List[AgentDescriptor]:
        """
        INT-DISC-011: Return all agent descriptors as a list.
        
        Alias for list_descriptors() returning a concrete list.
        """
        _register_core_agents()
        return [reg.descriptor for reg in cls._agents.values()]
    
    @classmethod
    def filter_by_capability_tags(
        cls,
        tags: List[str],
        *,
        match_all: bool = False,
    ) -> List[str]:
        """
        INT-DISC-012: Filter agents by capability tags.
        
        Args:
            tags: List of capability tags to match
            match_all: If True, require all tags to match. If False, match any.
            
        Returns:
            List of agent names matching the filter
        """
        _register_core_agents()
        result: List[str] = []
        tags_lower = [t.lower() for t in tags]
        
        for name, reg in cls._agents.items():
            caps_lower = [c.lower() for c in reg.descriptor.capabilities]
            
            if match_all:
                if all(t in caps_lower for t in tags_lower):
                    result.append(name)
            else:
                if any(t in caps_lower for t in tags_lower):
                    result.append(name)
        
        return result
    
    @classmethod
    def _coerce_descriptor(
        cls,
        name: str,
        factory: AgentFactory,
        meta: Dict[str, Any],
        descriptor: Optional[AgentDescriptor | Dict[str, Any]],
    ) -> AgentDescriptor:
        """Coerce descriptor from various input types."""
        if isinstance(descriptor, AgentDescriptor):
            return descriptor
        if isinstance(descriptor, dict):
            return AgentDescriptor.model_validate(descriptor)
        
        description = ""
        try:
            agent = factory()
            description = getattr(agent, "description", "") or ""
        except Exception:
            pass
        
        purposes = list(meta.get("purposes") or [])
        purpose = meta.get("purpose") or (purposes[0] if purposes else "")
        tags = list(meta.get("tags") or [])
        capabilities = list(meta.get("capabilities") or tags)  # Fall back to tags
        allowed_step_types = list(meta.get("allowed_step_types") or ["agent", "plan_proposal"])
        cost_hint = meta.get("cost_hint") or CostHint.UNKNOWN
        
        return AgentDescriptor(
            name=name,
            purpose=purpose,
            purposes=purposes,
            capabilities=capabilities,
            tags=tags,
            input_schema_ref=meta.get("input_schema_ref"),
            output_schema_ref=meta.get("output_schema_ref"),
            cost_hint=CostHint(str(cost_hint)) if not isinstance(cost_hint, CostHint) else cost_hint,
            allowed_step_types=allowed_step_types,
        )


# Lazy imports to avoid circular dependencies
def _get_core_factories() -> dict:
    from core.agents.llm_reasoner import (
        build as build_llm_reasoner,
        build_explanation_reasoner,
        build_insight_reasoner,
        build_prioritization_reasoner,
    )
    from core.agents.advisory import (
        build_tool_selector,
        build_agent_selector,
        build_gap_finder,
        build_summarizer,
        build_risk_explainer,
    )
    
    advisory_meta = {
        "tags": ["advisory"],
        "purposes": ["advisory"],
        "allowed_step_types": ["agent", "plan_proposal"],
    }
    
    return {
        build_llm_reasoner: None,
        build_insight_reasoner: None,
        build_prioritization_reasoner: None,
        build_explanation_reasoner: None,
        build_tool_selector: advisory_meta,
        build_agent_selector: advisory_meta,
        build_gap_finder: advisory_meta,
        build_summarizer: advisory_meta,
        build_risk_explainer: advisory_meta,
    }


_CORE_REGISTERED = False


def _register_core_agents() -> None:
    """Register core agents lazily on first access."""
    global _CORE_REGISTERED
    if _CORE_REGISTERED:
        return
    
    factories = _get_core_factories()
    for factory, meta in factories.items():
        name = AgentRegistry._normalize_name(factory().name)
        if name not in AgentRegistry._agents:
            AgentRegistry.register(name, factory, meta=meta)
    
    _CORE_REGISTERED = True
