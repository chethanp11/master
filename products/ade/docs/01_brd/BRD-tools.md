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

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-TOOL-001 | Tools MUST NOT call LLMs directly | Derived from: INT-TOOL-002 | P0 | 2026-01-13 | V1.1 |
| BRD-TOOL-002 | Tools MUST produce deterministic outputs | Derived from: INT-TOOL-003 | P0 | 2026-01-13 | V1.1 |
| BRD-TOOL-003 | Same inputs MUST produce same outputs | Derived from: INT-TOOL-004 | P0 | 2026-01-13 | V1.1 |
| BRD-TOOL-004 | Tools MUST NOT have external dependencies | Derived from: INT-TOOL-001 | P0 | 2026-01-13 | V1.1 |
| BRD-TOOL-005 | Tools MUST produce evidence items | Derived from: INT-TOOL-005 | P0 | 2026-01-13 | V1.1 |

---

## 3. Data Processing Requirements

### 3.1 Data Reading

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-DATA-001 | System MUST read CSV datasets | Derived from: INT-DATA-001 | P0 | 2026-01-13 | V1.1 |
| BRD-DATA-002 | System MUST extract column metadata | Derived from: INT-DATA-002 | P0 | 2026-01-13 | V1.1 |
| BRD-DATA-003 | System MUST extract row data | Derived from: INT-DATA-003 | P0 | 2026-01-13 | V1.1 |
| BRD-DATA-004 | System MUST infer field types (x, y, category) | Derived from: INT-DATA-004 | P1 | 2026-01-13 | V1.1 |
| BRD-DATA-005 | System MUST handle UTF-8 encoding | Derived from: INT-DATA-005 | P0 | 2026-01-13 | V1.1 |
| BRD-DATA-006 | System MUST handle quoted CSV fields | Derived from: INT-DATA-006 | P1 | 2026-01-13 | V1.1 |

### 3.2 Metric Computation

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-METRIC-001 | System MUST compute aggregated metrics | Derived from: INT-ANAL-001 | P0 | 2026-01-13 | V1.1 |
| BRD-METRIC-002 | System MUST support multiple metric types | Derived from: INT-ANAL-005 | P0 | 2026-01-13 | V1.1 |
| BRD-METRIC-003 | System MUST produce evidence items | Derived from: INT-TOOL-005 | P0 | 2026-01-13 | V1.1 |
| BRD-METRIC-004 | System MUST respect metric_focus parameter | Derived from: INT-UI-002 | P1 | 2026-01-13 | V1.1 |

**Metric Types**: mean, sum, median, growth_rate, anomalies

---

## 4. Analysis Requirements

### 4.1 Anomaly Detection

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-ANOM-001 | System MUST detect statistical anomalies | Derived from: INT-ANAL-001 | P0 | 2026-01-13 | V1.1 |
| BRD-ANOM-002 | System MUST use z-score analysis | Derived from: INT-ANAL-002 | P0 | 2026-01-13 | V1.1 |
| BRD-ANOM-003 | System MUST rank anomalies by severity | Derived from: INT-ANAL-003 | P1 | 2026-01-13 | V1.1 |
| BRD-ANOM-004 | System MUST explain anomaly reasons | Derived from: INT-ANAL-004 | P1 | 2026-01-13 | V1.1 |
| BRD-ANOM-005 | System MUST produce evidence items | Derived from: INT-TOOL-005 | P0 | 2026-01-13 | V1.1 |

### 4.2 Hypothesis Testing

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-HYP-001 | System MUST support data outage hypothesis | Derived from: INT-ANAL-005 | P1 | 2026-01-13 | V1.1 |
| BRD-HYP-002 | System MUST support seasonality hypothesis | Derived from: INT-ANAL-005 | P1 | 2026-01-13 | V1.1 |
| BRD-HYP-003 | Hypothesis tests MUST be toggleable | Derived from: INT-ANAL-006 | P0 | 2026-01-13 | V1.1 |
| BRD-HYP-004 | Tests MUST return status (confirmed/rejected/skipped) | Derived from: INT-ANAL-005 | P0 | 2026-01-13 | V1.1 |
| BRD-HYP-005 | Tests MUST provide reasoning | Derived from: INT-ANAL-005 | P1 | 2026-01-13 | V1.1 |
| BRD-HYP-006 | Tests MUST produce evidence items | Derived from: INT-TOOL-005 | P0 | 2026-01-13 | V1.1 |

### 4.3 Driver Analysis

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-DRIVER-001 | System SHOULD identify key metric drivers | Derived from: INT-ANAL-007 | P1 | 2026-01-13 | V1.1 |
| BRD-DRIVER-002 | Drivers SHOULD be ranked by contribution | Derived from: INT-ANAL-007 | P2 | 2026-01-13 | V1.1 |

---

## 5. Visualization Requirements

### 5.1 Chart Specification

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-CHART-001 | System MUST build chart specifications | Derived from: INT-VIS-001 | P0 | 2026-01-13 | V1.1 |
| BRD-CHART-002 | System MUST support bar charts | Derived from: INT-VIS-002, INT-OBJ-006 | P0 | 2026-01-13 | V1.1 |
| BRD-CHART-003 | System MUST support line charts | Derived from: INT-VIS-002, INT-OBJ-006 | P0 | 2026-01-13 | V1.1 |
| BRD-CHART-004 | System MUST support area charts | Derived from: INT-VIS-002, INT-OBJ-006 | P1 | 2026-01-13 | V1.1 |
| BRD-CHART-005 | System MUST support scatter charts | Derived from: INT-VIS-002, INT-OBJ-006 | P1 | 2026-01-13 | V1.1 |
| BRD-CHART-006 | System MUST use fallback type when needed | Derived from: INT-VIS-002 | P1 | 2026-01-13 | V1.1 |
| BRD-CHART-007 | Specs MUST be Vega-Lite compatible | Derived from: INT-VIS-004 | P0 | 2026-01-13 | V1.1 |

### 5.2 Chart Recommendation

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-REC-001 | System SHOULD recommend appropriate chart type | Derived from: INT-VIS-003 | P2 | 2026-01-13 | V1.1 |
| BRD-REC-002 | Recommendations SHOULD consider data shape | Derived from: INT-VIS-003 | P2 | 2026-01-13 | V1.1 |

---

## 6. Report Assembly Requirements

### 6.1 Decision Packet

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-PKT-001 | System MUST assemble decision packets | Derived from: INT-ASM-001 | P0 | 2026-01-13 | V1.1 |
| BRD-PKT-002 | Packets MUST include question | Derived from: INT-DP-001 | P0 | 2026-01-13 | V1.1 |
| BRD-PKT-003 | Packets MUST include decision summary | Derived from: INT-DP-002 | P0 | 2026-01-13 | V1.1 |
| BRD-PKT-004 | Packets MUST include confidence level | Derived from: INT-DP-003 | P0 | 2026-01-13 | V1.1 |
| BRD-PKT-005 | Packets MUST include assumptions | Derived from: INT-DP-004 | P0 | 2026-01-13 | V1.1 |
| BRD-PKT-006 | Packets MUST include limitations | Derived from: INT-DP-005 | P0 | 2026-01-13 | V1.1 |
| BRD-PKT-007 | Packets MUST include evidence references | Derived from: INT-DP-006, INT-AUDIT-001 | P0 | 2026-01-13 | V1.1 |
| BRD-PKT-008 | Packets MUST include trace references | Derived from: INT-DP-007, INT-TRACE-001 | P0 | 2026-01-13 | V1.1 |

### 6.2 Business Report

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-RPT-001 | System MUST assemble business reports | Derived from: INT-ASM-002 | P0 | 2026-01-13 | V1.1 |
| BRD-RPT-002 | Reports MUST include executive summary | Derived from: INT-BR-004 | P0 | 2026-01-13 | V1.1 |
| BRD-RPT-003 | Reports MUST include key findings | Derived from: INT-BR-005 | P0 | 2026-01-13 | V1.1 |
| BRD-RPT-004 | Reports MUST include visualizations | Derived from: INT-BR-006 | P0 | 2026-01-13 | V1.1 |
| BRD-RPT-005 | Reports MUST include anomalies | Derived from: INT-BR-007 | P1 | 2026-01-13 | V1.1 |
| BRD-RPT-006 | Reports MUST include recommendations | Derived from: INT-OUT-007, INT-NARR-004 | P1 | 2026-01-13 | V1.1 |
| BRD-RPT-007 | Reports MUST include appendix | Derived from: INT-BR-008 | P1 | 2026-01-13 | V1.1 |

### 6.3 Evidence Bundle

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-EVID-001 | System MUST bundle evidence items | Derived from: INT-ASM-003 | P0 | 2026-01-13 | V1.1 |
| BRD-EVID-002 | Bundles MUST preserve provenance | Derived from: INT-EV-004 | P0 | 2026-01-13 | V1.1 |
| BRD-EVID-003 | Bundles SHOULD deduplicate items | Derived from: INT-ASM-003 | P2 | 2026-01-13 | V1.1 |

### 6.4 Assembly Validation

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-ASM-004 | Assemblers MUST include all required sections in outputs | Derived from: INT-ASM-004 | P0 | 2026-01-13 | V1.1 |
| BRD-ASM-005 | Assemblers MUST validate outputs against schemas | Derived from: INT-ASM-005 | P0 | 2026-01-13 | V1.1 |

---

## 7. Rendering Requirements

### 7.1 HTML Rendering

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-HTML-001 | System MUST render business reports as HTML | Derived from: INT-REND-001, INT-OUT-001 | P0 | 2026-01-13 | V1.1 |
| BRD-HTML-002 | System MUST render decision packets as HTML | Derived from: INT-REND-001, INT-OUT-010 | P0 | 2026-01-13 | V1.1 |
| BRD-HTML-003 | HTML MUST be valid HTML5 | Derived from: INT-REND-002 | P0 | 2026-01-13 | V1.1 |
| BRD-HTML-004 | HTML SHOULD be self-contained | Derived from: INT-REND-003 | P1 | 2026-01-13 | V1.1 |

### 7.2 Export

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-EXP-001 | System MAY export to PDF | Derived from: INT-REND-004 | P2 | 2026-01-13 | V1.1 |
| BRD-EXP-003 | Exports MUST be written to staging/output/ | Derived from: INT-OUTLOC-001 | P1 | 2026-01-13 | V1.1 |

---

## Cross-References

- **Techspec**: [TOOL-tools.md](../02_techspec/TOOL-tools.md)
- **System Design**: [agents-and-tools.md](../04_systemdesign/agents-and-tools.md)
