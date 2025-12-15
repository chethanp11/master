# ==============================
# Base Agent Contract
# ==============================
"""
Base agent contract for master/.

Rules:
- Agents do NOT call tools directly. They may request tool usage via orchestrator steps
  or via higher-level agent logic that delegates to core/tools/executor.py (later phase).
- Agents do NOT persist. They can emit trace events through StepContext hooks.
- Agents do NOT read env vars. Configuration is injected by caller.

Interface:
- run(step_context) -> AgentResult (standard envelope in core/contracts/agent_schema.py)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from core.contracts.agent_schema import AgentResult
from core.orchestrator.context import StepContext


class BaseAgent(ABC):
    """
    Base class for all agents (core + products).

    Naming:
- Each concrete agent must provide a stable 'name' used in flows.
    """

    name: str

    def __init__(self, *, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}

    @abstractmethod
    def run(self, step_context: StepContext) -> AgentResult:
        """
        Execute the agent for a single step.

        step_context provides:
- run metadata
- step definition
- artifacts (shared state)
- trace hook (emit events)
        """
        raise NotImplementedError