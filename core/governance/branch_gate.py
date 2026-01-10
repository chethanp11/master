from __future__ import annotations

# ==============================
# Branch Condition Gating
# ==============================
"""
Policy validation for deterministic branch conditions.
"""

from typing import List, Set

from core.contracts.branch_schema import ConditionExpr
from core.contracts.flow_schema import FlowDef, StepType


_DISALLOWED_SEGMENTS = {
    "raw_text",
    "content",
    "prompt",
    "transcript",
    "free_text",
    "user_input",
    "content_ref",
}


def validate_branch_conditions(flow_def: FlowDef) -> List[str]:
    step_ids = {step.id for step in flow_def.steps}
    errors: List[str] = []

    for step in flow_def.steps:
        if step.type != StepType.BRANCH:
            continue
        if step.when is None:
            errors.append(f"branch.{step.id}.missing_condition")
            continue
        errors.extend(_validate_condition_expr(step.when, step_ids=step_ids, step_id=step.id))
        if step.then and step.then not in step_ids:
            errors.append(f"branch.{step.id}.unknown_then:{step.then}")
        if step.else_step and step.else_step not in step_ids:
            errors.append(f"branch.{step.id}.unknown_else:{step.else_step}")

    return errors


def validate_condition_path(path: str, *, step_ids: Set[str], step_id: str) -> List[str]:
    return _validate_path(path, step_ids=step_ids, step_id=step_id)


def _validate_condition_expr(condition: ConditionExpr, *, step_ids: Set[str], step_id: str) -> List[str]:
    errors: List[str] = []
    if condition.path:
        errors.extend(_validate_path(condition.path, step_ids=step_ids, step_id=step_id))
        return errors
    if condition.all:
        for child in condition.all:
            errors.extend(_validate_condition_expr(child, step_ids=step_ids, step_id=step_id))
    if condition.any:
        for child in condition.any:
            errors.extend(_validate_condition_expr(child, step_ids=step_ids, step_id=step_id))
    return errors


def _validate_path(path: str, *, step_ids: Set[str], step_id: str) -> List[str]:
    errors: List[str] = []
    parts = [seg for seg in path.split(".") if seg]
    if not parts:
        return [f"branch.{step_id}.empty_path"]
    if parts[0] not in {"steps", "artifacts"}:
        return [f"branch.{step_id}.unsupported_root:{parts[0]}"]
    if _has_disallowed_segment(parts):
        return [f"branch.{step_id}.disallowed_path:{path}"]
    if parts[0] == "steps":
        if len(parts) < 4 or parts[2] != "output":
            return [f"branch.{step_id}.invalid_steps_path:{path}"]
        if parts[1] not in step_ids:
            return [f"branch.{step_id}.unknown_step:{parts[1]}"]
    if parts[0] == "artifacts":
        if len(parts) < 3:
            return [f"branch.{step_id}.invalid_artifact_path:{path}"]
    return errors


def _has_disallowed_segment(parts: List[str]) -> bool:
    for seg in parts:
        if seg in _DISALLOWED_SEGMENTS:
            return True
    return False
