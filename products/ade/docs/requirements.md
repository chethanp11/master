# Analytical Decision Engine — Requirements (v1)

## Objective
ADE is an analyst-facing business analysis runner. It accepts open-ended analysis questions, executes deterministic tools where possible, and uses LLMs only for interpretation and synthesis. ADE produces a shareable Business Insight HTML and an auditable Evidence Pack derived from events.

---

## In-Scope (v1)

### Supported Inputs
- Uploaded datasets (CSV) staged under product input directories.
- Analyst intent as free-text `prompt`.

### Flow Behavior
- Intent-driven analysis flow with explicit planning.
- User inputs for clarification when intent is ambiguous.
- Approvals for decision gates (hypothesis inclusion, charting, final framing).
- Optional hypothesis checks only if required by the plan.

### Outputs
- Business Insight HTML (primary, shareable, no debug dumps).
- Evidence Pack (secondary, audit trail derived from events.jsonl).
- `response.json` with run status and output files.

### Observability
- `events.jsonl` must be written for every ADE run.
- Output files stored under `<observability_root>/ade/<run_id>/output/`.
- Datasets are referenced, not duplicated.

---

## Out of Scope (v1)
- BI dashboards or fixed analytics pipelines.
- Live database connectors or streaming inputs.
- Multi-dataset joins.
- Auto tool discovery.
- Agent-to-agent autonomy.

---

## Governance & Trust Requirements
- Trace events emitted per step/tool call.
- User inputs and approvals are logged and replayable.
- Evidence Pack is derived from events; no chain-of-thought storage.
- Redaction enforced by core governance hooks before trace/log emission.
