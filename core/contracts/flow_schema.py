# ==============================
# Flow Contracts
# ==============================
"""
Flow contracts for master/.

Flows are declarative graphs/sequences of steps executed by the orchestrator.
These models define the stable structure for flow configs (YAML/JSON).

This module consolidates:
- flow_schema.py (FlowDef, StepDef, StepType, etc.)
- branch_schema.py (ConditionExpr, ConditionOp, etc.)
- loop_schema.py (StopConditionExpr, LoopState, etc.)

Intended usage:
- flow_loader parses YAML/JSON into FlowDef
- orchestrator executes StepDef list/graph
"""

from __future__ import annotations


# ==============================
# Imports
# ==============================

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from typing_extensions import Annotated, Literal

from pydantic import AliasChoices, BaseModel, Field, ConfigDict, model_validator

from core.contracts.user_input_schema import UserInputRequest


# ==============================
# Branch Condition Types (from branch_schema)
# ==============================

ConditionOp = Literal["==", "!=", ">", ">=", "<", "<=", "in", "contains", "exists"]
ConditionScalar = Union[str, int, float, bool, None]
ConditionValue = Union[ConditionScalar, List[ConditionScalar]]

_MAX_CONDITION_NODES = 20


class ConditionExpr(BaseModel):
    """
    Deterministic condition expressions for branching.
    Supports path/op comparisons and nested all/any groups.
    """
    model_config = ConfigDict(extra="forbid")

    path: Optional[str] = None
    op: Optional[ConditionOp] = None
    value: Optional[ConditionValue] = None
    all: Optional[List["ConditionExpr"]] = Field(default=None)
    any: Optional[List["ConditionExpr"]] = Field(default=None)

    @model_validator(mode="after")
    def _validate_shape(self) -> "ConditionExpr":
        has_path = self.path is not None or self.op is not None
        has_group = self.all is not None or self.any is not None
        if has_path and has_group:
            raise ValueError("condition cannot mix path/op with all/any")
        if not has_path and not has_group:
            raise ValueError("condition must include path/op or all/any")
        if has_path:
            if not self.path or not self.op:
                raise ValueError("condition path and op are required")
            if self.op == "exists":
                return self
            if self.value is None:
                raise ValueError("condition value is required for op")
        if self.all is not None and not self.all:
            raise ValueError("all must contain at least one condition")
        if self.any is not None and not self.any:
            raise ValueError("any must contain at least one condition")
        if self._count_nodes() > _MAX_CONDITION_NODES:
            raise ValueError("condition too complex")
        return self

    def _count_nodes(self) -> int:
        if self.all:
            return 1 + sum(child._count_nodes() for child in self.all)
        if self.any:
            return 1 + sum(child._count_nodes() for child in self.any)
        return 1


ConditionExpr.model_rebuild()


# ==============================
# Loop Stop Condition Types (from loop_schema)
# ==============================

_MAX_STOP_NODES = 20


class ConfidenceThreshold(BaseModel):
    """Stop condition based on confidence threshold."""
    model_config = ConfigDict(extra="forbid")

    kind: Literal["confidence_threshold"]
    path: str
    op: Literal[">=", ">", "<", "<="] = ">="
    value: float


class NoMissingEvidence(BaseModel):
    """Stop condition when no missing evidence exists."""
    model_config = ConfigDict(extra="forbid")

    kind: Literal["no_missing_evidence"]
    path: str
    op: Literal["empty"] = "empty"


class StopConditionGroup(BaseModel):
    """Group of stop conditions with all/any logic."""
    model_config = ConfigDict(extra="forbid")

    kind: Literal["all", "any"]
    conditions: List["StopConditionExpr"]

    @model_validator(mode="after")
    def _validate_group(self) -> "StopConditionGroup":
        if not self.conditions:
            raise ValueError("stop condition group must include at least one condition")
        if self._count_nodes() > _MAX_STOP_NODES:
            raise ValueError("stop condition too complex")
        return self

    def _count_nodes(self) -> int:
        return 1 + sum(_count_stop_nodes(cond) for cond in self.conditions)


StopConditionExpr = Annotated[
    Union[ConfidenceThreshold, NoMissingEvidence, StopConditionGroup],
    Field(discriminator="kind"),
]


class LoopState(BaseModel):
    """Runtime state for bounded loops."""
    model_config = ConfigDict(extra="forbid")

    iters_used: int = 0
    terminated: bool = False
    termination_reason: str = ""
    last_evaluated_condition: Optional[Dict[str, Any]] = None
    started_at: Optional[int] = None
    ended_at: Optional[int] = None


def _count_stop_nodes(condition: StopConditionExpr) -> int:
    if isinstance(condition, StopConditionGroup):
        return condition._count_nodes()
    return 1


StopConditionGroup.model_rebuild()


# ==============================
# Flow Enums
# ==============================

class StepType(str, Enum):
    """Supported step types in a flow."""
    AGENT = "agent"
    TOOL = "tool"
    HUMAN_APPROVAL = "human_approval"
    USER_INPUT = "user_input"
    PLAN_PROPOSAL = "plan_proposal"
    PLAN_PROPOSE = "plan_propose"
    PLAN_GATE = "plan_gate"
    PLAN_EXECUTE = "plan_execute"
    BRANCH = "branch"
    REPEAT_UNTIL = "repeat_until"
    TOOL_BATCH = "tool_batch"
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


# Backwards-compatible lowercase attribute access (tests/users may reference StepType.tool)
StepType.agent = StepType.AGENT  # type: ignore[attr-defined]
StepType.tool = StepType.TOOL  # type: ignore[attr-defined]
StepType.human_approval = StepType.HUMAN_APPROVAL  # type: ignore[attr-defined]
StepType.user_input = StepType.USER_INPUT  # type: ignore[attr-defined]
StepType.plan_proposal = StepType.PLAN_PROPOSAL  # type: ignore[attr-defined]
StepType.plan_propose = StepType.PLAN_PROPOSE  # type: ignore[attr-defined]
StepType.plan_gate = StepType.PLAN_GATE  # type: ignore[attr-defined]
StepType.plan_execute = StepType.PLAN_EXECUTE  # type: ignore[attr-defined]
StepType.branch = StepType.BRANCH  # type: ignore[attr-defined]
StepType.repeat_until = StepType.REPEAT_UNTIL  # type: ignore[attr-defined]
StepType.tool_batch = StepType.TOOL_BATCH  # type: ignore[attr-defined]
StepType.subflow = StepType.SUBFLOW  # type: ignore[attr-defined]

AutonomyLevel.suggest_only = AutonomyLevel.SUGGEST_ONLY  # type: ignore[attr-defined]
AutonomyLevel.semi_auto = AutonomyLevel.SEMI_AUTO  # type: ignore[attr-defined]
AutonomyLevel.full_auto = AutonomyLevel.FULL_AUTO  # type: ignore[attr-defined]


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
    allow_tools: List[str] = Field(default_factory=list, description="Optional allowlist for plan execution tools.")
    allow_agents: List[str] = Field(default_factory=list, description="Optional allowlist for plan execution agents.")
    when: Optional[ConditionExpr] = Field(default=None, description="Branch condition when type=branch.")
    then: Optional[str] = Field(default=None, description="Next step id when branch condition is true.")
    else_step: Optional[str] = Field(
        default=None,
        description="Next step id when branch condition is false.",
        validation_alias=AliasChoices("else", "else_step"),
        serialization_alias="else",
    )
    max_iters: Optional[int] = Field(default=None, description="Maximum iterations when type=repeat_until.")
    stop_condition: Optional[StopConditionExpr] = Field(default=None, description="Stop condition when type=repeat_until.")
    iteration_step: Optional[str] = Field(default=None, description="Step id executed per iteration.")
    on_terminate: Optional[str] = Field(default=None, description="Optional next step id after loop termination.")
    tools: List["ToolBatchItem"] = Field(default_factory=list, description="Tool batch items when type=tool_batch.")
    parallel: bool = Field(default=False, description="Whether to run tool batch items in parallel.")

    @model_validator(mode="after")
    def _validate_target_fields(self) -> "StepDef":
        if self.type == StepType.TOOL and not self.tool:
            raise ValueError("tool steps require the 'tool' field")
        if self.type == StepType.AGENT and not self.agent:
            raise ValueError("agent steps require the 'agent' field")
        if self.type == StepType.PLAN_PROPOSAL and not self.agent:
            raise ValueError("plan_proposal steps require the 'agent' field")
        if self.type == StepType.PLAN_PROPOSE and not self.agent and "plan" not in (self.params or {}):
            raise ValueError("plan_propose steps require 'agent' or params.plan")
        if self.type == StepType.BRANCH:
            if self.when is None or not self.then or not self.else_step:
                raise ValueError("branch steps require when/then/else")
        if self.type == StepType.REPEAT_UNTIL:
            if self.max_iters is None or self.max_iters < 1:
                raise ValueError("repeat_until steps require max_iters >= 1")
            if self.stop_condition is None or not self.iteration_step:
                raise ValueError("repeat_until steps require stop_condition and iteration_step")
        if self.type == StepType.TOOL_BATCH:
            if not self.tools:
                raise ValueError("tool_batch steps require tools")
            if len(self.tools) > 20:
                raise ValueError("tool_batch steps exceed max tools")
        if self.type == StepType.USER_INPUT:
            params = self.params or {}
            if "question_set" not in params:
                UserInputRequest.model_validate(params)
        if self.type == StepType.SUBFLOW:
            raise ValueError("subflow steps are not supported in v1; compose flows at the entrypoint")
        return self


class ToolBatchItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    alias: Optional[str] = None


StepDef.model_rebuild()


class FlowDef(BaseModel):
    """
    Declarative flow definition.

    The orchestrator treats this as the authoritative spec.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="Flow id unique within product.",
        validation_alias=AliasChoices("id", "name"),
        serialization_alias="id",
    )
    description: Optional[str] = Field(default=None, description="Short description.")
    autonomy_level: AutonomyLevel = Field(default=AutonomyLevel.SEMI_AUTO, description="Autonomy behavior.")
    version: str = Field(default="v1", description="Flow version label.")

    steps: List[StepDef] = Field(..., min_length=1, description="Ordered list or graph definition of steps.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata for UI/runtime.")

    def to_dict(self) -> Dict[str, Any]:
        """Stable serialization wrapper."""
        return self.model_dump(mode="python")

    @property
    def name(self) -> str:
        return self.id


# ==============================
# Exports
# ==============================

__all__ = [
    # Branch conditions (from branch_schema)
    "ConditionOp",
    "ConditionScalar",
    "ConditionValue",
    "ConditionExpr",
    # Loop conditions (from loop_schema)
    "ConfidenceThreshold",
    "NoMissingEvidence",
    "StopConditionGroup",
    "StopConditionExpr",
    "LoopState",
    # Flow types
    "StepType",
    "AutonomyLevel",
    "BackendType",
    # Flow models
    "RetryPolicy",
    "StepDef",
    "ToolBatchItem",
    "FlowDef",
]
