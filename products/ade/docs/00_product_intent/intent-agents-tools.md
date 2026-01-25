# ADE Developer Intent

> **Document**: Product Developer Intent  
> **Product**: Analytical Decision Engine (ADE)  
> **Platform**: MASTER — Managed AI Systems for Trusted Execution & Reasoning  
> **Last Updated**: 2026-01-21  
> **Status**: V1.3 Release

---

## Version Control

| Version | Date | Changes |
|---------|------|--------|
| 1.3 | 2026-01-21 | Added INT-AGENTS-001 (agent as specialist), INT-TOOL-006 through INT-TOOL-013 (tool binding, discovery, eligibility) |
| 1.2 | 2026-01-18 | Initial sections |
| 1.1 | 2026-01-13 | Initial release |

---

## Scope

This file contains sections 3, 4 from the ADE Developer Intent.

---

# 3. Agents (INT-AGENTS)

> **Maps to**: [BRD-agents.md](../01_brd/BRD-agents.md)

## 3.1 Agent Overview

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-AGENTS-001** | ADE SHALL treat agents as specialists performing scoped tasks (e.g., "summarize risk signals", "interpret intent"): orchestrator SHALL control sequencing and authority, agents SHALL NOT control flow or make autonomous decisions — Agents as specialists | — | 2026-01-21 | V1.3 | Source: BULLET-15 |

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

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-INTENT-001** | Extract intent summary from user question — Structured understanding | — | 2026-01-13 | V1.1 | — |
| **INT-INTENT-002** | Identify referenced datasets — Data source identification | — | 2026-01-13 | V1.1 | — |
| **INT-INTENT-003** | Identify referenced metrics — Analysis focus | — | 2026-01-13 | V1.1 | — |
| **INT-INTENT-004** | Identify time window constraints — Temporal scoping | — | 2026-01-13 | V1.1 | — |
| **INT-INTENT-005** | Provide confidence score (0-1) — Uncertainty quantification | — | 2026-01-13 | V1.1 | — |
| **INT-INTENT-006** | Detect when clarification is needed — Avoid misinterpretation | — | 2026-01-13 | V1.1 | — |
| **INT-INTENT-007** | Generate clarifying questions — User guidance | — | 2026-01-13 | V1.1 | — |

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

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-PLAN-001** | Produce deterministic plans — Reproducibility | — | 2026-01-13 | V1.1 | — |
| **INT-PLAN-002** | Include all required analysis steps — Completeness | — | 2026-01-13 | V1.1 | — |
| **INT-PLAN-003** | Include tool flags for conditional execution — Flexibility | — | 2026-01-13 | V1.1 | — |
| **INT-PLAN-004** | Same inputs must produce same plan — Determinism | — | 2026-01-13 | V1.1 | — |
| **INT-PLAN-005** | Generate human-readable plan summary — Informed approval | — | 2026-01-13 | V1.1 | — |
| **INT-PLAN-006** | Estimate step count — User visibility | — | 2026-01-13 | V1.1 | — |
| **INT-PLAN-007** | Estimate execution cost — Cost transparency | — | 2026-01-13 | V1.1 | — |
| **INT-PLAN-008** | Require approval for non-trivial plans — Human oversight | — | 2026-01-13 | V1.1 | — |

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

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-SUFF-001** | Assess data sufficiency before analysis — Quality gate | — | 2026-01-13 | V1.1 | — |
| **INT-SUFF-002** | Provide confidence level (high/medium/low) — Uncertainty communication | — | 2026-01-13 | V1.1 | — |
| **INT-SUFF-003** | Explain confidence downgrades — Transparency | — | 2026-01-13 | V1.1 | — |
| **INT-SUFF-004** | Evaluate row count sufficiency — Statistical validity | — | 2026-01-13 | V1.1 | — |
| **INT-SUFF-005** | Evaluate column completeness — Data quality | — | 2026-01-13 | V1.1 | — |
| **INT-SUFF-006** | Evaluate data freshness — Temporal relevance | — | 2026-01-13 | V1.1 | — |

## 3.5 Narrative Generation

### Problem

Raw data needs narrative interpretation for human consumption.

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-NARR-001** | Generate dataset summary narratives — Human readability | — | 2026-01-13 | V1.1 | — |
| **INT-NARR-002** | Explain key findings in plain language — Accessibility | — | 2026-01-13 | V1.1 | — |
| **INT-NARR-003** | Summarize anomalies with context — Interpretation | — | 2026-01-13 | V1.1 | — |
| **INT-NARR-004** | Provide recommendations — Actionability | — | 2026-01-13 | V1.1 | — |
| **INT-NARR-005** | User-facing explanations SHALL be derived from platform decision records, not regenerated narratives — Preserve decision provenance | — | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |

## 3.6 Confidence and Escalation

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-CONF-001** | All agent outputs must include confidence level — Uncertainty transparency | — | 2026-01-13 | V1.1 | — |
| **INT-CONF-002** | Low confidence must trigger user clarification — Human intervention | — | 2026-01-13 | V1.1 | — |
| **INT-CONF-003** | Confidence thresholds must be configurable — Product flexibility | — | 2026-01-13 | V1.1 | — |
| **INT-CONF-004** | Confidence downgrades must be explained — Transparency | — | 2026-01-13 | V1.1 | — |
| **INT-CONF-005** | ADE SHALL respect platform-defined confidence thresholds and gates when requesting execution, escalation, or human input — Align product gating with platform policy | — | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |

---

# 4. Tools (INT-TOOLS)

> **Maps to**: [BRD-tools.md](../01_brd/BRD-tools.md)

## 4.1 Tool Overview

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-TOOL-001** | Tools perform factual computation only — Determinism | — | 2026-01-13 | V1.1 | — |
| **INT-TOOL-002** | Tools must NOT call LLMs directly — Reproducibility | — | 2026-01-13 | V1.1 | — |
| **INT-TOOL-003** | Tools must produce deterministic outputs — Audit requirement | — | 2026-01-13 | V1.1 | — |
| **INT-TOOL-004** | Same inputs must produce same outputs — Reproducibility | — | 2026-01-13 | V1.1 | — |
| **INT-TOOL-005** | Tools must produce evidence items — Traceability | — | 2026-01-13 | V1.1 | — |
| **INT-TOOL-006** | ADE SHALL bind tool selection directly to declared intent: analytical tools (anomaly detection, aggregation, visualization) SHALL only be invoked if explicitly justified by the resolved intent and constraints — Intent-bound tool selection | INT-TOOL-001 | 2026-01-21 | V1.3 | Source: BULLET-04 |
| **INT-TOOL-007** | ADE SHALL reject tool execution based on mere availability: tools SHALL NOT be selected simply because they exist; every tool invocation SHALL map to an intent dimension and be auditable — No availability-based selection | INT-TOOL-006 | 2026-01-21 | V1.3 | Source: BULLET-05 |
| **INT-TOOL-008** | ADE SHALL never hard-code tool lists: ADE SHALL request eligible tools from the platform per run and use only what is surfaced — Dynamic tool discovery | INT-TOOL-006 | 2026-01-21 | V1.3 | Source: BULLET-11 |
| **INT-TOOL-009** | ADE SHALL bind tools to intent-derived steps: tools SHALL be invoked because intent demands them, not because they exist or are convenient — Intent-driven invocation | INT-TOOL-006 | 2026-01-21 | V1.3 | Source: BULLET-12 |
| **INT-TOOL-010** | ADE SHALL declare tool intent at call time: each tool invocation SHALL specify "why this tool" and "what intent dimension it satisfies" — Documented tool rationale | INT-TOOL-009 | 2026-01-21 | V1.3 | Source: BULLET-13 |
| **INT-TOOL-011** | ADE SHALL fail if no eligible tools exist for the resolved intent: if intent cannot be satisfied with available tools, ADE SHALL stop, explain, and ask user — Fail on tool unavailability | INT-TOOL-008 | 2026-01-21 | V1.3 | Source: BULLET-14 |
| **INT-TOOL-012** | ADE SHALL never infer permissions: if a tool is not discoverable from the platform, it is not usable; ADE SHALL NOT use fallback logic that bypasses platform discovery — No permission inference | INT-TOOL-008 | 2026-01-21 | V1.3 | Source: BULLET-16 |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Tools cannot call LLMs | Tool calls OpenAI API |
| Same inputs produce same outputs | Tool uses random() |
| No external dependencies | Tool fetches from internet |
| Timestamps are only allowed variation | Tool uses current time |

## 4.2 Data Tools

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-DATA-001** | Read CSV datasets — Data source support | — | 2026-01-13 | V1.1 | — |
| **INT-DATA-002** | Extract column metadata — Schema understanding | — | 2026-01-13 | V1.1 | — |
| **INT-DATA-003** | Extract row data — Data access | — | 2026-01-13 | V1.1 | — |
| **INT-DATA-004** | Infer field types (x, y, category) — Smart defaults | — | 2026-01-13 | V1.1 | — |
| **INT-DATA-005** | Handle UTF-8 encoding — International support | — | 2026-01-13 | V1.1 | — |
| **INT-DATA-006** | Handle quoted CSV fields — Format robustness | — | 2026-01-13 | V1.1 | — |

### Tool Summary

| Tool | Function |
|------|----------|
| data_reader | Read CSV, extract columns, rows, field types |
| compute_business_metrics | Aggregate metrics, produce evidence items |

## 4.3 Analysis Tools

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-ANAL-001** | Detect statistical anomalies — Insight discovery | — | 2026-01-13 | V1.1 | — |
| **INT-ANAL-002** | Use z-score analysis — Standard methodology | — | 2026-01-13 | V1.1 | — |
| **INT-ANAL-003** | Rank anomalies by severity — Prioritization | — | 2026-01-13 | V1.1 | — |
| **INT-ANAL-004** | Explain anomaly reasons — Interpretation | — | 2026-01-13 | V1.1 | — |
| **INT-ANAL-005** | Support hypothesis testing — Deeper analysis | — | 2026-01-13 | V1.1 | — |
| **INT-ANAL-006** | Make hypothesis tests toggleable — User control | — | 2026-01-13 | V1.1 | — |
| **INT-ANAL-007** | Identify key metric drivers — Root cause analysis | — | 2026-01-13 | V1.1 | — |

### Tool Summary

| Tool | Function |
|------|----------|
| detect_anomalies | Z-score analysis, rank by severity |
| driver_analysis | Identify key metric drivers |
| hypothesis_test_outage | Test data outage hypothesis |
| hypothesis_test_seasonality | Test seasonality hypothesis |

## 4.4 Visualization Tools

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-VIS-001** | Build chart specifications — Visual output | — | 2026-01-13 | V1.1 | — |
| **INT-VIS-002** | Support multiple chart types — Flexibility | — | 2026-01-13 | V1.1 | — |
| **INT-VIS-003** | Recommend appropriate chart types — Smart defaults | — | 2026-01-13 | V1.1 | — |
| **INT-VIS-004** | Use Vega-Lite compatible specs — Standard format | — | 2026-01-13 | V1.1 | — |

### Tool Summary

| Tool | Function |
|------|----------|
| build_chart_spec | Generate Vega-Lite spec |
| recommend_chart | Suggest chart type |

## 4.5 Assembly Tools

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-ASM-001** | Assemble decision packets — Primary output | — | 2026-01-13 | V1.1 | — |
| **INT-ASM-002** | Assemble business reports — Primary output | — | 2026-01-13 | V1.1 | — |
| **INT-ASM-003** | Bundle evidence items — Traceability | — | 2026-01-13 | V1.1 | — |
| **INT-ASM-004** | Include all required sections — Completeness | — | 2026-01-13 | V1.1 | — |
| **INT-ASM-005** | Validate against schemas — Data integrity | — | 2026-01-13 | V1.1 | — |

### Tool Summary

| Tool | Function |
|------|----------|
| assemble_decision_packet | Build DecisionPacket schema |
| assemble_business_report | Build BusinessReport schema |
| assemble_evidence_bundle | Bundle evidence items |
| assemble_insight_card | Build insight cards |

## 4.6 Rendering Tools

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| **INT-REND-001** | Render HTML outputs — Web-compatible output | — | 2026-01-13 | V1.1 | — |
| **INT-REND-002** | Produce valid HTML5 — Standards compliance | — | 2026-01-13 | V1.1 | — |
| **INT-REND-003** | Embed visualizations — Self-contained output | — | 2026-01-13 | V1.1 | — |
| **INT-REND-004** | Support PDF export — Alternative format | — | 2026-01-13 | V1.1 | — |

### Tool Summary

| Tool | Function |
|------|----------|
| render_business_report_html | Generate HTML output |
| render_decision_packet_html | Generate HTML output |
| export_pdf | Optional PDF export |

---
