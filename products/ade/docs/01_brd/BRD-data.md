# ADE Data Business Requirements

> **Document**: Business Requirements — Data  
> **Version**: 1.0.0

---

## 1. Dataset Requirements

### 1.1 Format Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-FMT-001 | System MUST accept CSV format | P0 |
| BRD-FMT-002 | System MUST support UTF-8 encoding | P0 |
| BRD-FMT-003 | System MUST parse standard CSV headers | P0 |
| BRD-FMT-004 | System MUST handle quoted fields | P1 |
| BRD-FMT-005 | System MUST handle empty values | P1 |

### 1.2 Location Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-LOC-001 | User datasets MUST be in staging/input/ | P0 |
| BRD-LOC-002 | Built-in datasets MUST be in data/ | P0 |
| BRD-LOC-003 | Dataset names MUST resolve to file paths | P0 |
| BRD-LOC-004 | Missing datasets MUST produce clear errors | P0 |

### 1.3 Built-in Datasets

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-BUILTIN-001 | branded_cards_transactions MUST be available | P0 |
| BRD-BUILTIN-002 | Built-in datasets MUST work without configuration | P0 |

---

## 2. Schema Requirements

### 2.1 General Schema Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-SCHEMA-001 | All data structures MUST use Pydantic models | P0 |
| BRD-SCHEMA-002 | Schemas MUST reject unknown fields | P0 |
| BRD-SCHEMA-003 | Schemas MUST validate types | P0 |
| BRD-SCHEMA-004 | Schemas MUST use default factories for collections | P1 |

### 2.2 Decision Packet Schema

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-DP-001 | DecisionPacket MUST include question | P0 |
| BRD-DP-002 | DecisionPacket MUST include decision_summary | P0 |
| BRD-DP-003 | DecisionPacket MUST include confidence_level | P0 |
| BRD-DP-004 | DecisionPacket MUST include assumptions | P0 |
| BRD-DP-005 | DecisionPacket MUST include limitations | P0 |
| BRD-DP-006 | DecisionPacket MUST include sections | P0 |
| BRD-DP-007 | DecisionPacket MUST include trace_refs | P0 |

### 2.3 Business Report Schema

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-BR-001 | BusinessReport MUST include title | P0 |
| BRD-BR-002 | BusinessReport MUST include timestamp | P0 |
| BRD-BR-003 | BusinessReport MUST include dataset_id | P0 |
| BRD-BR-004 | BusinessReport MUST include executive_summary | P0 |
| BRD-BR-005 | BusinessReport MUST include key_findings | P0 |
| BRD-BR-006 | BusinessReport MUST include visuals | P1 |
| BRD-BR-007 | BusinessReport MUST include anomalies | P1 |
| BRD-BR-008 | BusinessReport MUST include appendix | P1 |

### 2.4 Intent Frame Schema

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-IF-001 | IntentFrame MUST include intent_summary | P0 |
| BRD-IF-002 | IntentFrame MUST include confidence_score | P0 |
| BRD-IF-003 | IntentFrame MUST include blocking_required | P0 |
| BRD-IF-004 | IntentFrame SHOULD include inferred_entities | P1 |
| BRD-IF-005 | IntentFrame SHOULD include inferred_metrics | P1 |

---

## 3. Evidence Requirements

### 3.1 Evidence References

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-EVREF-001 | All claims MUST have evidence_refs | P0 |
| BRD-EVREF-002 | evidence_refs MUST include dataset_id | P0 |
| BRD-EVREF-003 | evidence_refs MUST include columns | P0 |
| BRD-EVREF-004 | Evidence MUST be traceable to source data | P0 |

### 3.2 Trace References

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-TRACE-001 | DecisionPacket MUST include trace_refs | P0 |
| BRD-TRACE-002 | trace_refs MUST include step_id references | P0 |
| BRD-TRACE-003 | trace_refs MUST include user_inputs | P0 |
| BRD-TRACE-004 | All trace references MUST be valid | P0 |

### 3.3 Evidence Items

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-ITEM-001 | Tools MUST produce evidence_items | P0 |
| BRD-ITEM-002 | Evidence items MUST include provenance | P0 |
| BRD-ITEM-003 | Evidence items MUST include confidence | P1 |

---

## 4. Confidence Level Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-CL-001 | Confidence levels MUST use standard values | P0 |
| BRD-CL-002 | Valid confidence levels: high, medium, low | P0 |
| BRD-CL-003 | Confidence MUST be present in all packets | P0 |
| BRD-CL-004 | Confidence MUST be explainable | P1 |

---

## 5. Validation Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-VAL-001 | All outputs MUST pass Pydantic validation | P0 |
| BRD-VAL-002 | Invalid outputs MUST produce clear errors | P0 |
| BRD-VAL-003 | Validation MUST happen before rendering | P0 |

---

## Cross-References

- **Techspec**: [SCHEMA-schemas.md](../02_techspec/SCHEMA-schemas.md), [IO-inputs-outputs.md](../02_techspec/IO-inputs-outputs.md)
- **System Design**: [schemas.md](../04_systemdesign/schemas.md)
