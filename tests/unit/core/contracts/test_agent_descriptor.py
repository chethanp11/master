"""
Tests for AgentDescriptor contract.

AGT-DISC-AGT-001...012: Agent descriptor validation tests.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.contracts.descriptors_schema import (
    AgentDescriptor,
    CostHint,
    ReasoningType,
)


class TestAgentDescriptor:
    """Test AgentDescriptor schema and validation."""

    def test_minimal_valid_descriptor(self) -> None:
        """AGT-DISC-AGT-001: Name is required and must be unique."""
        desc = AgentDescriptor(name="test_agent")
        assert desc.name == "test_agent"
        assert desc.purpose == ""
        assert desc.version == "1.0.0"

    def test_full_descriptor(self) -> None:
        """AGT-DISC-AGT-001...012: All fields can be set."""
        desc = AgentDescriptor(
            name="full_agent",
            purpose="Primary reasoning agent",
            capabilities=["reasoning", "planning"],
            input_schema_ref="AgentInput",
            output_schema_ref="AgentOutput",
            reasoning_type=ReasoningType.ADVISORY,
            domain_tags=["finance", "analytics"],
            cost_hint=CostHint.MED,
            allowed_step_types=["agent", "evaluate"],
            requires_context_pack=True,
            min_confidence_threshold=0.8,
            version="2.0.0",
        )
        assert desc.name == "full_agent"
        assert desc.purpose == "Primary reasoning agent"
        assert desc.capabilities == ["reasoning", "planning"]
        assert desc.reasoning_type == ReasoningType.ADVISORY
        assert desc.domain_tags == ["finance", "analytics"]
        assert desc.requires_context_pack is True
        assert desc.min_confidence_threshold == 0.8
        assert desc.version == "2.0.0"

    def test_descriptor_is_frozen(self) -> None:
        """AGT-DISC-AGT: Model is frozen (immutable)."""
        desc = AgentDescriptor(name="frozen_agent")
        with pytest.raises(ValidationError):
            desc.name = "new_name"  # type: ignore

    def test_strict_validation_rejects_wrong_types(self) -> None:
        """AGT-DISC-AGT: Strict validation mode enabled."""
        # Wrong type for name (int instead of str)
        with pytest.raises(ValidationError):
            AgentDescriptor(name=123)  # type: ignore
        
        # Wrong type for requires_context_pack (str instead of bool)
        with pytest.raises(ValidationError):
            AgentDescriptor(name="agent", requires_context_pack="true")  # type: ignore

    def test_extra_fields_forbidden(self) -> None:
        """AGT-DISC-AGT: Extra fields are forbidden."""
        with pytest.raises(ValidationError):
            AgentDescriptor(name="agent", unknown_field="value")  # type: ignore

    def test_name_validation(self) -> None:
        """AGT-DISC-AGT-001: Name must be 1-128 chars."""
        # Empty name rejected
        with pytest.raises(ValidationError):
            AgentDescriptor(name="")
        
        # Very long name rejected
        with pytest.raises(ValidationError):
            AgentDescriptor(name="x" * 129)
        
        # Max length accepted
        desc = AgentDescriptor(name="x" * 128)
        assert len(desc.name) == 128

    def test_min_confidence_threshold_bounds(self) -> None:
        """AGT-DISC-AGT-011: Confidence threshold must be 0.0-1.0."""
        # Valid thresholds
        desc1 = AgentDescriptor(name="agent1", min_confidence_threshold=0.0)
        assert desc1.min_confidence_threshold == 0.0
        
        desc2 = AgentDescriptor(name="agent2", min_confidence_threshold=1.0)
        assert desc2.min_confidence_threshold == 1.0
        
        # Out of bounds
        with pytest.raises(ValidationError):
            AgentDescriptor(name="agent", min_confidence_threshold=-0.1)
        
        with pytest.raises(ValidationError):
            AgentDescriptor(name="agent", min_confidence_threshold=1.1)

    def test_reasoning_types(self) -> None:
        """AGT-DISC-AGT-006: Reasoning type classification."""
        for rt in ReasoningType:
            desc = AgentDescriptor(name=f"agent_{rt.value}", reasoning_type=rt)
            assert desc.reasoning_type == rt

    def test_to_json_schema(self) -> None:
        """JSON serialization for external tooling."""
        desc = AgentDescriptor(
            name="json_agent",
            purpose="JSON test",
            capabilities=["test"],
            reasoning_type=ReasoningType.CRITIC,
            version="1.0.0",
        )
        json_data = desc.to_json_schema()
        assert json_data["name"] == "json_agent"
        assert json_data["purpose"] == "JSON test"
        assert json_data["capabilities"] == ["test"]
        assert json_data["reasoning_type"] == "critic"
        assert json_data["version"] == "1.0.0"

    def test_default_values(self) -> None:
        """AGT-DISC-AGT: Default values are applied correctly."""
        desc = AgentDescriptor(name="defaults_agent")
        assert desc.purpose == ""
        assert desc.purposes == []
        assert desc.capabilities == []
        assert desc.tags == []
        assert desc.input_schema_ref is None
        assert desc.output_schema_ref is None
        assert desc.reasoning_type == ReasoningType.UNKNOWN
        assert desc.domain_tags == []
        assert desc.cost_hint == CostHint.UNKNOWN
        assert desc.allowed_step_types == []
        assert desc.requires_context_pack is False
        assert desc.min_confidence_threshold is None
        assert desc.version == "1.0.0"
