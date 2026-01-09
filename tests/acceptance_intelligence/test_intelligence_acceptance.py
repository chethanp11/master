from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from core.agents.registry import AgentRegistry
from core.contracts.run_schema import RunStatus, StepStatus
from core.config.schema import Settings
from core.governance.security import SecurityRedactor
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.memory.tracing import Tracer
from core.models.providers.openai_provider import OpenAIProvider, OpenAIResponse
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products

from tests.acceptance_intelligence import helpers


def _artifact_echo(step_output: dict[str, Any]) -> Any:
    return step_output.get("data", {}).get("echo")


def _run_and_collect_steps(engine: OrchestratorEngine, *, product: str, flow: str, payload: dict[str, Any]) -> tuple[str, list[tuple[str, str]]]:
    response = engine.run_flow(product=product, flow=flow, payload=payload)
    assert response.ok, response.error
    run_id = response.data["run_id"]
    bundle = engine.memory.get_run(run_id)
    assert bundle is not None
    steps = [(step.step_id, step.type) for step in bundle.steps]
    return run_id, steps


def _collect_step_output(engine: OrchestratorEngine, run_id: str, step_id: str) -> dict[str, Any]:
    bundle = engine.memory.get_run(run_id)
    assert bundle is not None
    step = next((step for step in bundle.steps if step.step_id == step_id), None)
    assert step is not None
    assert isinstance(step.output, dict), "Expected step output dictionary"
    return step.output


def test_deterministic_step_transitions(tmp_path: Path) -> None:
    """Lock the deterministic sequence/output of a pure tool flow."""
    helpers.build_product(
        tmp_path,
        product_name="deterministic_acceptance",
        flows={
            "deterministic_flow": """
            name: deterministic_flow
            version: "1.0"
            steps:
              - id: echo
                type: tool
                backend: local
                tool: echo_tool
                params:
                  message: "{{payload.message}}"
            """,
        },
    )
    engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="deterministic_acceptance")

    run_payload = {"message": "repeat"}

    run_a_id, steps_a = _run_and_collect_steps(
        engine, product="deterministic_acceptance", flow="deterministic_flow", payload=run_payload
    )
    run_b_id, steps_b = _run_and_collect_steps(
        engine, product="deterministic_acceptance", flow="deterministic_flow", payload=run_payload
    )

    assert steps_a == steps_b

    output_a = _collect_step_output(engine, run_a_id, "echo")
    output_b = _collect_step_output(engine, run_b_id, "echo")

    assert _artifact_echo(output_a) == _artifact_echo(output_b) == run_payload["message"]


def test_pause_resume_with_human_and_user_input(tmp_path: Path) -> None:
    """Assert HITL + user_input transitions pause/resume cleanly and are idempotent."""
    helpers.build_product(
        tmp_path,
        product_name="pause_resume_acceptance",
        flows={
            "pause_resume_flow": """
            name: pause_resume_flow
            version: "1.0"
            steps:
              - id: start_echo
                type: tool
                backend: local
                tool: echo_tool
                params:
                  message: "{{payload.prompt}}"

              - id: approval
                type: human_approval
                title: "Approve to continue"
                message: "Please approve."
                form:
                  fields:
                    - name: approved
                      type: boolean
                      required: true

              - id: notes
                type: user_input
                params:
                  schema_version: "1.0"
                  form_id: notes
                  title: "Add notes"
                  prompt: "Choose an option."
                  mode: choice_input
                  schema:
                    type: object
                    properties:
                      selection:
                        type: string
                        enum:
                          - alpha
                          - beta
                    required:
                      - selection

              - id: finish_echo
                type: tool
                backend: local
                tool: echo_tool
                params:
                  message: "{{artifacts.user_input.notes.values.selection}}"
            """,
        },
    )
    engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="pause_resume_acceptance")

    start = engine.run_flow(product="pause_resume_acceptance", flow="pause_resume_flow", payload={"prompt": "hello"})
    assert start.ok
    assert start.data["status"] == RunStatus.PENDING_HUMAN.value
    run_id = start.data["run_id"]

    bundle = engine.memory.get_run(run_id)
    assert bundle is not None
    assert bundle.run.status == RunStatus.PENDING_HUMAN

    approval_event = next((e for e in bundle.events if e.kind == "run_pending_human"), None)
    assert approval_event is not None
    assert approval_event.payload.get("reason") == "approval_requested"

    resume_approval = engine.resume_run(run_id=run_id, approval_payload={"approved": True})
    assert resume_approval.ok
    assert resume_approval.data["status"] == RunStatus.PAUSED_WAITING_FOR_USER.value

    bundle = engine.memory.get_run(run_id)
    assert bundle is not None
    notes_step = next((step for step in bundle.steps if step.step_id == "notes"), None)
    assert notes_step is not None
    assert notes_step.status == StepStatus.PENDING_USER_INPUT

    resume_input = engine.resume_run(
        run_id=run_id,
        user_input_response={"form_id": "notes", "values": {"selection": "alpha"}},
    )
    assert resume_input.ok
    assert resume_input.data["status"] == RunStatus.COMPLETED.value

    bundle = engine.memory.get_run(run_id)
    assert bundle is not None
    finish_step = next((step for step in bundle.steps if step.step_id == "finish_echo"), None)
    assert finish_step is not None
    assert finish_step.status == StepStatus.COMPLETED

    # idempotency: repeat input should not succeed again
    retry = engine.resume_run(
        run_id=run_id,
        user_input_response={"form_id": "notes", "values": {"selection": "alpha"}},
    )
    assert not retry.ok
    assert retry.error is not None
    assert retry.error.code == "invalid_state"


def test_governance_blocks_disallowed_tool() -> None:
    """Confirm governance denies blocked tools before execution."""
    settings = Settings()
    settings.policies.blocked_tools = ["echo_tool"]
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)

    backend = InMemoryBackend()
    memory = MemoryRouter(backend=backend, repo_root=settings.repo_root_path(), observability_root=settings.repo_root_path() / "observability")
    tracer = Tracer(memory=memory, redactor=SecurityRedactor(), mirror_to_log=False)
    engine = OrchestratorEngine.from_settings(settings=settings, memory=memory, tracer=tracer, sleep_fn=lambda _: None)

    result = engine.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "deny"})
    assert result.ok
    assert result.data["status"] == RunStatus.FAILED.value

    bundle = engine.memory.get_run(result.data["run_id"])
    assert bundle is not None
    assert bundle.run.status == RunStatus.FAILED

    denied_event = next(
        (e for e in bundle.events if e.kind in {"before_step_denied", "governance.decision"}), None
    )
    assert denied_event is not None
    assert denied_event.payload.get("reason") in {"tool_blocked", "governance_denied"}

    assert not any(e.kind == "tool_call_succeeded" for e in bundle.events)


def test_trace_records_tool_and_model_calls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify trace events capture tool + centralized model call boundaries."""
    helpers.build_product(
        tmp_path,
        product_name="trace_acceptance",
        flows={
            "trace_flow": """
            name: trace_flow
            version: "1.0"
            steps:
              - id: echo_tool
                type: tool
                backend: local
                tool: echo_tool
                params:
                  message: "{{payload.message}}"

              - id: reasoner
                type: agent
                backend: local
                agent: llm_reasoner
                params:
                  purpose: INSIGHT
                  prompt: "Analyze {{payload.message}}"
            """,
        },
    )
    engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="trace_acceptance")

    def _stub_complete(self, request):
        return OpenAIResponse(
            ok=True,
            model=request.model,
            content=f"stubbed {request.messages[-1]['content']}" if request.messages else "stubbed",
            usage={"total_tokens": 1},
            meta={"provider": "test"},
        )

    monkeypatch.setattr(OpenAIProvider, "complete", _stub_complete)

    run_result = engine.run_flow(product="trace_acceptance", flow="trace_flow", payload={"message": "trace"})
    assert run_result.ok
    run_id = run_result.data["run_id"]

    events = engine.memory.get_run(run_id).events
    assert any(e.kind == "step_started" and e.step_id == "echo_tool" for e in events)
    assert any(e.kind == "tool_call_attempt_started" for e in events)
    assert any(e.kind == "tool_call_succeeded" for e in events)
    assert any(e.kind == "step_completed" and e.step_id == "reasoner" for e in events)
    model_start = next((e for e in events if e.kind == "model_call_attempt_started"), None)
    assert model_start is not None
    assert model_start.payload.get("model")
    model_end = next((e for e in events if e.kind == "model_call_succeeded"), None)
    assert model_end is not None
    assert model_end.payload.get("model")


def test_plan_proposal_emits_artifact_without_tool_execution(tmp_path: Path) -> None:
    """Guard the baseline that plan_proposal emits artifacts but does not run tools."""
    helpers.build_product(
        tmp_path,
        product_name="plan_acceptance",
        flows={
            "plan_flow": """
            name: plan_flow
            version: "1.0"
            steps:
              - id: plan_proposal
                type: plan_proposal
                agent: acceptance_plan_agent
            """,
        },
    )
    engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="plan_acceptance")

    result = engine.run_flow(product="plan_acceptance", flow="plan_flow", payload={"message": "plan"})
    assert result.ok
    assert result.data["status"] == RunStatus.PENDING_HUMAN.value
    run_id = result.data["run_id"]

    bundle = engine.memory.get_run(run_id)
    assert bundle is not None
    plan_step = next((step for step in bundle.steps if step.step_id == "plan_proposal"), None)
    assert plan_step is not None
    assert isinstance(plan_step.output, dict)
    plan_payload = plan_step.output.get("plan_proposal", {}) or {}
    plan_data = plan_payload.get("data") or {}
    steps = plan_data.get("steps") or []
    assert any(step.get("tool") == "echo_tool" for step in steps)

    assert any(event.kind == "plan_proposed" for event in bundle.events)
    assert not any(event.kind == "tool_call_attempt_started" for event in bundle.events)
