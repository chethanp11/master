"""
Tests for Ambiguity schema and tracking.

ORC-SEM-AMB-001...006: Ambiguity detection and tracking tests.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.contracts.semantic_schema import (
    Ambiguity,
    SemanticEnvelope,
)


class TestAmbiguitySchema:
    """Test Ambiguity model validation."""

    def test_minimal_ambiguity(self) -> None:
        """ORC-SEM-AMB-001: Ambiguity requires id and description."""
        amb = Ambiguity(
            ambiguity_id="amb_001",
            description="The term 'bank' could mean financial institution or river bank",
        )
        assert amb.ambiguity_id == "amb_001"
        assert amb.description == "The term 'bank' could mean financial institution or river bank"
        assert amb.is_blocking is True
        assert amb.is_resolved is False

    def test_full_ambiguity(self) -> None:
        """ORC-SEM-AMB-001...006: All fields can be set."""
        amb = Ambiguity(
            ambiguity_id="amb_002",
            description="Date format unclear",
            options=["MM/DD/YYYY", "DD/MM/YYYY"],
            source_span=(10, 20),
            resolution_method="user_clarification",
            selected_option="MM/DD/YYYY",
            is_blocking=True,
        )
        assert amb.options == ["MM/DD/YYYY", "DD/MM/YYYY"]
        assert amb.source_span == (10, 20)
        assert amb.resolution_method == "user_clarification"
        assert amb.selected_option == "MM/DD/YYYY"
        assert amb.is_resolved is True

    def test_is_resolved_requires_both_fields(self) -> None:
        """ORC-SEM-AMB-005: Resolution requires both method and selected option."""
        # Only method - not resolved
        amb1 = Ambiguity(
            ambiguity_id="amb_003",
            description="Test",
            resolution_method="default_selection",
        )
        assert amb1.is_resolved is False
        
        # Only option - not resolved
        amb2 = Ambiguity(
            ambiguity_id="amb_004",
            description="Test",
            selected_option="option_a",
        )
        assert amb2.is_resolved is False
        
        # Both present - resolved
        amb3 = Ambiguity(
            ambiguity_id="amb_005",
            description="Test",
            resolution_method="context_inference",
            selected_option="option_b",
        )
        assert amb3.is_resolved is True

    def test_ambiguity_is_frozen(self) -> None:
        """ORC-SEM-AMB: Ambiguity model is frozen."""
        amb = Ambiguity(ambiguity_id="amb_006", description="Test")
        with pytest.raises(ValidationError):
            amb.description = "Changed"  # type: ignore

    def test_max_options_enforced(self) -> None:
        """ORC-SEM-AMB-003: Options list has max length."""
        amb = Ambiguity(
            ambiguity_id="amb_007",
            description="Test",
            options=["opt_" + str(i) for i in range(10)],  # max 10
        )
        assert len(amb.options) == 10


class TestSemanticEnvelopeAmbiguities:
    """Test SemanticEnvelope ambiguity integration."""

    def test_envelope_with_structured_ambiguities(self) -> None:
        """ORC-SEM-AMB: Envelope uses structured ambiguities."""
        amb1 = Ambiguity(ambiguity_id="amb_001", description="First ambiguity")
        amb2 = Ambiguity(ambiguity_id="amb_002", description="Second ambiguity")
        
        envelope = SemanticEnvelope(
            raw_input="Test input",
            normalized_input="test input",
            product_id="test_product",
            intent_type="query",
            ambiguities=[amb1, amb2],
        )
        
        assert len(envelope.ambiguities) == 2
        assert envelope.ambiguity_count == 2
        assert envelope.ambiguities[0].ambiguity_id == "amb_001"

    def test_ambiguity_count_property(self) -> None:
        """ORC-SEM-AMB: ambiguity_count computed property."""
        envelope = SemanticEnvelope(
            raw_input="Test",
            normalized_input="test",
            product_id="prod",
            intent_type="query",
            ambiguities=[
                Ambiguity(ambiguity_id="a1", description="A1"),
                Ambiguity(ambiguity_id="a2", description="A2"),
                Ambiguity(ambiguity_id="a3", description="A3"),
            ],
        )
        assert envelope.ambiguity_count == 3

    def test_blocking_ambiguity_count(self) -> None:
        """ORC-SEM-AMB: blocking_ambiguity_count computed property."""
        envelope = SemanticEnvelope(
            raw_input="Test",
            normalized_input="test",
            product_id="prod",
            intent_type="query",
            ambiguities=[
                Ambiguity(ambiguity_id="a1", description="Blocking", is_blocking=True),
                Ambiguity(ambiguity_id="a2", description="Non-blocking", is_blocking=False),
                Ambiguity(
                    ambiguity_id="a3",
                    description="Resolved",
                    is_blocking=True,
                    resolution_method="auto",
                    selected_option="opt",
                ),
            ],
        )
        # a1 is blocking and unresolved, a2 is not blocking, a3 is resolved
        assert envelope.blocking_ambiguity_count == 1

    def test_unresolved_ambiguity_count(self) -> None:
        """ORC-SEM-AMB: unresolved_ambiguity_count computed property."""
        envelope = SemanticEnvelope(
            raw_input="Test",
            normalized_input="test",
            product_id="prod",
            intent_type="query",
            ambiguities=[
                Ambiguity(ambiguity_id="a1", description="Unresolved 1"),
                Ambiguity(
                    ambiguity_id="a2",
                    description="Resolved",
                    resolution_method="user",
                    selected_option="opt",
                ),
                Ambiguity(ambiguity_id="a3", description="Unresolved 2"),
            ],
        )
        assert envelope.unresolved_ambiguity_count == 2

    def test_max_ambiguities_enforced(self) -> None:
        """ORC-SEM-AMB: Max 20 ambiguities enforced."""
        ambiguities = [
            Ambiguity(ambiguity_id=f"amb_{i}", description=f"Ambiguity {i}")
            for i in range(21)
        ]
        with pytest.raises(ValidationError):
            SemanticEnvelope(
                raw_input="Test",
                normalized_input="test",
                product_id="prod",
                intent_type="query",
                ambiguities=ambiguities,
            )

    def test_envelope_with_no_ambiguities(self) -> None:
        """ORC-SEM-AMB: Envelope without ambiguities has count 0."""
        envelope = SemanticEnvelope(
            raw_input="Clear input",
            normalized_input="clear input",
            product_id="prod",
            intent_type="query",
        )
        assert envelope.ambiguity_count == 0
        assert envelope.blocking_ambiguity_count == 0
        assert envelope.unresolved_ambiguity_count == 0
