# core/agents/base.py
# ==============================
# Base Agent Contract
# ==============================
"""
Base agent contract for master/.

Non-negotiable rules (master v1+):
- Agents are GOAL-DRIVEN (not prompt-driven). Apart from minimal foundational system
  instructions at the platform level, agents must not rely on prompts for behavior.
- Agents do NOT call tools directly. They may REQUEST tool usage through orchestrator
  mechanisms (e.g., returning structured tool requests in AgentResult), which are executed
  only via core/tools/executor.py.
- Agents do NOT persist state. They can read/write only to the orchestrator-managed
  artifacts/state provided via StepContext (ephemeral) and emit trace events via hooks.
- Agents do NOT read environment variables. Configuration is injected by the caller.

Interface:
- run(step_context) -> AgentResult (standard envelope in core/contracts/agent_schema.py)

Notes:
- Concrete agents MUST provide a stable `name` used in flows.
- Concrete agents MUST return structured outputs (Pydantic models via AgentResult.data).

Auto-discovery:
- Use the @agent decorator to enable auto-discovery for product agents.
- Decorated classes will be automatically registered when auto_register() is called.
"""

from __future__ import annotations



from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from core.contracts.agent_schema import AgentResult
from core.contracts.descriptors_schema import AgentDescriptor, CostHint
from core.orchestrator.context import StepContext


# Type variable for agent class
T = TypeVar("T", bound="BaseAgent")


def agent(
    name: str,
    purpose: str,
    *,
    capabilities: Optional[List[str]] = None,
    cost_hint: str = "LOW",
    allowed_step_types: Optional[List[str]] = None,
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for agent auto-discovery.

    Marks an agent class for automatic registration with the agent registry.
    The decorator attaches an AgentDescriptor to the class that provides
    metadata for selection, governance, and cost estimation.

    Args:
        name: Unique agent name (used in flows and registries)
        purpose: Primary purpose description of the agent
        capabilities: Semantic tags like ['reasoning', 'planning', 'evaluation']
        cost_hint: Cost estimate - "LOW", "MED", or "HIGH"
        allowed_step_types: Step types this agent can handle (e.g., ["agent"])

    Example:
        @agent(
            name="my_agent",
            purpose="Analyzes data and provides insights",
            capabilities=["analysis", "reasoning"],
            cost_hint="LOW",
        )
        class MyAgent(BaseAgent):
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

        descriptor = AgentDescriptor(
            name=name,
            purpose=purpose,
            capabilities=capabilities or [],
            cost_hint=hint,
            allowed_step_types=allowed_step_types or ["agent"],
        )
        cls._agent_descriptor = descriptor  # type: ignore[attr-defined]
        cls._auto_discover = True  # type: ignore[attr-defined]

        # Ensure the class has the name attribute set
        if not hasattr(cls, "name") or cls.name == "":
            cls.name = name  # type: ignore[misc]

        return cls

    return decorator


class BaseAgent(ABC):
    """
    Base class for all agents (core + products).

    Naming:
        Each concrete agent must provide a stable 'name' used in flows and registries.
        Prefer namespaced names like '{product}.{agent_name}' to avoid collisions.
    """

    name: str

    def __init__(self, *, config: Optional[Dict[str, Any]] = None) -> None:
        # config is injected (e.g., from product.yaml / settings) and must not be sourced
        # from env vars directly inside agents.
        self.config: Dict[str, Any] = config or {}

    @abstractmethod
    def run(self, step_context: StepContext) -> AgentResult:
        """
        Execute the agent for a single orchestrated step.

        step_context typically provides:
        - run metadata (run_id, product, flow)
        - step definition (what is expected in this step)
        - artifacts/state (shared ephemeral state for the run)
        - trace hook(s) (emit structured trace events)

        Contract:
        - Must return an AgentResult envelope (ok/data/error/meta).
        - Must NOT raise raw exceptions outward; handle and wrap in AgentResult.error.
        - Must NOT call tools directly; request tool usage via structured outputs.
        """
        raise NotImplementedError
