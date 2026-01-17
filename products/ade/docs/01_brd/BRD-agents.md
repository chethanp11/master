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

## 1.1 Advisory Boundary Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-AGT-001 | Agents MUST be advisory only (no direct execution) | P0 |
| BRD-AGT-002 | Agents MUST propose, never execute tools or change state | P0 |
| BRD-AGT-003 | Agents MUST produce structured outputs | P0 |
| BRD-AGT-004 | Agent reasoning MUST be auditable and traceable | P0 |

---

## 1.2 Reasoning Ladder Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-INTEL-001 | System MUST use multi-stage reasoning (interpret → propose → critique → finalize) | P0 |
| BRD-INTEL-002 | Each reasoning stage MUST be explicit and observable | P0 |
| BRD-INTEL-003 | Reasoning cycles MUST be bounded by limits (iterations/tools/time) | P0 |
| BRD-INTEL-004 | Reasoning MUST track sufficiency state across cycles | P1 |
| BRD-INTEL-005 | Final outputs MUST state why reasoning stopped | P1 |

---

## 1.3 Critique Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-CRIT-001 | System MUST run critique before finalizing outputs | P0 |
| BRD-CRIT-002 | Critique MUST identify missing or weak evidence | P0 |
| BRD-CRIT-003 | Critique MUST be able to downgrade confidence with reasons | P1 |
| BRD-CRIT-004 | Critique MUST remain advisory (no execution or routing) | P0 |
| BRD-CRIT-005 | Blocking critique findings MUST trigger clarification or safe abort | P0 |

---

## 1.4 Advisory Tool Selection

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-TOOLSEL-001 | Tool selection MUST be surfaced as advisory recommendations | P1 |
| BRD-TOOLSEL-002 | Tool recommendations MAY be ranked with rationales | P2 |
| BRD-TOOLSEL-003 | Orchestrator MUST remain the sole authority for tool execution | P0 |
| BRD-TOOLSEL-004 | Advisory tool suggestions MUST NOT force execution | P0 |

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
| BRD-NARR-004 | Narrative SHOULD include anomaly interpretation when present | P1 |

---

## 6. Confidence and Transparency Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-CONF-001 | All agents MUST provide confidence indicators | P0 |
| BRD-CONF-002 | Confidence MUST be explainable | P1 |
| BRD-CONF-003 | Low confidence MUST trigger clarification | P0 |
| BRD-CONF-004 | Confidence labels MUST use standard values | P0 |
| BRD-CONF-005 | Confidence thresholds MUST be configurable | P1 |

**Standard Confidence Labels**: "high", "medium", "low"

---

## 7. Agent Cost Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-COST-001 | All agents MUST have cost hints | P1 |
| BRD-COST-002 | Cost hints MUST be accurate | P1 |
| BRD-COST-003 | Cost hints MUST be exposed in descriptors | P1 |

---

## 8. Semantic Interpretation Requirements

### 8.1 ADESemanticAdapter

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-SEM-001 | System MUST interpret free-text questions into structured SemanticEnvelope | P0 |
| BRD-SEM-002 | SemanticEnvelope MUST include intent_type, requested_outputs, metrics, time_scope, constraints | P0 |
| BRD-SEM-003 | System MUST support all ADE intent types | P0 |
| BRD-SEM-004 | System MUST classify intent with confidence score | P0 |
| BRD-SEM-005 | System MUST use core-defined SemanticEnvelope contract | P0 |

### 8.2 ADE Intent Taxonomy

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-INTENT-TAX-001 | System MUST support DESCRIBE_DATA intent type | P0 |
| BRD-INTENT-TAX-002 | System MUST support COMPARE_PERIODS intent type | P0 |
| BRD-INTENT-TAX-003 | System MUST support TREND_ANALYSIS intent type | P0 |
| BRD-INTENT-TAX-004 | System MUST support ANOMALY_REVIEW intent type | P0 |
| BRD-INTENT-TAX-005 | System MUST support OPEN_ENDED_ANALYSIS intent type | P0 |
| BRD-INTENT-TAX-006 | Each intent type MUST define required and optional fields | P0 |

**Intent Types Summary**:

| Intent Type | Description | Required Fields |
|-------------|-------------|-----------------|
| DESCRIBE_DATA | Summarize dataset characteristics | dataset |
| COMPARE_PERIODS | Compare metrics across time periods | dataset, time_scope |
| TREND_ANALYSIS | Identify trends over time | dataset, metrics, time_scope |
| ANOMALY_REVIEW | Detect and explain anomalies | dataset, metrics |
| OPEN_ENDED_ANALYSIS | Exploratory analysis without specific focus | dataset |

### 8.3 Semantic Validation

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-SEM-VAL-001 | System MUST validate SemanticEnvelope against intent type rules | P0 |
| BRD-SEM-VAL-002 | Validation MUST identify missing required fields | P0 |
| BRD-SEM-VAL-003 | Validation MUST return ASK_USER when clarification is possible | P0 |
| BRD-SEM-VAL-004 | Validation MUST return ABORT when analysis cannot proceed | P0 |
| BRD-SEM-VAL-005 | Validation MUST compute confidence adjustment based on completeness | P1 |

### 8.4 Clarifying Questions

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-CLARIFY-001 | System MUST generate deterministic clarifying questions | P0 |
| BRD-CLARIFY-002 | Questions MUST be templated (no LLM generation) | P0 |
| BRD-CLARIFY-003 | Questions MUST target specific missing fields | P0 |
| BRD-CLARIFY-004 | System MUST provide templates for metric focus questions | P1 |
| BRD-CLARIFY-005 | System MUST provide templates for time range questions | P1 |
| BRD-CLARIFY-006 | System MUST provide templates for anomaly preference questions | P1 |

### 8.5 Intent Router

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-ROUTER-001 | System MUST route validated SemanticEnvelope to appropriate flow | P0 |
| BRD-ROUTER-002 | Router MUST output flow_name and initial_parameters | P0 |
| BRD-ROUTER-003 | Router MUST use deterministic mapping rules | P0 |
| BRD-ROUTER-004 | Router MUST support routing to ade_v1 and visualization flows | P0 |

### 8.6 Semantic Observability

| ID | Requirement | Priority |
|----|-------------|----------|
| BRD-SEM-OBS-001 | System MUST emit trace metadata for semantic interpretation | P0 |
| BRD-SEM-OBS-002 | Traces MUST include ade_intent field | P0 |
| BRD-SEM-OBS-003 | Traces MUST include ade_confidence field | P0 |
| BRD-SEM-OBS-004 | Traces MUST include ade_missing_fields when applicable | P1 |
| BRD-SEM-OBS-005 | Traces MUST include ade_clarifying_question when generated | P1 |

---

## Cross-References

- **Techspec**: [AGENT-agents.md](../02_techspec/AGENT-agents.md)
- **System Design**: [agents-and-tools.md](../04_systemdesign/agents-and-tools.md)
