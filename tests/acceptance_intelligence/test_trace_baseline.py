"""
Phase 0: Trace Baseline Tests

These tests lock in trace behavior that MUST hold before and after refactoring.
They verify that every tool call, model call is traced, and that traces contain
required fields for auditability.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest

from core.contracts.run_schema import RunStatus
from core.models.providers.openai_provider import OpenAIProvider, OpenAIResponse
from tests.acceptance_intelligence import helpers


def _get_events_by_kind(events: List[Any], kind: str) -> List[Any]:
    """Filter events by kind."""
    return [e for e in events if e.kind == kind]


def _get_events_matching(events: List[Any], kinds: List[str]) -> List[Any]:
    """Get events matching any of the given kinds."""
    return [e for e in events if e.kind in kinds]


class TestEveryToolCallTraced:
    """Verify that every tool call emits trace events."""

    def test_single_tool_call_traced(self, tmp_path: Path) -> None:
        """A single tool call should emit start and success/failure events."""
        helpers.build_product(
            tmp_path,
            product_name="tool_trace_test",
            flows={
                "tool_flow": """
                name: tool_flow
                version: "1.0"
                steps:
                  - id: echo
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "trace_test"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="tool_trace_test")

        result = engine.run_flow(product="tool_trace_test", flow="tool_flow", payload={})
        assert result.ok
        assert result.data["status"] == RunStatus.COMPLETED.value

        bundle = engine.memory.get_run(result.data["run_id"])
        events = bundle.events

        # Should have tool call attempt started
        tool_start_events = _get_events_by_kind(events, "tool_call_attempt_started")
        assert len(tool_start_events) >= 1, "Expected tool_call_attempt_started event"

        # Should have tool call succeeded (or failed)
        tool_end_events = _get_events_matching(events, ["tool_call_succeeded", "tool_call_failed"])
        assert len(tool_end_events) >= 1, "Expected tool_call_succeeded or tool_call_failed event"

    def test_multiple_tool_calls_each_traced(self, tmp_path: Path) -> None:
        """Each tool call in a multi-tool flow should be traced separately."""
        helpers.build_product(
            tmp_path,
            product_name="multi_tool_trace_test",
            flows={
                "multi_tool_flow": """
                name: multi_tool_flow
                version: "1.0"
                steps:
                  - id: tool_one
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "first"
                  - id: tool_two
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "second"
                  - id: tool_three
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "third"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="multi_tool_trace_test")

        result = engine.run_flow(product="multi_tool_trace_test", flow="multi_tool_flow", payload={})
        assert result.ok

        bundle = engine.memory.get_run(result.data["run_id"])
        events = bundle.events

        tool_start_events = _get_events_by_kind(events, "tool_call_attempt_started")
        tool_success_events = _get_events_by_kind(events, "tool_call_succeeded")

        # Should have 3 tool calls traced
        assert len(tool_start_events) >= 3, f"Expected 3 tool_call_attempt_started events, got {len(tool_start_events)}"
        assert len(tool_success_events) >= 3, f"Expected 3 tool_call_succeeded events, got {len(tool_success_events)}"

    def test_tool_call_trace_includes_tool_name(self, tmp_path: Path) -> None:
        """Tool call trace events should include the tool name."""
        helpers.build_product(
            tmp_path,
            product_name="tool_name_trace_test",
            flows={
                "tool_name_flow": """
                name: tool_name_flow
                version: "1.0"
                steps:
                  - id: echo_step
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "named"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="tool_name_trace_test")

        result = engine.run_flow(product="tool_name_trace_test", flow="tool_name_flow", payload={})
        assert result.ok

        bundle = engine.memory.get_run(result.data["run_id"])
        tool_events = _get_events_by_kind(bundle.events, "tool_call_attempt_started")

        assert len(tool_events) >= 1
        # At least one should have tool name in payload
        tool_names_found = [e.payload.get("tool") or e.payload.get("tool_name") for e in tool_events]
        assert any(name for name in tool_names_found), "Expected tool name in trace payload"


class TestEveryModelCallTraced:
    """Verify that every model/LLM call emits trace events."""

    def test_model_call_traced(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """An LLM/model call should emit start and success events."""
        helpers.build_product(
            tmp_path,
            product_name="model_trace_test",
            flows={
                "model_flow": """
                name: model_flow
                version: "1.0"
                steps:
                  - id: reason
                    type: agent
                    backend: local
                    agent: llm_reasoner
                    params:
                      purpose: INSIGHT
                      prompt: "Test prompt"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="model_trace_test")

        # Stub model provider
        def _stub_complete(self, request):
            return OpenAIResponse(
                ok=True,
                model=request.model,
                content="stubbed response",
                usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                meta={"provider": "test"},
            )

        monkeypatch.setattr(OpenAIProvider, "complete", _stub_complete)

        result = engine.run_flow(product="model_trace_test", flow="model_flow", payload={})
        assert result.ok

        bundle = engine.memory.get_run(result.data["run_id"])
        events = bundle.events

        # Should have model call started
        model_start = _get_events_by_kind(events, "model_call_attempt_started")
        assert len(model_start) >= 1, "Expected model_call_attempt_started event"

        # Should have model call succeeded
        model_success = _get_events_by_kind(events, "model_call_succeeded")
        assert len(model_success) >= 1, "Expected model_call_succeeded event"

    def test_model_call_trace_includes_model_name(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Model call trace should include the model name."""
        helpers.build_product(
            tmp_path,
            product_name="model_name_trace_test",
            flows={
                "model_name_flow": """
                name: model_name_flow
                version: "1.0"
                steps:
                  - id: reason
                    type: agent
                    backend: local
                    agent: llm_reasoner
                    params:
                      purpose: INSIGHT
                      prompt: "Model name test"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="model_name_trace_test")

        def _stub_complete(self, request):
            return OpenAIResponse(
                ok=True,
                model=request.model,
                content="stubbed",
                usage={"total_tokens": 1},
                meta={"provider": "test"},
            )

        monkeypatch.setattr(OpenAIProvider, "complete", _stub_complete)

        result = engine.run_flow(product="model_name_trace_test", flow="model_name_flow", payload={})
        assert result.ok

        bundle = engine.memory.get_run(result.data["run_id"])
        model_events = _get_events_matching(
            bundle.events, ["model_call_attempt_started", "model_call_succeeded"]
        )

        # At least one should have model name
        model_names = [e.payload.get("model") for e in model_events]
        assert any(name for name in model_names), "Expected model name in trace payload"


class TestTraceContainsRequiredFields:
    """Verify that trace events contain all required fields for auditability."""

    def test_trace_event_has_run_id(self, tmp_path: Path) -> None:
        """Every trace event should have a run_id."""
        helpers.build_product(
            tmp_path,
            product_name="run_id_trace_test",
            flows={
                "simple_flow": """
                name: simple_flow
                version: "1.0"
                steps:
                  - id: echo
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "test"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="run_id_trace_test")

        result = engine.run_flow(product="run_id_trace_test", flow="simple_flow", payload={})
        run_id = result.data["run_id"]

        bundle = engine.memory.get_run(run_id)

        for event in bundle.events:
            assert event.run_id == run_id, f"Event {event.kind} missing or wrong run_id"

    def test_step_events_have_step_id(self, tmp_path: Path) -> None:
        """Step-related events should have a step_id."""
        helpers.build_product(
            tmp_path,
            product_name="step_id_trace_test",
            flows={
                "step_flow": """
                name: step_flow
                version: "1.0"
                steps:
                  - id: my_step
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "step"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="step_id_trace_test")

        result = engine.run_flow(product="step_id_trace_test", flow="step_flow", payload={})

        bundle = engine.memory.get_run(result.data["run_id"])

        step_events = _get_events_matching(bundle.events, ["step_started", "step_completed"])

        for event in step_events:
            assert event.step_id is not None, f"Step event {event.kind} missing step_id"
            assert event.step_id == "my_step", f"Step event has wrong step_id: {event.step_id}"

    def test_trace_event_has_timestamp(self, tmp_path: Path) -> None:
        """Every trace event should have a timestamp."""
        helpers.build_product(
            tmp_path,
            product_name="timestamp_trace_test",
            flows={
                "ts_flow": """
                name: ts_flow
                version: "1.0"
                steps:
                  - id: echo
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "ts"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="timestamp_trace_test")

        result = engine.run_flow(product="timestamp_trace_test", flow="ts_flow", payload={})

        bundle = engine.memory.get_run(result.data["run_id"])

        for event in bundle.events:
            assert event.ts is not None, f"Event {event.kind} missing timestamp"
            assert event.ts > 0, f"Event {event.kind} has invalid timestamp: {event.ts}"

    def test_trace_event_has_event_type(self, tmp_path: Path) -> None:
        """Every trace event should have an event_type/kind."""
        helpers.build_product(
            tmp_path,
            product_name="event_type_trace_test",
            flows={
                "type_flow": """
                name: type_flow
                version: "1.0"
                steps:
                  - id: echo
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "type"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="event_type_trace_test")

        result = engine.run_flow(product="event_type_trace_test", flow="type_flow", payload={})

        bundle = engine.memory.get_run(result.data["run_id"])

        for event in bundle.events:
            assert event.kind is not None, f"Event missing kind/event_type"
            assert len(event.kind) > 0, f"Event has empty kind"

    def test_trace_has_run_lifecycle_events(self, tmp_path: Path) -> None:
        """A completed run should have run_started and run_completed events."""
        helpers.build_product(
            tmp_path,
            product_name="lifecycle_trace_test",
            flows={
                "lifecycle_flow": """
                name: lifecycle_flow
                version: "1.0"
                steps:
                  - id: echo
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "lifecycle"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="lifecycle_trace_test")

        result = engine.run_flow(product="lifecycle_trace_test", flow="lifecycle_flow", payload={})
        assert result.ok
        assert result.data["status"] == RunStatus.COMPLETED.value

        bundle = engine.memory.get_run(result.data["run_id"])

        run_started = _get_events_by_kind(bundle.events, "run_started")
        run_completed = _get_events_by_kind(bundle.events, "run_completed")

        assert len(run_started) >= 1, "Expected run_started event"
        assert len(run_completed) >= 1, "Expected run_completed event"

    def test_trace_events_ordered_by_timestamp(self, tmp_path: Path) -> None:
        """Trace events should be ordered by timestamp (non-decreasing)."""
        helpers.build_product(
            tmp_path,
            product_name="order_trace_test",
            flows={
                "order_flow": """
                name: order_flow
                version: "1.0"
                steps:
                  - id: a
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "a"
                  - id: b
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "b"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="order_trace_test")

        result = engine.run_flow(product="order_trace_test", flow="order_flow", payload={})

        bundle = engine.memory.get_run(result.data["run_id"])
        timestamps = [e.ts for e in bundle.events]

        # Timestamps should be non-decreasing
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i - 1], \
                f"Events out of order: ts[{i - 1}]={timestamps[i - 1]}, ts[{i}]={timestamps[i]}"

    def test_trace_contains_product_and_flow(self, tmp_path: Path) -> None:
        """Trace events should include product and flow names."""
        helpers.build_product(
            tmp_path,
            product_name="product_flow_trace_test",
            flows={
                "pf_flow": """
                name: pf_flow
                version: "1.0"
                steps:
                  - id: echo
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "pf"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="product_flow_trace_test")

        result = engine.run_flow(product="product_flow_trace_test", flow="pf_flow", payload={})

        bundle = engine.memory.get_run(result.data["run_id"])

        for event in bundle.events:
            assert event.product == "product_flow_trace_test", f"Event {event.kind} has wrong product"
            assert event.flow == "pf_flow", f"Event {event.kind} has wrong flow"
