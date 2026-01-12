# core/agents/advisors/summarizer.py
# ==============================
# Summarizer Advisory Agent
# ==============================
"""
Advisory agent that condenses evidence into narrative summary.

Outputs structured SummarizerOutput with:
- Summary narrative
- Key points extracted from evidence
- References to evidence sources
"""

from __future__ import annotations

from core.contracts.agent_schema import AgentKind
from core.contracts.advisory_schema import SummarizerOutput
from core.contracts.reasoning_schema import ReasoningPurpose

from .base import AdvisoryAgent


class Summarizer(AdvisoryAgent):
    """
    Advisory agent that summarizes evidence into narrative.

    Analyzes the question, context pack, and available evidence to produce:
    - A concise summary narrative
    - Key points extracted from evidence
    - References to the evidence sources used

    Does NOT generate new information - only summarizes what exists.
    """

    name: str = "summarizer"
    description: str = "Condenses evidence into narrative summary."
    kind: AgentKind = AgentKind.SUMMARIZER
    purpose: ReasoningPurpose = ReasoningPurpose.EXPLANATION
    output_model = SummarizerOutput

    def _build_system_prompt(self) -> str:
        return """You are a summarization advisor. Your role is to condense the provided evidence into a clear, concise narrative that addresses the question.

IMPORTANT RULES:
1. You CANNOT generate new information - only summarize what exists
2. You MUST return valid JSON matching the expected schema
3. Do NOT include any control directives (next_step, retry, branch, etc.)
4. Every claim must be traceable to evidence

For the summary:
- Be concise but comprehensive (max 1000 chars)
- Address the question directly
- Highlight the most important findings

For key points:
- Extract the most salient facts (max 10 points)
- Each point should be atomic and verifiable

For evidence refs:
- List the IDs of evidence items you referenced
- Only cite evidence you actually used

Return JSON only with this structure:
{
    "summary": "...",
    "key_points": [...],
    "evidence_refs": [...]
}"""


def build_summarizer() -> Summarizer:
    """Factory function to create a Summarizer agent."""
    return Summarizer()
