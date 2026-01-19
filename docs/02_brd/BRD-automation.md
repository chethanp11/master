# BRD: Intelligent Automation

> **Document ID**: BRD-AUTO  
> **Version**: V1.2  
> **Last Updated**: 2026-01-19  
> **Status**: V1 Release  

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-12 | Initial release |
| 1.1 | 2026-01-13 | Added §3.6 Semantic Interpretation Phase, §3.7 Product Semantic Adapter, §3.8 Stop/Pause Mechanism |
| V1.2 | 2026-01-19 | Standardized requirement tables, removed TSD-level detail, and aligned intent traceability |

---

## 1. Business Context

### Problem Statement
Organizations struggle to scale intelligent automation because:
- Manual processes don't scale with business growth
- Existing automation is brittle and lacks reasoning capability
- AI agents without structure create unpredictable outcomes
- Building agentic systems from scratch is expensive and slow

### Opportunity
A platform that provides structured, composable, and governed AI agents that can:
- Reason through multi-step tasks autonomously
- Adapt to changing conditions with evidence-based decisions
- Integrate with existing tools and systems
- Scale from simple tasks to complex workflows

### Business Value
- **Reduced manual effort**: Automate repetitive knowledge work
- **Faster time-to-value**: Compose existing agents/tools vs. build from scratch
- **Consistent quality**: Evidence-backed decisions reduce errors
- **Scalable intelligence**: Add capabilities without architectural changes

---

## 2. Stakeholders

| Stakeholder | Role | Primary Concern |
|-------------|------|-----------------|
| **Product Builder** | Creates products using agents/tools | Ease of composition, clear contracts |
| **End User** | Interacts with automated workflows | Reliable results, clear explanations |
| **Business Analyst** | Defines automation requirements | Traceability, measurable outcomes |
| **Data Scientist** | Tunes reasoning and intelligence | Evidence quality, model selection |

---

## 3. Business Requirements

> **Source**: [intent-automation.md](../01_vision_and_intent/intent-automation.md)

### 3.1 Agent Capabilities

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-001** | Agents must reason through multi-step tasks with observable decision points | Derived from: INT-AUTO-001 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-002** | Agents must provide evidence supporting their decisions | Derived from: INT-AUTO-002 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-003** | Agents must be composable—one agent can delegate to others | Derived from: INT-AUTO-003 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-004** | Agents must handle failures gracefully with retry or escalation | Derived from: INT-AUTO-004 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-005** | Agent behavior must be deterministic given the same inputs | Derived from: INT-AUTO-005 | P2 | 2026-01-12 | V1.1 | — |

**Constraints (Non-Negotiable from Intent)**:
| Constraint ID | Constraint Statement | Violation Example | Derived from (Intent ID) |
|---------------|----------------------|-------------------|--------------------------|
| **BRD-AUTO-CON-001** | Agents MUST be advisory only and MUST NOT execute tools | Agent calls a tool directly | INT-AUTO-006 |
| **BRD-AUTO-CON-002** | Agents MUST be stateless | Agent stores data in instance variables | INT-AUTO-007 |
| **BRD-AUTO-CON-003** | Agents MUST NOT branch flows | Agent decides execution path | INT-AUTO-008 |
| **BRD-AUTO-CON-004** | Agents MUST NOT modify policies | Agent changes its own permissions | INT-AUTO-009 |

### 3.2 Tool Ecosystem

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-010** | Tools must be discoverable with clear capability descriptions | Derived from: INT-AUTO-010 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-011** | Tools must have typed inputs and outputs | Derived from: INT-AUTO-011 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-012** | Tools must be executable in isolation for testing | Derived from: INT-AUTO-012 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-013** | Tool results must include structured evidence | Derived from: INT-AUTO-013 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-014** | Tool execution must be observable and traceable | Derived from: INT-AUTO-014 | P1 | 2026-01-12 | V1.1 | — |

**Constraints (Non-Negotiable from Intent)**:
| Constraint ID | Constraint Statement | Violation Example | Derived from (Intent ID) |
|---------------|----------------------|-------------------|--------------------------|
| **BRD-AUTO-CON-005** | Tools MUST be deterministic | Tool calls an LLM | INT-AUTO-015 |
| **BRD-AUTO-CON-006** | Tools MUST execute via the platform tool execution mechanism only | Tool runs outside orchestrator | INT-AUTO-016 |
| **BRD-AUTO-CON-007** | Tools MUST declare side effects | Tool modifies external state silently | INT-AUTO-017 |

### 3.3 Intelligence Layer

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-020** | System must select appropriate tools for tasks automatically | Derived from: INT-AUTO-020 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-021** | System must select appropriate agents for subtasks | Derived from: INT-AUTO-021 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-022** | System must identify gaps in information and request clarification | Derived from: INT-AUTO-022 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-023** | System must summarize complex results for human consumption | Derived from: INT-AUTO-023 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-024** | System must explain risks before executing high-impact actions | Derived from: INT-AUTO-024 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-025** | System must interpret user intent before planning/execution | Derived from: INT-AUTO-025 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-026** | System must normalize and validate input before acting | Derived from: INT-AUTO-026 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-027** | System must express interpretation confidence and request clarification when uncertain | Derived from: INT-AUTO-027 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-028** | System must support multiple competing hypotheses with confidence scores as first-class reasoning outputs | Derived from: PLAT-AUTO-001 | P1 | 2026-01-18 | V1.1 | — |
| **BRD-AUTO-029** | System must maintain a persistent sufficiency state tracking known facts, unknowns, assumptions, and blocking gaps | Derived from: PLAT-AUTO-002 | P1 | 2026-01-18 | V1.1 | — |

### 3.4 Reasoning Quality

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-030** | Reasoning must progress through structured phases (interpret→propose→select) | Derived from: INT-AUTO-030 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-031** | Proposals must be evaluated by critic before execution | Derived from: INT-AUTO-031 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-032** | Context must be enriched with relevant knowledge before reasoning | Derived from: INT-AUTO-032 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-033** | Reasoning failures must trigger appropriate escalation | Derived from: INT-AUTO-033 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-034** | Reasoning behavior must be observable, not just execution steps | Derived from: PLAT-INV-024 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-035** | Traces must expose options considered, confidence evolution, rejection reasons | Derived from: PLAT-INV-025 | P1 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-036** | Reasoning outputs must be first-class artifacts, not ephemeral responses | Derived from: PLAT-INV-004 | P1 | 2026-01-13 | V1.1 | — |

### 3.5 Workflow Execution

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-040** | Workflows must support sequential, parallel, and conditional steps | Derived from: INT-AUTO-040 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-041** | Workflows must support iteration over collections | Derived from: INT-AUTO-041 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-042** | Workflow steps must be independently restartable | Derived from: INT-AUTO-042 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-043** | Workflows must support nested sub-workflows | Derived from: INT-AUTO-043 | P2 | 2026-01-12 | V1.1 | — |
| **BRD-AUTO-044** | Iteration must follow governed cycle (propose→gate→execute→evaluate) | Derived from: PLAT-INV-017 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-045** | Iteration must have explicit deterministic stop conditions | Derived from: PLAT-INV-018 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-046** | Iterative state must be durable and resumable across restarts | Derived from: PLAT-INV-019 | P1 | 2026-01-13 | V1.1 | — |

### 3.6 Semantic Interpretation Phase (Added: 2026-01-13)

> **Source**: [intent-automation.md](../01_vision_and_intent/intent-automation.md)

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-SEM-001** | Every orchestrator run must execute a semantic interpretation phase before step execution | Derived from: INT-AUTO-SEM-001 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-SEM-002** | Semantic phase must interpret user intent and produce a structured envelope | Derived from: INT-AUTO-SEM-002 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-SEM-003** | Semantic envelope must capture interpreted intent, entities, constraints, confidence, and ambiguities | Derived from: INT-AUTO-SEM-003 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-SEM-004** | Semantic phase must determine next action: CONTINUE, ASK_USER, ABORT, or NEEDS_APPROVAL | Derived from: INT-AUTO-SEM-004 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-SEM-005** | Semantic envelope must be attached to run record for traceability | Derived from: INT-AUTO-SEM-005 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-SEM-006** | Core must provide domain-agnostic normalization rules (whitespace, deduplication, ordering) | Derived from: INT-AUTO-SEM-006 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-SEM-007** | Normalization must be deterministic and reproducible | Derived from: INT-AUTO-SEM-007 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-SEM-008** | Entities must be deduplicated (same type+value → single entity with highest confidence) | Derived from: INT-AUTO-SEM-008 | P1 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-SEM-009** | Constraints must be merged deterministically with stable key ordering | Derived from: INT-AUTO-SEM-009 | P1 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-SEM-010** | Type coercion must be supported for declared types | Derived from: INT-AUTO-SEM-010 | P1 | 2026-01-13 | V1.1 | — |

**Constraints (Non-Negotiable from Intent)**:
| Constraint ID | Constraint Statement | Violation Example | Derived from (Intent ID) |
|---------------|----------------------|-------------------|--------------------------|
| **BRD-AUTO-CON-008** | Semantic interpretation MUST be mandatory before step execution | Steps execute without interpretation | INT-AUTO-SEM-011 |
| **BRD-AUTO-CON-009** | Normalization MUST remain domain-agnostic | Core normalization includes business rules | INT-AUTO-SEM-006 |
| **BRD-AUTO-CON-010** | Semantic envelopes MUST be immutable once created | Envelope modified after semantic phase | Intent ID missing |
| **BRD-AUTO-CON-011** | Confidence MUST be bounded within 0.0–1.0 | Confidence value outside range | INT-AUTO-SEM-004 |

### 3.7 Product Semantic Adapter (Added: 2026-01-13)

> **Source**: [intent-automation.md](../01_vision_and_intent/intent-automation.md)

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-ADAPT-001** | Products must be able to provide custom semantic interpretation via adapter interface | Derived from: INT-AUTO-ADAPT-001 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-ADAPT-002** | Adapter interface must support interpretation of semantic context into a structured envelope | Derived from: INT-AUTO-ADAPT-002 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-ADAPT-003** | Adapter interface must support validation of semantic envelopes against product rules | Derived from: INT-AUTO-ADAPT-003 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-ADAPT-004** | Default adapter must be provided for products without custom implementation | Derived from: INT-AUTO-ADAPT-004 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-ADAPT-005** | Default adapter must return passthrough envelope with confidence=1.0 | Derived from: INT-AUTO-ADAPT-005 | P1 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-ADAPT-006** | Adapters must be discoverable via a standard product semantic adapter location | Derived from: INT-AUTO-ADAPT-006 | P1 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-ADAPT-007** | Adapters must be resolved via platform routing to preserve isolation | Derived from: INT-AUTO-ADAPT-007 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-ADAPT-008** | Product adapters must NOT depend on core orchestrator internals | Derived from: INT-AUTO-ADAPT-008 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-ADAPT-009** | Core orchestrator must NOT depend on product adapter code | Derived from: INT-AUTO-ADAPT-009 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-ADAPT-010** | Adapter execution must have timeout with fallback to default | Derived from: INT-AUTO-ADAPT-010 | P1 | 2026-01-13 | V1.1 | — |

**Constraints (Non-Negotiable from Intent)**:
| Constraint ID | Constraint Statement | Violation Example | Derived from (Intent ID) |
|---------------|----------------------|-------------------|--------------------------|
| **BRD-AUTO-CON-012** | Adapters MUST be pure functions | Adapter calls external API | INT-AUTO-ADAPT-011 |
| **BRD-AUTO-CON-013** | Adapters MUST NOT execute tools | Adapter triggers tool execution | INT-AUTO-ADAPT-012 |
| **BRD-AUTO-CON-014** | Adapters MUST NOT access other products | Adapter reads another product's config | INT-AUTO-ADAPT-013 |
| **BRD-AUTO-CON-015** | Isolation MUST be bidirectional between core and products | Core imports product, or product imports core orchestrator | INT-AUTO-ADAPT-014 |

### 3.8 Stop/Pause Mechanism (Added: 2026-01-13)

> **Source**: [intent-automation.md](../01_vision_and_intent/intent-automation.md)

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-STOP-001** | ASK_USER must pause the run and return a structured clarification response | Derived from: INT-AUTO-STOP-001 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-STOP-002** | Clarification response must include the question, ambiguity context, original confidence, and relevant context | Derived from: INT-AUTO-STOP-002 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-STOP-003** | Run status must reflect a paused state awaiting user clarification | Derived from: INT-AUTO-STOP-003 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-STOP-004** | ABORT must fail the run with structured error response | Derived from: INT-AUTO-STOP-004 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-STOP-005** | Abort response must include reason, violations, and ambiguity context | Derived from: INT-AUTO-STOP-005 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-STOP-006** | Run status must reflect failure after ABORT | Derived from: INT-AUTO-STOP-006 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-STOP-007** | ASK_USER and ABORT must prevent any step execution | Derived from: INT-AUTO-STOP-007 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-STOP-008** | Stop decisions must emit a trace event for auditability | Derived from: INT-AUTO-STOP-008 | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-STOP-009** | Paused runs must be resumable with user-provided clarification | Derived from: INT-AUTO-STOP-009 | P0 | 2026-01-13 | V1.1 | — |

**Constraints (Non-Negotiable from Intent)**:
| Constraint ID | Constraint Statement | Violation Example | Derived from (Intent ID) |
|---------------|----------------------|-------------------|--------------------------|
| **BRD-AUTO-CON-016** | Stop actions MUST block all step execution | Step executes after ASK_USER | INT-AUTO-STOP-010 |
| **BRD-AUTO-CON-017** | Abort MUST be terminal | Run continues after ABORT | INT-AUTO-STOP-011 |
| **BRD-AUTO-CON-018** | Clarification responses MUST be structured | Free-form error message only | INT-AUTO-STOP-012 |

### 3.9 Orchestrator-Controlled Reasoning (Added: 2026-01-18)

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-047** | Platform must provide a central, reusable reasoning lifecycle (interpret → propose → critique → recommend) that is orchestrator-controlled, bounded, and non-autonomous | Derived from: PLAT-ORCH-001 | P0 | 2026-01-18 | V1.1 | — |
| **BRD-AUTO-048** | Orchestrator must support bounded reasoning iteration with deterministic stop conditions based on sufficiency, budget, iteration limits, or human intervention | Derived from: PLAT-ORCH-002 | P0 | 2026-01-18 | V1.1 | — |

### 3.10 Confidence and Critique Control (Added: 2026-01-18)

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-049** | Platform must track, update, and propagate confidence as a core runtime signal across reasoning stages, steps, and decision gates | Derived from: PLAT-CTRL-001 | P0 | 2026-01-18 | V1.1 | — |
| **BRD-AUTO-050** | Platform must enforce a mandatory advisory critique phase before finalizing any decision or output, with the ability to downgrade confidence or block progression | Derived from: PLAT-CTRL-002 | P0 | 2026-01-18 | V1.1 | — |

### 3.11 Execution Gatekeeping (Added: 2026-01-18)

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-051** | Platform must construct and freeze a ContextPack before planning or execution, consolidating data availability, evidence, constraints, and quality limitations | Derived from: PLAT-EXEC-001 | P0 | 2026-01-18 | V1.1 | — |
| **BRD-AUTO-052** | Platform must define and enforce explicit terminal outcomes (SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT) with required explanations and artifacts | Derived from: PLAT-EXEC-002 | P0 | 2026-01-18 | V1.1 | — |

---

## 7. Cross-Cutting Requirements

### 7.1 Intent-to-BRD Traceability

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-LIFE-001** | Every automation intent point must map to at least one BRD requirement | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-LIFE-002** | BRD requirements must reference source intent | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-LIFE-003** | Unmapped intent points MUST be treated as coverage gaps requiring review | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |

### 7.2 Product Factory Model

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-AUTO-FAC-001** | Products must be shippable in < 1 day using framework automation primitives | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-FAC-002** | Products must focus on domain logic; automation infrastructure provided by framework | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-FAC-003** | Products MUST NOT re-implement agent/tool/reasoning services | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-FAC-004** | Design-time intelligence MUST be preferred over runtime autonomy | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-AUTO-FAC-005** | Runtime AI MUST be advisory only and MUST NOT be autonomous | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |

---

## 8. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| LLM Provider | External | OpenAI, Anthropic, etc. |
| Model Routing Service | Internal | Routes model requests |
| Governance Layer | Internal | Policy enforcement on agent actions |

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM hallucination | Wrong decisions | Evidence requirements, critic evaluation |
| Agent loops | Resource exhaustion | Budget limits, loop guards |
| Tool failures | Workflow interruption | Retry policies, graceful degradation |
| Unpredictable reasoning | Compliance issues | Structured phases, audit trails |

---

## 10. Appendix: Technical Details (Removed from BRD)

### Semantic Interpretation Contracts
| Contract | Purpose | Fields |
|----------|---------|--------|
| `SemanticEnvelope` | Structured interpretation result | raw_input, normalized_input, product_id, intent_type, entities, constraints, confidence, ambiguities, proposed_next_action |
| `NextAction` enum | Flow control decision | CONTINUE, ASK_USER, ABORT, NEEDS_APPROVAL |
| `ValidationResult` | Domain validation outcome | is_valid, missing_fields, violations, revised_confidence, clarifying_question |
| `SemanticContext` | Input to adapters | raw_input, payload, product_config |
| `Entity` | Extracted entity | type, value, confidence, start_pos, end_pos |

### Product Semantic Adapter Technical Notes
- Adapter interface methods: `interpret(context) → SemanticEnvelope`, `validate(envelope, context) → ValidationResult`.
- Discovery path: `products/<name>/semantic.py`.
- Routing mechanism: `ProductRouter`.
- Isolation boundaries: product adapters do not import `core/orchestrator/*`; core orchestrator does not import `products/*`.

### Stop/Pause Trace Event
- Event name: `semantic_stop_issued`.

---

## Related Documents

- [Vision.md](../01_vision_and_intent/Vision.md) — Platform vision and principles
- [intent-automation.md](../01_vision_and_intent/intent-automation.md) — Source intent
- [BRD-governance.md](BRD-governance.md) — Human oversight for high-risk actions
