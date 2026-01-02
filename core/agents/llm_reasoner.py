# ==============================
# Core LLM Reasoner Agent
# ==============================
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from core.agents.base import BaseAgent
from core.config.loader import load_settings
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult, AgentKind
from core.governance.hooks import GovernanceHooks
from core.models.providers.openai_provider import OpenAIRequest
from core.models.router import ModelRouter
from core.orchestrator.context import StepContext
from core.agents.renderer import render_messages


class LlmReasonerParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    purpose: Optional[str] = Field(default=None, description="Routing hint for model selection.")
    system: Optional[str] = Field(default=None, description="System instruction for the model.")
    prompt: Optional[str] = Field(default=None, description="Primary user instruction.")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Optional pre-built message list.")
    temperature: float = Field(default=0.2)
    max_tokens: Optional[int] = Field(default=None)
    override_model: Optional[str] = Field(default=None)


class LlmReasoner(BaseAgent):
    """
    Core generic LLM agent.

    Responsibilities:
    - Build model request from params + run context
    - Enforce governance hooks (model allow/deny + token budget)
    - Emit trace events for model calls
    - Return structured AgentResult
    """

    name: str = "llm_reasoner"
    description: str = "Core LLM reasoning agent with governance + tracing."

    def run(self, step_context: StepContext) -> AgentResult:
        meta = AgentMeta(
            agent_name=self.name,
            kind=AgentKind.OTHER,
            tags={"product": step_context.product, "flow": step_context.flow},
        )
        try:
            params = LlmReasonerParams.model_validate(step_context.step.params or {})
            context = {
                "artifacts": step_context.run.artifacts,
                "payload": step_context.run.payload,
            }
            messages = self._build_messages(params)
            try:
                messages = render_messages(messages, context)
            except KeyError as exc:
                err = AgentError(code=AgentErrorCode.INVALID_INPUT, message=str(exc))
                return AgentResult(ok=False, data=None, error=err, meta=meta)
            settings = load_settings()
            governance = GovernanceHooks(settings=settings)
            router = ModelRouter.from_settings(settings)

            # Pre-flight governance decision
            model_name = router.select(product=step_context.product, purpose=params.purpose, override_model=params.override_model).model
            decision = governance.before_model_call(
                model_name=model_name,
                purpose=params.purpose,
                messages={"messages": messages},
                max_tokens=params.max_tokens,
                ctx=step_context,
            )
            step_context.emit(
                "model_call_attempt_started",
                {
                    "model": model_name,
                    "purpose": params.purpose,
                    "allowed": decision.allowed,
                    "reason": decision.reason,
                },
            )
            if not decision.allowed:
                err = AgentError(code=AgentErrorCode.POLICY_BLOCKED, message=decision.reason, details=decision.details)
                meta.redacted = True
                return AgentResult(ok=False, data=None, error=err, meta=meta)

            req = OpenAIRequest(
                model=model_name,
                messages=messages,
                temperature=params.temperature,
                max_tokens=params.max_tokens,
                metadata={"product": step_context.product, "flow": step_context.flow, "step_id": step_context.step_id},
            )
            resp = router.completion_openai(
                request=req,
                product=step_context.product,
                purpose=params.purpose,
                override_model=params.override_model,
            )
            if not resp.ok:
                message = ""
                if resp.error and isinstance(resp.error, dict):
                    message = str(resp.error.get("message") or "")
                if not message:
                    message = "model_error"
                err = AgentError(code=AgentErrorCode.MODEL_ERROR, message=message, details=resp.error or {})
                step_context.emit(
                    "model_call_failed",
                    {"model": model_name, "reason": err.message, "error": resp.error or {}},
                )
                return AgentResult(ok=False, data=None, error=err, meta=meta)

            usage = resp.usage or {}
            meta.token_estimate = usage.get("total_tokens")
            step_context.emit(
                "model_call_succeeded",
                {
                    "model": resp.model,
                    "usage": usage,
                    "provider": resp.meta.get("provider") if isinstance(resp.meta, dict) else None,
                },
            )
            data = {
                "content": resp.content,
                "model": resp.model,
                "usage": usage,
                "provider": resp.meta.get("provider") if isinstance(resp.meta, dict) else None,
            }
            return AgentResult(ok=True, data=data, error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=meta)

    @staticmethod
    def _build_messages(params: LlmReasonerParams) -> List[Dict[str, Any]]:
        if params.messages:
            return params.messages
        messages: List[Dict[str, Any]] = []
        if params.system:
            messages.append({"role": "system", "content": params.system})
        if params.prompt:
            messages.append({"role": "user", "content": params.prompt})
        return messages


def build() -> LlmReasoner:
    return LlmReasoner()
