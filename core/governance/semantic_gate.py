"""
Semantic Gate Implementation (IMP-049)

GOV-GATE-SEM-001...012, GOV-GATE-SUFF-001...006: Semantic gate for envelope validation.

This module provides:
- SemanticGate: Unified gate validating envelope completeness, confidence, and sufficiency
- SemanticGateResult: Structured result with all validation outcomes
- Integration with GateRegistry for pluggable evaluation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from core.contracts.semantic_schema import SemanticEnvelope
from core.contracts.sufficiency_schema import SufficiencyState
from core.governance.gates import BaseGate, GateContext, GateResult


# ============================================================================
# Semantic Gate Result
# ============================================================================


@dataclass(frozen=True)
class SemanticGateResult:
    """
    Structured result from semantic gate evaluation.
    
    GOV-GATE-SEM-001...012: All validation outcomes in one result.
    
    Attributes:
        proceed: True if all validations passed, False otherwise
        envelope_complete: Whether envelope has all required fields
        confidence_passed: Whether confidence threshold passed
        sufficiency_passed: Whether sufficiency state is sufficient
        failures: List of failure reasons
        details: Additional validation details
    """
    proceed: bool
    envelope_complete: bool
    confidence_passed: bool
    sufficiency_passed: bool
    failures: List[str]
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload format."""
        return {
            "proceed": self.proceed,
            "envelope_complete": self.envelope_complete,
            "confidence_passed": self.confidence_passed,
            "sufficiency_passed": self.sufficiency_passed,
            "failures": self.failures,
            "failure_count": len(self.failures),
            "decision": "proceed" if self.proceed else "rejected",
            **self.details,
        }


# ============================================================================
# Semantic Gate
# ============================================================================


class SemanticGate(BaseGate):
    """
    Unified gate for semantic envelope validation.
    
    GOV-GATE-SEM-001...012: Validates:
    - Envelope completeness (all required fields present and valid)
    - Confidence threshold (overall and per-entity)
    - Intent sufficiency (no blocking gaps)
    
    Example:
        >>> gate = SemanticGate()
        >>> envelope = SemanticEnvelope(...)
        >>> result = gate.validate(envelope, sufficiency_state, confidence_threshold=0.7)
        >>> if not result.proceed:
        ...     # Handle gate rejection
    """

    name = "semantic"
    
    def __init__(
        self,
        default_confidence_threshold: float = 0.7,
        default_entity_threshold: float = 0.5,
        emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        """
        Initialize the semantic gate.
        
        Args:
            default_confidence_threshold: Default overall confidence threshold.
            default_entity_threshold: Default per-entity confidence threshold.
            emit_event_fn: Optional function to emit trace events.
        """
        self._default_confidence_threshold = default_confidence_threshold
        self._default_entity_threshold = default_entity_threshold
        self._emit_event = emit_event_fn

    def evaluate(self, context: GateContext) -> GateResult:
        """
        Evaluate the semantic gate from GateContext.
        
        Expects in context.extra:
        - envelope: SemanticEnvelope
        - sufficiency_state: Optional[SufficiencyState]
        - confidence_threshold: Optional[float]
        - entity_threshold: Optional[float]
        """
        envelope = context.extra.get("envelope")
        if envelope is None:
            return self._failure(
                "no_envelope",
                errors=["SemanticEnvelope not provided in context.extra"],
            )
        
        if not isinstance(envelope, SemanticEnvelope):
            return self._failure(
                "invalid_envelope",
                errors=["envelope must be a SemanticEnvelope instance"],
            )
        
        sufficiency_state = context.extra.get("sufficiency_state")
        confidence_threshold = context.extra.get(
            "confidence_threshold", 
            self._default_confidence_threshold,
        )
        entity_threshold = context.extra.get(
            "entity_threshold", 
            self._default_entity_threshold,
        )
        
        result = self.validate(
            envelope=envelope,
            sufficiency_state=sufficiency_state,
            confidence_threshold=confidence_threshold,
            entity_threshold=entity_threshold,
        )
        
        if result.proceed:
            return self._success(result.to_trace_payload())
        
        return self._failure(
            reason="semantic_gate_rejected",
            errors=result.failures,
            details=result.to_trace_payload(),
        )

    def validate(
        self,
        envelope: SemanticEnvelope,
        sufficiency_state: Optional[SufficiencyState] = None,
        confidence_threshold: Optional[float] = None,
        entity_threshold: Optional[float] = None,
    ) -> SemanticGateResult:
        """
        Validate semantic envelope against all gate criteria.
        
        Args:
            envelope: The SemanticEnvelope to validate.
            sufficiency_state: Optional SufficiencyState for sufficiency check.
            confidence_threshold: Confidence threshold (uses default if None).
            entity_threshold: Per-entity threshold (uses default if None).
            
        Returns:
            SemanticGateResult with all validation outcomes.
        """
        threshold = confidence_threshold or self._default_confidence_threshold
        entity_thresh = entity_threshold or self._default_entity_threshold
        
        failures: List[str] = []
        details: Dict[str, Any] = {}
        
        # Validation 1: Envelope completeness
        envelope_complete, completeness_errors = self.validate_envelope_completeness(envelope)
        if not envelope_complete:
            failures.extend(completeness_errors)
        details["completeness_errors"] = completeness_errors
        
        # Validation 2: Confidence threshold
        confidence_passed, confidence_errors = self.validate_confidence_threshold(
            envelope, 
            threshold=threshold, 
            entity_threshold=entity_thresh,
        )
        if not confidence_passed:
            failures.extend(confidence_errors)
        details["confidence_errors"] = confidence_errors
        details["confidence_threshold"] = threshold
        details["entity_threshold"] = entity_thresh
        details["actual_confidence"] = envelope.confidence
        
        # Validation 3: Intent sufficiency (if state provided)
        sufficiency_passed = True
        if sufficiency_state is not None:
            sufficiency_passed, sufficiency_errors = self.validate_intent_sufficiency(
                envelope, 
                sufficiency_state,
            )
            if not sufficiency_passed:
                failures.extend(sufficiency_errors)
            details["sufficiency_errors"] = sufficiency_errors
        else:
            details["sufficiency_errors"] = []
            details["sufficiency_skipped"] = True
        
        proceed = envelope_complete and confidence_passed and sufficiency_passed
        
        # Emit evaluation event
        if self._emit_event:
            self._emit_event("semantic_gate_evaluated", {
                "proceed": proceed,
                "envelope_complete": envelope_complete,
                "confidence_passed": confidence_passed,
                "sufficiency_passed": sufficiency_passed,
                "failure_count": len(failures),
            })
        
        # Emit rejected event if not proceeding
        if not proceed and self._emit_event:
            self._emit_event("semantic_gate_rejected", {
                "failures": failures,
                "envelope_complete": envelope_complete,
                "confidence_passed": confidence_passed,
                "sufficiency_passed": sufficiency_passed,
            })
        
        return SemanticGateResult(
            proceed=proceed,
            envelope_complete=envelope_complete,
            confidence_passed=confidence_passed,
            sufficiency_passed=sufficiency_passed,
            failures=failures,
            details=details,
        )

    def validate_envelope_completeness(
        self,
        envelope: SemanticEnvelope,
        require_validated_flag: bool = False,
    ) -> tuple:
        """
        Validate that envelope has all required fields with valid values.
        
        GOV-GATE-SEM-002: Envelope completeness validation.
        
        Args:
            envelope: The SemanticEnvelope to validate.
            require_validated_flag: If True, require envelope_validated == True.
            
        Returns:
            Tuple of (is_complete, error_messages).
        """
        errors: List[str] = []
        
        # Check required fields are not empty
        if not envelope.raw_input:
            errors.append("raw_input is empty")
        
        if not envelope.normalized_input:
            errors.append("normalized_input is empty")
        
        if not envelope.product_id:
            errors.append("product_id is empty")
        
        if not envelope.intent_type:
            errors.append("intent_type is empty")
        
        # Check for blocking ambiguities
        if envelope.ambiguities:
            blocking_ambiguities = [
                a for a in envelope.ambiguities 
                if a.is_blocking and not a.is_resolved
            ]
            if blocking_ambiguities:
                errors.append(
                    f"Has {len(blocking_ambiguities)} unresolved blocking ambiguities"
                )
        
        # Only check envelope_validated flag if explicitly required
        if require_validated_flag and hasattr(envelope, 'envelope_validated'):
            if not envelope.envelope_validated:
                errors.append("envelope_validated flag is False")
        
        return (len(errors) == 0, errors)

    def validate_confidence_threshold(
        self,
        envelope: SemanticEnvelope,
        threshold: float = 0.7,
        entity_threshold: float = 0.5,
    ) -> tuple:
        """
        Validate that envelope meets confidence thresholds.
        
        GOV-GATE-SEM-003: Confidence threshold validation.
        
        Args:
            envelope: The SemanticEnvelope to validate.
            threshold: Overall confidence threshold.
            entity_threshold: Per-entity confidence threshold.
            
        Returns:
            Tuple of (passed, error_messages).
        """
        errors: List[str] = []
        
        # Check overall confidence
        if envelope.confidence < threshold:
            errors.append(
                f"Confidence {envelope.confidence:.2f} below threshold {threshold:.2f}"
            )
        
        # Check per-entity confidence
        for entity in envelope.entities:
            if entity.confidence < entity_threshold:
                errors.append(
                    f"Entity '{entity.name}' confidence {entity.confidence:.2f} "
                    f"below threshold {entity_threshold:.2f}"
                )
        
        return (len(errors) == 0, errors)

    def validate_intent_sufficiency(
        self,
        envelope: SemanticEnvelope,
        sufficiency_state: SufficiencyState,
    ) -> tuple:
        """
        Validate that intent is sufficiently understood to proceed.
        
        GOV-GATE-SUFF-001...006: Intent sufficiency validation.
        
        Args:
            envelope: The SemanticEnvelope (for context).
            sufficiency_state: The SufficiencyState to check.
            
        Returns:
            Tuple of (passed, error_messages).
        """
        errors: List[str] = []
        
        # Check for blocking gaps
        blocking_gaps = sufficiency_state.get_blocking_gaps()
        if blocking_gaps:
            for gap in blocking_gaps:
                errors.append(f"Blocking gap: {gap.description}")
        
        # Check for blocking unknowns
        blocking_unknowns = sufficiency_state.get_blocking_unknowns()
        if blocking_unknowns:
            for unknown in blocking_unknowns:
                errors.append(f"Blocking unknown: {unknown.question}")
        
        return (len(errors) == 0, errors)


# ============================================================================
# Helper Functions
# ============================================================================


def create_semantic_gate(
    confidence_threshold: float = 0.7,
    entity_threshold: float = 0.5,
    emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
) -> SemanticGate:
    """
    Factory function to create a SemanticGate with configuration.
    
    Args:
        confidence_threshold: Overall confidence threshold.
        entity_threshold: Per-entity confidence threshold.
        emit_event_fn: Optional trace event emission function.
        
    Returns:
        Configured SemanticGate instance.
    """
    return SemanticGate(
        default_confidence_threshold=confidence_threshold,
        default_entity_threshold=entity_threshold,
        emit_event_fn=emit_event_fn,
    )
