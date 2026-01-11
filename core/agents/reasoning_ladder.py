from __future__ import annotations

# ==============================
# Reasoning Ladder Helper
# ==============================
"""
Deterministic multi-pass reasoning helper: interpret -> propose -> select.

Provides bounded multi-pass reasoning with governance:
- interpret: Extract intent, entities, constraints from question
- propose: Generate candidate solutions, tools, agents
- select: Choose best candidate with evidence refs

Budget enforcement ensures deterministic termination and HITL escalation
when limits are exceeded.
"""

import json
from typing import Any, Callable, Dict, List, Optional, Union

from core.contracts.context_pack_schema import ContextPack
from core.contracts.descriptors_schema import AgentDescriptor, ToolDescriptor
from core.contracts.reasoning_ladder_schema import (
    ReasoningLadderConfig,
    ReasoningLadderFailure,
    ReasoningLadderInterpret,
    ReasoningLadderOutput,
    ReasoningLadderPropose,
    ReasoningLadderResult,
    ReasoningLadderSelectPayload,
)
from core.contracts.budget_schema import Budget, BudgetState, ReasoningBudget
from core.governance.budgeting import (
    consume_budget,
    emit_budget_exceeded_event,
    emit_hitl_escalation_event,
    init_reasoning_budget,
    should_escalate_to_hitl,
)

TraceEmitter = Callable[[str, Dict[str, Any]], None]
LadderReasoner = Callable[[str, Dict[str, Any]], Union[Dict[str, Any], str]]


def run_reasoning_ladder(
    *,
    context_pack: ContextPack,
    question: str,
    config: ReasoningLadderConfig,
    llm_reasoner: LadderReasoner,
    trace: Optional[TraceEmitter] = None,
    available_tools: Optional[List[ToolDescriptor]] = None,
    available_agents: Optional[List[AgentDescriptor]] = None,
    budget: Optional[Budget] = None,
    budget_state: Optional[BudgetState] = None,
) -> ReasoningLadderResult:
    if config.max_passes < 3:
        failure = ReasoningLadderFailure(
            reason="max_passes_below_required",
            failed_pass="interpret",
            details={"max_passes": config.max_passes},
        )
        _emit(trace, "reasoning_ladder_pass_failed", {"pass_name": "interpret", "reason": failure.reason})
        return ReasoningLadderResult(ok=False, error=failure)

    interpret = _run_interpret_pass(
        context_pack=context_pack,
        question=question,
        llm_reasoner=llm_reasoner,
        trace=trace,
        available_tools=available_tools,
        available_agents=available_agents,
        budget=budget,
        budget_state=budget_state,
    )
    if isinstance(interpret, ReasoningLadderFailure):
        return ReasoningLadderResult(ok=False, error=interpret)

    propose = _run_propose_pass(
        context_pack=context_pack,
        question=question,
        interpret=interpret,
        llm_reasoner=llm_reasoner,
        trace=trace,
        config=config,
        available_tools=available_tools,
        available_agents=available_agents,
        budget=budget,
        budget_state=budget_state,
    )
    if isinstance(propose, ReasoningLadderFailure):
        return ReasoningLadderResult(ok=False, error=propose)

    select_payload = _run_select_pass(
        context_pack=context_pack,
        question=question,
        interpret=interpret,
        propose=propose,
        llm_reasoner=llm_reasoner,
        trace=trace,
        config=config,
        budget=budget,
        budget_state=budget_state,
    )
    if isinstance(select_payload, ReasoningLadderFailure):
        return ReasoningLadderResult(ok=False, error=select_payload)

    output = ReasoningLadderOutput(
        interpret=interpret,
        propose=propose,
        select=select_payload.select,
        confidence=select_payload.confidence,
        assumptions=select_payload.assumptions,
        unknowns=select_payload.unknowns,
    )
    return ReasoningLadderResult(ok=True, output=output)


def run_bounded_reasoning(
    *,
    context_pack: ContextPack,
    question: str,
    config: ReasoningLadderConfig,
    llm_reasoner: LadderReasoner,
    reasoning_budget: Optional[ReasoningBudget] = None,
    trace: Optional[TraceEmitter] = None,
    available_tools: Optional[List[ToolDescriptor]] = None,
    available_agents: Optional[List[AgentDescriptor]] = None,
) -> ReasoningLadderResult:
    """Run bounded multi-pass reasoning with ReasoningBudget support.
    
    Convenience wrapper around run_reasoning_ladder that:
    - Accepts ReasoningBudget instead of Budget/BudgetState
    - Auto-initializes budget state
    - Emits HITL escalation events when budget exceeded and escalate_on_exceed=True
    
    Args:
        context_pack: Evidence and context for reasoning.
        question: The question to answer.
        config: Reasoning ladder configuration.
        llm_reasoner: Callable to invoke the LLM.
        reasoning_budget: Optional ReasoningBudget config. Uses defaults if None.
        trace: Optional trace emitter for events.
        available_tools: Tools the reasoner can recommend.
        available_agents: Agents the reasoner can recommend.
        
    Returns:
        ReasoningLadderResult with output or error.
    """
    budget, budget_state = init_reasoning_budget(reasoning_budget)
    
    _emit(trace, "bounded_reasoning_started", {
        "max_passes": budget.max_passes,
        "max_tool_calls": budget.max_tool_calls,
        "escalate_on_exceed": reasoning_budget.escalate_on_exceed if reasoning_budget else True,
    })
    
    result = run_reasoning_ladder(
        context_pack=context_pack,
        question=question,
        config=config,
        llm_reasoner=llm_reasoner,
        trace=trace,
        available_tools=available_tools,
        available_agents=available_agents,
        budget=budget,
        budget_state=budget_state,
    )
    
    _emit(trace, "bounded_reasoning_completed", {
        "ok": result.ok,
        "passes_used": budget_state.passes_used,
        "violations": budget_state.violations,
    })
    
    return result


def _run_interpret_pass(
    *,
    context_pack: ContextPack,
    question: str,
    llm_reasoner: LadderReasoner,
    trace: Optional[TraceEmitter],
    available_tools: Optional[List[ToolDescriptor]],
    available_agents: Optional[List[AgentDescriptor]],
    budget: Optional[Budget],
    budget_state: Optional[BudgetState],
) -> Union[ReasoningLadderInterpret, ReasoningLadderFailure]:
    pass_name = "interpret"
    if not _consume_pass_budget(trace, pass_name, budget, budget_state):
        return ReasoningLadderFailure(reason="budget_exceeded", failed_pass=pass_name, details={})
    _emit_start(trace, pass_name, context_pack, question, available_tools, available_agents)
    payload = _call_reasoner(
        llm_reasoner,
        pass_name,
        _build_request(context_pack, question, available_tools, available_agents),
        trace=trace,
    )
    if isinstance(payload, ReasoningLadderFailure):
        return payload
    try:
        result = ReasoningLadderInterpret.model_validate(payload)
        _emit_complete(trace, pass_name, success=True, confidence=None)
        return result
    except Exception as exc:
        return _emit_failure(trace, pass_name, "validation_failed", exc)


def _run_propose_pass(
    *,
    context_pack: ContextPack,
    question: str,
    interpret: ReasoningLadderInterpret,
    llm_reasoner: LadderReasoner,
    trace: Optional[TraceEmitter],
    config: ReasoningLadderConfig,
    available_tools: Optional[List[ToolDescriptor]],
    available_agents: Optional[List[AgentDescriptor]],
    budget: Optional[Budget],
    budget_state: Optional[BudgetState],
) -> Union[ReasoningLadderPropose, ReasoningLadderFailure]:
    pass_name = "propose"
    if not _consume_pass_budget(trace, pass_name, budget, budget_state):
        return ReasoningLadderFailure(reason="budget_exceeded", failed_pass=pass_name, details={})
    _emit_start(trace, pass_name, context_pack, question, available_tools, available_agents)
    payload = _call_reasoner(
        llm_reasoner,
        pass_name,
        _build_request(context_pack, question, available_tools, available_agents, interpret=interpret.model_dump(mode="json")),
        trace=trace,
    )
    if isinstance(payload, ReasoningLadderFailure):
        return payload
    try:
        result = ReasoningLadderPropose.model_validate(payload)
        trimmed = result.model_copy(
            update={
                "candidates": result.candidates[: config.max_candidates],
                "tool_candidates": result.tool_candidates[: config.max_tool_candidates],
                "agent_candidates": result.agent_candidates[: config.max_agent_candidates],
            }
        )
        _emit_complete(trace, pass_name, success=True, confidence=None)
        return trimmed
    except Exception as exc:
        return _emit_failure(trace, pass_name, "validation_failed", exc)


def _run_select_pass(
    *,
    context_pack: ContextPack,
    question: str,
    interpret: ReasoningLadderInterpret,
    propose: ReasoningLadderPropose,
    llm_reasoner: LadderReasoner,
    trace: Optional[TraceEmitter],
    config: ReasoningLadderConfig,
    budget: Optional[Budget],
    budget_state: Optional[BudgetState],
) -> Union[ReasoningLadderSelectPayload, ReasoningLadderFailure]:
    pass_name = "select"
    if not _consume_pass_budget(trace, pass_name, budget, budget_state):
        return ReasoningLadderFailure(reason="budget_exceeded", failed_pass=pass_name, details={})
    _emit_start(trace, pass_name, context_pack, question, None, None)
    payload = _call_reasoner(
        llm_reasoner,
        pass_name,
        _build_request(
            context_pack,
            question,
            None,
            None,
            interpret=interpret.model_dump(mode="json"),
            propose=propose.model_dump(mode="json"),
        ),
        trace=trace,
    )
    if isinstance(payload, ReasoningLadderFailure):
        return payload
    try:
        result = ReasoningLadderSelectPayload.model_validate(payload)
        if config.min_confidence_to_select is not None and result.confidence < config.min_confidence_to_select:
            return _emit_failure(trace, pass_name, "confidence_below_threshold", None)
        _emit_complete(trace, pass_name, success=True, confidence=result.confidence)
        return result
    except Exception as exc:
        return _emit_failure(trace, pass_name, "validation_failed", exc)


def _build_request(
    context_pack: ContextPack,
    question: str,
    available_tools: Optional[List[ToolDescriptor]],
    available_agents: Optional[List[AgentDescriptor]],
    *,
    interpret: Optional[Dict[str, Any]] = None,
    propose: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "question": question,
        "context_pack": context_pack.model_dump(mode="json"),
        "available_tools": [tool.model_dump(mode="json") for tool in available_tools or []],
        "available_agents": [agent.model_dump(mode="json") for agent in available_agents or []],
    }
    if interpret is not None:
        payload["interpret"] = interpret
    if propose is not None:
        payload["propose"] = propose
    return payload


def _call_reasoner(
    llm_reasoner: LadderReasoner,
    pass_name: str,
    payload: Dict[str, Any],
    *,
    trace: Optional[TraceEmitter],
) -> Union[Dict[str, Any], ReasoningLadderFailure]:
    try:
        raw = llm_reasoner(pass_name, payload)
        if isinstance(raw, dict) and "output" in raw:
            model_call_id = raw.get("model_call_id")
            if model_call_id:
                _emit(trace, "reasoning_ladder_model_linked", {"pass_name": pass_name, "model_call_id": model_call_id})
            raw = raw.get("output")
        if isinstance(raw, str):
            data = json.loads(raw)
        elif isinstance(raw, dict):
            data = raw
        else:
            data = {"value": raw}
        return data
    except Exception as exc:
        return _emit_failure(trace, pass_name, "reasoner_call_failed", exc)


def _emit_start(
    trace: Optional[TraceEmitter],
    pass_name: str,
    context_pack: ContextPack,
    question: str,
    available_tools: Optional[List[ToolDescriptor]],
    available_agents: Optional[List[AgentDescriptor]],
) -> None:
    payload = {
        "pass_name": pass_name,
        "question_len": len(question or ""),
        "evidence_count": len(context_pack.evidence_index),
        "available_tools": len(available_tools or []),
        "available_agents": len(available_agents or []),
    }
    _emit(trace, "reasoning_ladder_pass_started", payload)


def _emit_complete(
    trace: Optional[TraceEmitter],
    pass_name: str,
    *,
    success: bool,
    confidence: Optional[float],
) -> None:
    payload = {"pass_name": pass_name, "success": success, "confidence": confidence}
    _emit(trace, "reasoning_ladder_pass_completed", payload)


def _emit_failure(
    trace: Optional[TraceEmitter],
    pass_name: str,
    reason: str,
    exc: Optional[Exception],
) -> ReasoningLadderFailure:
    details = {"error": str(exc)} if exc else {}
    _emit(trace, "reasoning_ladder_pass_failed", {"pass_name": pass_name, "reason": reason})
    return ReasoningLadderFailure(reason=reason, failed_pass=pass_name, details=details)


def _emit(trace: Optional[TraceEmitter], event_type: str, payload: Dict[str, Any]) -> None:
    if trace is None:
        return
    trace(event_type, payload)


def _consume_pass_budget(
    trace: Optional[TraceEmitter],
    pass_name: str,
    budget: Optional[Budget],
    budget_state: Optional[BudgetState],
) -> bool:
    """Consume budget for a reasoning pass with HITL escalation support.
    
    Args:
        trace: Optional trace emitter for events.
        pass_name: Name of the current pass (interpret, propose, select).
        budget: Budget limits.
        budget_state: Current budget state (mutated in place).
        
    Returns:
        True if pass is allowed, False if budget exceeded.
    """
    if budget is None or budget_state is None:
        return True
    allowed, action, updated = consume_budget(budget=budget, state=budget_state, kind="pass", amount=1, cost_units=1)
    # Update state in place
    budget_state.passes_used = updated.passes_used
    budget_state.tool_calls_used = updated.tool_calls_used
    budget_state.parallel_calls_used = updated.parallel_calls_used
    budget_state.cost_units_used = updated.cost_units_used
    budget_state.latency_bucket_observed = updated.latency_bucket_observed
    budget_state.violations = updated.violations
    
    _emit(trace, "budget_consumed", {
        "kind": "pass",
        "pass_name": pass_name,
        "state": updated.model_dump(mode="json"),
    })
    
    if not allowed:
        emit_budget_exceeded_event(
            trace,
            kind="pass",
            budget=budget,
            state=updated,
            action=action,
        )
        # Trigger HITL escalation if configured
        if should_escalate_to_hitl(action):
            emit_hitl_escalation_event(
                trace,
                reason="budget_exceeded",
                context={
                    "pass_name": pass_name,
                    "passes_used": updated.passes_used,
                    "max_passes": budget.max_passes,
                    "violations": updated.violations,
                },
            )
    return allowed
