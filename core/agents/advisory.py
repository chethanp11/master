from __future__ import annotations

# ==============================
# Advisory Agents
# ==============================
"""
Advisory-only agents that return structured recommendations.
"""

import json
from typing import Any, Callable, Dict, Optional, Type, Union

from pydantic import BaseModel

from core.agents.base import BaseAgent
from core.config.loader import load_settings
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult, AgentKind
from core.contracts.advisory_schema import (
    ToolSelectorOutput,
    AgentSelectorOutput,
    GapFinderOutput,
    SummarizerOutput,
    RiskExplainerOutput,
)
from core.contracts.context_pack_schema import ContextPack
from core.contracts.reasoning_schema import ReasoningPurpose
from core.governance.hooks import GovernanceHooks
from ..models.providers.openai_provider import OpenAIRequest
from ..models.router import ModelRouter
from core.orchestrator.context import StepContext

AdvisoryReasoner = Callable[[Dict[str, Any]], Union[Dict[str, Any], str]]


class _AdvisoryAgent(BaseAgent):
    name: str = "advisory_base"
    description: str = "Advisory base agent."
    kind: AgentKind = AgentKind.OTHER
    purpose: ReasoningPurpose = ReasoningPurpose.EXPLANATION
    output_model: Type[BaseModel]

    def __init__(self, *, llm_reasoner: Optional[AdvisoryReasoner] = None) -> None:
        super().__init__(config=None)
        self._llm_reasoner = llm_reasoner

    def run(self, step_context: StepContext) -> AgentResult:  # type: ignore[override]
        meta = AgentMeta(agent_name=self.name, kind=self.kind)
        params = step_context.step.params if step_context.step else {}
        payload = self._build_payload(params)
        try:
            raw = self._call_reasoner(step_context, payload)
            data = json.loads(raw) if isinstance(raw, str) else raw
            output = self.output_model.model_validate(data)
            return AgentResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.INVALID_INPUT, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=meta)

    def _build_payload(self, params: Dict[str, Any]) -> Dict[str, Any]:
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

    def _call_reasoner(self, step_context: StepContext, payload: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        if self._llm_reasoner is not None:
            return self._llm_reasoner(payload)

        settings = load_settings()
        governance = GovernanceHooks(settings=settings)
        router = ModelRouter.from_settings(settings)
        model = router.select(product=step_context.product, purpose=self.purpose, override_model=None).model
        messages = [
            {"role": "system", "content": "Return JSON only. Do not include any control directives."},
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
            {"model": model, "purpose": self.purpose.value, "allowed": decision.allowed, "reason": decision.reason},
        )
        if not decision.allowed:
            raise ValueError(decision.reason or "model_call_blocked")
        req = OpenAIRequest(model=model, messages=messages, temperature=0.2, max_tokens=None, metadata={})
        resp = router.completion_openai(request=req, product=step_context.product, purpose=self.purpose, override_model=None)
        if not resp.ok:
            raise ValueError("model_error")
        return resp.content


class ToolSelectorAgent(_AdvisoryAgent):
    name = "tool_selector"
    description = "Advisory tool selector."
    kind = AgentKind.ROUTER
    purpose = ReasoningPurpose.PRIORITIZATION
    output_model = ToolSelectorOutput


class AgentSelectorAgent(_AdvisoryAgent):
    name = "agent_selector"
    description = "Advisory agent selector."
    kind = AgentKind.ROUTER
    purpose = ReasoningPurpose.PRIORITIZATION
    output_model = AgentSelectorOutput


class GapFinderAgent(_AdvisoryAgent):
    name = "gap_finder"
    description = "Advisory gap finder."
    kind = AgentKind.VALIDATOR
    purpose = ReasoningPurpose.UNCERTAINTY
    output_model = GapFinderOutput


class SummarizerAgent(_AdvisoryAgent):
    name = "summarizer"
    description = "Advisory summarizer."
    kind = AgentKind.SUMMARIZER
    purpose = ReasoningPurpose.EXPLANATION
    output_model = SummarizerOutput


class RiskExplainerAgent(_AdvisoryAgent):
    name = "risk_explainer"
    description = "Advisory risk explainer."
    kind = AgentKind.OTHER
    purpose = ReasoningPurpose.EXPLANATION
    output_model = RiskExplainerOutput


def build_tool_selector() -> BaseAgent:
    return ToolSelectorAgent()


def build_agent_selector() -> BaseAgent:
    return AgentSelectorAgent()


def build_gap_finder() -> BaseAgent:
    return GapFinderAgent()


def build_summarizer() -> BaseAgent:
    return SummarizerAgent()


def build_risk_explainer() -> BaseAgent:
    return RiskExplainerAgent()
