from __future__ import annotations

# ==============================
# Critic Recommendation Gating
# ==============================
"""
Conservative gating for critic recommendations.
"""

from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.contracts.critic_schema import CriticOutput, CriticNextAction


class CriticGateContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allow_user_input: bool = False
    allow_hitl: bool = False
    allow_fetch_more_evidence: bool = False
    evidence_budget: int = 0


class GatedCriticDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: CriticNextAction
    allowed_actions: List[CriticNextAction] = Field(default_factory=list)
    reason: str
    details: Dict[str, str] = Field(default_factory=dict)


def gate_critic_recommendation(
    critic: CriticOutput,
    context: CriticGateContext,
) -> GatedCriticDecision:
    allowed = ["NONE"]
    if context.allow_user_input:
        allowed.append("USER_INPUT")
    if context.allow_hitl:
        allowed.append("HITL")
    if context.allow_fetch_more_evidence and context.evidence_budget > 0:
        allowed.append("FETCH_MORE_EVIDENCE")

    requested = critic.recommended_next_action
    if requested in allowed:
        return GatedCriticDecision(action=requested, allowed_actions=allowed, reason="allowed")

    return GatedCriticDecision(
        action="NONE",
        allowed_actions=allowed,
        reason="recommendation_blocked",
        details={"requested": requested},
    )
