# ADE Flow Business Requirements

> **Document**: Business Requirements — Flows  
> **Version**: V1.2  
> **Last Updated**: 2026-01-19

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial release |
| V1.2 | 2026-01-19 | Standardized tables, removed TSD-level detail, and aligned intent traceability |

## 1. Flow Overview

ADE provides two workflows optimized for different use cases:
### 1.1 Flow Coverage Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-FLOW-001 | ADE MUST provide two entry points for different analyst use cases | INT-FLOWS-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-FLOW-002 | ade_v1 flow MUST support question-first workflow | INT-FLOWS-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-FLOW-003 | visualization flow MUST support dataset-first workflow | INT-FLOWS-003 | P0 | 2026-01-13 | V1.1 | — |

---

## 2. ade_v1 Flow Requirements

### 2.1 Purpose

Enable analysts to ask free-text questions and receive structured business reports with evidence-backed decisions.

### 2.3 Business Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-V1-001 | User MUST be able to enter free-text question | INT-V1-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-V1-002 | System MUST interpret intent from question | INT-V1-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-V1-003 | User MUST select dataset for analysis | INT-V1-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-V1-004 | User MUST configure visualization preferences | INT-V1-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-V1-005 | User MUST approve plan before execution | INT-V1-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-V1-006 | System MUST produce business report | INT-V1-006 | P0 | 2026-01-13 | V1.1 | — |
| BRD-V1-007 | User SHOULD be able to enable/disable hypothesis checks | INT-V1-007 | P1 | 2026-01-13 | V1.1 | — |
| BRD-V1-008 | User SHOULD be able to add notes to analysis | INT-V1-008 | P2 | 2026-01-13 | V1.1 | — |

---

## 3. visualization Flow Requirements

### 3.1 Purpose

Enable analysts to explore a dataset with explicit visualization preferences and receive decision packets with hypothesis testing.

### 3.3 Business Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-VIZ-001 | User MUST select dataset first | INT-VIZ-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VIZ-002 | System MUST interpret dataset-based intent | INT-VIZ-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VIZ-003 | User MUST configure visualization preferences | INT-VIZ-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VIZ-004 | System MUST evaluate data sufficiency | INT-VIZ-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VIZ-005 | User MUST approve plan before execution | INT-VIZ-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VIZ-006 | System MUST produce decision packet | INT-VIZ-006 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VIZ-007 | System MUST produce business report | INT-VIZ-007 | P0 | 2026-01-13 | V1.1 | — |
| BRD-VIZ-008 | User SHOULD be able to toggle hypothesis checks | INT-UI-003 | P1 | 2026-01-13 | V1.1 | — |

---

## 4. User Interaction Requirements

### 4.1 Visualization Preferences

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-PREF-001 | User MUST select chart type | INT-UI-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PREF-002 | User MUST select metric focus | INT-UI-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PREF-003 | User SHOULD be able to toggle hypothesis checks | INT-UI-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PREF-004 | User MAY add notes | INT-V1-008 | P2 | 2026-01-13 | V1.1 | — |

### 4.2 Plan Approval

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-PLAN-001 | System MUST present plan summary before execution | INT-UI-004, INT-PLAN-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PLAN-002 | System MUST show estimated steps | INT-PLAN-006 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PLAN-003 | System MUST show estimated cost | INT-PLAN-007 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PLAN-004 | User MUST be able to approve plan | INT-UI-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PLAN-005 | User MUST be able to reject plan | INT-UI-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PLAN-006 | Rejection SHOULD trigger replanning | INT-UI-006 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PLAN-007 | Plan summary MUST include objective and expected evidence | INT-REVIEW-001 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PLAN-008 | Plan summary MUST include assumptions and risks | INT-REVIEW-001 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PLAN-009 | Replan output MUST highlight what changed and why | INT-REVIEW-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PLAN-010 | Users MUST be able to approve plans with constraints (time window, iteration caps, disabled tests) | INT-REVIEW-002 | P1 | 2026-01-13 | V1.1 | — |

---

## 5. Determinism Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-DET-001 | Same inputs MUST produce same outputs | INT-DET-001, INT-DET-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DET-002 | No random variations in analysis | INT-REPRO-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DET-003 | Timestamps are the only allowed variation | INT-REPRO-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-DET-004 | No LLM calls from tools | INT-TOOL-002 | P0 | 2026-01-13 | V1.1 | — |

---

## 6. Flow Configuration Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-CFG-001 | Flows MUST use suggest_only autonomy level | INT-DET-002 | P0 | 2026-01-13 | V1.1 | — |

---

## Appendix: Technical Details (Removed from BRD)

### Flow Overview (Technical Reference)
| Flow | Use Case | Entry Point |
|------|----------|-------------|
| `ade_v1` | Analyst has a question to answer | Question/prompt |
| `visualization` | Analyst has a dataset to explore | Dataset selection |

### ade_v1 User Journey (Technical Reference)
```
Analyst Question → Dataset Selection → Visualization Preferences 
    → Plan Approval → Analysis → Report Generation
```

### visualization User Journey (Technical Reference)
```
Dataset Selection → Intent Interpretation → Visualization Preferences 
    → Sufficiency Check → Plan Approval → Analysis → Decision Packet
```

### ade_v1 Inputs (Technical Reference)
| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | Yes* | Analyst question |
| `dataset` | string | Yes | Dataset name |
| `intent` | string | No | Alternate intent field |
| `question` | string | No | Alternate question field |
| `instructions` | string | No | Alternate instructions field |

*One of prompt/intent/question/instructions is required.

### ade_v1 Outputs (Technical Reference)
| Output | Format | Description |
|--------|--------|-------------|
| business_report.html | HTML | Primary stakeholder report |

### visualization Inputs (Technical Reference)
| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset` | string | Yes | Dataset name |
| `prompt` | string | No | Optional context |

### visualization Outputs (Technical Reference)
| Output | Format | Description |
|--------|--------|-------------|
| business_report.html | HTML | Primary stakeholder report |
| decision_packet.html | HTML | Supporting decision summary |

### Visualization Preference Options (Technical Reference)
- Chart Types: bar, line, area, scatter
- Metric Focus Options: mean, sum, median, growth_rate, anomalies
