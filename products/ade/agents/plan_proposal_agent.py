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
    def _plan_spec(artifacts: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(artifacts, dict):
            return {}
        plan_spec = artifacts.get("agent.plan_agent.output")
        if not isinstance(plan_spec, dict):
            return {}
        return plan_spec

    def run(self, step_context: StepContext) -> AgentResult:
        try:
            payload = step_context.run.payload or {}
            plan_input = PlanProposalInput(comment=payload.get("replan_comment", ""))
            plan_spec = self._plan_spec(step_context.run.artifacts)
            chart_type = str(plan_spec.get("chart_type") or "line")
            metric_focus = str(plan_spec.get("metric") or "metric")
            tool_flags = plan_spec.get("tool_flags") if isinstance(plan_spec.get("tool_flags"), dict) else {}
            notes = str(plan_input.comment or "")

            steps: List[PlanStep] = [
                PlanStep(
                    step_id="read",
                    description="Read the target dataset.",
                    step_type="tool",
                    tool="data_reader",
                ),
                PlanStep(
                    step_id="compute_business_metrics",
                    description="Compute metrics required for the business report.",
                    step_type="tool",
                    tool="compute_business_metrics",
                ),
            ]
            if tool_flags.get("detect_anomalies"):
                steps.append(
                    PlanStep(
                        step_id="detect_anomalies",
                        description="Detect anomalies if investigation requires it.",
                        step_type="tool",
                        tool="detect_anomalies",
                    )
                )
            if tool_flags.get("hypothesis_data_outage"):
                steps.append(
                    PlanStep(
                        step_id="hypothesis_data_outage",
                        description="Check for recent outage patterns.",
                        step_type="tool",
                        tool="hypothesis_test_data_outage",
                    )
                )
            if tool_flags.get("hypothesis_seasonality"):
                steps.append(
                    PlanStep(
                        step_id="hypothesis_seasonality",
                        description="Check for seasonal signals.",
                        step_type="tool",
                        tool="hypothesis_test_seasonality",
                    )
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
                        step_id="assemble_decision_packet",
                        description="Assemble decision packet with evidence and reasoning.",
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
                        step_id="build_reasoning_narrative",
                        description="Build reasoning narrative from run events.",
                        step_type="tool",
                        tool="build_reasoning_narrative",
                    ),
                    PlanStep(
                        step_id="render_decision_packet_html",
                        description="Render decision packet to HTML.",
                        step_type="tool",
                        tool="render_decision_packet_html",
                    ),
                ]
            )

            summary = f"Plan uses chart '{chart_type}' and focuses on '{metric_focus}'. {notes}".strip()
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
