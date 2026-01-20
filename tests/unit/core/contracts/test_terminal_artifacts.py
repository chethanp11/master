# ==============================
# IMP-013: Terminal Outcome Artifacts Tests
# ==============================
"""
Tests for terminal outcome artifact schemas.

Tech Spec IDs: ORC-TERM-ART-001, ORC-TERM-ART-002, ORC-TERM-ART-003, ORC-TERM-ART-004
BRD ID: BRD-AUTO-052
"""

import pytest
from pydantic import ValidationError

from core.contracts.run_schema import (
    AbortedArtifact,
    AbortSource,
    CancelledArtifact,
    CompletedArtifact,
    FailedArtifact,
    PausedIndefiniteArtifact,
    RunRecord,
    TerminalOutcome,
    OutcomeReason,
)


# ==============================
# CompletedArtifact Tests (ORC-TERM-ART-001)
# ==============================
class TestCompletedArtifact:
    """Tests for CompletedArtifact schema."""

    def test_completed_artifact_minimal(self):
        """CompletedArtifact requires only final_output."""
        artifact = CompletedArtifact(final_output={"result": "success"})
        assert artifact.final_output == {"result": "success"}
        assert artifact.output_summary is None
        assert artifact.metrics == {}

    def test_completed_artifact_full(self):
        """CompletedArtifact accepts all fields."""
        artifact = CompletedArtifact(
            final_output={"data": [1, 2, 3]},
            output_summary="Processed 3 items",
            metrics={"duration_ms": 150, "steps_executed": 5},
        )
        assert artifact.final_output == {"data": [1, 2, 3]}
        assert artifact.output_summary == "Processed 3 items"
        assert artifact.metrics["duration_ms"] == 150

    def test_completed_artifact_empty_output(self):
        """CompletedArtifact allows empty final_output."""
        artifact = CompletedArtifact(final_output={})
        assert artifact.final_output == {}

    def test_completed_artifact_missing_required(self):
        """CompletedArtifact requires final_output."""
        with pytest.raises(ValidationError):
            CompletedArtifact()

    def test_completed_artifact_extra_forbid(self):
        """CompletedArtifact forbids extra fields."""
        with pytest.raises(ValidationError):
            CompletedArtifact(final_output={}, unknown_field="test")

    def test_completed_artifact_serialization(self):
        """CompletedArtifact serializes to dict."""
        artifact = CompletedArtifact(
            final_output={"key": "value"},
            output_summary="Summary",
        )
        data = artifact.model_dump()
        assert data["final_output"] == {"key": "value"}
        assert data["output_summary"] == "Summary"
        assert data["metrics"] == {}


# ==============================
# FailedArtifact Tests (ORC-TERM-ART-002)
# ==============================
class TestFailedArtifact:
    """Tests for FailedArtifact schema."""

    def test_failed_artifact_minimal(self):
        """FailedArtifact requires error_code and error_message."""
        artifact = FailedArtifact(
            error_code="VALIDATION_ERROR",
            error_message="Input validation failed",
        )
        assert artifact.error_code == "VALIDATION_ERROR"
        assert artifact.error_message == "Input validation failed"
        assert artifact.stack_trace is None
        assert artifact.failed_step_id is None
        assert artifact.recovery_attempted is False

    def test_failed_artifact_full(self):
        """FailedArtifact accepts all fields."""
        artifact = FailedArtifact(
            error_code="TOOL_EXECUTION_ERROR",
            error_message="Tool failed to execute",
            stack_trace="Traceback (most recent call last):\n  ...",
            failed_step_id="step_3",
            recovery_attempted=True,
        )
        assert artifact.error_code == "TOOL_EXECUTION_ERROR"
        assert artifact.stack_trace.startswith("Traceback")
        assert artifact.failed_step_id == "step_3"
        assert artifact.recovery_attempted is True

    def test_failed_artifact_missing_error_code(self):
        """FailedArtifact requires error_code."""
        with pytest.raises(ValidationError):
            FailedArtifact(error_message="Something went wrong")

    def test_failed_artifact_missing_error_message(self):
        """FailedArtifact requires error_message."""
        with pytest.raises(ValidationError):
            FailedArtifact(error_code="ERROR")

    def test_failed_artifact_extra_forbid(self):
        """FailedArtifact forbids extra fields."""
        with pytest.raises(ValidationError):
            FailedArtifact(
                error_code="ERROR",
                error_message="msg",
                custom_field="test",
            )

    def test_failed_artifact_serialization(self):
        """FailedArtifact serializes to dict."""
        artifact = FailedArtifact(
            error_code="BUDGET_EXCEEDED",
            error_message="Token budget exceeded",
            stack_trace="...",
        )
        data = artifact.model_dump()
        assert data["error_code"] == "BUDGET_EXCEEDED"
        assert data["error_message"] == "Token budget exceeded"
        assert data["stack_trace"] == "..."
        assert data["recovery_attempted"] is False


# ==============================
# AbortedArtifact Tests (ORC-TERM-ART-003)
# ==============================
class TestAbortedArtifact:
    """Tests for AbortedArtifact schema."""

    def test_aborted_artifact_user_abort(self):
        """AbortedArtifact captures user-initiated abort."""
        artifact = AbortedArtifact(
            abort_reason="User requested cancellation",
            abort_source=AbortSource.USER,
        )
        assert artifact.abort_reason == "User requested cancellation"
        assert artifact.abort_source == AbortSource.USER
        assert artifact.aborted_at_step_id is None
        assert artifact.partial_output is None

    def test_aborted_artifact_system_abort(self):
        """AbortedArtifact captures system-initiated abort."""
        artifact = AbortedArtifact(
            abort_reason="System shutdown",
            abort_source=AbortSource.SYSTEM,
            aborted_at_step_id="step_5",
        )
        assert artifact.abort_source == AbortSource.SYSTEM
        assert artifact.aborted_at_step_id == "step_5"

    def test_aborted_artifact_governance_abort(self):
        """AbortedArtifact captures governance-initiated abort."""
        artifact = AbortedArtifact(
            abort_reason="Policy violation detected",
            abort_source=AbortSource.GOVERNANCE,
            partial_output={"partial": "data"},
        )
        assert artifact.abort_source == AbortSource.GOVERNANCE
        assert artifact.partial_output == {"partial": "data"}

    def test_aborted_artifact_missing_required(self):
        """AbortedArtifact requires abort_reason and abort_source."""
        with pytest.raises(ValidationError):
            AbortedArtifact(abort_reason="test")
        with pytest.raises(ValidationError):
            AbortedArtifact(abort_source=AbortSource.USER)

    def test_aborted_artifact_invalid_source(self):
        """AbortedArtifact requires valid AbortSource."""
        with pytest.raises(ValidationError):
            AbortedArtifact(
                abort_reason="test",
                abort_source="INVALID",
            )

    def test_aborted_artifact_extra_forbid(self):
        """AbortedArtifact forbids extra fields."""
        with pytest.raises(ValidationError):
            AbortedArtifact(
                abort_reason="test",
                abort_source=AbortSource.USER,
                extra="field",
            )

    def test_aborted_artifact_serialization(self):
        """AbortedArtifact serializes to dict."""
        artifact = AbortedArtifact(
            abort_reason="Governance block",
            abort_source=AbortSource.GOVERNANCE,
        )
        data = artifact.model_dump()
        assert data["abort_reason"] == "Governance block"
        assert data["abort_source"] == "GOVERNANCE"


# ==============================
# AbortSource Enum Tests
# ==============================
class TestAbortSource:
    """Tests for AbortSource enum."""

    def test_abort_source_values(self):
        """AbortSource has correct values."""
        assert AbortSource.USER.value == "USER"
        assert AbortSource.SYSTEM.value == "SYSTEM"
        assert AbortSource.GOVERNANCE.value == "GOVERNANCE"

    def test_abort_source_count(self):
        """AbortSource has exactly 3 values."""
        assert len(AbortSource) == 3


# ==============================
# CancelledArtifact Tests (ORC-TERM-ART-004)
# ==============================
class TestCancelledArtifact:
    """Tests for CancelledArtifact schema."""

    def test_cancelled_artifact_minimal(self):
        """CancelledArtifact has all optional fields."""
        artifact = CancelledArtifact()
        assert artifact.cancel_reason is None
        assert artifact.cancelled_by is None
        assert artifact.cancelled_at_step_id is None

    def test_cancelled_artifact_full(self):
        """CancelledArtifact accepts all fields."""
        artifact = CancelledArtifact(
            cancel_reason="User changed requirements",
            cancelled_by="user@example.com",
            cancelled_at_step_id="step_2",
        )
        assert artifact.cancel_reason == "User changed requirements"
        assert artifact.cancelled_by == "user@example.com"
        assert artifact.cancelled_at_step_id == "step_2"

    def test_cancelled_artifact_extra_forbid(self):
        """CancelledArtifact forbids extra fields."""
        with pytest.raises(ValidationError):
            CancelledArtifact(unknown="test")

    def test_cancelled_artifact_serialization(self):
        """CancelledArtifact serializes to dict."""
        artifact = CancelledArtifact(cancel_reason="Test")
        data = artifact.model_dump()
        assert data["cancel_reason"] == "Test"
        assert data["cancelled_by"] is None


# ==============================
# PausedIndefiniteArtifact Tests
# ==============================
class TestPausedIndefiniteArtifact:
    """Tests for PausedIndefiniteArtifact schema."""

    def test_paused_artifact_minimal(self):
        """PausedIndefiniteArtifact requires pause_reason."""
        artifact = PausedIndefiniteArtifact(pause_reason="Awaiting external input")
        assert artifact.pause_reason == "Awaiting external input"
        assert artifact.paused_at_step_id is None
        assert artifact.resumable is True
        assert artifact.resume_instructions is None

    def test_paused_artifact_full(self):
        """PausedIndefiniteArtifact accepts all fields."""
        artifact = PausedIndefiniteArtifact(
            pause_reason="Waiting for approval",
            paused_at_step_id="step_4",
            resumable=True,
            resume_instructions="Submit approval via HITL endpoint",
        )
        assert artifact.pause_reason == "Waiting for approval"
        assert artifact.paused_at_step_id == "step_4"
        assert artifact.resumable is True
        assert artifact.resume_instructions == "Submit approval via HITL endpoint"

    def test_paused_artifact_non_resumable(self):
        """PausedIndefiniteArtifact can be non-resumable."""
        artifact = PausedIndefiniteArtifact(
            pause_reason="Blocked indefinitely",
            resumable=False,
        )
        assert artifact.resumable is False

    def test_paused_artifact_missing_required(self):
        """PausedIndefiniteArtifact requires pause_reason."""
        with pytest.raises(ValidationError):
            PausedIndefiniteArtifact()

    def test_paused_artifact_extra_forbid(self):
        """PausedIndefiniteArtifact forbids extra fields."""
        with pytest.raises(ValidationError):
            PausedIndefiniteArtifact(pause_reason="test", extra="field")


# ==============================
# RunRecord terminal_artifact Field Tests
# ==============================
class TestRunRecordTerminalArtifact:
    """Tests for terminal_artifact field on RunRecord."""

    def test_run_record_terminal_artifact_default_none(self):
        """RunRecord has terminal_artifact defaulting to None."""
        run = RunRecord(product="test", flow="flow1")
        assert run.terminal_artifact is None

    def test_run_record_with_completed_artifact(self):
        """RunRecord can store CompletedArtifact."""
        artifact = CompletedArtifact(final_output={"result": "ok"})
        run = RunRecord(
            product="test",
            flow="flow1",
            terminal_outcome=TerminalOutcome.COMPLETED,
            outcome_reason=OutcomeReason.SUCCESS,
            terminal_artifact=artifact.model_dump(),
        )
        assert run.terminal_artifact is not None
        assert run.terminal_artifact["final_output"] == {"result": "ok"}

    def test_run_record_with_failed_artifact(self):
        """RunRecord can store FailedArtifact."""
        artifact = FailedArtifact(
            error_code="ERROR",
            error_message="Failed",
        )
        run = RunRecord(
            product="test",
            flow="flow1",
            terminal_outcome=TerminalOutcome.FAILED,
            outcome_reason=OutcomeReason.UNRECOVERABLE_ERROR,
            terminal_artifact=artifact.model_dump(),
        )
        assert run.terminal_artifact["error_code"] == "ERROR"

    def test_run_record_with_aborted_artifact(self):
        """RunRecord can store AbortedArtifact."""
        artifact = AbortedArtifact(
            abort_reason="Test",
            abort_source=AbortSource.USER,
        )
        run = RunRecord(
            product="test",
            flow="flow1",
            terminal_outcome=TerminalOutcome.ABORTED,
            outcome_reason=OutcomeReason.USER_ABORT,
            terminal_artifact=artifact.model_dump(),
        )
        assert run.terminal_artifact["abort_source"] == "USER"

    def test_run_record_serialization_with_artifact(self):
        """RunRecord with terminal_artifact serializes correctly."""
        artifact = CompletedArtifact(final_output={"x": 1})
        run = RunRecord(
            product="test",
            flow="flow1",
            terminal_outcome=TerminalOutcome.COMPLETED,
            terminal_artifact=artifact.model_dump(),
        )
        data = run.model_dump()
        assert "terminal_artifact" in data
        assert data["terminal_artifact"]["final_output"] == {"x": 1}


# ==============================
# Artifact Persistence Order Tests (ORC-TERM-ART-004)
# ==============================
class TestArtifactPersistenceContract:
    """Tests for artifact persistence contract."""

    def test_artifact_before_finalize(self):
        """Artifact should be set before run is finalized."""
        # This is a contract test - we verify the artifact can be set
        # independently of terminal outcome
        artifact = CompletedArtifact(final_output={"stage": "1"})
        run = RunRecord(
            product="test",
            flow="flow1",
            terminal_artifact=artifact.model_dump(),
        )
        # Terminal outcome not set yet
        assert run.terminal_outcome is None
        # But artifact is present
        assert run.terminal_artifact is not None

    def test_artifact_model_dump_stable(self):
        """Artifact model_dump produces stable output."""
        artifact = FailedArtifact(
            error_code="ERR",
            error_message="msg",
        )
        dump1 = artifact.model_dump()
        dump2 = artifact.model_dump()
        assert dump1 == dump2
