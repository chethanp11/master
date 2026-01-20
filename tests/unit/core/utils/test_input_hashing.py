# ==============================
# Tests for IMP-028: Input Hashing for Reproducibility
# ==============================
"""
Test suite for input hashing utilities.

IMP-028: MEM-REPRO-010, MEM-REPRO-011, MEM-REPRO-012
BRD: BRD-OPS-061
"""

import pytest
import json
import hashlib
from datetime import datetime, date

from core.utils.hashing import (
    CanonicalJSONEncoder,
    compute_hash,
    compute_input_hash,
    compute_output_hash,
    verify_hash,
)
from core.contracts.run_schema import RunRecord
from core.contracts.context_pack_schema import (
    ContextPack,
    EvidenceIndexEntry,
    TablesSummary,
    DocumentsSummary,
)


# ==============================
# MEM-REPRO-010: Canonical JSON Serialization
# ==============================

class TestCanonicalJSONEncoder:
    """Tests for CanonicalJSONEncoder."""
    
    def test_encoder_handles_dict(self):
        """Encoder serializes dict."""
        data = {"b": 2, "a": 1}
        result = json.dumps(data, cls=CanonicalJSONEncoder, sort_keys=True)
        assert result == '{"a": 1, "b": 2}'
    
    def test_encoder_handles_datetime(self):
        """Encoder serializes datetime to ISO format."""
        dt = datetime(2025, 1, 20, 12, 0, 0)
        result = json.dumps({"time": dt}, cls=CanonicalJSONEncoder)
        assert "2025-01-20T12:00:00" in result
    
    def test_encoder_handles_date(self):
        """Encoder serializes date to ISO format."""
        d = date(2025, 1, 20)
        result = json.dumps({"date": d}, cls=CanonicalJSONEncoder)
        assert "2025-01-20" in result
    
    def test_encoder_handles_set(self):
        """Encoder serializes set to sorted list."""
        data = {"items": {3, 1, 2}}
        result = json.dumps(data, cls=CanonicalJSONEncoder, sort_keys=True)
        parsed = json.loads(result)
        assert parsed["items"] == [1, 2, 3]
    
    def test_encoder_handles_nested_structure(self):
        """Encoder handles nested structures."""
        data = {
            "outer": {
                "inner": [1, 2, 3],
                "date": date(2025, 1, 1),
            }
        }
        result = json.dumps(data, cls=CanonicalJSONEncoder, sort_keys=True)
        assert '"inner": [1, 2, 3]' in result


# ==============================
# MEM-REPRO-011: SHA-256 Hashing
# ==============================

class TestComputeHash:
    """Tests for compute_hash function."""
    
    def test_compute_hash_returns_string(self):
        """MEM-REPRO-011: compute_hash returns string."""
        result = compute_hash({"key": "value"})
        assert isinstance(result, str)
    
    def test_compute_hash_sha256_length(self):
        """MEM-REPRO-011: SHA-256 hash is 64 hex characters."""
        result = compute_hash({"key": "value"})
        assert len(result) == 64
        # Verify it's valid hex
        int(result, 16)
    
    def test_compute_hash_deterministic(self):
        """MEM-REPRO-011: Same input produces same hash."""
        data = {"key": "value", "number": 42}
        hash1 = compute_hash(data)
        hash2 = compute_hash(data)
        assert hash1 == hash2
    
    def test_compute_hash_key_order_independent(self):
        """MEM-REPRO-012: Hash is independent of key order."""
        data1 = {"a": 1, "b": 2, "c": 3}
        data2 = {"c": 3, "b": 2, "a": 1}
        assert compute_hash(data1) == compute_hash(data2)
    
    def test_compute_hash_different_data_different_hash(self):
        """Different data produces different hash."""
        hash1 = compute_hash({"key": "value1"})
        hash2 = compute_hash({"key": "value2"})
        assert hash1 != hash2
    
    def test_compute_hash_empty_dict(self):
        """Empty dict can be hashed."""
        result = compute_hash({})
        assert isinstance(result, str)
        assert len(result) == 64
    
    def test_compute_hash_nested_data(self):
        """Nested data structures are hashed correctly."""
        data = {
            "level1": {
                "level2": {
                    "value": 123
                }
            }
        }
        result = compute_hash(data)
        assert len(result) == 64
    
    def test_compute_hash_list_data(self):
        """Lists are hashed correctly."""
        data = {"items": [1, 2, 3, 4, 5]}
        result = compute_hash(data)
        assert len(result) == 64
    
    def test_compute_hash_with_datetime(self):
        """Datetime values are handled."""
        data = {"time": datetime(2025, 1, 20, 12, 0, 0)}
        result = compute_hash(data)
        assert len(result) == 64


class TestComputeHashAlgorithms:
    """Tests for different hash algorithms."""
    
    def test_sha256_is_default(self):
        """SHA-256 is default algorithm."""
        data = {"test": "data"}
        result = compute_hash(data)
        # Manually compute to verify
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert result == expected
    
    def test_sha512_algorithm(self):
        """SHA-512 produces 128 character hash."""
        result = compute_hash({"test": "data"}, algorithm="sha512")
        assert len(result) == 128
    
    def test_md5_algorithm(self):
        """MD5 produces 32 character hash."""
        result = compute_hash({"test": "data"}, algorithm="md5")
        assert len(result) == 32
    
    def test_unsupported_algorithm_raises(self):
        """Unsupported algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            compute_hash({"test": "data"}, algorithm="unknown")


# ==============================
# Convenience Functions
# ==============================

class TestInputHash:
    """Tests for compute_input_hash."""
    
    def test_compute_input_hash_dict(self):
        """compute_input_hash handles dict payload."""
        payload = {"user_input": "test query", "params": {"limit": 10}}
        result = compute_input_hash(payload)
        assert len(result) == 64
    
    def test_compute_input_hash_none(self):
        """compute_input_hash handles None payload."""
        result = compute_input_hash(None)
        # Should hash empty dict
        expected = compute_hash({})
        assert result == expected
    
    def test_compute_input_hash_deterministic(self):
        """compute_input_hash is deterministic."""
        payload = {"query": "test"}
        hash1 = compute_input_hash(payload)
        hash2 = compute_input_hash(payload)
        assert hash1 == hash2


class TestOutputHash:
    """Tests for compute_output_hash."""
    
    def test_compute_output_hash_dict(self):
        """compute_output_hash handles dict output."""
        output = {"result": "success", "data": [1, 2, 3]}
        result = compute_output_hash(output)
        assert len(result) == 64
    
    def test_compute_output_hash_none(self):
        """compute_output_hash handles None output."""
        result = compute_output_hash(None)
        expected = compute_hash({})
        assert result == expected


class TestVerifyHash:
    """Tests for verify_hash."""
    
    def test_verify_hash_correct(self):
        """verify_hash returns True for matching hash."""
        data = {"key": "value"}
        computed = compute_hash(data)
        assert verify_hash(data, computed) is True
    
    def test_verify_hash_incorrect(self):
        """verify_hash returns False for non-matching hash."""
        data = {"key": "value"}
        assert verify_hash(data, "wrong_hash") is False
    
    def test_verify_hash_different_algorithm(self):
        """verify_hash works with different algorithms."""
        data = {"key": "value"}
        computed = compute_hash(data, algorithm="sha512")
        assert verify_hash(data, computed, algorithm="sha512") is True


# ==============================
# RunRecord Integration
# ==============================

class TestRunRecordInputHash:
    """Tests for RunRecord.input_hash field."""
    
    def test_run_record_has_input_hash_field(self):
        """RunRecord includes input_hash field."""
        run = RunRecord(product="test", flow="test_flow")
        assert hasattr(run, "input_hash")
    
    def test_run_record_input_hash_optional(self):
        """input_hash is optional (None by default)."""
        run = RunRecord(product="test", flow="test_flow")
        assert run.input_hash is None
    
    def test_run_record_with_input_hash(self):
        """RunRecord can store input_hash."""
        payload = {"query": "test"}
        input_hash = compute_input_hash(payload)
        run = RunRecord(
            product="test",
            flow="test_flow",
            input=payload,
            input_hash=input_hash,
        )
        assert run.input_hash == input_hash
    
    def test_input_hash_matches_input(self):
        """Stored hash matches input data."""
        payload = {"query": "test", "limit": 10}
        input_hash = compute_input_hash(payload)
        run = RunRecord(
            product="test",
            flow="test_flow",
            input=payload,
            input_hash=input_hash,
        )
        # Verify hash matches
        assert verify_hash(payload, run.input_hash)


# ==============================
# ContextPack Integration
# ==============================

class TestContextPackContentHash:
    """Tests for ContextPack.content_hash field."""
    
    @pytest.fixture(autouse=True)
    def setup_model(self):
        """Rebuild ContextPack model for forward references."""
        from core.contracts.hypothesis_schema import HypothesisSet
        from core.contracts.sufficiency_schema import SufficiencyState
        ContextPack.model_rebuild()
    
    def test_context_pack_has_content_hash_field(self):
        """ContextPack includes content_hash field."""
        pack = ContextPack(
            question="test",
            evidence_index=[],
            tables_summary=TablesSummary(stats={}, key_rows=[], column_profiles={}),
            documents_summary=DocumentsSummary(excerpts=[], metadata=[]),
        )
        assert hasattr(pack, "content_hash")
    
    def test_context_pack_content_hash_none_before_freeze(self):
        """content_hash is None before freeze."""
        pack = ContextPack(
            question="test",
            evidence_index=[],
            tables_summary=TablesSummary(stats={}, key_rows=[], column_profiles={}),
            documents_summary=DocumentsSummary(excerpts=[], metadata=[]),
        )
        assert pack.content_hash is None
    
    def test_context_pack_content_hash_set_on_freeze(self):
        """content_hash is set when ContextPack is frozen."""
        pack = ContextPack(
            question="test",
            evidence_index=[],
            tables_summary=TablesSummary(stats={}, key_rows=[], column_profiles={}),
            documents_summary=DocumentsSummary(excerpts=[], metadata=[]),
        )
        pack.freeze()
        assert pack.content_hash is not None
        assert len(pack.content_hash) == 64
    
    def test_content_hash_matches_frozen_hash(self):
        """content_hash matches frozen_hash."""
        pack = ContextPack(
            question="test question",
            evidence_index=[],
            tables_summary=TablesSummary(stats={}, key_rows=[], column_profiles={}),
            documents_summary=DocumentsSummary(excerpts=[], metadata=[]),
        )
        frozen_hash = pack.freeze()
        assert pack.content_hash == frozen_hash
        assert pack.frozen_hash == frozen_hash


# ==============================
# start_run Integration
# ==============================

class TestStartRunInputHash:
    """Tests for start_run input hash integration."""
    
    def test_start_run_computes_input_hash(self):
        """start_run computes and stores input_hash."""
        from unittest.mock import MagicMock
        from core.contracts.flow_schema import FlowDef, AutonomyLevel
        from core.orchestrator.context import RunContext
        from core.orchestrator.run_lifecycle import start_run
        
        memory = MagicMock()
        memory.create_run = MagicMock()
        
        flow_def = MagicMock(spec=FlowDef)
        flow_def.autonomy_level = AutonomyLevel.SEMI_AUTO
        flow_def.steps = []
        
        payload = {"query": "test", "limit": 10}
        run_ctx = RunContext(
            run_id="test-run-001",
            product="test",
            flow="test_flow",
            payload=payload,
            meta={},
        )
        
        emit_fn = MagicMock()
        
        run_record = start_run(
            memory=memory,
            flow_def=flow_def,
            run_ctx=run_ctx,
            emit_event_fn=emit_fn,
        )
        
        # Verify input_hash is set
        assert run_record.input_hash is not None
        assert len(run_record.input_hash) == 64
        
        # Verify hash matches input
        expected_hash = compute_input_hash(payload)
        assert run_record.input_hash == expected_hash
    
    def test_start_run_input_hash_none_payload(self):
        """start_run handles None payload."""
        from unittest.mock import MagicMock
        from core.contracts.flow_schema import FlowDef, AutonomyLevel
        from core.orchestrator.context import RunContext
        from core.orchestrator.run_lifecycle import start_run
        
        memory = MagicMock()
        memory.create_run = MagicMock()
        
        flow_def = MagicMock(spec=FlowDef)
        flow_def.autonomy_level = AutonomyLevel.SEMI_AUTO
        flow_def.steps = []
        
        run_ctx = RunContext(
            run_id="test-run-002",
            product="test",
            flow="test_flow",
            payload=None,
            meta={},
        )
        
        emit_fn = MagicMock()
        
        run_record = start_run(
            memory=memory,
            flow_def=flow_def,
            run_ctx=run_ctx,
            emit_event_fn=emit_fn,
        )
        
        # Verify input_hash is set (empty dict hash)
        assert run_record.input_hash is not None
        assert run_record.input_hash == compute_input_hash(None)


# ==============================
# Acceptance Checks
# ==============================

class TestAcceptanceChecks:
    """Acceptance criteria from imp_plan.md."""
    
    def test_all_inputs_hashed_sha256(self):
        """AC: All inputs hashed using SHA-256."""
        # Default is SHA-256
        data = {"test": "input"}
        result = compute_hash(data)
        # Verify it's SHA-256 (64 chars)
        assert len(result) == 64
    
    def test_input_hash_from_canonical_json(self):
        """AC: input_hash computed from canonical JSON."""
        data = {"z": 1, "a": 2}
        # Canonical = sorted keys, minimal separators
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert compute_hash(data) == expected
    
    def test_context_pack_includes_content_hash(self):
        """AC: ContextPack includes content_hash before freeze."""
        from core.contracts.hypothesis_schema import HypothesisSet
        from core.contracts.sufficiency_schema import SufficiencyState
        ContextPack.model_rebuild()
        
        pack = ContextPack(
            question="test",
            evidence_index=[],
            tables_summary=TablesSummary(stats={}, key_rows=[], column_profiles={}),
            documents_summary=DocumentsSummary(excerpts=[], metadata=[]),
        )
        pack.freeze()
        # After freeze, content_hash should be set
        assert pack.content_hash is not None
