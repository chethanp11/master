from __future__ import annotations

# ==============================
# Core LLM Reasoner Agent
# ==============================

from typing import Any, Dict, List, Optional
import json

from pydantic import BaseModel, Field, ConfigDict, ValidationError

from core.agents.base import BaseAgent
from core.config.loader import load_settings
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult, AgentKind
from core.contracts.reasoning_schema import ReasoningPurpose
from core.governance.hooks import GovernanceHooks
from ..models.providers.openai_provider import OpenAIRequest
from ..models.router import ModelRouter
from core.orchestrator.context import StepContext
from core.orchestrator.templating import render_messages


class LlmReasonerParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    purpose: ReasoningPurpose = Field(..., description="Required reasoning purpose for model selection.")
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
                    "purpose": params.purpose.value,
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
                metadata={
                    "product": step_context.product,
                    "flow": step_context.flow,
                    "step_id": step_context.step_id,
                    "reasoning_purpose": params.purpose.value,
                },
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
                    {
                        "model": model_name,
                        "purpose": params.purpose.value,
                        "reason": err.message,
                        "error": resp.error or {},
                    },
                )
                return AgentResult(ok=False, data=None, error=err, meta=meta)

            usage = resp.usage or {}
            meta.token_estimate = usage.get("total_tokens")
            tokens_used = usage.get("total_tokens")
            if tokens_used is None:
                tokens_used = params.max_tokens or 0
            try:
                tokens_used_int = int(tokens_used)
            except Exception:
                tokens_used_int = 0
            run_tokens = int(step_context.run.meta.get("tokens_used", 0))
            run_tokens += tokens_used_int
            step_context.run.meta["tokens_used"] = run_tokens
            run_budget = governance.settings.policies.max_tokens_per_run
            if run_budget is not None and run_tokens > run_budget:
                step_context.emit(
                    "model_call_budget_exceeded",
                    {
                        "model": resp.model,
                        "purpose": params.purpose.value,
                        "used": run_tokens,
                        "limit": run_budget,
                    },
                )
                err = AgentError(
                    code=AgentErrorCode.POLICY_BLOCKED,
                    message="run_token_budget_exceeded",
                    details={"used": run_tokens, "limit": run_budget},
                )
                meta.redacted = True
                return AgentResult(ok=False, data=None, error=err, meta=meta)
            step_context.emit(
                "model_call_succeeded",
                {
                    "model": resp.model,
                    "purpose": params.purpose.value,
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
        except ValidationError as exc:
            err = AgentError(code=AgentErrorCode.INVALID_INPUT, message="invalid_llm_reasoner_params", details=exc.errors())
            return AgentResult(ok=False, data=None, error=err, meta=meta)
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


class RoleReasonerParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str
    temperature: float = Field(default=0.2)
    max_tokens: Optional[int] = Field(default=None)
    override_model: Optional[str] = Field(default=None)


class InsightReasonerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    highlights: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class PrioritizedItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item: str
    priority: int
    rationale: str


class PrioritizationReasonerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    priorities: List[PrioritizedItem]


class ExplanationReasonerOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    explanation: str
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class _RoleReasoner(BaseAgent):
    name: str = "role_reasoner"
    purpose: ReasoningPurpose = ReasoningPurpose.EXPLANATION
    output_model: type[BaseModel]

    def run(self, step_context: StepContext) -> AgentResult:
        meta = AgentMeta(
            agent_name=self.name,
            kind=AgentKind.OTHER,
            tags={"product": step_context.product, "flow": step_context.flow},
        )
        try:
            if not step_context.step:
                raise ValueError("missing_step_definition")
            params = RoleReasonerParams.model_validate(step_context.step.params or {})
            llm_params = LlmReasonerParams(
                purpose=self.purpose,
                system=self._system_prompt(),
                prompt=params.prompt,
                temperature=params.temperature,
                max_tokens=params.max_tokens,
                override_model=params.override_model,
            )
            updated_step = step_context.step.model_copy(update={"params": llm_params.model_dump(mode="json")})
            llm_ctx = step_context.run.new_step(step_def=updated_step)
            llm_result = LlmReasoner().run(llm_ctx)
            if not llm_result.ok:
                return llm_result
            content = (llm_result.data or {}).get("content")
            payload = _parse_json_payload(content)
            output = self.output_model.model_validate(payload)
            meta = llm_result.meta.model_copy(update={"agent_name": self.name})
            return AgentResult(ok=True, data=output.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.CONTRACT_VIOLATION, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=meta)

    def _system_prompt(self) -> str:
        fields = list(getattr(self.output_model, "model_fields", {}).keys())
        return f"Return JSON only with keys: {', '.join(fields)}."


class InsightReasoner(_RoleReasoner):
    name = "insight_reasoner"
    purpose = ReasoningPurpose.INSIGHT
    output_model = InsightReasonerOutput


class PrioritizationReasoner(_RoleReasoner):
    name = "prioritization_reasoner"
    purpose = ReasoningPurpose.PRIORITIZATION
    output_model = PrioritizationReasonerOutput


class ExplanationReasoner(_RoleReasoner):
    name = "explanation_reasoner"
    purpose = ReasoningPurpose.EXPLANATION
    output_model = ExplanationReasonerOutput


def build_insight_reasoner() -> InsightReasoner:
    return InsightReasoner()


def build_prioritization_reasoner() -> PrioritizationReasoner:
    return PrioritizationReasoner()


def build_explanation_reasoner() -> ExplanationReasoner:
    return ExplanationReasoner()


def _parse_json_payload(content: Any) -> Dict[str, Any]:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        try:
            return json.loads(content)
        except Exception as exc:
            raise ValueError("invalid_json_output") from exc
    raise ValueError("missing_json_output")
