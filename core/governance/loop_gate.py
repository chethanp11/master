from __future__ import annotations

# ==============================
# Loop Condition Gating
# ==============================
"""
Policy validation for deterministic loop stop conditions.
"""

from typing import List, Set

from core.contracts.loop_schema import StopConditionExpr, StopConditionGroup, ConfidenceThreshold, NoMissingEvidence
from core.contracts.flow_schema import FlowDef, StepType
from core.governance.branch_gate import validate_condition_path


def validate_loop_conditions(flow_def: FlowDef) -> List[str]:
    step_ids = {step.id for step in flow_def.steps}
    errors: List[str] = []

    for step in flow_def.steps:
        if step.type != StepType.REPEAT_UNTIL:
            continue
        if step.stop_condition is None:
            errors.append(f"loop.{step.id}.missing_stop_condition")
            continue
        errors.extend(_validate_stop_condition(step.stop_condition, step_ids=step_ids, step_id=step.id))
        if step.iteration_step and step.iteration_step not in step_ids:
            errors.append(f"loop.{step.id}.unknown_iteration_step:{step.iteration_step}")
        if step.on_terminate and step.on_terminate not in step_ids:
            errors.append(f"loop.{step.id}.unknown_on_terminate:{step.on_terminate}")

    return errors


def _validate_stop_condition(condition: StopConditionExpr, *, step_ids: Set[str], step_id: str) -> List[str]:
    if isinstance(condition, StopConditionGroup):
        errors: List[str] = []
        for child in condition.conditions:
            errors.extend(_validate_stop_condition(child, step_ids=step_ids, step_id=step_id))
        return errors
    if isinstance(condition, (ConfidenceThreshold, NoMissingEvidence)):
        return validate_condition_path(condition.path, step_ids=step_ids, step_id=step_id)
    return [f"loop.{step_id}.unsupported_stop_condition"]
