# ADE Data Business Requirements

> **Document**: Business Requirements — Data  
> **Version**: V1.3  
> **Last Updated**: 2026-01-21

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial release |
| V1.2 | 2026-01-19 | Standardized tables, removed TSD-level detail, and aligned intent traceability |
| V1.3 | 2026-01-21 | Added BRD-FMT-006 (transaction-level default) |

## 1. Dataset Requirements

### 1.1 Format Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-FMT-001 | System MUST accept CSV format | INT-FMT-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-FMT-002 | System MUST support UTF-8 encoding | INT-FMT-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-FMT-003 | System MUST parse standard CSV headers | INT-FMT-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-FMT-004 | System MUST handle quoted fields | INT-FMT-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-FMT-005 | System MUST handle empty values | INT-FMT-005 | P1 | 2026-01-13 | V1.1 | — |
| BRD-FMT-006 | ADE MUST treat all datasets as transaction-level by default; row-level analysis SHALL be assumed unless a valid time field and aggregation grain are explicitly confirmed through semantic interpretation | INT-FMT-006 | P0 | 2026-01-21 | V1.3 | — |

### 1.2 Location Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-LOC-001 | User datasets MUST be stored in the designated input location | INT-LOC-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-LOC-002 | Built-in datasets MUST be stored in the designated built-in location | INT-LOC-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-LOC-003 | Dataset names MUST resolve to specific dataset sources | INT-LOC-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-LOC-004 | Missing datasets MUST produce clear errors | INT-LOC-004 | P0 | 2026-01-13 | V1.1 | — |

### 1.3 Built-in Datasets

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-BUILTIN-001 | A default demonstration dataset MUST be available | INT-LOC-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-BUILTIN-002 | Built-in datasets MUST work without configuration | INT-LOC-002 | P0 | 2026-01-13 | V1.1 | — |

---

## 2. Schema Requirements

### 2.1 General Schema Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-SCHEMA-001 | All data structures MUST use standardized schemas | INT-SCHEMA-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SCHEMA-002 | Schemas MUST reject unknown fields | INT-SCHEMA-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SCHEMA-003 | Schemas MUST validate types | INT-SCHEMA-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SCHEMA-004 | Schemas MUST use default factories for collections | INT-SCHEMA-004 | P1 | 2026-01-13 | V1.1 | — |

### 2.2 Decision Packet Schema

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-DP-001 | Decision packets MUST include question context | INT-DP-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DP-002 | Decision packets MUST include decision summary | INT-DP-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DP-003 | Decision packets MUST include confidence level | INT-DP-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DP-004 | Decision packets MUST include assumptions | INT-DP-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DP-005 | Decision packets MUST include limitations | INT-DP-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DP-006 | Decision packets MUST include structured sections | INT-DP-006 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DP-007 | Decision packets MUST include trace references | INT-DP-007 | P0 | 2026-01-13 | V1.1 | — |

### 2.3 Business Report Schema

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-BR-001 | BusinessReport MUST include title | INT-BR-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-BR-002 | BusinessReport MUST include timestamp | INT-BR-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-BR-003 | Business reports MUST include dataset identifiers | INT-BR-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-BR-004 | Business reports MUST include executive summaries | INT-BR-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-BR-005 | Business reports MUST include key findings | INT-BR-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-BR-006 | Business reports MUST include visuals | INT-BR-006 | P1 | 2026-01-13 | V1.1 | — |
| BRD-BR-007 | BusinessReport MUST include anomalies | INT-BR-007 | P1 | 2026-01-13 | V1.1 | — |
| BRD-BR-008 | BusinessReport MUST include appendix | INT-BR-008 | P1 | 2026-01-13 | V1.1 | — |

### 2.4 Intent Frame Schema

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-IF-001 | Intent frames MUST include intent summaries | INT-IF-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-IF-002 | Intent frames MUST include confidence scores | INT-IF-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-IF-003 | Intent frames MUST include blocking requirement indicators | INT-IF-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-IF-004 | Intent frames SHOULD include inferred entities | INT-IF-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-IF-005 | Intent frames SHOULD include inferred metrics | INT-IF-005 | P1 | 2026-01-13 | V1.1 | — |
| BRD-IF-006 | Intent frames MUST include blocking questions | INT-IF-006 | P0 | 2026-01-13 | V1.1 | — |

---

## 3. Evidence Requirements

### 3.1 Evidence References

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-EVREF-001 | All claims MUST have evidence references | INT-AUDIT-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-EVREF-002 | Evidence references MUST include dataset identifiers | INT-AUDIT-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-EVREF-003 | Evidence references MUST include referenced columns | INT-AUDIT-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-EVREF-004 | Evidence MUST be traceable to source data | INT-AUDIT-004 | P0 | 2026-01-13 | V1.1 | — |

### 3.2 Trace References

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-TRACE-001 | Decision packets MUST include trace references | INT-TRACE-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TRACE-002 | Trace references MUST include execution step identifiers | INT-TRACE-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TRACE-003 | Trace references MUST include user inputs | INT-TRACE-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TRACE-004 | All trace references MUST be valid | INT-TRACE-004 | P0 | 2026-01-13 | V1.1 | — |

### 3.3 Evidence Items

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-ITEM-001 | Tools MUST produce evidence_items | INT-TOOL-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ITEM-002 | Evidence items MUST include provenance | INT-EV-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ITEM-003 | Evidence items MUST include confidence | INT-EV-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-ITEM-004 | Evidence items MUST include dataset identifiers | INT-EV-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ITEM-005 | Evidence items MUST include referenced columns | INT-EV-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ITEM-006 | Evidence items MUST include referenced values | INT-EV-003 | P0 | 2026-01-13 | V1.1 | — |

---

## 4. Confidence Level Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-CL-001 | Confidence levels MUST use standard values | INT-SUFF-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CL-002 | Valid confidence levels: high, medium, low | INT-SUFF-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CL-003 | Confidence MUST be present in all packets | INT-DP-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CL-004 | Confidence MUST be explainable | INT-TRANS-003 | P1 | 2026-01-13 | V1.1 | — |

---

## 5. Validation Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-VAL-001 | All outputs MUST pass schema validation | INT-SCHEMA-001, INT-SCHEMA-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VAL-002 | Invalid outputs MUST produce clear errors | INT-SCHEMA-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VAL-003 | Validation MUST happen before rendering | INT-SCHEMA-003 | P0 | 2026-01-13 | V1.1 | — |

---

## 6. Context Pack Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-CTX-001 | System MUST construct a Context Pack after ingestion and before planning | INT-CTX-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CTX-002 | Context Packs MUST include dataset profile and coverage metrics | INT-CTX-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CTX-003 | Context Pack statistics MUST be backed by evidence items | INT-CTX-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CTX-004 | Advisory reasoning MUST reference Context Pack artifacts | INT-CTX-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-CTX-005 | ADE reasoning and outputs MUST treat Context Pack artifacts as the sole grounding source | INT-CTX-005 | P0 | 2026-01-13 | V1.1 | — |

---

## Appendix: Technical Details (Removed from BRD)

### Dataset Locations (Technical Reference)
- staging/input/
- data/

### Default Demonstration Dataset
- branded_cards_transactions

### Schema Field Names (Technical Reference)
- DecisionPacket: question, decision_summary, confidence_level, assumptions, limitations, sections, trace_refs
- BusinessReport: title, generated_at_iso, dataset_id, executive_summary, key_findings, visuals, anomalies, recommendations, appendix
- IntentFrame: intent_summary, inferred_entities, inferred_metrics, inferred_time_window, confidence_score, blocking_required, blocking_questions
