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
