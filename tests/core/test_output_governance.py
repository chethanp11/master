# ==============================
# Tests: Output Governance Enforcement
# ==============================
from __future__ import annotations

from pathlib import Path

from core.agents.registry import AgentRegistry
from core.config.schema import PoliciesConfig, Settings
from core.contracts.run_schema import RunStatus
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


class _BigOutputTool(BaseTool):
    name = "big_output_tool"

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult.ok(data={"summary": "x" * 200, "details": {"ok": True}}, meta=meta)


class _OutputFilesTool(BaseTool):
    name = "output_files_tool"

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult.ok(
            data={
                "summary": "ok",
                "details": {"ok": True},
                "output_files": [{"name": "big.txt", "content_base64": "x" * 200}],
            },
            meta=meta,
        )


def _write_flow(tmp_path: Path, *, tool_name: str) -> Path:
    flows_dir = tmp_path / "products" / "test_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "test_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "test_flow"',
                'version: "1.0.0"',
                "steps:",
                '  - id: "run_tool"',
                '    type: "tool"',
                '    backend: "local"',
                f'    tool: "{tool_name}"',
                "    params: {}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return flow_path


def _build_engine(tmp_path: Path, *, settings: Settings, tool_name: str) -> OrchestratorEngine:
    flow_path = _write_flow(tmp_path, tool_name=tool_name)
    flow_loader = FlowLoader(products_root=flow_path.parents[2])
    memory = MemoryRouter(backend=InMemoryBackend())
    tracer = Tracer(memory=memory, mirror_to_log=False)
    governance = GovernanceHooks(settings=settings)
    tool_executor = ToolExecutor(registry=ToolRegistry, hooks=governance, redactor=SecurityRedactor())
    step_executor = StepExecutor(tool_executor=tool_executor, governance=governance, agent_registry=AgentRegistry)
    return OrchestratorEngine(
        flow_loader=flow_loader,
        step_executor=step_executor,
        memory=memory,
        tracer=tracer,
        governance=governance,
    )


def test_output_payload_limit_blocks_run(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        ToolRegistry.register("big_output_tool", lambda: _BigOutputTool())
        settings = Settings(policies=PoliciesConfig(max_payload_bytes=50))
        engine = _build_engine(tmp_path, settings=settings, tool_name="big_output_tool")

        res = engine.run_flow(product="test_product", flow="test_flow", payload={})
        assert res.ok
        assert res.data["status"] == RunStatus.FAILED.value
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()


def test_output_files_limit_blocks_run(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        ToolRegistry.register("output_files_tool", lambda: _OutputFilesTool())
        settings = Settings(policies=PoliciesConfig(max_payload_bytes=50))
        engine = _build_engine(tmp_path, settings=settings, tool_name="output_files_tool")

        res = engine.run_flow(product="test_product", flow="test_flow", payload={})
        assert res.ok
        assert res.data["status"] == RunStatus.FAILED.value
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
