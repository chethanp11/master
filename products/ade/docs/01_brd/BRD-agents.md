# ADE Agent Business Requirements

> **Document**: Business Requirements — Agents  
> **Version**: 1.0.0

---

## 1. Agent Overview

Agents provide reasoning roles in ADE workflows:

| Agent | Role | Flows |
|-------|------|-------|
| `intent_agent` | Interpret user questions | ade_v1 |
| `plan_agent` | Create analysis plans | ade_v1 |
| `plan_proposal_agent` | Generate approval requests | Both |
| `planning_agent` | Interpret intent, handle replanning | visualization |
| `sufficiency_evaluator` | Assess data quality | Both |
| `dashboard_agent` | Generate narrative summaries | Both |

---

## 2. Intent Interpretation Requirements

### 2.1 intent_agent

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-INTENT-001 | System MUST extract intent summary from user question | P0 |
| BRD-INTENT-002 | System MUST identify referenced datasets | P0 |
| BRD-INTENT-003 | System MUST identify referenced metrics | P1 |
| BRD-INTENT-004 | System MUST identify time window constraints | P1 |
| BRD-INTENT-005 | System MUST provide confidence score (0-1) | P0 |
| BRD-INTENT-006 | System MUST detect when clarification is needed | P0 |
| BRD-INTENT-007 | System MUST generate clarifying questions | P1 |

### 2.2 planning_agent

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-PLANNING-001 | System MUST interpret intent from dataset context | P0 |
| BRD-PLANNING-002 | System MUST support replanning after rejection | P1 |
| BRD-PLANNING-003 | System MUST identify restart step after replan | P1 |

---

## 3. Plan Generation Requirements

### 3.1 plan_agent

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-PLANGEN-001 | System MUST produce deterministic plans | P0 |
| BRD-PLANGEN-002 | Plans MUST include all required analysis steps | P0 |
| BRD-PLANGEN-003 | Plans MUST include tool flags for conditional execution | P1 |
| BRD-PLANGEN-004 | Same inputs MUST produce same plan | P0 |

### 3.2 plan_proposal_agent

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-PROPOSAL-001 | System MUST generate human-readable plan summary | P0 |
| BRD-PROPOSAL-002 | System MUST estimate step count | P1 |
| BRD-PROPOSAL-003 | System MUST estimate execution cost | P1 |
| BRD-PROPOSAL-004 | System MUST require approval for non-trivial plans | P0 |

---

## 4. Data Quality Assessment Requirements

### 4.1 sufficiency_evaluator

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-SUFF-001 | System MUST assess data sufficiency | P0 |
| BRD-SUFF-002 | System MUST provide confidence level (high/medium/low) | P0 |
| BRD-SUFF-003 | System MUST explain confidence downgrades | P1 |
| BRD-SUFF-004 | System SHOULD evaluate row count sufficiency | P1 |
| BRD-SUFF-005 | System SHOULD evaluate column completeness | P1 |
| BRD-SUFF-006 | System SHOULD evaluate data freshness | P2 |

---

## 5. Narrative Generation Requirements

### 5.1 dashboard_agent

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-NARR-001 | System MUST generate human-readable narrative | P1 |
| BRD-NARR-002 | Narrative MUST summarize key dataset characteristics | P1 |
| BRD-NARR-003 | Narrative SHOULD be concise (< 500 words) | P2 |

---

## 6. Confidence and Transparency Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-CONF-001 | All agents MUST provide confidence indicators | P0 |
| BRD-CONF-002 | Confidence MUST be explainable | P1 |
| BRD-CONF-003 | Low confidence MUST trigger clarification | P0 |
| BRD-CONF-004 | Confidence labels MUST use standard values | P0 |

**Standard Confidence Labels**: "high", "medium", "low"

---

## 7. Agent Cost Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-COST-001 | All agents MUST have cost hints | P1 |
| BRD-COST-002 | Cost hints MUST be accurate | P1 |
| BRD-COST-003 | Cost hints MUST be exposed in descriptors | P1 |

---

## Cross-References

- **Techspec**: [AGENT-agents.md](../02_techspec/AGENT-agents.md)
- **System Design**: [agents-and-tools.md](../04_systemdesign/agents-and-tools.md)
