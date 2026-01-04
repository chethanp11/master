# ==============================
# Error Policy
# ==============================
"""
Retry/backoff policy evaluation for orchestrator steps.

This module is intentionally small and pure:
- No persistence
- No tool calls
- No environment reads

Intended usage:
- Step executor consults should_retry(...) after failures
- Orchestrator uses backoff_seconds(...) to sleep externally (if desired)
"""

from __future__ import annotations


# ==============================
# Imports
# ==============================

from dataclasses import dataclass
from typing import Optional, Sequence

from core.contracts.flow_schema import RetryPolicy

# ==============================
# Decision Model
# ==============================
@dataclass(frozen=True)
class RetryDecision:
    """Result of evaluating whether a retry should occur."""
    should_retry: bool
    reason: str
    next_backoff_seconds: float


# ==============================
# Policy Evaluation
# ==============================
def evaluate_retry(
    *,
    attempt_index: int,
    retry_policy: Optional[RetryPolicy],
    error_code: Optional[str] = None,
) -> RetryDecision:
    """
    Evaluate retry decision for a failed attempt.

    Parameters:
    - attempt_index: 1-based attempt number (1 = first attempt already executed)
    - retry_policy: RetryPolicy or None
    - error_code: Optional string code from error envelope

    Returns:
    - RetryDecision including should_retry and backoff
    """
    if retry_policy is None:
        return RetryDecision(False, "no_retry_policy", 0.0)

    max_attempts = retry_policy.max_attempts
    if attempt_index >= max_attempts:
        return RetryDecision(False, "max_attempts_reached", 0.0)

    if not _is_retryable_code(error_code, retry_policy.retry_on_codes):
        return RetryDecision(False, "error_code_not_retryable", 0.0)

    return RetryDecision(True, "retry_allowed", float(retry_policy.backoff_seconds))


def backoff_seconds(retry_policy: Optional[RetryPolicy]) -> float:
    """Return backoff seconds for a retry policy (0.0 if none)."""
    if retry_policy is None:
        return 0.0
    return float(retry_policy.backoff_seconds)


# ==============================
# Helpers
# ==============================
def _is_retryable_code(error_code: Optional[str], retry_on_codes: Sequence[str]) -> bool:
    """
    Determine if error_code is retryable.
    Rules:
    - If retry_on_codes list is empty: treat as retryable for any error_code (including None)
    - If list is not empty: only retry when error_code matches one of the entries
    """
    if len(retry_on_codes) == 0:
        return True
    if error_code is None:
        return False
    return error_code in set(retry_on_codes)
