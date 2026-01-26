# ==============================
# Unit Tests: Hard Budget Limits
# IMP-048: GOV-BUD-HARD-001...005
# ==============================
"""
Unit tests for hard budget limit enforcement.

These tests verify that:
- No overdraft is possible
- Pre-check before consumption
- Trace events are emitted
- Error codes are correct
"""

import pytest
from typing import Any, Dict, List

from core.governance.budgeting import (
    consume_budget,
    can_consume_budget,
    BudgetPreCheckResult,
    BUDGET_HARD_LIMIT_EXCEEDED,
    BUDGET_OPERATION_REJECTED,
    init_budget_state,
)
from core.contracts.budget_schema import Budget, BudgetState


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def captured_events() -> List[Dict[str, Any]]:
    """Capture emitted events for verification."""
    return []


@pytest.fixture
def emit_fn(captured_events: List[Dict[str, Any]]):
    """Create an emit function that captures events."""
    def _emit(event_type: str, payload: Dict[str, Any]) -> None:
        captured_events.append({"type": event_type, "payload": payload})
    return _emit


@pytest.fixture
def standard_budget() -> Budget:
    """Standard budget with known limits."""
    return Budget(
        max_passes=5,
        max_tool_calls=10,
        max_parallel_calls=3,
        max_total_cost_units=100,
    )


@pytest.fixture
def tight_budget() -> Budget:
    """Tight budget for edge case testing."""
    return Budget(
        max_passes=2,
        max_tool_calls=3,
        max_parallel_calls=1,
        max_total_cost_units=10,
    )


@pytest.fixture
def empty_state() -> BudgetState:
    """Fresh empty budget state."""
    return init_budget_state()


# ============================================================================
# Test Class: Error Codes Exist
# ============================================================================

class TestErrorCodesExist:
    """Verify error codes are defined."""
    
    def test_budget_hard_limit_exceeded_exists(self):
        """Verify BUDGET_HARD_LIMIT_EXCEEDED error code exists."""
        assert BUDGET_HARD_LIMIT_EXCEEDED == "budget_hard_limit_exceeded"
    
    def test_budget_operation_rejected_exists(self):
        """Verify BUDGET_OPERATION_REJECTED error code exists."""
        assert BUDGET_OPERATION_REJECTED == "budget_operation_rejected"


# ============================================================================
# Test Class: BudgetPreCheckResult
# ============================================================================

class TestBudgetPreCheckResult:
    """Test BudgetPreCheckResult structure."""
    
    def test_result_attributes(self):
        """Verify result has all required attributes."""
        result = BudgetPreCheckResult(
            can_proceed=True,
            reason="OK",
            requested_amount=1,
            remaining_budget=5,
            limit=10,
        )
        
        assert result.can_proceed is True
        assert result.reason == "OK"
        assert result.requested_amount == 1
        assert result.remaining_budget == 5
        assert result.limit == 10
        assert result.error_code is None
    
    def test_result_with_error_code(self):
        """Verify result can have error code."""
        result = BudgetPreCheckResult(
            can_proceed=False,
            reason="Limit exceeded",
            requested_amount=2,
            remaining_budget=0,
            limit=10,
            error_code=BUDGET_HARD_LIMIT_EXCEEDED,
        )
        
        assert result.can_proceed is False
        assert result.error_code == BUDGET_HARD_LIMIT_EXCEEDED
    
    def test_to_dict(self):
        """Verify to_dict method."""
        result = BudgetPreCheckResult(
            can_proceed=False,
            reason="Test",
            requested_amount=1,
            remaining_budget=0,
            limit=5,
            error_code="test_error",
        )
        
        d = result.to_dict()
        assert d["can_proceed"] is False
        assert d["reason"] == "Test"
        assert d["error_code"] == "test_error"


# ============================================================================
# Test Class: No Overdraft
# ============================================================================

class TestNoOverdraft:
    """GOV-BUD-HARD-001: No overdraft allowed."""
    
    def test_cannot_exceed_pass_limit(
        self,
        tight_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify cannot exceed pass limit."""
        # Use up all passes
        state = empty_state
        for _ in range(tight_budget.max_passes):
            allowed, action, state = consume_budget(
                budget=tight_budget,
                state=state,
                kind="pass",
                amount=1,
            )
            assert allowed is True
        
        # Next pass should be rejected
        allowed, action, state = consume_budget(
            budget=tight_budget,
            state=state,
            kind="pass",
            amount=1,
        )
        assert allowed is False
        assert state.passes_used == tight_budget.max_passes  # No overdraft
    
    def test_cannot_exceed_tool_limit(
        self,
        tight_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify cannot exceed tool call limit."""
        state = empty_state
        for _ in range(tight_budget.max_tool_calls):
            allowed, action, state = consume_budget(
                budget=tight_budget,
                state=state,
                kind="tool",
                amount=1,
            )
            assert allowed is True
        
        # Next tool call should be rejected
        allowed, action, state = consume_budget(
            budget=tight_budget,
            state=state,
            kind="tool",
            amount=1,
        )
        assert allowed is False
        assert state.tool_calls_used == tight_budget.max_tool_calls
    
    def test_cannot_exceed_parallel_limit(
        self,
        tight_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify cannot exceed parallel call limit."""
        state = empty_state
        for _ in range(tight_budget.max_parallel_calls):
            allowed, action, state = consume_budget(
                budget=tight_budget,
                state=state,
                kind="parallel",
                amount=1,
            )
            assert allowed is True
        
        # Next parallel call should be rejected
        allowed, action, state = consume_budget(
            budget=tight_budget,
            state=state,
            kind="parallel",
            amount=1,
        )
        assert allowed is False
        assert state.parallel_calls_used == tight_budget.max_parallel_calls
    
    def test_cannot_exceed_cost_units(
        self,
        tight_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify cannot exceed cost units limit."""
        # Try to consume more cost units than allowed
        allowed, action, state = consume_budget(
            budget=tight_budget,
            state=empty_state,
            kind="tool",
            amount=1,
            cost_units=tight_budget.max_total_cost_units + 1,
        )
        
        assert allowed is False
    
    def test_allow_overdraft_parameter_ignored(
        self,
        tight_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify allow_overdraft parameter is ignored."""
        # Use up all passes
        state = empty_state
        for _ in range(tight_budget.max_passes):
            _, _, state = consume_budget(
                budget=tight_budget,
                state=state,
                kind="pass",
                amount=1,
            )
        
        # Try with allow_overdraft=True - should still be rejected
        allowed, action, state = consume_budget(
            budget=tight_budget,
            state=state,
            kind="pass",
            amount=1,
            allow_overdraft=True,  # Should be ignored
        )
        assert allowed is False


# ============================================================================
# Test Class: Pre-Check Before Consumption
# ============================================================================

class TestPreCheckBeforeConsumption:
    """GOV-BUD-HARD-002, GOV-BUD-HARD-003: Pre-check before consumption."""
    
    def test_can_consume_budget_succeeds(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify pre-check succeeds when budget available."""
        result = can_consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="tool",
            amount=1,
        )
        
        assert result.can_proceed is True
        assert result.reason == "OK"
        assert result.error_code is None
    
    def test_can_consume_budget_fails_at_limit(
        self,
        tight_budget: Budget,
    ):
        """Verify pre-check fails when at limit."""
        # Create state at limit
        state = BudgetState(
            passes_used=0,
            tool_calls_used=tight_budget.max_tool_calls,
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        result = can_consume_budget(
            budget=tight_budget,
            state=state,
            kind="tool",
            amount=1,
        )
        
        assert result.can_proceed is False
        assert result.error_code == BUDGET_HARD_LIMIT_EXCEEDED
    
    def test_can_consume_budget_fails_would_exceed(
        self,
        tight_budget: Budget,
    ):
        """Verify pre-check fails when would exceed."""
        # Create state with 1 remaining
        state = BudgetState(
            passes_used=0,
            tool_calls_used=tight_budget.max_tool_calls - 1,
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        # Try to consume 2
        result = can_consume_budget(
            budget=tight_budget,
            state=state,
            kind="tool",
            amount=2,
        )
        
        assert result.can_proceed is False
        assert result.error_code == BUDGET_OPERATION_REJECTED
    
    def test_pre_check_includes_remaining_budget(
        self,
        standard_budget: Budget,
    ):
        """Verify pre-check includes remaining budget info."""
        state = BudgetState(
            passes_used=0,
            tool_calls_used=5,
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        result = can_consume_budget(
            budget=standard_budget,
            state=state,
            kind="tool",
            amount=1,
        )
        
        assert result.remaining_budget == 5  # 10 - 5
        assert result.limit == 10
        assert result.requested_amount == 1
    
    def test_state_unchanged_on_rejection(
        self,
        tight_budget: Budget,
    ):
        """Verify state is unchanged when consumption rejected."""
        # State at limit
        state = BudgetState(
            passes_used=0,
            tool_calls_used=tight_budget.max_tool_calls,
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        original_tool_calls = state.tool_calls_used
        
        allowed, action, new_state = consume_budget(
            budget=tight_budget,
            state=state,
            kind="tool",
            amount=1,
        )
        
        assert allowed is False
        # State should be unchanged - same object returned
        assert new_state.tool_calls_used == original_tool_calls


# ============================================================================
# Test Class: Trace Events
# ============================================================================

class TestTraceEvents:
    """GOV-BUD-HARD-004, GOV-BUD-HARD-005: Trace events emitted."""
    
    def test_budget_limit_reached_event(
        self,
        tight_budget: Budget,
        captured_events: List[Dict[str, Any]],
        emit_fn,
    ):
        """Verify budget_limit_reached event is emitted."""
        # State at limit
        state = BudgetState(
            passes_used=0,
            tool_calls_used=tight_budget.max_tool_calls,
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        consume_budget(
            budget=tight_budget,
            state=state,
            kind="tool",
            amount=1,
            emit_event_fn=emit_fn,
        )
        
        limit_events = [e for e in captured_events if e["type"] == "budget_limit_reached"]
        assert len(limit_events) == 1
        assert limit_events[0]["payload"]["kind"] == "tool"
        assert limit_events[0]["payload"]["limit"] == tight_budget.max_tool_calls
    
    def test_budget_operation_rejected_event(
        self,
        tight_budget: Budget,
        captured_events: List[Dict[str, Any]],
        emit_fn,
    ):
        """Verify budget_operation_rejected event is emitted."""
        # State with 1 remaining
        state = BudgetState(
            passes_used=0,
            tool_calls_used=tight_budget.max_tool_calls - 1,
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        consume_budget(
            budget=tight_budget,
            state=state,
            kind="tool",
            amount=2,  # Try to consume more than remaining
            emit_event_fn=emit_fn,
        )
        
        rejected_events = [e for e in captured_events if e["type"] == "budget_operation_rejected"]
        assert len(rejected_events) == 1
        assert rejected_events[0]["payload"]["kind"] == "tool"
        assert rejected_events[0]["payload"]["requested_amount"] == 2
        assert rejected_events[0]["payload"]["remaining_budget"] == 1
    
    def test_no_event_on_success(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
        captured_events: List[Dict[str, Any]],
        emit_fn,
    ):
        """Verify no rejection event when consumption succeeds."""
        consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="tool",
            amount=1,
            emit_event_fn=emit_fn,
        )
        
        # Should be no limit/rejection events
        problem_events = [
            e for e in captured_events 
            if e["type"] in ("budget_limit_reached", "budget_operation_rejected")
        ]
        assert len(problem_events) == 0


# ============================================================================
# Test Class: Error Details
# ============================================================================

class TestErrorDetails:
    """GOV-BUD-HARD-005: Error details include required fields."""
    
    def test_rejected_includes_requested_amount(
        self,
        tight_budget: Budget,
        captured_events: List[Dict[str, Any]],
        emit_fn,
    ):
        """Verify rejection includes requested_amount."""
        state = BudgetState(
            passes_used=0,
            tool_calls_used=tight_budget.max_tool_calls - 1,
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        consume_budget(
            budget=tight_budget,
            state=state,
            kind="tool",
            amount=5,
            emit_event_fn=emit_fn,
        )
        
        rejected_events = [e for e in captured_events if e["type"] == "budget_operation_rejected"]
        assert rejected_events[0]["payload"]["requested_amount"] == 5
    
    def test_rejected_includes_remaining_budget(
        self,
        tight_budget: Budget,
        captured_events: List[Dict[str, Any]],
        emit_fn,
    ):
        """Verify rejection includes remaining_budget."""
        state = BudgetState(
            passes_used=0,
            tool_calls_used=2,  # 1 remaining with max 3
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        consume_budget(
            budget=tight_budget,
            state=state,
            kind="tool",
            amount=5,
            emit_event_fn=emit_fn,
        )
        
        rejected_events = [e for e in captured_events if e["type"] == "budget_operation_rejected"]
        assert rejected_events[0]["payload"]["remaining_budget"] == 1
    
    def test_rejected_includes_limit(
        self,
        tight_budget: Budget,
        captured_events: List[Dict[str, Any]],
        emit_fn,
    ):
        """Verify rejection includes limit."""
        state = BudgetState(
            passes_used=0,
            tool_calls_used=tight_budget.max_tool_calls,
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        consume_budget(
            budget=tight_budget,
            state=state,
            kind="tool",
            amount=1,
            emit_event_fn=emit_fn,
        )
        
        limit_events = [e for e in captured_events if e["type"] == "budget_limit_reached"]
        assert limit_events[0]["payload"]["limit"] == tight_budget.max_tool_calls


# ============================================================================
# Test Class: Successful Consumption
# ============================================================================

class TestSuccessfulConsumption:
    """Verify successful consumption still works."""
    
    def test_tool_consumption(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify tool consumption works normally."""
        allowed, action, state = consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="tool",
            amount=1,
        )
        
        assert allowed is True
        assert action == "OK"
        assert state.tool_calls_used == 1
    
    def test_pass_consumption(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify pass consumption works normally."""
        allowed, action, state = consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="pass",
            amount=1,
        )
        
        assert allowed is True
        assert action == "OK"
        assert state.passes_used == 1
    
    def test_parallel_consumption(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify parallel consumption works normally."""
        allowed, action, state = consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="parallel",
            amount=1,
        )
        
        assert allowed is True
        assert action == "OK"
        assert state.parallel_calls_used == 1
    
    def test_cost_units_consumed(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify cost units are consumed."""
        allowed, action, state = consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="tool",
            amount=1,
            cost_units=5,
        )
        
        assert allowed is True
        assert state.cost_units_used == 5


# ============================================================================
# Test Class: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_exactly_at_limit(
        self,
        tight_budget: Budget,
    ):
        """Verify consumption works exactly at limit."""
        # 2 remaining, consume 2
        state = BudgetState(
            passes_used=tight_budget.max_passes - 2,
            tool_calls_used=0,
            parallel_calls_used=0,
            cost_units_used=0,
        )
        
        allowed, action, new_state = consume_budget(
            budget=tight_budget,
            state=state,
            kind="pass",
            amount=2,
        )
        
        assert allowed is True
        assert new_state.passes_used == tight_budget.max_passes
    
    def test_zero_amount(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify zero amount consumption works."""
        allowed, action, state = consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="tool",
            amount=0,
        )
        
        assert allowed is True
        assert state.tool_calls_used == 0
    
    def test_unknown_kind_rejected(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify unknown kind is handled."""
        result = can_consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="unknown_kind",
            amount=1,
        )
        
        assert result.can_proceed is False
        assert result.error_code == BUDGET_OPERATION_REJECTED


# ============================================================================
# Test Class: Backward Compatibility
# ============================================================================

class TestBackwardCompatibility:
    """Verify backward compatibility is maintained."""
    
    def test_consume_budget_returns_tuple(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify consume_budget returns tuple."""
        result = consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="tool",
            amount=1,
        )
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        allowed, action, state = result
        assert isinstance(allowed, bool)
        assert isinstance(action, str)
        assert isinstance(state, BudgetState)
    
    def test_consume_budget_works_without_emit_fn(
        self,
        standard_budget: Budget,
        empty_state: BudgetState,
    ):
        """Verify consume_budget works without emit function."""
        allowed, action, state = consume_budget(
            budget=standard_budget,
            state=empty_state,
            kind="tool",
            amount=1,
        )
        
        assert allowed is True
    
    def test_init_budget_state_still_works(self):
        """Verify init_budget_state still works."""
        state = init_budget_state()
        
        assert state.passes_used == 0
        assert state.tool_calls_used == 0
        assert state.parallel_calls_used == 0
        assert state.cost_units_used == 0
