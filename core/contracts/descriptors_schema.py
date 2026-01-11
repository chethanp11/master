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
    """
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    capabilities: List[str] = Field(
        default_factory=list,
        description="Semantic tags like ['data_reading', 'computation', 'visualization']"
    )
    tags: List[str] = Field(default_factory=list)  # Legacy alias for capabilities
    input_schema_ref: Optional[str] = None
    output_schema_ref: Optional[str] = None
    read_only: bool = False
    side_effect: bool = True
    sensitivity_class: SensitivityClass = SensitivityClass.UNKNOWN
    cost_hint: CostHint = CostHint.UNKNOWN


class AgentDescriptor(BaseModel):
    """
    Descriptor for agents in the registry.
    
    Provides metadata for agent selection, governance, and cost estimation
    without requiring agent execution.
    """
    model_config = ConfigDict(extra="forbid")

    name: str
    purpose: str = Field(default="", description="Primary purpose of the agent")
    purposes: List[str] = Field(default_factory=list, description="List of purposes (legacy)")
    capabilities: List[str] = Field(
        default_factory=list,
        description="Semantic tags like ['reasoning', 'planning', 'evaluation']"
    )
    tags: List[str] = Field(default_factory=list)  # Legacy alias for capabilities
    input_schema_ref: Optional[str] = None
    output_schema_ref: Optional[str] = None
    cost_hint: CostHint = CostHint.UNKNOWN
    allowed_step_types: List[str] = Field(default_factory=list)
