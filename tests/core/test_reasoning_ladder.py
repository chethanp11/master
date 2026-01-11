from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.agents.reasoning_ladder import run_reasoning_ladder
from core.contracts.context_pack_schema import ContextPackConfig, EvidenceItem, EvidenceSource
from core.contracts.reasoning_ladder_schema import ReasoningLadderConfig
from core.contracts.run_schema import ArtifactRef
from core.knowledge.context_pack import build_context_pack


class _StubReasoner:
    def __init__(self, *, invalid_pass: Optional[str] = None) -> None:
        self.invalid_pass = invalid_pass

    def __call__(self, pass_name: str, payload: Dict[str, Any]) -> str:
        if self.invalid_pass == pass_name:
            return "not-json"
        if pass_name == "interpret":
            return json.dumps({"intent": "summarize", "entities": [{"name": "alpha"}], "constraints": ["no tools"]})
        if pass_name == "propose":
            return json.dumps(
                {
                    "candidates": [
                        {"id": "c1", "title": "First", "description": "First option"},
                        {"id": "c2", "title": "Second", "description": "Second option"},
                    ],
                    "tool_candidates": [
                        {"tool": "echo_tool", "rationale": "safe", "required_inputs": ["message"], "confidence": 0.9},
                        {"tool": "report_tool", "rationale": "report", "required_inputs": ["query"], "confidence": 0.7},
                    ],
                    "agent_candidates": [
                        {"agent": "simple_agent", "rationale": "summarize", "confidence": 0.6},
                        {"agent": "llm_reasoner", "rationale": "explain", "confidence": 0.5},
                    ],
                }
            )
        if pass_name == "select":
            return json.dumps(
                {
                    "select": {"chosen": {"id": "c1"}, "rationale": "best", "evidence_refs": ["evidence-text-1"]},
                    "confidence": 0.7,
                    "assumptions": ["inputs stable"],
                    "unknowns": ["none"],
                }
            )
        return json.dumps({})


def _build_context_pack() -> Tuple[Any, Dict[str, Any]]:
    artifacts: Dict[str, Any] = {}
    table_key = "artifact.table"
    text_key = "artifact.text"
    artifacts[table_key] = [
        {"id": 2, "name": "beta", "score": 10.5},
        {"id": 1, "name": "alpha", "score": 8.0},
    ]
    artifacts[text_key] = {"text": "Deterministic text evidence."}

    table_ref = ArtifactRef(key=table_key, kind="json", uri=f"memory://{table_key}")
    text_ref = ArtifactRef(key=text_key, kind="text", uri=f"memory://{text_key}")

    now = datetime(2024, 1, 1)
    evidence = [
        EvidenceItem(
            id="evidence-table-1",
            type="table",
            source=EvidenceSource(tool="table_tool", ref="r1"),
            timestamp=now,
            confidence=0.9,
            content_ref=table_ref,
            summary="table summary",
            provenance={},
        ),
        EvidenceItem(
            id="evidence-text-1",
            type="text",
            source=EvidenceSource(tool="text_tool", ref="r2"),
            timestamp=now,
            confidence=0.8,
            content_ref=text_ref,
            summary="text summary",
            provenance={},
        ),
    ]
    config = ContextPackConfig(table_row_limit=1, excerpt_char_limit=40, artifacts=artifacts)
    pack = build_context_pack(evidence, question="What happened?", config=config)
    return pack, artifacts


def test_reasoning_ladder_respects_budgets() -> None:
    pack, _ = _build_context_pack()
    trace_events: List[Dict[str, Any]] = []

    def _trace(event_type: str, payload: Dict[str, Any]) -> None:
        trace_events.append({"event_type": event_type, "payload": payload})

    config = ReasoningLadderConfig(
        max_passes=3,
        max_candidates=1,
        max_tool_candidates=1,
        max_agent_candidates=1,
    )
    result = run_reasoning_ladder(
        context_pack=pack,
        question="What happened?",
        config=config,
        llm_reasoner=_StubReasoner(),
        trace=_trace,
    )

    assert result.ok
    assert result.output is not None
    assert len(result.output.propose.candidates) <= 1
    assert len(result.output.propose.tool_candidates) <= 1
    assert len(result.output.propose.agent_candidates) <= 1

    started = [e for e in trace_events if e["event_type"] == "reasoning_ladder_pass_started"]
    assert len(started) == 3


def test_reasoning_ladder_failure_is_safe() -> None:
    pack, _ = _build_context_pack()
    trace_events: List[Dict[str, Any]] = []

    def _trace(event_type: str, payload: Dict[str, Any]) -> None:
        trace_events.append({"event_type": event_type, "payload": payload})

    config = ReasoningLadderConfig(
        max_passes=3,
        max_candidates=1,
        max_tool_candidates=1,
        max_agent_candidates=1,
    )
    result = run_reasoning_ladder(
        context_pack=pack,
        question="What happened?",
        config=config,
        llm_reasoner=_StubReasoner(invalid_pass="propose"),
        trace=_trace,
    )

    assert not result.ok
    assert result.error is not None
    assert result.error.failed_pass == "propose"

    failed = [e for e in trace_events if e["event_type"] == "reasoning_ladder_pass_failed"]
    assert failed
    started = [e for e in trace_events if e["event_type"] == "reasoning_ladder_pass_started"]
    assert [e["payload"]["pass_name"] for e in started] == ["interpret", "propose"]
