# ==============================
# IMP-034: Reasoning Contract Tests
# ==============================
"""
Tests for Minimum Reasoning Contract Enforcement.

Tech Specs: ORC-REASON-CONTRACT-001..011
- ORC-REASON-CONTRACT-001: INTERPRET and PROPOSE are always mandatory
- ORC-REASON-CONTRACT-002: CRITIQUE can be waived with documented reason
- ORC-REASON-CONTRACT-003: RECOMMEND requires prior CRITIQUE (unless waived)
- ORC-REASON-CONTRACT-004: Waiver reason must be non-empty
- ORC-REASON-CONTRACT-005: Contract embedded in FlowDef
- ORC-REASON-CONTRACT-006: Validation occurs at lifecycle transition
- ORC-REASON-CONTRACT-007: critique_phase_waived trace event emitted
- ORC-REASON-CONTRACT-008: Contract immutable after creation
- ORC-REASON-CONTRACT-009: Default contract requires all phases
- ORC-REASON-CONTRACT-010: Contract persisted with lifecycle state
- ORC-REASON-CONTRACT-011: Contract queryable from lifecycle
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List

from core.contracts.reasoning_schema import (
    ReasoningContract,
    ReasoningContractError,
    ReasoningPhase,
    InterpretOutput,
    ProposeOutput,
    CritiqueOutput,
    RecommendOutput,
    get_default_reasoning_contract,
    create_waived_contract,
    REASONING_CONTRACT_VIOLATION,
    CRITIQUE_WAIVER_INVALID,
    MANDATORY_PHASE_MISSING,
)
from core.contracts.flow_schema import FlowDef, StepType
from core.orchestrator.reasoning_lifecycle import (
    ReasoningLifecycle,
    InvalidPhaseTransitionError,
    RecommendWithoutCritiqueError,
)
from core.memory.tracing import TraceEventType


# ==============================
# ReasoningContract Model Tests
# ==============================
class TestReasoningContractModel:
    """Tests for ReasoningContract Pydantic model."""
    
    def test_default_contract_no_waiver(self):
        """Default contract has no critique waiver."""
        contract = ReasoningContract()
        assert contract.critique_waiver is False
        assert contract.waiver_reason == ""
    
    def test_contract_immutable(self):
        """Contract is immutable (frozen=True)."""
        contract = ReasoningContract()
        with pytest.raises(Exception):  # Pydantic will raise on mutation
            contract.critique_waiver = True  # type: ignore
    
    def test_waiver_requires_reason(self):
        """Waiver without reason raises ValueError."""
        with pytest.raises(ValueError, match="waiver_reason is required"):
            ReasoningContract(critique_waiver=True, waiver_reason="")
    
    def test_waiver_with_reason_succeeds(self):
        """Waiver with non-empty reason succeeds."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Low-risk informational query",
        )
        assert contract.critique_waiver is True
        assert contract.waiver_reason == "Low-risk informational query"
    
    def test_waiver_reason_whitespace_only_fails(self):
        """Waiver with whitespace-only reason fails."""
        with pytest.raises(ValueError, match="waiver_reason is required"):
            ReasoningContract(critique_waiver=True, waiver_reason="   ")


class TestReasoningContractMandatoryPhases:
    """Tests for mandatory phase requirements."""
    
    def test_mandatory_phases_always_interpret_propose(self):
        """INTERPRET and PROPOSE are always mandatory (ORC-REASON-CONTRACT-001)."""
        contract = ReasoningContract()
        assert ReasoningPhase.INTERPRET in contract.mandatory_phases
        assert ReasoningPhase.PROPOSE in contract.mandatory_phases
        assert len(contract.mandatory_phases) == 2
    
    def test_mandatory_phases_same_with_waiver(self):
        """Mandatory phases unchanged with waiver."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test reason",
        )
        assert ReasoningPhase.INTERPRET in contract.mandatory_phases
        assert ReasoningPhase.PROPOSE in contract.mandatory_phases
        assert len(contract.mandatory_phases) == 2
    
    def test_optional_phases_includes_critique_without_waiver(self):
        """Optional phases includes CRITIQUE when no waiver."""
        contract = ReasoningContract()
        assert ReasoningPhase.CRITIQUE in contract.optional_phases
        assert len(contract.optional_phases) == 1
    
    def test_optional_phases_empty_with_waiver(self):
        """Optional phases empty when critique waived."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test reason",
        )
        assert len(contract.optional_phases) == 0
    
    def test_all_required_phases_without_waiver(self):
        """All required phases includes INTERPRET, PROPOSE, CRITIQUE."""
        contract = ReasoningContract()
        required = contract.all_required_phases
        assert ReasoningPhase.INTERPRET in required
        assert ReasoningPhase.PROPOSE in required
        assert ReasoningPhase.CRITIQUE in required
    
    def test_all_required_phases_with_waiver(self):
        """All required phases excludes CRITIQUE when waived."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test reason",
        )
        required = contract.all_required_phases
        assert ReasoningPhase.INTERPRET in required
        assert ReasoningPhase.PROPOSE in required
        assert ReasoningPhase.CRITIQUE not in required


class TestReasoningContractValidation:
    """Tests for contract validation of phases."""
    
    def test_validate_with_all_phases_succeeds(self):
        """Validation succeeds with all phases present."""
        contract = ReasoningContract()
        phases = [
            ReasoningPhase.INTERPRET,
            ReasoningPhase.PROPOSE,
            ReasoningPhase.CRITIQUE,
            ReasoningPhase.RECOMMEND,
        ]
        assert contract.validate_phases_present(phases) is True
    
    def test_validate_missing_interpret_fails(self):
        """Missing INTERPRET raises error."""
        contract = ReasoningContract()
        phases = [ReasoningPhase.PROPOSE, ReasoningPhase.CRITIQUE]
        with pytest.raises(ReasoningContractError) as exc_info:
            contract.validate_phases_present(phases)
        assert exc_info.value.error_code == MANDATORY_PHASE_MISSING
        assert "interpret" in str(exc_info.value).lower()
    
    def test_validate_missing_propose_fails(self):
        """Missing PROPOSE raises error."""
        contract = ReasoningContract()
        phases = [ReasoningPhase.INTERPRET, ReasoningPhase.CRITIQUE]
        with pytest.raises(ReasoningContractError) as exc_info:
            contract.validate_phases_present(phases)
        assert exc_info.value.error_code == MANDATORY_PHASE_MISSING
        assert "propose" in str(exc_info.value).lower()
    
    def test_validate_missing_critique_without_waiver_fails(self):
        """Missing CRITIQUE without waiver raises error."""
        contract = ReasoningContract()
        phases = [ReasoningPhase.INTERPRET, ReasoningPhase.PROPOSE]
        with pytest.raises(ReasoningContractError) as exc_info:
            contract.validate_phases_present(phases)
        assert exc_info.value.error_code == REASONING_CONTRACT_VIOLATION
        assert "critique" in str(exc_info.value).lower()
    
    def test_validate_missing_critique_with_waiver_succeeds(self):
        """Missing CRITIQUE with waiver succeeds."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test reason",
        )
        phases = [ReasoningPhase.INTERPRET, ReasoningPhase.PROPOSE]
        assert contract.validate_phases_present(phases) is True


class TestReasoningContractHelpers:
    """Tests for helper functions."""
    
    def test_get_default_reasoning_contract(self):
        """get_default_reasoning_contract returns standard contract."""
        contract = get_default_reasoning_contract()
        assert contract.critique_waiver is False
        assert ReasoningPhase.CRITIQUE in contract.all_required_phases
    
    def test_create_waived_contract_with_reason(self):
        """create_waived_contract creates contract with waiver."""
        contract = create_waived_contract("Low-risk query")
        assert contract.critique_waiver is True
        assert contract.waiver_reason == "Low-risk query"
    
    def test_create_waived_contract_empty_reason_fails(self):
        """create_waived_contract with empty reason fails."""
        with pytest.raises(ValueError):
            create_waived_contract("")


class TestReasoningContractTracePayload:
    """Tests for trace event payload generation."""
    
    def test_to_trace_payload_without_waiver(self):
        """Trace payload includes all contract info without waiver."""
        contract = ReasoningContract()
        payload = contract.to_trace_payload()
        
        assert payload["critique_waiver"] is False
        assert payload["waiver_reason"] is None
        assert "interpret" in payload["mandatory_phases"]
        assert "propose" in payload["mandatory_phases"]
        assert "critique" in payload["all_required_phases"]
    
    def test_to_trace_payload_with_waiver(self):
        """Trace payload includes waiver reason when waived."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test waiver reason",
        )
        payload = contract.to_trace_payload()
        
        assert payload["critique_waiver"] is True
        assert payload["waiver_reason"] == "Test waiver reason"
        assert "critique" not in payload["all_required_phases"]


# ==============================
# FlowDef Integration Tests
# ==============================
class TestFlowDefReasoningContract:
    """Tests for ReasoningContract integration in FlowDef."""
    
    def test_flow_def_without_contract(self):
        """FlowDef without reasoning_contract uses None."""
        flow_def = FlowDef(
            id="test-flow",
            steps=[{"id": "step1", "type": "tool", "tool": "test-tool"}],
        )
        assert flow_def.reasoning_contract is None
    
    def test_flow_def_with_default_contract(self):
        """FlowDef with default contract has no waiver."""
        contract = ReasoningContract()
        flow_def = FlowDef(
            id="test-flow",
            steps=[{"id": "step1", "type": "tool", "tool": "test-tool"}],
            reasoning_contract=contract,
        )
        assert flow_def.reasoning_contract is not None
        assert flow_def.reasoning_contract.critique_waiver is False
    
    def test_flow_def_with_waived_contract(self):
        """FlowDef with waived contract preserves waiver info."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Informational flow",
        )
        flow_def = FlowDef(
            id="info-flow",
            steps=[{"id": "step1", "type": "tool", "tool": "test-tool"}],
            reasoning_contract=contract,
        )
        assert flow_def.reasoning_contract is not None
        assert flow_def.reasoning_contract.critique_waiver is True
        assert flow_def.reasoning_contract.waiver_reason == "Informational flow"


# ==============================
# ReasoningLifecycle Contract Tests
# ==============================
class TestLifecycleWithDefaultContract:
    """Tests for lifecycle with default (no waiver) contract."""
    
    def test_lifecycle_default_contract_properties(self):
        """Default lifecycle has standard contract properties."""
        lifecycle = ReasoningLifecycle(run_id="test-run")
        assert lifecycle.contract.critique_waiver is False
        assert lifecycle.critique_waiver is False
        assert lifecycle.critique_required is True
    
    def test_lifecycle_cannot_skip_critique_without_waiver(self):
        """Cannot transition PROPOSE -> RECOMMEND without critique."""
        lifecycle = ReasoningLifecycle(run_id="test-run")
        
        # Progress to PROPOSE
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="test intent"))
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.set_phase_output(ProposeOutput(proposed_actions=[{"action": "test"}]))
        
        # Attempt to skip to RECOMMEND should fail
        with pytest.raises(InvalidPhaseTransitionError):
            lifecycle.transition_to(ReasoningPhase.RECOMMEND)
    
    def test_lifecycle_can_recommend_after_critique(self):
        """Can transition to RECOMMEND after CRITIQUE completion."""
        lifecycle = ReasoningLifecycle(run_id="test-run")
        
        # Full flow: INTERPRET -> PROPOSE -> CRITIQUE -> RECOMMEND
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="test intent"))
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.set_phase_output(ProposeOutput(proposed_actions=[{"action": "test"}]))
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        lifecycle.set_phase_output(CritiqueOutput(verdict="approved"))
        lifecycle.transition_to(ReasoningPhase.RECOMMEND)
        
        assert lifecycle.current_phase == ReasoningPhase.RECOMMEND
        assert lifecycle.critique_completed is True


class TestLifecycleWithWaiverContract:
    """Tests for lifecycle with critique waiver."""
    
    def test_lifecycle_waiver_properties(self):
        """Lifecycle with waiver has correct properties."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Low-risk query",
        )
        lifecycle = ReasoningLifecycle(
            run_id="test-run",
            contract=contract,
        )
        assert lifecycle.contract.critique_waiver is True
        assert lifecycle.critique_waiver is True
        assert lifecycle.critique_required is False
    
    def test_lifecycle_can_skip_critique_with_waiver(self):
        """Can transition PROPOSE -> RECOMMEND with waiver (ORC-REASON-CONTRACT-003)."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Low-risk query",
        )
        lifecycle = ReasoningLifecycle(
            run_id="test-run",
            contract=contract,
        )
        
        # INTERPRET -> PROPOSE -> RECOMMEND (skipping CRITIQUE)
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="test intent"))
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.set_phase_output(ProposeOutput(proposed_actions=[{"action": "test"}]))
        lifecycle.transition_to(ReasoningPhase.RECOMMEND)
        
        assert lifecycle.current_phase == ReasoningPhase.RECOMMEND
        assert lifecycle.critique_completed is False  # Never completed
    
    def test_lifecycle_can_transition_returns_true_for_waiver(self):
        """can_transition returns True for PROPOSE -> RECOMMEND with waiver."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test reason",
        )
        lifecycle = ReasoningLifecycle(
            run_id="test-run",
            contract=contract,
        )
        
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="test intent"))
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.set_phase_output(ProposeOutput(proposed_actions=[{"action": "test"}]))
        
        assert lifecycle.can_transition(ReasoningPhase.RECOMMEND) is True


class TestCritiqueWaiverTraceEvent:
    """Tests for critique_phase_waived trace event."""
    
    def test_waiver_emits_trace_event(self):
        """Skipping CRITIQUE with waiver emits trace event (ORC-REASON-CONTRACT-007)."""
        events: List[Dict[str, Any]] = []
        
        def emit_event(event_type: str, payload: Dict[str, Any]) -> None:
            events.append({"type": event_type, "payload": payload})
        
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Low-risk query",
        )
        lifecycle = ReasoningLifecycle(
            run_id="test-run",
            contract=contract,
            emit_event_fn=emit_event,
        )
        
        # Progress through phases
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="test intent"))
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.set_phase_output(ProposeOutput(proposed_actions=[{"action": "test"}]))
        lifecycle.transition_to(ReasoningPhase.RECOMMEND)
        
        # Check for waiver event
        waiver_events = [e for e in events if e["type"] == "critique_phase_waived"]
        assert len(waiver_events) == 1
        
        payload = waiver_events[0]["payload"]
        assert payload["run_id"] == "test-run"
        assert payload["waiver_reason"] == "Low-risk query"
        assert payload["from_phase"] == "propose"
        assert payload["to_phase"] == "recommend"
    
    def test_waiver_event_emitted_only_once(self):
        """Waiver event only emitted once per lifecycle."""
        events: List[Dict[str, Any]] = []
        
        def emit_event(event_type: str, payload: Dict[str, Any]) -> None:
            events.append({"type": event_type, "payload": payload})
        
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test reason",
        )
        lifecycle = ReasoningLifecycle(
            run_id="test-run",
            contract=contract,
            emit_event_fn=emit_event,
        )
        
        # Complete flow
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="test intent"))
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.set_phase_output(ProposeOutput(proposed_actions=[{"action": "test"}]))
        lifecycle.transition_to(ReasoningPhase.RECOMMEND)
        
        # Only one waiver event
        waiver_events = [e for e in events if e["type"] == "critique_phase_waived"]
        assert len(waiver_events) == 1
    
    def test_no_waiver_event_when_critique_completed(self):
        """No waiver event when CRITIQUE actually completed."""
        events: List[Dict[str, Any]] = []
        
        def emit_event(event_type: str, payload: Dict[str, Any]) -> None:
            events.append({"type": event_type, "payload": payload})
        
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test reason",
        )
        lifecycle = ReasoningLifecycle(
            run_id="test-run",
            contract=contract,
            emit_event_fn=emit_event,
        )
        
        # Full flow with CRITIQUE (even though waiver available)
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        lifecycle.set_phase_output(InterpretOutput(user_intent="test intent"))
        lifecycle.transition_to(ReasoningPhase.PROPOSE)
        lifecycle.set_phase_output(ProposeOutput(proposed_actions=[{"action": "test"}]))
        lifecycle.transition_to(ReasoningPhase.CRITIQUE)
        lifecycle.set_phase_output(CritiqueOutput(verdict="approved"))
        lifecycle.transition_to(ReasoningPhase.RECOMMEND)
        
        # No waiver event since CRITIQUE was completed
        waiver_events = [e for e in events if e["type"] == "critique_phase_waived"]
        assert len(waiver_events) == 0


class TestContractPersistence:
    """Tests for contract serialization and persistence."""
    
    def test_contract_in_serializable_output(self):
        """Contract included in to_serializable output (ORC-REASON-CONTRACT-010)."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test reason",
        )
        lifecycle = ReasoningLifecycle(
            run_id="test-run",
            contract=contract,
        )
        
        data = lifecycle.to_serializable()
        
        assert "contract" in data
        assert data["contract"]["critique_waiver"] is True
        assert data["contract"]["waiver_reason"] == "Test reason"
    
    def test_contract_restored_from_serializable(self):
        """Contract restored from serialized data."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Restored reason",
        )
        lifecycle = ReasoningLifecycle(
            run_id="test-run",
            contract=contract,
        )
        lifecycle.transition_to(ReasoningPhase.INTERPRET)
        
        # Serialize and restore
        data = lifecycle.to_serializable()
        restored = ReasoningLifecycle.from_serializable(data)
        
        assert restored.contract.critique_waiver is True
        assert restored.contract.waiver_reason == "Restored reason"
    
    def test_default_contract_restored_when_missing(self):
        """Default contract used when not in serialized data."""
        data = {
            "run_id": "test-run",
            "max_iterations": 3,
        }
        restored = ReasoningLifecycle.from_serializable(data)
        
        assert restored.contract.critique_waiver is False


class TestTraceEventTypeExists:
    """Tests for trace event type registration."""
    
    def test_critique_phase_waived_event_type_exists(self):
        """CRITIQUE_PHASE_WAIVED trace event type is registered."""
        assert hasattr(TraceEventType, "CRITIQUE_PHASE_WAIVED")
        assert TraceEventType.CRITIQUE_PHASE_WAIVED.value == "critique_phase_waived"
    
    def test_reasoning_contract_validated_event_type_exists(self):
        """REASONING_CONTRACT_VALIDATED trace event type is registered."""
        assert hasattr(TraceEventType, "REASONING_CONTRACT_VALIDATED")
        assert TraceEventType.REASONING_CONTRACT_VALIDATED.value == "reasoning_contract_validated"


class TestErrorCodes:
    """Tests for error code constants."""
    
    def test_reasoning_contract_violation_code(self):
        """REASONING_CONTRACT_VIOLATION error code exists."""
        assert REASONING_CONTRACT_VIOLATION == "REASONING_CONTRACT_VIOLATION"
    
    def test_critique_waiver_invalid_code(self):
        """CRITIQUE_WAIVER_INVALID error code exists."""
        assert CRITIQUE_WAIVER_INVALID == "CRITIQUE_WAIVER_INVALID"
    
    def test_mandatory_phase_missing_code(self):
        """MANDATORY_PHASE_MISSING error code exists."""
        assert MANDATORY_PHASE_MISSING == "MANDATORY_PHASE_MISSING"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_waiver_reason_with_special_characters(self):
        """Waiver reason with special characters works."""
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason="User query: 'What time is it?' - low risk",
        )
        assert "What time is it?" in contract.waiver_reason
    
    def test_very_long_waiver_reason(self):
        """Very long waiver reason accepted."""
        long_reason = "A" * 1000
        contract = ReasoningContract(
            critique_waiver=True,
            waiver_reason=long_reason,
        )
        assert len(contract.waiver_reason) == 1000
    
    def test_multiple_lifecycle_instances_independent(self):
        """Multiple lifecycle instances have independent contracts."""
        contract1 = ReasoningContract()
        contract2 = ReasoningContract(
            critique_waiver=True,
            waiver_reason="Test",
        )
        
        lifecycle1 = ReasoningLifecycle(run_id="run-1", contract=contract1)
        lifecycle2 = ReasoningLifecycle(run_id="run-2", contract=contract2)
        
        assert lifecycle1.critique_waiver is False
        assert lifecycle2.critique_waiver is True
