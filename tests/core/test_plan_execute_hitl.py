from __future__ import annotations

from pathlib import Path

from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.descriptors_schema import ToolDescriptor
from core.contracts.run_schema import RunStatus, StepStatus
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


class _SideEffectTool(BaseTool):
    name = "side_effect_tool"

    def __init__(self, counter) -> None:  # type: ignore[no-untyped-def]
        super().__init__(config=None)
        self._counter = counter

    def run(self, params, ctx):  # type: ignore[no-untyped-def]
        self._counter["calls"] += 1
        return {"ok": True, "data": {"echo": params}}


def _write_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "plan_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "plan_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "plan_flow"',
                'version: "1.0"',
                "steps:",
                '  - id: "propose"',
                '    type: "plan_propose"',
                "    params:",
                "      plan:",
                '        id: "plan1"',
                '        goal: "side effect"',
                "        steps:",
                '          - kind: "tool"',
                '            tool_name: "side_effect_tool"',
                "            inputs:",
                '              value: "x"',
                "            expected_evidence_types: []",
                "        required_inputs: []",
                "        expected_evidence: []",
                "        assumptions: []",
                "        confidence: 0.6",
                '  - id: "gate"',
                '    type: "plan_gate"',
                "    allow_tools:",
                '      - "side_effect_tool"',
                '  - id: "execute"',
                '    type: "plan_execute"',
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


def test_plan_execute_pauses_for_hitl_and_executes_after_approval(tmp_path: Path) -> None:
    ToolRegistry.clear()
    AgentRegistry.clear()
    counter = {"calls": 0}
    try:
        ToolRegistry.register(
            "side_effect_tool",
            lambda: _SideEffectTool(counter),
            descriptor=ToolDescriptor(
                name="side_effect_tool",
                description="side effect",
                tags=[],
                input_schema_ref=None,
                output_schema_ref=None,
                read_only=False,
                side_effect=True,
                sensitivity_class="LOW",
                cost_hint="LOW",
            ),
        )
        engine = _build_engine(tmp_path)

        started = engine.run_flow(product="plan_product", flow="plan_flow", payload={})
        assert started.ok, started.error
        assert started.data["status"] == RunStatus.PENDING_HUMAN.value
        assert counter["calls"] == 0

        bundle = engine.memory.get_run(started.data["run_id"])
        assert bundle is not None
        assert bundle.run.status == RunStatus.PENDING_HUMAN
        step = next(s for s in bundle.steps if s.step_id == "execute")
        assert step.status == StepStatus.PENDING_HUMAN

        resumed = engine.resume_run(
            run_id=started.data["run_id"],
            approval_payload={"approved": True},
            decision="APPROVED",
        )
        assert resumed.ok, resumed.error
        assert resumed.data["status"] == RunStatus.COMPLETED.value
        assert counter["calls"] == 1
    finally:
        ToolRegistry.clear()
        AgentRegistry.clear()
