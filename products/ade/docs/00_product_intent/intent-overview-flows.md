# ADE Developer Intent

> **Document**: Product Developer Intent  
> **Product**: Analytical Decision Engine (ADE)  
> **Platform**: MASTER — Managed AI Systems for Trusted Execution & Reasoning  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release

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

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OVERVIEW-001** | Transform analyst questions into structured, audit-ready outputs | Core product value proposition |
| **INT-OVERVIEW-002** | Every claim must be traceable to source data | Trust requires evidence |
| **INT-OVERVIEW-003** | Same inputs must always produce same outputs | Audit and reproducibility requirement |
| **INT-OVERVIEW-004** | Confidence, assumptions, and limitations must be explicit | Transparency requirement |
| **INT-OVERVIEW-005** | Plans must require human approval before execution | Human oversight by design |
| **INT-OVERVIEW-006** | Analyst questions must be semantically interpreted | Enable natural language interaction |

### The One-Liner

> ADE accepts analyst questions and CSV datasets to produce audit-ready analytical decisions with evidence, confidence, and traceability.

## 1.3 Objectives

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OBJ-001** | 100% of outputs must include evidence references | Evidence-based requirement |
| **INT-OBJ-002** | Same inputs must always produce same outputs | Reproducibility requirement |
| **INT-OBJ-003** | All plans must require explicit user approval | Human-in-the-loop requirement |
| **INT-OBJ-004** | All outputs must include confidence_level, assumptions, limitations | Transparency requirement |
| **INT-OBJ-005** | Time from question to report should be < 5 minutes | Usability target |
| **INT-OBJ-006** | 4+ chart types must be available | Visualization richness |
| **INT-OBJ-007** | Hypothesis checks must be toggleable | Analysis flexibility |

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

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-FLOWS-001** | Provide two entry points for different analyst use cases | Flexibility for different workflows |
| **INT-FLOWS-002** | ade_v1 flow: analyst has a question to answer | Question-first workflow |
| **INT-FLOWS-003** | visualization flow: analyst has a dataset to explore | Dataset-first workflow |

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

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-V1-001** | User must be able to enter free-text questions | Natural language interaction |
| **INT-V1-002** | System must interpret intent from question | Semantic understanding |
| **INT-V1-003** | User must select dataset for analysis | Data source specification |
| **INT-V1-004** | User must configure visualization preferences | Customization |
| **INT-V1-005** | User must approve plan before execution | Human oversight |
| **INT-V1-006** | System must produce business report | Primary output |
| **INT-V1-007** | User should be able to enable/disable hypothesis checks | Analysis flexibility |
| **INT-V1-008** | User should be able to add notes to analysis | Documentation |

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

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-VIZ-001** | User must select dataset first | Dataset-first workflow |
| **INT-VIZ-002** | System must interpret intent from dataset context | Intelligent interpretation |
| **INT-VIZ-003** | User must provide visualization preferences | Explicit preferences |
| **INT-VIZ-004** | System must check data sufficiency | Quality gate |
| **INT-VIZ-005** | User must approve plan before execution | Human oversight |
| **INT-VIZ-006** | System must produce decision packet | Primary output |
| **INT-VIZ-007** | System must also produce business report | Secondary output |

## 2.4 User Interaction Intent

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-UI-001** | Visualization preferences must include chart_type | User control |
| **INT-UI-002** | Visualization preferences must include metric_focus | Analysis direction |
| **INT-UI-003** | Visualization preferences must include hypothesis_enabled flag | Optional analysis |
| **INT-UI-004** | Plan approval must show plan summary | Informed decision |
| **INT-UI-005** | Plan approval must allow approve/reject | Human control |
| **INT-UI-006** | Rejection must trigger replanning | Recovery path |

### Preference Options

| Preference | Options |
|------------|---------|
| Chart type | bar, line, area, scatter |
| Metric focus | mean, sum, median, growth_rate, anomalies |
| Hypothesis checks | enabled / disabled |
| Notes | Optional user annotations |

## 2.5 Determinism Intent

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-DET-001** | Flows must be deterministic | Reproducibility |
| **INT-DET-002** | Flows must use suggest_only autonomy | Framework compliance |
| **INT-DET-003** | Same inputs must produce same execution | Audit requirement |
| **INT-DET-004** | No dynamic flow mutation | Predictability |

---

