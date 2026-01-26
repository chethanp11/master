"""
Tests for IMP-043: HITL Binding Requirements (GOV-HITL-BIND-001..007, GOV-HITL-DECL-001..005).

Verifies:
- HITLBinding immutability
- EscalationPath and condition matching
- HITLBindingRegistry operations
- Modification blocking and trace event emission
- Factory functions
"""

import pytest
from datetime import datetime
from typing import Any, Dict, List

from core.governance.hitl_binding import (
    EscalationAction,
    EscalationCondition,
    EscalationPath,
    EscalationTrigger,
    HITLBinding,
    HITLBindingModificationError,
    HITLBindingRegistry,
    HITLModificationAttempt,
    HITLPriority,
    create_default_hitl_binding,
    create_escalation_condition,
    create_escalation_path,
    create_hitl_binding,
)
from core.memory.tracing import TraceEventType


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_product_id() -> str:
    return "test_product"


@pytest.fixture
def sample_condition() -> EscalationCondition:
    return EscalationCondition(
        trigger=EscalationTrigger.LOW_CONFIDENCE,
        threshold=0.5,
        description="Confidence below 50%",
    )


@pytest.fixture
def sample_path(sample_condition: EscalationCondition) -> EscalationPath:
    return EscalationPath(
        path_id="path-test-001",
        name="test_path",
        conditions=(sample_condition,),
        action=EscalationAction.PAUSE_AND_WAIT,
        priority=HITLPriority.MEDIUM,
    )


@pytest.fixture
def sample_binding(sample_path: EscalationPath, sample_product_id: str) -> HITLBinding:
    return HITLBinding(
        binding_id="hitl-test-001",
        product_id=sample_product_id,
        escalation_paths=(("test_path", sample_path),),
    )


@pytest.fixture
def registry() -> HITLBindingRegistry:
    return HITLBindingRegistry()


# ============================================================================
# GOV-HITL-BIND-001: EscalationPath Tests
# ============================================================================


class TestEscalationCondition:
    """Test EscalationCondition behavior."""
    
    def test_condition_is_frozen(self, sample_condition: EscalationCondition):
        """GOV-HITL-BIND-001: Condition is immutable."""
        with pytest.raises(Exception):
            sample_condition.threshold = 0.8
    
    def test_condition_matches_trigger(self):
        """GOV-HITL-BIND-001: Condition matches on trigger."""
        condition = EscalationCondition(
            trigger=EscalationTrigger.BLOCKING_AMBIGUITY,
        )
        context = {"trigger": EscalationTrigger.BLOCKING_AMBIGUITY}
        assert condition.matches(context) is True
    
    def test_condition_matches_trigger_string(self):
        """GOV-HITL-BIND-001: Condition matches trigger as string value."""
        condition = EscalationCondition(
            trigger=EscalationTrigger.BLOCKING_AMBIGUITY,
        )
        context = {"trigger": "blocking_ambiguity"}
        assert condition.matches(context) is True
    
    def test_condition_no_match_wrong_trigger(self):
        """GOV-HITL-BIND-001: Condition doesn't match wrong trigger."""
        condition = EscalationCondition(
            trigger=EscalationTrigger.LOW_CONFIDENCE,
        )
        context = {"trigger": EscalationTrigger.BLOCKING_AMBIGUITY}
        assert condition.matches(context) is False
    
    def test_low_confidence_threshold_matching(self):
        """GOV-HITL-BIND-002: Low confidence with threshold."""
        condition = EscalationCondition(
            trigger=EscalationTrigger.LOW_CONFIDENCE,
            threshold=0.5,
        )
        # Below threshold - matches
        context = {"trigger": EscalationTrigger.LOW_CONFIDENCE, "value": 0.4}
        assert condition.matches(context) is True
        
        # Above threshold - no match
        context = {"trigger": EscalationTrigger.LOW_CONFIDENCE, "value": 0.6}
        assert condition.matches(context) is False
    
    def test_budget_threshold_matching(self):
        """GOV-HITL-BIND-002: Budget threshold (exceeds)."""
        condition = EscalationCondition(
            trigger=EscalationTrigger.BUDGET_THRESHOLD,
            threshold=0.8,
        )
        # Above threshold - matches
        context = {"trigger": EscalationTrigger.BUDGET_THRESHOLD, "value": 0.9}
        assert condition.matches(context) is True
        
        # Below threshold - no match
        context = {"trigger": EscalationTrigger.BUDGET_THRESHOLD, "value": 0.7}
        assert condition.matches(context) is False


class TestEscalationPath:
    """Test EscalationPath behavior."""
    
    def test_path_is_frozen(self, sample_path: EscalationPath):
        """GOV-HITL-BIND-001: Path is immutable."""
        with pytest.raises(Exception):
            sample_path.name = "new_name"
    
    def test_path_matches_any_condition(self):
        """GOV-HITL-BIND-001: Path matches if any condition matches."""
        cond1 = EscalationCondition(trigger=EscalationTrigger.LOW_CONFIDENCE)
        cond2 = EscalationCondition(trigger=EscalationTrigger.BLOCKING_AMBIGUITY)
        
        path = EscalationPath(
            path_id="path-001",
            name="test",
            conditions=(cond1, cond2),
            action=EscalationAction.PAUSE_AND_WAIT,
        )
        
        # Matches first condition
        context = {"trigger": EscalationTrigger.LOW_CONFIDENCE}
        assert path.matches_any_condition(context) is True
        
        # Matches second condition
        context = {"trigger": EscalationTrigger.BLOCKING_AMBIGUITY}
        assert path.matches_any_condition(context) is True
        
        # Matches neither
        context = {"trigger": EscalationTrigger.SECURITY_VIOLATION}
        assert path.matches_any_condition(context) is False
    
    def test_path_to_dict(self, sample_path: EscalationPath):
        """GOV-HITL-BIND-001: Path can be serialized."""
        data = sample_path.to_dict()
        
        assert data["path_id"] == "path-test-001"
        assert data["name"] == "test_path"
        assert data["action"] == "pause_and_wait"
        assert data["priority"] == "medium"
        assert len(data["conditions"]) == 1


# ============================================================================
# GOV-HITL-BIND-003: EscalationAction Tests
# ============================================================================


class TestEscalationAction:
    """Test EscalationAction enum."""
    
    def test_all_actions_exist(self):
        """GOV-HITL-BIND-003: All actions defined."""
        assert EscalationAction.PAUSE_AND_NOTIFY.value == "pause_and_notify"
        assert EscalationAction.PAUSE_AND_WAIT.value == "pause_and_wait"
        assert EscalationAction.REJECT_AND_NOTIFY.value == "reject_and_notify"
        assert EscalationAction.LOG_AND_CONTINUE.value == "log_and_continue"
        assert EscalationAction.EMERGENCY_STOP.value == "emergency_stop"


# ============================================================================
# GOV-HITL-BIND-004: Immutability Tests
# ============================================================================


class TestHITLBindingImmutability:
    """Test HITLBinding immutability."""
    
    def test_binding_is_frozen(self, sample_binding: HITLBinding):
        """GOV-HITL-BIND-004: Binding is immutable."""
        with pytest.raises(Exception):
            sample_binding.enabled = False
    
    def test_is_runtime_modifiable_returns_false(self, sample_binding: HITLBinding):
        """GOV-HITL-BIND-004: is_runtime_modifiable always returns False."""
        assert sample_binding.is_runtime_modifiable() is False
    
    def test_immutable_always_true(self, sample_product_id: str):
        """GOV-HITL-BIND-004: immutable field is always True."""
        binding = HITLBinding(
            binding_id="test",
            product_id=sample_product_id,
            escalation_paths=(),
            immutable=False,  # Try to set False
        )
        # Should still be True
        assert binding.immutable is True
    
    def test_binding_has_required_fields(self, sample_binding: HITLBinding):
        """GOV-HITL-BIND-001: Binding has all required fields."""
        assert sample_binding.binding_id == "hitl-test-001"
        assert sample_binding.product_id == "test_product"
        assert sample_binding.enabled is True
        assert sample_binding.immutable is True
        assert isinstance(sample_binding.created_at, datetime)


# ============================================================================
# GOV-HITL-BIND-005: Registry Tests
# ============================================================================


class TestHITLBindingRegistry:
    """Test HITLBindingRegistry operations."""
    
    def test_register_binding(
        self,
        registry: HITLBindingRegistry,
        sample_binding: HITLBinding,
    ):
        """GOV-HITL-BIND-005: Register binding."""
        binding_id = registry.register(sample_binding)
        assert binding_id == sample_binding.binding_id
        assert registry.count() == 1
    
    def test_get_binding(
        self,
        registry: HITLBindingRegistry,
        sample_binding: HITLBinding,
    ):
        """GOV-HITL-BIND-005: Get binding by ID."""
        registry.register(sample_binding)
        retrieved = registry.get(sample_binding.binding_id)
        assert retrieved == sample_binding
    
    def test_get_nonexistent_returns_none(self, registry: HITLBindingRegistry):
        """GOV-HITL-BIND-005: Get nonexistent returns None."""
        result = registry.get("nonexistent")
        assert result is None
    
    def test_get_by_product(
        self,
        registry: HITLBindingRegistry,
        sample_product_id: str,
    ):
        """GOV-HITL-BIND-005: Filter by product."""
        binding1 = create_hitl_binding(sample_product_id, {})
        binding2 = create_hitl_binding(sample_product_id, {})
        binding3 = create_hitl_binding("other_product", {})
        
        registry.register(binding1)
        registry.register(binding2)
        registry.register(binding3)
        
        results = registry.get_by_product(sample_product_id)
        assert len(results) == 2
        assert all(b.product_id == sample_product_id for b in results)
    
    def test_register_duplicate_without_overwrite_fails(
        self,
        registry: HITLBindingRegistry,
        sample_binding: HITLBinding,
    ):
        """GOV-HITL-BIND-005: Duplicate registration without overwrite fails."""
        registry.register(sample_binding)
        
        with pytest.raises(HITLBindingModificationError):
            registry.register(sample_binding, overwrite=False)
    
    def test_register_duplicate_with_overwrite_succeeds(
        self,
        registry: HITLBindingRegistry,
        sample_binding: HITLBinding,
    ):
        """GOV-HITL-BIND-005: Duplicate with overwrite succeeds."""
        registry.register(sample_binding)
        registry.register(sample_binding, overwrite=True)
        assert registry.count() == 1


# ============================================================================
# GOV-HITL-BIND-006: Modification Blocking Tests
# ============================================================================


class TestModificationBlocking:
    """Test modification blocking."""
    
    def test_update_raises_error(
        self,
        registry: HITLBindingRegistry,
        sample_binding: HITLBinding,
    ):
        """GOV-HITL-BIND-007: Update always raises error."""
        registry.register(sample_binding)
        
        with pytest.raises(HITLBindingModificationError) as exc_info:
            registry.update(sample_binding.binding_id, enabled=False)
        
        assert exc_info.value.binding_id == sample_binding.binding_id
        assert exc_info.value.operation == "update"
    
    def test_delete_raises_error(
        self,
        registry: HITLBindingRegistry,
        sample_binding: HITLBinding,
    ):
        """GOV-HITL-BIND-007: Delete always raises error."""
        registry.register(sample_binding)
        
        with pytest.raises(HITLBindingModificationError) as exc_info:
            registry.delete(sample_binding.binding_id)
        
        assert exc_info.value.binding_id == sample_binding.binding_id
        assert exc_info.value.operation == "delete"
    
    def test_modification_attempts_recorded(
        self,
        registry: HITLBindingRegistry,
        sample_binding: HITLBinding,
    ):
        """GOV-HITL-BIND-006: Modification attempts are logged."""
        registry.register(sample_binding)
        
        try:
            registry.update(sample_binding.binding_id, enabled=False)
        except HITLBindingModificationError:
            pass
        
        try:
            registry.delete(sample_binding.binding_id)
        except HITLBindingModificationError:
            pass
        
        attempts = registry.get_modification_attempts()
        assert len(attempts) == 2
        assert all(a.blocked for a in attempts)
    
    def test_modification_emits_trace_event(self, sample_binding: HITLBinding):
        """GOV-HITL-BIND-006: Modification triggers trace event."""
        emitted_events: List[Dict[str, Any]] = []
        
        def capture_event(event_type: str, payload: Dict[str, Any]):
            emitted_events.append({"type": event_type, "payload": payload})
        
        registry = HITLBindingRegistry(emit_event_fn=capture_event)
        registry.register(sample_binding)
        
        try:
            registry.update(sample_binding.binding_id, enabled=False)
        except HITLBindingModificationError:
            pass
        
        assert len(emitted_events) == 1
        assert emitted_events[0]["type"] == "hitl_binding_modification_blocked"
        assert emitted_events[0]["payload"]["binding_id"] == sample_binding.binding_id


class TestHITLModificationAttempt:
    """Test HITLModificationAttempt structure."""
    
    def test_attempt_has_required_fields(self):
        """GOV-HITL-BIND-006: Attempt has required fields."""
        attempt = HITLModificationAttempt(
            attempt_id="mod-001",
            binding_id="hitl-001",
            attempted_operation="update",
            source="runtime_api",
        )
        
        assert attempt.attempt_id == "mod-001"
        assert attempt.binding_id == "hitl-001"
        assert attempt.attempted_operation == "update"
        assert attempt.source == "runtime_api"
        assert attempt.blocked is True  # Always True
    
    def test_attempt_to_trace_payload(self):
        """GOV-HITL-BIND-006: Attempt can generate trace payload."""
        attempt = HITLModificationAttempt(
            attempt_id="mod-001",
            binding_id="hitl-001",
            attempted_operation="delete",
            source="api",
        )
        
        payload = attempt.to_trace_payload()
        assert payload["attempt_id"] == "mod-001"
        assert payload["binding_id"] == "hitl-001"
        assert payload["blocked"] is True


# ============================================================================
# GOV-HITL-BIND-007: Escalation Matching Tests
# ============================================================================


class TestEscalationMatching:
    """Test escalation path matching."""
    
    def test_find_matching_paths(
        self,
        registry: HITLBindingRegistry,
        sample_product_id: str,
    ):
        """GOV-HITL-BIND-007: Find matching escalation paths."""
        path = create_escalation_path(
            name="low_confidence",
            conditions=[
                create_escalation_condition(
                    EscalationTrigger.LOW_CONFIDENCE,
                    threshold=0.5,
                ),
            ],
            action=EscalationAction.PAUSE_AND_WAIT,
        )
        binding = create_hitl_binding(
            sample_product_id,
            {"low_confidence": path},
        )
        registry.register(binding)
        
        # Should match
        context = {"trigger": EscalationTrigger.LOW_CONFIDENCE, "value": 0.3}
        matches = registry.find_matching_escalations(sample_product_id, context)
        assert len(matches) == 1
        assert matches[0].name == "low_confidence"
        
        # Should not match
        context = {"trigger": EscalationTrigger.LOW_CONFIDENCE, "value": 0.8}
        matches = registry.find_matching_escalations(sample_product_id, context)
        assert len(matches) == 0
    
    def test_matching_paths_sorted_by_priority(
        self,
        registry: HITLBindingRegistry,
        sample_product_id: str,
    ):
        """GOV-HITL-BIND-007: Matching paths sorted by priority."""
        low_path = create_escalation_path(
            name="low_priority",
            conditions=[create_escalation_condition(EscalationTrigger.LOW_CONFIDENCE)],
            action=EscalationAction.LOG_AND_CONTINUE,
            priority=HITLPriority.LOW,
        )
        critical_path = create_escalation_path(
            name="critical_priority",
            conditions=[create_escalation_condition(EscalationTrigger.LOW_CONFIDENCE)],
            action=EscalationAction.EMERGENCY_STOP,
            priority=HITLPriority.CRITICAL,
        )
        medium_path = create_escalation_path(
            name="medium_priority",
            conditions=[create_escalation_condition(EscalationTrigger.LOW_CONFIDENCE)],
            action=EscalationAction.PAUSE_AND_WAIT,
            priority=HITLPriority.MEDIUM,
        )
        
        binding = create_hitl_binding(
            sample_product_id,
            {
                "low": low_path,
                "critical": critical_path,
                "medium": medium_path,
            },
        )
        registry.register(binding)
        
        context = {"trigger": EscalationTrigger.LOW_CONFIDENCE}
        matches = registry.find_matching_escalations(sample_product_id, context)
        
        assert len(matches) == 3
        assert matches[0].priority == HITLPriority.CRITICAL
        assert matches[1].priority == HITLPriority.MEDIUM
        assert matches[2].priority == HITLPriority.LOW
    
    def test_disabled_binding_no_matches(
        self,
        registry: HITLBindingRegistry,
        sample_product_id: str,
    ):
        """GOV-HITL-BIND-007: Disabled binding returns no matches."""
        path = create_escalation_path(
            name="test",
            conditions=[create_escalation_condition(EscalationTrigger.LOW_CONFIDENCE)],
            action=EscalationAction.PAUSE_AND_WAIT,
        )
        binding = HITLBinding(
            binding_id="hitl-disabled",
            product_id=sample_product_id,
            escalation_paths=(("test", path),),
            enabled=False,  # Disabled
        )
        registry.register(binding)
        
        context = {"trigger": EscalationTrigger.LOW_CONFIDENCE}
        matches = registry.find_matching_escalations(sample_product_id, context)
        assert len(matches) == 0


# ============================================================================
# Factory Function Tests
# ============================================================================


class TestFactoryFunctions:
    """Test factory functions."""
    
    def test_create_escalation_condition(self):
        """Factory creates valid condition."""
        condition = create_escalation_condition(
            EscalationTrigger.SECURITY_VIOLATION,
            threshold=1.0,
            description="Security alert",
        )
        
        assert condition.trigger == EscalationTrigger.SECURITY_VIOLATION
        assert condition.threshold == 1.0
        assert condition.description == "Security alert"
    
    def test_create_escalation_path(self):
        """Factory creates valid path."""
        condition = create_escalation_condition(EscalationTrigger.TOOL_FAILURE)
        path = create_escalation_path(
            name="tool_failure",
            conditions=[condition],
            action=EscalationAction.REJECT_AND_NOTIFY,
            priority=HITLPriority.HIGH,
            notification_targets=["admin@example.com"],
            timeout_seconds=300,
        )
        
        assert path.name == "tool_failure"
        assert path.action == EscalationAction.REJECT_AND_NOTIFY
        assert path.priority == HITLPriority.HIGH
        assert path.notification_targets == ("admin@example.com",)
        assert path.timeout_seconds == 300
        assert path.path_id.startswith("path-")
    
    def test_create_hitl_binding(self, sample_product_id: str):
        """Factory creates valid binding."""
        path = create_escalation_path(
            name="test",
            conditions=[],
            action=EscalationAction.PAUSE_AND_WAIT,
        )
        binding = create_hitl_binding(
            sample_product_id,
            {"test": path},
            registered_by="unit_test",
        )
        
        assert binding.product_id == sample_product_id
        assert binding.registered_by == "unit_test"
        assert binding.binding_id.startswith("hitl-")
        assert binding.get_path("test") == path
    
    def test_create_default_hitl_binding(self, sample_product_id: str):
        """Factory creates default binding with standard paths."""
        binding = create_default_hitl_binding(sample_product_id)
        
        assert binding.product_id == sample_product_id
        
        paths = binding.get_all_paths()
        assert "low_confidence" in paths
        assert "blocking_ambiguity" in paths
        assert "security_violation" in paths
        
        # Security violation should be CRITICAL priority
        security_path = paths["security_violation"]
        assert security_path.priority == HITLPriority.CRITICAL
        assert security_path.action == EscalationAction.EMERGENCY_STOP


# ============================================================================
# Trace Event Type Tests
# ============================================================================


class TestTraceEventTypes:
    """Test trace event type definitions."""
    
    def test_hitl_binding_modification_blocked_exists(self):
        """HITL_BINDING_MODIFICATION_BLOCKED event type exists."""
        assert hasattr(TraceEventType, "HITL_BINDING_MODIFICATION_BLOCKED")
        assert TraceEventType.HITL_BINDING_MODIFICATION_BLOCKED.value == "hitl_binding_modification_blocked"
    
    def test_hitl_escalation_triggered_exists(self):
        """HITL_ESCALATION_TRIGGERED event type exists."""
        assert hasattr(TraceEventType, "HITL_ESCALATION_TRIGGERED")
        assert TraceEventType.HITL_ESCALATION_TRIGGERED.value == "hitl_escalation_triggered"


# ============================================================================
# Integration Tests
# ============================================================================


class TestHITLBindingWorkflow:
    """Test complete HITL binding workflow."""
    
    def test_full_workflow(self, sample_product_id: str):
        """Test complete binding lifecycle."""
        emitted_events: List[Dict[str, Any]] = []
        
        def capture_event(event_type: str, payload: Dict[str, Any]):
            emitted_events.append({"type": event_type, "payload": payload})
        
        registry = HITLBindingRegistry(emit_event_fn=capture_event)
        
        # Register default binding
        binding = create_default_hitl_binding(sample_product_id)
        registry.register(binding)
        
        # Find matching escalations
        context = {
            "trigger": EscalationTrigger.LOW_CONFIDENCE,
            "value": 0.3,
        }
        matches = registry.find_matching_escalations(sample_product_id, context)
        assert len(matches) == 1
        assert matches[0].action == EscalationAction.PAUSE_AND_WAIT
        
        # Try to modify (should fail)
        try:
            registry.update(binding.binding_id, enabled=False)
        except HITLBindingModificationError:
            pass
        
        # Verify trace event was emitted
        assert len(emitted_events) == 1
        assert emitted_events[0]["type"] == "hitl_binding_modification_blocked"
        
        # Verify binding is still active
        assert registry.get(binding.binding_id).enabled is True
