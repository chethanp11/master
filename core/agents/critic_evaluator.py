from __future__ import annotations

# ==============================
# Critic Evaluator
# ==============================
"""
Bounded critic/evaluator helper and agent wrapper.
"""

import json
from typing import Any, Callable, Dict, List, Optional, Union

from core.agents.base import BaseAgent
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult
from core.contracts.context_pack_schema import ContextPack
from core.contracts.critic_schema import CriticFailure, CriticOutput, CriticResult
from core.contracts.evidence_schema import EvidenceItem
from core.contracts.reasoning_ladder_schema import ReasoningLadderOutput
from core.orchestrator.context import StepContext

TraceEmitter = Callable[[str, Dict[str, Any]], None]
CriticReasoner = Callable[[Dict[str, Any]], Union[Dict[str, Any], str]]


def run_critic_evaluator(
    *,
    context_pack: ContextPack,
    evidence: List[EvidenceItem],
    reasoning: ReasoningLadderOutput,
    question: str,
    llm_reasoner: CriticReasoner,
    trace: Optional[TraceEmitter] = None,
) -> CriticResult:
    payload = {
        "question": question,
        "context_pack": context_pack.model_dump(mode="json"),
        "evidence_ids": [item.id for item in evidence],
        "reasoning": reasoning.model_dump(mode="json"),
    }
    _emit(trace, "critic_evaluator_started", {"evidence_count": len(evidence), "question_len": len(question or "")})
    try:
        raw = llm_reasoner(payload)
        if isinstance(raw, str):
            data = json.loads(raw)
        else:
            data = raw
        output = CriticOutput.model_validate(data)
        _emit(
            trace,
            "critic_evaluator_completed",
            {
                "recommended_next_action": output.recommended_next_action,
                "completeness_score": output.completeness_score,
                "confidence_adjustment": output.confidence_adjustment,
            },
        )
        return CriticResult(ok=True, output=output)
    except Exception as exc:
        _emit(trace, "critic_evaluator_failed", {"reason": "validation_failed"})
        return CriticResult(ok=False, error=CriticFailure(reason="validation_failed", details={"error": str(exc)}))


class CriticEvaluatorAgent(BaseAgent):
    name: str = "critic_evaluator"
    description: str = "Bounded critic agent that returns structured review signals."

    def __init__(
        self,
        *,
        llm_reasoner: Optional[CriticReasoner] = None,
        trace: Optional[TraceEmitter] = None,
    ) -> None:
        super().__init__(config=None)
        self._llm_reasoner = llm_reasoner
        self._trace = trace

    def run(self, step_context: StepContext) -> AgentResult:  # type: ignore[override]
        params = step_context.step.params if step_context.step else {}
        meta = AgentMeta(agent_name=self.name)
        if self._llm_reasoner is None:
            err = AgentError(code=AgentErrorCode.INVALID_INPUT, message="llm_reasoner_missing")
            return AgentResult(ok=False, data=None, error=err, meta=meta)
        try:
            context_pack = ContextPack.model_validate(params.get("context_pack") or {})
            evidence_raw = params.get("evidence") or []
            evidence = [EvidenceItem.model_validate(item) for item in evidence_raw]
            reasoning = ReasoningLadderOutput.model_validate(params.get("reasoning") or {})
            question = params.get("question") or ""
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.INVALID_INPUT, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=meta)

        result = run_critic_evaluator(
            context_pack=context_pack,
            evidence=evidence,
            reasoning=reasoning,
            question=question,
            llm_reasoner=self._llm_reasoner,
            trace=self._trace or step_context.emit,
        )
        if not result.ok or result.output is None:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=result.error.reason if result.error else "critic_failed")
            return AgentResult(ok=False, data=None, error=err, meta=meta)
        return AgentResult(ok=True, data=result.output.model_dump(mode="json"), error=None, meta=meta)


def _emit(trace: Optional[TraceEmitter], event_type: str, payload: Dict[str, Any]) -> None:
    if trace is None:
        return
    trace(event_type, payload)
