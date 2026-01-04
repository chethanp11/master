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
