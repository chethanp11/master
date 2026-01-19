# BRD Coverage Analysis

> **Document ID**: BRD-COVERAGE  
> **Version**: V1.2  
> **Last Updated**: 2026-01-19  
> **Status**: V1 Release  

> **Purpose**: Track traceability between Developer Intent documents and Business Requirement Documents (BRDs).  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |
| V1.2 | 2026-01-19 | Standardized coverage schema and refreshed intent-to-BRD mappings |

## Coverage Summary

| Intent Document | BRD Document | Intent IDs | Covered | Missing | Clarification Needed |
|-----------------|--------------|------------|---------|---------|----------------------|
| [intent-automation.md](../01_vision_and_intent/intent-automation.md) | [BRD-automation.md](BRD-automation.md) | 81 | 78 | 3 | 2 |
| [intent-governance.md](../01_vision_and_intent/intent-governance.md) | [BRD-governance.md](BRD-governance.md) | 47 | 37 | 10 | 0 |
| [intent-experience.md](../01_vision_and_intent/intent-experience.md) | [BRD-experience.md](BRD-experience.md) | 31 | 31 | 0 | 0 |
| [intent-operations.md](../01_vision_and_intent/intent-operations.md) | [BRD-operations.md](BRD-operations.md) | 79 | 68 | 11 | 0 |

---
## 1. Automation (INT-AUTO / PLAT-* → BRD)

| Intent ID | Intent | Source File | BRD ID(s) | Covered status |
|-----------|--------|-------------|-----------|----------------|
| INT-AUTO-SEM-001 | Semantic interpretation SHALL run before any step execution in every flow — Validate understanding before acting | intent-automation.md | BRD-AUTO-SEM-001 | Covered |
| INT-AUTO-SEM-002 | Interpretation SHALL produce structured `SemanticEnvelope` output — Typed, parseable result | intent-automation.md | BRD-AUTO-SEM-002 | Covered |
| INT-AUTO-SEM-003 | `SemanticEnvelope` SHALL include normalized intent, confidence score, entities, constraints — Complete interpretation context | intent-automation.md | BRD-AUTO-SEM-003 | Covered |
| INT-AUTO-SEM-004 | Confidence score SHALL range 0.0–1.0 with semantic meaning — Quantified uncertainty | intent-automation.md | BRD-AUTO-CON-011, BRD-AUTO-SEM-004 | Covered |
| INT-AUTO-SEM-005 | Entities SHALL be typed: PERSON, ORGANIZATION, DATE, AMOUNT, PRODUCT, CUSTOM — Domain-appropriate classification | intent-automation.md | BRD-AUTO-SEM-005 | Covered |
| INT-AUTO-SEM-006 | Ambiguities SHALL be captured as a structured list with resolution options — Enable targeted clarification | intent-automation.md | BRD-AUTO-CON-009, BRD-AUTO-SEM-006 | Covered |
| INT-AUTO-SEM-007 | If confidence < threshold, next_action SHALL be ASK_USER — Fail safe: don't guess on ambiguity | intent-automation.md | BRD-AUTO-SEM-007 | Covered |
| INT-AUTO-SEM-008 | If unresolvable conflict detected, next_action SHALL be ABORT with reason — Clear failure path | intent-automation.md | BRD-AUTO-SEM-008 | Covered |
| INT-AUTO-SEM-009 | Interpretation phase SHALL be product-agnostic at framework level — Reusable across products | intent-automation.md | BRD-AUTO-SEM-009 | Covered |
| INT-AUTO-SEM-010 | Products SHALL be able to override interpretation via semantic adapter interface — Product-specific customization | intent-automation.md | BRD-AUTO-SEM-010 | Covered |
| INT-AUTO-SEM-011 | Semantic phase SHALL be mandatory — Prevent bypass of interpretation | intent-automation.md | BRD-AUTO-CON-008 | Covered |
| INT-AUTO-SEM-012 | Envelope SHALL be the only handoff to planning — Prevent raw text planning | intent-automation.md | — | Missing |
| INT-AUTO-SEM-013 | Confidence gates SHALL control execution — Prevent low-confidence execution | intent-automation.md | — | Missing |
| INT-AUTO-SEM-014 | Ambiguities SHALL be explicit — Ensure ambiguity is surfaced | intent-automation.md | — | Missing |
| INT-AUTO-ADAPT-001 | Products SHALL be able to provide custom semantic interpretation via adapter interface — Domain-specific interpretation logic | intent-automation.md | BRD-AUTO-ADAPT-001 | Covered |
| INT-AUTO-ADAPT-002 | Adapter interface SHALL define `interpret(context) → SemanticEnvelope` method — Standardized interpretation hook | intent-automation.md | BRD-AUTO-ADAPT-002 | Covered |
| INT-AUTO-ADAPT-003 | Adapter interface SHALL define `validate(envelope, context) → ValidationResult` method — Domain-specific validation rules | intent-automation.md | BRD-AUTO-ADAPT-003 | Covered |
| INT-AUTO-ADAPT-004 | Default adapter SHALL be provided for products without custom implementation — Graceful fallback behavior | intent-automation.md | BRD-AUTO-ADAPT-004 | Covered |
| INT-AUTO-ADAPT-005 | Default adapter SHALL return passthrough envelope with confidence=1.0 — Non-blocking default behavior | intent-automation.md | BRD-AUTO-ADAPT-005 | Covered |
| INT-AUTO-ADAPT-006 | Adapters SHALL be discovered from `products/<name>/semantic.py` — Convention-based discovery | intent-automation.md | BRD-AUTO-ADAPT-006 | Covered |
| INT-AUTO-ADAPT-007 | Adapters SHALL be resolved via ProductRouter, not direct import — Maintain product isolation | intent-automation.md | BRD-AUTO-ADAPT-007 | Covered |
| INT-AUTO-ADAPT-008 | Product adapters SHALL NOT import from `core/orchestrator/*` — Isolation: products don't depend on core internals | intent-automation.md | BRD-AUTO-ADAPT-008 | Covered |
| INT-AUTO-ADAPT-009 | Core orchestrator SHALL NOT import from `products/*` — Isolation: core doesn't depend on products | intent-automation.md | BRD-AUTO-ADAPT-009 | Covered |
| INT-AUTO-ADAPT-010 | Adapter execution SHALL have timeout with fallback to default — Prevent slow adapters from blocking | intent-automation.md | BRD-AUTO-ADAPT-010 | Covered |
| INT-AUTO-ADAPT-011 | Adapters SHALL be pure functions — Prevent side effects in interpretation | intent-automation.md | BRD-AUTO-CON-012 | Covered |
| INT-AUTO-ADAPT-012 | Adapters SHALL NOT execute tools — Keep interpretation advisory | intent-automation.md | BRD-AUTO-CON-013 | Covered |
| INT-AUTO-ADAPT-013 | Adapters SHALL NOT access other products — Enforce isolation | intent-automation.md | BRD-AUTO-CON-014 | Covered |
| INT-AUTO-ADAPT-014 | Isolation SHALL be bidirectional — Prevent cross-layer imports | intent-automation.md | BRD-AUTO-CON-015 | Covered |
| INT-AUTO-STOP-001 | ASK_USER SHALL pause the run and return a structured clarification response — Enable user to provide additional context | intent-automation.md | BRD-AUTO-STOP-001 | Covered |
| INT-AUTO-STOP-002 | Clarification response SHALL include: question, ambiguities, original confidence, context — User has information to respond | intent-automation.md | BRD-AUTO-STOP-002 | Covered |
| INT-AUTO-STOP-003 | Run status SHALL be PAUSED_WAITING_FOR_USER during clarification — Clear state management | intent-automation.md | BRD-AUTO-STOP-003 | Covered |
| INT-AUTO-STOP-004 | ABORT SHALL fail the run with structured error response — Clean failure with explanation | intent-automation.md | BRD-AUTO-STOP-004 | Covered |
| INT-AUTO-STOP-005 | Abort error SHALL include: error_code=semantic_abort, reason, violations, ambiguities — Debugging information preserved | intent-automation.md | BRD-AUTO-STOP-005 | Covered |
| INT-AUTO-STOP-006 | Run status SHALL be FAILED after ABORT — Terminal failure state | intent-automation.md | BRD-AUTO-STOP-006 | Covered |
| INT-AUTO-STOP-007 | ASK_USER and ABORT SHALL prevent any step execution — No partial execution on interpretation failure | intent-automation.md | BRD-AUTO-STOP-007 | Covered |
| INT-AUTO-STOP-008 | Trace event `semantic_stop_issued` SHALL be emitted on stop — Observability for stop decisions | intent-automation.md | BRD-AUTO-STOP-008 | Covered |
| INT-AUTO-STOP-009 | Paused runs SHALL be resumable with user-provided clarification — Continue workflow after clarification | intent-automation.md | BRD-AUTO-STOP-009 | Covered |
| INT-AUTO-STOP-010 | Stop SHALL block all steps — Prevent execution after ASK_USER | intent-automation.md | BRD-AUTO-CON-016 | Covered |
| INT-AUTO-STOP-011 | Abort SHALL be terminal — Prevent continuation after ABORT | intent-automation.md | BRD-AUTO-CON-017 | Covered |
| INT-AUTO-STOP-012 | Clarification SHALL be structured — Avoid free-form error messages | intent-automation.md | BRD-AUTO-CON-018 | Covered |
| INT-AUTO-001 | Agents SHALL reason through multi-step tasks with observable decision points — See what agents are thinking, not just outputs | intent-automation.md | BRD-AUTO-001 | Covered |
| INT-AUTO-002 | Agents SHALL provide evidence supporting their decisions — Trust requires traceability | intent-automation.md | BRD-AUTO-002 | Covered |
| INT-AUTO-003 | Agents SHALL be composable; one agent can delegate to others — Build complex workflows from tested components | intent-automation.md | BRD-AUTO-003 | Covered |
| INT-AUTO-004 | Agents SHALL handle failures gracefully with retry or escalation — Production systems must not fail silently | intent-automation.md | BRD-AUTO-004 | Covered |
| INT-AUTO-005 | Agent behavior SHALL be deterministic given the same inputs — Reproducibility for testing and compliance | intent-automation.md | BRD-AUTO-005 | Covered |
| INT-AUTO-006 | Agents SHALL be advisory only — Agents do not execute tools | intent-automation.md | BRD-AUTO-CON-001 | Covered |
| INT-AUTO-007 | Agents SHALL be stateless — Avoid implicit state | intent-automation.md | BRD-AUTO-CON-002 | Covered |
| INT-AUTO-008 | Agents SHALL NOT branch flows — Flow control remains orchestrator-owned | intent-automation.md | BRD-AUTO-CON-003 | Covered |
| INT-AUTO-009 | Agents SHALL NOT modify policies — Prevent privilege escalation | intent-automation.md | BRD-AUTO-CON-004 | Covered |
| INT-AUTO-010 | Tools SHALL be discoverable with clear capability descriptions — Agents need to understand tool capabilities | intent-automation.md | BRD-AUTO-010 | Covered |
| INT-AUTO-011 | Tools SHALL have typed inputs and outputs — Prevent type mismatch failures | intent-automation.md | BRD-AUTO-011 | Covered |
| INT-AUTO-012 | Tools SHALL be executable in isolation for testing — Independent testability | intent-automation.md | BRD-AUTO-012 | Covered |
| INT-AUTO-013 | Tool results SHALL include structured evidence — Support audit and explainability | intent-automation.md | BRD-AUTO-013 | Covered |
| INT-AUTO-014 | Tool execution SHALL be observable and traceable — Operational accountability | intent-automation.md | BRD-AUTO-014 | Covered |
| INT-AUTO-015 | Tools SHALL be deterministic — Prevent non-reproducible outputs | intent-automation.md | BRD-AUTO-CON-005 | Covered |
| INT-AUTO-016 | Tools SHALL execute via ToolExecutor only — Centralize execution control | intent-automation.md | BRD-AUTO-CON-006 | Covered |
| INT-AUTO-017 | Tools SHALL declare side effects — Avoid silent state changes | intent-automation.md | BRD-AUTO-CON-007 | Covered |
| INT-AUTO-020 | System SHALL select appropriate tools for tasks automatically — Manual tool selection does not scale | intent-automation.md | BRD-AUTO-020 | Covered |
| INT-AUTO-021 | System SHALL select appropriate agents for subtasks — Enable dynamic delegation without hardcoding | intent-automation.md | BRD-AUTO-021 | Covered |
| INT-AUTO-022 | System SHALL identify gaps in information and request clarification — Better to ask than assume | intent-automation.md | BRD-AUTO-022 | Covered |
| INT-AUTO-023 | System SHALL summarize complex results for human consumption — Raw outputs are unusable for decisions | intent-automation.md | BRD-AUTO-023 | Covered |
| INT-AUTO-024 | System SHALL explain risks before executing high-impact actions — Informed consent for consequential operations | intent-automation.md | BRD-AUTO-024 | Covered |
| INT-AUTO-025 | System SHALL interpret user intent before planning/execution — Prevent misunderstood tasks from proceeding | intent-automation.md | BRD-AUTO-025 | Covered |
| INT-AUTO-026 | System SHALL normalize and validate input before acting — Prevent garbage-in/garbage-out | intent-automation.md | BRD-AUTO-026 | Covered |
| INT-AUTO-027 | System SHALL express interpretation confidence and request clarification when uncertain — Trigger human involvement on low confidence | intent-automation.md | BRD-AUTO-027 | Covered |
| PLAT-AUTO-001 | System SHALL support multiple competing hypotheses with confidence scores as a first-class reasoning output — Preserve uncertainty and avoid single-authority interpretations | intent-automation.md | BRD-AUTO-028 | Clarification Needed |
| PLAT-AUTO-002 | System SHALL maintain a persistent sufficiency state tracking known facts, unknowns, assumptions, and blocking gaps — Make sufficiency explicit during execution | intent-automation.md | BRD-AUTO-029 | Clarification Needed |
| INT-AUTO-030 | Reasoning SHALL progress through structured phases (interpret → propose → select) — Predictable, auditable reasoning | intent-automation.md | BRD-AUTO-030 | Covered |
| INT-AUTO-031 | Proposals SHALL be evaluated by critic before execution — Quality gate before action | intent-automation.md | BRD-AUTO-031 | Covered |
| INT-AUTO-032 | Context SHALL be enriched with relevant knowledge before reasoning — Better context yields better decisions | intent-automation.md | BRD-AUTO-032 | Covered |
| INT-AUTO-033 | Reasoning failures SHALL trigger appropriate escalation — Fail gracefully, not silently | intent-automation.md | BRD-AUTO-033 | Covered |
| PLAT-ORCH-001 | Platform SHALL provide a central, reusable reasoning lifecycle (interpret → propose → critique → recommend) that is orchestrator-controlled, bounded, and non-autonomous — Make reasoning a governed platform primitive | intent-automation.md | BRD-AUTO-047 | Covered |
| PLAT-ORCH-002 | Orchestrator SHALL support bounded reasoning iteration with deterministic stop conditions based on sufficiency, budget, iteration limits, or human intervention — Prevent runaway reasoning loops | intent-automation.md | BRD-AUTO-048 | Covered |
| PLAT-CTRL-001 | Platform SHALL track, update, and propagate confidence as a core runtime signal across reasoning stages, steps, and decision gates — Make confidence a first-class control signal | intent-automation.md | BRD-AUTO-049 | Covered |
| PLAT-CTRL-002 | Platform SHALL enforce a mandatory advisory critique phase before finalizing any decision or output, with the ability to downgrade confidence or block progression — Ensure critique is a gate, not an afterthought | intent-automation.md | BRD-AUTO-050 | Covered |
| PLAT-EXEC-001 | Platform SHALL construct and freeze a ContextPack before planning or execution, consolidating data availability, evidence, constraints, and quality limitations — Provide a consistent decision context before execution | intent-automation.md | BRD-AUTO-051 | Covered |
| PLAT-EXEC-002 | Platform SHALL define and enforce explicit terminal outcomes (SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT) with required explanations and artifacts — Make termination semantics consistent and auditable | intent-automation.md | BRD-AUTO-052 | Covered |
| INT-AUTO-040 | Workflows SHALL support sequential, parallel, and conditional steps — Flexible automation patterns | intent-automation.md | BRD-AUTO-040 | Covered |
| INT-AUTO-041 | Workflows SHALL support iteration over collections — Batch processing is essential | intent-automation.md | BRD-AUTO-041 | Covered |
| INT-AUTO-042 | Workflow steps SHALL be independently restartable — Failure recovery without full reruns | intent-automation.md | BRD-AUTO-042 | Covered |
| INT-AUTO-043 | Workflows SHALL support nested sub-workflows — Complex composition from simple flows | intent-automation.md | BRD-AUTO-043 | Covered |

## 2. Governance (INT-GOV / PLAT-* → BRD)

| Intent ID | Intent | Source File | BRD ID(s) | Covered status |
|-----------|--------|-------------|-----------|----------------|
| INT-GOV-001 | High-risk actions SHALL require human approval before execution — Regulatory compliance, risk mitigation | intent-governance.md | BRD-GOV-001 | Covered |
| INT-GOV-002 | Approval requests SHALL include context: what, why, impact — Humans need information to decide | intent-governance.md | BRD-GOV-002 | Covered |
| INT-GOV-003 | Approvers SHALL be able to approve, reject, or request changes — Flexibility in oversight | intent-governance.md | BRD-GOV-003 | Covered |
| INT-GOV-004 | Approval decisions SHALL be recorded with approver identity and timestamp — Complete audit trail | intent-governance.md | BRD-GOV-004 | Covered |
| INT-GOV-005 | Workflows SHALL pause gracefully while awaiting approval — No orphaned or stuck processes | intent-governance.md | BRD-GOV-005 | Covered |
| INT-GOV-006 | Workflows SHALL resume correctly after approval/rejection — Seamless continuation | intent-governance.md | BRD-GOV-006 | Covered |
| INT-GOV-010 | PII SHALL never appear in logs, traces, or persisted data — Privacy regulations | intent-governance.md | BRD-GOV-010, BRD-GOV-CON-001 | Covered |
| INT-GOV-011 | Credentials and secrets SHALL be redacted from all outputs — Security best practice | intent-governance.md | BRD-GOV-011, BRD-GOV-CON-002 | Covered |
| INT-GOV-012 | Redaction SHALL be automatic, not dependent on developer action — Defense in depth | intent-governance.md | BRD-GOV-012, BRD-GOV-CON-003 | Covered |
| INT-GOV-013 | Custom redaction patterns SHALL be configurable per product — Domain-specific sensitivity | intent-governance.md | BRD-GOV-013 | Covered |
| INT-GOV-014 | Redaction failures SHALL halt execution rather than leak data — Fail-safe behavior | intent-governance.md | BRD-GOV-014 | Covered |
| INT-GOV-015 | PII SHALL never appear in logs — Prevent privacy leaks | intent-governance.md | — | Missing |
| INT-GOV-016 | Credentials SHALL never be exposed — Prevent secret leaks | intent-governance.md | — | Missing |
| INT-GOV-017 | Redaction SHALL be automatic — Remove manual redaction dependency | intent-governance.md | — | Missing |
| INT-GOV-020 | Certain tools SHALL be prohibitable by policy — Risk control | intent-governance.md | BRD-GOV-020 | Covered |
| INT-GOV-021 | Certain models SHALL be prohibitable by policy — Compliance with usage agreements | intent-governance.md | BRD-GOV-021 | Covered |
| INT-GOV-022 | Policy violations SHALL block execution, not just warn — Enforceable governance | intent-governance.md | BRD-GOV-022, BRD-GOV-CON-005 | Covered |
| INT-GOV-023 | Policies SHALL be configurable per product — Product-specific governance | intent-governance.md | BRD-GOV-023 | Covered |
| INT-GOV-024 | Policy decisions SHALL be logged for audit — Traceability | intent-governance.md | BRD-GOV-024 | Covered |
| INT-GOV-025 | Low-confidence interpretations SHALL pause for user clarification — Prevent misguided execution | intent-governance.md | BRD-GOV-025 | Covered |
| INT-GOV-026 | Confidence thresholds SHALL be configurable per product — Domain-appropriate sensitivity | intent-governance.md | BRD-GOV-026 | Covered |
| INT-GOV-027 | Semantic validation failures SHALL block execution — Fail-safe behavior | intent-governance.md | BRD-GOV-027 | Covered |
| INT-GOV-028 | Hooks SHALL NOT be bypassed — Prevent disabling governance | intent-governance.md | — | Missing |
| INT-GOV-029 | Policy violations SHALL block execution — Enforce policy compliance | intent-governance.md | — | Missing |
| INT-GOV-035 | Budgets SHALL be hard limits — Prevent overrun | intent-governance.md | — | Missing |
| INT-GOV-CONF-001 | Default confidence threshold SHALL be configurable in `configs/app.yaml` — Platform-wide baseline | intent-governance.md | BRD-GOV-CONF-001 | Covered |
| INT-GOV-CONF-002 | Per-product confidence threshold override SHALL be supported in `configs/products.yaml` — Domain-appropriate sensitivity | intent-governance.md | BRD-GOV-CON-008, BRD-GOV-CONF-002 | Covered |
| INT-GOV-CONF-003 | Default threshold SHALL be 0.7 (adjustable) — Balance usability and safety | intent-governance.md | BRD-GOV-CONF-003 | Covered |
| INT-GOV-CONF-004 | Confidence below threshold SHALL trigger ASK_USER — User gets opportunity to clarify | intent-governance.md | BRD-GOV-CON-007, BRD-GOV-CONF-004 | Covered |
| INT-GOV-CONF-005 | Governance hook `check_semantic_confidence` SHALL enforce thresholds — Enforceable via governance layer | intent-governance.md | BRD-GOV-CON-009, BRD-GOV-CONF-005 | Covered |
| INT-GOV-CONF-006 | Effective confidence SHALL be minimum of (envelope.confidence, validation.revised_confidence) — Conservative confidence calculation | intent-governance.md | BRD-GOV-CONF-006 | Covered |
| INT-GOV-CONF-007 | Threshold enforcement SHALL be logged with confidence values — Audit trail for decisions | intent-governance.md | BRD-GOV-CONF-007 | Covered |
| INT-GOV-CONF-008 | Threshold SHALL be enforced — Prevent low-confidence execution | intent-governance.md | — | Missing |
| INT-GOV-CONF-009 | Overrides SHALL require explicit config — Prevent implicit threshold changes | intent-governance.md | — | Missing |
| INT-GOV-CONF-010 | Confidence check SHALL be a governance hook — Avoid business-logic-only enforcement | intent-governance.md | — | Missing |
| INT-GOV-030 | Each workflow run SHALL have enforceable budget limits — Cost predictability | intent-governance.md | BRD-GOV-030 | Covered |
| INT-GOV-031 | Budget limits SHALL cover: LLM tokens, tool calls, time — Comprehensive control | intent-governance.md | BRD-GOV-031 | Covered |
| INT-GOV-032 | Budget exhaustion SHALL pause or terminate the workflow — Prevent runaway costs | intent-governance.md | BRD-GOV-032, BRD-GOV-CON-006 | Covered |
| INT-GOV-033 | Current budget consumption SHALL be trackable in real time — Operational awareness | intent-governance.md | BRD-GOV-033 | Covered |
| INT-GOV-034 | Budget alerts SHALL trigger before limits are reached — Proactive management | intent-governance.md | BRD-GOV-034 | Covered |
| INT-GOV-040 | Every action SHALL be traceable to: who, what, when, why — Compliance requirement | intent-governance.md | BRD-GOV-040 | Covered |
| INT-GOV-041 | State transitions SHALL be immutable once recorded — Non-repudiation | intent-governance.md | BRD-GOV-041 | Covered |
| INT-GOV-042 | Audit logs SHALL be queryable by run, user, timeframe — Investigation support | intent-governance.md | BRD-GOV-042 | Covered |
| INT-GOV-043 | Audit data SHALL be exportable in standard formats — External audit tools | intent-governance.md | BRD-GOV-043 | Covered |
| INT-GOV-044 | Audit retention period SHALL be configurable — Compliance with data policies | intent-governance.md | BRD-GOV-044 | Covered |
| PLAT-AUD-001 | Platform SHALL generate immutable decision records for every gated action, capturing options considered, evidence used, critique feedback, final choice, and confidence — Ensure auditable decision provenance | intent-governance.md | — | Missing |
| PLAT-POL-001 | Platform SHALL prevent runtime learning or self-modification during execution — Preserve determinism and auditability | intent-governance.md | BRD-GOV-054 | Covered |

## 3. Experience (INT-EXP → BRD)

| Intent ID | Intent | Source File | BRD ID(s) | Covered status |
|-----------|--------|-------------|-----------|----------------|
| INT-EXP-001 | Platform SHALL be accessible via HTTP REST API — Integration standard | intent-experience.md | BRD-EXP-001 | Covered |
| INT-EXP-002 | API responses SHALL follow a consistent envelope format — Predictable parsing | intent-experience.md | BRD-EXP-002 | Covered |
| INT-EXP-003 | API errors SHALL include machine-readable codes — Automated error handling | intent-experience.md | BRD-EXP-003 | Covered |
| INT-EXP-004 | API errors SHALL include human-readable messages — Developer debugging | intent-experience.md | BRD-EXP-004 | Covered |
| INT-EXP-005 | API SHALL support listing products and flows — Discovery | intent-experience.md | BRD-EXP-005 | Covered |
| INT-EXP-006 | API SHALL support starting, monitoring, and resuming runs — Core functionality | intent-experience.md | BRD-EXP-006 | Covered |
| INT-EXP-007 | API SHALL enforce payload size limits — Resource protection | intent-experience.md | BRD-EXP-007 | Covered |
| INT-EXP-010 | Platform SHALL be accessible via command-line interface — Operator standard | intent-experience.md | BRD-EXP-010 | Covered |
| INT-EXP-011 | CLI output SHALL be valid JSON for scripting — Automation support | intent-experience.md | BRD-EXP-011 | Covered |
| INT-EXP-012 | CLI SHALL provide commands for all core operations — Feature parity | intent-experience.md | BRD-EXP-012 | Covered |
| INT-EXP-013 | CLI errors SHALL exit with appropriate status codes — Script integration | intent-experience.md | BRD-EXP-013 | Covered |
| INT-EXP-014 | CLI SHALL provide helpful guidance on errors — User experience | intent-experience.md | BRD-EXP-014 | Covered |
| INT-EXP-020 | Platform SHALL be accessible via web interface — Non-technical users | intent-experience.md | BRD-EXP-020 | Covered |
| INT-EXP-021 | UI SHALL display available products and flows — Discovery | intent-experience.md | BRD-EXP-021 | Covered |
| INT-EXP-022 | UI SHALL allow running flows with input — Core functionality | intent-experience.md | BRD-EXP-022 | Covered |
| INT-EXP-023 | UI SHALL display run status and history — Monitoring | intent-experience.md | BRD-EXP-023 | Covered |
| INT-EXP-024 | UI SHALL support approval workflows — Human-in-the-loop | intent-experience.md | BRD-EXP-024 | Covered |
| INT-EXP-025 | UI SHALL support user input collection — Interactive workflows | intent-experience.md | BRD-EXP-025 | Covered |
| INT-EXP-026 | UI SHALL display execution timeline with events — Debugging support | intent-experience.md | BRD-EXP-026 | Covered |
| INT-EXP-030 | New products SHALL be creatable from standard structure — Fast onboarding | intent-experience.md | BRD-EXP-030 | Covered |
| INT-EXP-031 | Products SHALL declare capabilities via manifest — Self-documenting | intent-experience.md | BRD-EXP-031 | Covered |
| INT-EXP-032 | Products SHALL be auto-discovered without restart — Developer velocity | intent-experience.md | BRD-EXP-032 | Covered |
| INT-EXP-033 | Products SHALL be independently enableable/disableable — Operational control | intent-experience.md | BRD-EXP-033 | Covered |
| INT-EXP-034 | Product load errors SHALL NOT crash the platform — Fault isolation | intent-experience.md | BRD-EXP-034 | Covered |
| INT-EXP-040 | Products SHALL NOT access other products' agents or tools — Security boundary | intent-experience.md | BRD-EXP-040 | Covered |
| INT-EXP-041 | Products SHALL NOT access other products' data — Data isolation | intent-experience.md | BRD-EXP-041 | Covered |
| INT-EXP-042 | Product failures SHALL NOT affect other products — Fault isolation | intent-experience.md | BRD-EXP-042 | Covered |
| INT-EXP-043 | Products SHALL have isolated observability directories — Clean separation | intent-experience.md | BRD-EXP-043 | Covered |
| INT-EXP-044 | Products SHALL NOT modify core — Prevent platform corruption | intent-experience.md | BRD-EXP-044, BRD-EXP-CON-001 | Covered |
| INT-EXP-045 | Products SHALL be isolated — Prevent cross-product access | intent-experience.md | BRD-EXP-CON-002 | Covered |
| INT-EXP-046 | Products SHALL be fault-isolated — Prevent cascading failures | intent-experience.md | BRD-EXP-CON-003 | Covered |

## 4. Operations (INT-OPS / PLAT-* → BRD)

| Intent ID | Intent | Source File | BRD ID(s) | Covered status |
|-----------|--------|-------------|-----------|----------------|
| INT-OPS-001 | Run state SHALL survive process restarts — Reliability | intent-operations.md | BRD-OPS-001 | Covered |
| INT-OPS-002 | In-flight workflows SHALL be resumable after restart — No lost work | intent-operations.md | BRD-OPS-002 | Covered |
| INT-OPS-003 | State SHALL be persisted durably (not just in-memory) — Data safety | intent-operations.md | BRD-OPS-003 | Covered |
| INT-OPS-004 | State storage SHALL support concurrent access — Scalability | intent-operations.md | BRD-OPS-004 | Covered |
| INT-OPS-005 | Historical runs SHALL be queryable — Audit, debugging | intent-operations.md | BRD-OPS-005 | Covered |
| INT-OPS-006 | State SHALL survive restarts — Prevent run loss after restart | intent-operations.md | BRD-OPS-CON-001 | Covered |
| INT-OPS-007 | State transitions SHALL be traced — Prevent silent state changes | intent-operations.md | BRD-OPS-CON-002 | Covered |
| INT-OPS-008 | All actions SHALL be traced — Prevent untracked actions | intent-operations.md | BRD-OPS-CON-003 | Covered |
| INT-OPS-010 | Every execution step SHALL be traced — Debugging | intent-operations.md | BRD-OPS-010 | Covered |
| INT-OPS-011 | Traces SHALL include: timestamp, event type, data — Complete picture | intent-operations.md | BRD-OPS-011 | Covered |
| INT-OPS-012 | Traces SHALL be queryable by run, step, timeframe — Investigation | intent-operations.md | BRD-OPS-012 | Covered |
| INT-OPS-013 | Large outputs SHALL be stored to files, not inline — Storage efficiency | intent-operations.md | BRD-OPS-013 | Covered |
| INT-OPS-014 | Observability data SHALL be organized by product/run — Multi-tenancy | intent-operations.md | BRD-OPS-014 | Covered |
| INT-OPS-015 | Dashboards SHALL visualize run status and trends — Operations monitoring | intent-operations.md | BRD-OPS-015 | Covered |
| INT-OPS-SEM-001 | `semantic_interpretation_started` event SHALL be emitted when phase begins — Track phase lifecycle | intent-operations.md | BRD-OPS-SEM-001 | Covered |
| INT-OPS-SEM-002 | Started event SHALL include: run_id, product_id, raw_input_length — Context for debugging | intent-operations.md | BRD-OPS-SEM-002 | Covered |
| INT-OPS-SEM-003 | `semantic_interpretation_completed` event SHALL be emitted when phase succeeds — Track successful interpretation | intent-operations.md | BRD-OPS-SEM-003 | Covered |
| INT-OPS-SEM-004 | Completed event SHALL include: envelope_hash, confidence, ambiguity_count, entity_count, next_action — Interpretation metrics | intent-operations.md | BRD-OPS-SEM-004 | Covered |
| INT-OPS-SEM-005 | `semantic_validation_completed` event SHALL be emitted after validation — Track validation outcome | intent-operations.md | BRD-OPS-SEM-005 | Covered |
| INT-OPS-SEM-006 | Validation event SHALL include: is_valid, missing_fields, violation_count, revised_confidence — Validation metrics | intent-operations.md | BRD-OPS-SEM-006 | Covered |
| INT-OPS-SEM-007 | `semantic_stop_issued` event SHALL be emitted on ASK_USER or ABORT — Track stop decisions | intent-operations.md | BRD-OPS-SEM-007 | Covered |
| INT-OPS-SEM-008 | Stop event SHALL include: next_action, question (if ASK_USER), reason (if ABORT), violations — Stop context | intent-operations.md | BRD-OPS-SEM-008 | Covered |
| INT-OPS-SEM-009 | `semantic_interpretation_failed` event SHALL be emitted on exception — Error visibility | intent-operations.md | BRD-OPS-SEM-009 | Covered |
| INT-OPS-SEM-010 | Failed event SHALL include: error message — Debugging information | intent-operations.md | BRD-OPS-SEM-010 | Covered |
| INT-OPS-SEM-011 | Events SHALL be structured — Avoid free-form logs | intent-operations.md | BRD-OPS-CON-004 | Covered |
| INT-OPS-SEM-012 | Events SHALL include run_id — Ensure correlation | intent-operations.md | BRD-OPS-CON-005 | Covered |
| INT-OPS-SEM-013 | Events SHALL include timestamps — Ensure event ordering | intent-operations.md | BRD-OPS-CON-006 | Covered |
| PLAT-OPS-001 | Platform SHALL guarantee post-hoc explainability and reproducibility by retaining reasoning artifacts and execution context — Make outcomes explainable and repeatable | intent-operations.md | BRD-OPS-060 | Covered |
| PLAT-OPS-002 | Platform SHALL record versions, inputs, and hashes required to reproduce outcomes — Enable deterministic replay and audit | intent-operations.md | BRD-OPS-061 | Covered |
| INT-OPS-020 | API responses SHALL complete within 500ms (p95) — User experience | intent-operations.md | BRD-OPS-020 | Covered |
| INT-OPS-021 | Run startup SHALL complete within 2 seconds — Responsiveness | intent-operations.md | BRD-OPS-021 | Covered |
| INT-OPS-022 | Memory backend operations SHALL complete within 100ms — System responsiveness | intent-operations.md | BRD-OPS-022 | Covered |
| INT-OPS-023 | Performance metrics SHALL be measurable — SLA monitoring | intent-operations.md | BRD-OPS-023 | Covered |
| INT-OPS-030 | Core modules SHALL have ≥80% test coverage — Quality baseline | intent-operations.md | BRD-OPS-030 | Covered |
| INT-OPS-031 | Critical paths (run lifecycle) SHALL have 100% coverage — Risk mitigation | intent-operations.md | BRD-OPS-031 | Covered |
| INT-OPS-032 | All tests SHALL pass before deployment — Quality gate | intent-operations.md | BRD-OPS-032 | Covered |
| INT-OPS-033 | Tests SHALL complete within 10 minutes — Developer velocity | intent-operations.md | BRD-OPS-033 | Covered |
| INT-OPS-034 | Contracts (Pydantic models) SHALL have validation tests — Interface stability | intent-operations.md | BRD-OPS-034 | Covered |
| INT-OPS-040 | Failed runs SHALL include error details and stack traces — Root cause analysis | intent-operations.md | BRD-OPS-040 | Covered |
| INT-OPS-041 | Event timeline SHALL be viewable for any run — Execution understanding | intent-operations.md | BRD-OPS-041 | Covered |
| INT-OPS-042 | Input/output data SHALL be inspectable — Data debugging | intent-operations.md | BRD-OPS-042 | Covered |
| INT-OPS-043 | LLM calls and responses SHALL be logged — AI debugging | intent-operations.md | BRD-OPS-043 | Covered |
| INT-OPS-044 | Tool calls and results SHALL be logged — Integration debugging | intent-operations.md | BRD-OPS-044 | Covered |
| INT-OPS-ARCH-001 | Architecture test SHALL verify semantic phase is mandatory — Prevent regression of mandatory phase | intent-operations.md | BRD-OPS-ARCH-001 | Covered |
| INT-OPS-ARCH-002 | Architecture test SHALL verify ASK_USER blocks all step execution — Lock stop behavior | intent-operations.md | BRD-OPS-ARCH-002 | Covered |
| INT-OPS-ARCH-003 | Architecture test SHALL verify ABORT blocks all step execution — Lock abort behavior | intent-operations.md | BRD-OPS-ARCH-003 | Covered |
| INT-OPS-ARCH-004 | Architecture test SHALL verify product adapters do not import core orchestrator — Enforce isolation | intent-operations.md | BRD-OPS-ARCH-004 | Covered |
| INT-OPS-ARCH-005 | Architecture test SHALL verify core orchestrator does not import products — Enforce isolation | intent-operations.md | BRD-OPS-ARCH-005 | Covered |
| INT-OPS-ARCH-006 | Architecture tests SHALL live in `tests/architecture/` directory — Clear test organization | intent-operations.md | BRD-OPS-ARCH-006 | Covered |
| INT-OPS-ARCH-007 | Architecture tests SHALL run as part of CI pipeline — Continuous enforcement | intent-operations.md | BRD-OPS-ARCH-007 | Covered |
| INT-OPS-ARCH-008 | Architecture tests SHALL pass — Prevent ignoring failures | intent-operations.md | BRD-OPS-CON-007 | Covered |
| INT-OPS-ARCH-009 | Tests SHALL verify structure, not behavior — Validate architecture invariants | intent-operations.md | BRD-OPS-CON-008 | Covered |
| INT-OPS-ARCH-010 | Tests SHALL be automated — Avoid manual verification | intent-operations.md | BRD-OPS-CON-009 | Covered |
| PLAT-INV-001 | MASTER SHALL provide standard reasoning middleware primitives that products can invoke without custom orchestration — Reasoning is a platform capability | intent-operations.md | — | Missing |
| PLAT-INV-002 | Reasoning SHALL follow a structured, multi-phase pattern (interpret → propose → critique → recommend) within a controlled step — Consistent and auditable reasoning | intent-operations.md | — | Missing |
| PLAT-INV-003 | Reasoning primitives SHALL be bounded, repeatable, and auditable — Prevent open-ended reasoning | intent-operations.md | — | Missing |
| PLAT-INV-004 | Reasoning outputs SHALL be first-class artifacts, not ephemeral prompt responses — Preserve outputs for auditability | intent-operations.md | BRD-AUTO-036 | Covered |
| PLAT-INV-005 | MASTER SHALL support explicit critique passes as part of intelligent execution — Ensure quality checks | intent-operations.md | — | Missing |
| PLAT-INV-006 | Critique SHALL be advisory only: it may lower confidence, surface gaps, or recommend escalation — Preserve control boundaries | intent-operations.md | — | Missing |
| PLAT-INV-007 | Critique SHALL NEVER execute tools, route flows, override policies, or force decisions — Prevent unauthorized control | intent-operations.md | — | Missing |
| PLAT-INV-008 | Control authority SHALL always remain with the orchestrator and governance layer — Centralize control | intent-operations.md | — | Missing |
| PLAT-INV-009 | All semantic interpretations SHALL be treated as hypotheses with confidence, not facts — Prevent over-trust | intent-operations.md | BRD-GOV-060 | Covered |
| PLAT-INV-010 | MASTER SHALL represent interpretation as multiple competing candidates where ambiguity exists — Preserve ambiguity | intent-operations.md | BRD-GOV-061 | Covered |
| PLAT-INV-011 | Confidence and ambiguity SHALL propagate into downstream artifacts, decisions, and outputs — Preserve uncertainty | intent-operations.md | BRD-GOV-062 | Covered |
| PLAT-INV-012 | When ambiguity exceeds policy thresholds, execution SHALL require HITL or halt safely — Avoid unsafe execution | intent-operations.md | BRD-GOV-063 | Covered |
| PLAT-INV-013 | Any gated or consequential decision SHALL be recorded as a decision artifact — Preserve decision history | intent-operations.md | BRD-GOV-045 | Covered |
| PLAT-INV-014 | Decision artifacts SHALL capture options, evidence, critique input, final choice, justification, confidence — Ensure auditability | intent-operations.md | BRD-GOV-046 | Covered |
| PLAT-INV-015 | Decision artifacts SHALL be immutable once recorded — Prevent tampering | intent-operations.md | BRD-GOV-047 | Covered |
| PLAT-INV-016 | MASTER SHALL provide standard iteration patterns for intelligent workflows — Avoid ad hoc iteration | intent-operations.md | — | Missing |
| PLAT-INV-017 | Iteration SHALL follow a governed cycle (propose → gate → execute → evaluate) — Controlled iteration | intent-operations.md | BRD-AUTO-044 | Covered |
| PLAT-INV-018 | Iteration SHALL have explicit deterministic stop conditions (budgets, sufficiency, escalation) — Avoid runaway loops | intent-operations.md | BRD-AUTO-045 | Covered |
| PLAT-INV-019 | Iterative state SHALL be durable and resumable across restarts — Reliability | intent-operations.md | BRD-AUTO-046 | Covered |
| PLAT-INV-020 | Agents SHALL be advisory only and MUST NOT control execution, routing, or side effects — Preserve control boundaries | intent-operations.md | — | Missing |
| PLAT-INV-021 | Only the orchestrator SHALL execute tools, change flow state, pause/resume runs, and escalate to HITL — Centralize execution control | intent-operations.md | — | Missing |
| PLAT-INV-022 | Governance hooks SHALL be non-bypassable at all lifecycle points — Enforce governance | intent-operations.md | BRD-GOV-050, BRD-GOV-051, BRD-GOV-CON-004 | Covered |
| PLAT-INV-023 | Products SHALL be isolated and MUST NOT access other products' resources directly — Enforce product isolation | intent-operations.md | — | Missing |
| PLAT-INV-024 | MASTER SHALL make reasoning behavior observable, not just execution steps — Audit reasoning | intent-operations.md | BRD-AUTO-034, BRD-OPS-016 | Covered |
| PLAT-INV-025 | Traces SHALL expose options considered, confidence evolution, rejection and escalation reasons — Explainability | intent-operations.md | BRD-AUTO-035, BRD-OPS-017 | Covered |
| PLAT-INV-026 | Reasoning traces SHALL be queryable for audit, debugging, and improvement analysis — Continuous improvement | intent-operations.md | BRD-OPS-018 | Covered |

---

## Gap Register (Partial / Missing / Clarification Needed Only)

| Gap Type | Source File | ID | Detail |
|---------|-------------|----|--------|
| Missing | intent-automation.md | INT-AUTO-SEM-012 | No BRD mapping |
| Missing | intent-automation.md | INT-AUTO-SEM-013 | No BRD mapping |
| Missing | intent-automation.md | INT-AUTO-SEM-014 | No BRD mapping |
| Missing | intent-governance.md | INT-GOV-015 | No BRD mapping |
| Missing | intent-governance.md | INT-GOV-016 | No BRD mapping |
| Missing | intent-governance.md | INT-GOV-017 | No BRD mapping |
| Missing | intent-governance.md | INT-GOV-028 | No BRD mapping |
| Missing | intent-governance.md | INT-GOV-029 | No BRD mapping |
| Missing | intent-governance.md | INT-GOV-035 | No BRD mapping |
| Missing | intent-governance.md | INT-GOV-CONF-008 | No BRD mapping |
| Missing | intent-governance.md | INT-GOV-CONF-009 | No BRD mapping |
| Missing | intent-governance.md | INT-GOV-CONF-010 | No BRD mapping |
| Missing | intent-governance.md | PLAT-AUD-001 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-001 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-002 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-003 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-005 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-006 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-007 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-008 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-016 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-020 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-021 | No BRD mapping |
| Missing | intent-operations.md | PLAT-INV-023 | No BRD mapping |
| Clarification Needed | intent-automation.md | PLAT-AUTO-001 | Intent notes flag clarification |
| Clarification Needed | intent-automation.md | PLAT-AUTO-002 | Intent notes flag clarification |
| Clarification Needed | BRD-automation.md | BRD-AUTO-CON-010 | BRD row missing intent ID |
| Clarification Needed | BRD-automation.md | BRD-AUTO-LIFE-001 | BRD row missing intent ID |
| Clarification Needed | BRD-automation.md | BRD-AUTO-LIFE-002 | BRD row missing intent ID |
| Clarification Needed | BRD-automation.md | BRD-AUTO-LIFE-003 | BRD row missing intent ID |
| Clarification Needed | BRD-automation.md | BRD-AUTO-FAC-001 | BRD row missing intent ID |
| Clarification Needed | BRD-automation.md | BRD-AUTO-FAC-002 | BRD row missing intent ID |
| Clarification Needed | BRD-automation.md | BRD-AUTO-FAC-003 | BRD row missing intent ID |
| Clarification Needed | BRD-automation.md | BRD-AUTO-FAC-004 | BRD row missing intent ID |
| Clarification Needed | BRD-automation.md | BRD-AUTO-FAC-005 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-035 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-036 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-037 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-050 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-051 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-052 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-053 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-060 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-061 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-062 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-063 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-064 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-LIFE-001 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-LIFE-002 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-LIFE-003 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-FAC-001 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-FAC-002 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-FAC-003 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-FAC-004 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-FAC-010 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-FAC-011 | BRD row missing intent ID |
| Clarification Needed | BRD-experience.md | BRD-EXP-FAC-012 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-052 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-053 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-LIFE-001 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-LIFE-002 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-LIFE-003 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-LIFE-010 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-LIFE-011 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-LIFE-012 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-LIFE-013 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-FAC-001 | BRD row missing intent ID |
| Clarification Needed | BRD-governance.md | BRD-GOV-FAC-002 | BRD row missing intent ID |
| Clarification Needed | BRD-operations.md | BRD-OPS-050 | BRD row missing intent ID |
| Clarification Needed | BRD-operations.md | BRD-OPS-051 | BRD row missing intent ID |
| Clarification Needed | BRD-operations.md | BRD-OPS-052 | BRD row missing intent ID |
| Clarification Needed | BRD-operations.md | BRD-OPS-053 | BRD row missing intent ID |
| Clarification Needed | BRD-operations.md | BRD-OPS-LIFE-001 | BRD row missing intent ID |
| Clarification Needed | BRD-operations.md | BRD-OPS-LIFE-002 | BRD row missing intent ID |
| Clarification Needed | BRD-operations.md | BRD-OPS-FAC-001 | BRD row missing intent ID |
| Clarification Needed | BRD-operations.md | BRD-OPS-FAC-002 | BRD row missing intent ID |

## Next BRD Edits Required

- [ ] `docs/02_brd/BRD-automation.md` (resolve missing intent IDs and add mappings for missing INT/PLAT intents)
- [ ] `docs/02_brd/BRD-governance.md` (resolve missing intent IDs and add mappings for missing INT/PLAT intents)
- [ ] `docs/02_brd/BRD-experience.md` (resolve missing intent IDs)
- [ ] `docs/02_brd/BRD-operations.md` (resolve missing intent IDs and add mappings for missing INT/PLAT intents)

BRD-COVERAGE GAP COUNT: 76
