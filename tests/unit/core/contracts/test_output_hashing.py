# ==============================
# Tests for IMP-029: Output Hashing for Reproducibility
# ==============================
"""
Test suite for output hashing.

IMP-029: MEM-REPRO-020, MEM-REPRO-021
BRD: BRD-OPS-061
"""

import pytest
from unittest.mock import MagicMock

from core.contracts.run_schema import RunRecord, RunStatus
from core.utils.hashing import compute_output_hash


# ==============================
# RunRecord output_hash Field
# ==============================

class TestRunRecordOutputHash:
    """Tests for RunRecord.output_hash field."""
    
    def test_run_record_has_output_hash_field(self):
        """MEM-REPRO-020: RunRecord includes output_hash field."""
        run = RunRecord(product="test", flow="test_flow")
        assert hasattr(run, "output_hash")
    
    def test_run_record_output_hash_optional(self):
        """output_hash is optional (None by default)."""
        run = RunRecord(product="test", flow="test_flow")
        assert run.output_hash is None
    
    def test_run_record_with_output_hash(self):
        """RunRecord can store output_hash."""
        output = {"result": "success", "data": [1, 2, 3]}
        output_hash = compute_output_hash(output)
        run = RunRecord(
            product="test",
            flow="test_flow",
            output=output,
            output_hash=output_hash,
        )
        assert run.output_hash == output_hash
    
    def test_output_hash_is_sha256(self):
        """Output hash is 64 char hex (SHA-256)."""
        output = {"result": "success"}
        output_hash = compute_output_hash(output)
        run = RunRecord(
            product="test",
            flow="test_flow",
            output_hash=output_hash,
        )
        assert len(run.output_hash) == 64


# ==============================
# compute_output_hash Function
# ==============================

class TestComputeOutputHash:
    """Tests for compute_output_hash function."""
    
    def test_compute_output_hash_dict(self):
        """compute_output_hash handles dict output."""
        output = {"result": "success", "count": 42}
        result = compute_output_hash(output)
        assert len(result) == 64
    
    def test_compute_output_hash_deterministic(self):
        """compute_output_hash is deterministic."""
        output = {"result": "success"}
        hash1 = compute_output_hash(output)
        hash2 = compute_output_hash(output)
        assert hash1 == hash2
    
    def test_compute_output_hash_none(self):
        """compute_output_hash handles None."""
        result = compute_output_hash(None)
        assert len(result) == 64
    
    def test_compute_output_hash_nested(self):
        """compute_output_hash handles nested structures."""
        output = {
            "result": {
                "level1": {
                    "level2": "value"
                }
            }
        }
        result = compute_output_hash(output)
        assert len(result) == 64
    
    def test_compute_output_hash_with_list(self):
        """compute_output_hash handles lists."""
        output = {"items": [1, 2, 3, 4, 5]}
        result = compute_output_hash(output)
        assert len(result) == 64


# ==============================
# complete_run Integration
# ==============================

class TestCompleteRunOutputHash:
    """Tests for complete_run output hash integration."""
    
    def test_complete_run_computes_output_hash(self):
        """complete_run computes and includes output_hash in event."""
        from core.contracts.flow_schema import AutonomyLevel
        from core.orchestrator.run_lifecycle import complete_run
        
        memory = MagicMock()
        memory.get_run = MagicMock(return_value=MagicMock(
            run=RunRecord(
                run_id="test-run-001",
                product="test",
                flow="test_flow",
                status=RunStatus.COMPLETED,
            )
        ))
        
        events_captured = []
        def capture_emit(**kwargs):
            events_captured.append(kwargs)
        
        output = {"result": "success", "data": {"value": 123}}
        
        complete_run(
            memory=memory,
            emit_event_fn=capture_emit,
            run_id="test-run-001",
            product="test",
            flow="test_flow",
            current_status=RunStatus.RUNNING,
            output=output,
            summary={},
        )
        
        # Find run_completed event
        completed_events = [e for e in events_captured if e.get("kind") == "run_completed"]
        assert len(completed_events) >= 1
        
        # Verify output_hash is in payload
        payload = completed_events[0].get("payload", {})
        assert "output_hash" in payload
        assert len(payload["output_hash"]) == 64
        
        # Verify hash matches output
        expected_hash = compute_output_hash(output)
        assert payload["output_hash"] == expected_hash
    
    def test_complete_run_output_hash_stored(self):
        """complete_run stores output_hash via memory update."""
        from core.orchestrator.run_lifecycle import complete_run
        
        memory = MagicMock()
        memory.get_run = MagicMock(return_value=MagicMock(
            run=RunRecord(
                run_id="test-run-001",
                product="test",
                flow="test_flow",
                status=RunStatus.COMPLETED,
            )
        ))
        
        output = {"result": "success"}
        
        complete_run(
            memory=memory,
            emit_event_fn=MagicMock(),
            run_id="test-run-001",
            product="test",
            flow="test_flow",
            current_status=RunStatus.RUNNING,
            output=output,
            summary={},
        )
        
        # Verify update_run_status was called with output_hash
        update_calls = [c for c in memory.update_run_status.call_args_list]
        hash_updates = [c for c in update_calls if "output_hash" in str(c)]
        assert len(hash_updates) >= 1


# ==============================
# fail_run Integration
# ==============================

class TestFailRunOutputHash:
    """Tests for fail_run output hash integration."""
    
    def test_fail_run_computes_output_hash(self):
        """fail_run computes and includes output_hash in event."""
        from core.orchestrator.run_lifecycle import fail_run
        
        memory = MagicMock()
        memory.get_run = MagicMock(return_value=MagicMock(
            run=RunRecord(
                run_id="test-run-002",
                product="test",
                flow="test_flow",
                status=RunStatus.FAILED,
            )
        ))
        
        events_captured = []
        def capture_emit(**kwargs):
            events_captured.append(kwargs)
        
        fail_run(
            memory=memory,
            emit_event_fn=capture_emit,
            run_id="test-run-002",
            product="test",
            flow="test_flow",
            current_status=RunStatus.RUNNING,
            error_code="TEST_ERROR",
            error_message="Test error message",
        )
        
        # Find run_failed event
        failed_events = [e for e in events_captured if e.get("kind") == "run_failed"]
        assert len(failed_events) >= 1
        
        # Verify output_hash is in payload
        payload = failed_events[0].get("payload", {})
        assert "output_hash" in payload
        assert len(payload["output_hash"]) == 64
    
    def test_fail_run_error_output_hash(self):
        """fail_run hashes error code and message."""
        from core.orchestrator.run_lifecycle import fail_run
        
        memory = MagicMock()
        memory.get_run = MagicMock(return_value=MagicMock(
            run=RunRecord(
                run_id="test-run-003",
                product="test",
                flow="test_flow",
                status=RunStatus.FAILED,
            )
        ))
        
        events_captured = []
        def capture_emit(**kwargs):
            events_captured.append(kwargs)
        
        error_code = "VALIDATION_ERROR"
        error_message = "Input validation failed"
        
        fail_run(
            memory=memory,
            emit_event_fn=capture_emit,
            run_id="test-run-003",
            product="test",
            flow="test_flow",
            current_status=RunStatus.RUNNING,
            error_code=error_code,
            error_message=error_message,
        )
        
        # Verify hash matches error output
        expected_hash = compute_output_hash({
            "error_code": error_code,
            "error_message": error_message,
        })
        
        failed_events = [e for e in events_captured if e.get("kind") == "run_failed"]
        payload = failed_events[0].get("payload", {})
        assert payload["output_hash"] == expected_hash


# ==============================
# Acceptance Checks
# ==============================

class TestAcceptanceChecks:
    """Acceptance criteria from imp_plan.md."""
    
    def test_all_outputs_hashed_sha256(self):
        """AC: All outputs hashed using SHA-256."""
        output = {"test": "output"}
        result = compute_output_hash(output)
        assert len(result) == 64  # SHA-256 = 64 hex chars
    
    def test_output_hash_recorded_in_terminal_event(self):
        """AC: output_hash recorded in terminal event."""
        from core.orchestrator.run_lifecycle import complete_run
        
        memory = MagicMock()
        memory.get_run = MagicMock(return_value=MagicMock(
            run=RunRecord(
                run_id="test-run",
                product="test",
                flow="test_flow",
                status=RunStatus.COMPLETED,
            )
        ))
        
        events = []
        def capture(**kwargs):
            events.append(kwargs)
        
        complete_run(
            memory=memory,
            emit_event_fn=capture,
            run_id="test-run",
            product="test",
            flow="test_flow",
            current_status=RunStatus.RUNNING,
            output={"done": True},
        )
        
        # Terminal event should have output_hash
        terminal = [e for e in events if e.get("kind") == "run_completed"]
        assert len(terminal) > 0
        assert "output_hash" in terminal[0]["payload"]
    
    def test_hash_stored_in_run_record(self):
        """AC: Hash stored in RunRecord."""
        run = RunRecord(
            product="test",
            flow="test_flow",
            output={"result": "done"},
            output_hash=compute_output_hash({"result": "done"}),
        )
        assert run.output_hash is not None
        assert len(run.output_hash) == 64
