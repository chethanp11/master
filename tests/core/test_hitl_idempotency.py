# ==============================
# HITL Idempotency Tests
# ==============================
from __future__ import annotations

from typing import List

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.contracts.run_schema import RunStatus
from core.memory.router import MemoryRouter
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


def _register_products():
    settings = load_settings()
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)
    return settings


def test_hitl_idempotency(orchestrator, trace_sink: List[dict]) -> None:
    settings = _register_products()
    trace_sink.clear()

    # RunA -> Approve, double approve should fail
    start = orchestrator.run_flow(product="sandbox", flow="hello_world", payload={})
    assert start.ok
    run_id = start.data["run_id"]
    bundle = orchestrator.memory.get_run(run_id)
    assert bundle and bundle.run.status == RunStatus.PENDING_HUMAN

    # Persisted state accessible through new router
    router = MemoryRouter(backend=orchestrator.memory.backend)
    fresh = router.get_run(run_id)
    assert fresh and fresh.run.status == RunStatus.PENDING_HUMAN

    ok = orchestrator.resume_run(run_id=run_id, approval_payload={"approved": True}, decision="APPROVED")
    assert ok.ok
    result = orchestrator.resume_run(run_id=run_id, approval_payload={"approved": True}, decision="APPROVED")
    assert not result.ok
    assert result.error and result.error.code == "invalid_state"

    trace_types = [event["kind"] for event in trace_sink]
    assert "pending_human" in trace_types
    assert "run_resumed" in trace_types
    assert "run_completed" in trace_types

    trace_sink.clear()

    # RunB -> Reject, double reject and approve-after-reject should fail
    start_b = orchestrator.run_flow(product="sandbox", flow="hello_world", payload={})
    assert start_b.ok
    run_b = start_b.data["run_id"]
    reject_ok = orchestrator.resume_run(run_id=run_b, approval_payload={"approved": False}, decision="REJECTED")
    assert reject_ok.ok

    second_reject = orchestrator.resume_run(run_id=run_b, approval_payload={"approved": False}, decision="REJECTED")
    assert not second_reject.ok
    assert second_reject.error and second_reject.error.code == "invalid_state"

    approve_after_reject = orchestrator.resume_run(run_id=run_b, approval_payload={"approved": True}, decision="APPROVED")
    assert not approve_after_reject.ok
    assert approve_after_reject.error and approve_after_reject.error.code == "invalid_state"
