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
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    input_schema_ref: Optional[str] = None
    output_schema_ref: Optional[str] = None
    read_only: bool = False
    side_effect: bool = True
    sensitivity_class: SensitivityClass = SensitivityClass.UNKNOWN
    cost_hint: CostHint = CostHint.UNKNOWN


class AgentDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    purposes: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    input_schema_ref: Optional[str] = None
    output_schema_ref: Optional[str] = None
    cost_hint: CostHint = CostHint.UNKNOWN
    allowed_step_types: List[str] = Field(default_factory=list)
