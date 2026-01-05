from __future__ import annotations

import base64
import json
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


class _ReportTool(BaseTool):
    name = "report_tool"

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        content = "golden path report"
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult(
            ok=True,
            data={
                "summary": "ok",
                "details": params,
                "output_files": [
                    {
                        "name": "report.txt",
                        "content_type": "text/plain",
                        "role": "primary",
                        "content_base64": encoded,
                    }
                ],
            },
            error=None,
            meta=meta,
        )


def _write_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "test_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "spine_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "spine_flow"',
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
                "      required:",
                '        - "selection"',
                '  - id: "approval"',
                '    type: "human_approval"',
                '    message: "Proceed?"',
                '  - id: "report"',
                '    type: "tool"',
                '    backend: "local"',
                '    tool: "report_tool"',
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


def test_spine_golden_path(tmp_path: Path) -> None:
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        ToolRegistry.register("report_tool", lambda: _ReportTool())
        engine = _build_engine(tmp_path)

        started = engine.run_flow(product="test_product", flow="spine_flow", payload={})
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

        run_dir = tmp_path / "observability" / "test_product" / run_id
        assert (run_dir / "runtime" / "events.jsonl").exists()
        assert (run_dir / "output" / "response.json").exists()
        assert (run_dir / "output" / "reasoning.md").exists()
        assert (run_dir / "output" / "report.txt").exists()

        response = json.loads((run_dir / "output" / "response.json").read_text(encoding="utf-8"))
        file_names = {entry.get("stored_name") for entry in response.get("files") or []}
        assert "report.txt" in file_names
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
