from __future__ import annotations

from pathlib import Path

from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.descriptors_schema import ToolDescriptor
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


class _CountingTool(BaseTool):
    def __init__(self, counter: dict, name: str) -> None:  # type: ignore[no-untyped-def]
        super().__init__(config=None)
        self.name = name
        self._counter = counter

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        self._counter[self.name] = self._counter.get(self.name, 0) + 1
        return {"ok": True, "data": {"name": self.name, "value": params.get("value")}}


def _write_flow(tmp_path: Path, *, parallel: bool) -> Path:
    flows_dir = tmp_path / "products" / "batch_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "batch_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "batch_flow"',
                'version: "1.0"',
                "steps:",
                '  - id: "batch"',
                '    type: "tool_batch"',
                f"    parallel: {str(parallel).lower()}",
                "    tools:",
                '      - tool_name: "tool_one"',
                "        inputs:",
                "          value: 1",
                '      - tool_name: "tool_two"',
                "        inputs:",
                "          value: 2",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return flow_path


def _write_reject_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "batch_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "reject_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "reject_flow"',
                'version: "1.0"',
                "steps:",
                '  - id: "batch"',
                '    type: "tool_batch"',
                "    tools:",
                '      - tool_name: "tool_ro"',
                "        inputs: {}",
                '      - tool_name: "tool_rw"',
                "        inputs: {}",
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


def test_tool_batch_rejects_non_read_only(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter: dict = {}
    try:
        flow_path = _write_reject_flow(tmp_path)
        ToolRegistry.register(
            "tool_ro",
            lambda: _CountingTool(counter, "tool_ro"),
            descriptor=ToolDescriptor(
                name="tool_ro",
                description="ro",
                tags=[],
                input_schema_ref=None,
                output_schema_ref=None,
                read_only=True,
                side_effect=False,
                sensitivity_class="LOW",
                cost_hint="LOW",
            ),
        )
        ToolRegistry.register(
            "tool_rw",
            lambda: _CountingTool(counter, "tool_rw"),
            descriptor=ToolDescriptor(
                name="tool_rw",
                description="rw",
                tags=[],
                input_schema_ref=None,
                output_schema_ref=None,
                read_only=False,
                side_effect=True,
                sensitivity_class="LOW",
                cost_hint="LOW",
            ),
        )
        engine = _build_engine(tmp_path, flow_path)

        started = engine.run_flow(product="batch_product", flow="reject_flow", payload={})
        assert started.ok, started.error
        assert started.data["status"] == RunStatus.FAILED.value
        assert counter == {}
        bundle = engine.memory.get_run(started.data["run_id"])
        assert bundle is not None
        events = [evt for evt in bundle.events if evt.kind == "tool_batch_rejected"]
        assert events
        assert events[-1].payload.get("tool") == "tool_rw"
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()


def test_tool_batch_deterministic_merge_order_parallel(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter: dict = {}
    try:
        flow_path = _write_flow(tmp_path, parallel=True)
        ToolRegistry.register(
            "tool_one",
            lambda: _CountingTool(counter, "tool_one"),
            descriptor=ToolDescriptor(
                name="tool_one",
                description="ro",
                tags=[],
                input_schema_ref=None,
                output_schema_ref=None,
                read_only=True,
                side_effect=False,
                sensitivity_class="LOW",
                cost_hint="LOW",
            ),
        )
        ToolRegistry.register(
            "tool_two",
            lambda: _CountingTool(counter, "tool_two"),
            descriptor=ToolDescriptor(
                name="tool_two",
                description="ro",
                tags=[],
                input_schema_ref=None,
                output_schema_ref=None,
                read_only=True,
                side_effect=False,
                sensitivity_class="LOW",
                cost_hint="LOW",
            ),
        )
        engine = _build_engine(tmp_path, flow_path)

        first = engine.run_flow(product="batch_product", flow="batch_flow", payload={})
        assert first.ok, first.error
        bundle = engine.memory.get_run(first.data["run_id"])
        assert bundle is not None
        step = next(step for step in bundle.steps if step.step_id == "batch")
        evidence_ids = [item.get("id") for item in step.output.get("evidence", [])]

        second = engine.run_flow(product="batch_product", flow="batch_flow", payload={})
        assert second.ok, second.error
        bundle_2 = engine.memory.get_run(second.data["run_id"])
        assert bundle_2 is not None
        step_2 = next(step for step in bundle_2.steps if step.step_id == "batch")
        evidence_ids_2 = [item.get("id") for item in step_2.output.get("evidence", [])]

        assert evidence_ids == evidence_ids_2
        assert counter.get("tool_one", 0) == 2
        assert counter.get("tool_two", 0) == 2
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()


def test_tool_batch_emits_per_tool_trace(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter: dict = {}
    try:
        flow_path = _write_flow(tmp_path, parallel=False)
        ToolRegistry.register(
            "tool_one",
            lambda: _CountingTool(counter, "tool_one"),
            descriptor=ToolDescriptor(
                name="tool_one",
                description="ro",
                tags=[],
                input_schema_ref=None,
                output_schema_ref=None,
                read_only=True,
                side_effect=False,
                sensitivity_class="LOW",
                cost_hint="LOW",
            ),
        )
        ToolRegistry.register(
            "tool_two",
            lambda: _CountingTool(counter, "tool_two"),
            descriptor=ToolDescriptor(
                name="tool_two",
                description="ro",
                tags=[],
                input_schema_ref=None,
                output_schema_ref=None,
                read_only=True,
                side_effect=False,
                sensitivity_class="LOW",
                cost_hint="LOW",
            ),
        )
        engine = _build_engine(tmp_path, flow_path)

        started = engine.run_flow(product="batch_product", flow="batch_flow", payload={})
        assert started.ok, started.error
        bundle = engine.memory.get_run(started.data["run_id"])
        assert bundle is not None
        kinds = [evt.kind for evt in bundle.events]
        assert "tool_batch_started" in kinds
        assert "tool_batch_completed" in kinds
        tool_calls_started = [evt for evt in bundle.events if evt.kind == "tool_call_started"]
        tool_calls_completed = [evt for evt in bundle.events if evt.kind == "tool_call_completed"]
        assert len(tool_calls_started) == 2
        assert len(tool_calls_completed) == 2
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()
