from __future__ import annotations

# ==============================
# Orchestrator Engine
# ==============================

import base64
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, List, Union
from uuid import uuid4

from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.flow_schema import FlowDef, StepDef, StepType
from core.contracts.action_plan_schema import PlanGateResult
from core.contracts.budget_schema import Budget
from core.contracts.context_pack_schema import ContextPack
from core.contracts.interaction_schema import HitlInputSchema, HitlRequest, HitlResolution
from core.contracts.run_schema import (
    RunOperationResult,
    RunRecord,
    RunStatus,
    StepRecord,
    StepStatus,
    TraceEvent,
)
from core.contracts.semantic_schema import (
    NextAction,
    SemanticEnvelope,
)
from core.contracts.user_input_schema import (
    UserInputAnswer,
    UserInputModes,
    UserInputOption,
    UserInputPrompt,
    UserInputRequest,
    UserInputResponse,
)
from core.contracts.question_schema import QuestionSet, UserAnswers
from core.governance.hooks import GovernanceHooks
from core.orchestrator.branching import evaluate_condition, summarize_condition
from core.contracts.budget_schema import BudgetPolicy
from core.governance.budgeting import resolve_budget, init_budget_state
from core.governance.security import SecurityRedactor
from core.memory.tracing import Tracer
from core.memory.router import MemoryRouter
from core.orchestrator.context import RunContext
from core.orchestrator.flow_loader import FlowLoader
from core.orchestrator.hitl import HitlService
from core.orchestrator.state import is_valid_run_transition, to_run_state
from core.orchestrator.step_executor import StepExecutor
from core.orchestrator.run_lifecycle import (
    start_run,
    complete_run,
    fail_run,
    persist_run_output,
    transition_run_status,
    init_run_meta,
    summary_with_counters,
    _precreate_steps as precreate_steps,
)
from core.orchestrator.user_input_handler import (
    ValidationResult,
    build_user_input_prompt,
    build_question_set_request,
    build_hitl_request,
    validate_user_input,
    validate_user_input_values,
    validate_question_set_answers,
    merge_into_context_pack,
    looks_like_user_input_answer,
    looks_like_question_set_answers,
    answer_to_response,
    store_user_input_artifacts,
    resolve_question_set_from_request,
    question_set_key_from_request,
    context_pack_key_from_request,
    summarize_schema,
)
from core.orchestrator.plan_executor import (
    handle_plan_propose,
    handle_plan_gate,
    handle_plan_execute,
    execute_action_plan,
)
from core.orchestrator.loop_executor import (
    handle_repeat_until,
)
from core.orchestrator.templating import render_params
from core.knowledge.context_pack_merge import merge_answers_into_context_pack
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry
from core.contracts.run_schema import ArtifactRef
from core.utils.reasoning_exporter import build_reasoning_markdown


def _new_run_id() -> str:
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S%f")
    return f"run_{ts}_{uuid4().hex[:8]}"


def _payload_size_bytes(payload: Dict[str, Any]) -> int:
    try:
        raw = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    except Exception:
        raw = str(payload)
    return len(raw.encode("utf-8"))


class OrchestratorEngine:
    """
    Orchestrator entrypoint. Holds only shared dependencies; all run state is request-scoped.
    """
    __slots__ = ("flow_loader", "step_executor", "memory", "tracer", "governance", "hitl")
    def __init__(
        self,
        *,
        flow_loader: FlowLoader,
        step_executor: StepExecutor,
        memory: MemoryRouter,
        tracer: Tracer,
        governance: GovernanceHooks,
    ) -> None:
        self.flow_loader = flow_loader
        self.step_executor = step_executor
        self.memory = memory
        self.tracer = tracer
        self.governance = governance
        self.hitl = HitlService(memory)

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        *,
        memory: Optional[MemoryRouter] = None,
        tracer: Optional[Tracer] = None,
        sleep_fn: Optional[Callable[[float], None]] = None,
    ) -> "OrchestratorEngine":
        repo_root = settings.repo_root_path()
        products_root = repo_root / settings.products.products_dir
        flow_loader = FlowLoader(products_root=products_root)
        memory_router = memory or MemoryRouter.from_settings(settings)
        redactor = SecurityRedactor.from_settings(settings)
        tracer_instance = tracer or Tracer.from_settings(settings=settings, memory=memory_router)
        governance = GovernanceHooks(settings=settings, redactor=redactor)
        tool_executor = ToolExecutor(registry=ToolRegistry, hooks=governance, redactor=redactor)
        step_executor = StepExecutor(
            tool_executor=tool_executor,
            governance=governance,
            agent_registry=AgentRegistry,
            sleep_fn=sleep_fn or time.sleep,
        )
        return cls(
            flow_loader=flow_loader,
            step_executor=step_executor,
            memory=memory_router,
            tracer=tracer_instance,
            governance=governance,
        )

    # ------------------------------------------------------------------ API
    def run_flow(
        self,
        *,
        product: str,
        flow: str,
        payload: Dict[str, Any],
        requested_by: Optional[str] = None,
    ) -> RunOperationResult:
        try:
            flow_def = self.flow_loader.load(product=product, flow=flow)
            run_id = _new_run_id()
            run_ctx = RunContext(run_id=run_id, product=product, flow=flow, payload=payload)
            run_ctx.trace = self._trace_hook(run_ctx)
            self._resolve_budget(run_ctx, flow_def)

            payload_limit = self.governance.settings.policies.max_payload_bytes
            if payload_limit is not None:
                size_bytes = _payload_size_bytes(payload)
                if size_bytes > payload_limit:
                    return self._reject_run(
                        run_id=run_id,
                        product=product,
                        flow=flow,
                        autonomy_level=str(flow_def.autonomy_level.value),
                        payload=payload,
                        code="payload_limit_exceeded",
                        message="Payload exceeds configured limit.",
                        details={"size_bytes": size_bytes, "limit_bytes": payload_limit},
                    )

            step_limit = self.governance.settings.policies.max_steps
            if step_limit is not None and len(flow_def.steps) > step_limit:
                return self._reject_run(
                    run_id=run_id,
                    product=product,
                    flow=flow,
                    autonomy_level=str(flow_def.autonomy_level.value),
                    payload=payload,
                    code="max_steps_exceeded",
                    message="Flow exceeds configured step limit.",
                    details={"step_count": len(flow_def.steps), "limit": step_limit},
                )

            autonomy_decision = self.governance.check_autonomy(
                run_ctx=run_ctx,
                autonomy=flow_def.autonomy_level,
            )
            if not autonomy_decision.allowed:
                now = int(time.time())
                run_record = RunRecord(
                    run_id=run_id,
                    product=product,
                    flow=flow,
                    status=RunStatus.FAILED,
                    autonomy_level=str(flow_def.autonomy_level.value),
                    started_at=now,
                    finished_at=now,
                    input=payload,
                    summary={
                        "error": autonomy_decision.reason or "autonomy_denied",
                        "autonomy_level": flow_def.autonomy_level.value,
                    },
                )
                self.memory.create_run(run_record)
                run_ctx = RunContext(run_id=run_id, product=product, flow=flow, payload=payload)
                self._attach_run_dirs(run_ctx)
                self._stage_inputs(run_ctx)
                self._emit_event(
                    kind="autonomy_denied",
                    run_id=run_id,
                    step_id=None,
                    product=product,
                    flow=flow,
                    payload={
                        "reason": autonomy_decision.reason,
                        "autonomy_level": flow_def.autonomy_level.value,
                    },
                )
                self._persist_run_output(run_ctx)
                return RunOperationResult.failure(
                    code="autonomy_denied",
                    message=autonomy_decision.reason or "Autonomy denied by policy.",
                )

            branch_decision = self.governance.validate_branch_conditions(flow_def=flow_def, run_ctx=run_ctx)
            if not branch_decision.allowed:
                return self._reject_run(
                    run_id=run_id,
                    product=product,
                    flow=flow,
                    autonomy_level=str(flow_def.autonomy_level.value),
                    payload=payload,
                    code="branch_condition_disallowed",
                    message=branch_decision.reason or "Branch condition disallowed.",
                    details=branch_decision.details,
                )
            loop_decision = self.governance.validate_loop_conditions(flow_def=flow_def, run_ctx=run_ctx)
            if not loop_decision.allowed:
                return self._reject_run(
                    run_id=run_id,
                    product=product,
                    flow=flow,
                    autonomy_level=str(flow_def.autonomy_level.value),
                    payload=payload,
                    code="loop_condition_disallowed",
                    message=loop_decision.reason or "Loop condition disallowed.",
                    details=loop_decision.details,
                )

            run_record = RunRecord(
                run_id=run_id,
                product=product,
                flow=flow,
                status=RunStatus.RUNNING,
                autonomy_level=str(flow_def.autonomy_level.value),
                input=payload,
                summary={
                    "current_step_index": 0,
                    "steps_executed": 0,
                    "tool_calls": 0,
                    "tokens_used": 0,
                    "loops": {},
                },
            )
            self.memory.create_run(run_record)
            self._precreate_steps(flow_def=flow_def, run_ctx=run_ctx)
            run_ctx.meta.update({"steps_executed": 0, "tool_calls": 0, "tokens_used": 0})
            self.memory.clear_staging(product=product, clear_input=False, clear_output=True)
            self._attach_run_dirs(run_ctx)
            self._stage_inputs(run_ctx)

            self._emit_event(
                kind="run_started",
                run_id=run_id,
                step_id=None,
                product=product,
                flow=flow,
                payload={"autonomy_level": flow_def.autonomy_level.value},
            )

            # ORC-SEM-001: Execute semantic interpretation phase before step execution
            should_continue, envelope, error_code = self._run_semantic_interpretation(
                run_ctx=run_ctx,
                flow_def=flow_def,
            )
            
            # Store semantic envelope in run record if produced
            if envelope is not None:
                self.memory.update_run(
                    run_id,
                    {"semantic_envelope": envelope.model_dump(mode="json")},
                )
            
            if not should_continue:
                # Handle semantic phase stop/abort
                if error_code == "semantic_abort":
                    # ORC-SEM-STOP-004: Transition to FAILED
                    self._transition_run_status(
                        run_id=run_id,
                        product=product,
                        flow=flow,
                        current_status=RunStatus.RUNNING,
                        target_status=RunStatus.FAILED,
                        step_id=None,
                        summary={
                            "error": error_code,
                            "ambiguities": envelope.ambiguities if envelope else [],
                        },
                        reason="semantic_abort",
                    )
                    self._persist_run_output(run_ctx)
                    return RunOperationResult.failure(
                        code="semantic_abort",
                        message="Semantic interpretation aborted the run.",
                        details={
                            "run_id": run_id,
                            "ambiguities": envelope.ambiguities if envelope else [],
                        },
                    )
                
                if error_code == "semantic_ask_user":
                    # ORC-SEM-STOP-002: Transition to PAUSED_WAITING_FOR_USER
                    self._transition_run_status(
                        run_id=run_id,
                        product=product,
                        flow=flow,
                        current_status=RunStatus.RUNNING,
                        target_status=RunStatus.PAUSED_WAITING_FOR_USER,
                        step_id=None,
                        summary={
                            "semantic_pause": True,
                            "ambiguities": envelope.ambiguities if envelope else [],
                        },
                        reason="semantic_ask_user",
                    )
                    self._persist_run_output(run_ctx)
                    return RunOperationResult.success({
                        "run_id": run_id,
                        "status": RunStatus.PAUSED_WAITING_FOR_USER.value,
                        "clarification_needed": True,
                        "ambiguities": envelope.ambiguities if envelope else [],
                    })
                
                if error_code == "semantic_needs_approval":
                    # ORC-SEM-STOP-006: Transition to PENDING_HUMAN
                    self._transition_run_status(
                        run_id=run_id,
                        product=product,
                        flow=flow,
                        current_status=RunStatus.RUNNING,
                        target_status=RunStatus.PENDING_HUMAN,
                        step_id=None,
                        summary={"semantic_approval": True},
                        reason="semantic_needs_approval",
                    )
                    self._persist_run_output(run_ctx)
                    return RunOperationResult.success({
                        "run_id": run_id,
                        "status": RunStatus.PENDING_HUMAN.value,
                        "approval_needed": True,
                    })
                
                # ORC-SEM-004: General semantic failure
                self._transition_run_status(
                    run_id=run_id,
                    product=product,
                    flow=flow,
                    current_status=RunStatus.RUNNING,
                    target_status=RunStatus.FAILED,
                    step_id=None,
                    summary={"error": error_code or "semantic_interpretation_failed"},
                    reason=error_code or "semantic_interpretation_failed",
                )
                self._persist_run_output(run_ctx)
                return RunOperationResult.failure(
                    code=error_code or "semantic_interpretation_failed",
                    message="Semantic interpretation phase failed.",
                    details={"run_id": run_id},
                )

            # ORC-SEM-STOP-007: CONTINUE permits step execution
            status = self._execute_from_index(
                flow_def=flow_def,
                run_ctx=run_ctx,
                start_index=0,
                requested_by=requested_by,
            )
            return RunOperationResult.success({"run_id": run_id, "status": status})
        except Exception as exc:
            return RunOperationResult.failure(code="run_failed", message=str(exc))

    def get_run(self, *, run_id: str) -> RunOperationResult:
        bundle = self.memory.get_run(run_id)
        if bundle is None:
            return RunOperationResult.failure(code="not_found", message=f"Unknown run_id: {run_id}")
        return RunOperationResult.success(
            {
                "run_id": run_id,
                "run": bundle.run.model_dump(),
                "steps": [s.model_dump() for s in bundle.steps],
                "approvals": [a.model_dump() for a in bundle.approvals],
            }
        )

    def _precreate_steps(self, *, flow_def: FlowDef, run_ctx: RunContext) -> None:
        """Delegate to run_lifecycle module."""
        precreate_steps(memory=self.memory, flow_def=flow_def, run_ctx=run_ctx)

    def get_pending_user_input(self, *, run_id: str) -> RunOperationResult:
        bundle = self.memory.get_run(run_id)
        if bundle is None:
            return RunOperationResult.failure(code="not_found", message=f"Unknown run_id: {run_id}")
        if bundle.run.status not in {RunStatus.PENDING_USER_INPUT, RunStatus.PAUSED_WAITING_FOR_USER}:
            return RunOperationResult.success({"run_id": run_id, "pending": False, "prompt": None})
        pending_step = next(
            (s for s in bundle.steps if _is_step_status(s.status, StepStatus.PENDING_USER_INPUT)),
            None,
        )
        if pending_step is None:
            return RunOperationResult.success({"run_id": run_id, "pending": False, "prompt": None})
        prompt_payload = None
        if isinstance(pending_step.output, dict):
            request_payload = pending_step.output.get("user_input_request")
            if isinstance(request_payload, dict):
                prompt_payload = request_payload.get("prompt")
        if not isinstance(prompt_payload, dict):
            flow_def = self.flow_loader.load(product=bundle.run.product, flow=bundle.run.flow)
            step_def = next((s for s in flow_def.steps if (s.id or "") == pending_step.step_id), None)
            if step_def is None:
                return RunOperationResult.failure(code="invalid_state", message="Pending user input step not found.")
            run_ctx = RunContext(run_id=run_id, product=bundle.run.product, flow=bundle.run.flow, payload=bundle.run.input or {})
            context = {"payload": run_ctx.payload, "artifacts": run_ctx.artifacts}
            rendered_params = render_params(step_def.params or {}, context)
            required = rendered_params.get("required")
            if isinstance(required, list):
                flattened = []
                for item in required:
                    if isinstance(item, list):
                        flattened.extend(item)
                    else:
                        flattened.append(item)
                rendered_params["required"] = flattened
            request = UserInputRequest.model_validate(rendered_params)
            prompt_payload = _build_user_input_prompt(run_ctx=run_ctx, step_id=pending_step.step_id, request=request).model_dump(
                mode="json"
            )
        return RunOperationResult.success({"run_id": run_id, "pending": True, "prompt": prompt_payload})

    def resume_run(
        self,
        *,
        run_id: str,
        approval_payload: Optional[Dict[str, Any]] = None,
        user_input_response: Optional[Dict[str, Any]] = None,
        decision: str = "APPROVED",
        resolved_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> RunOperationResult:
        bundle = self.memory.get_run(run_id)
        if bundle is None:
            return RunOperationResult.failure(code="not_found", message=f"Unknown run_id: {run_id}")

        if bundle.run.status in {RunStatus.PENDING_USER_INPUT, RunStatus.PAUSED_WAITING_FOR_USER}:
            return self._resume_user_input(
                bundle=bundle,
                user_input_response=user_input_response,
                resolved_by=resolved_by,
                comment=comment,
            )

        if bundle.run.status != RunStatus.PENDING_HUMAN:
            return RunOperationResult.failure(code="invalid_state", message="Run is not awaiting approval.")

        pending = [a for a in bundle.approvals if a.status == "PENDING"]
        if not pending:
            return RunOperationResult.failure(code="invalid_state", message="No pending approvals.")

        approval = pending[0]
        payload = approval_payload or {}
        if "approved" not in payload:
            return RunOperationResult.failure(code="missing_approval_field", message="Approval payload must include 'approved' flag.")

        self.hitl.resolve_approval(
            approval_id=approval.approval_id,
            decision=decision,
            resolved_by=resolved_by,
            comment=comment,
        )
        self.memory.append_run_comment(
            product=bundle.run.product,
            run_id=run_id,
            comment=comment,
            decision=decision,
            step_id=approval.step_id,
            ts=int(time.time()),
        )

        step_status = StepStatus.COMPLETED
        if not payload.get("approved") or decision.upper() != "APPROVED":
            step_status = StepStatus.FAILED

        self.memory.update_step(
            run_id,
            approval.step_id,
            {
                "status": step_status.value,
                "finished_at": int(time.time()),
                "output": {
                    "approval": {
                        "decision": decision,
                        "comment": comment,
                        "payload": payload,
                    },
                    "hitl_resolution": HitlResolution(
                        request_id=approval.approval_id,
                        request_type="APPROVAL",
                        status="ACCEPTED" if step_status == StepStatus.COMPLETED else "REJECTED",
                        resolved_at=int(time.time()),
                        decision=decision,
                        comment=comment,
                        resolved_by=resolved_by,
                    ).model_dump(mode="json"),
                },
            },
        )

        if step_status == StepStatus.FAILED:
            if comment:
                rejected_count = sum(
                    1 for a in bundle.approvals if a.step_id == approval.step_id and a.status == "REJECTED"
                )
                if not payload.get("approved") or decision.upper() != "APPROVED":
                    rejected_count += 1
                if rejected_count >= 2:
                    return RunOperationResult.success({"run_id": run_id, "status": RunStatus.FAILED.value})
                replan_payload = dict(bundle.run.input or {})
                replan_payload.update(
                    {
                        "replan_comment": comment,
                        "previous_run": {
                            "run": bundle.run.model_dump(),
                            "steps": [s.model_dump() for s in bundle.steps],
                            "approvals": [a.model_dump() for a in bundle.approvals],
                        },
                    }
                )
                replan_flow = self.flow_loader.load(product=bundle.run.product, flow=bundle.run.flow)
                plan_index = None
                plan_def = None
                for idx, definition in enumerate(replan_flow.steps):
                    if (definition.id or f"step_{idx}") in {"plan", "planning"}:
                        plan_index = idx
                        plan_def = definition
                        break
                self._transition_run_status(
                    run_id=run_id,
                    product=bundle.run.product,
                    flow=bundle.run.flow,
                    current_status=bundle.run.status,
                    target_status=RunStatus.RUNNING,
                    step_id=approval.step_id,
                    summary={**(bundle.run.summary or {}), "current_step_index": plan_index or 0, "replan_of": run_id},
                    reason="replan_after_rejection",
                )
                replan_ctx = RunContext(
                    run_id=run_id,
                    product=bundle.run.product,
                    flow=bundle.run.flow,
                    payload=replan_payload,
                )
                self._init_run_meta(replan_ctx, summary=bundle.run.summary, steps=bundle.steps)
                replan_ctx.trace = self._trace_hook(replan_ctx)
                self._attach_run_dirs(replan_ctx)
                self._stage_inputs(replan_ctx)
                self._rehydrate_artifacts(bundle.steps, replan_ctx)
                self._emit_event(
                    kind="run_replan_started",
                    run_id=run_id,
                    step_id=None,
                    product=bundle.run.product,
                    flow=bundle.run.flow,
                    payload={"previous_run": run_id, "start_index": plan_index or 0},
                )
                next_index = 0
                if plan_def is not None and plan_index is not None:
                    replan_step_id = f"replan_plan_{int(time.time())}"
                    step_record = StepRecord(
                        run_id=run_id,
                        step_id=replan_step_id,
                        step_index=len(bundle.steps),
                        name=plan_def.name or "replan_plan",
                        type=plan_def.type.value,
                        status=StepStatus.RUNNING,
                        started_at=int(time.time()),
                        input={"params": plan_def.params or {}},
                        meta={"backend": plan_def.backend.value if getattr(plan_def.backend, "value", None) else plan_def.backend},
                    )
                    self.memory.add_step(step_record)
                    self._emit_event(
                        kind="step_started",
                        run_id=run_id,
                        step_id=replan_step_id,
                        product=bundle.run.product,
                        flow=bundle.run.flow,
                        payload={"step_index": step_record.step_index, "type": plan_def.type.value, "name": step_record.name},
                    )
                    try:
                        plan_result = self.step_executor.execute(run_ctx=replan_ctx, step_def=plan_def, step_id=replan_step_id)
                        self.memory.update_step(
                            run_id,
                            replan_step_id,
                            {"status": StepStatus.COMPLETED.value, "finished_at": int(time.time()), "output": plan_result},
                        )
                        self._emit_event(
                            kind="step_completed",
                            run_id=run_id,
                            step_id=replan_step_id,
                            product=bundle.run.product,
                            flow=bundle.run.flow,
                            payload={"ok": True},
                        )
                        next_index = self._resolve_plan_next_index(replan_flow, plan_index, plan_result)
                    except Exception as exc:
                        self.memory.update_step(
                            run_id,
                            replan_step_id,
                            {
                                "status": StepStatus.FAILED.value,
                                "finished_at": int(time.time()),
                                "error": {"message": str(exc), "type": type(exc).__name__},
                            },
                        )
                        self._transition_run_status(
                            run_id=run_id,
                            product=bundle.run.product,
                            flow=bundle.run.flow,
                            current_status=RunStatus.RUNNING,
                            target_status=RunStatus.FAILED,
                            step_id=replan_step_id,
                            summary=self._summary_with_counters(replan_ctx, {"failed_step_id": replan_step_id}),
                            reason="replan_failed",
                        )
                        self._emit_event(
                            kind="step_failed",
                            run_id=run_id,
                            step_id=replan_step_id,
                            product=bundle.run.product,
                            flow=bundle.run.flow,
                            payload={"error": {"message": str(exc), "type": type(exc).__name__}},
                        )
                        self._persist_run_output(replan_ctx)
                        return RunOperationResult.success({"run_id": run_id, "status": RunStatus.FAILED.value})
                status = self._execute_from_index(
                    flow_def=replan_flow,
                    run_ctx=replan_ctx,
                    start_index=next_index,
                    requested_by=resolved_by,
                )
                return RunOperationResult.success({"run_id": run_id, "status": status})
            self._transition_run_status(
                run_id=run_id,
                product=bundle.run.product,
                flow=bundle.run.flow,
                current_status=bundle.run.status,
                target_status=RunStatus.FAILED,
                step_id=approval.step_id,
                summary={**(bundle.run.summary or {}), "rejection": decision},
                reason="approval_rejected",
            )
            self._emit_event(
                kind="run_rejected",
                run_id=run_id,
                step_id=approval.step_id,
                product=bundle.run.product,
                flow=bundle.run.flow,
                payload={"decision": decision, "approved": payload.get("approved"), "comment": comment},
            )
            return RunOperationResult.success({"run_id": run_id, "status": RunStatus.FAILED.value})

        flow_def = self.flow_loader.load(product=bundle.run.product, flow=bundle.run.flow)
        next_index = self._find_step_index(flow_def, approval.step_id) + 1
        self._transition_run_status(
            run_id=run_id,
            product=bundle.run.product,
            flow=bundle.run.flow,
            current_status=bundle.run.status,
            target_status=RunStatus.RUNNING,
            step_id=approval.step_id,
            summary={**(bundle.run.summary or {}), "current_step_index": next_index},
            reason="approval_resumed",
        )
        self._emit_event(
            kind="run_resumed",
            run_id=run_id,
            step_id=approval.step_id,
            product=bundle.run.product,
            flow=bundle.run.flow,
            payload={"decision": decision, "comment": comment},
        )

        merged_payload = dict(bundle.run.input or {})
        merged_payload.update(payload)
        run_ctx = RunContext(run_id=run_id, product=bundle.run.product, flow=bundle.run.flow, payload=merged_payload)
        self._init_run_meta(run_ctx, summary=bundle.run.summary, steps=bundle.steps)
        run_ctx.trace = self._trace_hook(run_ctx)
        self._attach_run_dirs(run_ctx)
        self._rehydrate_artifacts(bundle.steps, run_ctx)

        step_def = next((s for s in flow_def.steps if (s.id or "") == approval.step_id), None)
        if step_def is not None and step_def.type == StepType.PLAN_EXECUTE:
            gate = self._get_artifact_payload(run_ctx, "plan.gate_result")
            if gate is None:
                return RunOperationResult.failure(code="invalid_state", message="plan.gate_result missing for plan_execute")
            gate_obj = PlanGateResult.model_validate(gate)
            executed = self._execute_action_plan(run_ctx, gate_obj)
            if executed is not None:
                return RunOperationResult.success({"run_id": run_id, "status": executed})
            run_ctx.meta["last_result_data"] = {
                "summary": "plan_executed",
                "details": {"plan_id": gate_obj.plan_id, "status": gate_obj.status},
            }

        status = self._execute_from_index(
            flow_def=flow_def,
            run_ctx=run_ctx,
            start_index=next_index,
            requested_by=resolved_by,
        )
        return RunOperationResult.success({"run_id": run_id, "status": status})

    def _resume_user_input(
        self,
        *,
        bundle,
        user_input_response: Optional[Dict[str, Any]],
        resolved_by: Optional[str],
        comment: Optional[str],
    ) -> RunOperationResult:
        response_payload = user_input_response or {}
        answer: Optional[UserInputAnswer] = None
        response: Optional[UserInputResponse] = None
        question_answers: Optional[UserAnswers] = None
        try:
            if _looks_like_question_set_answers(response_payload):
                question_answers = UserAnswers.model_validate(response_payload)
            elif _looks_like_user_input_answer(response_payload):
                answer = UserInputAnswer.model_validate(response_payload)
            else:
                response = UserInputResponse.model_validate(response_payload)
        except Exception as exc:
            return RunOperationResult.failure(code="invalid_input", message=str(exc))

        flow_def = self.flow_loader.load(product=bundle.run.product, flow=bundle.run.flow)
        pending_step = next(
            (s for s in bundle.steps if _is_step_status(s.status, StepStatus.PENDING_USER_INPUT)),
            None,
        )
        if pending_step is None:
            return RunOperationResult.failure(code="invalid_state", message="No pending user input.")

        step_id = pending_step.step_id
        step_def = next((s for s in flow_def.steps if (s.id or "") == step_id), None)
        if step_def is None:
            return RunOperationResult.failure(code="invalid_state", message="Pending step not found in flow.")

        run_ctx = RunContext(run_id=bundle.run.run_id, product=bundle.run.product, flow=bundle.run.flow, payload=bundle.run.input or {})
        self._init_run_meta(run_ctx, summary=bundle.run.summary, steps=bundle.steps)
        run_ctx.trace = self._trace_hook(run_ctx)
        self._rehydrate_artifacts(bundle.steps, run_ctx)

        try:
            context = {"payload": run_ctx.payload, "artifacts": run_ctx.artifacts}
            rendered_params = render_params(step_def.params or {}, context)
            question_set_payload = rendered_params.pop("question_set", None)
            context_pack_key = rendered_params.pop("context_pack_key", None)
            required = rendered_params.get("required")
            if isinstance(required, list):
                flattened = []
                for item in required:
                    if isinstance(item, list):
                        flattened.extend(item)
                    else:
                        flattened.append(item)
                rendered_params["required"] = flattened
            if question_set_payload is not None:
                question_set = QuestionSet.model_validate(question_set_payload)
                question_set_key = f"question_set.{question_set.id}"
                run_ctx.artifacts.setdefault(question_set_key, question_set.model_dump(mode="json"))
                request = _build_question_set_request(
                    question_set=question_set,
                    question_set_key=question_set_key,
                    context_pack_key=context_pack_key,
                )
            else:
                request = UserInputRequest.model_validate(rendered_params)
        except Exception as exc:
            return RunOperationResult.failure(code="invalid_state", message=str(exc))

        if response is None and answer is not None:
            if answer.prompt_id != request.form_id:
                return RunOperationResult.failure(code="invalid_input", message="prompt_id does not match pending request.")
            response = _answer_to_response(request, answer, comment=comment)

        if response is None and question_answers is None:
            return RunOperationResult.failure(code="invalid_input", message="Missing user input response.")

        if response is not None and response.form_id != request.form_id:
            return RunOperationResult.failure(code="invalid_input", message="form_id does not match pending request.")
        if response is not None and response.metadata and "metadata" not in response.values:
            response.values["metadata"] = response.metadata

        step_ctx = run_ctx.new_step(
            step_def=step_def,
            step_id=step_id,
            step_type=step_def.type.value,
            backend=step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend,
            target=step_def.agent or step_def.tool,
        )
        response_payload_json = response.model_dump(mode="json") if response is not None else question_answers.model_dump(mode="json")
        decision = self.governance.before_user_input_response(
            request=request.model_dump(mode="json"),
            response=response_payload_json,
            ctx=step_ctx,
        )
        if not decision.allowed:
            self._emit_event(
                kind="user_input_denied",
                run_id=bundle.run.run_id,
                step_id=step_id,
                product=bundle.run.product,
                flow=bundle.run.flow,
                payload={"reason": decision.reason, "details": decision.details},
            )
            return RunOperationResult.failure(code="policy_blocked", message=decision.reason, details=decision.details)

        question_set = _resolve_question_set_from_request(request, run_ctx)
        if question_set is not None:
            if question_answers is None:
                question_answers = UserAnswers(question_set_id=question_set.id, answers=response.values if response else {})
            errors = _validate_question_set_answers(question_set, question_answers)
        else:
            # Flexible validation: supports text-only, schema-only, or mixed inputs
            response_values = response.values if response else {}
            
            # Check for free text input (can come as "text", "response", or any non-schema key)
            # This supports products like ADE that use text-only input for reasoning
            has_free_text = bool(
                response_values.get("text") or 
                response_values.get("response") or
                response_values.get("free_text")
            )
            
            # If free_text is provided, accept it - skip schema validation entirely
            if has_free_text:
                errors = []
            elif request.required:
                # Schema mode: validate required fields
                errors = _validate_user_input_values(request, response_values)
            else:
                # No required fields - accept any input
                errors = [] if response_values else ["no_input_provided"]
        if errors:
            self.memory.update_step(
                bundle.run.run_id,
                step_id,
                {
                    "status": StepStatus.PENDING_USER_INPUT.value,
                    "output": {"validation_errors": errors},
                },
            )
            self._emit_event(
                kind="user_input_validation_failed",
                run_id=bundle.run.run_id,
                step_id=step_id,
                product=bundle.run.product,
                flow=bundle.run.flow,
                payload={
                    "form_id": request.form_id,
                    "question_set_id": question_set.id if question_set is not None else None,
                    "errors": errors,
                },
            )
            return RunOperationResult.failure(code="invalid_input", message="User input validation failed.", details={"errors": errors})

        if question_set is not None and question_answers is not None:
            context_pack_key = _context_pack_key_from_request(request)
            merged_pack = _merge_context_pack_if_present(
                run_ctx=run_ctx,
                question_set=question_set,
                answers=question_answers,
                context_pack_key=context_pack_key,
            )
        else:
            merged_pack = None
            context_pack_key = None

        # Merge defaults from request with provided values
        # This ensures that schema fields not provided by user (e.g., when free text is used)
        # still have sensible defaults for downstream steps
        response_values = response.values if response is not None else question_answers.answers
        request_defaults = request.defaults if hasattr(request, 'defaults') and request.defaults else {}
        accepted_values = {**request_defaults, **response_values}  # response values override defaults
        accepted_comment = response.comment if response is not None else (comment or "")

        # Build the user_input dict with merged values for proper artifact rehydration on resume
        user_input_for_storage = response.model_dump(mode="json") if response is not None else question_answers.model_dump(mode="json")
        user_input_for_storage["values"] = accepted_values  # Override with merged defaults

        self.memory.update_step(
            bundle.run.run_id,
            step_id,
            {
                "status": StepStatus.COMPLETED.value,
                "finished_at": int(time.time()),
                "output": {
                    "user_input": user_input_for_storage,
                    "hitl_resolution": HitlResolution(
                        request_id=request.form_id,
                        request_type="INPUT",
                        status="PROVIDED",
                        resolved_at=int(time.time()),
                        values=accepted_values,
                        comment=accepted_comment,
                        resolved_by=resolved_by,
                    ).model_dump(mode="json"),
                    "question_set": question_set.model_dump(mode="json") if question_set is not None else None,
                    "question_set_key": _question_set_key_from_request(request),
                    "context_pack_key": context_pack_key if question_set is not None else None,
                    "context_pack": merged_pack.model_dump(mode="json") if merged_pack is not None else None,
                },
            },
        )

        self.memory.write_user_input_response(
            product=bundle.run.product,
            run_id=bundle.run.run_id,
            form_id=request.form_id,
            payload=response_payload_json,
        )

        self._emit_event(
            kind="user_input_received",
            run_id=bundle.run.run_id,
            step_id=step_id,
            product=bundle.run.product,
            flow=bundle.run.flow,
            payload={
                "form_id": request.form_id,
                "mode": request.mode,
                "values": accepted_values,
                "comment": accepted_comment,
            },
        )
        self._emit_event(
            kind="user_input_accepted",
            run_id=bundle.run.run_id,
            step_id=step_id,
            product=bundle.run.product,
            flow=bundle.run.flow,
            payload={"question_set_id": question_set.id if question_set is not None else None},
        )
        if question_set is not None and merged_pack is not None:
            self._emit_event(
                kind="context_pack_merged",
                run_id=bundle.run.run_id,
                step_id=step_id,
                product=bundle.run.product,
                flow=bundle.run.flow,
                payload={
                    "question_set_id": question_set.id,
                    "keys_added_count": len(question_answers.answers),
                },
            )

        next_index = self._find_step_index(flow_def, step_id) + 1
        self._transition_run_status(
            run_id=bundle.run.run_id,
            product=bundle.run.product,
            flow=bundle.run.flow,
            current_status=bundle.run.status,
            target_status=RunStatus.RUNNING,
            step_id=step_id,
            summary={"current_step_index": next_index},
            reason="user_input_resumed",
        )
        self._emit_event(
            kind="run_resumed",
            run_id=bundle.run.run_id,
            step_id=step_id,
            product=bundle.run.product,
            flow=bundle.run.flow,
            payload={"reason": "user_input_resumed"},
        )

        self._attach_run_dirs(run_ctx)
        self._rehydrate_artifacts(bundle.steps, run_ctx)
        _store_user_input_artifacts(run_ctx, request.form_id, accepted_values, accepted_comment)

        status = self._execute_from_index(
            flow_def=flow_def,
            run_ctx=run_ctx,
            start_index=next_index,
            requested_by=resolved_by,
        )
        return RunOperationResult.success({"run_id": bundle.run.run_id, "status": status})

    # ------------------------------------------------------------------ internals
    def _trace_hook(self, run_ctx: RunContext):
        def _hook(event_type: str, payload: Dict[str, Any]) -> None:
            self._emit_event(
                kind=event_type,
                run_id=run_ctx.run_id,
                step_id=payload.get("step_id"),
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload=payload,
            )

        return _hook

    def _resolve_budget(self, run_ctx: RunContext, flow_def: FlowDef) -> None:
        policy_raw = run_ctx.payload.get("_budget_policy")
        if not isinstance(policy_raw, dict):
            return
        try:
            policy = BudgetPolicy.model_validate(policy_raw)
        except Exception:
            return
        sensitivity = str(run_ctx.payload.get("_budget_sensitivity") or "LOW")
        flow_type = str((flow_def.metadata or {}).get("flow_type") or flow_def.id)
        budget = resolve_budget(policy, sensitivity_class=sensitivity, flow_type=flow_type)
        state = init_budget_state()
        run_ctx.meta["budget"] = budget
        run_ctx.meta["budget_state"] = state
        self._emit_event(
            kind="budget_resolved",
            run_id=run_ctx.run_id,
            step_id=None,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={
                "sensitivity_class": sensitivity,
                "flow_type": flow_type,
                "budget": budget.model_dump(mode="json"),
            },
        )

    def _transition_run_status(
        self,
        *,
        run_id: str,
        product: str,
        flow: str,
        current_status: Union[RunStatus, str],
        target_status: Union[RunStatus, str],
        step_id: Optional[str],
        summary: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
    ) -> RunStatus:
        """Delegate to run_lifecycle module."""
        return transition_run_status(
            memory=self.memory,
            emit_event_fn=self._emit_event,
            run_id=run_id,
            product=product,
            flow=flow,
            current_status=current_status,
            target_status=target_status,
            step_id=step_id,
            summary=summary,
            reason=reason,
        )

    def _execute_from_index(
        self,
        *,
        flow_def: FlowDef,
        run_ctx: RunContext,
        start_index: int,
        requested_by: Optional[str],
    ) -> str:
        idx = start_index
        current_status = RunStatus.RUNNING
        last_result_data: Optional[Dict[str, Any]] = None
        while idx < len(flow_def.steps):
            step_def = flow_def.steps[idx]
            step_id = step_def.id or f"step_{idx}"
            if idx > 0:
                prev_def = flow_def.steps[idx - 1]
                if (
                    prev_def.type == StepType.USER_INPUT
                    and (prev_def.params or {}).get("mode") == UserInputModes.FREE_TEXT_INPUT
                    and step_def.type in {StepType.AGENT, StepType.TOOL}
                ):
                    prev_constraints = (prev_def.params or {}).get("constraints")
                    if isinstance(prev_constraints, dict):
                        allow_agents = prev_constraints.get("allow_next_agents") or []
                        allow_tools = prev_constraints.get("allow_next_tools") or []
                        if step_def.type == StepType.AGENT and step_def.agent in allow_agents:
                            pass
                        elif step_def.type == StepType.TOOL and step_def.tool in allow_tools:
                            pass
                        else:
                            self._transition_run_status(
                                run_id=run_ctx.run_id,
                                product=run_ctx.product,
                                flow=run_ctx.flow,
                                current_status=current_status,
                                target_status=RunStatus.FAILED,
                                step_id=step_id,
                                summary={"failed_step_id": step_id},
                                reason="free_text_guard_blocked",
                            )
                            current_status = RunStatus.FAILED
                            self._emit_event(
                                kind="free_text_guard_blocked",
                                run_id=run_ctx.run_id,
                                step_id=step_id,
                                product=run_ctx.product,
                                flow=run_ctx.flow,
                                payload={"message": "Free-text input cannot directly trigger tools or agents."},
                            )
                            self._persist_run_output(run_ctx)
                            return RunStatus.FAILED.value
                    else:
                        self._transition_run_status(
                            run_id=run_ctx.run_id,
                            product=run_ctx.product,
                            flow=run_ctx.flow,
                            current_status=current_status,
                            target_status=RunStatus.FAILED,
                            step_id=step_id,
                            summary={"failed_step_id": step_id},
                            reason="free_text_guard_blocked",
                        )
                        current_status = RunStatus.FAILED
                        self._emit_event(
                            kind="free_text_guard_blocked",
                            run_id=run_ctx.run_id,
                            step_id=step_id,
                            product=run_ctx.product,
                            flow=run_ctx.flow,
                            payload={"message": "Free-text input cannot directly trigger tools or agents."},
                        )
                        self._persist_run_output(run_ctx)
                        return RunStatus.FAILED.value

            step_record = StepRecord(
                run_id=run_ctx.run_id,
                step_id=step_id,
                step_index=idx,
                name=step_def.name or step_id,
                type=step_def.type.value,
                status=StepStatus.RUNNING,
                started_at=int(time.time()),
                input={"params": step_def.params or {}},
                meta={"backend": step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend},
            )
            self.memory.add_step(step_record)

            step_ctx = run_ctx.new_step(
                step_def=step_def,
                step_id=step_id,
                step_type=step_def.type.value,
                backend=step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend,
                target=step_def.agent or step_def.tool,
            )

            decision = self.governance.before_step(step_ctx=step_ctx)
            if not decision.allowed:
                self._emit_event(
                    kind="before_step_denied",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={"reason": decision.reason},
                )
                self.memory.update_step(
                    run_ctx.run_id,
                    step_id,
                    {
                        "status": StepStatus.FAILED.value,
                        "finished_at": int(time.time()),
                        "error": {"message": decision.reason, "type": "PermissionError"},
                    },
                )
                self._transition_run_status(
                    run_id=run_ctx.run_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    current_status=current_status,
                    target_status=RunStatus.FAILED,
                    step_id=step_id,
                    summary=self._summary_with_counters(run_ctx, {"failed_step_id": step_id, "reason": decision.reason}),
                    reason="governance_denied",
                )
                current_status = RunStatus.FAILED
                self._persist_run_output(run_ctx)
                return RunStatus.FAILED.value

            run_ctx.meta["steps_executed"] = int(run_ctx.meta.get("steps_executed", 0)) + 1

            self._emit_event(
                kind="step_started",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"step_index": idx, "type": step_def.type.value, "name": step_record.name},
            )

            if step_def.type == StepType.BRANCH:
                if step_def.when is None:
                    return self._fail_step(
                        run_ctx=run_ctx,
                        step_id=step_id,
                        reason="branch_missing_condition",
                        message="branch condition missing",
                    )
                decision_result = evaluate_condition(step_def.when, run_ctx=run_ctx, memory=self.memory)
                chosen = step_def.then if decision_result else step_def.else_step
                self.memory.update_step(
                    run_ctx.run_id,
                    step_id,
                    {
                        "status": StepStatus.COMPLETED.value,
                        "finished_at": int(time.time()),
                        "output": {
                            "branch": {
                                "result": decision_result,
                                "chosen_next_step": chosen,
                                "when": summarize_condition(step_def.when),
                            }
                        },
                    },
                )
                self._emit_event(
                    kind="branch_evaluated",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={
                        "when": summarize_condition(step_def.when),
                        "result": decision_result,
                        "chosen_next_step": chosen,
                    },
                )
                self._emit_event(
                    kind="step_completed",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={"ok": True},
                )
                if not chosen:
                    return self._fail_step(
                        run_ctx=run_ctx,
                        step_id=step_id,
                        reason="branch_missing_target",
                        message="branch target missing",
                    )
                next_index = self._find_step_index(flow_def, chosen)
                if next_index <= idx:
                    return self._fail_step(
                        run_ctx=run_ctx,
                        step_id=step_id,
                        reason="branch_invalid_target",
                        message="branch target must be a later step",
                    )
                self.memory.update_run_status(
                    run_ctx.run_id,
                    RunStatus.RUNNING.value,
                    summary=self._summary_with_counters(run_ctx, {"current_step_index": next_index}),
                )
                idx = next_index
                continue

            if step_def.type == StepType.REPEAT_UNTIL:
                result = self._handle_repeat_until(
                    flow_def=flow_def,
                    run_ctx=run_ctx,
                    step_def=step_def,
                    step_id=step_id,
                    step_record=step_record,
                    requested_by=requested_by,
                    current_index=idx,
                )
                if isinstance(result, str):
                    return result
                idx = result
                continue

            if step_def.type == StepType.HUMAN_APPROVAL:
                approval_payload = self._build_approval_payload(run_ctx, step_record, step_def)
                approval = self.hitl.create_approval(
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
                    payload={"approval_context": approval_payload.get("approval_context")},
                )
                self.memory.update_step(
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
                current_status = self._transition_run_status(
                    run_id=run_ctx.run_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    current_status=current_status,
                    target_status=RunStatus.PENDING_HUMAN,
                    step_id=step_id,
                    summary=self._summary_with_counters(run_ctx, {"current_step_index": idx}),
                    reason="approval_requested",
                )
                self._emit_event(
                    kind="pending_human",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={
                        "approval_id": approval.approval_id,
                        "approval_context": approval_payload.get("approval_context"),
                    },
                )
                self._emit_event(
                    kind="pending_approval",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={
                        "approval_id": approval.approval_id,
                        "approval_context": approval_payload.get("approval_context"),
                    },
                )
                self._emit_event(
                    kind="run_pending_human",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={"reason": "approval_requested", "approval_id": approval.approval_id},
                )
                return RunStatus.PENDING_HUMAN.value

            if step_def.type == StepType.USER_INPUT:
                context = {"payload": run_ctx.payload, "artifacts": run_ctx.artifacts}
                rendered_params = render_params(step_def.params or {}, context)
                question_set_payload = rendered_params.pop("question_set", None)
                context_pack_key = rendered_params.pop("context_pack_key", None)
                question_set = None
                question_set_key = None
                required = rendered_params.get("required")
                if isinstance(required, list):
                    flattened = []
                    for item in required:
                        if isinstance(item, list):
                            flattened.extend(item)
                        else:
                            flattened.append(item)
                    rendered_params["required"] = flattened
                step_def = step_def.model_copy(update={"params": rendered_params})
                try:
                    if question_set_payload is not None:
                        question_set = QuestionSet.model_validate(question_set_payload)
                        question_set_key = f"question_set.{question_set.id}"
                        run_ctx.artifacts[question_set_key] = question_set.model_dump(mode="json")
                        request = _build_question_set_request(
                            question_set=question_set,
                            question_set_key=question_set_key,
                            context_pack_key=context_pack_key,
                        )
                        self._emit_event(
                            kind="question_set_created",
                            run_id=run_ctx.run_id,
                            step_id=step_id,
                            product=run_ctx.product,
                            flow=run_ctx.flow,
                            payload={
                                "question_set_id": question_set.id,
                                "question_count": len(question_set.questions),
                                "required_fields": question_set.required_fields,
                            },
                        )
                    else:
                        request = UserInputRequest.model_validate(step_def.params or {})
                except Exception as exc:
                    self.memory.update_step(
                        run_ctx.run_id,
                        step_id,
                        {
                            "status": StepStatus.FAILED.value,
                            "finished_at": int(time.time()),
                            "error": {"message": str(exc), "type": type(exc).__name__},
                        },
                    )
                    self._transition_run_status(
                        run_id=run_ctx.run_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        current_status=current_status,
                        target_status=RunStatus.FAILED,
                        step_id=step_id,
                        summary=self._summary_with_counters(run_ctx, {"failed_step_id": step_id}),
                        reason="user_input_invalid_request",
                    )
                    current_status = RunStatus.FAILED
                    self._emit_event(
                        kind="step_failed",
                        run_id=run_ctx.run_id,
                        step_id=step_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        payload={"error": {"message": str(exc), "type": type(exc).__name__}},
                    )
                    self._persist_run_output(run_ctx)
                    return RunStatus.FAILED.value

                constraints = request.constraints if isinstance(request.constraints, dict) else {}
                pause_if = constraints.get("pause_if")
                if pause_if is False:
                    empty_values = {"text": ""}
                    user_input_payload = {
                        "form_id": request.form_id,
                        "values": empty_values,
                        "comment": "",
                        "metadata": {},
                    }
                    self.memory.update_step(
                        run_ctx.run_id,
                        step_id,
                        {
                            "status": StepStatus.COMPLETED.value,
                            "finished_at": int(time.time()),
                            "output": {"user_input": user_input_payload, "skipped": True},
                        },
                    )
                    _store_user_input_artifacts(run_ctx, request.form_id, empty_values, "")
                    self._emit_event(
                        kind="user_input_skipped",
                        run_id=run_ctx.run_id,
                        step_id=step_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        payload={"form_id": request.form_id, "reason": "pause_if_false"},
                    )
                    self._emit_event(
                        kind="step_completed",
                        run_id=run_ctx.run_id,
                        step_id=step_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        payload={"ok": True},
                    )
                    continue

                prompt = _build_user_input_prompt(run_ctx=run_ctx, step_id=step_id, request=request)
                schema_summary = _summarize_schema(request.schema)
                hitl_request = HitlRequest(
                    request_id=request.form_id,
                    request_type="INPUT",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    created_at=int(time.time()),
                    schema=HitlInputSchema(
                        schema=request.schema if isinstance(request.schema, dict) else {},
                        required=request.required,
                        defaults=request.defaults,
                        prompt=prompt.model_dump(mode="json"),
                    ),
                    payload={"title": request.title, "mode": request.mode, "input_type": request.input_type},
                )
                self._emit_event(
                    kind="pending_user_input",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload=prompt.model_dump(mode="json"),
                )
                self._emit_event(
                    kind="user_input_requested",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={
                        "form_id": request.form_id,
                        "title": request.title,
                        "mode": request.mode,
                        "required": request.required,
                        "defaults": request.defaults,
                        "schema_summary": schema_summary,
                        "prompt": prompt.model_dump(mode="json"),
                    },
                )
                self.memory.update_step(
                    run_ctx.run_id,
                    step_id,
                    {
                        "status": StepStatus.PENDING_USER_INPUT.value,
                        "output": {
                            "user_input_request": {"form_id": request.form_id, "prompt": prompt.model_dump(mode="json")},
                            "hitl_request": hitl_request.model_dump(mode="json"),
                            "question_set": question_set.model_dump(mode="json") if question_set_payload is not None else None,
                            "question_set_key": question_set_key if question_set_payload is not None else None,
                        },
                    },
                )
                current_status = self._transition_run_status(
                    run_id=run_ctx.run_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    current_status=current_status,
                    target_status=RunStatus.PAUSED_WAITING_FOR_USER,
                    step_id=step_id,
                    summary=self._summary_with_counters(
                        run_ctx,
                        {
                            "current_step_index": idx,
                            "form_id": request.form_id,
                            "pending_user_input": prompt.model_dump(mode="json"),
                            "question_set_id": question_set.id if question_set_payload is not None else None,
                        },
                    ),
                    reason="user_input_requested",
                )
                self._emit_event(
                    kind="run_paused",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={"reason": "user_input_requested", "form_id": request.form_id},
                )
                self._emit_event(
                    kind="run_paused_for_user_input",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={"question_set_id": request.constraints.get("question_set_id") if isinstance(request.constraints, dict) else None},
                )
                self._persist_run_output(run_ctx)
                return RunStatus.PAUSED_WAITING_FOR_USER.value

            if step_def.type == StepType.PLAN_PROPOSAL:
                if step_def.agent is None:
                    self._transition_run_status(
                        run_id=run_ctx.run_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        current_status=current_status,
                        target_status=RunStatus.FAILED,
                        step_id=step_id,
                        summary=self._summary_with_counters(run_ctx, {"failed_step_id": step_id}),
                        reason="plan_proposal_missing_agent",
                    )
                    current_status = RunStatus.FAILED
                    self._emit_event(
                        kind="step_failed",
                        run_id=run_ctx.run_id,
                        step_id=step_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        payload={"error": {"message": "plan_proposal step missing agent", "type": "ValueError"}},
                    )
                    self._persist_run_output(run_ctx)
                    return RunStatus.FAILED.value

            if step_def.type == StepType.PLAN_PROPOSE:
                handled = self._handle_plan_propose(
                    run_ctx=run_ctx,
                    step_def=step_def,
                    step_id=step_id,
                    step_record=step_record,
                    requested_by=requested_by,
                )
                if handled == "continue":
                    idx += 1
                    continue
                if handled is not None:
                    return handled

            if step_def.type == StepType.PLAN_GATE:
                handled = self._handle_plan_gate(
                    run_ctx=run_ctx,
                    step_def=step_def,
                    step_id=step_id,
                    step_record=step_record,
                )
                if handled == "continue":
                    idx += 1
                    continue
                if handled is not None:
                    return handled

            if step_def.type == StepType.PLAN_EXECUTE:
                handled = self._handle_plan_execute(
                    run_ctx=run_ctx,
                    step_def=step_def,
                    step_id=step_id,
                    step_record=step_record,
                    requested_by=requested_by,
                )
                if handled == "continue":
                    idx += 1
                    continue
                if handled is not None:
                    return handled

            try:
                result = self.step_executor.execute(run_ctx=run_ctx, step_def=step_def, step_id=step_id)
                result = self._persist_output_files(run_ctx, result)
                if isinstance(result, dict):
                    data = result.get("data")
                    if isinstance(data, dict) and data:
                        last_result_data = data
                if step_def.type == StepType.PLAN_PROPOSAL:
                    approval_payload = self._build_plan_proposal_payload(
                        run_ctx=run_ctx,
                        step_record=step_record,
                        step_def=step_def,
                        plan_result=result if isinstance(result, dict) else {},
                    )
                    approval = self.hitl.create_approval(
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
                        payload={"approval_context": approval_payload.get("approval_context")},
                    )
                    self.memory.update_step(
                        run_ctx.run_id,
                        step_id,
                        {
                            "status": StepStatus.PENDING_HUMAN.value,
                            "output": {
                                "approval_id": approval.approval_id,
                                "plan_proposal": result,
                                "hitl_request": hitl_request.model_dump(mode="json"),
                            },
                        },
                    )
                    current_status = self._transition_run_status(
                        run_id=run_ctx.run_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        current_status=current_status,
                        target_status=RunStatus.PENDING_HUMAN,
                        step_id=step_id,
                        summary=self._summary_with_counters(run_ctx, {"current_step_index": idx}),
                        reason="plan_proposal_requested",
                    )
                    self._emit_event(
                        kind="pending_human",
                        run_id=run_ctx.run_id,
                        step_id=step_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        payload={
                            "approval_id": approval.approval_id,
                            "approval_context": approval_payload.get("approval_context"),
                        },
                    )
                    self._emit_event(
                        kind="pending_approval",
                        run_id=run_ctx.run_id,
                        step_id=step_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        payload={
                            "approval_id": approval.approval_id,
                            "approval_context": approval_payload.get("approval_context"),
                        },
                    )
                    self._emit_event(
                        kind="run_pending_human",
                        run_id=run_ctx.run_id,
                        step_id=step_id,
                        product=run_ctx.product,
                        flow=run_ctx.flow,
                        payload={"reason": "plan_proposal_requested", "approval_id": approval.approval_id},
                    )
                    self._persist_run_output(run_ctx)
                    return RunStatus.PENDING_HUMAN.value
                self.memory.update_step(
                    run_ctx.run_id,
                    step_id,
                    {"status": StepStatus.COMPLETED.value, "finished_at": int(time.time()), "output": result},
                )
                self._emit_event(
                    kind="step_completed",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={"ok": True},
                )
            except Exception as exc:
                self.memory.update_step(
                    run_ctx.run_id,
                    step_id,
                    {
                        "status": StepStatus.FAILED.value,
                        "finished_at": int(time.time()),
                        "error": {"message": str(exc), "type": type(exc).__name__},
                    },
                )
                self._transition_run_status(
                    run_id=run_ctx.run_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    current_status=current_status,
                    target_status=RunStatus.FAILED,
                    step_id=step_id,
                    summary=self._summary_with_counters(run_ctx, {"failed_step_id": step_id}),
                    reason="step_failed",
                )
                current_status = RunStatus.FAILED
                self._emit_event(
                    kind="step_failed",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={"error": {"message": str(exc), "type": type(exc).__name__}},
                )
                self._persist_run_output(run_ctx)
                return RunStatus.FAILED.value

            next_index = idx + 1
            if step_id in {"plan", "planning"}:
                next_index = self._resolve_plan_next_index(flow_def, idx, result)
            self.memory.update_run_status(
                run_ctx.run_id,
                RunStatus.RUNNING.value,
                summary=self._summary_with_counters(run_ctx, {"current_step_index": next_index}),
            )
            idx = next_index

        if last_result_data is None:
            fallback_output = run_ctx.meta.get("last_result_data")
            if isinstance(fallback_output, dict):
                last_result_data = fallback_output
        if last_result_data is None:
            self._transition_run_status(
                run_id=run_ctx.run_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                current_status=current_status,
                target_status=RunStatus.FAILED,
                step_id="output",
                summary=self._summary_with_counters(run_ctx, {"failed_step_id": "output", "reason": "missing_run_output"}),
                reason="missing_run_output",
            )
            self._emit_event(
                kind="run_failed",
                run_id=run_ctx.run_id,
                step_id=None,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"error": {"message": "Missing run output", "type": "RuntimeError"}},
            )
            self._persist_run_output(run_ctx)
            return RunStatus.FAILED.value

        normalized_output = self._normalize_run_output(last_result_data)
        decision = self.governance.before_run_output(output=normalized_output, run_ctx=run_ctx)
        if not decision.allowed:
            self._transition_run_status(
                run_id=run_ctx.run_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                current_status=current_status,
                target_status=RunStatus.FAILED,
                step_id="output",
                summary=self._summary_with_counters(run_ctx, {"failed_step_id": "output", "reason": decision.reason}),
                reason="output_denied",
            )
            self._emit_event(
                kind="output_denied",
                run_id=run_ctx.run_id,
                step_id=None,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"reason": decision.reason, "details": decision.details},
            )
            self._persist_run_output(run_ctx)
            return RunStatus.FAILED.value
        self.memory.update_run_output(run_ctx.run_id, output=normalized_output)
        self._transition_run_status(
            run_id=run_ctx.run_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            current_status=current_status,
            target_status=RunStatus.COMPLETED,
            step_id=None,
            summary=self._summary_with_counters(run_ctx, {"current_step_index": len(flow_def.steps)}),
            reason="run_completed",
        )
        self._emit_event(
            kind="run_completed",
            run_id=run_ctx.run_id,
            step_id=None,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"ok": True},
        )
        self._export_reasoning_artifact(run_ctx)
        self._persist_run_output(run_ctx)
        return RunStatus.COMPLETED.value

    def _export_reasoning_artifact(self, run_ctx: RunContext) -> None:
        paths = self.memory.get_observability_dirs(product=run_ctx.product, run_id=run_ctx.run_id)
        if not paths:
            return
        runtime_dir = paths.get("runtime")
        if runtime_dir is None:
            return
        events_path = runtime_dir / "events.jsonl"
        content = build_reasoning_markdown(events_path)
        if not content:
            return
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        self.memory.write_output_files(
            product=run_ctx.product,
            run_id=run_ctx.run_id,
            files=[
                {
                    "name": "reasoning.md",
                    "content_type": "text/markdown",
                    "role": "supporting",
                    "content_base64": encoded,
                }
            ],
        )

    def _normalize_run_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data = {k: v for k, v in data.items() if k != "output_files"}
        summary = data.get("summary")
        details = data.get("details")
        if isinstance(summary, str) and isinstance(details, dict):
            output = dict(details)
            output["summary"] = summary
            return output
        return data

    def _persist_output_files(self, run_ctx: RunContext, result: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(result, dict):
            return result
        data = result.get("data")
        if not isinstance(data, dict):
            return result
        files = data.get("output_files")
        if not isinstance(files, list) or not files:
            return result
        decision = self.governance.before_output_files(files=files, run_ctx=run_ctx)
        if not decision.allowed:
            self._emit_event(
                kind="output_files_denied",
                run_id=run_ctx.run_id,
                step_id=None,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"reason": decision.reason, "details": decision.details},
            )
            raise RuntimeError(decision.reason or "output_files_denied")
        stored = self.memory.write_output_files(product=run_ctx.product, run_id=run_ctx.run_id, files=files) or []
        updated = dict(result)
        updated_data = dict(data)
        updated_data["output_files"] = stored
        updated["data"] = updated_data
        return updated

    def _handle_plan_propose(
        self,
        *,
        run_ctx: RunContext,
        step_def: StepDef,
        step_id: str,
        step_record: StepRecord,
        requested_by: Optional[str],
    ) -> Optional[str]:
        return handle_plan_propose(
            run_ctx=run_ctx,
            step_def=step_def,
            step_id=step_id,
            step_record=step_record,
            requested_by=requested_by,
            memory=self.memory,
            governance=self.governance,
            fail_step_fn=self._fail_step,
            emit_event_fn=self._emit_event,
        )

    def _handle_plan_gate(
        self,
        *,
        run_ctx: RunContext,
        step_def: StepDef,
        step_id: str,
        step_record: StepRecord,
    ) -> Optional[str]:
        return handle_plan_gate(
            run_ctx=run_ctx,
            step_def=step_def,
            step_id=step_id,
            step_record=step_record,
            memory=self.memory,
            fail_step_fn=self._fail_step,
            emit_event_fn=self._emit_event,
        )

    def _handle_plan_execute(
        self,
        *,
        run_ctx: RunContext,
        step_def: StepDef,
        step_id: str,
        step_record: StepRecord,
        requested_by: Optional[str],
    ) -> Optional[str]:
        return handle_plan_execute(
            run_ctx=run_ctx,
            step_def=step_def,
            step_id=step_id,
            step_record=step_record,
            requested_by=requested_by,
            memory=self.memory,
            hitl=self.hitl,
            governance=self.governance,
            step_executor=self.step_executor,
            fail_step_fn=self._fail_step,
            emit_event_fn=self._emit_event,
            transition_run_status_fn=self._transition_run_status,
            summary_with_counters_fn=self._summary_with_counters,
            persist_run_output_fn=self._persist_run_output,
        )

    def _handle_repeat_until(
        self,
        *,
        flow_def: FlowDef,
        run_ctx: RunContext,
        step_def: StepDef,
        step_id: str,
        step_record: StepRecord,
        requested_by: Optional[str],
        current_index: int,
    ) -> Union[str, int]:
        return handle_repeat_until(
            flow_def=flow_def,
            run_ctx=run_ctx,
            step_def=step_def,
            step_id=step_id,
            step_record=step_record,
            requested_by=requested_by,
            current_index=current_index,
            memory=self.memory,
            hitl=self.hitl,
            fail_step_fn=self._fail_step,
            emit_event_fn=self._emit_event,
            transition_run_status_fn=self._transition_run_status,
            summary_with_counters_fn=self._summary_with_counters,
            persist_run_output_fn=self._persist_run_output,
            find_step_def_fn=self._find_step_def,
            find_step_index_fn=self._find_step_index,
            execute_iteration_step_fn=self._execute_iteration_step,
        )

    def _execute_iteration_step(
        self,
        *,
        flow_def: FlowDef,
        run_ctx: RunContext,
        step_def: StepDef,
        step_index: int,
        requested_by: Optional[str],
    ) -> Optional[str]:
        step_id = step_def.id or f"loop_step_{step_index}"
        step_record = StepRecord(
            run_id=run_ctx.run_id,
            step_id=step_id,
            step_index=step_index,
            name=step_def.name or step_id,
            type=step_def.type.value,
            status=StepStatus.RUNNING,
            started_at=int(time.time()),
            input={"params": step_def.params or {}},
            meta={"backend": step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend},
        )
        self.memory.add_step(step_record)

        step_ctx = run_ctx.new_step(
            step_def=step_def,
            step_id=step_id,
            step_type=step_def.type.value,
            backend=step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend,
            target=step_def.agent or step_def.tool,
        )

        decision = self.governance.before_step(step_ctx=step_ctx)
        if not decision.allowed:
            self._emit_event(
                kind="before_step_denied",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"reason": decision.reason},
            )
            self.memory.update_step(
                run_ctx.run_id,
                step_id,
                {
                    "status": StepStatus.FAILED.value,
                    "finished_at": int(time.time()),
                    "error": {"message": decision.reason, "type": "PermissionError"},
                },
            )
            self._transition_run_status(
                run_id=run_ctx.run_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                current_status=RunStatus.RUNNING,
                target_status=RunStatus.FAILED,
                step_id=step_id,
                summary=self._summary_with_counters(run_ctx, {"failed_step_id": step_id, "reason": decision.reason}),
                reason="governance_denied",
            )
            self._persist_run_output(run_ctx)
            return RunStatus.FAILED.value

        run_ctx.meta["steps_executed"] = int(run_ctx.meta.get("steps_executed", 0)) + 1
        self._emit_event(
            kind="step_started",
            run_id=run_ctx.run_id,
            step_id=step_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"step_index": step_index, "type": step_def.type.value, "name": step_record.name},
        )

        if step_def.type in {StepType.HUMAN_APPROVAL, StepType.USER_INPUT, StepType.BRANCH, StepType.REPEAT_UNTIL, StepType.SUBFLOW}:
            return self._fail_step(
                run_ctx=run_ctx,
                step_id=step_id,
                reason="repeat_until_invalid_step",
                message="repeat_until iteration_step type not supported",
            )

        if step_def.type == StepType.PLAN_PROPOSE:
            handled = self._handle_plan_propose(
                run_ctx=run_ctx,
                step_def=step_def,
                step_id=step_id,
                step_record=step_record,
                requested_by=requested_by,
            )
            if handled == "continue":
                return None
            return handled

        if step_def.type == StepType.PLAN_GATE:
            handled = self._handle_plan_gate(
                run_ctx=run_ctx,
                step_def=step_def,
                step_id=step_id,
                step_record=step_record,
            )
            if handled == "continue":
                return None
            return handled

        if step_def.type == StepType.PLAN_EXECUTE:
            handled = self._handle_plan_execute(
                run_ctx=run_ctx,
                step_def=step_def,
                step_id=step_id,
                step_record=step_record,
                requested_by=requested_by,
            )
            if handled == "continue":
                return None
            return handled

        try:
            result = self.step_executor.execute(run_ctx=run_ctx, step_def=step_def, step_id=step_id)
            result = self._persist_output_files(run_ctx, result)
            if isinstance(result, dict):
                data = result.get("data")
                if isinstance(data, dict) and data:
                    run_ctx.meta["last_result_data"] = data
            self.memory.update_step(
                run_ctx.run_id,
                step_id,
                {"status": StepStatus.COMPLETED.value, "finished_at": int(time.time()), "output": result},
            )
            self._emit_event(
                kind="step_completed",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"ok": True},
            )
            return None
        except Exception as exc:
            self.memory.update_step(
                run_ctx.run_id,
                step_id,
                {
                    "status": StepStatus.FAILED.value,
                    "finished_at": int(time.time()),
                    "error": {"message": str(exc), "type": type(exc).__name__},
                },
            )
            self._transition_run_status(
                run_id=run_ctx.run_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                current_status=RunStatus.RUNNING,
                target_status=RunStatus.FAILED,
                step_id=step_id,
                summary=self._summary_with_counters(run_ctx, {"failed_step_id": step_id}),
                reason="step_failed",
            )
            self._emit_event(
                kind="step_failed",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"error": {"message": str(exc), "type": type(exc).__name__}},
            )
            self._persist_run_output(run_ctx)
            return RunStatus.FAILED.value

    def _find_step_def(self, flow_def: FlowDef, step_id: str) -> Optional[StepDef]:
        for definition in flow_def.steps:
            if (definition.id or "") == step_id:
                return definition
        return None

    def _execute_action_plan(self, run_ctx: RunContext, gate_obj: PlanGateResult) -> Optional[str]:
        return execute_action_plan(
            run_ctx=run_ctx,
            gate_obj=gate_obj,
            step_executor=self.step_executor,
            governance=self.governance,
            fail_step_fn=self._fail_step,
            emit_event_fn=self._emit_event,
        )

    def _store_artifact(self, run_ctx: RunContext, key: str, payload: Dict[str, Any]) -> ArtifactRef:
        full_key = key
        uri = f"memory://{full_key}"
        ref = ArtifactRef(key=full_key, kind="json", uri=uri)
        run_ctx.artifacts[full_key] = payload
        return ref

    def _get_artifact_payload(self, run_ctx: RunContext, key: str) -> Optional[Dict[str, Any]]:
        value = run_ctx.artifacts.get(key)
        if isinstance(value, dict):
            return value
        return None

    def _fail_step(self, *, run_ctx: RunContext, step_id: str, reason: str, message: str) -> str:
        self.memory.update_step(
            run_ctx.run_id,
            step_id,
            {"status": StepStatus.FAILED.value, "finished_at": int(time.time()), "error": {"message": message}},
        )
        self._transition_run_status(
            run_id=run_ctx.run_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            current_status=RunStatus.RUNNING,
            target_status=RunStatus.FAILED,
            step_id=step_id,
            summary=self._summary_with_counters(run_ctx, {"failed_step_id": step_id, "reason": reason}),
            reason=reason,
        )
        self._emit_event(
            kind="step_failed",
            run_id=run_ctx.run_id,
            step_id=step_id,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"error": {"message": message, "type": "ValueError"}},
        )
        self._persist_run_output(run_ctx)
        return RunStatus.FAILED.value

    def _find_step_index(self, flow_def: FlowDef, step_id: str) -> int:
        for idx, definition in enumerate(flow_def.steps):
            if (definition.id or f"step_{idx}") == step_id:
                return idx
        raise ValueError(f"Cannot map approval step '{step_id}' to flow definition.")

    def _resolve_plan_next_index(self, flow_def: FlowDef, current_index: int, result: Dict[str, Any]) -> int:
        data = result.get("data") if isinstance(result, dict) else None
        start_index = None
        if isinstance(data, dict):
            candidate_index = data.get("start_index")
            if isinstance(candidate_index, int):
                start_index = candidate_index
            else:
                for key in ("start_step_id", "start_from", "start_step", "start_at"):
                    step_id = data.get(key)
                    if step_id:
                        try:
                            start_index = self._find_step_index(flow_def, step_id)
                        except ValueError:
                            start_index = None
                        break
        if start_index is None:
            return current_index + 1
        if start_index <= current_index:
            return current_index + 1
        if start_index > len(flow_def.steps):
            return len(flow_def.steps)
        return start_index

    # ------------------------------------------------------------------ Semantic Interpretation Phase
    def _run_semantic_interpretation(
        self,
        *,
        run_ctx: RunContext,
        flow_def: FlowDef,
    ) -> tuple[bool, Optional[SemanticEnvelope], Optional[str]]:
        """
        Execute semantic interpretation phase before step execution.
        
        ORC-SEM-001: Semantic phase runs before planning/execution
        ORC-SEM-003: Produces SemanticEnvelope result
        
        Returns:
            (should_continue, envelope, error_code)
            - should_continue: True if execution should proceed to steps
            - envelope: The semantic envelope if produced
            - error_code: Error code if failed
        """
        # Check for skip flag in payload or flow metadata
        skip_semantic = (
            run_ctx.payload.get("skip_semantic_interpretation", False)
            or (flow_def.metadata or {}).get("skip_semantic_interpretation", False)
        )
        
        if skip_semantic:
            self._emit_event(
                kind="semantic_interpretation_skipped",
                run_id=run_ctx.run_id,
                step_id=None,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"reason": "skip_semantic_interpretation flag set"},
            )
            return (True, None, None)
        
        start_time = time.time()
        self._emit_event(
            kind="semantic_interpretation_started",
            run_id=run_ctx.run_id,
            step_id=None,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"raw_input": str(run_ctx.payload.get("user_input", ""))[:200]},
        )
        
        try:
            # Build semantic envelope from payload
            # TODO: Replace with product-specific semantic adapter (GAP-006)
            user_input = run_ctx.payload.get("user_input", "")
            if not isinstance(user_input, str):
                user_input = str(user_input) if user_input else ""
            
            envelope = SemanticEnvelope(
                raw_input=user_input,
                normalized_input=user_input.strip().lower() if user_input else "",
                product_id=run_ctx.product,
                intent_type=run_ctx.payload.get("intent_type", "unknown"),
                confidence=run_ctx.payload.get("confidence", 1.0),
                proposed_next_action=NextAction.CONTINUE,
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            self._emit_event(
                kind="semantic_interpretation_completed",
                run_id=run_ctx.run_id,
                step_id=None,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={
                    "duration_ms": duration_ms,
                    "confidence": envelope.confidence,
                    "next_action": envelope.proposed_next_action.value,
                },
            )
            
            # Handle NextAction outcomes (ORC-SEM-STOP-001...007)
            if envelope.proposed_next_action == NextAction.ABORT:
                # ORC-SEM-STOP-004: Transition to FAILED with code semantic_abort
                self._emit_event(
                    kind="semantic_stop_issued",
                    run_id=run_ctx.run_id,
                    step_id=None,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={
                        "next_action": "ABORT",
                        "ambiguities": envelope.ambiguities,
                    },
                )
                return (False, envelope, "semantic_abort")
            
            if envelope.proposed_next_action == NextAction.ASK_USER:
                # ORC-SEM-STOP-001/002: Pause for user clarification
                self._emit_event(
                    kind="semantic_stop_issued",
                    run_id=run_ctx.run_id,
                    step_id=None,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={
                        "next_action": "ASK_USER",
                        "ambiguities": envelope.ambiguities,
                    },
                )
                return (False, envelope, "semantic_ask_user")
            
            if envelope.proposed_next_action == NextAction.NEEDS_APPROVAL:
                # ORC-SEM-STOP-006: Pause for HITL approval
                self._emit_event(
                    kind="semantic_stop_issued",
                    run_id=run_ctx.run_id,
                    step_id=None,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={
                        "next_action": "NEEDS_APPROVAL",
                    },
                )
                return (False, envelope, "semantic_needs_approval")
            
            # ORC-SEM-STOP-007: CONTINUE permits step execution
            return (True, envelope, None)
            
        except Exception as exc:
            # ORC-SEM-004: Semantic phase failure → FAILED with semantic_interpretation_failed
            self._emit_event(
                kind="semantic_interpretation_failed",
                run_id=run_ctx.run_id,
                step_id=None,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"error": str(exc), "type": type(exc).__name__},
            )
            return (False, None, "semantic_interpretation_failed")

    def _emit_event(
        self,
        *,
        kind: str,
        run_id: str,
        step_id: Optional[str],
        product: str,
        flow: str,
        payload: Dict[str, Any],
    ) -> None:
        evt = TraceEvent(
            kind=kind,
            run_id=run_id,
            step_id=step_id,
            product=product,
            flow=flow,
            ts=int(time.time()),
            payload=payload,
        )
        self.tracer.emit(evt)

    def _reject_run(
        self,
        *,
        run_id: str,
        product: str,
        flow: str,
        autonomy_level: Optional[str] = None,
        payload: Dict[str, Any],
        code: str,
        message: str,
        details: Dict[str, Any],
    ) -> RunOperationResult:
        now = int(time.time())
        run_record = RunRecord(
            run_id=run_id,
            product=product,
            flow=flow,
            status=RunStatus.FAILED,
            autonomy_level=autonomy_level or "unknown",
            started_at=now,
            finished_at=now,
            input=payload,
            summary={"error": {"code": code, "message": message, "details": details}},
        )
        self.memory.create_run(run_record)
        run_ctx = RunContext(run_id=run_id, product=product, flow=flow, payload=payload)
        self._attach_run_dirs(run_ctx)
        self._stage_inputs(run_ctx)
        self._emit_event(
            kind="run_rejected",
            run_id=run_id,
            step_id=None,
            product=product,
            flow=flow,
            payload={"code": code, "message": message, "details": details},
        )
        self._persist_run_output(run_ctx)
        error_details = dict(details)
        error_details["run_id"] = run_id
        return RunOperationResult.failure(code=code, message=message, details=error_details)

    def _persist_run_output(self, run_ctx: RunContext) -> None:
        """Delegate to run_lifecycle module."""
        persist_run_output(
            memory=self.memory,
            emit_event_fn=self._emit_event,
            run_id=run_ctx.run_id,
        )

    def _rehydrate_artifacts(self, steps: List[StepRecord], run_ctx: RunContext) -> None:
        for step in steps:
            output = step.output or {}
            if not isinstance(output, dict):
                continue
            plan_payload = output.get("plan")
            if isinstance(plan_payload, dict):
                run_ctx.artifacts["plan.action_plan"] = plan_payload
            plan_gate_payload = output.get("plan_gate")
            if isinstance(plan_gate_payload, dict):
                run_ctx.artifacts["plan.gate_result"] = plan_gate_payload
            question_set_payload = output.get("question_set")
            if isinstance(question_set_payload, dict):
                question_set_key = output.get("question_set_key") or f"question_set.{question_set_payload.get('id', 'unknown')}"
                if isinstance(question_set_key, str):
                    run_ctx.artifacts[question_set_key] = question_set_payload
            context_pack_payload = output.get("context_pack")
            if isinstance(context_pack_payload, dict):
                context_pack_key = output.get("context_pack_key") or "context_pack"
                if isinstance(context_pack_key, str):
                    run_ctx.artifacts[context_pack_key] = context_pack_payload
            meta = output.get("meta")
            data = output.get("data")
            if not isinstance(meta, dict) or data is None:
                user_input = output.get("user_input")
                if isinstance(user_input, dict):
                    form_id = user_input.get("form_id")
                    values = user_input.get("values")
                    comment = user_input.get("comment")
                    if isinstance(form_id, str) and isinstance(values, dict):
                        _store_user_input_artifacts(run_ctx, form_id, values, comment)
                continue
            tool_name = meta.get("tool_name")
            agent_name = meta.get("agent_name")
            if tool_name:
                run_ctx.artifacts[f"tool.{tool_name}.output"] = data
                run_ctx.artifacts[f"tool.{tool_name}.meta"] = meta
            if agent_name:
                run_ctx.artifacts[f"agent.{agent_name}.output"] = data
                run_ctx.artifacts[f"agent.{agent_name}.meta"] = meta

    def _init_run_meta(
        self,
        run_ctx: RunContext,
        *,
        summary: Optional[Dict[str, Any]] = None,
        steps: Optional[List[StepRecord]] = None,
    ) -> None:
        """Delegate to run_lifecycle module."""
        init_run_meta(run_ctx, summary=summary, steps=steps)

    @staticmethod
    def _summary_with_counters(run_ctx: RunContext, summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delegate to run_lifecycle module."""
        return summary_with_counters(run_ctx, summary)

    def _stage_inputs(self, run_ctx: RunContext) -> None:
        self.memory.ensure_run_dirs(product=run_ctx.product, run_id=run_ctx.run_id)
        payload = run_ctx.payload or {}
        self.memory.capture_run_input(product=run_ctx.product, run_id=run_ctx.run_id, payload=payload)
        self.memory.move_staged_inputs_to_run(product=run_ctx.product, run_id=run_ctx.run_id)

    def _attach_run_dirs(self, run_ctx: RunContext) -> None:
        paths = self.memory.get_observability_dirs(product=run_ctx.product, run_id=run_ctx.run_id)
        if not paths:
            return
        input_dir = paths.get("input")
        output_dir = paths.get("output")
        if input_dir:
            run_ctx.meta["input_dir"] = str(input_dir)
        if output_dir:
            run_ctx.meta["output_dir"] = str(output_dir)

    def _build_approval_payload(self, run_ctx: RunContext, step_record: StepRecord, step_def: StepDef) -> Dict[str, Any]:
        intent = (
            run_ctx.payload.get("prompt")
            or run_ctx.payload.get("intent")
            or run_ctx.payload.get("instructions")
            or run_ctx.payload.get("notes")
            or ""
        )
        params = step_def.params or {}
        approval_context = params.get("approval_context") if isinstance(params, dict) else None
        return {
            "step": step_record.model_dump(),
            "intent": intent,
            "approval_context": approval_context,
            "artifacts": {"keys": sorted(run_ctx.artifacts.keys())},
        }

    def _build_plan_proposal_payload(
        self,
        *,
        run_ctx: RunContext,
        step_record: StepRecord,
        step_def: StepDef,
        plan_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        intent = (
            run_ctx.payload.get("prompt")
            or run_ctx.payload.get("intent")
            or run_ctx.payload.get("instructions")
            or run_ctx.payload.get("notes")
            or ""
        )
        params = step_def.params or {}
        approval_context = params.get("approval_context") if isinstance(params, dict) else None
        plan_payload = plan_result.get("data") if isinstance(plan_result, dict) else None
        return {
            "step": step_record.model_dump(),
            "intent": intent,
            "approval_context": approval_context,
            "plan": plan_payload or {},
            "artifacts": {"keys": sorted(run_ctx.artifacts.keys())},
        }

# Backwards compatibility for older imports/tests
Engine = OrchestratorEngine


# ============================================================================
# Helper function wrappers - delegate to user_input_handler module
# ============================================================================


def _summarize_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Delegate to user_input_handler module."""
    return summarize_schema(schema)


def _looks_like_user_input_answer(payload: Dict[str, Any]) -> bool:
    """Delegate to user_input_handler module."""
    return looks_like_user_input_answer(payload)


def _looks_like_question_set_answers(payload: Dict[str, Any]) -> bool:
    """Delegate to user_input_handler module."""
    return looks_like_question_set_answers(payload)


def _build_user_input_prompt(run_ctx: RunContext, step_id: str, request: UserInputRequest) -> UserInputPrompt:
    """Delegate to user_input_handler module."""
    return build_user_input_prompt(run_ctx, step_id, request)


def _answer_to_response(
    request: UserInputRequest,
    answer: UserInputAnswer,
    *,
    comment: Optional[str],
) -> UserInputResponse:
    """Delegate to user_input_handler module."""
    return answer_to_response(request, answer, comment=comment)


def _validate_user_input_values(request: UserInputRequest, values: Dict[str, Any]) -> List[str]:
    """Delegate to user_input_handler module."""
    return validate_user_input_values(request, values)


def _store_user_input_artifacts(run_ctx: RunContext, form_id: str, values: Dict[str, Any], comment: Optional[str]) -> None:
    """Delegate to user_input_handler module."""
    store_user_input_artifacts(run_ctx, form_id, values, comment)


def _build_question_set_request(
    *,
    question_set: QuestionSet,
    question_set_key: str,
    context_pack_key: Optional[str],
) -> UserInputRequest:
    """Delegate to user_input_handler module."""
    return build_question_set_request(
        question_set=question_set,
        question_set_key=question_set_key,
        context_pack_key=context_pack_key,
    )


def _resolve_question_set_from_request(request: UserInputRequest, run_ctx: RunContext) -> Optional[QuestionSet]:
    """Delegate to user_input_handler module."""
    return resolve_question_set_from_request(request, run_ctx)


def _question_set_key_from_request(request: UserInputRequest) -> Optional[str]:
    """Delegate to user_input_handler module."""
    return question_set_key_from_request(request)


def _context_pack_key_from_request(request: UserInputRequest) -> Optional[str]:
    """Delegate to user_input_handler module."""
    return context_pack_key_from_request(request)


def _validate_question_set_answers(question_set: QuestionSet, answers: UserAnswers) -> List[str]:
    """Delegate to user_input_handler module."""
    return validate_question_set_answers(question_set, answers)


def _merge_context_pack_if_present(
    *,
    run_ctx: RunContext,
    question_set: QuestionSet,
    answers: UserAnswers,
    context_pack_key: Optional[str],
) -> Optional[ContextPack]:
    """Delegate to user_input_handler module."""
    return merge_into_context_pack(
        run_ctx=run_ctx,
        question_set=question_set,
        answers=answers,
        context_pack_key=context_pack_key,
    )


def _is_step_status(value: Any, status: StepStatus) -> bool:
    if isinstance(value, StepStatus):
        return value == status
    if isinstance(value, str):
        return value == status.value
    return False


def _coerce_run_status(value: Union[RunStatus, str]) -> RunStatus:
    if isinstance(value, RunStatus):
        return value
    try:
        return RunStatus(value)
    except Exception:
        return RunStatus.RUNNING
