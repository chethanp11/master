# ADE Agents and Tools

> **Document**: System Design — Agents and Tools  
> **Version**: 1.1.0  
> **Last Updated**: 2026-01-21

---

## 1. Overview

ADE components are divided into:
- **Agents**: Provide reasoning roles (interpret, plan, evaluate)
- **Tools**: Perform factual computation (no reasoning)

All components have **descriptors** in `products/ade/descriptors.py` that provide metadata for selection, governance, and cost estimation.

---

## 2. Agents

### 2.1 intent_agent

| Attribute | Value |
|-----------|-------|
| **Purpose** | Interprets user intent and extracts analysis requirements |
| **Capabilities** | natural_language_understanding, intent_classification, parameter_extraction |
| **Cost Hint** | MED |
| **Location** | `products/ade/agents/intent_agent.py` |

**Output Schema** (`IntentFrame`):
```python
stage: str  # "interpret"
intent_summary: str
inferred_entities: List[str]
inferred_metrics: List[str]
inferred_time_window: Optional[str]
requested_outputs: List[str]
confidence_score: float
confidence_label: str  # "low", "medium", "high"
blocking_required: bool
blocking_questions: List[str]
blocking_question: Optional[str]
```

**Evidence**:
- `products/ade/agents/intent_agent.py` (`IntentAgent.run`)
- `products/ade/schemas/intent_frame.py` (`IntentFrame.stage`)

---

### 2.2 plan_agent

| Attribute | Value |
|-----------|-------|
| **Purpose** | Creates analysis plans based on user requirements |
| **Capabilities** | planning, step_sequencing, resource_estimation |
| **Cost Hint** | MED |
| **Location** | `products/ade/agents/plan_agent.py` |

**Output Schema** (`PlanSpec`):
- Deterministic plan specification
- Tool flags for conditional execution

**Evidence**:
- `products/ade/agents/plan_agent.py` (`PlanAgent.run`, `tool_recommendations`)
- `products/ade/schemas/plan_spec.py` (`ToolRecommendation`, `PlanSpec.tool_recommendations`)

---

### 2.3 plan_proposal_agent

| Attribute | Value |
|-----------|-------|
| **Purpose** | Generates formal plan proposals for human approval |
| **Capabilities** | plan_generation, approval_workflow, cost_estimation |
| **Cost Hint** | LOW |
| **Step Types** | agent, plan_proposal |
| **Location** | `products/ade/agents/plan_proposal_agent.py` |

**Output**: `PlanProposal` for user approval/rejection.

Key metadata (stored in `estimated_cost.details`):
- `objective`, `expected_evidence`, `assumptions`, `risks`
- `tool_recommendations` (optional, advisory)
- `replan_change_summary`, `replan_rationale`

**Evidence**:
- `products/ade/agents/plan_proposal_agent.py` (`PlanProposalAgent.run`, `estimated_cost.details`)

---

### 2.4 planning_agent

| Attribute | Value |
|-----------|-------|
| **Purpose** | High-level planning for complex analysis workflows |
| **Capabilities** | planning, workflow_orchestration, resource_allocation |
| **Cost Hint** | MED |
| **Location** | `products/ade/agents/planning_agent.py` |

**Used in**: visualization flow for intent interpretation and replanning after rejection.

**Evidence**:
- `products/ade/agents/planning_agent.py` (`PlanningAgent.run`, `replan_change_summary`)

---

### 2.5 sufficiency_evaluator

| Attribute | Value |
|-----------|-------|
| **Purpose** | Evaluates data sufficiency for analysis tasks |
| **Capabilities** | data_quality, sufficiency_analysis, confidence_scoring |
| **Cost Hint** | LOW |
| **Location** | `products/ade/agents/sufficiency_evaluator.py` |

**Output**:
```python
stage: str  # "critique"
confidence_level: str  # "high", "medium", "low"
downgrade_reasons: List[str]
sufficiency_state: Dict[str, List[str]]  # known/unknown/blocked
```

**Evidence**:
- `products/ade/agents/sufficiency_evaluator.py` (`SufficiencyOutput`)

---

### 2.6 critic_evaluator

| Attribute | Value |
|-----------|-------|
| **Purpose** | Evaluates critique requirements before final outputs |
| **Capabilities** | critique, evidence_review, confidence_adjustment |
| **Cost Hint** | LOW |
| **Location** | `products/ade/agents/critic_evaluator.py` |

**Output**:
```python
stage: str  # "critique"
evidence_gaps: List[str]
revised_confidence: str
downgrade_reason: Optional[str]
blocking_required: bool
stop_reason: str
recommended_next_action: str
```

**Evidence**:
- `products/ade/agents/critic_evaluator.py` (`CritiqueOutput`)

---

### 2.7 dashboard_agent

| Attribute | Value |
|-----------|-------|
| **Purpose** | Coordinates dashboard generation and visualization tasks |
| **Capabilities** | orchestration, visualization, coordination |
| **Cost Hint** | MED |
| **Location** | `products/ade/agents/dashboard_agent.py` |

**Output**:
```python
message: str
insight: str
anomaly_summary: str
anomaly_interpretation: str
anomaly_count: int
```

**Evidence**:
- `products/ade/agents/dashboard_agent.py` (`DashboardOutput`)

---

## 3. Tools

### 3.1 Data Tools

#### data_reader

| Attribute | Value |
|-----------|-------|
| **Description** | Reads and parses CSV datasets |
| **Capabilities** | data_reading, csv_parsing, data_extraction |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | MED |
| **Cost** | LOW |
| **Location** | `products/ade/tools/data_reader.py` |

**Input**:
```python
dataset: str  # Dataset name (file name)
```

**Output**:
```python
columns: List[str]
rows: List[List[Any]]
series: List[Dict[str, Any]]
data: Dict[str, Any]
x_field: Optional[str]
y_field: Optional[str]
category_field: Optional[str]
row_count: int
has_time: bool
input_path: str
```

**Evidence**:
- `products/ade/tools/data_reader.py` (`DataReaderTool.run`)

---

#### context_pack_builder

| Attribute | Value |
|-----------|-------|
| **Description** | Builds dataset profile and coverage context pack |
| **Capabilities** | context_pack, dataset_profile, coverage |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | LOW |
| **Cost** | LOW |
| **Location** | `products/ade/tools/context_pack_builder.py` |

**Output**:
```python
context_pack: ContextPack
```

**Evidence**:
- `products/ade/tools/context_pack_builder.py` (`ContextPackBuilderTool`)

---

#### compute_business_metrics

| Attribute | Value |
|-----------|-------|
| **Description** | Computes business metrics including trends, movers, and statistics |
| **Capabilities** | computation, business_metrics, statistical_analysis |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | MED |
| **Cost** | LOW |
| **Location** | `products/ade/tools/compute_business_metrics.py` |

**Input**:
```python
dataset_id: str
columns: List[str]
rows: List[Dict]
metric_focus: str
chart_type: str
include_hypothesis_checks: bool
```

**Output**:
```python
totals: List[Dict[str, Any]]
top_movers_abs: List[Dict[str, Any]]
top_movers_pct: List[Dict[str, Any]]
anomalies: List[Dict[str, Any]]
evidence_items: List[EvidenceItem]
```

---

### 3.2 Analysis Tools

#### detect_anomalies

| Attribute | Value |
|-----------|-------|
| **Description** | Detects statistical anomalies using z-score analysis |
| **Capabilities** | anomaly_detection, statistical_analysis, time_series |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | MED |
| **Cost** | LOW |
| **Location** | `products/ade/tools/detect_anomalies.py` |

**Input**:
```python
series: Dict
data: Dict
min_points: int = 3
enabled: bool = True
```

**Output**:
```python
anomalies: List[AnomalyRow]  # sorted by severity_score descending
evidence_items: List[EvidenceItem]
```

**Severity Ranking (TS-TOOL-ANOM-002)**:
- Each `Anomaly` has `severity_score: float = abs(zscore)`
- Anomalies are sorted by `severity_score` descending (highest severity first)
- Negative z-scores produce positive severity scores for proper ranking

**Evidence**:
- `products/ade/tools/detect_anomalies.py` (`Anomaly.severity_score`, sorted by `-severity_score`)

---

#### driver_analysis

| Attribute | Value |
|-----------|-------|
| **Description** | Identifies key factors affecting metrics |
| **Capabilities** | driver_analysis, statistical_analysis, root_cause |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | MED |
| **Cost** | MED |
| **Location** | `products/ade/tools/driver_analysis.py` |

---

#### hypothesis_test_data_outage

| Attribute | Value |
|-----------|-------|
| **Description** | Tests hypothesis of data outage affecting metrics |
| **Capabilities** | hypothesis_testing, data_quality, anomaly_detection |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | MED |
| **Cost** | LOW |
| **Location** | `products/ade/tools/hypothesis_test_data_outage.py` |

**Output**:
```python
status: str  # "confirmed", "rejected", "skipped"
reasoning: str
evidence_items: List[EvidenceItem]
```

---

#### hypothesis_test_seasonality

| Attribute | Value |
|-----------|-------|
| **Description** | Tests hypothesis of seasonality patterns in data |
| **Capabilities** | hypothesis_testing, time_series, pattern_detection |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | MED |
| **Cost** | LOW |
| **Location** | `products/ade/tools/hypothesis_test_seasonality.py` |

**Output**:
```python
status: str  # "confirmed", "rejected", "skipped"
reasoning: str
evidence_items: List[EvidenceItem]
```

---

### 3.3 Visualization Tools

#### build_chart_spec

| Attribute | Value |
|-----------|-------|
| **Description** | Builds chart specification from data |
| **Capabilities** | visualization, chart_building, data_presentation |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | LOW |
| **Cost** | LOW |
| **Location** | `products/ade/tools/build_chart_spec.py` |

**Input**:
```python
chart_type: str
fallback_chart_type: str
title: str
x: str
y: str
series: str
data: Dict
evidence_ref: Dict
```

**Output**:
```python
chart_spec: Dict  # Vega-Lite compatible spec
```

---

#### recommend_chart

| Attribute | Value |
|-----------|-------|
| **Description** | Recommends best chart type for dataset structure |
| **Capabilities** | visualization, recommendation, data_analysis |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | LOW |
| **Cost** | LOW |
| **Location** | `products/ade/tools/recommend_chart.py` |

---

### 3.4 Assembly Tools

#### assemble_decision_packet

| Attribute | Value |
|-----------|-------|
| **Description** | Assembles decision packet with evidence and recommendations |
| **Capabilities** | decision_support, report_building, evidence_aggregation |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | MED |
| **Cost** | LOW |
| **Location** | `products/ade/tools/assemble_decision_packet.py` |

**Output**: `DecisionPacket` structure.

---

#### assemble_business_report

| Attribute | Value |
|-----------|-------|
| **Description** | Assembles comprehensive business report |
| **Capabilities** | report_building, business_intelligence, summarization |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | MED |
| **Cost** | LOW |
| **Location** | `products/ade/tools/assemble_business_report.py` |

**Output**: `BusinessReport` structure.

---

#### assemble_evidence_bundle

| Attribute | Value |
|-----------|-------|
| **Description** | Bundles evidence items into cohesive package |
| **Capabilities** | evidence_aggregation, data_packaging, provenance_tracking |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | MED |
| **Cost** | LOW |
| **Location** | `products/ade/tools/assemble_evidence_bundle.py` |

---

#### assemble_insight_card

| Attribute | Value |
|-----------|-------|
| **Description** | Creates InsightCard objects from metrics and evidence |
| **Capabilities** | insight_generation, report_building, summarization |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | LOW |
| **Cost** | LOW |
| **Location** | `products/ade/tools/assemble_insight_card.py` |

---

### 3.5 Rendering Tools

#### render_business_report_html

| Attribute | Value |
|-----------|-------|
| **Description** | Renders business reports as HTML |
| **Capabilities** | rendering, html_generation, visualization |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | LOW |
| **Cost** | LOW |
| **Location** | `products/ade/tools/render_business_report_html.py` |

**Validation Gate**: rendering fails on schema validation errors.

**Evidence**:
- `products/ade/tools/render_business_report_html.py` (`RenderBusinessReportInput.model_validate`)

---

#### render_decision_packet_html

| Attribute | Value |
|-----------|-------|
| **Description** | Renders decision packets as HTML |
| **Capabilities** | rendering, html_generation, visualization |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | LOW |
| **Cost** | LOW |
| **Location** | `products/ade/tools/render_decision_packet_html.py` |

**Validation Gate**: rendering fails on schema validation errors.

**Evidence**:
- `products/ade/tools/render_decision_packet_html.py` (`RenderDecisionPacketInput.model_validate`)

---

#### export_pdf

| Attribute | Value |
|-----------|-------|
| **Description** | Exports reports to PDF format |
| **Capabilities** | export, pdf_generation, document_output |
| **Read Only** | No |
| **Side Effect** | Yes |
| **Sensitivity** | LOW |
| **Cost** | MED |
| **Location** | `products/ade/tools/export_pdf.py` |

**Output Files**:
- `ade.pdf`
- `ade.html`
- `ade_stub.json`

---

### 3.6 Narrative Tools

#### build_reasoning_narrative

| Attribute | Value |
|-----------|-------|
| **Description** | Constructs narrative explanation of analysis reasoning |
| **Capabilities** | narrative_generation, explanation, reasoning_chain |
| **Read Only** | Yes |
| **Side Effect** | No |
| **Sensitivity** | LOW |
| **Cost** | LOW |
| **Location** | `products/ade/tools/build_reasoning_narrative.py` |

---

## 4. Descriptor Lookup

All descriptors are exported via lookup maps in `descriptors.py`:

```python
TOOL_DESCRIPTORS = {
    "data_reader": DATA_READER_DESCRIPTOR,
    "build_chart_spec": BUILD_CHART_SPEC_DESCRIPTOR,
    # ... (registered tools)
}

AGENT_DESCRIPTORS = {
    "dashboard_agent": DASHBOARD_AGENT_DESCRIPTOR,
    "intent_agent": INTENT_AGENT_DESCRIPTOR,
    "critic_evaluator": CRITIC_EVALUATOR_DESCRIPTOR,
}
```

---

## 5. Tool Utilities (Non-registered)

These helpers are used internally but are not registered tools.

| Utility | Purpose | Location |
|---------|---------|----------|
| `export_rendering` | PDF rendering utilities for insight cards | `products/ade/tools/export_rendering.py` |
| `evidence_utils` | Evidence hashing and ID helpers | `products/ade/tools/evidence_utils.py` |

---

## 6. V1.2 Utility Modules

### 6.1 Narrative Builder (TS-AGENT-NARR-005)

Location: `products/ade/utils/narrative.py`

| Function | Purpose |
|----------|----------|
| `DecisionRecord` | Decision record class with record_id, step_id, decision, rationale, confidence |
| `build_explanation(decision_records)` | Generates user-facing text from decision records |
| `build_explanation_from_dicts(records)` | Converts dict records to DecisionRecord objects |
| `get_decision_records_summary()` | Returns traceability summary with record IDs |

**Evidence**:
- `products/ade/utils/narrative.py` (`DecisionRecord`, `build_explanation`)

### 6.2 Advisory Labeling (TS-BRD-DAB-001..005)

Location: `products/ade/utils/advisory.py`

| Function | Purpose |
|----------|----------|
| `ADVISORY_LABELS` | Dict mapping confidence levels to advisory labels |
| `get_advisory_label(confidence)` | Returns non-decisional label per confidence |
| `apply_advisory_language(text)` | Replaces decisional terms (must→should consider) |
| `format_advisory_header(title, confidence)` | Adds advisory labeling to headers |
| `format_recommendation_disclaimer()` | Generates appropriate disclaimers |
| `format_findings_preamble()` | Presents findings as observations |
| `validate_advisory_language(text)` | Detects inappropriate decisional terms |

**Evidence**:
- `products/ade/utils/advisory.py` (`get_advisory_label`, `apply_advisory_language`, `ADVISORY_LABELS`)

### 6.3 Semantic Validation (TS-SEM-VALIDATE-008, 009)

Location: `products/ade/utils/semantic_validation.py`

| Function | Purpose |
|----------|----------|
| `_validate_dataset_ref(dataset, available)` | Returns True/False for dataset validity |
| `_validate_metric_ref(metric, schema)` | Returns True/False for metric validity |
| `validate_dataset()` | Returns ValidationResult with ASK_USER outcome if invalid |
| `validate_metric()` | Returns ValidationResult with ASK_USER outcome if invalid |
| `validate_semantic_envelope()` | Validates both dataset and metric with context |

**Evidence**:
- `products/ade/utils/semantic_validation.py` (`validate_dataset`, `validate_metric`, `ValidationResult`)

### 6.4 Validation Utilities (TS-BRD-VAL-001..003, TS-BRD-QUAL-001..004)

Location: `products/ade/utils/validation.py`

| Function | Purpose |
|----------|----------|
| `ValidationResult` | Model for structured validation outcomes |
| `format_pydantic_errors()` | Produces clear field paths per TS-BRD-VAL-002 |
| `validate_output_schema()` | Validates data against Pydantic schemas |
| `ValidationGate` | Class that blocks rendering when validation fails |
| `validate_executive_summary()` | Checks for non-empty, substantive summaries |
| `validate_findings()` | Verifies evidence_refs present on all findings |
| `validate_recommendations()` | Ensures recommendations are not too generic |
| `validate_visuals()` | Checks visual titles and required data |
| `validate_report_quality()` | Runs all checks and returns combined result |

**Evidence**:
- `products/ade/utils/validation.py` (`ValidationGate`, `validate_report_quality`)

### 6.5 Output Directory Utilities (TS-IO-OUT-007)

Location: `products/ade/utils/output.py`

| Function | Purpose |
|----------|----------|
| `ensure_output_dir()` | Creates output directories with parents if needed |
| `get_output_path()` | Returns path with optional directory creation |
| `default_output_dir()` | Returns standard output directory location |

**Evidence**:
- `products/ade/utils/output.py` (`ensure_output_dir`, `get_output_path`)

---

## Cross-References

- [architecture.md](architecture.md) — Component overview
- [flows.md](flows.md) — Flow definitions
- [schemas.md](schemas.md) — Data schemas
