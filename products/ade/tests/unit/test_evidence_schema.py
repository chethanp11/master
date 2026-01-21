"""Unit tests for evidence schema.

Tests TS-SCHEMA-EVITEM-001, TS-SCHEMA-EVITEM-002, TS-SCHEMA-CTX-004, TS-SCHEMA-CTX-005.
"""

import pytest
from pydantic import ValidationError

from products.ade.schemas.evidence import (
    EvidenceItemBase,
    TrendEvidence,
    OutlierEvidence,
    DataQualityEvidence,
    HypothesisEvidence,
)
from products.ade.schemas.context_pack import ContextPack, ContextPackEvidenceItem


class TestEvidenceItemConfidence:
    """Tests for EvidenceItem confidence field (TS-SCHEMA-EVITEM-001)."""

    def test_evidence_has_confidence_field(self):
        evidence = TrendEvidence(
            evidence_id="ev-001",
            kind="trend",
            tool_step_id="step-1",
            dataset_id="sales.csv",
            created_at_iso="2026-01-21T00:00:00Z",
            inputs_hash="abc123",
            period_labels=["Jan", "Feb"],
            confidence=0.85,
        )
        assert evidence.confidence == 0.85

    def test_confidence_defaults_to_one(self):
        evidence = OutlierEvidence(
            evidence_id="ev-002",
            kind="outlier",
            tool_step_id="step-2",
            dataset_id="sales.csv",
            created_at_iso="2026-01-21T00:00:00Z",
            inputs_hash="def456",
        )
        assert evidence.confidence == 1.0

    def test_confidence_must_be_in_range(self):
        # confidence > 1.0 should fail
        with pytest.raises(ValidationError):
            TrendEvidence(
                evidence_id="ev-003",
                kind="trend",
                tool_step_id="step-3",
                dataset_id="sales.csv",
                created_at_iso="2026-01-21T00:00:00Z",
                inputs_hash="ghi789",
                period_labels=["Jan"],
                confidence=1.5,
            )

    def test_confidence_must_be_non_negative(self):
        # confidence < 0.0 should fail
        with pytest.raises(ValidationError):
            OutlierEvidence(
                evidence_id="ev-004",
                kind="outlier",
                tool_step_id="step-4",
                dataset_id="sales.csv",
                created_at_iso="2026-01-21T00:00:00Z",
                inputs_hash="jkl012",
                confidence=-0.1,
            )


class TestEvidenceItemValues:
    """Tests for EvidenceItem values field (TS-SCHEMA-EVITEM-002)."""

    def test_evidence_has_values_field(self):
        evidence = DataQualityEvidence(
            evidence_id="ev-005",
            kind="data_quality",
            tool_step_id="step-5",
            dataset_id="sales.csv",
            created_at_iso="2026-01-21T00:00:00Z",
            inputs_hash="mno345",
            row_count=100,
            deduped_row_count=95,
            duplicate_count=5,
            values={"quality_score": 0.95, "issues": ["duplicates"]},
        )
        assert evidence.values["quality_score"] == 0.95
        assert "issues" in evidence.values

    def test_values_defaults_to_empty_dict(self):
        evidence = HypothesisEvidence(
            evidence_id="ev-006",
            kind="hypothesis",
            tool_step_id="step-6",
            dataset_id="sales.csv",
            created_at_iso="2026-01-21T00:00:00Z",
            inputs_hash="pqr678",
            hypothesis_name="seasonality",
            status="confirmed",
            reasoning="Seasonal pattern detected",
        )
        assert evidence.values == {}


class TestEvidenceItemColumns:
    """Tests for EvidenceItem columns field (TS-SCHEMA-CTX-004)."""

    def test_evidence_has_columns_field(self):
        evidence = TrendEvidence(
            evidence_id="ev-007",
            kind="trend",
            tool_step_id="step-7",
            dataset_id="sales.csv",
            created_at_iso="2026-01-21T00:00:00Z",
            inputs_hash="stu901",
            period_labels=["Q1", "Q2"],
            columns=["revenue", "quantity", "date"],
        )
        assert evidence.columns == ["revenue", "quantity", "date"]

    def test_columns_defaults_to_empty_list(self):
        evidence = OutlierEvidence(
            evidence_id="ev-008",
            kind="outlier",
            tool_step_id="step-8",
            dataset_id="sales.csv",
            created_at_iso="2026-01-21T00:00:00Z",
            inputs_hash="vwx234",
        )
        assert evidence.columns == []


class TestContextPackEvidenceItem:
    """Tests for ContextPackEvidenceItem (TS-SCHEMA-CTX-004)."""

    def test_context_pack_evidence_item_has_dataset_and_columns(self):
        item = ContextPackEvidenceItem(
            dataset_id="sales.csv",
            columns=["revenue", "date"],
            source="data_reader",
            description="Dataset columns used for analysis",
        )
        assert item.dataset_id == "sales.csv"
        assert item.columns == ["revenue", "date"]

    def test_context_pack_evidence_item_has_confidence(self):
        item = ContextPackEvidenceItem(
            dataset_id="orders.csv",
            columns=["total"],
            confidence=0.9,
        )
        assert item.confidence == 0.9


class TestContextPackEvidenceItems:
    """Tests for ContextPack.evidence_items (TS-SCHEMA-CTX-004, TS-SCHEMA-CTX-005)."""

    def test_context_pack_has_evidence_items_field(self):
        pack = ContextPack(
            dataset_profile={"dataset_id": "sales.csv"},
            coverage={"row_count": 100},
            missingness={},
            evidence_items=[
                ContextPackEvidenceItem(
                    dataset_id="sales.csv",
                    columns=["revenue"],
                    source="compute_metrics",
                ),
            ],
        )
        assert len(pack.evidence_items) == 1
        assert pack.evidence_items[0].dataset_id == "sales.csv"

    def test_context_pack_has_context_pack_id(self):
        pack = ContextPack(
            dataset_profile={},
            coverage={},
            missingness={},
            context_pack_id="cp-001",
        )
        assert pack.context_pack_id == "cp-001"

    def test_evidence_items_defaults_to_empty_list(self):
        pack = ContextPack(
            dataset_profile={},
            coverage={},
            missingness={},
        )
        assert pack.evidence_items == []
