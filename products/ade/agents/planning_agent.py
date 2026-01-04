from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from core.agents.base import BaseAgent
from core.contracts.agent_schema import AgentResult, AgentError, AgentErrorCode, AgentMeta
from core.orchestrator.context import StepContext


class PlanningInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comment: str = Field(default="")
    previous_run: Dict[str, Any] = Field(default_factory=dict)


class PlanningAgent(BaseAgent):
    name = "planning_agent"
    description = "Produces a replan note and a suggested restart step based on rejection context."

    def run(self, step_context: StepContext) -> AgentResult:
        try:
            payload = step_context.run.payload or {}
            plan = PlanningInput(
                comment=payload.get("replan_comment", ""),
                previous_run=payload.get("previous_run", {}),
            )
            comment = (plan.comment or "").strip()
            note = "Replan requested."
            if comment:
                note = f"Replan requested: {comment}"

            start_step_id = None
            reason = "default_next"
            comment_lower = comment.lower()
            if comment_lower:
                if any(token in comment_lower for token in ("chart", "plot", "bar", "line", "scatter", "stacked", "table", "visual", "visualization")):
                    start_step_id = "recommend_chart"
                    reason = "comment_mentions_chart_change"
                elif any(token in comment_lower for token in ("approval", "approve", "review")):
                    start_step_id = "approval"
                    reason = "comment_mentions_approval"
                elif any(token in comment_lower for token in ("summarize", "summary", "dashboard", "visual")):
                    start_step_id = "summarize"
                    reason = "comment_mentions_summary"
                elif any(token in comment_lower for token in ("read", "re-run", "rerun", "refresh", "reload", "data")):
                    start_step_id = "read"
                    reason = "comment_mentions_data"

            if not start_step_id:
                previous_run = plan.previous_run or {}
                run_summary = (previous_run.get("run") or {}).get("summary") or {}
                failed_step = run_summary.get("failed_step_id") or run_summary.get("failed_step")
                if failed_step:
                    start_step_id = failed_step
                    reason = "resume_failed_step"
                else:
                    steps = previous_run.get("steps") or []
                    for step in steps:
                        if step.get("status") in {"FAILED", "PENDING_HUMAN"}:
                            start_step_id = step.get("step_id")
                            reason = "resume_incomplete_step"
                            break

            meta = AgentMeta(agent_name=self.name)
            return AgentResult(
                ok=True,
                data={
                    "note": note,
                    "start_step_id": start_step_id,
                    "decision_reason": reason,
                },
                error=None,
                meta=meta,
            )
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=AgentMeta(agent_name=self.name))


def build() -> PlanningAgent:
    return PlanningAgent()
