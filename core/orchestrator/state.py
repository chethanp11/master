# ==============================
# Orchestrator State
# ==============================
"""
Orchestrator state enums and helpers.

These are the canonical runtime statuses used by the orchestrator.
They intentionally reuse the platform contracts from core/contracts/run_schema.py.

Intended usage:
- Orchestrator sets RunStatus / StepStatus on RunRecord / StepRecord
- Gateway/UI reads these statuses for run tracking and approvals
"""

from __future__ import annotations


# ==============================
# Imports
# ==============================

from enum import Enum
from typing import FrozenSet, Union

from core.contracts.run_schema import RunStatus as RunStatus  # re-export
from core.contracts.run_schema import StepStatus as StepStatus  # re-export

# ==============================
# Status Groups
# ==============================
RUN_TERMINAL: FrozenSet[RunStatus] = frozenset(
    {
        RunStatus.COMPLETED,
        RunStatus.FAILED,
        RunStatus.CANCELLED,
    }
)

RUN_ACTIVE: FrozenSet[RunStatus] = frozenset(
    {
        RunStatus.RUNNING,
        RunStatus.PENDING_HUMAN,
        RunStatus.PENDING_USER_INPUT,
        RunStatus.PAUSED_WAITING_FOR_USER,
    }
)

STEP_TERMINAL: FrozenSet[StepStatus] = frozenset(
    {
        StepStatus.COMPLETED,
        StepStatus.FAILED,
        StepStatus.SKIPPED,
    }
)

STEP_ACTIVE: FrozenSet[StepStatus] = frozenset(
    {
        StepStatus.RUNNING,
        StepStatus.PENDING_HUMAN,
        StepStatus.PENDING_USER_INPUT,
        StepStatus.PAUSED_WAITING_FOR_USER,
    }
)


class RunState(str, Enum):
    """Finite-state machine states for deterministic runs."""

    RUNNING = "RUNNING"
    PENDING_USER_INPUT = "PENDING_USER_INPUT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


_RUN_STATUS_TO_STATE = {
    RunStatus.RUNNING: RunState.RUNNING,
    RunStatus.PENDING_USER_INPUT: RunState.PENDING_USER_INPUT,
    RunStatus.PAUSED_WAITING_FOR_USER: RunState.PENDING_USER_INPUT,
    RunStatus.PENDING_HUMAN: RunState.PENDING_APPROVAL,
    RunStatus.FAILED: RunState.FAILED,
    RunStatus.COMPLETED: RunState.COMPLETED,
    RunStatus.CANCELLED: RunState.FAILED,
}

_ALLOWED_TRANSITIONS = {
    RunState.RUNNING: {RunState.PENDING_USER_INPUT, RunState.PENDING_APPROVAL, RunState.FAILED, RunState.COMPLETED},
    RunState.PENDING_USER_INPUT: {RunState.RUNNING, RunState.FAILED},
    RunState.PENDING_APPROVAL: {RunState.RUNNING, RunState.FAILED},
    RunState.FAILED: set(),
    RunState.COMPLETED: set(),
}


def to_run_state(status: Union[RunStatus, str]) -> RunState:
    if isinstance(status, RunStatus):
        return _RUN_STATUS_TO_STATE.get(status, RunState.FAILED)
    try:
        return _RUN_STATUS_TO_STATE.get(RunStatus(status), RunState.FAILED)
    except Exception:
        return RunState.FAILED


def is_valid_run_transition(current: Union[RunStatus, str], target: Union[RunStatus, str]) -> bool:
    current_state = to_run_state(current)
    target_state = to_run_state(target)
    if current_state == target_state:
        return True
    return target_state in _ALLOWED_TRANSITIONS.get(current_state, set())


def require_valid_transition(current: Union[RunStatus, str], target: Union[RunStatus, str]) -> None:
    if not is_valid_run_transition(current, target):
        raise ValueError(f"Invalid run state transition: {to_run_state(current).value} -> {to_run_state(target).value}")
