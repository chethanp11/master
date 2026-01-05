from __future__ import annotations

from pathlib import Path

from core.agents.registry import AgentRegistry
from core.contracts.run_schema import RunStatus
from core.contracts.tool_schema import ToolMeta, ToolResult
from core.config.schema import Settings
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


class _EchoTool(BaseTool):
    name = "echo_tool"

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult(ok=True, data={"summary": "ok", "details": params}, error=None, meta=meta)


def _write_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "test_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "hitl_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "hitl_flow"',
                'version: "1.0.0"',
                "steps:",
                '  - id: "input"',
                '    type: "user_input"',
                "    params:",
                '      schema_version: "1.0"',
                '      form_id: "metric"',
                '      prompt: "Choose metric"',
                '      input_type: "select"',
                '      mode: "choice_input"',
                "      schema:",
                '        type: "object"',
                "        properties:",
                "          selection:",
                '            type: "string"',
                "            enum:",
                '              - "mean"',
                '              - "sum"',
                "      required:",
                '        - "selection"',
                '  - id: "approval"',
                '    type: "human_approval"',
                '    message: "Proceed with selected metric?"',
                '  - id: "echo"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "echo_tool"',
                "    params:",
                '      metric: "{{artifacts.user_input.metric.values.selection}}"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return flow_path


def _build_engine(tmp_path: Path) -> OrchestratorEngine:
    flow_path = _write_flow(tmp_path)
    flow_loader = FlowLoader(products_root=flow_path.parents[2])
    memory = MemoryRouter(backend=InMemoryBackend())
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


def test_hitl_pause_resume_order(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        ToolRegistry.register("echo_tool", lambda: _EchoTool())
        engine = _build_engine(tmp_path)

        started = engine.run_flow(product="test_product", flow="hitl_flow", payload={})
        assert started.ok, started.error
        assert started.data["status"] == RunStatus.PAUSED_WAITING_FOR_USER.value
        run_id = started.data["run_id"]

        after_input = engine.resume_run(
            run_id=run_id,
            user_input_response={"form_id": "metric", "values": {"selection": "mean"}},
        )
        assert after_input.ok, after_input.error
        assert after_input.data["status"] == RunStatus.PENDING_HUMAN.value

        after_approval = engine.resume_run(run_id=run_id, approval_payload={"approved": True}, decision="APPROVED")
        assert after_approval.ok, after_approval.error
        assert after_approval.data["status"] == RunStatus.COMPLETED.value
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
