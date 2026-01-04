from __future__ import annotations

# Analytical Decision Engine agent

from typing import Any, Dict

from pydantic import BaseModel, Field

from core.agents.base import BaseAgent
from core.contracts.agent_schema import AgentResult, AgentError, AgentErrorCode, AgentMeta
from core.orchestrator.context import StepContext


class DashboardAgentParams(BaseModel):
    template: str = Field(
        default="Dashboard summary: {summary}",
        description="Template used to synthesize insights.",
    )


class DashboardAgent(BaseAgent):
    name = "dashboard_agent"
    description = "Creates a narrative summary for the visual insights dashboard."

    def run(self, step_context: StepContext) -> AgentResult:
        try:
            params = DashboardAgentParams.model_validate(step_context.step.params or {})
            artifacts = step_context.run.artifacts or {}
            tool_output = artifacts.get("tool.data_reader.output", {}) or {}
            summary = tool_output.get("summary", "No insights available.")
            message = params.template.format(summary=summary)
            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=True, data={"message": message, "insight": summary}, error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            return AgentResult(ok=False, data=None, error=err, meta=AgentMeta(agent_name=self.name))


def build() -> DashboardAgent:
    return DashboardAgent()
