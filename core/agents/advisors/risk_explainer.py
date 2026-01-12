# core/agents/advisors/risk_explainer.py
# ==============================
# Risk Explainer Advisory Agent
# ==============================
"""
Advisory agent that explains confidence and risk factors.

Outputs structured RiskExplainerOutput with:
- Risk factors with severity levels
- Mitigations for identified risks
- Confidence in the risk assessment
- Assumptions and unknowns
"""

from __future__ import annotations

from core.contracts.agent_schema import AgentKind
from core.contracts.advisory_schema import RiskExplainerOutput
from core.contracts.reasoning_schema import ReasoningPurpose

from .base import AdvisoryAgent


class RiskExplainer(AdvisoryAgent):
    """
    Advisory agent that explains risks and confidence levels.

    Analyzes the question, context pack, and available evidence to:
    - Identify risk factors that affect the answer
    - Assess severity of each risk (LOW/MED/HIGH)
    - Suggest mitigations for identified risks
    - Explain confidence levels and their drivers

    Does NOT mitigate risks - only identifies and explains them.
    """

    name: str = "risk_explainer"
    description: str = "Explains confidence and risk factors."
    kind: AgentKind = AgentKind.OTHER
    purpose: ReasoningPurpose = ReasoningPurpose.EXPLANATION
    output_model = RiskExplainerOutput

    def _build_system_prompt(self) -> str:
        return """You are a risk analysis advisor. Your role is to identify and explain risk factors and confidence levels based on the provided context.

IMPORTANT RULES:
1. You CANNOT mitigate risks - you can only identify and explain them
2. You MUST return valid JSON matching the expected schema
3. Do NOT include any control directives (next_step, retry, branch, etc.)
4. Be specific about what drives each risk assessment

For each risk factor, provide:
- factor: Brief description of the risk (max 200 chars)
- rationale: Why this is a risk (max 500 chars)
- evidence_refs: Which evidence items relate to this risk
- severity: "LOW", "MED", or "HIGH"

For mitigations:
- List potential ways to address or reduce each risk
- Be actionable but advisory (the orchestrator decides execution)

Provide:
- confidence: Your confidence in this risk assessment (0.0-1.0)
- assumptions: What you assumed in making this assessment
- unknowns: Factors that could change your assessment

At least one risk factor must be identified.

Return JSON only with this structure:
{
    "risk_factors": [...],
    "mitigations": [...],
    "confidence": 0.0,
    "assumptions": [...],
    "unknowns": [...]
}"""


def build_risk_explainer() -> RiskExplainer:
    """Factory function to create a RiskExplainer agent."""
    return RiskExplainer()
