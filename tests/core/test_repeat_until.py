from __future__ import annotations

from pathlib import Path

from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.run_schema import RunStatus
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


class _ConfidenceTool(BaseTool):
    name = "confidence_tool"

    def __init__(self, counter: dict) -> None:  # type: ignore[no-untyped-def]
        super().__init__(config=None)
        self._counter = counter

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        self._counter["calls"] = self._counter.get("calls", 0) + 1
        return {"confidence": params.get("confidence", 0.4)}


class _MarkerTool(BaseTool):
    name = "marker_tool"

    def __init__(self, counter: dict) -> None:  # type: ignore[no-untyped-def]
        super().__init__(config=None)
        self._counter = counter

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        self._counter["marker_calls"] = self._counter.get("marker_calls", 0) + 1
        return {"marker": "done"}


def _write_loop_flow(tmp_path: Path, *, max_iters: int) -> Path:
    flows_dir = tmp_path / "products" / "loop_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "loop_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "loop_flow"',
                'version: "1.0"',
                "steps:",
                '  - id: "loop"',
                '    type: "repeat_until"',
                f"    max_iters: {max_iters}",
                "    stop_condition:",
                "      kind: confidence_threshold",
                "      path: artifacts.tool.confidence_tool.output.confidence",
                "      op: \">=\"",
                "      value: 0.9",
                "    iteration_step: iter",
                "    on_terminate: done",
                '  - id: "iter"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "confidence_tool"',
                "    params:",
                "      confidence: 0.4",
                '  - id: "done"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "marker_tool"',
                "    params: {}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return flow_path


def _build_engine(tmp_path: Path, flow_path: Path) -> OrchestratorEngine:
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


def test_repeat_until_max_iters(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter: dict = {}
    try:
        flow_path = _write_loop_flow(tmp_path, max_iters=3)
        ToolRegistry.register("confidence_tool", lambda: _ConfidenceTool(counter))
        ToolRegistry.register("marker_tool", lambda: _MarkerTool(counter))
        engine = _build_engine(tmp_path, flow_path)

        result = engine.run_flow(product="loop_product", flow="loop_flow", payload={})
        assert result.ok, result.error
        bundle = engine.memory.get_run(result.data["run_id"])
        assert bundle is not None
        assert counter.get("calls") == 3
        assert counter.get("marker_calls") == 1
        loop_state = bundle.run.summary.get("loops", {}).get("loop", {})
        assert loop_state.get("termination_reason") == "MAX_ITERS_REACHED"
        events = [evt for evt in bundle.events if evt.kind == "loop_iteration_started"]
        assert len(events) == 3
        terminated = [evt for evt in bundle.events if evt.kind == "loop_terminated"]
        assert terminated
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()


def test_repeat_until_respects_budget(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter: dict = {}
    try:
        flow_path = _write_loop_flow(tmp_path, max_iters=3)
        ToolRegistry.register("confidence_tool", lambda: _ConfidenceTool(counter))
        ToolRegistry.register("marker_tool", lambda: _MarkerTool(counter))
        engine = _build_engine(tmp_path, flow_path)
        budget_policy = {
            "defaults": {
                "max_passes": 1,
                "max_tool_calls": 10,
                "max_parallel_calls": 1,
                "max_total_cost_units": 10,
                "max_latency_bucket": "HIGH",
                "on_exceed": "FAIL",
                "degrade_to": None,
            },
            "overrides_by_sensitivity": {},
            "overrides_by_flow_type": {},
        }
        payload = {"_budget_policy": budget_policy, "_budget_sensitivity": "LOW"}
        result = engine.run_flow(product="loop_product", flow="loop_flow", payload=payload)
        assert result.ok, result.error
        assert result.data["status"] == RunStatus.FAILED.value
        bundle = engine.memory.get_run(result.data["run_id"])
        assert counter.get("calls") == 1
        assert bundle is not None
        loop_state = bundle.run.summary.get("loops", {}).get("loop", {})
        assert loop_state.get("termination_reason") == "BUDGET_EXCEEDED"
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()


def test_repeat_until_deterministic_termination(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    try:
        flow_path = _write_loop_flow(tmp_path, max_iters=2)
        ToolRegistry.register("confidence_tool", lambda: _ConfidenceTool({}))
        ToolRegistry.register("marker_tool", lambda: _MarkerTool({}))
        engine = _build_engine(tmp_path, flow_path)

        first = engine.run_flow(product="loop_product", flow="loop_flow", payload={})
        assert first.ok, first.error
        second = engine.run_flow(product="loop_product", flow="loop_flow", payload={})
        assert second.ok, second.error

        first_bundle = engine.memory.get_run(first.data["run_id"])
        second_bundle = engine.memory.get_run(second.data["run_id"])
        assert first_bundle is not None and second_bundle is not None
        first_loop = first_bundle.run.summary.get("loops", {}).get("loop", {})
        second_loop = second_bundle.run.summary.get("loops", {}).get("loop", {})
        assert first_loop.get("termination_reason") == second_loop.get("termination_reason")
        assert first_loop.get("iters_used") == second_loop.get("iters_used")
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()
