# ==============================
# Branching Contracts (DEPRECATED)
# ==============================
"""
DEPRECATED: This module is deprecated. Import from flow_schema instead.

Migration:
    # Old (deprecated):
    from core.contracts.branch_schema import ConditionExpr
    
    # New:
    from core.contracts.flow_schema import ConditionExpr
"""

from __future__ import annotations

import warnings

# Re-exports for backwards compatibility
from core.contracts.flow_schema import (
    ConditionOp,
    ConditionScalar,
    ConditionValue,
    ConditionExpr,
)

warnings.warn(
    "branch_schema is deprecated. Import from flow_schema instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ConditionOp",
    "ConditionScalar",
    "ConditionValue",
    "ConditionExpr",
]
