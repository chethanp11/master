# ==============================
# Orchestrator Runners
# ==============================
"""
Thin wrappers for CLI/API usage.

These wrappers keep gateway code simple and avoid coupling to Engine internals.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.orchestrator.engine import OrchestratorEngine


def run_flow(
    engine: OrchestratorEngine,
    *,
    product: str,
    flow: str,
    payload: Dict[str, Any],
    requested_by: Optional[str] = None,
) -> str:
    return engine.run_flow(product=product, flow=flow, payload=payload, requested_by=requested_by)


def resume_run(
    engine: OrchestratorEngine,
    *,
    run_id: str,
    decision: str,
    resolved_by: Optional[str] = None,
    comment: Optional[str] = None,
    approval_payload: Optional[Dict[str, Any]] = None,
) -> str:
    engine.resume_run(
        run_id=run_id,
        decision=decision,
        resolved_by=resolved_by,
        comment=comment,
        approval_payload=approval_payload or {},
    )
    return run_id