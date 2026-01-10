from __future__ import annotations

# ==============================
# Internal Orchestrator Types
# ==============================
"""
Lightweight internal types for orchestration plumbing.
"""

from typing import Any, Dict, Optional, TypedDict


class StepExecSummary(TypedDict):
    step_id: str
    step_type: str
    ok: bool
    error: Optional[str]


class ToolBatchResultItem(TypedDict):
    tool: str
    alias: Optional[str]
    data: Dict[str, Any]
