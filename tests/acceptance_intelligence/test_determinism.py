"""
Phase 0: Determinism Baseline Tests

These tests lock in deterministic behavior that MUST hold before and after refactoring.
They verify that identical inputs produce identical outputs and that step transitions
are reproducible.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest

from core.contracts.run_schema import RunStatus, StepStatus
from tests.acceptance_intelligence import helpers


def _get_step_outputs(engine, run_id: str) -> Dict[str, Any]:
    """Extract all step outputs from a run."""
    bundle = engine.memory.get_run(run_id)
    assert bundle is not None
    return {step.step_id: step.output for step in bundle.steps}


def _get_step_sequence(engine, run_id: str) -> List[tuple[str, str, str]]:
    """Extract step sequence as (step_id, type, status) tuples."""
    bundle = engine.memory.get_run(run_id)
    assert bundle is not None
    return [(step.step_id, step.type, step.status.value) for step in bundle.steps]


def _get_artifact_data(step_output: Dict[str, Any]) -> Any:
    """Extract artifact data from step output, handling various formats."""
    if not step_output:
        return None
    if "data" in step_output:
        return step_output["data"]
    return step_output


class TestSameInputProducesSameOutput:
    """Verify that running the same flow twice with identical input produces identical artifacts."""

    def test_pure_tool_flow_determinism(self, tmp_path: Path) -> None:
        """Run a pure tool flow twice and assert outputs are identical."""
        helpers.build_product(
            tmp_path,
            product_name="determinism_test",
            flows={
                "pure_tool": """
                name: pure_tool
                version: "1.0"
                steps:
                  - id: echo_first
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "{{payload.message}}"
                  - id: echo_second
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "{{payload.suffix}}"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="determinism_test")

        payload = {"message": "hello", "suffix": "world"}

        # Run 1
        result_a = engine.run_flow(product="determinism_test", flow="pure_tool", payload=payload)
        assert result_a.ok, f"Run A failed: {result_a.error}"
        run_id_a = result_a.data["run_id"]

        # Run 2
        result_b = engine.run_flow(product="determinism_test", flow="pure_tool", payload=payload)
        assert result_b.ok, f"Run B failed: {result_b.error}"
        run_id_b = result_b.data["run_id"]

        # Compare outputs
        outputs_a = _get_step_outputs(engine, run_id_a)
        outputs_b = _get_step_outputs(engine, run_id_b)

        # Artifact data should be identical
        assert _get_artifact_data(outputs_a["echo_first"]) == _get_artifact_data(outputs_b["echo_first"])
        assert _get_artifact_data(outputs_a["echo_second"]) == _get_artifact_data(outputs_b["echo_second"])

    def test_multiple_runs_same_final_status(self, tmp_path: Path) -> None:
        """Multiple runs with same input should reach same final status."""
        helpers.build_product(
            tmp_path,
            product_name="status_determinism",
            flows={
                "simple": """
                name: simple
                version: "1.0"
                steps:
                  - id: echo
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "test"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="status_determinism")

        statuses = []
        for _ in range(3):
            result = engine.run_flow(product="status_determinism", flow="simple", payload={})
            assert result.ok
            bundle = engine.memory.get_run(result.data["run_id"])
            statuses.append(bundle.run.status)

        assert all(s == statuses[0] for s in statuses), "All runs should have same final status"


class TestStepTransitionsAreDeterministic:
    """Verify that step order and transitions match flow definition."""

    def test_step_order_matches_flow_definition(self, tmp_path: Path) -> None:
        """Steps execute in the order defined in the flow YAML."""
        helpers.build_product(
            tmp_path,
            product_name="order_test",
            flows={
                "ordered_flow": """
                name: ordered_flow
                version: "1.0"
                steps:
                  - id: step_one
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "first"
                  - id: step_two
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "second"
                  - id: step_three
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "third"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="order_test")

        result = engine.run_flow(product="order_test", flow="ordered_flow", payload={})
        assert result.ok

        sequence = _get_step_sequence(engine, result.data["run_id"])
        step_ids = [s[0] for s in sequence]

        assert step_ids == ["step_one", "step_two", "step_three"], f"Steps out of order: {step_ids}"

    def test_all_steps_complete_in_sequence(self, tmp_path: Path) -> None:
        """All steps in a simple flow should complete."""
        helpers.build_product(
            tmp_path,
            product_name="complete_test",
            flows={
                "complete_flow": """
                name: complete_flow
                version: "1.0"
                steps:
                  - id: a
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "a"
                  - id: b
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "b"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="complete_test")

        result = engine.run_flow(product="complete_test", flow="complete_flow", payload={})
        assert result.ok

        sequence = _get_step_sequence(engine, result.data["run_id"])

        for step_id, step_type, status in sequence:
            assert status == StepStatus.COMPLETED.value, f"Step {step_id} has status {status}, expected COMPLETED"

    def test_step_indices_are_sequential(self, tmp_path: Path) -> None:
        """Step indices should be assigned sequentially starting from 0."""
        helpers.build_product(
            tmp_path,
            product_name="index_test",
            flows={
                "indexed_flow": """
                name: indexed_flow
                version: "1.0"
                steps:
                  - id: first
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "1"
                  - id: second
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "2"
                  - id: third
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "3"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="index_test")

        result = engine.run_flow(product="index_test", flow="indexed_flow", payload={})
        assert result.ok

        bundle = engine.memory.get_run(result.data["run_id"])
        indices = [step.step_index for step in bundle.steps]

        assert indices == [0, 1, 2], f"Step indices not sequential: {indices}"


class TestResumeProducesConsistentResult:
    """Verify that pause/resume produces consistent final state."""

    def test_hitl_pause_then_resume_completes_consistently(self, tmp_path: Path) -> None:
        """Pausing at HITL and resuming should produce consistent final state."""
        helpers.build_product(
            tmp_path,
            product_name="resume_test",
            flows={
                "hitl_flow": """
                name: hitl_flow
                version: "1.0"
                steps:
                  - id: before_approval
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "before"
                  - id: approval
                    type: human_approval
                    title: "Test approval"
                    message: "Approve?"
                    form:
                      fields:
                        - name: approved
                          type: boolean
                          required: true
                  - id: after_approval
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "after"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="resume_test")

        # Start run - should pause at approval
        result = engine.run_flow(product="resume_test", flow="hitl_flow", payload={})
        assert result.ok
        assert result.data["status"] == RunStatus.PENDING_HUMAN.value
        run_id = result.data["run_id"]

        # Verify paused state
        bundle = engine.memory.get_run(run_id)
        assert bundle.run.status == RunStatus.PENDING_HUMAN

        # Resume with approval
        resume_result = engine.resume_run(run_id=run_id, approval_payload={"approved": True})
        assert resume_result.ok
        assert resume_result.data["status"] == RunStatus.COMPLETED.value

        # Verify final state
        bundle = engine.memory.get_run(run_id)
        assert bundle.run.status == RunStatus.COMPLETED

        # Verify all steps completed
        after_step = next((s for s in bundle.steps if s.step_id == "after_approval"), None)
        assert after_step is not None
        assert after_step.status == StepStatus.COMPLETED

    def test_same_resume_input_produces_same_output(self, tmp_path: Path) -> None:
        """Two runs with same pause point and resume input should produce same output."""
        helpers.build_product(
            tmp_path,
            product_name="resume_determinism",
            flows={
                "resume_flow": """
                name: resume_flow
                version: "1.0"
                steps:
                  - id: start
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "start"
                  - id: approval
                    type: human_approval
                    title: "Approve"
                    message: "Continue?"
                    form:
                      fields:
                        - name: approved
                          type: boolean
                          required: true
                  - id: end
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "end"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="resume_determinism")

        final_outputs = []
        for _ in range(2):
            result = engine.run_flow(product="resume_determinism", flow="resume_flow", payload={})
            assert result.ok
            run_id = result.data["run_id"]

            resume = engine.resume_run(run_id=run_id, approval_payload={"approved": True})
            assert resume.ok

            bundle = engine.memory.get_run(run_id)
            end_step = next((s for s in bundle.steps if s.step_id == "end"), None)
            final_outputs.append(_get_artifact_data(end_step.output))

        assert final_outputs[0] == final_outputs[1], "Same resume input should produce same output"
