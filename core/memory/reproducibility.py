# ==============================
# Reproducibility Validation Module
# ==============================
"""
Reproducibility validation for MASTER platform.

IMP-030: MEM-REPRO-030, MEM-REPRO-031, MEM-REPRO-032
BRD: BRD-OPS-061

Provides:
- Reproducibility validation API
- Hash verification for inputs, outputs, and context packs
- Discrepancy detection and reporting
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.utils.hashing import compute_hash, compute_input_hash, compute_output_hash

if TYPE_CHECKING:
    from core.contracts.run_schema import RunRecord
    from core.memory.router import MemoryRouter


# ==============================
# Discrepancy Model
# ==============================

@dataclass
class Discrepancy:
    """
    A hash discrepancy detected during reproducibility validation.
    
    MEM-REPRO-032: Discrepancy includes field, expected_hash, actual_hash.
    """
    field: str  # e.g., "input_hash", "output_hash", "content_hash"
    expected_hash: str  # Hash stored in RunRecord
    actual_hash: str  # Hash recomputed from stored data
    details: Optional[str] = None  # Additional context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "field": self.field,
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
            "details": self.details,
        }


# ==============================
# Reproducibility Result Model
# ==============================

@dataclass
class ReproducibilityResult:
    """
    Result of reproducibility validation.
    
    MEM-REPRO-031: Result includes is_reproducible boolean and discrepancies list.
    """
    run_id: str
    is_reproducible: bool
    discrepancies: List[Discrepancy] = field(default_factory=list)
    verified_fields: List[str] = field(default_factory=list)
    skipped_fields: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "run_id": self.run_id,
            "is_reproducible": self.is_reproducible,
            "discrepancies": [d.to_dict() for d in self.discrepancies],
            "verified_fields": self.verified_fields,
            "skipped_fields": self.skipped_fields,
            "error": self.error,
        }
    
    @property
    def summary(self) -> str:
        """Human-readable summary of the result."""
        if self.error:
            return f"Validation failed: {self.error}"
        if self.is_reproducible:
            return f"Run {self.run_id} is reproducible ({len(self.verified_fields)} fields verified)"
        return f"Run {self.run_id} is NOT reproducible ({len(self.discrepancies)} discrepancies)"


# ==============================
# Validation Functions
# ==============================

def validate_input_hash(
    run_record: "RunRecord",
) -> Optional[Discrepancy]:
    """
    Validate input hash against stored input.
    
    Args:
        run_record: RunRecord to validate
        
    Returns:
        Discrepancy if mismatch, None if valid or not applicable
    """
    if run_record.input_hash is None:
        return None  # No hash to validate
    
    # Recompute from stored input
    recomputed = compute_input_hash(run_record.input)
    
    if recomputed != run_record.input_hash:
        return Discrepancy(
            field="input_hash",
            expected_hash=run_record.input_hash,
            actual_hash=recomputed,
            details="Input hash mismatch",
        )
    
    return None


def validate_output_hash(
    run_record: "RunRecord",
) -> Optional[Discrepancy]:
    """
    Validate output hash against stored output.
    
    Args:
        run_record: RunRecord to validate
        
    Returns:
        Discrepancy if mismatch, None if valid or not applicable
    """
    if run_record.output_hash is None:
        return None  # No hash to validate
    
    # Recompute from stored output
    recomputed = compute_output_hash(run_record.output)
    
    if recomputed != run_record.output_hash:
        return Discrepancy(
            field="output_hash",
            expected_hash=run_record.output_hash,
            actual_hash=recomputed,
            details="Output hash mismatch",
        )
    
    return None


def validate_version_consistency(
    run_record: "RunRecord",
) -> Optional[Discrepancy]:
    """
    Validate that version information is present and consistent.
    
    Args:
        run_record: RunRecord to validate
        
    Returns:
        Discrepancy if inconsistent, None if valid
    """
    if run_record.versions is None:
        return None  # No versions to validate
    
    # Versions are metadata - just check for presence
    v = run_record.versions
    if not v.platform_version or v.platform_version == "unknown":
        return Discrepancy(
            field="versions.platform_version",
            expected_hash="<valid>",
            actual_hash="unknown",
            details="Platform version not set",
        )
    
    return None


def validate_reproducibility(
    run_id: str,
    *,
    memory: Optional["MemoryRouter"] = None,
    run_record: Optional["RunRecord"] = None,
) -> ReproducibilityResult:
    """
    Validate reproducibility of a run by comparing stored vs. recomputed hashes.
    
    MEM-REPRO-030: validate_reproducibility(run_id) compares stored vs. recomputed hashes.
    
    Args:
        run_id: Run ID to validate
        memory: Memory router (optional, used to load run if run_record not provided)
        run_record: RunRecord to validate (optional, loaded from memory if not provided)
        
    Returns:
        ReproducibilityResult with validation outcome
    """
    # Load run record if not provided
    if run_record is None:
        if memory is None:
            return ReproducibilityResult(
                run_id=run_id,
                is_reproducible=False,
                error="No memory router or run_record provided",
            )
        
        bundle = memory.get_run(run_id)
        if bundle is None:
            return ReproducibilityResult(
                run_id=run_id,
                is_reproducible=False,
                error=f"Run {run_id} not found",
            )
        run_record = bundle.run
    
    discrepancies: List[Discrepancy] = []
    verified_fields: List[str] = []
    skipped_fields: List[str] = []
    
    # Validate input hash
    input_discrepancy = validate_input_hash(run_record)
    if input_discrepancy:
        discrepancies.append(input_discrepancy)
    elif run_record.input_hash is not None:
        verified_fields.append("input_hash")
    else:
        skipped_fields.append("input_hash")
    
    # Validate output hash
    output_discrepancy = validate_output_hash(run_record)
    if output_discrepancy:
        discrepancies.append(output_discrepancy)
    elif run_record.output_hash is not None:
        verified_fields.append("output_hash")
    else:
        skipped_fields.append("output_hash")
    
    # Validate version consistency
    version_discrepancy = validate_version_consistency(run_record)
    if version_discrepancy:
        discrepancies.append(version_discrepancy)
    elif run_record.versions is not None:
        verified_fields.append("versions")
    else:
        skipped_fields.append("versions")
    
    # Determine overall reproducibility
    is_reproducible = len(discrepancies) == 0 and len(verified_fields) > 0
    
    return ReproducibilityResult(
        run_id=run_id,
        is_reproducible=is_reproducible,
        discrepancies=discrepancies,
        verified_fields=verified_fields,
        skipped_fields=skipped_fields,
    )


def create_reproducibility_snapshot(
    run_record: "RunRecord",
) -> Dict[str, Any]:
    """
    Create a snapshot of reproducibility-relevant hashes.
    
    Useful for debugging and audit purposes.
    
    Args:
        run_record: RunRecord to snapshot
        
    Returns:
        Dict with hash values
    """
    snapshot = {
        "run_id": run_record.run_id,
        "input_hash": run_record.input_hash,
        "output_hash": run_record.output_hash,
    }
    
    if run_record.versions:
        snapshot["versions"] = {
            "platform_version": run_record.versions.platform_version,
            "flow_version": run_record.versions.flow_version,
            "python_version": run_record.versions.python_version,
            "models": run_record.versions.models,
        }
    
    return snapshot


__all__ = [
    "Discrepancy",
    "ReproducibilityResult",
    "validate_reproducibility",
    "validate_input_hash",
    "validate_output_hash",
    "validate_version_consistency",
    "create_reproducibility_snapshot",
]
