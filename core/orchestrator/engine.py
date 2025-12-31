# ==============================
# Orchestrator Engine
# ==============================
from __future__ import annotations

import time
import uuid
import json
import shutil
from datetime import datetime
from typing import Any, Callable, Dict, Optional, List

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
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return f"run_{ts}"


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
        tracer_instance = tracer or Tracer.from_settings(settings=settings, memory=memory_router)
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
                payload={"decision": decision, "approved": payload.get("approved"), "comment": comment},
            )
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
                self.memory.update_run_status(
                    run_id,
                    RunStatus.RUNNING.value,
                    summary={"current_step_index": plan_index or 0, "replan_of": run_id},
                )
                replan_ctx = RunContext(
                    run_id=run_id,
                    product=bundle.run.product,
                    flow=bundle.run.flow,
                    payload=replan_payload,
                )
                replan_ctx.trace = self._trace_hook(replan_ctx)
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
                        self.memory.update_run_status(run_id, RunStatus.FAILED.value, summary={"failed_step_id": replan_step_id})
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
            payload={"decision": decision, "comment": comment},
        )

        merged_payload = dict(bundle.run.input or {})
        merged_payload.update(payload)
        run_ctx = RunContext(run_id=run_id, product=bundle.run.product, flow=bundle.run.flow, payload=merged_payload)
        run_ctx.trace = self._trace_hook(run_ctx)
        self._rehydrate_artifacts(bundle.steps, run_ctx)

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
        idx = start_index
        while idx < len(flow_def.steps):
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
                self._persist_run_output(run_ctx)
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
                self.memory.update_run_status(run_ctx.run_id, RunStatus.PENDING_HUMAN.value, summary={"current_step_index": idx})
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
                self._persist_run_output(run_ctx)
                return RunStatus.FAILED.value

            next_index = idx + 1
            if step_id in {"plan", "planning"}:
                next_index = self._resolve_plan_next_index(flow_def, idx, result)
            self.memory.update_run_status(run_ctx.run_id, RunStatus.RUNNING.value, summary={"current_step_index": next_index})
            idx = next_index

        self.memory.update_run_status(run_ctx.run_id, RunStatus.COMPLETED.value, summary={"current_step_index": len(flow_def.steps)})
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

    def _persist_run_output(self, run_ctx: RunContext) -> None:
        writer = getattr(self.tracer, "writer", None)
        if writer is None:
            return
        bundle = self.memory.get_run(run_ctx.run_id)
        if bundle is None:
            return
        output = {
            "run": bundle.run.model_dump(),
            "steps": [s.model_dump() for s in bundle.steps],
            "approvals": [a.model_dump() for a in bundle.approvals],
            "artifacts": run_ctx.artifacts,
        }
        output_path = writer.output_path(product=run_ctx.product, run_id=run_ctx.run_id, name="response.json")
        output_path.write_text(json.dumps(output, indent=2, ensure_ascii=True), encoding="utf-8")

    def _rehydrate_artifacts(self, steps: List[StepRecord], run_ctx: RunContext) -> None:
        for step in steps:
            output = step.output or {}
            if not isinstance(output, dict):
                continue
            meta = output.get("meta")
            data = output.get("data")
            if not isinstance(meta, dict) or data is None:
                continue
            tool_name = meta.get("tool_name")
            agent_name = meta.get("agent_name")
            if tool_name:
                run_ctx.artifacts[f"tool.{tool_name}.output"] = data
                run_ctx.artifacts[f"tool.{tool_name}.meta"] = meta
            if agent_name:
                run_ctx.artifacts[f"agent.{agent_name}.output"] = data
                run_ctx.artifacts[f"agent.{agent_name}.meta"] = meta

    def _stage_inputs(self, run_ctx: RunContext) -> None:
        writer = getattr(self.tracer, "writer", None)
        if writer is None:
            return
        payload = run_ctx.payload or {}
        upload_id = payload.get("upload_id")
        files = payload.get("files") or []
        if not upload_id:
            return
        source_dir = writer.root / run_ctx.product / "uploads" / str(upload_id) / "input"
        if not source_dir.exists():
            return
        if not files:
            for source in source_dir.iterdir():
                if source.is_file():
                    target = writer.input_path(product=run_ctx.product, run_id=run_ctx.run_id, name=source.name)
                    if not target.exists():
                        shutil.copy2(source, target)
            return
        for file_ref in files:
            if not isinstance(file_ref, dict):
                continue
            name = file_ref.get("name") or file_ref.get("file_name")
            if not name:
                continue
            source = source_dir / name
            if not source.exists():
                continue
            target = writer.input_path(product=run_ctx.product, run_id=run_ctx.run_id, name=name)
            if not target.exists():
                shutil.copy2(source, target)

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
