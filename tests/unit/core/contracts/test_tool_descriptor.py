"""
Tests for ToolDescriptor contract.

AGT-DISC-TOOL-001...012: Tool descriptor validation tests.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.contracts.descriptors_schema import (
    CostHint,
    SensitivityClass,
    ToolDescriptor,
)


class TestToolDescriptor:
    """Test ToolDescriptor schema and validation."""

    def test_minimal_valid_descriptor(self) -> None:
        """AGT-DISC-TOOL-001: Name is required and must be unique."""
        desc = ToolDescriptor(name="test_tool")
        assert desc.name == "test_tool"
        assert desc.description == ""
        assert desc.version == "1.0.0"

    def test_full_descriptor(self) -> None:
        """AGT-DISC-TOOL-001...012: All fields can be set."""
        desc = ToolDescriptor(
            name="full_tool",
            description="A comprehensive tool",
            capabilities=["data_reading", "computation"],
            input_schema_ref="ToolInput",
            output_schema_ref="ToolOutput",
            read_only=True,
            side_effect=False,
            deterministic=True,
            domain_tags=["finance", "analytics"],
            sensitivity_class=SensitivityClass.HIGH,
            cost_hint=CostHint.LOW,
            version="2.1.0",
            deprecation="Use new_tool instead",
        )
        assert desc.name == "full_tool"
        assert desc.description == "A comprehensive tool"
        assert desc.capabilities == ["data_reading", "computation"]
        assert desc.read_only is True
        assert desc.side_effect is False
        assert desc.deterministic is True
        assert desc.domain_tags == ["finance", "analytics"]
        assert desc.version == "2.1.0"
        assert desc.deprecation == "Use new_tool instead"

    def test_descriptor_is_frozen(self) -> None:
        """AGT-DISC-TOOL: Model is frozen (immutable)."""
        desc = ToolDescriptor(name="frozen_tool")
        with pytest.raises(ValidationError):
            desc.name = "new_name"  # type: ignore

    def test_strict_validation_rejects_wrong_types(self) -> None:
        """AGT-DISC-TOOL: Strict validation mode enabled."""
        # Wrong type for name (int instead of str)
        with pytest.raises(ValidationError):
            ToolDescriptor(name=123)  # type: ignore
        
        # Wrong type for read_only (str instead of bool)
        with pytest.raises(ValidationError):
            ToolDescriptor(name="tool", read_only="true")  # type: ignore

    def test_extra_fields_forbidden(self) -> None:
        """AGT-DISC-TOOL: Extra fields are forbidden."""
        with pytest.raises(ValidationError):
            ToolDescriptor(name="tool", unknown_field="value")  # type: ignore

    def test_name_validation(self) -> None:
        """AGT-DISC-TOOL-001: Name must be 1-128 chars."""
        # Empty name rejected
        with pytest.raises(ValidationError):
            ToolDescriptor(name="")
        
        # Very long name rejected
        with pytest.raises(ValidationError):
            ToolDescriptor(name="x" * 129)
        
        # Max length accepted
        desc = ToolDescriptor(name="x" * 128)
        assert len(desc.name) == 128

    def test_to_json_schema(self) -> None:
        """AGT-DISC-TOOL-012: JSON serialization for external tooling."""
        desc = ToolDescriptor(
            name="json_tool",
            description="JSON test",
            capabilities=["test"],
            version="1.0.0",
        )
        json_data = desc.to_json_schema()
        assert json_data["name"] == "json_tool"
        assert json_data["description"] == "JSON test"
        assert json_data["capabilities"] == ["test"]
        assert json_data["version"] == "1.0.0"
        assert "sensitivity_class" in json_data

    def test_default_values(self) -> None:
        """AGT-DISC-TOOL: Default values are applied correctly."""
        desc = ToolDescriptor(name="defaults_tool")
        assert desc.capabilities == []
        assert desc.tags == []
        assert desc.input_schema_ref is None
        assert desc.output_schema_ref is None
        assert desc.read_only is False
        assert desc.side_effect is True
        assert desc.deterministic is True
        assert desc.domain_tags == []
        assert desc.sensitivity_class == SensitivityClass.UNKNOWN
        assert desc.cost_hint == CostHint.UNKNOWN
        assert desc.version == "1.0.0"
        assert desc.deprecation is None
