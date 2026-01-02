# Component Details

This document summarizes the major components in the `master` codebase, including their code
paths, intent, and key technical characteristics. It mirrors the codebase structure and
highlights how components collaborate at runtime.

---

## Top-Level Structure

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `/README.md` | Root overview | High-level description of the platform, bootstrap instructions, and governance expectations. | Markdown consumed by contributors; echoes product vision and links to docs. |
| `/configs` | Configuration bundles | Declarative settings for the runtime (app metadata, model defaults, policies, per-product enablement). | YAML files loaded via `core.config` utilities; injected into agents/tools (no direct env access). |
| `/core` | Core runtime | Houses the reusable orchestration, tool, and agent infrastructure shared by every product. | Pure Python package, typed and organized into submodules (agents, tools, orchestrator, memory, etc.). |
| `/docs` | Knowledge base | Internal documentation (architecture, flows, governance, product HOWTOs). | Markdown assets referenced by onboarding and governance processes. |
| `/gateway` | Entry points | API/CLI/UI shells that expose the orchestrator to users/services. | FastAPI app (`gateway/api`), argparse-based CLI (`gateway/cli`), and Streamlit UI (`gateway/ui`). |
| `/infra` | Deployment glue | Container/K8s definitions and platform scripts used for shipping the stack. | Dockerfile, docker-compose, and k8s manifests. |
| `/observability` | Run observability | Per-run input/runtime/output artifacts for all products. | `core/memory/observability_store.py` defines the directory layout and output paths. |
| `/products` | Product packs | Individual product definitions (flows, agents, tools, assets). | Each product ships a `manifest.yaml` plus `config/product.yaml`, custom agents/tools, templates. |
| `/storage` | Persistent state | Storage folders for legacy artifacts and memory DB files. | Still used for vector store/SQLite in dev; observability moved to `/observability`. |
| `/tests` | Automated tests | Pytest suites covering core units, integration flows, CLI/API/UI, and product regressions. | Organized into `tests/core`, `tests/integration`, and `products/*/tests`. |
| `/pyproject.toml` / `/requirements.txt` | Build metadata | PEP‑621 project definition and pip requirements for production tooling. | Used by CI/CD; coordinates dependency versions. |

```mermaid
flowchart LR
  README[README.md] --> DOCS[docs/]
  CONFIGS[configs/] --> CORE[core/]
  CORE --> GATEWAY[gateway/]
  CORE --> PRODUCTS[products/]
  CORE --> TESTS[tests/]
  INFRA[infra/] --> GATEWAY
  STORAGE[storage/] --> CORE
```

---

## Core Package (`/core`)

### Orchestrator

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/orchestrator/engine.py` | Flow engine | Drives flow execution, pause/resume, and trace emission. | Loads FlowDef from `products/<product>/flows/`, enforces autonomy policy, persists runs/steps, emits trace events. |
| `core/orchestrator/flow_loader.py` | Flow loader | Loads FlowDefs/StepDefs from flow YAML/JSON. | Validates and normalizes step ids; no execution or persistence. |
| `core/orchestrator/step_executor.py` | Step executor | Executes tool or agent steps. | Renders params from payload/artifacts, delegates to ToolExecutor/AgentRegistry, handles retry policy. |
| `core/orchestrator/hitl.py` | HITL service | Approval creation and resolution. | Persists approval records via MemoryRouter. |
| `core/contracts/user_input_schema.py` | User input contracts | Typed request/response for `user_input` steps. | Supports choice and free-text modes. |
| `core/contracts/plan_schema.py` | Plan proposal contracts | Structured plan proposal schema. | Used by `plan_proposal` steps. |
| `core/orchestrator/state.py` | Status helpers | Canonical run/step status groups. | Re-exports RunStatus/StepStatus for runtime use. |

```mermaid
sequenceDiagram
  participant Gateway as API/CLI
  participant Engine
  participant FlowLoader
  participant Governance
  participant StepExec
  participant ToolExec
  participant Memory
  participant Tracer

  Gateway->>Engine: run_flow
  Engine->>FlowLoader: load
  Engine->>Governance: check_autonomy
  Engine->>Memory: create_run
  Engine->>Tracer: run_started
  Engine->>StepExec: execute step
  StepExec->>ToolExec: execute tool
  ToolExec->>Tracer: tool.executed
  StepExec-->>Engine: result
  Engine->>Memory: update_step
  Engine->>Tracer: step_completed
```

### Agents

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/agents/base.py` | `BaseAgent` | Abstract contract for agents. | `run(step_context)` returns `AgentResult`. |
| `core/agents/registry.py` | Agent registry | Global DI container for agent factories. | Case-normalized name resolution; new instance per resolution. |

### Tools

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/tools/base.py` | `BaseTool` | Tool contract used by products. | `run(params, ctx)` returns `ToolResult`. |
| `core/tools/executor.py` | Tool executor | Central dispatcher for tool execution. | Applies governance hooks and redaction; emits trace events. |
| `core/tools/backends/local_backend.py` | Local backend | In-process tool execution. | Calls Python tool implementation directly. |
| `core/tools/backends/remote_backend.py` | Remote backend (stub) | Placeholder for HTTP/gRPC tools. | Returns error in v1. |
| `core/tools/backends/mcp_backend.py` | MCP backend (stub) | Placeholder for MCP tools. | Disabled by default; returns error in v1. |

```mermaid
sequenceDiagram
  participant StepExec
  participant ToolExec
  participant Governance
  participant Backend
  participant Tool

  StepExec->>ToolExec: execute(tool, params)
  ToolExec->>Governance: before_tool_call
  alt local backend
    ToolExec->>Backend: LocalToolBackend.run
    Backend->>Tool: run
    Tool-->>Backend: ToolResult
  else stub backend
    ToolExec->>Backend: run
    Backend-->>ToolExec: ToolResult (error)
  end
  ToolExec-->>StepExec: ToolResult
```

### Memory

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/memory/base.py` | Memory interfaces | Contracts for adapters (runs, steps, events, approvals). | Base classes consumed by routers/backends. |
| `core/memory/sqlite_backend.py` | SQLite backend | Durable run/memory persistence. | Stores runs, steps, events, approvals in SQLite. |
| `core/memory/in_memory.py` | In-memory backend | Lightweight store for tests/dev. | Dict-backed, non-durable. |
| `core/memory/router.py` | Memory router | Chooses appropriate backend and exposes CRUD. | Used by orchestrator, API, CLI, tracer. |

```mermaid
erDiagram
  RUNS {
    string run_id PK
    string product
    string flow
    string status
    string autonomy
    int started_at
    int finished_at
    text input_json
    text output_json
    text summary_json
  }
  STEPS {
    string run_id PK
    string step_id PK
    int step_index
    string name
    string type
    string status
    int started_at
    int finished_at
    text input_json
    text output_json
    text error_json
    text meta_json
  }
  EVENTS {
    int id PK
    string run_id
    string step_id
    string product
    string flow
    string kind
    int ts
    text payload_json
  }
  APPROVALS {
    string approval_id PK
    string run_id
    string step_id
    string product
    string flow
    string status
    string requested_by
    int requested_at
    string resolved_by
    int resolved_at
    string decision
    string comment
    text payload_json
  }
  RUNS ||--o{ STEPS : has
  RUNS ||--o{ EVENTS : has
  RUNS ||--o{ APPROVALS : has
```

### Governance & Security

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/governance/policies.py` | Policy engine | Evaluates tool/model allowlists and autonomy rules. | Per-product overrides supported. |
| `core/governance/hooks.py` | Governance hooks | Integration point for orchestrator/tools. | Autonomy check at run start; tool/step checks at execution. |
| `core/governance/security.py` | Redaction | Scrubs secrets/PII from payloads. | Regex + key-hint based sanitization. |

```mermaid
flowchart LR
  ORC[Orchestrator] --> HOOKS[Governance Hooks]
  TOOL[ToolExecutor] --> HOOKS
  HOOKS --> POLICY[Policy Engine]
  HOOKS --> REDACT[Security Redactor]
```

### Models

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/models/router.py` | Model router | Selects provider/model per product/purpose. | Enforces model policies. |
| `core/models/providers/openai_provider.py` | OpenAI provider (stub) | Placeholder adapter. | No network calls in v1. |

### Knowledge

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/knowledge/vector_store.py` | Vector store | SQLite-backed chunk store. | Lexical Jaccard scoring in v1. |
| `core/knowledge/retriever.py` | Retriever | Thin wrapper over VectorStore. | Adds filters/top_k defaults. |

```mermaid
flowchart TB
  Ingest[Ingestion] --> Store[SqliteVectorStore]
  Store --> Retriever[Retriever]
  Retriever --> Orchestrator
  Orchestrator --> Agents
```

### Tracing & Observability

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/memory/tracing.py` | Tracer | Persists trace events with redaction. | Writes to memory backend and `observability/<product>/<run_id>/runtime/events.jsonl`. |
| `core/memory/observability_store.py` | Observability store | Filesystem layout for run artifacts. | Creates `input/`, `runtime/`, `output/` and writes `response.json`. |

---

## Gateway (`/gateway`)

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `gateway/api/http_app.py` | FastAPI factory | Builds API router and app. | `/api` routes wired in `routes_run.py`. |
| `gateway/api/routes_run.py` | Run routes | Starts/resumes flows and reads runs. | Uses orchestrator + product catalog. |
| `gateway/cli/main.py` | CLI entry | Argparse CLI for local runs. | Directly calls orchestrator. |
| `gateway/ui/platform_app.py` | Streamlit UI | Control center for products, runs, approvals, user inputs. | Talks to API only. |

---

## Products (`/products`)

Each product pack includes:
- `manifest.yaml`
- `config/product.yaml`
- `flows/*.yaml`
- `agents/` and `tools/`
- `registry.py`
- `tests/`

Products are discovered and registered by `core/utils/product_loader.py`.

---

## Configurations (`/configs`)

| File | Purpose | Notes |
| --- | --- | --- |
| `app.yaml` | Global app metadata | Host/ports, paths, flags. |
| `logging.yaml` | Logging config | Level, redaction, tracing toggle. |
| `models.yaml` | Model routing | Provider and model defaults. |
| `policies.yaml` | Governance rules | Tool/model allowlists, autonomy. |
| `products.yaml` | Product enablement | Discovery settings. |

---

## Tests

| Path | Purpose | Notes |
| --- | --- | --- |
| `tests/core` | Unit/regression suites for core subsystems. | Orchestrator, memory, governance, tools, contracts. |
| `tests/integration` | End-to-end flows. | CLI, API, UI, knowledge, resilience. |
| `products/*/tests` | Product regressions. | Golden paths for each product. |

---

## Component Relationships

- Gateway (API/CLI/UI) invokes the core orchestrator.
- Orchestrator executes steps via tool and agent registries.
- Tool execution flows through `ToolExecutor` with governance checks.
- Memory persists runs, steps, events, and approvals.
- Tracing emits sanitized events to memory + observability store.

```mermaid
flowchart LR
  Gateway --> Orchestrator
  Orchestrator --> AgentRegistry
  Orchestrator --> ToolExecutor
  ToolExecutor --> ToolBackend
  Orchestrator --> Memory
  Orchestrator --> Tracer
  Tracer --> Memory
```

---

## Technical Standards Recap

- Agents/tools never read environment variables directly.
- All agent/tool outputs must use Pydantic contracts.
- Tracing goes through `core/memory/tracing.py`.
- Governance checks are centralized and non-bypassable.

---

This document should be updated whenever new top-level components or subsystems are added.
