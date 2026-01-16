# MASTER Framework — Developer Intent

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning

> **Document**: Framework Developer Intent  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release

---

## Purpose

This document captures the requirements that drive MASTER's Business Requirement Documents (BRDs). Each intent point (INT-*) and invariant (INV-*) maps directly to BRD requirements.

For framework philosophy, actors, and process, see [Vision.md](Vision.md).

---

## Document Structure

> **Note**: For easier reconciliation with BRD documents, domain-specific intents are also available as separate files:
> 
> | Standalone Document | Maps to BRD |
> |--------------------|-------------|
> | [intent-automation.md](intent-automation.md) | [BRD-automation.md](../02_brd/BRD-automation.md) |
> | [intent-governance.md](intent-governance.md) | [BRD-governance.md](../02_brd/BRD-governance.md) |
> | [intent-experience.md](intent-experience.md) | [BRD-experience.md](../02_brd/BRD-experience.md) |
> | [intent-operations.md](intent-operations.md) | [BRD-operations.md](../02_brd/BRD-operations.md) |

| Intent Section | Maps To | Theme |
|----------------|---------|-------|
| [Architecture Invariants](#architecture-invariants) | All BRDs | Non-negotiable platform laws |
| [§1 INT-AUTO](#1-intelligent-automation-int-auto) | [BRD-automation.md](../02_brd/BRD-automation.md) | Agents, tools, reasoning, semantic interpretation |
| [§2 INT-GOV](#2-governance--compliance-int-gov) | [BRD-governance.md](../02_brd/BRD-governance.md) | Approval, security, audit, budget, confidence thresholds |
| [§3 INT-EXP](#3-developer--user-experience-int-exp) | [BRD-experience.md](../02_brd/BRD-experience.md) | API, CLI, UI, products |
| [§4 INT-OPS](#4-operational-excellence-int-ops) | [BRD-operations.md](../02_brd/BRD-operations.md) | Persistence, observability, semantic traces, architecture tests |
| [§5 INT-LIFECYCLE](#5-developer-intent-lifecycle-int-lifecycle) | All BRDs | Ownership, evolution, feedback |
| [§6 INT-FACTORY](#6-product-factory-model-int-factory) | All BRDs | Intent-driven product creation |

---

# Architecture Invariants

> **Non-negotiable principles that force all BRDs, specs, and code to align.**

---

## INV-1: Reasoning as a Framework Primitive (Not Product Logic)

- MASTER SHALL provide standard reasoning middleware primitives that products can invoke without custom orchestration.
- Reasoning SHALL follow a structured, multi-phase pattern (interpret → propose → critique → recommend), executed within a single controlled step.
- Reasoning primitives SHALL be bounded, repeatable, and auditable, never open-ended.
- Reasoning outputs SHALL be first-class artifacts, not ephemeral prompt responses.

> **Intent signal**: Reasoning depth is a platform capability, not something each product reinvents.

---

## INV-2: Critique Is Mandatory, Bounded, and Non-Controlling

- MASTER SHALL support explicit critique passes as part of intelligent execution.
- Critique SHALL be advisory only: it may lower confidence, surface gaps, or recommend escalation.
- Critique SHALL NEVER execute tools, route flows, override policies, or force decisions.
- Control authority SHALL always remain with the orchestrator and governance layer.

> **Intent signal**: Self-reflection is allowed; self-control is not.

---

## INV-3: Semantic Interpretation Is Probabilistic, Not Truth

- All semantic interpretations SHALL be treated as hypotheses with confidence, not facts.
- MASTER SHALL represent interpretation as multiple competing candidates where ambiguity exists.
- Confidence and ambiguity SHALL propagate into downstream artifacts, decisions, and outputs.
- When ambiguity exceeds policy thresholds, execution SHALL require HITL or halt safely.

> **Intent signal**: Ambiguity is a first-class state, not an error condition.

---

## INV-4: Decisions Must Be Explainable and Auditable by Construction

- Any gated or consequential decision SHALL be recorded as a decision artifact, not just a log entry.
- Decision artifacts SHALL capture:
  - options considered
  - evidence used
  - critique input
  - final choice and justification
  - resulting confidence
- Decision artifacts SHALL be immutable once recorded.

> **Intent signal**: Explainability is structural, not narrative.

---

## INV-5: Iteration Is Orchestrator-Controlled, Not Agent-Driven

- MASTER SHALL provide standard iteration patterns for intelligent workflows.
- Iteration SHALL always follow a governed cycle (propose → gate → execute → evaluate).
- Iteration SHALL have explicit deterministic stop conditions (budgets, sufficiency, escalation).
- Iterative state SHALL be durable and resumable across restarts.

> **Intent signal**: Investigation is allowed; autonomy is not.

---

## INV-6: Platform Laws Are Explicit and Non-Negotiable

- Agents SHALL be advisory only and MUST NOT control execution, routing, or side effects.
- Only the orchestrator SHALL:
  - execute tools
  - change flow state
  - pause/resume runs
  - escalate to HITL
- Governance hooks SHALL be non-bypassable at all lifecycle points.
- Products SHALL be isolated and MUST NOT access other products' resources directly.

> **Intent signal**: Safety is enforced by structure, not convention.

---

## INV-7: Reasoning Observability Is as Important as Execution Observability

- MASTER SHALL make reasoning behavior observable, not just execution steps.
- Traces SHALL expose:
  - options considered
  - confidence evolution
  - rejection and escalation reasons
- Reasoning traces SHALL be queryable for audit, debugging, and improvement analysis.

> **Intent signal**: "Why" matters as much as "what happened".

---

## INV-8: Design-Time Intelligence Is Preferred Over Runtime Autonomy

- MASTER SHALL favor design-time use of LLMs (intent → BRD → specs → plans → code) over runtime autonomy.
- Runtime intelligence SHALL remain bounded, supervised, and deterministic.
- Product creation and evolution SHALL be intent-driven, with code as a generated artifact.

> **Intent signal**: Intelligence compounds safely before production, not unpredictably during it.

---

## INV-9: Feedback Feeds Intent, Not Direct Code Changes

- End-user feedback SHALL be captured as input to Developer Intent, not direct requirements.
- Bug fixes and enhancements SHALL still follow the governed lifecycle (intent → BRD → plan → implementation).
- Framework-level feedback SHALL be promoted separately and reviewed by Framework Developers.

> **Intent signal**: Speed does not justify bypassing governance.

---

## INV-10: MASTER Exists to Minimize Product Complexity, Not Maximize Flexibility

- If products need to re-implement reasoning patterns, orchestration, or governance, the framework has failed.
- MASTER SHALL continuously absorb common intelligence patterns into the core.
- Products SHOULD remain thin, declarative, and domain-focused.

> **Intent signal**: Complexity belongs in one place only — the framework.

---

# 1. Intelligent Automation (INT-AUTO)

> **Maps to**: [BRD-automation.md](../01_brd/BRD-automation.md)

## 1.1 Semantic Interpretation Phase (Added: 2026-01-13)

> **Intent**: Mandatory semantic interpretation before any planning or execution.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-SEM-001** | Every orchestrator run must execute a semantic interpretation phase before step execution | Prevent misunderstood tasks from proceeding to action |
| **INT-AUTO-SEM-002** | Semantic phase must interpret user intent and produce a structured envelope | Normalize and validate input before planning |
| **INT-AUTO-SEM-003** | Semantic envelope must capture: intent_type, entities, constraints, confidence, ambiguities | Structured representation enables validation and audit |
| **INT-AUTO-SEM-004** | Semantic phase must determine next action: CONTINUE, ASK_USER, ABORT, or NEEDS_APPROVAL | Explicit decision point for flow control |
| **INT-AUTO-SEM-005** | Semantic envelope must be attached to run record for traceability | Every interpretation decision is auditable |
| **INT-AUTO-SEM-006** | Core must provide domain-agnostic normalization rules (whitespace, deduplication, ordering) | Consistent preprocessing across all products |
| **INT-AUTO-SEM-007** | Normalization must be deterministic and reproducible | Same input produces same normalized output |
| **INT-AUTO-SEM-008** | Entities must be deduplicated (same type+value → single entity with highest confidence) | Prevent duplicate processing |
| **INT-AUTO-SEM-009** | Constraints must be merged deterministically with stable key ordering | Predictable constraint handling |
| **INT-AUTO-SEM-010** | Type coercion must be supported for schema-declared types (string→int, string→date) | Robust input handling |

### Contracts (New: 2026-01-13)

| Contract | Purpose | Fields |
|----------|---------|--------|
| `SemanticEnvelope` | Structured interpretation result | raw_input, normalized_input, product_id, intent_type, entities, constraints, confidence, ambiguities, proposed_next_action |
| `NextAction` enum | Flow control decision | CONTINUE, ASK_USER, ABORT, NEEDS_APPROVAL |
| `ValidationResult` | Domain validation outcome | is_valid, missing_fields, violations, revised_confidence, clarifying_question |
| `SemanticContext` | Input to adapters | raw_input, payload, product_config |
| `Entity` | Extracted entity | type, value, confidence, start_pos, end_pos |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Semantic phase is mandatory | Steps execute without interpretation |
| Normalization is domain-agnostic | Core normalization includes business rules |
| Envelope is immutable once created | Envelope modified after semantic phase |
| Confidence is bounded 0.0-1.0 | Confidence value outside range |

---

## 1.2 Product Semantic Adapter (Added: 2026-01-13)

> **Intent**: Products customize semantic interpretation via plugin adapters.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-ADAPT-001** | Products must be able to provide custom semantic interpretation via adapter interface | Domain-specific interpretation logic |
| **INT-AUTO-ADAPT-002** | Adapter interface must define `interpret(context) → SemanticEnvelope` method | Standardized interpretation hook |
| **INT-AUTO-ADAPT-003** | Adapter interface must define `validate(envelope, context) → ValidationResult` method | Domain-specific validation rules |
| **INT-AUTO-ADAPT-004** | Default adapter must be provided for products without custom implementation | Graceful fallback behavior |
| **INT-AUTO-ADAPT-005** | Default adapter must return passthrough envelope with confidence=1.0 | Non-blocking default behavior |
| **INT-AUTO-ADAPT-006** | Adapters must be discovered from `products/<name>/semantic.py` | Convention-based discovery |
| **INT-AUTO-ADAPT-007** | Adapters must be resolved via ProductRouter, not direct import | Maintain product isolation |
| **INT-AUTO-ADAPT-008** | Product adapters must NOT import from `core/orchestrator/*` | Isolation: products don't depend on core internals |
| **INT-AUTO-ADAPT-009** | Core orchestrator must NOT import from `products/*` | Isolation: core doesn't depend on products |
| **INT-AUTO-ADAPT-010** | Adapter execution must have timeout with fallback to default | Prevent slow adapters from blocking |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Adapters are pure functions | Adapter calls external API |
| Adapters don't execute tools | Adapter triggers tool execution |
| Adapters don't access other products | Adapter reads another product's config |
| Isolation is bidirectional | Core imports product, or product imports core orchestrator |

---

## 1.3 Stop/Pause Mechanism (Added: 2026-01-13)

> **Intent**: Structured handling of ASK_USER and ABORT next actions.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-STOP-001** | ASK_USER must pause the run and return a structured clarification response | Enable user to provide additional context |
| **INT-AUTO-STOP-002** | Clarification response must include: question, ambiguities, original confidence, context | User has information to respond |
| **INT-AUTO-STOP-003** | Run status must be PAUSED_WAITING_FOR_USER during clarification | Clear state management |
| **INT-AUTO-STOP-004** | ABORT must fail the run with structured error response | Clean failure with explanation |
| **INT-AUTO-STOP-005** | Abort error must include: error_code=semantic_abort, reason, violations, ambiguities | Debugging information preserved |
| **INT-AUTO-STOP-006** | Run status must be FAILED after ABORT | Terminal failure state |
| **INT-AUTO-STOP-007** | ASK_USER and ABORT must prevent any step execution | No partial execution on interpretation failure |
| **INT-AUTO-STOP-008** | Trace event `semantic_stop_issued` must be emitted on stop | Observability for stop decisions |
| **INT-AUTO-STOP-009** | Paused runs must be resumable with user-provided clarification | Continue workflow after clarification |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Stop blocks all steps | Step executes after ASK_USER |
| Abort is terminal | Run continues after ABORT |
| Clarification is structured | Free-form error message only |

---

## 1.4 Agent Capabilities

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-001** | Agents must reason through multi-step tasks with observable decision points | We need to see what agents are thinking, not just what they output |
| **INT-AUTO-002** | Agents must provide evidence supporting their decisions | Trust requires traceability; every claim needs backing |
| **INT-AUTO-003** | Agents must be composable—one agent can delegate to others | Complex workflows should be built from simple, tested components |
| **INT-AUTO-004** | Agents must handle failures gracefully with retry or escalation | Production systems can't crash on first error |
| **INT-AUTO-005** | Agent behavior must be deterministic given the same inputs | Reproducibility is non-negotiable for testing and compliance |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Agents advise, never execute | Agent calls a tool directly |
| Agents are stateless | Agent stores data in instance variables |
| Agents cannot branch flows | Agent decides execution path |
| Agents cannot modify policies | Agent changes its own permissions |

---

## 1.2 Tool Ecosystem

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-010** | Tools must be discoverable with clear capability descriptions | Agents need to understand what tools can do |
| **INT-AUTO-011** | Tools must have typed inputs and outputs | Runtime errors from type mismatches are unacceptable |
| **INT-AUTO-012** | Tools must be executable in isolation for testing | Each tool must be testable independently |
| **INT-AUTO-013** | Tool results must include structured evidence | Outputs must support audit and explainability |
| **INT-AUTO-014** | Tool execution must be observable and traceable | We need to know what tools did and when |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Tools are deterministic | Tool calls an LLM |
| Tools execute via ToolExecutor only | Tool runs outside orchestrator |
| Tools declare side effects | Tool modifies external state silently |

---

## 1.3 Intelligence Layer

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-020** | System must select appropriate tools for tasks automatically | Manual tool selection doesn't scale |
| **INT-AUTO-021** | System must select appropriate agents for subtasks | Enable dynamic delegation without hardcoding |
| **INT-AUTO-022** | System must identify gaps in information and request clarification | Better to ask than assume |
| **INT-AUTO-023** | System must summarize complex results for human consumption | Raw outputs are unusable for decisions |
| **INT-AUTO-024** | System must explain risks before executing high-impact actions | Informed consent for consequential operations |
| **INT-AUTO-025** | System must interpret user intent before planning/execution | Prevent misunderstood tasks from proceeding |
| **INT-AUTO-026** | System must normalize and validate input before acting | Garbage in, garbage out must be prevented |
| **INT-AUTO-027** | System must express interpretation confidence and request clarification when uncertain | Low confidence should trigger human involvement |

---

## 1.4 Reasoning Quality

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-030** | Reasoning must progress through structured phases (interpret→propose→select) | Predictable, auditable reasoning |
| **INT-AUTO-031** | Proposals must be evaluated by critic before execution | Quality gate before action |
| **INT-AUTO-032** | Context must be enriched with relevant knowledge before reasoning | Better context = better decisions |
| **INT-AUTO-033** | Reasoning failures must trigger appropriate escalation | Fail gracefully, not silently |

---

## 1.5 Workflow Execution

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-040** | Workflows must support sequential, parallel, and conditional steps | Flexible automation patterns |
| **INT-AUTO-041** | Workflows must support iteration over collections | Batch processing is essential |
| **INT-AUTO-042** | Workflow steps must be independently restartable | Failure recovery without full reruns |
| **INT-AUTO-043** | Workflows must support nested sub-workflows | Complex composition from simple flows |

---

# 2. Governance & Compliance (INT-GOV)

> **Maps to**: [BRD-governance.md](../01_brd/BRD-governance.md)

## 2.1 Human Oversight

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-001** | High-risk actions must require human approval before execution | Regulatory compliance, risk mitigation |
| **INT-GOV-002** | Approval requests must include context: what, why, impact | Humans need information to decide |
| **INT-GOV-003** | Approvers must be able to approve, reject, or request changes | Flexibility in oversight |
| **INT-GOV-004** | Approval decisions must be recorded with approver identity and timestamp | Complete audit trail |
| **INT-GOV-005** | Workflows must pause gracefully while awaiting approval | No orphaned or stuck processes |
| **INT-GOV-006** | Workflows must resume correctly after approval/rejection | Seamless continuation |

---

## 2.2 Security & Privacy

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-010** | PII must never appear in logs, traces, or persisted data | Privacy regulations (GDPR, SOC 2) |
| **INT-GOV-011** | Credentials and secrets must be redacted from all outputs | Security best practice |
| **INT-GOV-012** | Redaction must be automatic—not dependent on developer action | Defense in depth; humans forget |
| **INT-GOV-013** | Custom redaction patterns must be configurable per product | Domain-specific sensitivity |
| **INT-GOV-014** | Redaction failures must halt execution rather than leak data | Fail-safe, not fail-open |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| PII never in logs | SSN appears in trace event |
| Credentials never exposed | API key in error message |
| Redaction is automatic | Developer must call redact() |

---

## 2.3 Policy Enforcement

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-020** | Certain tools must be prohibitable by policy | Risk control |
| **INT-GOV-021** | Certain models must be prohibitable by policy | Compliance with usage agreements |
| **INT-GOV-022** | Policy violations must block execution—not just warn | Enforceable governance |
| **INT-GOV-023** | Policies must be configurable per product | Product-specific governance |
| **INT-GOV-024** | Policy decisions must be logged for audit | Traceability |
| **INT-GOV-025** | Low-confidence interpretations must pause for user clarification | Prevents misguided execution |
| **INT-GOV-026** | Confidence thresholds must be configurable per product | Domain-appropriate sensitivity |
| **INT-GOV-027** | Semantic validation failures must block execution | Fail-safe behavior |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Hooks cannot be bypassed | Developer disables governance |
| Policy violations block | Warning logged but execution continues |
| Budgets are hard limits | Limit exceeded but run continues |

---

## 2.4 Semantic Confidence Governance (Added: 2026-01-13)

> **Intent**: Confidence thresholds and governance hooks for semantic interpretation.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-CONF-001** | Default confidence threshold must be configurable in `configs/app.yaml` | Platform-wide baseline |
| **INT-GOV-CONF-002** | Per-product confidence threshold override must be supported in `configs/products.yaml` | Domain-appropriate sensitivity |
| **INT-GOV-CONF-003** | Default threshold must be 0.7 (adjustable) | Balance between usability and safety |
| **INT-GOV-CONF-004** | Confidence below threshold must trigger ASK_USER (not silent failure) | User gets opportunity to clarify |
| **INT-GOV-CONF-005** | Governance hook `check_semantic_confidence` must enforce thresholds | Enforceable via governance layer |
| **INT-GOV-CONF-006** | Effective confidence is minimum of (envelope.confidence, validation.revised_confidence) | Conservative confidence calculation |
| **INT-GOV-CONF-007** | Threshold enforcement must be logged with confidence values | Audit trail for threshold decisions |

### Configuration (New: 2026-01-13)

**Platform Default** (`configs/app.yaml`):
```yaml
semantic:
  default_confidence_threshold: 0.7
  require_semantic_phase: true
```

**Per-Product Override** (`configs/products.yaml`):
```yaml
by_product:
  ade:
    semantic_confidence_threshold: 0.8  # Stricter for production
  hello_world:
    semantic_confidence_threshold: 0.5  # More lenient for demo
```

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Threshold is enforced | Low confidence proceeds without check |
| Override requires explicit config | Implicit threshold changes |
| Confidence check is governance hook | Check embedded in business logic |

---

## 2.5 Cost Controls

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-030** | Each workflow run must have enforceable budget limits | Cost predictability |
| **INT-GOV-031** | Budget limits must cover: LLM tokens, tool calls, time | Comprehensive control |
| **INT-GOV-032** | Budget exhaustion must pause/terminate the workflow | Prevent runaway costs |
| **INT-GOV-033** | Current budget consumption must be trackable in real-time | Operational awareness |
| **INT-GOV-034** | Budget alerts must trigger before limits are reached | Proactive management |

---

## 2.6 Audit & Traceability

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-040** | Every action must be traceable to: who, what, when, why | Compliance requirement |
| **INT-GOV-041** | State transitions must be immutable once recorded | Non-repudiation |
| **INT-GOV-042** | Audit logs must be queryable by run, user, timeframe | Investigation support |
| **INT-GOV-043** | Audit data must be exportable in standard formats | External audit tools |
| **INT-GOV-044** | Audit retention period must be configurable | Compliance with data policies |

---

# 3. Developer & User Experience (INT-EXP)

> **Maps to**: [BRD-experience.md](../01_brd/BRD-experience.md)

## 3.1 API Experience

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-001** | Platform must be accessible via HTTP REST API | Integration standard |
| **INT-EXP-002** | API responses must follow consistent envelope format | Predictable parsing |
| **INT-EXP-003** | API errors must include machine-readable codes | Automated error handling |
| **INT-EXP-004** | API errors must include human-readable messages | Developer debugging |
| **INT-EXP-005** | API must support listing products and flows | Discovery |
| **INT-EXP-006** | API must support starting, monitoring, and resuming runs | Core functionality |
| **INT-EXP-007** | API must enforce payload size limits | Resource protection |

---

## 3.2 CLI Experience

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-010** | Platform must be accessible via command-line interface | Operator standard |
| **INT-EXP-011** | CLI output must be valid JSON for scripting | Automation support |
| **INT-EXP-012** | CLI must provide commands for all core operations | Feature parity |
| **INT-EXP-013** | CLI errors must exit with appropriate status codes | Script integration |
| **INT-EXP-014** | CLI must provide helpful guidance on errors | User experience |

---

## 3.3 UI Experience

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-020** | Platform must be accessible via web interface | Non-technical users |
| **INT-EXP-021** | UI must display available products and flows | Discovery |
| **INT-EXP-022** | UI must allow running flows with input | Core functionality |
| **INT-EXP-023** | UI must display run status and history | Monitoring |
| **INT-EXP-024** | UI must support approval workflows | Human-in-the-loop |
| **INT-EXP-025** | UI must support user input collection | Interactive workflows |
| **INT-EXP-026** | UI must display execution timeline with events | Debugging support |

---

## 3.4 Product System

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-030** | New products must be creatable from standard structure | Fast onboarding |
| **INT-EXP-031** | Products must declare capabilities via manifest | Self-documenting |
| **INT-EXP-032** | Products must be auto-discovered without restart | Developer velocity |
| **INT-EXP-033** | Products must be independently enableable/disableable | Operational control |
| **INT-EXP-034** | Product load errors must not crash the platform | Fault isolation |

---

## 3.5 Product Isolation

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-040** | Products must not access other products' agents or tools | Security boundary |
| **INT-EXP-041** | Products must not access other products' data | Data isolation |
| **INT-EXP-042** | Product failures must not affect other products | Fault isolation |
| **INT-EXP-043** | Products must have isolated observability directories | Clean separation |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Products cannot modify core | Product patches orchestrator |
| Products are isolated | Product A reads Product B's data |
| Products are fault-isolated | Product A crash takes down Product B |

---

# 4. Operational Excellence (INT-OPS)

> **Maps to**: [BRD-operations.md](../01_brd/BRD-operations.md)

## 4.1 State Persistence

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-001** | Run state must survive process restarts | Reliability |
| **INT-OPS-002** | In-flight workflows must be resumable after restart | No lost work |
| **INT-OPS-003** | State must be persisted durably (not just in-memory) | Data safety |
| **INT-OPS-004** | State storage must support concurrent access | Scalability |
| **INT-OPS-005** | Historical runs must be queryable | Audit, debugging |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| State survives restarts | Run lost after process restart |
| State transitions are traced | State changes without event |
| Everything is traced | Action taken without trace record |

---

## 4.2 Observability

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-010** | Every execution step must be traced | Debugging |
| **INT-OPS-011** | Traces must include: timestamp, event type, data | Complete picture |
| **INT-OPS-012** | Traces must be queryable by run, step, timeframe | Investigation |
| **INT-OPS-013** | Large outputs must be stored to files, not inline | Storage efficiency |
| **INT-OPS-014** | Observability data must be organized by product/run | Multi-tenancy |
| **INT-OPS-015** | Dashboards must visualize run status and trends | Operations monitoring |

---

## 4.3 Semantic Trace Events (Added: 2026-01-13)

> **Intent**: Structured trace events for semantic interpretation phase.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-SEM-001** | `semantic_interpretation_started` event must be emitted when phase begins | Track phase lifecycle |
| **INT-OPS-SEM-002** | Started event must include: run_id, product_id, raw_input_length | Context for debugging |
| **INT-OPS-SEM-003** | `semantic_interpretation_completed` event must be emitted when phase succeeds | Track successful interpretation |
| **INT-OPS-SEM-004** | Completed event must include: envelope_hash, confidence, ambiguity_count, entity_count, next_action | Interpretation metrics |
| **INT-OPS-SEM-005** | `semantic_validation_completed` event must be emitted after validation | Track validation outcome |
| **INT-OPS-SEM-006** | Validation event must include: is_valid, missing_fields, violation_count, revised_confidence | Validation metrics |
| **INT-OPS-SEM-007** | `semantic_stop_issued` event must be emitted on ASK_USER or ABORT | Track stop decisions |
| **INT-OPS-SEM-008** | Stop event must include: next_action, question (if ASK_USER), reason (if ABORT), violations | Stop context |
| **INT-OPS-SEM-009** | `semantic_interpretation_failed` event must be emitted on exception | Error visibility |
| **INT-OPS-SEM-010** | Failed event must include: error message | Debugging information |

### Event Catalog (New: 2026-01-13)

| Event | When | Payload |
|-------|------|---------|
| `semantic_interpretation_started` | Phase begins | `run_id`, `product_id`, `raw_input_length` |
| `semantic_interpretation_completed` | Phase succeeds | `envelope_hash`, `confidence`, `ambiguity_count`, `entity_count`, `next_action` |
| `semantic_validation_completed` | After validate() | `is_valid`, `missing_fields`, `violation_count`, `revised_confidence` |
| `semantic_stop_issued` | ASK_USER or ABORT | `next_action`, `question`, `reason`, `violations` |
| `semantic_interpretation_failed` | Exception thrown | `error` |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Events are structured | Free-form log message instead of event |
| Events include run_id | Event cannot be correlated to run |
| Events have timestamps | Event missing `ts` field |

---

## 4.4 Performance

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-020** | API responses must complete within 500ms (p95) | User experience |
| **INT-OPS-021** | Run startup must complete within 2 seconds | Responsiveness |
| **INT-OPS-022** | Memory backend operations must complete within 100ms | System responsiveness |
| **INT-OPS-023** | Performance metrics must be measurable | SLA monitoring |

---

## 4.5 Quality Assurance

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-030** | Core modules must have ≥80% test coverage | Quality baseline |
| **INT-OPS-031** | Critical paths (run lifecycle) must have 100% coverage | Risk mitigation |
| **INT-OPS-032** | All tests must pass before deployment | Quality gate |
| **INT-OPS-033** | Tests must complete within 10 minutes | Developer velocity |
| **INT-OPS-034** | Contracts (Pydantic models) must have validation tests | Interface stability |

---

## 4.6 Debugging Support

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-040** | Failed runs must include error details and stack traces | Root cause analysis |
| **INT-OPS-041** | Event timeline must be viewable for any run | Execution understanding |
| **INT-OPS-042** | Input/output data must be inspectable | Data debugging |
| **INT-OPS-043** | LLM calls and responses must be logged | AI debugging |
| **INT-OPS-044** | Tool calls and results must be logged | Integration debugging |

---

## 4.7 Architecture Tests (Added: 2026-01-13)

> **Intent**: Mandatory tests that lock critical semantic behavior.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-ARCH-001** | Architecture test must verify semantic phase is mandatory | Prevent regression of mandatory phase |
| **INT-OPS-ARCH-002** | Architecture test must verify ASK_USER blocks all step execution | Lock stop behavior |
| **INT-OPS-ARCH-003** | Architecture test must verify ABORT blocks all step execution | Lock abort behavior |
| **INT-OPS-ARCH-004** | Architecture test must verify product adapters don't import core orchestrator | Enforce isolation |
| **INT-OPS-ARCH-005** | Architecture test must verify core orchestrator doesn't import products | Enforce isolation |
| **INT-OPS-ARCH-006** | Architecture tests must live in `tests/architecture/` directory | Clear test organization |
| **INT-OPS-ARCH-007** | Architecture tests must be run as part of CI pipeline | Continuous enforcement |

### Required Architecture Tests (New: 2026-01-13)

| Test | Invariant Verified |
|------|-------------------|
| `test_semantic_phase_is_mandatory` | ORC-SEM-001: Semantic phase runs before any step execution |
| `test_stop_blocks_execution` | ORC-SEM-STOP-001: ASK_USER/ABORT prevent step execution |
| `test_product_adapter_isolated` | PROD-SEM-INT-005/006: No cross-layer imports |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Architecture tests must pass | Test failure ignored |
| Tests verify structure, not behavior | Test only checks runtime values |
| Tests are automated | Manual verification required |

---

# 5. Developer Intent Lifecycle (INT-LIFECYCLE)

## 5.1 Intent Ownership & Evolution

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-LIFECYCLE-001** | Framework Developer owns Framework Developer Intent | Clear accountability |
| **INT-LIFECYCLE-002** | Product Developer owns Product Developer Intent | Domain expertise at product level |
| **INT-LIFECYCLE-003** | End Users never modify intent directly | Preserve integrity of intent documents |
| **INT-LIFECYCLE-004** | Intent updates must be versioned and reviewed | Change control |
| **INT-LIFECYCLE-005** | Intent conflicts must have explicit resolution rules | Prevent deadlock |

---

## 5.2 User Feedback Handling

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-LIFECYCLE-010** | User feedback is not Developer Intent | Maintain separation of concerns |
| **INT-LIFECYCLE-011** | Feedback must be captured in structured format | Enable analysis and prioritization |
| **INT-LIFECYCLE-012** | Feedback must be reviewed before promotion to intent | Quality gate |
| **INT-LIFECYCLE-013** | Bugs and enhancements have different promotion rules | Different urgency levels |
| **INT-LIFECYCLE-014** | Framework gaps must escalate to Framework Developer | Clear escalation path |

---

## 5.3 Intent-to-BRD Mapping

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-LIFECYCLE-020** | Every intent point must map to at least one BRD requirement | Traceability |
| **INT-LIFECYCLE-021** | BRD requirements must reference source intent | Bidirectional traceability |
| **INT-LIFECYCLE-022** | Unmapped intent points are gaps | Coverage validation |
| **INT-LIFECYCLE-023** | BRD requirements without intent are suspect | Prevent scope creep |

---

# 6. Product Factory Model (INT-FACTORY)

## 6.1 MASTER as Product Factory

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-FACTORY-001** | Product creation is primarily an intent-driven activity | Capture intent, not code |
| **INT-FACTORY-002** | Code is a generated artifact, not the source of truth | Intent is the source |
| **INT-FACTORY-003** | Products must be shippable in < 1 day | Rapid value delivery |
| **INT-FACTORY-004** | Products must focus on domain logic only | No infrastructure burden |
| **INT-FACTORY-005** | Products must be evolvable via intent updates | Safe evolution |

---

## 6.2 Framework vs Product Asymmetry

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-FACTORY-010** | Framework owns orchestration, memory, governance, model routing | Single source of truth |
| **INT-FACTORY-011** | Products are forbidden from re-implementing framework services | Prevent duplication |
| **INT-FACTORY-012** | Framework evolution is rarer, heavier, more reviewed | Stability requirement |
| **INT-FACTORY-013** | Products define what, framework defines how | Clear separation |
| **INT-FACTORY-014** | Framework provides 90% of functionality, products add 10% | Thick core, thin products |

---

## 6.3 Success and Failure Smells

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-FACTORY-020** | Success/failure smells must be defined qualitatively | Guide future decisions |
| **INT-FACTORY-021** | Smells must be checked during architecture reviews | Early detection |
| **INT-FACTORY-022** | Smell detection must trigger design review | Corrective action |

---

## 6.4 Design-Time vs Runtime Intelligence

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-FACTORY-030** | Design-time intelligence is preferred over runtime autonomy | Safety through structure |
| **INT-FACTORY-031** | AI can derive BRDs from intent | Accelerate documentation |
| **INT-FACTORY-032** | AI can derive specs from BRDs | Consistent translation |
| **INT-FACTORY-033** | AI can generate code from specs | Reduce manual coding |
| **INT-FACTORY-034** | AI can generate system design from code | Keep docs current |
| **INT-FACTORY-035** | Runtime AI is advisory only, never autonomous | Human control preserved |

---

# 7. Framework Laws

> **What can never happen in MASTER.**

| Law | Violation Example |
|-----|-------------------|
| Agents never execute tools | Agent calls tool directly |
| Tools never call models | Tool makes LLM API call |
| Governance hooks are mandatory | Hook is bypassed or disabled |
| State transitions are traced | State changes without event |
| Budgets are enforced | Limits exceeded without halt |
| Products are isolated | Product accesses another's data |
| PII is never logged | Sensitive data in traces |
| Flows are explicit | Implicit execution path |
| Intent precedes BRD | BRD created without intent source |
| Feedback is not intent | User request treated as requirement |
| Semantic phase is mandatory | Steps execute without interpretation |
| Stop blocks all steps | Step executes after ASK_USER |
| Product adapters are isolated | Adapter imports core orchestrator |

---

# 8. Acceptance Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Time-to-first-product | < 1 day | Scaffolding to running |
| Compliance audit pass rate | 100% | External audit |
| PII leakage incidents | 0 | Security scans |
| Agent task success rate | > 85% | Production metrics |
| Test coverage (core) | > 80% | Coverage tools |
| Platform availability | > 99.5% | Uptime monitoring |
| Intent→BRD traceability | 100% | Document review |
| Failure smell occurrences | 0 | Architecture reviews |
| Semantic misunderstanding rate | < 5% | User reports after clarification |
| Clarification acceptance rate | > 80% | Users proceed after ASK_USER |
| Semantic phase latency | < 100ms | P99 execution time |
| Architecture tests passing | 100% | CI pipeline |

---

# 9. Derived Documents

| Document | Derivation |
|----------|------------|
| [Vision.md](Vision.md) | Framework philosophy and architecture |
| [BRD-automation.md](../01_brd/BRD-automation.md) | INT-AUTO-*, INT-AUTO-SEM-*, INT-AUTO-ADAPT-*, INT-AUTO-STOP-* → BRD-AUTO-* |
| [BRD-governance.md](../01_brd/BRD-governance.md) | INT-GOV-*, INT-GOV-CONF-* → BRD-GOV-* |
| [BRD-experience.md](../01_brd/BRD-experience.md) | INT-EXP-* → BRD-EXP-* |
| [BRD-operations.md](../01_brd/BRD-operations.md) | INT-OPS-*, INT-OPS-SEM-*, INT-OPS-ARCH-* → BRD-OPS-* |
