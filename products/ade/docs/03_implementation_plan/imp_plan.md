# ADE Implementation Plan (v1.2)

## Overview

**Purpose**: Implement Tech Spec requirements that are missing or only partially represented in System Design, without modifying System Design documents.

**Assumptions**:
- ADE product code exists under `products/ade/` with agents, tools, schemas, and flows as referenced by Tech Specs.
- Core framework primitives (orchestrator, governance, memory) are available and stable.
- Tech Specs under `products/ade/docs/02_techspec/` are the source of truth (V1.5 with TS- prefix normalization).

**Entry Criteria**:
- `products/ade/docs/02_techspec/TS-COVERAGE.md` shows full BRD→TS coverage.
- `products/ade/docs/04_systemdesign/SD-COVERAGE.md` is current and lists gaps (V1.2 with 20 gaps).
- ADE flows YAML are present and loadable.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-17 | Initial release with IMP-001 through IMP-016 |
| 1.1 | 2026-01-20 | Dependency ordering, non-goals |
| 1.2 | 2026-01-21 | Added IMP-017 through IMP-025 for V1.4/V1.5 Tech Spec gaps (GAP-020 through GAP-028) |

---

## Implementation Units

### IMP-001
- **Source Tech Spec IDs**: OBJ-001..OBJ-007
- **Related SD-COVERAGE Gap IDs**: GAP-001
- **Target Code Locations**: N/A (clarification)
- **Type of Change**: Clarification required
- **Steps**:
  1. Review OBJ-001..OBJ-007 in `products/ade/docs/02_techspec/IO-inputs-outputs.md`.
  2. Record which objectives are enforceable at runtime vs reporting-only.
  3. Capture clarification decisions in a project issue and link in plan notes.
- **Acceptance Checks**:
  - Clarification record exists for OBJ-001..OBJ-007.

---

### IMP-003
- **Source Tech Spec IDs**: BRD-INTEL-001..005
- **Related SD-COVERAGE Gap IDs**: GAP-003
- **Target Code Locations**: `products/ade/agents/plan_agent.py`, `products/ade/agents/plan_proposal_agent.py`, `products/ade/agents/critic_evaluator.py`
- **Type of Change**: Code addition required
- **Steps**:
  1. Add stage markers (interpret/propose/critique/finalize) to agent outputs.
  2. Add a sufficiency state object to reasoning outputs (known/unknown/blocked).
  3. Emit a stop_reason field in final outputs.
- **Acceptance Checks**:
  - Outputs contain stage identifiers.
  - stop_reason is present in final outputs.

---

### IMP-004
- **Source Tech Spec IDs**: BRD-CRIT-001..005
- **Related SD-COVERAGE Gap IDs**: GAP-004
- **Target Code Locations**: `products/ade/agents/critic_evaluator.py`, `products/ade/agents/plan_proposal_agent.py`
- **Type of Change**: Code addition required
- **Steps**:
  1. Implement critique evaluation output with evidence gap list.
  2. Add revised_confidence and downgrade_reason fields.
  3. Trigger ASK_USER/ABORT when critique blocks.
- **Acceptance Checks**:
  - Critique output exists for each run.
  - Blocking critique results stop execution.

---

### IMP-005
- **Source Tech Spec IDs**: BRD-TOOLSEL-001..004
- **Related SD-COVERAGE Gap IDs**: GAP-005
- **Target Code Locations**: `products/ade/agents/plan_agent.py`, `products/ade/agents/plan_proposal_agent.py`
- **Type of Change**: Wiring / integration only
- **Steps**:
  1. Add advisory tool recommendations to planning outputs.
  2. Ensure recommendations are marked optional and non-binding.
- **Acceptance Checks**:
  - Plan outputs list tool recommendations with rationales.
  - No recommendation forces execution.

---

### IMP-006
- **Source Tech Spec IDs**: BRD-NARR-004
- **Related SD-COVERAGE Gap IDs**: GAP-006
- **Target Code Locations**: `products/ade/agents/dashboard_agent.py`
- **Type of Change**: Code extension required
- **Steps**:
  1. Include anomaly interpretation text when anomaly artifacts are present.
  2. Add anomaly summary fields to narrative output schema.
- **Acceptance Checks**:
  - Narrative references anomalies when detected.

---

### IMP-007
- **Source Tech Spec IDs**: BRD-CONF-005
- **Related SD-COVERAGE Gap IDs**: GAP-007
- **Target Code Locations**: `products/ade/config/product.yaml`, `products/ade/agents/*`
- **Type of Change**: Code extension required
- **Steps**:
  1. Add configurable confidence thresholds to product config.
  2. Read thresholds in intent and critique evaluation.
- **Acceptance Checks**:
  - Thresholds applied without code changes.

---

### IMP-008
- **Source Tech Spec IDs**: BRD-PLAN-007..009
- **Related SD-COVERAGE Gap IDs**: GAP-008
- **Target Code Locations**: `products/ade/agents/plan_proposal_agent.py`, `products/ade/agents/planning_agent.py`
- **Type of Change**: Code extension required
- **Steps**:
  1. Add objective and expected evidence to plan summary output.
  2. Add assumptions and risks fields.
  3. For replans, add change summary and rationale fields.
- **Acceptance Checks**:
  - Plan summaries contain objective, evidence, assumptions, risks.
  - Replan output includes diff and rationale.

---

### IMP-011
- **Source Tech Spec IDs**: BRD-CTX-001..004
- **Related SD-COVERAGE Gap IDs**: GAP-012
- **Target Code Locations**: `products/ade/tools/context_pack_builder.py`, `products/ade/flows/*.yaml`, `products/ade/schemas/*`
- **Type of Change**: Code addition required
- **Steps**:
  1. Implement context pack builder tool to compute dataset profile and coverage.
  2. Persist context pack as a run artifact.
  3. Insert context pack step after data ingestion in flows.
- **Acceptance Checks**:
  - Context pack exists before planning steps.
  - Reasoning outputs reference context pack artifacts.

---

### IMP-012
- **Source Tech Spec IDs**: BRD-VAL-001..003
- **Related SD-COVERAGE Gap IDs**: GAP-013
- **Target Code Locations**: `products/ade/tools/assemble_business_report.py`, `products/ade/tools/assemble_decision_packet.py`, `products/ade/tools/render_*`
- **Type of Change**: Wiring / integration only
- **Steps**:
  1. Validate all outputs against Pydantic schemas before rendering.
  2. Emit clear validation errors with field paths.
- **Acceptance Checks**:
  - Rendering blocked when validation fails.

---

### IMP-013
- **Source Tech Spec IDs**: BRD-QUAL-001..004, BRD-QUAL-010..012
- **Related SD-COVERAGE Gap IDs**: GAP-014
- **Target Code Locations**: `products/ade/tools/assemble_*`, `products/ade/tools/render_*`
- **Type of Change**: Code extension required
- **Steps**:
  1. Add quality checks for executive summary, findings, recommendations.
  2. Validate chart/table rendering outputs.
- **Acceptance Checks**:
  - Quality checks are enforced before output finalization.

---

### IMP-014
- **Source Tech Spec IDs**: BRD-VER-001..003
- **Related SD-COVERAGE Gap IDs**: GAP-015
- **Target Code Locations**: `products/ade/tools/assemble_*`, `products/ade/schemas/*`
- **Type of Change**: Code extension required
- **Steps**:
  1. Add version metadata fields to output schemas.
  2. Populate product/flow/schema/tool versions in outputs.
  3. Record dataset hash and input hash.
- **Acceptance Checks**:
  - Outputs include version and hash metadata.

---

### IMP-015
- **Source Tech Spec IDs**: BRD-DAB-001..005
- **Related SD-COVERAGE Gap IDs**: GAP-016
- **Target Code Locations**: `products/ade/tools/render_*`, `products/ade/templates/*`
- **Type of Change**: Code extension required
- **Steps**:
  1. Add advisory labeling to report and decision packet templates.
  2. Ensure confidence language is non-decisional.
- **Acceptance Checks**:
  - Output text uses recommendation/findings terminology.

---

### IMP-016
- **Source Tech Spec IDs**: BRD-ALIGN-001..002, BRD-FRI-001..005, BRD-NRL-001..004
- **Related SD-COVERAGE Gap IDs**: GAP-017, GAP-018, GAP-019
- **Target Code Locations**: N/A (clarification)
- **Type of Change**: Clarification required
- **Steps**:
  1. Define enforcement mechanisms (tests vs runtime checks) for alignment/reliance/no-learning constraints.
  2. Record decisions in a tracked issue and link here.
- **Acceptance Checks**:
  - Clarification record exists with enforcement decision.

---

### IMP-017
- **Source Tech Spec IDs**: TS-AGENT-TERM-001, TS-AGENT-TERM-002, TS-AGENT-TERM-003
- **Related SD-COVERAGE Gap IDs**: GAP-020
- **Target Code Locations**: `products/ade/schemas/terminal_outcome.py`, `products/ade/schemas/run_result.py`, `products/ade/agents/*`
- **Type of Change**: Code addition required
- **Steps**:
  1. Create `TerminalOutcome` enum in `products/ade/schemas/terminal_outcome.py` with values: SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT.
  2. Add `PartialSuccessDetails` schema with fields: `completed_steps: List[str]`, `missing_steps: List[str]`, `reason: str`.
  3. Add `terminal_artifact: Dict[str, Any]` field to `RunResult` schema.
  4. Ensure all agents emit explicit terminal outcomes on completion or abort.
- **Acceptance Checks**:
  - TerminalOutcome enum exists with all four values.
  - PARTIAL_SUCCESS outcomes include PartialSuccessDetails.
  - All run completions have a terminal_artifact with explanation.
- **Estimated Effort**: 1.5 days

---

### IMP-018
- **Source Tech Spec IDs**: TS-AGENT-NARR-005
- **Related SD-COVERAGE Gap IDs**: GAP-021
- **Target Code Locations**: `products/ade/narrative.py`, `products/ade/tools/assemble_business_report.py`
- **Type of Change**: Code addition required
- **Steps**:
  1. Create `products/ade/narrative.py` with `build_explanation(decision_records: List[DecisionRecord]) -> str`.
  2. Integrate with `core.memory.observability_store.get_decision_records(run_id)`.
  3. Ensure user-facing explanations derive from platform decision records, not regenerated text.
- **Acceptance Checks**:
  - `narrative.py` exists with `build_explanation()` function.
  - Explanations reference decision record IDs.
  - No LLM regeneration of explanations.
- **Estimated Effort**: 1 day

---

### IMP-019
- **Source Tech Spec IDs**: TS-AGENT-CONF-003
- **Related SD-COVERAGE Gap IDs**: GAP-022
- **Target Code Locations**: `products/ade/configs/confidence.yaml`, `products/ade/config.py`
- **Type of Change**: Code extension required
- **Steps**:
  1. Create `products/ade/configs/confidence.yaml` with keys: `low_threshold: float`, `high_threshold: float`, `sufficiency_thresholds: Dict`.
  2. Add `load_confidence_config()` to `products/ade/config.py` returning `ConfidenceConfig(BaseModel)`.
  3. Update `intent_agent` and `sufficiency_evaluator` to read thresholds from config.
- **Acceptance Checks**:
  - `confidence.yaml` exists with configurable thresholds.
  - Changing thresholds in YAML changes agent behavior without code changes.
- **Estimated Effort**: 0.5 days

---

### IMP-020
- **Source Tech Spec IDs**: TS-SEM-VALIDATE-008, TS-SEM-VALIDATE-009
- **Related SD-COVERAGE Gap IDs**: GAP-023
- **Target Code Locations**: `products/ade/semantic_validation.py`
- **Type of Change**: Code addition required
- **Steps**:
  1. Add `_validate_dataset_ref(dataset: str, available: List[str]) -> bool` to semantic_validation.py.
  2. Add `_validate_metric_ref(metric: str, schema: DatasetSchema) -> bool` to semantic_validation.py.
  3. Return `ASK_USER` outcome with clarifying question when references are invalid.
- **Acceptance Checks**:
  - Invalid dataset references trigger ASK_USER.
  - Invalid metric references trigger ASK_USER.
  - Validation happens before planning proceeds.
- **Estimated Effort**: 1 day

---

### IMP-021
- **Source Tech Spec IDs**: TS-TOOL-GEN-007
- **Related SD-COVERAGE Gap IDs**: GAP-024
- **Target Code Locations**: CI configuration, `tests/unit/test_tool_dependencies.py`
- **Type of Change**: CI/test enforcement required
- **Steps**:
  1. Add static check to CI: `grep -r "import requests\|import urllib\|import httpx" products/ade/tools/` must return empty.
  2. Add unit test `test_tool_dependencies.py` to verify no external network imports in tool modules.
  3. Document policy in `products/ade/docs/TOOL_GUIDELINES.md`.
- **Acceptance Checks**:
  - CI fails if network imports found in tools.
  - Unit test passes verifying no external dependencies.
- **Estimated Effort**: 0.5 days

---

### IMP-022
- **Source Tech Spec IDs**: TS-TOOL-ANALYSIS-008
- **Related SD-COVERAGE Gap IDs**: GAP-025
- **Target Code Locations**: `products/ade/tools/anomaly_detection.py`, `products/ade/schemas/anomaly_output.py`
- **Type of Change**: Code extension required
- **Steps**:
  1. Add `severity_score: float = abs(z_score)` field to `AnomalyRow` schema.
  2. Update `detect_anomalies()` to sort anomalies by severity_score descending.
  3. Update tests to verify severity ranking.
- **Acceptance Checks**:
  - Anomalies are returned sorted by severity (highest first).
  - `severity_score` field present on all anomaly rows.
- **Estimated Effort**: 0.5 days

---

### IMP-023
- **Source Tech Spec IDs**: TS-IO-OUT-007
- **Related SD-COVERAGE Gap IDs**: GAP-026
- **Target Code Locations**: `products/ade/tools/render_report.py`, `products/ade/tools/render_packet.py`
- **Type of Change**: Code addition required
- **Steps**:
  1. Add `OUTPUT_DIR.mkdir(parents=True, exist_ok=True)` before any write operations in render tools.
  2. Ensure consistent behavior across all output writers.
- **Acceptance Checks**:
  - Outputs succeed even if `staging/output/` directory doesn't exist.
  - Directory is created automatically.
- **Estimated Effort**: 0.25 days

---

### IMP-024
- **Source Tech Spec IDs**: TS-FLOW-V1-006, TS-FLOW-V1-007, TS-FLOW-V1-008, TS-FLOW-V1-009
- **Related SD-COVERAGE Gap IDs**: GAP-027
- **Target Code Locations**: `products/ade/agents/plan_proposal_agent.py`, `products/ade/agents/planning_agent.py`, `products/ade/schemas/plan_summary.py`
- **Type of Change**: Code extension required
- **Steps**:
  1. Add `objective: str` and `expected_evidence: List[str]` to `PlanSummary` schema.
  2. Add `assumptions: List[str]` and `risks: List[str]` to `PlanSummary` schema.
  3. Add `change_summary: str` and `rationale: str` to `ReplanOutput` schema.
  4. Add `constraints: PlanConstraints` to `PlanApproval` schema with fields: `time_limit_seconds`, `max_iterations`, `hypothesis_enabled`.
  5. Update `plan_proposal_agent` and `planning_agent` to populate these fields.
- **Acceptance Checks**:
  - Plan summaries include objective, evidence, assumptions, risks.
  - Replan outputs include change summary and rationale.
  - Users can approve plans with constraints.
- **Estimated Effort**: 2 days

---

### IMP-025
- **Source Tech Spec IDs**: TS-SCHEMA-EVITEM-001, TS-SCHEMA-EVITEM-002, TS-SCHEMA-CTX-004, TS-SCHEMA-CTX-005
- **Related SD-COVERAGE Gap IDs**: GAP-028, GAP-012
- **Target Code Locations**: `products/ade/schemas/evidence.py`, `products/ade/schemas/context_pack.py`
- **Type of Change**: Schema addition required
- **Steps**:
  1. Add `confidence: float = Field(ge=0.0, le=1.0)` to `EvidenceItem` schema.
  2. Add `values: Dict[str, Any] = Field(default_factory=dict)` to `EvidenceItem` schema.
  3. Update Context Pack to include evidence items with dataset_id/columns.
  4. Ensure reasoning references Context Pack artifacts as sole grounding source.
- **Acceptance Checks**:
  - EvidenceItem includes confidence and values fields.
  - Context Pack evidence items reference dataset_id and columns.
  - Reasoning outputs cite context pack artifacts.
- **Estimated Effort**: 1 day

---

## Dependency Order

### Phase 1: Clarifications (Required before build)
1. IMP-001 (objectives clarification)
2. IMP-016 (alignment/reliance/no runtime learning clarifications)

### Phase 2: Core Reasoning & Outcomes
3. IMP-003 (reasoning ladder)
4. IMP-017 (terminal outcomes)
5. IMP-004 (critique)

### Phase 3: Planning & Validation
6. IMP-005 (advisory tool selection)
7. IMP-024 (plan detail + replan diff + constraints)
8. IMP-020 (dataset/metric validation)

### Phase 4: Configuration & Evidence
9. IMP-007 (confidence thresholds)
10. IMP-019 (confidence configuration)
11. IMP-025 (evidence item schema + context pack grounding)
12. IMP-011 (context pack)

### Phase 5: Narrative & Quality
13. IMP-006 (anomaly narrative)
14. IMP-018 (narrative source from decision records)
15. IMP-022 (anomaly severity ranking)

### Phase 6: Output Finalization
16. IMP-012 (validation gating)
17. IMP-013 (output quality)
18. IMP-023 (output directory creation)
19. IMP-014 (version transparency)
20. IMP-015 (decision authority boundary)

### Phase 7: Enforcement
21. IMP-021 (tool network dependency enforcement)

---

## Estimated Total Effort

| Phase | IMP Units | Estimated Days |
|-------|-----------|----------------|
| Phase 1 | IMP-001, IMP-016 | 1 day (clarification) |
| Phase 2 | IMP-003, IMP-017, IMP-004 | 4 days |
| Phase 3 | IMP-005, IMP-024, IMP-020 | 4 days |
| Phase 4 | IMP-007, IMP-019, IMP-025, IMP-011 | 4.5 days |
| Phase 5 | IMP-006, IMP-018, IMP-022 | 2.5 days |
| Phase 6 | IMP-012, IMP-013, IMP-023, IMP-014, IMP-015 | 4 days |
| Phase 7 | IMP-021 | 0.5 days |
| **Total** | **21 IMP units** | **~20.5 engineering days** |

---

## Non-Goals

- Editing any System Design documents under `products/ade/docs/04_systemdesign/`.
- Implementing features not defined in Tech Specs.
- Changing BRD requirements or IDs.

---

## Final Verification Checklist

- [x] Every Tech Spec ID in SD-COVERAGE gap register is mapped to an IMP unit.
- [x] IMP units reference exact Tech Spec IDs and SD gap IDs.
- [x] No remaining SD-COVERAGE gaps impacting runtime without a plan.
- [x] All new V1.4/V1.5 Tech Spec requirements (TS-AGENT-TERM-*, TS-AGENT-NARR-005, TS-AGENT-CONF-003, TS-SEM-VALIDATE-008/009, TS-TOOL-GEN-007, TS-TOOL-ANALYSIS-008, TS-IO-OUT-007, TS-FLOW-V1-006..009, TS-SCHEMA-EVITEM-*, TS-SCHEMA-CTX-004/005) have corresponding IMP units.

---

## Traceability Summary

| Gap ID Range | IMP Unit Range | Count |
|--------------|----------------|-------|
| GAP-001 | IMP-001 | 1 |
| GAP-003 | IMP-003 | 1 |
| GAP-004 | IMP-004 | 1 |
| GAP-006 | IMP-006 | 1 |
| GAP-012 | IMP-011, IMP-025 | 2 |
| GAP-014 | IMP-013 | 1 |
| GAP-015 | IMP-014 | 1 |
| GAP-016 | IMP-015 | 1 |
| GAP-017..019 | IMP-016 | 1 |
| GAP-020 | IMP-017 | 1 |
| GAP-021 | IMP-018 | 1 |
| GAP-022 | IMP-019 | 1 |
| GAP-023 | IMP-020 | 1 |
| GAP-024 | IMP-021 | 1 |
| GAP-025 | IMP-022 | 1 |
| GAP-026 | IMP-023 | 1 |
| GAP-027 | IMP-024 | 1 |
| GAP-028 | IMP-025 | 1 |
| **Total** | **21 IMP units** | **20 Gaps** |
