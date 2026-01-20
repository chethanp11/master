# ==============================
# Sufficiency Schema Tests (IMP-016)
# ==============================
"""
Tests for SufficiencyState and related models.

Tech Spec IDs: INT-SUFF-001, INT-SUFF-002, INT-SUFF-003, INT-SUFF-004, INT-SUFF-005
BRD ID: BRD-AUTO-029
"""

import pytest
from datetime import datetime, timezone

from core.contracts.sufficiency_schema import (
    Assumption,
    Fact,
    Gap,
    Importance,
    Priority,
    SufficiencyState,
    Unknown,
)


class TestFact:
    """Tests for Fact model."""

    def test_fact_valid_construction(self):
        """INT-SUFF-002: Fact with description and confidence."""
        fact = Fact(description="The customer has 3 accounts.")
        assert fact.id is not None
        assert fact.description == "The customer has 3 accounts."
        assert fact.confidence == 1.0
        assert fact.evidence_ref is None

    def test_fact_with_evidence_ref(self):
        """Verify Fact accepts evidence_ref."""
        fact = Fact(
            description="Revenue is $1M",
            evidence_ref="ev-001",
            confidence=0.95,
        )
        assert fact.evidence_ref == "ev-001"
        assert fact.confidence == 0.95

    def test_fact_confidence_bounds(self):
        """Verify confidence must be in [0.0, 1.0]."""
        with pytest.raises(ValueError):
            Fact(description="Test", confidence=1.5)
        with pytest.raises(ValueError):
            Fact(description="Test", confidence=-0.1)

    def test_fact_description_required(self):
        """Verify description is required and non-empty."""
        with pytest.raises(ValueError):
            Fact(description="")

    def test_fact_is_frozen(self):
        """Verify Fact is immutable."""
        fact = Fact(description="Test")
        with pytest.raises(Exception):
            fact.confidence = 0.5


class TestUnknown:
    """Tests for Unknown model."""

    def test_unknown_valid_construction(self):
        """INT-SUFF-003: Unknown with question."""
        unknown = Unknown(question="What is the customer's budget?")
        assert unknown.id is not None
        assert unknown.question == "What is the customer's budget?"
        assert unknown.importance == Importance.MEDIUM
        assert unknown.blocking is False

    def test_unknown_blocking(self):
        """Verify blocking unknown."""
        unknown = Unknown(
            question="What is the contract date?",
            importance=Importance.HIGH,
            blocking=True,
        )
        assert unknown.blocking is True
        assert unknown.importance == Importance.HIGH

    def test_unknown_question_required(self):
        """Verify question is required and non-empty."""
        with pytest.raises(ValueError):
            Unknown(question="")

    def test_unknown_is_frozen(self):
        """Verify Unknown is immutable."""
        unknown = Unknown(question="Test?")
        with pytest.raises(Exception):
            unknown.blocking = True


class TestAssumption:
    """Tests for Assumption model."""

    def test_assumption_valid_construction(self):
        """INT-SUFF-004: Assumption with description and confidence."""
        assumption = Assumption(description="Customer prefers cloud solutions.")
        assert assumption.id is not None
        assert assumption.description == "Customer prefers cloud solutions."
        assert assumption.confidence == 0.5
        assert assumption.evidence_ref is None

    def test_assumption_with_evidence_ref(self):
        """Verify Assumption accepts evidence_ref."""
        assumption = Assumption(
            description="Budget is approximately $500K",
            evidence_ref="ev-002",
            confidence=0.7,
        )
        assert assumption.evidence_ref == "ev-002"
        assert assumption.confidence == 0.7

    def test_assumption_confidence_bounds(self):
        """Verify confidence must be in [0.0, 1.0]."""
        with pytest.raises(ValueError):
            Assumption(description="Test", confidence=1.5)
        with pytest.raises(ValueError):
            Assumption(description="Test", confidence=-0.1)

    def test_assumption_description_required(self):
        """Verify description is required and non-empty."""
        with pytest.raises(ValueError):
            Assumption(description="")

    def test_assumption_is_frozen(self):
        """Verify Assumption is immutable."""
        assumption = Assumption(description="Test")
        with pytest.raises(Exception):
            assumption.confidence = 0.9


class TestGap:
    """Tests for Gap model."""

    def test_gap_valid_construction(self):
        """INT-SUFF-005: Gap with description and priority."""
        gap = Gap(description="Missing customer segmentation data.")
        assert gap.id is not None
        assert gap.description == "Missing customer segmentation data."
        assert gap.priority == Priority.MEDIUM
        assert gap.blocking is False

    def test_gap_blocking(self):
        """Verify blocking gap."""
        gap = Gap(
            description="No pricing information available.",
            priority=Priority.CRITICAL,
            blocking=True,
        )
        assert gap.blocking is True
        assert gap.priority == Priority.CRITICAL

    def test_gap_priorities(self):
        """Verify all priority levels."""
        assert Gap(description="Low", priority=Priority.LOW).priority == Priority.LOW
        assert Gap(description="Med", priority=Priority.MEDIUM).priority == Priority.MEDIUM
        assert Gap(description="High", priority=Priority.HIGH).priority == Priority.HIGH
        assert Gap(description="Crit", priority=Priority.CRITICAL).priority == Priority.CRITICAL

    def test_gap_description_required(self):
        """Verify description is required and non-empty."""
        with pytest.raises(ValueError):
            Gap(description="")

    def test_gap_is_frozen(self):
        """Verify Gap is immutable."""
        gap = Gap(description="Test")
        with pytest.raises(Exception):
            gap.blocking = True


class TestSufficiencyState:
    """Tests for SufficiencyState model."""

    def test_sufficiency_state_valid_construction(self):
        """INT-SUFF-001: SufficiencyState maintained per run."""
        state = SufficiencyState(run_id="run-001")
        assert state.run_id == "run-001"
        assert state.facts == []
        assert state.unknowns == []
        assert state.assumptions == []
        assert state.gaps == []
        assert isinstance(state.updated_at, datetime)

    def test_sufficiency_state_with_facts(self):
        """INT-SUFF-002: Contains facts (verified evidence)."""
        fact = Fact(description="Customer has 3 accounts.")
        state = SufficiencyState(run_id="run-001", facts=[fact])
        assert len(state.facts) == 1
        assert state.facts[0].description == "Customer has 3 accounts."

    def test_sufficiency_state_with_unknowns(self):
        """INT-SUFF-003: Contains unknowns (unresolved questions)."""
        unknown = Unknown(question="What is the budget?")
        state = SufficiencyState(run_id="run-001", unknowns=[unknown])
        assert len(state.unknowns) == 1

    def test_sufficiency_state_with_assumptions(self):
        """INT-SUFF-004: Contains assumptions (with confidence)."""
        assumption = Assumption(description="Budget is ~$500K", confidence=0.6)
        state = SufficiencyState(run_id="run-001", assumptions=[assumption])
        assert len(state.assumptions) == 1
        assert state.assumptions[0].confidence == 0.6

    def test_sufficiency_state_with_gaps(self):
        """INT-SUFF-005: Contains gaps (missing information)."""
        gap = Gap(description="Missing pricing data", priority=Priority.HIGH)
        state = SufficiencyState(run_id="run-001", gaps=[gap])
        assert len(state.gaps) == 1
        assert state.gaps[0].priority == Priority.HIGH

    def test_is_sufficient_empty(self):
        """Verify is_sufficient returns True when no gaps."""
        state = SufficiencyState(run_id="run-001")
        assert state.is_sufficient() is True

    def test_is_sufficient_non_blocking_gaps(self):
        """Verify is_sufficient returns True with non-blocking gaps."""
        gap = Gap(description="Nice to have", blocking=False)
        state = SufficiencyState(run_id="run-001", gaps=[gap])
        assert state.is_sufficient() is True

    def test_is_sufficient_blocking_gaps(self):
        """Verify is_sufficient returns False with blocking gaps."""
        gap = Gap(description="Critical data", blocking=True)
        state = SufficiencyState(run_id="run-001", gaps=[gap])
        assert state.is_sufficient() is False

    def test_has_blocking_unknowns(self):
        """Verify has_blocking_unknowns works correctly."""
        state = SufficiencyState(run_id="run-001")
        assert state.has_blocking_unknowns() is False
        
        unknown = Unknown(question="Test?", blocking=True)
        state.add_unknown(unknown)
        assert state.has_blocking_unknowns() is True

    def test_get_blocking_gaps(self):
        """Verify get_blocking_gaps returns correct list."""
        gap1 = Gap(description="Non-blocking", blocking=False)
        gap2 = Gap(description="Blocking", blocking=True)
        state = SufficiencyState(run_id="run-001", gaps=[gap1, gap2])
        blocking = state.get_blocking_gaps()
        assert len(blocking) == 1
        assert blocking[0].description == "Blocking"

    def test_get_blocking_unknowns(self):
        """Verify get_blocking_unknowns returns correct list."""
        u1 = Unknown(question="Non-blocking?", blocking=False)
        u2 = Unknown(question="Blocking?", blocking=True)
        state = SufficiencyState(run_id="run-001", unknowns=[u1, u2])
        blocking = state.get_blocking_unknowns()
        assert len(blocking) == 1
        assert blocking[0].question == "Blocking?"

    def test_add_fact(self):
        """Verify add_fact works correctly."""
        state = SufficiencyState(run_id="run-001")
        fact = Fact(description="New fact")
        state.add_fact(fact)
        assert len(state.facts) == 1

    def test_add_unknown(self):
        """Verify add_unknown works correctly."""
        state = SufficiencyState(run_id="run-001")
        unknown = Unknown(question="New question?")
        state.add_unknown(unknown)
        assert len(state.unknowns) == 1

    def test_add_assumption(self):
        """Verify add_assumption works correctly."""
        state = SufficiencyState(run_id="run-001")
        assumption = Assumption(description="New assumption")
        state.add_assumption(assumption)
        assert len(state.assumptions) == 1

    def test_add_gap(self):
        """Verify add_gap works correctly."""
        state = SufficiencyState(run_id="run-001")
        gap = Gap(description="New gap")
        state.add_gap(gap)
        assert len(state.gaps) == 1

    def test_resolve_unknown(self):
        """Verify resolve_unknown removes by ID."""
        unknown = Unknown(question="To resolve?")
        state = SufficiencyState(run_id="run-001", unknowns=[unknown])
        assert len(state.unknowns) == 1
        result = state.resolve_unknown(unknown.id)
        assert result is True
        assert len(state.unknowns) == 0

    def test_resolve_unknown_not_found(self):
        """Verify resolve_unknown returns False if not found."""
        state = SufficiencyState(run_id="run-001")
        result = state.resolve_unknown("nonexistent")
        assert result is False

    def test_resolve_gap(self):
        """Verify resolve_gap removes by ID."""
        gap = Gap(description="To resolve")
        state = SufficiencyState(run_id="run-001", gaps=[gap])
        assert len(state.gaps) == 1
        result = state.resolve_gap(gap.id)
        assert result is True
        assert len(state.gaps) == 0

    def test_resolve_gap_not_found(self):
        """Verify resolve_gap returns False if not found."""
        state = SufficiencyState(run_id="run-001")
        result = state.resolve_gap("nonexistent")
        assert result is False

    def test_to_summary(self):
        """Verify to_summary returns correct counts."""
        state = SufficiencyState(run_id="run-001")
        state.add_fact(Fact(description="Fact"))
        state.add_unknown(Unknown(question="Unknown?"))
        state.add_assumption(Assumption(description="Assumption"))
        state.add_gap(Gap(description="Gap", blocking=True))
        
        summary = state.to_summary()
        assert summary["fact_count"] == 1
        assert summary["unknown_count"] == 1
        assert summary["assumption_count"] == 1
        assert summary["gap_count"] == 1
        assert summary["blocking_gap_count"] == 1
        assert summary["is_sufficient"] is False

    def test_serialization(self):
        """Verify SufficiencyState serializes correctly."""
        state = SufficiencyState(run_id="run-001")
        state.add_fact(Fact(description="Test fact"))
        data = state.model_dump()
        assert data["run_id"] == "run-001"
        assert len(data["facts"]) == 1

    def test_json_roundtrip(self):
        """Verify SufficiencyState survives JSON roundtrip."""
        state = SufficiencyState(run_id="run-001")
        state.add_fact(Fact(description="Test fact", confidence=0.9))
        state.add_gap(Gap(description="Test gap", blocking=True))
        
        json_str = state.model_dump_json()
        restored = SufficiencyState.model_validate_json(json_str)
        
        assert restored.run_id == "run-001"
        assert len(restored.facts) == 1
        assert len(restored.gaps) == 1
        assert restored.facts[0].confidence == 0.9
        assert restored.gaps[0].blocking is True
