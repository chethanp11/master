# ADE Developer Intent

> **Document**: Product Developer Intent  
> **Product**: Analytical Decision Engine (ADE)  
> **Platform**: MASTER — Managed AI Systems for Trusted Execution & Reasoning  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release

---

## Scope

This file contains sections 7, 8, 9, 10 from the ADE Developer Intent.

---

# 7. Product Intelligence & Execution (INT-INTEL)

> **Cross-Cutting Intent**: These requirements close gaps in reasoning depth, iteration, critique, grounding, observability, and UX clarity.

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
| [BRD-agents.md](../01_brd/BRD-agents.md) | INT-INTENT-*, INT-PLAN-* → Agent requirements |
| [BRD-tools.md](../01_brd/BRD-tools.md) | INT-TOOL-*, INT-DATA-*, INT-ANAL-* → Tool requirements |
| [BRD-data.md](../01_brd/BRD-data.md) | INT-FMT-*, INT-SCHEMA-*, INT-DP-* → Data requirements |
| [BRD-outputs.md](../01_brd/BRD-outputs.md) | INT-OUT-*, INT-AUDIT-*, INT-TRACE-* → Output requirements |
| All BRDs (cross-cutting) | INT-SEM-*, INT-INTEL-*, INT-CRIT-*, INT-CTX-*, INT-QUAL-*, INT-VER-*, INT-ALIGN-*, INT-FRI-*, INT-DAB-*, INT-NRL-* → Semantic, intelligence, execution, and invariant requirements |

---

# 10. Summary Statement

> **We are building ADE because analysts need a way to produce audit-ready analytical decisions from data without sacrificing evidence traceability, reproducibility, or transparency. Questions should drive analysis. Evidence should back claims. Confidence should be explicit. And humans should approve plans before execution.**
