# ==============================
# Base Tool Contract
# ==============================
"""
Base tool contract for master/.

Rules:
- Tools are executed ONLY through core/tools/executor.py (later phase).
- Tools do not read env vars directly. Config is injected.
- Tools return ToolResult from core/contracts/tool_schema.py (standard envelope).

Auto-discovery:
- Use the @tool decorator to enable auto-discovery for product tools.
- Decorated classes will be automatically registered when auto_register() is called.
"""

from __future__ import annotations



from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from core.contracts.tool_schema import ToolResult
from core.contracts.descriptors_schema import ToolDescriptor, CostHint, SensitivityClass
from core.orchestrator.context import StepContext


# Type variable for tool class
T = TypeVar("T", bound="BaseTool")


def tool(
    name: str,
    description: str,
    *,
    capabilities: Optional[List[str]] = None,
    read_only: bool = True,
    side_effect: bool = False,
    sensitivity_class: str = "LOW",
    cost_hint: str = "LOW",
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for tool auto-discovery.

    Marks a tool class for automatic registration with the tool registry.
    The decorator attaches a ToolDescriptor to the class that provides
    metadata for selection, governance, and cost estimation.

    Args:
        name: Unique tool name (used in flows and registries)
        description: Human-readable description of what the tool does
        capabilities: Semantic tags like ['data_reading', 'computation', 'visualization']
        read_only: True if tool does not modify external state
        side_effect: True if tool has side effects (e.g., writes files, sends emails)
        sensitivity_class: Data sensitivity - "LOW", "MED", or "HIGH"
        cost_hint: Cost estimate - "LOW", "MED", or "HIGH"

    Example:
        @tool(
            name="my_tool",
            description="Reads data from CSV files",
            capabilities=["data_reading", "csv_parsing"],
            read_only=True,
            side_effect=False,
            sensitivity_class="MED",
            cost_hint="LOW",
        )
        class MyTool(BaseTool):
            ...

    Note:
        - The decorated class must have a `build()` function or be instantiable
          with no required arguments for auto-registration.
    """
    def decorator(cls: Type[T]) -> Type[T]:
        try:
            hint = CostHint(cost_hint.upper())
        except ValueError:
            hint = CostHint.UNKNOWN

        try:
            sensitivity = SensitivityClass(sensitivity_class.upper())
        except ValueError:
            sensitivity = SensitivityClass.UNKNOWN

        descriptor = ToolDescriptor(
            name=name,
            description=description,
            capabilities=capabilities or [],
            read_only=read_only,
            side_effect=side_effect,
            sensitivity_class=sensitivity,
            cost_hint=hint,
        )
        cls._tool_descriptor = descriptor  # type: ignore[attr-defined]
        cls._auto_discover = True  # type: ignore[attr-defined]

        # Ensure the class has the name attribute set
        if not hasattr(cls, "name") or cls.name == "":
            cls.name = name  # type: ignore[misc]

        return cls

    return decorator


class BaseTool(ABC):
    """
    Base class for all tools (core + products).

    Naming:
- Each concrete tool must provide a stable 'name' used in flows.
    """

    name: str

    def __init__(self, *, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

    @abstractmethod
    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        """
        Execute the tool.

        params:
- validated/typed upstream (executor may validate later)

        ctx:
- step/run context, artifacts, trace hook
        """
        raise NotImplementedError
