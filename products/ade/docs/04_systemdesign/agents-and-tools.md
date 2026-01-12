# ADE Agents and Tools

> **Document**: System Design — Agents and Tools  
> **Version**: 1.0.0

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
intent_summary: str
inferred_entities: List[str]
inferred_metrics: List[str]
inferred_time_window: Optional[str]
requested_outputs: List[str]
confidence_score: float
confidence_label: str  # "low", "medium", "high"
blocking_required: bool
blocking_questions: List[str]
```

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

---

### 2.4 planning_agent

| Attribute | Value |
|-----------|-------|
| **Purpose** | High-level planning for complex analysis workflows |
| **Capabilities** | planning, workflow_orchestration, resource_allocation |
| **Cost Hint** | MED |
| **Location** | `products/ade/agents/planning_agent.py` |

**Used in**: visualization flow for intent interpretation and replanning after rejection.

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
confidence_level: str  # "high", "medium", "low"
downgrade_reasons: List[str]
```

---

### 2.6 dashboard_agent

| Attribute | Value |
|-----------|-------|
| **Purpose** | Coordinates dashboard generation and visualization tasks |
| **Capabilities** | orchestration, visualization, coordination |
| **Cost Hint** | MED |
| **Location** | `products/ade/agents/dashboard_agent.py` |

**Output**: Narrative summary from dataset summaries.

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
rows: List[Dict]
series: Dict
data: Dict
x_field: str
y_field: str
category_field: str
```

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
totals: Dict
movers: List
anomalies: List
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
anomalies: List[AnomalyRow]
evidence_items: List[EvidenceItem]
```

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
    # ... (16 tools total)
}

AGENT_DESCRIPTORS = {
    "dashboard_agent": DASHBOARD_AGENT_DESCRIPTOR,
    "intent_agent": INTENT_AGENT_DESCRIPTOR,
    # ... (6 agents total)
}
```

---

## Cross-References

- [architecture.md](architecture.md) — Component overview
- [flows.md](flows.md) — Flow definitions
- [schemas.md](schemas.md) — Data schemas
