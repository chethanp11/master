from __future__ import annotations

import pytest

from core.contracts.critic_schema import CriticOutput
from core.governance.critic_gate import CriticGateContext, gate_critic_recommendation
from core.tools.executor import ToolExecutor


def test_critic_output_rejects_illegal_fields() -> None:
    payload = {
        "completeness_score": 0.5,
        "inconsistency_flags": [],
        "missing_evidence_requests": [],
        "confidence_adjustment": 0.0,
        "recommended_next_action": "NONE",
        "notes": "ok",
        "execute_tool": "not_allowed",
    }
    with pytest.raises(Exception):
        CriticOutput.model_validate(payload)

    bad_action = dict(payload)
    bad_action.pop("execute_tool")
    bad_action["recommended_next_action"] = "RUN_TOOL"
    with pytest.raises(Exception):
        CriticOutput.model_validate(bad_action)


def test_gate_blocks_fetch_more_evidence(monkeypatch) -> None:
    def _explode(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("ToolExecutor.execute should not be called during gating.")

    monkeypatch.setattr(ToolExecutor, "execute", _explode)

    critic = CriticOutput.model_validate(
        {
            "completeness_score": 0.6,
            "inconsistency_flags": [],
            "missing_evidence_requests": [],
            "confidence_adjustment": 0.1,
            "recommended_next_action": "FETCH_MORE_EVIDENCE",
            "notes": None,
        }
    )
    context = CriticGateContext(
        allow_user_input=True,
        allow_hitl=False,
        allow_fetch_more_evidence=False,
        evidence_budget=0,
    )
    decision = gate_critic_recommendation(critic, context)
    assert decision.action == "NONE"
    assert "FETCH_MORE_EVIDENCE" not in decision.allowed_actions
