# BRD: Intelligent Automation

> **Document ID**: BRD-AUTO  
> **Version**: V1.3
> **Last Updated**: 2026-01-25 

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-12 | Initial release |
| 1.1 | 2026-01-13 | Added §3.6 Semantic Interpretation Phase, §3.7 Product Semantic Adapter, §3.8 Stop/Pause Mechanism |
| V1.3 | 2026-01-25 | Added §3.12 Tool & Agent Discovery, §3.13 Minimum Reasoning Contract, §3.14 Intent Sufficiency Gate; closed coverage gaps for INT-AUTO-SEM-012/013/014 |

---

## Governing Architecture Invariants

The following architecture invariants from [Developer Intent](../00_developer_intent/intent.md) govern this BRD:

| INV | Invariant | Implication for Automation |
|-----|-----------|---------------------------|
| **INV-1** | Reasoning as a Framework Primitive | Agents use standard reasoning middleware, not custom orchestration |
| **INV-2** | Critique Is Mandatory, Bounded, Non-Controlling | Critique is advisory; control stays with orchestrator |
| **INV-5** | Iteration Is Orchestrator-Controlled | Investigation allowed; autonomy is not |
| **INV-7** | Reasoning Observability | "Why" matters as much as "what happened" |

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

> **Source**: [INT-AUTO](../00_developer_intent/intent.md#1-intelligent-automation-int-auto)

### 3.1 Agent Capabilities

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-AUTO-001** | Agents must reason through multi-step tasks with observable decision points | P0 | INT-AUTO-001 | 2026-01-12 |
| **BRD-AUTO-002** | Agents must provide evidence supporting their decisions | P0 | INT-AUTO-002 | 2026-01-12 |
| **BRD-AUTO-003** | Agents must be composable—one agent can delegate to others | P1 | INT-AUTO-003 | 2026-01-12 |
| **BRD-AUTO-004** | Agents must handle failures gracefully with retry or escalation | P1 | INT-AUTO-004 | 2026-01-12 |
| **BRD-AUTO-005** | Agent behavior must be deterministic given the same inputs | P2 | INT-AUTO-005 | 2026-01-12 |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Agents advise, never execute | Agent calls a tool directly |
| Agents are stateless | Agent stores data in instance variables |
| Agents cannot branch flows | Agent decides execution path |
| Agents cannot modify policies | Agent changes its own permissions |

### 3.2 Tool Ecosystem

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-AUTO-010** | Tools must be discoverable with clear capability descriptions | P0 | INT-AUTO-010 | 2026-01-12 |
| **BRD-AUTO-011** | Tools must have typed inputs and outputs | P0 | INT-AUTO-011 | 2026-01-12 |
| **BRD-AUTO-012** | Tools must be executable in isolation for testing | P0 | INT-AUTO-012 | 2026-01-12 |
| **BRD-AUTO-013** | Tool results must include structured evidence | P1 | INT-AUTO-013 | 2026-01-12 |
| **BRD-AUTO-014** | Tool execution must be observable and traceable | P1 | INT-AUTO-014 | 2026-01-12 |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Tools are deterministic | Tool calls an LLM |
| Tools execute via ToolExecutor only | Tool runs outside orchestrator |
| Tools declare side effects | Tool modifies external state silently |

### 3.3 Intelligence Layer

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-AUTO-020** | System must select appropriate tools for tasks automatically | P0 | INT-AUTO-020 | 2026-01-12 |
| **BRD-AUTO-021** | System must select appropriate agents for subtasks | P0 | INT-AUTO-021 | 2026-01-12 |
| **BRD-AUTO-022** | System must identify gaps in information and request clarification | P1 | INT-AUTO-022 | 2026-01-12 |
| **BRD-AUTO-023** | System must summarize complex results for human consumption | P1 | INT-AUTO-023 | 2026-01-12 |
| **BRD-AUTO-024** | System must explain risks before executing high-impact actions | P1 | INT-AUTO-024 | 2026-01-12 |
| **BRD-AUTO-025** | System must interpret user intent before planning/execution | P0 | INT-AUTO-025 | 2026-01-12 |
| **BRD-AUTO-026** | System must normalize and validate input before acting | P0 | INT-AUTO-026 | 2026-01-12 |
| **BRD-AUTO-027** | System must express interpretation confidence and request clarification when uncertain | P1 | INT-AUTO-027 | 2026-01-12 |
| **BRD-AUTO-028** | System must support multiple competing hypotheses with confidence scores as first-class reasoning outputs | P1 | PLAT-AUTO-001 | 2026-01-18 |
| **BRD-AUTO-029** | System must maintain a persistent sufficiency state tracking known facts, unknowns, assumptions, and blocking gaps | P1 | PLAT-AUTO-002 | 2026-01-18 |

### 3.4 Reasoning Quality

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-AUTO-030** | Reasoning must progress through structured phases (interpret→propose→select) | P0 | INT-AUTO-030, INV-1 | 2026-01-12 |
| **BRD-AUTO-031** | Proposals must be evaluated by critic before execution | P1 | INT-AUTO-031, INV-2 | 2026-01-12 |
| **BRD-AUTO-032** | Context must be enriched with relevant knowledge before reasoning | P1 | INT-AUTO-032 | 2026-01-12 |
| **BRD-AUTO-033** | Reasoning failures must trigger appropriate escalation | P1 | INT-AUTO-033 | 2026-01-12 |
| **BRD-AUTO-034** | Reasoning behavior must be observable, not just execution steps | P0 | INV-7 | Added: 2026-01-13 |
| **BRD-AUTO-035** | Traces must expose options considered, confidence evolution, rejection reasons | P1 | INV-7 | Added: 2026-01-13 |
| **BRD-AUTO-036** | Reasoning outputs must be first-class artifacts, not ephemeral responses | P1 | INV-1 | Added: 2026-01-13 |

### 3.5 Workflow Execution

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-AUTO-040** | Workflows must support sequential, parallel, and conditional steps | P0 | INT-AUTO-040 | 2026-01-12 |
| **BRD-AUTO-041** | Workflows must support iteration over collections | P0 | INT-AUTO-041 | 2026-01-12 |
| **BRD-AUTO-042** | Workflow steps must be independently restartable | P1 | INT-AUTO-042 | 2026-01-12 |
| **BRD-AUTO-043** | Workflows must support nested sub-workflows | P2 | INT-AUTO-043 | 2026-01-12 |
| **BRD-AUTO-044** | Iteration must follow governed cycle (propose→gate→execute→evaluate) | P0 | INV-5 | 1.0 | Added: 2026-01-13 |
| **BRD-AUTO-045** | Iteration must have explicit deterministic stop conditions | P0 | INV-5 | 1.0 | Added: 2026-01-13 |
| **BRD-AUTO-046** | Iterative state must be durable and resumable across restarts | P1 | INV-5 | 1.0 | Added: 2026-01-13 |

### 3.6 Semantic Interpretation Phase (Added: 2026-01-13)

> **Source**: [INT-AUTO-SEM](../00_developer_intent/intent.md#11-semantic-interpretation-phase-added-2026-01-13)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-AUTO-SEM-001** | Every orchestrator run must execute a semantic interpretation phase before step execution | P0 | INT-AUTO-SEM-001 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-002** | Semantic phase must interpret user intent and produce a structured envelope | P0 | INT-AUTO-SEM-002 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-003** | Semantic envelope must capture: intent_type, entities, constraints, confidence, ambiguities | P0 | INT-AUTO-SEM-003 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-004** | Semantic phase must determine next action: CONTINUE, ASK_USER, ABORT, or NEEDS_APPROVAL | P0 | INT-AUTO-SEM-004 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-005** | Semantic envelope must be attached to run record for traceability | P0 | INT-AUTO-SEM-005 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-006** | Core must provide domain-agnostic normalization rules (whitespace, deduplication, ordering) | P0 | INT-AUTO-SEM-006 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-007** | Normalization must be deterministic and reproducible | P0 | INT-AUTO-SEM-007 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-008** | Entities must be deduplicated (same type+value → single entity with highest confidence) | P1 | INT-AUTO-SEM-008 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-009** | Constraints must be merged deterministically with stable key ordering | P1 | INT-AUTO-SEM-009 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-010** | Type coercion must be supported for schema-declared types (string→int, string→date) | P1 | INT-AUTO-SEM-010 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-SEM-011** | Semantic envelope SHALL be the only handoff to planning phase — raw text input MUST NOT proceed directly to planning | P0 | INT-AUTO-SEM-012 | V1.3 | Added: 2026-01-25 |
| **BRD-AUTO-SEM-012** | Confidence gates SHALL control execution — low-confidence interpretations MUST NOT proceed without intervention | P0 | INT-AUTO-SEM-013 | V1.3 | Added: 2026-01-25 |
| **BRD-AUTO-SEM-013** | Ambiguities SHALL be explicit — all detected ambiguities MUST be surfaced in the semantic envelope as structured data | P0 | INT-AUTO-SEM-014 | V1.3 | Added: 2026-01-25 |

**Contracts (New: 2026-01-13)**:
| Contract | Purpose | Fields |
|----------|---------|--------|
| `SemanticEnvelope` | Structured interpretation result | raw_input, normalized_input, product_id, intent_type, entities, constraints, confidence, ambiguities, proposed_next_action |
| `NextAction` enum | Flow control decision | CONTINUE, ASK_USER, ABORT, NEEDS_APPROVAL |
| `ValidationResult` | Domain validation outcome | is_valid, missing_fields, violations, revised_confidence, clarifying_question |
| `SemanticContext` | Input to adapters | raw_input, payload, product_config |
| `Entity` | Extracted entity | type, value, confidence, start_pos, end_pos |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Semantic phase is mandatory | Steps execute without interpretation |
| Normalization is domain-agnostic | Core normalization includes business rules |
| Envelope is immutable once created | Envelope modified after semantic phase |
| Confidence is bounded 0.0-1.0 | Confidence value outside range |

### 3.7 Product Semantic Adapter (Added: 2026-01-13)

> **Source**: [INT-AUTO-ADAPT](../00_developer_intent/intent.md#12-product-semantic-adapter-added-2026-01-13)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-AUTO-ADAPT-001** | Products must be able to provide custom semantic interpretation via adapter interface | P0 | INT-AUTO-ADAPT-001 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-ADAPT-002** | Adapter interface must define `interpret(context) → SemanticEnvelope` method | P0 | INT-AUTO-ADAPT-002 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-ADAPT-003** | Adapter interface must define `validate(envelope, context) → ValidationResult` method | P0 | INT-AUTO-ADAPT-003 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-ADAPT-004** | Default adapter must be provided for products without custom implementation | P0 | INT-AUTO-ADAPT-004 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-ADAPT-005** | Default adapter must return passthrough envelope with confidence=1.0 | P1 | INT-AUTO-ADAPT-005 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-ADAPT-006** | Adapters must be discovered from `products/<name>/semantic.py` | P1 | INT-AUTO-ADAPT-006 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-ADAPT-007** | Adapters must be resolved via ProductRouter, not direct import | P0 | INT-AUTO-ADAPT-007 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-ADAPT-008** | Product adapters must NOT import from `core/orchestrator/*` | P0 | INT-AUTO-ADAPT-008 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-ADAPT-009** | Core orchestrator must NOT import from `products/*` | P0 | INT-AUTO-ADAPT-009 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-ADAPT-010** | Adapter execution must have timeout with fallback to default | P1 | INT-AUTO-ADAPT-010 | 1.1 | Added: 2026-01-13 |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Adapters are pure functions | Adapter calls external API |
| Adapters don't execute tools | Adapter triggers tool execution |
| Adapters don't access other products | Adapter reads another product's config |
| Isolation is bidirectional | Core imports product, or product imports core orchestrator |

### 3.8 Stop/Pause Mechanism (Added: 2026-01-13)

> **Source**: [INT-AUTO-STOP](../00_developer_intent/intent.md#13-stoppause-mechanism-added-2026-01-13)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-AUTO-STOP-001** | ASK_USER must pause the run and return a structured clarification response | P0 | INT-AUTO-STOP-001 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-STOP-002** | Clarification response must include: question, ambiguities, original confidence, context | P0 | INT-AUTO-STOP-002 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-STOP-003** | Run status must be PAUSED_WAITING_FOR_USER during clarification | P0 | INT-AUTO-STOP-003 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-STOP-004** | ABORT must fail the run with structured error response | P0 | INT-AUTO-STOP-004 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-STOP-005** | Abort error must include: error_code=semantic_abort, reason, violations, ambiguities | P0 | INT-AUTO-STOP-005 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-STOP-006** | Run status must be FAILED after ABORT | P0 | INT-AUTO-STOP-006 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-STOP-007** | ASK_USER and ABORT must prevent any step execution | P0 | INT-AUTO-STOP-007 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-STOP-008** | Trace event `semantic_stop_issued` must be emitted on stop | P0 | INT-AUTO-STOP-008 | 1.1 | Added: 2026-01-13 |
| **BRD-AUTO-STOP-009** | Paused runs must be resumable with user-provided clarification | P0 | INT-AUTO-STOP-009 | 1.1 | Added: 2026-01-13 |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Stop blocks all steps | Step executes after ASK_USER |
| Abort is terminal | Run continues after ABORT |
| Clarification is structured | Free-form error message only |

### 3.9 Orchestrator-Controlled Reasoning (Added: 2026-01-18)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-AUTO-047** | Platform must provide a central, reusable reasoning lifecycle (interpret → propose → critique → recommend) that is orchestrator-controlled, bounded, and non-autonomous | P0 | PLAT-ORCH-001 | 1.2 | Added: 2026-01-18 |
| **BRD-AUTO-048** | Orchestrator must support bounded reasoning iteration with deterministic stop conditions based on sufficiency, budget, iteration limits, or human intervention | P0 | PLAT-ORCH-002 | 1.2 | Added: 2026-01-18 |

### 3.10 Confidence and Critique Control (Added: 2026-01-18)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-AUTO-049** | Platform must track, update, and propagate confidence as a core runtime signal across reasoning stages, steps, and decision gates | P0 | PLAT-CTRL-001 | 1.2 | Added: 2026-01-18 |
| **BRD-AUTO-050** | Platform must enforce a mandatory advisory critique phase before finalizing any decision or output, with the ability to downgrade confidence or block progression | P0 | PLAT-CTRL-002 | 1.2 | Added: 2026-01-18 |

### 3.11 Execution Gatekeeping (Added: 2026-01-18)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-AUTO-051** | Platform must construct and freeze a ContextPack before planning or execution, consolidating data availability, evidence, constraints, and quality limitations | P0 | PLAT-EXEC-001 | 1.2 | Added: 2026-01-18 |
| **BRD-AUTO-052** | Platform must define and enforce explicit terminal outcomes (SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT) with required explanations and artifacts | P0 | PLAT-EXEC-002 | 1.2 | Added: 2026-01-18 |

### 3.12 Tool & Agent Discovery (Added: 2026-01-25)

> **Source**: [PLAT-AUTO-DISC](../01_vision_and_intent/intent-automation.md#plat-auto-disc--tool--agent-discovery)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-AUTO-DISC-001** | Every tool and agent SHALL declare capabilities explicitly via structured descriptors — no implicit capability assumptions are permitted | P0 | INT-AUTO-DISC-001 | V1.3 | Added: 2026-01-25 |
| **BRD-AUTO-DISC-002** | Platform SHALL own and maintain a centralized registry for all tools and agents — this registry is the single source of truth for discovery | P0 | INT-AUTO-DISC-002 | V1.3 | Added: 2026-01-25 |
| **BRD-AUTO-DISC-003** | Discovery SHALL be intent-filtered — tools and agents SHALL be discoverable only when relevant to the current intent context | P0 | INT-AUTO-DISC-003 | V1.3 | Added: 2026-01-25 |
| **BRD-AUTO-DISC-004** | Platform SHALL perform explicit eligibility checks before tool or agent execution — policy, budget, and capability requirements SHALL be validated prior to invocation | P0 | INT-AUTO-DISC-004 | V1.3 | Added: 2026-01-25 |
| **BRD-AUTO-DISC-005** | Discovery and selection SHALL be separate concerns — discovery returns candidates, selection applies ranking and policy | P1 | INT-AUTO-DISC-005 | V1.3 | Added: 2026-01-25 |
| **BRD-AUTO-DISC-006** | Platform SHALL provide first-class support for tool and agent extension — products SHALL be able to register additional capabilities via standard interfaces | P1 | INT-AUTO-DISC-006 | V1.3 | Added: 2026-01-25 |
| **BRD-AUTO-DISC-007** | Tool and agent exposure SHALL be governed by product — products SHALL control which of their capabilities are discoverable by other products | P1 | INT-AUTO-DISC-007 | V1.3 | Added: 2026-01-25 |
| **BRD-AUTO-DISC-008** | Tool and agent discovery SHALL be deterministic — same intent context and product configuration SHALL yield same discovery results | P0 | INT-AUTO-DISC-008 | V1.3 | Added: 2026-01-25 |

### 3.13 Minimum Reasoning Contract (Added: 2026-01-25)

> **Source**: [PLAT-AUTO-REASON](../01_vision_and_intent/intent-automation.md#plat-auto-reason--reasoning-quality)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-AUTO-053** | Platform SHALL define and enforce a Minimum Reasoning Contract for all products — products SHALL NOT bypass or reduce reasoning phases below platform-mandated minimums | P0 | INT-AUTO-034 | V1.3 | Added: 2026-01-25 |

### 3.14 Intent Sufficiency Gate (Added: 2026-01-25)

> **Source**: [PLAT-ORCH](../01_vision_and_intent/intent-automation.md#plat-orch--orchestrator-controlled-reasoning)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-AUTO-054** | Intent sufficiency SHALL be a first-class orchestration responsibility — orchestrator SHALL track, evaluate, and gate execution based on sufficiency state | P0 | PLAT-ORCH-003 | V1.3 | Added: 2026-01-25 |

---

## 4. User Stories

### Product Builder Stories
- **US-AUTO-001**: As a product builder, I want to compose agents from existing components so that I can ship products faster.
- **US-AUTO-002**: As a product builder, I want to define workflows in YAML so that non-engineers can understand the automation logic.
- **US-AUTO-003**: As a product builder, I want to test agents in isolation so that I can validate behavior before deployment.

### End User Stories
- **US-AUTO-010**: As an end user, I want to understand why the system made a decision so that I can trust the results.
- **US-AUTO-011**: As an end user, I want the system to ask clarifying questions so that I get accurate results.
- **US-AUTO-012**: As an end user, I want to see progress through multi-step tasks so that I know the system is working.

### Business Analyst Stories
- **US-AUTO-020**: As a business analyst, I want to trace every decision back to evidence so that I can audit automation quality.
- **US-AUTO-021**: As a business analyst, I want to measure agent success rates so that I can identify improvement opportunities.

---

## 5. Acceptance Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Agent task completion | Tasks completed without human intervention | > 85% |
| Evidence coverage | Decisions with supporting evidence | 100% |
| Tool discovery accuracy | Correct tool selected for task | > 90% |
| Workflow restart success | Successful restart after failure | > 95% |
| Reasoning phase completion | All phases complete without error | > 95% |

---

## 6. Techspec Mapping

| BRD ID | Description | Derived Techspec | Ver |
|--------|-------------|------------------|-----|
| BRD-AUTO-001 | Multi-step reasoning | AGT-BASE-001...005, INT-RL-001...010 | 1.0 |
| BRD-AUTO-002 | Evidence-backed decisions | AGT-BASE-020...022, TOOL-EXEC-010...012 | 1.0 |
| BRD-AUTO-003 | Agent composition | AGT-BASE-010, REG-001...005 | 1.0 |
| BRD-AUTO-010 | Tool discoverability | TOOL-BASE-010...015, TOOL-DESC-001...005 | 1.0 |
| BRD-AUTO-011 | Typed tool interfaces | TOOL-BASE-001...005 | 1.0 |
| BRD-AUTO-020 | Automatic tool selection | INT-ADV-001...005 (ToolSelector) | 1.0 |
| BRD-AUTO-021 | Automatic agent selection | INT-ADV-010...015 (AgentSelector) | 1.0 |
| BRD-AUTO-022 | Gap identification | INT-ADV-020...025 (GapFinder) | 1.0 |
| BRD-AUTO-025 | Semantic interpretation | ORC-SEM-*, INT-SEM-* | 1.0 |
| BRD-AUTO-026 | Input normalization | ORC-SEM-030...040 | 1.0 |
| BRD-AUTO-027 | Confidence propagation | INT-SEM-CONF-* | 1.0 |
| BRD-AUTO-030 | Structured reasoning | INT-RL-010...030 | 1.0 |
| BRD-AUTO-031 | Critic evaluation | INT-CRIT-001...015 | 1.0 |
| BRD-AUTO-034 | Reasoning observability | MEM-TRACE-REASON-* | 1.0 |
| BRD-AUTO-035 | Reasoning traces | MEM-TRACE-020...025 | 1.0 |
| BRD-AUTO-036 | Reasoning artifacts | INT-RL-ARTIFACT-* | 1.0 |
| BRD-AUTO-040 | Workflow patterns | ORC-STEP-001...010, ORC-BRANCH-*, ORC-LOOP-* | 1.0 |
| BRD-AUTO-044 | Governed iteration | ORC-LOOP-GOV-* | 1.0 |
| BRD-AUTO-045 | Stop conditions | ORC-LOOP-STOP-* | 1.0 |
| BRD-AUTO-046 | Durable iteration | ORC-LOOP-STATE-* | 1.0 |
| BRD-AUTO-SEM-* | Semantic interpretation phase | ORC-SEM-001...010, SEM-ENV-* | 1.1 |
| BRD-AUTO-ADAPT-* | Product semantic adapter | PROD-SEM-ADAPT-*, ORC-SEM-ADAPTER-* | 1.1 |
| BRD-AUTO-STOP-* | Stop/pause mechanism | ORC-SEM-STOP-*, ORC-PAUSE-SEM-* | 1.1 |
| BRD-AUTO-DISC-* | Tool & agent discovery | TOOL-DISC-*, AGT-DISC-*, REG-DISC-* | V1.3 |
| BRD-AUTO-053 | Minimum reasoning contract | ORC-REASON-CONTRACT-* | V1.3 |
| BRD-AUTO-054 | Intent sufficiency gate | ORC-SUFF-GATE-* | V1.3 |

---

## 7. Cross-Cutting Requirements

> **Source**: [INT-LIFECYCLE](../00_developer_intent/intent.md#5-developer-intent-lifecycle-int-lifecycle), [INT-FACTORY](../00_developer_intent/intent.md#6-product-factory-model-int-factory)

### 7.1 Intent-to-BRD Traceability

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-AUTO-LIFE-001** | Every automation intent point must map to at least one BRD requirement | P0 | INT-LIFECYCLE-020 | Added: 2026-01-13 |
| **BRD-AUTO-LIFE-002** | BRD requirements must reference source intent | P0 | INT-LIFECYCLE-021 | Added: 2026-01-13 |
| **BRD-AUTO-LIFE-003** | Unmapped intent points are coverage gaps requiring review | P1 | INT-LIFECYCLE-022 | Added: 2026-01-13 |

### 7.2 Product Factory Model

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-AUTO-FAC-001** | Products must be shippable in < 1 day using framework automation primitives | P1 | INT-FACTORY-003 | Added: 2026-01-13 |
| **BRD-AUTO-FAC-002** | Products must focus on domain logic; automation infrastructure provided by framework | P0 | INT-FACTORY-004 | Added: 2026-01-13 |
| **BRD-AUTO-FAC-003** | Products are forbidden from re-implementing agent/tool/reasoning services | P0 | INT-FACTORY-011 | Added: 2026-01-13 |
| **BRD-AUTO-FAC-004** | Design-time intelligence is preferred over runtime autonomy | P0 | INT-FACTORY-030, INV-8 | Added: 2026-01-13 |
| **BRD-AUTO-FAC-005** | Runtime AI is advisory only, never autonomous | P0 | INT-FACTORY-035 | Added: 2026-01-13 |

---

## 8. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| LLM Provider | External | OpenAI, Anthropic, etc. |
| Model Router | Internal | `core/models/router.py` |
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

## 10. Framework Laws Governing Automation

> **Source**: [Framework Laws](../00_developer_intent/intent.md#7-framework-laws)

| Law | Implication | Ver |
|-----|-------------|-----|
| Agents never execute tools | All tool execution via ToolExecutor only | 1.0 |
| Tools never call models | Tools are deterministic, no LLM calls | 1.0 |
| Governance hooks are mandatory | Every agent action passes through governance | 1.0 |
| Flows are explicit | No implicit execution paths; YAML-defined | 1.0 |
| Semantic phase is mandatory | Steps execute only after interpretation | 1.1 |
| Stop blocks all steps | ASK_USER/ABORT prevent any step execution | 1.1 |
| Product adapters are isolated | No cross-layer imports between core and products | 1.1 |
| Envelope is only planning handoff | Raw text cannot proceed directly to planning | V1.3 |
| Discovery is deterministic | Same context yields same discovery results | V1.3 |
| Reasoning contract is enforced | Products cannot bypass minimum reasoning phases | V1.3 |

---

## Related Documents

- [Intent.md](../00_developer_intent/intent.md) — Source developer intent
- [Vision.md](../00_developer_intent/Vision.md) — Platform vision and principles
- [BRD-governance.md](BRD-governance.md) — Human oversight for high-risk actions
- [AGT-agents-tools.md](../techspec/AGT-agents-tools.md) — Technical agent/tool specs
- [INT-intelligence.md](../techspec/INT-intelligence.md) — Technical intelligence specs
