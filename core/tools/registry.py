# ==============================
# Tool Registry
# ==============================
"""
Global tool registry.

Design:
- Registry stores name -> tool factory (no shared instances)
- Products can register their tools during boot (gateway startup, or product loader)
- Resolution is by string name used in StepDef.tool
- Extends ComponentRegistry for unified registry pattern
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional

from pydantic import ValidationError

from core.tools.base import BaseTool
from core.contracts.descriptors_schema import ToolDescriptor, SensitivityClass, CostHint
from core.utils.registry import ComponentRegistry
from core.agents.registry import DescriptorValidationError


ToolFactory = Callable[[], BaseTool]


@dataclass(frozen=True)
class ToolRegistration:
    """Registration record for a tool with descriptor."""
    
    name: str
    factory: ToolFactory
    meta: Dict[str, Any]
    descriptor: ToolDescriptor
    descriptor_auto: bool


class ToolRegistry(ComponentRegistry[BaseTool]):
    """
    Global tool registry (class-level for simplicity).
    
    Extends ComponentRegistry with tool-specific descriptor support including
    lazy hydration of descriptors from tool instances.
    """
    
    _component_type = "tool"
    _tools: Dict[str, ToolRegistration] = {}
    
    @classmethod
    def _get_components(cls) -> Dict[str, ToolRegistration]:
        return cls._tools
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools."""
        cls._tools.clear()
    
    @classmethod
    def register(
        cls,
        name: str,
        factory: ToolFactory | BaseTool,
        *,
        meta: Optional[Dict[str, Any]] = None,
        descriptor: Optional[ToolDescriptor | Dict[str, Any]] = None,
        overwrite: bool = False,
        emit_event_fn: Optional[Callable[..., None]] = None,
    ) -> None:
        """
        Register a tool factory.
        
        AGT-DISC-VAL-001...006: Validates descriptor schema during registration.
        
        Args:
            name: The tool name (will be normalized)
            factory: A callable that returns a new tool instance
            meta: Optional metadata dict
            descriptor: Optional ToolDescriptor or dict to coerce
            overwrite: If True, allow overwriting existing registrations
            emit_event_fn: Optional function to emit trace events
            
        Raises:
            ValueError: If factory is an instance instead of callable
            ValueError: If name is already registered and overwrite=False
            DescriptorValidationError: If descriptor validation fails
        """
        norm = cls._normalize_name(name)
        if not overwrite and norm in cls._tools:
            raise ValueError(f"Tool already registered: {name}")
        
        if isinstance(factory, BaseTool):
            raise ValueError(
                "ToolRegistry.register requires a factory to avoid shared state across runs."
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
                        "component_type": "tool",
                        "name": name,
                        "field_errors": field_errors,
                        "error_message": str(e),
                    },
                )
            
            raise DescriptorValidationError(
                "Tool descriptor validation failed",
                descriptor_name=name,
                field_errors=field_errors,
            ) from e
        
        cls._tools[norm] = ToolRegistration(
            name=norm,
            factory=actual_factory,
            meta=meta or {},
            descriptor=resolved_descriptor,
            descriptor_auto=descriptor is None,
        )
    
    @classmethod
    def resolve(cls, name: str) -> BaseTool:
        """Resolve a tool by name, returning a fresh instance."""
        norm = cls._normalize_name(name)
        reg = cls._tools.get(norm)
        if reg is None:
            raise KeyError(f"Unknown tool: {name}")
        return reg.factory()
    
    @classmethod
    def has(cls, name: str) -> bool:
        """Check if a tool is registered."""
        return cls._normalize_name(name) in cls._tools
    
    @classmethod
    def list(cls) -> Dict[str, Dict[str, Any]]:
        """Return a dict of registered tools with their metadata."""
        return {k: {"name": v.name, "meta": v.meta} for k, v in cls._tools.items()}
    
    @classmethod
    def list_registered(cls) -> List[str]:
        """Return a list of all registered tool names."""
        return list(cls._tools.keys())
    
    @classmethod
    def get_factory(cls, name: str) -> ToolFactory:
        """Get the factory function for a tool."""
        norm = cls._normalize_name(name)
        reg = cls._tools.get(norm)
        if reg is None:
            raise KeyError(f"Unknown tool: {name}")
        return reg.factory
    
    @classmethod
    def get_descriptor(cls, name: str) -> ToolDescriptor:
        """Get the descriptor for a tool, hydrating if needed."""
        norm = cls._normalize_name(name)
        reg = cls._tools.get(norm)
        if reg is None:
            raise KeyError(f"Unknown tool: {name}")
        if reg.descriptor_auto:
            reg = cls._hydrate_descriptor(reg)
        return reg.descriptor
    
    @classmethod
    def list_descriptors(cls) -> Iterable[ToolDescriptor]:
        """Return all tool descriptors."""
        descriptors: List[ToolDescriptor] = []
        for reg in cls._tools.values():
            if reg.descriptor_auto:
                reg = cls._hydrate_descriptor(reg)
            descriptors.append(reg.descriptor)
        return descriptors
    
    @classmethod
    def get_all_descriptors(cls) -> List[ToolDescriptor]:
        """
        INT-DISC-046: Return all tool descriptors as a list.
        
        Alias for list_descriptors() returning a concrete list.
        """
        return list(cls.list_descriptors())
    
    @classmethod
    def filter_by_capability_tags(
        cls,
        tags: List[str],
        *,
        match_all: bool = False,
    ) -> List[str]:
        """
        INT-DISC-047: Filter tools by capability tags.
        
        Args:
            tags: List of capability tags to match
            match_all: If True, require all tags to match. If False, match any.
            
        Returns:
            List of tool names matching the filter
        """
        result: List[str] = []
        tags_lower = [t.lower() for t in tags]
        
        for name, reg in cls._tools.items():
            caps_lower = [c.lower() for c in reg.descriptor.capabilities]
            
            if match_all:
                if all(t in caps_lower for t in tags_lower):
                    result.append(name)
            else:
                if any(t in caps_lower for t in tags_lower):
                    result.append(name)
        
        return result
    
    @classmethod
    def _hydrate_descriptor(cls, reg: ToolRegistration) -> ToolRegistration:
        """Hydrate an auto-generated descriptor with actual tool info."""
        try:
            tool = reg.factory()
        except Exception:
            return reg
        
        description = reg.descriptor.description or getattr(tool, "description", "") or ""
        read_only = reg.descriptor.read_only
        side_effect = reg.descriptor.side_effect
        risk = getattr(tool, "risk", None)
        
        if isinstance(risk, str) and risk.lower() == "read_only":
            read_only = True
            side_effect = False
        
        updated = reg.descriptor.model_copy(
            update={
                "description": description,
                "read_only": read_only,
                "side_effect": side_effect,
            }
        )
        hydrated = ToolRegistration(
            name=reg.name,
            factory=reg.factory,
            meta=reg.meta,
            descriptor=updated,
            descriptor_auto=False,
        )
        cls._tools[cls._normalize_name(reg.name)] = hydrated
        return hydrated
    
    @classmethod
    def _coerce_descriptor(
        cls,
        name: str,
        factory: ToolFactory,
        meta: Dict[str, Any],
        descriptor: Optional[ToolDescriptor | Dict[str, Any]],
    ) -> ToolDescriptor:
        """Coerce descriptor from various input types."""
        if isinstance(descriptor, ToolDescriptor):
            return descriptor
        if isinstance(descriptor, dict):
            return ToolDescriptor.model_validate(descriptor)
        
        description = ""
        risk = None
        tags = list(meta.get("tags") or [])
        capabilities = list(meta.get("capabilities") or tags)  # Fall back to tags
        
        read_only = bool(meta.get("read_only")) if "read_only" in meta else False
        side_effect = bool(meta.get("side_effect")) if "side_effect" in meta else True
        if isinstance(risk, str) and risk.lower() == "read_only":
            read_only = True
            side_effect = False
        
        sensitivity = meta.get("sensitivity_class") or SensitivityClass.UNKNOWN
        cost_hint = meta.get("cost_hint") or CostHint.UNKNOWN
        
        return ToolDescriptor(
            name=name,
            description=description,
            capabilities=capabilities,
            tags=tags,
            input_schema_ref=meta.get("input_schema_ref"),
            output_schema_ref=meta.get("output_schema_ref"),
            read_only=read_only,
            side_effect=side_effect,
            sensitivity_class=(
                SensitivityClass(str(sensitivity))
                if not isinstance(sensitivity, SensitivityClass)
                else sensitivity
            ),
            cost_hint=(
                CostHint(str(cost_hint))
                if not isinstance(cost_hint, CostHint)
                else cost_hint
            ),
        )
