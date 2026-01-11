# ==============================
# Generic Component Registry
# ==============================
"""
Generic registry base class for agents, tools, and other component factories.

This module provides a unified registry pattern that can be specialized for
different component types while maintaining consistent behavior.

Usage:
    class MyRegistry(ComponentRegistry[MyComponent]):
        _components: Dict[str, ComponentRegistration[MyComponent]] = {}
        
        @classmethod
        def _get_components(cls) -> Dict[str, ComponentRegistration[MyComponent]]:
            return cls._components
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")

ComponentFactory = Callable[[], T]


@dataclass(frozen=True)
class ComponentRegistration(Generic[T]):
    """Registration record for a component."""
    
    name: str
    factory: ComponentFactory[T]
    meta: Dict[str, Any]


class ComponentRegistry(Generic[T]):
    """
    Generic registry for agents, tools, or other component factories.
    
    Subclasses must:
    1. Define a class-level _components dict
    2. Implement _get_components() to return that dict
    3. Define _component_type class attribute for error messages
    
    The registry stores factories (not instances) to ensure every resolution
    gets a fresh instance, avoiding shared state across runs.
    """
    
    _component_type: str = "component"
    
    @classmethod
    def _get_components(cls) -> Dict[str, ComponentRegistration[T]]:
        """Return the component storage dict. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _get_components()")
    
    @classmethod
    def _normalize_name(cls, name: str) -> str:
        """Normalize a component name for consistent lookup."""
        return name.strip().lower().replace(" ", "_")
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered components."""
        cls._get_components().clear()
    
    @classmethod
    def register(
        cls,
        name: str,
        factory: ComponentFactory[T],
        *,
        meta: Optional[Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> None:
        """
        Register a component factory.
        
        Args:
            name: The component name (will be normalized)
            factory: A callable that returns a new component instance
            meta: Optional metadata dict
            overwrite: If True, allow overwriting existing registrations
            
        Raises:
            ValueError: If name is already registered and overwrite=False
        """
        norm = cls._normalize_name(name)
        components = cls._get_components()
        
        if not overwrite and norm in components:
            raise ValueError(f"{cls._component_type} already registered: {name}")
        
        components[norm] = ComponentRegistration(
            name=norm,
            factory=factory,
            meta=meta or {},
        )
    
    @classmethod
    def resolve(cls, name: str) -> T:
        """
        Resolve a component by name, returning a fresh instance.
        
        Args:
            name: The component name
            
        Returns:
            A new instance of the component
            
        Raises:
            KeyError: If the component is not registered
        """
        norm = cls._normalize_name(name)
        components = cls._get_components()
        reg = components.get(norm)
        if reg is None:
            raise KeyError(f"Unknown {cls._component_type}: {name}")
        return reg.factory()
    
    @classmethod
    def get_factory(cls, name: str) -> ComponentFactory[T]:
        """
        Get the factory function for a component.
        
        Args:
            name: The component name
            
        Returns:
            The factory callable
            
        Raises:
            KeyError: If the component is not registered
        """
        norm = cls._normalize_name(name)
        components = cls._get_components()
        reg = components.get(norm)
        if reg is None:
            raise KeyError(f"Unknown {cls._component_type}: {name}")
        return reg.factory
    
    @classmethod
    def has(cls, name: str) -> bool:
        """Check if a component is registered."""
        norm = cls._normalize_name(name)
        return norm in cls._get_components()
    
    @classmethod
    def list_registered(cls) -> List[str]:
        """Return a list of all registered component names."""
        return list(cls._get_components().keys())
    
    @classmethod
    def list(cls) -> Dict[str, Dict[str, Any]]:
        """Return a dict of registered components with their metadata."""
        return {
            k: {"name": v.name, "meta": v.meta}
            for k, v in cls._get_components().items()
        }
    
    @classmethod
    def get_meta(cls, name: str) -> Dict[str, Any]:
        """
        Get the metadata for a component.
        
        Args:
            name: The component name
            
        Returns:
            The metadata dict
            
        Raises:
            KeyError: If the component is not registered
        """
        norm = cls._normalize_name(name)
        components = cls._get_components()
        reg = components.get(norm)
        if reg is None:
            raise KeyError(f"Unknown {cls._component_type}: {name}")
        return reg.meta
