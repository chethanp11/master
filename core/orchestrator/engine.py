# ==============================
# Orchestrator Engine
# ==============================
"""
Main orchestration runtime.

v1 responsibilities:
- Load a flow definition
- Create a run record
- Execute steps sequentially
- Pause on HITL (human_approval) by creating an approval record and setting run status PENDING_HUMAN
- Resume from stored state after approval

Rules:
- No persistence outside MemoryRouter
- No tool calls outside core/tools/executor.py (step execution delegates to StepExecutor)
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional, Tuple

from core.contracts.flow_schema import FlowDef, StepDef, StepType
from core.contracts.run_schema import RunRecord, StepRecord, TraceEvent
from core.governance.hooks import GovernanceHooks, HookDecision
from core.logging.tracing import Tracer
from core.memory.router import MemoryRouter
from core.orchestrator.flow_loader import FlowLoader
from core.orchestrator.hitl import HitlService
from core.orchestrator.state import RunStatus, StepStatus
from core.orchestrator.step_executor import StepExecutor


def new_run_id() -> str:
    return f"run_{uuid.uuid4().hex}"


def new_step_id(flow_step: StepDef, idx: int) -> str:
    base = flow_step.id or f"step_{idx}"
    return f"{base}"


class OrchestratorEngine:
    def __init__(
        self,
        *,
        flow_loader: FlowLoader,
        step_executor: StepExecutor,
        memory: MemoryRouter,
        tracer: Tracer,
        governance: Optional[GovernanceHooks] = None,
    ) -> None:
        self.flow_loader = flow_loader
        self.step_executor = step_executor
        self.memory = memory
        self.tracer = tracer
        self.governance = governance or GovernanceHooks.noop()
        self.hitl = HitlService(memory)

    # ------------------------------
    # Public API
    # ------------------------------

    def run_flow(
        self,
        *,
        product: str,
        flow: str,
        payload: Dict[str, Any],
        requested_by: Optional[str] = None,
    ) -> str:
        run_id = new_run_id()
        flow_def = self._load_flow(product=product, flow=flow)

        run = RunRecord(
            run_id=run_id,
            product=product,
            flow=flow,
            status=RunStatus.RUNNING.value,
            autonomy_level=flow_def.autonomy_level,
            started_at=int(time.time()),
            finished_at=None,
            input=payload,
            output=None,
            summary={"current_step_index": 0},
        )
        self.memory.create_run(run)
        self._emit_event(
            kind="run_started",
            run_id=run_id,
            step_id=None,
            product=product,
            flow=flow,
            payload={"autonomy_level": flow_def.autonomy_level},
        )

        self._execute_from_index(
            flow_def=flow_def,
            run_id=run_id,
            start_index=0,
            requested_by=requested_by,
        )
        return run_id

    def resume_run(
        self,
        *,
        run_id: str,
        decision: str,
        resolved_by: Optional[str] = None,
        comment: Optional[str] = None,
        approval_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        bundle = self.memory.get_run(run_id)
        if bundle is None:
            raise ValueError(f"Unknown run_id: {run_id}")

        product = bundle.run.product
        flow = bundle.run.flow
        flow_def = self._load_flow(product=product, flow=flow)

        # find the pending approval (latest)
        pending = [a for a in bundle.approvals if a.status == "PENDING"]
        if not pending:
            raise ValueError(f"No pending approvals for run_id={run_id}")

        approval = pending[0]
        self.hitl.resolve_approval(
            approval_id=approval.approval_id,
            decision=decision,
            resolved_by=resolved_by,
            comment=comment,
        )

        # mark the step as completed and store approval outcome in step output
        self.memory.update_step(
            run_id,
            approval.step_id,
            {
                "status": StepStatus.COMPLETED.value,
                "finished_at": int(time.time()),
                "output": {"approval": {"decision": decision, "comment": comment, "payload": approval_payload or {}}},
            },
        )

        # resume: next step index is approval step index + 1
        approval_step_index = self._find_step_index(flow_def, approval.step_id)
        next_index = approval_step_index + 1

        self.memory.update_run_status(run_id, RunStatus.RUNNING.value, summary={"current_step_index": next_index})
        self._emit_event(
            kind="run_resumed",
            run_id=run_id,
            step_id=approval.step_id,
            product=product,
            flow=flow,
            payload={"decision": decision},
        )

        self._execute_from_index(
            flow_def=flow_def,
            run_id=run_id,
            start_index=next_index,
            requested_by=resolved_by,
        )

    # ------------------------------
    # Internals
    # ------------------------------

    def _load_flow(self, *, product: str, flow: str) -> FlowDef:
        return self.flow_loader.load(product=product, flow=flow)

    def _find_step_index(self, flow_def: FlowDef, step_id: str) -> int:
        # step_id in DB is the flow step id; if missing, cannot map reliably.
        for idx, s in enumerate(flow_def.steps):
            if (s.id or f"step_{idx}") == step_id:
                return idx
        # fallback: attempt exact match for name
        for idx, s in enumerate(flow_def.steps):
            if s.name == step_id:
                return idx
        raise ValueError(f"Cannot map approval step_id='{step_id}' to flow steps. Ensure StepDef.id is set.")

    def _execute_from_index(
        self,
        *,
        flow_def: FlowDef,
        run_id: str,
        start_index: int,
        requested_by: Optional[str],
    ) -> None:
        product = flow_def.product
        flow = flow_def.name

        for idx in range(start_index, len(flow_def.steps)):
            step_def = flow_def.steps[idx]
            step_id = new_step_id(step_def, idx)

            # Persist step record if not already there
            step_record = StepRecord(
                run_id=run_id,
                step_id=step_id,
                step_index=idx,
                name=step_def.name or step_id,
                type=step_def.type,
                status=StepStatus.RUNNING.value,
                started_at=int(time.time()),
                finished_at=None,
                input={"params": step_def.params or {}},
                output=None,
                error=None,
                meta={"backend": step_def.backend, "target": step_def.target},
            )
            self.memory.add_step(step_record)

            # Governance before_step
            dec = self.governance.before_step(run_id=run_id, step_id=step_id, product=product, flow=flow, payload=step_record.model_dump())
            self._enforce(dec, run_id=run_id, product=product, flow=flow, step_id=step_id, kind="before_step_denied")

            self._emit_event(
                kind="step_started",
                run_id=run_id,
                step_id=step_id,
                product=product,
                flow=flow,
                payload={"step_index": idx, "type": step_def.type, "name": step_record.name},
            )

            # HITL step: pause and return immediately
            if self._is_human_approval(step_def):
                approval = self.hitl.create_approval(
                    run_id=run_id,
                    step_id=step_id,
                    product=product,
                    flow=flow,
                    requested_by=requested_by,
                    payload={"step": step_record.model_dump()},
                )
                self.memory.update_step(
                    run_id,
                    step_id,
                    {"status": StepStatus.PENDING_HUMAN.value, "finished_at": None, "output": {"approval_id": approval.approval_id}},
                )
                self.memory.update_run_status(run_id, RunStatus.PENDING_HUMAN.value, summary={"current_step_index": idx})
                self._emit_event(
                    kind="pending_human",
                    run_id=run_id,
                    step_id=step_id,
                    product=product,
                    flow=flow,
                    payload={"approval_id": approval.approval_id},
                )
                return

            # Execute step
            try:
                result = self.step_executor.execute(run_id=run_id, step_id=step_id, product=product, flow=flow, step=step_def)
                self.memory.update_step(
                    run_id,
                    step_id,
                    {"status": StepStatus.COMPLETED.value, "finished_at": int(time.time()), "output": result},
                )
                self._emit_event(
                    kind="step_completed",
                    run_id=run_id,
                    step_id=step_id,
                    product=product,
                    flow=flow,
                    payload={"ok": True},
                )
            except Exception as e:
                # Never leak raw exceptions; store as error dict
                self.memory.update_step(
                    run_id,
                    step_id,
                    {
                        "status": StepStatus.FAILED.value,
                        "finished_at": int(time.time()),
                        "error": {"message": str(e), "type": type(e).__name__},
                    },
                )
                self.memory.update_run_status(run_id, RunStatus.FAILED.value, summary={"failed_step_id": step_id})
                self._emit_event(
                    kind="step_failed",
                    run_id=run_id,
                    step_id=step_id,
                    product=product,
                    flow=flow,
                    payload={"error": {"message": str(e), "type": type(e).__name__}},
                )
                return

            # Update run progress
            self.memory.update_run_status(run_id, RunStatus.RUNNING.value, summary={"current_step_index": idx + 1})

        # Completed run
        self.memory.update_run_status(run_id, RunStatus.COMPLETED.value, summary={"current_step_index": len(flow_def.steps)})
        self._emit_event(
            kind="run_completed",
            run_id=run_id,
            step_id=None,
            product=product,
            flow=flow,
            payload={"ok": True},
        )

    def _is_human_approval(self, step_def: StepDef) -> bool:
        return step_def.type == StepType.HUMAN_APPROVAL.value or step_def.type == "human_approval"

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

    def _enforce(self, decision: HookDecision, *, run_id: str, product: str, flow: str, step_id: Optional[str], kind: str) -> None:
        if decision.allowed:
            return
        self._emit_event(
            kind=kind,
            run_id=run_id,
            step_id=step_id,
            product=product,
            flow=flow,
            payload={"reason": decision.reason},
        )
        raise PermissionError(decision.reason or "Denied by governance")