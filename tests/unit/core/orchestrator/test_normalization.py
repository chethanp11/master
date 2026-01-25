# tests/unit/core/orchestrator/test_normalization.py
# ==============================
# Normalization Unit Tests
# ==============================
"""
Unit tests for semantic normalization functions.

Tests coverage:
- Whitespace normalization (ORC-SEM-030)
- Entity deduplication (ORC-SEM-031)
- Constraint merging (ORC-SEM-032)
- Stable ordering (ORC-SEM-033)
- Type coercion (ORC-SEM-034)
- Full normalization pipeline
"""

from __future__ import annotations

from datetime import date, datetime

import pytest

from core.contracts.semantic_schema import Ambiguity, Entity, NextAction, SemanticEnvelope
from core.orchestrator.normalization import (
    apply_core_normalization,
    apply_stable_ordering,
    coerce_types,
    deduplicate_entities,
    merge_constraints,
    normalize_whitespace,
)


# ==============================
# Test: Whitespace Normalization
# ==============================
class TestNormalizeWhitespace:
    """Tests for normalize_whitespace (ORC-SEM-030)."""

    def test_normalize_whitespace_collapses_spaces(self) -> None:
        """Multiple spaces should collapse to single space."""
        assert normalize_whitespace("hello   world") == "hello world"
        assert normalize_whitespace("a    b    c") == "a b c"
        assert normalize_whitespace("  hello   world  ") == "hello world"

    def test_normalize_whitespace_handles_tabs(self) -> None:
        """Tabs should be collapsed along with spaces."""
        assert normalize_whitespace("hello\tworld") == "hello world"
        assert normalize_whitespace("a\t\tb\t\tc") == "a b c"
        assert normalize_whitespace("  \t  hello \t world  \t  ") == "hello world"

    def test_normalize_whitespace_handles_empty(self) -> None:
        """Empty string should return empty."""
        assert normalize_whitespace("") == ""

    def test_normalize_whitespace_handles_newlines(self) -> None:
        """Newlines should be preserved but normalized."""
        result = normalize_whitespace("line1\r\nline2\rline3")
        assert result == "line1\nline2\nline3"

    def test_normalize_whitespace_strips_outer(self) -> None:
        """Leading/trailing whitespace should be stripped."""
        assert normalize_whitespace("   hello   ") == "hello"
        assert normalize_whitespace("\t\n  hello  \n\t") == "hello"


# ==============================
# Test: Entity Deduplication
# ==============================
class TestDeduplicateEntities:
    """Tests for deduplicate_entities (ORC-SEM-031)."""

    def test_deduplicate_entities_keeps_highest_confidence(self) -> None:
        """Should keep entity with highest confidence when duplicates exist."""
        e1 = Entity(name="date", type="datetime", value="2026-01-16", confidence=0.8)
        e2 = Entity(name="date", type="datetime", value="2026-01-16", confidence=0.95)
        e3 = Entity(name="date", type="datetime", value="2026-01-17", confidence=0.7)

        result = deduplicate_entities([e1, e2, e3])

        assert len(result) == 1
        assert result[0].confidence == 0.95
        # Note: value comes from highest confidence entity
        assert result[0].value == "2026-01-16"

    def test_deduplicate_entities_different_types_kept(self) -> None:
        """Entities with same name but different types should both be kept."""
        e1 = Entity(name="value", type="string", value="42", confidence=0.9)
        e2 = Entity(name="value", type="number", value=42, confidence=0.85)

        result = deduplicate_entities([e1, e2])

        assert len(result) == 2

    def test_deduplicate_entities_preserves_order(self) -> None:
        """Should preserve order of first occurrence."""
        e1 = Entity(name="a", type="t", value="v1", confidence=0.5)
        e2 = Entity(name="b", type="t", value="v2", confidence=0.5)
        e3 = Entity(name="a", type="t", value="v3", confidence=0.9)
        e4 = Entity(name="c", type="t", value="v4", confidence=0.5)

        result = deduplicate_entities([e1, e2, e3, e4])

        assert len(result) == 3
        assert result[0].name == "a"  # First occurrence of 'a'
        assert result[1].name == "b"
        assert result[2].name == "c"
        # 'a' should have highest confidence value
        assert result[0].confidence == 0.9

    def test_deduplicate_entities_empty_list(self) -> None:
        """Empty list should return empty list."""
        assert deduplicate_entities([]) == []

    def test_deduplicate_entities_no_duplicates(self) -> None:
        """List with no duplicates should be unchanged."""
        e1 = Entity(name="a", type="t1", value="v1", confidence=0.9)
        e2 = Entity(name="b", type="t2", value="v2", confidence=0.8)

        result = deduplicate_entities([e1, e2])

        assert len(result) == 2
        assert result[0].name == "a"
        assert result[1].name == "b"


# ==============================
# Test: Constraint Merging
# ==============================
class TestMergeConstraints:
    """Tests for merge_constraints (ORC-SEM-032)."""

    def test_merge_constraints_later_wins(self) -> None:
        """Later constraint values should override earlier ones."""
        result = merge_constraints([{"a": 1}, {"b": 2}, {"a": 3}])

        assert result == {"a": 3, "b": 2}

    def test_merge_constraints_deep_merge(self) -> None:
        """Nested dicts should be deep merged."""
        c1 = {"outer": {"a": 1, "b": 2}}
        c2 = {"outer": {"b": 3, "c": 4}}

        result = merge_constraints([c1, c2])

        assert result == {"outer": {"a": 1, "b": 3, "c": 4}}

    def test_merge_constraints_lists_replaced(self) -> None:
        """Lists should be replaced, not concatenated."""
        c1 = {"items": [1, 2, 3]}
        c2 = {"items": [4, 5]}

        result = merge_constraints([c1, c2])

        assert result == {"items": [4, 5]}

    def test_merge_constraints_empty_list(self) -> None:
        """Empty list should return empty dict."""
        assert merge_constraints([]) == {}

    def test_merge_constraints_single_dict(self) -> None:
        """Single dict should be returned as-is."""
        result = merge_constraints([{"a": 1, "b": 2}])
        assert result == {"a": 1, "b": 2}


# ==============================
# Test: Stable Ordering
# ==============================
class TestStableOrdering:
    """Tests for apply_stable_ordering (ORC-SEM-033)."""

    def test_stable_ordering_deterministic(self) -> None:
        """Same input should always produce same output order."""
        envelope = SemanticEnvelope(
            raw_input="test",
            normalized_input="test",
            product_id="p",
            intent_type="i",
            entities=[
                Entity(name="zebra", type="t", value="v1"),
                Entity(name="apple", type="t", value="v2"),
                Entity(name="mango", type="t", value="v3"),
            ],
            ambiguities=[
                Ambiguity(ambiguity_id="a1", description="z_ambiguity"),
                Ambiguity(ambiguity_id="a2", description="a_ambiguity"),
                Ambiguity(ambiguity_id="a3", description="m_ambiguity"),
            ],
            constraints={"z_key": 1, "a_key": 2, "m_key": 3},
            parameters={"z_param": 1, "a_param": 2},
        )

        result1 = apply_stable_ordering(envelope)
        result2 = apply_stable_ordering(envelope)

        # Same output both times
        assert result1.entities == result2.entities
        assert result1.ambiguities == result2.ambiguities
        assert list(result1.constraints.keys()) == list(result2.constraints.keys())

    def test_stable_ordering_entities_by_name(self) -> None:
        """Entities should be sorted by name alphabetically."""
        envelope = SemanticEnvelope(
            raw_input="test",
            normalized_input="test",
            product_id="p",
            intent_type="i",
            entities=[
                Entity(name="zebra", type="t", value="v1"),
                Entity(name="apple", type="t", value="v2"),
                Entity(name="mango", type="t", value="v3"),
            ],
        )

        result = apply_stable_ordering(envelope)

        assert [e.name for e in result.entities] == ["apple", "mango", "zebra"]

    def test_stable_ordering_ambiguities_alphabetically(self) -> None:
        """Ambiguities should be sorted alphabetically by description."""
        envelope = SemanticEnvelope(
            raw_input="test",
            normalized_input="test",
            product_id="p",
            intent_type="i",
            ambiguities=[
                Ambiguity(ambiguity_id="a1", description="Zebra issue"),
                Ambiguity(ambiguity_id="a2", description="Apple problem"),
                Ambiguity(ambiguity_id="a3", description="Mango concern"),
            ],
        )

        result = apply_stable_ordering(envelope)

        assert [a.description for a in result.ambiguities] == [
            "Apple problem",
            "Mango concern",
            "Zebra issue",
        ]

    def test_stable_ordering_constraint_keys(self) -> None:
        """Constraint dict keys should be sorted."""
        envelope = SemanticEnvelope(
            raw_input="test",
            normalized_input="test",
            product_id="p",
            intent_type="i",
            constraints={"z": 1, "a": 2, "m": 3},
        )

        result = apply_stable_ordering(envelope)

        assert list(result.constraints.keys()) == ["a", "m", "z"]


# ==============================
# Test: Type Coercion
# ==============================
class TestCoerceTypes:
    """Tests for coerce_types (ORC-SEM-034)."""

    def test_coerce_types_success_cases(self) -> None:
        """Successful coercions should work correctly."""
        # String -> int
        assert coerce_types("42", int) == 42
        assert coerce_types("  123  ", int) == 123

        # String -> float
        assert coerce_types("3.14", float) == 3.14
        assert coerce_types("  2.718  ", float) == 2.718

        # String -> bool
        assert coerce_types("true", bool) is True
        assert coerce_types("false", bool) is False
        assert coerce_types("1", bool) is True
        assert coerce_types("0", bool) is False
        assert coerce_types("yes", bool) is True
        assert coerce_types("no", bool) is False

        # String -> date
        assert coerce_types("2026-01-16", date) == date(2026, 1, 16)

        # String -> datetime
        dt = coerce_types("2026-01-16T10:30:00", datetime)
        assert dt == datetime(2026, 1, 16, 10, 30, 0)

        # Int -> float
        assert coerce_types(42, float) == 42.0

        # Float -> int (truncates)
        assert coerce_types(3.7, int) == 3

        # Any -> str
        assert coerce_types(42, str) == "42"
        assert coerce_types(3.14, str) == "3.14"

    def test_coerce_types_already_correct_type(self) -> None:
        """Value already of target type should be returned as-is."""
        assert coerce_types(42, int) == 42
        assert coerce_types("hello", str) == "hello"
        assert coerce_types(True, bool) is True

    def test_coerce_types_failure_raises(self) -> None:
        """Invalid coercions should raise TypeError."""
        # String that's not a number -> int
        with pytest.raises(TypeError) as exc_info:
            coerce_types("not_a_number", int)
        assert "Failed to coerce" in str(exc_info.value)

        # Invalid bool string
        with pytest.raises(TypeError) as exc_info:
            coerce_types("maybe", bool)
        assert "Failed to coerce" in str(exc_info.value)

        # Invalid date format
        with pytest.raises(TypeError) as exc_info:
            coerce_types("01-16-2026", date)  # Wrong format
        assert "Failed to coerce" in str(exc_info.value)

        # None to int
        with pytest.raises(TypeError) as exc_info:
            coerce_types(None, int)
        assert "Cannot coerce None" in str(exc_info.value)

    def test_coerce_types_unsupported_coercion(self) -> None:
        """Unsupported type coercions should raise TypeError."""
        with pytest.raises(TypeError) as exc_info:
            coerce_types([1, 2, 3], int)
        assert "Unsupported coercion" in str(exc_info.value)


# ==============================
# Test: Full Pipeline
# ==============================
class TestApplyCoreNormalization:
    """Tests for apply_core_normalization full pipeline."""

    def test_apply_core_normalization_full_pipeline(self) -> None:
        """Full pipeline should apply all normalizations."""
        # Create envelope with various normalization needs
        envelope = SemanticEnvelope(
            raw_input="  hello   world  ",
            normalized_input="",  # Will be normalized from raw_input
            product_id="test",
            intent_type="greeting",
            entities=[
                Entity(name="zebra", type="animal", value="z", confidence=0.5),
                Entity(name="apple", type="fruit", value="a", confidence=0.9),
                Entity(name="zebra", type="animal", value="z2", confidence=0.95),  # Duplicate
            ],
            constraints={"z_key": 1, "a_key": 2},
            ambiguities=[
                Ambiguity(ambiguity_id="a1", description="Z problem"),
                Ambiguity(ambiguity_id="a2", description="A issue"),
            ],
        )

        result = apply_core_normalization(envelope)

        # 1. Whitespace normalized
        assert result.normalized_input == "hello world"

        # 2. Entities deduplicated (zebra kept with higher confidence)
        assert len(result.entities) == 2
        zebra = next(e for e in result.entities if e.name == "zebra")
        assert zebra.confidence == 0.95

        # 3. Entities sorted by name
        assert [e.name for e in result.entities] == ["apple", "zebra"]

        # 4. Ambiguities sorted alphabetically by description
        assert [a.description for a in result.ambiguities] == ["A issue", "Z problem"]

        # 5. Constraint keys sorted
        assert list(result.constraints.keys()) == ["a_key", "z_key"]

    def test_apply_core_normalization_preserves_fields(self) -> None:
        """Normalization should preserve all other fields."""
        envelope = SemanticEnvelope(
            raw_input="test input",
            normalized_input="test input",
            product_id="my_product",
            intent_type="query",
            confidence=0.85,
            proposed_next_action=NextAction.ASK_USER,
            interpretation_method="llm",
        )

        result = apply_core_normalization(envelope)

        assert result.raw_input == "test input"
        assert result.product_id == "my_product"
        assert result.intent_type == "query"
        assert result.confidence == 0.85
        assert result.proposed_next_action == NextAction.ASK_USER
        assert result.interpretation_method == "llm"

    def test_apply_core_normalization_idempotent(self) -> None:
        """Applying normalization twice should produce same result."""
        envelope = SemanticEnvelope(
            raw_input="  hello  ",
            normalized_input="",
            product_id="p",
            intent_type="i",
            entities=[
                Entity(name="b", type="t", value="v1"),
                Entity(name="a", type="t", value="v2"),
            ],
        )

        result1 = apply_core_normalization(envelope)
        result2 = apply_core_normalization(result1)

        assert result1.normalized_input == result2.normalized_input
        assert result1.entities == result2.entities
        assert result1.ambiguities == result2.ambiguities
