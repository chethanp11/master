# ==============================
# Sufficiency Manager
# ==============================
"""
SufficiencyState lifecycle management.

IMP-017 (INT-SUFF-LC-001..005): Manage sufficiency state throughout reasoning.

This module provides:
- `SufficiencyManager`: Core manager class for state lifecycle
- Evidence integration and unknown/gap resolution
- Persistence and restoration of state

Lifecycle:
1. Initialize with empty or restored state
2. Update with evidence after each reasoning pass
3. Resolve unknowns/gaps as evidence arrives
4. Check sufficiency before proceeding
5. Persist after each update
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable
from uuid import uuid4

from core.contracts.sufficiency_schema import (
    Assumption,
    Fact,
    Gap,
    Importance,
    SufficiencyState,
    Unknown,
    Priority,
)


# ==============================
# Evidence Item
# ==============================
@dataclass
class EvidenceItem:
    """
    Evidence item used to update sufficiency state.
    
    An evidence item can establish facts, resolve unknowns, or fill gaps.
    """
    source: str
    description: str
    confidence: float = 1.0
    evidence_ref: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_fact(self) -> Fact:
        """Convert evidence item to a Fact."""
        return Fact(
            description=self.description,
            confidence=self.confidence,
            evidence_ref=self.evidence_ref,
        )


# ==============================
# State Diff
# ==============================
@dataclass
class SufficiencyStateDiff:
    """
    Diff between two sufficiency states for trace events.
    
    INT-SUFF-LC-002: Track changes for observability.
    """
    facts_added: int = 0
    unknowns_resolved: int = 0
    gaps_resolved: int = 0
    assumptions_added: int = 0
    new_unknowns: int = 0
    new_gaps: int = 0
    is_now_sufficient: bool = False
    was_sufficient: bool = False
    
    def to_trace_payload(self) -> Dict[str, Any]:
        """Convert to trace event payload."""
        return {
            "facts_added": self.facts_added,
            "unknowns_resolved": self.unknowns_resolved,
            "gaps_resolved": self.gaps_resolved,
            "assumptions_added": self.assumptions_added,
            "new_unknowns": self.new_unknowns,
            "new_gaps": self.new_gaps,
            "is_now_sufficient": self.is_now_sufficient,
            "was_sufficient": self.was_sufficient,
            "changed": self.has_changes(),
        }
    
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return (
            self.facts_added > 0
            or self.unknowns_resolved > 0
            or self.gaps_resolved > 0
            or self.assumptions_added > 0
            or self.new_unknowns > 0
            or self.new_gaps > 0
        )


# ==============================
# Sufficiency Manager
# ==============================
class SufficiencyManager:
    """
    Manager for SufficiencyState lifecycle.
    
    INT-SUFF-LC-001..005: Full lifecycle management.
    
    Example:
        >>> manager = SufficiencyManager(run_id="run-123")
        >>> evidence = EvidenceItem(source="tool", description="User is verified")
        >>> state = manager.update_with_evidence([evidence])
        >>> manager.is_sufficient()
        True
    """
    
    def __init__(
        self,
        run_id: str = "",
        initial_state: Optional[SufficiencyState] = None,
    ) -> None:
        """
        Initialize manager with optional initial state.
        
        Args:
            run_id: Run ID for new state (ignored if initial_state provided).
            initial_state: Existing state to restore (for resume).
        """
        if initial_state:
            self._state = initial_state
        else:
            self._state = SufficiencyState(run_id=run_id or "default")
        self._update_count = 0
    
    @property
    def state(self) -> SufficiencyState:
        """Current sufficiency state."""
        return self._state
    
    @property
    def update_count(self) -> int:
        """Number of updates applied."""
        return self._update_count
    
    def update_with_evidence(
        self,
        evidence: List[EvidenceItem],
    ) -> SufficiencyStateDiff:
        """
        Update state with new evidence.
        
        INT-SUFF-LC-001: Evidence updates facts.
        
        Args:
            evidence: List of evidence items to add.
            
        Returns:
            SufficiencyStateDiff showing what changed.
        """
        was_sufficient = self.is_sufficient()
        facts_added = 0
        
        for item in evidence:
            fact = item.to_fact()
            self._state.add_fact(fact)
            facts_added += 1
        
        self._update_count += 1
        
        return SufficiencyStateDiff(
            facts_added=facts_added,
            was_sufficient=was_sufficient,
            is_now_sufficient=self.is_sufficient(),
        )
    
    def resolve_unknown(
        self,
        unknown_id: str,
        evidence: EvidenceItem,
    ) -> SufficiencyStateDiff:
        """
        Resolve an unknown with evidence.
        
        INT-SUFF-LC-001: Resolving unknowns.
        
        Args:
            unknown_id: ID of unknown to resolve.
            evidence: Evidence that resolves the unknown.
            
        Returns:
            SufficiencyStateDiff showing what changed.
        """
        was_sufficient = self.is_sufficient()
        
        # Add fact from evidence
        fact = evidence.to_fact()
        self._state.add_fact(fact)
        
        # Remove the unknown
        self._state.resolve_unknown(unknown_id)
        
        self._update_count += 1
        
        return SufficiencyStateDiff(
            facts_added=1,
            unknowns_resolved=1,
            was_sufficient=was_sufficient,
            is_now_sufficient=self.is_sufficient(),
        )
    
    def resolve_gap(
        self,
        gap_id: str,
        evidence: EvidenceItem,
    ) -> SufficiencyStateDiff:
        """
        Resolve a gap with evidence.
        
        INT-SUFF-LC-001: Resolving gaps.
        
        Args:
            gap_id: ID of gap to resolve.
            evidence: Evidence that fills the gap.
            
        Returns:
            SufficiencyStateDiff showing what changed.
        """
        was_sufficient = self.is_sufficient()
        
        # Add fact from evidence
        fact = evidence.to_fact()
        self._state.add_fact(fact)
        
        # Remove the gap
        self._state.resolve_gap(gap_id)
        
        self._update_count += 1
        
        return SufficiencyStateDiff(
            facts_added=1,
            gaps_resolved=1,
            was_sufficient=was_sufficient,
            is_now_sufficient=self.is_sufficient(),
        )
    
    def add_unknown(
        self,
        question: str,
        *,
        importance: Importance = Importance.MEDIUM,
        blocking: bool = True,
    ) -> Unknown:
        """
        Add a new unknown to the state.
        
        Args:
            question: The question/unknown to track.
            importance: Importance level.
            blocking: Whether this blocks progress.
            
        Returns:
            The created Unknown.
        """
        unknown = Unknown(
            question=question,
            importance=importance,
            blocking=blocking,
        )
        self._state.add_unknown(unknown)
        return unknown
    
    def add_gap(
        self,
        description: str,
        *,
        priority: Priority = Priority.MEDIUM,
        blocking: bool = True,
    ) -> Gap:
        """
        Add a new gap to the state.
        
        Args:
            description: Description of the gap.
            priority: Priority level.
            blocking: Whether this blocks progress.
            
        Returns:
            The created Gap.
        """
        gap = Gap(
            description=description,
            priority=priority,
            blocking=blocking,
        )
        self._state.add_gap(gap)
        return gap
    
    def add_assumption(
        self,
        description: str,
        *,
        confidence: float = 0.5,
        evidence_ref: Optional[str] = None,
    ) -> Assumption:
        """
        Add a new assumption to the state.
        
        Args:
            description: Description of the assumption.
            confidence: Confidence level.
            evidence_ref: Reference to supporting evidence.
            
        Returns:
            The created Assumption.
        """
        assumption = Assumption(
            description=description,
            confidence=confidence,
            evidence_ref=evidence_ref,
        )
        self._state.add_assumption(assumption)
        return assumption
    
    def is_sufficient(self) -> bool:
        """
        Check if state is sufficient for proceeding.
        
        INT-SUFF-LC-005: Run proceeds only if sufficient.
        
        Returns:
            True if no blocking gaps/unknowns exist.
        """
        # Check for any blocking unknowns
        if any(u.blocking for u in self._state.unknowns):
            return False
        # Check for any blocking gaps
        if any(g.blocking for g in self._state.gaps):
            return False
        return True
    
    def has_blocking_issues(self) -> bool:
        """Check if there are any blocking issues."""
        return not self.is_sufficient()
    
    def get_blocking_issues_summary(self) -> Dict[str, Any]:
        """Get summary of blocking issues."""
        return {
            "blocking_unknowns": [
                {"id": u.id, "question": u.question}
                for u in self._state.get_blocking_unknowns()
            ],
            "blocking_gaps": [
                {"id": g.id, "description": g.description}
                for g in self._state.get_blocking_gaps()
            ],
            "total_blocking": (
                len(self._state.get_blocking_unknowns())
                + len(self._state.get_blocking_gaps())
            ),
        }
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert state to serializable dict for persistence.
        
        INT-SUFF-LC-003: Persist state.
        """
        return self._state.model_dump()
    
    @classmethod
    def from_serializable(
        cls,
        data: Dict[str, Any],
    ) -> "SufficiencyManager":
        """
        Restore manager from serialized state.
        
        INT-SUFF-LC-004: Restore state.
        
        Args:
            data: Serialized state dict.
            
        Returns:
            SufficiencyManager with restored state.
        """
        state = SufficiencyState.model_validate(data)
        return cls(initial_state=state)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get current state summary."""
        summary = self._state.to_summary()
        summary["is_sufficient"] = self.is_sufficient()
        summary["update_count"] = self._update_count
        return summary


# ==============================
# Utility Functions
# ==============================
def create_sufficiency_manager_from_context(
    context_data: Optional[Dict[str, Any]] = None,
) -> SufficiencyManager:
    """
    Create a SufficiencyManager from context data.
    
    Args:
        context_data: Optional context containing sufficiency_state.
        
    Returns:
        SufficiencyManager (new or restored).
    """
    if context_data and "sufficiency_state" in context_data:
        return SufficiencyManager.from_serializable(context_data["sufficiency_state"])
    return SufficiencyManager()


def check_sufficiency_for_proceed(
    manager: SufficiencyManager,
) -> tuple[bool, str]:
    """
    Check if run can proceed based on sufficiency.
    
    INT-SUFF-LC-005: Run proceeds only if sufficient.
    
    Args:
        manager: SufficiencyManager to check.
        
    Returns:
        Tuple of (can_proceed, reason).
    """
    if manager.is_sufficient():
        return (True, "Sufficiency check passed")
    
    issues = manager.get_blocking_issues_summary()
    reason_parts = []
    
    if issues["blocking_unknowns"]:
        reason_parts.append(
            f"{len(issues['blocking_unknowns'])} blocking unknowns"
        )
    if issues["blocking_gaps"]:
        reason_parts.append(
            f"{len(issues['blocking_gaps'])} blocking gaps"
        )
    
    reason = f"Cannot proceed: {', '.join(reason_parts)}"
    return (False, reason)
