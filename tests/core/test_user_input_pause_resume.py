# ==============================
# Tests: User Input Pause/Resume
# ==============================
from __future__ import annotations

from pathlib import Path

import pytest

from core.agents.registry import AgentRegistry
from core.config.schema import PoliciesConfig, Settings
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


class _EchoTool(BaseTool):
    name = "echo_tool"

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult.ok(data={"summary": "ok", "details": params}, meta=meta)


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
                '      input_type: "text"',
                '      mode: "free_text_input"',
                "      schema:",
                '        type: "object"',
                "        properties:",
                "          text:",
                '            type: "string"',
                "      required:",
                '        - "text"',
                '  - id: "echo"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "echo_tool"',
                "    params:",
                '      text: "{{artifacts.user_input.notes.values.text}}"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return flow_path


def _build_engine(tmp_path: Path, *, settings: Settings | None = None) -> OrchestratorEngine:
    flow_path = _write_flow(tmp_path)
    flow_loader = FlowLoader(products_root=flow_path.parents[2])
    memory = MemoryRouter(backend=InMemoryBackend())
    tracer = Tracer(memory=memory, mirror_to_log=False)
    settings = settings or Settings()
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


def test_user_input_pause_and_resume(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        ToolRegistry.register("echo_tool", lambda: _EchoTool())
        engine = _build_engine(tmp_path)

        started = engine.run_flow(product="test_product", flow="test_flow", payload={})
        assert started.ok, started.error
        assert started.data["status"] == RunStatus.PENDING_USER_INPUT.value
        run_id = started.data["run_id"]

        bundle = engine.memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.status == RunStatus.PENDING_USER_INPUT
        step = next(s for s in bundle.steps if s.step_id == "input")
        assert step.status == StepStatus.PENDING_USER_INPUT

        resumed = engine.resume_run(
            run_id=run_id,
            user_input_response={"form_id": "notes", "values": {"text": "hello"}},
        )
        assert resumed.ok, resumed.error
        assert resumed.data["status"] == RunStatus.COMPLETED.value

        bundle = engine.memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.status == RunStatus.COMPLETED
        step = next(s for s in bundle.steps if s.step_id == "input")
        assert step.status == StepStatus.COMPLETED
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()


def test_user_input_invalid_response_rejected(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        ToolRegistry.register("echo_tool", lambda: _EchoTool())
        engine = _build_engine(tmp_path)

        started = engine.run_flow(product="test_product", flow="test_flow", payload={})
        assert started.ok, started.error
        run_id = started.data["run_id"]

        rejected = engine.resume_run(
            run_id=run_id,
            user_input_response={"form_id": "notes", "values": {"text": ""}},
        )
        assert not rejected.ok
        assert rejected.error is not None
        assert rejected.error.code == "invalid_input"

        bundle = engine.memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.status == RunStatus.PENDING_USER_INPUT
        step = next(s for s in bundle.steps if s.step_id == "input")
        assert step.status == StepStatus.PENDING_USER_INPUT
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()


def test_user_input_payload_limit_blocked(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        ToolRegistry.register("echo_tool", lambda: _EchoTool())
        settings = Settings(policies=PoliciesConfig(max_payload_bytes=50))
        engine = _build_engine(tmp_path, settings=settings)

        started = engine.run_flow(product="test_product", flow="test_flow", payload={})
        assert started.ok, started.error
        run_id = started.data["run_id"]

        rejected = engine.resume_run(
            run_id=run_id,
            user_input_response={"form_id": "notes", "values": {"text": "x" * 200}},
        )
        assert not rejected.ok
        assert rejected.error is not None
        assert rejected.error.code == "policy_blocked"

        bundle = engine.memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.status == RunStatus.PENDING_USER_INPUT
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
