# BRD: Intelligent Automation

> **Document ID**: BRD-AUTO  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning

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
| **BRD-AUTO-044** | Iteration must follow governed cycle (propose→gate→execute→evaluate) | P0 | INV-5 | Added: 2026-01-13 |
| **BRD-AUTO-045** | Iteration must have explicit deterministic stop conditions | P0 | INV-5 | Added: 2026-01-13 |
| **BRD-AUTO-046** | Iterative state must be durable and resumable across restarts | P1 | INV-5 | Added: 2026-01-13 |

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

| BRD ID | Description | Derived Techspec |
|--------|-------------|------------------|
| BRD-AUTO-001 | Multi-step reasoning | AGT-BASE-001...005, INT-RL-001...010 |
| BRD-AUTO-002 | Evidence-backed decisions | AGT-BASE-020...022, TOOL-EXEC-010...012 |
| BRD-AUTO-003 | Agent composition | AGT-BASE-010, REG-001...005 |
| BRD-AUTO-010 | Tool discoverability | TOOL-BASE-010...015, TOOL-DESC-001...005 |
| BRD-AUTO-011 | Typed tool interfaces | TOOL-BASE-001...005 |
| BRD-AUTO-020 | Automatic tool selection | INT-ADV-001...005 (ToolSelector) |
| BRD-AUTO-021 | Automatic agent selection | INT-ADV-010...015 (AgentSelector) |
| BRD-AUTO-022 | Gap identification | INT-ADV-020...025 (GapFinder) |
| BRD-AUTO-025 | Semantic interpretation | ORC-SEM-*, INT-SEM-* |
| BRD-AUTO-026 | Input normalization | ORC-SEM-030...040 |
| BRD-AUTO-027 | Confidence propagation | INT-SEM-CONF-* |
| BRD-AUTO-030 | Structured reasoning | INT-RL-010...030 |
| BRD-AUTO-031 | Critic evaluation | INT-CRIT-001...015 |
| BRD-AUTO-034 | Reasoning observability | MEM-TRACE-REASON-* |
| BRD-AUTO-035 | Reasoning traces | MEM-TRACE-020...025 |
| BRD-AUTO-036 | Reasoning artifacts | INT-RL-ARTIFACT-* |
| BRD-AUTO-040 | Workflow patterns | ORC-STEP-001...010, ORC-BRANCH-*, ORC-LOOP-* |
| BRD-AUTO-044 | Governed iteration | ORC-LOOP-GOV-* |
| BRD-AUTO-045 | Stop conditions | ORC-LOOP-STOP-* |
| BRD-AUTO-046 | Durable iteration | ORC-LOOP-STATE-* |

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

| Law | Implication |
|-----|-------------|
| Agents never execute tools | All tool execution via ToolExecutor only |
| Tools never call models | Tools are deterministic, no LLM calls |
| Governance hooks are mandatory | Every agent action passes through governance |
| Flows are explicit | No implicit execution paths; YAML-defined |

---

## Related Documents

- [Intent.md](../00_developer_intent/intent.md) — Source developer intent
- [Vision.md](../00_developer_intent/Vision.md) — Platform vision and principles
- [BRD-governance.md](BRD-governance.md) — Human oversight for high-risk actions
- [AGT-agents-tools.md](../techspec/AGT-agents-tools.md) — Technical agent/tool specs
- [INT-intelligence.md](../techspec/INT-intelligence.md) — Technical intelligence specs
