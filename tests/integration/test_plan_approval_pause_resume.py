from __future__ import annotations

# ==============================
# Integration: Plan Proposal Pause/Resume
# ==============================

from pathlib import Path

from core.agents.base import BaseAgent
from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.agent_schema import AgentMeta, AgentResult
from core.contracts.action_plan_schema import EstimatedCost, PlanProposal, PlanProposalStep as PlanStep
from core.contracts.run_schema import RunStatus, StepStatus
from core.contracts.tool_schema import ToolMeta, ToolResult
from core.governance.hooks import GovernanceHooks
from core.governance.security import SecurityRedactor
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.memory.tracing import Tracer
from core.orchestrator.engine import OrchestratorEngine
from core.orchestrator.flow_loader import FlowLoader
from core.orchestrator.step_executor import StepExecutor
from core.tools.base import BaseTool
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry


class _PlanAgent(BaseAgent):
    name = "test_plan_agent"

    def run(self, step_context):  # type: ignore[no-untyped-def]
        plan = PlanProposal(
            summary="Test plan proposal",
            steps=[PlanStep(step_id="echo", description="Echo tool", step_type="tool", tool="echo_tool")],
            required_tools=["echo_tool"],
            approvals=[],
            estimated_cost=EstimatedCost(currency="USD", amount=0.0, tokens=0, details={}),
        )
        meta = AgentMeta(agent_name=self.name)
        return AgentResult(ok=True, data=plan.model_dump(mode="json"), error=None, meta=meta)


class _EchoTool(BaseTool):
    name = "echo_tool"

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult(ok=True, data={"summary": "ok", "details": params}, error=None, meta=meta)


def _write_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "test_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "test_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "test_flow"',
                'version: "1.0.0"',
                "steps:",
                '  - id: "plan_proposal"',
                '    type: "plan_proposal"',
                '    backend: "local"',
                '    agent: "test_plan_agent"',
                "    params: {}",
                '  - id: "echo"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "echo_tool"',
                "    params:",
                '      text: "done"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return flow_path


def _build_engine(tmp_path: Path) -> OrchestratorEngine:
    flow_path = _write_flow(tmp_path)
    flow_loader = FlowLoader(products_root=flow_path.parents[2])
    memory = MemoryRouter(backend=InMemoryBackend(), repo_root=tmp_path, observability_root=tmp_path / "observability")
    tracer = Tracer(memory=memory, mirror_to_log=False)
    governance = GovernanceHooks(settings=Settings())
    tool_executor = ToolExecutor(registry=ToolRegistry, hooks=governance, redactor=SecurityRedactor())
    step_executor = StepExecutor(tool_executor=tool_executor, governance=governance, agent_registry=AgentRegistry)
    return OrchestratorEngine(
        flow_loader=flow_loader,
        step_executor=step_executor,
        memory=memory,
        tracer=tracer,
        governance=governance,
    )


def test_plan_proposal_pause_and_resume(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        AgentRegistry.register("test_plan_agent", lambda: _PlanAgent())
        ToolRegistry.register("echo_tool", lambda: _EchoTool())
        engine = _build_engine(tmp_path)

        started = engine.run_flow(product="test_product", flow="test_flow", payload={})
        assert started.ok, started.error
        assert started.data["status"] == RunStatus.PENDING_HUMAN.value
        run_id = started.data["run_id"]

        bundle = engine.memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.status == RunStatus.PENDING_HUMAN
        step = next(s for s in bundle.steps if s.step_id == "plan_proposal")
        assert step.status == StepStatus.PENDING_HUMAN

        resumed = engine.resume_run(
            run_id=run_id,
            approval_payload={"approved": True},
            decision="APPROVED",
        )
        assert resumed.ok, resumed.error
        assert resumed.data["status"] == RunStatus.COMPLETED.value

        bundle = engine.memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.status == RunStatus.COMPLETED
        step = next(s for s in bundle.steps if s.step_id == "plan_proposal")
        assert step.status == StepStatus.COMPLETED
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
