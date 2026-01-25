from __future__ import annotations

# ==============================
# Descriptor Contracts
# ==============================
"""
Descriptor contracts for tool/agent registries.

These schemas provide a read-only catalog surface that is safe to query without
executing tools or agents.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SensitivityClass(str, Enum):
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class CostHint(str, Enum):
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class ToolDescriptor(BaseModel):
    """
    Descriptor for tools in the registry.
    
    Provides metadata for tool selection, governance, and cost estimation
    without requiring tool execution.
    
    AGT-DISC-TOOL-001...012: Frozen, strictly validated descriptor contract.
    """
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    # AGT-DISC-TOOL-001: Globally unique name
    name: str = Field(..., min_length=1, max_length=128, description="Globally unique tool name")
    
    # AGT-DISC-TOOL-002: Human-readable description
    description: str = Field(default="", max_length=1024, description="Human-readable description")
    
    # AGT-DISC-TOOL-003: Capability tags for discovery matching
    capabilities: List[str] = Field(
        default_factory=list,
        description="Semantic tags like ['data_reading', 'computation', 'visualization']"
    )
    tags: List[str] = Field(default_factory=list)  # Legacy alias for capabilities
    
    # AGT-DISC-TOOL-004/005: Input/output schema references
    input_schema_ref: Optional[str] = Field(
        default=None, description="JSON Schema reference for input validation"
    )
    output_schema_ref: Optional[str] = Field(
        default=None, description="JSON Schema reference for output validation"
    )
    
    # AGT-DISC-TOOL-006/007: Side effects and determinism flags
    read_only: bool = Field(default=False, description="True if tool does not modify external state")
    side_effect: bool = Field(default=True, description="True if tool has side effects")
    deterministic: bool = Field(default=True, description="True if tool output is deterministic")
    
    # AGT-DISC-TOOL-008: Domain scoping
    domain_tags: List[str] = Field(
        default_factory=list, description="Product domain tags for scoped discovery"
    )
    
    # AGT-DISC-TOOL-009: Sensitivity and cost classification
    sensitivity_class: SensitivityClass = SensitivityClass.UNKNOWN
    cost_hint: CostHint = CostHint.UNKNOWN
    
    # AGT-DISC-TOOL-010/011: Version and deprecation
    version: str = Field(default="1.0.0", description="Semantic version string")
    deprecation: Optional[str] = Field(
        default=None, description="Deprecation notice if tool is deprecated"
    )
    
    def to_json_schema(self) -> dict:
        """AGT-DISC-TOOL-012: JSON serialization for external tooling."""
        return self.model_dump(mode="json")


class ReasoningType(str, Enum):
    """Reasoning strategy type for agent classification."""
    ADVISORY = "advisory"
    CRITIC = "critic"
    LADDER = "ladder"
    SELECTOR = "selector"
    PLANNER = "planner"
    UNKNOWN = "unknown"


class AgentDescriptor(BaseModel):
    """
    Descriptor for agents in the registry.
    
    Provides metadata for agent selection, governance, and cost estimation
    without requiring agent execution.
    
    AGT-DISC-AGT-001...012: Frozen, strictly validated descriptor contract.
    """
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    # AGT-DISC-AGT-001: Globally unique name
    name: str = Field(..., min_length=1, max_length=128, description="Globally unique agent name")
    
    # AGT-DISC-AGT-002: Human-readable description/purpose
    purpose: str = Field(default="", max_length=1024, description="Primary purpose of the agent")
    purposes: List[str] = Field(default_factory=list, description="List of purposes (legacy)")
    
    # AGT-DISC-AGT-003: Capability tags for discovery matching
    capabilities: List[str] = Field(
        default_factory=list,
        description="Semantic tags like ['reasoning', 'planning', 'evaluation']"
    )
    tags: List[str] = Field(default_factory=list)  # Legacy alias for capabilities
    
    # AGT-DISC-AGT-004/005: Input/output schema references
    input_schema_ref: Optional[str] = Field(
        default=None, description="JSON Schema reference for input validation"
    )
    output_schema_ref: Optional[str] = Field(
        default=None, description="JSON Schema reference for output validation"
    )
    
    # AGT-DISC-AGT-006: Reasoning type classification
    reasoning_type: ReasoningType = Field(
        default=ReasoningType.UNKNOWN, description="Reasoning strategy type"
    )
    
    # AGT-DISC-AGT-007: Domain scoping
    domain_tags: List[str] = Field(
        default_factory=list, description="Product domain tags for scoped discovery"
    )
    
    # AGT-DISC-AGT-008: Cost classification
    cost_hint: CostHint = CostHint.UNKNOWN
    
    # AGT-DISC-AGT-009: Step type constraints
    allowed_step_types: List[str] = Field(default_factory=list)
    
    # AGT-DISC-AGT-010: Context pack requirement
    requires_context_pack: bool = Field(
        default=False, description="True if agent requires a ContextPack"
    )
    
    # AGT-DISC-AGT-011: Minimum confidence threshold
    min_confidence_threshold: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Minimum confidence threshold for agent"
    )
    
    # AGT-DISC-AGT-012: Version
    version: str = Field(default="1.0.0", description="Semantic version string")
    
    def to_json_schema(self) -> dict:
        """JSON serialization for external tooling."""
        return self.model_dump(mode="json")
