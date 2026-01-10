from __future__ import annotations

# ==============================
# Loop Evaluation Helpers
# ==============================
"""
Deterministic loop stop condition evaluation.
"""

from typing import Any, Dict, Optional

from core.contracts.loop_schema import (
    StopConditionExpr,
    StopConditionGroup,
    ConfidenceThreshold,
    NoMissingEvidence,
)
from core.orchestrator.branching import resolve_condition_path
from core.orchestrator.context import RunContext
from core.memory.router import MemoryRouter


def evaluate_stop_condition(
    condition: StopConditionExpr,
    *,
    run_ctx: RunContext,
    memory: MemoryRouter,
) -> bool:
    if isinstance(condition, StopConditionGroup):
        if condition.kind == "all":
            return all(evaluate_stop_condition(child, run_ctx=run_ctx, memory=memory) for child in condition.conditions)
        return any(evaluate_stop_condition(child, run_ctx=run_ctx, memory=memory) for child in condition.conditions)
    if isinstance(condition, ConfidenceThreshold):
        current = resolve_condition_path(condition.path, run_ctx=run_ctx, memory=memory)
        if not isinstance(current, (int, float)):
            return False
        if condition.op == ">=":
            return current >= condition.value
        if condition.op == ">":
            return current > condition.value
        if condition.op == "<":
            return current < condition.value
        if condition.op == "<=":
            return current <= condition.value
        return False
    if isinstance(condition, NoMissingEvidence):
        current = resolve_condition_path(condition.path, run_ctx=run_ctx, memory=memory)
        if isinstance(current, list):
            return len(current) == 0
        return current in (None, "")
    return False


def summarize_stop_condition(condition: StopConditionExpr) -> Dict[str, Any]:
    if isinstance(condition, StopConditionGroup):
        return {
            "kind": condition.kind,
            "conditions": [summarize_stop_condition(child) for child in condition.conditions],
        }
    if isinstance(condition, ConfidenceThreshold):
        return {"kind": condition.kind, "path": condition.path, "op": condition.op, "value": condition.value}
    if isinstance(condition, NoMissingEvidence):
        return {"kind": condition.kind, "path": condition.path, "op": condition.op}
    return {"kind": "unknown"}
