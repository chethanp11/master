# ADE Tool Business Requirements

> **Document**: Business Requirements — Tools  
> **Version**: 1.0.0

---

## 1. Tool Overview

Tools perform factual computation in ADE workflows:

| Category | Tools |
|----------|-------|
| **Data** | data_reader, compute_business_metrics |
| **Analysis** | detect_anomalies, driver_analysis, hypothesis_test_* |
| **Visualization** | build_chart_spec, recommend_chart |
| **Assembly** | assemble_decision_packet, assemble_business_report, assemble_evidence_bundle, assemble_insight_card |
| **Rendering** | render_business_report_html, render_decision_packet_html, export_pdf |
| **Narrative** | build_reasoning_narrative |

---

## 2. Determinism Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-TOOL-001 | Tools MUST NOT call LLMs directly | P0 |
| BRD-TOOL-002 | Tools MUST produce deterministic outputs | P0 |
| BRD-TOOL-003 | Same inputs MUST produce same outputs | P0 |
| BRD-TOOL-004 | Tools MUST NOT have external dependencies | P0 |

---

## 3. Data Processing Requirements

### 3.1 Data Reading

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-DATA-001 | System MUST read CSV datasets | P0 |
| BRD-DATA-002 | System MUST extract column metadata | P0 |
| BRD-DATA-003 | System MUST extract row data | P0 |
| BRD-DATA-004 | System MUST infer field types (x, y, category) | P1 |
| BRD-DATA-005 | System MUST handle UTF-8 encoding | P0 |
| BRD-DATA-006 | System MUST handle quoted CSV fields | P1 |

### 3.2 Metric Computation

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-METRIC-001 | System MUST compute aggregated metrics | P0 |
| BRD-METRIC-002 | System MUST support multiple metric types | P0 |
| BRD-METRIC-003 | System MUST produce evidence items | P0 |
| BRD-METRIC-004 | System MUST respect metric_focus parameter | P1 |

**Metric Types**: mean, sum, median, growth_rate, anomalies

---

## 4. Analysis Requirements

### 4.1 Anomaly Detection

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-ANOM-001 | System MUST detect statistical anomalies | P0 |
| BRD-ANOM-002 | System MUST use z-score analysis | P0 |
| BRD-ANOM-003 | System MUST rank anomalies by severity | P1 |
| BRD-ANOM-004 | System MUST explain anomaly reasons | P1 |
| BRD-ANOM-005 | System MUST produce evidence items | P0 |

### 4.2 Hypothesis Testing

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-HYP-001 | System MUST support data outage hypothesis | P1 |
| BRD-HYP-002 | System MUST support seasonality hypothesis | P1 |
| BRD-HYP-003 | Hypothesis tests MUST be toggleable | P0 |
| BRD-HYP-004 | Tests MUST return status (confirmed/rejected/skipped) | P0 |
| BRD-HYP-005 | Tests MUST provide reasoning | P1 |
| BRD-HYP-006 | Tests MUST produce evidence items | P0 |

### 4.3 Driver Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-DRIVER-001 | System SHOULD identify key metric drivers | P1 |
| BRD-DRIVER-002 | Drivers SHOULD be ranked by contribution | P2 |

---

## 5. Visualization Requirements

### 5.1 Chart Specification

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-CHART-001 | System MUST build chart specifications | P0 |
| BRD-CHART-002 | System MUST support bar charts | P0 |
| BRD-CHART-003 | System MUST support line charts | P0 |
| BRD-CHART-004 | System MUST support area charts | P1 |
| BRD-CHART-005 | System MUST support scatter charts | P1 |
| BRD-CHART-006 | System MUST use fallback type when needed | P1 |
| BRD-CHART-007 | Specs MUST be Vega-Lite compatible | P0 |

### 5.2 Chart Recommendation

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-REC-001 | System SHOULD recommend appropriate chart type | P2 |
| BRD-REC-002 | Recommendations SHOULD consider data shape | P2 |

---

## 6. Report Assembly Requirements

### 6.1 Decision Packet

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-PKT-001 | System MUST assemble decision packets | P0 |
| BRD-PKT-002 | Packets MUST include question | P0 |
| BRD-PKT-003 | Packets MUST include decision summary | P0 |
| BRD-PKT-004 | Packets MUST include confidence level | P0 |
| BRD-PKT-005 | Packets MUST include assumptions | P0 |
| BRD-PKT-006 | Packets MUST include limitations | P0 |
| BRD-PKT-007 | Packets MUST include evidence references | P0 |
| BRD-PKT-008 | Packets MUST include trace references | P0 |

### 6.2 Business Report

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-RPT-001 | System MUST assemble business reports | P0 |
| BRD-RPT-002 | Reports MUST include executive summary | P0 |
| BRD-RPT-003 | Reports MUST include key findings | P0 |
| BRD-RPT-004 | Reports MUST include visualizations | P0 |
| BRD-RPT-005 | Reports MUST include anomalies | P1 |
| BRD-RPT-006 | Reports MUST include recommendations | P1 |
| BRD-RPT-007 | Reports MUST include appendix | P1 |

### 6.3 Evidence Bundle

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-EVID-001 | System MUST bundle evidence items | P0 |
| BRD-EVID-002 | Bundles MUST preserve provenance | P0 |
| BRD-EVID-003 | Bundles SHOULD deduplicate items | P2 |

---

## 7. Rendering Requirements

### 7.1 HTML Rendering

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-HTML-001 | System MUST render business reports as HTML | P0 |
| BRD-HTML-002 | System MUST render decision packets as HTML | P0 |
| BRD-HTML-003 | HTML MUST be valid HTML5 | P0 |
| BRD-HTML-004 | HTML SHOULD be self-contained | P1 |

### 7.2 Export

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-EXP-001 | System MAY export to PDF | P2 |
| BRD-EXP-002 | System MAY export to JSON | P2 |
| BRD-EXP-003 | Exports MUST be written to staging/output/ | P1 |

---

## 8. Tool Transparency Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-TRANS-001 | All tools MUST have descriptors | P0 |
| BRD-TRANS-002 | Descriptors MUST declare side effects | P0 |
| BRD-TRANS-003 | Descriptors MUST declare sensitivity | P1 |
| BRD-TRANS-004 | Descriptors MUST declare cost hints | P1 |

---

## Cross-References

- **Techspec**: [TOOL-tools.md](../02_techspec/TOOL-tools.md)
- **System Design**: [agents-and-tools.md](../04_systemdesign/agents-and-tools.md)
