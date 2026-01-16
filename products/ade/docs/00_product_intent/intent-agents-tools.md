# ADE Developer Intent

> **Document**: Product Developer Intent  
> **Product**: Analytical Decision Engine (ADE)  
> **Platform**: MASTER — Managed AI Systems for Trusted Execution & Reasoning  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release

---

## Scope

This file contains sections 3, 4 from the ADE Developer Intent.

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

