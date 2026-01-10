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


class _ScoreTool(BaseTool):
    name = "score_tool"

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        return {"confidence": params.get("confidence", 0.4)}


class _MarkerTool(BaseTool):
    name = "marker_tool"

    def __init__(self, marker: str, counter: dict) -> None:  # type: ignore[no-untyped-def]
        super().__init__(config=None)
        self._marker = marker
        self._counter = counter

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        self._counter[self._marker] = self._counter.get(self._marker, 0) + 1
        return {"marker": self._marker}


def _write_branch_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "branch_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "branch_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "branch_flow"',
                'version: "1.0"',
                "steps:",
                '  - id: "score"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "score_tool"',
                "    params:",
                "      confidence: 0.4",
                '  - id: "branch"',
                '    type: "branch"',
                "    when:",
                "      path: steps.score.output.data.confidence",
                "      op: \">=\"",
                "      value: 0.5",
                "    then: high",
                "    else: low",
                '  - id: "high"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "high_tool"',
                "    params: {}",
                '  - id: "low"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "low_tool"',
                "    params: {}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return flow_path


def _write_invalid_branch_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "invalid_branch_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "invalid_branch_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "invalid_branch_flow"',
                'version: "1.0"',
                "steps:",
                '  - id: "input_step"',
                '    type: "user_input"',
                "    params:",
                "      form_id: \"input_form\"",
                "      prompt: \"Provide input\"",
                "      mode: free_text_input",
                "      required: []",
                '  - id: "branch"',
                '    type: "branch"',
                "    when:",
                "      path: steps.input_step.output.raw_text",
                "      op: exists",
                "    then: done",
                "    else: done",
                '  - id: "done"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "score_tool"',
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


def test_branch_repeatable_and_traced(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter: dict = {}
    try:
        flow_path = _write_branch_flow(tmp_path)
        ToolRegistry.register("score_tool", lambda: _ScoreTool())
        ToolRegistry.register("high_tool", lambda: _MarkerTool("HIGH", counter))
        ToolRegistry.register("low_tool", lambda: _MarkerTool("LOW", counter))
        engine = _build_engine(tmp_path, flow_path)

        first = engine.run_flow(product="branch_product", flow="branch_flow", payload={})
        assert first.ok, first.error
        bundle = engine.memory.get_run(first.data["run_id"])
        assert bundle is not None
        assert counter.get("HIGH", 0) == 0
        assert counter.get("LOW", 0) == 1
        events = [evt for evt in bundle.events if evt.kind == "branch_evaluated"]
        assert events
        chosen = events[-1].payload.get("chosen_next_step")
        assert chosen == "low"

        counter.clear()
        second = engine.run_flow(product="branch_product", flow="branch_flow", payload={})
        assert second.ok, second.error
        bundle = engine.memory.get_run(second.data["run_id"])
        assert bundle is not None
        assert counter.get("HIGH", 0) == 0
        assert counter.get("LOW", 0) == 1
        events = [evt for evt in bundle.events if evt.kind == "branch_evaluated"]
        assert events
        assert events[-1].payload.get("chosen_next_step") == "low"
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()


def test_branch_rejects_raw_text_reference(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    try:
        flow_path = _write_invalid_branch_flow(tmp_path)
        ToolRegistry.register("score_tool", lambda: _ScoreTool())
        engine = _build_engine(tmp_path, flow_path)

        result = engine.run_flow(product="invalid_branch_product", flow="invalid_branch_flow", payload={})
        assert not result.ok
        assert result.error
        assert "branch_condition" in result.error.message
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()
