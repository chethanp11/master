# ADE Implementation Strategy

**Prepared**: 2026-01-21  
**Plan Version**: v1.2  
**Total Units**: 21 (IMP-001 through IMP-025, skipping IMP-002, IMP-009, IMP-010)  
**Total Estimated Effort**: ~20.5 engineering days

---

## A) Unit Inventory Table

| Unit ID | Tech Spec ID(s) | Target Code Locations | Change Type | Primary Tests | Risk Notes |
|---------|---|---|---|---|---|
| IMP-001 | OBJ-001..007 | N/A | Clarification | N/A | **Documentation only** - no code change. Decision recorded in tracked issue. |
| IMP-003 | BRD-INTEL-001..005 | `agents/plan_agent.py`, `agents/plan_proposal_agent.py`, `agents/critic_evaluator.py` | Code addition | Unit tests for stage markers, stop_reason | Affects output contracts; existing callers must tolerate new fields. |
| IMP-004 | BRD-CRIT-001..005 | `agents/critic_evaluator.py`, `agents/plan_proposal_agent.py` | Code addition | Unit tests for critique output, blocking behavior | Blocking behavior changes flow; needs integration tests. |
| IMP-005 | BRD-TOOLSEL-001..004 | `agents/plan_agent.py`, `agents/plan_proposal_agent.py` | Wiring/integration | Unit tests for recommendation fields | Non-breaking; new optional fields. |
| IMP-006 | BRD-NARR-004 | `agents/dashboard_agent.py` | Code extension | Unit tests for anomaly references in narrative | Low risk; additive. |
| IMP-007 | BRD-CONF-005 | `config/product.yaml`, `agents/*` | Code extension | Unit tests for threshold application | Config-driven; test behavior with different thresholds. |
| IMP-008 | BRD-PLAN-007..009 | `agents/plan_proposal_agent.py`, `agents/planning_agent.py` | Code extension | Unit tests for plan summary fields, replan diff | Additive; non-breaking. |
| IMP-011 | BRD-CTX-001..004 | `tools/context_pack_builder.py`, `flows/*.yaml`, `schemas/*` | Code addition | Unit tests for context pack creation, persistence | New tool; integration test for flow insertion. |
| IMP-012 | BRD-VAL-001..003 | `tools/assemble_business_report.py`, `tools/assemble_decision_packet.py`, `tools/render_*` | Wiring/integration | Unit tests for validation blocking rendering | Blocking change; test error paths. |
| IMP-013 | BRD-QUAL-001..004, BRD-QUAL-010..012 | `tools/assemble_*`, `tools/render_*` | Code extension | Unit tests for quality checks (summary, findings, recommendations, charts) | New validation layer; test all output types. |
| IMP-014 | BRD-VER-001..003 | `tools/assemble_*`, `schemas/*` | Code extension | Unit tests for version/hash metadata | Additive; non-breaking. |
| IMP-015 | BRD-DAB-001..005 | `tools/render_*`, `templates/*` | Code extension | Unit tests for advisory labeling in templates | Additive; text changes only. |
| IMP-016 | BRD-ALIGN-001..002, BRD-FRI-001..005, BRD-NRL-001..004 | N/A | Clarification | N/A | **Documentation only** - no code change. Decision recorded in tracked issue. |
| IMP-017 | TS-AGENT-TERM-001..003 | `schemas/terminal_outcome.py`, `schemas/run_result.py`, `agents/*` | Code addition | Unit tests for enum values, partial success details, terminal artifacts | New schema; affects all agent outputs; must test all terminal paths. |
| IMP-018 | TS-AGENT-NARR-005 | `narrative.py`, `tools/assemble_business_report.py` | Code addition | Unit tests for narrative building from decision records | New module; integration with observability store. |
| IMP-019 | TS-AGENT-CONF-003 | `configs/confidence.yaml`, `config.py` | Code extension | Unit tests for threshold loading and application | Config-driven; test YAML parsing and fallback. |
| IMP-020 | TS-SEM-VALIDATE-008..009 | `semantic_validation.py` | Code addition | Unit tests for dataset/metric validation, ASK_USER outcome | New validation functions; test invalid references. |
| IMP-021 | TS-TOOL-GEN-007 | CI config, `tests/unit/test_tool_dependencies.py` | CI/test enforcement | Static grep check, unit test for import verification | CI blocking; test must verify absence of external network imports. |
| IMP-022 | TS-TOOL-ANALYSIS-008 | `tools/anomaly_detection.py`, `schemas/anomaly_output.py` | Code extension | Unit tests for severity score calculation and sorting | Non-breaking; additive field and behavior. |
| IMP-023 | TS-IO-OUT-007 | `tools/render_report.py`, `tools/render_packet.py` | Code addition | Unit tests for directory creation in render tools | Non-breaking; defensive coding. |
| IMP-024 | TS-FLOW-V1-006..009 | `agents/plan_proposal_agent.py`, `agents/planning_agent.py`, `schemas/plan_summary.py` | Code extension | Unit tests for plan fields (objective, evidence, assumptions, risks), replan rationale, constraints | Major schema extension; test all new fields on both create and replan paths. |
| IMP-025 | TS-SCHEMA-EVITEM-001..002, TS-SCHEMA-CTX-004..005 | `schemas/evidence.py`, `schemas/context_pack.py` | Schema addition | Unit tests for evidence confidence/values, context pack evidence references | Schema changes; test backward compatibility. |

---

## B) Execution Approach

### Sequencing

The plan follows a **7-phase dependency graph**:

1. **Phase 1 — Clarifications** (Parallel, documentation-only)
   - **IMP-001**: Objectives (OBJ-001..007) enforcement clarification
   - **IMP-016**: Alignment/Reliance/No-Learning enforcement clarification
   - **Action**: Create tracked GitHub issues documenting decisions; link in plan notes.
   - **Acceptance**: Clarification records exist with enforcement mechanism specified (test vs runtime vs documentation).
   - **Time**: ~1 day (research + doc)

2. **Phase 2 — Core Reasoning & Outcomes** (Sequential)
   - **IMP-003** → **IMP-017** → **IMP-004**
   - Implement reasoning ladder (stage markers, stop_reason), terminal outcomes, and critique.
   - **Rationale**: Terminal outcomes are required by downstream phases; critique depends on stage markers.
   - **Time**: ~4 days

3. **Phase 3 — Planning & Validation** (Sequential)
   - **IMP-005** → **IMP-024** → **IMP-020**
   - Add advisory tool recommendations, plan detail fields (objective, assumptions, risks, constraints, replan diff), and dataset/metric validation.
   - **Rationale**: Validation must happen before planning proceeds.
   - **Time**: ~4 days

4. **Phase 4 — Configuration & Evidence** (Mostly parallel, one blocker)
   - **IMP-007**, **IMP-019** (parallel) → **IMP-025** → **IMP-011**
   - Load confidence thresholds from config, define evidence schema with confidence/values, build context pack.
   - **Rationale**: Evidence schema required by context pack; both fed by confidence config.
   - **Time**: ~4.5 days

5. **Phase 5 — Narrative & Quality** (Sequential)
   - **IMP-006** → **IMP-018** → **IMP-022**
   - Add anomaly narrative references, build narrative from decision records, sort anomalies by severity.
   - **Rationale**: Narrative builder needs anomaly data and severity ranking.
   - **Time**: ~2.5 days

6. **Phase 6 — Output Finalization** (Sequential with one dependency)
   - **IMP-012** → **IMP-013** → (**IMP-023**, **IMP-014**, **IMP-015** in parallel)
   - Validate outputs, enforce quality checks, create output directories, add version metadata, advisory labeling.
   - **Rationale**: Validation gates quality and versioning; labeling is independent.
   - **Time**: ~4 days

7. **Phase 7 — Enforcement** (Final)
   - **IMP-021**: Tool dependency CI enforcement.
   - **Action**: Add static checks and unit tests to CI.
   - **Time**: ~0.5 days

**Total Estimated Effort**: ~20.5 days

---

### Testing Strategy: Fast → Full

For each unit, follow this testing hierarchy:

1. **Unit Tests** (Fastest, run first)
   - Test the minimal changed component in isolation.
   - Use mocks for dependencies; verify new fields/functions directly.
   - **Expected runtime**: < 1 second per unit

2. **Related Integration Tests** (Medium, run if unit tests pass)
   - Test cross-module interaction (e.g., agent + schema, tool + output).
   - Use realistic fixtures; verify end-to-end behavior for the affected flow section.
   - **Expected runtime**: 5–10 seconds per unit

3. **Full Smoke Tests** (Slowest, run if integration tests pass)
   - Test complete flow from input to output (if major changes).
   - Only for Phase 2–7 units that impact flow logic or output contracts.
   - **Expected runtime**: 10–30 seconds per flow

4. **CI Enforcement** (Static checks)
   - For IMP-021, add grep-based static checks to CI pipeline.

---

### Validation for "Done" on Each Unit

An IMP unit is **Done** when:

1. **Code changes implemented** per unit description (files created/modified/deleted).
2. **Unit tests pass** (100% green for target code).
3. **Related integration tests pass** (if applicable).
4. **Acceptance checks satisfied**:
   - All behavioral requirements listed in unit description are observable/testable.
   - All new fields/functions exist and are wired into calling code.
   - No existing tests broken (backward compatibility preserved unless explicitly required by IMP).
5. **Outcome logged** in `imp_outcome.md` with:
   - Tech Spec IDs + code locations
   - Concrete behaviors implemented
   - Test commands + results
   - Deviations/decisions documented

**Blocker Rule**: If any test fails, diagnose and fix code (or tests if incorrect) before proceeding to the next unit. No partial greens allowed.

---

## C) Risk Assessment & Mitigation

| Risk | Phase | Severity | Mitigation |
|------|-------|----------|-----------|
| Terminal outcome enum added; existing code not updated to handle | 2 (IMP-017) | **HIGH** | Add comprehensive agent tests verifying all agents emit terminal outcomes; use type hints to catch unmapped paths. |
| Schema extensions (evidence, context pack, plan) break existing code | 4–5 (IMP-025, IMP-024) | **MEDIUM** | Add default values to new fields; test backward compatibility with old code. |
| Validation blocking rendering (IMP-012) causes unexpected flow failures | 6 (IMP-012) | **MEDIUM** | Test all validation paths (success + error) in unit + integration tests. |
| Confidence thresholds config missing or invalid | 4 (IMP-019) | **MEDIUM** | Provide default values in code; test YAML parsing with invalid/missing config. |
| Network imports in tools not caught by static checks | 7 (IMP-021) | **LOW** | CI check must use strict grep; add unit test to double-check. |

---

## D) Code & Test Organization

### Code Layout Assumptions

- **Schemas**: `/products/ade/schemas/*.py` (Pydantic models)
- **Agents**: `/products/ade/agents/*.py` (agent implementations)
- **Tools**: `/products/ade/tools/*.py` (tool/utility implementations)
- **Config**: `/products/ade/config/` (config loading and YAML files)
- **Flows**: `/products/ade/flows/*.yaml` (orchestration YAML)

### Test Layout Assumptions

- **Unit tests**: `/products/ade/tests/unit/` (one file per module or feature)
- **Integration tests**: `/products/ade/tests/integration/` (cross-module scenarios)
- **Fixtures**: `/products/ade/tests/conftest.py` (shared test data and mocks)

### Test Naming Convention

- Unit test for `agents/plan_agent.py` → `tests/unit/test_plan_agent.py`
- Integration test for planning flow → `tests/integration/test_planning_flow.py`
- Test for new feature IMP-017 → `test_terminal_outcomes.py` or feature-specific file

---

## E) Acceptance Criteria Summary

| Phase | "Done" When... |
|-------|---|
| Phase 1 (Clarification) | Tracked issues created and linked; decision rationale recorded. |
| Phase 2 (Reasoning & Outcomes) | All agents emit stage markers, stop_reason, terminal outcomes; unit + integration tests pass. |
| Phase 3 (Planning & Validation) | Plans include objective/evidence/assumptions/risks; validation rejects invalid dataset/metric refs; tests pass. |
| Phase 4 (Config & Evidence) | Confidence config loaded from YAML; evidence items have confidence/values; context pack persists; tests pass. |
| Phase 5 (Narrative & Quality) | Anomalies referenced in narrative; narrative built from decision records; anomalies sorted by severity; tests pass. |
| Phase 6 (Output Finalization) | All outputs validated before rendering; quality checks enforced; version metadata included; advisory labels applied; output directories auto-created; tests pass. |
| Phase 7 (Enforcement) | CI rejects tools with network imports; unit test verifies same; tests pass. |

---

## F) Expected Deliverables

### Code Deliverables

1. New schemas: `terminal_outcome.py`, `narrative.py` (if new module)
2. Updated schemas: `run_result.py`, `evidence.py`, `context_pack.py`, `plan_summary.py`, `anomaly_output.py`, `version_metadata.py`
3. Config files: `products/ade/config/confidence.yaml`
4. New tools: `semantic_validation.py` extensions (or new file if not present)
5. Tool updates: `assemble_business_report.py`, `assemble_decision_packet.py`, `anomaly_detection.py`, `render_report.py`, `render_packet.py`
6. Agent updates: All agents (`plan_agent.py`, `plan_proposal_agent.py`, `critic_evaluator.py`, etc.)
7. Config updates: `config.py` to load confidence config
8. Flow updates: Flow YAML to insert context pack step
9. CI updates: Test enforcement for tool dependencies

### Test Deliverables

1. Unit tests for each new/modified function (estimated ~30–40 new test cases)
2. Integration tests for flow changes (estimated ~5–10 test scenarios)
3. Static checks in CI for tool dependency enforcement
4. Test coverage report (target: > 80% for new code)

### Documentation Deliverables

1. `imp_outcome.md` with entry for each IMP unit (populated incrementally)
2. Clarification records (GitHub issues) for IMP-001, IMP-016
3. Optional: `TOOL_GUIDELINES.md` documenting tool policy (if new)

---

## G) Next Steps

1. **Create** `imp_outcome.md` as blank file (ready for incremental population).
2. **Execute Phase 1** (IMP-001, IMP-016) — create clarification issues and document decisions.
3. **Execute Phase 2** (IMP-003, IMP-017, IMP-004) — implement reasoning, outcomes, critique.
4. **Continue** through Phases 3–7 sequentially, testing and logging outcomes after each unit.
5. **Verify** at completion that all tests pass, all IMP units have outcome entries, and code is traceable to Tech Spec IDs.

---

## Ready to Execute

All units are mapped, dependencies are clear, test strategy is defined. Ready to begin **Phase 1 (IMP-001, IMP-016)** or proceed directly to **Phase 2** if clarifications are externalized to tracked issues.
