# ==============================
# Human-in-the-Loop
# ==============================
"""
Human-in-the-loop (HITL) utilities.

This module creates and manages approval requests when a flow reaches a human_approval step.

Design:
- HITL is orchestrator-owned state (RunStatus.PENDING_HUMAN, StepStatus.WAITING_HUMAN)
- Persistence is handled ONLY by the injected memory backend (if provided)
- UI/API can resume by calling OrchestratorEngine.resume_run(run_id, decision_payload)

Decision payload is intentionally generic in v1:
- decision: "approve" | "reject"
- notes: optional string
- data: optional dict (human edits/overrides)

This module does NOT know about UI or API.
"""

# ==============================
# Imports
# ==============================
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.flow_schema import StepDef
from core.contracts.run_schema import RunRecord, StepRecord
from core.orchestrator.state import RunStatus, StepStatus

# ==============================
# Enums
# ==============================
class ApprovalDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


# ==============================
# Models
# ==============================
class ApprovalRequest(BaseModel):
    """
    Approval request captured when the orchestrator pauses.

    Stored in RunRecord.meta["approvals"][<step_id>] for v1.
    Memory backend may also persist this structure separately later.
    """
    model_config = ConfigDict(extra="forbid")

    approval_id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str = Field(...)

    step_id: str = Field(...)
    message: str = Field(...)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = Field(default=None)

    status: str = Field(default="pending", description="pending|approved|rejected")
    decision: Optional[ApprovalDecision] = Field(default=None)
    notes: Optional[str] = Field(default=None)

    # Optional human-provided edits/overrides
    data: Dict[str, Any] = Field(default_factory=dict)


class ResumePayload(BaseModel):
    """
    Payload used to resume a run from PENDING_HUMAN.

    Orchestrator/engine will validate this and then apply it.
    """
    model_config = ConfigDict(extra="forbid")

    decision: ApprovalDecision = Field(...)
    notes: Optional[str] = Field(default=None)
    data: Dict[str, Any] = Field(default_factory=dict)


# ==============================
# Public API
# ==============================
def create_approval_request(*, run: RunRecord, step: StepDef) -> ApprovalRequest:
    message = step.message or f"Approval required for step '{step.id}'."
    return ApprovalRequest(
        run_id=run.run_id,
        step_id=step.id,
        message=message,
    )


def attach_approval_to_run(*, run: RunRecord, approval: ApprovalRequest) -> None:
    approvals = run.meta.get("approvals")
    if approvals is None or not isinstance(approvals, dict):
        run.meta["approvals"] = {}
        approvals = run.meta["approvals"]
    approvals[approval.step_id] = approval.to_dict()  # stored as dict for portability


def mark_run_pending_human(*, run: RunRecord, step_id: str) -> None:
    run.status = RunStatus.PENDING_HUMAN
    run.current_step_id = step_id
    run.updated_at = datetime.utcnow()


def mark_step_waiting_human(*, step_rec: StepRecord) -> None:
    step_rec.status = StepStatus.WAITING_HUMAN
    step_rec.started_at = step_rec.started_at or datetime.utcnow()
    step_rec.ended_at = None


def apply_resume_payload(
    *,
    run: RunRecord,
    step_rec: StepRecord,
    payload: ResumePayload,
) -> None:
    approvals = run.meta.get("approvals", {})
    item = approvals.get(step_rec.step_id)
    if isinstance(item, dict):
        item["decided_at"] = datetime.utcnow().isoformat()
        item["decision"] = payload.decision.value
        item["notes"] = payload.notes
        item["data"] = payload.data
        item["status"] = "approved" if payload.decision == ApprovalDecision.APPROVE else "rejected"
        approvals[step_rec.step_id] = item
        run.meta["approvals"] = approvals

    # Record outcome in step meta for step-level audit
    step_rec.meta["hitl"] = {
        "decision": payload.decision.value,
        "notes": payload.notes,
        "data": payload.data,
        "decided_at": datetime.utcnow().isoformat(),
    }

    # Step ends when human decides
    step_rec.status = StepStatus.COMPLETED if payload.decision == ApprovalDecision.APPROVE else StepStatus.FAILED
    step_rec.ended_at = datetime.utcnow()

    # Run continues or fails based on decision
    run.status = RunStatus.RUNNING if payload.decision == ApprovalDecision.APPROVE else RunStatus.FAILED
    run.updated_at = datetime.utcnow()


# ==============================
# Helpers
# ==============================
def _safe_str(obj: Any) -> str:
    try:
        return str(obj)
    except Exception:
        return "<unprintable>"