# ==============================
# HITL Contracts (DEPRECATED)
# ==============================
"""
DEPRECATED: This module is deprecated. Import from interaction_schema instead.

Migration:
    # Old (deprecated):
    from core.contracts.hitl_schema import HitlRequest, HitlResolution
    
    # New:
    from core.contracts.interaction_schema import HitlRequest, HitlResolution
"""

from __future__ import annotations

import warnings

# Re-exports for backwards compatibility
from core.contracts.interaction_schema import (
    HitlRequestType,
    HitlResolutionStatus,
    HitlInputSchema,
    HitlRequest,
    HitlResolution,
)

warnings.warn(
    "hitl_schema is deprecated. Import from interaction_schema instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "HitlRequestType",
    "HitlResolutionStatus",
    "HitlInputSchema",
    "HitlRequest",
    "HitlResolution",
]
