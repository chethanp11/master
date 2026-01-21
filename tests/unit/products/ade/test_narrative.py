"""Tests for narrative builder.

IMP-018: TS-AGENT-NARR-005 narrative builder tests.
"""

import pytest

from products.ade.utils.narrative import (
    DecisionRecord,
    build_explanation,
    build_explanation_from_dicts,
    get_decision_records_summary,
)


class TestDecisionRecord:
    """Test DecisionRecord class."""

    def test_decision_record_creation(self):
        """Test creating a decision record."""
        record = DecisionRecord(
            record_id="rec-001",
            step_id="step-1",
            decision="Use linear regression",
            rationale="Data is linearly correlated",
            confidence="high",
            timestamp="2024-01-15T10:30:00Z",
        )
        assert record.record_id == "rec-001"
        assert record.step_id == "step-1"
        assert record.decision == "Use linear regression"
        assert record.rationale == "Data is linearly correlated"
        assert record.confidence == "high"
        assert record.timestamp == "2024-01-15T10:30:00Z"

    def test_decision_record_defaults(self):
        """Test decision record default values."""
        record = DecisionRecord(
            record_id="rec-002",
            step_id="step-2",
            decision="Skip feature X",
            rationale="Not relevant",
        )
        assert record.confidence == "medium"
        assert record.timestamp is None


class TestBuildExplanation:
    """Test build_explanation function."""

    def test_empty_records(self):
        """Test with no decision records."""
        result = build_explanation([])
        assert result == "No decision records available for this run."

    def test_single_record(self):
        """Test with one decision record."""
        record = DecisionRecord(
            record_id="rec-001",
            step_id="step-1",
            decision="Selected algorithm A",
            rationale="Best performance on validation set",
            confidence="high",
        )
        result = build_explanation([record])
        assert "[rec-001]" in result
        assert "Selected algorithm A" in result
        assert "Best performance on validation set" in result
        assert "Confidence: high" in result
        assert "1 recorded decisions" in result

    def test_multiple_records(self):
        """Test with multiple decision records."""
        records = [
            DecisionRecord(
                record_id="rec-001",
                step_id="step-1",
                decision="Decision 1",
                rationale="Reason 1",
            ),
            DecisionRecord(
                record_id="rec-002",
                step_id="step-2",
                decision="Decision 2",
                rationale="Reason 2",
            ),
        ]
        result = build_explanation(records)
        assert "2 recorded decisions" in result
        assert "[rec-001]" in result
        assert "[rec-002]" in result

    def test_includes_timestamp_when_present(self):
        """Test that timestamp is included when present."""
        record = DecisionRecord(
            record_id="rec-001",
            step_id="step-1",
            decision="Decision",
            rationale="Reason",
            timestamp="2024-01-15T10:30:00Z",
        )
        result = build_explanation([record])
        assert "Recorded: 2024-01-15T10:30:00Z" in result

    def test_no_timestamp_line_when_absent(self):
        """Test that timestamp line is not present when timestamp is None."""
        record = DecisionRecord(
            record_id="rec-001",
            step_id="step-1",
            decision="Decision",
            rationale="Reason",
        )
        result = build_explanation([record])
        assert "Recorded:" not in result


class TestBuildExplanationFromDicts:
    """Test build_explanation_from_dicts function."""

    def test_from_dict_empty(self):
        """Test with empty list."""
        result = build_explanation_from_dicts([])
        assert result == "No decision records available for this run."

    def test_from_dict_basic(self):
        """Test with dictionary records."""
        records = [
            {
                "record_id": "rec-001",
                "step_id": "step-1",
                "decision": "Chose option A",
                "rationale": "Better fit",
                "confidence": "high",
            }
        ]
        result = build_explanation_from_dicts(records)
        assert "[rec-001]" in result
        assert "Chose option A" in result
        assert "Better fit" in result

    def test_from_dict_missing_fields(self):
        """Test with minimal dictionary fields."""
        records = [{"decision": "Action taken", "rationale": "Some reason"}]
        result = build_explanation_from_dicts(records)
        # Should use default record_id
        assert "[rec-0]" in result
        assert "Action taken" in result


class TestGetDecisionRecordsSummary:
    """Test get_decision_records_summary function."""

    def test_empty_summary(self):
        """Test summary with no records."""
        result = get_decision_records_summary([])
        assert result["total_records"] == 0
        assert result["record_ids"] == []
        assert result["steps_covered"] == []

    def test_summary_with_records(self):
        """Test summary with multiple records."""
        records = [
            DecisionRecord(
                record_id="rec-001",
                step_id="step-1",
                decision="D1",
                rationale="R1",
            ),
            DecisionRecord(
                record_id="rec-002",
                step_id="step-1",
                decision="D2",
                rationale="R2",
            ),
            DecisionRecord(
                record_id="rec-003",
                step_id="step-2",
                decision="D3",
                rationale="R3",
            ),
        ]
        result = get_decision_records_summary(records)
        assert result["total_records"] == 3
        assert result["record_ids"] == ["rec-001", "rec-002", "rec-003"]
        # step-1 and step-2, order may vary
        assert set(result["steps_covered"]) == {"step-1", "step-2"}
