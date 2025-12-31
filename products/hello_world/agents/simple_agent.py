# ==============================
# Hello World Agent: simple_agent
# ==============================
from __future__ import annotations

from typing import Any, Dict

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
    description: str = "Deterministic summary agent for hello_world golden path."

    def run(self, step_context: StepContext) -> AgentResult:
        try:
            params = SimpleAgentParams.model_validate(step_context.step.params or {})
            payload = step_context.run.payload or {}
            message = payload.get("keyword") or payload.get("message") or ""
            approved = payload.get("approved", True)
            notes = payload.get("notes") or ""

            approval_status = "approved" if approved else "rejected"
            summary = (
                f"{params.template}\n\n"
                f"- Echoed message: {message!r}\n"
                f"- Approval status: {approval_status}\n"
                f"- Notes provided: {notes!r}\n"
            )
            details = {
                "message": message,
                "approved": approved,
                "notes": notes,
                "approval_status": approval_status,
            }

            meta = AgentMeta(agent_name=self.name, tags={"product": step_context.run.product, "flow": step_context.run.flow})
            return AgentResult(ok=True, data={"summary": summary, "details": details}, error=None, meta=meta)
        except Exception as exc:
            err = AgentError(code=AgentErrorCode.UNKNOWN, message=str(exc))
            meta = AgentMeta(agent_name=self.name)
            return AgentResult(ok=False, data=None, error=err, meta=meta)


def build() -> SimpleAgent:
    return SimpleAgent()
