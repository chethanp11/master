# Component Details

This document summarizes the major components in the `master` codebase, including their code
paths, intent, and key technical characteristics.

## Top-Level Structure

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `/README.md` | Root overview | High-level description of the platform, bootstrap instructions, and governance expectations. | Markdown consumed by contributors; echoes product vision and links to docs. |
| `/configs` | Configuration bundles | Declarative settings for the runtime (app metadata, model defaults, policies, per-product enablement). | YAML files loaded via `core.config` utilities; injected into agents/tools (no direct env access). |
| `/core` | Core runtime | Houses the reusable orchestration, tool, and agent infrastructure shared by every product. | Pure Python package, typed and organized into submodules (agents, tools, orchestrator, memory, etc.). |
| `/docs` | Knowledge base | Internal documentation (architecture, flows, governance, product HOWTOs). | Markdown assets referenced by onboarding and governance processes. |
| `/gateway` | Entry points | API/CLI/UI shells that expose the orchestrator to users/services. | FastAPI app (`gateway/api`), Typer CLI (`gateway/cli`), and developer UI stubs (`gateway/ui`). |
| `/infra` | Deployment glue | Container/K8s definitions and platform scripts used for shipping the stack. | Dockerfiles, docker-compose, and k8s manifests (no Terraform in v1). |
| `/logs` | Local log sink | Default on-disk location for structured run logs. | Writable at runtime; loggers in `core.logging` and gateway components point here by default. |
| `/products` | Product packs | Individual product definitions (flows, agents, prompts, assets). | Each product ships a `manifest.yaml` plus `config/product.yaml`, custom agents/tools, templates. |
| `/scripts` | Ops scripts | Helper scripts for maintenance (e.g., data migrations, health checks). | Python/Bash utilities executed manually or via CI. |
| `/storage` | Persistent state | Storage folders for artifacts and memory DB files. | Includes `storage/{memory,raw,processed,vectors}` for local/dev use. |
| `/tests` | Automated tests | Pytest suites targeting `core` subsystems and selected products. | Structured to mirror package layout (`tests/core`, `tests/products`, etc.). |
| `/pyproject.toml` / `/requirements.txt` | Build metadata | Poetry/PEP‑621 project definition and pip requirements for production tooling. | Used by CI/CD; coordinates dependency versions for agents, orchestration, and gateway. |

## Core Package (`/core`)

### Agents

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/agents/base.py` | `BaseAgent` | Abstract contract all agents must follow (goal-driven, no env reads, no direct tool calls). | Defines `BaseAgent.run(step_context)` returning `AgentResult`; enforces config injection and StepContext usage. |
| `core/agents/registry.py` | Agent registry | Global dependency injection container that maps agent names to factories. | Normalizes names, prevents duplicates, and returns fresh agent instances upon resolution. |
| `core/agents/__init__.py` & submodules | Concrete agents | Product/platform-specific agent implementations registered at boot. | Agents rely on `core.contracts.agent_schema.AgentResult` for outputs. |

### Tools

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/tools/base.py` | `BaseTool` | Shared contract for tools invoked by agents via the orchestrator. | Provides `run(params, StepContext)` abstract method returning `ToolResult`; configuration injected via constructor. |
| `core/tools/executor.py` | Tool executor | Centralized dispatcher that validates tool calls and executes the concrete tool implementations. | Handles serialization, audit logging, and ensures sandboxing policies defined in configs. |
| `core/tools/*` | Built-in tools | Standard tool catalog (filesystem, git, HTTP, LLM adapters, etc.). | Each inherits `BaseTool` and is registered through the tool registry. |

### Orchestrator

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/orchestrator/context.py` | `StepContext` | Provides run metadata, shared artifacts, and tracing hooks to agents/tools. | Immutable-ish dataclass propagated through orchestrator; manages artifact read/write shims. |
| `core/orchestrator/engine.py` | Flow engine | Coordinates planning/execution loops across flows. | Talks to `flow_loader`, `runners`, and the step executor. |
| `core/orchestrator/flow_loader.py` | Flow loader | Loads FlowDefs/StepDefs from product manifests. | Validates manifests and resolves agent/tool bindings. |
| `core/orchestrator/runners.py` | Flow runners | Implements entrypoints for different run modes (sync/HITL). | Uses `engine` and `step_executor` to drive StepDefs. |
| `core/orchestrator/step_executor.py` | Step executor | Executes a single step via agent+tool orchestrations. | Enforces policies (`error_policy.py`), HITL gates, and context updates. |
| `core/orchestrator/context.py` | `StepContext` | Provides run metadata, shared artifacts, and tracing hooks to agents/tools. | Immutable-ish dataclass propagated through orchestrator; manages artifact read/write shims. |
| `core/orchestrator/state.py` | Run state manager | Maintains per-run status, step pointers, and persistence hooks. | Persists snapshots for UI/API and ties into the memory router. |
| `core/orchestrator/error_policy.py` / `hitl.py` | Guardrails | Error handling and human-in-the-loop checkpoints. | Centralizes retries/escalations before aborting a flow. |

### Memory

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/memory/base.py` | Memory interfaces | Contracts for memory stores (short-term, episodic, knowledge). | Defines base classes for adapters (e.g., vector store, object store). |
| `core/memory/in_memory.py` | In-memory store | Lightweight cache for ephemeral artifacts/context. | Python dict-based store used mainly for tests/dev. |
| `core/memory/sqlite_backend.py` | SQLite backend | Durable run/memory persistence. | Writes to `storage/memory/*.db` (or configured path) via sqlite3. |
| `core/memory/router.py` | Memory router | Chooses appropriate backend (in-memory vs SQLite) based on config. | Provides unified interface consumed by orchestrator and agents. |

### Contracts & Models

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/contracts/agent_schema.py` | Agent result schema | Pydantic models for agent envelopes, errors, and output payloads. | Enforces serialization for gateway responses and logging. |
| `core/contracts/tool_schema.py` | Tool result schema | Standard response object for tool execution. | Includes metadata (status, artifacts) and optional error payloads. |
| `core/models/*` | Model integrations | LLM/model abstractions (OpenAI, Anthropic, local). | Provide typed interfaces to upstream SDKs; configs pulled from `/configs/models.yaml`. |

### Governance & Knowledge

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/governance/policies.py` | Policy engine | Defines guardrails (e.g., forbidden tool combos, approval rules). | Referenced by orchestrator before executing sensitive steps. |
| `core/knowledge/{base.py,vector_store.py,retriever.py,structured.py}` | Knowledge interfaces | Adapters for retrieving structured/unstructured knowledge. | Vector store abstractions + retrievers for prompts. |

### Logging & Utils

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `core/logging/{logger.py,tracing.py,metrics.py}` | Logging + telemetry | Configures logging, traces, and metrics using `/configs/logging.yaml`. | Centralized wrappers around Python logging and OTEL exporters. |
| `core/utils/*` | Utilities | Helpers for file IO, JSON/YAML parsing, time handling, retries. | Pure functions with Pytest coverage. |

## Gateway (`/gateway`)

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `gateway/api/http_app.py` | FastAPI factory | Builds the HTTP API exposing run/flow endpoints. | Includes `gateway.api.routes_run` router under `/api`; uses dependency providers in `deps.py`. |
| `gateway/api/routes_run.py` | Run routes | REST endpoints for submitting requirements, querying runs, and streaming logs. | Calls into `core.orchestrator.runner` and serializes `AgentResult`/`ToolResult` objects. |
| `gateway/cli/main.py` | CLI entry | Typer/Click CLI for developers to trigger flows locally (inspect, run, list products). | Shares config loading with API, uses same registries. |
| `gateway/ui/platform_app.py` | Streamlit UI | Single-file Streamlit dashboard for v1 run monitoring. | Communicates with API via HTTP/websocket helpers. |

## Products (`/products`)

Each folder under `/products` is a “product pack” with:
- `manifest.yaml`: product metadata + enabled flows.
- `config/product.yaml`: product-specific configuration injected into agents/tools.
- `/agents`: custom agent implementations inheriting from `BaseAgent`.
- `/tools`: product-specific tools.
- `/prompts`: curated prompt assets (if still required).
- `/tests`: optional product-level tests.

Example entry:

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `products/example_app/manifest.yaml` | Example product manifest | Declares supported flows (e.g., `build_app`, `diagnose_bug`), governance overrides. | Parsed by product loader at startup and registered with the gateway. |

## Configurations (`/configs`)

| File | Purpose | Notes |
| --- | --- | --- |
| `app.yaml` | Global app metadata (name, version, telemetry flags). | Loaded during gateway boot. |
| `logging.yaml` | Logging formatting and sink settings. | Supports local file, stdout, OTEL exporters. |
| `models.yaml` | LLM/model catalog with provider keys and rate limits. | Entries referenced by agents via config injection. |
| `policies.yaml` | Governance rules (tool allowlists, approval requirements). | Consumed by `core.governance`. |
| `products.yaml` | Product enablement list and default configs. | Boot loader reads this to know which products to register. |

## Infrastructure & Scripts

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `/infra/docker` | Containers | Dockerfiles / compose setups for local + prod builds. | Standard multi-stage builds referencing `/pyproject.toml`. |
| `/scripts/bootstrap.py` | Bootstrap script | Helper to initialize configs, secrets, storage for new environments. | Called by CI or ops teams. |

## Storage & Logs

| Code Path | Code Name | Functional Details | Technical Details |
| --- | --- | --- | --- |
| `/storage/{memory,raw,processed,vectors}` | Local storage backend | Keeps artifacts, SQLite memory DBs, processed assets for dev/local runs. | File-based; mirrors remote stores for portability. |
| `/logs` | Runtime logs | Stores structured JSON logs and rotation strategy per config. | Ensures developer visibility without external services. |

## Tests (`/tests`)

| File/Path | Purpose | Technical Notes |
| --- | --- | --- |
| `tests/core/test_memory_core.py` | Validates memory adapters | Ensures short-term/episodic stores persist state correctly across runs. |
| `tests/core/test_agents_registry.py` | Validates registry behaviors | Verifies registration, collision handling, and resolution semantics. |
| `tests/products/*` | Product regression tests | Smoke tests for each product flow (mocking tools/agents where needed). |

## Component Relationships

- **Gateway** (API/CLI/UI) ingests user requirements and instantiates **core orchestrator** flows.
- Orchestrator resolves **agents** via the registry, which may emit **tool** requests executed by the Tool Executor.
- Execution results, artifacts, and traces are written to **memory** and **storage**, while governance checks consult **configs/policies**.
- Products bundle their own agents/tools and register them during gateway boot, extending the shared platform without modifying `core`.

## Technical Standards Recap

- Agents/tools never read environment variables directly; configurations are injected from `configs/*`.
- All agent/tool outputs must use the contracts in `core/contracts/*` (Pydantic models) to ensure gateway serialization.
- Logging goes through `core.logging` so that monitoring/observability hooks can process events uniformly.
- Governance and policy checks are centralized; products can only extend them via declarative configs, not bypass them.

This document should be updated whenever new top-level components or subsystems are added.
