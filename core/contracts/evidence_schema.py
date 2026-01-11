# ==============================
# Evidence Contracts (DEPRECATED)
# ==============================
"""
DEPRECATED: This module is deprecated. Import from context_pack_schema instead.

Migration:
    # Old (deprecated):
    from core.contracts.evidence_schema import EvidenceItem, EvidenceSource
    
    # New:
    from core.contracts.context_pack_schema import EvidenceItem, EvidenceSource
"""

from __future__ import annotations

import warnings

# Re-exports for backwards compatibility
from core.contracts.context_pack_schema import (
    EvidenceType,
    EvidenceSource,
    EvidenceItem,
)

warnings.warn(
    "evidence_schema is deprecated. Import from context_pack_schema instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "EvidenceType",
    "EvidenceSource",
    "EvidenceItem",
]
