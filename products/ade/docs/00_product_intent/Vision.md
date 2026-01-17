# ADE Product Vision

> **Document**: Product Vision  
> **Product**: Analytical Decision Engine (ADE)  
> **Platform**: MASTER — Managed AI Systems for Trusted Execution & Reasoning  
> **Last Updated**: 2026-01-18  
> **Status**: V1.2 Release

---

## 1. Mission Statement

**ADE (Analytical Decision Engine)** transforms analyst questions and CSV datasets into structured, audit-ready business outputs. We combine the power of intelligent analysis with the rigor of evidence-based decision making, creating a foundation where analytical insights can be trusted, traced, and reproduced.

---

## 2. Product Philosophy

### 2.1 Evidence Over Assertion

> "Every claim must be traceable to source data."

- All findings include evidence_refs linking to datasets and columns
- trace_refs connect decisions to execution steps
- Assumptions and limitations are always explicit

### 2.2 Determinism is Mandatory

> "Same inputs, same outputs. Always."

- Tools perform deterministic computation only
- No LLM calls from tools
- Timestamps are the only allowed variation

### 2.3 Human Oversight by Design

> "Approve before execute."

- All plans require explicit user approval
- Users can reject and trigger replanning
- Confidence levels guide human judgment

### 2.4 Transparency First

> "No hidden assumptions, no unexplained confidence."

- Confidence levels (high/medium/low) present in all outputs
- Assumptions listed explicitly
- Limitations documented clearly

---

## 3. Target Audience

### Primary: Business Analysts

- **Who**: Analysts answering business questions from data
- **Need**: Turn questions into structured, professional reports
- **Value**: Get audit-ready outputs in minutes, not hours

### Secondary: Decision Makers

- **Who**: Executives, managers reviewing analytical outputs
- **Need**: Trust findings and understand confidence levels
- **Value**: Evidence-backed recommendations they can act on

### Tertiary: Auditors

- **Who**: Compliance teams verifying analytical integrity
- **Need**: Complete traceability from claims to source data
- **Value**: Full audit trail without manual reconstruction

---

## 4. Core Value Propositions

### 4.1 Question-Driven Analysis

> "Ask in English, get structured insights."

- Free-text question input
- Semantic interpretation of analyst intent
- Clarifying questions when information is missing

### 4.2 Audit-Ready Outputs

> "Every claim has a paper trail."

- Evidence references for all assertions
- Trace references for all decisions
- Complete reproducibility

### 4.3 Intelligent Analysis

> "Anomalies found. Hypotheses tested. Drivers identified."

- Statistical anomaly detection with z-score analysis
- Optional hypothesis testing (outage patterns, seasonality)
- Key metric driver identification

### 4.4 Professional Reports

> "Stakeholder-ready in one click."

- Business reports with executive summaries
- Decision packets with evidence sections
- Embedded visualizations (bar, line, area, scatter)

---

## 5. Product Capabilities

### 5.1 Two Workflows

| Flow | Entry Point | Primary Output |
|------|-------------|----------------|
| **ade_v1** | Analyst question | business_report.html |
| **visualization** | Dataset selection | decision_packet.html + business_report.html |

### 5.2 Semantic Interpretation

ADE interprets analyst questions to extract:

| Extraction | Example |
|------------|---------|
| Intent type | TREND_ANALYSIS, ANOMALY_REVIEW |
| Metrics | "revenue", "cost", "volume" |
| Time scope | "Q1 2024", "last 30 days" |
| Dataset reference | "sales data", "transactions" |

**Intent Types Supported**:
- DESCRIBE_DATA — Summarize dataset characteristics
- COMPARE_PERIODS — Compare metrics across time periods
- TREND_ANALYSIS — Identify trends over time
- ANOMALY_REVIEW — Detect and explain anomalies
- OPEN_ENDED_ANALYSIS — Exploratory analysis

### 5.3 Plan Approval

Before any analysis executes:
- System presents plan summary
- Shows estimated steps and cost
- User must approve to proceed
- Rejection triggers replanning

### 5.4 Evidence Generation

All tools produce:
- Structured outputs with evidence_items
- Dataset and column references
- Confidence indicators
- Provenance information

### 5.5 Report Assembly

Final outputs include:
- Executive summary with key takeaways
- Key findings with evidence references
- Visualizations (Vega-Lite compatible)
- Anomaly tables with severity ranking
- Recommendations based on analysis
- Appendix with methodology details

---

## 6. Scope Boundaries

### 6.1 In Scope

| Category | Included |
|----------|----------|
| **Data Sources** | CSV files (built-in and user-uploaded) |
| **Workflows** | ade_v1, visualization |
| **Outputs** | business_report.html, decision_packet.html |
| **Analysis** | Metrics, anomalies, hypotheses, drivers |
| **Visualizations** | Bar, line, area, scatter charts |
| **Interactions** | Question input, preferences, plan approval |

### 6.2 Out of Scope

| Category | Excluded | Rationale |
|----------|----------|-----------|
| **Data Sources** | Live databases | CSV focus for MVP |
| **Data Sources** | Streaming inputs | Batch processing only |
| **Data Operations** | Multi-dataset joins | Single dataset per run |
| **System Behavior** | Dynamic flow mutation | Deterministic requirement |
| **Product Surface** | BI dashboarding | Decision packets are primary |

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Output validation** | 100% | All outputs pass Pydantic schemas |
| **Evidence coverage** | 100% | All claims have evidence_refs |
| **Plan approval** | 100% | All plans require explicit approval |
| **Reproducibility** | 100% | Same inputs produce same outputs |
| **Time-to-insight** | < 5 min | Question to report |

---

## 8. Architectural Principles

### 8.1 Deterministic Tools

Tools perform factual computation only:
- No LLM calls inside tools
- No random variations
- Same inputs always produce same outputs

### 8.2 Advisory Agents

Agents advise but never execute:
- Interpret intent from questions
- Propose analysis plans
- Generate approval requests
- Assess data quality
- Create narratives

### 8.3 Evidence-First Design

Every output includes:
- evidence_refs linking claims to data
- trace_refs linking decisions to steps
- Explicit assumptions and limitations

### 8.4 Schema-Driven Contracts

All data structures use:
- Pydantic models with validation
- Extra fields forbidden
- Default factories for collections
- Standard confidence levels

---

## 9. Output Specifications

### 9.1 Business Report (business_report.html)

| Section | Content |
|---------|---------|
| Header | Title, timestamp, dataset info |
| Executive Summary | Key takeaways (bulleted) |
| Key Findings | Headline, value, context, evidence |
| Visualizations | Charts with Vega-Lite specs |
| Anomalies | Table with severity, reason |
| Recommendations | Actionable next steps |
| Appendix | Methodology, data summary |

### 9.2 Decision Packet (decision_packet.html)

| Section | Content |
|---------|---------|
| Question | Original analyst question |
| Decision Summary | Primary conclusion |
| Confidence Level | high / medium / low |
| Assumptions | What was assumed |
| Limitations | What wasn't possible |
| Evidence Sections | Claims with evidence_refs |
| Trace References | Links to execution steps |

---

## 10. Agent Capabilities

| Agent | Capabilities | Output |
|-------|--------------|--------|
| **intent_agent** | Extract intent, entities, metrics, time windows | IntentFrame |
| **plan_agent** | Generate deterministic analysis plans | PlanSpec |
| **plan_proposal_agent** | Create approval requests | PlanProposal |
| **planning_agent** | Handle replanning, dataset-context interpretation | IntentFrame |
| **sufficiency_evaluator** | Assess data quality | confidence_level, downgrade_reasons |
| **dashboard_agent** | Generate narrative summaries | narrative text |

---

## 11. Tool Categories

| Category | Tools | Function |
|----------|-------|----------|
| **Data** | data_reader, compute_business_metrics | Read data, compute aggregates |
| **Analysis** | detect_anomalies, driver_analysis, hypothesis_test_* | Find insights |
| **Visualization** | build_chart_spec, recommend_chart | Create visuals |
| **Assembly** | assemble_decision_packet, assemble_business_report | Build outputs |
| **Rendering** | render_*_html, export_pdf | Generate files |

---

## 12. User Interactions

### 12.1 Visualization Preferences

| Preference | Options |
|------------|---------|
| Chart type | bar, line, area, scatter |
| Metric focus | mean, sum, median, growth_rate, anomalies |
| Hypothesis checks | enabled / disabled |
| Notes | Optional user annotations |

### 12.2 Plan Approval

| Action | Result |
|--------|--------|
| Approve | Analysis proceeds |
| Reject | Replanning triggered |
| (Request changes) | Plan adjusted |

---

## 13. Roadmap Context

### V1 (Current)

- ✅ ade_v1 and visualization flows
- ✅ Semantic interpretation with intent taxonomy
- ✅ Plan approval workflow
- ✅ Business reports and decision packets
- ✅ Anomaly detection and hypothesis testing
- ✅ Evidence traceability

### Future Considerations

- 📋 Additional data source connectors
- 📋 Multi-dataset analysis
- 📋 Custom hypothesis definitions
- 📋 Export format options (PDF, PowerPoint)
- 📋 Scheduled/batch analysis runs

---

## 14. Guiding Questions

When making ADE product decisions, ask:

1. **Is it evidence-based?**
   If claims can't be traced to data, redesign it.

2. **Is it deterministic?**
   If same inputs might yield different outputs, fix it.

3. **Does the user approve?**
   If plans execute without consent, add a gate.

4. **Is confidence explicit?**
   If uncertainty is hidden, surface it.

5. **Can an auditor verify it?**
   If trace_refs are missing, add them.

---

## Related Documents

- [intent.md](intent.md) — Original developer intent
- [BRD-overview.md](../01_brd/BRD-overview.md) — Product objectives
- [BRD-flows.md](../01_brd/BRD-flows.md) — Flow requirements
- [BRD-agents.md](../01_brd/BRD-agents.md) — Agent requirements
- [BRD-tools.md](../01_brd/BRD-tools.md) — Tool requirements
- [BRD-data.md](../01_brd/BRD-data.md) — Data requirements
- [BRD-outputs.md](../01_brd/BRD-outputs.md) — Output requirements
