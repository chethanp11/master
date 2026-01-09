from __future__ import annotations

from pathlib import Path

from core.agents.registry import AgentRegistry
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


class _CountingTool(BaseTool):
    name = "count_tool"

    def __init__(self, counter) -> None:  # type: ignore[no-untyped-def]
        super().__init__(config=None)
        self._counter = counter

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        self._counter["calls"] += 1
        return {"ok": True, "data": {"echo": params}}


def _write_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "budget_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "budget_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "budget_flow"',
                'version: "1.0"',
                "steps:",
                '  - id: "first"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "count_tool"',
                "    params:",
                '      value: "one"',
                '  - id: "second"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "count_tool"',
                "    params:",
                '      value: "two"',
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
    governance = GovernanceHooks(settings=Settings(), redactor=SecurityRedactor())
    tool_executor = ToolExecutor(registry=ToolRegistry, hooks=governance, redactor=SecurityRedactor())
    step_executor = StepExecutor(tool_executor=tool_executor, governance=governance, agent_registry=AgentRegistry)
    return OrchestratorEngine(
        flow_loader=flow_loader,
        step_executor=step_executor,
        memory=memory,
        tracer=tracer,
        governance=governance,
    )


def test_budget_exceeded_stops_tool_calls(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter = {"calls": 0}
    try:
        ToolRegistry.register("count_tool", lambda: _CountingTool(counter))
        engine = _build_engine(tmp_path)
        budget_policy = {
            "defaults": {
                "max_passes": 3,
                "max_tool_calls": 1,
                "max_parallel_calls": 1,
                "max_total_cost_units": 5,
                "max_latency_bucket": "HIGH",
                "on_exceed": "FAIL",
                "degrade_to": None,
            },
            "overrides_by_sensitivity": {},
            "overrides_by_flow_type": {},
        }
        payload = {
            "_budget_policy": budget_policy,
            "_budget_sensitivity": "LOW",
        }
        started = engine.run_flow(product="budget_product", flow="budget_flow", payload=payload)
        assert started.ok
        bundle = engine.memory.get_run(started.data["run_id"])
        assert bundle is not None
        assert counter["calls"] == 1
        exceeded = [e for e in bundle.events if e.kind == "budget_exceeded"]
        assert exceeded
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()
