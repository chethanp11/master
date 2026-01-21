# ADE Flow Definitions

> **Document**: System Design — Flows  
> **Version**: 1.1.0  
> **Last Updated**: 2026-01-21

---

## 1. Flow Overview

| Flow | Purpose | Default |
|------|---------|---------|
| `ade_v1` | Free-text analyst workflow with visualization preferences and plan approval | ✓ |
| `visualization` | Dataset-first workflow with explicit preference input | |

Outputs by flow:
- `ade_v1`: `business_report.html` (decision packet is assembled but not rendered)
- `visualization`: `business_report.html` and `decision_packet.html`

---

## 2. ade_v1 Flow

### 2.1 Metadata

```yaml
id: "ade_v1"
version: "1.0.0"
description: "ADE workflow with visualization preferences, plan approval, and report outputs"
autonomy_level: "suggest_only"
```

### 2.2 Step Sequence

```
┌─────────┐     ┌──────────────┐     ┌────────────────┐
│  read   │────▶│ context_pack │────▶│ viz_preferences│
│         │     │   (tool)     │     │  (user_input)  │
└─────────┘     └──────────────┘     └──────────┬─────┘
                                                │
                                                ▼
                                      ┌──────────────────────┐
                                      │compute_business_     │
                                      │metrics               │
                                      └──────────┬───────────┘
                                                   │
                                                   ▼
┌────────────────┐     ┌───────────────┐     ┌─────────────┐
│sufficiency_eval│────▶│ plan_proposal │────▶│ critic_eval │
│   (agent)      │     │ (approval)    │     │  (agent)    │
└────────────────┘     └───────────────┘     └───────┬─────┘
                                                      │
                                                      ▼
                                           ┌────────────────┐
                                           │compute_anomalies│
                                           │                │
                                           └───────┬────────┘
                                                      │
                                                      ▼
┌───────────────────────────────────────────────────────────────┐
│  build_chart_spec → hypothesis_* → assemble_* → render_*      │
└───────────────────────────────────────────────────────────────┘
```

### 2.3 Step Details

| # | Step ID | Type | Component | Purpose |
|---|---------|------|-----------|---------|
| 1 | `read` | tool | `data_reader` | Read CSV dataset |
| 2 | `context_pack` | tool | `context_pack_builder` | Build dataset profile and coverage |
| 3 | `viz_preferences` | user_input | — | Collect chart type, metric focus |
| 4 | `compute_business_metrics` | tool | `compute_business_metrics` | Aggregate totals, movers, anomalies |
| 5 | `sufficiency_eval` | agent | `sufficiency_evaluator` | Score data sufficiency |
| 6 | `plan_proposal` | plan_proposal | `plan_proposal_agent` | Generate approval request |
| 7 | `critic_eval` | agent | `critic_evaluator` | Evaluate evidence gaps and blocking flags |
| 8 | `compute_anomalies` | tool | `detect_anomalies` | Z-score anomaly detection |
| 9 | `build_chart_spec` | tool | `build_chart_spec` | Build chart specification |
| 10 | `hypothesis_data_outage` | tool | `hypothesis_test_data_outage` | Check outage patterns |
| 11 | `hypothesis_seasonality` | tool | `hypothesis_test_seasonality` | Check seasonal signals |
| 12 | `assemble_decision_packet` | tool | `assemble_decision_packet` | Build decision packet |
| 13 | `assemble_evidence_bundle` | tool | `assemble_evidence_bundle` | Bundle evidence items |
| 14 | `assemble_business_report` | tool | `assemble_business_report` | Build business report |
| 15 | `render_business_report_html` | tool | `render_business_report_html` | Render report HTML |

**Evidence**:
- `products/ade/flows/ade_v1.yaml` (steps: `context_pack`, `critic_eval`, `assemble_decision_packet`)

### 2.4 Plan Proposal Details (TS-FLOW-V1-006..009)

The `plan_proposal` step generates a `PlanProposal` with detailed metadata in `estimated_cost.details`:

| Field | Description | TS ID |
|-------|-------------|-------|
| `objective` | Plan objective string | TS-FLOW-V1-006 |
| `expected_evidence` | List of evidence sources | TS-FLOW-V1-006 |
| `assumptions` | List of planning assumptions | TS-FLOW-V1-007 |
| `risks` | List of identified risks | TS-FLOW-V1-007 |
| `replan_change_summary` | Summary of changes from prior plan | TS-FLOW-V1-008 |
| `replan_rationale` | Rationale for replan | TS-FLOW-V1-008 |
| `tool_recommendations` | Advisory tool recommendations | TS-FLOW-V1-009 |

**Evidence**:
- `products/ade/agents/plan_proposal_agent.py` (`estimated_cost.details`)
- `products/ade/agents/planning_agent.py` (`replan_change_summary`)

### 2.5 User Input: viz_preferences

```yaml
form_id: "viz_preferences"
title: "Visualization preferences"
mode: "choice_input"
required:
  - "chart_type"
  - "metric_focus"
defaults:
  chart_type: "bar"
  metric_focus: "mean"
  include_hypothesis_checks: true
  notes: ""
schema:
  properties:
    chart_type:
      type: "string"
      enum: ["bar", "line", "area", "scatter"]
    metric_focus:
      type: "string"
      enum: ["mean", "sum", "median", "growth_rate", "anomalies"]
    include_hypothesis_checks:
      type: "boolean"
    notes:
      type: "string"
```

### 2.5 Artifact References

Steps reference prior outputs via template expressions:

| Reference | Source |
|-----------|--------|
| `{{artifacts.tool.data_reader.output.columns}}` | data_reader columns |
| `{{artifacts.tool.data_reader.output.rows}}` | data_reader rows |
| `{{artifacts.user_input.viz_preferences.values.chart_type}}` | User-selected chart type |
| `{{artifacts.agent.sufficiency_evaluator.output.confidence_level}}` | Sufficiency confidence |

---

## 3. visualization Flow

### 3.1 Metadata

```yaml
id: "visualization"
version: "1.0.0"
description: "Deterministic ADE decision packet generation"
autonomy_level: "suggest_only"
```

### 3.2 Step Sequence

```
┌─────────────────────┐     ┌─────────┐     ┌──────────────┐
│intent_interpretation│────▶│  read   │────▶│ context_pack │
│      (agent)        │     │         │     │   (tool)     │
└─────────────────────┘     └─────────┘     └───────┬──────┘
                                                    │
                                                    ▼
                                          ┌────────────────┐
                                          │ viz_preferences│
                                          │  (user_input)  │
                                          └───────┬────────┘
                                                    │
                                                    ▼
┌──────────────────────┐     ┌──────────────┐     ┌────────────────┐
│compute_business_     │────▶│sufficiency_  │────▶│   planning     │
│metrics               │     │eval (agent)  │     │   (agent)      │
└──────────────────────┘     └──────────────┘     └───────┬────────┘
                                                          │
                                                          ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────────────┐
│ plan_proposal │────▶│  critic_eval  │────▶│ anomalies → chart →   │
│  (approval)   │     │   (agent)     │     │ hypothesis → assembly │
└───────────────┘     └───────────────┘     │        → render        │
                                           └───────────────────────┘
```

### 3.3 Step Details

| # | Step ID | Type | Component | Purpose |
|---|---------|------|-----------|---------|
| 1 | `intent_interpretation` | agent | `planning_agent` | Interpret intent and plan |
| 2 | `read` | tool | `data_reader` | Read dataset |
| 3 | `context_pack` | tool | `context_pack_builder` | Build dataset profile and coverage |
| 4 | `viz_preferences` | user_input | — | Collect preferences |
| 5 | `compute_business_metrics` | tool | `compute_business_metrics` | Compute metrics |
| 6 | `sufficiency_eval` | agent | `sufficiency_evaluator` | Evaluate sufficiency |
| 7 | `planning` | agent | `planning_agent` | Refine plan |
| 8 | `plan_proposal` | plan_proposal | `plan_proposal_agent` | Request approval |
| 9 | `critic_eval` | agent | `critic_evaluator` | Evaluate evidence gaps and blocking flags |
| 10 | `compute_anomalies` | tool | `detect_anomalies` | Detect anomalies |
| 11 | `build_chart_spec` | tool | `build_chart_spec` | Build chart |
| 12 | `hypothesis_data_outage` | tool | `hypothesis_test_data_outage` | Check outage |
| 13 | `hypothesis_seasonality` | tool | `hypothesis_test_seasonality` | Check seasonality |
| 14 | `assemble_decision_packet` | tool | `assemble_decision_packet` | Build packet |
| 15 | `assemble_business_report` | tool | `assemble_business_report` | Build report |
| 16 | `render_business_report_html` | tool | `render_business_report_html` | Render report |
| 17 | `render_decision_packet_html` | tool | `render_decision_packet_html` | Render packet |

**Evidence**:
- `products/ade/flows/visualization.yaml` (steps: `context_pack`, `critic_eval`, `render_decision_packet_html`)

### 3.4 Differences from ade_v1

| Aspect | ade_v1 | visualization |
|--------|--------|---------------|
| Initial step | `read` | `intent_interpretation` |
| Planning agent | Not used | Used twice |
| Decision packet HTML | Not rendered | Rendered |
| Default metric_focus | `mean` | `anomalies` |

---

## 4. Conditional Execution

### 4.1 Hypothesis Checks

Hypothesis tools respect the `enabled` parameter from user input:

```yaml
params:
  enabled: "{{artifacts.user_input.viz_preferences.values.include_hypothesis_checks}}"
```

When `include_hypothesis_checks: false`, hypothesis tools return early with `status: "skipped"`.

### 4.2 Anomaly Detection

Anomaly detection runs unconditionally but uses the `min_points` parameter:

```yaml
params:
  min_points: 3
```

---

## 5. Error Handling

### 5.1 Retry Configuration

```yaml
retry:
  max_attempts: 2
  backoff_seconds: 1
```

Applied to: `read` (data_reader)

### 5.2 Fallback Values

Chart spec uses fallback when user-selected type is incompatible:

```yaml
params:
  chart_type: "{{artifacts.user_input.viz_preferences.values.chart_type}}"
  fallback_chart_type: "bar"
```

---

## Cross-References

- [architecture.md](architecture.md) — Component overview
- [agents-and-tools.md](agents-and-tools.md) — Agent/tool details
- [inputs-and-outputs.md](inputs-and-outputs.md) — I/O specifications
