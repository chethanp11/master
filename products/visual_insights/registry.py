# ==============================
# Product Registry (Registration Entrypoint)
# ==============================
"""
products/visual_insights/registry.py

This is the canonical registration entrypoint for this product.

Rules:
- Keep this module side-effect safe:
  - No persistence
  - No network calls
  - No model calls
- Only register agents/tools with core registries.
- Product loader will import this module to bind components.

How to use:
1) Implement agents in products/visual_insights/agents/
2) Implement tools in products/visual_insights/tools/
3) Register them in register()

Example (after you create a tool/agent):
  from core.utils.product_loader import ProductRegistries
  from products.visual_insights.agents.my_agent import build as build_agent
  from products.visual_insights.tools.my_tool import build as build_tool

  def register(registries: ProductRegistries) -> None:
      registries.agent_registry.register(build_agent().name, build_agent)
      registries.tool_registry.register(build_tool().name, build_tool)
"""

from __future__ import annotations


from core.utils.product_loader import ProductRegistries
from products.visual_insights.agents.dashboard_agent import build as build_agent
from products.visual_insights.tools.data_reader import build as build_tool


def register(registries: ProductRegistries) -> None:
    registries.agent_registry.register(build_agent().name, build_agent)
    registries.tool_registry.register(build_tool().name, build_tool)
