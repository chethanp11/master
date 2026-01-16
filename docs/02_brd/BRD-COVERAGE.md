# BRD Coverage Analysis

> **Document ID**: BRD-COVERAGE  
> **Last Updated**: 2026-01-17  
> **Status**: V1 Release

> **Purpose**: Track traceability between Developer Intent documents and Business Requirement Documents (BRDs).

---

## Coverage Summary

| Intent Document | BRD Document | Intent IDs Covered | BRD IDs Derived | Coverage |
|-----------------|--------------|-------------------|-----------------|----------|
| [intent-automation.md](../01_vision_and_intent/intent-automation.md) | [BRD-automation.md](BRD-automation.md) | 43 | 56 | ✅ Full |
| [intent-governance.md](../01_vision_and_intent/intent-governance.md) | [BRD-governance.md](BRD-governance.md) | 29 | 47 | ✅ Full |
| [intent-experience.md](../01_vision_and_intent/intent-experience.md) | [BRD-experience.md](BRD-experience.md) | 26 | 44 | ✅ Full |
| [intent-operations.md](../01_vision_and_intent/intent-operations.md) | [BRD-operations.md](BRD-operations.md) | 32 | 53 | ✅ Full |

---

## 1. Automation (INT-AUTO → BRD-AUTO)

### 1.1 Semantic Interpretation (INT-AUTO-SEM)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-AUTO-SEM-001 | Semantic interpretation must run before any step execution | BRD-AUTO-SEM-001 | ✅ |
| INT-AUTO-SEM-002 | Interpretation must produce structured `SemanticEnvelope` output | BRD-AUTO-SEM-002 | ✅ |
| INT-AUTO-SEM-003 | SemanticEnvelope must include normalized intent, confidence, entities, constraints | BRD-AUTO-SEM-003 | ✅ |
| INT-AUTO-SEM-004 | Confidence score must range 0.0–1.0 | BRD-AUTO-SEM-004 | ✅ |
| INT-AUTO-SEM-005 | Entities must be typed: PERSON, ORGANIZATION, DATE, AMOUNT, PRODUCT, CUSTOM | BRD-AUTO-SEM-003 | ✅ |
| INT-AUTO-SEM-006 | Ambiguities must be captured as structured list | BRD-AUTO-SEM-003 | ✅ |
| INT-AUTO-SEM-007 | If confidence < threshold, next_action must be ASK_USER | BRD-AUTO-SEM-004, BRD-GOV-CONF-004 | ✅ |
| INT-AUTO-SEM-008 | If unresolvable conflict detected, next_action must be ABORT | BRD-AUTO-SEM-004 | ✅ |
| INT-AUTO-SEM-009 | Interpretation phase must be product-agnostic at framework level | BRD-AUTO-SEM-006 | ✅ |
| INT-AUTO-SEM-010 | Products may override interpretation via semantic adapter interface | BRD-AUTO-ADAPT-001 | ✅ |

### 1.2 Product Semantic Adapter (INT-AUTO-ADAPT)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-AUTO-ADAPT-001 | Products must provide custom semantic interpretation via adapter interface | BRD-AUTO-ADAPT-001 | ✅ |
| INT-AUTO-ADAPT-002 | Adapter interface must define `interpret(context) → SemanticEnvelope` | BRD-AUTO-ADAPT-002 | ✅ |
| INT-AUTO-ADAPT-003 | Adapter interface must define `validate(envelope, context) → ValidationResult` | BRD-AUTO-ADAPT-003 | ✅ |
| INT-AUTO-ADAPT-004 | Default adapter must be provided for products without custom implementation | BRD-AUTO-ADAPT-004 | ✅ |
| INT-AUTO-ADAPT-005 | Default adapter must return passthrough envelope with confidence=1.0 | BRD-AUTO-ADAPT-005 | ✅ |
| INT-AUTO-ADAPT-006 | Adapters must be discovered from `products/<name>/semantic.py` | BRD-AUTO-ADAPT-006 | ✅ |
| INT-AUTO-ADAPT-007 | Adapters must be resolved via ProductRouter, not direct import | BRD-AUTO-ADAPT-007 | ✅ |
| INT-AUTO-ADAPT-008 | Product adapters must NOT import from `core/orchestrator/*` | BRD-AUTO-ADAPT-008 | ✅ |
| INT-AUTO-ADAPT-009 | Core orchestrator must NOT import from `products/*` | BRD-AUTO-ADAPT-009 | ✅ |
| INT-AUTO-ADAPT-010 | Adapter execution must have timeout with fallback to default | BRD-AUTO-ADAPT-010 | ✅ |

### 1.3 Stop/Pause Mechanism (INT-AUTO-STOP)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-AUTO-STOP-001 | ASK_USER must pause the run and return structured clarification response | BRD-AUTO-STOP-001 | ✅ |
| INT-AUTO-STOP-002 | Clarification response must include: question, ambiguities, confidence, context | BRD-AUTO-STOP-002 | ✅ |
| INT-AUTO-STOP-003 | Run status must be PAUSED_WAITING_FOR_USER during clarification | BRD-AUTO-STOP-003 | ✅ |
| INT-AUTO-STOP-004 | ABORT must fail the run with structured error response | BRD-AUTO-STOP-004 | ✅ |
| INT-AUTO-STOP-005 | Abort error must include: error_code, reason, violations, ambiguities | BRD-AUTO-STOP-005 | ✅ |
| INT-AUTO-STOP-006 | Run status must be FAILED after ABORT | BRD-AUTO-STOP-006 | ✅ |
| INT-AUTO-STOP-007 | ASK_USER and ABORT must prevent any step execution | BRD-AUTO-STOP-007 | ✅ |
| INT-AUTO-STOP-008 | Trace event `semantic_stop_issued` must be emitted on stop | BRD-AUTO-STOP-008, BRD-OPS-SEM-007 | ✅ |
| INT-AUTO-STOP-009 | Paused runs must be resumable with user-provided clarification | BRD-AUTO-STOP-009 | ✅ |

### 1.4 Agent Capabilities (INT-AUTO-001...005)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-AUTO-001 | Agents must reason through multi-step tasks with observable decision points | BRD-AUTO-001 | ✅ |
| INT-AUTO-002 | Agents must provide evidence supporting their decisions | BRD-AUTO-002 | ✅ |
| INT-AUTO-003 | Agents must be composable—one agent can delegate to others | BRD-AUTO-003 | ✅ |
| INT-AUTO-004 | Agents must handle failures gracefully with retry or escalation | BRD-AUTO-004 | ✅ |
| INT-AUTO-005 | Agent behavior must be deterministic given the same inputs | BRD-AUTO-005 | ✅ |

### 1.5 Tool Ecosystem (INT-AUTO-010...014)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-AUTO-010 | Tools must be discoverable with clear capability descriptions | BRD-AUTO-010 | ✅ |
| INT-AUTO-011 | Tools must have typed inputs and outputs | BRD-AUTO-011 | ✅ |
| INT-AUTO-012 | Tools must be executable in isolation for testing | BRD-AUTO-012 | ✅ |
| INT-AUTO-013 | Tool results must include structured evidence | BRD-AUTO-013 | ✅ |
| INT-AUTO-014 | Tool execution must be observable and traceable | BRD-AUTO-014 | ✅ |

### 1.6 Intelligence Layer (INT-AUTO-020...027)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-AUTO-020 | System must select appropriate tools for tasks automatically | BRD-AUTO-020 | ✅ |
| INT-AUTO-021 | System must select appropriate agents for subtasks | BRD-AUTO-021 | ✅ |
| INT-AUTO-022 | System must identify gaps in information and request clarification | BRD-AUTO-022 | ✅ |
| INT-AUTO-023 | System must summarize complex results for human consumption | BRD-AUTO-023 | ✅ |
| INT-AUTO-024 | System must explain risks before executing high-impact actions | BRD-AUTO-024 | ✅ |
| INT-AUTO-025 | System must interpret user intent before planning/execution | BRD-AUTO-025 | ✅ |
| INT-AUTO-026 | System must normalize and validate input before acting | BRD-AUTO-026 | ✅ |
| INT-AUTO-027 | System must express interpretation confidence and request clarification | BRD-AUTO-027 | ✅ |

### 1.7 Reasoning Quality (INT-AUTO-030...033)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-AUTO-030 | Reasoning must progress through structured phases | BRD-AUTO-030 | ✅ |
| INT-AUTO-031 | Proposals must be evaluated by critic before execution | BRD-AUTO-031 | ✅ |
| INT-AUTO-032 | Context must be enriched with relevant knowledge before reasoning | BRD-AUTO-032 | ✅ |
| INT-AUTO-033 | Reasoning failures must trigger appropriate escalation | BRD-AUTO-033 | ✅ |

### 1.8 Workflow Execution (INT-AUTO-040...043)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-AUTO-040 | Workflows must support sequential, parallel, and conditional steps | BRD-AUTO-040 | ✅ |
| INT-AUTO-041 | Workflows must support iteration over collections | BRD-AUTO-041 | ✅ |
| INT-AUTO-042 | Workflow steps must be independently restartable | BRD-AUTO-042 | ✅ |
| INT-AUTO-043 | Workflows must support nested sub-workflows | BRD-AUTO-043 | ✅ |

---

## 2. Governance (INT-GOV → BRD-GOV)

### 2.1 Human Oversight (INT-GOV-001...006)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-GOV-001 | High-risk actions must require human approval before execution | BRD-GOV-001 | ✅ |
| INT-GOV-002 | Approval requests must include context: what, why, impact | BRD-GOV-002 | ✅ |
| INT-GOV-003 | Approvers must be able to approve, reject, or request changes | BRD-GOV-003 | ✅ |
| INT-GOV-004 | Approval decisions must be recorded with approver identity and timestamp | BRD-GOV-004 | ✅ |
| INT-GOV-005 | Workflows must pause gracefully while awaiting approval | BRD-GOV-005 | ✅ |
| INT-GOV-006 | Workflows must resume correctly after approval/rejection | BRD-GOV-006 | ✅ |

### 2.2 Security & Privacy (INT-GOV-010...014)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-GOV-010 | PII must never appear in logs, traces, or persisted data | BRD-GOV-010 | ✅ |
| INT-GOV-011 | Credentials and secrets must be redacted from all outputs | BRD-GOV-011 | ✅ |
| INT-GOV-012 | Redaction must be automatic—not dependent on developer action | BRD-GOV-012 | ✅ |
| INT-GOV-013 | Custom redaction patterns must be configurable per product | BRD-GOV-013 | ✅ |
| INT-GOV-014 | Redaction failures must halt execution rather than leak data | BRD-GOV-014 | ✅ |

### 2.3 Policy Enforcement (INT-GOV-020...027)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-GOV-020 | Certain tools must be prohibitable by policy | BRD-GOV-020 | ✅ |
| INT-GOV-021 | Certain models must be prohibitable by policy | BRD-GOV-021 | ✅ |
| INT-GOV-022 | Policy violations must block execution—not just warn | BRD-GOV-022 | ✅ |
| INT-GOV-023 | Policies must be configurable per product | BRD-GOV-023 | ✅ |
| INT-GOV-024 | Policy decisions must be logged for audit | BRD-GOV-024 | ✅ |
| INT-GOV-025 | Low-confidence interpretations must pause for user clarification | BRD-GOV-025 | ✅ |
| INT-GOV-026 | Confidence thresholds must be configurable per product | BRD-GOV-026 | ✅ |
| INT-GOV-027 | Semantic validation failures must block execution | BRD-GOV-027 | ✅ |

### 2.4 Semantic Confidence Governance (INT-GOV-CONF)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-GOV-CONF-001 | Default confidence threshold must be configurable in `configs/app.yaml` | BRD-GOV-CONF-001 | ✅ |
| INT-GOV-CONF-002 | Per-product confidence threshold override must be supported | BRD-GOV-CONF-002 | ✅ |
| INT-GOV-CONF-003 | Default threshold must be 0.7 (adjustable) | BRD-GOV-CONF-003 | ✅ |
| INT-GOV-CONF-004 | Confidence below threshold must trigger ASK_USER | BRD-GOV-CONF-004 | ✅ |
| INT-GOV-CONF-005 | Governance hook `check_semantic_confidence` must enforce thresholds | BRD-GOV-CONF-005 | ✅ |
| INT-GOV-CONF-006 | Effective confidence is minimum of envelope and validation confidence | BRD-GOV-CONF-006 | ✅ |
| INT-GOV-CONF-007 | Threshold enforcement must be logged with confidence values | BRD-GOV-CONF-007 | ✅ |

### 2.5 Cost Controls (INT-GOV-030...034)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-GOV-030 | Each workflow run must have enforceable budget limits | BRD-GOV-030 | ✅ |
| INT-GOV-031 | Budget limits must cover: LLM tokens, tool calls, time | BRD-GOV-031 | ✅ |
| INT-GOV-032 | Budget exhaustion must pause/terminate the workflow | BRD-GOV-032 | ✅ |
| INT-GOV-033 | Current budget consumption must be trackable in real-time | BRD-GOV-033 | ✅ |
| INT-GOV-034 | Budget alerts must trigger before limits are reached | BRD-GOV-034 | ✅ |

### 2.6 Audit & Traceability (INT-GOV-040...044)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-GOV-040 | Every action must be traceable to: who, what, when, why | BRD-GOV-040 | ✅ |
| INT-GOV-041 | State transitions must be immutable once recorded | BRD-GOV-041 | ✅ |
| INT-GOV-042 | Audit logs must be queryable by run, user, timeframe | BRD-GOV-042 | ✅ |
| INT-GOV-043 | Audit data must be exportable in standard formats | BRD-GOV-043 | ✅ |
| INT-GOV-044 | Audit retention period must be configurable | BRD-GOV-044 | ✅ |

---

## 3. Experience (INT-EXP → BRD-EXP)

### 3.1 API Experience (INT-EXP-001...007)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-EXP-001 | Platform must be accessible via HTTP REST API | BRD-EXP-001 | ✅ |
| INT-EXP-002 | API responses must follow consistent envelope format | BRD-EXP-002 | ✅ |
| INT-EXP-003 | API errors must include machine-readable codes | BRD-EXP-003 | ✅ |
| INT-EXP-004 | API errors must include human-readable messages | BRD-EXP-004 | ✅ |
| INT-EXP-005 | API must support listing products and flows | BRD-EXP-005 | ✅ |
| INT-EXP-006 | API must support starting, monitoring, and resuming runs | BRD-EXP-006 | ✅ |
| INT-EXP-007 | API must enforce payload size limits | BRD-EXP-007 | ✅ |

### 3.2 CLI Experience (INT-EXP-010...014)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-EXP-010 | Platform must be accessible via command-line interface | BRD-EXP-010 | ✅ |
| INT-EXP-011 | CLI output must be valid JSON for scripting | BRD-EXP-011 | ✅ |
| INT-EXP-012 | CLI must provide commands for all core operations | BRD-EXP-012 | ✅ |
| INT-EXP-013 | CLI errors must exit with appropriate status codes | BRD-EXP-013 | ✅ |
| INT-EXP-014 | CLI must provide helpful guidance on errors | BRD-EXP-014 | ✅ |

### 3.3 UI Experience (INT-EXP-020...026)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-EXP-020 | Platform must be accessible via web interface | BRD-EXP-020 | ✅ |
| INT-EXP-021 | UI must display available products and flows | BRD-EXP-021 | ✅ |
| INT-EXP-022 | UI must allow running flows with input | BRD-EXP-022 | ✅ |
| INT-EXP-023 | UI must display run status and history | BRD-EXP-023 | ✅ |
| INT-EXP-024 | UI must support approval workflows | BRD-EXP-024 | ✅ |
| INT-EXP-025 | UI must support user input collection | BRD-EXP-025 | ✅ |
| INT-EXP-026 | UI must display execution timeline with events | BRD-EXP-026 | ✅ |

### 3.4 Product System (INT-EXP-030...034)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-EXP-030 | New products must be creatable from standard structure | BRD-EXP-030 | ✅ |
| INT-EXP-031 | Products must declare capabilities via manifest | BRD-EXP-031 | ✅ |
| INT-EXP-032 | Products must be auto-discovered without restart | BRD-EXP-032 | ✅ |
| INT-EXP-033 | Products must be independently enableable/disableable | BRD-EXP-033 | ✅ |
| INT-EXP-034 | Product load errors must not crash the platform | BRD-EXP-034 | ✅ |

### 3.5 Product Isolation (INT-EXP-040...043)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-EXP-040 | Products must not access other products' agents or tools | BRD-EXP-040 | ✅ |
| INT-EXP-041 | Products must not access other products' data | BRD-EXP-041 | ✅ |
| INT-EXP-042 | Product failures must not affect other products | BRD-EXP-042 | ✅ |
| INT-EXP-043 | Products must have isolated observability directories | BRD-EXP-043 | ✅ |

---

## 4. Operations (INT-OPS → BRD-OPS)

### 4.1 State Persistence (INT-OPS-001...005)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-OPS-001 | Run state must survive process restarts | BRD-OPS-001 | ✅ |
| INT-OPS-002 | In-flight workflows must be resumable after restart | BRD-OPS-002 | ✅ |
| INT-OPS-003 | State must be persisted durably (not just in-memory) | BRD-OPS-003 | ✅ |
| INT-OPS-004 | State storage must support concurrent access | BRD-OPS-004 | ✅ |
| INT-OPS-005 | Historical runs must be queryable | BRD-OPS-005 | ✅ |

### 4.2 Observability (INT-OPS-010...015)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-OPS-010 | Every execution step must be traced | BRD-OPS-010 | ✅ |
| INT-OPS-011 | Traces must include: timestamp, event type, data | BRD-OPS-011 | ✅ |
| INT-OPS-012 | Traces must be queryable by run, step, timeframe | BRD-OPS-012 | ✅ |
| INT-OPS-013 | Large outputs must be stored to files, not inline | BRD-OPS-013 | ✅ |
| INT-OPS-014 | Observability data must be organized by product/run | BRD-OPS-014 | ✅ |
| INT-OPS-015 | Dashboards must visualize run status and trends | BRD-OPS-015 | ✅ |

### 4.3 Semantic Trace Events (INT-OPS-SEM)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-OPS-SEM-001 | `semantic_interpretation_started` event must be emitted when phase begins | BRD-OPS-SEM-001 | ✅ |
| INT-OPS-SEM-002 | Started event must include: run_id, product_id, raw_input_length | BRD-OPS-SEM-002 | ✅ |
| INT-OPS-SEM-003 | `semantic_interpretation_completed` event must be emitted when phase succeeds | BRD-OPS-SEM-003 | ✅ |
| INT-OPS-SEM-004 | Completed event must include: envelope_hash, confidence, ambiguity_count, entity_count, next_action | BRD-OPS-SEM-004 | ✅ |
| INT-OPS-SEM-005 | `semantic_validation_completed` event must be emitted after validation | BRD-OPS-SEM-005 | ✅ |
| INT-OPS-SEM-006 | Validation event must include: is_valid, missing_fields, violation_count, revised_confidence | BRD-OPS-SEM-006 | ✅ |
| INT-OPS-SEM-007 | `semantic_stop_issued` event must be emitted on ASK_USER or ABORT | BRD-OPS-SEM-007 | ✅ |
| INT-OPS-SEM-008 | Stop event must include: next_action, question, reason, violations | BRD-OPS-SEM-008 | ✅ |
| INT-OPS-SEM-009 | `semantic_interpretation_failed` event must be emitted on exception | BRD-OPS-SEM-009 | ✅ |
| INT-OPS-SEM-010 | Failed event must include: error message | BRD-OPS-SEM-010 | ✅ |

### 4.4 Performance (INT-OPS-020...023)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-OPS-020 | API responses must complete within 500ms (p95) | BRD-OPS-020 | ✅ |
| INT-OPS-021 | Run startup must complete within 2 seconds | BRD-OPS-021 | ✅ |
| INT-OPS-022 | Memory backend operations must complete within 100ms | BRD-OPS-022 | ✅ |
| INT-OPS-023 | Performance metrics must be measurable | BRD-OPS-023 | ✅ |

### 4.5 Quality Assurance (INT-OPS-030...034)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-OPS-030 | Core modules must have ≥80% test coverage | BRD-OPS-030 | ✅ |
| INT-OPS-031 | Critical paths (run lifecycle) must have 100% coverage | BRD-OPS-031 | ✅ |
| INT-OPS-032 | All tests must pass before deployment | BRD-OPS-032 | ✅ |
| INT-OPS-033 | Tests must complete within 10 minutes | BRD-OPS-033 | ✅ |
| INT-OPS-034 | Contracts (Pydantic models) must have validation tests | BRD-OPS-034 | ✅ |

### 4.6 Debugging Support (INT-OPS-040...044)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-OPS-040 | Failed runs must include error details and stack traces | BRD-OPS-040 | ✅ |
| INT-OPS-041 | Event timeline must be viewable for any run | BRD-OPS-041 | ✅ |
| INT-OPS-042 | Input/output data must be inspectable | BRD-OPS-042 | ✅ |
| INT-OPS-043 | LLM calls and responses must be logged | BRD-OPS-043 | ✅ |
| INT-OPS-044 | Tool calls and results must be logged | BRD-OPS-044 | ✅ |

### 4.7 Architecture Tests (INT-OPS-ARCH)

| Intent ID | Intent | BRD ID | Covered |
|-----------|--------|--------|---------|
| INT-OPS-ARCH-001 | Architecture test must verify semantic phase is mandatory | BRD-OPS-ARCH-001 | ✅ |
| INT-OPS-ARCH-002 | Architecture test must verify ASK_USER blocks all step execution | BRD-OPS-ARCH-002 | ✅ |
| INT-OPS-ARCH-003 | Architecture test must verify ABORT blocks all step execution | BRD-OPS-ARCH-003 | ✅ |
| INT-OPS-ARCH-004 | Architecture test must verify product adapters don't import core orchestrator | BRD-OPS-ARCH-004 | ✅ |
| INT-OPS-ARCH-005 | Architecture test must verify core orchestrator doesn't import products | BRD-OPS-ARCH-005 | ✅ |
| INT-OPS-ARCH-006 | Architecture tests must live in `tests/architecture/` directory | BRD-OPS-ARCH-006 | ✅ |
| INT-OPS-ARCH-007 | Architecture tests must be run as part of CI pipeline | BRD-OPS-ARCH-007 | ✅ |

---

## 5. BRD Requirements Without Direct Intent Source

> These BRD requirements derive from Architecture Invariants (INV-*) or are operational necessities.

### BRD-automation.md

| BRD ID | Requirement | Source |
|--------|-------------|--------|
| BRD-AUTO-034 | Reasoning behavior must be observable | INV-7 |
| BRD-AUTO-035 | Traces must expose options considered, confidence evolution | INV-7 |
| BRD-AUTO-036 | Reasoning outputs must be first-class artifacts | INV-1 |
| BRD-AUTO-044 | Iteration must follow governed cycle | INV-5 |
| BRD-AUTO-045 | Iteration must have explicit stop conditions | INV-5 |
| BRD-AUTO-046 | Iterative state must be durable and resumable | INV-5 |

### BRD-governance.md

| BRD ID | Requirement | Source |
|--------|-------------|--------|
| BRD-GOV-045 | Gated decisions must be recorded as decision artifacts | INV-4 |
| BRD-GOV-046 | Decision artifacts must capture options, evidence, critique, choice | INV-4 |
| BRD-GOV-047 | Decision artifacts must be immutable once recorded | INV-4 |
| BRD-GOV-050...053 | Governance hooks lifecycle | INV-6 |
| BRD-GOV-060...063 | Semantic interpretation governance | INV-3 |

### BRD-experience.md

| BRD ID | Requirement | Source |
|--------|-------------|--------|
| BRD-EXP-035 | Products must be shippable in < 1 day | INT-FACTORY-003 |
| BRD-EXP-036 | Products must focus on domain logic only | INT-FACTORY-004 |
| BRD-EXP-037 | Products must be evolvable via intent updates | INT-FACTORY-005 |
| BRD-EXP-044 | Products cannot modify core framework | INV-6 |
| BRD-EXP-050...053 | Error experience | Operational necessity |
| BRD-EXP-060...064 | Product Factory Model | INT-FACTORY-* |

### BRD-operations.md

| BRD ID | Requirement | Source |
|--------|-------------|--------|
| BRD-OPS-016 | Reasoning behavior must be observable | INV-7 |
| BRD-OPS-017 | Traces must expose options, confidence, rejections | INV-7 |
| BRD-OPS-018 | Reasoning traces must be queryable | INV-7 |
| BRD-OPS-050...053 | Operational tooling | Operational necessity |

---

## 6. Gap Analysis

### Intents Without BRD Coverage

| Status | Count | Notes |
|--------|-------|-------|
| ✅ Covered | 130 | All intent IDs have corresponding BRD requirements |
| ⚠️ Gaps | 0 | No gaps identified |

### BRD Requirements Without Intent Source

| Status | Count | Notes |
|--------|-------|-------|
| INV-derived | 16 | Requirements derived from Architecture Invariants |
| INT-FACTORY | 6 | Requirements from Product Factory Model section |
| Operational | 8 | Operational necessities (error handling, tooling) |

---

## 7. Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-17 | — | Initial coverage analysis with 4 split intent documents |
