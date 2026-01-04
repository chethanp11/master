# V1 Acceptance Checklist

## Orchestration
- User input steps pause runs with status `PAUSED_WAITING_FOR_USER` and emit `pending_user_input` events that include the full prompt schema.
- User input answers are schema-validated and resume execution deterministically.
- Approvals and user inputs remain distinct; HITL approvals do not accept arbitrary data payloads.

## Observability
- Every run writes to `observability/<product>/<run_id>/` with `input/`, `runtime/events.jsonl`, and `output/response.json`.
- Observability artifacts are created for paused, failed, and completed runs.
- Output artifacts are persisted under `output/` when tools emit files.

## API + UI
- API exposes `GET /runs/{run_id}/pending_input` and `POST /runs/{run_id}/user_input`.
- UI surfaces pending user input prompts and allows submissions.

