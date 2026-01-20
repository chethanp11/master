# Intelligence Layer Technical Specification

> **Document ID**: INT  
> **Version**: V1.2  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-13  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial release |
| 1.1.0 | 2026-01-13 | Added §8 Failure Modes & Safe Exits, §9 Explicit Non-Goals, updated BRD mappings |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |

---

## 1. Overview

The intelligence layer provides bounded reasoning capabilities through advisory agents, 
a multi-pass reasoning ladder, critic evaluation, and deterministic context pack assembly.
This layer enhances decision quality while maintaining governance constraints.

## 2. Advisory Agent Requirements

### 2.1 Common Advisory Agent Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-ADV-001 | All advisory agents MUST inherit from `BaseAdvisoryAgent` base class | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-ADV-002 | All advisory agents MUST return JSON-only responses with no control directives | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-ADV-003 | Advisory agents MUST NOT directly invoke tools; they SHALL only return structured recommendations | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-ADV-004 | Every advisory agent MUST define an `output_schema` of type `Type[BaseModel]` for validation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-ADV-005 | Advisory agent outputs MUST be validated against the declared `output_schema` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-ADV-006 | Advisory agents MUST pass through governance hooks (`before_model`) before LLM invocation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-ADV-007 | Advisory agents MUST emit `model_call_attempt_started` event with model, purpose, allowed status, and reason | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-ADV-008 | If governance blocks a model call, the agent MUST raise `PolicyBlockedError` with the governance reason | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 2.2 ToolSelector Agent

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-TS-001 | ToolSelector MUST return a `ToolSelectorOutput` with `selected_tools`, `rejected_tools`, `reasoning`, and `confidence` | MUST | BRD-AUTO-020 | 1.1 | 13 Jan 2026 | — |
| INT-TS-002 | `selected_tools` list MUST NOT exceed 10 entries (`max_items=10`) | MUST | BRD-AUTO-020 | 1.1 | 13 Jan 2026 | — |
| INT-TS-003 | `rejected_tools` list MUST NOT exceed 10 entries (`max_items=10`) | MUST | BRD-AUTO-020 | 1.1 | 13 Jan 2026 | — |
| INT-TS-004 | Each `SelectedTool` MUST include `name`, `rationale` (max 300 chars), `confidence` (0.0-1.0) | MUST | BRD-AUTO-020 | 1.1 | 13 Jan 2026 | — |
| INT-TS-005 | Each `SelectedTool` MAY include `suggested_params` and `dependencies` (max 10 items) | MAY | BRD-AUTO-020 | 1.1 | 13 Jan 2026 | — |
| INT-TS-006 | ToolSelector SHALL use `ModelRouter` for model routing | SHALL | BRD-AUTO-020 | 1.1 | 13 Jan 2026 | — |


### 2.3 AgentSelector Agent

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-AS-001 | AgentSelector MUST return an `AgentSelectorOutput` with `selected_agents`, `rejected_agents`, `reasoning`, and `confidence` | MUST | BRD-AUTO-021 | 1.1 | 13 Jan 2026 | — |
| INT-AS-002 | `selected_agents` list MUST NOT exceed 10 entries | MUST | BRD-AUTO-021 | 1.1 | 13 Jan 2026 | — |
| INT-AS-003 | Each `SelectedAgent` MUST include `name`, `rationale` (max 300 chars), `confidence` (0.0-1.0) | MUST | BRD-AUTO-021 | 1.1 | 13 Jan 2026 | — |
| INT-AS-004 | AgentSelector SHALL use `ModelRouter` for model routing | SHALL | BRD-AUTO-021 | 1.1 | 13 Jan 2026 | — |


### 2.4 GapFinder Agent

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-GF-001 | GapFinder MUST return a `GapFinderOutput` with `identified_gaps`, `recommendations`, `reasoning`, and `confidence` | MUST | BRD-AUTO-022 | 1.1 | 13 Jan 2026 | — |
| INT-GF-002 | `identified_gaps` list MUST NOT exceed 10 entries | MUST | BRD-AUTO-022 | 1.1 | 13 Jan 2026 | — |
| INT-GF-003 | `recommendations` list MUST NOT exceed 10 entries | MUST | BRD-AUTO-022 | 1.1 | 13 Jan 2026 | — |
| INT-GF-004 | GapFinder SHALL use `ModelRouter` for model routing | SHALL | BRD-AUTO-022 | 1.1 | 13 Jan 2026 | — |


### 2.5 Summarizer Agent

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-SUM-001 | Summarizer MUST return a `SummarizerOutput` with `summary`, `key_points`, and `action_items` | MUST | BRD-AUTO-023 | 1.1 | 13 Jan 2026 | — |
| INT-SUM-002 | `summary` field MUST NOT exceed 1000 characters | MUST | BRD-AUTO-023 | 1.1 | 13 Jan 2026 | — |
| INT-SUM-003 | `key_points` and `action_items` lists MUST NOT exceed 10 entries each | MUST | BRD-AUTO-023 | 1.1 | 13 Jan 2026 | — |
| INT-SUM-004 | Summarizer SHALL use `ModelRouter` for model routing | SHALL | BRD-AUTO-023 | 1.1 | 13 Jan 2026 | — |


### 2.6 RiskExplainer Agent

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-RE-001 | RiskExplainer MUST return a `RiskExplainerOutput` with `risks`, `mitigations`, `overall_risk_level`, `reasoning`, and `confidence` | MUST | BRD-AUTO-024 | 1.1 | 13 Jan 2026 | — |
| INT-RE-002 | `risks` list MUST contain at least one entry (validated by `min_items=1`) | MUST | BRD-AUTO-024 | 1.1 | 13 Jan 2026 | — |
| INT-RE-003 | `risks` list MUST NOT exceed 10 entries | MUST | BRD-AUTO-024 | 1.1 | 13 Jan 2026 | — |
| INT-RE-004 | Each `Risk` MUST include `level` as one of `LOW`, `MED`, or `HIGH` | MUST | BRD-AUTO-024 | 1.1 | 13 Jan 2026 | — |
| INT-RE-005 | Each `Risk` MUST include `evidence_refs` for provenance tracking | MUST | BRD-AUTO-024 | 1.1 | 13 Jan 2026 | — |
| INT-RE-006 | RiskExplainer SHALL use `ModelRouter` for model routing | SHALL | BRD-AUTO-024 | 1.1 | 13 Jan 2026 | — |


---

## 3. Reasoning Ladder Requirements

### 3.1 Multi-Pass Structure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-RL-001 | Reasoning ladder MUST execute exactly three passes in order: `interpret` → `propose` → `select` | MUST | BRD-AUTO-001, BRD-AUTO-030 | 1.1 | 13 Jan 2026 | — |
| INT-RL-002 | Configuration `max_passes` MUST be at least 3; values below 3 SHALL cause immediate failure with reason `max_passes_below_required` | MUST | BRD-AUTO-001, BRD-AUTO-030 | 1.1 | 13 Jan 2026 | — |
| INT-RL-003 | Each pass MUST consume budget before execution; budget exhaustion SHALL halt the ladder | MUST | BRD-AUTO-001 | 1.1 | 13 Jan 2026 | — |
| INT-RL-004 | If any pass fails, the ladder MUST return `ReasoningLadderResult` with `ok=False` and error details | MUST | BRD-AUTO-001 | 1.1 | 13 Jan 2026 | — |


### 3.2 Interpret Pass

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-RL-INT-001 | Interpret pass MUST produce a `InterpretOutput` with `intent`, `entities`, and `constraints` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-INT-002 | Interpret pass MUST extract intent as a string describing the user's goal | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-INT-003 | Interpret pass MUST extract entities as a list of dictionaries | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-INT-004 | Interpret pass MUST extract constraints as a list of strings | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 3.3 Propose Pass

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-RL-PRO-001 | Propose pass MUST produce a `ProposeOutput` with `tool_candidates`, `agent_candidates`, and `reasoning` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-PRO-002 | Propose pass MUST receive the interpret output as input context | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-PRO-003 | `tool_candidates` list MUST be trimmed to `max_tool_candidates` (default 5) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-PRO-004 | `agent_candidates` list MUST be trimmed to `max_agent_candidates` (default 3) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-PRO-005 | `evidence_requests` list MUST be trimmed to `max_evidence_requests` (default 3) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-PRO-006 | Each `ToolCandidate` MUST include `name`, `rationale`, `params`, and `confidence` (0.0-1.0) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-PRO-007 | Each `AgentCandidate` MUST include `name`, `rationale`, and `confidence` (0.0-1.0) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 3.4 Select Pass

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-RL-SEL-001 | Select pass MUST produce a `SelectOutput` with `final_selection`, `reasoning`, `confidence`, and `alternative_approaches` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-SEL-002 | Select pass MUST receive both interpret and propose outputs as input context | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-SEL-003 | `final_selection` MUST include `action` (dict), `justification` (string), and `evidence_refs` (list) | MUST | BRD-AUTO-035, BRD-GOV-046 | 1.1 | 13 Jan 2026 | — |
| INT-RL-SEL-004 | If `min_confidence` is set and result confidence is below threshold, select pass MUST fail with `confidence_below_threshold` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-SEL-005 | Final output confidence MUST be bounded between 0.0 and 1.0 | MUST | BRD-GOV-062 | 1.1 | 13 Jan 2026 | — |


### 3.5 Budget Enforcement

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-RL-BUD-001 | Each pass MUST call `consume_budget` before execution with `reasoning_passes` and `cost_units` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-BUD-002 | Budget state MUST be updated in place after each consumption | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-BUD-003 | Budget consumption MUST emit `budget_consumed` event with pass name and state | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-BUD-004 | When budget is exceeded, system MUST emit `budget_exceeded` event | MUST | BRD-AUTO-033 | 1.1 | 13 Jan 2026 | — |
| INT-RL-BUD-005 | When budget exceeds and `escalate_on_exceed=True`, system MUST emit HITL escalation event | MUST | BRD-AUTO-033 | 1.1 | 13 Jan 2026 | — |
| INT-RL-BUD-006 | `execute_bounded_reasoning` MUST initialize budget state via `BudgetEnforcer` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-BUD-007 | `execute_bounded_reasoning` MUST emit `bounded_reasoning_started` with max_passes, max_tool_calls, and escalate_on_exceed | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-RL-BUD-008 | `execute_bounded_reasoning` MUST emit `bounded_reasoning_completed` with ok status, passes_used, and violations | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 4. Critic Evaluator Requirements

### 4.1 Core Critic Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CRIT-001 | Critic evaluator MUST NOT call tools directly; it SHALL only evaluate and recommend | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-002 | Critic MUST return a `CriticResult` with either `output` (success) or `error` (failure) | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-003 | Critic MUST emit `critic_evaluator_started` event with evidence_count, question_len, and reasoning_confidence | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-004 | Critic MUST emit `critic_evaluator_completed` event with recommended_next_action, completeness_score, confidence_adjustment, inconsistency_count, and missing_evidence_count | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-005 | On validation failure, critic MUST emit `critic_evaluator_failed` event with reason and error | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |


### 4.2 Critic Output Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CRIT-OUT-001 | `CriticOutput` MUST include `completeness_score` bounded between 0.0 and 1.0 | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-OUT-002 | `CriticOutput` MUST include `inconsistencies` as a list of strings | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-OUT-003 | `CriticOutput` MUST include `missing_evidence` as list of `MissingEvidenceRequest` | MUST | BRD-AUTO-022 | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-OUT-004 | `CriticOutput` MUST include `confidence_adjustment` bounded between -1.0 and 1.0 | MUST | BRD-GOV-062 | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-OUT-005 | `CriticOutput` MUST include `recommended_next_action` as one of: `NONE`, `USER_INPUT`, `HITL`, `FETCH_MORE_EVIDENCE` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-OUT-006 | `CriticOutput` MAY include `justification` field limited to 300 characters maximum | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.3 Missing Evidence Request Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CRIT-MER-001 | Each `MissingEvidenceRequest` MUST include `source_type` as one of: `table`, `doc`, `api` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-MER-002 | Each `MissingEvidenceRequest` MUST include `description` string | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-MER-003 | Each `MissingEvidenceRequest` MAY include `suggested_tools` as list of strings | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.4 Governance Gating

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CRIT-GOV-001 | `CriticGate.evaluate` MUST apply governance rules to critic output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-GOV-002 | If `FETCH_MORE_EVIDENCE` is recommended but `allow_fetch=False`, recommendation MUST be downgraded to `NONE` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-GOV-003 | If `FETCH_MORE_EVIDENCE` is recommended but `budget_remaining=0`, recommendation MUST be downgraded to `NONE` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-GOV-004 | When recommendation is blocked, system MUST emit `critic_recommendation_blocked` event with requested action and reason | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.5 Critic Budget

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CRIT-BUD-001 | Critic MUST consume budget with `consume_budget` before evaluation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-BUD-002 | Critic MUST emit `budget_consumed` event with critic_pass kind and state | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-BUD-003 | When budget exceeded, critic MUST return `CriticResult` with reason `budget_exceeded` | MUST | BRD-AUTO-033 | 1.1 | 13 Jan 2026 | — |
| INT-CRIT-BUD-004 | When budget exceeded and escalation configured, critic MUST emit HITL escalation event | MUST | BRD-AUTO-033 | 1.1 | 13 Jan 2026 | — |


---

## 5. Context Pack Requirements

### 5.1 Context Pack Structure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CP-001 | `ContextPack` MUST include `question` (string), `evidence_index`, `tables_summary`, and `documents_summary` | MUST | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |
| INT-CP-002 | `ContextPack` MUST include `assumptions` list documenting processing decisions | MUST | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |
| INT-CP-003 | `ContextPack` MUST include `limits_applied` dictionary documenting applied limits | MUST | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |
| INT-CP-004 | `ContextPack` MAY include `user_answers` for user-supplied answers | MAY | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |
| INT-CP-005 | `ContextPack` MAY include `content_hash` for content-based identity | MAY | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |


### 5.2 Evidence Index

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CP-EVI-001 | Each `EvidenceRef` MUST include `id`, `source_type`, and `confidence` | MUST | BRD-AUTO-002 | 1.1 | 13 Jan 2026 | — |
| INT-CP-EVI-002 | Each `EvidenceRef` MAY include `uri` and `tool_name` | MAY | BRD-AUTO-002 | 1.1 | 13 Jan 2026 | — |
| INT-CP-EVI-003 | Evidence items MUST be sorted deterministically by `id` | MUST | BRD-AUTO-002 | 1.1 | 13 Jan 2026 | — |


### 5.3 Evidence Item

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CP-ITEM-001 | Each `EvidenceItem` MUST include `id` (UUID default), `source_type`, `content`, `confidence`, and `provenance` | MUST | BRD-AUTO-013 | 1.1 | 13 Jan 2026 | — |
| INT-CP-ITEM-002 | `source_type` MUST be one of: `table`, `doc`, `api`, `metric`, `chart`, `document` | MUST | BRD-AUTO-013 | 1.1 | 13 Jan 2026 | — |
| INT-CP-ITEM-003 | `confidence` MUST be bounded between 0.0 and 1.0 (default 0.5) | MUST | BRD-AUTO-013 | 1.1 | 13 Jan 2026 | — |
| INT-CP-ITEM-004 | `content` MUST NOT be empty (validated by `min_length=1`) | MUST | BRD-AUTO-013 | 1.1 | 13 Jan 2026 | — |
| INT-CP-ITEM-005 | `provenance` MUST be an `EvidenceProvenance` with required `tool` field | MUST | BRD-AUTO-013 | 1.1 | 13 Jan 2026 | — |
| INT-CP-ITEM-006 | `EvidenceItem` MUST include `timestamp` (default UTC now) for temporal tracking | MUST | BRD-AUTO-013 | 1.1 | 13 Jan 2026 | — |
| INT-CP-ITEM-007 | `EvidenceItem` MAY include `metadata` dictionary for additional metadata | MAY | BRD-AUTO-013 | 1.1 | 13 Jan 2026 | — |


### 5.4 Tables Summary

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CP-TBL-001 | `TablesSummary` MUST include `table_count`, `total_rows`, and `tables` | MUST | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |
| INT-CP-TBL-002 | Table key rows MUST be sampled by stable JSON canonicalization | MUST | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |
| INT-CP-TBL-003 | Table key rows MUST be truncated to `max_key_rows` (default 5) | MUST | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |
| INT-CP-TBL-004 | Each `TableInfo` MUST include `name` and `columns` dictionary | MUST | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |
| INT-CP-TBL-005 | Column profiles MUST include `dtype`, `null_pct`, and `sample_values` for each column | MUST | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |
| INT-CP-TBL-006 | Numeric columns MUST include `min`, `max`, and `mean` in stats | MUST | BRD-AUTO-032 | 1.1 | 13 Jan 2026 | — |


### 5.5 Documents Summary

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CP-DOC-001 | `DocumentsSummary` MUST include `documents` and `excerpts` lists | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-DOC-002 | Document excerpts MUST use leading characters up to `max_excerpt_chars` (default 800) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-DOC-003 | Each `DocumentInfo` MUST include `name` and `char_count` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-DOC-004 | Each `Excerpt` MUST include `text` and `evidence_id` for position tracking | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-DOC-005 | Each `Excerpt` MUST include `source` dict with `tool`, `uri`, and `ref` from source | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 5.6 Context Pack Determinism

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CP-DET-001 | Context pack build MUST be deterministic: same inputs SHALL produce same `content_hash` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-DET-002 | `content_hash` MUST be computed as SHA-256 of canonical JSON (sorted keys, minimal separators, ASCII) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-DET-003 | `content_hash` computation MUST exclude `timestamp` and `content_hash` fields from payload | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-DET-004 | Evidence ordering MUST use stable tuple key `(source_type, id)` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-DET-005 | Table rows MUST be sorted by canonical JSON representation before sampling | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-DET-006 | Canonical JSON MUST use `sort_keys=True`, `separators=(',', ':')`, and `ensure_ascii=True` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 5.7 Context Pack Merge

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-CP-MRG-001 | `merge_user_answers` MUST create `UserAnswers` with `form_id`, `submitted_at`, `answers`, and `metadata` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-MRG-002 | User answers MUST be ordered deterministically by sorted keys | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-MRG-003 | Evidence refs in `user_answers` MUST be sorted | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-MRG-004 | Merge MUST add marker `[user_answers_merged]` to assumptions if not present | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-CP-MRG-005 | Merge MUST recompute `content_hash` after updating the context pack | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 6. Semantic Interpretation Requirements

### 6.1 Confidence Propagation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-SEM-CONF-001 | Core MUST enforce: if `confidence < threshold` then `NextAction` MUST be `ASK_USER` or `ABORT` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-CONF-002 | Confidence thresholds MUST be config-driven with product-level overrides | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-CONF-003 | Default confidence threshold MUST be 0.7 (configurable in `configs/app.yaml`) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-CONF-004 | Per-product thresholds MUST be defined in `configs/products.yaml` under `by_product.<product>.semantic_confidence_threshold` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-CONF-005 | Confidence MUST be bounded 0.0-1.0; values outside this range MUST raise validation error | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-CONF-006 | Ambiguity count SHOULD inversely correlate with confidence (guidance, not enforced) | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.2 Semantic Validation Result

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-SEM-VAL-001 | `ValidationResult` MUST include: `is_valid` (bool) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-VAL-002 | `ValidationResult` MUST include: `missing_fields` (list of field names) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-VAL-003 | `ValidationResult` MUST include: `violations` (list of violation descriptions) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-VAL-004 | `ValidationResult` MUST include: `revised_confidence` (float 0.0-1.0, after validation adjustments) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-VAL-005 | `ValidationResult` MAY include: `clarifying_question` (string, when user input needed) | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SEM-VAL-006 | If `is_valid=false`, `NextAction` MUST be `ASK_USER` or `ABORT` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 7. Evidence Provenance Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-PROV-001 | Every `EvidenceItem` MUST have `provenance.tool` identifying the originating tool | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-PROV-002 | Every `EvidenceProvenance` MAY have `uri` for external resource location | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-PROV-003 | Every `EvidenceProvenance` MAY have `ref` for internal reference | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-PROV-004 | Evidence provenance MUST be preserved in `EvidenceRef` with `tool_name`, `uri`, `confidence` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-PROV-005 | Document excerpts MUST preserve source tool, ref, and uri in metadata | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-PROV-006 | `SelectedTool` MUST include `dependencies` linking to supporting evidence | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-PROV-007 | `Risk` MUST include `evidence_refs` for traceability | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-PROV-008 | `Risk` MUST include `source` for risk justification | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 7. Schema Strictness Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-SCH-001 | All Pydantic models MUST use `model_config = ConfigDict(extra="forbid")` to reject unknown fields | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SCH-002 | All bounded lists MUST declare `max_items` constraints | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SCH-003 | All text fields with length limits MUST use `max_length` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SCH-004 | All confidence/score fields MUST use `ge=0.0, le=1.0` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-SCH-005 | Literal types MUST be used for enumerated values (e.g., `source_type`, `level`) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 8. Failure Modes & Safe Exits (Added: 2026-01-13)

> **Source**: BRD-AUTO-SEM-*, BRD-AUTO-STOP-*, BRD-GOV-CONF-*

### 8.1 Intelligence Layer Exit States

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-EXIT-010 | Intelligence layer MUST support exit state `SUCCESS` when reasoning completes with confidence ≥ threshold and allows the run to continue | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-011 | Intelligence layer MUST support exit state `PARTIAL_SUCCESS` when reasoning completes below confidence and returns results with warnings | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-012 | Intelligence layer MUST support exit state `ASK_USER` when ambiguity exceeds threshold or validation fails, and set run status to `PAUSED_WAITING_FOR_USER` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-013 | Intelligence layer MUST support exit state `ABORT` for unrecoverable interpretation failure and set run status to `FAILED` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-014 | Intelligence layer MUST support exit state `BUDGET_EXCEEDED` when reasoning budget is exhausted and set run status to `FAILED` or HITL | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

### 8.2 Confidence-Based Exit Decisions

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-EXIT-001 | If `confidence < threshold` and `ambiguity_count > 0`, MUST return `ASK_USER` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-002 | If `validation.is_valid = false`, MUST return `ASK_USER` or `ABORT` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-003 | If `validation.violations` contain critical violations, MUST return `ABORT` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-004 | Exit decision MUST be deterministic given same inputs | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-005 | Exit decision MUST be logged with all factors in trace event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 8.3 Safe Exit Artifacts

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| INT-EXIT-ART-001 | `ASK_USER` exit MUST produce `ClarificationRequest` artifact | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-ART-002 | `ClarificationRequest` MUST include: `question`, `ambiguities`, `original_confidence`, `context` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-ART-003 | `ABORT` exit MUST produce `AbortArtifact` with: `error_code`, `reason`, `violations`, `ambiguities` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| INT-EXIT-ART-004 | All exit artifacts MUST be persisted to run record | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

**AbortArtifact Schema**:


---

## 9. Explicit Non-Goals (Added: 2026-01-13)

> **The Intelligence Layer MUST NOT**:

| Non-Goal | Rationale | Violation Example |
|----------|-----------|-------------------|
| Autonomous decision-making | Intelligence is advisory only (INV-2) | System decides next step without orchestrator |
| Self-modification | Governance is immutable at runtime | System updates its own thresholds |
| Domain inference in core | Products own domain rules (INV-10) | Core intelligence infers "trend requires time axis" |
| Hidden heuristics | All decisions must be auditable (INV-4) | Undocumented scoring algorithm |
| Treating LLM output as truth | Interpretations are hypotheses (INV-3) | Using raw LLM response as fact |
| Unbounded exploration | Reasoning is bounded (INV-1) | Infinite reasoning loops |

---
