# ==============================
# Product Registration (Hello World)
# ==============================
"""
Registers hello_world agents/tools into core registries.

This module must remain side-effect safe:
- No persistence
- No network calls
- Only registry registration
"""

from __future__ import annotations

from core.contracts.descriptors_schema import (
    AgentDescriptor,
    ToolDescriptor,
    CostHint,
    SensitivityClass,
)
from products.hello_world.agents.simple_agent import build as build_agent
from products.hello_world.tools.echo_tool import build as build_tool
from core.utils.product_loader import ProductRegistries


# ==============================
# Descriptors
# ==============================

ECHO_TOOL_DESCRIPTOR = ToolDescriptor(
    name="echo_tool",
    description="Returns the provided message unchanged. Useful for testing and debugging.",
    capabilities=["echo", "testing", "debugging"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.LOW,
    cost_hint=CostHint.LOW,
)

SIMPLE_AGENT_DESCRIPTOR = AgentDescriptor(
    name="simple_agent",
    purpose="Simple demonstration agent for hello_world product",
    purposes=["demonstration", "testing"],
    capabilities=["basic_response", "testing"],
    cost_hint=CostHint.LOW,
    allowed_step_types=["agent"],
)


def register(registries: ProductRegistries) -> None:
    agent = build_agent()
    tool = build_tool()

    registries.agent_registry.register(
        agent.name,
        build_agent,
        descriptor=SIMPLE_AGENT_DESCRIPTOR,
    )
    registries.tool_registry.register(
        tool.name,
        build_tool,
        descriptor=ECHO_TOOL_DESCRIPTOR,
    )
