# core/agents/__init__.py
# ==============================
# Agents Package
# ==============================
"""
Core agents package.

Provides:
- BaseAgent: Base contract for all agents
- Advisory agents: Bounded intelligence components for recommendations
- Agent registry: Registration and lookup of agents
"""

from .base import BaseAgent
from .registry import AgentRegistry

# Import advisors subpackage
from . import advisors
from .advisors import (
    AdvisoryAgent,
    ToolSelector,
    AgentSelector,
    GapFinder,
    Summarizer,
    RiskExplainer,
    build_tool_selector,
    build_agent_selector,
    build_gap_finder,
    build_summarizer,
    build_risk_explainer,
)

__all__ = [
    # Base
    "BaseAgent",
    "AgentRegistry",
    # Advisors subpackage
    "advisors",
    # Advisory base and classes (re-exported for convenience)
    "AdvisoryAgent",
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
