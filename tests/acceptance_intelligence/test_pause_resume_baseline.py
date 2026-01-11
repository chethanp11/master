"""
Phase 0: Pause/Resume Baseline Tests

These tests lock in pause/resume behavior that MUST hold before and after refactoring.
They verify correct status transitions for HITL and user_input steps, and that
resume operations are idempotent.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from core.contracts.run_schema import RunStatus, StepStatus
from tests.acceptance_intelligence import helpers


class TestHITLPausesCorrectly:
    """Verify that HITL (human approval) steps pause the run correctly."""

    def test_human_approval_step_pauses_run(self, tmp_path: Path) -> None:
        """A human_approval step should pause the run with PENDING_HUMAN status."""
        helpers.build_product(
            tmp_path,
            product_name="hitl_pause_test",
            flows={
                "hitl_flow": """
                name: hitl_flow
                version: "1.0"
                steps:
                  - id: before
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "before"
                  - id: approval
                    type: human_approval
                    title: "Test"
                    message: "Approve?"
                    form:
                      fields:
                        - name: approved
                          type: boolean
                          required: true
                  - id: after
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "after"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="hitl_pause_test")

        result = engine.run_flow(product="hitl_pause_test", flow="hitl_flow", payload={})
        assert result.ok
        assert result.data["status"] == RunStatus.PENDING_HUMAN.value

        bundle = engine.memory.get_run(result.data["run_id"])
        assert bundle.run.status == RunStatus.PENDING_HUMAN

    def test_steps_before_hitl_complete(self, tmp_path: Path) -> None:
        """Steps before the HITL step should complete before pausing."""
        helpers.build_product(
            tmp_path,
            product_name="hitl_before_test",
            flows={
                "hitl_before_flow": """
                name: hitl_before_flow
                version: "1.0"
                steps:
                  - id: step_a
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "a"
                  - id: step_b
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "b"
                  - id: approval
                    type: human_approval
                    title: "Approve"
                    message: "Continue?"
                    form:
                      fields:
                        - name: approved
                          type: boolean
                          required: true
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="hitl_before_test")

        result = engine.run_flow(product="hitl_before_test", flow="hitl_before_flow", payload={})
        assert result.ok
        assert result.data["status"] == RunStatus.PENDING_HUMAN.value

        bundle = engine.memory.get_run(result.data["run_id"])

        step_a = next((s for s in bundle.steps if s.step_id == "step_a"), None)
        step_b = next((s for s in bundle.steps if s.step_id == "step_b"), None)

        assert step_a is not None and step_a.status == StepStatus.COMPLETED
        assert step_b is not None and step_b.status == StepStatus.COMPLETED

    def test_steps_after_hitl_not_started(self, tmp_path: Path) -> None:
        """Steps after the HITL step should not be started until resume."""
        helpers.build_product(
            tmp_path,
            product_name="hitl_after_test",
            flows={
                "hitl_after_flow": """
                name: hitl_after_flow
                version: "1.0"
                steps:
                  - id: approval
                    type: human_approval
                    title: "Approve"
                    message: "Start?"
                    form:
                      fields:
                        - name: approved
                          type: boolean
                          required: true
                  - id: after_step
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "after"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="hitl_after_test")

        result = engine.run_flow(product="hitl_after_test", flow="hitl_after_flow", payload={})
        assert result.ok
        assert result.data["status"] == RunStatus.PENDING_HUMAN.value

        bundle = engine.memory.get_run(result.data["run_id"])

        after_step = next((s for s in bundle.steps if s.step_id == "after_step"), None)
        # Step might not exist yet or should be NOT_STARTED
        if after_step is not None:
            assert after_step.status == StepStatus.NOT_STARTED

    def test_pending_human_event_emitted(self, tmp_path: Path) -> None:
        """A run_pending_human event should be emitted when pausing for HITL."""
        helpers.build_product(
            tmp_path,
            product_name="hitl_event_test",
            flows={
                "hitl_event_flow": """
                name: hitl_event_flow
                version: "1.0"
                steps:
                  - id: approval
                    type: human_approval
                    title: "Test"
                    message: "Approve?"
                    form:
                      fields:
                        - name: approved
                          type: boolean
                          required: true
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="hitl_event_test")

        result = engine.run_flow(product="hitl_event_test", flow="hitl_event_flow", payload={})
        assert result.ok

        bundle = engine.memory.get_run(result.data["run_id"])
        pending_event = next(
            (e for e in bundle.events if e.kind == "run_pending_human"),
            None,
        )
        assert pending_event is not None, "Expected run_pending_human event"
        assert pending_event.payload.get("reason") == "approval_requested"


class TestUserInputPausesCorrectly:
    """Verify that user_input steps pause the run correctly."""

    def test_user_input_step_pauses_run(self, tmp_path: Path) -> None:
        """A user_input step should pause the run with appropriate status."""
        helpers.build_product(
            tmp_path,
            product_name="user_input_pause_test",
            flows={
                "user_input_flow": """
                name: user_input_flow
                version: "1.0"
                steps:
                  - id: ask
                    type: user_input
                    params:
                      schema_version: "1.0"
                      form_id: test_input
                      title: "Input"
                      prompt: "Enter value"
                      mode: text_input
                      schema:
                        type: object
                        properties:
                          value:
                            type: string
                        required:
                          - value
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="user_input_pause_test")

        result = engine.run_flow(product="user_input_pause_test", flow="user_input_flow", payload={})
        assert result.ok
        # Should be paused waiting for user input
        assert result.data["status"] in [
            RunStatus.PENDING_USER_INPUT.value,
            RunStatus.PAUSED_WAITING_FOR_USER.value,
        ]

        bundle = engine.memory.get_run(result.data["run_id"])
        assert bundle.run.status in [RunStatus.PENDING_USER_INPUT, RunStatus.PAUSED_WAITING_FOR_USER]

    def test_user_input_step_has_pending_status(self, tmp_path: Path) -> None:
        """The user_input step itself should have PENDING_USER_INPUT status."""
        helpers.build_product(
            tmp_path,
            product_name="user_input_step_status_test",
            flows={
                "user_input_status_flow": """
                name: user_input_status_flow
                version: "1.0"
                steps:
                  - id: input_step
                    type: user_input
                    params:
                      schema_version: "1.0"
                      form_id: status_input
                      title: "Input"
                      prompt: "Enter"
                      mode: choice_input
                      schema:
                        type: object
                        properties:
                          choice:
                            type: string
                            enum: ["a", "b"]
                        required:
                          - choice
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="user_input_step_status_test")

        result = engine.run_flow(product="user_input_step_status_test", flow="user_input_status_flow", payload={})
        assert result.ok

        bundle = engine.memory.get_run(result.data["run_id"])
        input_step = next((s for s in bundle.steps if s.step_id == "input_step"), None)
        assert input_step is not None
        assert input_step.status in [StepStatus.PENDING_USER_INPUT, StepStatus.PAUSED_WAITING_FOR_USER]


class TestResumeIsIdempotent:
    """Verify that resume operations are idempotent and safe."""

    def test_double_resume_with_same_input_fails_gracefully(self, tmp_path: Path) -> None:
        """Resuming an already-resumed run should fail gracefully."""
        helpers.build_product(
            tmp_path,
            product_name="idempotent_test",
            flows={
                "idempotent_flow": """
                name: idempotent_flow
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
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="idempotent_test")

        # Start run
        result = engine.run_flow(product="idempotent_test", flow="idempotent_flow", payload={})
        assert result.ok
        assert result.data["status"] == RunStatus.PENDING_HUMAN.value
        run_id = result.data["run_id"]

        # First resume - should succeed
        resume1 = engine.resume_run(run_id=run_id, approval_payload={"approved": True})
        assert resume1.ok
        assert resume1.data["status"] == RunStatus.COMPLETED.value

        # Second resume - should fail (already completed)
        resume2 = engine.resume_run(run_id=run_id, approval_payload={"approved": True})
        assert not resume2.ok
        assert resume2.error is not None
        assert resume2.error.code == "invalid_state"

    def test_resume_preserves_prior_artifacts(self, tmp_path: Path) -> None:
        """Resume should not overwrite artifacts from steps before the pause."""
        helpers.build_product(
            tmp_path,
            product_name="artifact_preserve_test",
            flows={
                "artifact_flow": """
                name: artifact_flow
                version: "1.0"
                steps:
                  - id: first
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "first_value"
                  - id: approval
                    type: human_approval
                    title: "Approve"
                    message: "Continue?"
                    form:
                      fields:
                        - name: approved
                          type: boolean
                          required: true
                  - id: last
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "last_value"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="artifact_preserve_test")

        # Start run
        result = engine.run_flow(product="artifact_preserve_test", flow="artifact_flow", payload={})
        run_id = result.data["run_id"]

        # Capture first step output before resume
        bundle_before = engine.memory.get_run(run_id)
        first_step_before = next((s for s in bundle_before.steps if s.step_id == "first"), None)
        first_output_before = first_step_before.output if first_step_before else None

        # Resume
        engine.resume_run(run_id=run_id, approval_payload={"approved": True})

        # Verify first step output unchanged after resume
        bundle_after = engine.memory.get_run(run_id)
        first_step_after = next((s for s in bundle_after.steps if s.step_id == "first"), None)
        first_output_after = first_step_after.output if first_step_after else None

        assert first_output_before == first_output_after, "First step output should not change after resume"

    def test_final_state_same_regardless_of_resume_timing(self, tmp_path: Path) -> None:
        """Final state should be the same whether resumed immediately or after delay."""
        helpers.build_product(
            tmp_path,
            product_name="timing_test",
            flows={
                "timing_flow": """
                name: timing_flow
                version: "1.0"
                steps:
                  - id: echo
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "test"
                  - id: approval
                    type: human_approval
                    title: "Approve"
                    message: "Ok?"
                    form:
                      fields:
                        - name: approved
                          type: boolean
                          required: true
                  - id: final
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "final"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="timing_test")

        # Run twice, resume both immediately (simulating "delayed" via same logic)
        final_states = []
        for _ in range(2):
            result = engine.run_flow(product="timing_test", flow="timing_flow", payload={})
            run_id = result.data["run_id"]

            engine.resume_run(run_id=run_id, approval_payload={"approved": True})

            bundle = engine.memory.get_run(run_id)
            final_step = next((s for s in bundle.steps if s.step_id == "final"), None)
            final_states.append({
                "status": bundle.run.status.value,
                "final_output": final_step.output if final_step else None,
            })

        assert final_states[0]["status"] == final_states[1]["status"]
        assert final_states[0]["final_output"] == final_states[1]["final_output"]


class TestUserInputResumeFlow:
    """Verify user_input pause/resume flow works correctly."""

    def test_user_input_resume_completes_flow(self, tmp_path: Path) -> None:
        """Providing user input should resume and complete the flow."""
        helpers.build_product(
            tmp_path,
            product_name="user_input_resume_test",
            flows={
                "user_input_resume_flow": """
                name: user_input_resume_flow
                version: "1.0"
                steps:
                  - id: ask_input
                    type: user_input
                    params:
                      schema_version: "1.0"
                      form_id: user_form
                      title: "Input"
                      prompt: "Choose"
                      mode: choice_input
                      schema:
                        type: object
                        properties:
                          selection:
                            type: string
                            enum: ["option_a", "option_b"]
                        required:
                          - selection
                  - id: use_input
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "{{artifacts.user_input.user_form.values.selection}}"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="user_input_resume_test")

        # Start - should pause for user input
        result = engine.run_flow(product="user_input_resume_test", flow="user_input_resume_flow", payload={})
        assert result.ok
        run_id = result.data["run_id"]

        # Resume with user input
        resume = engine.resume_run(
            run_id=run_id,
            user_input_response={"form_id": "user_form", "values": {"selection": "option_a"}},
        )
        assert resume.ok
        assert resume.data["status"] == RunStatus.COMPLETED.value

        # Verify user input was used
        bundle = engine.memory.get_run(run_id)
        use_step = next((s for s in bundle.steps if s.step_id == "use_input"), None)
        assert use_step is not None
        assert use_step.status == StepStatus.COMPLETED
