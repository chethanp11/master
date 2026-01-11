# Analytical Decision Engine — Architecture (v1)

## Overview
ADE turns analyst questions and CSV datasets into structured business outputs. Product behavior is deterministic; ADE agents and tools do not call LLMs directly.

## Flows

### ade_v1
Purpose: free-text analyst workflow with conditional clarification and plan approval.

Step outline:
1. Interpret intent (`intent_agent`).
2. Request clarifications when required (`clarify_intent`, `clarify_followup`).
3. Build plan spec (`plan_agent`) and request approval (`plan_proposal_agent`).
4. Read data and compute metrics (`data_reader`, `compute_business_metrics`).
5. Run anomaly and hypothesis checks when enabled (`detect_anomalies`, `hypothesis_test_*`).
6. Build chart spec and reasoning narrative (`build_chart_spec`, `build_reasoning_narrative`).
7. Assemble decision packet and business report (`assemble_decision_packet`, `assemble_business_report`).
8. Render HTML outputs (`render_business_report_html`, `render_decision_packet_html`).

Inputs:
- `prompt` is the primary analyst question.
- `intent`, `question`, or `instructions` are accepted as alternates.
- Dataset is inferred from the prompt or `dataset`.

### visualization
Purpose: dataset-first visualization workflow with explicit preference input.

Step outline:
1. Interpret intent (`planning_agent`).
2. Read dataset (`data_reader`).
3. Collect visualization preferences (`viz_preferences` user input).
4. Compute metrics and evaluate sufficiency (`compute_business_metrics`, `sufficiency_evaluator`).
5. Request plan approval (`plan_proposal_agent`).
6. Run anomaly and hypothesis checks (`detect_anomalies`, `hypothesis_test_*`).
7. Build chart spec, assemble packet/report, and render HTML outputs.

Inputs:
- `dataset` is required.
- `prompt` is optional and used in summaries.

## Inputs and Datasets
- CSV files are expected to be staged under the ADE input directory; dataset names are file names.
- Built-in dataset: `branded_cards_transactions`.

## Outputs
- `business_report.html` (primary report).
- `decision_packet.html` (supporting decision summary).
- `build_reasoning_narrative` supplies a short narrative used in the decision packet.
- `export_pdf` can emit `ade.pdf`, `ade.html`, and `ade_stub.json` when invoked.

## Agents (Reasoning Roles)
- `intent_agent`: extracts intent summary, dataset, metric, time window, and clarification needs.
- `plan_agent`: produces a deterministic plan spec and tool flags.
- `plan_proposal_agent`: generates a PlanProposal for approval.
- `planning_agent`: proposes replan notes and a restart step after rejection.
- `sufficiency_evaluator`: scores data sufficiency from data-reader output.
- `dashboard_agent`: builds a short narrative summary from dataset summaries.

## Tools (Facts/Computation)
- `data_reader`: reads CSV data and derives column/series metadata.
- `compute_business_metrics`: aggregates totals, movers, anomalies, and evidence.
- `detect_anomalies`: z-score anomaly detection (skippable).
- `hypothesis_test_data_outage`: checks for recent outage patterns (skippable).
- `hypothesis_test_seasonality`: checks for seasonal signals (skippable).
- `driver_analysis`: identifies top drivers from computed metrics.
- `recommend_chart`: suggests a chart type using heuristics.
- `build_chart_spec`: builds a chart specification from data.
- `assemble_insight_card`: creates InsightCard objects from metrics and evidence.
- `assemble_decision_packet`: builds DecisionPacket structures.
- `assemble_business_report`: builds BusinessReport structures.
- `assemble_evidence_bundle`: aggregates EvidenceItem objects into a bundle.
- `build_reasoning_narrative`: summarizes run events into a short narrative.
- `render_business_report_html`: renders the BusinessReport HTML.
- `render_decision_packet_html`: renders the DecisionPacket HTML.
- `export_pdf`: exports insight cards to HTML/PDF/JSON.
