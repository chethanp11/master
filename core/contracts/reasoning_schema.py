# ==============================
# Reasoning Purpose Contract
# ==============================
"""
Reasoning purposes for LLM usage in master/.

This is a stable contract used across routing, governance, and tracing.
"""

from enum import Enum


class ReasoningPurpose(str, Enum):
    INSIGHT = "INSIGHT"
    PRIORITIZATION = "PRIORITIZATION"
    EXPLANATION = "EXPLANATION"
    UNCERTAINTY = "UNCERTAINTY"
