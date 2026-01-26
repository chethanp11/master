# ==============================
# Integration Tests: Auto-Redaction Enforcement
# IMP-046: GOV-SEC-AUTO-001...005
# ==============================
"""
Integration tests for automatic redaction enforcement.

These tests verify that:
- AutoRedactionEnforcer applies to all output paths
- Redaction cannot be bypassed
- Trace events are emitted
- API responses are redacted
- Artifacts are redacted
"""

import pytest
from typing import Any, Dict, List

from core.governance.security import (
    AutoRedactionEnforcer,
    SecurityRedactor,
    get_auto_redaction_enforcer,
    reset_auto_redaction_enforcer,
    DEFAULT_MASK,
)
from core.contracts.run_schema import TraceEvent


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
def enforcer(emit_fn) -> AutoRedactionEnforcer:
    """Create fresh enforcer for each test."""
    return AutoRedactionEnforcer(emit_event_fn=emit_fn)


@pytest.fixture(autouse=True)
def reset_global_enforcer():
    """Reset global enforcer before and after each test."""
    reset_auto_redaction_enforcer()
    yield
    reset_auto_redaction_enforcer()


# ============================================================================
# Test Class: AutoRedactionEnforcer Existence
# ============================================================================

class TestAutoRedactionEnforcerExists:
    """GOV-SEC-AUTO-001: AutoRedactionEnforcer class exists."""
    
    def test_class_exists(self):
        """Verify AutoRedactionEnforcer class is defined."""
        assert AutoRedactionEnforcer is not None
    
    def test_can_instantiate(self):
        """Verify can create instance."""
        enforcer = AutoRedactionEnforcer()
        assert enforcer is not None
    
    def test_default_redactor_created(self):
        """Verify default SecurityRedactor is created."""
        enforcer = AutoRedactionEnforcer()
        assert enforcer._redactor is not None
        assert isinstance(enforcer._redactor, SecurityRedactor)
    
    def test_custom_redactor_accepted(self):
        """Verify custom redactor can be passed."""
        custom_redactor = SecurityRedactor(include_pii=False)
        enforcer = AutoRedactionEnforcer(redactor=custom_redactor)
        assert enforcer._redactor is custom_redactor


# ============================================================================
# Test Class: Always Enabled
# ============================================================================

class TestAutoRedactionAlwaysEnabled:
    """GOV-SEC-AUTO-005: Auto-redaction cannot be disabled."""
    
    def test_is_enabled_always_true(self, enforcer: AutoRedactionEnforcer):
        """Verify is_enabled always returns True."""
        assert enforcer.is_enabled is True
    
    def test_no_disable_parameter_in_constructor(self):
        """Verify constructor has no 'enabled' parameter."""
        import inspect
        sig = inspect.signature(AutoRedactionEnforcer.__init__)
        param_names = [p for p in sig.parameters.keys() if p != 'self']
        assert 'enabled' not in param_names
        assert 'disable' not in param_names
        assert 'bypass' not in param_names
    
    def test_class_level_flag_is_true(self):
        """Verify class-level _ENABLED is True."""
        assert AutoRedactionEnforcer._ENABLED is True
    
    def test_cannot_disable_after_creation(self, enforcer: AutoRedactionEnforcer):
        """Verify no method to disable exists."""
        assert not hasattr(enforcer, 'disable')
        assert not hasattr(enforcer, 'set_enabled')
        assert not hasattr(enforcer, 'bypass')


# ============================================================================
# Test Class: enforce_on_output
# ============================================================================

class TestEnforceOnOutput:
    """GOV-SEC-AUTO-001: enforce_on_output method."""
    
    def test_redacts_string_with_secret(self, enforcer: AutoRedactionEnforcer):
        """Verify strings with secrets are redacted."""
        text = "API key is sk-abc123xyz456"
        result = enforcer.enforce_on_output(text)
        assert DEFAULT_MASK in result
        assert "sk-abc123xyz456" not in result
    
    def test_redacts_dict_with_password(self, enforcer: AutoRedactionEnforcer):
        """Verify dicts with password keys are redacted."""
        data = {"username": "admin", "password": "secret123"}
        result = enforcer.enforce_on_output(data)
        assert result["password"] == DEFAULT_MASK
        assert result["username"] == "admin"
    
    def test_redacts_nested_dict(self, enforcer: AutoRedactionEnforcer):
        """Verify nested structures are redacted."""
        data = {
            "user": {
                "credentials": {
                    "api_key": "sk-secret",
                    "token": "bearer123"
                }
            }
        }
        result = enforcer.enforce_on_output(data)
        assert result["user"]["credentials"]["api_key"] == DEFAULT_MASK
        assert result["user"]["credentials"]["token"] == DEFAULT_MASK
    
    def test_redacts_list_elements(self, enforcer: AutoRedactionEnforcer):
        """Verify list elements are redacted."""
        data = ["safe", "sk-abc123456"]
        result = enforcer.enforce_on_output(data)
        assert result[0] == "safe"
        assert DEFAULT_MASK in result[1]
    
    def test_none_returns_none(self, enforcer: AutoRedactionEnforcer):
        """Verify None is passed through."""
        assert enforcer.enforce_on_output(None) is None
    
    def test_safe_data_unchanged(self, enforcer: AutoRedactionEnforcer):
        """Verify safe data is not modified."""
        data = {"name": "John", "age": 30}
        result = enforcer.enforce_on_output(data)
        assert result == data
    
    def test_increments_redaction_count(self, enforcer: AutoRedactionEnforcer):
        """Verify redaction count increments."""
        assert enforcer.redaction_count == 0
        enforcer.enforce_on_output({"password": "secret"})
        assert enforcer.redaction_count == 1


# ============================================================================
# Test Class: Trace Event Payloads
# ============================================================================

class TestEnforceOnTracePayload:
    """GOV-SEC-AUTO-002: Apply to trace event payloads."""
    
    def test_redacts_trace_payload(self, enforcer: AutoRedactionEnforcer):
        """Verify trace payloads are redacted."""
        payload = {
            "action": "login",
            "token": "secret-token-123"
        }
        result = enforcer.enforce_on_trace_payload(payload)
        assert result["token"] == DEFAULT_MASK
        assert result["action"] == "login"
    
    def test_redacts_nested_trace_payload(self, enforcer: AutoRedactionEnforcer):
        """Verify nested trace payloads are redacted."""
        payload = {
            "user_input": "My password is abc123",
            "context": {
                "api_key": "sk-12345",
                "session_id": "sess-001"
            }
        }
        result = enforcer.enforce_on_trace_payload(payload)
        assert result["context"]["api_key"] == DEFAULT_MASK
        assert result["context"]["session_id"] == DEFAULT_MASK


# ============================================================================
# Test Class: API Responses
# ============================================================================

class TestEnforceOnAPIResponse:
    """GOV-SEC-AUTO-003: Apply to API responses."""
    
    def test_redacts_api_response(self, enforcer: AutoRedactionEnforcer):
        """Verify API responses are redacted."""
        response = {
            "status": "success",
            "data": {
                "user": "admin",
                "bearer_token": "xyz789"
            }
        }
        result = enforcer.enforce_on_api_response(response)
        assert result["status"] == "success"
        # bearer_token contains 'token' hint
        assert result["data"]["bearer_token"] == DEFAULT_MASK
    
    def test_api_response_with_pii(self, enforcer: AutoRedactionEnforcer):
        """Verify PII in API responses is redacted."""
        response = {
            "email": "user@example.com",
            "name": "John"
        }
        result = enforcer.enforce_on_api_response(response)
        assert DEFAULT_MASK in result["email"]
        assert result["name"] == "John"


# ============================================================================
# Test Class: Artifact Contents
# ============================================================================

class TestEnforceOnArtifact:
    """GOV-SEC-AUTO-004: Apply to artifact contents."""
    
    def test_redacts_artifact_dict(self, enforcer: AutoRedactionEnforcer):
        """Verify artifact dicts are redacted."""
        artifact = {
            "type": "credential",
            "value": "sk-abcdefghijk"
        }
        result = enforcer.enforce_on_artifact(artifact)
        assert DEFAULT_MASK in result["value"]
    
    def test_redacts_artifact_string(self, enforcer: AutoRedactionEnforcer):
        """Verify artifact strings are redacted."""
        artifact = "AWS Key: AKIAIOSFODNN7EXAMPLE"
        result = enforcer.enforce_on_artifact(artifact)
        assert DEFAULT_MASK in result
        assert "AKIA" not in result


# ============================================================================
# Test Class: Log Messages
# ============================================================================

class TestEnforceOnLogMessage:
    """Additional: Apply to log messages."""
    
    def test_redacts_log_message(self, enforcer: AutoRedactionEnforcer):
        """Verify log messages with secrets are redacted."""
        # Use a pattern that matches our regex (sk-xxx format)
        message = "User logged in with key: sk-abc123xyz456"
        result = enforcer.enforce_on_log_message(message)
        assert DEFAULT_MASK in result
        assert "sk-abc123xyz456" not in result
    
    def test_safe_log_unchanged(self, enforcer: AutoRedactionEnforcer):
        """Verify safe logs are unchanged."""
        message = "Processing request for user 123"
        result = enforcer.enforce_on_log_message(message)
        assert result == message


# ============================================================================
# Test Class: Trace Event Emission
# ============================================================================

class TestAutoRedactionTraceEvents:
    """Verify trace events are emitted on redaction."""
    
    def test_emits_auto_redaction_applied(
        self,
        enforcer: AutoRedactionEnforcer,
        captured_events: List[Dict[str, Any]]
    ):
        """Verify auto_redaction_applied event is emitted."""
        enforcer.enforce_on_output({"password": "secret"})
        
        assert len(captured_events) == 1
        event = captured_events[0]
        assert event["type"] == "auto_redaction_applied"
        assert "original_length" in event["payload"]
        assert "mask_count" in event["payload"]
    
    def test_no_event_when_no_redaction(
        self,
        enforcer: AutoRedactionEnforcer,
        captured_events: List[Dict[str, Any]]
    ):
        """Verify no event when data is safe."""
        enforcer.enforce_on_output({"name": "John", "age": 30})
        
        # No events because no redaction occurred
        assert len(captured_events) == 0
    
    def test_event_payload_includes_data_type(
        self,
        enforcer: AutoRedactionEnforcer,
        captured_events: List[Dict[str, Any]]
    ):
        """Verify event includes data type."""
        enforcer.enforce_on_output({"token": "secret"})
        
        event = captured_events[0]
        assert event["payload"]["data_type"] == "dict"


# ============================================================================
# Test Class: Wrap Emit Function
# ============================================================================

class TestWrapEmitFunction:
    """GOV-SEC-AUTO-002: Wrap trace event emission."""
    
    def test_wraps_emit_function(self, enforcer: AutoRedactionEnforcer):
        """Verify emit function is wrapped."""
        emitted_events = []
        
        def original_emit(event):
            emitted_events.append(event)
        
        wrapped = enforcer.wrap_emit_function(original_emit)
        
        # Create mock event with payload
        class MockEvent:
            def __init__(self, payload):
                self.payload = payload
            def model_copy(self, update):
                return MockEvent(update.get("payload", self.payload))
        
        event = MockEvent({"secret": "api_key=abc123"})
        wrapped(event)
        
        assert len(emitted_events) == 1
        # Payload should be redacted
        assert DEFAULT_MASK in str(emitted_events[0].payload)
    
    def test_wrapped_emit_handles_dict_events(self, enforcer: AutoRedactionEnforcer):
        """Verify dict events are handled."""
        emitted = []
        
        def emit(event):
            emitted.append(event)
        
        wrapped = enforcer.wrap_emit_function(emit)
        # Use a pattern that gets detected in the value, not just key hint
        wrapped({"payload": {"message": "secret sk-abc123xyz456"}})
        
        assert DEFAULT_MASK in str(emitted[0]["payload"]["message"])


# ============================================================================
# Test Class: Wrap Response Handler
# ============================================================================

class TestWrapResponseHandler:
    """GOV-SEC-AUTO-003: Wrap API response handlers."""
    
    def test_wraps_response_handler(self, enforcer: AutoRedactionEnforcer):
        """Verify response handler is wrapped."""
        def handler(request):
            return {"api_key": "sk-secret123", "status": "ok"}
        
        wrapped = enforcer.wrap_response_handler(handler)
        result = wrapped({})
        
        assert result["api_key"] == DEFAULT_MASK
        assert result["status"] == "ok"
    
    def test_non_dict_response_passthrough(self, enforcer: AutoRedactionEnforcer):
        """Verify non-dict responses pass through."""
        def handler(request):
            return "plain text response"
        
        wrapped = enforcer.wrap_response_handler(handler)
        result = wrapped({})
        
        assert result == "plain text response"


# ============================================================================
# Test Class: Global Enforcer
# ============================================================================

class TestGlobalEnforcer:
    """Test global enforcer access pattern."""
    
    def test_get_creates_enforcer(self):
        """Verify get_auto_redaction_enforcer creates instance."""
        enforcer = get_auto_redaction_enforcer()
        assert enforcer is not None
        assert isinstance(enforcer, AutoRedactionEnforcer)
    
    def test_get_returns_same_instance(self):
        """Verify singleton pattern."""
        enforcer1 = get_auto_redaction_enforcer()
        enforcer2 = get_auto_redaction_enforcer()
        assert enforcer1 is enforcer2
    
    def test_reset_clears_enforcer(self):
        """Verify reset clears global enforcer."""
        enforcer1 = get_auto_redaction_enforcer()
        reset_auto_redaction_enforcer()
        enforcer2 = get_auto_redaction_enforcer()
        assert enforcer1 is not enforcer2


# ============================================================================
# Test Class: Cloud Credential Integration
# ============================================================================

class TestCloudCredentialAutoRedaction:
    """Verify cloud credentials are auto-redacted."""
    
    def test_aws_key_redacted(self, enforcer: AutoRedactionEnforcer):
        """Verify AWS keys are redacted."""
        data = {"aws_key": "AKIAIOSFODNN7EXAMPLE"}
        result = enforcer.enforce_on_output(data)
        assert DEFAULT_MASK in str(result)
    
    def test_github_token_redacted(self, enforcer: AutoRedactionEnforcer):
        """Verify GitHub tokens are redacted."""
        data = {"token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
        # token key hint triggers redaction
        result = enforcer.enforce_on_output(data)
        assert result["token"] == DEFAULT_MASK
    
    def test_multiple_credentials_redacted(self, enforcer: AutoRedactionEnforcer):
        """Verify multiple credentials are all redacted."""
        data = {
            "aws": "AKIAIOSFODNN7EXAMPLE",
            "github_token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "api_key": "sk-12345"
        }
        result = enforcer.enforce_on_output(data)
        # All sensitive keys should be redacted
        assert result["github_token"] == DEFAULT_MASK
        assert result["api_key"] == DEFAULT_MASK


# ============================================================================
# Test Class: PII Integration
# ============================================================================

class TestPIIAutoRedaction:
    """Verify PII is auto-redacted."""
    
    def test_email_redacted(self, enforcer: AutoRedactionEnforcer):
        """Verify emails are redacted."""
        data = {"message": "Contact user@example.com for details"}
        result = enforcer.enforce_on_output(data)
        assert DEFAULT_MASK in result["message"]
        assert "user@example.com" not in result["message"]
    
    def test_credit_card_redacted(self, enforcer: AutoRedactionEnforcer):
        """Verify credit card numbers are redacted."""
        data = {"card": "4111-1111-1111-1111"}
        result = enforcer.enforce_on_output(data)
        assert DEFAULT_MASK in result["card"]


# ============================================================================
# Test Class: Non-Bypassable Verification
# ============================================================================

class TestNonBypassable:
    """GOV-SEC-AUTO-005: Verify cannot bypass auto-redaction."""
    
    def test_no_bypass_method(self, enforcer: AutoRedactionEnforcer):
        """Verify no bypass method exists."""
        methods = dir(enforcer)
        bypass_methods = [m for m in methods if 'bypass' in m.lower() or 'skip' in m.lower()]
        assert len(bypass_methods) == 0
    
    def test_no_raw_output_method(self, enforcer: AutoRedactionEnforcer):
        """Verify no get_raw_output method exists."""
        assert not hasattr(enforcer, 'get_raw_output')
        assert not hasattr(enforcer, 'raw_output')
        assert not hasattr(enforcer, 'unredacted_output')
    
    def test_always_processes_through_redactor(
        self,
        captured_events: List[Dict[str, Any]]
    ):
        """Verify all data paths go through redactor."""
        enforcer = AutoRedactionEnforcer(emit_event_fn=lambda t, p: captured_events.append({"type": t, "payload": p}))
        
        # All enforce methods should redact
        sensitive = {"password": "secret"}
        
        r1 = enforcer.enforce_on_output(sensitive.copy())
        r2 = enforcer.enforce_on_trace_payload(sensitive.copy())
        r3 = enforcer.enforce_on_api_response(sensitive.copy())
        r4 = enforcer.enforce_on_artifact(sensitive.copy())
        
        # All should be redacted
        for result in [r1, r2, r3, r4]:
            assert result["password"] == DEFAULT_MASK


# ============================================================================
# Test Class: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_dict(self, enforcer: AutoRedactionEnforcer):
        """Verify empty dict handled."""
        assert enforcer.enforce_on_output({}) == {}
    
    def test_empty_string(self, enforcer: AutoRedactionEnforcer):
        """Verify empty string handled."""
        assert enforcer.enforce_on_output("") == ""
    
    def test_empty_list(self, enforcer: AutoRedactionEnforcer):
        """Verify empty list handled."""
        assert enforcer.enforce_on_output([]) == []
    
    def test_numeric_values_preserved(self, enforcer: AutoRedactionEnforcer):
        """Verify numeric values are preserved."""
        data = {"count": 42, "price": 19.99}
        result = enforcer.enforce_on_output(data)
        assert result["count"] == 42
        assert result["price"] == 19.99
    
    def test_boolean_values_preserved(self, enforcer: AutoRedactionEnforcer):
        """Verify boolean values are preserved."""
        data = {"active": True, "deleted": False}
        result = enforcer.enforce_on_output(data)
        assert result["active"] is True
        assert result["deleted"] is False
    
    def test_deeply_nested_structure(self, enforcer: AutoRedactionEnforcer):
        """Verify deeply nested structures are handled."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "secret_key": "hidden"
                        }
                    }
                }
            }
        }
        result = enforcer.enforce_on_output(data)
        assert result["level1"]["level2"]["level3"]["level4"]["secret_key"] == DEFAULT_MASK
