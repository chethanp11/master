# ADE Developer Intent

> **Document**: Product Developer Intent  
> **Product**: Analytical Decision Engine (ADE)  
> **Platform**: MASTER — Managed AI Systems for Trusted Execution & Reasoning  
> **Last Updated**: 2026-01-18  
> **Status**: V1.2 Release

---

## Scope

This file contains sections 5, 6 from the ADE Developer Intent.

---

# 5. Data & Schemas (INT-DATA)

> **Maps to**: [BRD-data.md](../01_brd/BRD-data.md)

## 5.1 Dataset Requirements

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-FMT-001** | Accept CSV format — Standard format | — | 2026-01-13 | V1.1 | — |
| **INT-FMT-002** | Support UTF-8 encoding — International support | — | 2026-01-13 | V1.1 | — |
| **INT-FMT-003** | Parse standard CSV headers — Schema extraction | — | 2026-01-13 | V1.1 | — |
| **INT-FMT-004** | Handle quoted fields — Format robustness | — | 2026-01-13 | V1.1 | — |
| **INT-FMT-005** | Handle empty values — Data quality | — | 2026-01-13 | V1.1 | — |

### Location Rules

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-LOC-001** | User datasets in staging/input/ — User data isolation | — | 2026-01-13 | V1.1 | — |
| **INT-LOC-002** | Built-in datasets in data/ — Product data | — | 2026-01-13 | V1.1 | — |
| **INT-LOC-003** | Dataset names resolve to file paths — Abstraction | — | 2026-01-13 | V1.1 | — |
| **INT-LOC-004** | Missing datasets produce clear errors — User guidance | — | 2026-01-13 | V1.1 | — |

### Built-in Datasets

- branded_cards_transactions — Default demonstration dataset

## 5.2 Schema Requirements

### General Schema Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-SCHEMA-001** | All data structures use Pydantic models — Type safety | — | 2026-01-13 | V1.1 | — |
| **INT-SCHEMA-002** | Schemas reject unknown fields — Data integrity | — | 2026-01-13 | V1.1 | — |
| **INT-SCHEMA-003** | Schemas validate types — Error prevention | — | 2026-01-13 | V1.1 | — |
| **INT-SCHEMA-004** | Use default factories for collections — Safe initialization | — | 2026-01-13 | V1.1 | — |

## 5.3 DecisionPacket Schema

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-DP-001** | Include question — Context | — | 2026-01-13 | V1.1 | — |
| **INT-DP-002** | Include decision_summary — Primary output | — | 2026-01-13 | V1.1 | — |
| **INT-DP-003** | Include confidence_level — Uncertainty | — | 2026-01-13 | V1.1 | — |
| **INT-DP-004** | Include assumptions — Transparency | — | 2026-01-13 | V1.1 | — |
| **INT-DP-005** | Include limitations — Transparency | — | 2026-01-13 | V1.1 | — |
| **INT-DP-006** | Include sections — Structure | — | 2026-01-13 | V1.1 | — |
| **INT-DP-007** | Include trace_refs — Audit trail | — | 2026-01-13 | V1.1 | — |

### Schema

```
question: str
decision_summary: str
confidence_level: "high" | "medium" | "low"
assumptions: List[str]
limitations: List[str]
sections: List[DecisionSection]
trace_refs: List[Dict]
```

## 5.4 BusinessReport Schema

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-BR-001** | Include title — Identification | — | 2026-01-13 | V1.1 | — |
| **INT-BR-002** | Include timestamp — Temporal reference | — | 2026-01-13 | V1.1 | — |
| **INT-BR-003** | Include dataset_id — Data source | — | 2026-01-13 | V1.1 | — |
| **INT-BR-004** | Include executive_summary — Key takeaways | — | 2026-01-13 | V1.1 | — |
| **INT-BR-005** | Include key_findings — Detailed insights | — | 2026-01-13 | V1.1 | — |
| **INT-BR-006** | Include visuals — Visual communication | — | 2026-01-13 | V1.1 | — |
| **INT-BR-007** | Include anomalies — Issue identification | — | 2026-01-13 | V1.1 | — |
| **INT-BR-008** | Include appendix — Supporting detail | — | 2026-01-13 | V1.1 | — |

### Schema

```
title: str
generated_at_iso: str
dataset_id: str
executive_summary: List[str]
key_findings: List[Finding]
visuals: List[VisualSpec]
anomalies: List[AnomalyRow]
recommendations: List[str]
appendix: Appendix
```

## 5.5 IntentFrame Schema

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-IF-001** | Include intent_summary — Interpretation | — | 2026-01-13 | V1.1 | — |
| **INT-IF-002** | Include confidence_score — Uncertainty | — | 2026-01-13 | V1.1 | — |
| **INT-IF-003** | Include blocking_required — Flow control | — | 2026-01-13 | V1.1 | — |
| **INT-IF-004** | Include inferred_entities — Extraction | — | 2026-01-13 | V1.1 | — |
| **INT-IF-005** | Include inferred_metrics — Extraction | — | 2026-01-13 | V1.1 | — |
| **INT-IF-006** | Include blocking_questions — User guidance | — | 2026-01-13 | V1.1 | — |

### Schema

```
intent_summary: str
inferred_entities: List[str]
inferred_metrics: List[str]
inferred_time_window: Optional[str]
confidence_score: float
blocking_required: bool
blocking_questions: List[str]
```

## 5.6 Evidence Schema

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-EV-001** | Evidence includes dataset_id — Data source | — | 2026-01-13 | V1.1 | — |
| **INT-EV-002** | Evidence includes columns — Specific fields | — | 2026-01-13 | V1.1 | — |
| **INT-EV-003** | Evidence includes values — Actual data | — | 2026-01-13 | V1.1 | — |
| **INT-EV-004** | Evidence is verifiable — Audit requirement | — | 2026-01-13 | V1.1 | — |

---

# 6. Outputs & Audit (INT-OUTPUTS)

> **Maps to**: [BRD-outputs.md](../01_brd/BRD-outputs.md)

## 6.1 Primary Output Intent

### Business Report

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-OUT-001** | Produce business_report.html — Primary output | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-002** | Report must be valid HTML5 — Standards | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-003** | Include executive summary — Key takeaways | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-004** | Include key findings — Detailed insights | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-005** | Include visualizations — Visual communication | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-006** | Include anomaly table — Issue identification | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-007** | Include recommendations — Actionability | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-008** | Include appendix — Supporting detail | — | 2026-01-13 | V1.1 | — |

### Decision Packet

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-OUT-010** | Produce decision_packet.html — Primary output (viz flow) | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-011** | Packet must be valid HTML5 — Standards | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-012** | Include question — Context | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-013** | Include decision summary — Primary output | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-014** | Include confidence level — Uncertainty | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-015** | Include evidence sections — Traceability | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-016** | Include assumptions — Transparency | — | 2026-01-13 | V1.1 | — |
| **INT-OUT-017** | Include limitations — Transparency | — | 2026-01-13 | V1.1 | — |

### Output Summary

| Output | Format | Flow |
|--------|--------|------|
| business_report.html | HTML5 | Both |
| decision_packet.html | HTML5 | visualization |

## 6.2 Output Location Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-OUTLOC-001** | Outputs written to staging/output/ — Organization | — | 2026-01-13 | V1.1 | — |
| **INT-OUTLOC-002** | Create directory if missing — Robustness | — | 2026-01-13 | V1.1 | — |
| **INT-OUTLOC-003** | Consistent file naming — Predictability | — | 2026-01-13 | V1.1 | — |

## 6.3 Evidence Traceability Intent

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-AUDIT-001** | All claims traceable to evidence — Trust requirement | — | 2026-01-13 | V1.1 | — |
| **INT-AUDIT-002** | Evidence includes dataset references — Data source | — | 2026-01-13 | V1.1 | — |
| **INT-AUDIT-003** | Evidence includes column references — Specificity | — | 2026-01-13 | V1.1 | — |
| **INT-AUDIT-004** | Evidence verifiable against source data — Audit requirement | — | 2026-01-13 | V1.1 | — |

### Design Decision

**Evidence-First Architecture**: All outputs must include evidence references.

**Implications**:
- Tools produce evidence_items
- Assemblers include evidence_refs in outputs
- trace_refs link decisions to execution steps

## 6.4 Execution Traceability Intent

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-TRACE-001** | Outputs include trace_refs — Audit trail | — | 2026-01-13 | V1.1 | — |
| **INT-TRACE-002** | trace_refs link to execution steps — Step traceability | — | 2026-01-13 | V1.1 | — |
| **INT-TRACE-003** | trace_refs include user inputs — Input traceability | — | 2026-01-13 | V1.1 | — |
| **INT-TRACE-004** | Execution must be reproducible — Audit requirement | — | 2026-01-13 | V1.1 | — |

## 6.5 Transparency Intent

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-TRANS-001** | Outputs include explicit assumptions — Transparency | — | 2026-01-13 | V1.1 | — |
| **INT-TRANS-002** | Outputs include explicit limitations — Transparency | — | 2026-01-13 | V1.1 | — |
| **INT-TRANS-003** | Confidence levels must be explained — Understanding | — | 2026-01-13 | V1.1 | — |
| **INT-TRANS-004** | Downgrade reasons must be documented — Transparency | — | 2026-01-13 | V1.1 | — |

## 6.6 Reproducibility Intent

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-REPRO-001** | Same inputs produce same outputs — Audit requirement | — | 2026-01-13 | V1.1 | — |
| **INT-REPRO-002** | Timestamps are only allowed variation — Practical necessity | — | 2026-01-13 | V1.1 | — |
| **INT-REPRO-003** | No random or non-deterministic operations — Reproducibility | — | 2026-01-13 | V1.1 | — |
| **INT-REPRO-004** | Outputs can be regenerated from inputs — Verification | — | 2026-01-13 | V1.1 | — |

---

