from __future__ import annotations

from pathlib import Path

from core.agents.advisory import (
    ToolSelectorAgent,
    AgentSelectorAgent,
    GapFinderAgent,
    SummarizerAgent,
    RiskExplainerAgent,
)
from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.flow_schema import StepDef, StepType
from core.governance.hooks import GovernanceHooks
from core.governance.security import SecurityRedactor
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.memory.tracing import Tracer
from core.orchestrator.context import RunContext
from core.orchestrator.engine import OrchestratorEngine
from core.orchestrator.flow_loader import FlowLoader
from core.orchestrator.step_executor import StepExecutor
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry


def _tool_selector_reasoner(payload):  # type: ignore[no-untyped-def]
    return {
        "recommended_tools": [
            {
                "tool_name": "echo_tool",
                "reason": "safe",
                "required_inputs": {},
                "expected_evidence_types": ["text"],
                "confidence": 0.9,
            }
        ],
        "rejected_tools": [],
        "assumptions": [],
        "unknowns": [],
    }


def _agent_selector_reasoner(payload):  # type: ignore[no-untyped-def]
    return {
        "recommended_agents": [{"agent_name": "simple_agent", "reason": "ok", "confidence": 0.7}],
        "rejected_agents": [],
        "assumptions": [],
        "unknowns": [],
    }


def _gap_finder_reasoner(payload):  # type: ignore[no-untyped-def]
    return {
        "missing_evidence": [],
        "missing_fields": [],
        "questions_for_user": [],
        "confidence": 0.6,
    }


def _summarizer_reasoner(payload):  # type: ignore[no-untyped-def]
    return {
        "summary": "summary",
        "key_points": ["one"],
        "evidence_refs": [],
    }


def _risk_reasoner(payload):  # type: ignore[no-untyped-def]
    return {
        "risk_factors": [
            {"factor": "risk", "rationale": "rationale", "evidence_refs": [], "severity": "LOW"}
        ],
        "mitigations": [],
        "confidence": 0.5,
        "assumptions": [],
        "unknowns": [],
    }


def test_advisory_agents_do_not_call_tools() -> None:
    tool_executor = ToolExecutor(registry=ToolRegistry)
    tool_executor.execute = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("tool called"))
    step_executor = StepExecutor(
        tool_executor=tool_executor,
        governance=GovernanceHooks(settings=Settings(), redactor=SecurityRedactor()),
        agent_registry=AgentRegistry,
    )

    agents = [
        ToolSelectorAgent(llm_reasoner=_tool_selector_reasoner),
        AgentSelectorAgent(llm_reasoner=_agent_selector_reasoner),
        GapFinderAgent(llm_reasoner=_gap_finder_reasoner),
        SummarizerAgent(llm_reasoner=_summarizer_reasoner),
        RiskExplainerAgent(llm_reasoner=_risk_reasoner),
    ]

    for idx, agent in enumerate(agents):
        AgentRegistry.register(agent.name, lambda a=agent: a, overwrite=True)
        run_ctx = RunContext(run_id=f"run_{idx}", product="test", flow="flow", payload={})
        step_def = StepDef(id=f"agent_{idx}", type=StepType.AGENT, agent=agent.name, params={"question": "q"})
        result = step_executor.execute(run_ctx=run_ctx, step_def=step_def, step_id=step_def.id)
        assert result.get("ok") is True


def _write_flow(tmp_path: Path) -> Path:
    flows_dir = tmp_path / "products" / "advisory_product" / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)
    flow_path = flows_dir / "advisory_flow.yaml"
    flow_path.write_text(
        "\n".join(
            [
                'id: "advisory_flow"',
                'version: "1.0"',
                "steps:",
                '  - id: "select"',
                '    type: "agent"',
                '    backend: "local"',
                '    agent: "tool_selector"',
                "    params:",
                '      question: "test"',
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


def test_tool_selector_does_not_execute_tools(tmp_path: Path) -> None:
    AgentRegistry.clear()
    try:
        AgentRegistry.register("tool_selector", lambda: ToolSelectorAgent(llm_reasoner=_tool_selector_reasoner), overwrite=True)
        flow_path = _write_flow(tmp_path)
        engine = _build_engine(tmp_path, flow_path)

        started = engine.run_flow(product="advisory_product", flow="advisory_flow", payload={})
        assert started.ok, started.error
        bundle = engine.memory.get_run(started.data["run_id"])
        assert bundle is not None
        tool_calls = [evt for evt in bundle.events if evt.kind.startswith("tool_call")]
        assert tool_calls == []
    finally:
        AgentRegistry.clear()
