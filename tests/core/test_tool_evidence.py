from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from core.contracts.context_pack_schema import EvidenceItem, EvidenceSource, EvidenceType
from core.contracts.run_schema import ArtifactRef
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


def test_evidence_item_schema_validation() -> None:
    """Test EvidenceItem model validation with all required fields."""
    source = EvidenceSource(tool="test_tool", uri="memory://test", ref="test_ref")
    artifact_ref = ArtifactRef(key="test.key", kind="json", uri="memory://test")

    evidence = EvidenceItem(
        id="ev_001",
        type="table",
        source=source,
        timestamp=datetime.utcnow(),
        confidence=0.95,
        content_ref=artifact_ref,
        summary="Test evidence summary",
        provenance={"filter": "active"},
    )

    assert evidence.id == "ev_001"
    assert evidence.type == "table"
    assert evidence.confidence == 0.95
    assert evidence.provenance == {"filter": "active"}


def test_evidence_type_includes_metric() -> None:
    """Test that EvidenceType includes metric and chart types."""
    source = EvidenceSource(tool="metric_tool")
    artifact_ref = ArtifactRef(key="metric.key", kind="json", uri="memory://metric")

    # Test metric type
    metric_evidence = EvidenceItem(
        type="metric",
        source=source,
        content_ref=artifact_ref,
        summary="Metric evidence",
    )
    assert metric_evidence.type == "metric"

    # Test chart type
    chart_evidence = EvidenceItem(
        type="chart",
        source=source,
        content_ref=artifact_ref,
        summary="Chart evidence",
    )
    assert chart_evidence.type == "chart"

    # Test document type
    doc_evidence = EvidenceItem(
        type="document",
        source=source,
        content_ref=artifact_ref,
        summary="Document evidence",
    )
    assert doc_evidence.type == "document"


def test_evidence_confidence_bounds() -> None:
    """Test that evidence confidence is bounded between 0 and 1."""
    source = EvidenceSource(tool="test_tool")
    artifact_ref = ArtifactRef(key="test.key", kind="json", uri="memory://test")

    # Valid confidence values
    for conf in [0.0, 0.5, 1.0]:
        evidence = EvidenceItem(
            type="text",
            source=source,
            content_ref=artifact_ref,
            summary="Test",
            confidence=conf,
        )
        assert evidence.confidence == conf

    # Invalid confidence values should raise
    import pytest
    with pytest.raises(ValueError):
        EvidenceItem(
            type="text",
            source=source,
            content_ref=artifact_ref,
            summary="Test",
            confidence=1.5,
        )

    with pytest.raises(ValueError):
        EvidenceItem(
            type="text",
            source=source,
            content_ref=artifact_ref,
            summary="Test",
            confidence=-0.1,
        )


def test_tool_result_evidence_field() -> None:
    """Test that ToolResult has evidence field and handles empty evidence."""
    meta = ToolMeta(tool_name="test", backend="local")

    # Result without evidence
    result_no_evidence = ToolResult(ok=True, data={"key": "value"}, error=None, meta=meta)
    assert result_no_evidence.evidence == []

    # Result with evidence
    source = EvidenceSource(tool="test")
    artifact_ref = ArtifactRef(key="test.key", kind="json", uri="memory://test")
    evidence = EvidenceItem(
        type="text",
        source=source,
        content_ref=artifact_ref,
        summary="Evidence summary",
    )

    result_with_evidence = ToolResult(
        ok=True,
        data={"key": "value"},
        error=None,
        meta=meta,
        evidence=[evidence],
    )
    assert len(result_with_evidence.evidence) == 1
    assert result_with_evidence.evidence[0].summary == "Evidence summary"
