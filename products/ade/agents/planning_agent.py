
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

    def _analysis_plan(self, focus_metric: str, chart_type: str, time_axis: str) -> Dict[str, Any]:
        return {
            "baseline_comparisons": [
                "compare recent period vs prior period",
                "compare segment baselines vs overall baseline",
            ],
            "attribution_steps": [
                "identify top drivers by magnitude",
                "quantify contribution by segment",
            ],
            "seasonality_checks": [
                "check periodic patterns across time buckets",
                "flag deviations from expected seasonal bands",
            ],
            "hypothesis_tests": [
                "test variance vs baseline",
                "test segment lift vs control",
            ],
            "user_inputs": {
                "focus_metric": focus_metric,
                "chart_type": chart_type,
                "time_axis": time_axis,
            },
        }

    @staticmethod
    def _resolve_user_selection(artifacts: Dict[str, Any], form_id: str, default: str) -> str:
        user_inputs = artifacts.get("user_input") if isinstance(artifacts, dict) else None
        if not isinstance(user_inputs, dict):
            return default
        entry = user_inputs.get(form_id)
        if not isinstance(entry, dict):
            return default
        values = entry.get("values")
        if not isinstance(values, dict):
            return default
        selection = values.get("selection") or values.get("value") or values.get("text")
        if isinstance(selection, str) and selection.strip():
            return selection.strip()
        return default

    def run(self, step_context: StepContext) -> AgentResult:
        try:
            payload = step_context.run.payload or {}
            plan = PlanningInput(
                comment=payload.get("replan_comment", ""),
                previous_run=payload.get("previous_run", {}),
            )
            interpreted_intent = (payload.get("prompt") or "").strip()
            focus_metric = self._resolve_user_selection(step_context.run.artifacts, "select_focus_metric", "mean")
            chart_type = self._resolve_user_selection(step_context.run.artifacts, "select_chart_type", "bar")
            time_axis = self._resolve_user_selection(step_context.run.artifacts, "confirm_time_axis", "yes")
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
                    "analysis_plan": self._analysis_plan(focus_metric, chart_type, time_axis),
                    "interpreted_intent": interpreted_intent,
                    "analysis_preferences": {
                        "focus_metric": focus_metric,
                        "chart_type": chart_type,
                        "time_axis": time_axis,
                    },
                },
                error=None,
                meta=meta,
            )
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=AgentMeta(agent_name=self.name))


def build() -> PlanningAgent:
    return PlanningAgent()
