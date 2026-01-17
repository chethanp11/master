# ADE Implementation Plan (v1.1)

## Overview

**Purpose**: Implement Tech Spec requirements that are missing or only partially represented in System Design, without modifying System Design documents.

**Assumptions**:
- ADE product code exists under `products/ade/` with agents, tools, schemas, and flows as referenced by Tech Specs.
- Core framework primitives (orchestrator, governance, memory) are available and stable.
- Tech Specs under `products/ade/docs/02_techspec/` are the source of truth.

**Entry Criteria**:
- `products/ade/docs/02_techspec/TS-COVERAGE.md` shows full BRD→TS coverage.
- `products/ade/docs/04_systemdesign/SD-COVERAGE.md` is current and lists gaps.
- ADE flows YAML are present and loadable.

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

## Dependency Order

1. IMP-001 (objectives clarification)
2. IMP-003 (reasoning ladder)
3. IMP-004 (critique)
4. IMP-005 (advisory tool selection)
5. IMP-006 (anomaly narrative)
6. IMP-007 (confidence thresholds)
7. IMP-008 (plan detail + replan diff)
8. IMP-011 (context pack)
9. IMP-012 (validation gating)
10. IMP-013 (output quality)
11. IMP-014 (version transparency)
12. IMP-015 (decision authority boundary)
13. IMP-016 (alignment/reliance/no runtime learning clarifications)

---

## Non-Goals

- Editing any System Design documents under `products/ade/docs/04_systemdesign/`.
- Implementing features not defined in Tech Specs.
- Changing BRD requirements or IDs.

---

## Final Verification Checklist

- [ ] Every Tech Spec ID in SD-COVERAGE gap register is mapped to an IMP unit.
- [ ] IMP units reference exact Tech Spec IDs and SD gap IDs.
- [ ] No remaining SD-COVERAGE gaps impacting runtime without a plan.
