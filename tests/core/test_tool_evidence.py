from __future__ import annotations

from typing import Any, Dict, List

from core.orchestrator.context import RunContext
from core.tools.base import BaseTool
from core.tools.executor import ToolExecutor
from core.tools.registry import ToolRegistry
from core.contracts.tool_schema import ToolResult, ToolMeta


class _EvidenceTool(BaseTool):
    name = "evidence_tool"
    description = "Tool used for evidence tests."

    def run(self, params: Dict[str, Any], ctx) -> ToolResult:  # type: ignore[override]
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult(ok=True, data={"payload": params}, error=None, meta=meta)


def _build_ctx(events: List[Dict[str, Any]]):
    run_ctx = RunContext(run_id="run_1", product="demo", flow="flow", payload={})

    def _trace(event_type: str, payload: Dict[str, Any]) -> None:
        events.append({"event_type": event_type, "payload": payload})

    run_ctx.trace = _trace
    return run_ctx.new_step(step_id="step_1", step_type="tool", backend="local", target="evidence_tool")


def test_tool_result_contains_evidence_and_artifact() -> None:
    ToolRegistry.clear()
    ToolRegistry.register("evidence_tool", lambda: _EvidenceTool())
    try:
        events: List[Dict[str, Any]] = []
        ctx = _build_ctx(events)
        executor = ToolExecutor(registry=ToolRegistry)

        result = executor.execute(tool_name="evidence_tool", params={"note": "hello"}, ctx=ctx)
        assert result.evidence
        evidence = result.evidence[0]
        assert evidence.id
        assert evidence.type
        assert evidence.timestamp
        assert evidence.content_ref
        assert evidence.content_ref.key in ctx.run.artifacts
    finally:
        ToolRegistry.clear()


def test_trace_includes_evidence_metadata() -> None:
    ToolRegistry.clear()
    ToolRegistry.register("evidence_tool", lambda: _EvidenceTool())
    try:
        events: List[Dict[str, Any]] = []
        ctx = _build_ctx(events)
        executor = ToolExecutor(registry=ToolRegistry)

        result = executor.execute(tool_name="evidence_tool", params={"note": "trace"}, ctx=ctx)
        tool_event = next((e for e in events if e["event_type"] == "tool.executed"), None)
        assert tool_event is not None
        produced = tool_event["payload"].get("produced_evidence")
        assert produced
        assert produced[0].get("id")
        assert produced[0]["source"]["tool"] == "evidence_tool"
    finally:
        ToolRegistry.clear()
