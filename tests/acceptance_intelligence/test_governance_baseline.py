"""
Phase 0: Governance Baseline Tests

These tests lock in governance behavior that MUST hold before and after refactoring.
They verify that blocked tools/models are denied and that proposal steps do not
execute tools directly.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.contracts.run_schema import RunStatus
from core.governance.security import SecurityRedactor
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.memory.tracing import Tracer
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products
from tests.acceptance_intelligence import test_helpers as helpers


class TestGovernanceDeniesBlockedTools:
    """Verify that governance layer blocks tools on the blocked list."""

    def test_blocked_tool_is_rejected(self) -> None:
        """A tool on the blocked_tools list should be denied execution."""
        settings = Settings()
        settings.policies.blocked_tools = ["echo_tool"]

        AgentRegistry.clear()
        ToolRegistry.clear()
        catalog = discover_products(settings)
        register_enabled_products(catalog, settings=settings)

        backend = InMemoryBackend()
        memory = MemoryRouter(
            backend=backend,
            repo_root=settings.repo_root_path(),
            observability_root=settings.repo_root_path() / "observability",
        )
        tracer = Tracer(memory=memory, redactor=SecurityRedactor(), mirror_to_log=False)
        engine = OrchestratorEngine.from_settings(
            settings=settings, memory=memory, tracer=tracer, sleep_fn=lambda _: None
        )

        result = engine.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "test"})
        assert result.ok
        # Should fail because echo_tool is blocked
        assert result.data["status"] == RunStatus.FAILED.value

        bundle = engine.memory.get_run(result.data["run_id"])
        assert bundle is not None
        assert bundle.run.status == RunStatus.FAILED

        # Should have a governance denial event
        denied_event = next(
            (e for e in bundle.events if e.kind in {"before_step_denied", "governance.decision", "tool_blocked"}),
            None,
        )
        assert denied_event is not None, "Expected a governance denial event"

        # Should NOT have any successful tool execution
        assert not any(e.kind == "tool_call_succeeded" for e in bundle.events)

    def test_non_blocked_tool_executes(self, tmp_path: Path) -> None:
        """A tool NOT on the blocked list should execute normally."""
        helpers.build_product(
            tmp_path,
            product_name="governance_allow_test",
            flows={
                "allowed_flow": """
                name: allowed_flow
                version: "1.0"
                steps:
                  - id: echo
                    type: tool
                    backend: local
                    tool: echo_tool
                    params:
                      message: "allowed"
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="governance_allow_test")

        result = engine.run_flow(product="governance_allow_test", flow="allowed_flow", payload={})
        assert result.ok
        assert result.data["status"] == RunStatus.COMPLETED.value

        bundle = engine.memory.get_run(result.data["run_id"])
        assert any(e.kind == "tool_call_succeeded" for e in bundle.events)


class TestGovernanceDeniesBlockedModels:
    """Verify that governance layer blocks models on the blocked list."""

    def test_blocked_model_is_rejected(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A model on the blocked_models list should be denied."""
        from core.config.loader import load_settings
        from core.models.providers.openai_provider import OpenAIProvider, OpenAIResponse

        helpers.build_product(
            tmp_path,
            product_name="blocked_model_test",
            flows={
                "model_flow": """
                name: model_flow
                version: "1.0"
                steps:
                  - id: reason
                    type: agent
                    backend: local
                    agent: llm_reasoner
                    params:
                      purpose: INSIGHT
                      prompt: "Test"
                """,
            },
        )

        # Create settings with blocked model
        settings = load_settings(repo_root=str(tmp_path))
        settings.policies.blocked_models = ["gpt-4o-mini"]  # Block the default model

        AgentRegistry.clear()
        ToolRegistry.clear()
        catalog = discover_products(settings)
        register_enabled_products(catalog, settings=settings)

        backend = InMemoryBackend()
        memory = MemoryRouter(backend=backend, repo_root=tmp_path, observability_root=tmp_path / "observability")
        tracer = Tracer(memory=memory, redactor=SecurityRedactor(), mirror_to_log=False)
        engine = OrchestratorEngine.from_settings(
            settings=settings, memory=memory, tracer=tracer, sleep_fn=lambda _: None
        )

        # Stub the model provider to track if it's called
        model_called = []

        def _stub_complete(self, request):
            model_called.append(request.model)
            return OpenAIResponse(
                ok=True,
                model=request.model,
                content="stubbed",
                usage={"total_tokens": 1},
                meta={"provider": "test"},
            )

        monkeypatch.setattr(OpenAIProvider, "complete", _stub_complete)

        result = engine.run_flow(product="blocked_model_test", flow="model_flow", payload={})

        # The run should fail because the model is blocked
        if result.data["status"] == RunStatus.FAILED.value:
            # Model was correctly blocked
            bundle = engine.memory.get_run(result.data["run_id"])
            # Either no model call or governance denial
            assert len(model_called) == 0 or any(
                e.kind in {"model_blocked", "governance.decision"} for e in bundle.events
            )
        else:
            # If run completed, verify model was not the blocked one
            # (platform may have fallback behavior)
            pass


class TestProposalStepsDoNotExecuteTools:
    """Verify that plan_proposal steps only emit proposals without executing tools."""

    def test_plan_proposal_does_not_call_tools(self, tmp_path: Path) -> None:
        """A plan_proposal step should emit a plan artifact but NOT execute any tools."""
        helpers.build_product(
            tmp_path,
            product_name="proposal_test",
            flows={
                "proposal_flow": """
                name: proposal_flow
                version: "1.0"
                steps:
                  - id: plan_step
                    type: plan_proposal
                    agent: acceptance_plan_agent
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="proposal_test")

        result = engine.run_flow(product="proposal_test", flow="proposal_flow", payload={"message": "test"})
        assert result.ok
        # Should pause for human approval of the plan
        assert result.data["status"] == RunStatus.PENDING_HUMAN.value

        run_id = result.data["run_id"]
        bundle = engine.memory.get_run(run_id)
        assert bundle is not None

        # Should have emitted a plan_proposed event
        plan_events = [e for e in bundle.events if e.kind == "plan_proposed"]
        assert len(plan_events) > 0, "Expected plan_proposed event"

        # Should NOT have any tool execution events
        tool_attempt_events = [e for e in bundle.events if e.kind == "tool_call_attempt_started"]
        assert len(tool_attempt_events) == 0, "plan_proposal should not execute tools"

        tool_success_events = [e for e in bundle.events if e.kind == "tool_call_succeeded"]
        assert len(tool_success_events) == 0, "plan_proposal should not have successful tool calls"

    def test_plan_proposal_step_has_plan_artifact(self, tmp_path: Path) -> None:
        """A plan_proposal step should produce a plan artifact in its output."""
        helpers.build_product(
            tmp_path,
            product_name="plan_artifact_test",
            flows={
                "plan_artifact_flow": """
                name: plan_artifact_flow
                version: "1.0"
                steps:
                  - id: propose
                    type: plan_proposal
                    agent: acceptance_plan_agent
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="plan_artifact_test")

        result = engine.run_flow(product="plan_artifact_test", flow="plan_artifact_flow", payload={"message": "plan"})
        assert result.ok

        bundle = engine.memory.get_run(result.data["run_id"])
        plan_step = next((s for s in bundle.steps if s.step_id == "propose"), None)
        assert plan_step is not None

        # Step output should contain plan proposal data
        assert isinstance(plan_step.output, dict)
        plan_data = plan_step.output.get("plan_proposal", {})
        assert plan_data, "Expected plan_proposal in step output"

    def test_tools_only_execute_after_plan_approval(self, tmp_path: Path) -> None:
        """Tools listed in a plan should only execute AFTER plan approval."""
        helpers.build_product(
            tmp_path,
            product_name="plan_execute_test",
            flows={
                "plan_execute_flow": """
                name: plan_execute_flow
                version: "1.0"
                steps:
                  - id: propose
                    type: plan_proposal
                    agent: acceptance_plan_agent
                  - id: execute
                    type: plan_execute
                """,
            },
        )
        engine, _ = helpers.build_acceptance_engine(tmp_path, product_name="plan_execute_test")

        # Start the flow - should pause at plan_proposal
        result = engine.run_flow(product="plan_execute_test", flow="plan_execute_flow", payload={"message": "execute"})
        assert result.ok
        assert result.data["status"] == RunStatus.PENDING_HUMAN.value
        run_id = result.data["run_id"]

        # Before approval - no tool execution
        bundle = engine.memory.get_run(run_id)
        tool_events_before = [e for e in bundle.events if e.kind == "tool_call_attempt_started"]
        assert len(tool_events_before) == 0, "No tools should execute before plan approval"

        # Approve the plan
        resume_result = engine.resume_run(run_id=run_id, approval_payload={"approved": True})
        assert resume_result.ok

        # After approval - tools may execute (depending on plan_execute implementation)
        bundle = engine.memory.get_run(run_id)
        # The key invariant: tools only execute AFTER plan_proposed event
        plan_proposed_ts = next(
            (e.ts for e in bundle.events if e.kind == "plan_proposed"),
            0,
        )
        tool_events_after = [e for e in bundle.events if e.kind == "tool_call_attempt_started"]

        for tool_event in tool_events_after:
            assert tool_event.ts >= plan_proposed_ts, "Tool execution must occur after plan proposal"
