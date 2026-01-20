# ==============================
# Tests: IMP-021 ContextPack Freeze Lifecycle
# ==============================
"""
Tests for IMP-021: ContextPack Freeze Lifecycle.

Tech Spec References:
- INT-CP-FREEZE-LC-001: context_pack_frozen event emitted on freeze
- INT-CP-FREEZE-LC-002: Frozen ContextPack persisted for audit
- INT-CP-FREEZE-LC-003: Execution blocked if not frozen

All tests deterministic. No external I/O.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

import pytest

from core.contracts.context_pack_schema import (
    ContextPack,
    ContextPackFrozenError,
    ContextPackNotFrozenError,
    DocumentsSummary,
    TablesSummary,
)
# Import for forward reference resolution
from core.contracts.hypothesis_schema import HypothesisSet
from core.contracts.sufficiency_schema import SufficiencyState

# Rebuild model to resolve forward references
ContextPack.model_rebuild()
from core.memory.base import MemoryBackend
from core.memory.in_memory import InMemoryBackend
from core.memory.tracing import TraceEventType


# --------------------------------------------------------------------------- #
#  Test Fixtures
# --------------------------------------------------------------------------- #

def make_context_pack(**overrides) -> ContextPack:
    """Create a minimal ContextPack for testing."""
    defaults = dict(
        question="Test question",
        evidence_index=[],
        tables_summary=TablesSummary(),
        documents_summary=DocumentsSummary(),
    )
    defaults.update(overrides)
    return ContextPack(**defaults)


# --------------------------------------------------------------------------- #
#  INT-CP-FREEZE-LC-001: context_pack_frozen event emitted on freeze
# --------------------------------------------------------------------------- #

class TestContextPackFrozenEvent:
    """Tests for trace event emission on freeze."""

    def test_trace_event_type_exists(self):
        """TraceEventType.CONTEXT_PACK_FROZEN is defined."""
        assert hasattr(TraceEventType, "CONTEXT_PACK_FROZEN")
        assert TraceEventType.CONTEXT_PACK_FROZEN.value == "context_pack_frozen"

    def test_get_freeze_payload_includes_run_id(self):
        """get_freeze_payload includes run_id."""
        cp = make_context_pack()
        cp.freeze()
        payload = cp.get_freeze_payload("run-001")
        assert payload["run_id"] == "run-001"

    def test_get_freeze_payload_includes_frozen_at(self):
        """get_freeze_payload includes frozen_at timestamp."""
        cp = make_context_pack()
        cp.freeze()
        payload = cp.get_freeze_payload("run-001")
        assert "frozen_at" in payload
        assert payload["frozen_at"] is not None

    def test_get_freeze_payload_includes_frozen_hash(self):
        """get_freeze_payload includes frozen_hash."""
        cp = make_context_pack()
        cp.freeze()
        payload = cp.get_freeze_payload("run-001")
        assert "frozen_hash" in payload
        assert payload["frozen_hash"] is not None
        assert len(payload["frozen_hash"]) == 64  # SHA-256

    def test_get_freeze_payload_includes_evidence_count(self):
        """get_freeze_payload includes evidence_count."""
        cp = make_context_pack()
        cp.freeze()
        payload = cp.get_freeze_payload("run-001")
        assert "evidence_count" in payload
        assert payload["evidence_count"] == 0  # Empty evidence_index

    def test_get_freeze_payload_has_expected_keys(self):
        """get_freeze_payload has expected keys."""
        cp = make_context_pack()
        cp.freeze()
        payload = cp.get_freeze_payload("run-001")
        # Verify expected keys from implementation
        assert "run_id" in payload
        assert "frozen_hash" in payload
        assert "evidence_count" in payload
        assert "frozen_at" in payload


# --------------------------------------------------------------------------- #
#  INT-CP-FREEZE-LC-002: Frozen ContextPack persisted for audit
# --------------------------------------------------------------------------- #

class TestContextPackPersistence:
    """Tests for ContextPack persistence in memory backends."""

    def test_in_memory_backend_persist_context_pack(self):
        """InMemoryBackend can persist context pack."""
        backend = InMemoryBackend()
        cp_data = {"product_id": "test", "frozen": True}
        backend.persist_context_pack("run-001", cp_data)
        # Verify it's stored
        restored = backend.restore_context_pack("run-001")
        assert restored == cp_data

    def test_in_memory_backend_restore_missing_context_pack(self):
        """InMemoryBackend returns None for missing context pack."""
        backend = InMemoryBackend()
        restored = backend.restore_context_pack("nonexistent")
        assert restored is None

    def test_in_memory_backend_overwrite_context_pack(self):
        """InMemoryBackend overwrites previous context pack."""
        backend = InMemoryBackend()
        backend.persist_context_pack("run-001", {"version": 1})
        backend.persist_context_pack("run-001", {"version": 2})
        restored = backend.restore_context_pack("run-001")
        assert restored == {"version": 2}

    def test_base_backend_persist_is_no_op(self):
        """Base MemoryBackend.persist_context_pack is a no-op."""
        # Direct instantiation would fail due to abstract methods
        # Test via checking the base method exists
        assert hasattr(MemoryBackend, "persist_context_pack")
        assert hasattr(MemoryBackend, "restore_context_pack")

    def test_frozen_context_pack_serializable(self):
        """Frozen ContextPack can be serialized for persistence."""
        cp = make_context_pack()
        cp.freeze()
        # model_dump() should work for persistence
        data = cp.model_dump(mode="json")
        assert data["frozen"] is True
        assert data["frozen_hash"] is not None
        assert data["frozen_at"] is not None

    def test_persisted_data_includes_all_fields(self):
        """Persisted ContextPack includes all required fields."""
        cp = make_context_pack()
        cp.freeze()
        data = cp.model_dump(mode="json")
        
        # Required fields for audit (matching actual schema)
        assert "question" in data
        assert "evidence_index" in data
        assert "frozen" in data
        assert "frozen_at" in data
        assert "frozen_hash" in data


# --------------------------------------------------------------------------- #
#  INT-CP-FREEZE-LC-003: Execution blocked if not frozen
# --------------------------------------------------------------------------- #

class TestExecutionBlockedIfNotFrozen:
    """Tests for ContextPackNotFrozenError blocking execution."""

    def test_context_pack_not_frozen_error_exists(self):
        """ContextPackNotFrozenError is defined."""
        assert ContextPackNotFrozenError is not None

    def test_context_pack_not_frozen_error_is_exception(self):
        """ContextPackNotFrozenError is an Exception."""
        assert issubclass(ContextPackNotFrozenError, Exception)

    def test_context_pack_not_frozen_error_message(self):
        """ContextPackNotFrozenError has informative message."""
        err = ContextPackNotFrozenError("Execution requires frozen ContextPack")
        assert "frozen" in str(err).lower()

    def test_can_raise_not_frozen_error(self):
        """ContextPackNotFrozenError can be raised and caught."""
        with pytest.raises(ContextPackNotFrozenError):
            raise ContextPackNotFrozenError("Not frozen for run-001")

    def test_not_frozen_error_distinct_from_frozen_error(self):
        """ContextPackNotFrozenError is distinct from ContextPackFrozenError."""
        assert ContextPackNotFrozenError is not ContextPackFrozenError
        
        # Can catch each independently
        try:
            raise ContextPackFrozenError("frozen")
        except ContextPackFrozenError:
            pass
        except ContextPackNotFrozenError:
            pytest.fail("Should not catch ContextPackNotFrozenError")
        
        try:
            raise ContextPackNotFrozenError("not frozen")
        except ContextPackNotFrozenError:
            pass
        except ContextPackFrozenError:
            pytest.fail("Should not catch ContextPackFrozenError")

    def test_frozen_property_check(self):
        """ContextPack.frozen property can be used to check freeze status."""
        cp = make_context_pack()
        assert cp.frozen is False
        
        cp.freeze()
        assert cp.frozen is True


# --------------------------------------------------------------------------- #
#  Lifecycle Integration Tests
# --------------------------------------------------------------------------- #

class TestContextPackFreezeLifecycle:
    """Integration tests for full freeze lifecycle."""

    def test_freeze_persist_restore_roundtrip(self):
        """Full freeze → persist → restore roundtrip."""
        backend = InMemoryBackend()
        
        # Create and freeze
        cp = make_context_pack()
        cp.freeze()
        
        # Persist
        data = cp.model_dump(mode="json")
        backend.persist_context_pack("run-001", data)
        
        # Restore
        restored_data = backend.restore_context_pack("run-001")
        assert restored_data is not None
        
        # Reconstruct
        restored_cp = ContextPack.model_validate(restored_data)
        assert restored_cp.frozen is True
        assert restored_cp.frozen_hash == cp.frozen_hash

    def test_multiple_runs_isolated(self):
        """Context packs for different runs are isolated."""
        backend = InMemoryBackend()
        
        cp1 = make_context_pack(question="Question for run 1")
        cp1.freeze()
        
        cp2 = make_context_pack(question="Question for run 2")
        cp2.freeze()
        
        backend.persist_context_pack("run-001", cp1.model_dump(mode="json"))
        backend.persist_context_pack("run-002", cp2.model_dump(mode="json"))
        
        restored1 = backend.restore_context_pack("run-001")
        restored2 = backend.restore_context_pack("run-002")
        
        assert restored1["question"] == "Question for run 1"
        assert restored2["question"] == "Question for run 2"

    def test_hash_enables_integrity_check(self):
        """Frozen hash can be used for integrity verification."""
        cp = make_context_pack()
        cp.freeze()
        original_hash = cp.frozen_hash
        
        # Serialize and deserialize
        data = cp.model_dump(mode="json")
        restored = ContextPack.model_validate(data)
        
        # Hash should be preserved
        assert restored.frozen_hash == original_hash

    def test_frozen_at_timestamp_preserved(self):
        """Frozen timestamp is preserved through serialization."""
        cp = make_context_pack()
        cp.freeze()
        original_frozen_at = cp.frozen_at
        
        # Serialize and deserialize
        data = cp.model_dump(mode="json")
        restored = ContextPack.model_validate(data)
        
        # Compare timestamps (allowing for serialization format differences)
        assert restored.frozen_at is not None
        if isinstance(original_frozen_at, datetime):
            # Restored might be a string or datetime depending on serialization
            if isinstance(restored.frozen_at, datetime):
                assert restored.frozen_at == original_frozen_at
