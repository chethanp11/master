# ==============================
# Step Executor
# ==============================
"""
Execute a single flow step.

This module is pure execution orchestration:
- No direct persistence (uses injected memory backend via engine)
- No direct tool calls (delegates to injected tool runner)
- No direct model calls (delegates to injected agent runner)

Supported in v1:
- agent steps -> agent_runner(agent_name, step_ctx) -> envelope-like dict
- tool steps  -> tool_runner(tool_name, step_ctx)  -> envelope-like dict
- human_approval steps -> handled by hitl module (engine coordinates)
- subflow steps -> optional subflow_runner(subflow_id, step_ctx)

The runners are injected callables so products can plug in without touching core logic.
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

from core.contracts.flow_schema import StepType
from core.contracts.run_schema import StepRecord
from core.orchestrator.context import StepContext
from core.orchestrator.error_policy import evaluate_retry
from core.orchestrator.state import StepStatus

# ==============================
# Callable Types
# ==============================
AgentRunner = Callable[[str, StepContext], Dict[str, Any]]
ToolRunner = Callable[[str, StepContext], Dict[str, Any]]
SubflowRunner = Callable[[str, StepContext], Dict[str, Any]]

# ==============================
# Public API
# ==============================
def execute_step(
    *,
    step_ctx: StepContext,
    agent_runner: Optional[AgentRunner],
    tool_runner: Optional[ToolRunner],
    subflow_runner: Optional[SubflowRunner] = None,
) -> Tuple[StepRecord, Optional[Dict[str, Any]]]:
    """
    Execute a step and return (StepRecord, output_payload).

    output_payload is a sanitized dict representation of the runner result that the engine can
    later store as an artifact via memory backend (v1 keeps it in run.meta by default).
    """
    step = step_ctx.step
    step_rec = StepRecord(
        run_id=step_ctx.run.run_id,
        step_id=step.id,
        status=StepStatus.NOT_STARTED,
        started_at=None,
        ended_at=None,
        attempt=0,
        error=None,
        input_ref=None,
        output_ref=None,
        meta={},
    )

    # ==============================
    # Dispatch
    # ==============================
    if step.type == StepType.AGENT:
        if agent_runner is None:
            return _fail(step_ctx, step_rec, "agent_runner_missing"), None
        if not step.agent:
            return _fail(step_ctx, step_rec, "agent_name_missing"), None
        return _execute_with_retry(step_ctx, step_rec, lambda: agent_runner(step.agent, step_ctx))

    if step.type == StepType.TOOL:
        if tool_runner is None:
            return _fail(step_ctx, step_rec, "tool_runner_missing"), None
        if not step.tool:
            return _fail(step_ctx, step_rec, "tool_name_missing"), None
        return _execute_with_retry(step_ctx, step_rec, lambda: tool_runner(step.tool, step_ctx))

    if step.type == StepType.SUBFLOW:
        if subflow_runner is None:
            return _fail(step_ctx, step_rec, "subflow_runner_missing"), None
        if not step.subflow:
            return _fail(step_ctx, step_rec, "subflow_id_missing"), None
        return _execute_with_retry(step_ctx, step_rec, lambda: subflow_runner(step.subflow, step_ctx))

    if step.type == StepType.HUMAN_APPROVAL:
        return _fail(step_ctx, step_rec, "human_approval_handled_by_engine"), None

    return _fail(step_ctx, step_rec, "unsupported_step_type"), None


# ==============================
# Retry Wrapper
# ==============================
def _execute_with_retry(
    step_ctx: StepContext,
    step_rec: StepRecord,
    runner_call: Callable[[], Dict[str, Any]],
) -> Tuple[StepRecord, Optional[Dict[str, Any]]]:
    """
    Execute runner_call with retry policy from step definition.
    Runner is expected to return an envelope-like dict:
      { ok: bool, data: ..., error: { code: ..., message: ... } }
    """
    step = step_ctx.step
    step_rec.started_at = datetime.utcnow()

    attempt = 0
    while True:
        attempt += 1
        step_ctx.attempt = attempt
        step_rec.attempt = attempt
        step_rec.status = StepStatus.RUNNING

        step_ctx.emit("step_attempt_started", {"attempt": attempt})

        result = runner_call()
        ok = bool(result.get("ok", False))
        if ok:
            step_rec.status = StepStatus.COMPLETED
            step_rec.ended_at = datetime.utcnow()
            step_ctx.emit("step_completed", {"attempt": attempt})
            return step_rec, _sanitize_result(result)

        err = result.get("error") or {}
        code = err.get("code")
        msg = err.get("message") or "step_failed"
        step_rec.error = {"code": code, "message": msg}
        step_ctx.emit("step_failed", {"attempt": attempt, "error": step_rec.error})

        decision = evaluate_retry(
            attempt_index=attempt,
            retry_policy=step.retry,
            error_code=str(code) if code is not None else None,
        )
        if not decision.should_retry:
            step_rec.status = StepStatus.FAILED
            step_rec.ended_at = datetime.utcnow()
            step_ctx.emit("step_failed_terminal", {"attempt": attempt, "reason": decision.reason})
            return step_rec, _sanitize_result(result)

        step_ctx.emit(
            "step_retry_scheduled",
            {"attempt": attempt, "reason": decision.reason, "backoff_seconds": decision.next_backoff_seconds},
        )


# ==============================
# Helpers
# ==============================
def _fail(step_ctx: StepContext, step_rec: StepRecord, message: str) -> StepRecord:
    step_rec.status = StepStatus.FAILED
    step_rec.started_at = step_rec.started_at or datetime.utcnow()
    step_rec.ended_at = datetime.utcnow()
    step_rec.error = {"code": "executor_error", "message": message}
    step_ctx.emit("step_executor_error", {"error": step_rec.error})
    return step_rec


def _sanitize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "ok": bool(result.get("ok", False)),
        "meta": result.get("meta", {}) if isinstance(result.get("meta", {}), dict) else {},
    }
    if out["ok"]:
        out["data"] = result.get("data")
    else:
        out["error"] = result.get("error") if isinstance(result.get("error"), dict) else {"message": "unknown_error"}
    return out