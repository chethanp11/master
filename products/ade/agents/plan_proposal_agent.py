from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from core.agents.base import BaseAgent
from core.contracts.agent_schema import AgentError, AgentErrorCode, AgentMeta, AgentResult
from core.contracts.plan_schema import EstimatedCost, PlanProposal, PlanStep
from core.orchestrator.context import StepContext


class PlanProposalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comment: str = Field(default="")


class PlanProposalAgent(BaseAgent):
    name = "plan_proposal_agent"
    description = "Generates a deterministic plan proposal for ADE flows."

    @staticmethod
    def _resolve_pref(artifacts: Dict[str, Any], key: str, default: Any) -> Any:
        user_inputs = artifacts.get("user_input") if isinstance(artifacts, dict) else None
        if not isinstance(user_inputs, dict):
            return default
        entry = user_inputs.get("viz_preferences")
        if not isinstance(entry, dict):
            return default
        values = entry.get("values")
        if not isinstance(values, dict):
            return default
        value = values.get(key)
        return default if value is None else value

    def run(self, step_context: StepContext) -> AgentResult:
        try:
            payload = step_context.run.payload or {}
            plan_input = PlanProposalInput(comment=payload.get("replan_comment", ""))
            chart_type = str(self._resolve_pref(step_context.run.artifacts, "chart_type", "bar"))
            metric_focus = str(self._resolve_pref(step_context.run.artifacts, "metric_focus", "mean"))
            include_hypothesis_checks = bool(
                self._resolve_pref(step_context.run.artifacts, "include_hypothesis_checks", True)
            )
            notes = str(self._resolve_pref(step_context.run.artifacts, "notes", "") or "")

            steps: List[PlanStep] = [
                PlanStep(
                    step_id="compute_business_metrics",
                    description="Compute business metrics for reporting.",
                    step_type="tool",
                    tool="compute_business_metrics",
                ),
            ]
            if include_hypothesis_checks:
                steps.extend(
                    [
                        PlanStep(
                            step_id="hypothesis_data_outage",
                            description="Check for recent outage patterns.",
                            step_type="tool",
                            tool="hypothesis_test_data_outage",
                        ),
                        PlanStep(
                            step_id="hypothesis_seasonality",
                            description="Check for seasonal signals.",
                            step_type="tool",
                            tool="hypothesis_test_seasonality",
                        ),
                    ]
                )
            steps.extend(
                [
                    PlanStep(
                        step_id="build_chart_spec",
                        description="Build chart spec using selected chart type.",
                        step_type="tool",
                        tool="build_chart_spec",
                    ),
                    PlanStep(
                        step_id="assemble_evidence_bundle",
                        description="Assemble deterministic evidence bundle.",
                        step_type="tool",
                        tool="assemble_evidence_bundle",
                    ),
                    PlanStep(
                        step_id="assemble_decision_packet",
                        description="Assemble decision packet with evidence and narratives.",
                        step_type="tool",
                        tool="assemble_decision_packet",
                    ),
                    PlanStep(
                        step_id="assemble_business_report",
                        description="Assemble business report for stakeholders.",
                        step_type="tool",
                        tool="assemble_business_report",
                    ),
                    PlanStep(
                        step_id="render_business_report_html",
                        description="Render business report HTML.",
                        step_type="tool",
                        tool="render_business_report_html",
                    ),
                    PlanStep(
                        step_id="render_decision_packet_html",
                        description="Render decision packet to HTML.",
                        step_type="tool",
                        tool="render_decision_packet_html",
                    ),
                ]
            )

            checks_summary = "hypothesis checks enabled" if include_hypothesis_checks else "hypothesis checks skipped"
            summary = (
                f"Plan uses chart '{chart_type}' and focuses on '{metric_focus}'. "
                f"{checks_summary}. {notes}".strip()
            )
            plan = PlanProposal(
                summary=summary,
                steps=steps,
                required_tools=[step.tool for step in steps if step.tool],
                approvals=[],
                estimated_cost=EstimatedCost(currency="USD", amount=0.0, tokens=0, details={"comment": plan_input.comment}),
            )
            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=True, data=plan.model_dump(mode="json"), error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=AgentMeta(agent_name=self.name))


def build() -> PlanProposalAgent:
    return PlanProposalAgent()
