from __future__ import annotations

# ==============================
# Critic Evaluator
# ==============================
"""
Bounded critic/evaluator helper and agent wrapper.

The critic evaluates reasoning outputs without calling tools:
- Checks completeness and consistency
- Identifies missing evidence
- Recommends actions: NONE, USER_INPUT, HITL, FETCH_MORE_EVIDENCE

All recommendations are gated by governance policies before execution.
"""

import json
from typing import Any, Callable, Dict, List, Optional, Union

from core.agents.base import BaseAgent
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult
from core.contracts.budget_schema import Budget, BudgetState
from core.contracts.context_pack_schema import ContextPack, EvidenceItem
from core.contracts.critic_schema import CriticFailure, CriticOutput, CriticResult
from core.contracts.reasoning_ladder_schema import ReasoningLadderOutput
from core.governance.budgeting import consume_budget, should_escalate_to_hitl, emit_hitl_escalation_event
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
    budget: Optional[Budget] = None,
    budget_state: Optional[BudgetState] = None,
) -> CriticResult:
    """Run the bounded critic evaluator.
    
    The critic analyzes reasoning output and evidence to produce structured
    quality signals. It cannot call tools directly - only recommend actions
    that are gated by governance.
    
    Args:
        context_pack: The context pack with evidence index.
        evidence: List of evidence items to evaluate.
        reasoning: The reasoning ladder output to critique.
        question: The original question.
        llm_reasoner: Callable to invoke the LLM for critique.
        trace: Optional trace emitter for events.
        budget: Optional budget for tracking cost.
        budget_state: Optional budget state to update.
        
    Returns:
        CriticResult with output or error.
    """
    # Track budget consumption for critic pass
    if budget is not None and budget_state is not None:
        allowed, action, updated = consume_budget(
            budget=budget,
            state=budget_state,
            kind="pass",
            amount=1,
            cost_units=1,
        )
        # Update state in place
        budget_state.passes_used = updated.passes_used
        budget_state.cost_units_used = updated.cost_units_used
        budget_state.violations = updated.violations
        
        _emit(trace, "budget_consumed", {
            "kind": "critic_pass",
            "state": updated.model_dump(mode="json"),
        })
        
        if not allowed:
            _emit(trace, "budget_exceeded", {
                "kind": "critic_pass",
                "action_taken": action,
                "violations": updated.violations,
            })
            if should_escalate_to_hitl(action):
                emit_hitl_escalation_event(
                    trace,
                    reason="critic_budget_exceeded",
                    context={"violations": updated.violations},
                )
            return CriticResult(
                ok=False,
                error=CriticFailure(
                    reason="budget_exceeded",
                    details={"action": action, "violations": updated.violations},
                ),
            )
    
    payload = {
        "question": question,
        "context_pack": context_pack.model_dump(mode="json"),
        "evidence_ids": [item.id for item in evidence],
        "reasoning": reasoning.model_dump(mode="json"),
    }
    _emit(trace, "critic_evaluator_started", {
        "evidence_count": len(evidence),
        "question_len": len(question or ""),
        "reasoning_confidence": reasoning.confidence,
    })
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
                "inconsistency_count": len(output.inconsistency_flags),
                "missing_evidence_count": len(output.missing_evidence_requests),
            },
        )
        return CriticResult(ok=True, output=output)
    except Exception as exc:
        _emit(trace, "critic_evaluator_failed", {"reason": "validation_failed", "error": str(exc)})
        return CriticResult(ok=False, error=CriticFailure(reason="validation_failed", details={"error": str(exc)}))


def evaluate_with_governance(
    *,
    context_pack: ContextPack,
    evidence: List[EvidenceItem],
    reasoning: ReasoningLadderOutput,
    question: str,
    llm_reasoner: CriticReasoner,
    trace: Optional[TraceEmitter] = None,
    budget: Optional[Budget] = None,
    budget_state: Optional[BudgetState] = None,
    allow_fetch_more_evidence: bool = True,
    evidence_budget: int = 3,
) -> CriticResult:
    """Run critic evaluation with built-in governance gating.
    
    This is a convenience wrapper that runs the critic and applies
    governance rules to the output. Blocked recommendations are
    downgraded to NONE.
    
    Args:
        context_pack: The context pack with evidence index.
        evidence: List of evidence items to evaluate.
        reasoning: The reasoning ladder output to critique.
        question: The original question.
        llm_reasoner: Callable to invoke the LLM for critique.
        trace: Optional trace emitter for events.
        budget: Optional budget for tracking cost.
        budget_state: Optional budget state to update.
        allow_fetch_more_evidence: Whether FETCH_MORE_EVIDENCE is allowed.
        evidence_budget: Max evidence fetches allowed.
        
    Returns:
        CriticResult with potentially modified output.
    """
    result = run_critic_evaluator(
        context_pack=context_pack,
        evidence=evidence,
        reasoning=reasoning,
        question=question,
        llm_reasoner=llm_reasoner,
        trace=trace,
        budget=budget,
        budget_state=budget_state,
    )
    
    if not result.ok or result.output is None:
        return result
    
    output = result.output
    
    # Apply governance: block FETCH_MORE_EVIDENCE if not allowed or budget exhausted
    if output.recommended_next_action == "FETCH_MORE_EVIDENCE":
        if not allow_fetch_more_evidence or evidence_budget <= 0:
            _emit(trace, "critic_recommendation_blocked", {
                "requested": "FETCH_MORE_EVIDENCE",
                "reason": "governance_policy" if not allow_fetch_more_evidence else "evidence_budget_exhausted",
            })
            # Create new output with NONE action
            gated_output = output.model_copy(update={"recommended_next_action": "NONE"})
            return CriticResult(ok=True, output=gated_output)
    
    return result


class CriticEvaluatorAgent(BaseAgent):
    """Bounded critic agent that returns structured review signals.
    
    The critic evaluates reasoning outputs without calling tools.
    It produces structured recommendations that are gated by governance.
    """
    
    name: str = "critic_evaluator"
    description: str = "Bounded critic agent that returns structured review signals."

    def __init__(
        self,
        *,
        llm_reasoner: Optional[CriticReasoner] = None,
        trace: Optional[TraceEmitter] = None,
        budget: Optional[Budget] = None,
        budget_state: Optional[BudgetState] = None,
    ) -> None:
        super().__init__(config=None)
        self._llm_reasoner = llm_reasoner
        self._trace = trace
        self._budget = budget
        self._budget_state = budget_state

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
            budget=self._budget,
            budget_state=self._budget_state,
        )
        if not result.ok or result.output is None:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=result.error.reason if result.error else "critic_failed")
            return AgentResult(ok=False, data=None, error=err, meta=meta)
        return AgentResult(ok=True, data=result.output.model_dump(mode="json"), error=None, meta=meta)


def _emit(trace: Optional[TraceEmitter], event_type: str, payload: Dict[str, Any]) -> None:
    if trace is None:
        return
    trace(event_type, payload)
