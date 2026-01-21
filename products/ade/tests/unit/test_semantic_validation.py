"""Unit tests for semantic validation.

Tests TS-SEM-VALIDATE-008, TS-SEM-VALIDATE-009.
"""

import pytest

from products.ade.utils.semantic_validation import (
    DatasetSchema,
    ValidationResult,
    _validate_dataset_ref,
    _validate_metric_ref,
    validate_dataset,
    validate_metric,
    validate_semantic_envelope,
)


class TestValidateDatasetRef:
    """Tests for _validate_dataset_ref (TS-SEM-VALIDATE-008)."""

    def test_valid_dataset_returns_true(self):
        available = ["sales.csv", "inventory.csv", "orders.csv"]
        assert _validate_dataset_ref("sales.csv", available) is True

    def test_invalid_dataset_returns_false(self):
        available = ["sales.csv", "inventory.csv"]
        assert _validate_dataset_ref("unknown.csv", available) is False

    def test_empty_dataset_returns_false(self):
        available = ["sales.csv"]
        assert _validate_dataset_ref("", available) is False

    def test_empty_available_list_returns_false(self):
        assert _validate_dataset_ref("sales.csv", []) is False


class TestValidateMetricRef:
    """Tests for _validate_metric_ref (TS-SEM-VALIDATE-009)."""

    def test_valid_metric_returns_true(self):
        schema = DatasetSchema(dataset_id="sales.csv", columns=["amount", "quantity", "date"])
        assert _validate_metric_ref("amount", schema) is True

    def test_invalid_metric_returns_false(self):
        schema = DatasetSchema(dataset_id="sales.csv", columns=["amount", "quantity"])
        assert _validate_metric_ref("unknown_column", schema) is False

    def test_empty_metric_returns_false(self):
        schema = DatasetSchema(dataset_id="sales.csv", columns=["amount"])
        assert _validate_metric_ref("", schema) is False

    def test_empty_columns_returns_false(self):
        schema = DatasetSchema(dataset_id="sales.csv", columns=[])
        assert _validate_metric_ref("amount", schema) is False


class TestValidateDataset:
    """Tests for validate_dataset function."""

    def test_valid_dataset_returns_proceed(self):
        result = validate_dataset("sales.csv", ["sales.csv", "orders.csv"])
        assert result.is_valid is True
        assert result.outcome == "PROCEED"

    def test_invalid_dataset_returns_ask_user(self):
        result = validate_dataset("unknown.csv", ["sales.csv", "orders.csv"])
        assert result.is_valid is False
        assert result.outcome == "ASK_USER"
        assert "unknown.csv" in result.clarifying_question
        assert "sales.csv" in result.clarifying_question

    def test_empty_dataset_returns_ask_user(self):
        result = validate_dataset("", ["sales.csv"])
        assert result.is_valid is False
        assert result.outcome == "ASK_USER"
        assert "dataset" in result.missing_fields

    def test_invalid_dataset_includes_available_options(self):
        result = validate_dataset("missing.csv", ["a.csv", "b.csv"])
        assert "a.csv" in result.clarifying_question
        assert "b.csv" in result.clarifying_question


class TestValidateMetric:
    """Tests for validate_metric function."""

    def test_valid_metric_returns_proceed(self):
        schema = DatasetSchema(dataset_id="sales.csv", columns=["amount", "quantity"])
        result = validate_metric("amount", schema)
        assert result.is_valid is True
        assert result.outcome == "PROCEED"

    def test_invalid_metric_returns_ask_user(self):
        schema = DatasetSchema(dataset_id="sales.csv", columns=["amount", "quantity"])
        result = validate_metric("unknown", schema)
        assert result.is_valid is False
        assert result.outcome == "ASK_USER"
        assert "unknown" in result.clarifying_question
        assert "amount" in result.clarifying_question

    def test_empty_metric_returns_ask_user(self):
        schema = DatasetSchema(dataset_id="sales.csv", columns=["amount"])
        result = validate_metric("", schema)
        assert result.is_valid is False
        assert result.outcome == "ASK_USER"
        assert "metric" in result.missing_fields


class TestValidateSemanticEnvelope:
    """Tests for validate_semantic_envelope function."""

    def test_valid_envelope_returns_proceed(self):
        envelope = {"dataset": "sales.csv", "metric": "amount"}
        context = {
            "available_datasets": ["sales.csv"],
            "schema": {"dataset_id": "sales.csv", "columns": ["amount", "quantity"]},
        }
        result = validate_semantic_envelope(envelope, context)
        assert result.is_valid is True
        assert result.outcome == "PROCEED"

    def test_invalid_dataset_in_envelope_returns_ask_user(self):
        envelope = {"dataset": "unknown.csv", "metric": "amount"}
        context = {"available_datasets": ["sales.csv"]}
        result = validate_semantic_envelope(envelope, context)
        assert result.is_valid is False
        assert result.outcome == "ASK_USER"

    def test_invalid_metric_in_envelope_returns_ask_user(self):
        envelope = {"dataset": "sales.csv", "metric": "unknown"}
        context = {
            "available_datasets": ["sales.csv"],
            "schema": {"dataset_id": "sales.csv", "columns": ["amount"]},
        }
        result = validate_semantic_envelope(envelope, context)
        assert result.is_valid is False
        assert result.outcome == "ASK_USER"

    def test_missing_optional_fields_adjusts_confidence(self):
        envelope = {"dataset": "sales.csv"}
        context = {"available_datasets": ["sales.csv"]}
        result = validate_semantic_envelope(envelope, context)
        assert result.is_valid is True
        assert result.confidence_adjustment < 0  # Penalized for missing optionals

    def test_no_context_skips_validation(self):
        envelope = {"dataset": "anything", "metric": "anything"}
        result = validate_semantic_envelope(envelope)
        assert result.is_valid is True
        assert result.outcome == "PROCEED"
