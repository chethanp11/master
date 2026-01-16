# tests/unit/core/contracts/test_semantic_schema.py
# ==============================
# Semantic Schema Unit Tests
# ==============================
"""
Unit tests for semantic interpretation contracts.

Tests coverage:
- SemanticEnvelope valid construction
- Entity and envelope field validation
- Max entities/ambiguities enforcement
- Confidence bounds validation
- NextAction enum values
- Serialization roundtrip
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.contracts.semantic_schema import (
    Entity,
    NextAction,
    SemanticEnvelope,
)


# ==============================
# Test: NextAction Enum Values
# ==============================
class TestNextActionEnum:
    """Tests for NextAction enum (ORC-SEM-020...022)."""

    def test_next_action_enum_values(self) -> None:
        """NextAction MUST define CONTINUE, ASK_USER, ABORT, NEEDS_APPROVAL."""
        # ORC-SEM-020: Required values
        assert NextAction.CONTINUE.value == "CONTINUE"
        assert NextAction.ASK_USER.value == "ASK_USER"
        assert NextAction.ABORT.value == "ABORT"
        # ORC-SEM-021: Optional NEEDS_APPROVAL
        assert NextAction.NEEDS_APPROVAL.value == "NEEDS_APPROVAL"

    def test_next_action_is_string_enum(self) -> None:
        """NextAction values should be usable as strings."""
        assert str(NextAction.CONTINUE) == "NextAction.CONTINUE"
        assert NextAction.CONTINUE == "CONTINUE"

    def test_next_action_from_string(self) -> None:
        """NextAction can be constructed from string value."""
        assert NextAction("CONTINUE") == NextAction.CONTINUE
        assert NextAction("ASK_USER") == NextAction.ASK_USER
        assert NextAction("ABORT") == NextAction.ABORT


# ==============================
# Test: Entity Model
# ==============================
class TestEntityModel:
    """Tests for Entity model (ORC-SEM-015)."""

    def test_entity_valid_construction(self) -> None:
        """Entity with valid fields should construct successfully."""
        entity = Entity(
            name="user_name",
            type="name",
            value="Alice",
            confidence=0.95,
        )
        assert entity.name == "user_name"
        assert entity.type == "name"
        assert entity.value == "Alice"
        assert entity.confidence == 0.95

    def test_entity_confidence_bounds(self) -> None:
        """Entity confidence must be between 0.0 and 1.0."""
        # Valid bounds
        entity_low = Entity(name="e", type="t", value="v", confidence=0.0)
        assert entity_low.confidence == 0.0

        entity_high = Entity(name="e", type="t", value="v", confidence=1.0)
        assert entity_high.confidence == 1.0

        # Below 0.0 should fail
        with pytest.raises(ValidationError) as exc_info:
            Entity(name="e", type="t", value="v", confidence=-0.1)
        assert "greater than or equal to 0" in str(exc_info.value)

        # Above 1.0 should fail
        with pytest.raises(ValidationError) as exc_info:
            Entity(name="e", type="t", value="v", confidence=1.1)
        assert "less than or equal to 1" in str(exc_info.value)

    def test_entity_default_confidence(self) -> None:
        """Entity confidence defaults to 1.0 if not provided."""
        entity = Entity(name="e", type="t", value="v")
        assert entity.confidence == 1.0

    def test_entity_is_frozen(self) -> None:
        """Entity should be immutable (frozen)."""
        entity = Entity(name="e", type="t", value="v")
        with pytest.raises(ValidationError):
            entity.name = "new_name"  # type: ignore[misc]


# ==============================
# Test: SemanticEnvelope Construction
# ==============================
class TestSemanticEnvelopeConstruction:
    """Tests for SemanticEnvelope valid construction (ORC-SEM-010...019)."""

    def test_semantic_envelope_valid_construction(self) -> None:
        """SemanticEnvelope with all required fields should construct."""
        envelope = SemanticEnvelope(
            raw_input="Hello, my name is Alice",
            normalized_input="hello my name is alice",
            product_id="hello_world",
            intent_type="greeting",
        )
        # ORC-SEM-011
        assert envelope.raw_input == "Hello, my name is Alice"
        # ORC-SEM-012
        assert envelope.normalized_input == "hello my name is alice"
        # ORC-SEM-013
        assert envelope.product_id == "hello_world"
        # ORC-SEM-014
        assert envelope.intent_type == "greeting"
        # Defaults
        assert envelope.entities == []
        assert envelope.constraints == {}
        assert envelope.confidence == 1.0
        assert envelope.ambiguities == []
        assert envelope.proposed_next_action == NextAction.CONTINUE

    def test_semantic_envelope_with_entities(self) -> None:
        """SemanticEnvelope can include Entity objects."""
        entity = Entity(name="user_name", type="name", value="Alice", confidence=0.9)
        envelope = SemanticEnvelope(
            raw_input="Hello Alice",
            normalized_input="hello alice",
            product_id="hello_world",
            intent_type="greeting",
            entities=[entity],
        )
        assert len(envelope.entities) == 1
        assert envelope.entities[0].value == "Alice"

    def test_semantic_envelope_with_constraints(self) -> None:
        """SemanticEnvelope can include constraints dict."""
        envelope = SemanticEnvelope(
            raw_input="Hello in Spanish",
            normalized_input="hello in spanish",
            product_id="hello_world",
            intent_type="greeting",
            constraints={"language": "spanish"},
        )
        assert envelope.constraints["language"] == "spanish"

    def test_semantic_envelope_with_ambiguities(self) -> None:
        """SemanticEnvelope can include ambiguity strings."""
        envelope = SemanticEnvelope(
            raw_input="Hi",
            normalized_input="hi",
            product_id="hello_world",
            intent_type="unknown",
            ambiguities=["Unclear greeting type"],
            proposed_next_action=NextAction.ASK_USER,
        )
        assert len(envelope.ambiguities) == 1
        assert envelope.proposed_next_action == NextAction.ASK_USER

    def test_semantic_envelope_confidence_bounds(self) -> None:
        """SemanticEnvelope confidence must be 0.0-1.0 (ORC-SEM-017)."""
        # Valid bounds
        envelope_low = SemanticEnvelope(
            raw_input="x",
            normalized_input="x",
            product_id="p",
            intent_type="i",
            confidence=0.0,
        )
        assert envelope_low.confidence == 0.0

        envelope_high = SemanticEnvelope(
            raw_input="x",
            normalized_input="x",
            product_id="p",
            intent_type="i",
            confidence=1.0,
        )
        assert envelope_high.confidence == 1.0

        # Out of bounds
        with pytest.raises(ValidationError):
            SemanticEnvelope(
                raw_input="x",
                normalized_input="x",
                product_id="p",
                intent_type="i",
                confidence=-0.01,
            )

        with pytest.raises(ValidationError):
            SemanticEnvelope(
                raw_input="x",
                normalized_input="x",
                product_id="p",
                intent_type="i",
                confidence=1.01,
            )


# ==============================
# Test: Max Entities Enforcement
# ==============================
class TestMaxEntitiesEnforcement:
    """Tests for max entities limit (ORC-SEM-015 implied)."""

    def test_semantic_envelope_max_entities_enforced(self) -> None:
        """SemanticEnvelope MUST reject more than 20 entities."""
        # 20 entities should be allowed
        entities_20 = [
            Entity(name=f"e{i}", type="t", value=f"v{i}")
            for i in range(20)
        ]
        envelope = SemanticEnvelope(
            raw_input="x",
            normalized_input="x",
            product_id="p",
            intent_type="i",
            entities=entities_20,
        )
        assert len(envelope.entities) == 20

        # 21 entities should be rejected
        entities_21 = [
            Entity(name=f"e{i}", type="t", value=f"v{i}")
            for i in range(21)
        ]
        with pytest.raises(ValidationError) as exc_info:
            SemanticEnvelope(
                raw_input="x",
                normalized_input="x",
                product_id="p",
                intent_type="i",
                entities=entities_21,
            )
        assert "entities" in str(exc_info.value).lower()


# ==============================
# Test: Max Ambiguities Enforcement
# ==============================
class TestMaxAmbiguitiesEnforcement:
    """Tests for max ambiguities limit."""

    def test_semantic_envelope_max_ambiguities_enforced(self) -> None:
        """SemanticEnvelope MUST reject more than 20 ambiguities."""
        # 20 ambiguities should be allowed
        ambiguities_20 = [f"Ambiguity {i}" for i in range(20)]
        envelope = SemanticEnvelope(
            raw_input="x",
            normalized_input="x",
            product_id="p",
            intent_type="i",
            ambiguities=ambiguities_20,
        )
        assert len(envelope.ambiguities) == 20

        # 21 ambiguities should be rejected
        ambiguities_21 = [f"Ambiguity {i}" for i in range(21)]
        with pytest.raises(ValidationError) as exc_info:
            SemanticEnvelope(
                raw_input="x",
                normalized_input="x",
                product_id="p",
                intent_type="i",
                ambiguities=ambiguities_21,
            )
        assert "ambiguities" in str(exc_info.value).lower()


# ==============================
# Test: Serialization Roundtrip
# ==============================
class TestSerializationRoundtrip:
    """Tests for JSON serialization/deserialization."""

    def test_envelope_serialization_roundtrip(self) -> None:
        """SemanticEnvelope should serialize and deserialize correctly."""
        original = SemanticEnvelope(
            raw_input="Hello, my name is Bob",
            normalized_input="hello my name is bob",
            product_id="hello_world",
            intent_type="greeting",
            entities=[
                Entity(name="user_name", type="name", value="Bob", confidence=0.95)
            ],
            constraints={"language": "english", "formal": True},
            confidence=0.92,
            ambiguities=["Unclear formality level"],
            proposed_next_action=NextAction.CONTINUE,
            parameters={"greeting_detected": True},
            interpretation_method="rule-based",
        )

        # Serialize to JSON dict
        json_data = original.model_dump()

        # Verify JSON structure
        assert json_data["raw_input"] == "Hello, my name is Bob"
        assert json_data["product_id"] == "hello_world"
        assert len(json_data["entities"]) == 1
        assert json_data["entities"][0]["value"] == "Bob"
        assert json_data["proposed_next_action"] == "CONTINUE"

        # Deserialize back
        restored = SemanticEnvelope.model_validate(json_data)

        # Verify equality
        assert restored.raw_input == original.raw_input
        assert restored.normalized_input == original.normalized_input
        assert restored.product_id == original.product_id
        assert restored.intent_type == original.intent_type
        assert len(restored.entities) == len(original.entities)
        assert restored.entities[0].value == original.entities[0].value
        assert restored.constraints == original.constraints
        assert restored.confidence == original.confidence
        assert restored.ambiguities == original.ambiguities
        assert restored.proposed_next_action == original.proposed_next_action
        assert restored.parameters == original.parameters
        assert restored.interpretation_method == original.interpretation_method

    def test_envelope_to_json_string(self) -> None:
        """SemanticEnvelope can serialize to JSON string."""
        envelope = SemanticEnvelope(
            raw_input="Hi",
            normalized_input="hi",
            product_id="hello_world",
            intent_type="greeting",
        )
        json_str = envelope.model_dump_json()
        assert isinstance(json_str, str)
        assert "hello_world" in json_str
        assert "greeting" in json_str

    def test_envelope_from_json_string(self) -> None:
        """SemanticEnvelope can deserialize from JSON string."""
        json_str = '{"raw_input": "test", "normalized_input": "test", "product_id": "p", "intent_type": "i"}'
        envelope = SemanticEnvelope.model_validate_json(json_str)
        assert envelope.raw_input == "test"
        assert envelope.product_id == "p"
