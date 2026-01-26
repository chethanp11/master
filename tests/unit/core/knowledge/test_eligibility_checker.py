"""
Tests for Discovery Eligibility Checks (IMP-038).

Tests INT-DISC-029...037:
- EligibilityChecker class exists
- Budget-exhausted tools excluded
- Low-confidence candidates excluded
- Exclusion reasons traced
"""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

from core.contracts.budget_schema import Budget, BudgetState
from core.governance.budgeting import (
    can_afford_tool,
    estimated_cost_by_tool,
    register_tool_cost,
)
from core.knowledge.discovery_engine import (
    AgentCandidate,
    EligibilityChecker,
    EligibilityResult,
    ToolCandidate,
)


class TestEligibilityResult:
    """Tests for EligibilityResult dataclass."""

    def test_eligible_result(self) -> None:
        """INT-DISC-029: EligibilityResult should represent eligible candidate."""
        result = EligibilityResult(eligible=True, reasons=[])
        
        assert result.eligible is True
        assert result.reasons == []

    def test_ineligible_result_with_reasons(self) -> None:
        """INT-DISC-029: EligibilityResult should capture exclusion reasons."""
        result = EligibilityResult(
            eligible=False,
            reasons=["Budget insufficient", "Confidence too low"],
        )
        
        assert result.eligible is False
        assert len(result.reasons) == 2


class TestBudgetEligibility:
    """Tests for budget-related eligibility checks."""

    def test_estimated_cost_by_tool_default(self) -> None:
        """INT-DISC-032: Unknown tools should have default cost."""
        cost = estimated_cost_by_tool("unknown_tool")
        assert cost == 1  # Default cost

    def test_register_tool_cost(self) -> None:
        """INT-DISC-031: Tool costs should be registrable."""
        register_tool_cost("expensive_tool", 10)
        cost = estimated_cost_by_tool("expensive_tool")
        assert cost == 10

    def test_can_afford_tool_within_budget(self) -> None:
        """INT-DISC-033: Can afford tool when within budget."""
        budget = Budget(
            max_tool_calls=10,
            max_total_cost_units=100,
        )
        state = BudgetState()
        
        assert can_afford_tool("any_tool", budget, state) is True

    def test_cannot_afford_tool_calls_exhausted(self) -> None:
        """INT-DISC-033: Cannot afford when tool calls exhausted."""
        budget = Budget(
            max_tool_calls=5,
            max_total_cost_units=100,
        )
        state = BudgetState(tool_calls_used=5)
        
        assert can_afford_tool("any_tool", budget, state) is False

    def test_cannot_afford_cost_units_exhausted(self) -> None:
        """INT-DISC-033: Cannot afford when cost units exhausted."""
        register_tool_cost("costly_tool", 50)
        budget = Budget(
            max_tool_calls=100,
            max_total_cost_units=60,
        )
        state = BudgetState(cost_units_used=30)
        
        assert can_afford_tool("costly_tool", budget, state) is False


class TestEligibilityChecker:
    """Tests for EligibilityChecker class."""

    def test_checker_exists(self) -> None:
        """INT-DISC-030: EligibilityChecker should exist."""
        checker = EligibilityChecker()
        assert checker is not None

    def test_check_confidence_eligibility_pass(self) -> None:
        """INT-DISC-032: High confidence should pass."""
        checker = EligibilityChecker()
        candidate = ToolCandidate(
            name="test_tool",
            confidence=0.8,
            match_reason="Test",
        )
        
        assert checker.check_confidence_eligibility(candidate, 0.5) is True

    def test_check_confidence_eligibility_fail(self) -> None:
        """INT-DISC-032: Low confidence should fail."""
        checker = EligibilityChecker()
        candidate = ToolCandidate(
            name="test_tool",
            confidence=0.3,
            match_reason="Test",
        )
        
        assert checker.check_confidence_eligibility(candidate, 0.5) is False

    def test_check_budget_eligibility(self) -> None:
        """INT-DISC-031: Budget eligibility should use can_afford_tool."""
        checker = EligibilityChecker()
        candidate = ToolCandidate(
            name="affordable_tool",
            confidence=0.8,
            match_reason="Test",
        )
        budget = Budget(max_tool_calls=10, max_total_cost_units=100)
        state = BudgetState()
        
        assert checker.check_budget_eligibility(candidate, budget, state) is True

    def test_check_context_eligibility_no_context(self) -> None:
        """INT-DISC-033: No context should be eligible."""
        checker = EligibilityChecker()
        candidate = ToolCandidate(
            name="test_tool",
            confidence=0.8,
            match_reason="Test",
            domain_tags=["finance"],
        )
        
        assert checker.check_context_eligibility(candidate, None) is True

    def test_composite_check_all_pass(self) -> None:
        """INT-DISC-034: Composite check should pass when all pass."""
        checker = EligibilityChecker()
        candidate = ToolCandidate(
            name="test_tool",
            confidence=0.8,
            match_reason="Test",
        )
        budget = Budget(max_tool_calls=10, max_total_cost_units=100)
        state = BudgetState()
        
        result = checker.check_eligibility(
            candidate,
            budget=budget,
            budget_state=state,
            min_confidence=0.5,
        )
        
        assert result.eligible is True
        assert result.reasons == []

    def test_composite_check_confidence_fail(self) -> None:
        """INT-DISC-034: Composite check should fail on low confidence."""
        checker = EligibilityChecker()
        candidate = ToolCandidate(
            name="test_tool",
            confidence=0.3,
            match_reason="Test",
        )
        
        result = checker.check_eligibility(candidate, min_confidence=0.5)
        
        assert result.eligible is False
        assert any("Confidence" in r for r in result.reasons)

    def test_exclusion_event_emitted(self) -> None:
        """INT-DISC-035: Exclusion event should be emitted for ineligible."""
        events: List[Dict[str, Any]] = []
        
        def capture_event(**kwargs: Any) -> None:
            events.append(kwargs)
        
        checker = EligibilityChecker(emit_event_fn=capture_event)
        candidate = ToolCandidate(
            name="low_conf_tool",
            confidence=0.1,
            match_reason="Test",
        )
        
        checker.check_eligibility(candidate, min_confidence=0.5)
        
        assert len(events) == 1
        assert events[0]["kind"] == "candidate_excluded"
        assert events[0]["payload"]["candidate_name"] == "low_conf_tool"

    def test_filter_eligible_removes_ineligible(self) -> None:
        """INT-DISC-036: Filter should remove ineligible candidates."""
        checker = EligibilityChecker()
        candidates = [
            ToolCandidate(name="high_conf", confidence=0.9, match_reason="Test"),
            ToolCandidate(name="low_conf", confidence=0.2, match_reason="Test"),
            ToolCandidate(name="mid_conf", confidence=0.6, match_reason="Test"),
        ]
        
        eligible = checker.filter_eligible(candidates, min_confidence=0.5)
        
        assert len(eligible) == 2
        names = [c.name for c in eligible]
        assert "high_conf" in names
        assert "mid_conf" in names
        assert "low_conf" not in names

