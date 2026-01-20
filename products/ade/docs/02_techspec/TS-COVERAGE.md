# ADE Tech Spec Coverage Matrix

> **Document**: Tech Spec Coverage (ADE)  
> **Version**: 1.5  
> **Last Updated**: 2026-01-20  
> **Status**: V1.5 Release — TS- Prefix Normalization Complete

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added semantic interpretation coverage |
| 1.2 | 2026-01-20 | Normalized to canonical 6-column coverage matrix; added explicit TSD ID mappings. |
| 1.3 | 2026-01-21 | Complete BRD → TSD gap analysis; added 95 missing BRD IDs; identified 21 gaps. |
| 1.4 | 2026-01-21 | Added 17 new TSD IDs across 5 Tech Spec files to close gaps; 4 PARTIAL items remain. |
| 1.5 | 2026-01-20 | Converted all TSD IDs to TS- prefix format; added implementation details to all Tech Spec files. |

---

## Coverage Matrix

| BRD ID | Business Requirement (from BRD) | Source File | TSD ID | Tech Spec file | Covered |
|--------|--------------------------------|-------------|--------|----------------|---------|
| BRD-OVERVIEW-001 | ADE MUST transform analyst questions into structured, audit-ready outputs | BRD-overview.md | TS-IO-OBJ-001, TS-AGENT-INTENT-001 | TS-inputs-outputs.md, TS-agents.md | ✅ |
| BRD-OVERVIEW-002 | Every claim MUST be traceable to source data | BRD-overview.md | TS-IO-EVID-001, TS-IO-EVID-002 | TS-inputs-outputs.md | ✅ |
| BRD-OVERVIEW-003 | Same inputs MUST always produce same outputs | BRD-overview.md | TS-IO-OBJ-002, TS-FLOW-EXEC-001 | TS-inputs-outputs.md, TS-flows.md | ✅ |
| BRD-OVERVIEW-004 | Confidence, assumptions, and limitations MUST be explicit in outputs | BRD-overview.md | TS-IO-OBJ-004 | TS-inputs-outputs.md | ✅ |
| BRD-OVERVIEW-005 | Plans MUST require human approval before execution | BRD-overview.md | TS-IO-OBJ-003, TS-FLOW-V1-005 | TS-inputs-outputs.md, TS-flows.md | ✅ |
| BRD-OVERVIEW-006 | Analyst questions MUST be semantically interpreted before planning | BRD-overview.md | TS-SEM-ADAPTER-001 | TS-agents.md | ✅ |
| BRD-OBJ-001 | Produce audit-ready analytical decisions | BRD-overview.md | TS-IO-OBJ-001 | TS-inputs-outputs.md | ✅ |
| BRD-OBJ-002 | Enable deterministic, reproducible analysis | BRD-overview.md | TS-IO-OBJ-002 | TS-inputs-outputs.md | ✅ |
| BRD-OBJ-003 | Support human oversight through plan approval | BRD-overview.md | TS-IO-OBJ-003 | TS-inputs-outputs.md | ✅ |
| BRD-OBJ-004 | Provide clear confidence and limitations | BRD-overview.md | TS-IO-OBJ-004 | TS-inputs-outputs.md | ✅ |
| BRD-OBJ-005 | Minimize time-to-insight for analysts | BRD-overview.md | TS-IO-OBJ-005 | TS-inputs-outputs.md | ✅ |
| BRD-OBJ-006 | Support multiple visualization types | BRD-overview.md | TS-IO-OBJ-006 | TS-inputs-outputs.md | ✅ |
| BRD-OBJ-007 | Enable hypothesis testing when needed | BRD-overview.md | TS-IO-OBJ-007 | TS-inputs-outputs.md | ✅ |
| BRD-OBJ-008 | Objectives MUST be expressed through explicit goals, not embedded logic | BRD-overview.md | TS-IO-OBJ-008 | TS-inputs-outputs.md | ✅ |
| BRD-ALIGN-001 | Product reasoning MUST rely on framework primitives | BRD-overview.md | TS-AGENT-FRI-001 | TS-agents.md | ✅ |
| BRD-ALIGN-002 | Product requirements that bypass framework primitives MUST be treated as framework gaps | BRD-overview.md | TS-AGENT-FRI-002 | TS-agents.md | ✅ |
| BRD-ALIGN-003 | ADE MUST consume platform-provided reasoning outputs without altering structure or semantics | BRD-overview.md | TS-AGENT-FRI-003 | TS-agents.md | ✅ |
| BRD-FRI-001 | Product MUST NOT re-implement orchestrator logic | BRD-overview.md | TS-AGENT-FRI-001 | TS-agents.md | ✅ |
| BRD-FRI-002 | Product MUST NOT re-implement iteration control | BRD-overview.md | TS-AGENT-FRI-002 | TS-agents.md | ✅ |
| BRD-FRI-003 | Product MUST NOT re-implement reasoning ladder semantics | BRD-overview.md | TS-AGENT-FRI-003 | TS-agents.md | ✅ |
| BRD-FRI-004 | Product MUST NOT bypass framework governance hooks | BRD-overview.md | TS-AGENT-FRI-004 | TS-agents.md | ✅ |
| BRD-FRI-005 | Framework gaps MUST be escalated, not worked around | BRD-overview.md | TS-AGENT-FRI-005 | TS-agents.md | ✅ |
| BRD-NRL-001 | Product MUST NOT modify behavior at runtime based on prior runs | BRD-overview.md | TS-AGENT-NRL-001 | TS-agents.md | ✅ |
| BRD-NRL-002 | Product MUST NOT persist learned patterns across runs | BRD-overview.md | TS-AGENT-NRL-002 | TS-agents.md | ✅ |
| BRD-NRL-003 | Product evolution MUST happen through intent → BRD → implementation | BRD-overview.md | TS-AGENT-NRL-003 | TS-agents.md | ✅ |
| BRD-NRL-004 | Identical inputs MUST produce identical outputs across runs | BRD-overview.md | TS-AGENT-NRL-004 | TS-agents.md | ✅ |
| CON-TA-001 | Outputs MUST be reproducible for identical inputs | BRD-overview.md | TS-FLOW-EXEC-001 | TS-flows.md | ✅ |
| CON-TA-002 | Claims MUST be traceable to evidence in source data | BRD-overview.md | TS-IO-EVID-001 | TS-inputs-outputs.md | ✅ |
| CON-TA-003 | Outputs MUST include explicit assumptions | BRD-overview.md | TS-IO-OBJ-004, TS-SCHEMA-DP-004 | TS-inputs-outputs.md, TS-schemas.md | ✅ |
| CON-TA-004 | Outputs MUST include explicit limitations | BRD-overview.md | TS-IO-OBJ-004, TS-SCHEMA-DP-005 | TS-inputs-outputs.md, TS-schemas.md | ✅ |
| CON-TA-005 | Outputs MUST include trace references to analysis steps | BRD-overview.md | TS-IO-EVID-003, TS-SCHEMA-DP-007 | TS-inputs-outputs.md, TS-schemas.md | ✅ |
| BRD-FLOW-001 | ADE MUST provide two entry points | BRD-flows.md | TS-FLOW-EXEC-003 | TS-flows.md | ✅ |
| BRD-FLOW-002 | ade_v1 flow MUST support question-first | BRD-flows.md | TS-FLOW-V1-001 | TS-flows.md | ✅ |
| BRD-FLOW-003 | visualization flow MUST support dataset-first | BRD-flows.md | TS-FLOW-VIZ-001 | TS-flows.md | ✅ |
| BRD-V1-001 | User MUST enter free-text question | BRD-flows.md | TS-FLOW-ARTF-004 | TS-flows.md | ✅ |
| BRD-V1-002 | System MUST interpret intent from question | BRD-flows.md | TS-AGENT-INTENT-001, TS-SEM-ADAPTER-001 | TS-agents.md | ✅ |
| BRD-V1-003 | User MUST select dataset | BRD-flows.md | TS-FLOW-V1-003 | TS-flows.md | ✅ |
| BRD-V1-004 | User MUST configure preferences | BRD-flows.md | TS-FLOW-V1-004 | TS-flows.md | ✅ |
| BRD-V1-005 | User MUST approve plan | BRD-flows.md | TS-FLOW-V1-005 | TS-flows.md | ✅ |
| BRD-V1-006 | System MUST produce business report | BRD-flows.md | TS-FLOW-V1-002 | TS-flows.md | ✅ |
| BRD-V1-007 | User SHOULD toggle hypothesis checks | BRD-flows.md | TS-FLOW-COND-001 | TS-flows.md | ✅ |
| BRD-V1-008 | User SHOULD add notes to analysis | BRD-flows.md | TS-FLOW-INPUT-003 | TS-flows.md | ✅ |
| BRD-VIZ-001 | User MUST select dataset first | BRD-flows.md | TS-FLOW-ARTF-004 | TS-flows.md | ✅ |
| BRD-VIZ-002 | System MUST interpret intent | BRD-flows.md | TS-FLOW-VIZ-002 | TS-flows.md | ✅ |
| BRD-VIZ-003 | User MUST configure preferences | BRD-flows.md | TS-FLOW-INPUT-001 | TS-flows.md | ✅ |
| BRD-VIZ-004 | System MUST evaluate sufficiency | BRD-flows.md | TS-FLOW-VIZ-003 | TS-flows.md | ✅ |
| BRD-VIZ-005 | User MUST approve plan | BRD-flows.md | TS-FLOW-V1-005 | TS-flows.md | ✅ |
| BRD-VIZ-006 | System MUST produce decision packet | BRD-flows.md | TS-FLOW-VIZ-004 | TS-flows.md | ✅ |
| BRD-VIZ-007 | System MUST produce business report | BRD-flows.md | TS-FLOW-V1-002, TS-IO-OUT-001 | TS-flows.md, TS-inputs-outputs.md | ✅ |
| BRD-VIZ-008 | User SHOULD toggle hypothesis checks | BRD-flows.md | TS-FLOW-COND-001 | TS-flows.md | ✅ |
| BRD-PREF-001 | User MUST select chart type | BRD-flows.md | TS-FLOW-INPUT-002, TS-IO-USER-001 | TS-flows.md, TS-inputs-outputs.md | ✅ |
| BRD-PREF-002 | User MUST select metric focus | BRD-flows.md | TS-FLOW-INPUT-002, TS-IO-USER-002 | TS-flows.md, TS-inputs-outputs.md | ✅ |
| BRD-PREF-003 | User SHOULD toggle hypothesis | BRD-flows.md | TS-FLOW-COND-001 | TS-flows.md | ✅ |
| BRD-PREF-004 | User MAY add notes | BRD-flows.md | TS-FLOW-INPUT-003 | TS-flows.md | ✅ |
| BRD-PLAN-001 | System MUST present plan summary | BRD-flows.md | TS-FLOW-V1-005 | TS-flows.md | ✅ |
| BRD-PLAN-002 | System MUST show estimated steps | BRD-flows.md | TS-AGENT-PROPOSAL-003 | TS-agents.md | ✅ |
| BRD-PLAN-003 | System MUST show estimated cost | BRD-flows.md | TS-AGENT-PROPOSAL-003 | TS-agents.md | ✅ |
| BRD-PLAN-004 | User MUST be able to approve | BRD-flows.md | TS-FLOW-V1-005 | TS-flows.md | ✅ |
| BRD-PLAN-005 | User MUST be able to reject | BRD-flows.md | TS-FLOW-V1-005 | TS-flows.md | ✅ |
| BRD-PLAN-006 | Rejection SHOULD trigger replanning | BRD-flows.md | TS-AGENT-PLANNING-002 | TS-agents.md | ✅ |
| BRD-PLAN-007 | Plan summary MUST include objective | BRD-flows.md | TS-FLOW-V1-006 | TS-flows.md | ✅ |
| BRD-PLAN-008 | Plan summary MUST include assumptions | BRD-flows.md | TS-FLOW-V1-007 | TS-flows.md | ✅ |
| BRD-PLAN-009 | Replan MUST highlight changes | BRD-flows.md | TS-FLOW-V1-008 | TS-flows.md | ✅ |
| BRD-PLAN-010 | Users MUST approve plans with constraints | BRD-flows.md | TS-FLOW-V1-009 | TS-flows.md | ✅ |
| BRD-DET-001 | Same inputs MUST produce same outputs | BRD-flows.md | TS-FLOW-EXEC-001 | TS-flows.md | ✅ |
| BRD-DET-002 | No random variations | BRD-flows.md | TS-FLOW-EXEC-001 | TS-flows.md | ✅ |
| BRD-DET-003 | Timestamps are only allowed variation | BRD-flows.md | TS-FLOW-EXEC-001 | TS-flows.md | ✅ |
| BRD-DET-004 | No LLM calls from tools | BRD-flows.md | TS-TOOL-GEN-001 | TS-tools.md | ✅ |
| BRD-CFG-001 | Flows MUST use suggest_only autonomy | BRD-flows.md | TS-FLOW-EXEC-003 | TS-flows.md | ✅ |
| BRD-INTEL-001 | System MUST use multi-stage reasoning | BRD-agents.md | TS-AGENT-REASON-001 | TS-agents.md | ✅ |
| BRD-INTEL-002 | Reasoning MUST have observable stages | BRD-agents.md | TS-AGENT-REASON-002 | TS-agents.md | ✅ |
| BRD-INTEL-003 | Reasoning cycles MUST be bounded | BRD-agents.md | TS-AGENT-REASON-003 | TS-agents.md | ✅ |
| BRD-INTEL-004 | Reasoning MUST track sufficiency state | BRD-agents.md | TS-AGENT-REASON-004 | TS-agents.md | ✅ |
| BRD-INTEL-005 | Final outputs MUST state why reasoning stopped | BRD-agents.md | TS-AGENT-REASON-005 | TS-agents.md | ✅ |
| BRD-CRIT-001 | System MUST run critique before finalizing | BRD-agents.md | TS-AGENT-CRIT-001 | TS-agents.md | ✅ |
| BRD-CRIT-002 | Critique MUST identify evidence gaps | BRD-agents.md | TS-AGENT-CRIT-002 | TS-agents.md | ✅ |
| BRD-CRIT-003 | Critique MUST be able to downgrade confidence | BRD-agents.md | TS-AGENT-CRIT-003 | TS-agents.md | ✅ |
| BRD-CRIT-004 | Critique MUST remain advisory | BRD-agents.md | TS-AGENT-CRIT-004 | TS-agents.md | ✅ |
| BRD-CRIT-005 | Blocking findings MUST trigger clarification/abort | BRD-agents.md | TS-AGENT-CRIT-005 | TS-agents.md | ✅ |
| BRD-CRIT-006 | Critique results MUST be integrated into outcomes | BRD-agents.md | TS-AGENT-CRIT-001 | TS-agents.md | ✅ |
| BRD-TOOLSEL-001 | Tool selection MUST be advisory | BRD-agents.md | TS-AGENT-TOOLSEL-001 | TS-agents.md | ✅ |
| BRD-TOOLSEL-002 | Tool recommendations MAY be ranked | BRD-agents.md | TS-AGENT-TOOLSEL-002 | TS-agents.md | ✅ |
| BRD-TOOLSEL-003 | Orchestrator MUST be sole authority for tool execution | BRD-agents.md | TS-AGENT-TOOLSEL-003 | TS-agents.md | ✅ |
| BRD-TOOLSEL-004 | Advisory suggestions MUST NOT force execution | BRD-agents.md | TS-AGENT-TOOLSEL-004 | TS-agents.md | ✅ |
| BRD-TERM-001 | ADE MUST emit explicit terminal outcomes: SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT | BRD-agents.md | TS-AGENT-TERM-001 | TS-agents.md | ✅ |
| BRD-TERM-002 | PARTIAL_SUCCESS outcomes MUST state what was completed, what is missing, and why | BRD-agents.md | TS-AGENT-TERM-002 | TS-agents.md | ✅ |
| BRD-TERM-003 | Terminal outcomes MUST include required explanations and supporting artifacts | BRD-agents.md | TS-AGENT-TERM-003 | TS-agents.md | ✅ |
| BRD-INTENT-001 | System MUST extract intent summary | BRD-agents.md | TS-AGENT-INTENT-001 | TS-agents.md | ✅ |
| BRD-INTENT-002 | System MUST identify datasets | BRD-agents.md | TS-AGENT-INTENT-004 | TS-agents.md | ✅ |
| BRD-INTENT-003 | System MUST identify metrics | BRD-agents.md | TS-AGENT-INTENT-004 | TS-agents.md | ✅ |
| BRD-INTENT-004 | System MUST identify time window | BRD-agents.md | TS-AGENT-INTENT-004 | TS-agents.md | ✅ |
| BRD-INTENT-005 | System MUST provide confidence score | BRD-agents.md | TS-AGENT-INTENT-002 | TS-agents.md | ✅ |
| BRD-INTENT-006 | System MUST detect clarification needed | BRD-agents.md | TS-AGENT-INTENT-003 | TS-agents.md | ✅ |
| BRD-INTENT-007 | System MUST generate clarifying questions | BRD-agents.md | TS-AGENT-INTENT-003 | TS-agents.md | ✅ |
| BRD-PLANNING-001 | System MUST interpret intent from context | BRD-agents.md | TS-AGENT-PLANNING-001 | TS-agents.md | ✅ |
| BRD-PLANNING-002 | System MUST support replanning | BRD-agents.md | TS-AGENT-PLANNING-002 | TS-agents.md | ✅ |
| BRD-PLANGEN-001 | System MUST produce deterministic plans | BRD-agents.md | TS-AGENT-PLAN-002 | TS-agents.md | ✅ |
| BRD-PLANGEN-002 | Plans MUST include required steps | BRD-agents.md | TS-AGENT-PLAN-001 | TS-agents.md | ✅ |
| BRD-PLANGEN-003 | Plans MUST include tool flags | BRD-agents.md | TS-AGENT-PLAN-001 | TS-agents.md | ✅ |
| BRD-PLANGEN-004 | Same inputs MUST produce same plan | BRD-agents.md | TS-AGENT-PLAN-002 | TS-agents.md | ✅ |
| BRD-PROPOSAL-001 | System MUST generate plan summary | BRD-agents.md | TS-AGENT-PROPOSAL-001 | TS-agents.md | ✅ |
| BRD-PROPOSAL-002 | System MUST estimate step count | BRD-agents.md | TS-AGENT-PROPOSAL-003 | TS-agents.md | ✅ |
| BRD-PROPOSAL-003 | System MUST estimate execution cost | BRD-agents.md | TS-AGENT-PROPOSAL-003 | TS-agents.md | ✅ |
| BRD-PROPOSAL-004 | System MUST require approval for non-trivial plans | BRD-agents.md | TS-AGENT-PROPOSAL-002 | TS-agents.md | ✅ |
| BRD-SUFF-001 | System MUST assess data sufficiency | BRD-agents.md | TS-AGENT-SUFF-001 | TS-agents.md | ✅ |
| BRD-SUFF-002 | System MUST provide confidence level | BRD-agents.md | TS-AGENT-SUFF-002 | TS-agents.md | ✅ |
| BRD-SUFF-003 | System MUST explain confidence downgrades | BRD-agents.md | TS-AGENT-SUFF-003 | TS-agents.md | ✅ |
| BRD-SUFF-004 | System SHOULD evaluate row count sufficiency | BRD-agents.md | TS-AGENT-SUFF-004 | TS-agents.md | ✅ |
| BRD-SUFF-005 | System SHOULD evaluate column completeness | BRD-agents.md | TS-AGENT-SUFF-004 | TS-agents.md | ✅ |
| BRD-SUFF-006 | System SHOULD evaluate data freshness | BRD-agents.md | TS-AGENT-SUFF-004 | TS-agents.md | ✅ |
| BRD-NARR-001 | System MUST generate dataset summary narratives | BRD-agents.md | TS-AGENT-DASH-001 | TS-agents.md | ✅ |
| BRD-NARR-002 | System MUST explain key findings | BRD-agents.md | TS-AGENT-DASH-001 | TS-agents.md | ✅ |
| BRD-NARR-003 | System MUST summarize anomalies with context | BRD-agents.md | TS-AGENT-DASH-002 | TS-agents.md | ✅ |
| BRD-NARR-004 | System MUST provide recommendations | BRD-agents.md | TS-TOOL-NARR-001 | TS-tools.md | ✅ |
| BRD-NARR-005 | User-facing explanations MUST be derived from platform decision records | BRD-agents.md | TS-AGENT-NARR-005 | TS-agents.md | ✅ |
| BRD-CONF-001 | Agent outputs MUST include confidence level | BRD-agents.md | TS-AGENT-GEN-001 | TS-agents.md | ✅ |
| BRD-CONF-002 | Low confidence MUST trigger user clarification | BRD-agents.md | TS-SEM-VALIDATE-004 | TS-agents.md | ✅ |
| BRD-CONF-003 | Confidence thresholds MUST be configurable | BRD-agents.md | TS-AGENT-CONF-003 | TS-agents.md | ✅ |
| BRD-CONF-004 | Confidence downgrades MUST be explained | BRD-agents.md | TS-AGENT-SUFF-003 | TS-agents.md | ✅ |
| BRD-CONF-005 | System MUST respect platform confidence thresholds | BRD-agents.md | TS-AGENT-FRI-001 | TS-agents.md | ✅ |
| BRD-SEM-001 | System MUST interpret free-text questions | BRD-agents.md | TS-SEM-ADAPTER-001 | TS-agents.md | ✅ |
| BRD-SEM-002 | Interpretation MUST extract intent and entities | BRD-agents.md | TS-SEM-ADAPTER-003 | TS-agents.md | ✅ |
| BRD-SEM-003 | System MUST support all ADE intent types | BRD-agents.md | TS-SEM-ADAPTER-004 | TS-agents.md | ✅ |
| BRD-SEM-004 | System MUST classify intent with confidence | BRD-agents.md | TS-SEM-ADAPTER-005 | TS-agents.md | ✅ |
| BRD-SEM-005 | Interpretation MUST run before planning | BRD-agents.md | TS-SEM-ADAPTER-001 | TS-agents.md | ✅ |
| BRD-INTENT-TAX-001 | System MUST support DESCRIBE_DATA intent | BRD-agents.md | TS-SEM-INTENT-003 | TS-agents.md | ✅ |
| BRD-INTENT-TAX-002 | System MUST support COMPARE_PERIODS intent | BRD-agents.md | TS-SEM-INTENT-004 | TS-agents.md | ✅ |
| BRD-INTENT-TAX-003 | System MUST support TREND_ANALYSIS intent | BRD-agents.md | TS-SEM-INTENT-005 | TS-agents.md | ✅ |
| BRD-INTENT-TAX-004 | System MUST support ANOMALY_REVIEW intent | BRD-agents.md | TS-SEM-INTENT-006 | TS-agents.md | ✅ |
| BRD-INTENT-TAX-005 | System MUST support OPEN_ENDED_ANALYSIS intent | BRD-agents.md | TS-SEM-INTENT-007 | TS-agents.md | ✅ |
| BRD-INTENT-TAX-006 | Intent types MUST define field requirements | BRD-agents.md | TS-SEM-INTENT-001 | TS-agents.md | ✅ |
| BRD-SEM-VAL-001 | System MUST validate semantic output | BRD-agents.md | TS-SEM-VALIDATE-001 | TS-agents.md | ✅ |
| BRD-SEM-VAL-002 | Validation MUST identify missing fields | BRD-agents.md | TS-SEM-VALIDATE-003 | TS-agents.md | ✅ |
| BRD-SEM-VAL-003 | Validation MUST return ASK_USER when possible | BRD-agents.md | TS-SEM-VALIDATE-004 | TS-agents.md | ✅ |
| BRD-SEM-VAL-004 | Validation MUST return ABORT when needed | BRD-agents.md | TS-SEM-VALIDATE-005 | TS-agents.md | ✅ |
| BRD-SEM-VAL-005 | Validation MUST compute confidence adjustment | BRD-agents.md | TS-SEM-VALIDATE-007 | TS-agents.md | ✅ |
| BRD-SEM-VAL-006 | Dataset references MUST be validated against available datasets | BRD-agents.md | TS-SEM-VALIDATE-008 | TS-agents.md | ✅ |
| BRD-SEM-VAL-007 | Metric references MUST be validated against dataset schema when known | BRD-agents.md | TS-SEM-VALIDATE-009 | TS-agents.md | ✅ |
| BRD-CLARIFY-001 | System MUST generate deterministic questions | BRD-agents.md | TS-SEM-CLARIFY-001 | TS-agents.md | ✅ |
| BRD-CLARIFY-002 | Questions MUST be templated (no LLM) | BRD-agents.md | TS-SEM-CLARIFY-006 | TS-agents.md | ✅ |
| BRD-CLARIFY-003 | Questions MUST target missing fields | BRD-agents.md | TS-SEM-CLARIFY-002 | TS-agents.md | ✅ |
| BRD-CLARIFY-004 | System MUST provide metric focus templates | BRD-agents.md | TS-SEM-CLARIFY-003 | TS-agents.md | ✅ |
| BRD-CLARIFY-005 | System MUST provide time range templates | BRD-agents.md | TS-SEM-CLARIFY-004 | TS-agents.md | ✅ |
| BRD-CLARIFY-006 | System MUST provide anomaly templates | BRD-agents.md | TS-SEM-CLARIFY-005 | TS-agents.md | ✅ |
| BRD-ROUTER-001 | System MUST route to appropriate flow | BRD-agents.md | TS-SEM-ROUTER-001 | TS-agents.md | ✅ |
| BRD-ROUTER-002 | Router MUST output flow and parameters | BRD-agents.md | TS-SEM-ROUTER-002 | TS-agents.md | ✅ |
| BRD-ROUTER-003 | Router MUST use deterministic mapping | BRD-agents.md | TS-SEM-ROUTER-003 | TS-agents.md | ✅ |
| BRD-ROUTER-004 | Router MUST support both flow types | BRD-agents.md | TS-SEM-ROUTER-003 | TS-agents.md | ✅ |
| BRD-SEM-OBS-001 | System MUST emit trace metadata | BRD-agents.md | TS-SEM-OBS-001 | TS-agents.md | ✅ |
| BRD-SEM-OBS-002 | Traces MUST include intent | BRD-agents.md | TS-SEM-OBS-003 | TS-agents.md | ✅ |
| BRD-SEM-OBS-003 | Traces MUST include confidence | BRD-agents.md | TS-SEM-OBS-004 | TS-agents.md | ✅ |
| BRD-SEM-OBS-004 | Traces MUST include missing fields | BRD-agents.md | TS-SEM-OBS-005 | TS-agents.md | ✅ |
| BRD-SEM-OBS-005 | Traces MUST include clarifying questions | BRD-agents.md | TS-SEM-OBS-006 | TS-agents.md | ✅ |
| BRD-TOOL-001 | Tools MUST NOT call LLMs directly | BRD-tools.md | TS-TOOL-GEN-001 | TS-tools.md | ✅ |
| BRD-TOOL-002 | Tools MUST produce deterministic outputs | BRD-tools.md | TS-TOOL-GEN-005 | TS-tools.md | ✅ |
| BRD-TOOL-003 | Same inputs MUST produce same outputs | BRD-tools.md | TS-TOOL-GEN-005 | TS-tools.md | ✅ |
| BRD-TOOL-004 | Tools MUST NOT have external dependencies | BRD-tools.md | TS-TOOL-GEN-007 | TS-tools.md | ✅ |
| BRD-TOOL-005 | Tools MUST produce evidence items | BRD-tools.md | TS-TOOL-GEN-006 | TS-tools.md | ✅ |
| BRD-DATA-001 | System MUST read CSV datasets | BRD-tools.md | TS-TOOL-DATA-001 | TS-tools.md | ✅ |
| BRD-DATA-002 | System MUST extract column metadata | BRD-tools.md | TS-TOOL-DATA-001 | TS-tools.md | ✅ |
| BRD-DATA-003 | System MUST extract row data | BRD-tools.md | TS-TOOL-DATA-001 | TS-tools.md | ✅ |
| BRD-DATA-004 | System MUST infer field types | BRD-tools.md | TS-TOOL-DATA-003 | TS-tools.md | ✅ |
| BRD-DATA-005 | System MUST handle UTF-8 encoding | BRD-tools.md | TS-TOOL-DATA-002 | TS-tools.md | ✅ |
| BRD-DATA-006 | System MUST handle quoted CSV fields | BRD-tools.md | TS-TOOL-DATA-002 | TS-tools.md | ✅ |
| BRD-METRIC-001 | System MUST compute aggregated metrics | BRD-tools.md | TS-TOOL-DATA-004 | TS-tools.md | ✅ |
| BRD-METRIC-002 | System MUST support multiple metric types | BRD-tools.md | TS-TOOL-DATA-005 | TS-tools.md | ✅ |
| BRD-METRIC-003 | System MUST produce evidence items | BRD-tools.md | TS-TOOL-DATA-004 | TS-tools.md | ✅ |
| BRD-METRIC-004 | System MUST respect metric_focus parameter | BRD-tools.md | TS-TOOL-DATA-005 | TS-tools.md | ✅ |
| BRD-ANOM-001 | System MUST detect statistical anomalies | BRD-tools.md | TS-TOOL-ANALYSIS-001 | TS-tools.md | ✅ |
| BRD-ANOM-002 | System MUST use z-score analysis | BRD-tools.md | TS-TOOL-ANALYSIS-001 | TS-tools.md | ✅ |
| BRD-ANOM-003 | System MUST rank anomalies by severity | BRD-tools.md | TS-TOOL-ANALYSIS-008 | TS-tools.md | ✅ |
| BRD-ANOM-004 | System MUST explain anomaly reasons | BRD-tools.md | TS-SCHEMA-AR-007 | TS-schemas.md | ✅ |
| BRD-ANOM-005 | System MUST produce evidence items | BRD-tools.md | TS-TOOL-ANALYSIS-002 | TS-tools.md | ✅ |
| BRD-HYP-001 | System MUST support data outage hypothesis | BRD-tools.md | TS-TOOL-ANALYSIS-004 | TS-tools.md | ✅ |
| BRD-HYP-002 | System MUST support seasonality hypothesis | BRD-tools.md | TS-TOOL-ANALYSIS-005 | TS-tools.md | ✅ |
| BRD-HYP-003 | Hypothesis tests MUST be toggleable | BRD-tools.md | TS-TOOL-ANALYSIS-006 | TS-tools.md | ✅ |
| BRD-HYP-004 | Tests MUST return status (confirmed/rejected/skipped) | BRD-tools.md | TS-TOOL-ANALYSIS-003 | TS-tools.md | ✅ |
| BRD-HYP-005 | Tests MUST provide reasoning | BRD-tools.md | TS-TOOL-ANALYSIS-003 | TS-tools.md | ✅ |
| BRD-HYP-006 | Tests MUST produce evidence items | BRD-tools.md | TS-TOOL-ANALYSIS-003 | TS-tools.md | ✅ |
| BRD-DRIVER-001 | System SHOULD identify key metric drivers | BRD-tools.md | TS-TOOL-ANALYSIS-007 | TS-tools.md | ✅ |
| BRD-DRIVER-002 | Drivers SHOULD be ranked by contribution | BRD-tools.md | TS-TOOL-ANALYSIS-007 | TS-tools.md | ✅ |
| BRD-CHART-001 | System MUST build chart specifications | BRD-tools.md | TS-TOOL-VIZ-001 | TS-tools.md | ✅ |
| BRD-CHART-002 | System MUST support bar charts | BRD-tools.md | TS-TOOL-VIZ-002 | TS-tools.md | ✅ |
| BRD-CHART-003 | System MUST support line charts | BRD-tools.md | TS-TOOL-VIZ-002 | TS-tools.md | ✅ |
| BRD-CHART-004 | System MUST support area charts | BRD-tools.md | TS-TOOL-VIZ-002 | TS-tools.md | ✅ |
| BRD-CHART-005 | System MUST support scatter charts | BRD-tools.md | TS-TOOL-VIZ-002 | TS-tools.md | ✅ |
| BRD-CHART-006 | System MUST use fallback type when needed | BRD-tools.md | TS-TOOL-VIZ-003 | TS-tools.md | ✅ |
| BRD-CHART-007 | Specs MUST be Vega-Lite compatible | BRD-tools.md | TS-TOOL-VIZ-001 | TS-tools.md | ✅ |
| BRD-REC-001 | System SHOULD recommend chart type | BRD-tools.md | TS-TOOL-VIZ-004 | TS-tools.md | ✅ |
| BRD-REC-002 | Recommendations SHOULD consider data shape | BRD-tools.md | TS-TOOL-VIZ-004 | TS-tools.md | ✅ |
| BRD-PKT-001 | System MUST assemble decision packets | BRD-tools.md | TS-TOOL-ASSEMBLE-001 | TS-tools.md | ✅ |
| BRD-PKT-002 | Packets MUST include question context | BRD-tools.md | TS-SCHEMA-DP-001 | TS-schemas.md | ✅ |
| BRD-PKT-003 | Packets MUST include decision summary | BRD-tools.md | TS-SCHEMA-DP-002 | TS-schemas.md | ✅ |
| BRD-PKT-004 | Packets MUST include confidence level | BRD-tools.md | TS-SCHEMA-DP-003 | TS-schemas.md | ✅ |
| BRD-PKT-005 | Packets MUST include assumptions | BRD-tools.md | TS-SCHEMA-DP-004 | TS-schemas.md | ✅ |
| BRD-PKT-006 | Packets MUST include limitations | BRD-tools.md | TS-SCHEMA-DP-005 | TS-schemas.md | ✅ |
| BRD-PKT-007 | Packets MUST include evidence references | BRD-tools.md | TS-TOOL-ASSEMBLE-003 | TS-tools.md | ✅ |
| BRD-PKT-008 | Packets MUST include trace references | BRD-tools.md | TS-TOOL-ASSEMBLE-004 | TS-tools.md | ✅ |
| BRD-RPT-001 | System MUST assemble business reports | BRD-tools.md | TS-TOOL-ASSEMBLE-005 | TS-tools.md | ✅ |
| BRD-RPT-002 | Reports MUST include executive summary | BRD-tools.md | TS-SCHEMA-BR-007 | TS-schemas.md | ✅ |
| BRD-RPT-003 | Reports MUST include key findings | BRD-tools.md | TS-SCHEMA-BR-008, TS-TOOL-ASSEMBLE-007 | TS-schemas.md, TS-tools.md | ✅ |
| BRD-RPT-004 | Reports MUST include visualizations | BRD-tools.md | TS-SCHEMA-BR-009 | TS-schemas.md | ✅ |
| BRD-RPT-005 | Reports MUST include anomalies | BRD-tools.md | TS-SCHEMA-BR-010 | TS-schemas.md | ✅ |
| BRD-RPT-006 | Reports MUST include recommendations | BRD-tools.md | TS-TOOL-NARR-001, TS-SCHEMA-BR-011 | TS-tools.md, TS-schemas.md | ✅ |
| BRD-RPT-007 | Reports MUST include appendix | BRD-tools.md | TS-SCHEMA-BR-012 | TS-schemas.md | ✅ |
| BRD-EVID-001 | System MUST bundle evidence items | BRD-tools.md | TS-TOOL-ASSEMBLE-006 | TS-tools.md | ✅ |
| BRD-EVID-002 | Bundles MUST preserve provenance | BRD-tools.md | TS-TOOL-ASSEMBLE-006 | TS-tools.md | ✅ |
| BRD-EVID-003 | Bundles SHOULD deduplicate items | BRD-tools.md | — | — | PARTIAL |
| BRD-ASM-004 | Assemblers MUST include all required sections | BRD-tools.md | TS-TOOL-ASSEMBLE-002 | TS-tools.md | ✅ |
| BRD-ASM-005 | Assemblers MUST validate outputs against schemas | BRD-tools.md | TS-TOOL-ASSEMBLE-001 | TS-tools.md | ✅ |
| BRD-HTML-001 | System MUST render business reports as HTML | BRD-tools.md | TS-TOOL-RENDER-001 | TS-tools.md | ✅ |
| BRD-HTML-002 | System MUST render decision packets as HTML | BRD-tools.md | TS-TOOL-RENDER-002 | TS-tools.md | ✅ |
| BRD-HTML-003 | HTML MUST be valid HTML5 | BRD-tools.md | TS-TOOL-RENDER-001 | TS-tools.md | ✅ |
| BRD-HTML-004 | HTML SHOULD be self-contained | BRD-tools.md | — | — | PARTIAL |
| BRD-EXP-001 | System MAY export to PDF | BRD-tools.md | TS-TOOL-RENDER-003 | TS-tools.md | ✅ |
| BRD-EXP-003 | Exports MUST be written to output location | BRD-tools.md | TS-TOOL-RENDER-004 | TS-tools.md | ✅ |
| BRD-FMT-001 | System MUST accept CSV format | BRD-data.md | TS-IO-DATA-001 | TS-inputs-outputs.md | ✅ |
| BRD-FMT-002 | System MUST support UTF-8 encoding | BRD-data.md | TS-IO-DATA-003 | TS-inputs-outputs.md | ✅ |
| BRD-FMT-003 | System MUST parse standard CSV headers | BRD-data.md | TS-IO-DATA-002 | TS-inputs-outputs.md | ✅ |
| BRD-FMT-004 | System MUST handle quoted fields | BRD-data.md | TS-TOOL-DATA-002 | TS-tools.md | ✅ |
| BRD-FMT-005 | System MUST handle empty values | BRD-data.md | TS-TOOL-DATA-002 | TS-tools.md | ✅ |
| BRD-LOC-001 | User datasets MUST be stored in designated input location | BRD-data.md | TS-IO-DATA-004 | TS-inputs-outputs.md | ✅ |
| BRD-LOC-002 | Built-in datasets MUST be stored in designated built-in location | BRD-data.md | TS-IO-DATA-005 | TS-inputs-outputs.md | ✅ |
| BRD-LOC-003 | Dataset names MUST resolve to specific dataset sources | BRD-data.md | TS-IO-DATA-007 | TS-inputs-outputs.md | ✅ |
| BRD-LOC-004 | Missing datasets MUST produce clear errors | BRD-data.md | TS-IO-DATA-008 | TS-inputs-outputs.md | ✅ |
| BRD-BUILTIN-001 | A default demonstration dataset MUST be available | BRD-data.md | TS-IO-DATA-006 | TS-inputs-outputs.md | ✅ |
| BRD-BUILTIN-002 | Built-in datasets MUST work without configuration | BRD-data.md | TS-IO-DATA-006 | TS-inputs-outputs.md | ✅ |
| BRD-SCHEMA-001 | All data structures MUST use standardized schemas | BRD-data.md | TS-SCHEMA-GEN-001 | TS-schemas.md | ✅ |
| BRD-SCHEMA-002 | Schemas MUST reject unknown fields | BRD-data.md | TS-SCHEMA-GEN-002 | TS-schemas.md | ✅ |
| BRD-SCHEMA-003 | Schemas MUST validate types | BRD-data.md | TS-SCHEMA-VAL-001 | TS-schemas.md | ✅ |
| BRD-SCHEMA-004 | Schemas MUST use default factories for collections | BRD-data.md | TS-SCHEMA-GEN-003 | TS-schemas.md | ✅ |
| BRD-DP-001 | Decision packets MUST include question context | BRD-data.md | TS-SCHEMA-DP-001 | TS-schemas.md | ✅ |
| BRD-DP-002 | Decision packets MUST include decision summary | BRD-data.md | TS-SCHEMA-DP-002 | TS-schemas.md | ✅ |
| BRD-DP-003 | Decision packets MUST include confidence level | BRD-data.md | TS-SCHEMA-DP-003 | TS-schemas.md | ✅ |
| BRD-DP-004 | Decision packets MUST include assumptions | BRD-data.md | TS-SCHEMA-DP-004 | TS-schemas.md | ✅ |
| BRD-DP-005 | Decision packets MUST include limitations | BRD-data.md | TS-SCHEMA-DP-005 | TS-schemas.md | ✅ |
| BRD-DP-006 | Decision packets MUST include structured sections | BRD-data.md | TS-SCHEMA-DP-006 | TS-schemas.md | ✅ |
| BRD-DP-007 | Decision packets MUST include trace references | BRD-data.md | TS-SCHEMA-DP-007 | TS-schemas.md | ✅ |
| BRD-BR-001 | BusinessReport MUST include title | BRD-data.md | TS-SCHEMA-BR-001 | TS-schemas.md | ✅ |
| BRD-BR-002 | BusinessReport MUST include timestamp | BRD-data.md | TS-SCHEMA-BR-002 | TS-schemas.md | ✅ |
| BRD-BR-003 | Business reports MUST include dataset identifiers | BRD-data.md | TS-SCHEMA-BR-003 | TS-schemas.md | ✅ |
| BRD-BR-004 | Business reports MUST include executive summaries | BRD-data.md | TS-SCHEMA-BR-007 | TS-schemas.md | ✅ |
| BRD-BR-005 | Business reports MUST include key findings | BRD-data.md | TS-SCHEMA-BR-008 | TS-schemas.md | ✅ |
| BRD-BR-006 | Business reports MUST include visuals | BRD-data.md | TS-SCHEMA-BR-009 | TS-schemas.md | ✅ |
| BRD-BR-007 | BusinessReport MUST include anomalies | BRD-data.md | TS-SCHEMA-BR-010 | TS-schemas.md | ✅ |
| BRD-BR-008 | BusinessReport MUST include appendix | BRD-data.md | TS-SCHEMA-BR-012 | TS-schemas.md | ✅ |
| BRD-IF-001 | Intent frames MUST include intent summaries | BRD-data.md | TS-SCHEMA-IF-001 | TS-schemas.md | ✅ |
| BRD-IF-002 | Intent frames MUST include confidence scores | BRD-data.md | TS-SCHEMA-IF-006 | TS-schemas.md | ✅ |
| BRD-IF-003 | Intent frames MUST include blocking requirement indicators | BRD-data.md | TS-SCHEMA-IF-008 | TS-schemas.md | ✅ |
| BRD-IF-004 | Intent frames SHOULD include inferred entities | BRD-data.md | TS-SCHEMA-IF-002 | TS-schemas.md | ✅ |
| BRD-IF-005 | Intent frames SHOULD include inferred metrics | BRD-data.md | TS-SCHEMA-IF-003 | TS-schemas.md | ✅ |
| BRD-IF-006 | Intent frames MUST include blocking questions | BRD-data.md | TS-SCHEMA-IF-009 | TS-schemas.md | ✅ |
| BRD-EVREF-001 | All claims MUST have evidence references | BRD-data.md | TS-IO-EVID-001 | TS-inputs-outputs.md | ✅ |
| BRD-EVREF-002 | Evidence references MUST include dataset identifiers | BRD-data.md | TS-IO-EVID-002 | TS-inputs-outputs.md | ✅ |
| BRD-EVREF-003 | Evidence references MUST include referenced columns | BRD-data.md | TS-IO-EVID-002 | TS-inputs-outputs.md | ✅ |
| BRD-EVREF-004 | Evidence MUST be traceable to source data | BRD-data.md | TS-IO-EVID-001, TS-IO-EVID-002 | TS-inputs-outputs.md | ✅ |
| BRD-TRACE-001 | Decision packets MUST include trace references | BRD-data.md | TS-IO-EVID-003, TS-SCHEMA-DP-007 | TS-inputs-outputs.md, TS-schemas.md | ✅ |
| BRD-TRACE-002 | Trace references MUST include execution step identifiers | BRD-data.md | TS-IO-ARTF-001 | TS-inputs-outputs.md | ✅ |
| BRD-TRACE-003 | Trace references MUST include user inputs | BRD-data.md | TS-IO-ARTF-002 | TS-inputs-outputs.md | ✅ |
| BRD-TRACE-004 | All trace references MUST be valid | BRD-data.md | TS-IO-ARTF-005 | TS-inputs-outputs.md | ✅ |
| BRD-ITEM-001 | Tools MUST produce evidence_items | BRD-data.md | TS-IO-EVID-004 | TS-inputs-outputs.md | ✅ |
| BRD-ITEM-002 | Evidence items MUST include provenance | BRD-data.md | TS-TOOL-ASSEMBLE-006 | TS-tools.md | ✅ |
| BRD-ITEM-003 | Evidence items MUST include confidence | BRD-data.md | TS-SCHEMA-EVITEM-001 | TS-schemas.md | ✅ |
| BRD-ITEM-004 | Evidence items MUST include dataset identifiers | BRD-data.md | TS-IO-EVID-002 | TS-inputs-outputs.md | ✅ |
| BRD-ITEM-005 | Evidence items MUST include referenced columns | BRD-data.md | TS-IO-EVID-002 | TS-inputs-outputs.md | ✅ |
| BRD-ITEM-006 | Evidence items MUST include referenced values | BRD-data.md | TS-SCHEMA-EVITEM-002 | TS-schemas.md | ✅ |
| BRD-CL-001 | Confidence levels MUST use standard values | BRD-data.md | TS-SCHEMA-DP-003, TS-IO-OBJ-004 | TS-schemas.md, TS-inputs-outputs.md | ✅ |
| BRD-CL-002 | Valid confidence levels: high, medium, low | BRD-data.md | TS-AGENT-SUFF-002 | TS-agents.md | ✅ |
| BRD-CL-003 | Confidence MUST be present in all packets | BRD-data.md | TS-SCHEMA-DP-003 | TS-schemas.md | ✅ |
| BRD-CL-004 | Confidence MUST be explainable | BRD-data.md | TS-AGENT-SUFF-003 | TS-agents.md | ✅ |
| BRD-VAL-001 | All outputs MUST pass schema validation | BRD-data.md | TS-SCHEMA-VAL-001 | TS-schemas.md | ✅ |
| BRD-VAL-002 | Invalid outputs MUST produce clear errors | BRD-data.md | TS-SCHEMA-VAL-002 | TS-schemas.md | ✅ |
| BRD-VAL-003 | Validation MUST happen before rendering | BRD-data.md | TS-SCHEMA-VAL-003 | TS-schemas.md | ✅ |
| BRD-CTX-001 | System MUST construct Context Pack after ingestion and before planning | BRD-data.md | TS-SCHEMA-CTX-001 | TS-schemas.md | ✅ |
| BRD-CTX-002 | Context Packs MUST include dataset profile and coverage metrics | BRD-data.md | TS-SCHEMA-CTX-002 | TS-schemas.md | ✅ |
| BRD-CTX-003 | Context Pack statistics MUST be backed by evidence items | BRD-data.md | TS-SCHEMA-CTX-003 | TS-schemas.md | ✅ |
| BRD-CTX-004 | Advisory reasoning MUST reference Context Pack artifacts | BRD-data.md | TS-SCHEMA-CTX-004 | TS-schemas.md | ✅ |
| BRD-CTX-005 | ADE reasoning and outputs MUST treat Context Pack artifacts as the sole grounding source | BRD-data.md | TS-SCHEMA-CTX-005 | TS-schemas.md | ✅ |
| BRD-OUT-001 | System MUST produce the business report output | BRD-outputs.md | TS-IO-OUT-001 | TS-inputs-outputs.md | ✅ |
| BRD-OUT-002 | Report MUST be valid HTML5 | BRD-outputs.md | TS-IO-OUT-004 | TS-inputs-outputs.md | ✅ |
| BRD-OUT-003 | Report MUST include executive summary | BRD-outputs.md | TS-IO-QUAL-001 | TS-inputs-outputs.md | ✅ |
| BRD-OUT-004 | Report MUST include key findings | BRD-outputs.md | TS-IO-QUAL-002 | TS-inputs-outputs.md | ✅ |
| BRD-OUT-005 | Report MUST include visualizations | BRD-outputs.md | TS-IO-QUAL-005 | TS-inputs-outputs.md | ✅ |
| BRD-OUT-006 | Report MUST include anomaly table | BRD-outputs.md | TS-SCHEMA-BR-010 | TS-schemas.md | ✅ |
| BRD-OUT-007 | Report MUST include recommendations | BRD-outputs.md | TS-IO-QUAL-003 | TS-inputs-outputs.md | ✅ |
| BRD-OUT-008 | Report MUST include appendix | BRD-outputs.md | TS-SCHEMA-BR-012 | TS-schemas.md | ✅ |
| BRD-OUT-010 | System MUST produce the decision packet output for the visualization flow | BRD-outputs.md | TS-IO-OUT-002 | TS-inputs-outputs.md | ✅ |
| BRD-OUT-011 | Packet MUST be valid HTML5 | BRD-outputs.md | TS-IO-OUT-004 | TS-inputs-outputs.md | ✅ |
| BRD-OUT-012 | Packet MUST include question | BRD-outputs.md | TS-SCHEMA-DP-001 | TS-schemas.md | ✅ |
| BRD-OUT-013 | Packet MUST include decision summary | BRD-outputs.md | TS-SCHEMA-DP-002 | TS-schemas.md | ✅ |
| BRD-OUT-014 | Packet MUST include confidence level | BRD-outputs.md | TS-SCHEMA-DP-003 | TS-schemas.md | ✅ |
| BRD-OUT-015 | Packet MUST include evidence sections | BRD-outputs.md | TS-SCHEMA-DP-006 | TS-schemas.md | ✅ |
| BRD-OUT-016 | Packet MUST include assumptions | BRD-outputs.md | TS-SCHEMA-DP-004 | TS-schemas.md | ✅ |
| BRD-OUT-017 | Packet MUST include limitations | BRD-outputs.md | TS-SCHEMA-DP-005 | TS-schemas.md | ✅ |
| BRD-LOC-001 (outputs) | Outputs MUST be written to designated output location | BRD-outputs.md | TS-IO-OUT-003 | TS-inputs-outputs.md | ✅ |
| BRD-LOC-002 (outputs) | Output directory MUST be created if missing | BRD-outputs.md | TS-IO-OUT-007 | TS-inputs-outputs.md | ✅ |
| BRD-LOC-003 (outputs) | Output files MUST have consistent naming | BRD-outputs.md | TS-IO-OUT-001, TS-IO-OUT-002 | TS-inputs-outputs.md | ✅ |
| BRD-AUDIT-001 | All claims MUST be traceable to evidence | BRD-outputs.md | TS-IO-EVID-001 | TS-inputs-outputs.md | ✅ |
| BRD-AUDIT-002 | Evidence MUST include dataset references | BRD-outputs.md | TS-IO-EVID-002 | TS-inputs-outputs.md | ✅ |
| BRD-AUDIT-003 | Evidence MUST include column references | BRD-outputs.md | TS-IO-EVID-002 | TS-inputs-outputs.md | ✅ |
| BRD-AUDIT-004 | Evidence MUST be verifiable against source data | BRD-outputs.md | TS-IO-EVID-001 | TS-inputs-outputs.md | ✅ |
| BRD-AUDIT-010 | Outputs MUST include trace references | BRD-outputs.md | TS-IO-EVID-003 | TS-inputs-outputs.md | ✅ |
| BRD-AUDIT-011 | Trace references MUST link to execution steps | BRD-outputs.md | TS-IO-ARTF-001 | TS-inputs-outputs.md | ✅ |
| BRD-AUDIT-012 | Trace references MUST include user inputs | BRD-outputs.md | TS-IO-ARTF-002 | TS-inputs-outputs.md | ✅ |
| BRD-AUDIT-013 | Execution MUST be reproducible | BRD-outputs.md | TS-FLOW-EXEC-001 | TS-flows.md | ✅ |
| BRD-AUDIT-020 | Outputs MUST include explicit assumptions | BRD-outputs.md | TS-SCHEMA-DP-004, TS-SCHEMA-APP-004 | TS-schemas.md | ✅ |
| BRD-AUDIT-021 | Outputs MUST include explicit limitations | BRD-outputs.md | TS-SCHEMA-DP-005, TS-SCHEMA-APP-005 | TS-schemas.md | ✅ |
| BRD-AUDIT-022 | Confidence levels MUST be explained | BRD-outputs.md | TS-AGENT-SUFF-003 | TS-agents.md | ✅ |
| BRD-AUDIT-023 | Downgrade reasons MUST be documented | BRD-outputs.md | TS-SCHEMA-APP-002 | TS-schemas.md | ✅ |
| BRD-REPRO-001 | Same inputs MUST produce same outputs | BRD-outputs.md | TS-FLOW-EXEC-001 | TS-flows.md | ✅ |
| BRD-REPRO-002 | Timestamps are the only allowed variation | BRD-outputs.md | TS-FLOW-EXEC-001 | TS-flows.md | ✅ |
| BRD-REPRO-003 | No random variations in outputs | BRD-outputs.md | TS-FLOW-EXEC-001 | TS-flows.md | ✅ |
| BRD-REPRO-004 | Outputs MUST be deterministic | BRD-outputs.md | TS-FLOW-EXEC-001 | TS-flows.md | ✅ |
| BRD-PDF-001 | System MAY export to PDF | BRD-outputs.md | TS-TOOL-RENDER-003, TS-IO-OUT-006 | TS-tools.md, TS-inputs-outputs.md | ✅ |
| BRD-PDF-002 | PDF MUST include all report content | BRD-outputs.md | — | — | PARTIAL |
| BRD-PDF-003 | PDF MUST be printable | BRD-outputs.md | — | — | PARTIAL |
| BRD-QUAL-001 | All key findings MUST be backed by at least one evidence reference | BRD-outputs.md | TS-IO-QUAL-002 | TS-inputs-outputs.md | ✅ |
| BRD-QUAL-002 | Executive summaries MUST include scope, key result, confidence, and primary limitation | BRD-outputs.md | TS-IO-QUAL-001 | TS-inputs-outputs.md | ✅ |
| BRD-QUAL-003 | Recommendations MUST only be emitted when evidence-supported | BRD-outputs.md | TS-IO-QUAL-003 | TS-inputs-outputs.md | ✅ |
| BRD-QUAL-004 | Low-confidence outputs MUST include a "Next Inputs Needed" section | BRD-outputs.md | TS-IO-QUAL-008 | TS-inputs-outputs.md | ✅ |
| BRD-QUAL-010 | Charts MUST render correctly | BRD-outputs.md | TS-IO-QUAL-005 | TS-inputs-outputs.md | ✅ |
| BRD-QUAL-011 | Tables MUST be readable | BRD-outputs.md | TS-IO-QUAL-006 | TS-inputs-outputs.md | ✅ |
| BRD-QUAL-012 | HTML MUST display in modern browsers | BRD-outputs.md | TS-IO-QUAL-007 | TS-inputs-outputs.md | ✅ |
| BRD-VER-001 | Outputs MUST include product version, flow version, and schema version | BRD-outputs.md | TS-IO-VER-001 | TS-inputs-outputs.md | ✅ |
| BRD-VER-002 | Outputs MUST record dataset hash and input parameter hash | BRD-outputs.md | TS-IO-VER-002 | TS-inputs-outputs.md | ✅ |
| BRD-VER-003 | Non-deterministic dependencies MUST be version-pinned or disallowed | BRD-outputs.md | TS-IO-VER-003 | TS-inputs-outputs.md | ✅ |
| BRD-DAB-001 | Outputs MUST be labeled as recommendations/findings, not decisions | BRD-outputs.md | TS-IO-DAB-001 | TS-inputs-outputs.md | ✅ |
| BRD-DAB-002 | Decision packets MUST clarify human authority for final decisions | BRD-outputs.md | TS-IO-DAB-002 | TS-inputs-outputs.md | ✅ |
| BRD-DAB-003 | Outputs MUST NOT trigger downstream actions without explicit approval | BRD-outputs.md | TS-IO-DAB-003 | TS-inputs-outputs.md | ✅ |
| BRD-DAB-004 | Confidence language MUST avoid implying autonomous decisions | BRD-outputs.md | TS-IO-DAB-004 | TS-inputs-outputs.md | ✅ |
| BRD-DAB-005 | Recommendations MUST be presented as advisory | BRD-outputs.md | TS-IO-DAB-005 | TS-inputs-outputs.md | ✅ |

---

## Gap Register

| BRD ID | Gap Type | Requirement | Notes | Priority |
|--------|----------|-------------|-------|----------|
| BRD-EVID-003 | PARTIAL | Bundles SHOULD deduplicate items | Implied but not explicitly specified | P2 |
| BRD-HTML-004 | PARTIAL | HTML SHOULD be self-contained | Implied but not explicitly specified | P1 |
| BRD-PDF-002 | PARTIAL | PDF MUST include all report content | Implied by MAY export but not detailed | P2 |
| BRD-PDF-003 | PARTIAL | PDF MUST be printable | Implied by MAY export but not detailed | P2 |

---

## Summary

- **Total BRD Requirements**: 269
- **Covered (✅)**: 265
- **Gaps (❌ NO)**: 0
- **Partial Coverage**: 4
- **Coverage**: 98.5%

---

## TS-COVERAGE GAP COUNT: 4

---

## Closed Gaps (V1.4)

The following 17 TSD IDs were added to close gaps identified in V1.3:

### TS-agents.md
- **TS-AGENT-TERM-001**: ADE MUST emit explicit terminal outcomes (BRD-TERM-001)
- **TS-AGENT-TERM-002**: PARTIAL_SUCCESS outcomes MUST state completions, gaps, reasons (BRD-TERM-002)
- **TS-AGENT-TERM-003**: Terminal outcomes MUST include explanations and artifacts (BRD-TERM-003)
- **TS-AGENT-FRI-005**: Framework gaps MUST be escalated (BRD-FRI-005)
- **TS-AGENT-NARR-005**: Explanations MUST derive from platform decision records (BRD-NARR-005)
- **TS-AGENT-CONF-003**: Confidence thresholds MUST be configurable (BRD-CONF-003)
- **TS-SEM-VALIDATE-008**: Dataset references MUST be validated (BRD-SEM-VAL-006)
- **TS-SEM-VALIDATE-009**: Metric references MUST be validated (BRD-SEM-VAL-007)

### TS-tools.md
- **TS-TOOL-GEN-007**: Tools MUST NOT have external dependencies (BRD-TOOL-004)
- **TS-TOOL-ANALYSIS-008**: Anomalies MUST be ranked by severity (BRD-ANOM-003)

### TS-inputs-outputs.md
- **TS-IO-OBJ-008**: Objectives MUST be expressed through explicit goals (BRD-OBJ-008)
- **TS-IO-OUT-007**: Output directory MUST be created if missing (BRD-LOC-002)
- **TS-IO-QUAL-008**: Low-confidence outputs MUST include "Next Inputs Needed" (BRD-QUAL-004)

### TS-flows.md
- **TS-FLOW-V1-009**: Users MUST approve plans with constraints (BRD-PLAN-010)

### TS-schemas.md
- **TS-SCHEMA-EVITEM-001**: Evidence items MUST include confidence (BRD-ITEM-003)
- **TS-SCHEMA-EVITEM-002**: Evidence items MUST include values (BRD-ITEM-006)
- **TS-SCHEMA-CTX-005**: Context Pack MUST be sole grounding source (BRD-CTX-005)

---

## V1.5 Normalization

All TSD IDs across all Tech Spec files have been normalized to use the `TS-` prefix:

| Tech Spec File | Original Prefix | New Prefix |
|----------------|-----------------|------------|
| TS-agents.md | AGENT-*, SEM-* | TS-AGENT-*, TS-SEM-* |
| TS-tools.md | TOOL-* | TS-TOOL-* |
| TS-inputs-outputs.md | IO-* | TS-IO-* |
| TS-flows.md | FLOW-* | TS-FLOW-* |
| TS-schemas.md | SCHEMA-* | TS-SCHEMA-* |

All Tech Spec files now include an "Implementation Details" column with:
- File paths to implementation locations
- Class names and method signatures
- Pydantic field definitions and types
- Validation logic and constraints
