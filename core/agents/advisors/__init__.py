# core/agents/advisors/__init__.py
# ==============================
# Advisory Agents Package
# ==============================
"""
Bounded advisory agents that provide structured recommendations.

Advisory agents are intelligence components that:
- Analyze context and evidence
- Recommend actions without executing them
- Cannot invoke tool execution directly
- Output validated, structured results

Available advisors:
- ToolSelector: Recommends tools based on descriptors and context
- AgentSelector: Recommends agents for subtasks
- GapFinder: Identifies missing evidence in context pack
- Summarizer: Condenses evidence into narrative summary
- RiskExplainer: Explains confidence and risk factors

Usage:
    from core.agents.advisors import ToolSelector, build_tool_selector

    # Direct instantiation
    advisor = ToolSelector()

    # Factory function
    advisor = build_tool_selector()
"""

from .base import AdvisoryAgent, AdvisoryReasoner
from .tool_selector import ToolSelector, build_tool_selector
from .agent_selector import AgentSelector, build_agent_selector
from .gap_finder import GapFinder, build_gap_finder
from .summarizer import Summarizer, build_summarizer
from .risk_explainer import RiskExplainer, build_risk_explainer

__all__ = [
    # Base class
    "AdvisoryAgent",
    "AdvisoryReasoner",
    # Advisor classes
    "ToolSelector",
    "AgentSelector",
    "GapFinder",
    "Summarizer",
    "RiskExplainer",
    # Factory functions
    "build_tool_selector",
    "build_agent_selector",
    "build_gap_finder",
    "build_summarizer",
    "build_risk_explainer",
]
