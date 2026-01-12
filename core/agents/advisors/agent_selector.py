# core/agents/advisors/agent_selector.py
# ==============================
# Agent Selector Advisory Agent
# ==============================
"""
Advisory agent that recommends agents for subtasks.

Outputs structured AgentSelectionResult with:
- Recommended agents with rationale and confidence
- Rejected agents with reasons
- Assumptions made during selection
- Unknown factors that may affect selection
"""

from __future__ import annotations

from core.contracts.agent_schema import AgentKind
from core.contracts.advisory_schema import AgentSelectorOutput
from core.contracts.reasoning_schema import ReasoningPurpose

from .base import AdvisoryAgent


class AgentSelector(AdvisoryAgent):
    """
    Advisory agent that recommends agents for subtasks.

    Analyzes the question, context pack, and available agent descriptors to
    recommend which agents should handle specific subtasks or reasoning steps.

    Does NOT invoke agents - only recommends them.
    """

    name: str = "agent_selector"
    description: str = "Recommends agents for subtasks based on context."
    kind: AgentKind = AgentKind.ROUTER
    purpose: ReasoningPurpose = ReasoningPurpose.PRIORITIZATION
    output_model = AgentSelectorOutput

    def _build_system_prompt(self) -> str:
        return """You are an agent selection advisor. Your role is to recommend which agents should handle specific subtasks based on the question and context provided.

IMPORTANT RULES:
1. You CANNOT invoke agents - you can only recommend them
2. You MUST return valid JSON matching the expected schema
3. Do NOT include any control directives (next_step, retry, branch, etc.)
4. Base recommendations on agent capabilities and the nature of the subtask

For each recommended agent, provide:
- agent_name: The exact registered agent name
- reason: Why this agent is appropriate (max 300 chars)
- confidence: Your confidence in this recommendation (0.0-1.0)

For rejected agents, explain why they are not suitable for this task.

List any assumptions you made and any unknowns that affect your recommendations.

Return JSON only with this structure:
{
    "recommended_agents": [...],
    "rejected_agents": [...],
    "assumptions": [...],
    "unknowns": [...]
}"""


def build_agent_selector() -> AgentSelector:
    """Factory function to create an AgentSelector agent."""
    return AgentSelector()
