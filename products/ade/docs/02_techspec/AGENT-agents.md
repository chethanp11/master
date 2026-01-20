# ADE Agent Technical Specification

> **Document**: Technical Specification — Agents & Semantic Interpretation  
> **Prefix**: AGENT-*, SEM-*  
> **Version**: 1.2  
> **Last Updated**: 2026-01-20

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added semantic interpretation requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |

---

## 1. General Agent Requirements (AGENT-GEN)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-GEN-001 | All agents MUST have descriptors in products/ade/descriptors.py with purpose, capabilities, and cost_hint. | MUST | BRD-CONF-001 | 1.1 | 13 Jan 2026 | — |
| AGENT-GEN-002 | Agents MUST have accurate cost hints (intent_agent: MED, plan_agent: MED, plan_proposal_agent: LOW, planning_agent: MED, sufficiency_evaluator: LOW, dashboard_agent: MED). | MUST | BRD-CONF-001 | 1.1 | 13 Jan 2026 | — |
| AGENT-GEN-003 | Agents MUST only be invoked from allowed step types (plan_proposal_agent: agent/plan_proposal; others: agent). | MUST | BRD-INTEL-002 | 1.1 | 13 Jan 2026 | — |

---

## 2. intent_agent (AGENT-INTENT)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-INTENT-001 | intent_agent MUST output IntentFrame schema with fields: intent_summary, inferred_entities, inferred_metrics, inferred_time_window, requested_outputs, confidence_score, confidence_label, blocking_required, blocking_questions, blocking_question. | MUST | BRD-INTENT-001 | 1.1 | 13 Jan 2026 | — |
| AGENT-INTENT-002 | intent_agent MUST provide confidence_score (0.0-1.0) and confidence_label (low < 0.4, medium 0.4-0.7, high > 0.7). | MUST | BRD-INTENT-005 | 1.1 | 13 Jan 2026 | — |
| AGENT-INTENT-003 | intent_agent MUST detect when clarification is needed and set blocking_required=True when dataset/metric/time window is missing. | MUST | BRD-INTENT-006 | 1.1 | 13 Jan 2026 | — |
| AGENT-INTENT-004 | intent_agent MUST extract dataset names to inferred_entities, metric names to inferred_metrics, and time windows to inferred_time_window. | MUST | BRD-INTENT-002, BRD-INTENT-003, BRD-INTENT-004 | 1.1 | 13 Jan 2026 | — |

---

## 3. plan_agent (AGENT-PLAN)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-PLAN-001 | plan_agent MUST output valid PlanSpec schema with tool flags for conditional execution. | MUST | BRD-PLANGEN-002, BRD-PLANGEN-003 | 1.1 | 13 Jan 2026 | — |
| AGENT-PLAN-002 | plan_agent MUST produce deterministic plans (same inputs = identical plans, no random selection). | MUST | BRD-PLANGEN-001, BRD-PLANGEN-004 | 1.1 | 13 Jan 2026 | — |

---

## 4. plan_proposal_agent (AGENT-PROPOSAL)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-PROPOSAL-001 | plan_proposal_agent MUST output PlanProposal with fields: proposal_id, summary, estimated_steps, estimated_cost, requires_approval. | MUST | BRD-PROPOSAL-001 | 1.1 | 13 Jan 2026 | — |
| AGENT-PROPOSAL-002 | plan_proposal_agent MUST set requires_approval=True for non-trivial plans and pause execution for user decision. | MUST | BRD-PROPOSAL-004 | 1.1 | 13 Jan 2026 | — |
| AGENT-PROPOSAL-003 | plan_proposal_agent MUST estimate execution cost reflecting tool cost hints and step count. | MUST | BRD-PROPOSAL-002, BRD-PROPOSAL-003 | 1.1 | 13 Jan 2026 | — |

---

## 5. planning_agent (AGENT-PLANNING)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-PLANNING-001 | planning_agent MUST support both intent interpretation and replanning based on context. | MUST | BRD-PLANNING-001, BRD-PLANNING-002 | 1.1 | 13 Jan 2026 | — |
| AGENT-PLANNING-002 | planning_agent MUST produce replan notes after rejection explaining what changed and restart step. | MUST | BRD-PLANNING-002 | 1.1 | 13 Jan 2026 | — |

---

## 6. sufficiency_evaluator (AGENT-SUFF)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-SUFF-001 | sufficiency_evaluator MUST output confidence_level (high/medium/low) and downgrade_reasons. | MUST | BRD-SUFF-001, BRD-SUFF-002 | 1.1 | 13 Jan 2026 | — |
| AGENT-SUFF-002 | sufficiency_evaluator MUST use standard confidence levels reflecting data quality assessment. | MUST | BRD-SUFF-002 | 1.1 | 13 Jan 2026 | — |
| AGENT-SUFF-003 | sufficiency_evaluator MUST explain confidence downgrades with human-readable reasons (empty list when confidence is high). | MUST | BRD-SUFF-003, BRD-CONF-004 | 1.1 | 13 Jan 2026 | — |
| AGENT-SUFF-004 | sufficiency_evaluator SHOULD evaluate row count sufficiency, column completeness, and data freshness from data_reader output. | SHOULD | BRD-SUFF-004, BRD-SUFF-005, BRD-SUFF-006 | 1.1 | 13 Jan 2026 | — |

---

## 7. dashboard_agent (AGENT-DASH)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-DASH-001 | dashboard_agent MUST produce human-readable narrative summary reflecting dataset characteristics (< 500 words). | MUST | BRD-NARR-001, BRD-NARR-002 | 1.1 | 13 Jan 2026 | — |
| AGENT-DASH-002 | dashboard_agent MUST accept dataset summaries as input and summarize key metrics and trends. | MUST | BRD-NARR-001 | 1.1 | 13 Jan 2026 | — |

---

## 8. Reasoning Ladder (AGENT-REASON)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-REASON-001 | ADE MUST use multi-stage reasoning (interpret → propose → critique → finalize) with explicit stage identifiers in outputs. | MUST | BRD-INTEL-001, BRD-INTEL-002 | 1.1 | 13 Jan 2026 | — |
| AGENT-REASON-002 | Each reasoning stage MUST be observable in traces with stage name and stored artifacts. | MUST | BRD-INTEL-002 | 1.1 | 13 Jan 2026 | — |
| AGENT-REASON-003 | Reasoning cycles MUST be bounded by iterations, tools, and time limits. | MUST | BRD-INTEL-003 | 1.1 | 13 Jan 2026 | — |
| AGENT-REASON-004 | Reasoning MUST track sufficiency state across cycles with known/unknown/blocked fields. | MUST | BRD-INTEL-004 | 1.1 | 13 Jan 2026 | — |
| AGENT-REASON-005 | Final outputs MUST include stop_reason (sufficient/budget_exhausted/missing_inputs/conflict). | MUST | BRD-INTEL-005 | 1.1 | 13 Jan 2026 | — |

---

## 9. Critique Requirements (AGENT-CRIT)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-CRIT-001 | A critique stage MUST run before final outputs and be referenced by final output. | MUST | BRD-CRIT-001, BRD-CRIT-006 | 1.1 | 13 Jan 2026 | — |
| AGENT-CRIT-002 | Critique MUST identify missing or weak evidence and enumerate evidence gaps. | MUST | BRD-CRIT-002 | 1.1 | 13 Jan 2026 | — |
| AGENT-CRIT-003 | Critique MUST be able to downgrade confidence with revised_confidence and downgrade_reason fields. | MUST | BRD-CRIT-003 | 1.1 | 13 Jan 2026 | — |
| AGENT-CRIT-004 | Critique MUST NOT execute tools or route flows (advisory only). | MUST | BRD-CRIT-004 | 1.1 | 13 Jan 2026 | — |
| AGENT-CRIT-005 | Blocking critique findings MUST emit blocking_required flag and trigger ASK_USER or ABORT. | MUST | BRD-CRIT-005 | 1.1 | 13 Jan 2026 | — |

---

## 10. Advisory Tool Selection (AGENT-TOOLSEL)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-TOOLSEL-001 | Tool selection MUST be surfaced as advisory recommendations with explicit list and rationales. | MUST | BRD-TOOLSEL-001 | 1.1 | 13 Jan 2026 | — |
| AGENT-TOOLSEL-002 | Tool recommendations MAY be ranked with rationales. | MAY | BRD-TOOLSEL-002 | 1.1 | 13 Jan 2026 | — |
| AGENT-TOOLSEL-003 | Orchestrator MUST remain the sole authority for tool execution (not triggered by agent output). | MUST | BRD-TOOLSEL-003 | 1.1 | 13 Jan 2026 | — |
| AGENT-TOOLSEL-004 | Advisory tool suggestions MUST NOT force execution (recommendations are optional). | MUST | BRD-TOOLSEL-004 | 1.1 | 13 Jan 2026 | — |

---

## 11. Framework Alignment (AGENT-FRI)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-FRI-001 | Product reasoning MUST rely on framework primitives using core reasoning ladder interfaces. | MUST | BRD-CONF-005 | 1.1 | 13 Jan 2026 | — |
| AGENT-FRI-002 | Product MUST NOT re-implement orchestrator logic, iteration control, or reasoning ladder semantics. | MUST | BRD-CONF-005 | 1.1 | 13 Jan 2026 | — |
| AGENT-FRI-003 | Product MUST NOT bypass framework governance hooks. | MUST | BRD-CONF-005 | 1.1 | 13 Jan 2026 | — |
| AGENT-FRI-004 | Framework gaps MUST be escalated and logged in product docs, not worked around. | MUST | BRD-CONF-005 | 1.1 | 13 Jan 2026 | — |

---

## 12. No Runtime Learning (AGENT-NRL)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| AGENT-NRL-001 | Product MUST NOT modify behavior at runtime based on prior runs. | MUST | BRD-CONF-005 | 1.1 | 13 Jan 2026 | — |
| AGENT-NRL-002 | Product MUST NOT persist learned patterns across runs. | MUST | BRD-CONF-005 | 1.1 | 13 Jan 2026 | — |
| AGENT-NRL-003 | Product evolution MUST follow intent → BRD → implementation lifecycle. | MUST | BRD-CONF-005 | 1.1 | 13 Jan 2026 | — |
| AGENT-NRL-004 | Identical inputs MUST produce identical outputs across runs. | MUST | BRD-PLANGEN-004 | 1.1 | 13 Jan 2026 | — |

---

## 13. ADESemanticAdapter (SEM-ADAPTER)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SEM-ADAPTER-001 | ADESemanticAdapter MUST be implemented in products/ade/semantic_adapter.py exporting ADESemanticAdapter class. | MUST | BRD-SEM-001 | 1.1 | 13 Jan 2026 | — |
| SEM-ADAPTER-002 | ADESemanticAdapter.interpret() MUST accept string user_input and optional context Dict, returning SemanticEnvelope. | MUST | BRD-SEM-001 | 1.1 | 13 Jan 2026 | — |
| SEM-ADAPTER-003 | SemanticEnvelope MUST include fields: intent_type, requested_outputs, metrics, time_scope, constraints, confidence, raw_input. | MUST | BRD-SEM-002 | 1.1 | 13 Jan 2026 | — |
| SEM-ADAPTER-004 | ADESemanticAdapter MUST classify input into ADE intent types using deterministic keyword/pattern matching (no LLM). | MUST | BRD-SEM-002, BRD-SEM-003 | 1.1 | 13 Jan 2026 | — |
| SEM-ADAPTER-005 | ADESemanticAdapter MUST provide confidence score (0.0-1.0) reflecting certainty and field completeness. | MUST | BRD-SEM-004 | 1.1 | 13 Jan 2026 | — |

---

## 14. ADE Intent Taxonomy (SEM-INTENT)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SEM-INTENT-001 | ADE intent taxonomy MUST be implemented in products/ade/intents.py exporting ADEIntentType enum and INTENT_REQUIREMENTS mapping. | MUST | BRD-INTENT-TAX-006 | 1.1 | 13 Jan 2026 | — |
| SEM-INTENT-002 | ADEIntentType MUST define values: DESCRIBE_DATA, COMPARE_PERIODS, TREND_ANALYSIS, ANOMALY_REVIEW, OPEN_ENDED_ANALYSIS. | MUST | BRD-INTENT-TAX-001, BRD-INTENT-TAX-002, BRD-INTENT-TAX-003, BRD-INTENT-TAX-004, BRD-INTENT-TAX-005 | 1.1 | 13 Jan 2026 | — |
| SEM-INTENT-003 | DESCRIBE_DATA intent MUST require dataset field; metrics and time_scope are optional. | MUST | BRD-INTENT-TAX-001 | 1.1 | 13 Jan 2026 | — |
| SEM-INTENT-004 | COMPARE_PERIODS intent MUST require dataset and time_scope fields; metrics is optional. | MUST | BRD-INTENT-TAX-002 | 1.1 | 13 Jan 2026 | — |
| SEM-INTENT-005 | TREND_ANALYSIS intent MUST require dataset, metrics, and time_scope fields. | MUST | BRD-INTENT-TAX-003 | 1.1 | 13 Jan 2026 | — |
| SEM-INTENT-006 | ANOMALY_REVIEW intent MUST require dataset and metrics fields; time_scope is optional. | MUST | BRD-INTENT-TAX-004 | 1.1 | 13 Jan 2026 | — |
| SEM-INTENT-007 | OPEN_ENDED_ANALYSIS intent MUST require dataset field; metrics and time_scope are optional. | MUST | BRD-INTENT-TAX-005 | 1.1 | 13 Jan 2026 | — |

---

## 15. Semantic Validation (SEM-VALIDATE)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SEM-VALIDATE-001 | Semantic validation MUST be implemented in products/ade/semantic_validation.py exporting validate_semantic_envelope and ValidationResult. | MUST | BRD-SEM-VAL-001 | 1.1 | 13 Jan 2026 | — |
| SEM-VALIDATE-002 | validate_semantic_envelope MUST accept SemanticEnvelope and ADEIntentType, returning ValidationResult. | MUST | BRD-SEM-VAL-001 | 1.1 | 13 Jan 2026 | — |
| SEM-VALIDATE-003 | ValidationResult MUST include fields: is_valid, missing_fields, clarifying_question, confidence_adjustment, outcome. | MUST | BRD-SEM-VAL-001, BRD-SEM-VAL-002 | 1.1 | 13 Jan 2026 | — |
| SEM-VALIDATE-004 | Validation MUST return outcome="ASK_USER" with clarifying_question when missing_fields is non-empty. | MUST | BRD-SEM-VAL-003 | 1.1 | 13 Jan 2026 | — |
| SEM-VALIDATE-005 | Validation MUST return outcome="ABORT" when critical fields cannot be inferred and no clarification is possible. | MUST | BRD-SEM-VAL-004 | 1.1 | 13 Jan 2026 | — |
| SEM-VALIDATE-006 | Validation MUST return outcome="PROCEED" with is_valid=True when all required fields present. | MUST | BRD-SEM-VAL-001 | 1.1 | 13 Jan 2026 | — |
| SEM-VALIDATE-007 | ValidationResult MUST compute confidence_adjustment (-1.0 to 0.0) based on field completeness. | MUST | BRD-SEM-VAL-005 | 1.1 | 13 Jan 2026 | — |

---

## 16. Clarifying Question Templates (SEM-CLARIFY)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SEM-CLARIFY-001 | Clarifying questions MUST be implemented in products/ade/clarifying_questions.py exporting get_clarifying_question and CLARIFYING_TEMPLATES. | MUST | BRD-CLARIFY-001, BRD-CLARIFY-002 | 1.1 | 13 Jan 2026 | — |
| SEM-CLARIFY-002 | CLARIFYING_TEMPLATES MUST map missing fields to deterministic question templates. | MUST | BRD-CLARIFY-002, BRD-CLARIFY-003 | 1.1 | 13 Jan 2026 | — |
| SEM-CLARIFY-003 | System MUST provide template for metric focus: "Which specific metric would you like to focus on? (e.g., revenue, cost, volume)". | MUST | BRD-CLARIFY-004 | 1.1 | 13 Jan 2026 | — |
| SEM-CLARIFY-004 | System MUST provide template for time range: "What time period should we analyze? (e.g., last 30 days, Q1 2024, YTD)". | MUST | BRD-CLARIFY-005 | 1.1 | 13 Jan 2026 | — |
| SEM-CLARIFY-005 | System MUST provide template for anomaly preference: "What threshold should we use for anomaly detection? (default: 2.0 standard deviations)". | MUST | BRD-CLARIFY-006 | 1.1 | 13 Jan 2026 | — |
| SEM-CLARIFY-006 | Clarifying questions MUST NOT use LLM for generation (all from predefined templates). | MUST | BRD-CLARIFY-002 | 1.1 | 13 Jan 2026 | — |

---

## 17. Intent Router (SEM-ROUTER)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SEM-ROUTER-001 | Intent router MUST be implemented in products/ade/intent_router.py exporting route_intent and RouteResult. | MUST | BRD-ROUTER-001 | 1.1 | 13 Jan 2026 | — |
| SEM-ROUTER-002 | route_intent MUST accept SemanticEnvelope and return RouteResult with flow_name and initial_parameters. | MUST | BRD-ROUTER-002 | 1.1 | 13 Jan 2026 | — |
| SEM-ROUTER-003 | Router MUST use deterministic mapping: DESCRIBE_DATA→visualization, COMPARE_PERIODS→ade_v1, TREND_ANALYSIS→ade_v1, ANOMALY_REVIEW→ade_v1, OPEN_ENDED_ANALYSIS→visualization. | MUST | BRD-ROUTER-003, BRD-ROUTER-004 | 1.1 | 13 Jan 2026 | — |
| SEM-ROUTER-004 | Router MUST map SemanticEnvelope fields to flow parameters with dataset always included. | MUST | BRD-ROUTER-002 | 1.1 | 13 Jan 2026 | — |

---

## 18. Semantic Observability (SEM-OBS)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SEM-OBS-001 | Semantic observability MUST be implemented in products/ade/observability.py exporting emit_semantic_trace and integrating with core hooks. | MUST | BRD-SEM-OBS-001 | 1.1 | 13 Jan 2026 | — |
| SEM-OBS-002 | Semantic traces MUST extend core trace events with ADE fields in metadata.product_specific namespace. | MUST | BRD-SEM-OBS-001 | 1.1 | 13 Jan 2026 | — |
| SEM-OBS-003 | Trace MUST include ade_intent field with intent type string on all semantic interpretation events. | MUST | BRD-SEM-OBS-002 | 1.1 | 13 Jan 2026 | — |
| SEM-OBS-004 | Trace MUST include ade_confidence field (0.0-1.0) reflecting final adjusted confidence. | MUST | BRD-SEM-OBS-003 | 1.1 | 13 Jan 2026 | — |
| SEM-OBS-005 | Trace MUST include ade_missing_fields (List[str]) when validation detects gaps. | MUST | BRD-SEM-OBS-004 | 1.1 | 13 Jan 2026 | — |
| SEM-OBS-006 | Trace MUST include ade_clarifying_question when question is generated. | MUST | BRD-SEM-OBS-005 | 1.1 | 13 Jan 2026 | — |

---

## Cross-References

- **BRD**: [BRD-agents.md](../01_brd/BRD-agents.md)
