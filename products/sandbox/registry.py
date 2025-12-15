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

from products.sandbox.agents.simple_agent import build as build_agent
from products.sandbox.tools.echo_tool import build as build_tool
from core.utils.product_loader import ProductRegistries


def register(registries: ProductRegistries) -> None:
    agent = build_agent()
    tool = build_tool()

    registries.agent_registry.register(agent.name, build_agent)
    registries.tool_registry.register(tool.name, build_tool)
