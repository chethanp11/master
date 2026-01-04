from __future__ import annotations

# ==============================
# Integration: Observability Artifacts
# ==============================

import json
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
                '  - id: "input"',
                '    type: "user_input"',
                "    params:",
                '      schema_version: "1.0"',
                '      form_id: "notes"',
                '      prompt: "Notes"',
                '      input_type: "select"',
                '      mode: "choice_input"',
                "      schema:",
                '        type: "object"',
                "        properties:",
                "          selection:",
                '            type: "string"',
                "            enum:",
                '              - "alpha"',
                '              - "beta"',
                "      required:",
                '        - "selection"',
                '  - id: "echo"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "echo_tool"',
                "    params:",
                '      text: "{{artifacts.user_input.notes.values.selection}}"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return flow_path


def _build_engine(tmp_path: Path) -> OrchestratorEngine:
    flow_path = _write_flow(tmp_path)
    flow_loader = FlowLoader(products_root=flow_path.parents[2])
    observability_root = tmp_path / "observability"
    memory = MemoryRouter(backend=InMemoryBackend(), repo_root=tmp_path, observability_root=observability_root)
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


def test_observability_artifacts_written(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        ToolRegistry.register("echo_tool", lambda: _EchoTool())
        engine = _build_engine(tmp_path)

        started = engine.run_flow(product="test_product", flow="test_flow", payload={})
        assert started.ok, started.error
        run_id = started.data["run_id"]

        run_dir = tmp_path / "observability" / "test_product" / run_id
        input_dir = run_dir / "input"
        runtime_dir = run_dir / "runtime"
        output_dir = run_dir / "output"

        assert input_dir.exists()
        assert (input_dir / "input.json").exists()
        assert runtime_dir.exists()
        assert (runtime_dir / "events.jsonl").exists()
        assert output_dir.exists()
        assert (output_dir / "response.json").exists()

        response = json.loads((output_dir / "response.json").read_text(encoding="utf-8"))
        assert response.get("status") == "PAUSED_WAITING_FOR_USER"

        events_text = (runtime_dir / "events.jsonl").read_text(encoding="utf-8")
        assert "pending_user_input" in events_text
        assert "run_paused" in events_text

        resumed = engine.resume_run(
            run_id=run_id,
            user_input_response={"prompt_id": "notes", "selected_option_ids": ["alpha"]},
        )
        assert resumed.ok, resumed.error

        response = json.loads((output_dir / "response.json").read_text(encoding="utf-8"))
        assert response.get("status") == "COMPLETED"
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
