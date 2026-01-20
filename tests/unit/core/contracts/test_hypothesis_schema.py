# ==============================
# Hypothesis Schema Tests (IMP-014)
# ==============================
"""
Tests for Hypothesis and HypothesisSet models.

Tech Spec IDs: INT-HYP-001, INT-HYP-002, INT-HYP-003, INT-HYP-004, INT-HYP-005
BRD ID: BRD-AUTO-028
"""

import pytest
from datetime import datetime, timezone

from core.contracts.hypothesis_schema import (
    EvidenceRef,
    Hypothesis,
    HypothesisSet,
    HypothesisSetFrozenError,
)


class TestEvidenceRef:
    """Tests for EvidenceRef model."""

    def test_evidence_ref_valid_construction(self):
        """Verify EvidenceRef can be constructed with required fields."""
        ref = EvidenceRef(
            id="ev-001",
            source_type="table",
            confidence=0.85,
        )
        assert ref.id == "ev-001"
        assert ref.source_type == "table"
        assert ref.confidence == 0.85
        assert ref.uri is None
        assert ref.tool_name is None

    def test_evidence_ref_with_optional_fields(self):
        """Verify EvidenceRef accepts optional fields."""
        ref = EvidenceRef(
            id="ev-002",
            source_type="doc",
            confidence=0.75,
            uri="s3://bucket/file.pdf",
            tool_name="read_pdf",
        )
        assert ref.uri == "s3://bucket/file.pdf"
        assert ref.tool_name == "read_pdf"

    def test_evidence_ref_confidence_bounds(self):
        """INT-CP-EVI-001: Confidence must be in [0.0, 1.0]."""
        with pytest.raises(ValueError):
            EvidenceRef(id="ev", source_type="text", confidence=1.5)
        with pytest.raises(ValueError):
            EvidenceRef(id="ev", source_type="text", confidence=-0.1)

    def test_evidence_ref_is_frozen(self):
        """Verify EvidenceRef is immutable."""
        ref = EvidenceRef(id="ev", source_type="text", confidence=0.5)
        with pytest.raises(Exception):
            ref.confidence = 0.9


class TestHypothesis:
    """Tests for Hypothesis model."""

    def test_hypothesis_valid_construction(self):
        """INT-HYP-001: Hypothesis MUST have id, description, confidence, evidence_refs."""
        h = Hypothesis(
            description="The customer prefers automated solutions.",
            confidence=0.8,
        )
        assert h.id is not None  # UUID auto-generated
        assert h.description == "The customer prefers automated solutions."
        assert h.confidence == 0.8
        assert h.evidence_refs == []

    def test_hypothesis_with_evidence_refs(self):
        """Verify Hypothesis accepts evidence_refs."""
        ref = EvidenceRef(id="ev-001", source_type="table", confidence=0.9)
        h = Hypothesis(
            description="Test hypothesis",
            confidence=0.75,
            evidence_refs=[ref],
        )
        assert len(h.evidence_refs) == 1
        assert h.evidence_refs[0].id == "ev-001"

    def test_hypothesis_confidence_bounds(self):
        """INT-HYP-002: Hypothesis confidence MUST be in range [0.0, 1.0]."""
        with pytest.raises(ValueError):
            Hypothesis(description="Test", confidence=1.1)
        with pytest.raises(ValueError):
            Hypothesis(description="Test", confidence=-0.1)

    def test_hypothesis_evidence_refs_limit(self):
        """INT-HYP-003: Evidence refs limited to max 20 items."""
        refs = [
            EvidenceRef(id=f"ev-{i}", source_type="text", confidence=0.5)
            for i in range(21)
        ]
        with pytest.raises(ValueError, match="cannot exceed 20 items"):
            Hypothesis(description="Test", confidence=0.5, evidence_refs=refs)

    def test_hypothesis_evidence_refs_at_limit(self):
        """Verify 20 evidence refs is allowed."""
        refs = [
            EvidenceRef(id=f"ev-{i}", source_type="text", confidence=0.5)
            for i in range(20)
        ]
        h = Hypothesis(description="Test", confidence=0.5, evidence_refs=refs)
        assert len(h.evidence_refs) == 20

    def test_hypothesis_description_required(self):
        """Verify description is required and non-empty."""
        with pytest.raises(ValueError):
            Hypothesis(description="", confidence=0.5)

    def test_hypothesis_is_frozen(self):
        """Verify Hypothesis is immutable."""
        h = Hypothesis(description="Test", confidence=0.5)
        with pytest.raises(Exception):
            h.confidence = 0.9


class TestHypothesisSet:
    """Tests for HypothesisSet model."""

    def test_hypothesis_set_valid_construction(self):
        """INT-HYP-001: HypothesisSet contains list of Hypothesis objects."""
        hs = HypothesisSet()
        assert hs.hypotheses == []
        assert hs.frozen is False
        assert isinstance(hs.created_at, datetime)

    def test_hypothesis_set_with_hypotheses(self):
        """Verify HypothesisSet can be constructed with hypotheses."""
        h1 = Hypothesis(description="Hypothesis 1", confidence=0.8)
        h2 = Hypothesis(description="Hypothesis 2", confidence=0.6)
        hs = HypothesisSet(hypotheses=[h1, h2])
        assert len(hs.hypotheses) == 2

    def test_hypothesis_set_created_at(self):
        """INT-HYP-002: HypothesisSet has created_at timestamp."""
        hs = HypothesisSet()
        assert hs.created_at is not None
        assert isinstance(hs.created_at, datetime)
        # Should be recent (within last minute)
        now = datetime.now(timezone.utc)
        delta = abs((now - hs.created_at).total_seconds())
        assert delta < 60

    def test_hypothesis_set_context_hash(self):
        """INT-HYP-002: HypothesisSet has optional context_hash."""
        hs = HypothesisSet(context_hash="abc123hash")
        assert hs.context_hash == "abc123hash"

    def test_hypothesis_set_hypotheses_limit(self):
        """Verify hypotheses limited to 10 per set."""
        hypotheses = [
            Hypothesis(description=f"Hypothesis {i}", confidence=0.5)
            for i in range(11)
        ]
        with pytest.raises(ValueError, match="cannot exceed 10 items"):
            HypothesisSet(hypotheses=hypotheses)

    def test_hypothesis_set_freeze(self):
        """INT-HYP-004: HypothesisSet is immutable once frozen."""
        hs = HypothesisSet()
        assert hs.frozen is False
        hs.freeze()
        assert hs.frozen is True

    def test_hypothesis_set_freeze_returns_self(self):
        """Verify freeze() returns self for method chaining."""
        hs = HypothesisSet()
        result = hs.freeze()
        assert result is hs

    def test_hypothesis_set_double_freeze_raises(self):
        """Verify freezing already frozen set raises error."""
        hs = HypothesisSet()
        hs.freeze()
        with pytest.raises(HypothesisSetFrozenError, match="already frozen"):
            hs.freeze()

    def test_hypothesis_set_add_hypothesis(self):
        """Verify add_hypothesis works on unfrozen set."""
        hs = HypothesisSet()
        h = Hypothesis(description="Test", confidence=0.5)
        hs.add_hypothesis(h)
        assert len(hs.hypotheses) == 1
        assert hs.hypotheses[0].description == "Test"

    def test_hypothesis_set_add_hypothesis_when_frozen_raises(self):
        """INT-HYP-004: Cannot add hypothesis to frozen set."""
        hs = HypothesisSet()
        hs.freeze()
        h = Hypothesis(description="Test", confidence=0.5)
        with pytest.raises(HypothesisSetFrozenError):
            hs.add_hypothesis(h)

    def test_hypothesis_set_add_hypothesis_limit(self):
        """Verify cannot add more than 10 hypotheses."""
        hs = HypothesisSet()
        for i in range(10):
            hs.add_hypothesis(Hypothesis(description=f"H{i}", confidence=0.5))
        with pytest.raises(ValueError, match="limit of 10 reached"):
            hs.add_hypothesis(Hypothesis(description="H10", confidence=0.5))

    def test_hypothesis_set_get_highest_confidence(self):
        """Verify get_highest_confidence returns correct hypothesis."""
        h1 = Hypothesis(description="Low", confidence=0.3)
        h2 = Hypothesis(description="High", confidence=0.9)
        h3 = Hypothesis(description="Medium", confidence=0.6)
        hs = HypothesisSet(hypotheses=[h1, h2, h3])
        highest = hs.get_highest_confidence()
        assert highest is not None
        assert highest.description == "High"
        assert highest.confidence == 0.9

    def test_hypothesis_set_get_highest_confidence_empty(self):
        """Verify get_highest_confidence returns None for empty set."""
        hs = HypothesisSet()
        assert hs.get_highest_confidence() is None

    def test_hypothesis_set_get_sorted_by_confidence(self):
        """Verify get_sorted_by_confidence returns descending order."""
        h1 = Hypothesis(description="Low", confidence=0.3)
        h2 = Hypothesis(description="High", confidence=0.9)
        h3 = Hypothesis(description="Medium", confidence=0.6)
        hs = HypothesisSet(hypotheses=[h1, h2, h3])
        sorted_list = hs.get_sorted_by_confidence()
        assert sorted_list[0].confidence == 0.9
        assert sorted_list[1].confidence == 0.6
        assert sorted_list[2].confidence == 0.3

    def test_hypothesis_set_serialization(self):
        """Verify HypothesisSet serializes correctly."""
        h = Hypothesis(description="Test", confidence=0.75)
        hs = HypothesisSet(hypotheses=[h], context_hash="hash123")
        data = hs.model_dump()
        assert "hypotheses" in data
        assert len(data["hypotheses"]) == 1
        assert data["context_hash"] == "hash123"
        assert data["frozen"] is False

    def test_hypothesis_set_json_roundtrip(self):
        """Verify HypothesisSet survives JSON roundtrip."""
        h = Hypothesis(description="Test hypothesis", confidence=0.85)
        hs = HypothesisSet(hypotheses=[h], context_hash="abc")
        json_str = hs.model_dump_json()
        restored = HypothesisSet.model_validate_json(json_str)
        assert len(restored.hypotheses) == 1
        assert restored.hypotheses[0].description == "Test hypothesis"
        assert restored.context_hash == "abc"


class TestHypothesisSetFrozenError:
    """Tests for HypothesisSetFrozenError exception."""

    def test_error_message_default(self):
        """Verify default error message."""
        err = HypothesisSetFrozenError()
        assert "frozen" in str(err).lower()

    def test_error_message_custom(self):
        """Verify custom error message."""
        err = HypothesisSetFrozenError("Custom message")
        assert str(err) == "Custom message"
