from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.agents.base import BaseAgent, agent
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult


class CritiqueOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: str = "critique"
    evidence_gaps: List[str] = Field(default_factory=list)
    revised_confidence: str = "medium"
    downgrade_reason: Optional[str] = None
    blocking_required: bool = False
    stop_reason: str = "sufficient"
    recommended_next_action: str = "CONTINUE"


def _extract_confidence(payload: Dict[str, Any]) -> str:
    level = payload.get("confidence_level")
    if isinstance(level, str) and level:
        return level
    return "medium"


def _has_plan_steps(payload: Dict[str, Any]) -> bool:
    steps = payload.get("steps") if isinstance(payload, dict) else None
    return isinstance(steps, list) and bool(steps)


def _build_evidence_gaps(
    *,
    sufficiency: Dict[str, Any],
    plan: Dict[str, Any],
    data_reader: Dict[str, Any],
) -> List[str]:
    gaps: List[str] = []
    if not data_reader:
        gaps.append("missing_dataset_profile")
    reasons = sufficiency.get("downgrade_reasons") if isinstance(sufficiency, dict) else []
    if isinstance(reasons, list):
        for reason in reasons:
            if isinstance(reason, str) and reason:
                gaps.append(reason)
    if not _has_plan_steps(plan):
        gaps.append("missing_plan_steps")
    return sorted(set(gaps))


@agent(
    name="critic_evaluator",
    purpose="Evaluates critique requirements before final outputs",
    capabilities=["critique", "evidence_review", "confidence_adjustment"],
    cost_hint="LOW",
)
class CriticEvaluatorAgent(BaseAgent):
    name = "critic_evaluator"
    description = "Evaluates evidence gaps and recommends whether to continue or ask for clarification."

    def run(self, step_context: Any) -> AgentResult:
        try:
            artifacts = step_context.run.artifacts or {}
            sufficiency = artifacts.get("agent.sufficiency_evaluator.output") or {}
            plan = artifacts.get("agent.plan_proposal_agent.output") or {}
            data_reader = artifacts.get("tool.data_reader.output") or {}

            evidence_gaps = _build_evidence_gaps(
                sufficiency=sufficiency,
                plan=plan,
                data_reader=data_reader,
            )
            confidence = _extract_confidence(sufficiency)
            revised_confidence = confidence
            downgrade_reason = None
            if evidence_gaps:
                if confidence == "high":
                    revised_confidence = "medium"
                elif confidence == "medium":
                    revised_confidence = "low"
                downgrade_reason = "critique_evidence_gap"

            blocking_markers = {
                "insufficient_rows",
                "insufficient_time_window",
                "missing_plan_steps",
                "missing_dataset_profile",
            }
            blocking_required = bool(blocking_markers.intersection(evidence_gaps))
            if blocking_required:
                revised_confidence = "low"
            stop_reason = "missing_inputs" if blocking_required else "sufficient"
            next_action = "ASK_USER" if blocking_required else "CONTINUE"

            payload = CritiqueOutput(
                evidence_gaps=evidence_gaps,
                revised_confidence=revised_confidence,
                downgrade_reason=downgrade_reason,
                blocking_required=blocking_required,
                stop_reason=stop_reason,
                recommended_next_action=next_action,
            ).model_dump(mode="json")
            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=True, data=payload, error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=AgentMeta(agent_name=self.name))


def build() -> CriticEvaluatorAgent:
    return CriticEvaluatorAgent()
