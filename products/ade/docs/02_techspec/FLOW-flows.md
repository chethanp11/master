# ADE Flow Technical Specification

> **Document**: Technical Specification — Flows  
> **Prefix**: FLOW-*  
> **Version**: 1.2  
> **Last Updated**: 2026-01-20

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added visualization flow requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |

---

## 1. Flow Execution (FLOW-EXEC)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| FLOW-EXEC-001 | Flows MUST execute deterministically—same inputs produce same outputs; no random or time-based variations except timestamps. | MUST | BRD-DET-001, BRD-DET-002, BRD-DET-003 | 1.1 | 13 Jan 2026 | — |
| FLOW-EXEC-002 | Flow steps MUST execute in YAML-defined sequence with dependencies completing before dependent steps and artifact references resolving to prior outputs. | MUST | BRD-DET-001 | 1.1 | 13 Jan 2026 | — |
| FLOW-EXEC-003 | All ADE flows MUST use autonomy_level: "suggest_only" requiring plan approval before execution. | MUST | BRD-CFG-001 | 1.1 | 13 Jan 2026 | — |

---

## 2. ade_v1 Flow (FLOW-V1)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| FLOW-V1-001 | ade_v1 flow MUST have exactly 13 steps with all required steps present. | MUST | BRD-FLOW-002 | 1.1 | 13 Jan 2026 | — |
| FLOW-V1-002 | ade_v1 MUST include steps: read (data_reader), viz_preferences (user_input), compute_business_metrics, sufficiency_eval, plan_proposal, compute_anomalies, build_chart_spec, hypothesis_data_outage, hypothesis_seasonality, assemble_decision_packet, assemble_evidence_bundle, assemble_business_report, render_business_report_html. | MUST | BRD-V1-006 | 1.1 | 13 Jan 2026 | — |
| FLOW-V1-003 | data_reader MUST execute as step 1 before any computation steps, with all subsequent steps able to reference its output. | MUST | BRD-V1-003 | 1.1 | 13 Jan 2026 | — |
| FLOW-V1-004 | viz_preferences MUST execute after data_reader and before compute_business_metrics so user sees dataset summary before selecting preferences. | MUST | BRD-V1-004 | 1.1 | 13 Jan 2026 | — |
| FLOW-V1-005 | plan_proposal MUST execute before hypothesis and assembly steps, pausing for user approval; rejection triggers error handling, approval proceeds to remaining steps. | MUST | BRD-V1-005, BRD-PLAN-004, BRD-PLAN-005 | 1.1 | 13 Jan 2026 | — |
| FLOW-V1-006 | Plan summary MUST include objective and expected evidence items. | MUST | BRD-PLAN-007 | 1.1 | 13 Jan 2026 | — |
| FLOW-V1-007 | Plan summary MUST include assumptions and risks. | MUST | BRD-PLAN-008 | 1.1 | 13 Jan 2026 | — |
| FLOW-V1-008 | Replan output MUST highlight what changed and why with change summary and rationale. | MUST | BRD-PLAN-009 | 1.1 | 13 Jan 2026 | — |

---

## 3. visualization Flow (FLOW-VIZ)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| FLOW-VIZ-001 | visualization flow MUST have exactly 15 steps. | MUST | BRD-FLOW-003 | 1.1 | 13 Jan 2026 | — |
| FLOW-VIZ-002 | visualization flow MUST start with intent_interpretation agent step using planning_agent before data reading. | MUST | BRD-VIZ-002 | 1.1 | 13 Jan 2026 | — |
| FLOW-VIZ-003 | visualization flow MUST use planning_agent twice: first for intent_interpretation (step 1), second for planning (step 6 after sufficiency_eval). | MUST | BRD-VIZ-002, BRD-VIZ-004 | 1.1 | 13 Jan 2026 | — |
| FLOW-VIZ-004 | visualization flow MUST include render_decision_packet_html step producing decision_packet.html. | MUST | BRD-VIZ-006 | 1.1 | 13 Jan 2026 | — |

---

## 4. User Input Steps (FLOW-INPUT)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| FLOW-INPUT-001 | viz_preferences MUST validate against schema with properties: chart_type (enum: bar/line/area/scatter), metric_focus (enum: mean/sum/median/growth_rate/anomalies), include_hypothesis_checks (boolean), notes (string). | MUST | BRD-PREF-001, BRD-PREF-002, BRD-PREF-003, BRD-PREF-004 | 1.1 | 13 Jan 2026 | — |
| FLOW-INPUT-002 | viz_preferences MUST require chart_type and metric_focus; include_hypothesis_checks and notes are optional. | MUST | BRD-PREF-001, BRD-PREF-002 | 1.1 | 13 Jan 2026 | — |
| FLOW-INPUT-003 | viz_preferences MUST provide defaults: chart_type=bar, metric_focus=mean (ade_v1) or anomalies (visualization), include_hypothesis_checks=true, notes="". | MUST | BRD-PREF-001, BRD-PREF-002 | 1.1 | 13 Jan 2026 | — |

---

## 5. Conditional Execution (FLOW-COND)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| FLOW-COND-001 | Hypothesis tests MUST respect include_hypothesis_checks flag: when false return status="skipped", when true execute normally, skipped tools produce valid output structure. | MUST | BRD-V1-007, BRD-VIZ-008 | 1.1 | 13 Jan 2026 | — |
| FLOW-COND-002 | Hypothesis tools MUST receive enabled parameter from user input via artifact reference: "{{artifacts.user_input.viz_preferences.values.include_hypothesis_checks}}". | MUST | BRD-V1-007 | 1.1 | 13 Jan 2026 | — |

---

## 6. Error Handling (FLOW-ERR)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| FLOW-ERR-001 | data_reader step MUST have retry configuration with max_attempts: 2 and backoff_seconds: 1. | MUST | BRD-V1-003 | 1.1 | 13 Jan 2026 | — |
| FLOW-ERR-002 | build_chart_spec MUST use fallback_chart_type="bar" when user selection is incompatible. | MUST | BRD-PREF-001 | 1.1 | 13 Jan 2026 | — |

---

## 7. Artifact References (FLOW-ARTF)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| FLOW-ARTF-001 | Tool outputs MUST be referenceable via syntax: {{artifacts.tool.<tool_name>.output.<field>}}. | MUST | BRD-DET-001 | 1.1 | 13 Jan 2026 | — |
| FLOW-ARTF-002 | User inputs MUST be referenceable via syntax: {{artifacts.user_input.<form_id>.values.<field>}}. | MUST | BRD-V1-004, BRD-VIZ-003 | 1.1 | 13 Jan 2026 | — |
| FLOW-ARTF-003 | Agent outputs MUST be referenceable via syntax: {{artifacts.agent.<agent_name>.output.<field>}}. | MUST | BRD-VIZ-002 | 1.1 | 13 Jan 2026 | — |
| FLOW-ARTF-004 | Payload fields MUST be referenceable via syntax: {{payload.<field>}}. | MUST | BRD-V1-001, BRD-VIZ-001 | 1.1 | 13 Jan 2026 | — |

---

## Cross-References

- **BRD**: [BRD-flows.md](../01_brd/BRD-flows.md)
