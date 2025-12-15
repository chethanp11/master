# ==============================
# Human-in-the-Loop (HITL)
# ==============================
"""
HITL helpers:
- Create approval requests
- Pause runs (PENDING_HUMAN)
- Resolve approvals

Rules:
- No direct DB calls here. Use MemoryBackend interface only.
- Keep payload scrubbed BEFORE calling into here (ideally via governance hooks/security).
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

from core.memory.base import ApprovalRecord
from core.memory.router import MemoryRouter


def new_approval_id() -> str:
    return f"appr_{uuid.uuid4().hex}"


class HitlService:
    def __init__(self, memory: MemoryRouter) -> None:
        self.memory = memory

    def create_approval(
        self,
        *,
        run_id: str,
        step_id: str,
        product: str,
        flow: str,
        requested_by: Optional[str],
        payload: Dict[str, Any],
    ) -> ApprovalRecord:
        now = int(time.time())
        approval = ApprovalRecord(
            approval_id=new_approval_id(),
            run_id=run_id,
            step_id=step_id,
            product=product,
            flow=flow,
            status="PENDING",
            requested_by=requested_by,
            requested_at=now,
            payload=payload,
        )
        self.memory.create_approval(approval)
        return approval

    def resolve_approval(
        self,
        *,
        approval_id: str,
        decision: str,
        resolved_by: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> None:
        self.memory.resolve_approval(
            approval_id,
            decision=decision,
            resolved_by=resolved_by,
            comment=comment,
        )