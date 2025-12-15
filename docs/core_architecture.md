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
```
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
```
---

## 3. Core Folder Structure (Detailed)
```
core/
├── orchestrator/        # Flow engine and execution control
├── agents/              # Agent contracts and registry
├── tools/               # Tool contracts, registry, execution
├── memory/              # Persistence and run state
├── knowledge/           # Vector + structured retrieval helpers
├── models/              # Model routing and providers
├── governance/          # Policies, guardrails, security
├── logging/             # Tracing, logging, metrics
├── prompts/             # Shared prompt templates and helpers
└── utils/               # Cross-cutting helpers (config, product loader, etc.)
```
Each module is described below.

---

## 4. Orchestrator

**Purpose:**  
Controls flow execution, step sequencing, retries, HITL pauses, and resume.
```
core/orchestrator/
├── engine.py
├── flow_loader.py
├── runners.py
├── context.py
├── state.py
├── error_policy.py
└── hitl.py
```
### Responsibilities
- Load flow definitions (YAML/manifest) via `FlowLoader`
- Execute steps in order, honoring retry policies & backoff
- Pause execution for HITL approvals and persist approvals
- Resume execution deterministically using stored run/step snapshots
- Emit trace events for every transition (run, step, tool, approval)

### What It Does NOT Do
- Call models directly
- Call tools directly
- Persist data directly
- Contain business logic

---

## 5. Agents

**Purpose:**  
Encapsulate reasoning logic. Agents decide *what* to do, not *how* to do it.
```
core/agents/
├── base.py
├── registry.py
└── utils.py
```
### Responsibilities
- Consume `RunContext`/`StepContext` supplied via orchestrator
- Perform reasoning or planning purely in-memory
- Request tool execution via the orchestrator (never directly)
- Return structured `AgentResult` (envelope + meta)

### Constraints
- Stateless
- No IO
- No tool execution
- No persistence

---

## 6. Tools

**Purpose:**  
Encapsulate external actions (APIs, scripts, DB access).
```
core/tools/
├── base.py
├── registry.py
├── executor.py
└── backends/
├── local_backend.py
├── remote_backend.py
└── mcp_backend.py
```
### Responsibilities
- Validate inputs via Pydantic contracts
- Execute actions via registered backends (local, future adapters)
- Return structured `ToolResult` and never raise for expected failures
- Surface governance errors & retries via `ToolExecutor`

### Constraints
- No direct calls from agents
- No persistence (memory router owns DB)
- No retry loops (retry policy & orchestrator enforce)

---

## 7. Memory

**Purpose:**  
Persist everything needed to audit, pause, and resume execution.
```
core/memory/
├── base.py
├── sqlite_backend.py
├── in_memory.py
└── router.py
```
### Stores
- Runs, steps, approvals, trace events, artifacts, governance metadata
### Key Guarantee
> Any run can be resumed after a crash or restart because every approval and step state is persisted via SQLite (or in-memory for tests).

### Key Guarantee
> Any run can be resumed after a crash or restart.

---

## 8. Knowledge (RAG + Structured Data)

**Purpose:**  
Provide retrieval capability for agents.
```
core/knowledge/
├── base.py
├── vector_store.py
├── retriever.py
└── structured.py
```
### Supports
- Unstructured vector retrieval from the local sqlite vector store in `storage/vectors`
- Structured helpers for CSV ingestion/querying (pandas fallback)
- Ingest pipeline via `scripts/ingest_knowledge.py` that chunk documents with deterministic ids

---

## 9. Models

**Purpose:**  
Centralize all LLM / embedding access.
```
core/models/
├── router.py
└── providers/
├── openai_provider.py
└── other_provider.py
```
### Responsibilities
- Select models via a routing table (`core/models/router.py`)
- Abstract vendor SDKs behind providers
- Enforce model-level governance policies (per `configs/policies.yaml`)

### Constraint
> No other module may call vendors directly.

---

## 10. Governance

**Purpose:**  
Enforce safety, policy, and enterprise constraints.
```
core/governance/
├── policies.py
├── security.py
└── hooks.py
```
### Enforces
- Allowed tools, autonomy levels, and model choices
- Data redaction before logging/tracing
- Flow/step restrictions and approval gating before execution/resume

Governance hooks run:
- Before step execution
- Before tool execution
- Before flow completion

---

## 11. Logging & Observability

**Purpose:**  
Provide full traceability.
```
core/logging/
├── logger.py
├── tracing.py
└── metrics.py
```
### Guarantees
- Every step, tool, pause, resume, and error is traced (`tracing.py`)
- Trace events persist via the memory router for API/UI visibility
- Metrics/alerts can hook into `metrics.py` for observability

---

## 12. Prompts

**Purpose:**  
Centralize prompt templates.
```
core/prompts/
├── system/
├── tasks/
└── fewshot/
```
Used by products and agents but owned by the platform.

---

## 13. Products

**Purpose:**  
Define business logic without touching core.
```
products//
├── flows/
├── agents/
├── tools/
├── prompts/
├── config/
└── tests/
```
### Product Capabilities
- Define flows (`flows/*.yaml`) that reference registered agents/tools
- Provide agents/tools that obey platform laws
- Ship product-specific prompts/configs/registries without touching core

### Product Limitations
- Cannot modify execution engine
- Cannot bypass governance
- Cannot persist state outside `core/memory`

---

## 14. Gateway

**Purpose:**  
Expose the platform.
```
gateway/
├── api/
├── ui/
└── cli/
```
### API
- Run flows (`/api/run/{product}/{flow}`)
- Resume HITL approvals (`/api/resume_run/{run_id}`)
- Fetch run status/approvals and product catalog

### UI
- Streamlit control center (`gateway/ui/platform_app.py`) that lists products and flows, runs flows, and shows approvals/run history
- Communicates exclusively with the gateway API and keeps state in Streamlit `session_state`

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
