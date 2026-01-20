# ==============================
# IMP-020: ContextPack Freeze Requirements Tests
# ==============================
"""
Tests for ContextPack freeze requirements.

Tech Spec IDs: INT-CP-FREEZE-001, INT-CP-FREEZE-002, INT-CP-FREEZE-003
BRD ID: BRD-AUTO-051
"""

import pytest
from datetime import datetime, timezone

from core.contracts.context_pack_schema import (
    ContextPack,
    ContextPackFrozenError,
    DocumentsSummary,
    EvidenceIndexEntry,
    TablesSummary,
)
# Import for forward reference resolution
from core.contracts.hypothesis_schema import HypothesisSet
from core.contracts.sufficiency_schema import SufficiencyState

# Rebuild model to resolve forward references
ContextPack.model_rebuild()


def create_test_context_pack() -> ContextPack:
    """Create a minimal ContextPack for testing."""
    return ContextPack(
        question="Test question",
        evidence_index=[],
        tables_summary=TablesSummary(),
        documents_summary=DocumentsSummary(),
    )


# ==============================
# ContextPackFrozenError Tests
# ==============================
class TestContextPackFrozenError:
    """Tests for ContextPackFrozenError exception."""

    def test_exception_creation(self):
        """ContextPackFrozenError can be created."""
        error = ContextPackFrozenError()
        assert "Cannot modify frozen ContextPack" in str(error)

    def test_exception_custom_message(self):
        """ContextPackFrozenError accepts custom message."""
        error = ContextPackFrozenError("Custom message")
        assert "Custom message" in str(error)


# ==============================
# Freeze Fields Tests
# ==============================
class TestContextPackFreezeFields:
    """Tests for freeze-related fields on ContextPack."""

    def test_frozen_default_false(self):
        """frozen field defaults to False."""
        pack = create_test_context_pack()
        
        assert pack.frozen is False

    def test_frozen_at_default_none(self):
        """frozen_at field defaults to None."""
        pack = create_test_context_pack()
        
        assert pack.frozen_at is None

    def test_frozen_hash_default_none(self):
        """frozen_hash field defaults to None."""
        pack = create_test_context_pack()
        
        assert pack.frozen_hash is None


# ==============================
# Freeze Method Tests
# ==============================
class TestContextPackFreeze:
    """Tests for ContextPack.freeze() method."""

    def test_freeze_sets_frozen_true_int_cp_freeze_001(self):
        """INT-CP-FREEZE-001: ContextPack frozen (immutable) via freeze()."""
        pack = create_test_context_pack()
        
        pack.freeze()
        
        assert pack.frozen is True

    def test_freeze_sets_frozen_at_int_cp_freeze_002(self):
        """INT-CP-FREEZE-002: Frozen ContextPack has frozen_at timestamp."""
        pack = create_test_context_pack()
        before = datetime.now(timezone.utc)
        
        pack.freeze()
        
        assert pack.frozen_at is not None
        assert pack.frozen_at >= before

    def test_freeze_sets_frozen_hash_int_cp_freeze_002(self):
        """INT-CP-FREEZE-002: Frozen ContextPack has frozen_hash (SHA-256)."""
        pack = create_test_context_pack()
        
        hash_result = pack.freeze()
        
        assert pack.frozen_hash is not None
        assert len(pack.frozen_hash) == 64  # SHA-256 hex length
        assert hash_result == pack.frozen_hash

    def test_freeze_returns_hash(self):
        """freeze() returns the frozen_hash."""
        pack = create_test_context_pack()
        
        result = pack.freeze()
        
        assert result == pack.frozen_hash

    def test_freeze_already_frozen_raises(self):
        """Attempting to freeze already frozen pack raises error."""
        pack = create_test_context_pack()
        pack.freeze()
        
        with pytest.raises(ContextPackFrozenError) as exc_info:
            pack.freeze()
        
        assert "already frozen" in str(exc_info.value)

    def test_freeze_hash_deterministic(self):
        """Same content produces same hash."""
        pack1 = ContextPack(
            question="Same question",
            evidence_index=[],
            tables_summary=TablesSummary(),
            documents_summary=DocumentsSummary(),
        )
        pack2 = ContextPack(
            question="Same question",
            evidence_index=[],
            tables_summary=TablesSummary(),
            documents_summary=DocumentsSummary(),
        )
        
        hash1 = pack1.freeze()
        hash2 = pack2.freeze()
        
        assert hash1 == hash2

    def test_freeze_hash_different_for_different_content(self):
        """Different content produces different hash."""
        pack1 = ContextPack(
            question="Question 1",
            evidence_index=[],
            tables_summary=TablesSummary(),
            documents_summary=DocumentsSummary(),
        )
        pack2 = ContextPack(
            question="Question 2",
            evidence_index=[],
            tables_summary=TablesSummary(),
            documents_summary=DocumentsSummary(),
        )
        
        hash1 = pack1.freeze()
        hash2 = pack2.freeze()
        
        assert hash1 != hash2


# ==============================
# Freeze Guard Tests (INT-CP-FREEZE-003)
# ==============================
class TestContextPackFreezeGuards:
    """Tests for freeze guards on mutating methods."""

    def test_add_evidence_blocked_when_frozen_int_cp_freeze_003(self):
        """INT-CP-FREEZE-003: Modification attempts raise ContextPackFrozenError."""
        pack = create_test_context_pack()
        pack.freeze()
        
        entry = EvidenceIndexEntry(
            evidence_id="test",
            source_tool="test_tool",
            type="table",
        )
        
        with pytest.raises(ContextPackFrozenError):
            pack.add_evidence(entry)

    def test_add_assumption_blocked_when_frozen(self):
        """add_assumption raises ContextPackFrozenError when frozen."""
        pack = create_test_context_pack()
        pack.freeze()
        
        with pytest.raises(ContextPackFrozenError):
            pack.add_assumption("New assumption")

    def test_add_hypothesis_set_blocked_when_frozen(self):
        """add_hypothesis_set raises ContextPackFrozenError when frozen."""
        from core.contracts.hypothesis_schema import HypothesisSet

        pack = create_test_context_pack()
        pack.freeze()
        
        with pytest.raises(ContextPackFrozenError):
            pack.add_hypothesis_set(HypothesisSet())

    def test_set_limit_blocked_when_frozen(self):
        """set_limit raises ContextPackFrozenError when frozen."""
        pack = create_test_context_pack()
        pack.freeze()
        
        with pytest.raises(ContextPackFrozenError):
            pack.set_limit("max_items", 100)


# ==============================
# Unfrozen Mutation Tests
# ==============================
class TestContextPackUnfrozenMutations:
    """Tests that mutations work when not frozen."""

    def test_add_evidence_works_when_not_frozen(self):
        """add_evidence works on unfrozen pack."""
        pack = create_test_context_pack()
        
        entry = EvidenceIndexEntry(
            evidence_id="test",
            source_tool="test_tool",
            type="table",
        )
        
        pack.add_evidence(entry)
        
        assert len(pack.evidence_index) == 1

    def test_add_assumption_works_when_not_frozen(self):
        """add_assumption works on unfrozen pack."""
        pack = create_test_context_pack()
        
        pack.add_assumption("Test assumption")
        
        assert "Test assumption" in pack.assumptions

    def test_set_limit_works_when_not_frozen(self):
        """set_limit works on unfrozen pack."""
        pack = create_test_context_pack()
        
        pack.set_limit("max_items", 50)
        
        assert pack.limits["max_items"] == 50


# ==============================
# Utility Method Tests
# ==============================
class TestContextPackUtilityMethods:
    """Tests for ContextPack utility methods."""

    def test_get_evidence_count(self):
        """get_evidence_count returns correct count."""
        pack = create_test_context_pack()
        
        assert pack.get_evidence_count() == 0
        
        pack.add_evidence(EvidenceIndexEntry(
            evidence_id="e1",
            source_tool="tool1",
            type="table",
        ))
        
        assert pack.get_evidence_count() == 1

    def test_get_freeze_payload(self):
        """get_freeze_payload returns correct payload."""
        pack = create_test_context_pack()
        pack.add_evidence(EvidenceIndexEntry(
            evidence_id="e1",
            source_tool="tool1",
            type="table",
        ))
        pack.freeze()
        
        payload = pack.get_freeze_payload(run_id="test-run")
        
        assert payload["run_id"] == "test-run"
        assert payload["frozen_hash"] == pack.frozen_hash
        assert payload["evidence_count"] == 1
        assert payload["frozen_at"] is not None
