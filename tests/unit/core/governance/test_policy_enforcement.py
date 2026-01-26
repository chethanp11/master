# ==============================
# Unit Tests: Policy Enforcement (No Bypass)
# IMP-047: GOV-POL-NOBYPASS-001...005, GOV-POL-BLOCK-001...005
# ==============================
"""
Unit tests for policy enforcement without bypass capability.

These tests verify that:
- No bypass configuration exists
- Violations block immediately  
- Trace events are emitted
- enforce=false is ignored
"""

import pytest
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

from core.governance.policies import (
    PolicyEngine,
    PolicyDecision,
    PolicyBypassAttemptError,
    POLICY_VIOLATION_IMMEDIATE,
    POLICY_BYPASS_ATTEMPTED,
)
from core.contracts.flow_schema import AutonomyLevel
from core.config.schema import Settings, PoliciesConfig


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
def settings_with_enforce_true() -> Settings:
    """Settings with enforce=True (default)."""
    return Settings(
        policies=PoliciesConfig(
            enforce=True,
            allowed_tools=["allowed_tool"],
            blocked_tools=["blocked_tool"],
            allowed_models=["allowed_model"],
            blocked_models=["blocked_model"],
            allow_full_autonomy=False,
        )
    )


@pytest.fixture
def settings_with_enforce_false() -> Settings:
    """Settings with enforce=False (should be blocked)."""
    return Settings(
        policies=PoliciesConfig(
            enforce=False,  # This should be ignored per IMP-047
            allowed_tools=["allowed_tool"],
            blocked_tools=["blocked_tool"],
        )
    )


@pytest.fixture
def mock_run_ctx() -> MagicMock:
    """Create a mock RunContext."""
    ctx = MagicMock()
    ctx.product = "test_product"
    return ctx


@pytest.fixture
def mock_step_ctx() -> MagicMock:
    """Create a mock StepContext."""
    ctx = MagicMock()
    run = MagicMock()
    run_record = MagicMock()
    run_record.product = "test_product"
    run.run_record = run_record
    ctx.run = run
    ctx.product = "test_product"
    return ctx


# ============================================================================
# Test Class: Error Codes Exist
# ============================================================================

class TestErrorCodesExist:
    """Verify error codes are defined."""
    
    def test_policy_violation_immediate_exists(self):
        """Verify POLICY_VIOLATION_IMMEDIATE error code exists."""
        assert POLICY_VIOLATION_IMMEDIATE == "policy_violation_immediate"
    
    def test_policy_bypass_attempted_exists(self):
        """Verify POLICY_BYPASS_ATTEMPTED error code exists."""
        assert POLICY_BYPASS_ATTEMPTED == "policy_bypass_attempted"


# ============================================================================
# Test Class: No Bypass Configuration
# ============================================================================

class TestNoBypassConfiguration:
    """GOV-POL-NOBYPASS-001: No bypass configuration allowed."""
    
    def test_enforce_false_is_blocked(
        self,
        settings_with_enforce_false: Settings,
        captured_events: List[Dict[str, Any]],
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify enforce=false is detected and blocked."""
        engine = PolicyEngine(settings_with_enforce_false, emit_event_fn=emit_fn)
        
        # Make a tool call - should trigger bypass detection
        result = engine.evaluate_tool_call(tool_name="allowed_tool", step_ctx=mock_step_ctx)
        
        # Should have emitted bypass blocked event
        bypass_events = [e for e in captured_events if e["type"] == "policy_bypass_blocked"]
        assert len(bypass_events) >= 1
    
    def test_bypass_attempt_counter_increments(
        self,
        settings_with_enforce_false: Settings,
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify bypass attempt counter increments."""
        engine = PolicyEngine(settings_with_enforce_false, emit_event_fn=emit_fn)
        
        # Multiple calls should increment counter
        engine.evaluate_tool_call(tool_name="tool1", step_ctx=mock_step_ctx)
        engine.evaluate_tool_call(tool_name="tool2", step_ctx=mock_step_ctx)
        
        assert engine.bypass_attempt_count >= 2
    
    def test_policy_still_enforced_when_bypass_attempted(
        self,
        settings_with_enforce_false: Settings,
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify policy is still enforced even with enforce=false."""
        engine = PolicyEngine(settings_with_enforce_false, emit_event_fn=emit_fn)
        
        # Blocked tool should still be blocked
        result = engine.evaluate_tool_call(tool_name="blocked_tool", step_ctx=mock_step_ctx)
        assert result.allow is False
        assert result.reason == "tool_blocked"


# ============================================================================
# Test Class: Immediate Blocking
# ============================================================================

class TestImmediateBlocking:
    """GOV-POL-BLOCK-001...005: Block immediately on violations."""
    
    def test_tool_blocked_immediately(
        self,
        settings_with_enforce_true: Settings,
        captured_events: List[Dict[str, Any]],
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify blocked tool is rejected immediately."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_tool_call(tool_name="blocked_tool", step_ctx=mock_step_ctx)
        
        assert result.allow is False
        assert result.reason == "tool_blocked"
        assert POLICY_VIOLATION_IMMEDIATE in result.details.get("error_code", "")
    
    def test_tool_not_in_allowlist_blocked_immediately(
        self,
        settings_with_enforce_true: Settings,
        captured_events: List[Dict[str, Any]],
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify tool not in allowlist is rejected immediately."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_tool_call(tool_name="unknown_tool", step_ctx=mock_step_ctx)
        
        assert result.allow is False
        assert result.reason == "tool_not_in_allowlist"
    
    def test_model_blocked_immediately(
        self,
        settings_with_enforce_true: Settings,
        captured_events: List[Dict[str, Any]],
        emit_fn,
    ):
        """Verify blocked model is rejected immediately."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_model_selection(
            product="test_product", 
            model_name="blocked_model"
        )
        
        assert result.allow is False
        assert result.reason == "model_blocked"
    
    def test_model_not_in_allowlist_blocked_immediately(
        self,
        settings_with_enforce_true: Settings,
        captured_events: List[Dict[str, Any]],
        emit_fn,
    ):
        """Verify model not in allowlist is rejected immediately."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_model_selection(
            product="test_product", 
            model_name="unknown_model"
        )
        
        assert result.allow is False
        assert result.reason == "model_not_in_allowlist"
    
    def test_full_autonomy_blocked_immediately(
        self,
        settings_with_enforce_true: Settings,
        captured_events: List[Dict[str, Any]],
        emit_fn,
        mock_run_ctx: MagicMock,
    ):
        """Verify full autonomy is rejected immediately when disabled."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_autonomy(
            autonomy=AutonomyLevel.FULL_AUTO,
            run_ctx=mock_run_ctx
        )
        
        assert result.allow is False
        assert result.reason == "full_autonomy_disabled"


# ============================================================================
# Test Class: Trace Events Emitted
# ============================================================================

class TestTraceEventsEmitted:
    """Verify trace events are emitted on violations and bypass attempts."""
    
    def test_policy_violation_blocked_event_emitted(
        self,
        settings_with_enforce_true: Settings,
        captured_events: List[Dict[str, Any]],
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify policy_violation_blocked event is emitted."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        engine.evaluate_tool_call(tool_name="blocked_tool", step_ctx=mock_step_ctx)
        
        violation_events = [e for e in captured_events if e["type"] == "policy_violation_blocked"]
        assert len(violation_events) == 1
        assert violation_events[0]["payload"]["reason"] == "tool_blocked"
    
    def test_policy_bypass_blocked_event_emitted(
        self,
        settings_with_enforce_false: Settings,
        captured_events: List[Dict[str, Any]],
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify policy_bypass_blocked event is emitted."""
        engine = PolicyEngine(settings_with_enforce_false, emit_event_fn=emit_fn)
        
        engine.evaluate_tool_call(tool_name="allowed_tool", step_ctx=mock_step_ctx)
        
        bypass_events = [e for e in captured_events if e["type"] == "policy_bypass_blocked"]
        assert len(bypass_events) >= 1
    
    def test_no_event_when_allowed(
        self,
        settings_with_enforce_true: Settings,
        captured_events: List[Dict[str, Any]],
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify no violation event when action is allowed."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        engine.evaluate_tool_call(tool_name="allowed_tool", step_ctx=mock_step_ctx)
        
        violation_events = [e for e in captured_events if e["type"] == "policy_violation_blocked"]
        assert len(violation_events) == 0


# ============================================================================
# Test Class: Allowed Actions Still Work
# ============================================================================

class TestAllowedActionsWork:
    """Verify allowed actions still succeed."""
    
    def test_allowed_tool_succeeds(
        self,
        settings_with_enforce_true: Settings,
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify allowed tool is permitted."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_tool_call(tool_name="allowed_tool", step_ctx=mock_step_ctx)
        
        assert result.allow is True
        assert result.reason == "ok"
    
    def test_allowed_model_succeeds(
        self,
        settings_with_enforce_true: Settings,
        emit_fn,
    ):
        """Verify allowed model is permitted."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_model_selection(
            product="test_product",
            model_name="allowed_model"
        )
        
        assert result.allow is True
        assert result.reason == "ok"
    
    def test_limited_autonomy_succeeds(
        self,
        settings_with_enforce_true: Settings,
        emit_fn,
        mock_run_ctx: MagicMock,
    ):
        """Verify limited autonomy is permitted."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_autonomy(
            autonomy=AutonomyLevel.SEMI_AUTO,
            run_ctx=mock_run_ctx
        )
        
        assert result.allow is True
        assert result.reason == "ok"


# ============================================================================
# Test Class: PolicyDecision Structure
# ============================================================================

class TestPolicyDecisionStructure:
    """Verify PolicyDecision dataclass structure."""
    
    def test_decision_is_frozen(self):
        """Verify PolicyDecision is frozen (immutable)."""
        decision = PolicyDecision(allow=True, reason="test", details={})
        with pytest.raises(AttributeError):
            decision.allow = False
    
    def test_decision_has_bypass_attempted_field(self):
        """Verify PolicyDecision has bypass_attempted field."""
        decision = PolicyDecision(allow=True, reason="test", details={})
        assert hasattr(decision, 'bypass_attempted')
        assert decision.bypass_attempted is False
    
    def test_decision_default_bypass_false(self):
        """Verify bypass_attempted defaults to False."""
        decision = PolicyDecision(allow=True, reason="test", details={})
        assert decision.bypass_attempted is False


# ============================================================================
# Test Class: No Disable Mechanism
# ============================================================================

class TestNoDisableMechanism:
    """GOV-POL-NOBYPASS-005: No configuration can disable policy checks."""
    
    def test_no_disable_method_on_engine(
        self,
        settings_with_enforce_true: Settings,
    ):
        """Verify no disable method exists on PolicyEngine."""
        engine = PolicyEngine(settings_with_enforce_true)
        
        assert not hasattr(engine, 'disable')
        assert not hasattr(engine, 'disable_enforcement')
        assert not hasattr(engine, 'set_enforce')
    
    def test_no_bypass_method_on_engine(
        self,
        settings_with_enforce_true: Settings,
    ):
        """Verify no bypass method exists on PolicyEngine."""
        engine = PolicyEngine(settings_with_enforce_true)
        
        assert not hasattr(engine, 'bypass')
        assert not hasattr(engine, 'skip_enforcement')
        assert not hasattr(engine, 'allow_bypass')
    
    def test_constructor_has_no_disable_param(self):
        """Verify constructor has no disable parameter."""
        import inspect
        sig = inspect.signature(PolicyEngine.__init__)
        param_names = [p for p in sig.parameters.keys() if p != 'self']
        
        assert 'disable' not in param_names
        assert 'enabled' not in param_names
        assert 'bypass' not in param_names
        assert 'enforce' not in param_names


# ============================================================================
# Test Class: Error Code in Details
# ============================================================================

class TestErrorCodeInDetails:
    """Verify error code is included in violation details."""
    
    def test_tool_violation_includes_error_code(
        self,
        settings_with_enforce_true: Settings,
        emit_fn,
        mock_step_ctx: MagicMock,
    ):
        """Verify tool violation includes error code."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_tool_call(tool_name="blocked_tool", step_ctx=mock_step_ctx)
        
        assert "error_code" in result.details
        assert result.details["error_code"] == POLICY_VIOLATION_IMMEDIATE
    
    def test_model_violation_includes_error_code(
        self,
        settings_with_enforce_true: Settings,
        emit_fn,
    ):
        """Verify model violation includes error code."""
        engine = PolicyEngine(settings_with_enforce_true, emit_event_fn=emit_fn)
        
        result = engine.evaluate_model_selection(
            product="test_product",
            model_name="blocked_model"
        )
        
        assert "error_code" in result.details
        assert result.details["error_code"] == POLICY_VIOLATION_IMMEDIATE


# ============================================================================
# Test Class: PolicyBypassAttemptError
# ============================================================================

class TestPolicyBypassAttemptError:
    """Test PolicyBypassAttemptError exception."""
    
    def test_exception_exists(self):
        """Verify exception class exists."""
        assert PolicyBypassAttemptError is not None
    
    def test_exception_inherits_from_exception(self):
        """Verify inherits from Exception."""
        assert issubclass(PolicyBypassAttemptError, Exception)
    
    def test_exception_has_context(self):
        """Verify exception stores context."""
        error = PolicyBypassAttemptError("test", context={"key": "value"})
        assert error.context == {"key": "value"}
    
    def test_exception_default_context(self):
        """Verify exception has default empty context."""
        error = PolicyBypassAttemptError("test")
        assert error.context == {}


# ============================================================================
# Test Class: Backward Compatibility
# ============================================================================

class TestBackwardCompatibility:
    """Verify backward compatibility is maintained."""
    
    def test_engine_can_be_created_without_emit_fn(
        self,
        settings_with_enforce_true: Settings,
    ):
        """Verify engine can be created without emit function."""
        engine = PolicyEngine(settings_with_enforce_true)
        assert engine is not None
    
    def test_engine_works_without_emit_fn(
        self,
        settings_with_enforce_true: Settings,
        mock_step_ctx: MagicMock,
    ):
        """Verify engine works without emit function."""
        engine = PolicyEngine(settings_with_enforce_true)
        
        result = engine.evaluate_tool_call(tool_name="blocked_tool", step_ctx=mock_step_ctx)
        assert result.allow is False
    
    def test_policy_decision_still_has_original_fields(self):
        """Verify PolicyDecision still has allow, reason, details."""
        decision = PolicyDecision(allow=True, reason="test", details={"key": "value"})
        assert hasattr(decision, 'allow')
        assert hasattr(decision, 'reason')
        assert hasattr(decision, 'details')


# ============================================================================
# Test Class: Product Override Still Works
# ============================================================================

class TestProductOverrideWorks:
    """Verify per-product overrides still work (without bypass)."""
    
    def test_product_override_allows_tool(self):
        """Verify product override can allow a tool."""
        settings = Settings(
            policies=PoliciesConfig(
                allowed_tools=["base_tool"],
                by_product={
                    "special_product": {
                        "allowed_tools": ["special_tool", "base_tool"]
                    }
                }
            )
        )
        
        engine = PolicyEngine(settings)
        
        # Mock step context for special product
        ctx = MagicMock()
        run = MagicMock()
        run_record = MagicMock()
        run_record.product = "special_product"
        run.run_record = run_record
        ctx.run = run
        
        result = engine.evaluate_tool_call(tool_name="special_tool", step_ctx=ctx)
        assert result.allow is True
    
    def test_product_override_cannot_disable_enforcement(self):
        """Verify product override cannot disable enforcement."""
        settings = Settings(
            policies=PoliciesConfig(
                allowed_tools=["base_tool"],
                by_product={
                    "bypass_product": {
                        "enforce": False,  # Attempt to disable
                        "allowed_tools": ["any_tool"]
                    }
                }
            )
        )
        
        captured = []
        def emit_fn(event_type, payload):
            captured.append({"type": event_type, "payload": payload})
        
        engine = PolicyEngine(settings, emit_event_fn=emit_fn)
        
        # Mock step context for bypass product
        ctx = MagicMock()
        run = MagicMock()
        run_record = MagicMock()
        run_record.product = "bypass_product"
        run.run_record = run_record
        ctx.run = run
        
        # Should detect bypass attempt
        engine.evaluate_tool_call(tool_name="some_tool", step_ctx=ctx)
        
        bypass_events = [e for e in captured if e["type"] == "policy_bypass_blocked"]
        assert len(bypass_events) >= 1
