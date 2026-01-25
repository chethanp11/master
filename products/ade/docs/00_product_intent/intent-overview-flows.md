# ADE Developer Intent

> **Document**: Product Developer Intent  
> **Product**: Analytical Decision Engine (ADE)  
> **Platform**: MASTER — Managed AI Systems for Trusted Execution & Reasoning  
> **Last Updated**: 2026-01-21  
> **Status**: V1.3 Release

---

## Version Control

| Version | Date | Changes |
|---------|------|--------|
| 1.3 | 2026-01-21 | Added INT-OVERVIEW-007 (analysis-agnostic extensibility) |
| 1.2 | 2026-01-18 | Added INT-OBJ-008 |
| 1.1 | 2026-01-13 | Initial release |

---

## Scope

This file contains sections 1, 2 from the ADE Developer Intent.

---

# 1. Product Overview (INT-OVERVIEW)

> **Maps to**: [BRD-overview.md](../01_brd/BRD-overview.md)

## 1.1 The Problem We're Solving

### Analyst Pain Points

Analysts struggle to produce audit-ready analytical decisions because:

1. **Manual analysis is slow** — Extracting insights from data requires significant time and expertise
2. **Evidence is scattered** — Claims are made without clear traceability to source data
3. **Confidence is subjective** — No standardized way to express certainty in findings
4. **Reports lack structure** — Ad-hoc formats make comparison and audit difficult
5. **Reproducibility is impossible** — Same question on same data may yield different results

### What Doesn't Exist Today

There is no tool that:
- Accepts **free-text analyst questions** and produces structured outputs
- Provides **evidence-backed decisions** with full traceability
- Generates **audit-ready reports** with confidence levels and limitations
- Ensures **deterministic analysis** where same inputs always produce same outputs
- Supports **human oversight** through plan approval before execution

## 1.2 Core Intent

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-OVERVIEW-001** | Transform analyst questions into structured, audit-ready outputs — Core product value proposition | — | 2026-01-13 | V1.1 | — |
| **INT-OVERVIEW-002** | Every claim must be traceable to source data — Trust requires evidence | — | 2026-01-13 | V1.1 | — |
| **INT-OVERVIEW-003** | Same inputs must always produce same outputs — Audit and reproducibility requirement | — | 2026-01-13 | V1.1 | — |
| **INT-OVERVIEW-004** | Confidence, assumptions, and limitations must be explicit — Transparency requirement | — | 2026-01-13 | V1.1 | — |
| **INT-OVERVIEW-005** | Plans must require human approval before execution — Human oversight by design | — | 2026-01-13 | V1.1 | — |
| **INT-OVERVIEW-006** | Analyst questions must be semantically interpreted — Enable natural language interaction | — | 2026-01-13 | V1.1 | — |
| **INT-OVERVIEW-007** | ADE SHALL remain analysis-agnostic and extensible across use cases: ADE SHALL support exploratory analysis, risk review, fraud inspection, and business summarization without hard-coding a single analytical worldview — Analysis-agnostic extensibility | — | 2026-01-21 | V1.3 | Source: BULLET-10 |

### The One-Liner

> ADE accepts analyst questions and CSV datasets to produce audit-ready analytical decisions with evidence, confidence, and traceability.

## 1.3 Objectives

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-OBJ-001** | 100% of outputs must include evidence references — Evidence-based requirement | — | 2026-01-13 | V1.1 | — |
| **INT-OBJ-002** | Same inputs must always produce same outputs — Reproducibility requirement | — | 2026-01-13 | V1.1 | — |
| **INT-OBJ-003** | All plans must require explicit user approval — Human-in-the-loop requirement | — | 2026-01-13 | V1.1 | — |
| **INT-OBJ-004** | All outputs must include confidence_level, assumptions, limitations — Transparency requirement | — | 2026-01-13 | V1.1 | — |
| **INT-OBJ-005** | Time from question to report should be < 5 minutes — Usability target | — | 2026-01-13 | V1.1 | — |
| **INT-OBJ-006** | 4+ chart types must be available — Visualization richness | — | 2026-01-13 | V1.1 | — |
| **INT-OBJ-007** | Hypothesis checks must be toggleable — Analysis flexibility | — | 2026-01-13 | V1.1 | — |
| **INT-OBJ-008** | Objectives and success criteria SHALL be expressed through schemas and goals, not embedded logic or heuristics — Keep objectives explicit and auditable | — | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |

## 1.4 Scope

### In Scope

| Category | Intent |
|----------|--------|
| **Workflows** | Two entry points: question-first (ade_v1) and dataset-first (visualization) |
| **Inputs** | Free-text analyst questions and CSV datasets |
| **Outputs** | HTML business reports and decision packets |
| **User Interactions** | Visualization preferences and plan approval |
| **Analysis** | Anomaly detection, hypothesis testing, metric computation |

### Out of Scope (Non-Goals)

| Non-Goal | Rationale |
|----------|-----------|
| BI dashboarding platform | Decision packets are primary output |
| Live database connectors | CSV focus for MVP |
| Multi-dataset joins | Single dataset per analysis |
| Streaming analysis | Batch processing only |
| Dynamic flow mutation | Deterministic flows only |
| Automatic tool discovery | Explicit tool configuration |

## 1.5 Target Users

### Primary: Analysts

Business and data analysts who need to answer questions about data.

| Need | They Get |
|------|----------|
| Ask questions in natural language | Free-text question input |
| Get structured, professional reports | Business reports with evidence references |
| Trust the results with clear evidence | Confidence levels and limitations disclosed |

### Secondary: Decision Makers

Executives and managers who consume analytical outputs.

| Need | They Get |
|------|----------|
| Clear recommendations | Decision packets with audit trails |
| Confidence in findings | Executive summaries |
| Ability to trace claims to evidence | Evidence-backed key findings |

### Tertiary: Auditors

Compliance and audit teams who verify analytical integrity.

| Need | They Get |
|------|----------|
| Complete traceability | trace_refs linking decisions to steps |
| Reproducible results | evidence_refs linking claims to data |
| Documented assumptions | Explicit assumptions and limitations |

---

# 2. Flows (INT-FLOWS)

> **Maps to**: [BRD-flows.md](../01_brd/BRD-flows.md)

## 2.1 Flow Overview

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-FLOWS-001** | Provide two entry points for different analyst use cases — Flexibility for different workflows | — | 2026-01-13 | V1.1 | — |
| **INT-FLOWS-002** | ade_v1 flow: analyst has a question to answer — Question-first workflow | — | 2026-01-13 | V1.1 | — |
| **INT-FLOWS-003** | visualization flow: analyst has a dataset to explore — Dataset-first workflow | — | 2026-01-13 | V1.1 | — |

### Flow Summary

| Flow | Entry Point | Primary Output | Use Case |
|------|-------------|----------------|----------|
| `ade_v1` | Question/prompt | business_report.html | Analyst has a question |
| `visualization` | Dataset selection | decision_packet.html + business_report.html | Analyst has data to explore |

## 2.2 ade_v1 Flow Intent

### User Journey

```
Analyst Question → Dataset Selection → Visualization Preferences 
    → Plan Approval → Analysis → Report Generation
```

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-V1-001** | User must be able to enter free-text questions — Natural language interaction | — | 2026-01-13 | V1.1 | — |
| **INT-V1-002** | System must interpret intent from question — Semantic understanding | — | 2026-01-13 | V1.1 | — |
| **INT-V1-003** | User must select dataset for analysis — Data source specification | — | 2026-01-13 | V1.1 | — |
| **INT-V1-004** | User must configure visualization preferences — Customization | — | 2026-01-13 | V1.1 | — |
| **INT-V1-005** | User must approve plan before execution — Human oversight | — | 2026-01-13 | V1.1 | — |
| **INT-V1-006** | System must produce business report — Primary output | — | 2026-01-13 | V1.1 | — |
| **INT-V1-007** | User should be able to enable/disable hypothesis checks — Analysis flexibility | — | 2026-01-13 | V1.1 | — |
| **INT-V1-008** | User should be able to add notes to analysis — Documentation | — | 2026-01-13 | V1.1 | — |

### Inputs

| Input | Required | Intent |
|-------|----------|--------|
| `prompt` | Yes* | Analyst question (or intent/question/instructions) |
| `dataset` | Yes | Dataset name |
| `preferences` | Yes | Visualization preferences |

*One of prompt/intent/question/instructions is required.

## 2.3 visualization Flow Intent

### User Journey

```
Dataset Selection → Intent Interpretation → Visualization Preferences 
    → Sufficiency Check → Plan Approval → Analysis → Decision Packet
```

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-VIZ-001** | User must select dataset first — Dataset-first workflow | — | 2026-01-13 | V1.1 | — |
| **INT-VIZ-002** | System must interpret intent from dataset context — Intelligent interpretation | — | 2026-01-13 | V1.1 | — |
| **INT-VIZ-003** | User must provide visualization preferences — Explicit preferences | — | 2026-01-13 | V1.1 | — |
| **INT-VIZ-004** | System must check data sufficiency — Quality gate | — | 2026-01-13 | V1.1 | — |
| **INT-VIZ-005** | User must approve plan before execution — Human oversight | — | 2026-01-13 | V1.1 | — |
| **INT-VIZ-006** | System must produce decision packet — Primary output | — | 2026-01-13 | V1.1 | — |
| **INT-VIZ-007** | System must also produce business report — Secondary output | — | 2026-01-13 | V1.1 | — |

## 2.4 User Interaction Intent

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-UI-001** | Visualization preferences must include chart_type — User control | — | 2026-01-13 | V1.1 | — |
| **INT-UI-002** | Visualization preferences must include metric_focus — Analysis direction | — | 2026-01-13 | V1.1 | — |
| **INT-UI-003** | Visualization preferences must include hypothesis_enabled flag — Optional analysis | — | 2026-01-13 | V1.1 | — |
| **INT-UI-004** | Plan approval must show plan summary — Informed decision | — | 2026-01-13 | V1.1 | — |
| **INT-UI-005** | Plan approval must allow approve/reject — Human control | — | 2026-01-13 | V1.1 | — |
| **INT-UI-006** | Rejection must trigger replanning — Recovery path | — | 2026-01-13 | V1.1 | — |

### Preference Options

| Preference | Options |
|------------|---------|
| Chart type | bar, line, area, scatter |
| Metric focus | mean, sum, median, growth_rate, anomalies |
| Hypothesis checks | enabled / disabled |
| Notes | Optional user annotations |

## 2.5 Determinism Intent

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-DET-001** | Flows must be deterministic — Reproducibility | — | 2026-01-13 | V1.1 | — |
| **INT-DET-002** | Flows must use suggest_only autonomy — Framework compliance | — | 2026-01-13 | V1.1 | — |
| **INT-DET-003** | Same inputs must produce same execution — Audit requirement | — | 2026-01-13 | V1.1 | — |

---
