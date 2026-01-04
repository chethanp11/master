from __future__ import annotations

# ==============================
# Governance Limits Tests
# ==============================

from pathlib import Path

from core.config.schema import AppConfig, PathsConfig, PoliciesConfig, Settings
from core.contracts.reasoning_schema import ReasoningPurpose
from core.governance.hooks import GovernanceHooks
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.memory.tracing import Tracer
from core.orchestrator.context import RunContext
from core.orchestrator.engine import OrchestratorEngine


def _settings_with_policies(repo_root: Path, *, policies: PoliciesConfig) -> Settings:
    app = AppConfig(paths=PathsConfig(repo_root=repo_root.as_posix()))
    return Settings(app=app, policies=policies)


def test_max_payload_bytes_exceeded(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    policies = PoliciesConfig(max_payload_bytes=10)
    settings = _settings_with_policies(repo_root, policies=policies)
    memory = MemoryRouter(backend=InMemoryBackend())
    tracer = Tracer(memory=memory)
    engine = OrchestratorEngine.from_settings(settings=settings, memory=memory, tracer=tracer, sleep_fn=lambda _: None)

    res = engine.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "too-large-payload"})
    assert res.ok is False
    assert res.error is not None
    assert res.error.code == "payload_limit_exceeded"

    runs = memory.list_runs()
    assert runs
    assert runs[0].status == "FAILED"
    assert runs[0].summary.get("error", {}).get("code") == "payload_limit_exceeded"


def test_max_steps_exceeded(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    policies = PoliciesConfig(max_steps=1)
    settings = _settings_with_policies(repo_root, policies=policies)
    memory = MemoryRouter(backend=InMemoryBackend())
    tracer = Tracer(memory=memory)
    engine = OrchestratorEngine.from_settings(settings=settings, memory=memory, tracer=tracer, sleep_fn=lambda _: None)

    res = engine.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "hello"})
    assert res.ok is False
    assert res.error is not None
    assert res.error.code == "max_steps_exceeded"

    runs = memory.list_runs()
    assert runs
    assert runs[0].status == "FAILED"
    assert runs[0].summary.get("error", {}).get("code") == "max_steps_exceeded"


def test_max_tool_calls_exceeded() -> None:
    policies = PoliciesConfig(max_tool_calls=1)
    settings = Settings(policies=policies)
    hooks = GovernanceHooks(settings=settings)
    run_ctx = RunContext(run_id="run_1", product="demo", flow="demo", payload={})
    step_ctx = run_ctx.new_step(step_id="tool_step", step_type="tool")

    decision1 = hooks.before_tool_call(tool_name="tool_a", params={}, ctx=step_ctx)
    assert decision1.allowed is True

    decision2 = hooks.before_tool_call(tool_name="tool_b", params={}, ctx=step_ctx)
    assert decision2.allowed is False
    assert decision2.reason == "tool_call_limit_exceeded"


def test_max_tokens_exceeded() -> None:
    policies = PoliciesConfig(model_max_tokens=5)
    settings = Settings(policies=policies)
    hooks = GovernanceHooks(settings=settings)
    run_ctx = RunContext(run_id="run_1", product="demo", flow="demo", payload={})
    step_ctx = run_ctx.new_step(step_id="agent_step", step_type="agent")

    decision = hooks.before_model_call(
        model_name="gpt-4o-mini",
        purpose=ReasoningPurpose.EXPLANATION,
        messages={"messages": [{"role": "user", "content": "hi"}]},
        max_tokens=10,
        ctx=step_ctx,
    )
    assert decision.allowed is False
    assert decision.reason == "model_token_limit_exceeded"


def test_max_steps_per_run_exceeded() -> None:
    policies = PoliciesConfig(max_steps=1)
    settings = Settings(policies=policies)
    hooks = GovernanceHooks(settings=settings)
    run_ctx = RunContext(run_id="run_1", product="demo", flow="demo", payload={})
    run_ctx.meta["steps_executed"] = 1
    step_ctx = run_ctx.new_step(step_id="agent_step", step_type="agent")

    decision = hooks.before_step(step_ctx=step_ctx)
    assert decision.allowed is False
    assert decision.reason == "step_limit_exceeded"


def test_run_token_budget_exceeded() -> None:
    policies = PoliciesConfig(max_tokens_per_run=5)
    settings = Settings(policies=policies)
    hooks = GovernanceHooks(settings=settings)
    run_ctx = RunContext(run_id="run_1", product="demo", flow="demo", payload={})
    run_ctx.meta["tokens_used"] = 4
    step_ctx = run_ctx.new_step(step_id="agent_step", step_type="agent")

    decision = hooks.before_model_call(
        model_name="gpt-4o-mini",
        purpose=ReasoningPurpose.EXPLANATION,
        messages={"messages": [{"role": "user", "content": "hi"}]},
        max_tokens=2,
        ctx=step_ctx,
    )
    assert decision.allowed is False
    assert decision.reason == "run_token_budget_exceeded"
