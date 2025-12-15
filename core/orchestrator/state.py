# ==============================
# Orchestrator State
# ==============================
"""
Orchestrator state enums and helpers.

These are the canonical runtime statuses used by the orchestrator.
They intentionally reuse the platform contracts from core/contracts/run_schema.py.

Intended usage:
- Orchestrator sets RunStatus / StepStatus on RunRecord / StepRecord
- Gateway/UI reads these statuses for run tracking and approvals
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from typing import FrozenSet

from core.contracts.run_schema import RunStatus as RunStatus  # re-export
from core.contracts.run_schema import StepStatus as StepStatus  # re-export

# ==============================
# Status Groups
# ==============================
RUN_TERMINAL: FrozenSet[RunStatus] = frozenset(
    {
        RunStatus.COMPLETED,
        RunStatus.FAILED,
        RunStatus.CANCELLED,
    }
)

RUN_ACTIVE: FrozenSet[RunStatus] = frozenset(
    {
        RunStatus.RUNNING,
        RunStatus.PENDING_HUMAN,
    }
)

STEP_TERMINAL: FrozenSet[StepStatus] = frozenset(
    {
        StepStatus.COMPLETED,
        StepStatus.FAILED,
        StepStatus.SKIPPED,
    }
)

STEP_ACTIVE: FrozenSet[StepStatus] = frozenset(
    {
        StepStatus.RUNNING,
        StepStatus.WAITING_HUMAN,
    }
)