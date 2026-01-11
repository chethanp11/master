"""
Plan Executor Module

This module handles action plan lifecycle operations:
- Plan proposal handling (_handle_plan_propose)
- Plan gate evaluation (_handle_plan_gate)
- Plan execution handling (_handle_plan_execute)
- Action plan step execution (_execute_action_plan)

Internal module - only imported by engine.py
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

from core.agents.registry import AgentRegistry
from core.contracts.action_plan_schema import (
    ActionPlan,
    PlanAgentCall,
    PlanGateResult,
    PlanToolCall,
)
from core.contracts.budget_schema import Budget
from core.contracts.interaction_schema import HitlRequest
from core.contracts.run_schema import (
    ArtifactRef,
    RunStatus,
    StepRecord,
    StepStatus,
)
from core.governance.gates import gate_action_plan
from core.memory.router import MemoryRouter
from core.orchestrator.context import RunContext

if TYPE_CHECKING:
    from core.contracts.flow_schema import StepDef
    from core.governance.hooks import GovernanceHooks
    from core.orchestrator.hitl import HitlService
    from core.orchestrator.step_executor import StepExecutor


# ============================================================================
# Plan Artifact Helpers
# ============================================================================


def store_plan_artifact(
    run_ctx: RunContext,
    key: str,
    payload: Dict[str, Any],
) -> ArtifactRef:
    """
    Store a plan artifact in run context.

    Args:
        run_ctx: Run context
        key: Artifact key
        payload: Artifact payload

    Returns:
        ArtifactRef pointing to stored artifact
    """
    full_key = key
    uri = f"memory://{full_key}"
    ref = ArtifactRef(key=full_key, kind="json", uri=uri)
    run_ctx.artifacts[full_key] = payload
    return ref


def get_plan_artifact_payload(
    run_ctx: RunContext,
    key: str,
) -> Optional[Dict[str, Any]]:
    """
    Get a plan artifact payload from run context.

    Args:
        run_ctx: Run context
        key: Artifact key

    Returns:
        Artifact payload if found and is a dict, None otherwise
    """
    value = run_ctx.artifacts.get(key)
    if isinstance(value, dict):
        return value
    return None


# ============================================================================
# Plan Propose Handling
# ============================================================================


def handle_plan_propose(
    *,
    run_ctx: RunContext,
    step_def: "StepDef",
    step_id: str,
    step_record: StepRecord,
    requested_by: Optional[str],
    memory: MemoryRouter,
    governance: "GovernanceHooks",
    fail_step_fn: Callable[..., str],
    emit_event_fn: Callable[..., None],
) -> Optional[str]:
    """
    Handle a PLAN_PROPOSE step.

    This step proposes an action plan either from step params or by running an agent.

    Args:
        run_ctx: Run context
        step_def: Step definition
        step_id: Step ID
        step_record: Step record
        requested_by: User who requested the run
        memory: Memory router
        governance: Governance hooks
        fail_step_fn: Function to call when step fails
        emit_event_fn: Function to emit events

    Returns:
        "continue" to proceed, status string on failure/pause, None to continue processing
    """
    plan_payload = (step_def.params or {}).get("plan")

    if plan_payload is None:
        if step_def.agent is None:
            return fail_step_fn(
                run_ctx=run_ctx,
                step_id=step_id,
                reason="plan_propose_missing_agent",
                message="plan_propose step missing agent",
            )

        agent = AgentRegistry.resolve(step_def.agent)
        step_ctx = run_ctx.new_step(step_def=step_def, step_id=step_id)
        result = agent.run(step_ctx)

        if not result.ok:
            return fail_step_fn(
                run_ctx=run_ctx,
                step_id=step_id,
                reason="plan_propose_failed",
                message="agent_failed",
            )

        decision = governance.validate_agent_output(
            agent_name=step_def.agent,
            output=result.data or {},
            ctx=step_ctx,
        )
        if not decision.allowed:
            return fail_step_fn(
                run_ctx=run_ctx,
                step_id=step_id,
                reason=decision.reason,
                message="agent_output_denied",
            )

        plan_payload = result.data or {}

    # Validate and store the plan
    try:
        plan = ActionPlan.model_validate(plan_payload)
    except Exception as exc:
        return fail_step_fn(
            run_ctx=run_ctx,
            step_id=step_id,
            reason="plan_invalid",
            message=str(exc),
        )

    plan_ref = store_plan_artifact(run_ctx, "plan.action_plan", plan.model_dump(mode="json"))

    memory.update_step(
        run_ctx.run_id,
        step_id,
        {
            "status": StepStatus.COMPLETED.value,
            "finished_at": int(time.time()),
            "output": {"plan_ref": plan_ref.model_dump(), "plan": plan.model_dump(mode="json")},
        },
    )

    run_ctx.meta["last_result_data"] = {
        "summary": "plan_proposed",
        "details": {"plan_id": plan.id},
    }

    emit_event_fn(
        kind="plan_proposed",
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        payload={
            "plan_id": plan.id,
            "step_count": len(plan.steps),
            "confidence": plan.confidence,
        },
    )

    return "continue"


# ============================================================================
# Plan Gate Handling
# ============================================================================


def handle_plan_gate(
    *,
    run_ctx: RunContext,
    step_def: "StepDef",
    step_id: str,
    step_record: StepRecord,
    memory: MemoryRouter,
    fail_step_fn: Callable[..., str],
    emit_event_fn: Callable[..., None],
) -> Optional[str]:
    """
    Handle a PLAN_GATE step.

    This step evaluates an action plan against governance policies.

    Args:
        run_ctx: Run context
        step_def: Step definition
        step_id: Step ID
        step_record: Step record
        memory: Memory router
        fail_step_fn: Function to call when step fails
        emit_event_fn: Function to emit events

    Returns:
        "continue" to proceed, status string on failure, None to continue processing
    """
    # Get the plan artifact
    plan = get_plan_artifact_payload(run_ctx, "plan.action_plan")
    if plan is None:
        return fail_step_fn(
            run_ctx=run_ctx,
            step_id=step_id,
            reason="plan_missing",
            message="plan.action_plan missing",
        )

    try:
        plan_obj = ActionPlan.model_validate(plan)
    except Exception as exc:
        return fail_step_fn(
            run_ctx=run_ctx,
            step_id=step_id,
            reason="plan_invalid",
            message=str(exc),
        )

    # Get budget from context
    budget = run_ctx.meta.get("budget")
    if isinstance(budget, dict):
        try:
            budget = Budget.model_validate(budget)
        except Exception:
            budget = None

    sensitivity = str(run_ctx.payload.get("_budget_sensitivity") or "LOW")

    # Run the gate
    gate_result = gate_action_plan(
        plan_obj,
        allow_tools=step_def.allow_tools,
        allow_agents=step_def.allow_agents,
        budget=budget,
        sensitivity=sensitivity,
    )

    # Store gate result
    gate_ref = store_plan_artifact(run_ctx, "plan.gate_result", gate_result.model_dump(mode="json"))

    memory.update_step(
        run_ctx.run_id,
        step_id,
        {
            "status": StepStatus.COMPLETED.value,
            "finished_at": int(time.time()),
            "output": {
                "plan_gate_ref": gate_ref.model_dump(),
                "plan_gate": gate_result.model_dump(mode="json"),
            },
        },
    )

    run_ctx.meta["last_result_data"] = {
        "summary": "plan_gated",
        "details": {"plan_id": gate_result.plan_id, "status": gate_result.status},
    }

    emit_event_fn(
        kind="plan_gated",
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        payload={
            "status": gate_result.status,
            "approved_count": len(gate_result.approved_steps),
            "rejected_count": len(gate_result.rejected_steps),
            "requires_hitl_count": len(gate_result.requires_hitl_for_steps),
            "reasons": gate_result.reasons,
        },
    )

    return "continue"


# ============================================================================
# Plan Execute Handling
# ============================================================================


def handle_plan_execute(
    *,
    run_ctx: RunContext,
    step_def: "StepDef",
    step_id: str,
    step_record: StepRecord,
    requested_by: Optional[str],
    memory: MemoryRouter,
    hitl: "HitlService",
    governance: "GovernanceHooks",
    step_executor: "StepExecutor",
    fail_step_fn: Callable[..., str],
    emit_event_fn: Callable[..., None],
    transition_run_status_fn: Callable[..., None],
    summary_with_counters_fn: Callable[..., Dict[str, Any]],
    persist_run_output_fn: Callable[..., None],
) -> Optional[str]:
    """
    Handle a PLAN_EXECUTE step.

    This step executes an approved action plan, handling HITL if required.

    Args:
        run_ctx: Run context
        step_def: Step definition
        step_id: Step ID
        step_record: Step record
        requested_by: User who requested the run
        memory: Memory router
        hitl: HITL service
        governance: Governance hooks
        step_executor: Step executor
        fail_step_fn: Function to call when step fails
        emit_event_fn: Function to emit events
        transition_run_status_fn: Function to transition run status
        summary_with_counters_fn: Function to build summary with counters
        persist_run_output_fn: Function to persist run output

    Returns:
        "continue" to proceed, status string on failure/pause, None to continue processing
    """
    # Get the gate result artifact
    gate = get_plan_artifact_payload(run_ctx, "plan.gate_result")
    if gate is None:
        return fail_step_fn(
            run_ctx=run_ctx,
            step_id=step_id,
            reason="plan_gate_missing",
            message="plan.gate_result missing",
        )

    try:
        gate_obj = PlanGateResult.model_validate(gate)
    except Exception as exc:
        return fail_step_fn(
            run_ctx=run_ctx,
            step_id=step_id,
            reason="plan_gate_invalid",
            message=str(exc),
        )

    # Handle rejected plan
    if gate_obj.status == "REJECTED":
        return fail_step_fn(
            run_ctx=run_ctx,
            step_id=step_id,
            reason="plan_rejected",
            message="plan rejected",
        )

    # Handle HITL requirement
    if gate_obj.status == "REQUIRES_HITL":
        approval_payload = {
            "plan_id": gate_obj.plan_id,
            "requires_hitl_steps": gate_obj.requires_hitl_for_steps,
        }
        approval = hitl.create_approval(
            run_id=run_ctx.run_id,
            step_id=step_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            requested_by=requested_by,
            payload=approval_payload,
        )
        hitl_request = HitlRequest(
            request_id=approval.approval_id,
            request_type="APPROVAL",
            run_id=run_ctx.run_id,
            step_id=step_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            created_at=int(time.time()),
            payload={"approval_context": approval_payload},
        )
        memory.update_step(
            run_ctx.run_id,
            step_id,
            {
                "status": StepStatus.PENDING_HUMAN.value,
                "output": {
                    "approval_id": approval.approval_id,
                    "hitl_request": hitl_request.model_dump(mode="json"),
                },
            },
        )
        transition_run_status_fn(
            run_id=run_ctx.run_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            current_status=RunStatus.RUNNING,
            target_status=RunStatus.PENDING_HUMAN,
            step_id=step_id,
            summary=summary_with_counters_fn(run_ctx, {"current_step_index": step_record.step_index}),
            reason="plan_execute_requires_hitl",
        )
        emit_event_fn(
            kind="run_pending_human",
            run_id=run_ctx.run_id,
            step_id=step_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={
                "reason": "plan_execute_requires_hitl",
                "approval_id": approval.approval_id,
            },
        )
        persist_run_output_fn(run_ctx)
        return RunStatus.PENDING_HUMAN.value

    # Execute the approved plan
    executed = execute_action_plan(
        run_ctx=run_ctx,
        gate_obj=gate_obj,
        step_executor=step_executor,
        governance=governance,
        fail_step_fn=fail_step_fn,
        emit_event_fn=emit_event_fn,
    )
    if executed is not None:
        return executed

    run_ctx.meta["last_result_data"] = {
        "summary": "plan_executed",
        "details": {"plan_id": gate_obj.plan_id, "status": gate_obj.status},
    }

    memory.update_step(
        run_ctx.run_id,
        step_id,
        {
            "status": StepStatus.COMPLETED.value,
            "finished_at": int(time.time()),
            "output": {"plan_execute": "ok"},
        },
    )

    emit_event_fn(
        kind="step_completed",
        run_id=run_ctx.run_id,
        step_id=step_id,
        product=run_ctx.product,
        flow=run_ctx.flow,
        payload={"ok": True},
    )

    return "continue"


# ============================================================================
# Action Plan Execution
# ============================================================================


def execute_action_plan(
    *,
    run_ctx: RunContext,
    gate_obj: PlanGateResult,
    step_executor: "StepExecutor",
    governance: "GovernanceHooks",
    fail_step_fn: Callable[..., str],
    emit_event_fn: Callable[..., None],
) -> Optional[str]:
    """
    Execute an approved action plan.

    Iterates through approved steps in the plan and executes each one.

    Args:
        run_ctx: Run context
        gate_obj: Plan gate result with approved steps
        step_executor: Step executor
        governance: Governance hooks
        fail_step_fn: Function to call when step fails
        emit_event_fn: Function to emit events

    Returns:
        None on success, status string on failure
    """
    for idx, step in enumerate(gate_obj.approved_steps):
        step_id = f"plan_step_{idx}"

        if isinstance(step, PlanToolCall):
            step_ctx = run_ctx.new_step(
                step_id=step_id,
                step_type="tool",
                backend="local",
                target=step.tool_name,
            )
            emit_event_fn(
                kind="plan_step_started",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"kind": "tool", "tool": step.tool_name},
            )

            result = step_executor.tool_executor.execute(
                tool_name=step.tool_name,
                params=step.inputs,
                ctx=step_ctx,
            )
            if not result.ok:
                return fail_step_fn(
                    run_ctx=run_ctx,
                    step_id=step_id,
                    reason="plan_step_failed",
                    message="tool_failed",
                )

            evidence_ids = [item.id for item in result.evidence]
            run_ctx.artifacts.setdefault("plan.evidence", []).extend(result.evidence)

            emit_event_fn(
                kind="plan_step_completed",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={
                    "kind": "tool",
                    "tool": step.tool_name,
                    "evidence_ids": evidence_ids,
                },
            )

        elif isinstance(step, PlanAgentCall):
            step_ctx = run_ctx.new_step(
                step_id=step_id,
                step_type="agent",
                backend="local",
                target=step.agent_name,
            )
            emit_event_fn(
                kind="plan_step_started",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"kind": "agent", "agent": step.agent_name},
            )

            agent = AgentRegistry.resolve(step.agent_name)
            agent_result = agent.run(step_ctx)

            if not agent_result.ok:
                return fail_step_fn(
                    run_ctx=run_ctx,
                    step_id=step_id,
                    reason="plan_step_failed",
                    message="agent_failed",
                )

            decision = governance.validate_agent_output(
                agent_name=step.agent_name,
                output=agent_result.data or {},
                ctx=step_ctx,
            )
            if not decision.allowed:
                return fail_step_fn(
                    run_ctx=run_ctx,
                    step_id=step_id,
                    reason=decision.reason,
                    message="agent_output_denied",
                )

            run_ctx.artifacts.setdefault("plan.agent_outputs", []).append(
                agent_result.data or {}
            )

            emit_event_fn(
                kind="plan_step_completed",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"kind": "agent", "agent": step.agent_name},
            )

    return None
