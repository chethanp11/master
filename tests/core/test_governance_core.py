# ==============================
# Tests: Governance (Policies + Redaction)
# ==============================
from __future__ import annotations

from typing import Any, Dict

import pytest

from core.config.schema import Settings
from core.governance.policies import PolicyEngine
from core.governance.security import Redactor
from core.orchestrator.context import RunContext, StepContext
from core.orchestrator.state import RunStatus, StepStatus
from core.contracts.flow_schema import AutonomyLevel


def _minimal_settings() -> Settings:
    # Settings has defaults in schema; instantiate minimal.
    return Settings()


def _ctx(product: str = "sandbox", flow: str = "hello_world") -> StepContext:
    run = RunContext(
        run_id="r1",
        product=product,
        flow=flow,
        status=RunStatus.RUNNING,
        payload={"x": 1},
        artifacts={},
        meta={},
    )
    step = run.new_step(step_id="s1", step_type="tool", backend="local", target="echo_tool")
    return step


def test_redactor_scrubs_secrets_like_api_keys() -> None:
    settings = _minimal_settings()
    redactor = Redactor.from_settings(settings)

    payload = {
        "token": "sk-123456789012345678901234567890",
        "nested": {"Authorization": "Bearer sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
    }
    scrubbed = redactor.scrub(payload)
    s = str(scrubbed)
    assert "sk-" not in s
    assert "***REDACTED***" in s


def test_redactor_scrubs_emails_by_default_pattern_if_enabled() -> None:
    settings = _minimal_settings()
    redactor = Redactor.from_settings(settings)

    payload = {"email": "user@example.com"}
    scrubbed = redactor.scrub(payload)
    assert "user@example.com" not in str(scrubbed)
    assert "***REDACTED***" in str(scrubbed)


def test_policy_engine_allows_basic_tool_call_by_default() -> None:
    settings = _minimal_settings()
    pe = PolicyEngine(settings)
    ctx = _ctx()

    decision = pe.allow_tool(tool_name="echo_tool", step_ctx=ctx, autonomy=AutonomyLevel.suggest_only)
    assert decision.allowed is True


def test_policy_engine_can_deny_tool_via_overrides() -> None:
    settings = _minimal_settings()

    # Inject a deny list directly (schema should support policies overrides).
    # If schema differs, adjust policies.yaml in real setup; for unit test we set in-memory.
    settings.policies.deny_tools = ["echo_tool"]  # type: ignore[attr-defined]

    pe = PolicyEngine(settings)
    ctx = _ctx()

    decision = pe.allow_tool(tool_name="echo_tool", step_ctx=ctx, autonomy=AutonomyLevel.suggest_only)
    assert decision.allowed is False
    assert "denied" in (decision.reason or "").lower()