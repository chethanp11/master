# Analytical Decision Engine — Requirements (v1)

## Objective
ADE accepts analyst questions and CSV datasets to produce a business report and decision packet using deterministic agents and tools.

## In Scope

### Inputs
- Analyst question via `prompt` (or `intent` / `question` / `instructions`).
- CSV datasets referenced by name, staged under the ADE input directory.
- Built-in dataset: `branded_cards_transactions`.

### Flows
- `ade_v1`: free-text analyst flow with conditional clarification and plan approval.
- `visualization`: dataset-first flow with explicit visualization preferences.

### User Input
- Clarification prompts for missing dataset/metric/time window (`ade_v1`).
- Visualization preferences (`visualization`): `chart_type`, `metric_focus`, `include_hypothesis_checks`, `notes`.

### Outputs
- `business_report.html` (primary).
- `decision_packet.html` (supporting).
- Optional exports from `export_pdf` when used.

## Out of Scope
- Live database connectors or streaming inputs.
- Multi-dataset joins.
- Automatic tool discovery or dynamic flow mutation.
- BI dashboarding as a primary product surface.

## Trust and Audit Expectations
- Outputs must be reproducible from the same inputs.
- Evidence references are embedded in decision packets and reports.
- No chain-of-thought storage is produced by ADE tools.
