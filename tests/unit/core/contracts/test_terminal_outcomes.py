# ==============================
# Terminal Outcomes Tests (IMP-012)
# ==============================
"""
Tests for terminal outcome enums and RunRecord fields.

Tech Spec IDs: ORC-TERM-001, ORC-TERM-002, ORC-TERM-003, ORC-TERM-004, ORC-TERM-005
BRD ID: BRD-AUTO-052
"""

import pytest

from core.contracts.run_schema import (
    OutcomeReason,
    RunRecord,
    RunStatus,
    TerminalOutcome,
)


class TestTerminalOutcomeEnum:
    """ORC-TERM-001: TerminalOutcome enum exists with required values."""

    def test_terminal_outcome_enum_exists(self):
        """Verify TerminalOutcome enum is defined."""
        assert hasattr(TerminalOutcome, "COMPLETED")
        assert hasattr(TerminalOutcome, "FAILED")
        assert hasattr(TerminalOutcome, "CANCELLED")
        assert hasattr(TerminalOutcome, "ABORTED")
        assert hasattr(TerminalOutcome, "PAUSED_INDEFINITE")

    def test_terminal_outcome_values(self):
        """Verify enum values are strings."""
        assert TerminalOutcome.COMPLETED.value == "COMPLETED"
        assert TerminalOutcome.FAILED.value == "FAILED"
        assert TerminalOutcome.CANCELLED.value == "CANCELLED"
        assert TerminalOutcome.ABORTED.value == "ABORTED"
        assert TerminalOutcome.PAUSED_INDEFINITE.value == "PAUSED_INDEFINITE"

    def test_terminal_outcome_has_5_values(self):
        """Verify exactly 5 terminal outcomes defined."""
        assert len(TerminalOutcome) == 5


class TestOutcomeReasonEnum:
    """ORC-TERM-002: OutcomeReason enum exists with required values."""

    def test_outcome_reason_enum_exists(self):
        """Verify OutcomeReason enum is defined."""
        assert hasattr(OutcomeReason, "SUCCESS")
        assert hasattr(OutcomeReason, "USER_ABORT")
        assert hasattr(OutcomeReason, "GOVERNANCE_BLOCK")
        assert hasattr(OutcomeReason, "BUDGET_EXCEEDED")
        assert hasattr(OutcomeReason, "MAX_ITERATIONS")
        assert hasattr(OutcomeReason, "VALIDATION_FAILED")
        assert hasattr(OutcomeReason, "UNRECOVERABLE_ERROR")

    def test_outcome_reason_values(self):
        """Verify enum values are strings."""
        assert OutcomeReason.SUCCESS.value == "SUCCESS"
        assert OutcomeReason.USER_ABORT.value == "USER_ABORT"
        assert OutcomeReason.GOVERNANCE_BLOCK.value == "GOVERNANCE_BLOCK"
        assert OutcomeReason.BUDGET_EXCEEDED.value == "BUDGET_EXCEEDED"
        assert OutcomeReason.MAX_ITERATIONS.value == "MAX_ITERATIONS"
        assert OutcomeReason.VALIDATION_FAILED.value == "VALIDATION_FAILED"
        assert OutcomeReason.UNRECOVERABLE_ERROR.value == "UNRECOVERABLE_ERROR"

    def test_outcome_reason_has_7_values(self):
        """Verify exactly 7 outcome reasons defined."""
        assert len(OutcomeReason) == 7


class TestRunRecordTerminalOutcomeFields:
    """ORC-TERM-003..005: RunRecord includes terminal outcome fields."""

    def test_run_record_terminal_outcome_field_optional(self):
        """Verify terminal_outcome field is optional (None by default)."""
        run = RunRecord(product="test", flow="test_flow")
        assert run.terminal_outcome is None

    def test_run_record_outcome_reason_field_optional(self):
        """Verify outcome_reason field is optional (None by default)."""
        run = RunRecord(product="test", flow="test_flow")
        assert run.outcome_reason is None

    def test_run_record_outcome_explanation_field_optional(self):
        """Verify outcome_explanation field is optional (None by default)."""
        run = RunRecord(product="test", flow="test_flow")
        assert run.outcome_explanation is None

    def test_run_record_with_terminal_outcome_completed(self):
        """Verify RunRecord accepts COMPLETED terminal outcome."""
        run = RunRecord(
            product="test",
            flow="test_flow",
            terminal_outcome=TerminalOutcome.COMPLETED,
            outcome_reason=OutcomeReason.SUCCESS,
            outcome_explanation="Run completed successfully.",
        )
        assert run.terminal_outcome == TerminalOutcome.COMPLETED
        assert run.outcome_reason == OutcomeReason.SUCCESS
        assert run.outcome_explanation == "Run completed successfully."

    def test_run_record_with_terminal_outcome_failed(self):
        """Verify RunRecord accepts FAILED terminal outcome."""
        run = RunRecord(
            product="test",
            flow="test_flow",
            terminal_outcome=TerminalOutcome.FAILED,
            outcome_reason=OutcomeReason.UNRECOVERABLE_ERROR,
            outcome_explanation="An unrecoverable error occurred.",
        )
        assert run.terminal_outcome == TerminalOutcome.FAILED
        assert run.outcome_reason == OutcomeReason.UNRECOVERABLE_ERROR
        assert run.outcome_explanation == "An unrecoverable error occurred."

    def test_run_record_terminal_outcome_serialization(self):
        """Verify terminal outcome fields serialize correctly."""
        run = RunRecord(
            product="test",
            flow="test_flow",
            terminal_outcome=TerminalOutcome.ABORTED,
            outcome_reason=OutcomeReason.USER_ABORT,
            outcome_explanation="User cancelled the operation.",
        )
        data = run.model_dump()
        assert data["terminal_outcome"] == "ABORTED"
        assert data["outcome_reason"] == "USER_ABORT"
        assert data["outcome_explanation"] == "User cancelled the operation."

    def test_run_record_terminal_outcome_json_roundtrip(self):
        """Verify terminal outcome fields survive JSON roundtrip."""
        run = RunRecord(
            product="test",
            flow="test_flow",
            terminal_outcome=TerminalOutcome.CANCELLED,
            outcome_reason=OutcomeReason.GOVERNANCE_BLOCK,
            outcome_explanation="Blocked by governance policy.",
        )
        json_str = run.model_dump_json()
        restored = RunRecord.model_validate_json(json_str)
        assert restored.terminal_outcome == TerminalOutcome.CANCELLED
        assert restored.outcome_reason == OutcomeReason.GOVERNANCE_BLOCK
        assert restored.outcome_explanation == "Blocked by governance policy."

    def test_outcome_explanation_is_human_readable(self):
        """ORC-TERM-004: outcome_explanation should be human-readable string."""
        run = RunRecord(
            product="test",
            flow="test_flow",
            terminal_outcome=TerminalOutcome.FAILED,
            outcome_reason=OutcomeReason.BUDGET_EXCEEDED,
            outcome_explanation="The run exceeded its allocated token budget of 10000 tokens.",
        )
        # Human-readable means it's a non-empty string with meaningful content
        assert isinstance(run.outcome_explanation, str)
        assert len(run.outcome_explanation) > 10
        assert "budget" in run.outcome_explanation.lower()
