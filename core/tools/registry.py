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
from typing import Any, Callable, Dict, Optional, Iterable

from core.tools.base import BaseTool
from core.contracts.descriptors_schema import ToolDescriptor, SensitivityClass, CostHint


ToolFactory = Callable[[], BaseTool]


@dataclass(frozen=True)
class ToolRegistration:
    name: str
    factory: ToolFactory
    meta: Dict[str, Any]
    descriptor: ToolDescriptor


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
        descriptor: Optional[ToolDescriptor | Dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> None:
        norm = _norm(name)
        if not overwrite and norm in cls._tools:
            raise ValueError(f"Tool already registered: {name}")

        if isinstance(factory, BaseTool):
            raise ValueError("ToolRegistry.register requires a factory to avoid shared state across runs.")
        actual_factory = factory

        resolved_descriptor = cls._coerce_descriptor(norm, actual_factory, meta or {}, descriptor)
        cls._tools[norm] = ToolRegistration(
            name=norm,
            factory=actual_factory,
            meta=meta or {},
            descriptor=resolved_descriptor,
        )

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

    @classmethod
    def get_descriptor(cls, name: str) -> ToolDescriptor:
        norm = _norm(name)
        reg = cls._tools.get(norm)
        if reg is None:
            raise KeyError(f"Unknown tool: {name}")
        return reg.descriptor

    @classmethod
    def list_descriptors(cls) -> Iterable[ToolDescriptor]:
        return [reg.descriptor for reg in cls._tools.values()]

    @classmethod
    def _coerce_descriptor(
        cls,
        name: str,
        factory: ToolFactory,
        meta: Dict[str, Any],
        descriptor: Optional[ToolDescriptor | Dict[str, Any]],
    ) -> ToolDescriptor:
        if isinstance(descriptor, ToolDescriptor):
            return descriptor
        if isinstance(descriptor, dict):
            return ToolDescriptor.model_validate(descriptor)

        description = ""
        risk = None
        try:
            tool = factory()
            description = getattr(tool, "description", "") or ""
            risk = getattr(tool, "risk", None)
        except Exception:
            tool = None  # type: ignore[assignment]
        tags = list(meta.get("tags") or [])

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
            tags=tags,
            input_schema_ref=meta.get("input_schema_ref"),
            output_schema_ref=meta.get("output_schema_ref"),
            read_only=read_only,
            side_effect=side_effect,
            sensitivity_class=SensitivityClass(str(sensitivity)) if not isinstance(sensitivity, SensitivityClass) else sensitivity,
            cost_hint=CostHint(str(cost_hint)) if not isinstance(cost_hint, CostHint) else cost_hint,
        )


def _norm(name: str) -> str:
    return name.strip().lower().replace(" ", "_")
