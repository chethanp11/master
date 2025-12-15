# ==============================
# Step Executor
# ==============================
from __future__ import annotations

from typing import Dict, Optional

from core.agents.registry import AgentRegistry
from core.contracts.agent_schema import AgentResult
from core.contracts.flow_schema import StepDef, StepType
from core.contracts.run_schema import StepStatus
from core.contracts.tool_schema import ToolResult
from core.orchestrator.context import RunContext, StepContext
from core.tools.executor import ToolExecutor


class StepExecutor:
    """
    Executes a single StepDef using registered agents/tools.
    """

    def __init__(
        self,
        *,
        tool_executor: ToolExecutor,
        agent_registry: AgentRegistry = AgentRegistry,
    ) -> None:
        self.tool_executor = tool_executor
        self.agent_registry = agent_registry

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
        result = self.tool_executor.execute(tool_name=step_def.tool, params=params, ctx=step_ctx)
        if not result.ok:
            raise RuntimeError(result.error.message if result.error else "tool_failed")
        return result


def build_step_context(run_ctx: RunContext, *, step_id: str, step_def: StepDef) -> StepContext:
    return run_ctx.new_step(
        step_id=step_id,
        step_type=step_def.type.value if isinstance(step_def.type, StepType) else str(step_def.type),
        backend=step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend,
        target=step_def.agent or step_def.tool,
    )
