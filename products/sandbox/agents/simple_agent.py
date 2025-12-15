# ==============================
# Sandbox Agent: simple_agent
# ==============================
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from core.agents.base import BaseAgent
from core.contracts.agent_schema import AgentResult, AgentError, AgentMeta, AgentErrorCode
from core.orchestrator.context import StepContext


class SimpleAgentParams(BaseModel):
    template: str = Field(default="Summarize the run.")


class SimpleAgent(BaseAgent):
    """
    A minimal agent that reads artifacts from the StepContext and produces a summary.
    No model calls in v1 (keeps the golden path deterministic).
    """

    name: str = "simple_agent"
    description: str = "Deterministic summary agent for sandbox golden path."

    def run(self, step_context: StepContext) -> AgentResult:
        try:
            params = SimpleAgentParams.model_validate(step_context.step.params or {})
            artifacts = step_context.run.artifacts or {}

            echo_out: Dict[str, Any] = artifacts.get("tool.echo.output", {}) or {}
            approval: Dict[str, Any] = artifacts.get("hitl.approval", {}) or {}

            approved = approval.get("approved")
            notes = approval.get("notes", "")

            msg = echo_out.get("echo") or echo_out.get("message") or echo_out.get("input") or ""
            summary = (
                f"{params.template}\n\n"
                f"- Echoed message: {msg!r}\n"
                f"- Approved: {approved}\n"
                f"- Notes: {notes!r}\n"
            )

            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=True, data={"summary": summary}, error=None, meta=meta)
        except Exception as e:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(e))
            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=False, data=None, error=err, meta=meta)


def build() -> SimpleAgent:
    return SimpleAgent()
