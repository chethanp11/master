# ==============================
# Tests: Orchestrator State Enums + Transitions
# ==============================
from __future__ import annotations

from core.orchestrator.state import RunStatus, StepStatus


def test_run_status_has_pending_human() -> None:
    assert hasattr(RunStatus, "PENDING_HUMAN")
    assert RunStatus.PENDING_HUMAN.value == "PENDING_HUMAN"


def test_step_status_has_pending_human() -> None:
    assert hasattr(StepStatus, "PENDING_HUMAN")
    assert StepStatus.PENDING_HUMAN.value == "PENDING_HUMAN"


def test_status_string_roundtrip() -> None:
    # Ensure enum values are stable strings (used in DB/status API).
    assert str(RunStatus.RUNNING.value) == "RUNNING"
    assert str(StepStatus.COMPLETED.value) == "COMPLETED"