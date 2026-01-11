from __future__ import annotations

# ==============================
# Step Executor
# ==============================

import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, Optional, List, Tuple, Any

from core.agents.registry import AgentRegistry
from core.contracts.agent_schema import AgentResult
from core.governance.hooks import GovernanceHooks
from core.contracts.flow_schema import StepDef, StepType, RetryPolicy, ToolBatchItem
from core.contracts.action_plan_schema import PlanProposal
from core.contracts.run_schema import StepStatus
from core.contracts.tool_schema import ToolResult
from core.orchestrator.context import RunContext, StepContext
from core.orchestrator.templating import render_params
from core.orchestrator._types import ToolBatchResultItem
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry
from core.orchestrator.error_policy import evaluate_retry


class StepExecutor:
    """
    Executes a single StepDef using registered agents/tools.
    """

    def __init__(
        self,
        *,
        tool_executor: ToolExecutor,
        governance: GovernanceHooks,
        agent_registry: AgentRegistry = AgentRegistry,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self.tool_executor = tool_executor
        self.governance = governance
        self.agent_registry = agent_registry
        self.sleep_fn = sleep_fn

    def execute(
        self,
        *,
        run_ctx: RunContext,
        step_def: StepDef,
        step_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        resolved_step_id = step_id or step_def.id or "step"
        step_ctx = run_ctx.new_step(
            step_def=step_def,
            step_id=resolved_step_id,
            step_type=step_def.type.value if isinstance(step_def.type, StepType) else str(step_def.type),
            backend=step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend,
            target=step_def.agent or step_def.tool,
        )

        if step_def.type == StepType.TOOL:
            context = {"payload": run_ctx.payload, "artifacts": run_ctx.artifacts}
            rendered_params = render_params(step_def.params or {}, context)
            step_def = step_def.model_copy(update={"params": rendered_params})
            tool_result = self._execute_tool(step_ctx=step_ctx, step_def=step_def)
            if tool_result.ok:
                run_ctx.artifacts[f"tool.{step_def.tool}.output"] = tool_result.data
                run_ctx.artifacts[f"tool.{step_def.tool}.meta"] = tool_result.meta.model_dump(mode="json")
            return tool_result.model_dump(mode="json")

        if step_def.type == StepType.TOOL_BATCH:
            return self._execute_tool_batch(run_ctx=run_ctx, step_def=step_def, step_ctx=step_ctx)

        if step_def.type == StepType.USER_INPUT:
            raise ValueError("user_input steps are orchestrator-managed; use OrchestratorEngine to pause/resume.")

        if step_def.type == StepType.AGENT:
            if not step_def.agent:
                raise ValueError("agent step missing 'agent' field")
            agent = self.agent_registry.resolve(step_def.agent)
            result: AgentResult = agent.run(step_ctx)
            if not result.ok:
                raise RuntimeError(result.error.message if result.error else "agent_failed")
            decision = self.governance.validate_agent_output(
                agent_name=step_def.agent,
                output=result.data or {},
                ctx=step_ctx,
            )
            if not decision.allowed:
                step_ctx.emit(
                    "agent_output_denied",
                    {"agent": step_def.agent, "reason": decision.reason, "details": decision.details},
                )
                raise RuntimeError(decision.reason or "agent_output_denied")
            step_ctx.emit(
                "agent.executed",
                {
                    "agent": step_def.agent,
                    "result": result.model_dump(mode="json"),
                },
            )
            run_ctx.artifacts[f"agent.{step_def.agent}.output"] = result.data
            run_ctx.artifacts[f"agent.{step_def.agent}.meta"] = result.meta.model_dump(mode="json")
            return result.model_dump(mode="json")

        if step_def.type == StepType.PLAN_PROPOSAL:
            if not step_def.agent:
                raise ValueError("plan_proposal step missing 'agent' field")
            agent = self.agent_registry.resolve(step_def.agent)
            result = agent.run(step_ctx)
            if not result.ok:
                raise RuntimeError(result.error.message if result.error else "plan_proposal_failed")
            decision = self.governance.validate_agent_output(
                agent_name=step_def.agent,
                output=result.data or {},
                ctx=step_ctx,
            )
            if not decision.allowed:
                step_ctx.emit(
                    "agent_output_denied",
                    {"agent": step_def.agent, "reason": decision.reason, "details": decision.details},
                )
                raise RuntimeError(decision.reason or "agent_output_denied")
            step_ctx.emit(
                "agent.executed",
                {
                    "agent": step_def.agent,
                    "result": result.model_dump(mode="json"),
                },
            )
            try:
                plan = PlanProposal.model_validate(result.data or {})
            except Exception as exc:
                step_ctx.emit("plan_validation_failed", {"error": str(exc)})
                raise RuntimeError("plan_validation_failed")
            plan_payload = plan.model_dump(mode="json")
            run_ctx.artifacts["plan.proposal"] = plan_payload
            step_ctx.emit("plan_proposed", {"plan": _summarize_plan(plan)})
            result = result.model_copy(update={"data": plan_payload})
            return result.model_dump(mode="json")

        if step_def.type == StepType.SUBFLOW:
            raise NotImplementedError("subflow execution is not implemented in v1")

        raise ValueError(f"Unsupported step type: {step_def.type}")

    def _execute_tool(self, *, step_ctx: StepContext, step_def: StepDef) -> ToolResult:
        if not step_def.tool:
            raise ValueError("tool step missing 'tool' field")

        params = step_def.params or {}
        attempt = 1
        retry_policy: Optional[RetryPolicy] = step_def.retry
        while True:
            step_ctx.emit("tool_call_attempt_started", {"attempt": attempt, "tool": step_def.tool})
            result = self.tool_executor.execute(tool_name=step_def.tool, params=params, ctx=step_ctx)
            if result.ok:
                step_ctx.emit("tool_call_succeeded", {"attempt": attempt, "tool": step_def.tool})
                return result

            error_code = None
            error_type = None
            if result.error:
                error_code = result.error.code.value if hasattr(result.error.code, "value") else str(result.error.code)
                error_type = result.error.code.name if hasattr(result.error.code, "name") else type(result.error).__name__
            step_ctx.emit(
                "tool_call_attempt_failed",
                {
                    "attempt": attempt,
                    "tool": step_def.tool,
                    "error_code": error_code,
                    "error_type": error_type,
                    "message": result.error.message if result.error else "tool_failed",
                },
            )

            decision = evaluate_retry(attempt_index=attempt, retry_policy=retry_policy, error_code=error_code)
            if not decision.should_retry:
                raise RuntimeError(result.error.message if result.error else "tool_failed")

            delay = decision.next_backoff_seconds
            step_ctx.emit(
                "tool_call_retry_scheduled",
                {"attempt": attempt + 1, "tool": step_def.tool, "delay_ms": int(delay * 1000)},
            )
            if delay > 0:
                self.sleep_fn(delay)
            attempt += 1

    def _execute_tool_batch(
        self,
        *,
        run_ctx: RunContext,
        step_def: StepDef,
        step_ctx: StepContext,
    ) -> Dict[str, Any]:
        items = step_def.tools or []
        if not items:
            raise ValueError("tool_batch requires tools")

        for item in items:
            if not ToolRegistry.has(item.tool_name):
                step_ctx.emit("tool_batch_rejected", {"tool": item.tool_name, "reason": "tool_not_registered"})
                raise RuntimeError(f"tool_batch_rejected:{item.tool_name}")
            descriptor = ToolRegistry.get_descriptor(item.tool_name)
            if not descriptor.read_only:
                step_ctx.emit("tool_batch_rejected", {"tool": item.tool_name, "reason": "tool_not_read_only"})
                raise RuntimeError(f"tool_batch_rejected:{item.tool_name}")
            if descriptor.side_effect:
                step_ctx.emit("tool_batch_rejected", {"tool": item.tool_name, "reason": "tool_has_side_effect"})
                raise RuntimeError(f"tool_batch_rejected:{item.tool_name}")

        parallel_requested = bool(step_def.parallel)
        parallel_effective = parallel_requested
        budget = run_ctx.meta.get("budget")
        if parallel_effective and budget is not None:
            max_parallel = getattr(budget, "max_parallel_calls", None)
            if isinstance(max_parallel, int) and max_parallel < len(items):
                parallel_effective = False
                step_ctx.emit(
                    "tool_batch_degraded",
                    {"reason": "max_parallel_calls_exceeded", "requested": len(items), "limit": max_parallel},
                )

        step_ctx.emit(
            "tool_batch_started",
            {"count": len(items), "parallel": parallel_requested, "parallel_effective": parallel_effective},
        )

        results: List[Tuple[int, ToolBatchItem, ToolResult]] = []
        if parallel_effective:
            with ThreadPoolExecutor(max_workers=len(items)) as executor:
                futures = {
                    executor.submit(self._run_batch_tool, run_ctx, step_ctx.step_id, idx, item): (idx, item)
                    for idx, item in enumerate(items)
                }
                for future in as_completed(futures):
                    idx, item = futures[future]
                    results.append((idx, item, future.result()))
        else:
            for idx, item in enumerate(items):
                results.append((idx, item, self._run_batch_tool(run_ctx, step_ctx.step_id, idx, item)))

        results.sort(key=lambda entry: entry[0])
        merged_evidence = []
        merged_artifacts: Dict[str, Any] = {}
        merged_results: List[ToolBatchResultItem] = []

        for idx, item, result in results:
            if not result.ok:
                raise RuntimeError(f"tool_batch_tool_failed:{item.tool_name}")
            tool_results_data = result.data or {}
            merged_results.append({"tool": item.tool_name, "alias": item.alias, "data": tool_results_data})

            for evidence_index, evidence in enumerate(result.evidence or []):
                stable_id = _stable_batch_evidence_id(
                    step_ctx.step_id,
                    item.tool_name,
                    idx,
                    evidence_index,
                )
                merged_evidence.append(evidence.model_copy(update={"id": stable_id}))

            if result.artifacts:
                prefix = item.alias or item.tool_name
                for key, ref in result.artifacts.items():
                    merged_artifacts[f"{prefix}.{key}"] = ref

        step_ctx.emit(
            "tool_batch_completed",
            {"count": len(items), "evidence_count": len(merged_evidence)},
        )

        meta = result.meta.model_copy(update={"tool_name": "tool_batch"}) if results else None
        envelope = ToolResult(
            ok=True,
            data={"results": merged_results},
            error=None,
            meta=meta or ToolResult.ok().meta,
            evidence=merged_evidence,
            artifacts=merged_artifacts or None,
        )
        return envelope.model_dump(mode="json")

    def _run_batch_tool(
        self,
        run_ctx: RunContext,
        batch_step_id: str,
        idx: int,
        item: ToolBatchItem,
    ) -> ToolResult:
        sub_step_id = f"{batch_step_id}/tool[{idx}]"
        sub_ctx = run_ctx.new_step(step_id=sub_step_id, step_type="tool", backend="local", target=item.tool_name)
        sub_ctx.emit("tool_call_started", {"tool": item.tool_name, "index": idx, "alias": item.alias})
        result = self.tool_executor.execute(tool_name=item.tool_name, params=item.inputs, ctx=sub_ctx)
        evidence_ids = [e.id for e in result.evidence] if result.evidence else []
        sub_ctx.emit(
            "tool_call_completed",
            {"tool": item.tool_name, "index": idx, "alias": item.alias, "ok": result.ok, "evidence_ids": evidence_ids},
        )
        return result


def _stable_batch_evidence_id(
    step_id: str,
    tool_name: str,
    tool_index: int,
    evidence_index: int,
) -> str:
    seed = f"{step_id}:{tool_name}:{tool_index}:{evidence_index}"
    return f"batch_{hashlib.sha256(seed.encode('utf-8')).hexdigest()}"

def build_step_context(run_ctx: RunContext, *, step_id: Optional[str], step_def: StepDef) -> StepContext:
    resolved_step_id = step_id or step_def.id or "step"
    return run_ctx.new_step(
        step_id=resolved_step_id,
        step_type=step_def.type.value if isinstance(step_def.type, StepType) else str(step_def.type),
        backend=step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend,
        target=step_def.agent or step_def.tool,
    )


def _summarize_plan(plan: PlanProposal) -> Dict[str, Any]:
    step_ids = [step.step_id for step in plan.steps]
    return {
        "summary": plan.summary,
        "steps_count": len(plan.steps),
        "step_ids": step_ids[:10],
        "required_tools": plan.required_tools,
        "approvals_count": len(plan.approvals),
        "estimated_cost": plan.estimated_cost.model_dump(mode="json"),
    }
