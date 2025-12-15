# ==============================
# Step Executor
# ==============================
from __future__ import annotations

import time
import re
from typing import Any, Callable, Dict, Optional

from core.agents.registry import AgentRegistry
from core.contracts.agent_schema import AgentResult
from core.contracts.flow_schema import StepDef, StepType, RetryPolicy
from core.contracts.run_schema import StepStatus
from core.contracts.tool_schema import ToolResult
from core.orchestrator.context import RunContext, StepContext
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
        agent_registry: AgentRegistry = AgentRegistry,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self.tool_executor = tool_executor
        self.agent_registry = agent_registry
        self.sleep_fn = sleep_fn

    def execute(
        self,
        *,
        run_ctx: RunContext,
        step_def: StepDef,
    ) -> Dict[str, Any]:
        step_ctx = run_ctx.new_step(
            step_def=step_def,
            step_id=step_def.id,
            step_type=step_def.type.value if isinstance(step_def.type, StepType) else str(step_def.type),
            backend=step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend,
            target=step_def.agent or step_def.tool,
        )

        if step_def.type == StepType.TOOL:
            rendered_params = self._render_params(step_def.params or {}, run_ctx.payload)
            step_def = step_def.model_copy(update={"params": rendered_params})
            return self._execute_tool(step_ctx=step_ctx, step_def=step_def).model_dump(mode="json")

        if step_def.type == StepType.AGENT:
            if not step_def.agent:
                raise ValueError("agent step missing 'agent' field")
            agent = self.agent_registry.resolve(step_def.agent)
            result: AgentResult = agent.run(step_ctx)
            if not result.ok:
                raise RuntimeError(result.error.message if result.error else "agent_failed")
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

    def _render_params(self, params: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        def render(value: Any) -> Any:
            if isinstance(value, str):
                def replace(match: re.Match[str]) -> str:
                    key = match.group(1)
                    return str(payload.get(key, ""))

                return re.sub(r"\{\{\s*payload\.([\w_]+)\s*\}\}", replace, value)
            if isinstance(value, dict):
                return {k: render(v) for k, v in value.items()}
            if isinstance(value, list):
                return [render(item) for item in value]
            return value

        return {k: render(v) for k, v in params.items()}


def build_step_context(run_ctx: RunContext, *, step_id: str, step_def: StepDef) -> StepContext:
    return run_ctx.new_step(
        step_id=step_id,
        step_type=step_def.type.value if isinstance(step_def.type, StepType) else str(step_def.type),
        backend=step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend,
        target=step_def.agent or step_def.tool,
    )
