from __future__ import annotations

from pathlib import Path

from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.context_pack_schema import ContextPack, DocumentsSummary, TablesSummary
from core.contracts.run_schema import RunStatus, StepStatus
from core.governance.hooks import GovernanceHooks
from core.governance.security import SecurityRedactor
from core.knowledge.context_pack import compute_context_pack_hash
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.memory.tracing import Tracer
from core.orchestrator.engine import OrchestratorEngine
from core.orchestrator.flow_loader import FlowLoader
from core.orchestrator.step_executor import StepExecutor
from core.tools.base import BaseTool
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry


class _ContextPackTool(BaseTool):
    name = "context_pack_tool"

    def __init__(self) -> None:  # type: ignore[no-untyped-def]
        super().__init__(config=None)

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        pack = ContextPack(
            question="What is needed?",
            evidence_index=[],
            tables_summary=TablesSummary(stats={}, key_rows=[], column_profiles={}),
            documents_summary=DocumentsSummary(excerpts=[], metadata=[]),
            assumptions=[],
            limits={},
        )
        packed = pack.model_dump(mode="json")
        packed["pack_hash"] = compute_context_pack_hash(pack)
        return packed


class _MarkerTool(BaseTool):
    name = "marker_tool"

    def __init__(self, counter: dict) -> None:  # type: ignore[no-untyped-def]
        super().__init__(config=None)
        self._counter = counter

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        self._counter["done"] = self._counter.get("done", 0) + 1
        return {"ok": True, "data": {"marker": "done"}}


def _write_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "question_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "question_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "question_flow"',
                'version: "1.0"',
                "steps:",
                '  - id: "prepare"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "context_pack_tool"',
                "    params: {}",
                '  - id: "question"',
                '    type: "user_input"',
                "    params:",
                "      question_set:",
                '        id: "qs1"',
                '        title: "Missing info"',
                "        questions:",
                '          - key: "customer_id"',
                '            prompt: "Provide customer id"',
                '            type: "string"',
                "            required: true",
                "        required_fields:",
                '          - "customer_id"',
                "        validation_schema: {}",
                '        guidance: "Fill required fields."',
                "        provenance:",
                '          created_from: "critic-output-1"',
                "          evidence_refs: []",
                '      context_pack_key: "tool.context_pack_tool.output"',
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


def test_invalid_user_input_does_not_resume(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter: dict = {}
    try:
        flow_path = _write_flow(tmp_path)
        ToolRegistry.register("context_pack_tool", lambda: _ContextPackTool())
        ToolRegistry.register("marker_tool", lambda: _MarkerTool(counter))
        engine = _build_engine(tmp_path, flow_path)

        started = engine.run_flow(product="question_product", flow="question_flow", payload={})
        assert started.ok, started.error
        assert started.data["status"] == RunStatus.PAUSED_WAITING_FOR_USER.value
        run_id = started.data["run_id"]

        resumed = engine.resume_run(
            run_id=run_id,
            user_input_response={"form_id": "qs1", "values": {}, "comment": ""},
        )
        assert not resumed.ok
        bundle = engine.memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.status == RunStatus.PAUSED_WAITING_FOR_USER
        pending = next(step for step in bundle.steps if step.step_id == "question")
        assert pending.status == StepStatus.PENDING_USER_INPUT
        events = [evt for evt in bundle.events if evt.kind == "user_input_validation_failed"]
        assert events
        assert events[-1].payload.get("question_set_id") == "qs1"
        assert counter.get("done") is None
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()


def test_user_input_merges_context_pack_deterministically(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter: dict = {}
    try:
        flow_path = _write_flow(tmp_path)
        ToolRegistry.register("context_pack_tool", lambda: _ContextPackTool())
        ToolRegistry.register("marker_tool", lambda: _MarkerTool(counter))
        engine = _build_engine(tmp_path, flow_path)

        first = engine.run_flow(product="question_product", flow="question_flow", payload={})
        assert first.ok, first.error
        run_id = first.data["run_id"]
        resumed = engine.resume_run(
            run_id=run_id,
            user_input_response={"form_id": "qs1", "values": {"customer_id": "123"}, "comment": ""},
        )
        assert resumed.ok, resumed.error
        assert resumed.data["status"] == RunStatus.COMPLETED.value

        bundle = engine.memory.get_run(run_id)
        assert bundle is not None
        step = next(step for step in bundle.steps if step.step_id == "question")
        merged_pack = step.output.get("context_pack")
        assert isinstance(merged_pack, dict)
        user_provided = merged_pack.get("user_provided", {})
        assert user_provided.get("question_set_id") == "qs1"
        assert user_provided.get("answers") == {"customer_id": "123"}

        second = engine.run_flow(product="question_product", flow="question_flow", payload={})
        assert second.ok, second.error
        run_id_2 = second.data["run_id"]
        resumed_2 = engine.resume_run(
            run_id=run_id_2,
            user_input_response={"form_id": "qs1", "values": {"customer_id": "123"}, "comment": ""},
        )
        assert resumed_2.ok, resumed_2.error
        bundle_2 = engine.memory.get_run(run_id_2)
        assert bundle_2 is not None
        step_2 = next(step for step in bundle_2.steps if step.step_id == "question")
        merged_pack_2 = step_2.output.get("context_pack")
        assert isinstance(merged_pack_2, dict)
        assert merged_pack.get("pack_hash") == merged_pack_2.get("pack_hash")
        assert counter.get("done") == 2
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()
