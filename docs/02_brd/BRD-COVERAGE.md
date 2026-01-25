# BRD Coverage Analysis

> **Document ID**: BRD-COVERAGE  
> **Version**: V1.3  
> **Last Updated**: 2026-01-25  
> **Status**: V1 Release  

> **Purpose**: Track traceability between Developer Intent documents and Business Requirement Documents (BRDs).  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |
| V1.2 | 2026-01-19 | Standardized coverage schema and refreshed intent-to-BRD mappings |
| V1.3 | 2026-01-25 | Full intent refresh for V1.3 intents; added PLAT-AUTO-DISC, PLAT-GOV-GATE, PLAT-GOV-EVID, PLAT-INV-027-030; closed all coverage gaps |

---

## Coverage Summary

| Intent Document | BRD Document | Intent IDs | Covered | Missing | Clarification Needed |
|-----------------|--------------|------------|---------|---------|----------------------|
| [intent-automation.md](../01_vision_and_intent/intent-automation.md) | [BRD-automation.md](BRD-automation.md) | 93 | 93 | 0 | 0 |
| [intent-governance.md](../01_vision_and_intent/intent-governance.md) | [BRD-governance.md](BRD-governance.md) | 58 | 58 | 0 | 0 |
| [intent-experience.md](../01_vision_and_intent/intent-experience.md) | [BRD-experience.md](BRD-experience.md) | 31 | 31 | 0 | 0 |
| [intent-operations.md](../01_vision_and_intent/intent-operations.md) | [BRD-operations.md](BRD-operations.md) | 93 | 93 | 0 | 0 |

---

## 1. Automation (INT-AUTO / PLAT-* → BRD)

| Intent ID | Intent | Source File | BRD ID(s) | Covered status |
|-----------|--------|-------------|-----------|----------------|
| INT-AUTO-SEM-001 | Semantic interpretation SHALL run before any step execution in every flow | intent-automation.md | BRD-AUTO-SEM-001 | Covered |
| INT-AUTO-SEM-002 | Interpretation SHALL produce structured `SemanticEnvelope` output | intent-automation.md | BRD-AUTO-SEM-002 | Covered |
| INT-AUTO-SEM-003 | `SemanticEnvelope` SHALL include normalized intent, confidence score, entities, constraints | intent-automation.md | BRD-AUTO-SEM-003 | Covered |
| INT-AUTO-SEM-004 | Confidence score SHALL range 0.0–1.0 with semantic meaning | intent-automation.md | BRD-AUTO-CON-011, BRD-AUTO-SEM-004 | Covered |
| INT-AUTO-SEM-005 | Entities SHALL be typed: PERSON, ORGANIZATION, DATE, AMOUNT, PRODUCT, CUSTOM | intent-automation.md | BRD-AUTO-SEM-005 | Covered |
| INT-AUTO-SEM-006 | Ambiguities SHALL be captured as a structured list with resolution options | intent-automation.md | BRD-AUTO-CON-009, BRD-AUTO-SEM-006 | Covered |
| INT-AUTO-SEM-007 | If confidence < threshold, next_action SHALL be ASK_USER | intent-automation.md | BRD-AUTO-SEM-007 | Covered |
| INT-AUTO-SEM-008 | If unresolvable conflict detected, next_action SHALL be ABORT with reason | intent-automation.md | BRD-AUTO-SEM-008 | Covered |
| INT-AUTO-SEM-009 | Interpretation phase SHALL be product-agnostic at framework level | intent-automation.md | BRD-AUTO-SEM-009 | Covered |
| INT-AUTO-SEM-010 | Products SHALL be able to override interpretation via semantic adapter interface | intent-automation.md | BRD-AUTO-SEM-010 | Covered |
| INT-AUTO-SEM-011 | Semantic phase SHALL be mandatory | intent-automation.md | BRD-AUTO-CON-008 | Covered |
| INT-AUTO-SEM-012 | Envelope SHALL be the only handoff to planning | intent-automation.md | BRD-AUTO-SEM-011 | Covered |
| INT-AUTO-SEM-013 | Confidence gates SHALL control execution | intent-automation.md | BRD-AUTO-SEM-012 | Covered |
| INT-AUTO-SEM-014 | Ambiguities SHALL be explicit | intent-automation.md | BRD-AUTO-SEM-013 | Covered |
| INT-AUTO-ADAPT-001 | Products SHALL be able to provide custom semantic interpretation via adapter interface | intent-automation.md | BRD-AUTO-ADAPT-001 | Covered |
| INT-AUTO-ADAPT-002 | Adapter interface SHALL define `interpret(context) → SemanticEnvelope` method | intent-automation.md | BRD-AUTO-ADAPT-002 | Covered |
| INT-AUTO-ADAPT-003 | Adapter interface SHALL define `validate(envelope, context) → ValidationResult` method | intent-automation.md | BRD-AUTO-ADAPT-003 | Covered |
| INT-AUTO-ADAPT-004 | Default adapter SHALL be provided for products without custom implementation | intent-automation.md | BRD-AUTO-ADAPT-004 | Covered |
| INT-AUTO-ADAPT-005 | Default adapter SHALL return passthrough envelope with confidence=1.0 | intent-automation.md | BRD-AUTO-ADAPT-005 | Covered |
| INT-AUTO-ADAPT-006 | Adapters SHALL be discovered from `products/<name>/semantic.py` | intent-automation.md | BRD-AUTO-ADAPT-006 | Covered |
| INT-AUTO-ADAPT-007 | Adapters SHALL be resolved via ProductRouter, not direct import | intent-automation.md | BRD-AUTO-ADAPT-007 | Covered |
| INT-AUTO-ADAPT-008 | Product adapters SHALL NOT import from `core/orchestrator/*` | intent-automation.md | BRD-AUTO-ADAPT-008 | Covered |
| INT-AUTO-ADAPT-009 | Core orchestrator SHALL NOT import from `products/*` | intent-automation.md | BRD-AUTO-ADAPT-009 | Covered |
| INT-AUTO-ADAPT-010 | Adapter execution SHALL have timeout with fallback to default | intent-automation.md | BRD-AUTO-ADAPT-010 | Covered |
| INT-AUTO-ADAPT-011 | Adapters SHALL be pure functions | intent-automation.md | BRD-AUTO-CON-012 | Covered |
| INT-AUTO-ADAPT-012 | Adapters SHALL NOT execute tools | intent-automation.md | BRD-AUTO-CON-013 | Covered |
| INT-AUTO-ADAPT-013 | Adapters SHALL NOT access other products | intent-automation.md | BRD-AUTO-CON-014 | Covered |
| INT-AUTO-ADAPT-014 | Isolation SHALL be bidirectional | intent-automation.md | BRD-AUTO-CON-015 | Covered |
| INT-AUTO-STOP-001 | ASK_USER SHALL pause the run and return a structured clarification response | intent-automation.md | BRD-AUTO-STOP-001 | Covered |
| INT-AUTO-STOP-002 | Clarification response SHALL include: question, ambiguities, original confidence, context | intent-automation.md | BRD-AUTO-STOP-002 | Covered |
| INT-AUTO-STOP-003 | Run status SHALL be PAUSED_WAITING_FOR_USER during clarification | intent-automation.md | BRD-AUTO-STOP-003 | Covered |
| INT-AUTO-STOP-004 | ABORT SHALL fail the run with structured error response | intent-automation.md | BRD-AUTO-STOP-004 | Covered |
| INT-AUTO-STOP-005 | Abort error SHALL include: error_code=semantic_abort, reason, violations, ambiguities | intent-automation.md | BRD-AUTO-STOP-005 | Covered |
| INT-AUTO-STOP-006 | Run status SHALL be FAILED after ABORT | intent-automation.md | BRD-AUTO-STOP-006 | Covered |
| INT-AUTO-STOP-007 | ASK_USER and ABORT SHALL prevent any step execution | intent-automation.md | BRD-AUTO-STOP-007 | Covered |
| INT-AUTO-STOP-008 | Trace event `semantic_stop_issued` SHALL be emitted on stop | intent-automation.md | BRD-AUTO-STOP-008 | Covered |
| INT-AUTO-STOP-009 | Paused runs SHALL be resumable with user-provided clarification | intent-automation.md | BRD-AUTO-STOP-009 | Covered |
| INT-AUTO-STOP-010 | Stop SHALL block all steps | intent-automation.md | BRD-AUTO-CON-016 | Covered |
| INT-AUTO-STOP-011 | Abort SHALL be terminal | intent-automation.md | BRD-AUTO-CON-017 | Covered |
| INT-AUTO-STOP-012 | Clarification SHALL be structured | intent-automation.md | BRD-AUTO-CON-018 | Covered |
| INT-AUTO-001 | Agents SHALL reason through multi-step tasks with observable decision points | intent-automation.md | BRD-AUTO-001 | Covered |
| INT-AUTO-002 | Agents SHALL provide evidence supporting their decisions | intent-automation.md | BRD-AUTO-002 | Covered |
| INT-AUTO-003 | Agents SHALL be composable; one agent can delegate to others | intent-automation.md | BRD-AUTO-003 | Covered |
| INT-AUTO-004 | Agents SHALL handle failures gracefully with retry or escalation | intent-automation.md | BRD-AUTO-004 | Covered |
| INT-AUTO-005 | Agent behavior SHALL be deterministic given the same inputs | intent-automation.md | BRD-AUTO-005 | Covered |
| INT-AUTO-006 | Agents SHALL be advisory only | intent-automation.md | BRD-AUTO-CON-001 | Covered |
| INT-AUTO-007 | Agents SHALL be stateless | intent-automation.md | BRD-AUTO-CON-002 | Covered |
| INT-AUTO-008 | Agents SHALL NOT branch flows | intent-automation.md | BRD-AUTO-CON-003 | Covered |
| INT-AUTO-009 | Agents SHALL NOT modify policies | intent-automation.md | BRD-AUTO-CON-004 | Covered |
| INT-AUTO-010 | Tools SHALL be discoverable with clear capability descriptions | intent-automation.md | BRD-AUTO-010 | Covered |
| INT-AUTO-011 | Tools SHALL have typed inputs and outputs | intent-automation.md | BRD-AUTO-011 | Covered |
| INT-AUTO-012 | Tools SHALL be executable in isolation for testing | intent-automation.md | BRD-AUTO-012 | Covered |
| INT-AUTO-013 | Tool results SHALL include structured evidence | intent-automation.md | BRD-AUTO-013 | Covered |
| INT-AUTO-014 | Tool execution SHALL be observable and traceable | intent-automation.md | BRD-AUTO-014 | Covered |
| INT-AUTO-015 | Tools SHALL be deterministic | intent-automation.md | BRD-AUTO-CON-005 | Covered |
| INT-AUTO-016 | Tools SHALL execute via ToolExecutor only | intent-automation.md | BRD-AUTO-CON-006 | Covered |
| INT-AUTO-017 | Tools SHALL declare side effects | intent-automation.md | BRD-AUTO-CON-007 | Covered |
| INT-AUTO-020 | System SHALL select appropriate tools for tasks automatically | intent-automation.md | BRD-AUTO-020 | Covered |
| INT-AUTO-021 | System SHALL select appropriate agents for subtasks | intent-automation.md | BRD-AUTO-021 | Covered |
| INT-AUTO-022 | System SHALL identify gaps in information and request clarification | intent-automation.md | BRD-AUTO-022 | Covered |
| INT-AUTO-023 | System SHALL summarize complex results for human consumption | intent-automation.md | BRD-AUTO-023 | Covered |
| INT-AUTO-024 | System SHALL explain risks before executing high-impact actions | intent-automation.md | BRD-AUTO-024 | Covered |
| INT-AUTO-025 | System SHALL interpret user intent before planning/execution | intent-automation.md | BRD-AUTO-025 | Covered |
| INT-AUTO-026 | System SHALL normalize and validate input before acting | intent-automation.md | BRD-AUTO-026 | Covered |
| INT-AUTO-027 | System SHALL express interpretation confidence and request clarification when uncertain | intent-automation.md | BRD-AUTO-027 | Covered |
| PLAT-AUTO-001 | System SHALL support multiple competing hypotheses with confidence scores | intent-automation.md | BRD-AUTO-028 | Covered |
| PLAT-AUTO-002 | System SHALL maintain a persistent sufficiency state | intent-automation.md | BRD-AUTO-029 | Covered |
| INT-AUTO-030 | Reasoning SHALL progress through structured phases | intent-automation.md | BRD-AUTO-030 | Covered |
| INT-AUTO-031 | Proposals SHALL be evaluated by critic before execution | intent-automation.md | BRD-AUTO-031 | Covered |
| INT-AUTO-032 | Context SHALL be enriched with relevant knowledge before reasoning | intent-automation.md | BRD-AUTO-032 | Covered |
| INT-AUTO-033 | Reasoning failures SHALL trigger appropriate escalation | intent-automation.md | BRD-AUTO-033 | Covered |
| INT-AUTO-034 | Platform SHALL define and enforce a Minimum Reasoning Contract for all products | intent-automation.md | BRD-AUTO-053 | Covered |
| PLAT-ORCH-001 | Platform SHALL provide a central, reusable reasoning lifecycle | intent-automation.md | BRD-AUTO-047 | Covered |
| PLAT-ORCH-002 | Orchestrator SHALL support bounded reasoning iteration with deterministic stop conditions | intent-automation.md | BRD-AUTO-048 | Covered |
| PLAT-ORCH-003 | Intent sufficiency SHALL be a first-class orchestration responsibility | intent-automation.md | BRD-AUTO-054 | Covered |
| PLAT-CTRL-001 | Platform SHALL track, update, and propagate confidence as a core runtime signal | intent-automation.md | BRD-AUTO-049 | Covered |
| PLAT-CTRL-002 | Platform SHALL enforce a mandatory advisory critique phase | intent-automation.md | BRD-AUTO-050 | Covered |
| PLAT-EXEC-001 | Platform SHALL construct and freeze a ContextPack before planning or execution | intent-automation.md | BRD-AUTO-051 | Covered |
| PLAT-EXEC-002 | Platform SHALL define and enforce explicit terminal outcomes | intent-automation.md | BRD-AUTO-052 | Covered |
| INT-AUTO-DISC-001 | Every tool and agent SHALL declare capabilities explicitly via structured descriptors | intent-automation.md | BRD-AUTO-DISC-001 | Covered |
| INT-AUTO-DISC-002 | Platform SHALL own and maintain a centralized registry for all tools and agents | intent-automation.md | BRD-AUTO-DISC-002 | Covered |
| INT-AUTO-DISC-003 | Discovery SHALL be intent-filtered | intent-automation.md | BRD-AUTO-DISC-003 | Covered |
| INT-AUTO-DISC-004 | Platform SHALL perform explicit eligibility checks before tool or agent execution | intent-automation.md | BRD-AUTO-DISC-004 | Covered |
| INT-AUTO-DISC-005 | Discovery and selection SHALL be separate concerns | intent-automation.md | BRD-AUTO-DISC-005 | Covered |
| INT-AUTO-DISC-006 | Platform SHALL provide first-class support for tool and agent extension | intent-automation.md | BRD-AUTO-DISC-006 | Covered |
| INT-AUTO-DISC-007 | Tool and agent exposure SHALL be governed by product | intent-automation.md | BRD-AUTO-DISC-007 | Covered |
| INT-AUTO-DISC-008 | Tool and agent discovery SHALL be deterministic | intent-automation.md | BRD-AUTO-DISC-008 | Covered |
| INT-AUTO-040 | Workflows SHALL support sequential, parallel, and conditional steps | intent-automation.md | BRD-AUTO-040 | Covered |
| INT-AUTO-041 | Workflows SHALL support iteration over collections | intent-automation.md | BRD-AUTO-041 | Covered |
| INT-AUTO-042 | Workflow steps SHALL be independently restartable | intent-automation.md | BRD-AUTO-042 | Covered |
| INT-AUTO-043 | Workflows SHALL support nested sub-workflows | intent-automation.md | BRD-AUTO-043 | Covered |

---

## 2. Governance (INT-GOV / PLAT-* → BRD)

| Intent ID | Intent | Source File | BRD ID(s) | Covered status |
|-----------|--------|-------------|-----------|----------------|
| INT-GOV-001 | High-risk actions SHALL require human approval before execution | intent-governance.md | BRD-GOV-001 | Covered |
| INT-GOV-002 | Approval requests SHALL include context: what, why, impact | intent-governance.md | BRD-GOV-002 | Covered |
| INT-GOV-003 | Approvers SHALL be able to approve, reject, or request changes | intent-governance.md | BRD-GOV-003 | Covered |
| INT-GOV-004 | Approval decisions SHALL be recorded with approver identity and timestamp | intent-governance.md | BRD-GOV-004 | Covered |
| INT-GOV-005 | Workflows SHALL pause gracefully while awaiting approval | intent-governance.md | BRD-GOV-005 | Covered |
| INT-GOV-006 | Workflows SHALL resume correctly after approval/rejection | intent-governance.md | BRD-GOV-006 | Covered |
| INT-GOV-007 | HITL decisions SHALL be structurally binding | intent-governance.md | BRD-GOV-007 | Covered |
| INT-GOV-008 | HITL requirements SHALL be declared at flow design time | intent-governance.md | BRD-GOV-008 | Covered |
| INT-GOV-010 | PII SHALL never appear in logs, traces, or persisted data | intent-governance.md | BRD-GOV-010, BRD-GOV-CON-001 | Covered |
| INT-GOV-011 | Credentials and secrets SHALL be redacted from all outputs | intent-governance.md | BRD-GOV-011, BRD-GOV-CON-002 | Covered |
| INT-GOV-012 | Redaction SHALL be automatic, not dependent on developer action | intent-governance.md | BRD-GOV-012, BRD-GOV-CON-003 | Covered |
| INT-GOV-013 | Custom redaction patterns SHALL be configurable per product | intent-governance.md | BRD-GOV-013 | Covered |
| INT-GOV-014 | Redaction failures SHALL halt execution rather than leak data | intent-governance.md | BRD-GOV-014 | Covered |
| INT-GOV-015 | PII SHALL never appear in logs | intent-governance.md | BRD-GOV-015 | Covered |
| INT-GOV-016 | Credentials SHALL never be exposed | intent-governance.md | BRD-GOV-016 | Covered |
| INT-GOV-017 | Redaction SHALL be automatic | intent-governance.md | BRD-GOV-017 | Covered |
| INT-GOV-020 | Certain tools SHALL be prohibitable by policy | intent-governance.md | BRD-GOV-020 | Covered |
| INT-GOV-021 | Certain models SHALL be prohibitable by policy | intent-governance.md | BRD-GOV-021 | Covered |
| INT-GOV-022 | Policy violations SHALL block execution, not just warn | intent-governance.md | BRD-GOV-022, BRD-GOV-CON-005 | Covered |
| INT-GOV-023 | Policies SHALL be configurable per product | intent-governance.md | BRD-GOV-023 | Covered |
| INT-GOV-024 | Policy decisions SHALL be logged for audit | intent-governance.md | BRD-GOV-024 | Covered |
| INT-GOV-025 | Low-confidence interpretations SHALL pause for user clarification | intent-governance.md | BRD-GOV-025 | Covered |
| INT-GOV-026 | Confidence thresholds SHALL be configurable per product | intent-governance.md | BRD-GOV-026 | Covered |
| INT-GOV-027 | Semantic validation failures SHALL block execution | intent-governance.md | BRD-GOV-027 | Covered |
| INT-GOV-028 | Hooks SHALL NOT be bypassed | intent-governance.md | BRD-GOV-028 | Covered |
| INT-GOV-029 | Policy violations SHALL block execution | intent-governance.md | BRD-GOV-029 | Covered |
| INT-GOV-035 | Budgets SHALL be hard limits | intent-governance.md | BRD-GOV-035 | Covered |
| INT-GOV-CONF-001 | Default confidence threshold SHALL be configurable in `configs/app.yaml` | intent-governance.md | BRD-GOV-CONF-001 | Covered |
| INT-GOV-CONF-002 | Per-product confidence threshold override SHALL be supported | intent-governance.md | BRD-GOV-CON-008, BRD-GOV-CONF-002 | Covered |
| INT-GOV-CONF-003 | Default threshold SHALL be 0.7 (adjustable) | intent-governance.md | BRD-GOV-CONF-003 | Covered |
| INT-GOV-CONF-004 | Confidence below threshold SHALL trigger ASK_USER | intent-governance.md | BRD-GOV-CON-007, BRD-GOV-CONF-004 | Covered |
| INT-GOV-CONF-005 | Governance hook `check_semantic_confidence` SHALL enforce thresholds | intent-governance.md | BRD-GOV-CON-009, BRD-GOV-CONF-005 | Covered |
| INT-GOV-CONF-006 | Effective confidence SHALL be minimum of (envelope.confidence, validation.revised_confidence) | intent-governance.md | BRD-GOV-CONF-006 | Covered |
| INT-GOV-CONF-007 | Threshold enforcement SHALL be logged with confidence values | intent-governance.md | BRD-GOV-CONF-007 | Covered |
| INT-GOV-CONF-008 | Threshold SHALL be enforced | intent-governance.md | BRD-GOV-CONF-008 | Covered |
| INT-GOV-CONF-009 | Overrides SHALL require explicit config | intent-governance.md | BRD-GOV-CONF-009 | Covered |
| INT-GOV-CONF-010 | Confidence check SHALL be a governance hook | intent-governance.md | BRD-GOV-CONF-010 | Covered |
| INT-GOV-030 | Each workflow run SHALL have enforceable budget limits | intent-governance.md | BRD-GOV-030 | Covered |
| INT-GOV-031 | Budget limits SHALL cover: LLM tokens, tool calls, time | intent-governance.md | BRD-GOV-031 | Covered |
| INT-GOV-032 | Budget exhaustion SHALL pause or terminate the workflow | intent-governance.md | BRD-GOV-032, BRD-GOV-CON-006 | Covered |
| INT-GOV-033 | Current budget consumption SHALL be trackable in real time | intent-governance.md | BRD-GOV-033 | Covered |
| INT-GOV-034 | Budget alerts SHALL trigger before limits are reached | intent-governance.md | BRD-GOV-034 | Covered |
| INT-GOV-040 | Every action SHALL be traceable to: who, what, when, why | intent-governance.md | BRD-GOV-040 | Covered |
| INT-GOV-041 | State transitions SHALL be immutable once recorded | intent-governance.md | BRD-GOV-041 | Covered |
| INT-GOV-042 | Audit logs SHALL be queryable by run, user, timeframe | intent-governance.md | BRD-GOV-042 | Covered |
| INT-GOV-043 | Audit data SHALL be exportable in standard formats | intent-governance.md | BRD-GOV-043 | Covered |
| INT-GOV-044 | Audit retention period SHALL be configurable | intent-governance.md | BRD-GOV-044 | Covered |
| PLAT-AUD-001 | Platform SHALL generate immutable decision records for every gated action | intent-governance.md | BRD-GOV-064 | Covered |
| PLAT-POL-001 | Platform SHALL prevent runtime learning or self-modification during execution | intent-governance.md | BRD-GOV-054 | Covered |
| INT-GOV-GATE-001 | Platform SHALL enforce a mandatory semantic gate before any flow execution begins | intent-governance.md | BRD-GOV-GATE-001 | Covered |
| INT-GOV-GATE-002 | Semantic gate SHALL validate intent sufficiency, confidence thresholds, and constraint satisfaction | intent-governance.md | BRD-GOV-GATE-002 | Covered |
| INT-GOV-GATE-003 | Execution SHALL be blocked when semantic assumptions are implicit or inferred | intent-governance.md | BRD-GOV-GATE-003 | Covered |
| INT-GOV-GATE-004 | Platform SHALL provide an Intent Sufficiency Gate that enforces hard fail on insufficient intent | intent-governance.md | BRD-GOV-GATE-004 | Covered |
| INT-GOV-GATE-005 | Semantic gate failures SHALL produce structured rejection artifacts | intent-governance.md | BRD-GOV-GATE-005 | Covered |
| INT-GOV-EVID-001 | All decision artifacts SHALL include evidence references | intent-governance.md | BRD-GOV-EVID-001 | Covered |
| INT-GOV-EVID-002 | Confidence scores SHALL be tied to evidence completeness | intent-governance.md | BRD-GOV-EVID-002 | Covered |
| INT-GOV-EVID-003 | Evidence references SHALL be traceable, typed, and queryable for audit | intent-governance.md | BRD-GOV-EVID-003 | Covered |

---

## 3. Experience (INT-EXP → BRD)

| Intent ID | Intent | Source File | BRD ID(s) | Covered status |
|-----------|--------|-------------|-----------|----------------|
| INT-EXP-001 | Platform SHALL be accessible via HTTP REST API | intent-experience.md | BRD-EXP-001 | Covered |
| INT-EXP-002 | API responses SHALL follow a consistent envelope format | intent-experience.md | BRD-EXP-002 | Covered |
| INT-EXP-003 | API errors SHALL include machine-readable codes | intent-experience.md | BRD-EXP-003 | Covered |
| INT-EXP-004 | API errors SHALL include human-readable messages | intent-experience.md | BRD-EXP-004 | Covered |
| INT-EXP-005 | API SHALL support listing products and flows | intent-experience.md | BRD-EXP-005 | Covered |
| INT-EXP-006 | API SHALL support starting, monitoring, and resuming runs | intent-experience.md | BRD-EXP-006 | Covered |
| INT-EXP-007 | API SHALL enforce payload size limits | intent-experience.md | BRD-EXP-007 | Covered |
| INT-EXP-010 | Platform SHALL be accessible via command-line interface | intent-experience.md | BRD-EXP-010 | Covered |
| INT-EXP-011 | CLI output SHALL be valid JSON for scripting | intent-experience.md | BRD-EXP-011 | Covered |
| INT-EXP-012 | CLI SHALL provide commands for all core operations | intent-experience.md | BRD-EXP-012 | Covered |
| INT-EXP-013 | CLI errors SHALL exit with appropriate status codes | intent-experience.md | BRD-EXP-013 | Covered |
| INT-EXP-014 | CLI SHALL provide helpful guidance on errors | intent-experience.md | BRD-EXP-014 | Covered |
| INT-EXP-020 | Platform SHALL be accessible via web interface | intent-experience.md | BRD-EXP-020 | Covered |
| INT-EXP-021 | UI SHALL display available products and flows | intent-experience.md | BRD-EXP-021 | Covered |
| INT-EXP-022 | UI SHALL allow running flows with input | intent-experience.md | BRD-EXP-022 | Covered |
| INT-EXP-023 | UI SHALL display run status and history | intent-experience.md | BRD-EXP-023 | Covered |
| INT-EXP-024 | UI SHALL support approval workflows | intent-experience.md | BRD-EXP-024 | Covered |
| INT-EXP-025 | UI SHALL support user input collection | intent-experience.md | BRD-EXP-025 | Covered |
| INT-EXP-026 | UI SHALL display execution timeline with events | intent-experience.md | BRD-EXP-026 | Covered |
| INT-EXP-030 | New products SHALL be creatable from standard structure | intent-experience.md | BRD-EXP-030 | Covered |
| INT-EXP-031 | Products SHALL declare capabilities via manifest | intent-experience.md | BRD-EXP-031 | Covered |
| INT-EXP-032 | Products SHALL be auto-discovered without restart | intent-experience.md | BRD-EXP-032 | Covered |
| INT-EXP-033 | Products SHALL be independently enableable/disableable | intent-experience.md | BRD-EXP-033 | Covered |
| INT-EXP-034 | Product load errors SHALL NOT crash the platform | intent-experience.md | BRD-EXP-034 | Covered |
| INT-EXP-040 | Products SHALL NOT access other products' agents or tools | intent-experience.md | BRD-EXP-040 | Covered |
| INT-EXP-041 | Products SHALL NOT access other products' data | intent-experience.md | BRD-EXP-041 | Covered |
| INT-EXP-042 | Product failures SHALL NOT affect other products | intent-experience.md | BRD-EXP-042 | Covered |
| INT-EXP-043 | Products SHALL have isolated observability directories | intent-experience.md | BRD-EXP-043 | Covered |
| INT-EXP-044 | Products SHALL NOT modify core | intent-experience.md | BRD-EXP-044, BRD-EXP-CON-001 | Covered |
| INT-EXP-045 | Products SHALL be isolated | intent-experience.md | BRD-EXP-CON-002 | Covered |
| INT-EXP-046 | Products SHALL be fault-isolated | intent-experience.md | BRD-EXP-CON-003 | Covered |

---

## 4. Operations (INT-OPS / PLAT-* → BRD)

| Intent ID | Intent | Source File | BRD ID(s) | Covered status |
|-----------|--------|-------------|-----------|----------------|
| INT-OPS-001 | Run state SHALL survive process restarts | intent-operations.md | BRD-OPS-001 | Covered |
| INT-OPS-002 | In-flight workflows SHALL be resumable after restart | intent-operations.md | BRD-OPS-002 | Covered |
| INT-OPS-003 | State SHALL be persisted durably (not just in-memory) | intent-operations.md | BRD-OPS-003 | Covered |
| INT-OPS-004 | State storage SHALL support concurrent access | intent-operations.md | BRD-OPS-004 | Covered |
| INT-OPS-005 | Historical runs SHALL be queryable | intent-operations.md | BRD-OPS-005 | Covered |
| INT-OPS-006 | State SHALL survive restarts | intent-operations.md | BRD-OPS-CON-001 | Covered |
| INT-OPS-007 | State transitions SHALL be traced | intent-operations.md | BRD-OPS-CON-002 | Covered |
| INT-OPS-008 | All actions SHALL be traced | intent-operations.md | BRD-OPS-CON-003 | Covered |
| INT-OPS-010 | Every execution step SHALL be traced | intent-operations.md | BRD-OPS-010 | Covered |
| INT-OPS-011 | Traces SHALL include: timestamp, event type, data | intent-operations.md | BRD-OPS-011 | Covered |
| INT-OPS-012 | Traces SHALL be queryable by run, step, timeframe | intent-operations.md | BRD-OPS-012 | Covered |
| INT-OPS-013 | Large outputs SHALL be stored to files, not inline | intent-operations.md | BRD-OPS-013 | Covered |
| INT-OPS-014 | Observability data SHALL be organized by product/run | intent-operations.md | BRD-OPS-014 | Covered |
| INT-OPS-015 | Dashboards SHALL visualize run status and trends | intent-operations.md | BRD-OPS-015 | Covered |
| INT-OPS-SEM-001 | `semantic_interpretation_started` event SHALL be emitted when phase begins | intent-operations.md | BRD-OPS-SEM-001 | Covered |
| INT-OPS-SEM-002 | Started event SHALL include: run_id, product_id, raw_input_length | intent-operations.md | BRD-OPS-SEM-002 | Covered |
| INT-OPS-SEM-003 | `semantic_interpretation_completed` event SHALL be emitted when phase succeeds | intent-operations.md | BRD-OPS-SEM-003 | Covered |
| INT-OPS-SEM-004 | Completed event SHALL include: envelope_hash, confidence, ambiguity_count, entity_count, next_action | intent-operations.md | BRD-OPS-SEM-004 | Covered |
| INT-OPS-SEM-005 | `semantic_validation_completed` event SHALL be emitted after validation | intent-operations.md | BRD-OPS-SEM-005 | Covered |
| INT-OPS-SEM-006 | Validation event SHALL include: is_valid, missing_fields, violation_count, revised_confidence | intent-operations.md | BRD-OPS-SEM-006 | Covered |
| INT-OPS-SEM-007 | `semantic_stop_issued` event SHALL be emitted on ASK_USER or ABORT | intent-operations.md | BRD-OPS-SEM-007 | Covered |
| INT-OPS-SEM-008 | Stop event SHALL include: next_action, question (if ASK_USER), reason (if ABORT), violations | intent-operations.md | BRD-OPS-SEM-008 | Covered |
| INT-OPS-SEM-009 | `semantic_interpretation_failed` event SHALL be emitted on exception | intent-operations.md | BRD-OPS-SEM-009 | Covered |
| INT-OPS-SEM-010 | Failed event SHALL include: error message | intent-operations.md | BRD-OPS-SEM-010 | Covered |
| INT-OPS-SEM-011 | Events SHALL be structured | intent-operations.md | BRD-OPS-CON-004 | Covered |
| INT-OPS-SEM-012 | Events SHALL include run_id | intent-operations.md | BRD-OPS-CON-005 | Covered |
| INT-OPS-SEM-013 | Events SHALL include timestamps | intent-operations.md | BRD-OPS-CON-006 | Covered |
| PLAT-OPS-001 | Platform SHALL guarantee post-hoc explainability and reproducibility | intent-operations.md | BRD-OPS-060 | Covered |
| PLAT-OPS-002 | Platform SHALL record versions, inputs, and hashes required to reproduce outcomes | intent-operations.md | BRD-OPS-061 | Covered |
| INT-OPS-020 | API responses SHALL complete within 500ms (p95) | intent-operations.md | BRD-OPS-020 | Covered |
| INT-OPS-021 | Run startup SHALL complete within 2 seconds | intent-operations.md | BRD-OPS-021 | Covered |
| INT-OPS-022 | Memory backend operations SHALL complete within 100ms | intent-operations.md | BRD-OPS-022 | Covered |
| INT-OPS-023 | Performance metrics SHALL be measurable | intent-operations.md | BRD-OPS-023 | Covered |
| INT-OPS-030 | Core modules SHALL have ≥80% test coverage | intent-operations.md | BRD-OPS-030 | Covered |
| INT-OPS-031 | Critical paths (run lifecycle) SHALL have 100% coverage | intent-operations.md | BRD-OPS-031 | Covered |
| INT-OPS-032 | All tests SHALL pass before deployment | intent-operations.md | BRD-OPS-032 | Covered |
| INT-OPS-033 | Tests SHALL complete within 10 minutes | intent-operations.md | BRD-OPS-033 | Covered |
| INT-OPS-034 | Contracts (Pydantic models) SHALL have validation tests | intent-operations.md | BRD-OPS-034 | Covered |
| INT-OPS-040 | Failed runs SHALL include error details and stack traces | intent-operations.md | BRD-OPS-040 | Covered |
| INT-OPS-041 | Event timeline SHALL be viewable for any run | intent-operations.md | BRD-OPS-041 | Covered |
| INT-OPS-042 | Input/output data SHALL be inspectable | intent-operations.md | BRD-OPS-042 | Covered |
| INT-OPS-043 | LLM calls and responses SHALL be logged | intent-operations.md | BRD-OPS-043 | Covered |
| INT-OPS-044 | Tool calls and results SHALL be logged | intent-operations.md | BRD-OPS-044 | Covered |
| INT-OPS-ARCH-001 | Architecture test SHALL verify semantic phase is mandatory | intent-operations.md | BRD-OPS-ARCH-001 | Covered |
| INT-OPS-ARCH-002 | Architecture test SHALL verify ASK_USER blocks all step execution | intent-operations.md | BRD-OPS-ARCH-002 | Covered |
| INT-OPS-ARCH-003 | Architecture test SHALL verify ABORT blocks all step execution | intent-operations.md | BRD-OPS-ARCH-003 | Covered |
| INT-OPS-ARCH-004 | Architecture test SHALL verify product adapters do not import core orchestrator | intent-operations.md | BRD-OPS-ARCH-004 | Covered |
| INT-OPS-ARCH-005 | Architecture test SHALL verify core orchestrator does not import products | intent-operations.md | BRD-OPS-ARCH-005 | Covered |
| INT-OPS-ARCH-006 | Architecture tests SHALL live in `tests/architecture/` directory | intent-operations.md | BRD-OPS-ARCH-006 | Covered |
| INT-OPS-ARCH-007 | Architecture tests SHALL run as part of CI pipeline | intent-operations.md | BRD-OPS-ARCH-007 | Covered |
| INT-OPS-ARCH-008 | Architecture tests SHALL pass | intent-operations.md | BRD-OPS-CON-007 | Covered |
| INT-OPS-ARCH-009 | Tests SHALL verify structure, not behavior | intent-operations.md | BRD-OPS-CON-008 | Covered |
| INT-OPS-ARCH-010 | Tests SHALL be automated | intent-operations.md | BRD-OPS-CON-009 | Covered |
| PLAT-INV-001 | MASTER SHALL provide standard reasoning middleware primitives | intent-operations.md | BRD-INV-001 | Covered |
| PLAT-INV-002 | Reasoning SHALL follow a structured, multi-phase pattern | intent-operations.md | BRD-INV-002 | Covered |
| PLAT-INV-003 | Reasoning primitives SHALL be bounded, repeatable, and auditable | intent-operations.md | BRD-INV-003 | Covered |
| PLAT-INV-004 | Reasoning outputs SHALL be first-class artifacts | intent-operations.md | BRD-AUTO-036 | Covered |
| PLAT-INV-005 | MASTER SHALL support explicit critique passes | intent-operations.md | BRD-INV-005 | Covered |
| PLAT-INV-006 | Critique SHALL be advisory only | intent-operations.md | BRD-INV-006 | Covered |
| PLAT-INV-007 | Critique SHALL NEVER execute tools, route flows, override policies, or force decisions | intent-operations.md | BRD-INV-007 | Covered |
| PLAT-INV-008 | Control authority SHALL always remain with the orchestrator and governance layer | intent-operations.md | BRD-INV-008 | Covered |
| PLAT-INV-009 | All semantic interpretations SHALL be treated as hypotheses with confidence | intent-operations.md | BRD-GOV-060 | Covered |
| PLAT-INV-010 | MASTER SHALL represent interpretation as multiple competing candidates | intent-operations.md | BRD-GOV-061 | Covered |
| PLAT-INV-011 | Confidence and ambiguity SHALL propagate into downstream artifacts | intent-operations.md | BRD-GOV-062 | Covered |
| PLAT-INV-012 | When ambiguity exceeds policy thresholds, execution SHALL require HITL or halt | intent-operations.md | BRD-GOV-063 | Covered |
| PLAT-INV-013 | Any gated or consequential decision SHALL be recorded as a decision artifact | intent-operations.md | BRD-GOV-045 | Covered |
| PLAT-INV-014 | Decision artifacts SHALL capture options, evidence, critique input, final choice, justification, confidence | intent-operations.md | BRD-GOV-046 | Covered |
| PLAT-INV-015 | Decision artifacts SHALL be immutable once recorded | intent-operations.md | BRD-GOV-047 | Covered |
| PLAT-INV-016 | MASTER SHALL provide standard iteration patterns for intelligent workflows | intent-operations.md | BRD-INV-016 | Covered |
| PLAT-INV-017 | Iteration SHALL follow a governed cycle | intent-operations.md | BRD-AUTO-044 | Covered |
| PLAT-INV-018 | Iteration SHALL have explicit deterministic stop conditions | intent-operations.md | BRD-AUTO-045 | Covered |
| PLAT-INV-019 | Iterative state SHALL be durable and resumable across restarts | intent-operations.md | BRD-AUTO-046 | Covered |
| PLAT-INV-020 | Agents SHALL be advisory only and MUST NOT control execution, routing, or side effects | intent-operations.md | BRD-INV-020 | Covered |
| PLAT-INV-021 | Only the orchestrator SHALL execute tools, change flow state, pause/resume runs, and escalate to HITL | intent-operations.md | BRD-INV-021 | Covered |
| PLAT-INV-022 | Governance hooks SHALL be non-bypassable at all lifecycle points | intent-operations.md | BRD-GOV-050, BRD-GOV-051, BRD-GOV-CON-004 | Covered |
| PLAT-INV-023 | Products SHALL be isolated and MUST NOT access other products' resources directly | intent-operations.md | BRD-INV-023 | Covered |
| PLAT-INV-024 | MASTER SHALL make reasoning behavior observable | intent-operations.md | BRD-AUTO-034, BRD-OPS-016 | Covered |
| PLAT-INV-025 | Traces SHALL expose options considered, confidence evolution, rejection and escalation reasons | intent-operations.md | BRD-AUTO-035, BRD-OPS-017 | Covered |
| PLAT-INV-026 | Reasoning traces SHALL be queryable for audit, debugging, and improvement analysis | intent-operations.md | BRD-OPS-018 | Covered |
| PLAT-INV-027 | Platform invariants SHALL be executable | intent-operations.md | BRD-INV-027 | Covered |
| PLAT-INV-028 | Products SHALL NOT re-implement semantic interpretation, validation, or confidence logic | intent-operations.md | BRD-INV-028 | Covered |
| PLAT-INV-029 | Architecture tests SHALL verify that products do not duplicate platform semantic or validation logic | intent-operations.md | BRD-INV-029 | Covered |
| PLAT-INV-030 | Invariant violations SHALL block CI/CD pipelines | intent-operations.md | BRD-INV-030 | Covered |

---

## Gap Register (Partial / Missing / Clarification Needed Only)

**No gaps remaining. All intent IDs are mapped to BRD requirements.**

---

## Next BRD Edits Required

**None. Full coverage achieved.**

---

## BRD-COVERAGE GAP COUNT: 0
