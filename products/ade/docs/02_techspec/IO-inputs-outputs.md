# ADE Input/Output Technical Specification

> **Document**: Technical Specification — Inputs and Outputs  
> **Prefix**: IO-*  
> **Version**: 1.2  
> **Last Updated**: 2026-01-20

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added evidence and artifact requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |

---

## 1. Product Objectives

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-OBJ-001 | The ADE system MUST include evidence references in 100% of outputs. | MUST | BRD-OBJ-001 | 1.1 | 13 Jan 2026 | Maps to OBJ-001 |
| IO-OBJ-002 | The ADE system MUST produce identical outputs for identical inputs. | MUST | BRD-OBJ-002 | 1.1 | 13 Jan 2026 | Reproducibility requirement |
| IO-OBJ-003 | The ADE system MUST require explicit user approval for all plans before execution. | MUST | BRD-OBJ-003 | 1.1 | 13 Jan 2026 | — |
| IO-OBJ-004 | The ADE system MUST include confidence_level, assumptions, and limitations in all outputs. | MUST | BRD-OBJ-004 | 1.1 | 13 Jan 2026 | Transparency fields |
| IO-OBJ-005 | The ADE system SHOULD produce a report within 5 minutes of question submission. | SHOULD | BRD-OBJ-005 | 1.1 | 13 Jan 2026 | Time-to-report target |
| IO-OBJ-006 | The ADE system MUST support at least 4 chart types (bar, line, area, scatter). | MUST | BRD-OBJ-006 | 1.1 | 13 Jan 2026 | — |
| IO-OBJ-007 | The ADE system MUST allow users to toggle hypothesis checks on or off. | MUST | BRD-OBJ-007 | 1.1 | 13 Jan 2026 | — |

---

## 2. Input Payload Requirements (IO-IN)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-IN-001 | The ADE payload MUST include a dataset field. | MUST | BRD-FMT-001 | 1.1 | 13 Jan 2026 | Required for both flows |
| IO-IN-002 | The ade_v1 flow MUST accept payload fields: dataset (required), prompt (optional), intent (optional), question (optional), instructions (optional). | MUST | BRD-V1-001, BRD-V1-003 | 1.1 | 13 Jan 2026 | — |
| IO-IN-003 | The visualization flow MUST accept payload fields: dataset (required), prompt (optional). | MUST | BRD-VIZ-001 | 1.1 | 13 Jan 2026 | — |
| IO-IN-004 | The ade_v1 flow MUST accept intent from alternate fields in priority order: prompt, intent, question, instructions. | MUST | BRD-V1-001, BRD-V1-002 | 1.1 | 13 Jan 2026 | — |

---

## 3. Dataset Requirements (IO-DATA)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-DATA-001 | The ADE system MUST accept datasets in CSV format with comma delimiter. | MUST | BRD-FMT-001 | 1.1 | 13 Jan 2026 | — |
| IO-DATA-002 | The ADE system MUST treat the first row of CSV files as the header row. | MUST | BRD-FMT-003 | 1.1 | 13 Jan 2026 | — |
| IO-DATA-003 | The ADE system MUST support UTF-8 encoding for dataset files. | MUST | BRD-FMT-002 | 1.1 | 13 Jan 2026 | — |
| IO-DATA-004 | The ADE system MUST read user datasets from products/ade/staging/input/. | MUST | BRD-LOC-001 | 1.1 | 13 Jan 2026 | — |
| IO-DATA-005 | The ADE system MUST read built-in datasets from products/ade/data/. | MUST | BRD-LOC-002 | 1.1 | 13 Jan 2026 | — |
| IO-DATA-006 | The ADE system MUST provide the branded_cards_transactions dataset as a built-in dataset. | MUST | BRD-BUILTIN-001 | 1.1 | 13 Jan 2026 | Location: products/ade/data/branded_cards_transactions.csv |
| IO-DATA-007 | The ADE system MUST resolve dataset names to file paths using case-sensitive matching. | MUST | BRD-LOC-003 | 1.1 | 13 Jan 2026 | — |
| IO-DATA-008 | The ADE system MUST produce a clear error when a dataset file is missing. | MUST | BRD-LOC-004 | 1.1 | 13 Jan 2026 | — |

---

## 4. User Input Requirements (IO-USER)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-USER-001 | The viz_preferences user input MUST validate against a schema with properties: chart_type (enum: bar, line, area, scatter), metric_focus (enum: mean, sum, median, growth_rate, anomalies), include_hypothesis_checks (boolean), notes (string). | MUST | BRD-PREF-001, BRD-PREF-002, BRD-PREF-003 | 1.1 | 13 Jan 2026 | — |
| IO-USER-002 | The viz_preferences user input MUST require chart_type and metric_focus fields. | MUST | BRD-PREF-001, BRD-PREF-002 | 1.1 | 13 Jan 2026 | — |
| IO-USER-003 | The ade_v1 flow MUST use default values: chart_type=bar, metric_focus=mean, include_hypothesis_checks=true. | MUST | BRD-PREF-001, BRD-PREF-002 | 1.1 | 13 Jan 2026 | — |
| IO-USER-004 | The visualization flow MUST use default values: chart_type=bar, metric_focus=anomalies, include_hypothesis_checks=true. | MUST | BRD-PREF-001, BRD-PREF-002 | 1.1 | 13 Jan 2026 | — |

---

## 5. Output Requirements (IO-OUT)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-OUT-001 | The ADE system MUST produce business_report.html as a primary output. | MUST | BRD-OUT-001 | 1.1 | 13 Jan 2026 | — |
| IO-OUT-002 | The visualization flow MUST produce decision_packet.html as an additional output. | MUST | BRD-OUT-010 | 1.1 | 13 Jan 2026 | — |
| IO-OUT-003 | The ADE system MUST write outputs to products/ade/staging/output/. | MUST | BRD-LOC-001 | 1.1 | 13 Jan 2026 | — |
| IO-OUT-004 | The ADE system MUST produce HTML outputs that are valid HTML5 with DOCTYPE declaration. | MUST | BRD-OUT-002, BRD-OUT-011 | 1.1 | 13 Jan 2026 | — |
| IO-OUT-005 | The ADE system MUST produce well-formed HTML with no unclosed tags. | MUST | BRD-HTML-003 | 1.1 | 13 Jan 2026 | — |
| IO-OUT-006 | The export_pdf tool MAY produce ade.pdf, ade.html, and ade_stub.json as optional outputs. | MAY | BRD-PDF-001 | 1.1 | 13 Jan 2026 | — |

---

## 6. Output Quality Requirements (IO-QUAL)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-QUAL-001 | The ADE system MUST produce non-empty executive summaries that reflect key findings. | MUST | BRD-QUAL-001, BRD-QUAL-002 | 1.1 | 13 Jan 2026 | — |
| IO-QUAL-002 | The ADE system MUST produce key findings that include implications and map to evidence. | MUST | BRD-QUAL-001 | 1.1 | 13 Jan 2026 | — |
| IO-QUAL-003 | The ADE system SHOULD produce recommendations that include concrete actions when present. | SHOULD | BRD-QUAL-003 | 1.1 | 13 Jan 2026 | — |
| IO-QUAL-004 | The ADE system MUST produce narratives in human-readable plain-language text. | MUST | BRD-NARR-002 | 1.1 | 13 Jan 2026 | — |
| IO-QUAL-005 | The ADE system MUST render charts using valid Vega-Lite specifications. | MUST | BRD-QUAL-010, BRD-CHART-007 | 1.1 | 13 Jan 2026 | — |
| IO-QUAL-006 | The ADE system MUST render tables with visible column headers and no overflow clipping. | MUST | BRD-QUAL-011 | 1.1 | 13 Jan 2026 | — |
| IO-QUAL-007 | The ADE system MUST produce HTML that renders correctly in Chrome, Firefox, and Safari. | MUST | BRD-QUAL-012 | 1.1 | 13 Jan 2026 | — |

---

## 7. Version Transparency Requirements (IO-VER)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-VER-001 | The ADE system MUST include product, flow, and schema versions in output metadata. | MUST | BRD-VER-001 | 1.1 | 13 Jan 2026 | — |
| IO-VER-002 | The ADE system SHOULD record dataset_hash and input_hash in outputs. | SHOULD | BRD-VER-002 | 1.1 | 13 Jan 2026 | — |
| IO-VER-003 | The ADE system MUST version-pin or disallow non-deterministic dependencies. | MUST | BRD-VER-003 | 1.1 | 13 Jan 2026 | — |

---

## 8. Decision Authority Boundary (IO-DAB)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-DAB-001 | The ADE system MUST label outputs as recommendations/findings, not decisions. | MUST | BRD-DAB-001 | 1.1 | 13 Jan 2026 | — |
| IO-DAB-002 | The ADE decision packets MUST clarify that human authority is required for final decisions. | MUST | BRD-DAB-002 | 1.1 | 13 Jan 2026 | — |
| IO-DAB-003 | The ADE outputs MUST NOT trigger downstream actions without explicit approval. | MUST | BRD-DAB-003 | 1.1 | 13 Jan 2026 | — |
| IO-DAB-004 | The ADE system SHOULD use confidence language that avoids implying autonomous decisions. | SHOULD | BRD-DAB-004 | 1.1 | 13 Jan 2026 | — |
| IO-DAB-005 | The ADE system MUST present recommendations as advisory. | MUST | BRD-DAB-005 | 1.1 | 13 Jan 2026 | — |

---

## 9. Evidence Requirements (IO-EVID)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-EVID-001 | The ADE system MUST include evidence_refs in all claims (DecisionSection and Finding). | MUST | BRD-EVREF-001 | 1.1 | 13 Jan 2026 | — |
| IO-EVID-002 | The evidence_refs MUST include dataset_id and columns fields. | MUST | BRD-EVREF-002, BRD-EVREF-003 | 1.1 | 13 Jan 2026 | — |
| IO-EVID-003 | The DecisionPacket MUST include trace_refs with step_id references and user_inputs. | MUST | BRD-TRACE-001, BRD-TRACE-002, BRD-TRACE-003 | 1.1 | 13 Jan 2026 | — |
| IO-EVID-004 | The tools compute_business_metrics, detect_anomalies, hypothesis_test_data_outage, and hypothesis_test_seasonality MUST produce evidence_items. | MUST | BRD-ITEM-001 | 1.1 | 13 Jan 2026 | — |

---

## 10. Artifact Reference Requirements (IO-ARTF)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| IO-ARTF-001 | The ADE system MUST support tool output references using syntax {{artifacts.tool.<tool_name>.output.<field>}}. | MUST | BRD-TRACE-002 | 1.1 | 13 Jan 2026 | — |
| IO-ARTF-002 | The ADE system MUST support user input references using syntax {{artifacts.user_input.<form_id>.values.<field>}}. | MUST | BRD-TRACE-003 | 1.1 | 13 Jan 2026 | — |
| IO-ARTF-003 | The ADE system MUST support agent output references using syntax {{artifacts.agent.<agent_name>.output.<field>}}. | MUST | BRD-TRACE-002 | 1.1 | 13 Jan 2026 | — |
| IO-ARTF-004 | The ADE system MUST support payload references using syntax {{payload.<field>}}. | MUST | BRD-V1-001, BRD-VIZ-001 | 1.1 | 13 Jan 2026 | — |
| IO-ARTF-005 | The ADE system MUST resolve all artifact references at runtime and produce clear errors for missing references. | MUST | BRD-TRACE-004 | 1.1 | 13 Jan 2026 | — |

---

## Cross-References

- **BRD**: [BRD-data.md](../01_brd/BRD-data.md), [BRD-outputs.md](../01_brd/BRD-outputs.md), [BRD-overview.md](../01_brd/BRD-overview.md)
