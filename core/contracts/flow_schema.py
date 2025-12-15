# ==============================
# Flow Contracts
# ==============================
"""
Flow contracts for master/.

Flows are declarative graphs/sequences of steps executed by the orchestrator.
These models define the stable structure for flow configs (YAML/JSON).

Intended usage:
- flow_loader parses YAML/JSON into FlowDef
- orchestrator executes StepDef list/graph
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, Field, ConfigDict

# ==============================
# Enums
# ==============================
class StepType(str, Enum):
    """Supported step types in a flow."""
    AGENT = "agent"
    TOOL = "tool"
    HUMAN_APPROVAL = "human_approval"
    SUBFLOW = "subflow"


class AutonomyLevel(str, Enum):
    """Autonomy level for a flow."""
    SUGGEST_ONLY = "suggest_only"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"


class BackendType(str, Enum):
    """Execution backend for steps that need backends."""
    LOCAL = "local"
    REMOTE = "remote"
    MCP = "mcp"


# ==============================
# Models
# ==============================
class RetryPolicy(BaseModel):
    """Retry policy for a step."""
    model_config = ConfigDict(extra="forbid")

    max_attempts: int = Field(default=1, ge=1, le=10, description="Max attempts including first try.")
    backoff_seconds: float = Field(default=0.0, ge=0.0, le=60.0, description="Fixed backoff between retries.")
    retry_on_codes: List[str] = Field(
        default_factory=list,
        description="Optional list of error codes eligible for retry.",
        validation_alias=AliasChoices("retry_on_codes", "retry_on"),
        serialization_alias="retry_on_codes",
    )


class StepDef(BaseModel):
    """
    Declarative step definition.

    Notes:
    - 'type' determines which fields are required (validated by orchestrator/loader logic).
    - params is a freeform dict but must be sanitized before tracing/persistence.
    """
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=80, description="Unique step id within the flow.")
    type: StepType = Field(..., description="Step type.")
    name: Optional[str] = Field(default=None, description="Human-friendly step name.")

    backend: Optional[BackendType] = Field(default=None, description="Execution backend (if applicable).")

    agent: Optional[str] = Field(default=None, description="Agent name when type=agent.")
    tool: Optional[str] = Field(default=None, description="Tool name when type=tool.")
    subflow: Optional[str] = Field(default=None, description="Subflow id/name when type=subflow.")

    message: Optional[str] = Field(default=None, description="Approval prompt when type=human_approval.")
    title: Optional[str] = Field(default=None, description="Optional UI title for human approval steps.")
    form: Dict[str, Any] = Field(default_factory=dict, description="Optional structured UI metadata.")

    params: Dict[str, Any] = Field(default_factory=dict, description="Step parameters/arguments.")
    retry: Optional[RetryPolicy] = Field(default=None, description="Retry policy for the step.")

    depends_on: List[str] = Field(default_factory=list, description="Optional dependency step ids.")
    next_steps: List[str] = Field(default_factory=list, description="Optional explicit next steps for graph flows.")


class FlowDef(BaseModel):
    """
    Declarative flow definition.

    The orchestrator treats this as the authoritative spec.
    """
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=80, description="Flow id unique within product.")
    description: Optional[str] = Field(default=None, description="Short description.")
    autonomy_level: AutonomyLevel = Field(default=AutonomyLevel.SEMI_AUTO, description="Autonomy behavior.")
    version: str = Field(default="v1", description="Flow version label.")

    steps: List[StepDef] = Field(..., min_length=1, description="Ordered list or graph definition of steps.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata for UI/runtime.")

    def to_dict(self) -> Dict[str, Any]:
        """Stable serialization wrapper."""
        return self.model_dump(mode="python")
