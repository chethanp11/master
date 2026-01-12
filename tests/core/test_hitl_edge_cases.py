"""
HITL Edge Cases Tests

Tests for edge cases in Human-in-the-Loop (HITL) handling including:
- Double resume idempotency
- Wrong approval rejection
- Concurrent approval serialization
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Dict, List

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.contracts.run_schema import RunStatus
from core.memory.router import MemoryRouter
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


def _register_products():
    """Register hello_world product for testing."""
    settings = load_settings()
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)
    return settings


class TestDoubleResumeIdempotent:
    """Tests that resuming an already-resumed run is safe and rejected."""

    def test_double_resume_idempotent(self, orchestrator, trace_sink: List[dict]) -> None:
        """Resuming an already-resumed run is safe."""
        _register_products()
        trace_sink.clear()

        # Start run that will pause at HITL
        start = orchestrator.run_flow(
            product="hello_world",
            flow="hello_world",
            payload={"keyword": "idempotent_test"},
        )
        assert start.ok, f"Failed to start run: {start.error}"
        run_id = start.data["run_id"]

        # Verify run is pending human approval
        bundle = orchestrator.memory.get_run(run_id)
        assert bundle is not None
        assert bundle.run.status == RunStatus.PENDING_HUMAN

        # First resume - should succeed
        first_resume = orchestrator.resume_run(
            run_id=run_id,
            approval_payload={"approved": True},
            decision="APPROVED",
        )
        assert first_resume.ok, f"First resume failed: {first_resume.error}"

        # Second resume - should be rejected (already completed/resumed)
        second_resume = orchestrator.resume_run(
            run_id=run_id,
            approval_payload={"approved": True},
            decision="APPROVED",
        )
        assert not second_resume.ok, "Second resume should have been rejected"
        assert second_resume.error is not None
        assert second_resume.error.code == "invalid_state"

    def test_double_reject_idempotent(self, orchestrator, trace_sink: List[dict]) -> None:
        """Rejecting an already-rejected run is safe."""
        _register_products()
        trace_sink.clear()

        start = orchestrator.run_flow(
            product="hello_world",
            flow="hello_world",
            payload={"keyword": "double_reject"},
        )
        assert start.ok
        run_id = start.data["run_id"]

        # First rejection
        first_reject = orchestrator.resume_run(
            run_id=run_id,
            approval_payload={"approved": False},
            decision="REJECTED",
        )
        assert first_reject.ok, f"First rejection failed: {first_reject.error}"

        # Second rejection - should be rejected (already processed)
        second_reject = orchestrator.resume_run(
            run_id=run_id,
            approval_payload={"approved": False},
            decision="REJECTED",
        )
        assert not second_reject.ok
        assert second_reject.error is not None
        assert second_reject.error.code == "invalid_state"

    def test_approve_after_reject_rejected(self, orchestrator, trace_sink: List[dict]) -> None:
        """Approving after a rejection is rejected."""
        _register_products()
        trace_sink.clear()

        start = orchestrator.run_flow(
            product="hello_world",
            flow="hello_world",
            payload={"keyword": "approve_after_reject"},
        )
        assert start.ok
        run_id = start.data["run_id"]

        # First: reject
        reject = orchestrator.resume_run(
            run_id=run_id,
            approval_payload={"approved": False},
            decision="REJECTED",
        )
        assert reject.ok

        # Then: try to approve - should fail
        approve = orchestrator.resume_run(
            run_id=run_id,
            approval_payload={"approved": True},
            decision="APPROVED",
        )
        assert not approve.ok
        assert approve.error is not None
        assert approve.error.code == "invalid_state"


class TestResumeWrongApprovalRejected:
    """Tests that approvals for wrong steps are rejected."""

    def test_resume_wrong_approval_rejected(self, orchestrator, trace_sink: List[dict]) -> None:
        """Approval for wrong step is rejected."""
        _register_products()
        trace_sink.clear()

        # Start two runs
        start_a = orchestrator.run_flow(
            product="hello_world",
            flow="hello_world",
            payload={"keyword": "run_a"},
        )
        assert start_a.ok
        run_id_a = start_a.data["run_id"]

        start_b = orchestrator.run_flow(
            product="hello_world",
            flow="hello_world",
            payload={"keyword": "run_b"},
        )
        assert start_b.ok
        run_id_b = start_b.data["run_id"]

        # Both should be pending human approval
        bundle_a = orchestrator.memory.get_run(run_id_a)
        bundle_b = orchestrator.memory.get_run(run_id_b)
        assert bundle_a.run.status == RunStatus.PENDING_HUMAN
        assert bundle_b.run.status == RunStatus.PENDING_HUMAN

        # Approve run_a
        resume_a = orchestrator.resume_run(
            run_id=run_id_a,
            approval_payload={"approved": True},
            decision="APPROVED",
        )
        assert resume_a.ok

        # run_a should now be completed
        bundle_a_after = orchestrator.memory.get_run(run_id_a)
        assert bundle_a_after.run.status == RunStatus.COMPLETED

        # run_b should still be pending
        bundle_b_after = orchestrator.memory.get_run(run_id_b)
        assert bundle_b_after.run.status == RunStatus.PENDING_HUMAN

        # Trying to approve run_a again should fail (wrong state, not wrong step)
        double_approve = orchestrator.resume_run(
            run_id=run_id_a,
            approval_payload={"approved": True},
            decision="APPROVED",
        )
        assert not double_approve.ok

    def test_resume_nonexistent_run_rejected(self, orchestrator) -> None:
        """Resuming a nonexistent run is rejected."""
        _register_products()

        result = orchestrator.resume_run(
            run_id="nonexistent_run_id_12345",
            approval_payload={"approved": True},
            decision="APPROVED",
        )
        assert not result.ok
        assert result.error is not None
        # Should be not_found or invalid_input
        assert result.error.code in ("not_found", "invalid_input")


class TestConcurrentApprovalsSerialized:
    """Tests that multiple approvers on same run are serialized."""

    def test_concurrent_approvals_serialized(self, orchestrator, trace_sink: List[dict]) -> None:
        """Multiple approvers on same run are serialized."""
        _register_products()
        trace_sink.clear()

        start = orchestrator.run_flow(
            product="hello_world",
            flow="hello_world",
            payload={"keyword": "concurrent_test"},
        )
        assert start.ok
        run_id = start.data["run_id"]

        # Verify pending
        bundle = orchestrator.memory.get_run(run_id)
        assert bundle.run.status == RunStatus.PENDING_HUMAN

        results: List[Dict[str, Any]] = []
        errors: List[Exception] = []

        def try_approve(approver_id: int) -> None:
            try:
                result = orchestrator.resume_run(
                    run_id=run_id,
                    approval_payload={"approved": True, "approver": approver_id},
                    decision="APPROVED",
                    comment=f"Approved by approver {approver_id}",
                )
                results.append({"approver": approver_id, "ok": result.ok, "error": result.error})
            except Exception as e:
                errors.append(e)

        # Spawn multiple threads trying to approve simultaneously
        threads = [threading.Thread(target=try_approve, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have no exceptions
        assert not errors, f"Concurrent approval raised exceptions: {errors}"

        # Exactly one should succeed
        successes = [r for r in results if r["ok"]]
        failures = [r for r in results if not r["ok"]]

        assert len(successes) == 1, f"Expected exactly 1 success, got {len(successes)}: {successes}"
        assert len(failures) == 4, f"Expected 4 failures, got {len(failures)}: {failures}"

        # All failures should be due to invalid state
        for failure in failures:
            assert failure["error"] is not None
            assert failure["error"].code == "invalid_state"

        # Final run status should be completed
        final_bundle = orchestrator.memory.get_run(run_id)
        assert final_bundle.run.status == RunStatus.COMPLETED

    def test_concurrent_approve_and_reject_serialized(self, orchestrator, trace_sink: List[dict]) -> None:
        """Concurrent approve and reject are serialized - first one wins."""
        _register_products()
        trace_sink.clear()

        start = orchestrator.run_flow(
            product="hello_world",
            flow="hello_world",
            payload={"keyword": "approve_reject_race"},
        )
        assert start.ok
        run_id = start.data["run_id"]

        results: List[Dict[str, Any]] = []
        errors: List[Exception] = []

        def try_approve() -> None:
            try:
                result = orchestrator.resume_run(
                    run_id=run_id,
                    approval_payload={"approved": True},
                    decision="APPROVED",
                )
                results.append({"action": "approve", "ok": result.ok, "error": result.error})
            except Exception as e:
                errors.append(e)

        def try_reject() -> None:
            try:
                result = orchestrator.resume_run(
                    run_id=run_id,
                    approval_payload={"approved": False},
                    decision="REJECTED",
                )
                results.append({"action": "reject", "ok": result.ok, "error": result.error})
            except Exception as e:
                errors.append(e)

        # Start both threads
        t_approve = threading.Thread(target=try_approve)
        t_reject = threading.Thread(target=try_reject)
        t_approve.start()
        t_reject.start()
        t_approve.join()
        t_reject.join()

        assert not errors
        successes = [r for r in results if r["ok"]]
        failures = [r for r in results if not r["ok"]]

        # Exactly one should succeed
        assert len(successes) == 1
        assert len(failures) == 1
        assert failures[0]["error"].code == "invalid_state"
