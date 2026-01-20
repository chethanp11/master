# ==============================
# IMP-015: Hypothesis Selection Tests
# ==============================
"""
Tests for hypothesis selection logic.

Tech Spec IDs: INT-HYP-SEL-001, INT-HYP-SEL-002, INT-HYP-SEL-003, INT-HYP-SEL-004, INT-HYP-SEL-005
BRD ID: BRD-AUTO-028
"""

import pytest

from core.contracts.hypothesis_schema import Hypothesis, HypothesisSet
from core.knowledge.hypothesis_selector import (
    HypothesisRejection,
    HypothesisSelectionResult,
    calculate_confidence_gap,
    get_top_hypotheses,
    select_hypothesis,
)


# ==============================
# HypothesisRejection Tests
# ==============================
class TestHypothesisRejection:
    """Tests for HypothesisRejection dataclass."""
    
    def test_rejection_construction(self):
        """HypothesisRejection stores all fields."""
        rejection = HypothesisRejection(
            hypothesis_id="hyp-123",
            reason="Lower confidence",
            confidence=0.7,
            rank=2,
        )
        assert rejection.hypothesis_id == "hyp-123"
        assert rejection.reason == "Lower confidence"
        assert rejection.confidence == 0.7
        assert rejection.rank == 2
    
    def test_rejection_is_frozen(self):
        """HypothesisRejection is immutable."""
        rejection = HypothesisRejection(
            hypothesis_id="hyp-123",
            reason="test",
            confidence=0.5,
            rank=1,
        )
        with pytest.raises(AttributeError):
            rejection.reason = "modified"


# ==============================
# HypothesisSelectionResult Tests
# ==============================
class TestHypothesisSelectionResult:
    """Tests for HypothesisSelectionResult dataclass."""
    
    def test_result_with_selection(self):
        """HypothesisSelectionResult stores selected hypothesis."""
        hyp = Hypothesis(description="Test", confidence=0.9)
        result = HypothesisSelectionResult(
            selected=hyp,
            selection_reason="Clear winner",
        )
        assert result.selected is hyp
        assert result.selection_reason == "Clear winner"
        assert result.needs_user_input is False
    
    def test_result_without_selection(self):
        """HypothesisSelectionResult can have None selected."""
        result = HypothesisSelectionResult(
            selected=None,
            needs_user_input=True,
            selection_reason="Ambiguous",
        )
        assert result.selected is None
        assert result.needs_user_input is True
    
    def test_result_to_trace_payload(self):
        """to_trace_payload converts result to dict."""
        hyp = Hypothesis(description="Selected", confidence=0.9)
        alt = Hypothesis(description="Alt", confidence=0.7)
        rejection = HypothesisRejection(
            hypothesis_id=alt.id,
            reason="Lower",
            confidence=0.7,
            rank=2,
        )
        result = HypothesisSelectionResult(
            selected=hyp,
            alternatives=[alt],
            rejections=[rejection],
            margin_used=0.1,
            selection_reason="Clear winner",
        )
        payload = result.to_trace_payload()
        
        assert payload["selected_id"] == hyp.id
        assert payload["alternatives"] == [alt.id]
        assert payload["margin"] == 0.1
        assert payload["reason"] == "Clear winner"
        assert len(payload["rejections"]) == 1
        assert payload["rejections"][0]["hypothesis_id"] == alt.id
    
    def test_result_to_trace_payload_no_selection(self):
        """to_trace_payload handles None selection."""
        result = HypothesisSelectionResult(
            selected=None,
            needs_user_input=True,
        )
        payload = result.to_trace_payload()
        assert payload["selected_id"] is None
        assert payload["needs_user_input"] is True


# ==============================
# select_hypothesis Tests (INT-HYP-SEL-001..005)
# ==============================
class TestSelectHypothesis:
    """Tests for select_hypothesis function."""
    
    def test_empty_set_returns_none(self):
        """Empty hypothesis set returns None selection."""
        hs = HypothesisSet()
        result = select_hypothesis(hs)
        
        assert result.selected is None
        assert result.needs_user_input is False
        assert "No hypotheses" in result.selection_reason
    
    def test_single_hypothesis_auto_selected(self):
        """Single hypothesis is automatically selected."""
        hyp = Hypothesis(description="Only one", confidence=0.8)
        hs = HypothesisSet(hypotheses=[hyp])
        result = select_hypothesis(hs)
        
        assert result.selected is hyp
        assert result.needs_user_input is False
        assert "Single hypothesis" in result.selection_reason
        assert len(result.rejections) == 0
    
    def test_clear_winner_selected(self):
        """Highest confidence hypothesis selected when margin is clear."""
        h1 = Hypothesis(description="High", confidence=0.9)
        h2 = Hypothesis(description="Low", confidence=0.5)
        hs = HypothesisSet(hypotheses=[h2, h1])  # Unsorted input
        
        result = select_hypothesis(hs)
        
        assert result.selected is h1
        assert result.selected.confidence == 0.9
        assert result.needs_user_input is False
    
    def test_within_margin_returns_none(self):
        """Within margin triggers ASK_USER (None selection)."""
        h1 = Hypothesis(description="A", confidence=0.85)
        h2 = Hypothesis(description="B", confidence=0.82)  # 0.03 diff < 0.1 margin
        hs = HypothesisSet(hypotheses=[h1, h2])
        
        result = select_hypothesis(hs, confidence_margin=0.1)
        
        assert result.selected is None
        assert result.needs_user_input is True
        assert len(result.alternatives) == 2
        assert "within margin" in result.selection_reason
    
    def test_exactly_at_margin_selects(self):
        """At exactly the margin, selection proceeds."""
        h1 = Hypothesis(description="A", confidence=0.9)
        h2 = Hypothesis(description="B", confidence=0.79)  # 0.11 diff > 0.1 margin
        hs = HypothesisSet(hypotheses=[h1, h2])
        
        result = select_hypothesis(hs, confidence_margin=0.1)
        
        # 0.11 diff is greater than 0.1 margin, so selection proceeds
        assert result.selected is h1
        assert result.needs_user_input is False
    
    def test_custom_margin(self):
        """Custom confidence margin is respected."""
        h1 = Hypothesis(description="A", confidence=0.9)
        h2 = Hypothesis(description="B", confidence=0.85)  # 0.05 diff
        hs = HypothesisSet(hypotheses=[h1, h2])
        
        # With 0.1 margin: 0.05 < 0.1, needs user input
        result1 = select_hypothesis(hs, confidence_margin=0.1)
        assert result1.selected is None
        assert result1.needs_user_input is True
        
        # With 0.03 margin: 0.05 >= 0.03, selects
        result2 = select_hypothesis(hs, confidence_margin=0.03)
        assert result2.selected is h1
        assert result2.needs_user_input is False
    
    def test_rejection_reasons_recorded(self):
        """Rejection reasons recorded for non-selected hypotheses."""
        h1 = Hypothesis(description="A", confidence=0.9)
        h2 = Hypothesis(description="B", confidence=0.6)
        h3 = Hypothesis(description="C", confidence=0.3)
        hs = HypothesisSet(hypotheses=[h1, h2, h3])
        
        result = select_hypothesis(hs)
        
        assert result.selected is h1
        assert len(result.rejections) == 2
        
        # Check rejection details
        rejection_ids = {r.hypothesis_id for r in result.rejections}
        assert h2.id in rejection_ids
        assert h3.id in rejection_ids
        
        # Check ranks
        ranks = {r.hypothesis_id: r.rank for r in result.rejections}
        assert ranks[h2.id] == 2
        assert ranks[h3.id] == 3
    
    def test_alternatives_list(self):
        """Alternatives list contains non-selected hypotheses."""
        h1 = Hypothesis(description="A", confidence=0.9)
        h2 = Hypothesis(description="B", confidence=0.6)
        h3 = Hypothesis(description="C", confidence=0.3)
        hs = HypothesisSet(hypotheses=[h1, h2, h3])
        
        result = select_hypothesis(hs)
        
        assert len(result.alternatives) == 2
        assert h2 in result.alternatives
        assert h3 in result.alternatives
        assert h1 not in result.alternatives
    
    def test_margin_used_recorded(self):
        """margin_used field records the margin used."""
        h1 = Hypothesis(description="A", confidence=0.9)
        h2 = Hypothesis(description="B", confidence=0.5)
        hs = HypothesisSet(hypotheses=[h1, h2])
        
        result = select_hypothesis(hs, confidence_margin=0.25)
        
        assert result.margin_used == 0.25
    
    def test_three_way_tie_near_margin(self):
        """Three hypotheses near margin triggers user input."""
        h1 = Hypothesis(description="A", confidence=0.88)
        h2 = Hypothesis(description="B", confidence=0.85)
        h3 = Hypothesis(description="C", confidence=0.82)
        hs = HypothesisSet(hypotheses=[h1, h2, h3])
        
        # Only top 2 matter for margin check
        result = select_hypothesis(hs, confidence_margin=0.1)
        
        # 0.88 - 0.85 = 0.03 < 0.1, needs user input
        assert result.selected is None
        assert result.needs_user_input is True
    
    def test_selection_with_equal_confidence(self):
        """Equal confidence hypotheses trigger user input."""
        h1 = Hypothesis(description="A", confidence=0.8)
        h2 = Hypothesis(description="B", confidence=0.8)
        hs = HypothesisSet(hypotheses=[h1, h2])
        
        result = select_hypothesis(hs)
        
        assert result.selected is None
        assert result.needs_user_input is True
        assert "within margin" in result.selection_reason


# ==============================
# get_top_hypotheses Tests
# ==============================
class TestGetTopHypotheses:
    """Tests for get_top_hypotheses utility."""
    
    def test_get_top_n(self):
        """get_top_hypotheses returns top N by confidence."""
        h1 = Hypothesis(description="A", confidence=0.3)
        h2 = Hypothesis(description="B", confidence=0.9)
        h3 = Hypothesis(description="C", confidence=0.6)
        hs = HypothesisSet(hypotheses=[h1, h2, h3])
        
        top2 = get_top_hypotheses(hs, n=2)
        
        assert len(top2) == 2
        assert top2[0].confidence == 0.9
        assert top2[1].confidence == 0.6
    
    def test_get_top_more_than_available(self):
        """get_top_hypotheses returns all if n > available."""
        h1 = Hypothesis(description="A", confidence=0.5)
        hs = HypothesisSet(hypotheses=[h1])
        
        top3 = get_top_hypotheses(hs, n=3)
        
        assert len(top3) == 1
    
    def test_get_top_empty(self):
        """get_top_hypotheses returns empty list for empty set."""
        hs = HypothesisSet()
        
        top = get_top_hypotheses(hs, n=5)
        
        assert top == []
    
    def test_get_top_default_n(self):
        """get_top_hypotheses defaults to n=3."""
        hyps = [
            Hypothesis(description=f"H{i}", confidence=i / 10)
            for i in range(5)
        ]
        hs = HypothesisSet(hypotheses=hyps)
        
        top = get_top_hypotheses(hs)
        
        assert len(top) == 3


# ==============================
# calculate_confidence_gap Tests
# ==============================
class TestCalculateConfidenceGap:
    """Tests for calculate_confidence_gap utility."""
    
    def test_gap_calculation(self):
        """calculate_confidence_gap returns correct gap."""
        h1 = Hypothesis(description="A", confidence=0.9)
        h2 = Hypothesis(description="B", confidence=0.6)
        hs = HypothesisSet(hypotheses=[h1, h2])
        
        gap, top_id, second_id = calculate_confidence_gap(hs)
        
        assert abs(gap - 0.3) < 0.001
        assert top_id == h1.id
        assert second_id == h2.id
    
    def test_gap_single_hypothesis(self):
        """calculate_confidence_gap returns 0 for single hypothesis."""
        h1 = Hypothesis(description="A", confidence=0.9)
        hs = HypothesisSet(hypotheses=[h1])
        
        gap, top_id, second_id = calculate_confidence_gap(hs)
        
        assert gap == 0.0
        assert top_id is None
        assert second_id is None
    
    def test_gap_empty_set(self):
        """calculate_confidence_gap returns 0 for empty set."""
        hs = HypothesisSet()
        
        gap, top_id, second_id = calculate_confidence_gap(hs)
        
        assert gap == 0.0
        assert top_id is None
        assert second_id is None
    
    def test_gap_with_equal_confidence(self):
        """calculate_confidence_gap handles equal confidence."""
        h1 = Hypothesis(description="A", confidence=0.7)
        h2 = Hypothesis(description="B", confidence=0.7)
        hs = HypothesisSet(hypotheses=[h1, h2])
        
        gap, _, _ = calculate_confidence_gap(hs)
        
        assert gap == 0.0


# ==============================
# TraceEventType Tests
# ==============================
class TestTraceEventTypes:
    """Tests for hypothesis selection trace event types."""
    
    def test_hypothesis_selected_event_exists(self):
        """HYPOTHESIS_SELECTED trace event type exists."""
        from core.memory.tracing import TraceEventType
        
        assert hasattr(TraceEventType, "HYPOTHESIS_SELECTED")
        assert TraceEventType.HYPOTHESIS_SELECTED.value == "hypothesis_selected"
    
    def test_hypothesis_selection_deferred_event_exists(self):
        """HYPOTHESIS_SELECTION_DEFERRED trace event type exists."""
        from core.memory.tracing import TraceEventType
        
        assert hasattr(TraceEventType, "HYPOTHESIS_SELECTION_DEFERRED")
        assert TraceEventType.HYPOTHESIS_SELECTION_DEFERRED.value == "hypothesis_selection_deferred"


# ==============================
# Integration Tests
# ==============================
class TestHypothesisSelectionIntegration:
    """Integration tests for hypothesis selection."""
    
    def test_selection_result_trace_payload_complete(self):
        """Selection result produces complete trace payload."""
        h1 = Hypothesis(description="Best", confidence=0.9)
        h2 = Hypothesis(description="Good", confidence=0.6)
        h3 = Hypothesis(description="OK", confidence=0.4)
        hs = HypothesisSet(hypotheses=[h1, h2, h3])
        
        result = select_hypothesis(hs)
        payload = result.to_trace_payload()
        
        # Verify all required fields for INT-HYP-SEL-005
        assert "selected_id" in payload
        assert "alternatives" in payload
        assert "margin" in payload
        assert "reason" in payload
        assert "rejections" in payload
        assert "needs_user_input" in payload
        
        # Verify rejection structure
        for rejection in payload["rejections"]:
            assert "hypothesis_id" in rejection
            assert "reason" in rejection
            assert "confidence" in rejection
            assert "rank" in rejection
