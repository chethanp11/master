# ==============================
# Step Executor
# ==============================
from __future__ import annotations

import time
from typing import Callable, Dict, Optional

from core.agents.registry import AgentRegistry
from core.contracts.agent_schema import AgentResult
from core.governance.hooks import GovernanceHooks
from core.contracts.flow_schema import StepDef, StepType, RetryPolicy
from core.contracts.plan_schema import PlanProposal
from core.contracts.run_schema import StepStatus
from core.contracts.tool_schema import ToolResult
from core.orchestrator.context import RunContext, StepContext
from core.orchestrator.templating import render_params
from core.tools.executor import ToolExecutor
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
