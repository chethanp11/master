# ADE Output Business Requirements

> **Document**: Business Requirements — Outputs  
> **Version**: V1.3  
> **Last Updated**: 2026-01-21

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial release |
| V1.2 | 2026-01-19 | Standardized tables, removed TSD-level detail, and aligned intent traceability |
| V1.3 | 2026-01-21 | Added BRD-OUT-018 (reasoning narrative), BRD-FAIL-001...003 (failure modes), BRD-FRI-006, BRD-ALIGN-004 |

## 1. Primary Output Requirements

### 1.1 Business Report

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-OUT-001 | System MUST produce the business report output | INT-OUT-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-002 | Report MUST be valid HTML5 | INT-OUT-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-003 | Report MUST include executive summary | INT-OUT-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-004 | Report MUST include key findings | INT-OUT-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-005 | Report MUST include visualizations | INT-OUT-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-006 | Report MUST include anomaly table | INT-OUT-006 | P1 | 2026-01-13 | V1.1 | — |
| BRD-OUT-007 | Report MUST include recommendations | INT-OUT-007 | P1 | 2026-01-13 | V1.1 | — |
| BRD-OUT-008 | Report MUST include appendix | INT-OUT-008 | P1 | 2026-01-13 | V1.1 | — |

### 1.2 Decision Packet

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-OUT-010 | System MUST produce the decision packet output for the visualization flow | INT-OUT-010 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-011 | Packet MUST be valid HTML5 | INT-OUT-011 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-012 | Packet MUST include question | INT-OUT-012 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-013 | Packet MUST include decision summary | INT-OUT-013 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-014 | Packet MUST include confidence level | INT-OUT-014 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-015 | Packet MUST include evidence sections | INT-OUT-015 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-016 | Packet MUST include assumptions | INT-OUT-016 | P0 | 2026-01-13 | V1.1 | — |
| BRD-OUT-017 | Packet MUST include limitations | INT-OUT-017 | P0 | 2026-01-13 | V1.1 | — |

### 1.3 Reasoning Narrative

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-OUT-018 | ADE MUST declare "Reasoning Narrative" as a required output artifact; every ADE run SHALL produce a coherent, human-readable reasoning narrative explaining why each analysis or decision was made | INT-OUT-018 | P0 | 2026-01-21 | V1.3 | — |

---

## 2. Output Location Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-LOC-001 | Outputs MUST be written to the designated output location | INT-OUTLOC-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-LOC-002 | Output directory MUST be created if missing | INT-OUTLOC-002 | P1 | 2026-01-13 | V1.1 | — |
| BRD-LOC-003 | Output files MUST have consistent naming | INT-OUTLOC-003 | P0 | 2026-01-13 | V1.1 | — |

---

## 3. Audit Requirements

### 3.1 Evidence Traceability

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-AUDIT-001 | All claims MUST be traceable to evidence | INT-AUDIT-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-AUDIT-002 | Evidence MUST include dataset references | INT-AUDIT-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-AUDIT-003 | Evidence MUST include column references | INT-AUDIT-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-AUDIT-004 | Evidence MUST be verifiable against source data | INT-AUDIT-004 | P0 | 2026-01-13 | V1.1 | — |

### 3.2 Execution Traceability

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-AUDIT-010 | Outputs MUST include trace references | INT-TRACE-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-AUDIT-011 | Trace references MUST link to execution steps | INT-TRACE-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-AUDIT-012 | Trace references MUST include user inputs | INT-TRACE-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-AUDIT-013 | Execution MUST be reproducible | INT-TRACE-004 | P0 | 2026-01-13 | V1.1 | — |

### 3.3 Transparency

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-AUDIT-020 | Outputs MUST include explicit assumptions | INT-TRANS-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-AUDIT-021 | Outputs MUST include explicit limitations | INT-TRANS-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-AUDIT-022 | Confidence levels MUST be explained | INT-TRANS-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-AUDIT-023 | Downgrade reasons MUST be documented | INT-TRANS-004 | P1 | 2026-01-13 | V1.1 | — |

---

## 4. Reproducibility Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-REPRO-001 | Same inputs MUST produce same outputs | INT-REPRO-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-REPRO-002 | Timestamps are the only allowed variation | INT-REPRO-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-REPRO-003 | No random variations in outputs | INT-REPRO-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-REPRO-004 | Outputs MUST be deterministic | INT-REPRO-004 | P0 | 2026-01-13 | V1.1 | — |

---

## 5. Optional Export Requirements

### 5.1 PDF Export

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-PDF-001 | System MAY export to PDF | INT-REND-004 | P2 | 2026-01-13 | V1.1 | — |
| BRD-PDF-002 | PDF MUST include all report content | INT-REND-004 | P2 | 2026-01-13 | V1.1 | — |
| BRD-PDF-003 | PDF MUST be printable | INT-REND-004 | P2 | 2026-01-13 | V1.1 | — |

## 6. Output Quality Requirements

### 6.1 Content Quality

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-QUAL-001 | All key findings or assertions MUST be backed by at least one evidence reference | INT-QUAL-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-QUAL-002 | Executive summaries MUST include scope, key result, confidence, and primary limitation | INT-QUAL-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-QUAL-003 | Recommendations MUST only be emitted when evidence-supported; otherwise they MUST be omitted | INT-QUAL-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-QUAL-004 | Low-confidence outputs MUST include a \"Next Inputs Needed\" section | INT-QUAL-004 | P0 | 2026-01-13 | V1.1 | — |

### 6.2 Visual Quality

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-QUAL-010 | Charts MUST render correctly | INT-OUT-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-QUAL-011 | Tables MUST be readable | INT-OUT-006 | P0 | 2026-01-13 | V1.1 | — |
| BRD-QUAL-012 | HTML MUST display in modern browsers | INT-OUT-002, INT-OUT-011 | P0 | 2026-01-13 | V1.1 | — |

---

## 7. Version Transparency Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-VER-001 | Outputs MUST include product version, flow version, and schema version | INT-VER-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VER-002 | Outputs MUST record dataset hash and input parameter hash | INT-VER-002 | P1 | 2026-01-13 | V1.1 | — |
| BRD-VER-003 | Non-deterministic dependencies MUST be version-pinned or disallowed | INT-VER-003 | P0 | 2026-01-13 | V1.1 | — |

---

## 8. Decision Authority Boundary

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-DAB-001 | Outputs MUST be labeled as recommendations/findings, not decisions | INT-DAB-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DAB-002 | Decision packets MUST clarify human authority for final decisions | INT-DAB-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DAB-003 | Outputs MUST NOT trigger downstream actions without explicit approval | INT-DAB-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DAB-004 | Confidence language MUST avoid implying autonomous decisions | INT-DAB-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-DAB-005 | Recommendations MUST be presented as advisory | INT-DAB-001 | P0 | 2026-01-13 | V1.1 | — |

---

## 9. Failure Mode Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-FAIL-001 | ADE MUST fail fast when resolved intent is incompatible with the provided data structure; if the intent cannot be executed on the dataset (e.g., anomaly detection without numeric measures, trend analysis without time field), ADE SHALL halt and explain why | INT-FAIL-001 | P0 | 2026-01-21 | V1.3 | — |
| BRD-FAIL-002 | ADE MUST NOT proceed with analysis when required data dimensions are missing; execution SHALL be blocked with structured explanation of the gap | INT-FAIL-002 | P0 | 2026-01-21 | V1.3 | — |
| BRD-FAIL-003 | ADE MUST prohibit time-series or period-over-period analysis without explicit approval; ADE SHALL stop and request clarification before performing any temporal aggregation, trend analysis, or delta computation | INT-FAIL-003 | P0 | 2026-01-21 | V1.3 | — |

---

## 10. Framework Alignment Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-ALIGN-004 | ADE MUST separate reasoning and business conclusions from HTML or visualization rendering; reasoning artifacts SHALL be generated independently from presentation to ensure auditability and reuse | INT-ALIGN-004 | P0 | 2026-01-21 | V1.3 | — |
| BRD-FRI-006 | ADE MUST consume platform-provided semantic envelopes and validation outputs; ADE SHALL NOT re-implement semantic parsing, intent extraction, or validation logic inside product code | INT-FRI-006 | P0 | 2026-01-21 | V1.3 | — |

---

## Appendix: Technical Details (Removed from BRD)

### Output File Names (Technical Reference)
- business_report.html
- decision_packet.html
- ade.pdf

### Output Location (Technical Reference)
- staging/output/

### Output by Flow (Technical Reference)
| Output | Required | Description |
|--------|----------|-------------|
| business report output | Yes | Primary stakeholder report |
| decision packet output | Yes | Supporting decision summary |
