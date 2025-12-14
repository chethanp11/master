# Core Architecture — master/

This document describes the **core architecture** of the `master/` agentic framework.  
It explains **what exists, why it exists, and how the pieces interact**, with enough detail for engineers to reason about changes without reading all the code.

---

## 1. Architectural Principles

The architecture follows these non-negotiable principles:

- **Thin Products, Thick Platform**
- **Headless Core Runtime**
- **Explicit Contracts Everywhere**
- **No Hidden Side Effects**
- **Auditability > Cleverness**
- **Pause / Resume is First-Class**

Everything in `core/` is **product-agnostic**.  
Everything in `products/` is **domain-specific**.

---

## 2. High-Level Layering

┌───────────────────────────────┐
│           Products            │  ← Business logic only
│  (flows, agents, tools)       │
└──────────────▲────────────────┘
│
┌──────────────┴────────────────┐
│             Core              │  ← Runtime + rules
│  Orchestrator, Memory,        │
│  Governance, Models, Tools    │
└──────────────▲────────────────┘
│
┌──────────────┴────────────────┐
│            Gateway            │  ← API, UI, CLI
│  HTTP, UI routing, auth stub  │
└───────────────────────────────┘

---

## 3. Core Folder Structure (Detailed)

core/
├── orchestrator/        # Flow engine and execution control
├── agents/              # Agent contracts and registry
├── tools/               # Tool contracts, registry, execution
├── memory/              # Persistence and run state
├── knowledge/           # RAG + structured data access
├── models/              # Model routing and providers
├── governance/          # Policies, guardrails, security
├── logging/             # Tracing, logging, metrics
├── prompts/             # Shared prompt templates
└── utils/               # Cross-cutting helpers

Each module is described below.

---

## 4. Orchestrator

**Purpose:**  
Controls flow execution, step sequencing, retries, HITL pauses, and resume.

core/orchestrator/
├── engine.py
├── flow_loader.py
├── runners.py
├── context.py
├── state.py
├── error_policy.py
└── hitl.py

### Responsibilities
- Load flow definitions (YAML/JSON)
- Execute steps in order or loops
- Handle retries and backoff
- Pause execution for human approval
- Resume execution from persisted state
- Emit trace events for every transition

### What It Does NOT Do
- Call models directly
- Call tools directly
- Persist data directly
- Contain business logic

---

## 5. Agents

**Purpose:**  
Encapsulate reasoning logic. Agents decide *what* to do, not *how* to do it.

core/agents/
├── base.py
├── registry.py
└── utils.py

### Responsibilities
- Consume `RunContext`
- Perform reasoning or planning
- Request tool execution
- Return structured `AgentResult`

### Constraints
- Stateless
- No IO
- No tool execution
- No persistence

---

## 6. Tools

**Purpose:**  
Encapsulate external actions (APIs, scripts, DB access).

core/tools/
├── base.py
├── registry.py
├── executor.py
└── backends/
├── local_backend.py
├── remote_backend.py
└── mcp_backend.py

### Responsibilities
- Validate inputs
- Execute actions via backends
- Return structured `ToolResult`
- Surface errors as data

### Constraints
- No direct calls from agents
- No persistence
- No retries (handled by orchestrator)

---

## 7. Memory

**Purpose:**  
Persist everything needed to audit, pause, and resume execution.

core/memory/
├── base.py
├── sqlite_backend.py
├── in_memory.py
└── router.py

### Stores
- Runs
- Steps
- Status transitions
- Trace events
- Artifacts
- Human approvals

### Key Guarantee
> Any run can be resumed after a crash or restart.

---

## 8. Knowledge (RAG + Structured Data)

**Purpose:**  
Provide retrieval capability for agents.

core/knowledge/
├── base.py
├── vector_store.py
├── retriever.py
└── structured.py

### Supports
- Unstructured retrieval (documents)
- Structured access (CSV, Pandas, SQL later)
- Formatting for agent consumption

---

## 9. Models

**Purpose:**  
Centralize all LLM / embedding access.

core/models/
├── router.py
└── providers/
├── openai_provider.py
└── other_provider.py

### Responsibilities
- Select model per use-case
- Abstract vendor differences
- Enforce limits and policies

### Constraint
> No other module may call vendors directly.

---

## 10. Governance

**Purpose:**  
Enforce safety, policy, and enterprise constraints.

core/governance/
├── policies.py
├── security.py
└── hooks.py

### Enforces
- Allowed tools
- Autonomy levels
- Data redaction
- Flow restrictions

Governance hooks run:
- Before step execution
- Before tool execution
- Before flow completion

---

## 11. Logging & Observability

**Purpose:**  
Provide full traceability.

core/logging/
├── logger.py
├── tracing.py
└── metrics.py

### Guarantees
- Every decision is traceable
- Every error is auditable
- Every pause/resume is recorded

---

## 12. Prompts

**Purpose:**  
Centralize prompt templates.

core/prompts/
├── system/
├── tasks/
└── fewshot/

Used by products and agents but owned by the platform.

---

## 13. Products

**Purpose:**  
Define business logic without touching core.

products//
├── flows/
├── agents/
├── tools/
├── prompts/
├── config/
└── tests/

### Product Capabilities
- Define flows
- Create agents/tools
- Tune prompts
- Configure defaults

### Product Limitations
- Cannot modify execution engine
- Cannot bypass governance
- Cannot persist state directly

---

## 14. Gateway

**Purpose:**  
Expose the platform.

gateway/
├── api/
├── ui/
└── cli/

### API
- Run flows
- Resume paused runs
- Fetch run status

### UI
- Platform homepage
- Product pages (`/{product}`)
- Approval queue
- Run history

---

## 15. Adding a New Product (No Core Changes)

Steps:
1. Create `products/<new_product>/`
2. Define flows in YAML
3. Add agents/tools
4. Register via manifest
5. UI auto-discovers product

No changes required in `core/`.

---

## 16. Why This Architecture Scales

- Clear ownership boundaries
- Strong contracts
- Centralized governance
- Headless execution
- Pluggable products
- Resume-safe execution

This is a **platform**, not a bot.

---