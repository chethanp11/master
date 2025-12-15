# ==============================
# Base Tool Contract
# ==============================
"""
Base tool contract for master/.

Rules:
- Tools are executed ONLY through core/tools/executor.py (later phase).
- Tools do not read env vars directly. Config is injected.
- Tools return ToolResult from core/contracts/tool_schema.py (standard envelope).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from core.contracts.tool_schema import ToolResult
from core.orchestrator.context import StepContext


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