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

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-V1-001 | User MUST be able to enter free-text question | P0 |
| BRD-V1-002 | System MUST interpret intent from question | P0 |
| BRD-V1-003 | User MUST select dataset for analysis | P0 |
| BRD-V1-004 | User MUST configure visualization preferences | P0 |
| BRD-V1-005 | User MUST approve plan before execution | P0 |
| BRD-V1-006 | System MUST produce business report | P0 |
| BRD-V1-007 | User SHOULD be able to enable/disable hypothesis checks | P1 |
| BRD-V1-008 | User SHOULD be able to add notes to analysis | P2 |

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

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-VIZ-001 | User MUST select dataset first | P0 |
| BRD-VIZ-002 | System MUST interpret dataset-based intent | P0 |
| BRD-VIZ-003 | User MUST configure visualization preferences | P0 |
| BRD-VIZ-004 | System MUST evaluate data sufficiency | P0 |
| BRD-VIZ-005 | User MUST approve plan before execution | P0 |
| BRD-VIZ-006 | System MUST produce decision packet | P0 |
| BRD-VIZ-007 | System MUST produce business report | P0 |
| BRD-VIZ-008 | User SHOULD be able to toggle hypothesis checks | P1 |

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

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-PREF-001 | User MUST select chart type | P0 |
| BRD-PREF-002 | User MUST select metric focus | P0 |
| BRD-PREF-003 | User SHOULD be able to toggle hypothesis checks | P1 |
| BRD-PREF-004 | User MAY add notes | P2 |

**Chart Types**: bar, line, area, scatter

**Metric Focus Options**: mean, sum, median, growth_rate, anomalies

### 4.2 Plan Approval

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-PLAN-001 | System MUST present plan summary before execution | P0 |
| BRD-PLAN-002 | System MUST show estimated steps | P1 |
| BRD-PLAN-003 | System MUST show estimated cost | P1 |
| BRD-PLAN-004 | User MUST be able to approve plan | P0 |
| BRD-PLAN-005 | User MUST be able to reject plan | P0 |
| BRD-PLAN-006 | Rejection SHOULD trigger replanning | P1 |
| BRD-PLAN-007 | Plan summary MUST include objective and expected evidence | P1 |
| BRD-PLAN-008 | Plan summary MUST include assumptions and risks | P1 |
| BRD-PLAN-009 | Replan output MUST highlight what changed and why | P1 |

---

## 5. Determinism Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-DET-001 | Same inputs MUST produce same outputs | P0 |
| BRD-DET-002 | No random variations in analysis | P0 |
| BRD-DET-003 | Timestamps are the only allowed variation | P0 |
| BRD-DET-004 | No LLM calls from tools | P0 |
| BRD-DET-005 | Flows MUST NOT mutate dynamically at runtime | P0 |

---

## 6. Flow Configuration Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-CFG-001 | Flows MUST use suggest_only autonomy level | P0 |
| BRD-CFG-002 | Data reading SHOULD have retry configuration | P1 |
| BRD-CFG-003 | Chart building SHOULD have fallback type | P1 |

---

## 7. Terminal Outcomes and Safe Exits

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-TERM-001 | System MUST support explicit outcomes: SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT | P0 |
| BRD-TERM-002 | PARTIAL_SUCCESS outputs MUST include limitations and unresolved gaps | P1 |
| BRD-TERM-003 | ABORT outcomes MUST include reason codes and recommended next actions | P0 |
| BRD-TERM-004 | ASK_USER MUST be used when missing inputs are resolvable via clarification | P0 |
| BRD-STOP-001 | System MUST prefer safe exits over forced outputs | P0 |
| BRD-STOP-002 | Low signal or conflicting evidence MUST result in safe exit | P0 |

---

## Cross-References

- **Techspec**: [FLOW-flows.md](../02_techspec/FLOW-flows.md)
- **System Design**: [flows.md](../04_systemdesign/flows.md)
