# v1 Acceptance Checklist

## Step 1 — Repo health & import sanity

- [x] DONE — Added missing `scripts/__init__.py`, introduced `Engine` alias for `core.orchestrator.engine.OrchestratorEngine`.
- Validated imports via:
  - `python -m compileall core gateway products scripts`
  - `python - <<'PY'\nimport core\nimport gateway\nimport products\nfrom core.orchestrator.engine import Engine\nfrom gateway.api.http_app import create_app\nfrom gateway.cli.main import main\nprint(\"IMPORTS_OK\")\nPY`

Subsequent hardening steps can now assume clean module imports.

## Step 2 — Contracts & envelopes consistency

- [x] DONE — Audit confirmed existing modules already use shared contracts/envelopes; no code changes required.
- Validation (already satisfied by existing code paths):
  - `python -m compileall core gateway`
  - `python - <<'PY'\nfrom core.contracts.tool_schema import ToolResult\nfrom core.contracts.agent_schema import AgentResult\nfrom core.contracts.flow_schema import FlowDef, StepDef, StepType, AutonomyLevel\nfrom core.contracts.run_schema import RunRecord, StepRecord, TraceEvent\nfrom core.tools.executor import ToolExecutor\nfrom core.orchestrator.step_executor import StepExecutor\nprint(\"CONTRACTS_OK\")\nPY`

## Step 3 — Orchestrator state machine & pause/resume

- [x] DONE — No code changes required; existing engine + memory implementations already persist every transition and enforce deterministic resume semantics.
- Invariants verified:
  - `RUNNING → PENDING_HUMAN → RUNNING → (COMPLETED|FAILED|CANCELLED)` stored via memory backend.
  - HITL creates approval records before switching to `PENDING_HUMAN`; resume guards reject double execution.
- State machine diagram:
  ```
  RUNNING
      |
      v
  PENDING_HUMAN --(resume)--> RUNNING
      |
  +--> COMPLETED / FAILED / CANCELLED
  ```

## Step 4 — Configuration & secrets

- [x] DONE — Audit confirmed config loader already handles env > secrets > configs precedence and Settings are injected via loader everywhere; no code changes required in this step.
- Notes:
  - `core/config/loader.py` is the sole env/secrets reader.
  - Gateway API + CLI import the shared loader once per process.

## Step 5 — Tool execution & governance enforcement

- [x] DONE — Audit confirmed ToolExecutor + governance hooks already enforce centralized execution, policy gating, redaction, and envelope-based error handling; no code changes required.
- Invariants:
  - All tool calls flow: Agent → StepExecutor → ToolExecutor → backend.
  - Governance hooks run before execution; denied calls never reach tool code.
  - ToolResult envelopes (with scrubbed payloads) are always returned and traced.

## Step 6 — Orchestrator determinism & HITL pause/resume

- [x] DONE — Existing orchestrator state machine already persists RUNNING ↔ PENDING_HUMAN transitions, enforces resume guards, and emits trace events; no changes required in this step.
- Semantics:
  - Pausing a step records approval via HITL service before switching run/step statuses to `PENDING_HUMAN`.
  - Resuming validates approvals, resumes at the appropriate step index, and rejects duplicate resumes.

## Step 7 — Memory persistence, schema, migrations & traces

- [x] DONE — Hardened sqlite backend + router, added migration utility, and expanded tests.
- Changes:
  - `core/memory/base.py`, `core/memory/in_memory.py`, `core/memory/router.py`, `core/memory/sqlite_backend.py`
  - `scripts/migrate_memory.py`
  - `tests/core/test_memory_core.py`, `tests/integration/test_sample_flows.py`
- DB invariants:
  - Tables: `schema_version`, `runs`, `steps`, `events`, `approvals`.
  - Indices: `runs(status)`, `steps(run_id, step_index)`, `events(run_id, ts)`, `approvals(status, requested_at)`.
  - Versioning: integer `schema_version` row (id=1); `ensure_schema()` idempotently migrates to v1.
  - Trace payloads are scrubbed + clamped before persisting (`MAX_PAYLOAD_CHARS=4096`).
- Validation:
  - `python scripts/migrate_memory.py --db-path /tmp/master.sqlite --apply`
  - `pytest tests/core/test_memory_core.py tests/integration/test_sample_flows.py`

## Step 8 — Governance enforcement & security redaction

- [x] DONE — Governance hooks/policies now drive tool + model enforcement; redaction sanitizes params/results end-to-end.
- Changes:
  - `core/governance/{policies.py,security.py,hooks.py}`
  - `core/tools/executor.py`, `core/logging/tracing.py`, `core/models/router.py`
  - `configs/policies.yaml`, `tests/core/{test_governance_core.py,test_tools_core.py}`
- Invariants:
  - Denied tools never execute; executor returns `POLICY_DENIED` envelope and logs a governance decision.
  - Scrubbing happens before trace persistence/logging, with bounded payload sizes.
  - Model routing consults governance allow/deny lists; per-product overrides respected.
- Validation:
  - `pytest tests/core/test_governance_core.py tests/core/test_tools_core.py`

## Step 9 — Orchestrator pause/resume + HITL correctness

- [x] DONE — Hardened the full HITL path so paused runs persist cleanly, resumes are idempotent, and Flow/HITL schemas reflect reality.
- Changes:
  - `core/contracts/{agent_schema.py,flow_schema.py}` — restored `AgentResult`, added retry aliases/UI fields.
  - `core/config/loader.py`, `core/utils/product_loader.py`, `scripts/migrate_memory.py` — loader normalization + backwards-compatible settings API.
  - `core/orchestrator/{engine.py,flow_loader.py,step_executor.py}` — normalized flows, injected StepDef into contexts, ensured approval + resume sequencing, JSON-safe result storage.
  - `core/logging/tracing.py` — removed nonexistent `message` field, tracked redaction flag.
  - `products/sandbox/agents/simple_agent.py` — aligned error codes with `AgentErrorCode`.
- Invariants enforced:
  - Pausing creates and persists approval records before switching run/step to `PENDING_HUMAN`; run state survives restart.
  - Resume validates pending approval, resolves exactly once, restarts from the paused step index, and rejects second resumes gracefully.
  - Agent/tool outputs persisted via memory are JSON-safe; artifacts/approvals feed downstream steps (summary agent now succeeds).
  - Flow loader accepts legacy manifests (`name`, `retry_on`) but emits schema-compliant FlowDef instances (ids normalized, UI metadata captured).
  - Approvals and trace events remain auditable with scrubbed payloads.
- Validation:
  - `PYTHONPATH=. pytest tests/core/test_orchestrator_state.py tests/core/test_orchestrator.py tests/integration/test_sample_flows.py`

## Step 10 — Knowledge layer v1 (vector + structured)

- [x] DONE — Implemented stable chunk contracts, SQLite-backed vector store, ingestion CLI, retriever, and structured helpers.
- Changes:
  - `core/knowledge/{base.py,vector_store.py,retriever.py,structured.py}`
  - `scripts/ingest_knowledge.py`
  - `tests/core/test_knowledge_core.py`, `tests/integration/test_knowledge_ingest.py`
  - Documentation: `docs/knowledge_layer.md`
- Invariants:
  - Ingestion is deterministic: chunk ids = `normalized_doc_path::index`, metadata captures provenance and tags.
  - Upserts are idempotent via `(collection, doc_id, chunk_id)` primary key; repeated ingests rewrite instead of duplicating.
  - Retrieval honors collection boundaries, top_k limits, and metadata filters; results expose `Chunk` schema (id/text/source/metadata/score).
  - Structured helpers load CSVs locally with no external services.
- Validation:
  - `PYTHONPATH=. pytest tests/core/test_knowledge_core.py tests/integration/test_knowledge_ingest.py`

## Step 11 — Product loader + pack conventions

- [x] DONE — Implemented deterministic product discovery, manifest/config validation, safe registry imports, and scaffolding updates.
- Changes:
  - `core/utils/product_loader.py`, `core/config/schema.py`, `configs/products.yaml`
  - `products/sandbox/{manifest.yaml,registry.py}`, `scripts/create_product.py`
  - `gateway/*`, `products/sandbox/tests`, and new tests (`tests/core/test_product_loader.py`, `tests/integration/test_product_discovery.py`)
  - Documentation updates: `docs/product_howto.md`
- Invariants:
  - Each product pack contains `manifest.yaml`, `config/product.yaml`, and `registry.py`; missing files are reported as catalog errors.
  - Enabled filtering obeys `configs/products.yaml` unless `auto_enable=true`.
  - Registry import is idempotent and side-effect free: `register(registries: ProductRegistries)` receives Agent/Tool registries + Settings.
  - Flow listing is deterministic (sorted by filename) and exposed via the ProductCatalog.
- Validation:
  - `PYTHONPATH=. pytest tests/core/test_product_loader.py tests/integration/test_product_discovery.py`

## Step 12 — Gateway API + CLI hardening

- [x] DONE — Gateway now exposes product-aware endpoints + envelopes and CLI mirrors the same run lifecycle (list/run/status/approvals/resume).
- Changes:
  - `gateway/api/routes_run.py`
  - `gateway/cli/main.py`
  - Tests: `tests/integration/{test_api_runs.py,test_cli_runs.py}`
  - Docs: `docs/overview.md`, this checklist
- API invariants:
  - `/api/products` + `/api/products/{product}/flows` return deterministic, catalog-backed metadata.
  - `/api/run/{product}/{flow}`, `/api/run/{run_id}`, `/api/resume_run/{run_id}` always emit `{ok,data,error,meta}` envelopes.
  - Product/flow validation happens before engine invocation; catalog errors surface with 404/503.
- CLI invariants:
  - Commands: `list-products`, `list-flows`, `run`, `status`, `approvals`, `resume` (plus legacy `get-run`).
  - Runs/resume reuse the same envelopes printed as JSON; approvals list is trimmed + scrubbed.
- Validation:
  - `PYTHONPATH=. pytest tests/integration/test_api_runs.py tests/integration/test_cli_runs.py`
