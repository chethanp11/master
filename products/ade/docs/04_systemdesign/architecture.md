# ADE Architecture

> **Document**: System Design — Architecture  
> **Version**: 1.1.0  
> **Last Updated**: 2026-01-21

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

### 3.1.1 Registration Entrypoint

Location: `products/ade/registry.py` (`register`)

**Evidence**:
- `products/ade/registry.py` (`register`, `auto_register`)

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
| `critic_evaluator` | Evaluate evidence gaps and blocking flags | LOW |
| `dashboard_agent` | Build narrative summary | MED |

**Evidence**:
- `products/ade/agents/critic_evaluator.py` (`CriticEvaluatorAgent`, `CritiqueOutput`)
- `products/ade/agents/sufficiency_evaluator.py` (`SufficiencyEvaluatorAgent`, `SufficiencyOutput`)

### 3.4 Tools

Tools perform factual computation (no reasoning):

| Category | Tool | Side Effect |
|----------|------|-------------|
| **Data** | `data_reader` | No |
| **Data** | `context_pack_builder` | No |
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

**Evidence**:
- `products/ade/tools/context_pack_builder.py` (`ContextPackBuilderTool`)
- `products/ade/tools/export_pdf.py` (`ExportPdfTool`)

### 3.5 Schemas

Pydantic models in `products/ade/schemas/`:

| Schema | Purpose |
|--------|---------|
| `DecisionPacket` | Primary decision output structure (with stop_reason + version metadata) |
| `BusinessReport` | Stakeholder report structure (with stop_reason + version metadata) |
| `IntentFrame` | Parsed user intent |
| `PlanSpec` | Execution plan specification |
| `DecisionSection` | Section within decision packet |
| `Evidence` | Evidence item with provenance |
| `InsightCard` | Standalone insight card |
| `ContextPack` | Dataset profile and coverage summary |
| `VersionMetadata` | Output version + hashing metadata |
| `TerminalOutcome` | Terminal outcome enum (SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT) |
| `RunResult` | Run result with outcome, partial details, terminal artifact |

**Evidence**:
- `products/ade/schemas/decision_packet.py` (`DecisionPacket.stop_reason`, `DecisionPacket.version_metadata`)
- `products/ade/schemas/business_report.py` (`BusinessReport.stop_reason`, `BusinessReport.version_metadata`)
- `products/ade/schemas/context_pack.py` (`ContextPack`)
- `products/ade/schemas/version_metadata.py` (`VersionMetadata`)
- `products/ade/schemas/terminal_outcome.py` (`TerminalOutcome`, `PartialSuccessDetails`, `TerminalArtifact`, `RunResult`)

### 3.6 Utilities

Product utilities in `products/ade/utils/`:

| Utility | Purpose | Location |
|---------|---------|----------|
| `advisory.py` | Advisory labeling and non-decisional language | `products/ade/utils/advisory.py` |
| `confidence.py` | Confidence threshold loading from YAML | `products/ade/utils/confidence.py` |
| `narrative.py` | Decision record-based explanations | `products/ade/utils/narrative.py` |
| `output.py` | Output directory creation utilities | `products/ade/utils/output.py` |
| `semantic_validation.py` | Dataset/metric reference validation | `products/ade/utils/semantic_validation.py` |
| `validation.py` | Validation gating and quality checks | `products/ade/utils/validation.py` |
| `versioning.py` | Version metadata generation | `products/ade/utils/versioning.py` |

**Evidence**:
- `products/ade/utils/advisory.py` (`get_advisory_label`, `apply_advisory_language`, `ADVISORY_LABELS`)
- `products/ade/utils/narrative.py` (`DecisionRecord`, `build_explanation`, `get_decision_records_summary`)
- `products/ade/utils/validation.py` (`ValidationGate`, `validate_report_quality`)
- `products/ade/utils/semantic_validation.py` (`validate_dataset`, `validate_metric`, `ValidationResult`)

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
| `clarify_intent` | ade_v1 | Free-text clarification (planned, not wired) |
| `clarify_followup` | ade_v1 | Additional clarification (planned, not wired) |

**Evidence**:
- `products/ade/flows/ade_v1.yaml` (no `clarify_*` steps wired)

### 5.2 Plan Approval

The `plan_proposal` step type invokes `plan_proposal_agent` to generate a PlanProposal. Users can:
- **Approve**: Proceed to execution
- **Reject**: Trigger replan via `planning_agent`

---

## 6. Configuration

### 6.1 Product Config

Location: `products/ade/config/product.yaml`

Key ADE-specific metadata:
```yaml
metadata:
  confidence:
    thresholds:
      high: 0.7
      medium: 0.4
```

**Evidence**:
- `products/ade/config/product.yaml` (`metadata.confidence.thresholds`)
- `products/ade/config/confidence.py` (`load_confidence_thresholds`)

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
| **Advisory Boundary** | Outputs include advisory-only language and recommendations, not decisions |
| **Version Metadata** | Product/flow/schema versions and hashes added to outputs |

**Evidence**:
- `products/ade/tools/render_decision_packet_html.py` (advisory label in HTML output)
- `products/ade/tools/render_business_report_html.py` (advisory label in HTML output)
- `products/ade/tools/assemble_decision_packet.py` (`build_version_metadata` injection)
- `products/ade/tools/assemble_business_report.py` (`build_version_metadata` injection)

---

## 9. Behavioral Test Coverage

ADE behavior is exercised by unit and integration tests:
- Flow execution and output persistence: `products/ade/tests/integration/test_ade_v1.py`
- Orchestrator flow wiring: `products/ade/tests/integration/test_ade_orchestrator_flow.py`
- Business report rendering: `products/ade/tests/integration/test_business_report_html.py`
- Quality checks: `products/ade/tests/unit/test_assemble_business_report_quality.py`

---

## 10. Framework Alignment and Constraints

ADE follows framework alignment constraints documented in `clarification_records.md` and `FRAMEWORK_GAPS.md`.

### 10.1 Framework Reliance (TS-AGENT-FRI-*)

| Constraint | Enforcement | Evidence |
|------------|-------------|----------|
| No core module re-implementation | Static analysis + code review | `clarification_records.md` |
| Agent base class hooks | Runtime enforcement | `core/agents/base.py` |
| Framework gap logging | FRAMEWORK_GAPS.md | `products/ade/docs/FRAMEWORK_GAPS.md` |
| Escalation via `escalate_framework_gap()` | Runtime | Agent base class |

### 10.2 No Runtime Learning (TS-AGENT-NRL-*)

| Constraint | Enforcement | Evidence |
|------------|-------------|----------|
| No state persistence across runs | Static analysis + test | `clarification_records.md` |
| No ML training | Static analysis + test | `clarification_records.md` |
| BRD-first policy | Process enforcement | PR review |
| Determinism (same inputs → same outputs) | Test enforcement | Unit tests |

**Evidence**:
- `products/ade/docs/03_implementation_plan/clarification_records.md`
- `products/ade/docs/FRAMEWORK_GAPS.md`

---

## 11. Terminal Outcomes

ADE supports explicit terminal outcomes per TS-AGENT-TERM-*.

| Outcome | Description | Schema |
|---------|-------------|--------|
| SUCCESS | Run completed successfully with all outputs | `TerminalOutcome.SUCCESS` |
| PARTIAL_SUCCESS | Some outputs generated, some missing | `TerminalOutcome.PARTIAL_SUCCESS` |
| ASK_USER | User input required to proceed | `TerminalOutcome.ASK_USER` |
| ABORT | Run aborted due to error or blocking condition | `TerminalOutcome.ABORT` |

**Evidence**:
- `products/ade/schemas/terminal_outcome.py` (`TerminalOutcome`, `PartialSuccessDetails`, `TerminalArtifact`, `RunResult`)

---

## Cross-References

- [flows.md](flows.md) — Detailed flow step definitions
- [agents-and-tools.md](agents-and-tools.md) — Agent/tool specifications
- [schemas.md](schemas.md) — Data schema definitions
- [inputs-and-outputs.md](inputs-and-outputs.md) — I/O specifications
