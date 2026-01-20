# ==============================
# IMP-009: Reasoning Lifecycle Phases Tests
# ==============================
"""
Tests for ReasoningLifecycle and phase management.

Tech Spec IDs: ORC-REASON-001, ORC-REASON-002, ORC-REASON-003, ORC-REASON-004, ORC-REASON-005
Tech Spec IDs (IMP-010): ORC-REASON-010, ORC-REASON-011, ORC-REASON-012, ORC-REASON-013, ORC-REASON-014, ORC-REASON-015
Tech Spec IDs (IMP-011): ORC-REASON-020, ORC-REASON-021, ORC-REASON-022
BRD ID: BRD-AUTO-047, BRD-AUTO-048
"""

import pytest
from datetime import datetime

from core.contracts.reasoning_schema import (
    CritiqueOutput,
    InterpretOutput,
    ProposeOutput,
    ReasoningPhase,
    RecommendOutput,
)
from core.orchestrator.reasoning_lifecycle import (
    InvalidPhaseTransitionError,
    PhaseTransitionRecord,
    ReasoningLifecycle,
    ReasoningLifecycleError,
    ReasoningTerminationReason,
    RecommendWithoutCritiqueError,
    VALID_TRANSITIONS,
)


# ==============================
# ReasoningPhase Enum Tests
# ==============================
class TestReasoningPhaseEnum:
    """Tests for ReasoningPhase enum."""

    def test_phase_enum_has_four_values(self):
        """ORC-REASON-001: Reasoning proceeds through 4 phases."""
        phases = list(ReasoningPhase)
        assert len(phases) == 4
    
    def test_phase_enum_values(self):
        """ReasoningPhase has correct enum values."""
        assert ReasoningPhase.INTERPRET.value == "interpret"
        assert ReasoningPhase.PROPOSE.value == "propose"
        assert ReasoningPhase.CRITIQUE.value == "critique"
        assert ReasoningPhase.RECOMMEND.value == "recommend"
    
    def test_phase_enum_is_string(self):
        """ReasoningPhase is a string enum."""
        assert isinstance(ReasoningPhase.INTERPRET, str)
        assert ReasoningPhase.INTERPRET == "interpret"


# ==============================
# Phase Output Schema Tests
# ==============================
class TestPhaseOutputSchemas:
    """Tests for phase output schemas."""

    def test_interpret_output_creation(self):
        """InterpretOutput can be created with required fields."""
        output = InterpretOutput(user_intent="Find user data")
        assert output.user_intent == "Find user data"
        assert output.confidence == 1.0
        assert output.entities == []
        assert output.id is not None
    
    def test_interpret_output_full(self):
        """InterpretOutput stores all fields."""
        output = InterpretOutput(
            user_intent="Find user data",
            entities=["user", "data"],
            constraints={"limit": 10},
            ambiguities=["Which user?"],
            confidence=0.8,
        )
        assert output.entities == ["user", "data"]
        assert output.constraints == {"limit": 10}
        assert output.ambiguities == ["Which user?"]
        assert output.confidence == 0.8

    def test_propose_output_creation(self):
        """ProposeOutput can be created."""
        output = ProposeOutput()
        assert output.proposed_actions == []
        assert output.hypotheses == []
        assert output.confidence == 1.0
    
    def test_critique_output_creation(self):
        """CritiqueOutput can be created."""
        output = CritiqueOutput()
        assert output.issues_found == []
        assert output.improvements == []
        assert output.verdict == ""
    
    def test_recommend_output_creation(self):
        """RecommendOutput can be created with required fields."""
        output = RecommendOutput(recommendation="Execute action A")
        assert output.recommendation == "Execute action A"
        assert output.selected_action is None
        assert output.confidence == 1.0

    def test_phase_outputs_are_frozen(self):
        """All phase outputs are frozen (immutable)."""
        interpret = InterpretOutput(user_intent="Test")
        propose = ProposeOutput()
        critique = CritiqueOutput()
        recommend = RecommendOutput(recommendation="Test")
        
        for output in [interpret, propose, critique, recommend]:
            with pytest.raises(Exception):  # ValidationError or AttributeError
                output.confidence = 0.5


# ==============================
# PhaseTransitionRecord Tests
# ==============================
class TestPhaseTransitionRecord:
    """Tests for PhaseTransitionRecord."""

    def test_transition_record_creation(self):
        """PhaseTransitionRecord stores transition details."""
        record = PhaseTransitionRecord(
            from_phase=None,
            to_phase=ReasoningPhase.INTERPRET,
            timestamp=datetime.now(),
            iteration=0,
        )
        assert record.from_phase is None
        assert record.to_phase == ReasoningPhase.INTERPRET
        assert record.iteration == 0
        assert record.transition_id is not None

    def test_transition_record_to_trace_payload(self):
        """to_trace_payload converts record to dict."""
        record = PhaseTransitionRecord(
            from_phase=ReasoningPhase.INTERPRET,
            to_phase=ReasoningPhase.PROPOSE,
            timestamp=datetime.now(),
            iteration=1,
        )
        payload = record.to_trace_payload()
        
        assert payload["from_phase"] == "interpret"
        assert payload["to_phase"] == "propose"
        assert payload["iteration"] == 1
        assert "transition_id" in payload
        assert "timestamp" in payload


# ==============================
# ReasoningLifecycle Tests
# ==============================
class TestReasoningLifecycleInit:
    """Tests for ReasoningLifecycle initialization."""

    def test_lifecycle_init_empty(self):
        """Lifecycle initializes with default state."""
        lifecycle = ReasoningLifecycle()
        assert lifecycle.current_phase is None
        assert lifecycle.iteration == 0
        assert lifecycle.max_iterations == 3
        assert not lifecycle.is_complete
        assert not lifecycle.critique_completed

    def test_lifecycle_init_with_run_id(self):
        """Lifecycle accepts run_id."""
        lifecycle = ReasoningLifecycle(run_id="test-run")
        assert lifecycle.run_id == "test-run"

    def test_lifecycle_init_max_iterations_clamped(self):
        """max_iterations is clamped to 1-10."""
        low = ReasoningLifecycle(max_iterations=0)
        high = ReasoningLifecycle(max_iterations=20)
        
        assert low.max_iterations == 1
        assert high.max_iterations == 10


class TestReasoningLifecycleTransitions:
    """Tests for phase transitions."""

    def test_valid_initial_transition(self):
        """Initial transition to INTERPRET is valid."""
        lifecycle = ReasoningLifecycle()
        assert lifecycle.can_transition(ReasoningPhase.INTERPRET)
        
        record = lifecycle.transition_to(ReasoningPhase.INTERPRET)
        assert lifecycle.current_phase == ReasoningPhase.INTERPRET
        assert record.to_phase == ReasoningPhase.INTERPRET
        assert record.from_phase is None

    def test_valid_interpret_to_propose(self):
        """INTERPRET -> PROPOSE transition is valid."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        assert lifecycle.can_transition(ReasoningPhase.PROPOSE)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        assert lifecycle.current_phase == ReasoningPhase.PROPOSE

    def test_valid_propose_to_critique(self):
        """PROPOSE -> CRITIQUE transition is valid."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        
        assert lifecycle.can_transition(ReasoningPhase.CRITIQUE)
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        assert lifecycle.current_phase == ReasoningPhase.CRITIQUE

    def test_valid_critique_to_recommend(self):
        """CRITIQUE -> RECOMMEND transition is valid after CRITIQUE output."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        lifecycle.set_phase_output(CritiqueOutput())
        
        assert lifecycle.can_transition(ReasoningPhase.RECOMMEND)
        lifecycle.transition_to(ReasoningPhase.RECOMMEND)
        assert lifecycle.current_phase == ReasoningPhase.RECOMMEND
        assert lifecycle.is_complete

    def test_valid_critique_to_propose_loop(self):
        """CRITIQUE -> PROPOSE loop transition is valid."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        
        assert lifecycle.can_transition(ReasoningPhase.PROPOSE)
        initial_iteration = lifecycle.iteration
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        
        assert lifecycle.current_phase == ReasoningPhase.PROPOSE
        assert lifecycle.iteration == initial_iteration + 1

    def test_invalid_initial_transition(self):
        """Initial transition to non-INTERPRET is invalid."""
        lifecycle = ReasoningLifecycle()
        
        for phase in [ReasoningPhase.PROPOSE, ReasoningPhase.CRITIQUE, ReasoningPhase.RECOMMEND]:
            assert not lifecycle.can_transition(phase)
            with pytest.raises(InvalidPhaseTransitionError):
                lifecycle.transition_to(phase)

    def test_invalid_skip_transition(self):
        """Skipping phases is invalid."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        # Cannot skip to CRITIQUE
        with pytest.raises(InvalidPhaseTransitionError):
            lifecycle.transition_to(ReasoningPhase.CRITIQUE)

    def test_recommend_blocked_without_critique_orc_reason_005(self):
        """ORC-REASON-005: RECOMMEND blocked without CRITIQUE pass."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        # Do NOT set output, so critique not completed
        
        # can_transition should return False
        assert not lifecycle.can_transition(ReasoningPhase.RECOMMEND)
        
        # transition_to should raise
        with pytest.raises(RecommendWithoutCritiqueError):
            lifecycle.transition_to(ReasoningPhase.RECOMMEND)


class TestReasoningLifecycleOutputs:
    """Tests for phase output management."""

    def test_set_phase_output_orc_reason_003(self):
        """ORC-REASON-003: Each phase produces typed output artifact."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        output = InterpretOutput(user_intent="Test intent")
        lifecycle.set_phase_output(output)
        
        assert lifecycle.has_phase_output(ReasoningPhase.INTERPRET)
        assert lifecycle.get_phase_output(ReasoningPhase.INTERPRET) == output

    def test_set_output_wrong_type_raises(self):
        """Setting wrong output type raises error."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        wrong_output = ProposeOutput()  # Wrong type for INTERPRET
        with pytest.raises(ReasoningLifecycleError):
            lifecycle.set_phase_output(wrong_output)

    def test_set_output_no_phase_raises(self):
        """Setting output with no current phase raises error."""
        lifecycle = ReasoningLifecycle()
        
        output = InterpretOutput(user_intent="Test")
        with pytest.raises(ReasoningLifecycleError):
            lifecycle.set_phase_output(output)

    def test_critique_output_marks_completed(self):
        """Setting CRITIQUE output marks critique_completed."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        
        assert not lifecycle.critique_completed
        lifecycle.set_phase_output(CritiqueOutput())
        assert lifecycle.critique_completed

    def test_phase_outputs_persisted_orc_reason_004(self):
        """ORC-REASON-004: Phase outputs persisted before transition."""
        lifecycle = ReasoningLifecycle()
        
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        interpret_out = InterpretOutput(user_intent="Test")
        lifecycle.set_phase_output(interpret_out)
        
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        propose_out = ProposeOutput()
        lifecycle.set_phase_output(propose_out)
        
        # Outputs should still be accessible
        outputs = lifecycle.phase_outputs
        assert ReasoningPhase.INTERPRET in outputs
        assert ReasoningPhase.PROPOSE in outputs
        assert outputs[ReasoningPhase.INTERPRET] == interpret_out


class TestReasoningLifecycleTransitionRecords:
    """Tests for transition record tracking."""

    def test_transitions_recorded_orc_reason_002(self):
        """ORC-REASON-002: Phase transitions logged."""
        lifecycle = ReasoningLifecycle()
        
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        
        transitions = lifecycle.transitions
        assert len(transitions) == 3
        assert transitions[0].to_phase == ReasoningPhase.INTERPRET
        assert transitions[1].to_phase == ReasoningPhase.PROPOSE
        assert transitions[2].to_phase == ReasoningPhase.CRITIQUE

    def test_transition_has_timestamp(self):
        """Transition records include timestamp."""
        lifecycle = ReasoningLifecycle()
        record = lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        assert record.timestamp is not None
        assert isinstance(record.timestamp, datetime)


class TestReasoningLifecycleSerialization:
    """Tests for lifecycle serialization/restoration."""

    def test_to_serializable(self):
        """to_serializable produces dict."""
        lifecycle = ReasoningLifecycle(run_id="test-run")
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="Test"))
        
        data = lifecycle.to_serializable()
        
        assert isinstance(data, dict)
        assert data["run_id"] == "test-run"
        assert data["current_phase"] == "interpret"
        assert "phase_outputs" in data
        assert "interpret" in data["phase_outputs"]

    def test_from_serializable(self):
        """from_serializable restores lifecycle."""
        original = ReasoningLifecycle(run_id="test-run", max_iterations=5)
        original.transition_to(ReasoningPhase.INTERPRET)
        original.set_phase_output(InterpretOutput(user_intent="Test"))
        original.transition_to(ReasoningPhase.PROPOSE)
        
        data = original.to_serializable()
        restored = ReasoningLifecycle.from_serializable(data)
        
        assert restored.run_id == "test-run"
        assert restored.max_iterations == 5
        assert restored.current_phase == ReasoningPhase.PROPOSE
        assert restored.has_phase_output(ReasoningPhase.INTERPRET)

    def test_roundtrip_serialization(self):
        """Full roundtrip serialization preserves state."""
        lifecycle = ReasoningLifecycle(run_id="full-test")
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="Test"))
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.set_phase_output(ProposeOutput())
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        lifecycle.set_phase_output(CritiqueOutput())
        
        data = lifecycle.to_serializable()
        restored = ReasoningLifecycle.from_serializable(data)
        
        assert restored.critique_completed
        assert restored.can_transition(ReasoningPhase.RECOMMEND)


class TestReasoningLifecycleSummary:
    """Tests for get_summary method."""

    def test_get_summary(self):
        """get_summary returns comprehensive state."""
        lifecycle = ReasoningLifecycle(run_id="summary-test")
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="Test"))
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        
        summary = lifecycle.get_summary()
        
        assert summary["run_id"] == "summary-test"
        assert summary["current_phase"] == "propose"
        assert summary["iteration"] == 0
        assert summary["max_iterations"] == 3
        assert not summary["is_complete"]
        assert "interpret" in summary["phases_completed"]


class TestTraceEventTypes:
    """Tests for reasoning trace event types."""

    def test_reasoning_phase_started_event_exists(self):
        """REASONING_PHASE_STARTED trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "REASONING_PHASE_STARTED")
        assert TraceEventType.REASONING_PHASE_STARTED.value == "reasoning_phase_started"

    def test_reasoning_phase_completed_event_exists(self):
        """REASONING_PHASE_COMPLETED trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "REASONING_PHASE_COMPLETED")
        assert TraceEventType.REASONING_PHASE_COMPLETED.value == "reasoning_phase_completed"

    def test_reasoning_phase_transition_event_exists(self):
        """REASONING_PHASE_TRANSITION trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "REASONING_PHASE_TRANSITION")
        assert TraceEventType.REASONING_PHASE_TRANSITION.value == "reasoning_phase_transition"


class TestValidTransitions:
    """Tests for VALID_TRANSITIONS map."""

    def test_valid_transitions_covers_all_phases(self):
        """VALID_TRANSITIONS defines transitions for all phases."""
        # None and all phases should be in keys
        assert None in VALID_TRANSITIONS
        for phase in ReasoningPhase:
            assert phase in VALID_TRANSITIONS

    def test_recommend_is_terminal(self):
        """RECOMMEND has no valid outgoing transitions."""
        assert VALID_TRANSITIONS[ReasoningPhase.RECOMMEND] == []

    def test_interpret_only_from_none(self):
        """INTERPRET can only be reached from None."""
        assert ReasoningPhase.INTERPRET in VALID_TRANSITIONS[None]
        # No other phase should have INTERPRET as target
        for phase in ReasoningPhase:
            assert ReasoningPhase.INTERPRET not in VALID_TRANSITIONS.get(phase, [])


# ==============================
# IMP-010: Bounded Reasoning Iteration Tests
# ==============================
class TestReasoningTerminationReason:
    """Tests for ReasoningTerminationReason enum."""

    def test_termination_reason_enum_values(self):
        """ReasoningTerminationReason has correct values."""
        assert ReasoningTerminationReason.SUFFICIENT.value == "sufficient"
        assert ReasoningTerminationReason.MAX_ITERATIONS.value == "max_iterations"
        assert ReasoningTerminationReason.BUDGET_EXCEEDED.value == "budget_exceeded"
        assert ReasoningTerminationReason.CONFIDENCE_MET.value == "confidence_met"
        assert ReasoningTerminationReason.USER_CANCELLED.value == "user_cancelled"
        assert ReasoningTerminationReason.ERROR.value == "error"


class TestMaxIterationsConfig:
    """Tests for max_reasoning_iterations configuration."""

    def test_max_iterations_default_orc_reason_010(self):
        """ORC-REASON-010: max_reasoning_iterations defaults to 3."""
        lifecycle = ReasoningLifecycle()
        assert lifecycle.max_iterations == 3

    def test_max_iterations_configurable(self):
        """max_reasoning_iterations is configurable."""
        lifecycle = ReasoningLifecycle(max_iterations=5)
        assert lifecycle.max_iterations == 5

    def test_max_iterations_capped_at_10_orc_reason_010(self):
        """ORC-REASON-010: max_reasoning_iterations max is 10."""
        lifecycle = ReasoningLifecycle(max_iterations=15)
        assert lifecycle.max_iterations == 10

    def test_max_iterations_minimum_is_1(self):
        """max_reasoning_iterations minimum is 1."""
        lifecycle = ReasoningLifecycle(max_iterations=0)
        assert lifecycle.max_iterations == 1


class TestIterationTracking:
    """Tests for iteration count tracking."""

    def test_iteration_starts_at_zero(self):
        """Iteration count starts at 0."""
        lifecycle = ReasoningLifecycle()
        assert lifecycle.iteration == 0

    def test_iteration_increments_on_loop_orc_reason_011(self):
        """ORC-REASON-011: Iteration increments on CRITIQUE->PROPOSE loop."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        
        assert lifecycle.iteration == 0
        
        lifecycle.transition_to(ReasoningPhase.PROPOSE)  # Loop back
        assert lifecycle.iteration == 1

    def test_has_reached_max_iterations_orc_reason_012(self):
        """ORC-REASON-012: has_reached_max_iterations detects limit."""
        lifecycle = ReasoningLifecycle(max_iterations=2)
        assert not lifecycle.has_reached_max_iterations
        
        # Simulate reaching max
        lifecycle._iteration = 2
        assert lifecycle.has_reached_max_iterations


class TestBudgetConsumption:
    """Tests for budget consumption."""

    def test_budget_starts_at_zero(self):
        """Budget consumption starts at 0."""
        lifecycle = ReasoningLifecycle()
        assert lifecycle.budget_consumed == 0.0

    def test_consume_iteration_budget_orc_reason_011(self):
        """ORC-REASON-011: Each iteration consumes reasoning budget."""
        lifecycle = ReasoningLifecycle()
        
        result = lifecycle.consume_iteration_budget(1.0)
        assert result == 1.0
        assert lifecycle.budget_consumed == 1.0
        
        result = lifecycle.consume_iteration_budget(0.5)
        assert result == 1.5
        assert lifecycle.budget_consumed == 1.5


class TestTermination:
    """Tests for termination logic."""

    def test_should_terminate_when_terminated(self):
        """should_terminate returns True when already terminated."""
        lifecycle = ReasoningLifecycle()
        lifecycle.terminate(ReasoningTerminationReason.SUFFICIENT)
        assert lifecycle.should_terminate()

    def test_should_terminate_at_max_iterations_orc_reason_012(self):
        """ORC-REASON-012: Deterministic termination at max iterations."""
        lifecycle = ReasoningLifecycle(max_iterations=2)
        lifecycle._iteration = 2
        assert lifecycle.should_terminate()

    def test_should_terminate_when_complete(self):
        """should_terminate returns True when reasoning complete."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        lifecycle.set_phase_output(CritiqueOutput())
        lifecycle.transition_to(ReasoningPhase.RECOMMEND)
        
        assert lifecycle.should_terminate()

    def test_terminate_sets_state(self):
        """terminate sets termination state."""
        lifecycle = ReasoningLifecycle()
        payload = lifecycle.terminate(ReasoningTerminationReason.MAX_ITERATIONS, 0.85)
        
        assert lifecycle.is_terminated
        assert lifecycle.termination_reason == ReasoningTerminationReason.MAX_ITERATIONS
        assert lifecycle.final_confidence == 0.85
        assert payload["reason"] == "max_iterations"

    def test_get_termination_payload_orc_reason_014(self):
        """ORC-REASON-014: reasoning_terminated event has correct payload."""
        lifecycle = ReasoningLifecycle(run_id="test-run")
        lifecycle._iteration = 2
        lifecycle._budget_consumed = 3.5
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="Test"))
        lifecycle.terminate(ReasoningTerminationReason.CONFIDENCE_MET, 0.95)
        
        payload = lifecycle.get_termination_payload()
        
        assert payload["run_id"] == "test-run"
        assert payload["iteration_count"] == 2
        assert payload["reason"] == "confidence_met"
        assert payload["final_confidence"] == 0.95
        assert payload["budget_consumed"] == 3.5
        assert "interpret" in payload["phases_completed"]
        assert payload["terminated_at"] is not None


class TestCheckAndTerminate:
    """Tests for check_and_terminate_if_needed."""

    def test_returns_none_when_no_termination(self):
        """Returns None when no termination condition met."""
        lifecycle = ReasoningLifecycle(max_iterations=5)
        result = lifecycle.check_and_terminate_if_needed()
        assert result is None
        assert not lifecycle.is_terminated

    def test_terminates_at_max_iterations_orc_reason_012(self):
        """ORC-REASON-012: Auto-terminates at max iterations."""
        lifecycle = ReasoningLifecycle(max_iterations=2)
        lifecycle._iteration = 2
        
        result = lifecycle.check_and_terminate_if_needed(current_confidence=0.7)
        
        assert result == ReasoningTerminationReason.MAX_ITERATIONS
        assert lifecycle.is_terminated
        assert lifecycle.final_confidence == 0.7

    def test_terminates_at_budget_exceeded(self):
        """Auto-terminates when budget exceeded."""
        lifecycle = ReasoningLifecycle()
        
        result = lifecycle.check_and_terminate_if_needed(
            budget_remaining=0,
            current_confidence=0.5,
        )
        
        assert result == ReasoningTerminationReason.BUDGET_EXCEEDED
        assert lifecycle.is_terminated

    def test_terminates_at_confidence_threshold(self):
        """Auto-terminates when confidence threshold met."""
        lifecycle = ReasoningLifecycle()
        
        result = lifecycle.check_and_terminate_if_needed(
            confidence_threshold=0.8,
            current_confidence=0.85,
        )
        
        assert result == ReasoningTerminationReason.CONFIDENCE_MET
        assert lifecycle.is_terminated

    def test_max_iterations_checked_first(self):
        """Max iterations is checked before other conditions."""
        lifecycle = ReasoningLifecycle(max_iterations=1)
        lifecycle._iteration = 1
        
        result = lifecycle.check_and_terminate_if_needed(
            budget_remaining=0,
            confidence_threshold=0.5,
            current_confidence=0.9,
        )
        
        # Max iterations should trigger first
        assert result == ReasoningTerminationReason.MAX_ITERATIONS


class TestTerminationTraceEvent:
    """Tests for reasoning_terminated trace event type."""

    def test_reasoning_terminated_event_exists(self):
        """REASONING_TERMINATED trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "REASONING_TERMINATED")
        assert TraceEventType.REASONING_TERMINATED.value == "reasoning_terminated"


class TestTerminationSerialization:
    """Tests for termination state serialization."""

    def test_terminated_state_serialized(self):
        """Termination state is included in serialization."""
        lifecycle = ReasoningLifecycle()
        lifecycle.terminate(ReasoningTerminationReason.BUDGET_EXCEEDED, 0.6)
        lifecycle._budget_consumed = 5.0
        
        data = lifecycle.to_serializable()
        
        assert data["terminated"] is True
        assert data["termination_reason"] == "budget_exceeded"
        assert data["final_confidence"] == 0.6
        assert data["budget_consumed"] == 5.0

    def test_terminated_state_restored(self):
        """Termination state is restored from serialization."""
        data = {
            "run_id": "test",
            "max_iterations": 3,
            "terminated": True,
            "termination_reason": "max_iterations",
            "final_confidence": 0.75,
            "budget_consumed": 2.5,
        }
        
        restored = ReasoningLifecycle.from_serializable(data)
        
        assert restored.is_terminated
        assert restored.termination_reason == ReasoningTerminationReason.MAX_ITERATIONS
        assert restored.final_confidence == 0.75
        assert restored.budget_consumed == 2.5

    def test_summary_includes_termination_info(self):
        """get_summary includes termination information."""
        lifecycle = ReasoningLifecycle()
        lifecycle.terminate(ReasoningTerminationReason.SUFFICIENT, 0.99)
        
        summary = lifecycle.get_summary()
        
        assert summary["is_terminated"] is True
        assert summary["termination_reason"] == "sufficient"
        assert summary["final_confidence"] == 0.99


# ==============================
# IMP-011: Reasoning Phase Events Tests
# ==============================
class TestReasoningPhaseStartedEvent:
    """Tests for reasoning_phase_started event (ORC-REASON-020)."""

    def test_phase_started_payload_has_required_fields(self):
        """ORC-REASON-020: reasoning_phase_started includes phase_name, iteration, input_hash."""
        lifecycle = ReasoningLifecycle(run_id="test-run")
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        payload = lifecycle.get_phase_started_payload(input_hash="abc123")
        
        assert payload["run_id"] == "test-run"
        assert payload["phase_name"] == "interpret"
        assert payload["iteration"] == 0
        assert payload["input_hash"] == "abc123"
        assert "timestamp" in payload

    def test_phase_started_payload_no_hash(self):
        """Phase started payload works without input_hash."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        payload = lifecycle.get_phase_started_payload()
        
        assert payload["phase_name"] == "interpret"
        assert payload["input_hash"] is None

    def test_phase_started_payload_iteration_tracked(self):
        """Phase started payload tracks iteration correctly."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        lifecycle.set_phase_output(CritiqueOutput())
        lifecycle.transition_to(ReasoningPhase.PROPOSE)  # Loop back
        
        payload = lifecycle.get_phase_started_payload()
        
        assert payload["phase_name"] == "propose"
        assert payload["iteration"] == 1


class TestReasoningPhaseCompletedEvent:
    """Tests for reasoning_phase_completed event (ORC-REASON-021)."""

    def test_phase_completed_payload_has_required_fields(self):
        """ORC-REASON-021: reasoning_phase_completed includes phase_name, iteration, output_hash, confidence."""
        lifecycle = ReasoningLifecycle(run_id="test-run")
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="Test"))
        
        payload = lifecycle.get_phase_completed_payload(
            output_hash="def456",
            confidence=0.92,
        )
        
        assert payload["run_id"] == "test-run"
        assert payload["phase_name"] == "interpret"
        assert payload["iteration"] == 0
        assert payload["output_hash"] == "def456"
        assert payload["confidence"] == 0.92
        assert "timestamp" in payload

    def test_phase_completed_payload_defaults(self):
        """Phase completed payload has sensible defaults."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        payload = lifecycle.get_phase_completed_payload()
        
        assert payload["output_hash"] is None
        assert payload["confidence"] == 0.0


class TestReasoningPhaseFailedEvent:
    """Tests for reasoning_phase_failed event (ORC-REASON-022)."""

    def test_phase_failed_payload_has_required_fields(self):
        """ORC-REASON-022: reasoning_phase_failed includes phase_name, iteration, error_code, reason."""
        lifecycle = ReasoningLifecycle(run_id="test-run")
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        payload = lifecycle.get_phase_failed_payload(
            error_code="VALIDATION_ERROR",
            reason="Input failed validation checks",
        )
        
        assert payload["run_id"] == "test-run"
        assert payload["phase_name"] == "interpret"
        assert payload["iteration"] == 0
        assert payload["error_code"] == "VALIDATION_ERROR"
        assert payload["reason"] == "Input failed validation checks"
        assert "timestamp" in payload

    def test_phase_failed_tracks_current_phase(self):
        """Phase failed payload tracks the failed phase correctly."""
        lifecycle = ReasoningLifecycle()
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        
        payload = lifecycle.get_phase_failed_payload(
            error_code="MODEL_ERROR",
            reason="LLM returned malformed response",
        )
        
        assert payload["phase_name"] == "propose"


class TestReasoningPhaseFailedEventType:
    """Tests for REASONING_PHASE_FAILED trace event type."""

    def test_reasoning_phase_failed_event_exists(self):
        """REASONING_PHASE_FAILED trace event type exists."""
        from core.memory.tracing import TraceEventType

        assert hasattr(TraceEventType, "REASONING_PHASE_FAILED")
        assert TraceEventType.REASONING_PHASE_FAILED.value == "reasoning_phase_failed"