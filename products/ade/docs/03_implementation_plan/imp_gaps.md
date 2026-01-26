# ADE Implementation Gaps

> **Document**: Implementation Gaps Reconciliation  
> **Version**: 1.0  
> **Last Updated**: 2026-01-22  
> **Status**: Code-to-Documentation Reconciliation Complete

---

## 1. Summary

This document provides a precise gap analysis across plan, outcome, code, and system design for all 25 IMP units defined in `imp_plan.md`.

| Metric | Value |
|--------|-------|
| Total IMP Units Analyzed | 25 |
| Gaps Found | 3 (Doc Drift) |
| Outcome Overclaims | 0 |
| Test Gaps | 0 |
| Speculative SD | 0 |
| Implementation Missing/Partial | 0 |

---

## 2. Gap Classifications

| Classification | Definition |
|----------------|------------|
| **Outcome Overclaim** | imp_outcome.md claims verification that cannot be confirmed by code or tests |
| **Doc Drift** | Documentation references files, symbols, or paths that don't exist in code |
| **Test Gap** | Tests exist but do not actually verify the claimed IMP unit requirements |
| **Speculative SD** | System Design describes components that don't exist in code |
| **Implementation Missing** | Code expected by TSD ID does not exist |
| **Implementation Partial** | Code exists but is incomplete relative to TSD ID requirements |

---

## 3. Gaps Identified

### GAP-IMP-010: Doc Drift — Non-existent File References

| Attribute | Value |
|-----------|-------|
| **Gap ID** | GAP-IMP-010 |
| **IMP Unit** | IMP-010 (Data Tools) |
| **Classification** | Doc Drift |
| **Severity** | Low (documentation only) |
| **Description** | imp_outcome.md references files that do not exist |

**Claimed Code Locations** (from imp_outcome.md):
- `products/ade/tools/data_reader.py` ✅ EXISTS
- `products/ade/tools/compute_aggregate.py` ❌ NOT FOUND
- `products/ade/tools/compute_period_comparison.py` ❌ NOT FOUND

**Resolution**: These files never existed. The documentation should reference:
- `products/ade/tools/compute_business_metrics.py` (provides aggregation functionality)

---

### GAP-IMP-011: Doc Drift — Non-existent File References

| Attribute | Value |
|-----------|-------|
| **Gap ID** | GAP-IMP-011 |
| **IMP Unit** | IMP-011 (Analysis Tools) |
| **Classification** | Doc Drift |
| **Severity** | Low (documentation only) |
| **Description** | imp_outcome.md references files that do not exist |

**Claimed Code Locations** (from imp_outcome.md):
- `products/ade/tools/detect_anomalies.py` ✅ EXISTS
- `products/ade/tools/compute_driver_decomposition.py` ❌ NOT FOUND
- `products/ade/tools/check_hypothesis.py` ❌ NOT FOUND

**Actual Files**:
- `products/ade/tools/driver_analysis.py` ✅ EXISTS (correct name)
- `products/ade/tools/hypothesis_test_data_outage.py` ✅ EXISTS
- `products/ade/tools/hypothesis_test_seasonality.py` ✅ EXISTS

**Resolution**: File names were incorrectly documented. The actual tools exist with different names.

---

### GAP-IMP-025: Doc Drift — Non-existent File Reference

| Attribute | Value |
|-----------|-------|
| **Gap ID** | GAP-IMP-025 |
| **IMP Unit** | IMP-025 (Context Pack and Evidence Schemas) |
| **Classification** | Doc Drift |
| **Severity** | Low (documentation only) |
| **Description** | imp_outcome.md references file that does not exist |

**Claimed Code Locations** (from imp_outcome.md):
- `products/ade/schemas/evidence.py` ✅ EXISTS
- `products/ade/tools/build_context_pack.py` ❌ NOT FOUND

**Actual File**:
- `products/ade/tools/context_pack_builder.py` ✅ EXISTS (correct name)

**Resolution**: File name was incorrectly documented.

---

## 4. Full Reconciliation Table

| IMP ID | TSD IDs | Status | Classification | Notes |
|--------|---------|--------|----------------|-------|
| IMP-001 | TS-IO-OBJ-001..008 | ✅ Verified | — | Clarification records in intent_frame.py, evidence schema tests |
| IMP-002 | TS-AGENT-REASON-001..002 | ✅ Verified | — | Multi-stage reasoning in planning_agent.py |
| IMP-003 | TS-AGENT-REASON-003 | ✅ Verified | — | Bounded cycles enforced by platform |
| IMP-004 | TS-AGENT-CRIT-005 | ✅ Verified | — | Blocking critique in critic_evaluator.py |
| IMP-005 | TS-AGENT-CRIT-001..004 | ✅ Verified | — | Critique integration in ade_v1.yaml |
| IMP-006 | TS-TOOL-NARR-001 | ✅ Verified | — | Anomaly interpretation in dashboard_agent.py |
| IMP-007 | TS-AGENT-DASH-001..002 | ✅ Verified | — | Dashboard agent outputs verified |
| IMP-008 | TS-FLOW-V1-001..005 | ✅ Verified | — | ade_v1 flow steps in YAML |
| IMP-009 | TS-FLOW-VIZ-001..004 | ✅ Verified | — | Chart type guardrails verified |
| IMP-010 | TS-TOOL-DATA-001..005 | ⚠️ Doc Drift | GAP-IMP-010 | Incorrect file names in imp_outcome.md |
| IMP-011 | TS-TOOL-ANALYSIS-001..007 | ⚠️ Doc Drift | GAP-IMP-011 | Incorrect file names in imp_outcome.md |
| IMP-012 | TS-TOOL-VIZ-001..004 | ✅ Verified | — | Visualization tools verified |
| IMP-013 | TS-IO-QUAL-001..008 | ✅ Verified | — | Quality validation in validation.py |
| IMP-014 | TS-IO-VER-001..003 | ✅ Verified | — | Version metadata in version_metadata.py |
| IMP-015 | TS-IO-DAB-001..005 | ✅ Verified | — | Advisory boundary in advisory.py |
| IMP-016 | TS-AGENT-FRI + NRL | ✅ Verified | — | Framework alignment documented |
| IMP-017 | TS-AGENT-TERM-001..003 | ✅ Verified | — | Terminal outcomes in terminal_outcome.py |
| IMP-018 | TS-AGENT-NARR-005 | ✅ Verified | — | Narrative builder in narrative.py |
| IMP-019 | TS-AGENT-CONF-003 | ✅ Verified | — | Confidence config in confidence.py |
| IMP-020 | TS-SEM-VALIDATE-008..009 | ✅ Verified | — | Semantic validation in semantic_validation.py |
| IMP-021 | TS-TOOL-GEN-007 | ✅ Verified | — | Tool dependency checks verified |
| IMP-022 | TS-TOOL-ANALYSIS-008 | ✅ Verified | — | Anomaly severity scoring verified |
| IMP-023 | TS-IO-OUT-007 | ✅ Verified | — | Output directory utilities in output.py |
| IMP-024 | TS-FLOW-V1-006..009 | ✅ Verified | — | Plan detail metadata in plan_proposal_agent.py |
| IMP-025 | TS-SCHEMA-CTX + EVITEM | ⚠️ Doc Drift | GAP-IMP-025 | Incorrect file name in imp_outcome.md |

---

## 5. Code-to-System-Design Verification

### 5.1 Agents (7 in code, 7 in SD)

| Agent | In Code | In System Design | Match |
|-------|---------|------------------|-------|
| intent_agent | `agents/intent_agent.py` | agents-and-tools.md#2.1 | ✅ |
| plan_agent | `agents/plan_agent.py` | agents-and-tools.md#2.2 | ✅ |
| plan_proposal_agent | `agents/plan_proposal_agent.py` | agents-and-tools.md#2.3 | ✅ |
| planning_agent | `agents/planning_agent.py` | agents-and-tools.md#2.4 | ✅ |
| sufficiency_evaluator | `agents/sufficiency_evaluator.py` | agents-and-tools.md#2.5 | ✅ |
| critic_evaluator | `agents/critic_evaluator.py` | agents-and-tools.md#2.6 | ✅ |
| dashboard_agent | `agents/dashboard_agent.py` | agents-and-tools.md#2.7 | ✅ |

### 5.2 Tools (17 registered, 17 in SD)

| Tool | In Code | In System Design | Match |
|------|---------|------------------|-------|
| data_reader | `tools/data_reader.py` | agents-and-tools.md#3.1 | ✅ |
| context_pack_builder | `tools/context_pack_builder.py` | agents-and-tools.md#3.1 | ✅ |
| compute_business_metrics | `tools/compute_business_metrics.py` | agents-and-tools.md#3.1 | ✅ |
| detect_anomalies | `tools/detect_anomalies.py` | agents-and-tools.md#3.2 | ✅ |
| driver_analysis | `tools/driver_analysis.py` | agents-and-tools.md#3.2 | ✅ |
| hypothesis_test_data_outage | `tools/hypothesis_test_data_outage.py` | agents-and-tools.md#3.2 | ✅ |
| hypothesis_test_seasonality | `tools/hypothesis_test_seasonality.py` | agents-and-tools.md#3.2 | ✅ |
| build_chart_spec | `tools/build_chart_spec.py` | agents-and-tools.md#3.3 | ✅ |
| recommend_chart | `tools/recommend_chart.py` | agents-and-tools.md#3.3 | ✅ |
| assemble_decision_packet | `tools/assemble_decision_packet.py` | agents-and-tools.md#3.4 | ✅ |
| assemble_business_report | `tools/assemble_business_report.py` | agents-and-tools.md#3.4 | ✅ |
| assemble_evidence_bundle | `tools/assemble_evidence_bundle.py` | agents-and-tools.md#3.4 | ✅ |
| assemble_insight_card | `tools/assemble_insight_card.py` | agents-and-tools.md#3.4 | ✅ |
| render_business_report_html | `tools/render_business_report_html.py` | agents-and-tools.md#3.5 | ✅ |
| render_decision_packet_html | `tools/render_decision_packet_html.py` | agents-and-tools.md#3.5 | ✅ |
| export_pdf | `tools/export_pdf.py` | agents-and-tools.md#3.5 | ✅ |
| build_reasoning_narrative | `tools/build_reasoning_narrative.py` | agents-and-tools.md#3.6 | ✅ |

### 5.3 Tool Utilities (Non-registered, 2 in code, 2 in SD)

| Utility | In Code | In System Design | Match |
|---------|---------|------------------|-------|
| export_rendering | `tools/export_rendering.py` | agents-and-tools.md#5 | ✅ |
| evidence_utils | `tools/evidence_utils.py` | agents-and-tools.md#5 | ✅ |

### 5.4 Schemas (12 files, all documented in SD)

| Schema | In Code | In System Design | Match |
|--------|---------|------------------|-------|
| decision_packet | `schemas/decision_packet.py` | schemas.md#2.1 | ✅ |
| decision_section | `schemas/decision_section.py` | schemas.md#2.2 | ✅ |
| business_report | `schemas/business_report.py` | schemas.md#2.3 | ✅ |
| intent_frame | `schemas/intent_frame.py` | schemas.md#2.8 | ✅ |
| plan_spec | `schemas/plan_spec.py` | schemas.md#2.9 | ✅ |
| evidence | `schemas/evidence.py` | schemas.md#3.1 | ✅ |
| context_pack | `schemas/context_pack.py` | schemas.md#6 | ✅ |
| version_metadata | `schemas/version_metadata.py` | schemas.md#7 | ✅ |
| terminal_outcome | `schemas/terminal_outcome.py` | schemas.md#9 | ✅ |
| card | `schemas/card.py` | schemas.md#4.1 | ✅ |
| citations | `schemas/citations.py` | schemas.md#3.2 | ✅ |
| slices | `schemas/slices.py` | schemas.md#4.2 | ✅ |

### 5.5 Utility Modules (7 in code, 7 in SD)

| Utility | In Code | In System Design | Match |
|---------|---------|------------------|-------|
| narrative | `utils/narrative.py` | agents-and-tools.md#6.1 | ✅ |
| advisory | `utils/advisory.py` | agents-and-tools.md#6.2 | ✅ |
| semantic_validation | `utils/semantic_validation.py` | agents-and-tools.md#6.3 | ✅ |
| validation | `utils/validation.py` | agents-and-tools.md#6.4 | ✅ |
| output | `utils/output.py` | agents-and-tools.md#6.5 | ✅ |
| confidence | `utils/confidence.py` | schemas.md#10 | ✅ |
| versioning | `utils/versioning.py` | schemas.md#7 | ✅ |

### 5.6 Flows (2 in code, 2 in SD)

| Flow | In Code | In System Design | Match |
|------|---------|------------------|-------|
| ade_v1 | `flows/ade_v1.yaml` | flows.md#2 | ✅ |
| visualization | `flows/visualization.yaml` | flows.md#3 | ✅ |

---

## 6. SD-COVERAGE Updates Applied

During this reconciliation, the following items in SD-COVERAGE.md were updated:

| Tech Spec ID | Old Status | New Status | Reason |
|--------------|------------|------------|--------|
| BRD-INTEL-003 | Missing | Covered | Gap Register GAP-003 closed; architecture.md §10 documents bounded cycles |
| BRD-VER-003 | Partial | Covered | Gap Register GAP-015 closed; version_metadata implemented |
| BRD-DAB-003 | Partial | Covered | Gap Register GAP-016 closed; advisory.py implemented |
| BRD-DAB-004 | Partial | Covered | Gap Register GAP-016 closed; advisory.py implemented |
| BRD-DAB-005 | Partial | Covered | Gap Register GAP-016 closed; advisory.py implemented |

**SD-COVERAGE Version**: Updated from V1.4 to V1.5

---

## 7. Known Blockers (Out of Scope)

### 7.1 Platform Bug

**Location**: `core/memory/sqlite_backend.py` (line 257)

**Issue**: `_loads()` function called with 1 argument but requires 2

**Impact**: 7 integration tests blocked

**Status**: Out of ADE scope per project constraints (changes must be in `products/ade/` only)

---

## 8. Conclusion

The ADE implementation is complete. All 25 IMP units are verified through code inspection and test coverage. The only gaps found are documentation drift issues in `imp_outcome.md` where incorrect file names were referenced. These gaps do not affect the actual implementation quality.

### Final Counts

| Metric | Count |
|--------|-------|
| IMP Units Verified Complete | 25/25 |
| Unit Tests Passing | 87/87 |
| Integration Tests Blocked | 7 (platform bug) |
| Documentation Drift Gaps | 3 |
| System Design Gaps | 0 |
| Implementation Gaps | 0 |

---

## IMP-GAPS GAP COUNT: 3 (Doc Drift only)

---

## Cross-References

- **Implementation Plan**: imp_plan.md (V2.0)
- **Implementation Outcome**: imp_outcome.md (V1.0)
- **System Design Coverage**: SD-COVERAGE.md (V1.5)
- **Tech Spec Coverage**: TS-COVERAGE.md (V1.6)

