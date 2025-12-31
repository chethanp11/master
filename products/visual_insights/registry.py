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
from products.visual_insights.tools.assemble_insight_card import build as build_assemble_insight_card
from products.visual_insights.tools.build_chart_spec import build as build_chart_spec
from products.visual_insights.tools.data_reader import build as build_data_reader
from products.visual_insights.tools.detect_anomalies import build as build_detect_anomalies
from products.visual_insights.tools.driver_analysis import build as build_driver_analysis
from products.visual_insights.tools.export_pdf import build as build_export_pdf
from products.visual_insights.tools.ingest_files import build as build_ingest_files
from products.visual_insights.tools.profile_index import build as build_profile_index
from products.visual_insights.tools.recommend_chart import build as build_recommend_chart


def register(registries: ProductRegistries) -> None:
    registries.agent_registry.register(build_agent().name, build_agent)
    registries.tool_registry.register(build_data_reader().name, build_data_reader)
    registries.tool_registry.register(build_chart_spec().name, build_chart_spec)
    registries.tool_registry.register(build_recommend_chart().name, build_recommend_chart)
    registries.tool_registry.register(build_detect_anomalies().name, build_detect_anomalies)
    registries.tool_registry.register(build_driver_analysis().name, build_driver_analysis)
    registries.tool_registry.register(build_assemble_insight_card().name, build_assemble_insight_card)
    registries.tool_registry.register(build_ingest_files().name, build_ingest_files)
    registries.tool_registry.register(build_profile_index().name, build_profile_index)
    registries.tool_registry.register(build_export_pdf().name, build_export_pdf)
