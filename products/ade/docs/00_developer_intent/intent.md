# ADE Developer Intent

> **Document**: Product Developer Intent  
> **Product**: Analytical Decision Engine (ADE)  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release

---

## Purpose

This document captures the original developer intent behind ADE. It is the seed from which the BRD, techspec, and all downstream specifications were derived.

**Developer Intent is the only required manual input. Everything else flows from here.**

---

## 1. The Problem We're Solving

### 1.1 Analyst Pain Points

Analysts struggle to produce audit-ready analytical decisions because:

1. **Manual analysis is slow** — Extracting insights from data requires significant time and expertise
2. **Evidence is scattered** — Claims are made without clear traceability to source data
3. **Confidence is subjective** — No standardized way to express certainty in findings
4. **Reports lack structure** — Ad-hoc formats make comparison and audit difficult
5. **Reproducibility is impossible** — Same question on same data may yield different results

### 1.2 What Doesn't Exist Today

There is no tool that:
- Accepts **free-text analyst questions** and produces structured outputs
- Provides **evidence-backed decisions** with full traceability
- Generates **audit-ready reports** with confidence levels and limitations
- Ensures **deterministic analysis** where same inputs always produce same outputs
- Supports **human oversight** through plan approval before execution

---

## 2. What We Want to Build

### 2.1 Core Intent

> **Build an analytical decision engine that transforms analyst questions and CSV datasets into structured, audit-ready business outputs with evidence, confidence, and traceability.**

### 2.2 Key Properties

| Property | Intent |
|----------|--------|
| **Evidence-based** | Every claim traceable to source data |
| **Deterministic** | Same inputs always produce same outputs |
| **Transparent** | Confidence levels, assumptions, limitations explicit |
| **Audit-ready** | Full trace references for compliance review |
| **Human-in-the-loop** | Plan approval required before execution |
| **Semantic** | Interpret analyst intent from free-text questions |

### 2.3 The One-Liner

> ADE accepts analyst questions and CSV datasets to produce audit-ready analytical decisions with evidence, confidence, and traceability.

---

## 3. Target Users

### 3.1 Primary: Analysts

Business and data analysts who need to answer questions about data.

**They need:**
- Ask questions in natural language
- Get structured, professional reports
- Trust the results with clear evidence

**They get:**
- Free-text question input
- Business reports with evidence references
- Confidence levels and limitations disclosed

### 3.2 Secondary: Decision Makers

Executives and managers who consume analytical outputs.

**They need:**
- Clear recommendations
- Confidence in findings
- Ability to trace claims to evidence

**They get:**
- Decision packets with audit trails
- Executive summaries
- Evidence-backed key findings

### 3.3 Tertiary: Auditors

Compliance and audit teams who verify analytical integrity.

**They need:**
- Complete traceability
- Reproducible results
- Documented assumptions

**They get:**
- trace_refs linking decisions to steps
- evidence_refs linking claims to data
- Explicit assumptions and limitations

---

## 4. Constraints (Non-Negotiable)

### 4.1 Determinism Constraints

| Constraint | Rationale |
|------------|-----------|
| Tools cannot call LLMs | Ensures reproducible computation |
| Same inputs produce same outputs | Audit requirement |
| No random variations | Reproducibility |
| Timestamps are only allowed variation | Practical necessity |

### 4.2 Evidence Constraints

| Constraint | Rationale |
|------------|-----------|
| All claims have evidence_refs | Traceability requirement |
| Evidence includes dataset_id and columns | Verification capability |
| trace_refs link to execution steps | Audit trail |
| Assumptions and limitations explicit | Transparency |

### 4.3 Governance Constraints

| Constraint | Rationale |
|------------|-----------|
| Plans require approval | Human oversight |
| Confidence levels mandatory | Transparency |
| Schema validation enforced | Data integrity |
| Flows use suggest_only autonomy | Framework compliance |

---

## 5. What Success Looks Like

### 5.1 For Analysts

- Ask a question in **plain English**
- Get a **structured business report** in < 5 minutes
- Trust findings with **clear evidence trails**
- Understand **confidence and limitations**

### 5.2 For Decision Makers

- **Executive summary** highlights key insights
- **Recommendations** are specific and actionable
- **Confidence level** indicates reliability
- **Visualizations** communicate findings clearly

### 5.3 For Auditors

- **100% evidence traceability** — every claim linked to data
- **Reproducible results** — same inputs, same outputs
- **Full trace references** — execution steps documented
- **Explicit assumptions** — no hidden dependencies

---

## 6. What We're NOT Building

| Non-Goal | Why |
|----------|-----|
| BI dashboarding platform | Decision packets are primary output |
| Live database connector | CSV focus for MVP |
| Multi-dataset joins | Single dataset per analysis |
| Streaming analysis | Batch processing only |
| Dynamic flow mutation | Deterministic flows only |
| Automatic tool discovery | Explicit tool configuration |

---

## 7. Key Design Decisions

### 7.1 Two Workflows

**Decision**: Provide two entry points for different use cases.

| Flow | Entry Point | Use Case |
|------|-------------|----------|
| ade_v1 | Question/prompt | Analyst has a question |
| visualization | Dataset | Analyst has data to explore |

### 7.2 Semantic Interpretation

**Decision**: Interpret free-text questions into structured intents.

**Intent Taxonomy**:
- DESCRIBE_DATA — Summarize dataset characteristics
- COMPARE_PERIODS — Compare metrics across time periods
- TREND_ANALYSIS — Identify trends over time
- ANOMALY_REVIEW — Detect and explain anomalies
- OPEN_ENDED_ANALYSIS — Exploratory analysis

**Implications**:
- Intent classification is deterministic (pattern matching, no LLM)
- Missing fields trigger clarifying questions
- Confidence scores guide user interaction

### 7.3 Evidence-First Architecture

**Decision**: All outputs must include evidence references.

**Implications**:
- Tools produce evidence_items
- Assemblers include evidence_refs in outputs
- trace_refs link decisions to execution steps

### 7.4 Plan Approval Gate

**Decision**: Users must approve plans before execution.

**Implications**:
- plan_proposal_agent generates approval requests
- Plans show estimated steps and cost
- Users can approve, reject, or request changes
- Rejection triggers replanning

### 7.5 Output Formats

**Decision**: HTML outputs with embedded visualizations.

| Output | Format | Flow |
|--------|--------|------|
| business_report.html | HTML5 | Both |
| decision_packet.html | HTML5 | visualization |

---

## 8. Agents and Their Roles

| Agent | Role | Advisory Function |
|-------|------|-------------------|
| intent_agent | Interpret questions | Extract intent, entities, metrics, time windows |
| plan_agent | Create analysis plans | Generate deterministic step sequence |
| plan_proposal_agent | Request approval | Summarize plan for human review |
| planning_agent | Handle replanning | Interpret dataset context, recover from rejection |
| sufficiency_evaluator | Assess data quality | Evaluate row count, completeness, freshness |
| dashboard_agent | Generate narratives | Summarize dataset characteristics |

**All agents are advisory only — they propose, never execute.**

---

## 9. Tools and Their Functions

### 9.1 Data Tools

| Tool | Function |
|------|----------|
| data_reader | Read CSV, extract columns, rows, field types |
| compute_business_metrics | Aggregate metrics, produce evidence items |

### 9.2 Analysis Tools

| Tool | Function |
|------|----------|
| detect_anomalies | Z-score analysis, rank by severity |
| driver_analysis | Identify key metric drivers |
| hypothesis_test_* | Test outage/seasonality hypotheses |

### 9.3 Assembly Tools

| Tool | Function |
|------|----------|
| assemble_decision_packet | Build DecisionPacket schema |
| assemble_business_report | Build BusinessReport schema |
| assemble_evidence_bundle | Bundle evidence items |

### 9.4 Rendering Tools

| Tool | Function |
|------|----------|
| render_business_report_html | Generate HTML output |
| render_decision_packet_html | Generate HTML output |
| export_pdf | Optional PDF export |

**All tools are deterministic — no LLM calls.**

---

## 10. Schemas (Key Structures)

### 10.1 DecisionPacket

```
question: str
decision_summary: str
confidence_level: "high" | "medium" | "low"
assumptions: List[str]
limitations: List[str]
sections: List[DecisionSection]
trace_refs: List[Dict]
```

### 10.2 BusinessReport

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

### 10.3 IntentFrame

```
intent_summary: str
inferred_entities: List[str]
inferred_metrics: List[str]
inferred_time_window: Optional[str]
confidence_score: float
blocking_required: bool
blocking_questions: List[str]
```

---

## 11. Acceptance Criteria

ADE is successful when:

| Criterion | Target |
|-----------|--------|
| All outputs pass Pydantic validation | 100% |
| All claims have evidence_refs | 100% |
| Plans require approval | 100% |
| Hypothesis checks are toggleable | Yes |
| Same inputs produce same outputs | Yes |
| Confidence level present in all packets | 100% |

---

## 12. Derived Documents

This intent document drives:

| Document | Derivation |
|----------|------------|
| [Vision.md](Vision.md) | Expands intent into product philosophy |
| [BRD-overview.md](../01_brd/BRD-overview.md) | Product objectives and scope |
| [BRD-flows.md](../01_brd/BRD-flows.md) | Flow requirements |
| [BRD-agents.md](../01_brd/BRD-agents.md) | Agent and semantic interpretation requirements |
| [BRD-tools.md](../01_brd/BRD-tools.md) | Tool requirements |
| [BRD-data.md](../01_brd/BRD-data.md) | Data and schema requirements |
| [BRD-outputs.md](../01_brd/BRD-outputs.md) | Output and audit requirements |

---

## 13. Summary Statement

> **We are building ADE because analysts need a way to produce audit-ready analytical decisions from data without sacrificing evidence traceability, reproducibility, or transparency. Questions should drive analysis. Evidence should back claims. Confidence should be explicit. And humans should approve plans before execution.**
