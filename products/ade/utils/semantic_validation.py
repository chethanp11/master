"""Semantic Validation for ADE.

TS-SEM-VALIDATE-001: Semantic validation implementation.
TS-SEM-VALIDATE-008: Dataset reference validation.
TS-SEM-VALIDATE-009: Metric reference validation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ValidationResult(BaseModel):
    """Result of semantic validation per TS-SEM-VALIDATE-003."""

    model_config = ConfigDict(extra="forbid")

    is_valid: bool = True
    missing_fields: List[str] = Field(default_factory=list)
    clarifying_question: Optional[str] = None
    confidence_adjustment: float = 0.0
    outcome: Literal["PROCEED", "ASK_USER", "ABORT"] = "PROCEED"


class DatasetSchema(BaseModel):
    """Schema representing dataset columns for metric validation."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    columns: List[str] = Field(default_factory=list)


def _validate_dataset_ref(dataset: str, available: List[str]) -> bool:
    """Validate dataset reference against available datasets.

    TS-SEM-VALIDATE-008: Dataset references MUST be validated against
    available_datasets list before proceeding.

    Args:
        dataset: The dataset name to validate.
        available: List of available dataset names.

    Returns:
        True if dataset is valid, False otherwise.
    """
    if not dataset:
        return False
    return dataset in available


def _validate_metric_ref(metric: str, schema: DatasetSchema) -> bool:
    """Validate metric reference against dataset schema.

    TS-SEM-VALIDATE-009: Metric references MUST be validated against
    dataset schema columns when known.

    Args:
        metric: The metric/column name to validate.
        schema: The dataset schema with available columns.

    Returns:
        True if metric is valid column, False otherwise.
    """
    if not metric:
        return False
    return metric in schema.columns


def validate_dataset(
    dataset: str,
    available_datasets: List[str],
) -> ValidationResult:
    """Validate a dataset reference and return ASK_USER if invalid.

    TS-SEM-VALIDATE-008: Invalid dataset references trigger ASK_USER.

    Args:
        dataset: The dataset name to validate.
        available_datasets: List of available dataset names.

    Returns:
        ValidationResult with outcome and clarifying question if needed.
    """
    if not dataset:
        return ValidationResult(
            is_valid=False,
            missing_fields=["dataset"],
            clarifying_question="Which dataset would you like to analyze?",
            confidence_adjustment=-0.3,
            outcome="ASK_USER",
        )

    if not _validate_dataset_ref(dataset, available_datasets):
        available_str = ", ".join(available_datasets) if available_datasets else "none available"
        return ValidationResult(
            is_valid=False,
            missing_fields=["dataset"],
            clarifying_question=f"Dataset '{dataset}' not found. Available datasets: {available_str}. Which would you like to use?",
            confidence_adjustment=-0.3,
            outcome="ASK_USER",
        )

    return ValidationResult(
        is_valid=True,
        outcome="PROCEED",
    )


def validate_metric(
    metric: str,
    schema: DatasetSchema,
) -> ValidationResult:
    """Validate a metric reference and return ASK_USER if invalid.

    TS-SEM-VALIDATE-009: Invalid metric references trigger ASK_USER.

    Args:
        metric: The metric/column name to validate.
        schema: The dataset schema with available columns.

    Returns:
        ValidationResult with outcome and clarifying question if needed.
    """
    if not metric:
        columns_str = ", ".join(schema.columns) if schema.columns else "none available"
        return ValidationResult(
            is_valid=False,
            missing_fields=["metric"],
            clarifying_question=f"Which metric would you like to analyze? Available columns: {columns_str}",
            confidence_adjustment=-0.2,
            outcome="ASK_USER",
        )

    if not _validate_metric_ref(metric, schema):
        columns_str = ", ".join(schema.columns) if schema.columns else "none available"
        return ValidationResult(
            is_valid=False,
            missing_fields=["metric"],
            clarifying_question=f"Metric '{metric}' not found in dataset '{schema.dataset_id}'. Available columns: {columns_str}. Which would you like to use?",
            confidence_adjustment=-0.2,
            outcome="ASK_USER",
        )

    return ValidationResult(
        is_valid=True,
        outcome="PROCEED",
    )


def validate_semantic_envelope(
    envelope: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
) -> ValidationResult:
    """Validate a semantic envelope for completeness.

    TS-SEM-VALIDATE-001: Main validation entry point.

    Args:
        envelope: The semantic envelope to validate.
        context: Optional context with available_datasets and schema.

    Returns:
        ValidationResult with combined validation outcome.
    """
    context = context or {}
    missing_fields: List[str] = []
    confidence_adjustment = 0.0

    # Check dataset
    dataset = envelope.get("dataset")
    available_datasets = context.get("available_datasets", [])
    if available_datasets:
        dataset_result = validate_dataset(dataset or "", available_datasets)
        if not dataset_result.is_valid:
            return dataset_result

    # Check metric if schema provided
    metric = envelope.get("metric")
    schema_data = context.get("schema")
    if schema_data and isinstance(schema_data, dict):
        schema = DatasetSchema(**schema_data)
        if metric:
            metric_result = validate_metric(metric, schema)
            if not metric_result.is_valid:
                return metric_result

    # Check for missing optional fields
    optional_fields = ["time_scope", "constraints"]
    for field in optional_fields:
        if not envelope.get(field):
            missing_fields.append(field)
            confidence_adjustment -= 0.1

    # Clamp adjustment
    confidence_adjustment = max(-1.0, confidence_adjustment)

    return ValidationResult(
        is_valid=True,
        missing_fields=missing_fields,
        confidence_adjustment=confidence_adjustment,
        outcome="PROCEED",
    )
