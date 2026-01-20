# ==============================
# Tracing Pipeline
# ==============================
"""
Tracing pipeline.

Responsibilities:
- Accept TraceEvent (contract)
- Scrub payload via SecurityRedactor
- Persist via MemoryBackend interface only
- Optionally mirror to logs

No direct sqlite calls here.
"""

from __future__ import annotations


import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from core.contracts.run_schema import TraceEvent
from core.config.schema import Settings
from core.governance.security import SecurityRedactor
from core.memory.base import MemoryBackend


# ==============================
# Trace Event Types
# ==============================
class TraceEventType(str, Enum):
    """
    Standard trace event types for the orchestrator.
    
    Semantic Interpretation Events (ORC-SEM-040...043):
    - SEMANTIC_INTERPRETATION_STARTED: Semantic phase begins
    - SEMANTIC_INTERPRETATION_COMPLETED: Semantic phase succeeds
    - SEMANTIC_VALIDATION_COMPLETED: Envelope validation done
    - SEMANTIC_STOP_ISSUED: NextAction != CONTINUE
    """
    
    # Run lifecycle events
    RUN_STARTED = "run_started"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    RUN_PAUSED = "run_paused"
    RUN_RESUMED = "run_resumed"
    RUN_REJECTED = "run_rejected"
    
    # Step lifecycle events
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    STEP_SKIPPED = "step_skipped"
    
    # Semantic interpretation events (ORC-SEM-040...043)
    SEMANTIC_INTERPRETATION_STARTED = "semantic_interpretation_started"  # ORC-SEM-040
    SEMANTIC_INTERPRETATION_COMPLETED = "semantic_interpretation_completed"  # ORC-SEM-041
    SEMANTIC_INTERPRETATION_FAILED = "semantic_interpretation_failed"
    SEMANTIC_INTERPRETATION_SKIPPED = "semantic_interpretation_skipped"
    SEMANTIC_VALIDATION_COMPLETED = "semantic_validation_completed"  # ORC-SEM-042
    SEMANTIC_STOP_ISSUED = "semantic_stop_issued"  # ORC-SEM-043
    
    # Tool events
    TOOL_CALL_STARTED = "tool_call_started"
    TOOL_CALL_COMPLETED = "tool_call_completed"
    TOOL_CALL_FAILED = "tool_call_failed"
    
    # Agent events
    AGENT_INVOKED = "agent_invoked"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    
    # Governance events
    GOVERNANCE_CHECK = "governance_check"
    BEFORE_STEP_DENIED = "before_step_denied"
    AUTONOMY_DENIED = "autonomy_denied"
    
    # HITL events
    HITL_REQUESTED = "hitl_requested"
    HITL_RESOLVED = "hitl_resolved"
    
    # User input events
    USER_INPUT_REQUESTED = "user_input_requested"
    USER_INPUT_RECEIVED = "user_input_received"

    # Terminal outcome events (IMP-012: ORC-TERM-001..005)
    RUN_TERMINAL_OUTCOME = "run_terminal_outcome"
    
    # Hypothesis selection events (IMP-015: INT-HYP-SEL-001..005)
    HYPOTHESIS_SELECTED = "hypothesis_selected"
    HYPOTHESIS_SELECTION_DEFERRED = "hypothesis_selection_deferred"
    
    # Sufficiency state events (IMP-017: INT-SUFF-LC-001..005)
    SUFFICIENCY_STATE_UPDATED = "sufficiency_state_updated"
    SUFFICIENCY_STATE_RESTORED = "sufficiency_state_restored"
    
    # Reasoning lifecycle events (IMP-009: ORC-REASON-001..005)
    REASONING_PHASE_STARTED = "reasoning_phase_started"
    REASONING_PHASE_COMPLETED = "reasoning_phase_completed"
    REASONING_PHASE_TRANSITION = "reasoning_phase_transition"
    
    # Reasoning phase failure events (IMP-011: ORC-REASON-020..022)
    REASONING_PHASE_FAILED = "reasoning_phase_failed"
    
    # Reasoning termination events (IMP-010: ORC-REASON-010..015)
    REASONING_TERMINATED = "reasoning_terminated"
    
    # Confidence events (IMP-018: INT-CONF-001..005)
    CONFIDENCE_BELOW_THRESHOLD = "confidence_below_threshold"
    CONFIDENCE_AGGREGATED = "confidence_aggregated"
    
    # Confidence threshold events (IMP-019: INT-CONF-THR-001..005)
    CONFIDENCE_THRESHOLD_VIOLATED = "confidence_threshold_violated"
    
    # ContextPack freeze events (IMP-021: INT-CP-FREEZE-LC-001..003)
    CONTEXT_PACK_FROZEN = "context_pack_frozen"
    
    # Self-modification events (IMP-022: GOV-POL-SELFMOD-001..003)
    SELF_MODIFICATION_BLOCKED = "self_modification_blocked"


class Tracer:
    def __init__(
        self,
        *,
        memory: MemoryBackend,
        logger: Optional[logging.Logger] = None,
        redactor: Optional[SecurityRedactor] = None,
        mirror_to_log: bool = True,
    ) -> None:
        self.memory = memory
        self.logger = logger or logging.getLogger("master.trace")
        self.redactor = redactor or SecurityRedactor()
        self.mirror_to_log = mirror_to_log

    def emit(self, event: TraceEvent) -> None:
        sanitized_payload = self.redactor.sanitize(event.payload)
        safe = event.model_copy(
            update={
                "payload": sanitized_payload,
                "redacted": sanitized_payload != event.payload,
            }
        )
        # Persist through backend interface only
        self.memory.append_trace_event(safe)

        if self.mirror_to_log:
            self.logger.info(
                "trace",
                extra={
                    "run_id": safe.run_id,
                    "step_id": safe.step_id,
                    "product": safe.product,
                    "flow": safe.flow,
                    "kind": safe.kind,
                },
            )

    @classmethod
    def from_settings(cls, *, settings: Settings, memory: MemoryBackend) -> "Tracer":
        """
        Convenience constructor for gateway/CLI wiring.
        """
        redactor = SecurityRedactor.from_settings(settings)
        mirror = bool(getattr(settings.logging, "console", True))
        return cls(memory=memory, redactor=redactor, mirror_to_log=mirror)

    # ------------------------------------------------------------------ Semantic Trace Helpers
    def emit_semantic_started(
        self,
        *,
        run_id: str,
        product: str,
        flow: str,
        user_input: str,
    ) -> None:
        """
        Emit SEMANTIC_INTERPRETATION_STARTED event.
        
        ORC-SEM-040: Trace when semantic interpretation begins.
        
        Args:
            run_id: The run identifier
            product: Product name
            flow: Flow name
            user_input: Raw user input (truncated for safety)
        """
        self.emit(TraceEvent(
            kind=TraceEventType.SEMANTIC_INTERPRETATION_STARTED.value,
            run_id=run_id,
            step_id=None,
            product=product,
            flow=flow,
            ts=int(time.time()),
            payload={
                "raw_input": user_input[:500] if user_input else "",
            },
        ))

    def emit_semantic_completed(
        self,
        *,
        run_id: str,
        product: str,
        flow: str,
        envelope_summary: Dict[str, Any],
        duration_ms: int,
    ) -> None:
        """
        Emit SEMANTIC_INTERPRETATION_COMPLETED event.
        
        ORC-SEM-041: Trace when semantic interpretation succeeds.
        
        Args:
            run_id: The run identifier
            product: Product name
            flow: Flow name
            envelope_summary: Summary of envelope (not full envelope for perf)
            duration_ms: Duration in milliseconds
        """
        self.emit(TraceEvent(
            kind=TraceEventType.SEMANTIC_INTERPRETATION_COMPLETED.value,
            run_id=run_id,
            step_id=None,
            product=product,
            flow=flow,
            ts=int(time.time()),
            payload={
                "duration_ms": duration_ms,
                "confidence": envelope_summary.get("confidence"),
                "intent_type": envelope_summary.get("intent_type"),
                "entity_count": envelope_summary.get("entity_count", 0),
                "next_action": envelope_summary.get("proposed_next_action"),
            },
        ))

    def emit_semantic_validation(
        self,
        *,
        run_id: str,
        product: str,
        flow: str,
        is_valid: bool,
        errors: Optional[List[str]] = None,
    ) -> None:
        """
        Emit SEMANTIC_VALIDATION_COMPLETED event.
        
        ORC-SEM-042: Trace envelope validation result.
        
        Args:
            run_id: The run identifier
            product: Product name
            flow: Flow name
            is_valid: Whether validation passed
            errors: List of validation error messages
        """
        self.emit(TraceEvent(
            kind=TraceEventType.SEMANTIC_VALIDATION_COMPLETED.value,
            run_id=run_id,
            step_id=None,
            product=product,
            flow=flow,
            ts=int(time.time()),
            payload={
                "is_valid": is_valid,
                "errors": errors or [],
                "error_count": len(errors) if errors else 0,
            },
        ))

    def emit_semantic_stop(
        self,
        *,
        run_id: str,
        product: str,
        flow: str,
        next_action: str,
        reason: Optional[str] = None,
        ambiguities: Optional[List[str]] = None,
    ) -> None:
        """
        Emit SEMANTIC_STOP_ISSUED event.
        
        ORC-SEM-043: Trace when NextAction != CONTINUE.
        
        Args:
            run_id: The run identifier
            product: Product name
            flow: Flow name
            next_action: The NextAction value (ASK_USER, ABORT, NEEDS_APPROVAL)
            reason: Optional reason for stop
            ambiguities: Optional list of ambiguities
        """
        self.emit(TraceEvent(
            kind=TraceEventType.SEMANTIC_STOP_ISSUED.value,
            run_id=run_id,
            step_id=None,
            product=product,
            flow=flow,
            ts=int(time.time()),
            payload={
                "next_action": next_action,
                "reason": reason,
                "ambiguities": ambiguities or [],
            },
        ))


# ==============================
# Standalone Helper Functions
# ==============================
def emit_semantic_started(
    tracer: Tracer,
    *,
    run_id: str,
    product: str,
    flow: str,
    user_input: str,
) -> None:
    """Convenience wrapper for Tracer.emit_semantic_started."""
    tracer.emit_semantic_started(
        run_id=run_id,
        product=product,
        flow=flow,
        user_input=user_input,
    )


def emit_semantic_completed(
    tracer: Tracer,
    *,
    run_id: str,
    product: str,
    flow: str,
    envelope_summary: Dict[str, Any],
    duration_ms: int,
) -> None:
    """Convenience wrapper for Tracer.emit_semantic_completed."""
    tracer.emit_semantic_completed(
        run_id=run_id,
        product=product,
        flow=flow,
        envelope_summary=envelope_summary,
        duration_ms=duration_ms,
    )


def emit_semantic_validation(
    tracer: Tracer,
    *,
    run_id: str,
    product: str,
    flow: str,
    is_valid: bool,
    errors: Optional[List[str]] = None,
) -> None:
    """Convenience wrapper for Tracer.emit_semantic_validation."""
    tracer.emit_semantic_validation(
        run_id=run_id,
        product=product,
        flow=flow,
        is_valid=is_valid,
        errors=errors,
    )


def emit_semantic_stop(
    tracer: Tracer,
    *,
    run_id: str,
    product: str,
    flow: str,
    next_action: str,
    reason: Optional[str] = None,
    ambiguities: Optional[List[str]] = None,
) -> None:
    """Convenience wrapper for Tracer.emit_semantic_stop."""
    tracer.emit_semantic_stop(
        run_id=run_id,
        product=product,
        flow=flow,
        next_action=next_action,
        reason=reason,
        ambiguities=ambiguities,
    )


# ==============================
# Exports
# ==============================
__all__ = [
    "Tracer",
    "TraceEventType",
    # Semantic trace helpers
    "emit_semantic_started",
    "emit_semantic_completed",
    "emit_semantic_validation",
    "emit_semantic_stop",
]
