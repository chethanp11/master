"""
Tests for Semantic Envelope Enforcement (IMP-031).

Tests ORC-SEM-ENV-001...005:
- ORC-SEM-ENV-001: Planning phase MUST require valid SemanticEnvelope
- ORC-SEM-ENV-002: Engine MUST reject calls without envelope
- ORC-SEM-ENV-003: Engine MUST verify envelope_validated == True
- ORC-SEM-ENV-004: Bypass attempts MUST emit trace event
- ORC-SEM-ENV-005: Error code MUST be semantic_envelope_required
"""

from __future__ import annotations

import pytest
from typing import Any, Dict, List, Optional

from core.contracts.semantic_schema import (
    Ambiguity,
    NextAction,
    SemanticEnvelope,
    SemanticEnvelopeRequiredError,
    SemanticEnvelopeNotValidatedError,
)
from core.orchestrator.context import RunContext
from core.orchestrator.plan_executor import validate_semantic_envelope


class TestSemanticEnvelopeRequiredError:
    """Tests for SemanticEnvelopeRequiredError exception."""

    def test_error_exists(self) -> None:
        """SemanticEnvelopeRequiredError should exist as an exception."""
        assert issubclass(SemanticEnvelopeRequiredError, Exception)

    def test_error_default_message(self) -> None:
        """SemanticEnvelopeRequiredError should have default message."""
        error = SemanticEnvelopeRequiredError()
        assert "SemanticEnvelope required" in str(error)

    def test_error_custom_message(self) -> None:
        """SemanticEnvelopeRequiredError should accept custom message."""
        error = SemanticEnvelopeRequiredError("Custom error message")
        assert error.message == "Custom error message"
        assert str(error) == "Custom error message"

    def test_error_can_be_raised(self) -> None:
        """SemanticEnvelopeRequiredError should be raisable."""
        with pytest.raises(SemanticEnvelopeRequiredError):
            raise SemanticEnvelopeRequiredError()


class TestSemanticEnvelopeNotValidatedError:
    """Tests for SemanticEnvelopeNotValidatedError exception."""

    def test_error_exists(self) -> None:
        """SemanticEnvelopeNotValidatedError should exist as an exception."""
        assert issubclass(SemanticEnvelopeNotValidatedError, Exception)

    def test_error_default_message(self) -> None:
        """SemanticEnvelopeNotValidatedError should have default message."""
        error = SemanticEnvelopeNotValidatedError()
        assert "validated" in str(error).lower()

    def test_error_custom_message(self) -> None:
        """SemanticEnvelopeNotValidatedError should accept custom message."""
        error = SemanticEnvelopeNotValidatedError("Validation required")
        assert error.message == "Validation required"

    def test_error_can_be_raised(self) -> None:
        """SemanticEnvelopeNotValidatedError should be raisable."""
        with pytest.raises(SemanticEnvelopeNotValidatedError):
            raise SemanticEnvelopeNotValidatedError()


class TestValidateSemanticEnvelope:
    """Tests for validate_semantic_envelope function."""

    def _create_run_context(
        self,
        envelope: Optional[SemanticEnvelope] = None,
        envelope_dict: Optional[Dict[str, Any]] = None,
    ) -> RunContext:
        """Helper to create RunContext with optional envelope."""
        ctx = RunContext(
            run_id="test-run-001",
            product="test_product",
            flow="test_flow",
        )
        if envelope is not None:
            ctx.artifacts["semantic_envelope"] = envelope
        elif envelope_dict is not None:
            ctx.artifacts["semantic_envelope"] = envelope_dict
        return ctx

    def _create_valid_envelope(self, validated: bool = True) -> SemanticEnvelope:
        """Helper to create a valid envelope."""
        return SemanticEnvelope(
            raw_input="test input",
            normalized_input="test input",
            product_id="test_product",
            intent_type="test_intent",
            envelope_validated=validated,
        )

    def test_validate_raises_when_no_envelope_orc_sem_env_001(self) -> None:
        """ORC-SEM-ENV-001: Should raise SemanticEnvelopeRequiredError when no envelope."""
        ctx = self._create_run_context()
        
        with pytest.raises(SemanticEnvelopeRequiredError):
            validate_semantic_envelope(ctx)

    def test_validate_raises_when_envelope_not_validated_orc_sem_env_003(self) -> None:
        """ORC-SEM-ENV-003: Should raise when envelope_validated is False."""
        envelope = self._create_valid_envelope(validated=False)
        ctx = self._create_run_context(envelope=envelope)
        
        with pytest.raises(SemanticEnvelopeNotValidatedError):
            validate_semantic_envelope(ctx)

    def test_validate_returns_envelope_when_valid(self) -> None:
        """Should return envelope when valid and validated."""
        envelope = self._create_valid_envelope(validated=True)
        ctx = self._create_run_context(envelope=envelope)
        
        result = validate_semantic_envelope(ctx)
        
        assert result is not None
        assert result.envelope_validated is True
        assert result.raw_input == "test input"

    def test_validate_accepts_dict_envelope(self) -> None:
        """Should accept envelope as dict and parse it."""
        envelope_dict = {
            "raw_input": "test input",
            "normalized_input": "test input",
            "product_id": "test_product",
            "intent_type": "test_intent",
            "envelope_validated": True,
            "entities": [],
            "constraints": {},
            "ambiguities": [],
            "proposed_next_action": "CONTINUE",
        }
        ctx = self._create_run_context(envelope_dict=envelope_dict)
        
        result = validate_semantic_envelope(ctx)
        
        assert result is not None
        assert result.envelope_validated is True

    def test_validate_emits_bypass_event_when_no_envelope_orc_sem_env_004(self) -> None:
        """ORC-SEM-ENV-004: Should emit envelope_bypass_blocked event when no envelope."""
        ctx = self._create_run_context()
        events: List[Dict[str, Any]] = []
        
        def capture_event(
            kind: str,
            run_id: str,
            step_id: Optional[str],
            product: str,
            flow: str,
            payload: Dict[str, Any],
        ) -> None:
            events.append({
                "kind": kind,
                "run_id": run_id,
                "step_id": step_id,
                "product": product,
                "flow": flow,
                "payload": payload,
            })
        
        with pytest.raises(SemanticEnvelopeRequiredError):
            validate_semantic_envelope(ctx, emit_event_fn=capture_event)
        
        assert len(events) == 1
        assert events[0]["kind"] == "envelope_bypass_blocked"
        assert events[0]["payload"]["error_code"] == "semantic_envelope_required"

    def test_validate_emits_bypass_event_when_not_validated_orc_sem_env_004(self) -> None:
        """ORC-SEM-ENV-004: Should emit bypass event when envelope not validated."""
        envelope = self._create_valid_envelope(validated=False)
        ctx = self._create_run_context(envelope=envelope)
        events: List[Dict[str, Any]] = []
        
        def capture_event(
            kind: str,
            run_id: str,
            step_id: Optional[str],
            product: str,
            flow: str,
            payload: Dict[str, Any],
        ) -> None:
            events.append({
                "kind": kind,
                "payload": payload,
            })
        
        with pytest.raises(SemanticEnvelopeNotValidatedError):
            validate_semantic_envelope(ctx, emit_event_fn=capture_event)
        
        assert len(events) == 1
        assert events[0]["kind"] == "envelope_bypass_blocked"
        assert events[0]["payload"]["error_code"] == "semantic_envelope_not_validated"

    def test_validate_rejects_invalid_envelope_type(self) -> None:
        """Should raise when envelope is invalid type."""
        ctx = self._create_run_context()
        ctx.artifacts["semantic_envelope"] = "not an envelope"
        
        with pytest.raises(SemanticEnvelopeRequiredError) as exc_info:
            validate_semantic_envelope(ctx)
        
        assert "Invalid semantic envelope type" in str(exc_info.value)


class TestSemanticEnvelopeEnforcementFields:
    """Tests for SemanticEnvelope enforcement fields."""

    def test_envelope_has_all_constraints_satisfiable_field(self) -> None:
        """SemanticEnvelope should have all_constraints_satisfiable field."""
        envelope = SemanticEnvelope(
            raw_input="test",
            normalized_input="test",
            product_id="test",
            intent_type="test",
            all_constraints_satisfiable=True,
        )
        assert envelope.all_constraints_satisfiable is True

    def test_envelope_has_envelope_validated_field(self) -> None:
        """SemanticEnvelope should have envelope_validated field."""
        envelope = SemanticEnvelope(
            raw_input="test",
            normalized_input="test",
            product_id="test",
            intent_type="test",
            envelope_validated=True,
        )
        assert envelope.envelope_validated is True

    def test_envelope_has_bypass_attempt_blocked_field(self) -> None:
        """SemanticEnvelope should have bypass_attempt_blocked field."""
        envelope = SemanticEnvelope(
            raw_input="test",
            normalized_input="test",
            product_id="test",
            intent_type="test",
            bypass_attempt_blocked=True,
        )
        assert envelope.bypass_attempt_blocked is True

    def test_envelope_defaults(self) -> None:
        """Enforcement fields should have correct defaults."""
        envelope = SemanticEnvelope(
            raw_input="test",
            normalized_input="test",
            product_id="test",
            intent_type="test",
        )
        assert envelope.all_constraints_satisfiable is True
        assert envelope.envelope_validated is False
        assert envelope.bypass_attempt_blocked is False


class TestPlanningPhaseEnforcement:
    """Tests for planning phase semantic envelope enforcement."""

    def test_error_code_semantic_envelope_required_orc_sem_env_005(self) -> None:
        """ORC-SEM-ENV-005: Error code should be semantic_envelope_required."""
        ctx = RunContext(
            run_id="test-run",
            product="test",
            flow="test",
        )
        events: List[Dict[str, Any]] = []
        
        def capture_event(**kwargs: Any) -> None:
            events.append(kwargs)
        
        with pytest.raises(SemanticEnvelopeRequiredError):
            validate_semantic_envelope(ctx, emit_event_fn=capture_event)
        
        # Verify error code in the emitted event
        assert len(events) >= 1
        event_payload = events[0].get("payload", {})
        assert event_payload.get("error_code") == "semantic_envelope_required"
