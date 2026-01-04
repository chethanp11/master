# Visual Insights — Requirements (v1)

## Objective
Visual Insights turns a CSV dataset into a single, traceable insight card with a chart, narrative, and exportable artifacts. The workflow is deterministic for tools and governed end-to-end by the core runtime.

---

## In-Scope (v1)

### Supported Inputs
- CSV files only (uploaded and staged under product input directories).
- Optional `prompt` text used for chart recommendation and narrative context.

### Flow Behavior
- One flow: `visualization`.
- Step order is fixed by the YAML flow definition.
- Two approval gates: one before chart configuration and one before export.
- One user-input form (`chart_config`) to capture chart options and output format.

### Outputs
- `InsightCard` object from `assemble_insight_card`.
- Export artifacts:
  - JSON stub (`visualization_stub.json`)
  - Optional HTML (`visualization.html`)
  - Optional PDF (`visualization.pdf`)

### Allowed Chart Types
`line`, `bar`, `stacked_bar`, `scatter`, `table`.

---

## Out of Scope (v1)
- PDF ingestion or retrieval.
- Multiple insight modes or dynamic flow branching.
- Additional chart types (maps, heatmaps, networks).
- Live data connectors or streaming inputs.
- UI-driven business logic (UI remains a thin client).

---

## Governance & Trust Requirements
- Trace events are emitted for each step/tool call.
- Citations in cards reference CSV slices.
- Redaction is enforced by core governance hooks before trace/log emission.
