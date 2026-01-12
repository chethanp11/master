# ADE Flow Definitions

> **Document**: System Design — Flows  
> **Version**: 1.0.0

---

## 1. Flow Overview

| Flow | Purpose | Default |
|------|---------|---------|
| `ade_v1` | Free-text analyst workflow with visualization preferences and plan approval | ✓ |
| `visualization` | Dataset-first workflow with explicit preference input | |

Both flows produce `business_report.html` and `decision_packet.html`.

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
┌─────────┐     ┌────────────────┐     ┌──────────────────────┐
│  read   │────▶│ viz_preferences│────▶│compute_business_     │
│         │     │  (user_input)  │     │metrics               │
└─────────┘     └────────────────┘     └──────────┬───────────┘
                                                  │
                                                  ▼
┌────────────────┐     ┌───────────────┐     ┌────────────────┐
│sufficiency_eval│────▶│ plan_proposal │────▶│compute_anomalies│
│   (agent)      │     │ (approval)    │     │                │
└────────────────┘     └───────────────┘     └───────┬────────┘
                                                     │
                                                     ▼
┌───────────────────────────────────────────────────────────────┐
│  build_chart_spec → hypothesis_* → assemble_* → render_*     │
└───────────────────────────────────────────────────────────────┘
```

### 2.3 Step Details

| # | Step ID | Type | Component | Purpose |
|---|---------|------|-----------|---------|
| 1 | `read` | tool | `data_reader` | Read CSV dataset |
| 2 | `viz_preferences` | user_input | — | Collect chart type, metric focus |
| 3 | `compute_business_metrics` | tool | `compute_business_metrics` | Aggregate totals, movers, anomalies |
| 4 | `sufficiency_eval` | agent | `sufficiency_evaluator` | Score data sufficiency |
| 5 | `plan_proposal` | plan_proposal | `plan_proposal_agent` | Generate approval request |
| 6 | `compute_anomalies` | tool | `detect_anomalies` | Z-score anomaly detection |
| 7 | `build_chart_spec` | tool | `build_chart_spec` | Build chart specification |
| 8 | `hypothesis_data_outage` | tool | `hypothesis_test_data_outage` | Check outage patterns |
| 9 | `hypothesis_seasonality` | tool | `hypothesis_test_seasonality` | Check seasonal signals |
| 10 | `assemble_decision_packet` | tool | `assemble_decision_packet` | Build decision packet |
| 11 | `assemble_evidence_bundle` | tool | `assemble_evidence_bundle` | Bundle evidence items |
| 12 | `assemble_business_report` | tool | `assemble_business_report` | Build business report |
| 13 | `render_business_report_html` | tool | `render_business_report_html` | Render report HTML |

### 2.4 User Input: viz_preferences

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
┌─────────────────────┐     ┌─────────┐     ┌────────────────┐
│intent_interpretation│────▶│  read   │────▶│ viz_preferences│
│      (agent)        │     │         │     │  (user_input)  │
└─────────────────────┘     └─────────┘     └───────┬────────┘
                                                    │
                                                    ▼
┌──────────────────────┐     ┌──────────────┐     ┌────────────────┐
│compute_business_     │────▶│sufficiency_  │────▶│   planning     │
│metrics               │     │eval (agent)  │     │   (agent)      │
└──────────────────────┘     └──────────────┘     └───────┬────────┘
                                                          │
                                                          ▼
┌───────────────┐     ┌───────────────────────────────────────────┐
│ plan_proposal │────▶│ anomalies → chart → hypothesis → assembly │
│  (approval)   │     │                  → render                 │
└───────────────┘     └───────────────────────────────────────────┘
```

### 3.3 Step Details

| # | Step ID | Type | Component | Purpose |
|---|---------|------|-----------|---------|
| 1 | `intent_interpretation` | agent | `planning_agent` | Interpret intent and plan |
| 2 | `read` | tool | `data_reader` | Read dataset |
| 3 | `viz_preferences` | user_input | — | Collect preferences |
| 4 | `compute_business_metrics` | tool | `compute_business_metrics` | Compute metrics |
| 5 | `sufficiency_eval` | agent | `sufficiency_evaluator` | Evaluate sufficiency |
| 6 | `planning` | agent | `planning_agent` | Refine plan |
| 7 | `plan_proposal` | plan_proposal | `plan_proposal_agent` | Request approval |
| 8 | `compute_anomalies` | tool | `detect_anomalies` | Detect anomalies |
| 9 | `build_chart_spec` | tool | `build_chart_spec` | Build chart |
| 10 | `hypothesis_data_outage` | tool | `hypothesis_test_data_outage` | Check outage |
| 11 | `hypothesis_seasonality` | tool | `hypothesis_test_seasonality` | Check seasonality |
| 12 | `assemble_decision_packet` | tool | `assemble_decision_packet` | Build packet |
| 13 | `assemble_business_report` | tool | `assemble_business_report` | Build report |
| 14 | `render_business_report_html` | tool | `render_business_report_html` | Render report |
| 15 | `render_decision_packet_html` | tool | `render_decision_packet_html` | Render packet |

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
