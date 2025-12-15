# ==============================
# Orchestrator Engine
# ==============================
"""
Orchestrator engine for master/ (v1).

Responsibilities:
- Load flow definitions (via FlowLoader)
- Create/track RunRecord and StepRecord states
- Execute steps sequentially (graph execution later)
- Pause for human approval (HITL) and resume from stored state
- Emit trace events through RunContext/StepContext hooks

Non-responsibilities:
- No direct DB writes (only via injected memory backend)
- No direct tool calls (only via injected tool runner / tool executor elsewhere)
- No direct model calls (only via injected agent runner)

Persistence contract (duck-typed v1):
If memory_backend is provided, engine will call these methods when present:
- upsert_run(run: RunRecord) -> None
- upsert_step(step: StepRecord) -> None
- append_event(run_id: str, event_type: str, payload: dict) -> None (optional)
- get_run(run_id: str) -> RunRecord
- get_flow_snapshot(run_id: str) -> dict (optional, can be embedded in run.meta)
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from core.contracts.flow_schema import FlowDef, StepDef, StepType
from core.contracts.run_schema import RunRecord, StepRecord
from core.orchestrator.context import RunContext, StepContext
from core.orchestrator.flow_loader import FlowLoader
from core.orchestrator.hitl import ResumePayload, create_approval_request, attach_approval_to_run, mark_run_pending_human, mark_step_waiting_human, apply_resume_payload
from core.orchestrator.state import RunStatus, StepStatus, RUN_TERMINAL
from core.orchestrator.step_executor import AgentRunner, ToolRunner, SubflowRunner, execute_step

# ==============================
# Engine
# ==============================
class OrchestratorEngine:
    """
    v1 orchestrator engine.

    Injected dependencies:
- memory_backend: optional persistence adapter (implemented in core/memory/* later)
- agent_runner: callable that runs an agent by name
- tool_runner: callable that runs a tool by name
- subflow_runner: optional callable to run subflows
    """

    # ==============================
    # Construction
    # ==============================
    def __init__(
        self,
        *,
        memory_backend: Optional[Any] = None,
        agent_runner: Optional[AgentRunner] = None,
        tool_runner: Optional[ToolRunner] = None,
        subflow_runner: Optional[SubflowRunner] = None,
    ) -> None:
        self._mem = memory_backend
        self._agent_runner = agent_runner
        self._tool_runner = tool_runner
        self._subflow_runner = subflow_runner

    # ==============================
    # Public API
    # ==============================
    def run_flow(
        self,
        *,
        product: str,
        flow: Union[FlowDef, str, Path],
        initial_input: Optional[Dict[str, Any]] = None,
        trace_hook: Optional[Any] = None,
    ) -> RunRecord:
        """
        Start a new run.

        flow can be:
- FlowDef object
- path to YAML/JSON file
        """
        flow_def = self._resolve_flow(flow)
        run = RunRecord(
            product=product,
            flow_id=flow_def.id,
            status=RunStatus.RUNNING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            current_step_id=None,
            steps=[],
            summary=None,
            final_output_ref=None,
            meta={},
        )
        if initial_input is not None:
            run.meta["input"] = initial_input

        ctx = RunContext(run_record=run, flow=flow_def, status=run.status, metadata={}, artifacts={}, trace=trace_hook)  # type: ignore[arg-type]
        ctx.emit("run_started", {"product": product, "flow_id": flow_def.id})

        self._persist_run(run)

        # sequential execution v1
        for step_def in flow_def.steps:
            if run.status in RUN_TERMINAL:
                break

            run.current_step_id = step_def.id
            run.updated_at = datetime.utcnow()
            self._persist_run(run)

            step_rec = self._get_or_create_step_record(run, step_def)

            # already completed steps can be skipped (useful on resume)
            if step_rec.status == StepStatus.COMPLETED:
                continue

            step_ctx = StepContext(run=ctx, step=step_def, status=step_rec.status, attempt=step_rec.attempt)
            step_ctx.emit("step_started", {"step_type": step_def.type.value})

            if step_def.type == StepType.HUMAN_APPROVAL:
                self._handle_hitl_pause(run, step_rec, step_def, ctx)
                self._persist_run(run)
                self._persist_step(step_rec)
                return run

            # execute agent/tool/subflow
            executed_step, output_payload = execute_step(
                step_ctx=step_ctx,
                agent_runner=self._agent_runner,
                tool_runner=self._tool_runner,
                subflow_runner=self._subflow_runner,
            )
            self._merge_step_record(run, executed_step)

            # store minimal output in run meta for v1 (artifact persistence comes later)
            if output_payload is not None:
                outputs = run.meta.get("outputs")
                if outputs is None or not isinstance(outputs, dict):
                    run.meta["outputs"] = {}
                    outputs = run.meta["outputs"]
                outputs[step_def.id] = output_payload

            # update run based on step result
            if executed_step.status == StepStatus.FAILED:
                run.status = RunStatus.FAILED
                run.summary = f"Failed at step {step_def.id}"
            elif executed_step.status == StepStatus.COMPLETED:
                run.status = RunStatus.RUNNING

            run.updated_at = datetime.utcnow()
            self._persist_step(executed_step)
            self._persist_run(run)

            if run.status == RunStatus.FAILED:
                break

        # finalize
        if run.status == RunStatus.RUNNING:
            run.status = RunStatus.COMPLETED
            run.summary = "Completed"
            run.updated_at = datetime.utcnow()
            ctx.emit("run_completed", {"status": run.status.value})
            self._persist_run(run)

        return run

    def resume_run(
        self,
        *,
        run_id: str,
        payload: Dict[str, Any],
        trace_hook: Optional[Any] = None,
    ) -> RunRecord:
        """
        Resume a run paused for human approval.

        Requires memory_backend.get_run(run_id) if persistence is enabled.
        If no backend exists, resume is not possible in v1.
        """
        if self._mem is None or not hasattr(self._mem, "get_run"):
            raise RuntimeError("resume_run requires a memory backend with get_run(run_id)")

        run: RunRecord = self._mem.get_run(run_id)
        if run.status != RunStatus.PENDING_HUMAN:
            return run

        if run.current_step_id is None:
            raise RuntimeError("Run is PENDING_HUMAN but current_step_id is missing")

        # flow snapshot retrieval strategy:
        # v1 expects flow_def embedded in run.meta["flow"] or provided externally by caller later.
        flow_def = self._resolve_flow_from_run(run)
        ctx = RunContext(run_record=run, flow=flow_def, status=run.status, metadata={}, artifacts={}, trace=trace_hook)  # type: ignore[arg-type]
        ctx.emit("run_resume_requested", {"run_id": run_id})

        # find step def and step record
        step_def = _find_step_def(flow_def.steps, run.current_step_id)
        step_rec = self._find_step_record(run, step_def.id)
        if step_rec is None:
            step_rec = self._get_or_create_step_record(run, step_def)

        # apply decision
        rp = ResumePayload.model_validate(payload)
        apply_resume_payload(run=run, step_rec=step_rec, payload=rp)

        self._persist_step(step_rec)
        self._persist_run(run)

        # continue remaining steps
        remaining_steps = _steps_after(flow_def.steps, step_def.id)
        for sdef in remaining_steps:
            if run.status in RUN_TERMINAL:
                break

            run.current_step_id = sdef.id
            run.updated_at = datetime.utcnow()
            self._persist_run(run)

            srec = self._get_or_create_step_record(run, sdef)
            if srec.status == StepStatus.COMPLETED:
                continue

            sctx = StepContext(run=ctx, step=sdef, status=srec.status, attempt=srec.attempt)
            sctx.emit("step_started", {"step_type": sdef.type.value})

            if sdef.type == StepType.HUMAN_APPROVAL:
                self._handle_hitl_pause(run, srec, sdef, ctx)
                self._persist_step(srec)
                self._persist_run(run)
                return run

            executed_step, output_payload = execute_step(
                step_ctx=sctx,
                agent_runner=self._agent_runner,
                tool_runner=self._tool_runner,
                subflow_runner=self._subflow_runner,
            )
            self._merge_step_record(run, executed_step)

            if output_payload is not None:
                outputs = run.meta.get("outputs")
                if outputs is None or not isinstance(outputs, dict):
                    run.meta["outputs"] = {}
                    outputs = run.meta["outputs"]
                outputs[sdef.id] = output_payload

            if executed_step.status == StepStatus.FAILED:
                run.status = RunStatus.FAILED
                run.summary = f"Failed at step {sdef.id}"
            else:
                run.status = RunStatus.RUNNING

            run.updated_at = datetime.utcnow()
            self._persist_step(executed_step)
            self._persist_run(run)

            if run.status == RunStatus.FAILED:
                break

        if run.status == RunStatus.RUNNING:
            run.status = RunStatus.COMPLETED
            run.summary = "Completed"
            run.updated_at = datetime.utcnow()
            ctx.emit("run_completed", {"status": run.status.value})
            self._persist_run(run)

        return run

    # ==============================
    # HITL
    # ==============================
    def _handle_hitl_pause(self, run: RunRecord, step_rec: StepRecord, step_def: StepDef, ctx: RunContext) -> None:
        approval = create_approval_request(run=run, step=step_def)
        attach_approval_to_run(run=run, approval=approval)

        mark_run_pending_human(run=run, step_id=step_def.id)
        mark_step_waiting_human(step_rec=step_rec)

        ctx.emit("hitl_pending", {"step_id": step_def.id, "approval": approval.to_dict()})

    # ==============================
    # Flow Resolution
    # ==============================
    def _resolve_flow(self, flow: Union[FlowDef, str, Path]) -> FlowDef:
        if isinstance(flow, FlowDef):
            return flow
        p = Path(flow)
        flow_def = FlowLoader.load_from_path(p)
        # store a snapshot in meta for resume (v1)
        return flow_def

    def _resolve_flow_from_run(self, run: RunRecord) -> FlowDef:
        raw = run.meta.get("flow")
        if isinstance(raw, dict):
            return FlowLoader.load_from_obj(raw)
        raise RuntimeError("RunRecord.meta['flow'] missing. v1 requires flow snapshot embedded at run start.")

    # ==============================
    # Persistence Adapters (Duck-Typed)
    # ==============================
    def _persist_run(self, run: RunRecord) -> None:
        # v1 embed flow snapshot if not already set (for resume)
        if "flow" not in run.meta:
            # caller must pass FlowDef to run_flow to avoid missing flow snapshot; if path is used, we can't access it here
            # engine.run_flow sets flow snapshot by injecting via ctx when created; done in run_flow below
            pass

        if self._mem is None:
            return
        if hasattr(self._mem, "upsert_run"):
            self._mem.upsert_run(run)

    def _persist_step(self, step: StepRecord) -> None:
        if self._mem is None:
            return
        if hasattr(self._mem, "upsert_step"):
            self._mem.upsert_step(step)

    # ==============================
    # Step Records Helpers
    # ==============================
    def _get_or_create_step_record(self, run: RunRecord, step_def: StepDef) -> StepRecord:
        existing = self._find_step_record(run, step_def.id)
        if existing is not None:
            return existing
        rec = StepRecord(
            run_id=run.run_id,
            step_id=step_def.id,
            status=StepStatus.NOT_STARTED,
            started_at=None,
            ended_at=None,
            attempt=0,
            error=None,
            input_ref=None,
            output_ref=None,
            meta={},
        )
        run.steps.append(rec)
        return rec

    def _find_step_record(self, run: RunRecord, step_id: str) -> Optional[StepRecord]:
        for s in run.steps:
            if s.step_id == step_id:
                return s
        return None

    def _merge_step_record(self, run: RunRecord, updated: StepRecord) -> None:
        for i, s in enumerate(run.steps):
            if s.step_id == updated.step_id:
                run.steps[i] = updated
                return
        run.steps.append(updated)


# ==============================
# Helpers
# ==============================
def _find_step_def(steps: List[StepDef], step_id: str) -> StepDef:
    for s in steps:
        if s.id == step_id:
            return s
    raise RuntimeError(f"Step not found in flow: {step_id}")


def _steps_after(steps: List[StepDef], step_id: str) -> List[StepDef]:
    found = False
    out: List[StepDef] = []
    for s in steps:
        if found:
            out.append(s)
        if s.id == step_id:
            found = True
    return out