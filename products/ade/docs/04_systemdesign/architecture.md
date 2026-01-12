# ADE Architecture

> **Document**: System Design — Architecture  
> **Version**: 1.0.0

---

## 1. Overview

The Analytical Decision Engine (ADE) transforms analyst questions and CSV datasets into structured business outputs. Product behavior is **deterministic** — ADE agents and tools do not call LLMs directly.

```
┌─────────────────────────────────────────────────────────────────┐
│                         ADE Product                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Flows     │───▶│   Agents    │───▶│       Tools         │  │
│  │ (ade_v1,    │    │ (intent,    │    │ (data_reader,       │  │
│  │  visualiz.) │    │  plan, ...)  │    │  compute_metrics,   │  │
│  └─────────────┘    └─────────────┘    │  assemble_*, ...)   │  │
│                                        └─────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      Schemas                                ││
│  │  DecisionPacket | BusinessReport | IntentFrame | PlanSpec   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Design Principles

| Principle | Description |
|-----------|-------------|
| **Deterministic** | No LLM calls from ADE tools; same inputs → same outputs |
| **Evidence-first** | Every claim is backed by traceable evidence references |
| **Audit-ready** | Decision packets include assumptions, limitations, trace refs |
| **Configurable** | User inputs control chart type, metric focus, hypothesis checks |

---

## 3. Component Architecture

### 3.1 Manifest

Location: `products/ade/manifest.yaml`

```yaml
name: "ade"
display_name: "Analytical Decision Engine"
version: "0.1.0"
default_flow: "ade_v1"
flows:
  - "visualization"
  - "ade_v1"
```

### 3.2 Flows

| Flow | Purpose | Default |
|------|---------|---------|
| `ade_v1` | Free-text analyst workflow | ✓ |
| `visualization` | Dataset-first visualization workflow | |

### 3.3 Agents

Agents provide reasoning roles:

| Agent | Purpose | Cost Hint |
|-------|---------|-----------|
| `intent_agent` | Extract intent, dataset, metric, time window | MED |
| `plan_agent` | Produce deterministic plan spec | MED |
| `plan_proposal_agent` | Generate PlanProposal for approval | LOW |
| `planning_agent` | Propose replan after rejection | MED |
| `sufficiency_evaluator` | Score data sufficiency | LOW |
| `dashboard_agent` | Build narrative summary | MED |

### 3.4 Tools

Tools perform factual computation (no reasoning):

| Category | Tool | Side Effect |
|----------|------|-------------|
| **Data** | `data_reader` | No |
| **Data** | `compute_business_metrics` | No |
| **Analysis** | `detect_anomalies` | No |
| **Analysis** | `driver_analysis` | No |
| **Analysis** | `hypothesis_test_data_outage` | No |
| **Analysis** | `hypothesis_test_seasonality` | No |
| **Visualization** | `build_chart_spec` | No |
| **Visualization** | `recommend_chart` | No |
| **Assembly** | `assemble_decision_packet` | No |
| **Assembly** | `assemble_business_report` | No |
| **Assembly** | `assemble_evidence_bundle` | No |
| **Assembly** | `assemble_insight_card` | No |
| **Rendering** | `render_business_report_html` | No |
| **Rendering** | `render_decision_packet_html` | No |
| **Rendering** | `export_pdf` | Yes |
| **Narrative** | `build_reasoning_narrative` | No |

### 3.5 Schemas

Pydantic models in `products/ade/schemas/`:

| Schema | Purpose |
|--------|---------|
| `DecisionPacket` | Primary decision output structure |
| `BusinessReport` | Stakeholder report structure |
| `IntentFrame` | Parsed user intent |
| `PlanSpec` | Execution plan specification |
| `DecisionSection` | Section within decision packet |
| `Evidence` | Evidence item with provenance |
| `InsightCard` | Standalone insight card |

---

## 4. Data Flow

```
┌─────────┐     ┌─────────────┐     ┌──────────────────┐
│ Payload │────▶│ data_reader │────▶│ compute_business │
│ (prompt,│     │             │     │ _metrics         │
│ dataset)│     └─────────────┘     └────────┬─────────┘
└─────────┘                                  │
                                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Analysis Layer                           │
│  ┌───────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │detect_anomalies│  │hypothesis_test_ │  │driver_analysis│  │
│  └───────────────┘  │data_outage      │  └───────────────┘  │
│                     │hypothesis_test_ │                      │
│                     │seasonality      │                      │
│                     └─────────────────┘                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Assembly Layer                           │
│  ┌────────────────┐  ┌───────────────────┐  ┌────────────┐  │
│  │build_chart_spec│  │assemble_decision_ │  │assemble_   │  │
│  │                │  │packet             │  │business_   │  │
│  └────────────────┘  └───────────────────┘  │report      │  │
│                                             └────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Rendering Layer                          │
│  ┌──────────────────────┐  ┌──────────────────────────┐     │
│  │render_business_report│  │render_decision_packet_   │     │
│  │_html                 │  │html                      │     │
│  └──────────────────────┘  └──────────────────────────┘     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │ business_report.html │
                │ decision_packet.html │
                └──────────────────────┘
```

---

## 5. User Interaction Points

### 5.1 User Inputs (HITL)

| Step ID | Flow | Purpose |
|---------|------|---------|
| `viz_preferences` | Both | Chart type, metric focus, hypothesis toggle |
| `clarify_intent` | ade_v1 | Free-text clarification |
| `clarify_followup` | ade_v1 | Additional clarification |

### 5.2 Plan Approval

The `plan_proposal` step type invokes `plan_proposal_agent` to generate a PlanProposal. Users can:
- **Approve**: Proceed to execution
- **Reject**: Trigger replan via `planning_agent`

---

## 6. Configuration

### 6.1 Product Config

Location: `products/ade/config/product.yaml`

### 6.2 User Input Schemas

Location: `products/ade/config/`
- `confirm_time_axis.yaml`
- `select_chart_type.yaml`
- `select_focus_metric.yaml`

---

## 7. UI Integration

```yaml
ui_enabled: true
ui:
  nav_label: "Analytical Decision Engine"
  panels:
    - id: "runner"
      title: "Run a Flow"
    - id: "runs"
      title: "Run History"
    - id: "approvals"
      title: "Approvals Queue"
```

---

## 8. Trust and Audit

| Aspect | Implementation |
|--------|----------------|
| **Reproducibility** | Deterministic tools; same inputs → same outputs |
| **Evidence Provenance** | `evidence_refs` in DecisionPacket sections |
| **Trace References** | `trace_refs` link decisions to step outputs |
| **Assumptions** | Explicitly listed in DecisionPacket |
| **Limitations** | Explicitly listed in DecisionPacket |

---

## Cross-References

- [flows.md](flows.md) — Detailed flow step definitions
- [agents-and-tools.md](agents-and-tools.md) — Agent/tool specifications
- [schemas.md](schemas.md) — Data schema definitions
- [inputs-and-outputs.md](inputs-and-outputs.md) — I/O specifications
