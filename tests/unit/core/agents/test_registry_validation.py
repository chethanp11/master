"""
Tests for Descriptor Validation in Registry (IMP-042).

Tests AGT-DISC-VAL-001...006 and AGT-DISC-SCHEMA-001...005:
- Registration validates descriptor schema
- Name conflicts rejected
- Missing required fields rejected with error details
- Optional fields don't cause failures
- registration_failed trace event on validation errors
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

from core.agents.base import BaseAgent
from core.agents.registry import AgentRegistry, DescriptorValidationError
from core.contracts.agent_schema import AgentResult, AgentMeta
from core.contracts.descriptors_schema import (
    AgentDescriptor,
    ToolDescriptor,
    CostHint,
    ReasoningType,
)
from core.contracts.tool_schema import ToolResult, ToolMeta
from core.orchestrator.context import StepContext
from core.tools.base import BaseTool
from core.tools.registry import ToolRegistry


class _TestAgent(BaseAgent):
    name = "test_agent"
    description = "Test agent for validation tests."

    def run(self, step_context: StepContext) -> AgentResult:
        meta = AgentMeta(agent_name=self.name)
        return AgentResult(ok=True, data={"ok": True}, error=None, meta=meta)


class _TestTool(BaseTool):
    name = "test_tool"
    description = "Test tool for validation tests."

    def run(self, params: Dict[str, Any], ctx: StepContext) -> ToolResult:
        meta = ToolMeta(tool_name=self.name, backend="local")
        return ToolResult(ok=True, data={"ok": True}, error=None, meta=meta)


class TestDescriptorValidationError:
    """Tests for DescriptorValidationError exception."""

    def test_error_exists(self) -> None:
        """AGT-DISC-VAL-001: DescriptorValidationError should exist."""
        assert issubclass(DescriptorValidationError, Exception)

    def test_error_has_field_details(self) -> None:
        """AGT-DISC-VAL-002: Error should include field details."""
        error = DescriptorValidationError(
            "Validation failed",
            descriptor_name="test",
            field_errors={"name": "required field missing"},
        )
        assert error.descriptor_name == "test"
        assert "name" in error.field_errors
        assert "required field missing" in error.field_errors["name"]

    def test_error_string_representation(self) -> None:
        """Error should have informative string representation."""
        error = DescriptorValidationError(
            "Invalid descriptor",
            descriptor_name="bad_agent",
            field_errors={"name": "too short"},
        )
        assert "bad_agent" in str(error)
        assert "Invalid descriptor" in str(error)


class TestAgentRegistryValidation:
    """Tests for AgentRegistry descriptor validation."""

    def setup_method(self) -> None:
        """Clear registry before each test."""
        AgentRegistry.clear()

    def test_valid_descriptor_accepted(self) -> None:
        """AGT-DISC-VAL-003: Valid descriptors should be accepted."""
        descriptor = AgentDescriptor(
            name="valid_agent",
            purpose="A valid test agent",
            capabilities=["testing"],
        )
        AgentRegistry.register(
            "valid_agent",
            lambda: _TestAgent(),
            descriptor=descriptor,
        )
        assert AgentRegistry.has("valid_agent")

    def test_name_conflict_rejected(self) -> None:
        """AGT-DISC-VAL-004: Name conflicts should be rejected."""
        AgentRegistry.register("conflict_agent", lambda: _TestAgent())
        
        with pytest.raises(ValueError) as exc_info:
            AgentRegistry.register("conflict_agent", lambda: _TestAgent())
        
        assert "already registered" in str(exc_info.value).lower()

    def test_name_conflict_with_overwrite_allowed(self) -> None:
        """Name conflicts with overwrite=True should succeed."""
        AgentRegistry.register("overwrite_agent", lambda: _TestAgent())
        AgentRegistry.register(
            "overwrite_agent",
            lambda: _TestAgent(),
            overwrite=True,
        )
        assert AgentRegistry.has("overwrite_agent")

    def test_invalid_descriptor_dict_rejected(self) -> None:
        """AGT-DISC-VAL-005: Invalid descriptor dicts should be rejected."""
        invalid_descriptor = {
            "name": "",  # Empty name is invalid
            "purpose": "Test",
        }
        
        with pytest.raises(DescriptorValidationError) as exc_info:
            AgentRegistry.register(
                "invalid_agent",
                lambda: _TestAgent(),
                descriptor=invalid_descriptor,
            )
        
        assert exc_info.value.descriptor_name == "invalid_agent"

    def test_optional_fields_dont_cause_failure(self) -> None:
        """AGT-DISC-SCHEMA-001: Optional fields should not cause failures."""
        # Minimal descriptor with only required fields
        descriptor = AgentDescriptor(
            name="minimal_agent",
        )
        AgentRegistry.register(
            "minimal_agent",
            lambda: _TestAgent(),
            descriptor=descriptor,
        )
        
        retrieved = AgentRegistry.get_descriptor("minimal_agent")
        assert retrieved.name == "minimal_agent"
        # Optional fields should have defaults
        assert retrieved.purpose == ""
        assert retrieved.capabilities == []

    def test_schema_version_compatibility(self) -> None:
        """AGT-DISC-SCHEMA-002: Schema version should be checked."""
        descriptor = AgentDescriptor(
            name="versioned_agent",
            version="2.0.0",
        )
        AgentRegistry.register(
            "versioned_agent",
            lambda: _TestAgent(),
            descriptor=descriptor,
        )
        
        retrieved = AgentRegistry.get_descriptor("versioned_agent")
        assert retrieved.version == "2.0.0"


class TestToolRegistryValidation:
    """Tests for ToolRegistry descriptor validation."""

    def setup_method(self) -> None:
        """Clear registry before each test."""
        ToolRegistry.clear()

    def test_valid_descriptor_accepted(self) -> None:
        """Valid tool descriptors should be accepted."""
        descriptor = ToolDescriptor(
            name="valid_tool",
            description="A valid test tool",
            capabilities=["testing"],
        )
        ToolRegistry.register(
            "valid_tool",
            lambda: _TestTool(),
            descriptor=descriptor,
        )
        assert ToolRegistry.has("valid_tool")

    def test_name_conflict_rejected(self) -> None:
        """Name conflicts should be rejected for tools."""
        ToolRegistry.register("conflict_tool", lambda: _TestTool())
        
        with pytest.raises(ValueError) as exc_info:
            ToolRegistry.register("conflict_tool", lambda: _TestTool())
        
        assert "already registered" in str(exc_info.value).lower()

    def test_invalid_descriptor_dict_rejected(self) -> None:
        """Invalid tool descriptor dicts should be rejected."""
        invalid_descriptor = {
            "name": "",  # Empty name is invalid
        }
        
        with pytest.raises(DescriptorValidationError) as exc_info:
            ToolRegistry.register(
                "invalid_tool",
                lambda: _TestTool(),
                descriptor=invalid_descriptor,
            )
        
        assert exc_info.value.descriptor_name == "invalid_tool"


class TestRegistrationFailedEvent:
    """Tests for registration_failed trace event emission."""

    def test_registration_failed_event_emitted_on_validation_error(self) -> None:
        """AGT-DISC-VAL-006: registration_failed event should be emitted."""
        AgentRegistry.clear()
        events: List[Dict[str, Any]] = []
        
        def capture_event(**kwargs: Any) -> None:
            events.append(kwargs)
        
        invalid_descriptor = {"name": ""}  # Invalid
        
        with pytest.raises(DescriptorValidationError):
            AgentRegistry.register(
                "bad_agent",
                lambda: _TestAgent(),
                descriptor=invalid_descriptor,
                emit_event_fn=capture_event,
            )
        
        assert len(events) == 1
        assert events[0]["kind"] == "registration_failed"
        assert events[0]["payload"]["component_type"] == "agent"
        assert events[0]["payload"]["name"] == "bad_agent"

    def test_registration_failed_event_includes_field_errors(self) -> None:
        """registration_failed event should include field error details."""
        ToolRegistry.clear()
        events: List[Dict[str, Any]] = []
        
        def capture_event(**kwargs: Any) -> None:
            events.append(kwargs)
        
        invalid_descriptor = {"name": ""}  # Invalid
        
        with pytest.raises(DescriptorValidationError):
            ToolRegistry.register(
                "bad_tool",
                lambda: _TestTool(),
                descriptor=invalid_descriptor,
                emit_event_fn=capture_event,
            )
        
        assert len(events) == 1
        assert "field_errors" in events[0]["payload"]

