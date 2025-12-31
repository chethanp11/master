# ==============================
# Orchestrator Engine
# ==============================
from __future__ import annotations

import time
import uuid
from typing import Any, Callable, Dict, Optional

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
from core.governance.hooks import GovernanceHooks
from core.governance.security import SecurityRedactor
from core.logging.tracing import Tracer
from core.memory.router import MemoryRouter
from core.orchestrator.context import RunContext
from core.orchestrator.flow_loader import FlowLoader
from core.orchestrator.hitl import HitlService
from core.orchestrator.step_executor import StepExecutor
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry


def _new_run_id() -> str:
    return f"run_{uuid.uuid4().hex}"


class OrchestratorEngine:
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
        tracer_instance = tracer or Tracer(memory=memory_router, redactor=redactor)
        governance = GovernanceHooks(settings=settings, redactor=redactor)
        tool_executor = ToolExecutor(registry=ToolRegistry, hooks=governance, redactor=redactor)
        step_executor = StepExecutor(
            tool_executor=tool_executor,
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
                summary={"current_step_index": 0},
            )
            self.memory.create_run(run_record)

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

    def resume_run(
        self,
        *,
        run_id: str,
        approval_payload: Optional[Dict[str, Any]] = None,
        decision: str = "APPROVED",
        resolved_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> RunOperationResult:
        bundle = self.memory.get_run(run_id)
        if bundle is None:
            return RunOperationResult.failure(code="not_found", message=f"Unknown run_id: {run_id}")

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
            self.memory.update_run_status(run_id, RunStatus.FAILED.value, summary={"rejection": decision})
            self._emit_event(
                kind="run_rejected",
                run_id=run_id,
                step_id=approval.step_id,
                product=bundle.run.product,
                flow=bundle.run.flow,
                payload={"decision": decision, "approved": payload.get("approved")},
            )
            return RunOperationResult.success({"run_id": run_id, "status": RunStatus.FAILED.value})

        flow_def = self.flow_loader.load(product=bundle.run.product, flow=bundle.run.flow)
        next_index = self._find_step_index(flow_def, approval.step_id) + 1
        self.memory.update_run_status(run_id, RunStatus.RUNNING.value, summary={"current_step_index": next_index})
        self._emit_event(
            kind="run_resumed",
            run_id=run_id,
            step_id=approval.step_id,
            product=bundle.run.product,
            flow=bundle.run.flow,
            payload={"decision": decision},
        )

        merged_payload = dict(bundle.run.input or {})
        merged_payload.update(payload)
        run_ctx = RunContext(run_id=run_id, product=bundle.run.product, flow=bundle.run.flow, payload=merged_payload)
        run_ctx.trace = self._trace_hook(run_ctx)

        status = self._execute_from_index(
            flow_def=flow_def,
            run_ctx=run_ctx,
            start_index=next_index,
            requested_by=resolved_by,
        )
        return RunOperationResult.success({"run_id": run_id, "status": status})

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

    def _execute_from_index(
        self,
        *,
        flow_def: FlowDef,
        run_ctx: RunContext,
        start_index: int,
        requested_by: Optional[str],
    ) -> str:
        for idx in range(start_index, len(flow_def.steps)):
            step_def = flow_def.steps[idx]
            step_id = step_def.id or f"step_{idx}"

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
                self.memory.update_run_status(
                    run_ctx.run_id,
                    RunStatus.FAILED.value,
                    summary={"failed_step_id": step_id, "reason": decision.reason},
                )
                return RunStatus.FAILED.value

            self._emit_event(
                kind="step_started",
                run_id=run_ctx.run_id,
                step_id=step_id,
                product=run_ctx.product,
                flow=run_ctx.flow,
                payload={"step_index": idx, "type": step_def.type.value, "name": step_record.name},
            )

            if step_def.type == StepType.HUMAN_APPROVAL:
                approval = self.hitl.create_approval(
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    requested_by=requested_by,
                    payload={"step": step_record.model_dump()},
                )
                self.memory.update_step(
                    run_ctx.run_id,
                    step_id,
                    {
                        "status": StepStatus.PENDING_HUMAN.value,
                        "output": {"approval_id": approval.approval_id},
                    },
                )
                self.memory.update_run_status(run_ctx.run_id, RunStatus.PENDING_HUMAN.value, summary={"current_step_index": idx})
                self._emit_event(
                    kind="pending_human",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={"approval_id": approval.approval_id},
                )
                return RunStatus.PENDING_HUMAN.value

            try:
                result = self.step_executor.execute(run_ctx=run_ctx, step_def=step_def, step_id=step_id)
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
                self.memory.update_run_status(run_ctx.run_id, RunStatus.FAILED.value, summary={"failed_step_id": step_id})
                self._emit_event(
                    kind="step_failed",
                    run_id=run_ctx.run_id,
                    step_id=step_id,
                    product=run_ctx.product,
                    flow=run_ctx.flow,
                    payload={"error": {"message": str(exc), "type": type(exc).__name__}},
                )
                return RunStatus.FAILED.value

            self.memory.update_run_status(run_ctx.run_id, RunStatus.RUNNING.value, summary={"current_step_index": idx + 1})

        self.memory.update_run_status(run_ctx.run_id, RunStatus.COMPLETED.value, summary={"current_step_index": len(flow_def.steps)})
        self._emit_event(
            kind="run_completed",
            run_id=run_ctx.run_id,
            step_id=None,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"ok": True},
        )
        return RunStatus.COMPLETED.value

    def _find_step_index(self, flow_def: FlowDef, step_id: str) -> int:
        for idx, definition in enumerate(flow_def.steps):
            if (definition.id or f"step_{idx}") == step_id:
                return idx
        raise ValueError(f"Cannot map approval step '{step_id}' to flow definition.")

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

# Backwards compatibility for older imports/tests
Engine = OrchestratorEngine
