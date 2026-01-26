# ==============================
# IMP-052: Decision Records Tests
# ==============================
"""
Tests for Decision Record Schema.

Tech Specs: GOV-DEC-RECORD-001..010
- GOV-DEC-RECORD-001: DecisionRecord captures each decision point
- GOV-DEC-RECORD-002: Includes decision_id, type, timestamp
- GOV-DEC-RECORD-003: Tracks run_id and phase context
- GOV-DEC-RECORD-004: Records options_considered
- GOV-DEC-RECORD-005: Records selected_option with rationale
- GOV-DEC-RECORD-006: Includes confidence and evidence_refs
- GOV-DEC-RECORD-007: Optional approver for HITL decisions
- GOV-DEC-RECORD-008: Persist via memory backend
- GOV-DEC-RECORD-009: Emit decision_recorded event
- GOV-DEC-RECORD-010: Queryable decision chain
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List

from core.contracts.decision_schema import (
    DecisionType,
    Option,
    DecisionRecord,
    DecisionChain,
    DecisionRecorder,
    create_option,
    create_decision_record,
    DECISION_RECORD_INVALID,
    DECISION_NOT_FOUND,
    DECISION_CHAIN_EMPTY,
)
from core.contracts.reasoning_schema import ReasoningPhase
from core.memory.tracing import TraceEventType


# ==============================
# DecisionType Tests
# ==============================
class TestDecisionType:
    """Tests for DecisionType enum."""
    
    def test_reasoning_decision_types_exist(self):
        """Reasoning decision types are defined."""
        assert DecisionType.PHASE_TRANSITION.value == "phase_transition"
        assert DecisionType.HYPOTHESIS_SELECTION.value == "hypothesis_selection"
        assert DecisionType.TOOL_SELECTION.value == "tool_selection"
        assert DecisionType.AGENT_DELEGATION.value == "agent_delegation"
    
    def test_governance_decision_types_exist(self):
        """Governance decision types are defined."""
        assert DecisionType.POLICY_CHECK.value == "policy_check"
        assert DecisionType.SUFFICIENCY_GATE.value == "sufficiency_gate"
        assert DecisionType.CONFIDENCE_GATE.value == "confidence_gate"
        assert DecisionType.SECURITY_CHECK.value == "security_check"
    
    def test_hitl_decision_types_exist(self):
        """HITL decision types are defined."""
        assert DecisionType.HITL_APPROVAL.value == "hitl_approval"
        assert DecisionType.HITL_REJECTION.value == "hitl_rejection"
        assert DecisionType.USER_CLARIFICATION.value == "user_clarification"
    
    def test_termination_decision_types_exist(self):
        """Termination decision types are defined."""
        assert DecisionType.COMPLETION.value == "completion"
        assert DecisionType.EARLY_TERMINATION.value == "early_termination"
        assert DecisionType.ERROR_RECOVERY.value == "error_recovery"
    
    def test_decision_type_is_string_enum(self):
        """DecisionType inherits from str."""
        assert isinstance(DecisionType.PHASE_TRANSITION, str)


# ==============================
# Option Tests
# ==============================
class TestOption:
    """Tests for Option dataclass."""
    
    def test_option_creation(self):
        """Option stores all fields."""
        opt = Option(
            option_id="opt-001",
            name="Option A",
            description="First option",
            score=0.85,
        )
        
        assert opt.option_id == "opt-001"
        assert opt.name == "Option A"
        assert opt.description == "First option"
        assert opt.score == 0.85
    
    def test_option_immutable(self):
        """Option is frozen/immutable."""
        opt = Option(
            option_id="opt-001",
            name="Test",
        )
        
        with pytest.raises(Exception):
            opt.name = "Changed"  # type: ignore
    
    def test_option_defaults(self):
        """Option has sensible defaults."""
        opt = Option(
            option_id="opt-001",
            name="Test",
        )
        
        assert opt.description == ""
        assert opt.score == 0.0
        assert opt.metadata == {}
    
    def test_option_to_dict(self):
        """to_dict includes all fields."""
        opt = Option(
            option_id="opt-001",
            name="Test",
            description="Desc",
            score=0.7,
            metadata={"key": "value"},
        )
        
        d = opt.to_dict()
        
        assert d["option_id"] == "opt-001"
        assert d["name"] == "Test"
        assert d["description"] == "Desc"
        assert d["score"] == 0.7
        assert d["metadata"] == {"key": "value"}


# ==============================
# DecisionRecord Tests
# ==============================
class TestDecisionRecord:
    """Tests for DecisionRecord Pydantic model."""
    
    def test_record_creation(self):
        """DecisionRecord stores all required fields."""
        record = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        
        assert record.decision_type == DecisionType.TOOL_SELECTION
        assert record.run_id == "run-001"
        assert len(record.decision_id) > 0
        assert isinstance(record.timestamp, datetime)
    
    def test_record_immutable(self):
        """DecisionRecord is frozen/immutable."""
        record = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        
        with pytest.raises(Exception):
            record.run_id = "changed"  # type: ignore
    
    def test_record_with_phase(self):
        """DecisionRecord tracks reasoning phase."""
        record = DecisionRecord(
            decision_type=DecisionType.PHASE_TRANSITION,
            run_id="run-001",
            phase=ReasoningPhase.PROPOSE,
            step_index=2,
        )
        
        assert record.phase == ReasoningPhase.PROPOSE
        assert record.step_index == 2
    
    def test_record_with_options(self):
        """DecisionRecord tracks options considered."""
        options = [
            {"option_id": "opt-001", "name": "A"},
            {"option_id": "opt-002", "name": "B"},
        ]
        selected = {"option_id": "opt-001", "name": "A"}
        
        record = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            options_considered=options,
            selected_option=selected,
            selection_rationale="A is better",
        )
        
        assert record.options_count == 2
        assert record.has_selection is True
        assert record.selection_rationale == "A is better"
    
    def test_record_with_confidence_and_evidence(self):
        """DecisionRecord tracks confidence and evidence."""
        record = DecisionRecord(
            decision_type=DecisionType.HYPOTHESIS_SELECTION,
            run_id="run-001",
            confidence=0.9,
            evidence_refs=["ev-001", "ev-002"],
        )
        
        assert record.confidence == 0.9
        assert record.evidence_count == 2
    
    def test_record_with_approver(self):
        """DecisionRecord tracks HITL approver."""
        record = DecisionRecord(
            decision_type=DecisionType.HITL_APPROVAL,
            run_id="run-001",
            approver="user@example.com",
        )
        
        assert record.has_approver is True
        assert record.is_hitl_decision is True
        assert record.approver == "user@example.com"
    
    def test_record_confidence_bounds(self):
        """Confidence must be between 0 and 1."""
        # Valid bounds
        record_min = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            confidence=0.0,
        )
        record_max = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            confidence=1.0,
        )
        
        assert record_min.confidence == 0.0
        assert record_max.confidence == 1.0
        
        # Invalid bounds
        with pytest.raises(Exception):
            DecisionRecord(
                decision_type=DecisionType.TOOL_SELECTION,
                run_id="run-001",
                confidence=1.5,
            )


class TestDecisionRecordProperties:
    """Tests for DecisionRecord properties."""
    
    def test_is_hitl_decision_approval(self):
        """is_hitl_decision returns True for HITL_APPROVAL."""
        record = DecisionRecord(
            decision_type=DecisionType.HITL_APPROVAL,
            run_id="run-001",
        )
        assert record.is_hitl_decision is True
    
    def test_is_hitl_decision_rejection(self):
        """is_hitl_decision returns True for HITL_REJECTION."""
        record = DecisionRecord(
            decision_type=DecisionType.HITL_REJECTION,
            run_id="run-001",
        )
        assert record.is_hitl_decision is True
    
    def test_is_hitl_decision_other_types(self):
        """is_hitl_decision returns False for other types."""
        record = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        assert record.is_hitl_decision is False
    
    def test_options_count_empty(self):
        """options_count returns 0 for empty options."""
        record = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        assert record.options_count == 0
    
    def test_has_selection_false(self):
        """has_selection returns False when no selection."""
        record = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        assert record.has_selection is False


class TestDecisionRecordSerialization:
    """Tests for DecisionRecord serialization."""
    
    def test_to_trace_payload(self):
        """to_trace_payload includes key fields."""
        record = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            phase=ReasoningPhase.PROPOSE,
            confidence=0.85,
        )
        
        payload = record.to_trace_payload()
        
        assert payload["decision_type"] == "tool_selection"
        assert payload["run_id"] == "run-001"
        assert payload["phase"] == "propose"
        assert payload["confidence"] == 0.85
    
    def test_to_dict(self):
        """to_dict includes all fields."""
        record = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            selection_rationale="Best option",
        )
        
        d = record.to_dict()
        
        assert d["decision_type"] == "tool_selection"
        assert d["run_id"] == "run-001"
        assert d["selection_rationale"] == "Best option"
        assert "timestamp" in d


# ==============================
# DecisionChain Tests
# ==============================
class TestDecisionChain:
    """Tests for DecisionChain dataclass."""
    
    def test_chain_creation(self):
        """DecisionChain initializes with run_id."""
        chain = DecisionChain(run_id="run-001")
        
        assert chain.run_id == "run-001"
        assert chain.is_empty is True
        assert chain.length == 0
    
    def test_add_decision(self):
        """add() appends decision to chain."""
        chain = DecisionChain(run_id="run-001")
        
        decision = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        
        chain.add(decision)
        
        assert chain.length == 1
        assert chain.is_empty is False
    
    def test_add_mismatched_run_id_raises(self):
        """add() raises when run_id doesn't match."""
        chain = DecisionChain(run_id="run-001")
        
        decision = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-002",  # Different run_id
        )
        
        with pytest.raises(ValueError, match="does not match"):
            chain.add(decision)
    
    def test_filter_by_type(self):
        """filter_by_type returns matching decisions."""
        chain = DecisionChain(run_id="run-001")
        
        chain.add(DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        ))
        chain.add(DecisionRecord(
            decision_type=DecisionType.PHASE_TRANSITION,
            run_id="run-001",
        ))
        chain.add(DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        ))
        
        tool_decisions = chain.filter_by_type(DecisionType.TOOL_SELECTION)
        
        assert len(tool_decisions) == 2
    
    def test_filter_by_phase(self):
        """filter_by_phase returns matching decisions."""
        chain = DecisionChain(run_id="run-001")
        
        chain.add(DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            phase=ReasoningPhase.PROPOSE,
        ))
        chain.add(DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            phase=ReasoningPhase.CRITIQUE,
        ))
        
        propose_decisions = chain.filter_by_phase(ReasoningPhase.PROPOSE)
        
        assert len(propose_decisions) == 1
    
    def test_get_latest(self):
        """get_latest returns most recent decision."""
        chain = DecisionChain(run_id="run-001")
        
        d1 = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        d2 = DecisionRecord(
            decision_type=DecisionType.PHASE_TRANSITION,
            run_id="run-001",
        )
        
        chain.add(d1)
        chain.add(d2)
        
        latest = chain.get_latest()
        
        # d2 was added later, should be latest
        assert latest is not None
        assert latest.decision_type == DecisionType.PHASE_TRANSITION
    
    def test_get_latest_empty(self):
        """get_latest returns None for empty chain."""
        chain = DecisionChain(run_id="run-001")
        assert chain.get_latest() is None
    
    def test_get_by_id(self):
        """get_by_id returns matching decision."""
        chain = DecisionChain(run_id="run-001")
        
        d1 = DecisionRecord(
            decision_id="d-001",
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        
        chain.add(d1)
        
        found = chain.get_by_id("d-001")
        
        assert found is not None
        assert found.decision_id == "d-001"
    
    def test_get_by_id_not_found(self):
        """get_by_id returns None when not found."""
        chain = DecisionChain(run_id="run-001")
        assert chain.get_by_id("nonexistent") is None
    
    def test_to_trace_payload(self):
        """to_trace_payload includes summary."""
        chain = DecisionChain(run_id="run-001")
        chain.add(DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            phase=ReasoningPhase.PROPOSE,
        ))
        
        payload = chain.to_trace_payload()
        
        assert payload["run_id"] == "run-001"
        assert payload["decision_count"] == 1


# ==============================
# DecisionRecorder Tests
# ==============================
class TestDecisionRecorder:
    """Tests for DecisionRecorder class."""
    
    def test_record_decision(self):
        """record() stores decision in chain."""
        recorder = DecisionRecorder()
        
        decision = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        
        recorded = recorder.record(decision)
        
        assert recorded.decision_id == decision.decision_id
        
        chain = recorder.get_chain("run-001")
        assert chain is not None
        assert chain.length == 1
    
    def test_record_emits_event(self):
        """record() emits decision_recorded event."""
        events: List[Dict[str, Any]] = []
        
        def emit(event_type: str, payload: Dict[str, Any]) -> None:
            events.append({"type": event_type, "payload": payload})
        
        recorder = DecisionRecorder(emit_event_fn=emit)
        
        decision = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        
        recorder.record(decision)
        
        assert len(events) == 1
        assert events[0]["type"] == "decision_recorded"
        assert events[0]["payload"]["run_id"] == "run-001"
    
    def test_record_persists(self):
        """record() calls persist function."""
        persisted: List[DecisionRecord] = []
        
        def persist(decision: DecisionRecord) -> None:
            persisted.append(decision)
        
        recorder = DecisionRecorder(persist_fn=persist)
        
        decision = DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        
        recorder.record(decision)
        
        assert len(persisted) == 1
        assert persisted[0].decision_id == decision.decision_id
    
    def test_create_and_record(self):
        """create_and_record creates and records in one call."""
        recorder = DecisionRecorder()
        
        options = [
            create_option("Option A", score=0.8),
            create_option("Option B", score=0.6),
        ]
        selected = options[0]
        
        decision = recorder.create_and_record(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            phase=ReasoningPhase.PROPOSE,
            options=options,
            selected=selected,
            rationale="Higher score",
            confidence=0.9,
        )
        
        assert decision.decision_type == DecisionType.TOOL_SELECTION
        assert decision.options_count == 2
        assert decision.has_selection is True
        assert decision.confidence == 0.9
    
    def test_list_decisions(self):
        """list_decisions returns all decisions for run."""
        recorder = DecisionRecorder()
        
        recorder.record(DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        ))
        recorder.record(DecisionRecord(
            decision_type=DecisionType.PHASE_TRANSITION,
            run_id="run-001",
        ))
        recorder.record(DecisionRecord(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-002",  # Different run
        ))
        
        decisions = recorder.list_decisions("run-001")
        
        assert len(decisions) == 2
    
    def test_list_decisions_empty(self):
        """list_decisions returns empty for unknown run."""
        recorder = DecisionRecorder()
        
        decisions = recorder.list_decisions("nonexistent")
        
        assert decisions == []
    
    def test_get_decision(self):
        """get_decision returns specific decision."""
        recorder = DecisionRecorder()
        
        decision = DecisionRecord(
            decision_id="d-001",
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
        )
        recorder.record(decision)
        
        found = recorder.get_decision("run-001", "d-001")
        
        assert found is not None
        assert found.decision_id == "d-001"
    
    def test_get_decision_not_found(self):
        """get_decision returns None when not found."""
        recorder = DecisionRecorder()
        
        found = recorder.get_decision("run-001", "nonexistent")
        
        assert found is None


# ==============================
# Factory Function Tests
# ==============================
class TestFactoryFunctions:
    """Tests for factory functions."""
    
    def test_create_option(self):
        """create_option creates Option with UUID."""
        opt = create_option(
            name="Test Option",
            description="A test",
            score=0.75,
        )
        
        assert len(opt.option_id) == 8
        assert opt.name == "Test Option"
        assert opt.score == 0.75
    
    def test_create_decision_record(self):
        """create_decision_record creates DecisionRecord."""
        record = create_decision_record(
            decision_type=DecisionType.TOOL_SELECTION,
            run_id="run-001",
            phase=ReasoningPhase.PROPOSE,
            confidence=0.85,
        )
        
        assert record.decision_type == DecisionType.TOOL_SELECTION
        assert record.run_id == "run-001"
        assert record.phase == ReasoningPhase.PROPOSE
        assert record.confidence == 0.85


# ==============================
# Trace Event Type Tests
# ==============================
class TestTraceEventType:
    """Tests for trace event type registration."""
    
    def test_decision_recorded_event_exists(self):
        """DECISION_RECORDED trace event type exists."""
        assert hasattr(TraceEventType, "DECISION_RECORDED")
        assert TraceEventType.DECISION_RECORDED.value == "decision_recorded"


# ==============================
# Error Code Tests
# ==============================
class TestErrorCodes:
    """Tests for error code constants."""
    
    def test_decision_record_invalid_code(self):
        """DECISION_RECORD_INVALID error code exists."""
        assert DECISION_RECORD_INVALID == "DECISION_RECORD_INVALID"
    
    def test_decision_not_found_code(self):
        """DECISION_NOT_FOUND error code exists."""
        assert DECISION_NOT_FOUND == "DECISION_NOT_FOUND"
    
    def test_decision_chain_empty_code(self):
        """DECISION_CHAIN_EMPTY error code exists."""
        assert DECISION_CHAIN_EMPTY == "DECISION_CHAIN_EMPTY"
