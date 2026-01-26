# ADE Tool Business Requirements

> **Document**: Business Requirements — Tools  
> **Version**: V1.3  
> **Last Updated**: 2026-01-21

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial release |
| V1.2 | 2026-01-19 | Standardized tables, removed TSD-level detail, and aligned intent traceability |
| V1.3 | 2026-01-21 | Added BRD-TOOL-006...012 (intent-bound tool selection, dynamic discovery, no availability-based selection) |

## 1. Tool Overview

Tools perform factual computation in ADE workflows:
---

## 2. Determinism Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-TOOL-001 | Tools MUST NOT call LLMs directly | INT-TOOL-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TOOL-002 | Tools MUST produce deterministic outputs | INT-TOOL-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TOOL-003 | Same inputs MUST produce same outputs | INT-TOOL-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TOOL-004 | Tools MUST NOT have external dependencies | INT-TOOL-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TOOL-005 | Tools MUST produce evidence items | INT-TOOL-005 | P0 | 2026-01-13 | V1.1 | — |

---

## 2.1 Intent-Bound Tool Selection Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-TOOL-006 | ADE MUST bind tool selection directly to declared intent; analytical tools (anomaly detection, aggregation, visualization) SHALL only be invoked if explicitly justified by the resolved intent and constraints | INT-TOOL-006 | P0 | 2026-01-21 | V1.3 | — |
| BRD-TOOL-007 | ADE MUST reject tool execution based on mere availability; tools SHALL NOT be selected simply because they exist; every tool invocation SHALL map to an intent dimension and be auditable | INT-TOOL-007 | P0 | 2026-01-21 | V1.3 | — |
| BRD-TOOL-008 | ADE MUST never hard-code tool lists; ADE SHALL request eligible tools from the platform per run and use only what is surfaced | INT-TOOL-008 | P0 | 2026-01-21 | V1.3 | — |
| BRD-TOOL-009 | ADE MUST bind tools to intent-derived steps; tools SHALL be invoked because intent demands them, not because they exist or are convenient | INT-TOOL-009 | P0 | 2026-01-21 | V1.3 | — |
| BRD-TOOL-010 | ADE MUST declare tool intent at call time; each tool invocation SHALL specify "why this tool" and "what intent dimension it satisfies" | INT-TOOL-010 | P0 | 2026-01-21 | V1.3 | — |
| BRD-TOOL-011 | ADE MUST fail if no eligible tools exist for the resolved intent; if intent cannot be satisfied with available tools, ADE SHALL stop, explain, and ask user | INT-TOOL-011 | P0 | 2026-01-21 | V1.3 | — |
| BRD-TOOL-012 | ADE MUST never infer permissions; if a tool is not discoverable from the platform, it is not usable; ADE SHALL NOT use fallback logic that bypasses platform discovery | INT-TOOL-012 | P0 | 2026-01-21 | V1.3 | — |

---

## 3. Data Processing Requirements

### 3.1 Data Reading

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-DATA-001 | System MUST read CSV datasets | INT-DATA-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DATA-002 | System MUST extract column metadata | INT-DATA-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DATA-003 | System MUST extract row data | INT-DATA-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DATA-004 | System MUST infer field types for analysis and visualization | INT-DATA-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-DATA-005 | System MUST handle UTF-8 encoding | INT-DATA-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DATA-006 | System MUST handle quoted CSV fields | INT-DATA-006 | P1 | 2026-01-13 | V1.1 | — |

### 3.2 Metric Computation

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-METRIC-001 | System MUST compute aggregated metrics | INT-ANAL-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-METRIC-002 | System MUST support multiple metric types | INT-ANAL-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-METRIC-003 | System MUST produce evidence items | INT-TOOL-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-METRIC-004 | System MUST respect metric_focus parameter | INT-UI-002 | P1 | 2026-01-13 | V1.1 | — |

---

## 4. Analysis Requirements

### 4.1 Anomaly Detection

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-ANOM-001 | System MUST detect statistical anomalies | INT-ANAL-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ANOM-002 | System MUST use z-score analysis | INT-ANAL-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ANOM-003 | System MUST rank anomalies by severity | INT-ANAL-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-ANOM-004 | System MUST explain anomaly reasons | INT-ANAL-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-ANOM-005 | System MUST produce evidence items | INT-TOOL-005 | P0 | 2026-01-13 | V1.1 | — |

### 4.2 Hypothesis Testing

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-HYP-001 | System MUST support data outage hypothesis | INT-ANAL-005 | P1 | 2026-01-13 | V1.1 | — |
| BRD-HYP-002 | System MUST support seasonality hypothesis | INT-ANAL-005 | P1 | 2026-01-13 | V1.1 | — |
| BRD-HYP-003 | Hypothesis tests MUST be toggleable | INT-ANAL-006 | P0 | 2026-01-13 | V1.1 | — |
| BRD-HYP-004 | Tests MUST return a status indicating confirmation, rejection, or skip | INT-ANAL-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-HYP-005 | Tests MUST provide reasoning | INT-ANAL-005 | P1 | 2026-01-13 | V1.1 | — |
| BRD-HYP-006 | Tests MUST produce evidence items | INT-TOOL-005 | P0 | 2026-01-13 | V1.1 | — |

### 4.3 Driver Analysis

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-DRIVER-001 | System SHOULD identify key metric drivers | INT-ANAL-007 | P1 | 2026-01-13 | V1.1 | — |
| BRD-DRIVER-002 | Drivers SHOULD be ranked by contribution | INT-ANAL-007 | P2 | 2026-01-13 | V1.1 | — |

---

## 5. Visualization Requirements

### 5.1 Chart Specification

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-CHART-001 | System MUST build chart specifications | INT-VIS-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CHART-002 | System MUST support bar charts | INT-VIS-002, INT-OBJ-006 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CHART-003 | System MUST support line charts | INT-VIS-002, INT-OBJ-006 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CHART-004 | System MUST support area charts | INT-VIS-002, INT-OBJ-006 | P1 | 2026-01-13 | V1.1 | — |
| BRD-CHART-005 | System MUST support scatter charts | INT-VIS-002, INT-OBJ-006 | P1 | 2026-01-13 | V1.1 | — |
| BRD-CHART-006 | System MUST use fallback type when needed | INT-VIS-002 | P1 | 2026-01-13 | V1.1 | — |
| BRD-CHART-007 | Specs MUST be Vega-Lite compatible | INT-VIS-004 | P0 | 2026-01-13 | V1.1 | — |

### 5.2 Chart Recommendation

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-REC-001 | System SHOULD recommend appropriate chart type | INT-VIS-003 | P2 | 2026-01-13 | V1.1 | — |
| BRD-REC-002 | Recommendations SHOULD consider data shape | INT-VIS-003 | P2 | 2026-01-13 | V1.1 | — |

---

## 6. Report Assembly Requirements

### 6.1 Decision Packet

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-PKT-001 | System MUST assemble decision packets | INT-ASM-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PKT-002 | Packets MUST include question context | INT-DP-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PKT-003 | Packets MUST include decision summary | INT-DP-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PKT-004 | Packets MUST include confidence level | INT-DP-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PKT-005 | Packets MUST include assumptions | INT-DP-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PKT-006 | Packets MUST include limitations | INT-DP-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PKT-007 | Packets MUST include evidence references | INT-DP-006, INT-AUDIT-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PKT-008 | Packets MUST include trace references | INT-DP-007, INT-TRACE-001 | P0 | 2026-01-13 | V1.1 | — |

### 6.2 Business Report

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-RPT-001 | System MUST assemble business reports | INT-ASM-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-RPT-002 | Reports MUST include executive summary | INT-BR-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-RPT-003 | Reports MUST include key findings | INT-BR-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-RPT-004 | Reports MUST include visualizations | INT-BR-006 | P0 | 2026-01-13 | V1.1 | — |
| BRD-RPT-005 | Reports MUST include anomalies | INT-BR-007 | P1 | 2026-01-13 | V1.1 | — |
| BRD-RPT-006 | Reports MUST include recommendations | INT-OUT-007, INT-NARR-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-RPT-007 | Reports MUST include appendix | INT-BR-008 | P1 | 2026-01-13 | V1.1 | — |

### 6.3 Evidence Bundle

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-EVID-001 | System MUST bundle evidence items | INT-ASM-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-EVID-002 | Bundles MUST preserve provenance | INT-EV-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-EVID-003 | Bundles SHOULD deduplicate items | INT-ASM-003 | P2 | 2026-01-13 | V1.1 | — |

### 6.4 Assembly Validation

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-ASM-004 | Assemblers MUST include all required sections in outputs | INT-ASM-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ASM-005 | Assemblers MUST validate outputs against schemas | INT-ASM-005 | P0 | 2026-01-13 | V1.1 | — |

---

## 7. Rendering Requirements

### 7.1 HTML Rendering

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-HTML-001 | System MUST render business reports as HTML | INT-REND-001, INT-OUT-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-HTML-002 | System MUST render decision packets as HTML | INT-REND-001, INT-OUT-010 | P0 | 2026-01-13 | V1.1 | — |
| BRD-HTML-003 | HTML MUST be valid HTML5 | INT-REND-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-HTML-004 | HTML SHOULD be self-contained | INT-REND-003 | P1 | 2026-01-13 | V1.1 | — |

### 7.2 Export

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-EXP-001 | System MAY export to PDF | INT-REND-004 | P2 | 2026-01-13 | V1.1 | — |
| BRD-EXP-003 | Exports MUST be written to the designated output location | INT-OUTLOC-001 | P1 | 2026-01-13 | V1.1 | — |

---

## Appendix: Technical Details (Removed from BRD)

### Tool Inventory (Technical Reference)
| Category | Tools |
|----------|-------|
| **Data** | data_reader, compute_business_metrics |
| **Analysis** | detect_anomalies, driver_analysis, hypothesis_test_* |
| **Visualization** | build_chart_spec, recommend_chart |
| **Assembly** | assemble_decision_packet, assemble_business_report, assemble_evidence_bundle, assemble_insight_card |
| **Rendering** | render_business_report_html, render_decision_packet_html, export_pdf |
| **Narrative** | build_reasoning_narrative |

### Metric Types (Technical Reference)
- mean
- sum
- median
- growth_rate
- anomalies

### Output Location (Technical Reference)
- staging/output/
