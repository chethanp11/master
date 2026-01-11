# ==============================
# ADE Product Descriptors
# ==============================
"""
Descriptors for ADE (Analytical Decision Engine) tools and agents.

These descriptors provide metadata for tool/agent selection, governance,
and cost estimation without requiring execution.
"""

from __future__ import annotations

from core.contracts.descriptors_schema import (
    AgentDescriptor,
    ToolDescriptor,
    CostHint,
    SensitivityClass,
)


# ==============================
# Tool Descriptors
# ==============================

DATA_READER_DESCRIPTOR = ToolDescriptor(
    name="data_reader",
    description="Reads and parses CSV datasets, extracting columns, rows, and basic metadata.",
    capabilities=["data_reading", "csv_parsing", "data_extraction"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.MED,
    cost_hint=CostHint.LOW,
)

BUILD_CHART_SPEC_DESCRIPTOR = ToolDescriptor(
    name="build_chart_spec",
    description="Builds a chart specification from data for visualization.",
    capabilities=["visualization", "chart_building", "data_presentation"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.LOW,
    cost_hint=CostHint.LOW,
)

RECOMMEND_CHART_DESCRIPTOR = ToolDescriptor(
    name="recommend_chart",
    description="Recommends the best chart type for a given dataset structure.",
    capabilities=["visualization", "recommendation", "data_analysis"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.LOW,
    cost_hint=CostHint.LOW,
)

DETECT_ANOMALIES_DESCRIPTOR = ToolDescriptor(
    name="detect_anomalies",
    description="Detects statistical anomalies in time series data using z-score analysis.",
    capabilities=["anomaly_detection", "statistical_analysis", "time_series"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.MED,
    cost_hint=CostHint.LOW,
)

DRIVER_ANALYSIS_DESCRIPTOR = ToolDescriptor(
    name="driver_analysis",
    description="Performs driver analysis to identify key factors affecting metrics.",
    capabilities=["driver_analysis", "statistical_analysis", "root_cause"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.MED,
    cost_hint=CostHint.MED,
)

ASSEMBLE_INSIGHT_CARD_DESCRIPTOR = ToolDescriptor(
    name="assemble_insight_card",
    description="Assembles structured insight cards from analysis results.",
    capabilities=["insight_generation", "report_building", "summarization"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.LOW,
    cost_hint=CostHint.LOW,
)

ASSEMBLE_DECISION_PACKET_DESCRIPTOR = ToolDescriptor(
    name="assemble_decision_packet",
    description="Assembles a decision packet with evidence, reasoning, and recommendations.",
    capabilities=["decision_support", "report_building", "evidence_aggregation"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.MED,
    cost_hint=CostHint.LOW,
)

ASSEMBLE_EVIDENCE_BUNDLE_DESCRIPTOR = ToolDescriptor(
    name="assemble_evidence_bundle",
    description="Bundles evidence items from multiple sources into a cohesive package.",
    capabilities=["evidence_aggregation", "data_packaging", "provenance_tracking"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.MED,
    cost_hint=CostHint.LOW,
)

BUILD_REASONING_NARRATIVE_DESCRIPTOR = ToolDescriptor(
    name="build_reasoning_narrative",
    description="Constructs a narrative explanation of the analysis reasoning chain.",
    capabilities=["narrative_generation", "explanation", "reasoning_chain"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.LOW,
    cost_hint=CostHint.LOW,
)

COMPUTE_BUSINESS_METRICS_DESCRIPTOR = ToolDescriptor(
    name="compute_business_metrics",
    description="Computes business metrics including trends, movers, and period statistics.",
    capabilities=["computation", "business_metrics", "statistical_analysis"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.MED,
    cost_hint=CostHint.LOW,
)

ASSEMBLE_BUSINESS_REPORT_DESCRIPTOR = ToolDescriptor(
    name="assemble_business_report",
    description="Assembles a comprehensive business report from metrics and analysis.",
    capabilities=["report_building", "business_intelligence", "summarization"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.MED,
    cost_hint=CostHint.LOW,
)

EXPORT_PDF_DESCRIPTOR = ToolDescriptor(
    name="export_pdf",
    description="Exports reports to PDF format.",
    capabilities=["export", "pdf_generation", "document_output"],
    read_only=False,
    side_effect=True,
    sensitivity_class=SensitivityClass.LOW,
    cost_hint=CostHint.MED,
)

RENDER_BUSINESS_REPORT_HTML_DESCRIPTOR = ToolDescriptor(
    name="render_business_report_html",
    description="Renders business reports as HTML for web display.",
    capabilities=["rendering", "html_generation", "visualization"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.LOW,
    cost_hint=CostHint.LOW,
)

RENDER_DECISION_PACKET_HTML_DESCRIPTOR = ToolDescriptor(
    name="render_decision_packet_html",
    description="Renders decision packets as HTML for web display.",
    capabilities=["rendering", "html_generation", "visualization"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.LOW,
    cost_hint=CostHint.LOW,
)

HYPOTHESIS_TEST_DATA_OUTAGE_DESCRIPTOR = ToolDescriptor(
    name="hypothesis_test_data_outage",
    description="Tests hypothesis of data outage affecting metrics.",
    capabilities=["hypothesis_testing", "data_quality", "anomaly_detection"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.MED,
    cost_hint=CostHint.LOW,
)

HYPOTHESIS_TEST_SEASONALITY_DESCRIPTOR = ToolDescriptor(
    name="hypothesis_test_seasonality",
    description="Tests hypothesis of seasonality patterns in time series data.",
    capabilities=["hypothesis_testing", "time_series", "pattern_detection"],
    read_only=True,
    side_effect=False,
    sensitivity_class=SensitivityClass.MED,
    cost_hint=CostHint.LOW,
)


# ==============================
# Agent Descriptors
# ==============================

DASHBOARD_AGENT_DESCRIPTOR = AgentDescriptor(
    name="dashboard_agent",
    purpose="Coordinates dashboard generation and visualization tasks",
    purposes=["dashboard_generation", "visualization_coordination"],
    capabilities=["orchestration", "visualization", "coordination"],
    cost_hint=CostHint.MED,
    allowed_step_types=["agent"],
)

INTENT_AGENT_DESCRIPTOR = AgentDescriptor(
    name="intent_agent",
    purpose="Interprets user intent and extracts analysis requirements",
    purposes=["intent_extraction", "requirement_analysis"],
    capabilities=["natural_language_understanding", "intent_classification", "parameter_extraction"],
    cost_hint=CostHint.MED,
    allowed_step_types=["agent"],
)

PLAN_AGENT_DESCRIPTOR = AgentDescriptor(
    name="plan_agent",
    purpose="Creates analysis plans based on user requirements",
    purposes=["planning", "analysis_design"],
    capabilities=["planning", "step_sequencing", "resource_estimation"],
    cost_hint=CostHint.MED,
    allowed_step_types=["agent"],
)

PLAN_PROPOSAL_AGENT_DESCRIPTOR = AgentDescriptor(
    name="plan_proposal_agent",
    purpose="Generates formal plan proposals for human approval",
    purposes=["plan_proposal", "human_approval"],
    capabilities=["plan_generation", "approval_workflow", "cost_estimation"],
    cost_hint=CostHint.LOW,
    allowed_step_types=["agent", "plan_proposal"],
)

PLANNING_AGENT_DESCRIPTOR = AgentDescriptor(
    name="planning_agent",
    purpose="High-level planning agent for complex analysis workflows",
    purposes=["strategic_planning", "workflow_design"],
    capabilities=["planning", "workflow_orchestration", "resource_allocation"],
    cost_hint=CostHint.MED,
    allowed_step_types=["agent"],
)

SUFFICIENCY_EVALUATOR_DESCRIPTOR = AgentDescriptor(
    name="sufficiency_evaluator",
    purpose="Evaluates data sufficiency for analysis tasks",
    purposes=["data_evaluation", "quality_assessment"],
    capabilities=["data_quality", "sufficiency_analysis", "confidence_scoring"],
    cost_hint=CostHint.LOW,
    allowed_step_types=["agent"],
)


# ==============================
# Descriptor Lookup Maps
# ==============================

TOOL_DESCRIPTORS = {
    "data_reader": DATA_READER_DESCRIPTOR,
    "build_chart_spec": BUILD_CHART_SPEC_DESCRIPTOR,
    "recommend_chart": RECOMMEND_CHART_DESCRIPTOR,
    "detect_anomalies": DETECT_ANOMALIES_DESCRIPTOR,
    "driver_analysis": DRIVER_ANALYSIS_DESCRIPTOR,
    "assemble_insight_card": ASSEMBLE_INSIGHT_CARD_DESCRIPTOR,
    "assemble_decision_packet": ASSEMBLE_DECISION_PACKET_DESCRIPTOR,
    "assemble_evidence_bundle": ASSEMBLE_EVIDENCE_BUNDLE_DESCRIPTOR,
    "build_reasoning_narrative": BUILD_REASONING_NARRATIVE_DESCRIPTOR,
    "compute_business_metrics": COMPUTE_BUSINESS_METRICS_DESCRIPTOR,
    "assemble_business_report": ASSEMBLE_BUSINESS_REPORT_DESCRIPTOR,
    "export_pdf": EXPORT_PDF_DESCRIPTOR,
    "render_business_report_html": RENDER_BUSINESS_REPORT_HTML_DESCRIPTOR,
    "render_decision_packet_html": RENDER_DECISION_PACKET_HTML_DESCRIPTOR,
    "hypothesis_test_data_outage": HYPOTHESIS_TEST_DATA_OUTAGE_DESCRIPTOR,
    "hypothesis_test_seasonality": HYPOTHESIS_TEST_SEASONALITY_DESCRIPTOR,
}

AGENT_DESCRIPTORS = {
    "dashboard_agent": DASHBOARD_AGENT_DESCRIPTOR,
    "intent_agent": INTENT_AGENT_DESCRIPTOR,
    "plan_agent": PLAN_AGENT_DESCRIPTOR,
    "plan_proposal_agent": PLAN_PROPOSAL_AGENT_DESCRIPTOR,
    "planning_agent": PLANNING_AGENT_DESCRIPTOR,
    "sufficiency_evaluator": SUFFICIENCY_EVALUATOR_DESCRIPTOR,
}
