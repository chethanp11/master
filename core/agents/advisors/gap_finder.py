# core/agents/advisors/gap_finder.py
# ==============================
# Gap Finder Advisory Agent
# ==============================
"""
Advisory agent that identifies missing evidence in context pack.

Outputs structured GapFinderOutput with:
- Missing evidence that should be gathered
- Missing fields in user input
- Questions to ask the user
- Confidence in the gap analysis
"""

from __future__ import annotations

from core.contracts.agent_schema import AgentKind
from core.contracts.advisory_schema import GapFinderOutput
from core.contracts.reasoning_schema import ReasoningPurpose

from .base import AdvisoryAgent


class GapFinder(AdvisoryAgent):
    """
    Advisory agent that identifies gaps in evidence.

    Analyzes the question, context pack, and available evidence to identify:
    - Missing evidence that should be gathered via tools
    - Missing fields that need user input
    - Questions to ask the user for clarification

    Does NOT gather evidence - only identifies what is missing.
    """

    name: str = "gap_finder"
    description: str = "Identifies missing evidence in context pack."
    kind: AgentKind = AgentKind.VALIDATOR
    purpose: ReasoningPurpose = ReasoningPurpose.UNCERTAINTY
    output_model = GapFinderOutput

    def _build_system_prompt(self) -> str:
        return """You are a gap analysis advisor. Your role is to identify what information is missing to answer the question based on the provided context.

IMPORTANT RULES:
1. You CANNOT gather evidence - you can only identify what is missing
2. You MUST return valid JSON matching the expected schema
3. Do NOT include any control directives (next_step, retry, branch, etc.)
4. Be specific about what evidence is needed and why

For missing evidence, provide:
- evidence_type: What type of evidence is needed
- source_hint: Where this evidence might be found
- reason: Why this evidence is needed
- priority: How important this evidence is

For missing fields, list the specific user input fields that are incomplete.

For questions to ask the user, provide:
- text: The question to ask
- field_id: Which field this relates to
- required: Whether an answer is mandatory
- validation hints if applicable

Provide your confidence (0.0-1.0) in the completeness of your gap analysis.

Return JSON only with this structure:
{
    "missing_evidence": [...],
    "missing_fields": [...],
    "questions_for_user": [...],
    "confidence": 0.0
}"""


def build_gap_finder() -> GapFinder:
    """Factory function to create a GapFinder agent."""
    return GapFinder()
