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

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-OPS-001 | Run state SHALL survive process restarts | Reliability | — | legacy content (intent-operations.md#4.1) | ID NEEDS NORMALIZATION |
| INT-OPS-002 | In-flight workflows SHALL be resumable after restart | No lost work | — | legacy content (intent-operations.md#4.1) | ID NEEDS NORMALIZATION |
| INT-OPS-003 | State SHALL be persisted durably (not just in-memory) | Data safety | — | legacy content (intent-operations.md#4.1) | ID NEEDS NORMALIZATION |
| INT-OPS-004 | State storage SHALL support concurrent access | Scalability | — | legacy content (intent-operations.md#4.1) | ID NEEDS NORMALIZATION |
| INT-OPS-005 | Historical runs SHALL be queryable | Audit, debugging | — | legacy content (intent-operations.md#4.1) | ID NEEDS NORMALIZATION |
| — | State SHALL survive restarts | Prevent run loss after restart | — | legacy content (intent-operations.md#4.1 constraints) | ID NEEDS NORMALIZATION |
| — | State transitions SHALL be traced | Prevent silent state changes | — | legacy content (intent-operations.md#4.1 constraints) | ID NEEDS NORMALIZATION |
| — | All actions SHALL be traced | Prevent untracked actions | — | legacy content (intent-operations.md#4.1 constraints) | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-OBS — Observability

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-OPS-010 | Every execution step SHALL be traced | Debugging | — | legacy content (intent-operations.md#4.2) | ID NEEDS NORMALIZATION |
| INT-OPS-011 | Traces SHALL include: timestamp, event type, data | Complete picture | — | legacy content (intent-operations.md#4.2) | ID NEEDS NORMALIZATION |
| INT-OPS-012 | Traces SHALL be queryable by run, step, timeframe | Investigation | — | legacy content (intent-operations.md#4.2) | ID NEEDS NORMALIZATION |
| INT-OPS-013 | Large outputs SHALL be stored to files, not inline | Storage efficiency | — | legacy content (intent-operations.md#4.2) | ID NEEDS NORMALIZATION |
| INT-OPS-014 | Observability data SHALL be organized by product/run | Multi-tenancy | — | legacy content (intent-operations.md#4.2) | ID NEEDS NORMALIZATION |
| INT-OPS-015 | Dashboards SHALL visualize run status and trends | Operations monitoring | — | legacy content (intent-operations.md#4.2) | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-SEM-TRACE — Semantic Trace Events

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-OPS-SEM-001 | `semantic_interpretation_started` event SHALL be emitted when phase begins | Track phase lifecycle | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-002 | Started event SHALL include: run_id, product_id, raw_input_length | Context for debugging | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-003 | `semantic_interpretation_completed` event SHALL be emitted when phase succeeds | Track successful interpretation | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-004 | Completed event SHALL include: envelope_hash, confidence, ambiguity_count, entity_count, next_action | Interpretation metrics | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-005 | `semantic_validation_completed` event SHALL be emitted after validation | Track validation outcome | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-006 | Validation event SHALL include: is_valid, missing_fields, violation_count, revised_confidence | Validation metrics | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-007 | `semantic_stop_issued` event SHALL be emitted on ASK_USER or ABORT | Track stop decisions | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-008 | Stop event SHALL include: next_action, question (if ASK_USER), reason (if ABORT), violations | Stop context | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-009 | `semantic_interpretation_failed` event SHALL be emitted on exception | Error visibility | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| INT-OPS-SEM-010 | Failed event SHALL include: error message | Debugging information | — | legacy content (intent-operations.md#4.3) | ID NEEDS NORMALIZATION |
| — | Events SHALL be structured | Avoid free-form logs | — | legacy content (intent-operations.md#4.3 constraints) | ID NEEDS NORMALIZATION |
| — | Events SHALL include run_id | Ensure correlation | — | legacy content (intent-operations.md#4.3 constraints) | ID NEEDS NORMALIZATION |
| — | Events SHALL include timestamps | Ensure event ordering | — | legacy content (intent-operations.md#4.3 constraints) | ID NEEDS NORMALIZATION |

### Event Catalog (Reference)

- `semantic_interpretation_started`: `run_id`, `product_id`, `raw_input_length`
- `semantic_interpretation_completed`: `envelope_hash`, `confidence`, `ambiguity_count`, `entity_count`, `next_action`
- `semantic_validation_completed`: `is_valid`, `missing_fields`, `violation_count`, `revised_confidence`
- `semantic_stop_issued`: `next_action`, `question`, `reason`, `violations`
- `semantic_interpretation_failed`: `error`

---

## PLAT-OPS-REPRO — Explainability & Reproducibility

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| PLAT-OPS-001 | Platform SHALL guarantee post-hoc explainability and reproducibility by retaining reasoning artifacts and execution context | Make outcomes explainable and repeatable | PLAT-AUD-001 | bullet 10 | V1.2, 2026-01-18 |
| PLAT-OPS-002 | Platform SHALL record versions, inputs, and hashes required to reproduce outcomes | Enable deterministic replay and audit | PLAT-OPS-001 | bullet 10 | V1.2, 2026-01-18 |

---

## PLAT-OPS-PERF — Performance

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-OPS-020 | API responses SHALL complete within 500ms (p95) | User experience | — | legacy content (intent-operations.md#4.4) | ID NEEDS NORMALIZATION |
| INT-OPS-021 | Run startup SHALL complete within 2 seconds | Responsiveness | — | legacy content (intent-operations.md#4.4) | ID NEEDS NORMALIZATION |
| INT-OPS-022 | Memory backend operations SHALL complete within 100ms | System responsiveness | — | legacy content (intent-operations.md#4.4) | ID NEEDS NORMALIZATION |
| INT-OPS-023 | Performance metrics SHALL be measurable | SLA monitoring | — | legacy content (intent-operations.md#4.4) | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-QA — Quality Assurance

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-OPS-030 | Core modules SHALL have ≥80% test coverage | Quality baseline | — | legacy content (intent-operations.md#4.5) | ID NEEDS NORMALIZATION |
| INT-OPS-031 | Critical paths (run lifecycle) SHALL have 100% coverage | Risk mitigation | — | legacy content (intent-operations.md#4.5) | ID NEEDS NORMALIZATION |
| INT-OPS-032 | All tests SHALL pass before deployment | Quality gate | — | legacy content (intent-operations.md#4.5) | ID NEEDS NORMALIZATION |
| INT-OPS-033 | Tests SHALL complete within 10 minutes | Developer velocity | — | legacy content (intent-operations.md#4.5) | ID NEEDS NORMALIZATION |
| INT-OPS-034 | Contracts (Pydantic models) SHALL have validation tests | Interface stability | — | legacy content (intent-operations.md#4.5) | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-DEBUG — Debugging Support

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-OPS-040 | Failed runs SHALL include error details and stack traces | Root cause analysis | — | legacy content (intent-operations.md#4.6) | ID NEEDS NORMALIZATION |
| INT-OPS-041 | Event timeline SHALL be viewable for any run | Execution understanding | — | legacy content (intent-operations.md#4.6) | ID NEEDS NORMALIZATION |
| INT-OPS-042 | Input/output data SHALL be inspectable | Data debugging | — | legacy content (intent-operations.md#4.6) | ID NEEDS NORMALIZATION |
| INT-OPS-043 | LLM calls and responses SHALL be logged | AI debugging | — | legacy content (intent-operations.md#4.6) | ID NEEDS NORMALIZATION |
| INT-OPS-044 | Tool calls and results SHALL be logged | Integration debugging | — | legacy content (intent-operations.md#4.6) | ID NEEDS NORMALIZATION |

---

## PLAT-OPS-ARCHTEST — Architecture Tests

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-OPS-ARCH-001 | Architecture test SHALL verify semantic phase is mandatory | Prevent regression of mandatory phase | — | legacy content (intent-operations.md#4.7) | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-002 | Architecture test SHALL verify ASK_USER blocks all step execution | Lock stop behavior | — | legacy content (intent-operations.md#4.7) | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-003 | Architecture test SHALL verify ABORT blocks all step execution | Lock abort behavior | — | legacy content (intent-operations.md#4.7) | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-004 | Architecture test SHALL verify product adapters do not import core orchestrator | Enforce isolation | — | legacy content (intent-operations.md#4.7) | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-005 | Architecture test SHALL verify core orchestrator does not import products | Enforce isolation | — | legacy content (intent-operations.md#4.7) | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-006 | Architecture tests SHALL live in `tests/architecture/` directory | Clear test organization | — | legacy content (intent-operations.md#4.7) | ID NEEDS NORMALIZATION |
| INT-OPS-ARCH-007 | Architecture tests SHALL run as part of CI pipeline | Continuous enforcement | — | legacy content (intent-operations.md#4.7) | ID NEEDS NORMALIZATION |
| — | Architecture tests SHALL pass | Prevent ignoring failures | — | legacy content (intent-operations.md#4.7 constraints) | ID NEEDS NORMALIZATION |
| — | Tests SHALL verify structure, not behavior | Validate architecture invariants | — | legacy content (intent-operations.md#4.7 constraints) | ID NEEDS NORMALIZATION |
| — | Tests SHALL be automated | Avoid manual verification | — | legacy content (intent-operations.md#4.7 constraints) | ID NEEDS NORMALIZATION |

### Required Architecture Tests (Reference)

- `test_semantic_phase_is_mandatory`: ORC-SEM-001
- `test_stop_blocks_execution`: ORC-SEM-STOP-001
- `test_product_adapter_isolated`: PROD-SEM-INT-005/006

---

## PLAT-INV — Architecture Invariants

> **Non-negotiable principles that force all BRDs, specs, and code to align.**

### INV-1: Reasoning as a Framework Primitive (Not Product Logic)

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| — | MASTER SHALL provide standard reasoning middleware primitives that products can invoke without custom orchestration | Reasoning is a platform capability | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Reasoning SHALL follow a structured, multi-phase pattern (interpret → propose → critique → recommend) within a controlled step | Consistent and auditable reasoning | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Reasoning primitives SHALL be bounded, repeatable, and auditable | Prevent open-ended reasoning | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Reasoning outputs SHALL be first-class artifacts, not ephemeral prompt responses | Preserve outputs for auditability | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |

Intent signal: Reasoning depth is a platform capability, not something each product reinvents.

### INV-2: Critique Is Mandatory, Bounded, and Non-Controlling

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| — | MASTER SHALL support explicit critique passes as part of intelligent execution | Ensure quality checks | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Critique SHALL be advisory only: it may lower confidence, surface gaps, or recommend escalation | Preserve control boundaries | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Critique SHALL NEVER execute tools, route flows, override policies, or force decisions | Prevent unauthorized control | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Control authority SHALL always remain with the orchestrator and governance layer | Centralize control | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |

Intent signal: Self-reflection is allowed; self-control is not.

### INV-3: Semantic Interpretation Is Probabilistic, Not Truth

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| — | All semantic interpretations SHALL be treated as hypotheses with confidence, not facts | Prevent over-trust | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | MASTER SHALL represent interpretation as multiple competing candidates where ambiguity exists | Preserve ambiguity | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Confidence and ambiguity SHALL propagate into downstream artifacts, decisions, and outputs | Preserve uncertainty | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | When ambiguity exceeds policy thresholds, execution SHALL require HITL or halt safely | Avoid unsafe execution | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |

Intent signal: Ambiguity is a first-class state, not an error condition.

### INV-4: Decisions Must Be Explainable and Auditable by Construction

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| — | Any gated or consequential decision SHALL be recorded as a decision artifact | Preserve decision history | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Decision artifacts SHALL capture options, evidence, critique input, final choice, justification, confidence | Ensure auditability | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Decision artifacts SHALL be immutable once recorded | Prevent tampering | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |

Intent signal: Explainability is structural, not narrative.

### INV-5: Iteration Is Orchestrator-Controlled, Not Agent-Driven

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| — | MASTER SHALL provide standard iteration patterns for intelligent workflows | Avoid ad hoc iteration | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Iteration SHALL follow a governed cycle (propose → gate → execute → evaluate) | Controlled iteration | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Iteration SHALL have explicit deterministic stop conditions (budgets, sufficiency, escalation) | Avoid runaway loops | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Iterative state SHALL be durable and resumable across restarts | Reliability | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |

Intent signal: Investigation is allowed; autonomy is not.

### INV-6: Platform Laws Are Explicit and Non-Negotiable

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| — | Agents SHALL be advisory only and MUST NOT control execution, routing, or side effects | Preserve control boundaries | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Only the orchestrator SHALL execute tools, change flow state, pause/resume runs, and escalate to HITL | Centralize execution control | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Governance hooks SHALL be non-bypassable at all lifecycle points | Enforce governance | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Products SHALL be isolated and MUST NOT access other products' resources directly | Enforce product isolation | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |

Intent signal: Safety is enforced by structure, not convention.

### INV-7: Reasoning Observability Is as Important as Execution Observability

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| — | MASTER SHALL make reasoning behavior observable, not just execution steps | Audit reasoning | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Traces SHALL expose options considered, confidence evolution, rejection and escalation reasons | Explainability | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |
| — | Reasoning traces SHALL be queryable for audit, debugging, and improvement analysis | Continuous improvement | — | legacy content (intent-operations.md#Architecture Invariants) | ID NEEDS NORMALIZATION |

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
