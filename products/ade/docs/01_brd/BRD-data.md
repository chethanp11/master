# ADE Data Business Requirements

> **Document**: Business Requirements — Data  
> **Version**: 1.0.0

---

## 1. Dataset Requirements

### 1.1 Format Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-FMT-001 | System MUST accept CSV format | Derived from: INT-FMT-001 | P0 | 2026-01-13 | V1.1 |
| BRD-FMT-002 | System MUST support UTF-8 encoding | Derived from: INT-FMT-002 | P0 | 2026-01-13 | V1.1 |
| BRD-FMT-003 | System MUST parse standard CSV headers | Derived from: INT-FMT-003 | P0 | 2026-01-13 | V1.1 |
| BRD-FMT-004 | System MUST handle quoted fields | Derived from: INT-FMT-004 | P1 | 2026-01-13 | V1.1 |
| BRD-FMT-005 | System MUST handle empty values | Derived from: INT-FMT-005 | P1 | 2026-01-13 | V1.1 |

### 1.2 Location Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-LOC-001 | User datasets MUST be in staging/input/ | Derived from: INT-LOC-001 | P0 | 2026-01-13 | V1.1 |
| BRD-LOC-002 | Built-in datasets MUST be in data/ | Derived from: INT-LOC-002 | P0 | 2026-01-13 | V1.1 |
| BRD-LOC-003 | Dataset names MUST resolve to file paths | Derived from: INT-LOC-003 | P0 | 2026-01-13 | V1.1 |
| BRD-LOC-004 | Missing datasets MUST produce clear errors | Derived from: INT-LOC-004 | P0 | 2026-01-13 | V1.1 |

### 1.3 Built-in Datasets

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-BUILTIN-001 | branded_cards_transactions MUST be available | Derived from: INT-LOC-002 | P0 | 2026-01-13 | V1.1 |
| BRD-BUILTIN-002 | Built-in datasets MUST work without configuration | Derived from: INT-LOC-002 | P0 | 2026-01-13 | V1.1 |

---

## 2. Schema Requirements

### 2.1 General Schema Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-SCHEMA-001 | All data structures MUST use Pydantic models | Derived from: INT-SCHEMA-001 | P0 | 2026-01-13 | V1.1 |
| BRD-SCHEMA-002 | Schemas MUST reject unknown fields | Derived from: INT-SCHEMA-002 | P0 | 2026-01-13 | V1.1 |
| BRD-SCHEMA-003 | Schemas MUST validate types | Derived from: INT-SCHEMA-003 | P0 | 2026-01-13 | V1.1 |
| BRD-SCHEMA-004 | Schemas MUST use default factories for collections | Derived from: INT-SCHEMA-004 | P1 | 2026-01-13 | V1.1 |

### 2.2 Decision Packet Schema

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-DP-001 | DecisionPacket MUST include question | Derived from: INT-DP-001 | P0 | 2026-01-13 | V1.1 |
| BRD-DP-002 | DecisionPacket MUST include decision_summary | Derived from: INT-DP-002 | P0 | 2026-01-13 | V1.1 |
| BRD-DP-003 | DecisionPacket MUST include confidence_level | Derived from: INT-DP-003 | P0 | 2026-01-13 | V1.1 |
| BRD-DP-004 | DecisionPacket MUST include assumptions | Derived from: INT-DP-004 | P0 | 2026-01-13 | V1.1 |
| BRD-DP-005 | DecisionPacket MUST include limitations | Derived from: INT-DP-005 | P0 | 2026-01-13 | V1.1 |
| BRD-DP-006 | DecisionPacket MUST include sections | Derived from: INT-DP-006 | P0 | 2026-01-13 | V1.1 |
| BRD-DP-007 | DecisionPacket MUST include trace_refs | Derived from: INT-DP-007 | P0 | 2026-01-13 | V1.1 |

### 2.3 Business Report Schema

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-BR-001 | BusinessReport MUST include title | Derived from: INT-BR-001 | P0 | 2026-01-13 | V1.1 |
| BRD-BR-002 | BusinessReport MUST include timestamp | Derived from: INT-BR-002 | P0 | 2026-01-13 | V1.1 |
| BRD-BR-003 | BusinessReport MUST include dataset_id | Derived from: INT-BR-003 | P0 | 2026-01-13 | V1.1 |
| BRD-BR-004 | BusinessReport MUST include executive_summary | Derived from: INT-BR-004 | P0 | 2026-01-13 | V1.1 |
| BRD-BR-005 | BusinessReport MUST include key_findings | Derived from: INT-BR-005 | P0 | 2026-01-13 | V1.1 |
| BRD-BR-006 | BusinessReport MUST include visuals | Derived from: INT-BR-006 | P1 | 2026-01-13 | V1.1 |
| BRD-BR-007 | BusinessReport MUST include anomalies | Derived from: INT-BR-007 | P1 | 2026-01-13 | V1.1 |
| BRD-BR-008 | BusinessReport MUST include appendix | Derived from: INT-BR-008 | P1 | 2026-01-13 | V1.1 |

### 2.4 Intent Frame Schema

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-IF-001 | IntentFrame MUST include intent_summary | Derived from: INT-IF-001 | P0 | 2026-01-13 | V1.1 |
| BRD-IF-002 | IntentFrame MUST include confidence_score | Derived from: INT-IF-002 | P0 | 2026-01-13 | V1.1 |
| BRD-IF-003 | IntentFrame MUST include blocking_required | Derived from: INT-IF-003 | P0 | 2026-01-13 | V1.1 |
| BRD-IF-004 | IntentFrame SHOULD include inferred_entities | Derived from: INT-IF-004 | P1 | 2026-01-13 | V1.1 |
| BRD-IF-005 | IntentFrame SHOULD include inferred_metrics | Derived from: INT-IF-005 | P1 | 2026-01-13 | V1.1 |
| BRD-IF-006 | IntentFrame MUST include blocking_questions | Derived from: INT-IF-006 | P0 | 2026-01-13 | V1.1 |

---

## 3. Evidence Requirements

### 3.1 Evidence References

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-EVREF-001 | All claims MUST have evidence_refs | Derived from: INT-AUDIT-001 | P0 | 2026-01-13 | V1.1 |
| BRD-EVREF-002 | evidence_refs MUST include dataset_id | Derived from: INT-AUDIT-002 | P0 | 2026-01-13 | V1.1 |
| BRD-EVREF-003 | evidence_refs MUST include columns | Derived from: INT-AUDIT-003 | P0 | 2026-01-13 | V1.1 |
| BRD-EVREF-004 | Evidence MUST be traceable to source data | Derived from: INT-AUDIT-004 | P0 | 2026-01-13 | V1.1 |

### 3.2 Trace References

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-TRACE-001 | DecisionPacket MUST include trace_refs | Derived from: INT-TRACE-001 | P0 | 2026-01-13 | V1.1 |
| BRD-TRACE-002 | trace_refs MUST include step_id references | Derived from: INT-TRACE-002 | P0 | 2026-01-13 | V1.1 |
| BRD-TRACE-003 | trace_refs MUST include user_inputs | Derived from: INT-TRACE-003 | P0 | 2026-01-13 | V1.1 |
| BRD-TRACE-004 | All trace references MUST be valid | Derived from: INT-TRACE-004 | P0 | 2026-01-13 | V1.1 |

### 3.3 Evidence Items

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-ITEM-001 | Tools MUST produce evidence_items | Derived from: INT-TOOL-005 | P0 | 2026-01-13 | V1.1 |
| BRD-ITEM-002 | Evidence items MUST include provenance | Derived from: INT-EV-004 | P0 | 2026-01-13 | V1.1 |
| BRD-ITEM-003 | Evidence items MUST include confidence | Derived from: INT-EV-004 | P1 | 2026-01-13 | V1.1 |
| BRD-ITEM-004 | Evidence items MUST include dataset_id | Derived from: INT-EV-001 | P0 | 2026-01-13 | V1.1 |
| BRD-ITEM-005 | Evidence items MUST include columns | Derived from: INT-EV-002 | P0 | 2026-01-13 | V1.1 |
| BRD-ITEM-006 | Evidence items MUST include values | Derived from: INT-EV-003 | P0 | 2026-01-13 | V1.1 |

---

## 4. Confidence Level Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-CL-001 | Confidence levels MUST use standard values | Derived from: INT-SUFF-002 | P0 | 2026-01-13 | V1.1 |
| BRD-CL-002 | Valid confidence levels: high, medium, low | Derived from: INT-SUFF-002 | P0 | 2026-01-13 | V1.1 |
| BRD-CL-003 | Confidence MUST be present in all packets | Derived from: INT-DP-003 | P0 | 2026-01-13 | V1.1 |
| BRD-CL-004 | Confidence MUST be explainable | Derived from: INT-TRANS-003 | P1 | 2026-01-13 | V1.1 |

---

## 5. Validation Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-VAL-001 | All outputs MUST pass Pydantic validation | Derived from: INT-SCHEMA-001, INT-SCHEMA-003 | P0 | 2026-01-13 | V1.1 |
| BRD-VAL-002 | Invalid outputs MUST produce clear errors | Derived from: INT-SCHEMA-002 | P0 | 2026-01-13 | V1.1 |
| BRD-VAL-003 | Validation MUST happen before rendering | Derived from: INT-SCHEMA-003 | P0 | 2026-01-13 | V1.1 |

---

## 6. Context Pack Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-CTX-001 | System MUST construct a Context Pack after ingestion and before planning | Derived from: INT-CTX-001 | P0 | 2026-01-13 | V1.1 |
| BRD-CTX-002 | Context Packs MUST include dataset profile and coverage metrics | Derived from: INT-CTX-002 | P0 | 2026-01-13 | V1.1 |
| BRD-CTX-003 | Context Pack statistics MUST be backed by evidence items | Derived from: INT-CTX-003 | P0 | 2026-01-13 | V1.1 |
| BRD-CTX-004 | Advisory reasoning MUST reference Context Pack artifacts | Derived from: INT-CTX-004 | P1 | 2026-01-13 | V1.1 |
| BRD-CTX-005 | ADE reasoning and outputs MUST treat Context Pack artifacts as the sole grounding source | Derived from: INT-CTX-005 | P0 | 2026-01-13 | V1.1 |

---

## Cross-References

- **Techspec**: [SCHEMA-schemas.md](../02_techspec/SCHEMA-schemas.md), [IO-inputs-outputs.md](../02_techspec/IO-inputs-outputs.md)
- **System Design**: [schemas.md](../04_systemdesign/schemas.md)
