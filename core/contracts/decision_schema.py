# ==============================
# Decision Record Schema (IMP-052)
# ==============================
"""
Decision records for capturing and tracing reasoning decisions.

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

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.reasoning_schema import ReasoningPhase


# ==============================
# Error Codes
# ==============================
DECISION_RECORD_INVALID = "DECISION_RECORD_INVALID"
DECISION_NOT_FOUND = "DECISION_NOT_FOUND"
DECISION_CHAIN_EMPTY = "DECISION_CHAIN_EMPTY"


# ==============================
# Decision Type Enum
# ==============================
class DecisionType(str, Enum):
    """
    Types of decisions that can be recorded.
    
    GOV-DEC-RECORD-002: Decision type categorization.
    """
    # Reasoning decisions
    PHASE_TRANSITION = "phase_transition"
    HYPOTHESIS_SELECTION = "hypothesis_selection"
    TOOL_SELECTION = "tool_selection"
    AGENT_DELEGATION = "agent_delegation"
    
    # Governance decisions
    POLICY_CHECK = "policy_check"
    SUFFICIENCY_GATE = "sufficiency_gate"
    CONFIDENCE_GATE = "confidence_gate"
    SECURITY_CHECK = "security_check"
    
    # User interaction decisions
    HITL_APPROVAL = "hitl_approval"
    HITL_REJECTION = "hitl_rejection"
    USER_CLARIFICATION = "user_clarification"
    
    # Termination decisions
    COMPLETION = "completion"
    EARLY_TERMINATION = "early_termination"
    ERROR_RECOVERY = "error_recovery"


# ==============================
# Option Model
# ==============================
@dataclass(frozen=True)
class Option:
    """
    A single option considered during decision-making.
    
    GOV-DEC-RECORD-004: Options considered must be recorded.
    """
    option_id: str
    name: str
    description: str = ""
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert option to dictionary."""
        return {
            "option_id": self.option_id,
            "name": self.name,
            "description": self.description,
            "score": self.score,
            "metadata": dict(self.metadata),
        }


# ==============================
# Decision Record Model
# ==============================
class DecisionRecord(BaseModel):
    """
    Immutable record of a decision made during reasoning.
    
    GOV-DEC-RECORD-001: Each decision point creates a record.
    GOV-DEC-RECORD-002: Includes type, timestamp.
    GOV-DEC-RECORD-003: Tracks run_id, phase context.
    GOV-DEC-RECORD-005: Selected option with rationale.
    GOV-DEC-RECORD-006: Confidence and evidence references.
    GOV-DEC-RECORD-007: Optional approver for HITL.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    decision_id: str = Field(
        default_factory=lambda: str(uuid4())[:8],
        description="Unique decision identifier.",
    )
    decision_type: DecisionType = Field(
        ...,
        description="Type of decision being recorded.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the decision was made.",
    )
    run_id: str = Field(
        ...,
        description="Associated run identifier.",
    )
    phase: Optional[ReasoningPhase] = Field(
        default=None,
        description="Reasoning phase when decision was made.",
    )
    step_index: int = Field(
        default=0,
        ge=0,
        description="Step index within the run.",
    )
    options_considered: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of options that were considered.",
    )
    selected_option: Optional[Dict[str, Any]] = Field(
        default=None,
        description="The option that was selected.",
    )
    selection_rationale: str = Field(
        default="",
        description="Rationale for the selection.",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the decision.",
    )
    evidence_refs: List[str] = Field(
        default_factory=list,
        description="References to evidence supporting the decision.",
    )
    approver: Optional[str] = Field(
        default=None,
        description="Approver identifier for HITL decisions.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the decision.",
    )
    
    @property
    def has_approver(self) -> bool:
        """Check if decision has an approver."""
        return self.approver is not None
    
    @property
    def is_hitl_decision(self) -> bool:
        """Check if this is a HITL-related decision."""
        return self.decision_type in (
            DecisionType.HITL_APPROVAL,
            DecisionType.HITL_REJECTION,
        )
    
    @property
    def options_count(self) -> int:
        """Number of options considered."""
        return len(self.options_considered)
    
    @property
    def has_selection(self) -> bool:
        """Check if an option was selected."""
        return self.selected_option is not None
    
    @property
    def evidence_count(self) -> int:
        """Number of evidence references."""
        return len(self.evidence_refs)
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """
        Convert to trace event payload.
        
        GOV-DEC-RECORD-009: Trace event payload format.
        """
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "run_id": self.run_id,
            "phase": self.phase.value if self.phase else None,
            "step_index": self.step_index,
            "options_count": self.options_count,
            "has_selection": self.has_selection,
            "selection_rationale": self.selection_rationale,
            "confidence": self.confidence,
            "evidence_count": self.evidence_count,
            "has_approver": self.has_approver,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to full dictionary for persistence."""
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "timestamp": self.timestamp.isoformat(),
            "run_id": self.run_id,
            "phase": self.phase.value if self.phase else None,
            "step_index": self.step_index,
            "options_considered": list(self.options_considered),
            "selected_option": dict(self.selected_option) if self.selected_option else None,
            "selection_rationale": self.selection_rationale,
            "confidence": self.confidence,
            "evidence_refs": list(self.evidence_refs),
            "approver": self.approver,
            "metadata": dict(self.metadata),
        }


# ==============================
# Decision Chain Model
# ==============================
@dataclass
class DecisionChain:
    """
    A chain of decisions for a run.
    
    GOV-DEC-RECORD-010: Decisions form a queryable chain.
    """
    run_id: str
    decisions: List[DecisionRecord] = field(default_factory=list)
    
    def add(self, decision: DecisionRecord) -> None:
        """Add a decision to the chain."""
        if decision.run_id != self.run_id:
            raise ValueError(
                f"Decision run_id '{decision.run_id}' does not match "
                f"chain run_id '{self.run_id}'"
            )
        self.decisions.append(decision)
    
    @property
    def length(self) -> int:
        """Number of decisions in the chain."""
        return len(self.decisions)
    
    @property
    def is_empty(self) -> bool:
        """Check if chain is empty."""
        return len(self.decisions) == 0
    
    def filter_by_type(self, decision_type: DecisionType) -> List[DecisionRecord]:
        """Get decisions of a specific type."""
        return [d for d in self.decisions if d.decision_type == decision_type]
    
    def filter_by_phase(self, phase: ReasoningPhase) -> List[DecisionRecord]:
        """Get decisions from a specific phase."""
        return [d for d in self.decisions if d.phase == phase]
    
    def get_latest(self) -> Optional[DecisionRecord]:
        """Get the most recent decision."""
        if not self.decisions:
            return None
        return max(self.decisions, key=lambda d: d.timestamp)
    
    def get_by_id(self, decision_id: str) -> Optional[DecisionRecord]:
        """Get a decision by ID."""
        for d in self.decisions:
            if d.decision_id == decision_id:
                return d
        return None
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert chain to trace payload."""
        return {
            "run_id": self.run_id,
            "decision_count": self.length,
            "decision_types": list(set(d.decision_type.value for d in self.decisions)),
            "phases": list(set(d.phase.value for d in self.decisions if d.phase)),
        }


# ==============================
# Decision Recorder
# ==============================
class DecisionRecorder:
    """
    Records decisions and manages decision chains.
    
    GOV-DEC-RECORD-008: Persist via memory backend.
    GOV-DEC-RECORD-009: Emit decision_recorded event.
    """
    
    def __init__(
        self,
        emit_event_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        persist_fn: Optional[Callable[[DecisionRecord], None]] = None,
    ):
        """
        Initialize decision recorder.
        
        Args:
            emit_event_fn: Function to emit trace events.
            persist_fn: Function to persist decisions.
        """
        self._emit_event_fn = emit_event_fn
        self._persist_fn = persist_fn
        self._chains: Dict[str, DecisionChain] = {}
    
    def _emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Emit a trace event if function is configured."""
        if self._emit_event_fn:
            self._emit_event_fn(event_type, payload)
    
    def record(self, decision: DecisionRecord) -> DecisionRecord:
        """
        Record a decision.
        
        GOV-DEC-RECORD-008: Persist decision.
        GOV-DEC-RECORD-009: Emit decision_recorded event.
        
        Args:
            decision: The decision to record.
            
        Returns:
            The recorded decision.
        """
        # Add to chain
        if decision.run_id not in self._chains:
            self._chains[decision.run_id] = DecisionChain(run_id=decision.run_id)
        self._chains[decision.run_id].add(decision)
        
        # Persist if configured
        if self._persist_fn:
            self._persist_fn(decision)
        
        # Emit trace event
        self._emit_event(
            "decision_recorded",
            decision.to_trace_payload(),
        )
        
        return decision
    
    def create_and_record(
        self,
        decision_type: DecisionType,
        run_id: str,
        phase: Optional[ReasoningPhase] = None,
        step_index: int = 0,
        options: Optional[List[Option]] = None,
        selected: Optional[Option] = None,
        rationale: str = "",
        confidence: float = 1.0,
        evidence_refs: Optional[List[str]] = None,
        approver: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DecisionRecord:
        """
        Create and record a decision in one call.
        
        Args:
            decision_type: Type of decision.
            run_id: Run identifier.
            phase: Current reasoning phase.
            step_index: Step index in run.
            options: Options considered.
            selected: Selected option.
            rationale: Selection rationale.
            confidence: Decision confidence.
            evidence_refs: Evidence references.
            approver: Approver for HITL.
            metadata: Additional metadata.
            
        Returns:
            The recorded decision.
        """
        options_dicts = [o.to_dict() for o in (options or [])]
        selected_dict = selected.to_dict() if selected else None
        
        decision = DecisionRecord(
            decision_type=decision_type,
            run_id=run_id,
            phase=phase,
            step_index=step_index,
            options_considered=options_dicts,
            selected_option=selected_dict,
            selection_rationale=rationale,
            confidence=confidence,
            evidence_refs=evidence_refs or [],
            approver=approver,
            metadata=metadata or {},
        )
        
        return self.record(decision)
    
    def get_chain(self, run_id: str) -> Optional[DecisionChain]:
        """
        Get decision chain for a run.
        
        GOV-DEC-RECORD-010: Query decision chain.
        
        Args:
            run_id: Run identifier.
            
        Returns:
            Decision chain or None.
        """
        return self._chains.get(run_id)
    
    def list_decisions(self, run_id: str) -> List[DecisionRecord]:
        """
        List all decisions for a run.
        
        GOV-DEC-RECORD-010: List decisions.
        
        Args:
            run_id: Run identifier.
            
        Returns:
            List of decisions.
        """
        chain = self._chains.get(run_id)
        if not chain:
            return []
        return list(chain.decisions)
    
    def get_decision(
        self,
        run_id: str,
        decision_id: str,
    ) -> Optional[DecisionRecord]:
        """
        Get a specific decision by ID.
        
        Args:
            run_id: Run identifier.
            decision_id: Decision identifier.
            
        Returns:
            The decision or None.
        """
        chain = self._chains.get(run_id)
        if not chain:
            return None
        return chain.get_by_id(decision_id)


# ==============================
# Factory Functions
# ==============================
def create_option(
    name: str,
    description: str = "",
    score: float = 0.0,
    metadata: Optional[Dict[str, Any]] = None,
) -> Option:
    """
    Factory to create an Option with generated ID.
    
    Args:
        name: Option name.
        description: Option description.
        score: Option score.
        metadata: Additional metadata.
        
    Returns:
        New Option instance.
    """
    return Option(
        option_id=str(uuid4())[:8],
        name=name,
        description=description,
        score=score,
        metadata=metadata or {},
    )


def create_decision_record(
    decision_type: DecisionType,
    run_id: str,
    phase: Optional[ReasoningPhase] = None,
    **kwargs: Any,
) -> DecisionRecord:
    """
    Factory to create a DecisionRecord.
    
    Args:
        decision_type: Type of decision.
        run_id: Run identifier.
        phase: Reasoning phase.
        **kwargs: Additional fields.
        
    Returns:
        New DecisionRecord instance.
    """
    return DecisionRecord(
        decision_type=decision_type,
        run_id=run_id,
        phase=phase,
        **kwargs,
    )
