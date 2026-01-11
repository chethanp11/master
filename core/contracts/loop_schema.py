# ==============================
# Loop Contracts (DEPRECATED)
# ==============================
"""
DEPRECATED: This module is deprecated. Import from flow_schema instead.

Migration:
    # Old (deprecated):
    from core.contracts.loop_schema import LoopState, StopConditionExpr
    
    # New:
    from core.contracts.flow_schema import LoopState, StopConditionExpr
"""

from __future__ import annotations

import warnings

# Re-exports for backwards compatibility
from core.contracts.flow_schema import (
    ConfidenceThreshold,
    NoMissingEvidence,
    StopConditionGroup,
    StopConditionExpr,
    LoopState,
)

warnings.warn(
    "loop_schema is deprecated. Import from flow_schema instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ConfidenceThreshold",
    "NoMissingEvidence",
    "StopConditionGroup",
    "StopConditionExpr",
    "LoopState",
]
