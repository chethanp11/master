# ==============================
# Question Set Contracts (DEPRECATED)
# ==============================
"""
DEPRECATED: This module is deprecated. Import from interaction_schema instead.

Migration:
    # Old (deprecated):
    from core.contracts.question_schema import QuestionSet, UserAnswers
    
    # New:
    from core.contracts.interaction_schema import QuestionSet, UserAnswers
"""

from __future__ import annotations

import warnings

# Re-exports for backwards compatibility
from core.contracts.interaction_schema import (
    QuestionType,
    Question,
    QuestionSetProvenance,
    QuestionSet,
    UserAnswers,
)

warnings.warn(
    "question_schema is deprecated. Import from interaction_schema instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "QuestionType",
    "Question",
    "QuestionSetProvenance",
    "QuestionSet",
    "UserAnswers",
]
