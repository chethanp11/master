# Developer Intent: Intelligent Automation (INT-AUTO)

> **Maps to**: [BRD-automation.md](../02_brd/BRD-automation.md)  
> **Version**: 1.2  

---

## Purpose

Define platform-level intent for intelligent automation that drives BRD derivation.

## Scope

- Platform-only requirements for automation primitives, reasoning, tools, and workflows.
- Product-specific behavior and product requirements are out of scope.

---

## PLAT-AUTO-SEM — Semantic Interpretation

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-AUTO-SEM-001 | Semantic interpretation SHALL run before any step execution in every flow — Validate understanding before acting | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-002 | Interpretation SHALL produce structured `SemanticEnvelope` output — Typed, parseable result | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-003 | `SemanticEnvelope` SHALL include normalized intent, confidence score, entities, constraints — Complete interpretation context | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-004 | Confidence score SHALL range 0.0–1.0 with semantic meaning — Quantified uncertainty | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-005 | Entities SHALL be typed: PERSON, ORGANIZATION, DATE, AMOUNT, PRODUCT, CUSTOM — Domain-appropriate classification | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-006 | Ambiguities SHALL be captured as a structured list with resolution options — Enable targeted clarification | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-007 | If confidence < threshold, next_action SHALL be ASK_USER — Fail safe: don't guess on ambiguity | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-008 | If unresolvable conflict detected, next_action SHALL be ABORT with reason — Clear failure path | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-009 | Interpretation phase SHALL be product-agnostic at framework level — Reusable across products | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-010 | Products SHALL be able to override interpretation via semantic adapter interface — Product-specific customization | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-011 | Semantic phase SHALL be mandatory — Prevent bypass of interpretation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-012 | Envelope SHALL be the only handoff to planning — Prevent raw text planning | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-013 | Confidence gates SHALL control execution — Prevent low-confidence execution | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-SEM-014 | Ambiguities SHALL be explicit — Ensure ambiguity is surfaced | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-AUTO-ADAPT — Product Semantic Adapter Interface

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-AUTO-ADAPT-001 | Products SHALL be able to provide custom semantic interpretation via adapter interface — Domain-specific interpretation logic | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-002 | Adapter interface SHALL define `interpret(context) → SemanticEnvelope` method — Standardized interpretation hook | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-003 | Adapter interface SHALL define `validate(envelope, context) → ValidationResult` method — Domain-specific validation rules | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-004 | Default adapter SHALL be provided for products without custom implementation — Graceful fallback behavior | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-005 | Default adapter SHALL return passthrough envelope with confidence=1.0 — Non-blocking default behavior | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-006 | Adapters SHALL be discovered from `products/<name>/semantic.py` — Convention-based discovery | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-007 | Adapters SHALL be resolved via ProductRouter, not direct import — Maintain product isolation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-008 | Product adapters SHALL NOT import from `core/orchestrator/*` — Isolation: products don't depend on core internals | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-009 | Core orchestrator SHALL NOT import from `products/*` — Isolation: core doesn't depend on products | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-010 | Adapter execution SHALL have timeout with fallback to default — Prevent slow adapters from blocking | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-011 | Adapters SHALL be pure functions — Prevent side effects in interpretation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-012 | Adapters SHALL NOT execute tools — Keep interpretation advisory | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-013 | Adapters SHALL NOT access other products — Enforce isolation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-ADAPT-014 | Isolation SHALL be bidirectional — Prevent cross-layer imports | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-AUTO-STOP — Stop/Pause Mechanism

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-AUTO-STOP-001 | ASK_USER SHALL pause the run and return a structured clarification response — Enable user to provide additional context | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-002 | Clarification response SHALL include: question, ambiguities, original confidence, context — User has information to respond | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-003 | Run status SHALL be PAUSED_WAITING_FOR_USER during clarification — Clear state management | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-004 | ABORT SHALL fail the run with structured error response — Clean failure with explanation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-005 | Abort error SHALL include: error_code=semantic_abort, reason, violations, ambiguities — Debugging information preserved | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-006 | Run status SHALL be FAILED after ABORT — Terminal failure state | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-007 | ASK_USER and ABORT SHALL prevent any step execution — No partial execution on interpretation failure | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-008 | Trace event `semantic_stop_issued` SHALL be emitted on stop — Observability for stop decisions | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-009 | Paused runs SHALL be resumable with user-provided clarification — Continue workflow after clarification | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-010 | Stop SHALL block all steps — Prevent execution after ASK_USER | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-011 | Abort SHALL be terminal — Prevent continuation after ABORT | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-STOP-012 | Clarification SHALL be structured — Avoid free-form error messages | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-AUTO-AGENT — Agent Capabilities

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-AUTO-001 | Agents SHALL reason through multi-step tasks with observable decision points — See what agents are thinking, not just outputs | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-002 | Agents SHALL provide evidence supporting their decisions — Trust requires traceability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-003 | Agents SHALL be composable; one agent can delegate to others — Build complex workflows from tested components | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-004 | Agents SHALL handle failures gracefully with retry or escalation — Production systems must not fail silently | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-005 | Agent behavior SHALL be deterministic given the same inputs — Reproducibility for testing and compliance | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-006 | Agents SHALL be advisory only — Agents do not execute tools | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-007 | Agents SHALL be stateless — Avoid implicit state | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-008 | Agents SHALL NOT branch flows — Flow control remains orchestrator-owned | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-009 | Agents SHALL NOT modify policies — Prevent privilege escalation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-AUTO-TOOLS — Tool Ecosystem

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-AUTO-010 | Tools SHALL be discoverable with clear capability descriptions — Agents need to understand tool capabilities | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-011 | Tools SHALL have typed inputs and outputs — Prevent type mismatch failures | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-012 | Tools SHALL be executable in isolation for testing — Independent testability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-013 | Tool results SHALL include structured evidence — Support audit and explainability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-014 | Tool execution SHALL be observable and traceable — Operational accountability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-015 | Tools SHALL be deterministic — Prevent non-reproducible outputs | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-016 | Tools SHALL execute via ToolExecutor only — Centralize execution control | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-017 | Tools SHALL declare side effects — Avoid silent state changes | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-AUTO-INTEL — Intelligence Layer

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-AUTO-020 | System SHALL select appropriate tools for tasks automatically — Manual tool selection does not scale | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-021 | System SHALL select appropriate agents for subtasks — Enable dynamic delegation without hardcoding | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-022 | System SHALL identify gaps in information and request clarification — Better to ask than assume | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-023 | System SHALL summarize complex results for human consumption — Raw outputs are unusable for decisions | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-024 | System SHALL explain risks before executing high-impact actions — Informed consent for consequential operations | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-025 | System SHALL interpret user intent before planning/execution — Prevent misunderstood tasks from proceeding | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-026 | System SHALL normalize and validate input before acting — Prevent garbage-in/garbage-out | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-027 | System SHALL express interpretation confidence and request clarification when uncertain — Trigger human involvement on low confidence | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| PLAT-AUTO-001 | System SHALL support multiple competing hypotheses with confidence scores as a first-class reasoning output — Preserve uncertainty and avoid single-authority interpretations | — | 2026-01-13 | V1.1 | Clarification Needed: confirm PLAT-AUTO sequence start |
| PLAT-AUTO-002 | System SHALL maintain a persistent sufficiency state tracking known facts, unknowns, assumptions, and blocking gaps — Make sufficiency explicit during execution | — | 2026-01-13 | V1.1 | Clarification Needed: confirm PLAT-AUTO sequence start |

---

## PLAT-AUTO-REASON — Reasoning Quality

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-AUTO-030 | Reasoning SHALL progress through structured phases (interpret → propose → select) — Predictable, auditable reasoning | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-031 | Proposals SHALL be evaluated by critic before execution — Quality gate before action | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-032 | Context SHALL be enriched with relevant knowledge before reasoning — Better context yields better decisions | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-033 | Reasoning failures SHALL trigger appropriate escalation — Fail gracefully, not silently | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-ORCH — Orchestrator-Controlled Reasoning

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-ORCH-001 | Platform SHALL provide a central, reusable reasoning lifecycle (interpret → propose → critique → recommend) that is orchestrator-controlled, bounded, and non-autonomous — Make reasoning a governed platform primitive | PLAT-AUTO-001 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |
| PLAT-ORCH-002 | Orchestrator SHALL support bounded reasoning iteration with deterministic stop conditions based on sufficiency, budget, iteration limits, or human intervention — Prevent runaway reasoning loops | PLAT-AUTO-002 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |

---

## PLAT-CTRL — Confidence and Critique Control

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-CTRL-001 | Platform SHALL track, update, and propagate confidence as a core runtime signal across reasoning stages, steps, and decision gates — Make confidence a first-class control signal | PLAT-AUTO-001 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |
| PLAT-CTRL-002 | Platform SHALL enforce a mandatory advisory critique phase before finalizing any decision or output, with the ability to downgrade confidence or block progression — Ensure critique is a gate, not an afterthought | PLAT-ORCH-001 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |

---

## PLAT-EXEC — Execution Gatekeeping

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-EXEC-001 | Platform SHALL construct and freeze a ContextPack before planning or execution, consolidating data availability, evidence, constraints, and quality limitations — Provide a consistent decision context before execution | PLAT-AUTO-002 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |
| PLAT-EXEC-002 | Platform SHALL define and enforce explicit terminal outcomes (SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT) with required explanations and artifacts — Make termination semantics consistent and auditable | PLAT-CTRL-001 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |

---

## PLAT-AUTO-WORKFLOW — Workflow Execution

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-AUTO-040 | Workflows SHALL support sequential, parallel, and conditional steps — Flexible automation patterns | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-041 | Workflows SHALL support iteration over collections — Batch processing is essential | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-042 | Workflow steps SHALL be independently restartable — Failure recovery without full reruns | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-AUTO-043 | Workflows SHALL support nested sub-workflows — Complex composition from simple flows | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## Removed / Quarantined Content (Out of Platform Scope)

- None.

---

## BRD Derivation

This document derives the following in [BRD-automation.md](../02_brd/BRD-automation.md):

- INT-AUTO-* → BRD-AUTO-*
- INT-AUTO-SEM-* → BRD-AUTO-SEM-*
- INT-AUTO-ADAPT-* → BRD-AUTO-ADAPT-*
- INT-AUTO-STOP-* → BRD-AUTO-STOP-*
