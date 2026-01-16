# Developer Intent: Intelligent Automation (INT-AUTO)

> **Maps to**: [BRD-automation.md](../02_brd/BRD-automation.md)  
> **Version**: 1.1  
>
> **Source**: Extracted from [intent.md](intent.md) § 1  

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
| [Architecture Invariants](intent-operations.md#architecture-invariants) | All BRDs | Non-negotiable platform laws |
| [§1 INT-AUTO](#1-intelligent-automation-int-auto) | [BRD-automation.md](../02_brd/BRD-automation.md) | Agents, tools, reasoning, semantic interpretation |
| [§2 INT-GOV](intent-governance.md) | [BRD-governance.md](../02_brd/BRD-governance.md) | Approval, security, audit, budget, confidence thresholds |
| [§3 INT-EXP](intent-experience.md) | [BRD-experience.md](../02_brd/BRD-experience.md) | API, CLI, UI, products |
| [§4 INT-OPS](intent-operations.md#4-operational-excellence-int-ops) | [BRD-operations.md](../02_brd/BRD-operations.md) | Persistence, observability, semantic traces, architecture tests |
| [§5 INT-LIFECYCLE](intent-operations.md#5-developer-intent-lifecycle-int-lifecycle) | All BRDs | Ownership, evolution, feedback |
| [§6 INT-FACTORY](intent-operations.md#6-product-factory-model-int-factory) | All BRDs | Intent-driven product creation |

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |

## 1.1 Semantic Interpretation (Added: 2026-01-13)

> **Intent**: Every user input must pass through a semantic interpretation phase before any step execution.  

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-SEM-001** | Semantic interpretation must run before any step execution in every flow | Validate understanding before acting |
| **INT-AUTO-SEM-002** | Interpretation must produce structured `SemanticEnvelope` output | Typed, parseable result |
| **INT-AUTO-SEM-003** | SemanticEnvelope must include normalized intent, confidence score, entities, constraints | Complete interpretation context |
| **INT-AUTO-SEM-004** | Confidence score must range 0.0–1.0 with semantic meaning | Quantified uncertainty |
| **INT-AUTO-SEM-005** | Entities must be typed: PERSON, ORGANIZATION, DATE, AMOUNT, PRODUCT, CUSTOM | Domain-appropriate classification |
| **INT-AUTO-SEM-006** | Ambiguities must be captured as structured list with resolution options | Enable targeted clarification |
| **INT-AUTO-SEM-007** | If confidence < threshold, next_action must be ASK_USER | Fail safe: don't guess on ambiguity |
| **INT-AUTO-SEM-008** | If unresolvable conflict detected, next_action must be ABORT with reason | Clear failure path |
| **INT-AUTO-SEM-009** | Interpretation phase must be product-agnostic at framework level | Reusable across products |
| **INT-AUTO-SEM-010** | Products may override interpretation via semantic adapter interface | Product-specific customization |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Semantic phase is mandatory | Step executes before interpretation |
| Envelope is the only handoff | Raw text passed to planner |
| Confidence gates execution | Low confidence proceeds silently |
| Ambiguities must be explicit | Ambiguity swallowed without surfacing |

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

## 1.5 Tool Ecosystem

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

## 1.6 Intelligence Layer

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

## 1.7 Reasoning Quality

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-030** | Reasoning must progress through structured phases (interpret→propose→select) | Predictable, auditable reasoning |
| **INT-AUTO-031** | Proposals must be evaluated by critic before execution | Quality gate before action |
| **INT-AUTO-032** | Context must be enriched with relevant knowledge before reasoning | Better context = better decisions |
| **INT-AUTO-033** | Reasoning failures must trigger appropriate escalation | Fail gracefully, not silently |

---

## 1.8 Workflow Execution

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUTO-040** | Workflows must support sequential, parallel, and conditional steps | Flexible automation patterns |
| **INT-AUTO-041** | Workflows must support iteration over collections | Batch processing is essential |
| **INT-AUTO-042** | Workflow steps must be independently restartable | Failure recovery without full reruns |
| **INT-AUTO-043** | Workflows must support nested sub-workflows | Complex composition from simple flows |

---

## BRD Derivation

This document derives the following in [BRD-automation.md](../02_brd/BRD-automation.md):

- INT-AUTO-* → BRD-AUTO-*
- INT-AUTO-SEM-* → BRD-AUTO-SEM-*
- INT-AUTO-ADAPT-* → BRD-AUTO-ADAPT-*
- INT-AUTO-STOP-* → BRD-AUTO-STOP-*
