# ADE — ade_v1 Flow

## Purpose
`ade_v1` is the free-text analyst workflow. It interprets an analyst question, requests clarifications when needed, obtains plan approval, and produces a business report plus a decision packet.

## Inputs
Primary payload fields:
- `prompt`: analyst question (primary input).
- `intent`, `question`, or `instructions`: alternate inputs for intent parsing.
- `dataset`: optional dataset name; also inferred from the prompt when possible.

## User Inputs
`ade_v1` includes two conditional clarification steps:
- `clarify_intent` (free-text).
- `clarify_followup` (free-text).

These steps are skipped when the intent agent marks `blocking_required` as false.

## Flow Steps (High Level)
1. **Intent interpretation**: `intent_agent` extracts intent summary, dataset, metric focus, and time window.
2. **Clarification** (conditional): user input when dataset/metric/time window is missing.
3. **Planning**: `plan_agent` builds a deterministic plan spec.
4. **Plan approval**: `plan_proposal_agent` produces a plan proposal for approval.
5. **Data read + metrics**: `data_reader` + `compute_business_metrics`.
6. **Anomaly + hypothesis checks**: `detect_anomalies` and `hypothesis_test_*` run only if enabled by the plan flags.
7. **Chart + narrative**: `build_chart_spec` and `build_reasoning_narrative`.
8. **Decision packet**: `assemble_decision_packet`.
9. **Business report**: `assemble_business_report`.
10. **HTML rendering**: `render_business_report_html` and `render_decision_packet_html`.

## Outputs
- `business_report.html`: primary report for stakeholders.
- `decision_packet.html`: supporting decision summary for audit and review.

## Notes
- The flow is deterministic and uses only ADE agents/tools.
- Hypothesis checks are optional and controlled by the plan flags.
