"""Unit tests for terminal outcome schema.

Tests TS-AGENT-TERM-001, TS-AGENT-TERM-002, TS-AGENT-TERM-003.
"""

import pytest

from products.ade.schemas.terminal_outcome import (
    PartialSuccessDetails,
    RunResult,
    TerminalArtifact,
    TerminalOutcome,
)


class TestTerminalOutcomeEnum:
    """Tests for TerminalOutcome enum (TS-AGENT-TERM-001)."""

    def test_enum_has_success_value(self):
        assert TerminalOutcome.SUCCESS.value == "success"

    def test_enum_has_partial_success_value(self):
        assert TerminalOutcome.PARTIAL_SUCCESS.value == "partial_success"

    def test_enum_has_ask_user_value(self):
        assert TerminalOutcome.ASK_USER.value == "ask_user"

    def test_enum_has_abort_value(self):
        assert TerminalOutcome.ABORT.value == "abort"

    def test_enum_has_exactly_four_values(self):
        assert len(TerminalOutcome) == 4


class TestPartialSuccessDetails:
    """Tests for PartialSuccessDetails schema (TS-AGENT-TERM-002)."""

    def test_partial_success_with_completed_and_missing_steps(self):
        details = PartialSuccessDetails(
            completed_steps=["data_load", "analysis"],
            missing_steps=["visualization", "report"],
            reason="Visualization tool unavailable",
        )
        assert details.completed_steps == ["data_load", "analysis"]
        assert details.missing_steps == ["visualization", "report"]
        assert details.reason == "Visualization tool unavailable"

    def test_partial_success_defaults(self):
        details = PartialSuccessDetails()
        assert details.completed_steps == []
        assert details.missing_steps == []
        assert details.reason == ""


class TestTerminalArtifact:
    """Tests for TerminalArtifact schema (TS-AGENT-TERM-003)."""

    def test_terminal_artifact_with_explanation(self):
        artifact = TerminalArtifact(
            explanation="Analysis completed successfully",
            supporting_refs=["evidence_001", "trace_002"],
            confidence="high",
        )
        assert artifact.explanation == "Analysis completed successfully"
        assert artifact.supporting_refs == ["evidence_001", "trace_002"]
        assert artifact.confidence == "high"

    def test_terminal_artifact_defaults(self):
        artifact = TerminalArtifact()
        assert artifact.explanation == ""
        assert artifact.supporting_refs == []
        assert artifact.confidence == "medium"


class TestRunResult:
    """Tests for RunResult schema with terminal outcome fields."""

    def test_run_result_success(self):
        result = RunResult(
            run_id="run-001",
            outcome=TerminalOutcome.SUCCESS,
            terminal_artifact={"explanation": "Done", "confidence": "high"},
        )
        assert result.run_id == "run-001"
        assert result.outcome == TerminalOutcome.SUCCESS
        assert result.terminal_artifact["explanation"] == "Done"

    def test_run_result_partial_success_with_details(self):
        details = PartialSuccessDetails(
            completed_steps=["step1", "step2"],
            missing_steps=["step3"],
            reason="Data insufficient for step3",
        )
        result = RunResult(
            run_id="run-002",
            outcome=TerminalOutcome.PARTIAL_SUCCESS,
            partial_details=details,
            terminal_artifact={"explanation": "Partial completion"},
        )
        assert result.outcome == TerminalOutcome.PARTIAL_SUCCESS
        assert result.partial_details is not None
        assert result.partial_details.completed_steps == ["step1", "step2"]
        assert result.partial_details.missing_steps == ["step3"]

    def test_run_result_ask_user(self):
        result = RunResult(
            run_id="run-003",
            outcome=TerminalOutcome.ASK_USER,
            terminal_artifact={"explanation": "Clarification needed for metric selection"},
        )
        assert result.outcome == TerminalOutcome.ASK_USER

    def test_run_result_abort(self):
        result = RunResult(
            run_id="run-004",
            outcome=TerminalOutcome.ABORT,
            error_message="Dataset not found",
            terminal_artifact={"explanation": "Cannot proceed without dataset"},
        )
        assert result.outcome == TerminalOutcome.ABORT
        assert result.error_message == "Dataset not found"

    def test_run_result_defaults(self):
        result = RunResult(run_id="run-default")
        assert result.outcome == TerminalOutcome.SUCCESS
        assert result.partial_details is None
        assert result.terminal_artifact == {}
        assert result.artifacts == {}
        assert result.error_message is None
