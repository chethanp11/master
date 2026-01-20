# ==============================
# Tests for IMP-030: Reproducibility Validation API
# ==============================
"""
Test suite for reproducibility validation.

IMP-030: MEM-REPRO-030, MEM-REPRO-031, MEM-REPRO-032
BRD: BRD-OPS-061
"""

import pytest
from unittest.mock import MagicMock

from core.contracts.run_schema import RunRecord, Versions
from core.utils.hashing import compute_input_hash, compute_output_hash
from core.memory.reproducibility import (
    Discrepancy,
    ReproducibilityResult,
    validate_reproducibility,
    validate_input_hash,
    validate_output_hash,
    validate_version_consistency,
    create_reproducibility_snapshot,
)


# ==============================
# MEM-REPRO-032: Discrepancy Model
# ==============================

class TestDiscrepancy:
    """Tests for Discrepancy dataclass."""
    
    def test_discrepancy_has_field(self):
        """Discrepancy has field attribute."""
        d = Discrepancy(
            field="input_hash",
            expected_hash="abc123",
            actual_hash="def456",
        )
        assert d.field == "input_hash"
    
    def test_discrepancy_has_expected_hash(self):
        """Discrepancy has expected_hash attribute."""
        d = Discrepancy(
            field="input_hash",
            expected_hash="abc123",
            actual_hash="def456",
        )
        assert d.expected_hash == "abc123"
    
    def test_discrepancy_has_actual_hash(self):
        """Discrepancy has actual_hash attribute."""
        d = Discrepancy(
            field="input_hash",
            expected_hash="abc123",
            actual_hash="def456",
        )
        assert d.actual_hash == "def456"
    
    def test_discrepancy_has_details(self):
        """Discrepancy has optional details."""
        d = Discrepancy(
            field="input_hash",
            expected_hash="abc123",
            actual_hash="def456",
            details="Input data was modified",
        )
        assert d.details == "Input data was modified"
    
    def test_discrepancy_to_dict(self):
        """Discrepancy serializes to dict."""
        d = Discrepancy(
            field="output_hash",
            expected_hash="abc",
            actual_hash="def",
            details="Mismatch",
        )
        result = d.to_dict()
        assert result["field"] == "output_hash"
        assert result["expected_hash"] == "abc"
        assert result["actual_hash"] == "def"
        assert result["details"] == "Mismatch"


# ==============================
# MEM-REPRO-031: ReproducibilityResult Model
# ==============================

class TestReproducibilityResult:
    """Tests for ReproducibilityResult dataclass."""
    
    def test_result_has_run_id(self):
        """Result has run_id."""
        result = ReproducibilityResult(run_id="run-001", is_reproducible=True)
        assert result.run_id == "run-001"
    
    def test_result_has_is_reproducible(self):
        """Result has is_reproducible boolean."""
        result = ReproducibilityResult(run_id="run-001", is_reproducible=True)
        assert result.is_reproducible is True
        
        result2 = ReproducibilityResult(run_id="run-002", is_reproducible=False)
        assert result2.is_reproducible is False
    
    def test_result_has_discrepancies(self):
        """Result has discrepancies list."""
        d = Discrepancy(field="input_hash", expected_hash="a", actual_hash="b")
        result = ReproducibilityResult(
            run_id="run-001",
            is_reproducible=False,
            discrepancies=[d],
        )
        assert len(result.discrepancies) == 1
        assert result.discrepancies[0].field == "input_hash"
    
    def test_result_defaults_to_empty_discrepancies(self):
        """Result defaults to empty discrepancies."""
        result = ReproducibilityResult(run_id="run-001", is_reproducible=True)
        assert result.discrepancies == []
    
    def test_result_has_verified_fields(self):
        """Result has verified_fields list."""
        result = ReproducibilityResult(
            run_id="run-001",
            is_reproducible=True,
            verified_fields=["input_hash", "output_hash"],
        )
        assert "input_hash" in result.verified_fields
        assert "output_hash" in result.verified_fields
    
    def test_result_has_skipped_fields(self):
        """Result has skipped_fields list."""
        result = ReproducibilityResult(
            run_id="run-001",
            is_reproducible=True,
            skipped_fields=["output_hash"],
        )
        assert "output_hash" in result.skipped_fields
    
    def test_result_to_dict(self):
        """Result serializes to dict."""
        result = ReproducibilityResult(
            run_id="run-001",
            is_reproducible=True,
            verified_fields=["input_hash"],
        )
        d = result.to_dict()
        assert d["run_id"] == "run-001"
        assert d["is_reproducible"] is True
        assert d["verified_fields"] == ["input_hash"]
    
    def test_result_summary_reproducible(self):
        """Summary for reproducible run."""
        result = ReproducibilityResult(
            run_id="run-001",
            is_reproducible=True,
            verified_fields=["input_hash", "output_hash"],
        )
        assert "reproducible" in result.summary.lower()
        assert "2 fields verified" in result.summary
    
    def test_result_summary_not_reproducible(self):
        """Summary for non-reproducible run."""
        result = ReproducibilityResult(
            run_id="run-001",
            is_reproducible=False,
            discrepancies=[Discrepancy(field="x", expected_hash="a", actual_hash="b")],
        )
        assert "NOT reproducible" in result.summary
        assert "1 discrepancies" in result.summary
    
    def test_result_summary_error(self):
        """Summary for error case."""
        result = ReproducibilityResult(
            run_id="run-001",
            is_reproducible=False,
            error="Run not found",
        )
        assert "failed" in result.summary.lower()
        assert "Run not found" in result.summary


# ==============================
# MEM-REPRO-030: validate_reproducibility
# ==============================

class TestValidateReproducibility:
    """Tests for validate_reproducibility function."""
    
    def test_validate_reproducibility_returns_result(self):
        """validate_reproducibility returns ReproducibilityResult."""
        payload = {"query": "test"}
        input_hash = compute_input_hash(payload)
        
        run = RunRecord(
            run_id="run-001",
            product="test",
            flow="test_flow",
            input=payload,
            input_hash=input_hash,
        )
        
        result = validate_reproducibility("run-001", run_record=run)
        assert isinstance(result, ReproducibilityResult)
    
    def test_validate_reproducibility_valid_input(self):
        """validate_reproducibility passes with valid input hash."""
        payload = {"query": "test", "limit": 10}
        input_hash = compute_input_hash(payload)
        
        run = RunRecord(
            run_id="run-001",
            product="test",
            flow="test_flow",
            input=payload,
            input_hash=input_hash,
        )
        
        result = validate_reproducibility("run-001", run_record=run)
        assert result.is_reproducible is True
        assert "input_hash" in result.verified_fields
        assert len(result.discrepancies) == 0
    
    def test_validate_reproducibility_invalid_input(self):
        """validate_reproducibility fails with invalid input hash."""
        payload = {"query": "test"}
        
        run = RunRecord(
            run_id="run-001",
            product="test",
            flow="test_flow",
            input=payload,
            input_hash="wrong_hash_value",  # Invalid hash
        )
        
        result = validate_reproducibility("run-001", run_record=run)
        assert result.is_reproducible is False
        assert len(result.discrepancies) == 1
        assert result.discrepancies[0].field == "input_hash"
    
    def test_validate_reproducibility_valid_output(self):
        """validate_reproducibility passes with valid output hash."""
        output = {"result": "success"}
        output_hash = compute_output_hash(output)
        input_hash = compute_input_hash({})
        
        run = RunRecord(
            run_id="run-001",
            product="test",
            flow="test_flow",
            input={},
            input_hash=input_hash,
            output=output,
            output_hash=output_hash,
        )
        
        result = validate_reproducibility("run-001", run_record=run)
        assert result.is_reproducible is True
        assert "output_hash" in result.verified_fields
    
    def test_validate_reproducibility_invalid_output(self):
        """validate_reproducibility fails with invalid output hash."""
        output = {"result": "success"}
        input_hash = compute_input_hash({})
        
        run = RunRecord(
            run_id="run-001",
            product="test",
            flow="test_flow",
            input={},
            input_hash=input_hash,
            output=output,
            output_hash="wrong_hash",  # Invalid
        )
        
        result = validate_reproducibility("run-001", run_record=run)
        assert result.is_reproducible is False
        assert any(d.field == "output_hash" for d in result.discrepancies)
    
    def test_validate_reproducibility_no_hashes(self):
        """validate_reproducibility handles runs without hashes."""
        run = RunRecord(
            run_id="run-001",
            product="test",
            flow="test_flow",
        )
        
        result = validate_reproducibility("run-001", run_record=run)
        # Not reproducible because no fields verified
        assert result.is_reproducible is False
        assert "input_hash" in result.skipped_fields
        assert "output_hash" in result.skipped_fields
    
    def test_validate_reproducibility_with_memory(self):
        """validate_reproducibility loads from memory if run_record not provided."""
        payload = {"query": "test"}
        input_hash = compute_input_hash(payload)
        
        run = RunRecord(
            run_id="run-001",
            product="test",
            flow="test_flow",
            input=payload,
            input_hash=input_hash,
        )
        
        memory = MagicMock()
        memory.get_run = MagicMock(return_value=MagicMock(run=run))
        
        result = validate_reproducibility("run-001", memory=memory)
        assert result.is_reproducible is True
        memory.get_run.assert_called_once_with("run-001")
    
    def test_validate_reproducibility_run_not_found(self):
        """validate_reproducibility returns error if run not found."""
        memory = MagicMock()
        memory.get_run = MagicMock(return_value=None)
        
        result = validate_reproducibility("run-999", memory=memory)
        assert result.is_reproducible is False
        assert "not found" in result.error
    
    def test_validate_reproducibility_no_memory_no_record(self):
        """validate_reproducibility returns error if no memory or run_record."""
        result = validate_reproducibility("run-001")
        assert result.is_reproducible is False
        assert result.error is not None


# ==============================
# Individual Validation Functions
# ==============================

class TestValidateInputHash:
    """Tests for validate_input_hash function."""
    
    def test_validate_input_hash_valid(self):
        """Returns None for valid input hash."""
        payload = {"key": "value"}
        run = RunRecord(
            product="test",
            flow="test",
            input=payload,
            input_hash=compute_input_hash(payload),
        )
        result = validate_input_hash(run)
        assert result is None
    
    def test_validate_input_hash_invalid(self):
        """Returns Discrepancy for invalid input hash."""
        run = RunRecord(
            product="test",
            flow="test",
            input={"key": "value"},
            input_hash="wrong",
        )
        result = validate_input_hash(run)
        assert isinstance(result, Discrepancy)
        assert result.field == "input_hash"
    
    def test_validate_input_hash_none(self):
        """Returns None if no input hash."""
        run = RunRecord(product="test", flow="test")
        result = validate_input_hash(run)
        assert result is None


class TestValidateOutputHash:
    """Tests for validate_output_hash function."""
    
    def test_validate_output_hash_valid(self):
        """Returns None for valid output hash."""
        output = {"result": "done"}
        run = RunRecord(
            product="test",
            flow="test",
            output=output,
            output_hash=compute_output_hash(output),
        )
        result = validate_output_hash(run)
        assert result is None
    
    def test_validate_output_hash_invalid(self):
        """Returns Discrepancy for invalid output hash."""
        run = RunRecord(
            product="test",
            flow="test",
            output={"result": "done"},
            output_hash="wrong",
        )
        result = validate_output_hash(run)
        assert isinstance(result, Discrepancy)
        assert result.field == "output_hash"


class TestValidateVersionConsistency:
    """Tests for validate_version_consistency function."""
    
    def test_validate_version_valid(self):
        """Returns None for valid versions."""
        run = RunRecord(
            product="test",
            flow="test",
            versions=Versions(platform_version="1.0.0"),
        )
        result = validate_version_consistency(run)
        assert result is None
    
    def test_validate_version_unknown(self):
        """Returns Discrepancy for unknown platform version."""
        run = RunRecord(
            product="test",
            flow="test",
            versions=Versions(platform_version="unknown"),
        )
        result = validate_version_consistency(run)
        assert isinstance(result, Discrepancy)


# ==============================
# Snapshot Function
# ==============================

class TestCreateReproducibilitySnapshot:
    """Tests for create_reproducibility_snapshot function."""
    
    def test_snapshot_includes_run_id(self):
        """Snapshot includes run_id."""
        run = RunRecord(run_id="run-001", product="test", flow="test")
        snapshot = create_reproducibility_snapshot(run)
        assert snapshot["run_id"] == "run-001"
    
    def test_snapshot_includes_hashes(self):
        """Snapshot includes input and output hashes."""
        run = RunRecord(
            product="test",
            flow="test",
            input_hash="input123",
            output_hash="output456",
        )
        snapshot = create_reproducibility_snapshot(run)
        assert snapshot["input_hash"] == "input123"
        assert snapshot["output_hash"] == "output456"
    
    def test_snapshot_includes_versions(self):
        """Snapshot includes version information."""
        run = RunRecord(
            product="test",
            flow="test",
            versions=Versions(
                platform_version="1.0.0",
                flow_version="v1",
                python_version="3.10.0",
                models={"gpt-4": "turbo"},
            ),
        )
        snapshot = create_reproducibility_snapshot(run)
        assert "versions" in snapshot
        assert snapshot["versions"]["platform_version"] == "1.0.0"
        assert snapshot["versions"]["models"] == {"gpt-4": "turbo"}


# ==============================
# Acceptance Checks
# ==============================

class TestAcceptanceChecks:
    """Acceptance criteria from imp_plan.md."""
    
    def test_validate_reproducibility_compares_hashes(self):
        """AC: validate_reproducibility compares stored vs. recomputed hashes."""
        payload = {"test": "data"}
        correct_hash = compute_input_hash(payload)
        wrong_hash = "not_the_right_hash"
        
        # Correct hash should pass
        run_valid = RunRecord(
            product="test",
            flow="test",
            input=payload,
            input_hash=correct_hash,
        )
        result_valid = validate_reproducibility("run-1", run_record=run_valid)
        assert result_valid.is_reproducible is True
        
        # Wrong hash should fail
        run_invalid = RunRecord(
            product="test",
            flow="test",
            input=payload,
            input_hash=wrong_hash,
        )
        result_invalid = validate_reproducibility("run-2", run_record=run_invalid)
        assert result_invalid.is_reproducible is False
    
    def test_returns_is_reproducible_boolean(self):
        """AC: Returns is_reproducible boolean."""
        run = RunRecord(
            product="test",
            flow="test",
            input_hash=compute_input_hash({}),
            input={},
        )
        result = validate_reproducibility("run-1", run_record=run)
        assert isinstance(result.is_reproducible, bool)
    
    def test_returns_discrepancies_with_required_fields(self):
        """AC: Returns discrepancies list with required fields."""
        run = RunRecord(
            product="test",
            flow="test",
            input={"key": "value"},
            input_hash="wrong_hash",
        )
        result = validate_reproducibility("run-1", run_record=run)
        
        assert len(result.discrepancies) > 0
        discrepancy = result.discrepancies[0]
        assert hasattr(discrepancy, "field")
        assert hasattr(discrepancy, "expected_hash")
        assert hasattr(discrepancy, "actual_hash")
