"""Tests for output validation utilities.

IMP-012: TS-BRD-VAL-001..003 validation gating tests.
IMP-013: TS-BRD-QUAL-001..004 quality check tests.
"""

import pytest
from pydantic import BaseModel, Field, ValidationError

from products.ade.utils.validation import (
    ValidationResult,
    format_pydantic_errors,
    validate_output_schema,
    validate_executive_summary,
    validate_findings,
    validate_recommendations,
    validate_visuals,
    validate_report_quality,
    ValidationGate,
)


class SampleModel(BaseModel):
    """Sample model for testing."""

    name: str
    value: int = Field(ge=0)


class TestFormatPydanticErrors:
    """Tests for format_pydantic_errors function."""

    def test_formats_single_error(self):
        """Test formatting single validation error."""
        try:
            SampleModel(name=123, value=-1)  # type: ignore
        except ValidationError as exc:
            errors = format_pydantic_errors(exc)
            assert len(errors) >= 1
            assert "field_path" in errors[0]
            assert "message" in errors[0]

    def test_includes_field_path(self):
        """Test that field path is included."""
        try:
            SampleModel(name="test", value=-5)
        except ValidationError as exc:
            errors = format_pydantic_errors(exc)
            assert any(e["field_path"] == "value" for e in errors)


class TestValidateOutputSchema:
    """Tests for validate_output_schema function."""

    def test_valid_data(self):
        """Test validation of valid data."""
        data = {"name": "test", "value": 10}
        result = validate_output_schema(SampleModel, data)
        assert result.valid
        assert result.errors == []

    def test_invalid_data(self):
        """Test validation of invalid data."""
        data = {"name": "test", "value": -1}
        result = validate_output_schema(SampleModel, data)
        assert not result.valid
        assert len(result.errors) > 0


class TestValidateExecutiveSummary:
    """Tests for validate_executive_summary (TS-BRD-QUAL-001)."""

    def test_empty_summary(self):
        """Test empty summary fails."""
        valid, msg = validate_executive_summary([])
        assert not valid
        assert msg == "executive_summary_empty"

    def test_too_brief_summary(self):
        """Test single item summary fails."""
        valid, msg = validate_executive_summary(["One item only"])
        assert not valid
        assert msg == "executive_summary_too_brief"

    def test_valid_summary(self):
        """Test multi-item summary passes."""
        valid, msg = validate_executive_summary(["First point", "Second point"])
        assert valid
        assert msg is None


class TestValidateFindings:
    """Tests for validate_findings (TS-BRD-QUAL-002)."""

    def test_empty_findings(self):
        """Test empty findings fails."""
        valid, msg = validate_findings([])
        assert not valid
        assert msg == "key_findings_empty"

    def test_finding_missing_refs(self):
        """Test finding without evidence refs fails."""
        findings = [{"headline": "Test", "evidence_refs": []}]
        valid, msg = validate_findings(findings)
        assert not valid
        assert "missing_evidence_refs" in msg

    def test_valid_findings(self):
        """Test finding with evidence refs passes."""
        findings = [{"headline": "Test", "evidence_refs": ["ref1"]}]
        valid, msg = validate_findings(findings)
        assert valid


class TestValidateRecommendations:
    """Tests for validate_recommendations (TS-BRD-QUAL-003)."""

    def test_too_short_recommendation(self):
        """Test short recommendation fails."""
        valid, msg = validate_recommendations(["OK"])
        assert not valid
        assert "too_generic" in msg

    def test_valid_recommendations(self):
        """Test substantive recommendations pass."""
        valid, msg = validate_recommendations(["Review the quarterly data trends"])
        assert valid


class TestValidateVisuals:
    """Tests for validate_visuals (TS-BRD-QUAL-004)."""

    def test_empty_visuals(self):
        """Test empty visuals fails."""
        valid, msg = validate_visuals([])
        assert not valid
        assert msg == "visuals_missing"

    def test_visual_missing_title(self):
        """Test visual without title fails."""
        visuals = [{"kind": "line", "data": {}}]
        valid, msg = validate_visuals(visuals)
        assert not valid
        assert "title_missing" in msg

    def test_valid_visuals(self):
        """Test visual with title passes."""
        visuals = [{"title": "Revenue Trend", "kind": "line"}]
        valid, msg = validate_visuals(visuals)
        assert valid


class TestValidateReportQuality:
    """Tests for validate_report_quality combined check."""

    def test_valid_report_dict(self):
        """Test valid report as dict."""
        report = {
            "executive_summary": ["Point 1", "Point 2"],
            "key_findings": [{"headline": "Finding", "evidence_refs": ["ref1"]}],
            "recommendations": ["Review the quarterly data trends"],
            "visuals": [{"title": "Chart", "kind": "line"}],
        }
        result = validate_report_quality(report)
        assert result.valid

    def test_multiple_errors(self):
        """Test report with multiple issues."""
        report = {
            "executive_summary": [],
            "key_findings": [],
            "recommendations": [],
            "visuals": [],
        }
        result = validate_report_quality(report)
        assert not result.valid
        assert len(result.errors) >= 3


class TestValidationGate:
    """Tests for ValidationGate class (TS-BRD-VAL-003)."""

    def test_gate_passes_valid(self):
        """Test gate passes valid result."""
        gate = ValidationGate(strict=True)
        result = ValidationResult(valid=True)
        assert gate.check(result) is True

    def test_gate_raises_on_invalid_strict(self):
        """Test gate raises on invalid in strict mode."""
        gate = ValidationGate(strict=True)
        result = ValidationResult(
            valid=False,
            errors=[{"field_path": "test", "message": "error"}],
        )
        with pytest.raises(ValueError, match="Validation failed"):
            gate.check(result)

    def test_gate_no_raise_non_strict(self):
        """Test gate doesn't raise in non-strict mode."""
        gate = ValidationGate(strict=False)
        result = ValidationResult(
            valid=False,
            errors=[{"field_path": "test", "message": "error"}],
        )
        assert gate.check(result) is False

    def test_gate_stores_last_result(self):
        """Test gate stores last validation result."""
        gate = ValidationGate(strict=False)
        result = ValidationResult(valid=True)
        gate.check(result)
        assert gate.last_result == result
