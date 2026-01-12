# core/agents/advisors/tool_selector.py
# ==============================
# Tool Selector Advisory Agent
# ==============================
"""
Advisory agent that recommends tools based on descriptors and context.

Outputs structured ToolSelectionResult with:
- Recommended tools with rationale and confidence
- Rejected tools with reasons
- Assumptions made during selection
- Unknown factors that may affect selection
"""

from __future__ import annotations

from core.contracts.agent_schema import AgentKind
from core.contracts.advisory_schema import ToolSelectorOutput
from core.contracts.reasoning_schema import ReasoningPurpose

from .base import AdvisoryAgent


class ToolSelector(AdvisoryAgent):
    """
    Advisory agent that recommends tools based on context and descriptors.

    Analyzes the question, context pack, and available tool descriptors to
    recommend which tools should be used to gather evidence or perform actions.

    Does NOT execute tools - only recommends them.
    """

    name: str = "tool_selector"
    description: str = "Recommends tools based on descriptors and context."
    kind: AgentKind = AgentKind.ROUTER
    purpose: ReasoningPurpose = ReasoningPurpose.PRIORITIZATION
    output_model = ToolSelectorOutput

    def _build_system_prompt(self) -> str:
        return """You are a tool selection advisor. Your role is to recommend which tools should be used based on the question and context provided.

IMPORTANT RULES:
1. You CANNOT execute tools - you can only recommend them
2. You MUST return valid JSON matching the expected schema
3. Do NOT include any control directives (next_step, retry, branch, etc.)
4. Base recommendations on tool capabilities, required inputs, and expected outputs

For each recommended tool, provide:
- tool_name: The exact registered tool name
- reason: Why this tool is appropriate (max 300 chars)
- required_inputs: What inputs the tool needs
- expected_evidence_types: What types of evidence it will produce
- confidence: Your confidence in this recommendation (0.0-1.0)

For rejected tools, explain why they are not suitable.

List any assumptions you made and any unknowns that affect your recommendations.

Return JSON only with this structure:
{
    "recommended_tools": [...],
    "rejected_tools": [...],
    "assumptions": [...],
    "unknowns": [...]
}"""


def build_tool_selector() -> ToolSelector:
    """Factory function to create a ToolSelector agent."""
    return ToolSelector()
