# ADE Developer Intent

> **Document**: Product Developer Intent  
> **Product**: Analytical Decision Engine (ADE)  
> **Platform**: MASTER — Managed AI Systems for Trusted Execution & Reasoning  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release

---

## Purpose

This document captures the original developer intent behind ADE. It is the seed from which the BRD, techspec, and all downstream specifications were derived.

**Developer Intent is the only required manual input. Everything else flows from here.**

---

## Document Structure

This intent document is organized to map directly to Business Requirement Documents:

| Intent Section | Maps To | Theme |
|----------------|---------|-------|
| [§1 INT-OVERVIEW](#1-product-overview-int-overview) | [BRD-overview.md](../01_brd/BRD-overview.md) | Vision, objectives, scope, stakeholders |
| [§2 INT-FLOWS](#2-flows-int-flows) | [BRD-flows.md](../01_brd/BRD-flows.md) | ade_v1, visualization workflows |
| [§3 INT-AGENTS](#3-agents-int-agents) | [BRD-agents.md](../01_brd/BRD-agents.md) | Intent, planning, sufficiency, narrative |
| [§4 INT-TOOLS](#4-tools-int-tools) | [BRD-tools.md](../01_brd/BRD-tools.md) | Data, analysis, assembly, rendering |
| [§5 INT-DATA](#5-data--schemas-int-data) | [BRD-data.md](../01_brd/BRD-data.md) | Datasets, schemas, validation |
| [§6 INT-OUTPUTS](#6-outputs--audit-int-outputs) | [BRD-outputs.md](../01_brd/BRD-outputs.md) | Reports, packets, evidence, traceability |
| [§7 INT-INTEL](#7-product-intelligence--execution-int-intel) | All BRDs (cross-cutting) | Reasoning, critique, grounding, termination |

---

# 1. Product Overview (INT-OVERVIEW)

> **Maps to**: [BRD-overview.md](../01_brd/BRD-overview.md)

## 1.1 The Problem We're Solving

### Analyst Pain Points

Analysts struggle to produce audit-ready analytical decisions because:

1. **Manual analysis is slow** — Extracting insights from data requires significant time and expertise
2. **Evidence is scattered** — Claims are made without clear traceability to source data
3. **Confidence is subjective** — No standardized way to express certainty in findings
4. **Reports lack structure** — Ad-hoc formats make comparison and audit difficult
5. **Reproducibility is impossible** — Same question on same data may yield different results

### What Doesn't Exist Today

There is no tool that:
- Accepts **free-text analyst questions** and produces structured outputs
- Provides **evidence-backed decisions** with full traceability
- Generates **audit-ready reports** with confidence levels and limitations
- Ensures **deterministic analysis** where same inputs always produce same outputs
- Supports **human oversight** through plan approval before execution

## 1.2 Core Intent

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OVERVIEW-001** | Transform analyst questions into structured, audit-ready outputs | Core product value proposition |
| **INT-OVERVIEW-002** | Every claim must be traceable to source data | Trust requires evidence |
| **INT-OVERVIEW-003** | Same inputs must always produce same outputs | Audit and reproducibility requirement |
| **INT-OVERVIEW-004** | Confidence, assumptions, and limitations must be explicit | Transparency requirement |
| **INT-OVERVIEW-005** | Plans must require human approval before execution | Human oversight by design |
| **INT-OVERVIEW-006** | Analyst questions must be semantically interpreted | Enable natural language interaction |

### The One-Liner

> ADE accepts analyst questions and CSV datasets to produce audit-ready analytical decisions with evidence, confidence, and traceability.

## 1.3 Objectives

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OBJ-001** | 100% of outputs must include evidence references | Evidence-based requirement |
| **INT-OBJ-002** | Same inputs must always produce same outputs | Reproducibility requirement |
| **INT-OBJ-003** | All plans must require explicit user approval | Human-in-the-loop requirement |
| **INT-OBJ-004** | All outputs must include confidence_level, assumptions, limitations | Transparency requirement |
| **INT-OBJ-005** | Time from question to report should be < 5 minutes | Usability target |
| **INT-OBJ-006** | 4+ chart types must be available | Visualization richness |
| **INT-OBJ-007** | Hypothesis checks must be toggleable | Analysis flexibility |

## 1.4 Scope

### In Scope

| Category | Intent |
|----------|--------|
| **Workflows** | Two entry points: question-first (ade_v1) and dataset-first (visualization) |
| **Inputs** | Free-text analyst questions and CSV datasets |
| **Outputs** | HTML business reports and decision packets |
| **User Interactions** | Visualization preferences and plan approval |
| **Analysis** | Anomaly detection, hypothesis testing, metric computation |

### Out of Scope (Non-Goals)

| Non-Goal | Rationale |
|----------|-----------|
| BI dashboarding platform | Decision packets are primary output |
| Live database connectors | CSV focus for MVP |
| Multi-dataset joins | Single dataset per analysis |
| Streaming analysis | Batch processing only |
| Dynamic flow mutation | Deterministic flows only |
| Automatic tool discovery | Explicit tool configuration |

## 1.5 Target Users

### Primary: Analysts

Business and data analysts who need to answer questions about data.

| Need | They Get |
|------|----------|
| Ask questions in natural language | Free-text question input |
| Get structured, professional reports | Business reports with evidence references |
| Trust the results with clear evidence | Confidence levels and limitations disclosed |

### Secondary: Decision Makers

Executives and managers who consume analytical outputs.

| Need | They Get |
|------|----------|
| Clear recommendations | Decision packets with audit trails |
| Confidence in findings | Executive summaries |
| Ability to trace claims to evidence | Evidence-backed key findings |

### Tertiary: Auditors

Compliance and audit teams who verify analytical integrity.

| Need | They Get |
|------|----------|
| Complete traceability | trace_refs linking decisions to steps |
| Reproducible results | evidence_refs linking claims to data |
| Documented assumptions | Explicit assumptions and limitations |

---

# 2. Flows (INT-FLOWS)

> **Maps to**: [BRD-flows.md](../01_brd/BRD-flows.md)

## 2.1 Flow Overview

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-FLOWS-001** | Provide two entry points for different analyst use cases | Flexibility for different workflows |
| **INT-FLOWS-002** | ade_v1 flow: analyst has a question to answer | Question-first workflow |
| **INT-FLOWS-003** | visualization flow: analyst has a dataset to explore | Dataset-first workflow |

### Flow Summary

| Flow | Entry Point | Primary Output | Use Case |
|------|-------------|----------------|----------|
| `ade_v1` | Question/prompt | business_report.html | Analyst has a question |
| `visualization` | Dataset selection | decision_packet.html + business_report.html | Analyst has data to explore |

## 2.2 ade_v1 Flow Intent

### User Journey

```
Analyst Question → Dataset Selection → Visualization Preferences 
    → Plan Approval → Analysis → Report Generation
```

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-V1-001** | User must be able to enter free-text questions | Natural language interaction |
| **INT-V1-002** | System must interpret intent from question | Semantic understanding |
| **INT-V1-003** | User must select dataset for analysis | Data source specification |
| **INT-V1-004** | User must configure visualization preferences | Customization |
| **INT-V1-005** | User must approve plan before execution | Human oversight |
| **INT-V1-006** | System must produce business report | Primary output |
| **INT-V1-007** | User should be able to enable/disable hypothesis checks | Analysis flexibility |
| **INT-V1-008** | User should be able to add notes to analysis | Documentation |

### Inputs

| Input | Required | Intent |
|-------|----------|--------|
| `prompt` | Yes* | Analyst question (or intent/question/instructions) |
| `dataset` | Yes | Dataset name |
| `preferences` | Yes | Visualization preferences |

*One of prompt/intent/question/instructions is required.

## 2.3 visualization Flow Intent

### User Journey

```
Dataset Selection → Intent Interpretation → Visualization Preferences 
    → Sufficiency Check → Plan Approval → Analysis → Decision Packet
```

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-VIZ-001** | User must select dataset first | Dataset-first workflow |
| **INT-VIZ-002** | System must interpret intent from dataset context | Intelligent interpretation |
| **INT-VIZ-003** | User must provide visualization preferences | Explicit preferences |
| **INT-VIZ-004** | System must check data sufficiency | Quality gate |
| **INT-VIZ-005** | User must approve plan before execution | Human oversight |
| **INT-VIZ-006** | System must produce decision packet | Primary output |
| **INT-VIZ-007** | System must also produce business report | Secondary output |

## 2.4 User Interaction Intent

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-UI-001** | Visualization preferences must include chart_type | User control |
| **INT-UI-002** | Visualization preferences must include metric_focus | Analysis direction |
| **INT-UI-003** | Visualization preferences must include hypothesis_enabled flag | Optional analysis |
| **INT-UI-004** | Plan approval must show plan summary | Informed decision |
| **INT-UI-005** | Plan approval must allow approve/reject | Human control |
| **INT-UI-006** | Rejection must trigger replanning | Recovery path |

### Preference Options

| Preference | Options |
|------------|---------|
| Chart type | bar, line, area, scatter |
| Metric focus | mean, sum, median, growth_rate, anomalies |
| Hypothesis checks | enabled / disabled |
| Notes | Optional user annotations |

## 2.5 Determinism Intent

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-DET-001** | Flows must be deterministic | Reproducibility |
| **INT-DET-002** | Flows must use suggest_only autonomy | Framework compliance |
| **INT-DET-003** | Same inputs must produce same execution | Audit requirement |
| **INT-DET-004** | No dynamic flow mutation | Predictability |

---

# 3. Agents (INT-AGENTS)

> **Maps to**: [BRD-agents.md](../01_brd/BRD-agents.md)

## 3.1 Agent Overview

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AGT-001** | All agents must be advisory only | Framework compliance |
| **INT-AGT-002** | Agents propose, never execute | Safety boundary |
| **INT-AGT-003** | Agents produce structured outputs | Schema compliance |
| **INT-AGT-004** | Agents support reasoning transparency | Auditability |

### Agent Summary

| Agent | Role | Advisory Function |
|-------|------|-------------------|
| intent_agent | Interpret questions | Extract intent, entities, metrics, time windows |
| plan_agent | Create analysis plans | Generate deterministic step sequence |
| plan_proposal_agent | Request approval | Summarize plan for human review |
| planning_agent | Handle replanning | Interpret dataset context, recover from rejection |
| sufficiency_evaluator | Assess data quality | Evaluate row count, completeness, freshness |
| dashboard_agent | Generate narratives | Summarize dataset characteristics |

## 3.2 Intent Interpretation

### Problem

Users express questions in natural language, but the system needs structured intent.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-INTENT-001** | Extract intent summary from user question | Structured understanding |
| **INT-INTENT-002** | Identify referenced datasets | Data source identification |
| **INT-INTENT-003** | Identify referenced metrics | Analysis focus |
| **INT-INTENT-004** | Identify time window constraints | Temporal scoping |
| **INT-INTENT-005** | Provide confidence score (0-1) | Uncertainty quantification |
| **INT-INTENT-006** | Detect when clarification is needed | Avoid misinterpretation |
| **INT-INTENT-007** | Generate clarifying questions | User guidance |

### Semantic Interpretation Design

**Intent Taxonomy**:
- DESCRIBE_DATA — Summarize dataset characteristics
- COMPARE_PERIODS — Compare metrics across time periods
- TREND_ANALYSIS — Identify trends over time
- ANOMALY_REVIEW — Detect and explain anomalies
- OPEN_ENDED_ANALYSIS — Exploratory analysis

**Design Decisions**:
- Intent classification is deterministic (pattern matching, no LLM in classification)
- Missing fields trigger clarifying questions
- Confidence scores guide user interaction
- Low confidence triggers blocking_required=True

## 3.3 Plan Generation

### Problem

Analysis must be planned before execution to enable human oversight.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-PLAN-001** | Produce deterministic plans | Reproducibility |
| **INT-PLAN-002** | Include all required analysis steps | Completeness |
| **INT-PLAN-003** | Include tool flags for conditional execution | Flexibility |
| **INT-PLAN-004** | Same inputs must produce same plan | Determinism |
| **INT-PLAN-005** | Generate human-readable plan summary | Informed approval |
| **INT-PLAN-006** | Estimate step count | User visibility |
| **INT-PLAN-007** | Estimate execution cost | Cost transparency |
| **INT-PLAN-008** | Require approval for non-trivial plans | Human oversight |

### Plan Approval Gate

**Design Decision**: Users must approve plans before execution.

**Implications**:
- plan_proposal_agent generates approval requests
- Plans show estimated steps and cost
- Users can approve, reject, or request changes
- Rejection triggers replanning

## 3.4 Data Quality Assessment

### Problem

Analysis quality depends on data quality; users need visibility into data sufficiency.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-SUFF-001** | Assess data sufficiency before analysis | Quality gate |
| **INT-SUFF-002** | Provide confidence level (high/medium/low) | Uncertainty communication |
| **INT-SUFF-003** | Explain confidence downgrades | Transparency |
| **INT-SUFF-004** | Evaluate row count sufficiency | Statistical validity |
| **INT-SUFF-005** | Evaluate column completeness | Data quality |
| **INT-SUFF-006** | Evaluate data freshness | Temporal relevance |

## 3.5 Narrative Generation

### Problem

Raw data needs narrative interpretation for human consumption.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-NARR-001** | Generate dataset summary narratives | Human readability |
| **INT-NARR-002** | Explain key findings in plain language | Accessibility |
| **INT-NARR-003** | Summarize anomalies with context | Interpretation |
| **INT-NARR-004** | Provide recommendations | Actionability |

## 3.6 Confidence and Escalation

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-CONF-001** | All agent outputs must include confidence level | Uncertainty transparency |
| **INT-CONF-002** | Low confidence must trigger user clarification | Human intervention |
| **INT-CONF-003** | Confidence thresholds must be configurable | Product flexibility |
| **INT-CONF-004** | Confidence downgrades must be explained | Transparency |

---

# 4. Tools (INT-TOOLS)

> **Maps to**: [BRD-tools.md](../01_brd/BRD-tools.md)

## 4.1 Tool Overview

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-TOOL-001** | Tools perform factual computation only | Determinism |
| **INT-TOOL-002** | Tools must NOT call LLMs directly | Reproducibility |
| **INT-TOOL-003** | Tools must produce deterministic outputs | Audit requirement |
| **INT-TOOL-004** | Same inputs must produce same outputs | Reproducibility |
| **INT-TOOL-005** | Tools must produce evidence items | Traceability |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Tools cannot call LLMs | Tool calls OpenAI API |
| Same inputs produce same outputs | Tool uses random() |
| No external dependencies | Tool fetches from internet |
| Timestamps are only allowed variation | Tool uses current time |

## 4.2 Data Tools

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-DATA-001** | Read CSV datasets | Data source support |
| **INT-DATA-002** | Extract column metadata | Schema understanding |
| **INT-DATA-003** | Extract row data | Data access |
| **INT-DATA-004** | Infer field types (x, y, category) | Smart defaults |
| **INT-DATA-005** | Handle UTF-8 encoding | International support |
| **INT-DATA-006** | Handle quoted CSV fields | Format robustness |

### Tool Summary

| Tool | Function |
|------|----------|
| data_reader | Read CSV, extract columns, rows, field types |
| compute_business_metrics | Aggregate metrics, produce evidence items |

## 4.3 Analysis Tools

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-ANAL-001** | Detect statistical anomalies | Insight discovery |
| **INT-ANAL-002** | Use z-score analysis | Standard methodology |
| **INT-ANAL-003** | Rank anomalies by severity | Prioritization |
| **INT-ANAL-004** | Explain anomaly reasons | Interpretation |
| **INT-ANAL-005** | Support hypothesis testing | Deeper analysis |
| **INT-ANAL-006** | Make hypothesis tests toggleable | User control |
| **INT-ANAL-007** | Identify key metric drivers | Root cause analysis |

### Tool Summary

| Tool | Function |
|------|----------|
| detect_anomalies | Z-score analysis, rank by severity |
| driver_analysis | Identify key metric drivers |
| hypothesis_test_outage | Test data outage hypothesis |
| hypothesis_test_seasonality | Test seasonality hypothesis |

## 4.4 Visualization Tools

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-VIS-001** | Build chart specifications | Visual output |
| **INT-VIS-002** | Support multiple chart types | Flexibility |
| **INT-VIS-003** | Recommend appropriate chart types | Smart defaults |
| **INT-VIS-004** | Use Vega-Lite compatible specs | Standard format |

### Tool Summary

| Tool | Function |
|------|----------|
| build_chart_spec | Generate Vega-Lite spec |
| recommend_chart | Suggest chart type |

## 4.5 Assembly Tools

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-ASM-001** | Assemble decision packets | Primary output |
| **INT-ASM-002** | Assemble business reports | Primary output |
| **INT-ASM-003** | Bundle evidence items | Traceability |
| **INT-ASM-004** | Include all required sections | Completeness |
| **INT-ASM-005** | Validate against schemas | Data integrity |

### Tool Summary

| Tool | Function |
|------|----------|
| assemble_decision_packet | Build DecisionPacket schema |
| assemble_business_report | Build BusinessReport schema |
| assemble_evidence_bundle | Bundle evidence items |
| assemble_insight_card | Build insight cards |

## 4.6 Rendering Tools

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-REND-001** | Render HTML outputs | Web-compatible output |
| **INT-REND-002** | Produce valid HTML5 | Standards compliance |
| **INT-REND-003** | Embed visualizations | Self-contained output |
| **INT-REND-004** | Support PDF export | Alternative format |

### Tool Summary

| Tool | Function |
|------|----------|
| render_business_report_html | Generate HTML output |
| render_decision_packet_html | Generate HTML output |
| export_pdf | Optional PDF export |

---

# 5. Data & Schemas (INT-DATA)

> **Maps to**: [BRD-data.md](../01_brd/BRD-data.md)

## 5.1 Dataset Requirements

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-FMT-001** | Accept CSV format | Standard format |
| **INT-FMT-002** | Support UTF-8 encoding | International support |
| **INT-FMT-003** | Parse standard CSV headers | Schema extraction |
| **INT-FMT-004** | Handle quoted fields | Format robustness |
| **INT-FMT-005** | Handle empty values | Data quality |

### Location Rules

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-LOC-001** | User datasets in staging/input/ | User data isolation |
| **INT-LOC-002** | Built-in datasets in data/ | Product data |
| **INT-LOC-003** | Dataset names resolve to file paths | Abstraction |
| **INT-LOC-004** | Missing datasets produce clear errors | User guidance |

### Built-in Datasets

- branded_cards_transactions — Default demonstration dataset

## 5.2 Schema Requirements

### General Schema Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-SCHEMA-001** | All data structures use Pydantic models | Type safety |
| **INT-SCHEMA-002** | Schemas reject unknown fields | Data integrity |
| **INT-SCHEMA-003** | Schemas validate types | Error prevention |
| **INT-SCHEMA-004** | Use default factories for collections | Safe initialization |

## 5.3 DecisionPacket Schema

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-DP-001** | Include question | Context |
| **INT-DP-002** | Include decision_summary | Primary output |
| **INT-DP-003** | Include confidence_level | Uncertainty |
| **INT-DP-004** | Include assumptions | Transparency |
| **INT-DP-005** | Include limitations | Transparency |
| **INT-DP-006** | Include sections | Structure |
| **INT-DP-007** | Include trace_refs | Audit trail |

### Schema

```
question: str
decision_summary: str
confidence_level: "high" | "medium" | "low"
assumptions: List[str]
limitations: List[str]
sections: List[DecisionSection]
trace_refs: List[Dict]
```

## 5.4 BusinessReport Schema

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-BR-001** | Include title | Identification |
| **INT-BR-002** | Include timestamp | Temporal reference |
| **INT-BR-003** | Include dataset_id | Data source |
| **INT-BR-004** | Include executive_summary | Key takeaways |
| **INT-BR-005** | Include key_findings | Detailed insights |
| **INT-BR-006** | Include visuals | Visual communication |
| **INT-BR-007** | Include anomalies | Issue identification |
| **INT-BR-008** | Include appendix | Supporting detail |

### Schema

```
title: str
generated_at_iso: str
dataset_id: str
executive_summary: List[str]
key_findings: List[Finding]
visuals: List[VisualSpec]
anomalies: List[AnomalyRow]
recommendations: List[str]
appendix: Appendix
```

## 5.5 IntentFrame Schema

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-IF-001** | Include intent_summary | Interpretation |
| **INT-IF-002** | Include confidence_score | Uncertainty |
| **INT-IF-003** | Include blocking_required | Flow control |
| **INT-IF-004** | Include inferred_entities | Extraction |
| **INT-IF-005** | Include inferred_metrics | Extraction |
| **INT-IF-006** | Include blocking_questions | User guidance |

### Schema

```
intent_summary: str
inferred_entities: List[str]
inferred_metrics: List[str]
inferred_time_window: Optional[str]
confidence_score: float
blocking_required: bool
blocking_questions: List[str]
```

## 5.6 Evidence Schema

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EV-001** | Evidence includes dataset_id | Data source |
| **INT-EV-002** | Evidence includes columns | Specific fields |
| **INT-EV-003** | Evidence includes values | Actual data |
| **INT-EV-004** | Evidence is verifiable | Audit requirement |

---

# 6. Outputs & Audit (INT-OUTPUTS)

> **Maps to**: [BRD-outputs.md](../01_brd/BRD-outputs.md)

## 6.1 Primary Output Intent

### Business Report

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OUT-001** | Produce business_report.html | Primary output |
| **INT-OUT-002** | Report must be valid HTML5 | Standards |
| **INT-OUT-003** | Include executive summary | Key takeaways |
| **INT-OUT-004** | Include key findings | Detailed insights |
| **INT-OUT-005** | Include visualizations | Visual communication |
| **INT-OUT-006** | Include anomaly table | Issue identification |
| **INT-OUT-007** | Include recommendations | Actionability |
| **INT-OUT-008** | Include appendix | Supporting detail |

### Decision Packet

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OUT-010** | Produce decision_packet.html | Primary output (viz flow) |
| **INT-OUT-011** | Packet must be valid HTML5 | Standards |
| **INT-OUT-012** | Include question | Context |
| **INT-OUT-013** | Include decision summary | Primary output |
| **INT-OUT-014** | Include confidence level | Uncertainty |
| **INT-OUT-015** | Include evidence sections | Traceability |
| **INT-OUT-016** | Include assumptions | Transparency |
| **INT-OUT-017** | Include limitations | Transparency |

### Output Summary

| Output | Format | Flow |
|--------|--------|------|
| business_report.html | HTML5 | Both |
| decision_packet.html | HTML5 | visualization |

## 6.2 Output Location Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OUTLOC-001** | Outputs written to staging/output/ | Organization |
| **INT-OUTLOC-002** | Create directory if missing | Robustness |
| **INT-OUTLOC-003** | Consistent file naming | Predictability |

## 6.3 Evidence Traceability Intent

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-AUDIT-001** | All claims traceable to evidence | Trust requirement |
| **INT-AUDIT-002** | Evidence includes dataset references | Data source |
| **INT-AUDIT-003** | Evidence includes column references | Specificity |
| **INT-AUDIT-004** | Evidence verifiable against source data | Audit requirement |

### Design Decision

**Evidence-First Architecture**: All outputs must include evidence references.

**Implications**:
- Tools produce evidence_items
- Assemblers include evidence_refs in outputs
- trace_refs link decisions to execution steps

## 6.4 Execution Traceability Intent

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-TRACE-001** | Outputs include trace_refs | Audit trail |
| **INT-TRACE-002** | trace_refs link to execution steps | Step traceability |
| **INT-TRACE-003** | trace_refs include user inputs | Input traceability |
| **INT-TRACE-004** | Execution must be reproducible | Audit requirement |

## 6.5 Transparency Intent

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-TRANS-001** | Outputs include explicit assumptions | Transparency |
| **INT-TRANS-002** | Outputs include explicit limitations | Transparency |
| **INT-TRANS-003** | Confidence levels must be explained | Understanding |
| **INT-TRANS-004** | Downgrade reasons must be documented | Transparency |

## 6.6 Reproducibility Intent

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-REPRO-001** | Same inputs produce same outputs | Audit requirement |
| **INT-REPRO-002** | Timestamps are only allowed variation | Practical necessity |
| **INT-REPRO-003** | No random or non-deterministic operations | Reproducibility |
| **INT-REPRO-004** | Outputs can be regenerated from inputs | Verification |

---

# 7. Product Intelligence & Execution (INT-INTEL)

> **Cross-Cutting Intent**: These requirements close gaps in reasoning depth, iteration, critique, grounding, safe exits, observability, and UX clarity.

## 7.1 Semantic Interpretation Phase

> **Framework Integration**: ADE provides a product-specific semantic adapter that integrates with MASTER's semantic interpretation phase.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-SEM-001** | ADE SHALL provide a ProductSemanticAdapter that interprets analyst questions into structured semantic envelopes | Domain-specific interpretation |
| **INT-SEM-002** | Semantic interpretation SHALL extract intent_type (DESCRIBE_DATA, COMPARE_PERIODS, TREND_ANALYSIS, ANOMALY_REVIEW, OPEN_ENDED_ANALYSIS) | Intent classification |
| **INT-SEM-003** | Semantic interpretation SHALL extract entities: metrics, time_windows, dataset_references, filter_conditions | Entity extraction |
| **INT-SEM-004** | Semantic interpretation SHALL produce confidence score (0.0-1.0) indicating interpretation certainty | Uncertainty quantification |
| **INT-SEM-005** | Low confidence (< 0.8 for ADE) SHALL trigger ASK_USER next action | Clarification threshold |
| **INT-SEM-006** | Semantic validation SHALL check for required fields based on intent_type | Domain validation |
| **INT-SEM-007** | Missing required fields SHALL generate clarifying_questions | User guidance |
| **INT-SEM-008** | Ambiguous inputs SHALL be captured in ambiguities list | Transparency |
| **INT-SEM-009** | Semantic interpretation SHALL run BEFORE planning phase | Correct ordering |
| **INT-SEM-010** | Semantic interpretation SHALL be traced with structured events | Observability |

### Intent Type Requirements

| Intent Type | Required Entities | Optional Entities |
|-------------|-------------------|-------------------|
| DESCRIBE_DATA | dataset | metric_focus |
| COMPARE_PERIODS | dataset, time_windows (2+) | metrics |
| TREND_ANALYSIS | dataset, time_axis | metrics, trend_type |
| ANOMALY_REVIEW | dataset | threshold, metric_focus |
| OPEN_ENDED_ANALYSIS | dataset | any |

### Validation Rules

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-SEM-VAL-001** | TREND_ANALYSIS without time_axis SHALL trigger clarifying question | Missing required field |
| **INT-SEM-VAL-002** | COMPARE_PERIODS with single time_window SHALL trigger clarifying question | Insufficient data |
| **INT-SEM-VAL-003** | Dataset references SHALL be validated against available datasets | Data availability |
| **INT-SEM-VAL-004** | Metric references SHALL be validated against dataset schema when known | Schema validation |
| **INT-SEM-VAL-005** | Validation failures SHALL produce violations list with specific field references | Actionable errors |

### NextAction Mapping

| Condition | NextAction | User Experience |
|-----------|------------|-----------------|
| Confidence ≥ 0.8, valid | CONTINUE | Proceed to planning |
| Confidence < 0.8, valid | ASK_USER | Request clarification |
| Invalid (missing fields) | ASK_USER | Request missing inputs |
| Unresolvable ambiguity | ABORT | Clear failure message |
| High-risk interpretation | NEEDS_APPROVAL | Semantic approval gate |

---

## 7.2 Multi-Pass Reasoning

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-INTEL-001** | Product SHALL reason using a multi-stage reasoning ladder rather than single-pass analysis | Depth over speed |
| **INT-INTEL-002** | Reasoning SHALL progress through explicit stages: interpretation, proposal, gated execution, critique, and finalization | Structured reasoning |
| **INT-INTEL-003** | Each reasoning cycle SHALL be bounded by explicit limits (iterations, tools, tokens, time) | Governance enforcement |
| **INT-INTEL-004** | System SHALL track sufficiency state across cycles (what is known, unknown, blocked) | State awareness |
| **INT-INTEL-005** | Final outputs SHALL explicitly state why reasoning stopped (sufficient, budget exhausted, missing inputs, or conflict) | Transparency |

## 7.3 Mandatory Critique

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-CRIT-001** | Product SHALL execute a critique stage before finalizing any decision or report | Quality gate |
| **INT-CRIT-002** | Critique SHALL identify missing evidence, weak evidence, unsupported claims, and overreach | Evidence validation |
| **INT-CRIT-003** | Critique SHALL be able to downgrade confidence and record downgrade reasons | Honest uncertainty |
| **INT-CRIT-004** | Critique SHALL NEVER execute tools, route flows, or override orchestrator policies | Advisory boundary |
| **INT-CRIT-005** | Blocking critique findings SHALL force either user clarification (HITL) or a safe abort | Safe escalation |

## 7.4 Evidence-First Grounding via Context Packs

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-CTX-001** | Product SHALL construct a Context Pack after ingestion and before planning or reasoning | Grounding first |
| **INT-CTX-002** | Context Packs SHALL include dataset profile, coverage, missingness, data quality flags, and metric availability | Comprehensive context |
| **INT-CTX-003** | All computed statistics SHALL be backed by Evidence Items included in the Context Pack | Evidence-backed |
| **INT-CTX-004** | Advisory reasoning SHALL reference Context Pack artifacts, not ungrounded free text | Grounded reasoning |

## 7.5 Advisory Tool Selection

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-TOOLSEL-001** | Tool choice SHALL be surfaced as an advisory recommendation, not embedded silently in plans | Transparency |
| **INT-TOOLSEL-002** | System MAY produce ranked tool suggestions with rationales and exclusions | Informed choice |
| **INT-TOOLSEL-003** | Orchestrator SHALL remain the sole authority to approve or reject tool execution based on policy and budgets | Governance boundary |
| **INT-TOOLSEL-004** | Advisory tool suggestions SHALL NOT force execution | Advisory only |

## 7.6 Explicit Failure Modes and Safe Termination

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-TERM-001** | Product SHALL support explicit terminal outcomes: SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT | Clear outcomes |
| **INT-TERM-002** | PARTIAL_SUCCESS outputs SHALL include limitations and unresolved gaps | Honest outputs |
| **INT-TERM-003** | ABORT outcomes SHALL include reason codes, blocking conditions, and recommended next actions | Actionable failures |
| **INT-TERM-004** | ASK_USER outcomes SHALL be used when missing inputs are resolvable via clarification | HITL integration |

## 7.7 Output Quality Gates

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-QUAL-001** | All key findings or assertions SHALL be backed by at least one evidence reference | Evidence requirement |
| **INT-QUAL-002** | Executive summaries SHALL include scope, key result, confidence, and primary limitation | Completeness |
| **INT-QUAL-003** | Recommendations SHALL only be emitted when evidence-supported; otherwise they SHALL be omitted | No speculation |
| **INT-QUAL-004** | Low-confidence outputs SHALL include a "Next Inputs Needed" section | User guidance |

## 7.8 Reproducibility and Version Transparency

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-VER-001** | Every output SHALL include product version, flow version, schema version, and tool versions | Version tracking |
| **INT-VER-002** | Outputs SHALL record dataset hash (or checksum) and input parameter hash | Input traceability |
| **INT-VER-003** | Non-deterministic dependencies SHALL be disallowed or explicitly version-pinned | Reproducibility |

## 7.9 Informed User Review and Approval

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-REVIEW-001** | Plan proposals SHALL clearly present objective, steps, expected evidence, assumptions, risks, and estimated runtime | Informed consent |
| **INT-REVIEW-002** | Users SHALL be able to approve plans with constraints (time window, iteration caps, disabled tests) | User control |
| **INT-REVIEW-003** | Replans after rejection SHALL explicitly show what changed and why | Transparency |

## 7.10 Knowing When to Stop

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-STOP-001** | Product SHALL prioritize knowing when not to proceed over producing forced outputs | Safety first |
| **INT-STOP-002** | Low signal, conflicting evidence, or insufficient data SHALL result in safe exits rather than speculative conclusions | No forced outputs |

## 7.11 Thin, Declarative, Framework-Aligned Products

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-ALIGN-001** | All reasoning, iteration, critique, and governance patterns SHALL rely on framework-provided primitives | Framework leverage |
| **INT-ALIGN-002** | If a product needs to re-implement these mechanisms, it indicates a framework gap—not a product feature | Gap detection |

## 7.12 Framework Reliance Invariant (P0)

> **Critical Constraint**: This prevents silent erosion of the thick framework / thin product architecture.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-FRI-001** | Product SHALL NOT re-implement orchestration logic already provided by MASTER framework | No shadow orchestration |
| **INT-FRI-002** | Product SHALL NOT re-implement iteration control already provided by MASTER framework | No shadow loops |
| **INT-FRI-003** | Product SHALL NOT re-implement reasoning ladder semantics already provided by MASTER framework | No shadow reasoning |
| **INT-FRI-004** | Product SHALL NOT bypass framework governance hooks | Governance integrity |
| **INT-FRI-005** | Any product requirement that cannot be satisfied using existing framework primitives SHALL be treated as a framework gap and escalated, not worked around | Gap escalation |

### Violation Examples

| Violation | Why It's Wrong |
|-----------|----------------|
| Product adds "just a small loop" for retries | Re-implements iteration control |
| Product does "local reasoning pass" before calling agent | Re-implements reasoning ladder |
| Product calls tools directly without orchestrator | Bypasses governance hooks |
| Product implements custom error recovery | Re-implements error policy |

## 7.13 Decision Authority Boundary (P0)

> **Critical Constraint**: This protects ADE's positioning as decision-support, not decision-making, which is essential for regulated environments.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-DAB-001** | ADE SHALL produce decision-support artifacts, not autonomous decisions | Human authority preserved |
| **INT-DAB-002** | Final business decisions SHALL always remain with a human or downstream governed system | Accountability clarity |
| **INT-DAB-003** | DecisionPackets represent recommendations with evidence and confidence, not authoritative outcomes | Semantic precision |
| **INT-DAB-004** | ADE outputs SHALL be labeled as "recommendations" or "findings", never as "decisions" or "actions" | Language discipline |
| **INT-DAB-005** | No ADE output SHALL trigger downstream actions without explicit human or system approval | Action boundary |

### Terminology Discipline

| Term | ADE MAY Use | ADE SHALL NOT Use |
|------|-------------|-------------------|
| Output type | Recommendation, Finding, Insight | Decision, Ruling, Verdict |
| Confidence | "High confidence recommendation" | "Decided with high confidence" |
| Action | "Recommended next steps" | "Actions to be taken" |

## 7.14 No Runtime Learning Invariant

> **Strategic Constraint**: This locks ADE's behavior to governed evolution only, preventing scope creep into adaptive systems.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-NRL-001** | ADE SHALL NOT modify its behavior, thresholds, or logic at runtime based on prior executions | No implicit adaptation |
| **INT-NRL-002** | ADE SHALL NOT persist learned patterns, weights, or preferences across runs | No hidden state |
| **INT-NRL-003** | All learning and evolution SHALL occur through the governed intent → BRD → implementation lifecycle | Governed evolution only |
| **INT-NRL-004** | Run N SHALL produce identical outputs to Run 1 given identical inputs | Run independence |

### What This Prevents

| Prevented Behavior | Why It's Prevented |
|--------------------|-------------------|
| "ADE learns from analyst feedback" | Creates ungoverned behavior drift |
| "ADE improves thresholds over time" | Makes reproducibility impossible |
| "ADE remembers user preferences" | Hidden state violates determinism |
| "ADE adapts to data patterns" | Breaks audit trail requirements |

### How Evolution Happens Instead

```
Feedback → Intent Update → BRD Update → Code Change → Version Bump → Deployment
```

All changes are:
- Explicit (documented in intent)
- Versioned (traceable)
- Governed (reviewed and approved)
- Reproducible (same version = same behavior)

---

# 8. Acceptance Criteria

ADE is successful when:

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| All outputs pass Pydantic validation | 100% | Schema validation |
| All claims have evidence_refs | 100% | Output inspection |
| Plans require approval | 100% | Flow enforcement |
| Hypothesis checks are toggleable | Yes | User preference |
| Same inputs produce same outputs | Yes | Reproducibility test |
| Confidence level present in all packets | 100% | Output inspection |
| Intent→BRD traceability | 100% | Document review |
| Critique stage executes before finalization | 100% | Flow inspection |
| Outputs include version metadata | 100% | Output inspection |
| Safe termination on insufficient data | Yes | Behavior test |
| Context Pack constructed before reasoning | 100% | Flow enforcement |
| No product re-implementation of framework primitives | 0 violations | Code review |
| All outputs labeled as recommendations/findings | 100% | Output inspection |
| No runtime learning or state persistence | 0 violations | Behavior test |
| Semantic interpretation runs before planning | 100% | Flow enforcement |
| Low confidence triggers ASK_USER | Yes | Behavior test |
| Semantic trace events emitted | 100% | Observability inspection |
| Product semantic adapter provides ADE-specific interpretation | Yes | Adapter implementation |

---

# 9. Derived Documents

This intent document drives:

| Document | Derivation |
|----------|------------|
| [Vision.md](Vision.md) | Expands intent into product philosophy |
| [BRD-overview.md](../01_brd/BRD-overview.md) | INT-OVERVIEW-* → BRD objectives and scope |
| [BRD-flows.md](../01_brd/BRD-flows.md) | INT-FLOWS-*, INT-V1-*, INT-VIZ-* → Flow requirements |
| [BRD-agents.md](../01_brd/BRD-agents.md) | INT-AGT-*, INT-INTENT-*, INT-PLAN-* → Agent requirements |
| [BRD-tools.md](../01_brd/BRD-tools.md) | INT-TOOL-*, INT-DATA-*, INT-ANAL-* → Tool requirements |
| [BRD-data.md](../01_brd/BRD-data.md) | INT-FMT-*, INT-SCHEMA-*, INT-DP-* → Data requirements |
| [BRD-outputs.md](../01_brd/BRD-outputs.md) | INT-OUT-*, INT-AUDIT-*, INT-TRACE-* → Output requirements |
| All BRDs (cross-cutting) | INT-SEM-*, INT-INTEL-*, INT-CRIT-*, INT-CTX-*, INT-TERM-*, INT-QUAL-*, INT-VER-*, INT-STOP-*, INT-ALIGN-*, INT-FRI-*, INT-DAB-*, INT-NRL-* → Semantic, intelligence, execution, and invariant requirements |

---

# 10. Summary Statement

> **We are building ADE because analysts need a way to produce audit-ready analytical decisions from data without sacrificing evidence traceability, reproducibility, or transparency. Questions should drive analysis. Evidence should back claims. Confidence should be explicit. And humans should approve plans before execution.**
