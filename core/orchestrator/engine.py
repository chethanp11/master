from __future__ import annotations

# ==============================
# Orchestrator Engine
# ==============================

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, List, Union
from uuid import uuid4

from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.flow_schema import FlowDef, StepDef, StepType
from core.contracts.run_schema import (
    RunOperationResult,
    RunRecord,
    RunStatus,
    StepRecord,
    StepStatus,
    TraceEvent,
)
from core.contracts.user_input_schema import (
    UserInputAnswer,
    UserInputModes,
    UserInputOption,
    UserInputPrompt,
    UserInputRequest,
    UserInputResponse,
)
from core.governance.hooks import GovernanceHooks
from core.governance.security import SecurityRedactor
from core.memory.tracing import Tracer
from core.memory.router import MemoryRouter
from core.orchestrator.context import RunContext
from core.orchestrator.flow_loader import FlowLoader
from core.orchestrator.hitl import HitlService
from core.orchestrator.state import is_valid_run_transition, to_run_state
from core.orchestrator.step_executor import StepExecutor
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry


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

            payload_limit = self.governance.settings.policies.max_payload_bytes
            if payload_limit is not None:
                size_bytes = _payload_size_bytes(payload)
                if size_bytes > payload_limit:
                    return self._reject_run(
                        run_id=run_id,
                        product=product,
                        flow=flow,
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
                },
            )
            self.memory.create_run(run_record)
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
            request = UserInputRequest.model_validate(step_def.params or {})
            run_ctx = RunContext(run_id=run_id, product=bundle.run.product, flow=bundle.run.flow, payload=bundle.run.input or {})
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
                    }
                },
            },
        )

        if step_status == StepStatus.FAILED:
            if comment:
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
        try:
            if _looks_like_user_input_answer(response_payload):
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

        try:
            request = UserInputRequest.model_validate(step_def.params or {})
        except Exception as exc:
            return RunOperationResult.failure(code="invalid_state", message=str(exc))

        if response is None and answer is not None:
            if answer.prompt_id != request.form_id:
                return RunOperationResult.failure(code="invalid_input", message="prompt_id does not match pending request.")
            response = _answer_to_response(request, answer, comment=comment)

        if response is None:
            return RunOperationResult.failure(code="invalid_input", message="Missing user input response.")

        if response.form_id != request.form_id:
            return RunOperationResult.failure(code="invalid_input", message="form_id does not match pending request.")
        if response.metadata and "metadata" not in response.values:
            response.values["metadata"] = response.metadata

        run_ctx = RunContext(run_id=bundle.run.run_id, product=bundle.run.product, flow=bundle.run.flow, payload=bundle.run.input or {})
        self._init_run_meta(run_ctx, summary=bundle.run.summary, steps=bundle.steps)
        run_ctx.trace = self._trace_hook(run_ctx)

        step_ctx = run_ctx.new_step(
            step_def=step_def,
            step_id=step_id,
            step_type=step_def.type.value,
            backend=step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend,
            target=step_def.agent or step_def.tool,
        )
        decision = self.governance.before_user_input_response(
            request=request.model_dump(mode="json"),
            response=response.model_dump(mode="json"),
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

        errors = _validate_user_input_values(request, response.values)
        if errors:
            self._emit_event(
                kind="user_input_validation_failed",
                run_id=bundle.run.run_id,
                step_id=step_id,
                product=bundle.run.product,
                flow=bundle.run.flow,
                payload={"form_id": request.form_id, "errors": errors},
            )
            return RunOperationResult.failure(code="invalid_input", message="User input validation failed.", details={"errors": errors})

        self.memory.update_step(
            bundle.run.run_id,
            step_id,
            {
                "status": StepStatus.COMPLETED.value,
                "finished_at": int(time.time()),
                "output": {"user_input": response.model_dump(mode="json")},
            },
        )

        self.memory.write_user_input_response(
            product=bundle.run.product,
            run_id=bundle.run.run_id,
            form_id=request.form_id,
            payload=response.model_dump(mode="json"),
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
                "values": response.values,
                "comment": response.comment or comment or "",
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
        _store_user_input_artifacts(run_ctx, request.form_id, response.values, response.comment)

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
        current = _coerce_run_status(current_status)
        target = _coerce_run_status(target_status)
        if not is_valid_run_transition(current, target):
            raise ValueError(f"Invalid run transition: {to_run_state(current).value} -> {to_run_state(target).value}")
        if current != target:
            self._emit_event(
                kind="run_state_transition",
                run_id=run_id,
                step_id=step_id,
                product=product,
                flow=flow,
                payload={
                    "from": to_run_state(current).value,
                    "to": to_run_state(target).value,
                    "reason": reason or "",
                },
            )
        self.memory.update_run_status(run_id, target.value, summary=summary)
        return target

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
                self.memory.update_step(
                    run_ctx.run_id,
                    step_id,
                    {
                        "status": StepStatus.PENDING_HUMAN.value,
                        "output": {"approval_id": approval.approval_id},
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
                return RunStatus.PENDING_HUMAN.value

            if step_def.type == StepType.USER_INPUT:
                try:
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

                prompt = _build_user_input_prompt(run_ctx=run_ctx, step_id=step_id, request=request)
                schema_summary = _summarize_schema(request.schema)
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
                        "output": {"user_input_request": {"form_id": request.form_id, "prompt": prompt.model_dump(mode="json")}},
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
                        {"current_step_index": idx, "form_id": request.form_id, "pending_user_input": prompt.model_dump(mode="json")},
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

            try:
                result = self.step_executor.execute(run_ctx=run_ctx, step_def=step_def, step_id=step_id)
                result = self._persist_output_files(run_ctx, result)
                if isinstance(result, dict):
                    data = result.get("data")
                    if isinstance(data, dict) and data:
                        last_result_data = data
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
        self._persist_run_output(run_ctx)
        return RunStatus.COMPLETED.value

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
            autonomy_level=None,
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
        bundle = self.memory.get_run(run_ctx.run_id)
        if bundle is None:
            return
        run = bundle.run
        status = run.status.value if hasattr(run.status, "value") else str(run.status)
        pending_statuses = {
            RunStatus.PENDING_USER_INPUT.value,
            RunStatus.PAUSED_WAITING_FOR_USER.value,
            RunStatus.PENDING_HUMAN.value,
        }
        result = run.output if status == RunStatus.COMPLETED.value else None
        if isinstance(result, dict) and "output_files" in result:
            result = {k: v for k, v in result.items() if k != "output_files"}
        error = None
        if status == RunStatus.COMPLETED.value and result is None:
            status = RunStatus.FAILED.value
            error = {"code": "missing_output", "message": "Missing run output", "step_id": None, "details": {}}
        if error is None and status != RunStatus.COMPLETED.value and status not in pending_statuses:
            failed = next((s for s in bundle.steps if s.status == StepStatus.FAILED), None)
            if failed:
                if failed.error and isinstance(failed.error, dict):
                    error = {
                        "code": "step_failed",
                        "message": failed.error.get("message") or "Step failed.",
                        "step_id": failed.step_id,
                        "details": failed.error,
                    }
                else:
                    error = {"code": "step_failed", "message": "Step failed.", "step_id": failed.step_id, "details": {}}
            elif run.summary:
                error = {
                    "code": "run_failed",
                    "message": run.summary.get("reason") or run.summary.get("error") or "Run failed.",
                    "step_id": None,
                    "details": run.summary or {},
                }
        response = {
            "response_version": "1.0",
            "run_id": run.run_id,
            "product": run.product,
            "flow": run.flow,
            "status": status,
            "result": result if status != RunStatus.COMPLETED.value else (result or {"kind": "files"}),
            "error": error,
            "finished_at": run.finished_at,
            "finished_at_iso": datetime.fromtimestamp(run.finished_at, tz=timezone.utc).isoformat()
            if run.finished_at
            else None,
        }
        output_info = self.memory.write_run_response(product=run.product, run_id=run.run_id, response=response)
        if output_info:
            self._emit_event(
                kind="output_written",
                run_id=run.run_id,
                step_id=None,
                product=run.product,
                flow=run.flow,
                payload=output_info,
            )

    def _rehydrate_artifacts(self, steps: List[StepRecord], run_ctx: RunContext) -> None:
        for step in steps:
            output = step.output or {}
            if not isinstance(output, dict):
                continue
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
        summary = summary or {}
        def _as_int(value: Any) -> Optional[int]:
            try:
                return int(value)
            except Exception:
                return None

        steps_executed = _as_int(summary.get("steps_executed"))
        if steps_executed is None and steps is not None:
            steps_executed = sum(1 for s in steps if not _is_step_status(s.status, StepStatus.NOT_STARTED))
        run_ctx.meta["steps_executed"] = steps_executed or 0
        run_ctx.meta["tool_calls"] = _as_int(summary.get("tool_calls")) or 0
        run_ctx.meta["tokens_used"] = _as_int(summary.get("tokens_used")) or 0

    @staticmethod
    def _summary_with_counters(run_ctx: RunContext, summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        merged = dict(summary or {})
        for key in ("steps_executed", "tool_calls", "tokens_used"):
            if key in run_ctx.meta:
                merged[key] = run_ctx.meta.get(key)
        return merged

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

# Backwards compatibility for older imports/tests
Engine = OrchestratorEngine


def _summarize_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    try:
        encoded = json.dumps(schema, sort_keys=True, ensure_ascii=True).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
    except Exception:
        digest = "unknown"
    props = schema.get("properties") if isinstance(schema, dict) else {}
    prop_keys = []
    if isinstance(props, dict):
        prop_keys = list(props.keys())
    return {"properties": prop_keys[:10], "property_count": len(prop_keys), "sha256": digest}


def _looks_like_user_input_answer(payload: Dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False
    return any(key in payload for key in ("prompt_id", "selected_option_ids", "free_text"))


def _primary_selection_key(request: UserInputRequest) -> str:
    props = request.schema.get("properties") if isinstance(request.schema, dict) else {}
    if isinstance(props, dict) and len(props) == 1:
        return next(iter(props))
    if isinstance(props, dict):
        if "selection" in props:
            return "selection"
        if "value" in props:
            return "value"
    return "selection"


def _options_from_request(request: UserInputRequest) -> List[UserInputOption]:
    options: List[UserInputOption] = []
    if isinstance(request.choices, list):
        for item in request.choices:
            if not isinstance(item, dict):
                continue
            option_id = str(item.get("id") or item.get("value") or item.get("label") or "").strip()
            if not option_id:
                continue
            label = str(item.get("label") or item.get("value") or option_id)
            options.append(
                UserInputOption(
                    option_id=option_id,
                    label=label,
                    value=item.get("value"),
                    description=item.get("description"),
                )
            )
        return options
    props = request.schema.get("properties") if isinstance(request.schema, dict) else {}
    if isinstance(props, dict):
        for spec in props.values():
            if not isinstance(spec, dict):
                continue
            enum = spec.get("enum")
            if isinstance(enum, list):
                for item in enum:
                    option_id = str(item)
                    options.append(UserInputOption(option_id=option_id, label=option_id, value=item))
                break
    return options


def _build_user_input_prompt(run_ctx: RunContext, step_id: str, request: UserInputRequest) -> UserInputPrompt:
    allow_free_text = request.mode == UserInputModes.FREE_TEXT_INPUT or request.input_type == "text"
    question = request.prompt or request.title or request.form_id
    return UserInputPrompt(
        schema_version=request.schema_version,
        prompt_id=request.form_id,
        run_id=run_ctx.run_id,
        step_id=step_id,
        title=request.title,
        question=question,
        options=_options_from_request(request),
        defaults=request.defaults,
        required=request.required,
        allow_free_text=allow_free_text,
    )


def _answer_to_response(
    request: UserInputRequest,
    answer: UserInputAnswer,
    *,
    comment: Optional[str],
) -> UserInputResponse:
    values: Dict[str, Any] = {}
    selected = answer.selected_option_ids or []
    if selected:
        values[_primary_selection_key(request)] = selected[0]
    if answer.free_text:
        values["text"] = answer.free_text
    if answer.metadata:
        values["metadata"] = answer.metadata
    return UserInputResponse(
        schema_version=request.schema_version,
        form_id=request.form_id,
        values=values,
        comment=comment or "",
        metadata=answer.metadata,
    )


def _validate_user_input_values(request: UserInputRequest, values: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    mode = request.mode or UserInputModes.CHOICE_INPUT
    if mode == UserInputModes.FREE_TEXT_INPUT:
        text_value = values.get("text")
        if not isinstance(text_value, str) or not text_value.strip():
            errors.append("missing_or_empty:text")
        return errors
    if mode != UserInputModes.CHOICE_INPUT:
        errors.append("invalid_mode")
        return errors
    for key in request.required:
        if key not in values:
            errors.append(f"missing_required:{key}")
    props = request.schema.get("properties") if isinstance(request.schema, dict) else {}
    if isinstance(props, dict):
        for key, spec in props.items():
            if key not in values:
                continue
            value = values.get(key)
            if not isinstance(spec, dict):
                continue
            expected_type = spec.get("type")
            if expected_type:
                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"type_mismatch:{key}")
                if expected_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"type_mismatch:{key}")
                if expected_type == "integer" and not isinstance(value, int):
                    errors.append(f"type_mismatch:{key}")
                if expected_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"type_mismatch:{key}")
            enum = spec.get("enum")
            if isinstance(enum, list) and value not in enum:
                errors.append(f"enum_mismatch:{key}")
    return errors


def _store_user_input_artifacts(run_ctx: RunContext, form_id: str, values: Dict[str, Any], comment: Optional[str]) -> None:
    bucket = run_ctx.artifacts.setdefault("user_input", {})
    if isinstance(bucket, dict):
        bucket[form_id] = {"values": values, "comment": comment or "", "metadata": values.get("metadata", {})}


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
