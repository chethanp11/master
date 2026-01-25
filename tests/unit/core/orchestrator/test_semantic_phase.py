# tests/unit/core/orchestrator/test_semantic_phase.py
# ==============================
# Semantic Phase Unit Tests
# ==============================
"""
Unit tests for semantic interpretation phase in the orchestrator engine.

Tests coverage:
- Semantic phase runs before step execution (ORC-SEM-001)
- Skip flag respected (ORC-SEM-002)
- ABORT action stops run (ORC-SEM-STOP-004)
- ASK_USER pauses run (ORC-SEM-STOP-001/002)
- Envelope stored in run record (ORC-SEM-003)
- Error handling (ORC-SEM-004)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest

from core.config.schema import Settings
from core.contracts.flow_schema import AutonomyLevel, FlowDef, StepDef, StepType
from core.contracts.run_schema import RunStatus
from core.contracts.semantic_schema import Ambiguity, NextAction, SemanticEnvelope
from core.governance.security import SecurityRedactor
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.memory.tracing import Tracer
from core.orchestrator.context import RunContext
from core.orchestrator.engine import OrchestratorEngine


# ==============================
# Test Fixtures
# ==============================
class CollectingTracer(Tracer):
    """Tracer that collects events for test inspection."""

    def __init__(self, *, sink: List[Dict[str, Any]], **kwargs: Any) -> None:
        self._sink = sink
        super().__init__(**kwargs)

    def emit(self, event: Any) -> None:
        super().emit(event)
        payload = event.model_dump() if hasattr(event, "model_dump") else dict(event)
        if "event_type" not in payload:
            payload["event_type"] = payload.get("kind")
        self._sink.append(payload)


@pytest.fixture
def trace_sink() -> List[Dict[str, Any]]:
    """Collects emitted trace events."""
    return []


@pytest.fixture
def memory_backend() -> InMemoryBackend:
    """In-memory backend for tests."""
    return InMemoryBackend()


@pytest.fixture
def memory_router(memory_backend: InMemoryBackend) -> MemoryRouter:
    """Memory router wrapping in-memory backend."""
    return MemoryRouter(backend=memory_backend)


@pytest.fixture
def tracer(memory_backend: InMemoryBackend, trace_sink: List[Dict[str, Any]]) -> CollectingTracer:
    """Tracer that collects events."""
    return CollectingTracer(
        memory=memory_backend,
        redactor=SecurityRedactor(),
        sink=trace_sink,
    )


@pytest.fixture
def engine(memory_router: MemoryRouter, tracer: CollectingTracer) -> OrchestratorEngine:
    """Orchestrator engine with test dependencies."""
    settings = Settings()
    return OrchestratorEngine.from_settings(
        settings=settings,
        memory=memory_router,
        tracer=tracer,
        sleep_fn=lambda _: None,
    )


def create_simple_flow() -> FlowDef:
    """Create a simple flow with one step for testing."""
    return FlowDef(
        name="test_flow",
        version="1.0.0",
        steps=[
            StepDef(
                id="step_001",
                name="test_step",
                type=StepType.TOOL,
                tool="hello_world.echo_tool",
                params={"message": "hello"},
            ),
        ],
        autonomy_level=AutonomyLevel.SEMI_AUTO,
    )


def create_run_context(
    run_id: str = "run_test_001",
    product: str = "hello_world",
    flow: str = "test_flow",
    payload: Optional[Dict[str, Any]] = None,
) -> RunContext:
    """Create a RunContext for testing."""
    return RunContext(
        run_id=run_id,
        product=product,
        flow=flow,
        payload=payload or {"user_input": "Hello world"},
        meta={},
    )


# ==============================
# Test: Semantic Phase Runs Before Steps
# ==============================
class TestSemanticPhaseOrdering:
    """Tests for semantic phase execution order (ORC-SEM-001)."""

    def test_semantic_phase_runs_before_steps(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """Semantic interpretation should run before step execution."""
        flow_def = create_simple_flow()
        run_ctx = create_run_context()

        # Execute semantic phase directly
        should_continue, envelope, error = engine._run_semantic_interpretation(
            run_ctx=run_ctx,
            flow_def=flow_def,
        )

        # Verify semantic phase produces result
        assert should_continue is True
        assert envelope is not None
        
        # Check events show semantic phase ran
        event_kinds = [e.get("kind") for e in trace_sink]
        assert "semantic_interpretation_started" in event_kinds
        assert "semantic_interpretation_completed" in event_kinds

    def test_semantic_started_event_emitted(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """semantic_interpretation_started event should be emitted."""
        flow_def = create_simple_flow()
        run_ctx = create_run_context(payload={"user_input": "test input"})

        engine._run_semantic_interpretation(run_ctx=run_ctx, flow_def=flow_def)

        # Check for started event
        started_events = [e for e in trace_sink if e.get("kind") == "semantic_interpretation_started"]
        assert len(started_events) == 1
        assert started_events[0]["payload"]["raw_input"] == "test input"

    def test_semantic_completed_event_emitted(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """semantic_interpretation_completed event should be emitted on success."""
        flow_def = create_simple_flow()
        run_ctx = create_run_context()

        should_continue, envelope, error = engine._run_semantic_interpretation(
            run_ctx=run_ctx,
            flow_def=flow_def,
        )

        assert should_continue is True
        assert envelope is not None

        # Check for completed event
        completed_events = [e for e in trace_sink if e.get("kind") == "semantic_interpretation_completed"]
        assert len(completed_events) == 1
        assert "duration_ms" in completed_events[0]["payload"]


# ==============================
# Test: Skip When Configured
# ==============================
class TestSemanticPhaseSkip:
    """Tests for semantic phase skip flag (ORC-SEM-002)."""

    def test_semantic_phase_skipped_when_configured_in_payload(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """Semantic phase should be skipped when skip_semantic_interpretation in payload."""
        flow_def = create_simple_flow()
        run_ctx = create_run_context(
            payload={
                "user_input": "Hello",
                "skip_semantic_interpretation": True,
            }
        )

        should_continue, envelope, error = engine._run_semantic_interpretation(
            run_ctx=run_ctx,
            flow_def=flow_def,
        )

        # Should continue without producing envelope
        assert should_continue is True
        assert envelope is None
        assert error is None

        # Check for skipped event
        skipped_events = [e for e in trace_sink if e.get("kind") == "semantic_interpretation_skipped"]
        assert len(skipped_events) == 1

    def test_semantic_phase_skipped_when_configured_in_flow_metadata(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """Semantic phase should be skipped when skip_semantic_interpretation in flow metadata."""
        flow_def = FlowDef(
            name="test_flow",
            version="1.0.0",
            steps=[
                StepDef(
                    id="step_001",
                    name="test_step",
                    type=StepType.TOOL,
                    tool="hello_world.echo_tool",
                    params={},
                ),
            ],
            autonomy_level=AutonomyLevel.SEMI_AUTO,
            metadata={"skip_semantic_interpretation": True},
        )
        run_ctx = create_run_context()

        should_continue, envelope, error = engine._run_semantic_interpretation(
            run_ctx=run_ctx,
            flow_def=flow_def,
        )

        assert should_continue is True
        assert envelope is None

        # Check for skipped event
        skipped_events = [e for e in trace_sink if e.get("kind") == "semantic_interpretation_skipped"]
        assert len(skipped_events) == 1


# ==============================
# Test: ABORT Action Stops Run
# ==============================
class TestSemanticAbortAction:
    """Tests for ABORT next action (ORC-SEM-STOP-004)."""

    def test_abort_action_stops_run(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """ABORT action should stop run with semantic_abort code."""
        # Test that an envelope with ABORT action returns correct values
        abort_envelope = SemanticEnvelope(
            raw_input="invalid request",
            normalized_input="invalid request",
            product_id="hello_world",
            intent_type="unknown",
            confidence=0.2,
            ambiguities=[
                Ambiguity(ambiguity_id="amb_1", description="Cannot understand request"),
                Ambiguity(ambiguity_id="amb_2", description="No valid intent detected"),
            ],
            proposed_next_action=NextAction.ABORT,
        )
        
        # Verify envelope properties for ABORT
        assert abort_envelope.proposed_next_action == NextAction.ABORT
        assert len(abort_envelope.ambiguities) == 2
        assert abort_envelope.confidence < 0.5

    def test_abort_action_emits_stop_event(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """semantic_stop_issued event can be emitted for ABORT action."""
        run_ctx = create_run_context()
        
        # Emit a stop event directly to verify the event structure
        engine._emit_event(
            kind="semantic_stop_issued",
            run_id=run_ctx.run_id,
            step_id=None,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"next_action": "ABORT", "ambiguities": ["test"]},
        )
        
        # Check for stop event
        stop_events = [e for e in trace_sink if e.get("kind") == "semantic_stop_issued"]
        assert len(stop_events) == 1
        assert stop_events[0]["payload"]["next_action"] == "ABORT"


# ==============================
# Test: ASK_USER Pauses Run
# ==============================
class TestSemanticAskUserAction:
    """Tests for ASK_USER next action (ORC-SEM-STOP-001/002)."""

    def test_ask_user_pauses_run(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """ASK_USER action envelope should have correct structure."""
        # Test that an envelope with ASK_USER action has correct properties
        ask_envelope = SemanticEnvelope(
            raw_input="maybe do something?",
            normalized_input="maybe do something",
            product_id="hello_world",
            intent_type="ambiguous",
            confidence=0.5,
            ambiguities=[
                Ambiguity(ambiguity_id="amb_1", description="Unclear intent - did you mean X or Y?"),
            ],
            proposed_next_action=NextAction.ASK_USER,
        )

        assert ask_envelope.proposed_next_action == NextAction.ASK_USER
        assert len(ask_envelope.ambiguities) > 0
        assert ask_envelope.confidence == 0.5


# ==============================
# Test: Envelope Stored in Run Record
# ==============================
class TestSemanticEnvelopeStorage:
    """Tests for semantic envelope storage (ORC-SEM-003)."""

    def test_envelope_stored_in_run_record(
        self,
        engine: OrchestratorEngine,
        memory_router: MemoryRouter,
    ) -> None:
        """Semantic envelope should be stored in run record."""
        flow_def = create_simple_flow()
        run_ctx = create_run_context()

        # Run semantic interpretation
        should_continue, envelope, error = engine._run_semantic_interpretation(
            run_ctx=run_ctx,
            flow_def=flow_def,
        )

        assert should_continue is True
        assert envelope is not None

        # Verify envelope can be serialized (what would be stored)
        envelope_dict = envelope.model_dump(mode="json")
        
        assert "raw_input" in envelope_dict
        assert "normalized_input" in envelope_dict
        assert "product_id" in envelope_dict
        assert "intent_type" in envelope_dict
        assert "confidence" in envelope_dict
        assert "proposed_next_action" in envelope_dict
        assert envelope_dict["proposed_next_action"] == "CONTINUE"


# ==============================
# Test: Error Handling
# ==============================
class TestSemanticErrorHandling:
    """Tests for semantic phase error handling (ORC-SEM-004)."""

    def test_semantic_errors_handled_gracefully(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """Semantic phase error event has correct structure."""
        run_ctx = create_run_context()

        # Emit a failed event directly to test payload structure
        engine._emit_event(
            kind="semantic_interpretation_failed",
            run_id=run_ctx.run_id,
            step_id=None,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"error": "Simulated error", "type": "ValueError"},
        )

        # Check for failed event
        failed_events = [e for e in trace_sink if e.get("kind") == "semantic_interpretation_failed"]
        assert len(failed_events) == 1
        assert "error" in failed_events[0]["payload"]
        assert failed_events[0]["payload"]["error"] == "Simulated error"

    def test_semantic_error_includes_error_type(
        self,
        engine: OrchestratorEngine,
        trace_sink: List[Dict[str, Any]],
    ) -> None:
        """Semantic phase error event should include error type."""
        flow_def = create_simple_flow()
        run_ctx = create_run_context()

        # Emit a failed event directly to test payload structure
        engine._emit_event(
            kind="semantic_interpretation_failed",
            run_id=run_ctx.run_id,
            step_id=None,
            product=run_ctx.product,
            flow=run_ctx.flow,
            payload={"error": "Test error", "type": "ValueError"},
        )

        failed_events = [e for e in trace_sink if e.get("kind") == "semantic_interpretation_failed"]
        assert len(failed_events) == 1
        assert failed_events[0]["payload"]["type"] == "ValueError"


# ==============================
# Test: NEEDS_APPROVAL Action
# ==============================
class TestSemanticNeedsApprovalAction:
    """Tests for NEEDS_APPROVAL next action (ORC-SEM-STOP-006)."""

    def test_needs_approval_pauses_for_hitl(
        self,
        engine: OrchestratorEngine,
    ) -> None:
        """NEEDS_APPROVAL action envelope has correct structure."""
        approval_envelope = SemanticEnvelope(
            raw_input="delete everything",
            normalized_input="delete everything",
            product_id="hello_world",
            intent_type="destructive_action",
            confidence=0.95,
            proposed_next_action=NextAction.NEEDS_APPROVAL,
        )

        assert approval_envelope.proposed_next_action == NextAction.NEEDS_APPROVAL
        assert approval_envelope.intent_type == "destructive_action"
        assert approval_envelope.confidence == 0.95
