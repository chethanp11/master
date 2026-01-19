# ADE Flow Business Requirements

> **Document**: Business Requirements — Flows  
> **Version**: 1.0.0

---

## 1. Flow Overview

ADE provides two workflows optimized for different use cases:

| Flow | Use Case | Entry Point |
|------|----------|-------------|
| `ade_v1` | Analyst has a question to answer | Question/prompt |
| `visualization` | Analyst has a dataset to explore | Dataset selection |

### 1.1 Flow Coverage Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-FLOW-001 | ADE MUST provide two entry points for different analyst use cases | Derived from: INT-FLOWS-001 | P0 | 2026-01-13 | V1.1 |
| BRD-FLOW-002 | ade_v1 flow MUST support question-first workflow | Derived from: INT-FLOWS-002 | P0 | 2026-01-13 | V1.1 |
| BRD-FLOW-003 | visualization flow MUST support dataset-first workflow | Derived from: INT-FLOWS-003 | P0 | 2026-01-13 | V1.1 |

---

## 2. ade_v1 Flow Requirements

### 2.1 Purpose

Enable analysts to ask free-text questions and receive structured business reports with evidence-backed decisions.

### 2.2 User Journey

```
Analyst Question → Dataset Selection → Visualization Preferences 
    → Plan Approval → Analysis → Report Generation
```

### 2.3 Business Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-V1-001 | User MUST be able to enter free-text question | Derived from: INT-V1-001 | P0 | 2026-01-13 | V1.1 |
| BRD-V1-002 | System MUST interpret intent from question | Derived from: INT-V1-002 | P0 | 2026-01-13 | V1.1 |
| BRD-V1-003 | User MUST select dataset for analysis | Derived from: INT-V1-003 | P0 | 2026-01-13 | V1.1 |
| BRD-V1-004 | User MUST configure visualization preferences | Derived from: INT-V1-004 | P0 | 2026-01-13 | V1.1 |
| BRD-V1-005 | User MUST approve plan before execution | Derived from: INT-V1-005 | P0 | 2026-01-13 | V1.1 |
| BRD-V1-006 | System MUST produce business report | Derived from: INT-V1-006 | P0 | 2026-01-13 | V1.1 |
| BRD-V1-007 | User SHOULD be able to enable/disable hypothesis checks | Derived from: INT-V1-007 | P1 | 2026-01-13 | V1.1 |
| BRD-V1-008 | User SHOULD be able to add notes to analysis | Derived from: INT-V1-008 | P2 | 2026-01-13 | V1.1 |

### 2.4 Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | Yes* | Analyst question |
| `dataset` | string | Yes | Dataset name |
| `intent` | string | No | Alternate intent field |
| `question` | string | No | Alternate question field |
| `instructions` | string | No | Alternate instructions field |

*One of prompt/intent/question/instructions is required.

### 2.5 Outputs

| Output | Format | Description |
|--------|--------|-------------|
| business_report.html | HTML | Primary stakeholder report |

---

## 3. visualization Flow Requirements

### 3.1 Purpose

Enable analysts to explore a dataset with explicit visualization preferences and receive decision packets with hypothesis testing.

### 3.2 User Journey

```
Dataset Selection → Intent Interpretation → Visualization Preferences 
    → Sufficiency Check → Plan Approval → Analysis → Decision Packet
```

### 3.3 Business Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-VIZ-001 | User MUST select dataset first | Derived from: INT-VIZ-001 | P0 | 2026-01-13 | V1.1 |
| BRD-VIZ-002 | System MUST interpret dataset-based intent | Derived from: INT-VIZ-002 | P0 | 2026-01-13 | V1.1 |
| BRD-VIZ-003 | User MUST configure visualization preferences | Derived from: INT-VIZ-003 | P0 | 2026-01-13 | V1.1 |
| BRD-VIZ-004 | System MUST evaluate data sufficiency | Derived from: INT-VIZ-004 | P0 | 2026-01-13 | V1.1 |
| BRD-VIZ-005 | User MUST approve plan before execution | Derived from: INT-VIZ-005 | P0 | 2026-01-13 | V1.1 |
| BRD-VIZ-006 | System MUST produce decision packet | Derived from: INT-VIZ-006 | P0 | 2026-01-13 | V1.1 |
| BRD-VIZ-007 | System MUST produce business report | Derived from: INT-VIZ-007 | P0 | 2026-01-13 | V1.1 |
| BRD-VIZ-008 | User SHOULD be able to toggle hypothesis checks | Derived from: INT-UI-003 | P1 | 2026-01-13 | V1.1 |

### 3.4 Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset` | string | Yes | Dataset name |
| `prompt` | string | No | Optional context |

### 3.5 Outputs

| Output | Format | Description |
|--------|--------|-------------|
| business_report.html | HTML | Primary stakeholder report |
| decision_packet.html | HTML | Supporting decision summary |

---

## 4. User Interaction Requirements

### 4.1 Visualization Preferences

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-PREF-001 | User MUST select chart type | Derived from: INT-UI-001 | P0 | 2026-01-13 | V1.1 |
| BRD-PREF-002 | User MUST select metric focus | Derived from: INT-UI-002 | P0 | 2026-01-13 | V1.1 |
| BRD-PREF-003 | User SHOULD be able to toggle hypothesis checks | Derived from: INT-UI-003 | P1 | 2026-01-13 | V1.1 |
| BRD-PREF-004 | User MAY add notes | Derived from: INT-V1-008 | P2 | 2026-01-13 | V1.1 |

**Chart Types**: bar, line, area, scatter

**Metric Focus Options**: mean, sum, median, growth_rate, anomalies

### 4.2 Plan Approval

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-PLAN-001 | System MUST present plan summary before execution | Derived from: INT-UI-004, INT-PLAN-005 | P0 | 2026-01-13 | V1.1 |
| BRD-PLAN-002 | System MUST show estimated steps | Derived from: INT-PLAN-006 | P1 | 2026-01-13 | V1.1 |
| BRD-PLAN-003 | System MUST show estimated cost | Derived from: INT-PLAN-007 | P1 | 2026-01-13 | V1.1 |
| BRD-PLAN-004 | User MUST be able to approve plan | Derived from: INT-UI-005 | P0 | 2026-01-13 | V1.1 |
| BRD-PLAN-005 | User MUST be able to reject plan | Derived from: INT-UI-005 | P0 | 2026-01-13 | V1.1 |
| BRD-PLAN-006 | Rejection SHOULD trigger replanning | Derived from: INT-UI-006 | P1 | 2026-01-13 | V1.1 |
| BRD-PLAN-007 | Plan summary MUST include objective and expected evidence | Derived from: INT-REVIEW-001 | P1 | 2026-01-13 | V1.1 |
| BRD-PLAN-008 | Plan summary MUST include assumptions and risks | Derived from: INT-REVIEW-001 | P1 | 2026-01-13 | V1.1 |
| BRD-PLAN-009 | Replan output MUST highlight what changed and why | Derived from: INT-REVIEW-003 | P1 | 2026-01-13 | V1.1 |
| BRD-PLAN-010 | Users MUST be able to approve plans with constraints (time window, iteration caps, disabled tests) | Derived from: INT-REVIEW-002 | P1 | 2026-01-13 | V1.1 |

---

## 5. Determinism Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-DET-001 | Same inputs MUST produce same outputs | Derived from: INT-DET-001, INT-DET-003 | P0 | 2026-01-13 | V1.1 |
| BRD-DET-002 | No random variations in analysis | Derived from: INT-REPRO-003 | P0 | 2026-01-13 | V1.1 |
| BRD-DET-003 | Timestamps are the only allowed variation | Derived from: INT-REPRO-002 | P0 | 2026-01-13 | V1.1 |
| BRD-DET-004 | No LLM calls from tools | Derived from: INT-TOOL-002 | P0 | 2026-01-13 | V1.1 |

---

## 6. Flow Configuration Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| BRD-CFG-001 | Flows MUST use suggest_only autonomy level | Derived from: INT-DET-002 | P0 | 2026-01-13 | V1.1 |

---

## Cross-References

- **Techspec**: [FLOW-flows.md](../02_techspec/FLOW-flows.md)
- **System Design**: [flows.md](../04_systemdesign/flows.md)
