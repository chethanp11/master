# Intelligence Layer Technical Specification

> **Document ID**: INT  
> **Version**: 1.0.0  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-12

---

## 1. Overview

The intelligence layer provides bounded reasoning capabilities through advisory agents, 
a multi-pass reasoning ladder, critic evaluation, and deterministic context pack assembly.
This layer enhances decision quality while maintaining governance constraints.

### 1.1 Implementation References

| Component | File |
|-----------|------|
| Advisory Agents | `core/agents/advisory.py` |
| Reasoning Ladder | `core/agents/reasoning_ladder.py` |
| Critic Evaluator | `core/agents/critic_evaluator.py` |
| Context Pack Builder | `core/knowledge/context_pack.py` |
| Context Pack Merge | `core/knowledge/context_pack_merge.py` |
| Advisory Schema | `core/contracts/advisory_schema.py` |
| Reasoning Schema | `core/contracts/reasoning_ladder_schema.py` |
| Critic Schema | `core/contracts/critic_schema.py` |
| Context Pack Schema | `core/contracts/context_pack_schema.py` |

---

## 2. Advisory Agent Requirements

### 2.1 Common Advisory Agent Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-ADV-001** | [V1] All advisory agents MUST inherit from `BaseAdvisoryAgent` base class | MUST |
| **INT-ADV-002** | [V1] All advisory agents MUST return JSON-only responses with no control directives | MUST |
| **INT-ADV-003** | [V1] Advisory agents MUST NOT directly invoke tools; they SHALL only return structured recommendations | MUST |
| **INT-ADV-004** | [V1] Every advisory agent MUST define an `output_schema` of type `Type[BaseModel]` for validation | MUST |
| **INT-ADV-005** | [V1] Advisory agent outputs MUST be validated against the declared `output_schema` | MUST |
| **INT-ADV-006** | [V1] Advisory agents MUST pass through governance hooks (`before_model`) before LLM invocation | MUST |
| **INT-ADV-007** | [V1] Advisory agents MUST emit `model_call_attempt_started` event with model, purpose, allowed status, and reason | MUST |
| **INT-ADV-008** | [V1] If governance blocks a model call, the agent MUST raise `PolicyBlockedError` with the governance reason | MUST |

**Implementation**: `core/agents/advisory.py`

### 2.2 ToolSelector Agent

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-TS-001** | [V1] ToolSelector MUST return a `ToolSelectorOutput` with `selected_tools`, `rejected_tools`, `reasoning`, and `confidence` | MUST |
| **INT-TS-002** | [V1] `selected_tools` list MUST NOT exceed 10 entries (`max_items=10`) | MUST |
| **INT-TS-003** | [V1] `rejected_tools` list MUST NOT exceed 10 entries (`max_items=10`) | MUST |
| **INT-TS-004** | [V1] Each `SelectedTool` MUST include `name`, `rationale` (max 300 chars), `confidence` (0.0-1.0) | MUST |
| **INT-TS-005** | [V1] Each `SelectedTool` MAY include `suggested_params` and `dependencies` (max 10 items) | MAY |
| **INT-TS-006** | [V1] ToolSelector SHALL use `ModelRouter` for model routing | SHALL |

**Implementation**: `core/agents/advisory.py`, `core/contracts/advisory_schema.py`

### 2.3 AgentSelector Agent

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-AS-001** | [V1] AgentSelector MUST return an `AgentSelectorOutput` with `selected_agents`, `rejected_agents`, `reasoning`, and `confidence` | MUST |
| **INT-AS-002** | [V1] `selected_agents` list MUST NOT exceed 10 entries | MUST |
| **INT-AS-003** | [V1] Each `SelectedAgent` MUST include `name`, `rationale` (max 300 chars), `confidence` (0.0-1.0) | MUST |
| **INT-AS-004** | [V1] AgentSelector SHALL use `ModelRouter` for model routing | SHALL |

**Implementation**: `core/agents/advisory.py`, `core/contracts/advisory_schema.py`

### 2.4 GapFinder Agent

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-GF-001** | [V1] GapFinder MUST return a `GapFinderOutput` with `identified_gaps`, `recommendations`, `reasoning`, and `confidence` | MUST |
| **INT-GF-002** | [V1] `identified_gaps` list MUST NOT exceed 10 entries | MUST |
| **INT-GF-003** | [V1] `recommendations` list MUST NOT exceed 10 entries | MUST |
| **INT-GF-004** | [V1] GapFinder SHALL use `ModelRouter` for model routing | SHALL |

**Implementation**: `core/agents/advisory.py`, `core/contracts/advisory_schema.py`

### 2.5 Summarizer Agent

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-SUM-001** | [V1] Summarizer MUST return a `SummarizerOutput` with `summary`, `key_points`, and `action_items` | MUST |
| **INT-SUM-002** | [V1] `summary` field MUST NOT exceed 1000 characters | MUST |
| **INT-SUM-003** | [V1] `key_points` and `action_items` lists MUST NOT exceed 10 entries each | MUST |
| **INT-SUM-004** | [V1] Summarizer SHALL use `ModelRouter` for model routing | SHALL |

**Implementation**: `core/agents/advisory.py`, `core/contracts/advisory_schema.py`

### 2.6 RiskExplainer Agent

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-RE-001** | [V1] RiskExplainer MUST return a `RiskExplainerOutput` with `risks`, `mitigations`, `overall_risk_level`, `reasoning`, and `confidence` | MUST |
| **INT-RE-002** | [V1] `risks` list MUST contain at least one entry (validated by `min_items=1`) | MUST |
| **INT-RE-003** | [V1] `risks` list MUST NOT exceed 10 entries | MUST |
| **INT-RE-004** | [V1] Each `Risk` MUST include `level` as one of `LOW`, `MED`, or `HIGH` | MUST |
| **INT-RE-005** | [V1] Each `Risk` MUST include `evidence_refs` for provenance tracking | MUST |
| **INT-RE-006** | [V1] RiskExplainer SHALL use `ModelRouter` for model routing | SHALL |

**Implementation**: `core/agents/advisory.py`, `core/contracts/advisory_schema.py`

---

## 3. Reasoning Ladder Requirements

### 3.1 Multi-Pass Structure

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-RL-001** | [V1] Reasoning ladder MUST execute exactly three passes in order: `interpret` → `propose` → `select` | MUST |
| **INT-RL-002** | [V1] Configuration `max_passes` MUST be at least 3; values below 3 SHALL cause immediate failure with reason `max_passes_below_required` | MUST |
| **INT-RL-003** | [V1] Each pass MUST consume budget before execution; budget exhaustion SHALL halt the ladder | MUST |
| **INT-RL-004** | [V1] If any pass fails, the ladder MUST return `ReasoningLadderResult` with `ok=False` and error details | MUST |

**Implementation**: `core/agents/reasoning_ladder.py`

### 3.2 Interpret Pass

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-RL-INT-001** | [V1] Interpret pass MUST produce a `InterpretOutput` with `intent`, `entities`, and `constraints` | MUST |
| **INT-RL-INT-002** | [V1] Interpret pass MUST extract intent as a string describing the user's goal | MUST |
| **INT-RL-INT-003** | [V1] Interpret pass MUST extract entities as a list of dictionaries | MUST |
| **INT-RL-INT-004** | [V1] Interpret pass MUST extract constraints as a list of strings | MUST |

**Implementation**: `core/agents/reasoning_ladder.py`, `core/contracts/reasoning_ladder_schema.py`

### 3.3 Propose Pass

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-RL-PRO-001** | [V1] Propose pass MUST produce a `ProposeOutput` with `tool_candidates`, `agent_candidates`, and `reasoning` | MUST |
| **INT-RL-PRO-002** | [V1] Propose pass MUST receive the interpret output as input context | MUST |
| **INT-RL-PRO-003** | [V1] `tool_candidates` list MUST be trimmed to `max_tool_candidates` (default 5) | MUST |
| **INT-RL-PRO-004** | [V1] `agent_candidates` list MUST be trimmed to `max_agent_candidates` (default 3) | MUST |
| **INT-RL-PRO-005** | [V1] `evidence_requests` list MUST be trimmed to `max_evidence_requests` (default 3) | MUST |
| **INT-RL-PRO-006** | [V1] Each `ToolCandidate` MUST include `name`, `rationale`, `params`, and `confidence` (0.0-1.0) | MUST |
| **INT-RL-PRO-007** | [V1] Each `AgentCandidate` MUST include `name`, `rationale`, and `confidence` (0.0-1.0) | MUST |

**Implementation**: `core/agents/reasoning_ladder.py`, `core/contracts/reasoning_ladder_schema.py`

### 3.4 Select Pass

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-RL-SEL-001** | [V1] Select pass MUST produce a `SelectOutput` with `final_selection`, `reasoning`, `confidence`, and `alternative_approaches` | MUST |
| **INT-RL-SEL-002** | [V1] Select pass MUST receive both interpret and propose outputs as input context | MUST |
| **INT-RL-SEL-003** | [V1] `final_selection` MUST include `action` (dict), `justification` (string), and `evidence_refs` (list) | MUST |
| **INT-RL-SEL-004** | [V1] If `min_confidence` is set and result confidence is below threshold, select pass MUST fail with `confidence_below_threshold` | MUST |
| **INT-RL-SEL-005** | [V1] Final output confidence MUST be bounded between 0.0 and 1.0 | MUST |

**Implementation**: `core/agents/reasoning_ladder.py`, `core/contracts/reasoning_ladder_schema.py`

### 3.5 Budget Enforcement

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-RL-BUD-001** | [V1] Each pass MUST call `consume_budget` before execution with `reasoning_passes` and `cost_units` | MUST |
| **INT-RL-BUD-002** | [V1] Budget state MUST be updated in place after each consumption | MUST |
| **INT-RL-BUD-003** | [V1] Budget consumption MUST emit `budget_consumed` event with pass name and state | MUST |
| **INT-RL-BUD-004** | [V1] When budget is exceeded, system MUST emit `budget_exceeded` event | MUST |
| **INT-RL-BUD-005** | [V1] When budget exceeds and `escalate_on_exceed=True`, system MUST emit HITL escalation event | MUST |
| **INT-RL-BUD-006** | [V1] `execute_bounded_reasoning` MUST initialize budget state via `BudgetEnforcer` | MUST |
| **INT-RL-BUD-007** | [V1] `execute_bounded_reasoning` MUST emit `bounded_reasoning_started` with max_passes, max_tool_calls, and escalate_on_exceed | MUST |
| **INT-RL-BUD-008** | [V1] `execute_bounded_reasoning` MUST emit `bounded_reasoning_completed` with ok status, passes_used, and violations | MUST |

**Implementation**: `core/agents/reasoning_ladder.py`

---

## 4. Critic Evaluator Requirements

### 4.1 Core Critic Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CRIT-001** | [V1] Critic evaluator MUST NOT call tools directly; it SHALL only evaluate and recommend | MUST |
| **INT-CRIT-002** | [V1] Critic MUST return a `CriticResult` with either `output` (success) or `error` (failure) | MUST |
| **INT-CRIT-003** | [V1] Critic MUST emit `critic_evaluator_started` event with evidence_count, question_len, and reasoning_confidence | MUST |
| **INT-CRIT-004** | [V1] Critic MUST emit `critic_evaluator_completed` event with recommended_next_action, completeness_score, confidence_adjustment, inconsistency_count, and missing_evidence_count | MUST |
| **INT-CRIT-005** | [V1] On validation failure, critic MUST emit `critic_evaluator_failed` event with reason and error | MUST |

**Implementation**: `core/agents/critic_evaluator.py`

### 4.2 Critic Output Schema

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CRIT-OUT-001** | [V1] `CriticOutput` MUST include `completeness_score` bounded between 0.0 and 1.0 | MUST |
| **INT-CRIT-OUT-002** | [V1] `CriticOutput` MUST include `inconsistencies` as a list of strings | MUST |
| **INT-CRIT-OUT-003** | [V1] `CriticOutput` MUST include `missing_evidence` as list of `MissingEvidenceRequest` | MUST |
| **INT-CRIT-OUT-004** | [V1] `CriticOutput` MUST include `confidence_adjustment` bounded between -1.0 and 1.0 | MUST |
| **INT-CRIT-OUT-005** | [V1] `CriticOutput` MUST include `recommended_next_action` as one of: `NONE`, `USER_INPUT`, `HITL`, `FETCH_MORE_EVIDENCE` | MUST |
| **INT-CRIT-OUT-006** | [V1] `CriticOutput` MAY include `justification` field limited to 300 characters maximum | MAY |

**Implementation**: `core/contracts/critic_schema.py`

### 4.3 Missing Evidence Request Schema

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CRIT-MER-001** | [V1] Each `MissingEvidenceRequest` MUST include `source_type` as one of: `table`, `doc`, `api` | MUST |
| **INT-CRIT-MER-002** | [V1] Each `MissingEvidenceRequest` MUST include `description` string | MUST |
| **INT-CRIT-MER-003** | [V1] Each `MissingEvidenceRequest` MAY include `suggested_tools` as list of strings | MAY |

**Implementation**: `core/contracts/critic_schema.py`

### 4.4 Governance Gating

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CRIT-GOV-001** | [V1] `CriticGate.evaluate` MUST apply governance rules to critic output | MUST |
| **INT-CRIT-GOV-002** | [V1] If `FETCH_MORE_EVIDENCE` is recommended but `allow_fetch=False`, recommendation MUST be downgraded to `NONE` | MUST |
| **INT-CRIT-GOV-003** | [V1] If `FETCH_MORE_EVIDENCE` is recommended but `budget_remaining=0`, recommendation MUST be downgraded to `NONE` | MUST |
| **INT-CRIT-GOV-004** | [V1] When recommendation is blocked, system MUST emit `critic_recommendation_blocked` event with requested action and reason | MUST |

**Implementation**: `core/governance/gates.py`

### 4.5 Critic Budget

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CRIT-BUD-001** | [V1] Critic MUST consume budget with `consume_budget` before evaluation | MUST |
| **INT-CRIT-BUD-002** | [V1] Critic MUST emit `budget_consumed` event with critic_pass kind and state | MUST |
| **INT-CRIT-BUD-003** | [V1] When budget exceeded, critic MUST return `CriticResult` with reason `budget_exceeded` | MUST |
| **INT-CRIT-BUD-004** | [V1] When budget exceeded and escalation configured, critic MUST emit HITL escalation event | MUST |

**Implementation**: `core/agents/critic_evaluator.py`

---

## 5. Context Pack Requirements

### 5.1 Context Pack Structure

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CP-001** | [V1] `ContextPack` MUST include `question` (string), `evidence_index`, `tables_summary`, and `documents_summary` | MUST |
| **INT-CP-002** | [V1] `ContextPack` MUST include `assumptions` list documenting processing decisions | MUST |
| **INT-CP-003** | [V1] `ContextPack` MUST include `limits_applied` dictionary documenting applied limits | MUST |
| **INT-CP-004** | [V1] `ContextPack` MAY include `user_answers` for user-supplied answers | MAY |
| **INT-CP-005** | [V1] `ContextPack` MAY include `content_hash` for content-based identity | MAY |

**Implementation**: `core/contracts/context_pack_schema.py`

### 5.2 Evidence Index

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CP-EVI-001** | [V1] Each `EvidenceRef` MUST include `id`, `source_type`, and `confidence` | MUST |
| **INT-CP-EVI-002** | [V1] Each `EvidenceRef` MAY include `uri` and `tool_name` | MAY |
| **INT-CP-EVI-003** | [V1] Evidence items MUST be sorted deterministically by `id` | MUST |

**Implementation**: `core/contracts/context_pack_schema.py`

### 5.3 Evidence Item

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CP-ITEM-001** | [V1] Each `EvidenceItem` MUST include `id` (UUID default), `source_type`, `content`, `confidence`, and `provenance` | MUST |
| **INT-CP-ITEM-002** | [V1] `source_type` MUST be one of: `table`, `doc`, `api`, `metric`, `chart`, `document` | MUST |
| **INT-CP-ITEM-003** | [V1] `confidence` MUST be bounded between 0.0 and 1.0 (default 0.5) | MUST |
| **INT-CP-ITEM-004** | [V1] `content` MUST NOT be empty (validated by `min_length=1`) | MUST |
| **INT-CP-ITEM-005** | [V1] `provenance` MUST be an `EvidenceProvenance` with required `tool` field | MUST |
| **INT-CP-ITEM-006** | [V1] `EvidenceItem` MUST include `timestamp` (default UTC now) for temporal tracking | MUST |
| **INT-CP-ITEM-007** | [V1] `EvidenceItem` MAY include `metadata` dictionary for additional metadata | MAY |

**Implementation**: `core/contracts/context_pack_schema.py`, `core/contracts/retrieval_schema.py`

### 5.4 Tables Summary

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CP-TBL-001** | [V1] `TablesSummary` MUST include `table_count`, `total_rows`, and `tables` | MUST |
| **INT-CP-TBL-002** | [V1] Table key rows MUST be sampled by stable JSON canonicalization | MUST |
| **INT-CP-TBL-003** | [V1] Table key rows MUST be truncated to `max_key_rows` (default 5) | MUST |
| **INT-CP-TBL-004** | [V1] Each `TableInfo` MUST include `name` and `columns` dictionary | MUST |
| **INT-CP-TBL-005** | [V1] Column profiles MUST include `dtype`, `null_pct`, and `sample_values` for each column | MUST |
| **INT-CP-TBL-006** | [V1] Numeric columns MUST include `min`, `max`, and `mean` in stats | MUST |

**Implementation**: `core/contracts/context_pack_schema.py`

### 5.5 Documents Summary

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CP-DOC-001** | [V1] `DocumentsSummary` MUST include `documents` and `excerpts` lists | MUST |
| **INT-CP-DOC-002** | [V1] Document excerpts MUST use leading characters up to `max_excerpt_chars` (default 800) | MUST |
| **INT-CP-DOC-003** | [V1] Each `DocumentInfo` MUST include `name` and `char_count` | MUST |
| **INT-CP-DOC-004** | [V1] Each `Excerpt` MUST include `text` and `evidence_id` for position tracking | MUST |
| **INT-CP-DOC-005** | [V1] Each `Excerpt` MUST include `source` dict with `tool`, `uri`, and `ref` from source | MUST |

**Implementation**: `core/contracts/context_pack_schema.py`

### 5.6 Context Pack Determinism

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CP-DET-001** | [V1] Context pack build MUST be deterministic: same inputs SHALL produce same `content_hash` | MUST |
| **INT-CP-DET-002** | [V1] `content_hash` MUST be computed as SHA-256 of canonical JSON (sorted keys, minimal separators, ASCII) | MUST |
| **INT-CP-DET-003** | [V1] `content_hash` computation MUST exclude `timestamp` and `content_hash` fields from payload | MUST |
| **INT-CP-DET-004** | [V1] Evidence ordering MUST use stable tuple key `(source_type, id)` | MUST |
| **INT-CP-DET-005** | [V1] Table rows MUST be sorted by canonical JSON representation before sampling | MUST |
| **INT-CP-DET-006** | [V1] Canonical JSON MUST use `sort_keys=True`, `separators=(',', ':')`, and `ensure_ascii=True` | MUST |

**Implementation**: `core/knowledge/context_pack.py`

### 5.7 Context Pack Merge

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-CP-MRG-001** | [V1] `merge_user_answers` MUST create `UserAnswers` with `form_id`, `submitted_at`, `answers`, and `metadata` | MUST |
| **INT-CP-MRG-002** | [V1] User answers MUST be ordered deterministically by sorted keys | MUST |
| **INT-CP-MRG-003** | [V1] Evidence refs in `user_answers` MUST be sorted | MUST |
| **INT-CP-MRG-004** | [V1] Merge MUST add marker `[user_answers_merged]` to assumptions if not present | MUST |
| **INT-CP-MRG-005** | [V1] Merge MUST recompute `content_hash` after updating the context pack | MUST |

**Implementation**: `core/knowledge/context_pack_merge.py`

---

## 6. Semantic Interpretation Requirements

### 6.1 Confidence Propagation

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-SEM-CONF-001** | [V1] Core MUST enforce: if `confidence < threshold` then `NextAction` MUST be `ASK_USER` or `ABORT` | MUST |
| **INT-SEM-CONF-002** | [V1] Confidence thresholds MUST be config-driven with product-level overrides | MUST |
| **INT-SEM-CONF-003** | [V1] Default confidence threshold MUST be 0.7 (configurable in `configs/app.yaml`) | MUST |
| **INT-SEM-CONF-004** | [V1] Per-product thresholds MUST be defined in `configs/products.yaml` under `by_product.<product>.semantic_confidence_threshold` | MUST |
| **INT-SEM-CONF-005** | [V1] Confidence MUST be bounded 0.0-1.0; values outside this range MUST raise validation error | MUST |
| **INT-SEM-CONF-006** | [V1] Ambiguity count SHOULD inversely correlate with confidence (guidance, not enforced) | SHOULD |

**Implementation**: `core/governance/hooks.py`, `core/contracts/semantic_schema.py`

### 6.2 Semantic Validation Result

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-SEM-VAL-001** | [V1] `ValidationResult` MUST include: `is_valid` (bool) | MUST |
| **INT-SEM-VAL-002** | [V1] `ValidationResult` MUST include: `missing_fields` (list of field names) | MUST |
| **INT-SEM-VAL-003** | [V1] `ValidationResult` MUST include: `violations` (list of violation descriptions) | MUST |
| **INT-SEM-VAL-004** | [V1] `ValidationResult` MUST include: `revised_confidence` (float 0.0-1.0, after validation adjustments) | MUST |
| **INT-SEM-VAL-005** | [V1] `ValidationResult` MAY include: `clarifying_question` (string, when user input needed) | MAY |
| **INT-SEM-VAL-006** | [V1] If `is_valid=false`, `NextAction` MUST be `ASK_USER` or `ABORT` | MUST |

**Implementation**: `core/contracts/semantic_schema.py`

---

## 7. Evidence Provenance Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-PROV-001** | [V1] Every `EvidenceItem` MUST have `provenance.tool` identifying the originating tool | MUST |
| **INT-PROV-002** | [V1] Every `EvidenceProvenance` MAY have `uri` for external resource location | MAY |
| **INT-PROV-003** | [V1] Every `EvidenceProvenance` MAY have `ref` for internal reference | MAY |
| **INT-PROV-004** | [V1] Evidence provenance MUST be preserved in `EvidenceRef` with `tool_name`, `uri`, `confidence` | MUST |
| **INT-PROV-005** | [V1] Document excerpts MUST preserve source tool, ref, and uri in metadata | MUST |
| **INT-PROV-006** | [V1] `SelectedTool` MUST include `dependencies` linking to supporting evidence | MUST |
| **INT-PROV-007** | [V1] `Risk` MUST include `evidence_refs` for traceability | MUST |
| **INT-PROV-008** | [V1] `Risk` MUST include `source` for risk justification | MUST |

**Implementation**: `core/contracts/retrieval_schema.py`, `core/contracts/advisory_schema.py`

---

## 7. Schema Strictness Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **INT-SCH-001** | [V1] All Pydantic models MUST use `model_config = ConfigDict(extra="forbid")` to reject unknown fields | MUST |
| **INT-SCH-002** | [V1] All bounded lists MUST declare `max_items` constraints | MUST |
| **INT-SCH-003** | [V1] All text fields with length limits MUST use `max_length` | MUST |
| **INT-SCH-004** | [V1] All confidence/score fields MUST use `ge=0.0, le=1.0` | MUST |
| **INT-SCH-005** | [V1] Literal types MUST be used for enumerated values (e.g., `source_type`, `level`) | MUST |

**Implementation**: All schema files in `core/contracts/`

---

## 9. Future Considerations

### 9.1 V1.1 Enhancements

| ID | Feature | Description |
|----|---------|-------------|
| **INT-FUTURE-001** | Confidence calibration | Learn from historical accuracy |
| **INT-FUTURE-002** | Evidence caching | Cache context packs across runs |
| **INT-FUTURE-003** | Parallel advisory | Execute multiple advisory agents concurrently |

### 9.2 V2 Features

| ID | Feature | Description |
|----|---------|-------------|
| **INT-FUTURE-010** | Multi-model reasoning | Ensemble reasoning with multiple LLMs |
| **INT-FUTURE-011** | Self-critique loop | Iterative refinement via critic feedback |
| **INT-FUTURE-012** | External knowledge | Integration with external knowledge bases |

---

## 10. Traceability Matrix

| Requirement | Implementation | Test |
|-------------|----------------|------|
| INT-ADV-001 | `core/agents/advisory.py` | `tests/unit/core/agents/test_advisory.py` |
| INT-RL-001 | `core/agents/reasoning_ladder.py` | `tests/unit/core/agents/test_reasoning_ladder.py` |
| INT-CRIT-001 | `core/agents/critic_evaluator.py` | `tests/unit/core/agents/test_critic_evaluator.py` |
| INT-CP-001 | `core/knowledge/context_pack.py` | `tests/unit/core/knowledge/test_context_pack.py` |
| INT-CP-DET-001 | `core/knowledge/context_pack.py` | `tests/unit/core/knowledge/test_context_pack_determinism.py` |
| INT-CP-MRG-001 | `core/knowledge/context_pack_merge.py` | `tests/unit/core/knowledge/test_context_pack_merge.py` |
| INT-SEM-CONF-001 | `core/governance/hooks.py` | `tests/unit/core/governance/test_semantic_confidence.py` |
| INT-SEM-VAL-001 | `core/contracts/semantic_schema.py` | `tests/unit/core/contracts/test_semantic_schema.py` |
