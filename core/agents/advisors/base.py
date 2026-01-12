# core/agents/advisors/base.py
# ==============================
# Advisory Agent Base Class
# ==============================
"""
Base class for advisory agents that cannot execute tools.

Advisory agents are bounded intelligence components that:
- Provide structured recommendations (tool selection, gap analysis, etc.)
- Cannot invoke tool execution directly
- Cannot produce control-flow directives
- Output validated against schemas

Non-negotiable rules:
- Advisory agents MUST NOT import core.tools.executor
- Advisory agents MUST return structured AdvisoryResult outputs
- Advisory agents CANNOT call tools; only recommend them
"""

from __future__ import annotations

import json
from abc import abstractmethod
from typing import Any, Callable, Dict, Optional, Type, Union

from pydantic import BaseModel

from core.agents.base import BaseAgent
from core.config.loader import load_settings
from core.contracts.agent_schema import (
    AgentError,
    AgentErrorCode,
    AgentKind,
    AgentMeta,
    AgentResult,
)
from core.contracts.context_pack_schema import ContextPack
from core.contracts.reasoning_schema import ReasoningPurpose
from core.governance.hooks import GovernanceHooks
from ...models.router import ModelRouter, OpenAIRequest
from core.orchestrator.context import StepContext


# Type for injectable LLM reasoner (for testing)
AdvisoryReasoner = Callable[[Dict[str, Any]], Union[Dict[str, Any], str]]


class AdvisoryAgent(BaseAgent):
    """
    Base class for advisory agents that cannot execute tools.

    Advisory agents provide structured recommendations without direct tool invocation.
    They are bounded intelligence components that:
    - Analyze context and evidence
    - Recommend actions (tools, agents, next steps)
    - Identify gaps in evidence
    - Explain risks and confidence levels

    All outputs are structured and validated against Pydantic schemas.

    Subclasses must:
    - Set `name`, `description`, `kind`, `purpose`, `output_model`
    - Implement `_build_system_prompt()` for LLM guidance
    - Optionally override `_build_payload()` for custom input formatting
    """

    # Class attributes to be set by subclasses
    name: str = "advisory_base"
    description: str = "Base advisory agent."
    kind: AgentKind = AgentKind.OTHER
    purpose: ReasoningPurpose = ReasoningPurpose.EXPLANATION
    output_model: Type[BaseModel]

    # Enforced: advisory agents cannot execute tools
    _can_execute_tools: bool = False

    def __init__(
        self,
        *,
        config: Optional[Dict[str, Any]] = None,
        llm_reasoner: Optional[AdvisoryReasoner] = None,
    ) -> None:
        """
        Initialize advisory agent.

        Args:
            config: Optional configuration dict (injected, not from env vars)
            llm_reasoner: Optional injectable reasoner for testing
        """
        super().__init__(config=config)
        self._llm_reasoner = llm_reasoner
        # Enforce no tool execution capability
        self._can_execute_tools = False

    @property
    def can_execute_tools(self) -> bool:
        """Advisory agents cannot execute tools."""
        return False

    def run(self, step_context: StepContext) -> AgentResult:
        """
        Execute the advisory agent for a single step.

        Returns structured recommendations in AgentResult envelope.
        """
        meta = AgentMeta(agent_name=self.name, kind=self.kind)
        params = step_context.step.params if step_context.step else {}

        try:
            payload = self._build_payload(params)
            raw = self._call_reasoner(step_context, payload)
            data = json.loads(raw) if isinstance(raw, str) else raw
            output = self.output_model.model_validate(data)
            return AgentResult(
                ok=True,
                data=output.model_dump(mode="json"),
                error=None,
                meta=meta,
            )
        except Exception as exc:
            err = AgentError(
                code=AgentErrorCode.INVALID_INPUT,
                message=str(exc),
                recoverable=False,
            )
            return AgentResult(ok=False, data=None, error=err, meta=meta)

    def _build_payload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the payload for the LLM reasoner.

        Subclasses can override for custom input formatting.
        """
        question = params.get("question") or ""
        context_pack = params.get("context_pack")

        if isinstance(context_pack, dict):
            context_pack = ContextPack.model_validate(context_pack).model_dump(mode="json")

        tools = params.get("tools")
        agents = params.get("agents")
        evidence_ids = params.get("evidence_ids")

        return {
            "question": question,
            "context_pack": context_pack or {},
            "tools": tools or [],
            "agents": agents or [],
            "evidence_ids": evidence_ids or [],
        }

    @abstractmethod
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for the LLM.

        Subclasses must implement to provide task-specific guidance.
        """
        raise NotImplementedError

    def _call_reasoner(
        self, step_context: StepContext, payload: Dict[str, Any]
    ) -> Union[Dict[str, Any], str]:
        """
        Call the LLM reasoner to generate advisory output.

        Uses injectable reasoner if provided (for testing), otherwise calls LLM.
        """
        if self._llm_reasoner is not None:
            return self._llm_reasoner(payload)

        settings = load_settings()
        governance = GovernanceHooks(settings=settings)
        router = ModelRouter.from_settings(settings)
        model = router.select(
            product=step_context.product,
            purpose=self.purpose,
            override_model=None,
        ).model

        system_prompt = self._build_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=True)},
        ]

        decision = governance.before_model_call(
            model_name=model,
            purpose=self.purpose,
            messages={"messages": messages},
            max_tokens=None,
            ctx=step_context,
        )

        step_context.emit(
            "model_call_attempt_started",
            {
                "model": model,
                "purpose": self.purpose.value,
                "allowed": decision.allowed,
                "reason": decision.reason,
                "agent": self.name,
            },
        )

        if not decision.allowed:
            raise ValueError(decision.reason or "model_call_blocked")

        req = OpenAIRequest(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=None,
            metadata={"agent": self.name, "kind": "advisory"},
        )

        resp = router.completion_openai(
            request=req,
            product=step_context.product,
            purpose=self.purpose,
            override_model=None,
        )

        if not resp.ok:
            raise ValueError("model_error")

        return resp.content
