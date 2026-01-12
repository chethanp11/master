from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.agents.base import BaseAgent, agent
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult
from products.ade.schemas.plan_spec import PlanDecision, PlanSpec


class PlanInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comment: str = Field(default="")


@agent(
    name="plan_agent",
    purpose="Creates analysis plans based on user requirements",
    capabilities=["planning", "step_sequencing", "resource_estimation"],
    cost_hint="MED",
)
class PlanAgent(BaseAgent):
    name = "plan_agent"
    description = "Builds a deterministic plan spec for ADE runs."

    @staticmethod
    def _question_type(text: str) -> str:
        lowered = text.lower()
        if any(token in lowered for token in ("why", "root cause", "cause", "explain")):
            return "explain_drop"
        if any(token in lowered for token in ("anomaly", "outlier", "spike", "unexpected")):
            return "anomaly_investigation"
        if any(token in lowered for token in ("compare", "vs", "versus")):
            return "comparison"
        if any(token in lowered for token in ("trend", "over time", "growth")):
            return "trend_summary"
        return "summary"

    def run(self, step_context: Any) -> AgentResult:
        try:
            payload = step_context.run.payload or {}
            plan_input = PlanInput(comment=payload.get("replan_comment", ""))
            intent = step_context.run.artifacts.get("agent.intent_agent.output")
            if not isinstance(intent, dict):
                intent = {}

            if intent.get("blocking_required"):
                raise ValueError("Blocking intent fields unresolved; cannot plan execution.")

            inferred_entities = intent.get("inferred_entities") or []
            inferred_metrics = intent.get("inferred_metrics") or []
            dataset_id = inferred_entities[0] if isinstance(inferred_entities, list) and inferred_entities else None
            metric = inferred_metrics[0] if isinstance(inferred_metrics, list) and inferred_metrics else None
            time_window = intent.get("inferred_time_window")
            chart_type = "line"
            include_hypothesis = False
            question_type = self._question_type(intent.get("intent_summary", ""))

            if not dataset_id:
                raise ValueError("Missing dataset selection; cannot build a deterministic plan.")
            if not metric:
                raise ValueError("Missing metric selection; cannot build a deterministic plan.")

            tool_flags = {
                "detect_anomalies": question_type in {"explain_drop", "anomaly_investigation"},
                "hypothesis_data_outage": question_type in {"explain_drop", "anomaly_investigation"} and include_hypothesis,
                "hypothesis_seasonality": question_type in {"explain_drop", "anomaly_investigation"} and include_hypothesis,
            }

            decisions = [
                PlanDecision(decision=f"Metric: {metric or 'unspecified'}", rationale="Aligns with stated intent."),
                PlanDecision(decision=f"Chart: {chart_type}", rationale="Readable summary for analyst review."),
            ]
            if time_window:
                decisions.append(PlanDecision(decision=f"Time window: {time_window}", rationale="Derived from intent or user input."))

            summary = "Plan focuses on required metrics and produces a business report with audit trail."
            if plan_input.comment:
                summary = f"{summary} Revision note: {plan_input.comment}"

            spec = PlanSpec(
                plan_summary=summary,
                question_type=question_type,
                dataset_id=dataset_id,
                metric=metric,
                time_window=time_window,
                chart_type=chart_type,
                aggregation="total",
                tool_flags=tool_flags,
                decision_points=decisions,
            )

            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=True, data=spec.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=AgentMeta(agent_name=self.name))


def build() -> PlanAgent:
    return PlanAgent()
