# ADE Product Overview

> **Document**: Business Requirements — Overview  
> **Version**: 1.0.0

---

## 1. Product Vision

The **Analytical Decision Engine (ADE)** transforms analyst questions and CSV datasets into structured, audit-ready business outputs. ADE produces decision packets and business reports with embedded evidence, confidence levels, and full traceability.

### 1.1 Core Intent Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-OVERVIEW-001 | ADE MUST transform analyst questions into structured, audit-ready outputs | Derived from: INT-OVERVIEW-001 | P0 | 2026-01-13 | V1.1 |
| BRD-OVERVIEW-002 | Every claim MUST be traceable to source data | Derived from: INT-OVERVIEW-002 | P0 | 2026-01-13 | V1.1 |
| BRD-OVERVIEW-003 | Same inputs MUST always produce same outputs | Derived from: INT-OVERVIEW-003 | P0 | 2026-01-13 | V1.1 |
| BRD-OVERVIEW-004 | Confidence, assumptions, and limitations MUST be explicit in outputs | Derived from: INT-OVERVIEW-004 | P0 | 2026-01-13 | V1.1 |
| BRD-OVERVIEW-005 | Plans MUST require human approval before execution | Derived from: INT-OVERVIEW-005 | P0 | 2026-01-13 | V1.1 |
| BRD-OVERVIEW-006 | Analyst questions MUST be semantically interpreted before planning | Derived from: INT-OVERVIEW-006 | P0 | 2026-01-13 | V1.1 |

---

## 2. Objectives

### 2.1 Primary Objectives

| ID | Objective | Derived from | Success Metric |
|----|-----------|--------------|----------------|
| BRD-OBJ-001 | Produce audit-ready analytical decisions | Derived from: INT-OBJ-001 | 100% of outputs include evidence references |
| BRD-OBJ-002 | Enable deterministic, reproducible analysis | Derived from: INT-OBJ-002 | Same inputs always produce same outputs |
| BRD-OBJ-003 | Support human oversight through plan approval | Derived from: INT-OBJ-003 | All plans require explicit user approval |
| BRD-OBJ-004 | Provide clear confidence and limitations | Derived from: INT-OBJ-004 | All outputs include confidence_level, assumptions, limitations |

### 2.2 Secondary Objectives

| ID | Objective | Derived from | Success Metric |
|----|-----------|--------------|----------------|
| BRD-OBJ-005 | Minimize time-to-insight for analysts | Derived from: INT-OBJ-005 | < 5 minutes from question to report |
| BRD-OBJ-006 | Support multiple visualization types | Derived from: INT-OBJ-006 | 4+ chart types available |
| BRD-OBJ-007 | Enable hypothesis testing when needed | Derived from: INT-OBJ-007 | Hypothesis checks are toggleable |
| BRD-OBJ-008 | Objectives and success criteria MUST be expressed through schemas and goals, not embedded logic or heuristics | Derived from: INT-OBJ-008 | Objectives are schema-backed and externally auditable |

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

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-ALIGN-001 | Product reasoning MUST rely on framework primitives | Derived from: INT-ALIGN-001 | P0 | 2026-01-13 | V1.1 |
| BRD-ALIGN-002 | Product requirements that bypass framework primitives MUST be treated as framework gaps | Derived from: INT-ALIGN-002 | P0 | 2026-01-13 | V1.1 |
| BRD-ALIGN-003 | ADE MUST consume platform-provided reasoning outputs without altering structure or semantics | Derived from: INT-ALIGN-003 | P0 | 2026-01-13 | V1.1 |

### 8.2 Framework Reliance Invariant

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-FRI-001 | Product MUST NOT re-implement orchestrator logic | Derived from: INT-FRI-001 | P0 | 2026-01-13 | V1.1 |
| BRD-FRI-002 | Product MUST NOT re-implement iteration control | Derived from: INT-FRI-002 | P0 | 2026-01-13 | V1.1 |
| BRD-FRI-003 | Product MUST NOT re-implement reasoning ladder semantics | Derived from: INT-FRI-003 | P0 | 2026-01-13 | V1.1 |
| BRD-FRI-004 | Product MUST NOT bypass framework governance hooks | Derived from: INT-FRI-004 | P0 | 2026-01-13 | V1.1 |
| BRD-FRI-005 | Framework gaps MUST be escalated, not worked around | Derived from: INT-FRI-005 | P0 | 2026-01-13 | V1.1 |

### 8.3 No Runtime Learning

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-NRL-001 | Product MUST NOT modify behavior at runtime based on prior runs | Derived from: INT-NRL-001 | P0 | 2026-01-13 | V1.1 |
| BRD-NRL-002 | Product MUST NOT persist learned patterns across runs | Derived from: INT-NRL-002 | P0 | 2026-01-13 | V1.1 |
| BRD-NRL-003 | Product evolution MUST happen through intent → BRD → implementation | Derived from: INT-NRL-003 | P0 | 2026-01-13 | V1.1 |
| BRD-NRL-004 | Identical inputs MUST produce identical outputs across runs | Derived from: INT-NRL-004 | P0 | 2026-01-13 | V1.1 |

---

## Cross-References

- **Techspec**: [README.md](../02_techspec/README.md)
- **System Design**: [architecture.md](../04_systemdesign/architecture.md)
