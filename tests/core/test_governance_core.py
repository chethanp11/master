
from __future__ import annotations

from typing import Dict, List

from core.config.schema import Settings
from core.contracts.flow_schema import AutonomyLevel, FlowDef, StepDef, StepType
from core.contracts.run_schema import RunRecord, RunStatus
from core.governance.policies import PolicyEngine
from core.governance.security import SecurityRedactor
from core.orchestrator.context import RunContext, StepContext


def _settings() -> Settings:
    return Settings()


def _step_ctx(product: str = "hello_world") -> StepContext:
    run_record = RunRecord(run_id="run_test", product=product, flow_id="hello", status=RunStatus.RUNNING)
    flow = FlowDef(
        id="hello",
        steps=[StepDef(id="s1", type=StepType.TOOL, tool="echo_tool", backend=None)],
    )
    run_ctx = RunContext(run_id=run_record.run_id, product=run_record.product, flow=flow.id)
    return run_ctx.new_step(step_def=flow.steps[0])


def test_redactor_scrubs_tokens_and_pii() -> None:
    redactor = SecurityRedactor()
    payload = {
        "api_key": "sk-12345678901234567890ABCDE",
        "nested": {"Authorization": "Bearer sk-AAAAAAAAAAAAAAAAAAAAAAAAAA"},
        "contact": "user@example.com",
    }
    sanitized = redactor.sanitize(payload)
    assert sanitized["api_key"] == SecurityRedactor().mask
    assert "sk-" not in str(sanitized["nested"]["Authorization"])
    assert "user@example.com" not in sanitized["contact"]


def test_policy_engine_allows_tool_by_default() -> None:
    settings = _settings()
    engine = PolicyEngine(settings)
    decision = engine.evaluate_tool_call(tool_name="echo_tool", step_ctx=_step_ctx())
    assert decision.allow is True


def test_policy_engine_blocks_tool_via_blocklist() -> None:
    settings = _settings()
    settings.policies.blocked_tools = ["echo_tool"]
    engine = PolicyEngine(settings)
    decision = engine.evaluate_tool_call(tool_name="echo_tool", step_ctx=_step_ctx())
    assert decision.allow is False
    assert decision.reason == "tool_blocked"


def test_policy_engine_applies_per_product_override() -> None:
    settings = _settings()
    settings.policies.blocked_tools = ["echo_tool"]
    settings.policies.by_product = {"hello_world": {"blocked_tools": []}}
    engine = PolicyEngine(settings)
    decision = engine.evaluate_tool_call(tool_name="echo_tool", step_ctx=_step_ctx())
    assert decision.allow is True


def test_policy_engine_enforces_model_allowlist() -> None:
    settings = _settings()
    settings.policies.allowed_models = ["gpt-4o-mini"]
    engine = PolicyEngine(settings)
    allowed = engine.evaluate_model_selection(product="hello_world", model_name="gpt-4o-mini")
    denied = engine.evaluate_model_selection(product="hello_world", model_name="other-model")
    assert allowed.allow is True
    assert denied.allow is False
