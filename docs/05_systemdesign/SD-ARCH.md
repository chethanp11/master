# System Design: Architecture

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  
> **Version**: 1.1  

> **Last Updated**: 2026-01-17  
> **Status**: V1 Release  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |
| 1.1 | 2026-01-17 | Align architecture with component docs |

## Purpose

This document defines the **stable architectural boundaries** of the MASTER framework. It describes:
- Module boundaries and responsibilities
- Dependency direction rules
- Non-negotiable invariants

This is the **C4-ish** architecture view — stable across releases.

---

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              GATEWAY LAYER                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │   HTTP API  │  │     CLI     │  │  Streamlit  │                      │
│  │  gateway/   │  │  gateway/   │  │   gateway/  │                      │
│  │    api/     │  │    cli/     │  │     ui/     │                      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                      │
│         │                │                │                              │
│         └────────────────┼────────────────┘                              │
│                          ▼                                               │
├─────────────────────────────────────────────────────────────────────────┤
│                           ORCHESTRATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     core/orchestrator/                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │   │
│  │  │   Engine   │  │  Context   │  │   State    │  │ StepExec   │  │   │
│  │  │            │  │            │  │            │  │            │  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  │   │
│  │  │  FlowLoad  │  │    HITL    │  │  Looping   │  │ Branching  │  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                           INTELLIGENCE LAYER                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        core/agents/                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │ │
│  │  │   Advisory   │  │   Reasoning  │  │    Critic    │              │ │
│  │  │    Agent     │  │    Ladder    │  │   Evaluator  │              │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │ │
│  │  ┌──────────────┐  ┌──────────────┐                                │ │
│  │  │  LLM Router  │  │   Registry   │                                │ │
│  │  │ core/models/ │  │              │                                │ │
│  │  └──────────────┘  └──────────────┘                                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                           GOVERNANCE LAYER                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                       core/governance/                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │ │
│  │  │    Hooks     │  │   Policies   │  │    Gates     │              │ │
│  │  │              │  │              │  │              │              │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │ │
│  │  ┌──────────────┐  ┌──────────────┐                                │ │
│  │  │   Security   │  │   Budgets    │                                │ │
│  │  │              │  │              │                                │ │
│  │  └──────────────┘  └──────────────┘                                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                            TOOLS LAYER                                   │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                         core/tools/                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │ │
│  │  │   Registry   │  │   Executor   │  │   BaseTool   │              │ │
│  │  │              │  │              │  │              │              │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │ │
│  │  ┌──────────────┐                                                  │ │
│  │  │   Backends   │                                                  │ │
│  │  │ (local_exec) │                                                  │ │
│  │  └──────────────┘                                                  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                       MEMORY & PERSISTENCE LAYER                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        core/memory/                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │ │
│  │  │    Router    │  │   In-Memory  │  │    SQLite    │              │ │
│  │  │              │  │   Backend    │  │   Backend    │              │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │ │
│  │  ┌──────────────┐  ┌──────────────┐                                │ │
│  │  │   Tracing    │  │ Observability│                                │ │
│  │  │              │  │    Store     │                                │ │
│  │  └──────────────┘  └──────────────┘                                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                            PRODUCTS LAYER                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                          products/                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │ │
│  │  │     ADE      │  │  Hello World │  │   (others)   │              │ │
│  │  │              │  │              │  │              │              │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Module Boundaries

| Module | Path | Responsibility | Owns |
|--------|------|----------------|------|
| **Orchestrator** | `core/orchestrator/` | Run lifecycle, step execution, flow control | `OrchestratorEngine`, `FlowLoader`, `StepExecutor`, semantic normalization |
| **Intelligence** | `core/agents/`, `core/models/` | Advisory reasoning + model routing | `AgentRegistry`, reasoning ladder, critic evaluator, `ModelRouter` |
| **Tools** | `core/tools/` | Deterministic tool execution | `ToolRegistry`, `ToolExecutor`, tool descriptors/results |
| **Governance** | `core/governance/` | Policies, hooks, security, budgets, gates | `GovernanceHooks`, `PolicyEngine`, `GateRegistry`, `SecurityRedactor` |
| **Memory** | `core/memory/` | Persistence, tracing, observability | `MemoryRouter`, backends, `Tracer`, observability store |
| **Gateway** | `gateway/` | External interfaces | HTTP API, CLI, Streamlit UI |
| **Products** | `products/` | Domain-specific applications | Product manifest, registry, semantic adapter, flows/tools/agents |

---

## Dependency Direction Rules

```
                    ┌─────────────┐
                    │   Gateway   │
                    └──────┬──────┘
                           │ imports
                           ▼
                    ┌─────────────┐
                    │   Products  │
                    └──────┬──────┘
                           │ imports
                           ▼
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   ┌──────────┐     ┌──────────┐     ┌──────────┐
   │Orchestr- │     │ Agents/  │     │Governance│
   │  ator    │     │  Tools   │     │          │
   └────┬─────┘     └────┬─────┘     └────┬─────┘
        │                │                │
        └────────────────┼────────────────┘
                         │ imports
                         ▼
                  ┌─────────────┐
                  │   Memory    │
                  └──────┬──────┘
                         │ imports
                         ▼
                  ┌─────────────┐
                  │  Contracts  │
                  │  (schemas)  │
                  └─────────────┘
```

### Rules (Enforced by Architecture Tests)

| Rule ID | Rule | Rationale |
|---------|------|-----------|
| **DEP-001** | Products MUST NOT import from other products | Product isolation |
| **DEP-002** | Core MUST NOT import from gateway | Layer separation |
| **DEP-003** | Core MUST NOT import from products | Framework independence |
| **DEP-004** | Memory MUST NOT import from orchestrator | Prevent cycles |
| **DEP-005** | Contracts MUST NOT import from any module | Schema purity |

---

## Architecture Invariants

These are non-negotiable principles enforced at all levels.

### INV-1: Agents Are Advisory Only

```
┌─────────────────────────────────────────────────────────┐
│                    INVARIANT: INV-1                      │
├─────────────────────────────────────────────────────────┤
│  Agents RECOMMEND. Orchestrator DECIDES.                 │
│                                                          │
│  • Agents return recommendations, never execute actions  │
│  • Orchestrator owns all control flow decisions          │
│  • LLMs never directly invoke tools or change state      │
└─────────────────────────────────────────────────────────┘
```

**Enforcement**: `tests/architecture/test_agent_advisory.py`

### INV-2: Governance Is Non-Bypassable

```
┌─────────────────────────────────────────────────────────┐
│                    INVARIANT: INV-2                      │
├─────────────────────────────────────────────────────────┤
│  Every step passes through governance hooks.             │
│                                                          │
│  • pre_step_hook → step execution → post_step_hook       │
│  • Gates pause execution until approval                  │
│  • No backdoor paths around governance                   │
└─────────────────────────────────────────────────────────┘
```

**Enforcement**: `tests/architecture/test_governance_required.py`

### INV-3: All Actions Are Traced

```
┌─────────────────────────────────────────────────────────┐
│                    INVARIANT: INV-3                      │
├─────────────────────────────────────────────────────────┤
│  Every significant action emits a trace event.           │
│                                                          │
│  • Run start/complete                                    │
│  • Step execution                                        │
│  • Agent invocation                                      │
│  • Tool execution                                        │
│  • Governance decisions                                  │
└─────────────────────────────────────────────────────────┘
```

**Enforcement**: `tests/architecture/test_trace_completeness.py`

### INV-4: Determinism at Runtime

```
┌─────────────────────────────────────────────────────────┐
│                    INVARIANT: INV-4                      │
├─────────────────────────────────────────────────────────┤
│  Given same inputs + same LLM responses → same outputs.  │
│                                                          │
│  • Tools are deterministic functions                     │
│  • State transitions are predictable                     │
│  • Randomness is seeded and reproducible                 │
└─────────────────────────────────────────────────────────┘
```

**Enforcement**: `tests/architecture/test_determinism.py`

### INV-5: Products Are Isolated

```
┌─────────────────────────────────────────────────────────┐
│                    INVARIANT: INV-5                      │
├─────────────────────────────────────────────────────────┤
│  Products cannot see or affect each other.               │
│                                                          │
│  • No cross-product imports                              │
│  • Separate namespaces for agents/tools/flows            │
│  • Isolated storage paths                                │
└─────────────────────────────────────────────────────────┘
```

**Enforcement**: `tests/architecture/test_product_isolation.py`

---

## Data Flow

```
Request → Gateway → Orchestrator → [Steps] → Response
                         │
                         ├── Agent (advisory) → Recommendation
                         │         │
                         │         └── LLM Router → Model Provider
                         │
                         ├── Tool (execution) → Result
                         │
                         ├── Governance (check) → Approve/Reject/Pause
                         │
                         └── Memory (persist) → Trace + State
```

---

## Component Docs

Each component has a detailed design doc following the **contracts + evidence** pattern:

| Component | Document | Key Contracts |
|-----------|----------|---------------|
| Orchestration | [SD-ORC.md](components/SD-ORC.md) | `OrchestratorEngine`, `RunContext`, `StepExecutor`, `FlowLoader` |
| Governance | [SD-GOV.md](components/SD-GOV.md) | `GovernanceHooks`, `PolicyEngine`, `GateRegistry`, `SecurityRedactor` |
| Memory | [SD-MEM.md](components/SD-MEM.md) | `MemoryBackend`, `MemoryRouter`, `Tracer`, `ObservabilityStore` |
| Intelligence | [SD-INT.md](components/SD-INT.md) | `AgentRegistry`, `run_reasoning_ladder()`, `run_critic_evaluator()`, `ModelRouter` |
| Tools | [SD-TOOLS.md](components/SD-TOOLS.md) | `ToolRegistry`, `ToolExecutor`, `BaseTool`, `ToolResult` |
| Gateway | [SD-GW.md](components/SD-GW.md) | HTTP routes, CLI commands, Streamlit UI |
| Products | [SD-PROD.md](components/SD-PROD.md) | Product manifest, registry, semantic adapter |

---

## See Also

- [SD-INDEX.md](SD-INDEX.md) — Navigation and delta detection loop
- [SD-COVERAGE.md](SD-COVERAGE.md) — Requirement → implementation mapping
- [../03_techspec/](../03_techspec/) — Source requirements
