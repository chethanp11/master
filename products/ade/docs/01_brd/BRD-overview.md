# ADE Product Overview

> **Document**: Business Requirements — Overview  
> **Version**: 1.0.0

---

## 1. Product Vision

The **Analytical Decision Engine (ADE)** transforms analyst questions and CSV datasets into structured, audit-ready business outputs. ADE produces decision packets and business reports with embedded evidence, confidence levels, and full traceability.

---

## 2. Objectives

### 2.1 Primary Objectives

| ID | Objective | Success Metric |
|----|-----------|----------------|
| OBJ-001 | Produce audit-ready analytical decisions | 100% of outputs include evidence references |
| OBJ-002 | Enable deterministic, reproducible analysis | Same inputs always produce same outputs |
| OBJ-003 | Support human oversight through plan approval | All plans require explicit user approval |
| OBJ-004 | Provide clear confidence and limitations | All outputs include confidence_level, assumptions, limitations |

### 2.2 Secondary Objectives

| ID | Objective | Success Metric |
|----|-----------|----------------|
| OBJ-005 | Minimize time-to-insight for analysts | < 5 minutes from question to report |
| OBJ-006 | Support multiple visualization types | 4+ chart types available |
| OBJ-007 | Enable hypothesis testing when needed | Hypothesis checks are toggleable |

---

## 3. Scope

### 3.1 In Scope

| Category | Items |
|----------|-------|
| **Workflows** | ade_v1 (free-text), visualization (dataset-first) |
| **Inputs** | Analyst questions, CSV datasets |
| **Outputs** | business_report.html, decision_packet.html |
| **User Interactions** | Visualization preferences, plan approval |
| **Analysis** | Anomaly detection, hypothesis testing, metric computation |

### 3.2 Out of Scope

| Category | Exclusion | Rationale |
|----------|-----------|-----------|
| **Data Sources** | Live database connectors | Focus on CSV for MVP |
| **Data Sources** | Streaming inputs | Batch processing only |
| **Data Operations** | Multi-dataset joins | Single dataset per run |
| **System Behavior** | Dynamic flow mutation | Deterministic flows only |
| **Product Surface** | BI dashboarding | Decision packets are primary |

---

## 4. Stakeholders

| Role | Interest | Engagement |
|------|----------|------------|
| **Analysts** | Use ADE to answer business questions | Primary users |
| **Decision Makers** | Review decision packets for approval | Consumers of outputs |
| **Auditors** | Verify evidence and reasoning | Review trace references |
| **Engineers** | Build and maintain ADE | Implementers |

---

## 5. Key Capabilities

### 5.1 Intent Interpretation

ADE interprets analyst questions to extract:
- Intent summary
- Dataset and metric references
- Time window constraints
- Clarification needs

### 5.2 Plan Approval

Before execution, ADE presents a plan proposal including:
- Summary of planned analysis
- Estimated steps and cost
- Requires explicit user approval

### 5.3 Evidence-Based Analysis

All outputs include:
- Evidence references linking claims to data
- Trace references linking decisions to steps
- Confidence levels for all assertions

### 5.4 Hypothesis Testing

Optional hypothesis tests evaluate alternative explanations:
- Data outage patterns
- Seasonality signals

---

## 6. Trust and Audit Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Reproducibility** | Deterministic tools; no LLM calls from tools |
| **Evidence Provenance** | evidence_refs in all decision sections |
| **Trace References** | trace_refs link decisions to step outputs |
| **Explicit Assumptions** | Listed in DecisionPacket.assumptions |
| **Explicit Limitations** | Listed in DecisionPacket.limitations |

---

## 7. Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| All outputs pass schema validation | 100% Pydantic validation pass rate |
| All claims have evidence | evidence_refs.length > 0 for all sections |
| Plans require approval | requires_approval = true for all plan proposals |
| Hypothesis checks are toggleable | include_hypothesis_checks parameter respected |
| Confidence is always present | confidence_level non-empty in all packets |

---

## 8. Framework Alignment and Runtime Constraints

### 8.1 Framework Alignment

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-ALIGN-001 | Product reasoning MUST rely on framework primitives | P0 |
| BRD-ALIGN-002 | Product requirements that bypass framework primitives MUST be treated as framework gaps | P0 |

### 8.2 Framework Reliance Invariant

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-FRI-001 | Product MUST NOT re-implement orchestrator logic | P0 |
| BRD-FRI-002 | Product MUST NOT re-implement iteration control | P0 |
| BRD-FRI-003 | Product MUST NOT re-implement reasoning ladder semantics | P0 |
| BRD-FRI-004 | Product MUST NOT bypass framework governance hooks | P0 |
| BRD-FRI-005 | Framework gaps MUST be escalated, not worked around | P0 |

### 8.3 No Runtime Learning

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-NRL-001 | Product MUST NOT modify behavior at runtime based on prior runs | P0 |
| BRD-NRL-002 | Product MUST NOT persist learned patterns across runs | P0 |
| BRD-NRL-003 | Product evolution MUST happen through intent → BRD → implementation | P0 |
| BRD-NRL-004 | Identical inputs MUST produce identical outputs across runs | P0 |

---

## Cross-References

- **Techspec**: [README.md](../02_techspec/README.md)
- **System Design**: [architecture.md](../04_systemdesign/architecture.md)
