"""Output validation utilities for ADE.

TS-BRD-VAL-001..003: Validation gating for output rendering.
TS-BRD-QUAL-001..004: Quality checks for output content.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, ValidationError


class ValidationResult(BaseModel):
    """Result of output validation."""

    valid: bool
    errors: List[Dict[str, Any]] = []
    warnings: List[str] = []


def format_pydantic_errors(exc: ValidationError) -> List[Dict[str, Any]]:
    """Format Pydantic validation errors with clear field paths.

    TS-BRD-VAL-002: Emit clear validation errors with field paths.

    Args:
        exc: Pydantic ValidationError.

    Returns:
        List of error dicts with path, message, and type.
    """
    errors = []
    for error in exc.errors():
        path = ".".join(str(loc) for loc in error.get("loc", []))
        errors.append({
            "field_path": path,
            "message": error.get("msg", "Unknown error"),
            "error_type": error.get("type", "validation_error"),
            "input": error.get("input"),
        })
    return errors


def validate_output_schema(model_class: type, data: Dict[str, Any]) -> ValidationResult:
    """Validate data against a Pydantic schema.

    TS-BRD-VAL-001: All outputs validated against Pydantic schemas.

    Args:
        model_class: Pydantic model class to validate against.
        data: Data dictionary to validate.

    Returns:
        ValidationResult with valid flag and any errors.
    """
    try:
        model_class.model_validate(data)
        return ValidationResult(valid=True)
    except ValidationError as exc:
        return ValidationResult(
            valid=False,
            errors=format_pydantic_errors(exc),
        )


def validate_executive_summary(summary: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate executive summary content.

    TS-BRD-QUAL-001: Executive summary must be present and non-empty.

    Args:
        summary: List of executive summary items.

    Returns:
        Tuple of (valid, error_message).
    """
    if not summary:
        return False, "executive_summary_empty"
    if len(summary) < 2:
        return False, "executive_summary_too_brief"
    return True, None


def validate_findings(findings: List[Any]) -> Tuple[bool, Optional[str]]:
    """Validate key findings content.

    TS-BRD-QUAL-002: Key findings must have evidence references.

    Args:
        findings: List of Finding objects.

    Returns:
        Tuple of (valid, error_message).
    """
    if not findings:
        return False, "key_findings_empty"
    for i, finding in enumerate(findings):
        refs = getattr(finding, "evidence_refs", None)
        if refs is None:
            refs = finding.get("evidence_refs") if isinstance(finding, dict) else None
        if not refs:
            return False, f"finding_{i}_missing_evidence_refs"
    return True, None


def validate_recommendations(recommendations: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate recommendations content.

    TS-BRD-QUAL-003: Recommendations must be substantive.

    Args:
        recommendations: List of recommendation strings.

    Returns:
        Tuple of (valid, error_message).
    """
    for i, rec in enumerate(recommendations):
        if len(str(rec).split()) < 3:
            return False, f"recommendation_{i}_too_generic"
    return True, None


def validate_visuals(visuals: List[Any]) -> Tuple[bool, Optional[str]]:
    """Validate visual specifications.

    TS-BRD-QUAL-004: Visuals must have titles and required data.

    Args:
        visuals: List of VisualSpec objects.

    Returns:
        Tuple of (valid, error_message).
    """
    if not visuals:
        return False, "visuals_missing"
    for i, visual in enumerate(visuals):
        title = getattr(visual, "title", None)
        if title is None:
            title = visual.get("title") if isinstance(visual, dict) else None
        if not title:
            return False, f"visual_{i}_title_missing"
    return True, None


def validate_report_quality(report: Any) -> ValidationResult:
    """Run all quality checks on a report.

    TS-BRD-QUAL-001..004: Combined quality validation.

    Args:
        report: BusinessReport or similar object.

    Returns:
        ValidationResult with all quality check results.
    """
    errors: List[Dict[str, Any]] = []
    warnings: List[str] = []

    # Get attributes (support both objects and dicts)
    def get_attr(name: str, default: Any = None) -> Any:
        if hasattr(report, name):
            return getattr(report, name)
        if isinstance(report, dict):
            return report.get(name, default)
        return default

    # Check executive summary
    summary = get_attr("executive_summary", [])
    valid, msg = validate_executive_summary(summary)
    if not valid and msg:
        errors.append({"field_path": "executive_summary", "message": msg})

    # Check findings
    findings = get_attr("key_findings", [])
    valid, msg = validate_findings(findings)
    if not valid and msg:
        errors.append({"field_path": "key_findings", "message": msg})

    # Check recommendations
    recommendations = get_attr("recommendations", [])
    valid, msg = validate_recommendations(recommendations)
    if not valid and msg:
        errors.append({"field_path": "recommendations", "message": msg})

    # Check visuals
    visuals = get_attr("visuals", [])
    valid, msg = validate_visuals(visuals)
    if not valid and msg:
        errors.append({"field_path": "visuals", "message": msg})

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


class ValidationGate:
    """Gate that blocks rendering if validation fails.

    TS-BRD-VAL-003: Rendering blocked when validation fails.
    """

    def __init__(self, strict: bool = True):
        """Initialize validation gate.

        Args:
            strict: If True, raise on validation failure.
        """
        self.strict = strict
        self.last_result: Optional[ValidationResult] = None

    def check(self, result: ValidationResult) -> bool:
        """Check validation result and optionally raise.

        Args:
            result: ValidationResult to check.

        Returns:
            True if valid.

        Raises:
            ValueError: If invalid and strict mode enabled.
        """
        self.last_result = result
        if not result.valid and self.strict:
            error_msgs = [
                f"{e['field_path']}: {e['message']}"
                for e in result.errors
            ]
            raise ValueError(f"Validation failed: {'; '.join(error_msgs)}")
        return result.valid
