# ADE Flow Technical Specification

> **Document**: Technical Specification — Flows  
> **Prefix**: TS-FLOW-*  
> **Version**: 1.4  
> **Last Updated**: 2026-01-20

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added visualization flow requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |
| 1.3 | 2026-01-21 | Added plan approval constraints requirement per gap analysis. |
| 1.4 | 2026-01-20 | Converted all TSD IDs to TS- prefix; added implementation-level technical details (file paths, step configs, executors). |

---

## 1. Flow Execution (TS-FLOW-EXEC)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-FLOW-EXEC-001 | Flows MUST execute deterministically—same inputs produce same outputs; no random or time-based variations except timestamps. | Enforcement: No `random` module in flow steps; No `datetime.now()` in computation; Determinism tests in `tests/unit/test_flow_determinism.py` | MUST | BRD-DET-001, BRD-DET-002, BRD-DET-003 | — |
| TS-FLOW-EXEC-002 | Flow steps MUST execute in YAML-defined sequence with dependencies completing before dependent steps and artifact references resolving to prior outputs. | Executor: `core.orchestrator.step_executor.py::StepExecutor.execute()`; Resolver: `core.orchestrator.normalization.py::resolve_artifact_ref()` | MUST | BRD-DET-001 | — |
| TS-FLOW-EXEC-003 | All ADE flows MUST use autonomy_level: "suggest_only" requiring plan approval before execution. | Config: `products/ade/flows/*.yaml`; Field: `autonomy_level: "suggest_only"`; Validator: `assert flow_config.autonomy_level == "suggest_only"` | MUST | BRD-CFG-001 | — |

---

## 2. ade_v1 Flow (TS-FLOW-V1)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-FLOW-V1-001 | ade_v1 flow MUST have exactly 13 steps with all required steps present. | File: `products/ade/flows/ade_v1.yaml`; Validation: `assert len(flow.steps) == 13` | MUST | BRD-FLOW-002 | — |
| TS-FLOW-V1-002 | ade_v1 MUST include steps: read (data_reader), viz_preferences (user_input), compute_business_metrics, sufficiency_eval, plan_proposal, compute_anomalies, build_chart_spec, hypothesis_data_outage, hypothesis_seasonality, assemble_decision_packet, assemble_evidence_bundle, assemble_business_report, render_business_report_html. | YAML structure: `steps: [{step_id: read, tool: data_reader}, {step_id: viz_preferences, step_type: hitl}, ...]` | MUST | BRD-V1-006 | — |
| TS-FLOW-V1-003 | data_reader MUST execute as step 1 before any computation steps, with all subsequent steps able to reference its output. | Step config: `step_id: read`; `index: 0`; Artifact: `{{artifacts.tool.read.output.*}}` | MUST | BRD-V1-003 | — |
| TS-FLOW-V1-004 | viz_preferences MUST execute after data_reader and before compute_business_metrics so user sees dataset summary before selecting preferences. | Step order: `[read (0), viz_preferences (1), compute_business_metrics (2)]`; Form context: `{{artifacts.tool.read.output.columns}}` | MUST | BRD-V1-004 | — |
| TS-FLOW-V1-005 | plan_proposal MUST execute before hypothesis and assembly steps, pausing for user approval; rejection triggers error handling, approval proceeds to remaining steps. | Step config: `step_id: plan_proposal`; `step_type: hitl`; `on_reject: raise_error`; `on_approve: continue` | MUST | BRD-V1-005, BRD-PLAN-004, BRD-PLAN-005 | — |
| TS-FLOW-V1-006 | Plan summary MUST include objective and expected evidence items. | Schema: `PlanSummary.objective: str`; `PlanSummary.expected_evidence: List[str]`; Generator: `products/ade/agents/planning_agent.py` | MUST | BRD-PLAN-007 | — |
| TS-FLOW-V1-007 | Plan summary MUST include assumptions and risks. | Schema: `PlanSummary.assumptions: List[str]`; `PlanSummary.risks: List[str]` | MUST | BRD-PLAN-008 | — |
| TS-FLOW-V1-008 | Replan output MUST highlight what changed and why with change summary and rationale. | Schema: `ReplanOutput.change_summary: str`; `ReplanOutput.rationale: str`; Logic: diff previous vs current plan | MUST | BRD-PLAN-009 | — |
| TS-FLOW-V1-009 | Users MUST be able to approve plans with constraints including time window limits, iteration caps, and disabled hypothesis tests. | Schema: `PlanApproval.constraints: PlanConstraints`; Fields: `time_limit_seconds: int`, `max_iterations: int`, `hypothesis_enabled: bool` | MUST | BRD-PLAN-010 | — |

---

## 3. visualization Flow (TS-FLOW-VIZ)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-FLOW-VIZ-001 | visualization flow MUST have exactly 15 steps. | File: `products/ade/flows/visualization.yaml`; Validation: `assert len(flow.steps) == 15` | MUST | BRD-FLOW-003 | — |
| TS-FLOW-VIZ-002 | visualization flow MUST start with intent_interpretation agent step using planning_agent before data reading. | Step config: `step_id: intent_interpretation`; `step_type: agent`; `agent: planning_agent`; Index: 0 | MUST | BRD-VIZ-002 | — |
| TS-FLOW-VIZ-003 | visualization flow MUST use planning_agent twice: first for intent_interpretation (step 1), second for planning (step 6 after sufficiency_eval). | Steps: `[{index: 0, agent: planning_agent}, ..., {index: 5, agent: planning_agent}]`; Validation: `len([s for s in steps if s.agent == "planning_agent"]) == 2` | MUST | BRD-VIZ-002, BRD-VIZ-004 | — |
| TS-FLOW-VIZ-004 | visualization flow MUST include render_decision_packet_html step producing decision_packet.html. | Step config: `step_id: render_decision_packet`; `tool: render_decision_packet_html`; Output: `products/ade/staging/output/decision_packet.html` | MUST | BRD-VIZ-006 | — |

---

## 4. User Input Steps (TS-FLOW-INPUT)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-FLOW-INPUT-001 | viz_preferences MUST validate against schema with properties: chart_type (enum: bar/line/area/scatter), metric_focus (enum: mean/sum/median/growth_rate/anomalies), include_hypothesis_checks (boolean), notes (string). | Schema: `products/ade/schemas/viz_preferences.py::VizPreferences`; Validation: Pydantic model with enums | MUST | BRD-PREF-001, BRD-PREF-002, BRD-PREF-003, BRD-PREF-004 | — |
| TS-FLOW-INPUT-002 | viz_preferences MUST require chart_type and metric_focus; include_hypothesis_checks and notes are optional. | Schema: `chart_type: Literal[...] = Field(...)` (required); `notes: Optional[str] = None` (optional) | MUST | BRD-PREF-001, BRD-PREF-002 | — |
| TS-FLOW-INPUT-003 | viz_preferences MUST provide defaults: chart_type=bar, metric_focus=mean (ade_v1) or anomalies (visualization), include_hypothesis_checks=true, notes="". | Config: `products/ade/flows/ade_v1.yaml::steps[viz_preferences].defaults`; Values: `{chart_type: bar, metric_focus: mean, include_hypothesis_checks: true}` | MUST | BRD-PREF-001, BRD-PREF-002 | — |

---

## 5. Conditional Execution (TS-FLOW-COND)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-FLOW-COND-001 | Hypothesis tests MUST respect include_hypothesis_checks flag: when false return status="skipped", when true execute normally, skipped tools produce valid output structure. | Tool param: `enabled: bool`; Logic: `if not enabled: return HypothesisResult(status="skipped")`; Schema: `HypothesisResult.status: Literal["confirmed", "rejected", "skipped"]` | MUST | BRD-V1-007, BRD-VIZ-008 | — |
| TS-FLOW-COND-002 | Hypothesis tools MUST receive enabled parameter from user input via artifact reference: "{{artifacts.user_input.viz_preferences.values.include_hypothesis_checks}}". | Step config: `inputs: {enabled: "{{artifacts.user_input.viz_preferences.values.include_hypothesis_checks}}"}`; Resolver: `core.orchestrator.normalization.py` | MUST | BRD-V1-007 | — |

---

## 6. Error Handling (TS-FLOW-ERR)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-FLOW-ERR-001 | data_reader step MUST have retry configuration with max_attempts: 2 and backoff_seconds: 1. | Step config: `retry: {max_attempts: 2, backoff_seconds: 1}`; Executor: `core.orchestrator.step_executor.py::_execute_with_retry()` | MUST | BRD-V1-003 | — |
| TS-FLOW-ERR-002 | build_chart_spec MUST use fallback_chart_type="bar" when user selection is incompatible. | Tool param: `fallback_chart_type: str = "bar"`; Logic: `if not _is_compatible(chart_type, data): chart_type = fallback_chart_type` | MUST | BRD-PREF-001 | — |

---

## 7. Artifact References (TS-FLOW-ARTF)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-FLOW-ARTF-001 | Tool outputs MUST be referenceable via syntax: {{artifacts.tool.<tool_name>.output.<field>}}. | Parser: `core.orchestrator.normalization.py::resolve_artifact_ref()`; Regex: `r"\{\{artifacts\.tool\.(\w+)\.output\.(\w+)\}\}"`; Storage: `core.orchestrator.context.py::ExecutionContext.artifacts` | MUST | BRD-DET-001 | — |
| TS-FLOW-ARTF-002 | User inputs MUST be referenceable via syntax: {{artifacts.user_input.<form_id>.values.<field>}}. | Parser: `resolve_artifact_ref()`; Key: `artifacts.user_input.{form_id}.values`; Type: `Dict[str, Any]` | MUST | BRD-V1-004, BRD-VIZ-003 | — |
| TS-FLOW-ARTF-003 | Agent outputs MUST be referenceable via syntax: {{artifacts.agent.<agent_name>.output.<field>}}. | Parser: `resolve_artifact_ref()`; Key: `artifacts.agent.{agent_name}.output`; Type: `Dict[str, Any]` | MUST | BRD-VIZ-002 | — |
| TS-FLOW-ARTF-004 | Payload fields MUST be referenceable via syntax: {{payload.<field>}}. | Parser: `resolve_artifact_ref()`; Source: `ExecutionContext.payload: Dict[str, Any]` | MUST | BRD-V1-001, BRD-VIZ-001 | — |

---

## Cross-References

- **BRD**: [BRD-flows.md](../01_brd/BRD-flows.md)
- **System Design**: [flows.md](../04_systemdesign/flows.md)
