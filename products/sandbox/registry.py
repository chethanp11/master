# ==============================
# Product Registration (Sandbox)
# ==============================
"""
Registers sandbox agents/tools into core registries.

This module must remain side-effect safe:
- No persistence
- No network calls
- Only registry registration
"""

from __future__ import annotations

from core.agents.registry import AgentRegistry
from core.tools.registry import ToolRegistry

from products.sandbox.agents.simple_agent import build as build_agent
from products.sandbox.tools.echo_tool import build as build_tool


def register() -> None:
    agent = build_agent()
    tool = build_tool()
    AgentRegistry.register(agent.name, build_agent)
    ToolRegistry.register(tool.name, build_tool)


# Run registration on import (explicitly imported by product_loader.register_product)
register()
