# ADE Implementation Gaps (Plan vs Outcome vs Code vs System Design)

## Summary
- Plan units total (in-scope): 13
- Units verified: 4
- Units partial: 6
- Units missing: 2
- Outcome overclaims: 1
- Doc drift items: 0
- Test gaps: 2
- Last updated: 2026-01-17

## Reconciliation Table
| IMP Unit | TS IDs | Plan | Outcome | Code Evidence | SD Evidence | Test Evidence | Status |
|---|---|---|---|---|---|---|---|
| IMP-001 | OBJ-001..OBJ-007 | Clarify objectives and enforcement | Not completed | None | None | None | MISSING |
| IMP-003 | BRD-INTEL-001..005 | Stage markers + sufficiency state + stop_reason | Claimed completed | `products/ade/schemas/intent_frame.py` (stage), `products/ade/schemas/plan_spec.py` (stage), `products/ade/agents/sufficiency_evaluator.py` (sufficiency_state), `products/ade/schemas/decision_packet.py` (stop_reason) | `products/ade/docs/04_systemdesign/schemas.md#2-core-schemas` | `products/ade/tests/unit/test_sufficiency_evaluator.py` | OVERCLAIM |
| IMP-004 | BRD-CRIT-001..005 | Critique output + blocking enforcement | Critique output added | `products/ade/agents/critic_evaluator.py` (blocking_required) | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-6-critic_evaluator` | `products/ade/tests/unit/test_critic_evaluator.py` | PARTIAL |
| IMP-005 | BRD-TOOLSEL-001..004 | Advisory tool recommendations | Completed | `products/ade/agents/plan_agent.py` (tool_recommendations), `products/ade/agents/plan_proposal_agent.py` (tool_recommendations) | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-2-plan_agent` | `products/ade/tests/unit/test_plan_agent_recommendations.py` | VERIFIED |
| IMP-006 | BRD-NARR-004 | Anomaly interpretation in narrative | Dashboard agent updated | `products/ade/agents/dashboard_agent.py` (anomaly_interpretation) | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-7-dashboard_agent` | `products/ade/tests/unit/test_dashboard_agent_anomalies.py` | PARTIAL |
| IMP-007 | BRD-CONF-005 | Configurable confidence thresholds | Intent uses config | `products/ade/config/confidence.py` (`load_confidence_thresholds`), `products/ade/agents/intent_agent.py` | `products/ade/docs/04_systemdesign/architecture.md#6-configuration` | `products/ade/tests/unit/test_confidence_thresholds.py` | PARTIAL |
| IMP-008 | BRD-PLAN-007..009 | Plan objective/evidence + replan diff | Completed | `products/ade/agents/plan_proposal_agent.py` (objective/evidence), `products/ade/agents/planning_agent.py` (replan_change_summary) | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-3-plan_proposal_agent` | `products/ade/tests/unit/test_plan_proposal_details.py` | VERIFIED |
| IMP-011 | BRD-CTX-001..004 | Context pack tool + wiring | Context pack added | `products/ade/tools/context_pack_builder.py` (ContextPack), `products/ade/flows/ade_v1.yaml` (context_pack step) | `products/ade/docs/04_systemdesign/schemas.md#6-context-pack-schema` | `products/ade/tests/unit/test_context_pack_builder.py` | PARTIAL |
| IMP-012 | BRD-VAL-001..003 | Validation gating pre-render | Render validation added | `products/ade/tools/render_decision_packet_html.py` (model_validate) | `products/ade/docs/04_systemdesign/agents-and-tools.md#3-5-rendering-tools` | `products/ade/tests/unit/test_render_validation.py` | VERIFIED |
| IMP-013 | BRD-QUAL-001..004, BRD-QUAL-010..012 | Output quality checks | Report quality checks added | `products/ade/tools/assemble_business_report.py` (`_validate_report_quality`) | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-2-output-quality-gates` | `products/ade/tests/unit/test_assemble_business_report_quality.py` | PARTIAL |
| IMP-014 | BRD-VER-001..003 | Version metadata + hashing + pinning | Version metadata added | `products/ade/utils/versioning.py` (`build_version_metadata`) | `products/ade/docs/04_systemdesign/schemas.md#7-version-metadata-schema` | `products/ade/tests/unit/test_version_metadata.py` | PARTIAL |
| IMP-015 | BRD-DAB-001..005 | Advisory labeling in outputs | Templates updated | `products/ade/tools/render_decision_packet_html.py` (advisory label), `products/ade/tools/render_business_report_html.py` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-1-primary-outputs` | `products/ade/tests/unit/test_decision_packet_advisory.py` | VERIFIED |
| IMP-016 | BRD-ALIGN-001..002, BRD-FRI-001..005, BRD-NRL-001..004 | Clarify framework alignment/reliance/no-learning | Not completed | None | None | None | MISSING |

## Gap Register
| Gap ID | Category | Severity | IMP Unit(s) | TS IDs | Description | Evidence | Recommended Fix |
|---|---|---|---|---|---|---|---|
| GAP-IMP-001 | Implementation Missing / Partial | High | IMP-001 | OBJ-001..OBJ-007 | Objectives clarification not performed. | `products/ade/docs/03_implementation_plan/imp_plan.md#imp-001` | Record clarification decision and link in plan/outcome. |
| GAP-IMP-003 | Outcome Overclaim | Medium | IMP-003 | BRD-INTEL-001..005 | Stage markers are not present on all agent outputs (plan_proposal/planning). | `products/ade/agents/plan_proposal_agent.py` | Add stage fields to remaining agent outputs or narrow outcome claim. |
| GAP-IMP-004 | Implementation Missing / Partial | High | IMP-004 | BRD-CRIT-005 | Critique blocking does not enforce ASK_USER/ABORT. | `products/ade/agents/critic_evaluator.py` | Add orchestration gate or downstream handling. |
| GAP-IMP-005 | Implementation Missing / Partial | Medium | IMP-006 | BRD-NARR-004 | Anomaly narrative exists but is not wired into flows. | `products/ade/agents/dashboard_agent.py` | Wire dashboard_agent into flows or surface narrative in outputs. |
| GAP-IMP-006 | Implementation Missing / Partial | Medium | IMP-007 | BRD-CONF-005 | Critique evaluation does not use config thresholds. | `products/ade/config/confidence.py` | Apply thresholds in critic_evaluator. |
| GAP-IMP-009 | Implementation Missing / Partial | Medium | IMP-011 | BRD-CTX-004 | Reasoning outputs do not reference context pack artifacts. | `products/ade/agents/plan_proposal_agent.py` | Add explicit context pack references in outputs. |
| GAP-IMP-010 | Implementation Missing / Partial | Medium | IMP-013 | BRD-QUAL-010..012 | Quality checks do not validate Vega-Lite specs or browser compatibility. | `products/ade/tools/assemble_business_report.py` | Add spec validation and rendering checks. |
| GAP-IMP-011 | Implementation Missing / Partial | Medium | IMP-014 | BRD-VER-003 | Dependency pinning not enforced; only recorded. | `products/ade/utils/versioning.py` | Add dependency pinning or explicit rejection logic. |
| GAP-IMP-012 | Implementation Missing / Partial | Medium | IMP-015 | BRD-DAB-003..005 | Advisory language present but no enforcement of downstream action prevention. | `products/ade/tools/render_decision_packet_html.py` | Add explicit advisory flags in outputs or orchestration checks. |
| GAP-IMP-013 | Test Gap | Low | IMP-012 | BRD-VAL-001..003 | Render business report validation gating lacks unit test. | `products/ade/tools/render_business_report_html.py` | Add unit test for validation error path. |
| GAP-IMP-014 | Test Gap | Low | IMP-014 | BRD-VER-001..003 | Business report version metadata not asserted in tests. | `products/ade/tools/assemble_business_report.py` | Add unit test for report version_metadata. |
| GAP-IMP-015 | Implementation Missing / Partial | Medium | IMP-016 | BRD-ALIGN-001..002, BRD-FRI-001..005, BRD-NRL-001..004 | Alignment/reliance/no-learning clarifications not recorded. | `products/ade/docs/03_implementation_plan/imp_plan.md#imp-016` | Record clarification decisions and link in plan/outcome. |

## Recommended Next Actions
- Address GAP-IMP-003 by adding stage fields to remaining agent outputs or narrowing the outcome claim.
- Wire anomaly narrative into runtime outputs to resolve GAP-IMP-005.
- Apply confidence thresholds in critique evaluation to resolve GAP-IMP-006.
- Add context pack references to reasoning outputs for GAP-IMP-009.
- Implement Vega-Lite validation and browser checks for GAP-IMP-010.
- Add dependency pinning enforcement for GAP-IMP-011.
- Add explicit advisory prevention flags for GAP-IMP-012.
- Add tests for render validation and version metadata (GAP-IMP-013, GAP-IMP-014).
