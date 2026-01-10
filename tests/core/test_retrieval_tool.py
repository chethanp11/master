from __future__ import annotations

from typing import Any, Dict, List

from core.config.schema import Settings
from core.contracts.run_schema import RunRecord, TraceEvent
from core.governance.hooks import GovernanceHooks
from core.governance.security import SecurityRedactor
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.orchestrator.context import RunContext
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry
from core.tools.retrieval import register_retrieval_tool


def _build_tool_executor(settings: Settings, memory: MemoryRouter) -> ToolExecutor:
    governance = GovernanceHooks(settings=settings, redactor=SecurityRedactor())
    return ToolExecutor(registry=ToolRegistry, hooks=governance, redactor=SecurityRedactor())


def test_retrieval_blocks_disallowed_sources() -> None:
    ToolRegistry.clear()
    memory = MemoryRouter(backend=InMemoryBackend())
    settings = Settings()
    settings.policies.by_product["retrieval_product"] = {"retrieval_allowed_sources": ["run_records"]}
    register_retrieval_tool(memory=memory, settings=settings)
    tool_executor = _build_tool_executor(settings, memory)

    trace_events: List[Dict[str, Any]] = []
    run_ctx = RunContext(run_id="run_retrieval_1", product="retrieval_product", flow="flow_a", payload={})
    run_ctx.trace = lambda kind, payload: trace_events.append({"kind": kind, "payload": payload})
    step_ctx = run_ctx.new_step(step_id="retrieve", step_type="tool", backend="local", target="approved_retrieval")

    result = tool_executor.execute(
        tool_name="approved_retrieval",
        params={"query": "alpha", "top_k": 3, "sources_requested": ["run_records", "trace_events"]},
        ctx=step_ctx,
    )

    assert not result.ok
    assert result.error is not None
    assert result.error.code.value == "permission_denied"
    assert result.evidence == []
    applied = [evt for evt in trace_events if evt["kind"] == "retrieval_policy_applied"]
    assert applied
    assert "trace_events" in applied[-1]["payload"].get("denied_sources", [])


def test_retrieval_provenance_and_artifacts() -> None:
    ToolRegistry.clear()
    memory = MemoryRouter(backend=InMemoryBackend())
    settings = Settings()
    settings.policies.by_product["retrieval_product"] = {"retrieval_allowed_sources": ["run_records", "trace_events"]}
    register_retrieval_tool(memory=memory, settings=settings)
    tool_executor = _build_tool_executor(settings, memory)

    run_record = RunRecord(
        run_id="run_alpha",
        product="retrieval_product",
        flow="flow_a",
        status="COMPLETED",
        input={"note": "alpha record"},
        output={"summary": "alpha output"},
        summary={"info": "alpha summary"},
    )
    memory.create_run(run_record)
    event = TraceEvent(
        run_id="run_alpha",
        step_id="step1",
        product="retrieval_product",
        flow="flow_a",
        kind="custom_event",
        payload={"message": "alpha trace"},
    )
    memory.add_event(event)

    trace_events: List[Dict[str, Any]] = []
    run_ctx = RunContext(run_id="run_retrieval_2", product="retrieval_product", flow="flow_a", payload={})
    run_ctx.trace = lambda kind, payload: trace_events.append({"kind": kind, "payload": payload})
    step_ctx = run_ctx.new_step(step_id="retrieve", step_type="tool", backend="local", target="approved_retrieval")

    result = tool_executor.execute(
        tool_name="approved_retrieval",
        params={"query": "alpha", "top_k": 5, "sources_requested": ["run_records", "trace_events"]},
        ctx=step_ctx,
    )

    assert result.ok, result.error
    assert result.evidence
    data = result.data or {}
    citations = data.get("citations", [])
    assert citations
    for item in result.evidence:
        assert item.provenance.get("source_type")
        assert item.provenance.get("run_id")
        assert item.content_ref is not None
        assert item.content_ref.key in run_ctx.artifacts
        assert item.summary
