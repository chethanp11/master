# ADE System Design Documentation

> **Product**: Analytical Decision Engine (ADE)  
> **Version**: 1.0.0  
> **Last Updated**: 2026-01-12

---

## Document Index

| Document | Description |
|----------|-------------|
| [architecture.md](architecture.md) | High-level architecture, components, and data flow |
| [flows.md](flows.md) | Flow definitions: ade_v1 and visualization |
| [agents-and-tools.md](agents-and-tools.md) | Agent and tool specifications with descriptors |
| [schemas.md](schemas.md) | Data schemas: DecisionPacket, BusinessReport, IntentFrame |
| [inputs-and-outputs.md](inputs-and-outputs.md) | Input payloads, datasets, and output artifacts |

---

## Quick Reference

### Flows
- **ade_v1**: Free-text analyst workflow with visualization preferences and plan approval
- **visualization**: Dataset-first workflow with explicit preference input

### Primary Outputs
- `business_report.html` — Primary stakeholder report
- `decision_packet.html` — Supporting decision summary for audit

### Agents
| Agent | Purpose |
|-------|---------|
| `intent_agent` | Extracts intent, dataset, metric, time window |
| `plan_agent` | Produces deterministic plan spec |
| `plan_proposal_agent` | Generates PlanProposal for approval |
| `planning_agent` | Proposes replan notes after rejection |
| `sufficiency_evaluator` | Scores data sufficiency |
| `dashboard_agent` | Builds narrative summary |

### Tools
| Category | Tools |
|----------|-------|
| Data | `data_reader`, `compute_business_metrics` |
| Analysis | `detect_anomalies`, `driver_analysis`, `hypothesis_test_*` |
| Visualization | `build_chart_spec`, `recommend_chart` |
| Assembly | `assemble_decision_packet`, `assemble_business_report`, `assemble_evidence_bundle`, `assemble_insight_card` |
| Rendering | `render_business_report_html`, `render_decision_packet_html`, `export_pdf` |
| Narrative | `build_reasoning_narrative` |
