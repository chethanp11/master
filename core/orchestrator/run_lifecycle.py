"""
Run Lifecycle Management

This module encapsulates run lifecycle operations:
- Run initialization (start_run)
- Run completion (complete_run)
- Run failure (fail_run)
- Status transitions and persistence

Internal module - only imported by engine.py
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from core.contracts.flow_schema import FlowDef, StepDef
from core.contracts.run_schema import (
    AbortedArtifact,
    AbortSource,
    CancelledArtifact,
    CompletedArtifact,
    FailedArtifact,
    OutcomeReason,
    PausedIndefiniteArtifact,
    RunRecord,
    RunStatus,
    StepRecord,
    StepStatus,
    TerminalOutcome,
    Versions,
)
from core.memory.router import MemoryRouter
from core.orchestrator.context import RunContext
from core.orchestrator.state import is_valid_run_transition, to_run_state


def transition_run_status(
    *,
    memory: MemoryRouter,
    emit_event_fn,
    run_id: str,
    product: str,
    flow: str,
    current_status: Union[RunStatus, str],
    target_status: Union[RunStatus, str],
    step_id: Optional[str],
    summary: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
) -> RunStatus:
    """
    Transition run from one status to another.
    
    Validates transition, emits trace event, and persists to memory.
    
    Args:
        memory: Memory router for persistence
        emit_event_fn: Callback to emit trace events
        run_id: Run ID
        product: Product name
        flow: Flow name
        current_status: Current run status
        target_status: Target run status
        step_id: Step ID (if step-specific)
        summary: Updated summary metadata
        reason: Reason for transition (for tracing)
        
    Returns:
        Normalized target status
        
    Raises:
        ValueError: If transition is invalid
    """
    current = _coerce_run_status(current_status)
    target = _coerce_run_status(target_status)
    
    if not is_valid_run_transition(current, target):
        raise ValueError(
            f"Invalid run transition: {to_run_state(current).value} -> {to_run_state(target).value}"
        )
    
    if current != target:
        emit_event_fn(
            kind="run_state_transition",
            run_id=run_id,
            step_id=step_id,
            product=product,
            flow=flow,
            payload={
                "from": to_run_state(current).value,
                "to": to_run_state(target).value,
                "reason": reason or "",
            },
        )
    
    memory.update_run_status(run_id, target.value, summary=summary)
    return target


def start_run(
    *,
    memory: MemoryRouter,
    flow_def: FlowDef,
    run_ctx: RunContext,
    emit_event_fn,
    platform_version: str = "1.0.0",
    model_versions: Optional[Dict[str, str]] = None,
) -> RunRecord:
    """
    Initialize and start a run.
    
    Creates run record, pre-creates steps, initializes metadata, and emits start event.
    
    Args:
        memory: Memory router
        flow_def: Flow definition
        run_ctx: Run context (with run_id, product, flow, payload)
        emit_event_fn: Callback to emit trace events
        platform_version: Optional platform version (default "1.0.0")
        model_versions: Optional dict of model name → version
        
    Returns:
        Created RunRecord
    """
    # IMP-027: Capture version information for reproducibility
    versions = Versions.capture(
        platform_version=platform_version,
        flow_version=getattr(flow_def, 'version', 'unknown'),
        models=model_versions,
    )
    
    # IMP-028: Compute input hash for reproducibility
    from core.utils.hashing import compute_input_hash
    input_hash = compute_input_hash(run_ctx.payload)
    
    run_record = RunRecord(
        run_id=run_ctx.run_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        status=RunStatus.RUNNING,
        autonomy_level=str(flow_def.autonomy_level.value),
        input=run_ctx.payload,
        versions=versions,
        input_hash=input_hash,
        summary={
            "current_step_index": 0,
            "steps_executed": 0,
            "tool_calls": 0,
            "tokens_used": 0,
            "loops": {},
        },
    )
    
    memory.create_run(run_record)
    _precreate_steps(memory=memory, flow_def=flow_def, run_ctx=run_ctx)
    
    run_ctx.meta.update({"steps_executed": 0, "tool_calls": 0, "tokens_used": 0})
    memory.clear_staging(product=run_ctx.product, clear_input=False, clear_output=True)
    
    emit_event_fn(
        kind="run_started",
        run_id=run_ctx.run_id,
        step_id=None,
        product=run_ctx.product,
        flow=run_ctx.flow,
        payload={"autonomy_level": flow_def.autonomy_level.value},
    )
    
    return run_record


def complete_run(
    *,
    memory: MemoryRouter,
    emit_event_fn,
    run_id: str,
    product: str,
    flow: str,
    current_status: Union[RunStatus, str],
    output: Optional[Dict[str, Any]] = None,
    summary: Optional[Dict[str, Any]] = None,
) -> RunRecord:
    """
    Mark run as completed successfully.
    
    Transitions status, records output, and emits completion event.
    
    Args:
        memory: Memory router
        emit_event_fn: Callback to emit trace events
        run_id: Run ID
        product: Product name
        flow: Flow name
        current_status: Current status before completion
        output: Run output data
        summary: Summary metadata
        
    Returns:
        Updated RunRecord
    """
    transition_run_status(
        memory=memory,
        emit_event_fn=emit_event_fn,
        run_id=run_id,
        product=product,
        flow=flow,
        current_status=current_status,
        target_status=RunStatus.COMPLETED,
        step_id=None,
        summary=summary or {},
        reason="run_completed",
    )
    
    # IMP-029: Compute output hash for reproducibility
    from core.utils.hashing import compute_output_hash
    output_hash = compute_output_hash(output)
    
    if output:
        memory.set_run_output(run_id, output)
    
    # Store output hash
    memory.update_run_status(run_id, RunStatus.COMPLETED.value, summary={"output_hash": output_hash})
    
    # IMP-013: Create completed artifact
    completed_artifact = CompletedArtifact(
        final_output=output or {},
        output_summary=summary.get("output_summary") if summary else None,
        metrics=summary.get("metrics", {}) if summary else {},
    )
    
    # IMP-012: Set terminal outcome and emit event
    # IMP-013: Include terminal artifact (persisted BEFORE finalize)
    _set_terminal_outcome(
        memory=memory,
        emit_event_fn=emit_event_fn,
        run_id=run_id,
        product=product,
        flow=flow,
        terminal_outcome=TerminalOutcome.COMPLETED,
        outcome_reason=OutcomeReason.SUCCESS,
        outcome_explanation="Run completed successfully.",
        terminal_artifact=completed_artifact.model_dump(),
    )
    
    emit_event_fn(
        kind="run_completed",
        run_id=run_id,
        step_id=None,
        product=product,
        flow=flow,
        payload={"output": output or {}, "output_hash": output_hash},
    )
    
    bundle = memory.get_run(run_id)
    assert bundle is not None, f"Run {run_id} not found after completion"
    return bundle.run


def fail_run(
    *,
    memory: MemoryRouter,
    emit_event_fn,
    run_id: str,
    product: str,
    flow: str,
    current_status: Union[RunStatus, str],
    error_code: str,
    error_message: str,
    summary: Optional[Dict[str, Any]] = None,
    stack_trace: Optional[str] = None,
    failed_step_id: Optional[str] = None,
    recovery_attempted: bool = False,
) -> RunRecord:
    """
    Mark run as failed.
    
    Transitions status and emits failure event.
    
    Args:
        memory: Memory router
        emit_event_fn: Callback to emit trace events
        run_id: Run ID
        product: Product name
        flow: Flow name
        current_status: Current status before failure
        error_code: Error classification code
        error_message: Error message
        summary: Summary metadata
        stack_trace: Optional stack trace for debugging (IMP-013)
        failed_step_id: ID of step that caused failure (IMP-013)
        recovery_attempted: Whether recovery was attempted (IMP-013)
        
    Returns:
        Updated RunRecord
    """
    error_summary = dict(summary or {})
    error_summary["error"] = error_message
    error_summary["error_code"] = error_code
    
    transition_run_status(
        memory=memory,
        emit_event_fn=emit_event_fn,
        run_id=run_id,
        product=product,
        flow=flow,
        current_status=current_status,
        target_status=RunStatus.FAILED,
        step_id=None,
        summary=error_summary,
        reason="run_failed",
    )
    
    # IMP-029: Compute output hash for error artifact
    from core.utils.hashing import compute_output_hash
    error_output = {"error_code": error_code, "error_message": error_message}
    output_hash = compute_output_hash(error_output)
    
    # Store output hash
    memory.update_run_status(run_id, RunStatus.FAILED.value, summary={"output_hash": output_hash})
    
    # IMP-012: Determine outcome reason from error code
    outcome_reason = _error_code_to_outcome_reason(error_code)
    
    # IMP-013: Create failed artifact
    failed_artifact = FailedArtifact(
        error_code=error_code,
        error_message=error_message,
        stack_trace=stack_trace,
        failed_step_id=failed_step_id,
        recovery_attempted=recovery_attempted,
    )
    
    # IMP-012: Set terminal outcome and emit event
    # IMP-013: Include terminal artifact (persisted BEFORE finalize)
    _set_terminal_outcome(
        memory=memory,
        emit_event_fn=emit_event_fn,
        run_id=run_id,
        product=product,
        flow=flow,
        terminal_outcome=TerminalOutcome.FAILED,
        outcome_reason=outcome_reason,
        outcome_explanation=error_message,
        terminal_artifact=failed_artifact.model_dump(),
    )
    
    emit_event_fn(
        kind="run_failed",
        run_id=run_id,
        step_id=None,
        product=product,
        flow=flow,
        payload={
            "error_code": error_code,
            "error_message": error_message,
            "output_hash": output_hash,
        },
    )
    
    bundle = memory.get_run(run_id)
    assert bundle is not None, f"Run {run_id} not found after failure"
    return bundle.run


def persist_run_output(
    *,
    memory: MemoryRouter,
    emit_event_fn,
    run_id: str,
) -> None:
    """
    Write final run output to observability storage.
    
    Constructs response payload with status, result, and error information,
    then writes to run response file.
    
    Args:
        memory: Memory router
        emit_event_fn: Callback to emit trace events
        run_id: Run ID
    """
    bundle = memory.get_run(run_id)
    if bundle is None:
        return
    
    run = bundle.run
    status = run.status.value if hasattr(run.status, "value") else str(run.status)
    
    pending_statuses = {
        RunStatus.PENDING_USER_INPUT.value,
        RunStatus.PAUSED_WAITING_FOR_USER.value,
        RunStatus.PENDING_HUMAN.value,
    }
    
    result = run.output if status == RunStatus.COMPLETED.value else None
    if isinstance(result, dict) and "output_files" in result:
        result = {k: v for k, v in result.items() if k != "output_files"}
    
    error = None
    if status == RunStatus.COMPLETED.value and result is None:
        status = RunStatus.FAILED.value
        error = {
            "code": "missing_output",
            "message": "Missing run output",
            "step_id": None,
            "details": {},
        }
    
    if error is None and status != RunStatus.COMPLETED.value and status not in pending_statuses:
        failed = next((s for s in bundle.steps if s.status == StepStatus.FAILED), None)
        if failed:
            if failed.error and isinstance(failed.error, dict):
                error = {
                    "code": "step_failed",
                    "message": failed.error.get("message") or "Step failed.",
                    "step_id": failed.step_id,
                    "details": failed.error,
                }
            else:
                error = {
                    "code": "step_failed",
                    "message": "Step failed.",
                    "step_id": failed.step_id,
                    "details": {},
                }
        elif run.summary:
            error = {
                "code": "run_failed",
                "message": run.summary.get("reason") or run.summary.get("error") or "Run failed.",
                "step_id": None,
                "details": run.summary or {},
            }
    
    response = {
        "response_version": "1.0",
        "run_id": run.run_id,
        "product": run.product,
        "flow": run.flow,
        "status": status,
        "result": result if status != RunStatus.COMPLETED.value else (result or {"kind": "files"}),
        "error": error,
        "finished_at": run.finished_at,
        "finished_at_iso": (
            datetime.fromtimestamp(run.finished_at, tz=timezone.utc).isoformat()
            if run.finished_at
            else None
        ),
    }
    
    output_info = memory.write_run_response(product=run.product, run_id=run.run_id, response=response)
    if output_info:
        emit_event_fn(
            kind="output_written",
            run_id=run.run_id,
            step_id=None,
            product=run.product,
            flow=run.flow,
            payload=output_info,
        )


def init_run_meta(
    run_ctx: RunContext,
    *,
    summary: Optional[Dict[str, Any]] = None,
    steps: Optional[List[StepRecord]] = None,
) -> None:
    """
    Initialize run context metadata from summary or steps.
    
    Populates run_ctx.meta with steps_executed, tool_calls, tokens_used, loops.
    
    Args:
        run_ctx: Run context to initialize
        summary: Summary dict (may contain counters)
        steps: Existing step records (to infer counter values)
    """
    summary = summary or {}
    
    def _as_int(value: Any) -> Optional[int]:
        try:
            return int(value)
        except Exception:
            return None
    
    steps_executed = _as_int(summary.get("steps_executed"))
    if steps_executed is None and steps is not None:
        steps_executed = sum(1 for s in steps if not _is_step_status(s.status, StepStatus.NOT_STARTED))
    
    run_ctx.meta["steps_executed"] = steps_executed or 0
    run_ctx.meta["tool_calls"] = _as_int(summary.get("tool_calls")) or 0
    run_ctx.meta["tokens_used"] = _as_int(summary.get("tokens_used")) or 0
    
    loops = summary.get("loops")
    run_ctx.meta["loops"] = loops if isinstance(loops, dict) else {}


def summary_with_counters(
    run_ctx: RunContext,
    summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Merge run context counters into summary dict.
    
    Args:
        run_ctx: Run context with meta counters
        summary: Base summary dict
        
    Returns:
        Merged summary with step/tool/token counts
    """
    merged = dict(summary or {})
    for key in ("steps_executed", "tool_calls", "tokens_used", "loops"):
        if key in run_ctx.meta:
            merged[key] = run_ctx.meta.get(key)
    return merged


# ============================================================================
# Helper functions (internal to module)
# ============================================================================


def _coerce_run_status(status: Union[RunStatus, str]) -> RunStatus:
    """Convert string or RunStatus to RunStatus enum."""
    if isinstance(status, RunStatus):
        return status
    if isinstance(status, str):
        return RunStatus(status)
    raise TypeError(f"Expected RunStatus or str, got {type(status)}")


def _error_code_to_outcome_reason(error_code: str) -> OutcomeReason:
    """
    Map error code to OutcomeReason enum.
    
    IMP-012: Provides deterministic mapping from error codes to outcome reasons.
    
    Args:
        error_code: Error classification code
        
    Returns:
        Corresponding OutcomeReason enum value
    """
    error_code_lower = error_code.lower()
    if "budget" in error_code_lower:
        return OutcomeReason.BUDGET_EXCEEDED
    if "governance" in error_code_lower or "blocked" in error_code_lower:
        return OutcomeReason.GOVERNANCE_BLOCK
    if "max_iterations" in error_code_lower or "iteration" in error_code_lower:
        return OutcomeReason.MAX_ITERATIONS
    if "validation" in error_code_lower:
        return OutcomeReason.VALIDATION_FAILED
    if "user_abort" in error_code_lower or "cancelled" in error_code_lower:
        return OutcomeReason.USER_ABORT
    return OutcomeReason.UNRECOVERABLE_ERROR


def _set_terminal_outcome(
    *,
    memory: MemoryRouter,
    emit_event_fn,
    run_id: str,
    product: str,
    flow: str,
    terminal_outcome: TerminalOutcome,
    outcome_reason: OutcomeReason,
    outcome_explanation: str,
    terminal_artifact: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Set terminal outcome on run record and emit trace event.
    
    IMP-012 (ORC-TERM-001..005): Every run must end with explicit terminal outcome.
    IMP-013 (ORC-TERM-ART-001..004): Terminal outcomes include typed artifacts.
    
    Args:
        memory: Memory router for persistence
        emit_event_fn: Callback to emit trace events
        run_id: Run ID
        product: Product name
        flow: Flow name
        terminal_outcome: Terminal outcome classification
        outcome_reason: Reason for terminal outcome
        outcome_explanation: Human-readable explanation
        terminal_artifact: Optional serialized artifact for the outcome
    """
    # Persist terminal outcome to run record (IMP-013: artifact persisted BEFORE finalize)
    memory.update_run_terminal_outcome(
        run_id=run_id,
        terminal_outcome=terminal_outcome.value,
        outcome_reason=outcome_reason.value,
        outcome_explanation=outcome_explanation,
        terminal_artifact=terminal_artifact,
    )
    
    # Emit run_terminal_outcome trace event
    payload = {
        "terminal_outcome": terminal_outcome.value,
        "outcome_reason": outcome_reason.value,
        "outcome_explanation": outcome_explanation,
    }
    if terminal_artifact is not None:
        payload["terminal_artifact"] = terminal_artifact
    
    emit_event_fn(
        kind="run_terminal_outcome",
        run_id=run_id,
        step_id=None,
        product=product,
        flow=flow,
        payload=payload,
    )


def _precreate_steps(
    *,
    memory: MemoryRouter,
    flow_def: FlowDef,
    run_ctx: RunContext,
) -> None:
    """Create step records for all steps in flow."""
    for idx, step_def in enumerate(flow_def.steps):
        step_id = step_def.id or f"step_{idx}"
        step_record = StepRecord(
            run_id=run_ctx.run_id,
            step_id=step_id,
            step_index=idx,
            name=step_def.name or step_id,
            type=step_def.type.value,
            status=StepStatus.NOT_STARTED,
            meta={
                "backend": (
                    step_def.backend.value
                    if getattr(step_def.backend, "value", None)
                    else step_def.backend
                ),
                "target": step_def.agent or step_def.tool,
            },
        )
        memory.add_step(step_record)


def _is_step_status(status: Union[StepStatus, str], target: StepStatus) -> bool:
    """Check if step status matches target."""
    if isinstance(status, StepStatus):
        return status == target
    return status == target.value
