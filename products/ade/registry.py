# ==============================
# Product Registry (Registration Entrypoint)
# ==============================
"""
products/ade/registry.py

This is the canonical registration entrypoint for this product.

Rules:
- Keep this module side-effect safe:
  - No persistence
  - No network calls
  - No model calls
- Only register agents/tools with core registries.
- Product loader will import this module to bind components.

How to use:
1) Implement agents in products/ade/agents/
2) Implement tools in products/ade/tools/
3) Register them in register()

Example (after you create a tool/agent):
  from core.utils.product_loader import ProductRegistries
  from products.ade.agents.my_agent import build as build_agent
  from products.ade.tools.my_tool import build as build_tool

  def register(registries: ProductRegistries) -> None:
      registries.agent_registry.register(build_agent().name, build_agent)
      registries.tool_registry.register(build_tool().name, build_tool)
"""

from __future__ import annotations




from core.utils.product_loader import ProductRegistries
from products.ade.agents.dashboard_agent import build as build_agent
from products.ade.agents.planning_agent import build as build_planning_agent
from products.ade.agents.sufficiency_evaluator import build as build_sufficiency_evaluator
from products.ade.tools.assemble_decision_packet import build as build_assemble_decision_packet
from products.ade.tools.assemble_insight_card import build as build_assemble_insight_card
from products.ade.tools.build_chart_spec import build as build_chart_spec
from products.ade.tools.data_reader import build as build_data_reader
from products.ade.tools.detect_anomalies import build as build_detect_anomalies
from products.ade.tools.driver_analysis import build as build_driver_analysis
from products.ade.tools.export_pdf import build as build_export_pdf
from products.ade.tools.hypothesis_test_data_outage import build as build_hypothesis_test_data_outage
from products.ade.tools.hypothesis_test_seasonality import build as build_hypothesis_test_seasonality
from products.ade.tools.render_decision_packet_html import build as build_render_decision_packet_html
from products.ade.tools.recommend_chart import build as build_recommend_chart


def register(registries: ProductRegistries) -> None:
    registries.agent_registry.register(build_agent().name, build_agent)
    registries.agent_registry.register(build_planning_agent().name, build_planning_agent)
    registries.agent_registry.register(build_sufficiency_evaluator().name, build_sufficiency_evaluator)
    registries.tool_registry.register(build_data_reader().name, build_data_reader)
    registries.tool_registry.register(build_chart_spec().name, build_chart_spec)
    registries.tool_registry.register(build_recommend_chart().name, build_recommend_chart)
    registries.tool_registry.register(build_detect_anomalies().name, build_detect_anomalies)
    registries.tool_registry.register(build_driver_analysis().name, build_driver_analysis)
    registries.tool_registry.register(build_assemble_insight_card().name, build_assemble_insight_card)
    registries.tool_registry.register(build_assemble_decision_packet().name, build_assemble_decision_packet)
    registries.tool_registry.register(build_export_pdf().name, build_export_pdf)
    registries.tool_registry.register(build_render_decision_packet_html().name, build_render_decision_packet_html)
    registries.tool_registry.register(build_hypothesis_test_data_outage().name, build_hypothesis_test_data_outage)
    registries.tool_registry.register(build_hypothesis_test_seasonality().name, build_hypothesis_test_seasonality)
