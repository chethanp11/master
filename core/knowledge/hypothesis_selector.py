# ==============================
# Hypothesis Selector
# ==============================
"""
Hypothesis selection logic for the reasoning system.

IMP-015 (INT-HYP-SEL-001..005): Select best hypothesis from a set.

This module provides:
- `select_hypothesis`: Core selection function
- `HypothesisRejection`: Rejection reason tracking
- `HypothesisSelectionResult`: Full selection result with audit trail

Selection algorithm:
1. Sort hypotheses by confidence descending
2. If top 2 hypotheses are within `confidence_margin`, return None (ASK_USER)
3. Otherwise return highest confidence hypothesis
4. Record rejection reasons for non-selected hypotheses
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from core.contracts.hypothesis_schema import Hypothesis, HypothesisSet


# ==============================
# Rejection Reason
# ==============================
@dataclass(frozen=True)
class HypothesisRejection:
    """
    Record of why a hypothesis was not selected.
    
    INT-HYP-SEL-004: Store rejection reasons for each non-selected hypothesis.
    """
    hypothesis_id: str
    reason: str
    confidence: float
    rank: int  # 1-indexed rank in sorted list


# ==============================
# Selection Result
# ==============================
@dataclass
class HypothesisSelectionResult:
    """
    Complete result of hypothesis selection including audit trail.
    
    INT-HYP-SEL-001..005: Full selection result with alternatives and rejections.
    """
    selected: Optional[Hypothesis]
    alternatives: List[Hypothesis] = field(default_factory=list)
    rejections: List[HypothesisRejection] = field(default_factory=list)
    margin_used: float = 0.1
    selection_reason: str = ""
    needs_user_input: bool = False
    
    def to_trace_payload(self) -> dict:
        """Convert to trace event payload."""
        return {
            "selected_id": self.selected.id if self.selected else None,
            "alternatives": [h.id for h in self.alternatives],
            "margin": self.margin_used,
            "reason": self.selection_reason,
            "needs_user_input": self.needs_user_input,
            "rejections": [
                {
                    "hypothesis_id": r.hypothesis_id,
                    "reason": r.reason,
                    "confidence": r.confidence,
                    "rank": r.rank,
                }
                for r in self.rejections
            ],
        }


# ==============================
# Selection Function
# ==============================
def select_hypothesis(
    hypothesis_set: HypothesisSet,
    *,
    confidence_margin: float = 0.1,
) -> HypothesisSelectionResult:
    """
    Select the best hypothesis from a set.
    
    INT-HYP-SEL-001: Select exactly one hypothesis or None.
    INT-HYP-SEL-002: Prefer highest confidence.
    INT-HYP-SEL-003: If top 2 within margin, return None (ASK_USER).
    INT-HYP-SEL-004: Store rejection reasons.
    
    Args:
        hypothesis_set: The set of hypotheses to select from.
        confidence_margin: Minimum difference between top 2 for auto-selection.
            Default 0.1 (10% confidence difference required).
            
    Returns:
        HypothesisSelectionResult with selected hypothesis or None if ambiguous.
        
    Example:
        >>> h1 = Hypothesis(description="A", confidence=0.9)
        >>> h2 = Hypothesis(description="B", confidence=0.7)
        >>> hs = HypothesisSet(hypotheses=[h1, h2])
        >>> result = select_hypothesis(hs)
        >>> result.selected.description
        'A'
    """
    hypotheses = hypothesis_set.hypotheses
    
    # Empty set: nothing to select
    if not hypotheses:
        return HypothesisSelectionResult(
            selected=None,
            alternatives=[],
            rejections=[],
            margin_used=confidence_margin,
            selection_reason="No hypotheses in set",
            needs_user_input=False,
        )
    
    # Single hypothesis: auto-select
    if len(hypotheses) == 1:
        return HypothesisSelectionResult(
            selected=hypotheses[0],
            alternatives=[],
            rejections=[],
            margin_used=confidence_margin,
            selection_reason="Single hypothesis in set",
            needs_user_input=False,
        )
    
    # Sort by confidence descending
    sorted_hyps = sorted(hypotheses, key=lambda h: h.confidence, reverse=True)
    
    top = sorted_hyps[0]
    second = sorted_hyps[1]
    
    # Check if top 2 are within margin
    confidence_diff = top.confidence - second.confidence
    within_margin = confidence_diff < confidence_margin
    
    if within_margin:
        # Ambiguous: need user input
        # All hypotheses are alternatives (none selected)
        rejections = [
            HypothesisRejection(
                hypothesis_id=h.id,
                reason="Ambiguous: top hypotheses within confidence margin",
                confidence=h.confidence,
                rank=i + 1,
            )
            for i, h in enumerate(sorted_hyps)
        ]
        return HypothesisSelectionResult(
            selected=None,
            alternatives=sorted_hyps[:2],  # Top 2 ambiguous candidates
            rejections=rejections,
            margin_used=confidence_margin,
            selection_reason=f"Top 2 within margin ({confidence_diff:.3f} < {confidence_margin})",
            needs_user_input=True,
        )
    
    # Clear winner: select top
    rejections = [
        HypothesisRejection(
            hypothesis_id=h.id,
            reason=f"Lower confidence than selected ({h.confidence:.3f} vs {top.confidence:.3f})",
            confidence=h.confidence,
            rank=i + 2,  # rank 1 is selected
        )
        for i, h in enumerate(sorted_hyps[1:])
    ]
    
    return HypothesisSelectionResult(
        selected=top,
        alternatives=sorted_hyps[1:],  # All non-selected as alternatives
        rejections=rejections,
        margin_used=confidence_margin,
        selection_reason=f"Clear winner with margin ({confidence_diff:.3f} >= {confidence_margin})",
        needs_user_input=False,
    )


def get_top_hypotheses(
    hypothesis_set: HypothesisSet,
    *,
    n: int = 3,
) -> List[Hypothesis]:
    """
    Get top N hypotheses by confidence.
    
    Utility function for presenting options to users.
    
    Args:
        hypothesis_set: The set to select from.
        n: Number of top hypotheses to return.
        
    Returns:
        List of top N hypotheses sorted by confidence descending.
    """
    sorted_hyps = sorted(
        hypothesis_set.hypotheses,
        key=lambda h: h.confidence,
        reverse=True,
    )
    return sorted_hyps[:n]


def calculate_confidence_gap(
    hypothesis_set: HypothesisSet,
) -> Tuple[float, Optional[str], Optional[str]]:
    """
    Calculate the confidence gap between top 2 hypotheses.
    
    Utility function for diagnostics.
    
    Args:
        hypothesis_set: The set to analyze.
        
    Returns:
        Tuple of (gap, top_id, second_id). Gap is 0 if fewer than 2 hypotheses.
    """
    if len(hypothesis_set.hypotheses) < 2:
        return (0.0, None, None)
    
    sorted_hyps = sorted(
        hypothesis_set.hypotheses,
        key=lambda h: h.confidence,
        reverse=True,
    )
    
    top = sorted_hyps[0]
    second = sorted_hyps[1]
    
    return (top.confidence - second.confidence, top.id, second.id)
