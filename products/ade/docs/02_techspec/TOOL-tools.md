# ADE Tool Technical Specification

> **Document**: Technical Specification — Tools  
> **Prefix**: TOOL-*  
> **Version**: 1.2  
> **Last Updated**: 2026-01-20

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added evidence item requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |

---

## 1. General Tool Requirements (TOOL-GEN)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| TOOL-GEN-001 | ADE tools MUST NOT call LLMs directly. | MUST | BRD-TOOL-001 | 1.1 | 13 Jan 2026 | — |
| TOOL-GEN-002 | All tools MUST have descriptors in products/ade/descriptors.py with capabilities, sensitivity, and cost_hint. | MUST | BRD-TOOL-002 | 1.1 | 13 Jan 2026 | — |
| TOOL-GEN-003 | Tools MUST accurately declare side_effect status (only export_pdf has side_effect=True). | MUST | BRD-TOOL-003 | 1.1 | 13 Jan 2026 | — |
| TOOL-GEN-004 | Tools MUST accurately declare read_only status (only export_pdf has read_only=False). | MUST | BRD-TOOL-002 | 1.1 | 13 Jan 2026 | — |
| TOOL-GEN-005 | Tools MUST produce deterministic outputs for the same inputs. | MUST | BRD-TOOL-002, BRD-TOOL-003 | 1.1 | 13 Jan 2026 | — |
| TOOL-GEN-006 | Tools MUST produce evidence items for traceability. | MUST | BRD-TOOL-005 | 1.1 | 13 Jan 2026 | — |

---

## 2. Data Tools (TOOL-DATA)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| TOOL-DATA-001 | data_reader MUST output standardized structure with columns, rows, series, data, x_field, y_field, category_field. | MUST | BRD-DATA-001, BRD-DATA-002, BRD-DATA-003 | 1.1 | 13 Jan 2026 | — |
| TOOL-DATA-002 | data_reader MUST parse CSV files correctly with UTF-8 encoding, headers, quoted fields, and empty values. | MUST | BRD-DATA-005, BRD-DATA-006 | 1.1 | 13 Jan 2026 | — |
| TOOL-DATA-003 | data_reader MUST infer x_field (time columns), y_field (numeric columns), and category_field (categorical columns). | MUST | BRD-DATA-004 | 1.1 | 13 Jan 2026 | — |
| TOOL-DATA-004 | compute_business_metrics MUST output metrics structure with totals, movers, anomalies, and evidence_items. | MUST | BRD-METRIC-001, BRD-METRIC-003 | 1.1 | 13 Jan 2026 | — |
| TOOL-DATA-005 | compute_business_metrics MUST respect metric_focus parameter (mean, sum, median, growth_rate, anomalies). | MUST | BRD-METRIC-002, BRD-METRIC-004 | 1.1 | 13 Jan 2026 | — |

---

## 3. Analysis Tools (TOOL-ANALYSIS)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| TOOL-ANALYSIS-001 | detect_anomalies MUST use z-score analysis with configurable threshold. | MUST | BRD-ANOM-001, BRD-ANOM-002 | 1.1 | 13 Jan 2026 | — |
| TOOL-ANALYSIS-002 | detect_anomalies MUST output AnomalyRow list with evidence_items. | MUST | BRD-ANOM-005 | 1.1 | 13 Jan 2026 | — |
| TOOL-ANALYSIS-003 | Hypothesis tools MUST output standard structure with status (confirmed/rejected/skipped), reasoning, and evidence_items. | MUST | BRD-HYP-004, BRD-HYP-005, BRD-HYP-006 | 1.1 | 13 Jan 2026 | — |
| TOOL-ANALYSIS-004 | hypothesis_test_data_outage MUST check for outage patterns including gaps and sudden value drops. | MUST | BRD-HYP-001 | 1.1 | 13 Jan 2026 | — |
| TOOL-ANALYSIS-005 | hypothesis_test_seasonality MUST check for seasonal signals and identify periodic patterns. | MUST | BRD-HYP-002 | 1.1 | 13 Jan 2026 | — |
| TOOL-ANALYSIS-006 | Hypothesis tools MUST respect enabled parameter and return status="skipped" when disabled. | MUST | BRD-HYP-003 | 1.1 | 13 Jan 2026 | — |
| TOOL-ANALYSIS-007 | driver_analysis SHOULD identify key metric drivers with ranked contribution percentages. | SHOULD | BRD-DRIVER-001, BRD-DRIVER-002 | 1.1 | 13 Jan 2026 | — |

---

## 4. Visualization Tools (TOOL-VIZ)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| TOOL-VIZ-001 | build_chart_spec MUST output Vega-Lite compatible chart specifications. | MUST | BRD-CHART-001, BRD-CHART-007 | 1.1 | 13 Jan 2026 | — |
| TOOL-VIZ-002 | build_chart_spec MUST support bar, line, area, and scatter chart types. | MUST | BRD-CHART-002, BRD-CHART-003, BRD-CHART-004, BRD-CHART-005 | 1.1 | 13 Jan 2026 | — |
| TOOL-VIZ-003 | build_chart_spec MUST use fallback_chart_type (default: bar) when type is incompatible. | MUST | BRD-CHART-006 | 1.1 | 13 Jan 2026 | — |
| TOOL-VIZ-004 | recommend_chart SHOULD suggest appropriate chart type based on data shape using heuristics. | SHOULD | BRD-REC-001, BRD-REC-002 | 1.1 | 13 Jan 2026 | — |

---

## 5. Assembly Tools (TOOL-ASSEMBLE)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| TOOL-ASSEMBLE-001 | assemble_decision_packet MUST output valid DecisionPacket that passes Pydantic validation. | MUST | BRD-PKT-001, BRD-ASM-005 | 1.1 | 13 Jan 2026 | — |
| TOOL-ASSEMBLE-002 | assemble_decision_packet MUST include required sections: sufficiency and hypotheses. | MUST | BRD-ASM-004 | 1.1 | 13 Jan 2026 | — |
| TOOL-ASSEMBLE-003 | assemble_decision_packet MUST include evidence_refs in each section with dataset_id and columns. | MUST | BRD-PKT-007 | 1.1 | 13 Jan 2026 | — |
| TOOL-ASSEMBLE-004 | assemble_decision_packet MUST include trace_refs with step_id references and user_inputs. | MUST | BRD-PKT-008 | 1.1 | 13 Jan 2026 | — |
| TOOL-ASSEMBLE-005 | assemble_business_report MUST output valid BusinessReport that passes Pydantic validation. | MUST | BRD-RPT-001, BRD-ASM-005 | 1.1 | 13 Jan 2026 | — |
| TOOL-ASSEMBLE-006 | assemble_evidence_bundle MUST aggregate evidence items from multiple sources with preserved provenance. | MUST | BRD-EVID-001, BRD-EVID-002 | 1.1 | 13 Jan 2026 | — |
| TOOL-ASSEMBLE-007 | assemble_insight_card SHOULD create InsightCard objects with headline, value, context, and evidence references. | SHOULD | BRD-RPT-003 | 1.1 | 13 Jan 2026 | — |

---

## 6. Rendering Tools (TOOL-RENDER)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| TOOL-RENDER-001 | render_business_report_html MUST produce valid HTML5 with all report sections and charts. | MUST | BRD-HTML-001, BRD-HTML-003 | 1.1 | 13 Jan 2026 | — |
| TOOL-RENDER-002 | render_decision_packet_html MUST produce valid HTML5 with all packet sections and visible evidence references. | MUST | BRD-HTML-002, BRD-HTML-003 | 1.1 | 13 Jan 2026 | — |
| TOOL-RENDER-003 | export_pdf MAY produce multiple output formats (ade.pdf, ade.html, ade_stub.json). | MAY | BRD-EXP-001 | 1.1 | 13 Jan 2026 | — |
| TOOL-RENDER-004 | export_pdf MUST be the only tool with side_effect=True and write files to staging/output/. | MUST | BRD-EXP-003 | 1.1 | 13 Jan 2026 | — |

---

## 7. Narrative Tools (TOOL-NARR)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| TOOL-NARR-001 | build_reasoning_narrative MUST summarize run events in human-readable format (< 200 words). | MUST | BRD-RPT-006 | 1.1 | 13 Jan 2026 | — |

---

## Cross-References

- **BRD**: [BRD-tools.md](../01_brd/BRD-tools.md)
