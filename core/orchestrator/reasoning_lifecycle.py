# ==============================
# Reasoning Lifecycle Manager
# ==============================
"""
Orchestrator Reasoning Lifecycle Phases.

IMP-009 (ORC-REASON-001..005): Reasoning proceeds through 4 phases
with typed outputs and controlled transitions.

IMP-010 (ORC-REASON-010..015): Bounded reasoning iteration with
configurable limits and budget integration.

IMP-034 (ORC-REASON-CONTRACT-001..011): Reasoning contract enforcement
with mandatory phases and critique waiver support.

This module provides:
- `ReasoningLifecycle`: Core lifecycle manager
- `ReasoningTerminationReason`: Termination reasons enum
- Phase transition validation
- Phase output persistence
- Iteration bounding and termination logic
- Trace event emission
- Reasoning contract validation (IMP-034)

Phases:
1. INTERPRET: Parse user intent, extract entities, identify constraints
2. PROPOSE: Generate hypotheses and action proposals
3. CRITIQUE: Evaluate proposals, identify issues, assess risks
4. RECOMMEND: Select final action with justification
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4

from core.contracts.reasoning_schema import (
    CritiqueOutput,
    InterpretOutput,
    ProposeOutput,
    ReasoningPhase,
    RecommendOutput,
    ReasoningContract,
    ReasoningContractError,
    get_default_reasoning_contract,
)


# ==============================
# Reasoning Termination Reason (IMP-010)
# ==============================
class ReasoningTerminationReason(str, Enum):
    """
    Reasons for reasoning termination.
    
    ORC-REASON-010..015: Bounded reasoning iteration.
    """
    SUFFICIENT = "sufficient"  # Evidence is sufficient
    MAX_ITERATIONS = "max_iterations"  # Hit max_reasoning_iterations
    BUDGET_EXCEEDED = "budget_exceeded"  # Reasoning budget exhausted
    CONFIDENCE_MET = "confidence_met"  # Confidence threshold reached
    USER_CANCELLED = "user_cancelled"  # User requested stop
    ERROR = "error"  # Error during reasoning


# ==============================
# Phase Transition Rules
# ==============================
# Valid transitions between phases
VALID_TRANSITIONS: Dict[Optional[ReasoningPhase], List[ReasoningPhase]] = {
    None: [ReasoningPhase.INTERPRET],  # Initial state can only go to INTERPRET
    ReasoningPhase.INTERPRET: [ReasoningPhase.PROPOSE],
    ReasoningPhase.PROPOSE: [ReasoningPhase.CRITIQUE],
    ReasoningPhase.CRITIQUE: [ReasoningPhase.PROPOSE, ReasoningPhase.RECOMMEND],  # Can loop back or proceed
    ReasoningPhase.RECOMMEND: [],  # Terminal state
}


# ==============================
# Exceptions
# ==============================
class ReasoningLifecycleError(Exception):
    """Base exception for reasoning lifecycle errors."""
    pass


class InvalidPhaseTransitionError(ReasoningLifecycleError):
    """Raised when attempting an invalid phase transition."""
    
    def __init__(
        self,
        from_phase: Optional[ReasoningPhase],
        to_phase: ReasoningPhase,
        reason: str = "",
    ):
        self.from_phase = from_phase
        self.to_phase = to_phase
        self.reason = reason
        from_name = from_phase.value if from_phase else "None"
        msg = f"Invalid transition from {from_name} to {to_phase.value}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class RecommendWithoutCritiqueError(ReasoningLifecycleError):
    """
    Raised when RECOMMEND phase is attempted without CRITIQUE pass.
    
    ORC-REASON-005: RECOMMEND blocked without CRITIQUE pass.
    """
    
    def __init__(self):
        super().__init__(
            "Cannot transition to RECOMMEND phase without completing CRITIQUE phase first"
        )


# ==============================
# Phase Output Type
# ==============================
PhaseOutput = Union[InterpretOutput, ProposeOutput, CritiqueOutput, RecommendOutput]


# ==============================
# Phase Transition Record
# ==============================
@dataclass(frozen=True)
class PhaseTransitionRecord:
    """
    Record of a phase transition.
    
    ORC-REASON-002: Phase transitions logged via trace events.
    """
    from_phase: Optional[ReasoningPhase]
    to_phase: ReasoningPhase
    timestamp: datetime
    iteration: int
    transition_id: str = field(default_factory=lambda: str(uuid4()))
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload."""
        return {
            "transition_id": self.transition_id,
            "from_phase": self.from_phase.value if self.from_phase else None,
            "to_phase": self.to_phase.value,
            "timestamp": self.timestamp.isoformat(),
            "iteration": self.iteration,
        }


# ==============================
# Reasoning Lifecycle
# ==============================
class ReasoningLifecycle:
    """
    Manager for reasoning lifecycle phases.
    
    ORC-REASON-001..005: 4-phase reasoning with controlled transitions.
    ORC-REASON-CONTRACT-001..011: Contract enforcement (IMP-034).
    
    Example:
        >>> lifecycle = ReasoningLifecycle(run_id="run-123")
        >>> lifecycle.transition_to(ReasoningPhase.INTERPRET)
        >>> lifecycle.set_phase_output(interpret_output)
        >>> lifecycle.transition_to(ReasoningPhase.PROPOSE)
    """
    
    def __init__(
        self,
        run_id: str = "",
        max_iterations: int = 3,
        contract: Optional[ReasoningContract] = None,
        emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        """
        Initialize reasoning lifecycle.
        
        Args:
            run_id: Associated run ID.
            max_iterations: Maximum reasoning iterations (default: 3).
            contract: Optional reasoning contract. Default contract requires all phases.
            emit_event_fn: Optional function to emit trace events.
        """
        self._run_id = run_id or str(uuid4())
        self._max_iterations = min(max(max_iterations, 1), 10)  # Clamp 1-10
        self._current_phase: Optional[ReasoningPhase] = None
        self._iteration: int = 0
        self._critique_completed: bool = False
        self._phase_outputs: Dict[ReasoningPhase, PhaseOutput] = {}
        self._transitions: List[PhaseTransitionRecord] = []
        self._started_at: Optional[datetime] = None
        self._completed_at: Optional[datetime] = None
        # IMP-010: Termination state
        self._terminated: bool = False
        self._termination_reason: Optional[ReasoningTerminationReason] = None
        self._final_confidence: float = 0.0
        # IMP-034: Reasoning contract
        self._contract: ReasoningContract = contract or get_default_reasoning_contract()
        self._emit_event_fn = emit_event_fn
        self._critique_waived_emitted: bool = False
        self._budget_consumed: float = 0.0
    
    @property
    def run_id(self) -> str:
        """Associated run ID."""
        return self._run_id
    
    @property
    def current_phase(self) -> Optional[ReasoningPhase]:
        """Current reasoning phase."""
        return self._current_phase
    
    @property
    def iteration(self) -> int:
        """Current iteration count."""
        return self._iteration
    
    @property
    def max_iterations(self) -> int:
        """Maximum iterations allowed."""
        return self._max_iterations
    
    @property
    def is_complete(self) -> bool:
        """Check if reasoning is complete (reached RECOMMEND)."""
        return self._current_phase == ReasoningPhase.RECOMMEND
    
    @property
    def is_terminated(self) -> bool:
        """Check if reasoning has been terminated (IMP-010)."""
        return self._terminated
    
    @property
    def termination_reason(self) -> Optional[ReasoningTerminationReason]:
        """Get termination reason if terminated (IMP-010)."""
        return self._termination_reason
    
    @property
    def final_confidence(self) -> float:
        """Get final confidence at termination (IMP-010)."""
        return self._final_confidence
    
    @property
    def budget_consumed(self) -> float:
        """Get total budget consumed (IMP-010)."""
        return self._budget_consumed
    
    @property
    def has_reached_max_iterations(self) -> bool:
        """Check if max iterations reached (IMP-010: ORC-REASON-012)."""
        return self._iteration >= self._max_iterations
    
    @property
    def critique_completed(self) -> bool:
        """Check if CRITIQUE phase has been completed at least once."""
        return self._critique_completed
    
    @property
    def phase_outputs(self) -> Dict[ReasoningPhase, PhaseOutput]:
        """Get all phase outputs (read-only copy)."""
        return dict(self._phase_outputs)
    
    # ==============================
    # IMP-034: Contract Properties
    # ==============================
    @property
    def contract(self) -> ReasoningContract:
        """Get the reasoning contract for this lifecycle."""
        return self._contract
    
    @property
    def critique_waiver(self) -> bool:
        """Check if critique phase is waived (IMP-034)."""
        return self._contract.critique_waiver
    
    @property
    def critique_required(self) -> bool:
        """Check if critique phase is required (not waived)."""
        return not self._contract.critique_waiver
    
    @property
    def transitions(self) -> List[PhaseTransitionRecord]:
        """Get all transition records (read-only copy)."""
        return list(self._transitions)
    
    def can_transition(
        self,
        to_phase: ReasoningPhase,
    ) -> bool:
        """
        Check if transition to phase is valid.
        
        ORC-REASON-CONTRACT-003: RECOMMEND requires prior CRITIQUE unless waived.
        
        Args:
            to_phase: Target phase.
            
        Returns:
            True if transition is valid.
        """
        valid_targets = VALID_TRANSITIONS.get(self._current_phase, [])
        if to_phase not in valid_targets:
            # IMP-034: Allow PROPOSE -> RECOMMEND if critique is waived
            if (
                to_phase == ReasoningPhase.RECOMMEND
                and self._current_phase == ReasoningPhase.PROPOSE
                and self._contract.critique_waiver
            ):
                return True
            return False
        
        # Special check: RECOMMEND requires CRITIQUE (unless waived)
        if to_phase == ReasoningPhase.RECOMMEND:
            if self._contract.critique_waiver:
                return True  # Waiver allows skipping CRITIQUE
            if not self._critique_completed:
                return False
        
        return True
    
    def transition_to(
        self,
        phase: ReasoningPhase,
    ) -> PhaseTransitionRecord:
        """
        Transition to a new phase.
        
        ORC-REASON-002: Transitions logged via trace events.
        ORC-REASON-005: RECOMMEND blocked without CRITIQUE.
        ORC-REASON-CONTRACT-003: Waiver allows skipping CRITIQUE (IMP-034).
        
        Args:
            phase: Target phase.
            
        Returns:
            PhaseTransitionRecord for the transition.
            
        Raises:
            InvalidPhaseTransitionError: If transition is invalid.
            RecommendWithoutCritiqueError: If RECOMMEND attempted without CRITIQUE (and no waiver).
        """
        # Check valid transition
        valid_targets = VALID_TRANSITIONS.get(self._current_phase, [])
        
        # IMP-034: Allow PROPOSE -> RECOMMEND if critique is waived
        is_waiver_transition = (
            phase == ReasoningPhase.RECOMMEND
            and self._current_phase == ReasoningPhase.PROPOSE
            and self._contract.critique_waiver
        )
        
        if phase not in valid_targets and not is_waiver_transition:
            raise InvalidPhaseTransitionError(
                from_phase=self._current_phase,
                to_phase=phase,
                reason=f"Valid targets from {self._current_phase}: {[p.value for p in valid_targets]}",
            )
        
        # Special check: RECOMMEND requires CRITIQUE (unless waived)
        if phase == ReasoningPhase.RECOMMEND and not self._critique_completed:
            if not self._contract.critique_waiver:
                raise RecommendWithoutCritiqueError()
            # Emit waiver event (once per lifecycle)
            if not self._critique_waived_emitted and self._emit_event_fn:
                self._emit_event_fn(
                    "critique_phase_waived",
                    {
                        "run_id": self._run_id,
                        "waiver_reason": self._contract.waiver_reason,
                        "from_phase": self._current_phase.value if self._current_phase else None,
                        "to_phase": phase.value,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )
                self._critique_waived_emitted = True
        
        # Record start time on first transition
        if self._started_at is None:
            self._started_at = datetime.now(timezone.utc)
        
        # Increment iteration when looping back to PROPOSE
        if self._current_phase == ReasoningPhase.CRITIQUE and phase == ReasoningPhase.PROPOSE:
            self._iteration += 1
        
        # Record transition
        record = PhaseTransitionRecord(
            from_phase=self._current_phase,
            to_phase=phase,
            timestamp=datetime.now(timezone.utc),
            iteration=self._iteration,
        )
        self._transitions.append(record)
        
        # Update state
        previous_phase = self._current_phase
        self._current_phase = phase
        
        # Track completion of phases
        if phase == ReasoningPhase.RECOMMEND:
            self._completed_at = datetime.now(timezone.utc)
        
        return record
    
    def set_phase_output(
        self,
        output: PhaseOutput,
    ) -> None:
        """
        Set output for current phase.
        
        ORC-REASON-003: Each phase produces typed output artifact.
        ORC-REASON-004: Phase outputs persisted before transition.
        Args:
            output: Typed output for current phase.
            
        Raises:
            ReasoningLifecycleError: If no current phase or wrong output type.
        """
        if self._current_phase is None:
            raise ReasoningLifecycleError("Cannot set output: no current phase")
        
        # Validate output type matches phase
        expected_types = {
            ReasoningPhase.INTERPRET: InterpretOutput,
            ReasoningPhase.PROPOSE: ProposeOutput,
            ReasoningPhase.CRITIQUE: CritiqueOutput,
            ReasoningPhase.RECOMMEND: RecommendOutput,
        }
        expected_type = expected_types.get(self._current_phase)
        if expected_type and not isinstance(output, expected_type):
            raise ReasoningLifecycleError(
                f"Expected {expected_type.__name__} for {self._current_phase.value} phase, "
                f"got {type(output).__name__}"
            )
        
        self._phase_outputs[self._current_phase] = output
        
        # Track CRITIQUE completion
        if self._current_phase == ReasoningPhase.CRITIQUE:
            self._critique_completed = True
    
    def get_phase_output(
        self,
        phase: ReasoningPhase,
    ) -> Optional[PhaseOutput]:
        """
        Get output for a specific phase.
        
        Args:
            phase: Phase to get output for.
            
        Returns:
            Phase output or None if not set.
        """
        return self._phase_outputs.get(phase)
    
    def has_phase_output(self, phase: ReasoningPhase) -> bool:
        """Check if phase has output set."""
        return phase in self._phase_outputs
    
    # ==============================
    # Termination Methods (IMP-010)
    # ==============================
    def should_terminate(self) -> bool:
        """
        Check if reasoning should terminate.
        
        ORC-REASON-012: Deterministic termination at max iterations.
        
        Returns:
            True if should terminate, False otherwise.
        """
        if self._terminated:
            return True
        if self.has_reached_max_iterations:
            return True
        if self.is_complete:
            return True
        return False
    
    def terminate(
        self,
        reason: ReasoningTerminationReason,
        final_confidence: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Terminate the reasoning lifecycle.
        
        ORC-REASON-013..015: Controlled termination with reason tracking.
        
        Args:
            reason: Why reasoning is terminating.
            final_confidence: Final confidence level achieved.
            
        Returns:
            Termination payload for trace event.
        """
        self._terminated = True
        self._termination_reason = reason
        self._final_confidence = final_confidence
        self._completed_at = datetime.now(timezone.utc)
        
        return self.get_termination_payload()
    
    def get_termination_payload(self) -> Dict[str, Any]:
        """
        Get payload for reasoning_terminated trace event.
        
        ORC-REASON-014: reasoning_terminated event with correct payload.
        
        Returns:
            Dict with iteration_count, reason, final_confidence.
        """
        return {
            "run_id": self._run_id,
            "iteration_count": self._iteration,
            "reason": self._termination_reason.value if self._termination_reason else None,
            "final_confidence": self._final_confidence,
            "budget_consumed": self._budget_consumed,
            "phases_completed": [p.value for p in self._phase_outputs.keys()],
            "is_complete": self.is_complete,
            "terminated_at": self._completed_at.isoformat() if self._completed_at else None,
        }
    
    # ==============================
    # Event Payload Methods (IMP-011)
    # ==============================
    def get_phase_started_payload(
        self,
        input_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get payload for reasoning_phase_started trace event.
        
        ORC-REASON-020: reasoning_phase_started event with correct payload.
        
        Args:
            input_hash: Hash of input data for this phase.
            
        Returns:
            Dict with phase_name, iteration, input_hash.
        """
        return {
            "run_id": self._run_id,
            "phase_name": self._current_phase.value if self._current_phase else None,
            "iteration": self._iteration,
            "input_hash": input_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def get_phase_completed_payload(
        self,
        output_hash: Optional[str] = None,
        confidence: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Get payload for reasoning_phase_completed trace event.
        
        ORC-REASON-021: reasoning_phase_completed event with correct payload.
        
        Args:
            output_hash: Hash of output data from this phase.
            confidence: Confidence level of phase output.
            
        Returns:
            Dict with phase_name, iteration, output_hash, confidence.
        """
        return {
            "run_id": self._run_id,
            "phase_name": self._current_phase.value if self._current_phase else None,
            "iteration": self._iteration,
            "output_hash": output_hash,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def get_phase_failed_payload(
        self,
        error_code: str,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Get payload for reasoning_phase_failed trace event.
        
        ORC-REASON-022: reasoning_phase_failed event with correct payload.
        
        Args:
            error_code: Error code for the failure.
            reason: Human-readable failure reason.
            
        Returns:
            Dict with phase_name, iteration, error_code, reason.
        """
        return {
            "run_id": self._run_id,
            "phase_name": self._current_phase.value if self._current_phase else None,
            "iteration": self._iteration,
            "error_code": error_code,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def consume_iteration_budget(self, amount: float = 1.0) -> float:
        """
        Consume budget for an iteration.
        
        ORC-REASON-011: Each iteration consumes reasoning budget.
        
        Args:
            amount: Budget amount to consume.
            
        Returns:
            Total budget consumed.
        """
        self._budget_consumed += amount
        return self._budget_consumed
    
    def check_and_terminate_if_needed(
        self,
        budget_remaining: Optional[float] = None,
        confidence_threshold: Optional[float] = None,
        current_confidence: float = 0.0,
    ) -> Optional[ReasoningTerminationReason]:
        """
        Check termination conditions and terminate if needed.
        
        ORC-REASON-010..015: Bounded reasoning iteration.
        
        Args:
            budget_remaining: Remaining budget (if None, not checked).
            confidence_threshold: Confidence threshold to meet (if None, not checked).
            current_confidence: Current confidence level.
            
        Returns:
            ReasoningTerminationReason if terminated, None otherwise.
        """
        if self._terminated:
            return self._termination_reason
        
        # Check max iterations (ORC-REASON-012)
        if self.has_reached_max_iterations:
            self.terminate(ReasoningTerminationReason.MAX_ITERATIONS, current_confidence)
            return ReasoningTerminationReason.MAX_ITERATIONS
        
        # Check budget (ORC-REASON-011)
        if budget_remaining is not None and budget_remaining <= 0:
            self.terminate(ReasoningTerminationReason.BUDGET_EXCEEDED, current_confidence)
            return ReasoningTerminationReason.BUDGET_EXCEEDED
        
        # Check confidence threshold
        if confidence_threshold is not None and current_confidence >= confidence_threshold:
            self.terminate(ReasoningTerminationReason.CONFIDENCE_MET, current_confidence)
            return ReasoningTerminationReason.CONFIDENCE_MET
        
        return None

    def get_summary(self) -> Dict[str, Any]:
        """Get lifecycle summary for diagnostics."""
        return {
            "run_id": self._run_id,
            "current_phase": self._current_phase.value if self._current_phase else None,
            "iteration": self._iteration,
            "max_iterations": self._max_iterations,
            "is_complete": self.is_complete,
            "is_terminated": self._terminated,
            "termination_reason": self._termination_reason.value if self._termination_reason else None,
            "final_confidence": self._final_confidence,
            "budget_consumed": self._budget_consumed,
            "critique_completed": self._critique_completed,
            "phases_completed": [p.value for p in self._phase_outputs.keys()],
            "transition_count": len(self._transitions),
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "completed_at": self._completed_at.isoformat() if self._completed_at else None,
        }
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert lifecycle state to serializable dict for persistence.
        
        Returns:
            Dict with all state for restoration.
        """
        return {
            "run_id": self._run_id,
            "max_iterations": self._max_iterations,
            "current_phase": self._current_phase.value if self._current_phase else None,
            "iteration": self._iteration,
            "critique_completed": self._critique_completed,
            "terminated": self._terminated,
            "termination_reason": self._termination_reason.value if self._termination_reason else None,
            "final_confidence": self._final_confidence,
            "budget_consumed": self._budget_consumed,
            "phase_outputs": {
                phase.value: output.model_dump()
                for phase, output in self._phase_outputs.items()
            },
            "transitions": [t.to_trace_payload() for t in self._transitions],
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "completed_at": self._completed_at.isoformat() if self._completed_at else None,
            # IMP-034: Include contract info
            "contract": self._contract.to_trace_payload(),
        }
    
    @classmethod
    def from_serializable(
        cls,
        data: Dict[str, Any],
        emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> "ReasoningLifecycle":
        """
        Restore lifecycle from serialized data.
        
        Args:
            data: Serialized lifecycle data.
            emit_event_fn: Optional function to emit trace events.
            
        Returns:
            Restored ReasoningLifecycle instance.
        """
        # IMP-034: Restore contract if present
        contract = None
        if data.get("contract"):
            contract_data = data["contract"]
            # Handle waiver_reason being None (serialized when critique_waiver=False)
            waiver_reason = contract_data.get("waiver_reason")
            if waiver_reason is None:
                waiver_reason = ""
            contract = ReasoningContract(
                critique_waiver=contract_data.get("critique_waiver", False),
                waiver_reason=waiver_reason,
            )
        
        lifecycle = cls(
            run_id=data.get("run_id", ""),
            max_iterations=data.get("max_iterations", 3),
            contract=contract,
            emit_event_fn=emit_event_fn,
        )
        
        # Restore state
        if data.get("current_phase"):
            lifecycle._current_phase = ReasoningPhase(data["current_phase"])
        lifecycle._iteration = data.get("iteration", 0)
        lifecycle._critique_completed = data.get("critique_completed", False)
        
        # Restore termination state (IMP-010)
        lifecycle._terminated = data.get("terminated", False)
        if data.get("termination_reason"):
            lifecycle._termination_reason = ReasoningTerminationReason(data["termination_reason"])
        lifecycle._final_confidence = data.get("final_confidence", 0.0)
        lifecycle._budget_consumed = data.get("budget_consumed", 0.0)
        
        # Restore phase outputs
        output_types = {
            "interpret": InterpretOutput,
            "propose": ProposeOutput,
            "critique": CritiqueOutput,
            "recommend": RecommendOutput,
        }
        for phase_str, output_data in data.get("phase_outputs", {}).items():
            phase = ReasoningPhase(phase_str)
            output_cls = output_types.get(phase_str)
            if output_cls:
                lifecycle._phase_outputs[phase] = output_cls.model_validate(output_data)
        
        # Restore timestamps
        if data.get("started_at"):
            lifecycle._started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            lifecycle._completed_at = datetime.fromisoformat(data["completed_at"])
        
        return lifecycle
