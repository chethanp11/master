from __future__ import annotations

# Analytical Decision Engine agent

from typing import Any, Dict

from pydantic import BaseModel, Field

from core.agents.base import BaseAgent, agent
from core.contracts.agent_schema import AgentResult, AgentError, AgentErrorCode, AgentMeta


class DashboardAgentParams(BaseModel):
    template: str = Field(
        default="Dashboard summary: {summary}",
        description="Template used to synthesize insights.",
    )


class DashboardOutput(BaseModel):
    message: str
    insight: str
    anomaly_summary: str = ""
    anomaly_interpretation: str = ""
    anomaly_count: int = 0


@agent(
    name="dashboard_agent",
    purpose="Coordinates dashboard generation and visualization tasks",
    capabilities=["orchestration", "visualization", "coordination"],
    cost_hint="MED",
)
class DashboardAgent(BaseAgent):
    name = "dashboard_agent"
    description = "Creates a narrative summary for the visual insights dashboard."

    def run(self, step_context: Any) -> AgentResult:
        try:
            params = DashboardAgentParams.model_validate(step_context.step.params or {})
            artifacts = step_context.run.artifacts or {}
            tool_output = artifacts.get("tool.data_reader.output", {}) or {}
            summary = tool_output.get("summary", "No insights available.")
            message = params.template.format(summary=summary)
            anomaly_output = artifacts.get("tool.detect_anomalies.output", {}) or {}
            anomalies = anomaly_output.get("anomalies") if isinstance(anomaly_output, dict) else None
            anomaly_count = len(anomalies) if isinstance(anomalies, list) else 0
            anomaly_summary = anomaly_output.get("summary", "") if isinstance(anomaly_output, dict) else ""
            anomaly_interpretation = ""
            if anomaly_count:
                anomaly_interpretation = (
                    f"Detected {anomaly_count} anomaly candidates; review periods with the largest deviations."
                )
            payload = DashboardOutput(
                message=message,
                insight=summary,
                anomaly_summary=str(anomaly_summary or ""),
                anomaly_interpretation=anomaly_interpretation,
                anomaly_count=anomaly_count,
            ).model_dump(mode="json")
            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=True, data=payload, error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=AgentMeta(agent_name=self.name))


def build() -> DashboardAgent:
    return DashboardAgent()
