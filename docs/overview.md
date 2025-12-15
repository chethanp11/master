# master — Architecture Overview

This document explains the **high-level architecture** of the `master/` agentic framework.  
It is intended for engineers building products on top of the platform.

---

## 1. Core Design Principles

- **Thin products, thick platform**
  - All heavy logic lives in `core/`
  - Products define *what* to run, not *how* it runs
- **Single runtime**
  - One deployable service
  - One API
  - One platform UI
- **No domain logic in core**
  - Core is reusable across teams and business units
- **Config > code**
  - Flows, prompts, policies, limits defined in YAML
- **Auditability first**
  - Every run, step, tool call, and decision is traceable

---

## 2. Core vs Products Separation

### Core (`core/`)
The **framework runtime**. Product-agnostic and centrally managed.

Core owns:
- Orchestration & workflow execution
- Agent and tool contracts
- Model routing
- Memory & persistence
- Governance & safety
- Logging, tracing, metrics
- Knowledge (RAG + structured access)

Core **must not**:
- Contain domain logic
- Reference specific products
- Contain hardcoded flows, agents, or tools

---

### Products (`products/`)
Thin plug-ins built on top of core.

Each product defines:
- Flows (YAML / JSON)
- Agents (Python)
- Tools (Python)
- Prompts (YAML)
- Product-level config

Products **must not**:
- Implement orchestration logic
- Bypass governance, memory, or logging
- Modify core code

---

## 3. Core Subsystems (What lives in `core/`)

### 3.1 Orchestrator
Location:
core/orchestrator/{engine.py,flow_loader.py,runners.py,step_executor.py,context.py,state.py,error_policy.py,hitl.py}
Responsibilities:
- Load and validate flows
- Execute flows step-by-step
- Handle retries, branching, and loops
- Pause on human approval (HITL)
- Resume from persisted state

Key concepts:
- `FlowDef` → sequence/graph of steps
- `RunStatus` → RUNNING, PENDING_HUMAN, COMPLETED, FAILED
- `RunContext` → shared state across steps

---

### 3.2 Agents
Location:
core/agents/
Responsibilities:
- Encapsulate reasoning logic
- Operate on structured context
- Produce typed results

Key rules:
- Agents implement `BaseAgent`
- Agents do not call tools directly
- Agents receive all inputs via context

---

### 3.3 Tools
Location:
core/tools/
Responsibilities:
- Execute external actions (APIs, DBs, scripts)
- Enforce typed inputs/outputs
- Apply governance before execution

Execution flow:
Agent → Tool Executor → Governance → Backend → Result
Backends supported:
- Local Python functions
- Remote HTTP/gRPC services
- MCP (optional / future)

---

### 3.4 Memory & Persistence
Location:
core/memory/
Responsibilities:
- Store run metadata
- Store step results and traces
- Enable pause/resume
- Enable audit & replay

Memory types:
- Short-term: in-run context
- Long-term: persisted runs & outcomes
- Episodic: traces, events, artifacts

---

### 3.5 Knowledge (RAG + Structured Data)
Location:
core/knowledge/
Responsibilities:
- Retrieve unstructured knowledge (docs, PDFs)
- Access structured data (CSV, Pandas, SQL)
- Feed retrieved context into agents

Design:
- Vector store abstraction
- Retriever orchestration
- Structured access isolated from agent logic

---

### 3.6 Governance & Safety
Location:
core/governance/
Responsibilities:
- Enforce policies defined in `configs/policies.yaml`
- Block disallowed tools or flows
- Redact PII and secrets from logs
- Inject hooks at key lifecycle points

Governance hooks:
- Before step execution
- Before tool execution
- Before run completion

---

### 3.7 Logging, Tracing & Metrics
Location:
Responsibilities:
- Enforce policies defined in `configs/policies.yaml`
- Block disallowed tools or flows
- Redact PII and secrets from logs
- Inject hooks at key lifecycle points

Governance hooks:
- Before step execution
- Before tool execution
- Before run completion

---

### 3.7 Logging, Tracing & Metrics
Location:
core/logging/
Responsibilities:
- Centralized logging
- Structured tracing for every run
- Metrics for runs, steps, failures

Guarantees:
- No execution without trace emission
- Logs sanitized before persistence
- Replayable execution history

---

## 4. Platform UI & Routing

### Gateway (`gateway/`)
Single external entrypoint.

Contains:
- HTTP API
- Platform UI
- CLI utilities

---

### Platform UI Routing
URL structure:
/                 → Platform home (product list)
/{product}        → Product-specific UI
Behavior:
- UI dynamically reads product manifests
- UI renders generic flow runner forms
- UI shows run history and approvals
- UI does not contain product logic

UI talks only to API:
- GET  /api/products
- GET  /api/products/{product}/flows
- POST /api/run/{product}/{flow}
- POST /api/resume_run/{run_id}
- GET  /api/run/{run_id}

### Streamlit Control Center
- `/gateway/ui/platform_app.py` delivers the single page control center.
- The UI hits the API endpoints above for every product, run, and approval action.
- Session state backs run history/approvals; errors and empty lists show friendly guidance so the page stays thin and predictable.
---

## 5. Golden-path Sandbox product

- Focus: `products/sandbox` is the canonical demo product that exercises the full platform (core orchestrator, product tooling, governance, memory, API, and UI).
- Manifest:
  - `manifest.yaml` declares `name: sandbox`, publishes the sandbox APIs/UI, and lists `hello_world` as the default flow.
  - `registry.py` registers `echo_tool` and `simple_agent` into the shared registries safely on import.
- Flow (`hello_world.yaml`):
  1. Tool step calls `echo_tool` with `payload.message`.
  2. Human approval step pauses the run (`PENDING_HUMAN`) and creates a persisted approval record.
  3. `simple_agent` summarizes the echoed message plus the approval status to produce the final result.
- Run the golden path:
  - API: `POST /api/run/sandbox/hello_world` → run_id returned, status `PENDING_HUMAN`.
  - Resume: `POST /api/resume_run/{run_id}` with `{"approved": true, "notes": "ok"}` → run continues and eventually `COMPLETED`.
  - UI: Platform control center lists sandbox, lets you trigger the flow, shows the pending approval, and renders the final summary.
- Tests:
  - `products/sandbox/tests/test_sandbox_flow.py` drives the sandbox run via sqlite, ensures the run pauses, resumes, and persists the echoed message + approval-aware summary data.

## 6. Adding a New Product (No Core Changes)

### Steps to add a product
1. Create new folder:
products/<product_name>/
2. Define product manifest:
products//manifest.yaml
3. Add flows:
products//flows/
4. Add agents and tools:
products//agents/
products//tools/
5. Add prompts and config:
products//prompts/
products/<product>/config/product.yaml
Result:
- Product is auto-discovered
- Product appears in UI
- Product accessible via API
- No core or gateway changes

---

## 7. Why This Architecture Scales

- Centralized governance and safety
- Consistent execution model
- Low skill barrier for product teams
- Fast prototyping with enterprise controls
- Direct path from prototype → production

---

## 8. Non-Negotiable Rules

- Products never bypass core
- Core never imports products
- All execution flows through orchestrator
- All side-effects go through tools
- All data is logged, traced, and governed
