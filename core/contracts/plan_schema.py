# ==============================
# Plan Proposal Contracts (DEPRECATED)
# ==============================
"""
DEPRECATED: This module is deprecated. Import from action_plan_schema instead.

Migration:
    # Old (deprecated):
    from core.contracts.plan_schema import PlanStep, PlanProposal, EstimatedCost
    
    # New:
    from core.contracts.action_plan_schema import PlanProposalStep, PlanProposal, EstimatedCost
    
Note: PlanStep has been renamed to PlanProposalStep to avoid conflict with
      the PlanStep discriminated union in action_plan_schema.
"""

from __future__ import annotations

import warnings

# Re-exports for backwards compatibility
from core.contracts.action_plan_schema import (
    PlanProposalStep,
    PlanApproval,
    EstimatedCost,
    PlanProposal,
)

# Alias for backwards compatibility - PlanStep -> PlanProposalStep
PlanStep = PlanProposalStep

warnings.warn(
    "plan_schema is deprecated. Import from action_plan_schema instead. "
    "Note: PlanStep has been renamed to PlanProposalStep.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "PlanStep",  # Aliased to PlanProposalStep for backwards compat
    "PlanProposalStep",
    "PlanApproval",
    "EstimatedCost",
    "PlanProposal",
]
