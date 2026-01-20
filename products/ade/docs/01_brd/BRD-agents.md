# ADE Agent Business Requirements

> **Document**: Business Requirements — Agents  
> **Version**: V1.2  
> **Last Updated**: 2026-01-19

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial release |
| V1.2 | 2026-01-19 | Standardized tables, removed TSD-level detail, and aligned intent traceability |

## 1. Agent Overview

Agents provide reasoning roles in ADE workflows:

---

## 1.1 Reasoning Ladder Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-INTEL-001 | System MUST use multi-stage reasoning (interpret → propose → critique → finalize) | INT-INTEL-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTEL-002 | Reasoning MUST progress through explicit stages: interpretation, proposal, gated execution, critique, and finalization | INT-INTEL-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTEL-003 | Reasoning cycles MUST be bounded by explicit limits (iterations, tools, tokens, time) | INT-INTEL-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTEL-004 | Reasoning MUST track sufficiency state across cycles | INT-INTEL-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-INTEL-005 | Final outputs MUST state why reasoning stopped | INT-INTEL-005 | P1 | 2026-01-13 | V1.1 | — |

---

## 1.3 Critique Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-CRIT-001 | System MUST run critique before finalizing outputs | INT-CRIT-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CRIT-002 | Critique MUST identify missing evidence, weak evidence, unsupported claims, and overreach | INT-CRIT-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CRIT-003 | Critique MUST be able to downgrade confidence with reasons | INT-CRIT-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-CRIT-004 | Critique MUST remain advisory (no execution or routing) | INT-CRIT-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CRIT-005 | Blocking critique findings MUST trigger clarification or safe abort | INT-CRIT-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CRIT-006 | Critique results MUST be integrated into outcomes, allowing confidence downgrades or blocking gaps to influence final results | INT-CRIT-006 | P0 | 2026-01-13 | V1.1 | — |

---

## 1.4 Advisory Tool Selection

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-TOOLSEL-001 | Tool selection MUST be surfaced as advisory recommendations | INT-TOOLSEL-001 | P1 | 2026-01-13 | V1.1 | — |
| BRD-TOOLSEL-002 | Tool recommendations MAY be ranked with rationales | INT-TOOLSEL-002 | P2 | 2026-01-13 | V1.1 | — |
| BRD-TOOLSEL-003 | Orchestrator MUST remain the sole authority for tool execution | INT-TOOLSEL-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TOOLSEL-004 | Advisory tool suggestions MUST NOT force execution | INT-TOOLSEL-004 | P0 | 2026-01-13 | V1.1 | — |

## 1.5 Terminal Outcome Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-TERM-001 | ADE MUST emit explicit terminal outcomes: SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT | INT-TERM-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TERM-002 | PARTIAL_SUCCESS outcomes MUST state what was completed, what is missing, and why | INT-TERM-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-TERM-003 | Terminal outcomes MUST include required explanations and supporting artifacts | INT-TERM-003 | P0 | 2026-01-13 | V1.1 | — |

---

## 2. Intent Interpretation Requirements

### 2.1 intent_agent

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-INTENT-001 | System MUST extract intent summary from user question | INT-INTENT-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-002 | System MUST identify referenced datasets | INT-INTENT-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-003 | System MUST identify referenced metrics | INT-INTENT-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-004 | System MUST identify time window constraints | INT-INTENT-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-005 | System MUST provide a confidence score | INT-INTENT-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-006 | System MUST detect when clarification is needed | INT-INTENT-006 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-007 | System MUST generate clarifying questions | INT-INTENT-007 | P1 | 2026-01-13 | V1.1 | — |

### 2.2 planning_agent

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-PLANNING-001 | System MUST interpret intent from dataset context | INT-VIZ-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PLANNING-002 | System MUST support replanning after rejection | INT-UI-006 | P1 | 2026-01-13 | V1.1 | — |

---

## 3. Plan Generation Requirements

### 3.1 plan_agent

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-PLANGEN-001 | System MUST produce deterministic plans | INT-PLAN-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PLANGEN-002 | Plans MUST include all required analysis steps | INT-PLAN-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PLANGEN-003 | Plans MUST include tool flags for conditional execution | INT-PLAN-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PLANGEN-004 | Same inputs MUST produce same plan | INT-PLAN-004 | P0 | 2026-01-13 | V1.1 | — |

### 3.2 plan_proposal_agent

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-PROPOSAL-001 | System MUST generate human-readable plan summary | INT-PLAN-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-PROPOSAL-002 | System MUST estimate step count | INT-PLAN-006 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PROPOSAL-003 | System MUST estimate execution cost | INT-PLAN-007 | P1 | 2026-01-13 | V1.1 | — |
| BRD-PROPOSAL-004 | System MUST require approval for non-trivial plans | INT-PLAN-008 | P0 | 2026-01-13 | V1.1 | — |

---

## 4. Data Quality Assessment Requirements

### 4.1 sufficiency_evaluator

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-SUFF-001 | System MUST assess data sufficiency | INT-SUFF-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SUFF-002 | System MUST provide a confidence level | INT-SUFF-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SUFF-003 | System MUST explain confidence downgrades | INT-SUFF-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-SUFF-004 | System SHOULD evaluate row count sufficiency | INT-SUFF-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-SUFF-005 | System SHOULD evaluate column completeness | INT-SUFF-005 | P1 | 2026-01-13 | V1.1 | — |
| BRD-SUFF-006 | System SHOULD evaluate data freshness | INT-SUFF-006 | P2 | 2026-01-13 | V1.1 | — |

---

## 5. Narrative Generation Requirements

### 5.1 dashboard_agent

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-NARR-001 | System MUST generate dataset summary narratives | INT-NARR-001 | P1 | 2026-01-13 | V1.1 | — |
| BRD-NARR-002 | System MUST explain key findings in plain language | INT-NARR-002 | P1 | 2026-01-13 | V1.1 | — |
| BRD-NARR-003 | System MUST summarize anomalies with context | INT-NARR-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-NARR-004 | System MUST provide recommendations | INT-NARR-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-NARR-005 | User-facing explanations MUST be derived from platform decision records, not regenerated narratives | INT-NARR-005 | P0 | 2026-01-13 | V1.1 | — |

---

## 6. Confidence and Transparency Requirements

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-CONF-001 | All agent outputs MUST include confidence level | INT-CONF-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CONF-002 | Low confidence MUST trigger user clarification | INT-CONF-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CONF-003 | Confidence thresholds MUST be configurable | INT-CONF-003 | P1 | 2026-01-13 | V1.1 | — |
| BRD-CONF-004 | Confidence downgrades MUST be explained | INT-CONF-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-CONF-005 | ADE MUST respect platform-defined confidence thresholds and gates when requesting execution, escalation, or human input | INT-CONF-005 | P0 | 2026-01-13 | V1.1 | — |

---

## 7. Semantic Interpretation Requirements

### 7.1 ADESemanticAdapter

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-SEM-001 | System MUST interpret free-text questions into a structured semantic interpretation output | INT-SEM-001 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-002 | Semantic interpretation MUST extract intent types and required entities | INT-SEM-002, INT-SEM-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-003 | System MUST support all ADE intent types | INT-SEM-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-004 | System MUST classify intent with confidence score | INT-SEM-004 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-005 | Semantic interpretation MUST run before planning phase | INT-SEM-009 | P0 | 2026-01-13 | V1.1 | — |

### 8.2 ADE Intent Taxonomy

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-INTENT-TAX-001 | System MUST support DESCRIBE_DATA intent type | INT-SEM-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-TAX-002 | System MUST support COMPARE_PERIODS intent type | INT-SEM-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-TAX-003 | System MUST support TREND_ANALYSIS intent type | INT-SEM-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-TAX-004 | System MUST support ANOMALY_REVIEW intent type | INT-SEM-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-TAX-005 | System MUST support OPEN_ENDED_ANALYSIS intent type | INT-SEM-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-INTENT-TAX-006 | Each intent type MUST define required and optional fields | INT-SEM-006 | P0 | 2026-01-13 | V1.1 | — |

### 8.3 Semantic Validation

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-SEM-VAL-001 | System MUST validate the semantic interpretation output against intent type rules | INT-SEM-VAL-001, INT-SEM-VAL-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-VAL-002 | Validation MUST identify missing required fields | INT-SEM-006, INT-SEM-VAL-005 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-VAL-003 | Validation MUST return ASK_USER when clarification is possible | INT-SEM-005, INT-SEM-VAL-001, INT-SEM-VAL-002 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-VAL-004 | Validation MUST return ABORT when analysis cannot proceed | INT-SEM-008 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-VAL-005 | Validation MUST compute confidence adjustment based on completeness | INT-SEM-004 | P1 | 2026-01-13 | V1.1 | — |
| BRD-SEM-VAL-006 | Dataset references MUST be validated against available datasets | INT-SEM-VAL-003 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-VAL-007 | Metric references MUST be validated against dataset schema when known | INT-SEM-VAL-004 | P0 | 2026-01-13 | V1.1 | — |

### 8.4 Clarifying Questions

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-CLARIFY-001 | System MUST generate deterministic clarifying questions | INT-SEM-007 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CLARIFY-002 | Questions MUST be templated (no LLM generation) | INT-SEM-007 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CLARIFY-003 | Questions MUST target specific missing fields | INT-SEM-007 | P0 | 2026-01-13 | V1.1 | — |
| BRD-CLARIFY-004 | System MUST provide templates for metric focus questions | INT-SEM-007 | P1 | 2026-01-13 | V1.1 | — |
| BRD-CLARIFY-005 | System MUST provide templates for time range questions | INT-SEM-007 | P1 | 2026-01-13 | V1.1 | — |
| BRD-CLARIFY-006 | System MUST provide templates for anomaly preference questions | INT-SEM-007 | P1 | 2026-01-13 | V1.1 | — |

### 8.5 Intent Router

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-ROUTER-001 | System MUST route validated semantic interpretation output to appropriate flow | INT-SEM-009 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ROUTER-002 | Router MUST output target flow and initial parameters | INT-SEM-009 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ROUTER-003 | Router MUST use deterministic mapping rules | INT-SEM-009 | P0 | 2026-01-13 | V1.1 | — |
| BRD-ROUTER-004 | Router MUST support routing to question-first and dataset-first flows | INT-SEM-009 | P0 | 2026-01-13 | V1.1 | — |

### 8.6 Semantic Observability

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-SEM-OBS-001 | System MUST emit trace metadata for semantic interpretation | INT-SEM-010 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-OBS-002 | Traces MUST include interpreted intent | INT-SEM-010 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-OBS-003 | Traces MUST include confidence information | INT-SEM-010 | P0 | 2026-01-13 | V1.1 | — |
| BRD-SEM-OBS-004 | Traces MUST include missing-field indicators when applicable | INT-SEM-010 | P1 | 2026-01-13 | V1.1 | — |
| BRD-SEM-OBS-005 | Traces MUST include clarifying questions when generated | INT-SEM-010 | P1 | 2026-01-13 | V1.1 | — |

---

## Appendix: Technical Details (Removed from BRD)

### Agent Summary (Technical Reference)
| Agent | Role | Flows |
|-------|------|-------|
| `intent_agent` | Interpret user questions | ade_v1 |
| `plan_agent` | Create analysis plans | ade_v1 |
| `plan_proposal_agent` | Generate approval requests | Both |
| `planning_agent` | Interpret intent, handle replanning | visualization |
| `sufficiency_evaluator` | Assess data quality | Both |
| `dashboard_agent` | Generate narrative summaries | Both |

### Intent Types Summary (Technical Reference)
| Intent Type | Description | Required Fields |
|-------------|-------------|-----------------|
| DESCRIBE_DATA | Summarize dataset characteristics | dataset |
| COMPARE_PERIODS | Compare metrics across time periods | dataset, time_scope |
| TREND_ANALYSIS | Identify trends over time | dataset, metrics, time_scope |
| ANOMALY_REVIEW | Detect and explain anomalies | dataset, metrics |
| OPEN_ENDED_ANALYSIS | Exploratory analysis without specific focus | dataset |

### Standard Confidence Labels
- high
- medium
- low

### Trace Field Names (Technical Reference)
- ade_intent
- ade_confidence
- ade_missing_fields
- ade_clarifying_question
