# Developer Intent: Operational Excellence (INT-OPS)

> **Maps to**: [BRD-operations.md](../02_brd/BRD-operations.md)  
> **Version**: 1.2  
> **Source**: Extracted from [intent.md](intent.md) § 4

---

## Purpose

Define platform-level operational intent for state, observability, performance, testing, and architecture invariants.

## Scope

- Platform-only operational requirements.
- Product-specific operational policies are out of scope.

---

## PLAT-OPS-STATE — State Persistence

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-OPS-001 | Run state SHALL survive process restarts — Reliability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-002 | In-flight workflows SHALL be resumable after restart — No lost work | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-003 | State SHALL be persisted durably (not just in-memory) — Data safety | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-004 | State storage SHALL support concurrent access — Scalability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-005 | Historical runs SHALL be queryable — Audit, debugging | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-006 | State SHALL survive restarts — Prevent run loss after restart | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-007 | State transitions SHALL be traced — Prevent silent state changes | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-008 | All actions SHALL be traced — Prevent untracked actions | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-OBS — Observability

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-OPS-010 | Every execution step SHALL be traced — Debugging | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-011 | Traces SHALL include: timestamp, event type, data — Complete picture | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-012 | Traces SHALL be queryable by run, step, timeframe — Investigation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-013 | Large outputs SHALL be stored to files, not inline — Storage efficiency | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-014 | Observability data SHALL be organized by product/run — Multi-tenancy | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-015 | Dashboards SHALL visualize run status and trends — Operations monitoring | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-SEM-TRACE — Semantic Trace Events

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-OPS-SEM-001 | `semantic_interpretation_started` event SHALL be emitted when phase begins — Track phase lifecycle | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-002 | Started event SHALL include: run_id, product_id, raw_input_length — Context for debugging | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-003 | `semantic_interpretation_completed` event SHALL be emitted when phase succeeds — Track successful interpretation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-004 | Completed event SHALL include: envelope_hash, confidence, ambiguity_count, entity_count, next_action — Interpretation metrics | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-005 | `semantic_validation_completed` event SHALL be emitted after validation — Track validation outcome | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-006 | Validation event SHALL include: is_valid, missing_fields, violation_count, revised_confidence — Validation metrics | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-007 | `semantic_stop_issued` event SHALL be emitted on ASK_USER or ABORT — Track stop decisions | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-008 | Stop event SHALL include: next_action, question (if ASK_USER), reason (if ABORT), violations — Stop context | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-009 | `semantic_interpretation_failed` event SHALL be emitted on exception — Error visibility | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-010 | Failed event SHALL include: error message — Debugging information | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-011 | Events SHALL be structured — Avoid free-form logs | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-012 | Events SHALL include run_id — Ensure correlation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-013 | Events SHALL include timestamps — Ensure event ordering | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

### Event Catalog (Reference)

- `semantic_interpretation_started`: `run_id`, `product_id`, `raw_input_length`
- `semantic_interpretation_completed`: `envelope_hash`, `confidence`, `ambiguity_count`, `entity_count`, `next_action`
- `semantic_validation_completed`: `is_valid`, `missing_fields`, `violation_count`, `revised_confidence`
- `semantic_stop_issued`: `next_action`, `question`, `reason`, `violations`
- `semantic_interpretation_failed`: `error`

---

## PLAT-OPS-REPRO — Explainability & Reproducibility

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-OPS-001 | Platform SHALL guarantee post-hoc explainability and reproducibility by retaining reasoning artifacts and execution context — Make outcomes explainable and repeatable | PLAT-AUD-001 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |
| PLAT-OPS-002 | Platform SHALL record versions, inputs, and hashes required to reproduce outcomes — Enable deterministic replay and audit | PLAT-OPS-001 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |

---

## PLAT-OPS-PERF — Performance

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-OPS-020 | API responses SHALL complete within 500ms (p95) — User experience | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-021 | Run startup SHALL complete within 2 seconds — Responsiveness | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-022 | Memory backend operations SHALL complete within 100ms — System responsiveness | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-023 | Performance metrics SHALL be measurable — SLA monitoring | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-QA — Quality Assurance

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-OPS-030 | Core modules SHALL have ≥80% test coverage — Quality baseline | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-031 | Critical paths (run lifecycle) SHALL have 100% coverage — Risk mitigation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-032 | All tests SHALL pass before deployment — Quality gate | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-033 | Tests SHALL complete within 10 minutes — Developer velocity | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-034 | Contracts (Pydantic models) SHALL have validation tests — Interface stability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-DEBUG — Debugging Support

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-OPS-040 | Failed runs SHALL include error details and stack traces — Root cause analysis | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-041 | Event timeline SHALL be viewable for any run — Execution understanding | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-042 | Input/output data SHALL be inspectable — Data debugging | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-043 | LLM calls and responses SHALL be logged — AI debugging | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-044 | Tool calls and results SHALL be logged — Integration debugging | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-ARCHTEST — Architecture Tests

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-OPS-ARCH-001 | Architecture test SHALL verify semantic phase is mandatory — Prevent regression of mandatory phase | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-002 | Architecture test SHALL verify ASK_USER blocks all step execution — Lock stop behavior | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-003 | Architecture test SHALL verify ABORT blocks all step execution — Lock abort behavior | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-004 | Architecture test SHALL verify product adapters do not import core orchestrator — Enforce isolation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-005 | Architecture test SHALL verify core orchestrator does not import products — Enforce isolation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-006 | Architecture tests SHALL live in `tests/architecture/` directory — Clear test organization | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-007 | Architecture tests SHALL run as part of CI pipeline — Continuous enforcement | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-008 | Architecture tests SHALL pass — Prevent ignoring failures | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-009 | Tests SHALL verify structure, not behavior — Validate architecture invariants | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-010 | Tests SHALL be automated — Avoid manual verification | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

### Required Architecture Tests (Reference)

- `test_semantic_phase_is_mandatory`: ORC-SEM-001
- `test_stop_blocks_execution`: ORC-SEM-STOP-001
- `test_product_adapter_isolated`: PROD-SEM-INT-005/006

---

## PLAT-INV — Architecture Invariants

> **Non-negotiable principles that force all BRDs, specs, and code to align.**

### INV-1: Reasoning as a Framework Primitive (Not Product Logic)

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-INV-001 | MASTER SHALL provide standard reasoning middleware primitives that products can invoke without custom orchestration — Reasoning is a platform capability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-002 | Reasoning SHALL follow a structured, multi-phase pattern (interpret → propose → critique → recommend) within a controlled step — Consistent and auditable reasoning | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-003 | Reasoning primitives SHALL be bounded, repeatable, and auditable — Prevent open-ended reasoning | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-004 | Reasoning outputs SHALL be first-class artifacts, not ephemeral prompt responses — Preserve outputs for auditability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

Intent signal: Reasoning depth is a platform capability, not something each product reinvents.

### INV-2: Critique Is Mandatory, Bounded, and Non-Controlling

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-INV-005 | MASTER SHALL support explicit critique passes as part of intelligent execution — Ensure quality checks | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-006 | Critique SHALL be advisory only: it may lower confidence, surface gaps, or recommend escalation — Preserve control boundaries | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-007 | Critique SHALL NEVER execute tools, route flows, override policies, or force decisions — Prevent unauthorized control | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-008 | Control authority SHALL always remain with the orchestrator and governance layer — Centralize control | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

Intent signal: Self-reflection is allowed; self-control is not.

### INV-3: Semantic Interpretation Is Probabilistic, Not Truth

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-INV-009 | All semantic interpretations SHALL be treated as hypotheses with confidence, not facts — Prevent over-trust | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-010 | MASTER SHALL represent interpretation as multiple competing candidates where ambiguity exists — Preserve ambiguity | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-011 | Confidence and ambiguity SHALL propagate into downstream artifacts, decisions, and outputs — Preserve uncertainty | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-012 | When ambiguity exceeds policy thresholds, execution SHALL require HITL or halt safely — Avoid unsafe execution | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

Intent signal: Ambiguity is a first-class state, not an error condition.

### INV-4: Decisions Must Be Explainable and Auditable by Construction

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-INV-013 | Any gated or consequential decision SHALL be recorded as a decision artifact — Preserve decision history | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-014 | Decision artifacts SHALL capture options, evidence, critique input, final choice, justification, confidence — Ensure auditability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-015 | Decision artifacts SHALL be immutable once recorded — Prevent tampering | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

Intent signal: Explainability is structural, not narrative.

### INV-5: Iteration Is Orchestrator-Controlled, Not Agent-Driven

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-INV-016 | MASTER SHALL provide standard iteration patterns for intelligent workflows — Avoid ad hoc iteration | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-017 | Iteration SHALL follow a governed cycle (propose → gate → execute → evaluate) — Controlled iteration | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-018 | Iteration SHALL have explicit deterministic stop conditions (budgets, sufficiency, escalation) — Avoid runaway loops | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-019 | Iterative state SHALL be durable and resumable across restarts — Reliability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

Intent signal: Investigation is allowed; autonomy is not.

### INV-6: Platform Laws Are Explicit and Non-Negotiable

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-INV-020 | Agents SHALL be advisory only and MUST NOT control execution, routing, or side effects — Preserve control boundaries | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-021 | Only the orchestrator SHALL execute tools, change flow state, pause/resume runs, and escalate to HITL — Centralize execution control | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-022 | Governance hooks SHALL be non-bypassable at all lifecycle points — Enforce governance | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-023 | Products SHALL be isolated and MUST NOT access other products' resources directly — Enforce product isolation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

Intent signal: Safety is enforced by structure, not convention.

### INV-7: Reasoning Observability Is as Important as Execution Observability

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-INV-024 | MASTER SHALL make reasoning behavior observable, not just execution steps — Audit reasoning | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-025 | Traces SHALL expose options considered, confidence evolution, rejection and escalation reasons — Explainability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-INV-026 | Reasoning traces SHALL be queryable for audit, debugging, and improvement analysis — Continuous improvement | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

Intent signal: "Why" matters as much as "what happened".

---

## Removed / Quarantined Content (Out of Platform Scope)

- None.

---

## BRD Derivation

This document derives the following in [BRD-operations.md](../02_brd/BRD-operations.md):

- INT-OPS-* → BRD-OPS-*
- INT-OPS-SEM-* → BRD-OPS-SEM-*
- INT-OPS-ARCH-* → BRD-OPS-ARCH-*
