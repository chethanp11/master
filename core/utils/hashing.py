# ==============================
# Hashing Utilities
# ==============================
"""
Hashing utilities for reproducibility.

IMP-028: MEM-REPRO-010, MEM-REPRO-011, MEM-REPRO-012
BRD: BRD-OPS-061

Provides:
- Canonical JSON serialization
- SHA-256 hashing
- Consistent hash computation for any data structure
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from typing import Any, Optional


# ==============================
# Canonical JSON Encoder
# ==============================

class CanonicalJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for canonical, reproducible serialization.
    
    MEM-REPRO-010: Ensures consistent serialization for hashing.
    
    Handles:
    - datetime/date objects → ISO format strings
    - Sets → sorted lists
    - Custom objects with __dict__ → dict representation
    """
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, set):
            return sorted(list(obj), key=str)
        if isinstance(obj, frozenset):
            return sorted(list(obj), key=str)
        if hasattr(obj, "model_dump"):
            # Pydantic models
            return obj.model_dump(mode="json")
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        # Let the base class raise TypeError
        return super().default(obj)


# ==============================
# Hash Computation
# ==============================

def compute_hash(data: Any, *, algorithm: str = "sha256") -> str:
    """
    Compute hash of any data structure.
    
    MEM-REPRO-011: All inputs hashed using SHA-256.
    MEM-REPRO-012: Hash computed from canonical JSON.
    
    Args:
        data: Any JSON-serializable data structure
        algorithm: Hash algorithm (default "sha256")
        
    Returns:
        Hex digest of the hash
        
    Raises:
        ValueError: If data cannot be serialized to JSON
    """
    try:
        # Canonical JSON: sorted keys, minimal separators, ASCII-safe
        canonical = json.dumps(
            data,
            cls=CanonicalJSONEncoder,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot serialize data for hashing: {e}") from e
    
    # Compute hash
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "sha512":
        hasher = hashlib.sha512()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    hasher.update(canonical.encode("utf-8"))
    return hasher.hexdigest()


def compute_input_hash(payload: Optional[dict]) -> str:
    """
    Compute hash of run input payload.
    
    MEM-REPRO-011: Input hash for run reproducibility.
    
    Args:
        payload: Input payload dict (can be None)
        
    Returns:
        SHA-256 hex digest of the payload
    """
    if payload is None:
        return compute_hash({})
    return compute_hash(payload)


def compute_output_hash(output: Optional[dict]) -> str:
    """
    Compute hash of run output.
    
    MEM-REPRO-020: Output hash for verification.
    
    Args:
        output: Output data dict (can be None)
        
    Returns:
        SHA-256 hex digest of the output
    """
    if output is None:
        return compute_hash({})
    return compute_hash(output)


def verify_hash(data: Any, expected_hash: str, *, algorithm: str = "sha256") -> bool:
    """
    Verify that data matches expected hash.
    
    Args:
        data: Data to hash
        expected_hash: Expected hash value
        algorithm: Hash algorithm
        
    Returns:
        True if hashes match, False otherwise
    """
    actual_hash = compute_hash(data, algorithm=algorithm)
    return actual_hash == expected_hash


__all__ = [
    "CanonicalJSONEncoder",
    "compute_hash",
    "compute_input_hash",
    "compute_output_hash",
    "verify_hash",
]
