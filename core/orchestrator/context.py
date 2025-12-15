# ==============================
# Orchestrator Context
# ==============================
"""
RunContext and StepContext for orchestrator execution.

Principles:
- Context is the in-memory working set for a run.
- Context is NOT persistence. Persistence happens via core/memory/* only.
- Context provides:
    - metadata (safe, non-secret)
    - artifacts (references + inline working objects)
    - trace hook placeholder (emit events via tracing pipeline elsewhere)

Intended usage:
- Orchestrator constructs RunContext at run start (or resume)
- Each step receives a StepContext derived from RunContext
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.flow_schema import StepDef
from core.contracts.run_schema import RunStatus, StepStatus

TraceHook = Callable[[str, Dict[str, Any]], None]


class RunContext(BaseModel):
    """
    Lightweight run context shared across step execution.

    Provides:
    - run metadata (ids, payload, artifacts)
    - trace hook used by agents/tools
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    run_id: str
    product: str
    flow: str
    status: RunStatus = RunStatus.RUNNING
    payload: Dict[str, Any] = Field(default_factory=dict)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)
    trace: Optional[TraceHook] = Field(default=None)

    def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        if self.trace is None:
            return
        self.trace(event_type, payload)

    def new_step(
        self,
        step_def: Optional[StepDef] = None,
        *,
        step_id: Optional[str] = None,
        step_type: Optional[str] = None,
        backend: Optional[str] = None,
        target: Optional[str] = None,
    ) -> "StepContext":
        if step_def is not None:
            step_id = step_def.id or step_id or "step"
            step_type = step_def.type.value if hasattr(step_def.type, "value") else str(step_def.type)
            backend = backend or (step_def.backend.value if getattr(step_def.backend, "value", None) else step_def.backend)
            target = target or step_def.agent or step_def.tool
        if step_id is None or step_type is None:
            raise ValueError("step_id and step_type are required when step_def is not provided")
        return StepContext(
            run=self,
            step=step_def,
            step_id=step_id,
            type=step_type,
            backend=backend,
            target=target,
        )


class StepContext(BaseModel):
    """Execution context for a single step."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    run: RunContext
    step: Optional[StepDef] = Field(default=None)
    step_id: str
    type: str
    backend: Optional[str] = None
    target: Optional[str] = None
    status: StepStatus = StepStatus.NOT_STARTED
    attempt: int = 0

    def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        merged = {"step_id": self.step_id, **payload}
        self.run.emit(event_type, merged)

    @property
    def run_id(self) -> str:
        return self.run.run_id

    @property
    def product(self) -> str:
        return self.run.product

    @property
    def flow(self) -> str:
        return self.run.flow
