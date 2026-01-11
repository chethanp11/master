"""
Loop Executor Module

This module handles repeat_until loop execution:
- Loop state management
- Stop condition evaluation
- Iteration step execution
- Budget enforcement within loops

Internal module - only imported by engine.py
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, Union, TYPE_CHECKING

from core.contracts.budget_schema import Budget
from core.contracts.interaction_schema import HitlRequest
from core.contracts.flow_schema import LoopState
from core.contracts.run_schema import (
    RunStatus,
    StepRecord,
    StepStatus,
)
from core.governance.budgeting import consume_budget
from core.memory.router import MemoryRouter
from core.orchestrator.context import RunContext
from core.orchestrator.looping import evaluate_stop_condition, summarize_stop_condition

if TYPE_CHECKING:
    from core.contracts.flow_schema import FlowDef, StepDef
    from core.orchestrator.hitl import HitlService


# ============================================================================
# Loop State Management
# ============================================================================


def get_or_create_loop_state(
    run_ctx: RunContext,
    step_id: str,
) -> LoopState:
    """
    Get existing loop state or create a new one.

    Args:
        run_ctx: Run context
        step_id: Step ID for the loop

    Returns:
        LoopState for this loop step
    """
    loops = run_ctx.meta.setdefault("loops", {})
    raw_state = loops.get(step_id) if isinstance(loops, dict) else None

    if isinstance(raw_state, dict):
        loop_state = LoopState.model_validate(raw_state)
    else:
        loop_state = LoopState()

    if loop_state.started_at is None:
        loop_state.started_at = int(time.time())

    return loop_state


def save_loop_state(
    run_ctx: RunContext,
    step_id: str,
    loop_state: LoopState,
) -> None:
    """
    Save loop state to run context.

    Args:
        run_ctx: Run context
        step_id: Step ID for the loop
        loop_state: Loop state to save
    """
    loops = run_ctx.meta.setdefault("loops", {})
    loops[step_id] = loop_state.model_dump(mode="json")
    run_ctx.meta["loops"] = loops


# ============================================================================
# Loop Budget Handling
# ============================================================================


def check_loop_budget(
    *,
    run_ctx: RunContext,
    step_id: str,
    loop_state: LoopState,
    emit_event_fn: Callable[..., None],
) -> tuple[bool, Optional[str]]:
    """
    Check and consume loop budget.

    Args:
        run_ctx: Run context
        step_id: Step ID
        loop_state: Current loop state
        emit_event_fn: Function to emit events

    Returns:
        Tuple of (allowed, action_if_exceeded)
    """
    budget = run_ctx.meta.get("budget")
    budget_state = run_ctx.meta.get("budget_state")

    if not isinstance(budget, Budget) or budget_state is None:
        return True, None

    allowed, action, updated = consume_budget(
        budget=budget,
        state=budget_state,
        kind="pass",
        amount=1,
        cost_units=1,
    )
    run_ctx.meta["budget_state"] = updated

    emit_event_fn(
        kind="budget_consumed",
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        payload={"kind": "pass", "state": updated.model_dump(mode="json")},
    )

    if not allowed:
        emit_event_fn(
            kind="budget_exceeded",
            run_id=run_ctx.run_id,
            step_id=step_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={
                "kind": "pass",
                "limit": budget.max_passes,
                "state": updated.model_dump(mode="json"),
                "action_taken": action,
            },
        )

    return allowed, action


def handle_budget_exceeded_hitl(
    *,
    run_ctx: RunContext,
    step_id: str,
    step_record: StepRecord,
    current_index: int,
    loop_state: LoopState,
    requested_by: Optional[str],
    memory: MemoryRouter,
    hitl: "HitlService",
    emit_event_fn: Callable[..., None],
    transition_run_status_fn: Callable[..., None],
    summary_with_counters_fn: Callable[..., Dict[str, Any]],
    persist_run_output_fn: Callable[..., None],
) -> str:
    """
    Handle budget exceeded with HITL escalation.

    Args:
        run_ctx: Run context
        step_id: Step ID
        step_record: Step record
        current_index: Current step index
        loop_state: Loop state
        requested_by: User who requested the run
        memory: Memory router
        hitl: HITL service
        emit_event_fn: Function to emit events
        transition_run_status_fn: Function to transition run status
        summary_with_counters_fn: Function to build summary with counters
        persist_run_output_fn: Function to persist run output

    Returns:
        RunStatus.PENDING_HUMAN value
    """
    loop_state.terminated = True
    loop_state.termination_reason = "BUDGET_EXCEEDED"
    loop_state.ended_at = int(time.time())
    save_loop_state(run_ctx, step_id, loop_state)

    emit_event_fn(
        kind="loop_terminated",
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        payload={
            "loop_step_id": step_id,
            "termination_reason": loop_state.termination_reason,
            "iters_used": loop_state.iters_used,
            "stop_condition_met": False,
        },
    )

    approval_payload = {"reason": "budget_exceeded", "loop_step_id": step_id}
    approval = hitl.create_approval(
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        requested_by=requested_by,
        payload=approval_payload,
    )
    hitl_request = HitlRequest(
        request_id=approval.approval_id,
        request_type="APPROVAL",
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        created_at=int(time.time()),
        payload={"approval_context": approval_payload},
    )
    memory.update_step(
        run_ctx.run_id,
        step_id,
        {
            "status": StepStatus.PENDING_HUMAN.value,
            "output": {
                "approval_id": approval.approval_id,
                "hitl_request": hitl_request.model_dump(mode="json"),
            },
        },
    )
    transition_run_status_fn(
        run_id=run_ctx.run_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        current_status=RunStatus.RUNNING,
        target_status=RunStatus.PENDING_HUMAN,
        step_id=step_id,
        summary=summary_with_counters_fn(run_ctx, {"current_step_index": current_index}),
        reason="loop_budget_exceeded",
    )
    emit_event_fn(
        kind="run_pending_human",
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        payload={"reason": "loop_budget_exceeded", "approval_id": approval.approval_id},
    )
    persist_run_output_fn(run_ctx)
    return RunStatus.PENDING_HUMAN.value


# ============================================================================
# Loop Execution
# ============================================================================


def handle_repeat_until(
    *,
    flow_def: "FlowDef",
    run_ctx: RunContext,
    step_def: "StepDef",
    step_id: str,
    step_record: StepRecord,
    requested_by: Optional[str],
    current_index: int,
    memory: MemoryRouter,
    hitl: "HitlService",
    fail_step_fn: Callable[..., str],
    emit_event_fn: Callable[..., None],
    transition_run_status_fn: Callable[..., None],
    summary_with_counters_fn: Callable[..., Dict[str, Any]],
    persist_run_output_fn: Callable[..., None],
    find_step_def_fn: Callable[..., Optional["StepDef"]],
    find_step_index_fn: Callable[..., int],
    execute_iteration_step_fn: Callable[..., Optional[str]],
) -> Union[str, int]:
    """
    Handle a REPEAT_UNTIL step.

    This step repeatedly executes an iteration step until a stop condition is met.

    Args:
        flow_def: Flow definition
        run_ctx: Run context
        step_def: Step definition
        step_id: Step ID
        step_record: Step record
        requested_by: User who requested the run
        current_index: Current step index
        memory: Memory router
        hitl: HITL service
        fail_step_fn: Function to call when step fails
        emit_event_fn: Function to emit events
        transition_run_status_fn: Function to transition run status
        summary_with_counters_fn: Function to build summary with counters
        persist_run_output_fn: Function to persist run output
        find_step_def_fn: Function to find step definition by ID
        find_step_index_fn: Function to find step index by ID
        execute_iteration_step_fn: Function to execute an iteration step

    Returns:
        Next step index, or status string on failure/pause
    """
    # Validate configuration
    if step_def.stop_condition is None or step_def.iteration_step is None:
        return fail_step_fn(
            run_ctx=run_ctx,
            step_id=step_id,
            reason="repeat_until_missing_config",
            message="repeat_until missing stop_condition or iteration_step",
        )

    # Get or create loop state
    loop_state = get_or_create_loop_state(run_ctx, step_id)

    # Find iteration step
    iteration_def = find_step_def_fn(flow_def, step_def.iteration_step)
    if iteration_def is None:
        return fail_step_fn(
            run_ctx=run_ctx,
            step_id=step_id,
            reason="repeat_until_missing_iteration_step",
            message="iteration_step not found",
        )
    iteration_index = find_step_index_fn(flow_def, step_def.iteration_step)

    # Emit loop started event on first iteration
    if loop_state.iters_used == 0 and not loop_state.terminated:
        emit_event_fn(
            kind="loop_started",
            run_id=run_ctx.run_id,
            step_id=step_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"loop_step_id": step_id, "max_iters": step_def.max_iters},
        )

    # Main loop
    while True:
        # Check stop condition
        stop_summary = summarize_stop_condition(step_def.stop_condition)
        stop_met = evaluate_stop_condition(step_def.stop_condition, run_ctx=run_ctx, memory=memory)
        loop_state.last_evaluated_condition = {"summary": stop_summary, "result": stop_met}

        if stop_met:
            loop_state.terminated = True
            loop_state.termination_reason = "STOP_CONDITION_MET"
            break

        if loop_state.iters_used >= int(step_def.max_iters or 0):
            loop_state.terminated = True
            loop_state.termination_reason = "MAX_ITERS_REACHED"
            break

        # Check budget
        allowed, action = check_loop_budget(
            run_ctx=run_ctx,
            step_id=step_id,
            loop_state=loop_state,
            emit_event_fn=emit_event_fn,
        )

        if not allowed:
            loop_state.terminated = True
            loop_state.termination_reason = "BUDGET_EXCEEDED"
            loop_state.ended_at = int(time.time())
            save_loop_state(run_ctx, step_id, loop_state)

            emit_event_fn(
                kind="loop_terminated",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={
                    "loop_step_id": step_id,
                    "termination_reason": loop_state.termination_reason,
                    "iters_used": loop_state.iters_used,
                    "stop_condition_met": False,
                },
            )

            if action == "HITL":
                return handle_budget_exceeded_hitl(
                    run_ctx=run_ctx,
                    step_id=step_id,
                    step_record=step_record,
                    current_index=current_index,
                    loop_state=loop_state,
                    requested_by=requested_by,
                    memory=memory,
                    hitl=hitl,
                    emit_event_fn=emit_event_fn,
                    transition_run_status_fn=transition_run_status_fn,
                    summary_with_counters_fn=summary_with_counters_fn,
                    persist_run_output_fn=persist_run_output_fn,
                )

            return fail_step_fn(
                run_ctx=run_ctx,
                step_id=step_id,
                reason="budget_exceeded",
                message="loop budget exceeded",
            )

        # Execute iteration
        emit_event_fn(
            kind="loop_iteration_started",
            run_id=run_ctx.run_id,
            step_id=step_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"loop_step_id": step_id, "iter_index": loop_state.iters_used},
        )

        iteration_result = execute_iteration_step_fn(
            flow_def=flow_def,
            run_ctx=run_ctx,
            step_def=iteration_def,
            step_index=iteration_index,
            requested_by=requested_by,
        )

        if iteration_result is not None:
            save_loop_state(run_ctx, step_id, loop_state)
            return iteration_result

        loop_state.iters_used += 1

        emit_event_fn(
            kind="loop_iteration_completed",
            run_id=run_ctx.run_id,
            step_id=step_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"loop_step_id": step_id, "iter_index": loop_state.iters_used - 1},
        )

    # Loop terminated normally
    loop_state.ended_at = int(time.time())
    save_loop_state(run_ctx, step_id, loop_state)

    memory.update_step(
        run_ctx.run_id,
        step_id,
        {
            "status": StepStatus.COMPLETED.value,
            "finished_at": int(time.time()),
            "output": {"loop_state": loop_state.model_dump(mode="json")},
        },
    )

    emit_event_fn(
        kind="loop_terminated",
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        payload={
            "loop_step_id": step_id,
            "termination_reason": loop_state.termination_reason,
            "iters_used": loop_state.iters_used,
            "stop_condition_met": loop_state.termination_reason == "STOP_CONDITION_MET",
        },
    )

    memory.update_run_status(
        run_ctx.run_id,
        RunStatus.RUNNING.value,
        summary=summary_with_counters_fn(run_ctx, {"current_step_index": current_index + 1}),
    )

    # Determine next step
    next_index = current_index + 1
    if step_def.on_terminate:
        next_index = find_step_index_fn(flow_def, step_def.on_terminate)

    if next_index == iteration_index:
        next_index = iteration_index + 1

    if next_index <= current_index:
        return fail_step_fn(
            run_ctx=run_ctx,
            step_id=step_id,
            reason="repeat_until_invalid_target",
            message="repeat_until target must be a later step",
        )

    return next_index
