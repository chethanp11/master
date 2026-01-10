from __future__ import annotations

# ==============================
# Branch Evaluation Helpers
# ==============================
"""
Deterministic branch evaluation with safe value extraction.
"""

from typing import Any, Dict, List, Optional

from core.contracts.branch_schema import ConditionExpr
from core.orchestrator.context import RunContext
from core.memory.router import MemoryRouter


ConditionValue = Any


def evaluate_condition(
    condition: ConditionExpr,
    *,
    run_ctx: RunContext,
    memory: MemoryRouter,
) -> bool:
    if condition.all:
        return all(evaluate_condition(child, run_ctx=run_ctx, memory=memory) for child in condition.all)
    if condition.any:
        return any(evaluate_condition(child, run_ctx=run_ctx, memory=memory) for child in condition.any)
    value = resolve_condition_path(condition.path or "", run_ctx=run_ctx, memory=memory)
    return _evaluate_op(condition.op or "exists", value, condition.value)


def resolve_condition_path(path: str, *, run_ctx: RunContext, memory: MemoryRouter) -> Optional[ConditionValue]:
    parts = [seg for seg in path.split(".") if seg]
    if not parts:
        return None
    if parts[0] == "steps":
        return _resolve_step_path(parts, run_ctx=run_ctx, memory=memory)
    if parts[0] == "artifacts":
        return _resolve_artifact_path(parts, run_ctx=run_ctx)
    return None


def summarize_condition(condition: ConditionExpr) -> Dict[str, Any]:
    if condition.all:
        return {"all": [summarize_condition(child) for child in condition.all]}
    if condition.any:
        return {"any": [summarize_condition(child) for child in condition.any]}
    summary: Dict[str, Any] = {"path": condition.path, "op": condition.op}
    if condition.op != "exists":
        summary["value"] = _summarize_value(condition.value)
    return summary


def _evaluate_op(op: str, current: Any, expected: Any) -> bool:
    if op == "exists":
        return current is not None
    if current is None:
        return False
    if op == "==":
        return current == expected
    if op == "!=":
        return current != expected
    if op in {">", ">=", "<", "<="}:
        if not isinstance(current, (int, float)) or not isinstance(expected, (int, float)):
            return False
        if op == ">":
            return current > expected
        if op == ">=":
            return current >= expected
        if op == "<":
            return current < expected
        if op == "<=":
            return current <= expected
    if op == "in":
        return isinstance(expected, list) and current in expected
    if op == "contains":
        if isinstance(current, str) and isinstance(expected, str):
            return expected in current
        if isinstance(current, list):
            return expected in current
        return False
    return False


def _resolve_step_path(parts: List[str], *, run_ctx: RunContext, memory: MemoryRouter) -> Optional[Any]:
    if len(parts) < 4 or parts[2] != "output":
        return None
    step_id = parts[1]
    bundle = memory.get_run(run_ctx.run_id)
    if bundle is None:
        return None
    step = next((s for s in bundle.steps if s.step_id == step_id), None)
    if step is None:
        return None
    current: Any = step.output
    for seg in parts[3:]:
        if isinstance(current, dict) and seg in current:
            current = current[seg]
        else:
            return None
    return _coerce_scalar(current)


def _resolve_artifact_path(parts: List[str], *, run_ctx: RunContext) -> Optional[Any]:
    if len(parts) < 3:
        return None
    segments = parts[1:]
    artifacts = run_ctx.artifacts
    key, remainder = _resolve_artifact_key(segments, artifacts)
    if key is None:
        return None
    current: Any = artifacts.get(key)
    for seg in remainder:
        if isinstance(current, dict) and seg in current:
            current = current[seg]
        else:
            return None
    return _coerce_scalar(current)


def _resolve_artifact_key(segments: List[str], artifacts: Dict[str, Any]) -> tuple[Optional[str], List[str]]:
    for idx in range(len(segments), 0, -1):
        candidate = ".".join(segments[:idx])
        if candidate in artifacts:
            return candidate, segments[idx:]
    return None, segments


def _coerce_scalar(value: Any) -> Optional[Any]:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list) and all(isinstance(item, (str, int, float, bool)) or item is None for item in value):
        return value
    return None


def _summarize_value(value: Any, *, limit: int = 80) -> Any:
    if isinstance(value, str):
        trimmed = value.strip()
        if len(trimmed) > limit:
            return trimmed[: limit - 1] + "…"
        return trimmed
    if isinstance(value, list):
        return [_summarize_value(item, limit=limit) for item in value[:10]]
    return value
