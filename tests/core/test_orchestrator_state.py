from __future__ import annotations

# ==============================
# Tests: Orchestrator State Enums + Transitions
# ==============================

from core.orchestrator.state import RunStatus, StepStatus, RunState, is_valid_run_transition, to_run_state


def test_run_status_has_pending_human() -> None:
    assert hasattr(RunStatus, "PENDING_HUMAN")
    assert RunStatus.PENDING_HUMAN.value == "PENDING_HUMAN"
    assert hasattr(RunStatus, "PENDING_USER_INPUT")
    assert RunStatus.PENDING_USER_INPUT.value == "PENDING_USER_INPUT"


def test_step_status_has_pending_human() -> None:
    assert hasattr(StepStatus, "PENDING_HUMAN")
    assert StepStatus.PENDING_HUMAN.value == "PENDING_HUMAN"
    assert hasattr(StepStatus, "PENDING_USER_INPUT")
    assert StepStatus.PENDING_USER_INPUT.value == "PENDING_USER_INPUT"


def test_status_string_roundtrip() -> None:
    # Ensure enum values are stable strings (used in DB/status API).
    assert str(RunStatus.RUNNING.value) == "RUNNING"
    assert str(StepStatus.COMPLETED.value) == "COMPLETED"


def test_run_state_mapping() -> None:
    assert to_run_state(RunStatus.PENDING_HUMAN) == RunState.PENDING_APPROVAL
    assert to_run_state(RunStatus.PENDING_USER_INPUT) == RunState.PENDING_USER_INPUT


def test_run_state_transitions() -> None:
    assert is_valid_run_transition(RunStatus.RUNNING, RunStatus.PENDING_HUMAN)
    assert is_valid_run_transition(RunStatus.PENDING_HUMAN, RunStatus.RUNNING)
    assert is_valid_run_transition(RunStatus.PENDING_USER_INPUT, RunStatus.RUNNING)
    assert not is_valid_run_transition(RunStatus.COMPLETED, RunStatus.RUNNING)
