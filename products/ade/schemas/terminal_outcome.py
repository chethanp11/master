"""Terminal Outcome Schema for ADE.

TS-AGENT-TERM-001: TerminalOutcome enum with SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT.
TS-AGENT-TERM-002: PartialSuccessDetails with completed/missing steps and reason.
TS-AGENT-TERM-003: terminal_artifact containing explanations and supporting artifacts.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TerminalOutcome(str, Enum):
    """Terminal outcome enum per TS-AGENT-TERM-001."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    ASK_USER = "ask_user"
    ABORT = "abort"


class PartialSuccessDetails(BaseModel):
    """Details for partial success outcomes per TS-AGENT-TERM-002."""

    model_config = ConfigDict(extra="forbid")

    completed_steps: List[str] = Field(default_factory=list)
    missing_steps: List[str] = Field(default_factory=list)
    reason: str = ""


class TerminalArtifact(BaseModel):
    """Terminal artifact with explanation per TS-AGENT-TERM-003."""

    model_config = ConfigDict(extra="forbid")

    explanation: str = ""
    supporting_refs: List[str] = Field(default_factory=list)
    confidence: str = "medium"


class RunResult(BaseModel):
    """Run result schema with terminal outcome fields."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    outcome: TerminalOutcome = TerminalOutcome.SUCCESS
    partial_details: Optional[PartialSuccessDetails] = None
    terminal_artifact: Dict[str, Any] = Field(default_factory=dict)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
