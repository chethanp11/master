# V1 Acceptance Checklist

## Spine vs Product Boundaries
- Core spine owns orchestration, registries, governance hooks, HITL handling, and observability persistence.
- Products own domain analysis logic, tools, and renderers; core must not import products modules.
- Optional capabilities are behind feature flags and default OFF.

## Orchestration + HITL
- User input steps pause runs with status `PAUSED_WAITING_FOR_USER` and emit `pending_user_input` events with prompt schemas.
- HITL uses a unified request primitive (APPROVAL or INPUT) with structured request/response payloads.
- User input answers are schema-validated and resume deterministically; approvals resolve ACCEPTED/REJECTED.

## Observability
- Every run writes `observability/<product>/<run_id>/runtime/events.jsonl` and `output/response.json`.
- Output artifacts are persisted under `output/` when tools emit files.
- `output/reasoning.md` is derived post-run from events (no LLM).
- Input mirroring to `input/` is opt-in via feature flag.

## API + UI
- API exposes `GET /runs/{run_id}/pending_input` and `POST /runs/{run_id}/user_input`.
- UI surfaces pending user input prompts and allows submissions.

## Feature Flags (default OFF)
- `observability_input_mirroring`
- `enable_sqlite_backend`
- `enable_vector_backend`
- `enable_knowledge_index`

## ADE Usage (V1)
- ADE should rely on HITL prompts for clarifications and approvals.
- ADE evidence/insight packs should be derived from events and tool outputs, not model chain-of-thought.
