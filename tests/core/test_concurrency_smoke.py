from __future__ import annotations

# ==============================
# Tests: Concurrency Smoke
# ==============================

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from core.agents.registry import AgentRegistry
from core.config.schema import Settings
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


class _RunIdTool(BaseTool):
    name = "run_id_tool"

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        meta = ToolMeta(tool_name=self.name, backend="local")
        payload = {"summary": ctx.run_id, "details": {"run_id": ctx.run_id, "marker": params.get("marker")}}
        return ToolResult.ok(data=payload, meta=meta)


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
                '  - id: "run_tool"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "run_id_tool"',
                "    params:",
                '      marker: "{{payload.marker}}"',
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
    settings = Settings()
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


def test_parallel_runs_isolated(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        ToolRegistry.register("run_id_tool", lambda: _RunIdTool())
        engine = _build_engine(tmp_path)

        def _run(marker: str):
            res = engine.run_flow(product="test_product", flow="test_flow", payload={"marker": marker})
            assert res.ok
            return res.data["run_id"], marker

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(_run, "a"), executor.submit(_run, "b")]
            results = [f.result() for f in futures]

        for run_id, marker in results:
            bundle = engine.memory.get_run(run_id)
            assert bundle is not None
            output = bundle.run.output or {}
            assert output.get("run_id") == run_id
            assert output.get("marker") == marker
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
