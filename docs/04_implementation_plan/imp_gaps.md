# Master Implementation Gaps (Plan vs Outcome vs Code vs System Design)

> **Generated:** 2026-01-26  
> **Tech Spec Version:** V1.4  
> **Authoritative Order:** imp_outcome.md → codebase → system design → imp_plan.md

---

## Summary

| Metric | Value |
|--------|-------|
| Plan units total | 25 |
| Units verified complete | 23 |
| Units partial | 0 |
| Units missing | 2 (IMP-054, IMP-055) |
| Outcome overclaims | 0 |
| Doc drift items fixed | 26 (GAP-031 to GAP-056 now closed in SD-COVERAGE.md) |
| Test gaps | 0 |
| Last updated | 2026-01-26 |

---

## Verification Status

All 23 claimed IMP units have been verified against:
1. ✅ **imp_outcome.md** — Claims match
2. ✅ **Codebase** — Files exist with correct implementations
3. ✅ **System Design** — SD-COVERAGE.md and SD-COMP-LIST.md updated
4. ✅ **imp_plan.md** — Plan specifications matched

---

## Reconciliation Table

| IMP Unit | Tech Spec IDs | Plan | Outcome | Code Evidence | SD Evidence | Test Evidence | Status |
|----------|---------------|------|---------|---------------|-------------|---------------|--------|
| IMP-031 | ORC-SEM-ENV-001...005 | Semantic envelope enforcement | ✅ 20/20 tests | `core/contracts/semantic_schema.py`, `core/orchestrator/plan_executor.py` | SD-COVERAGE GAP-031 ✅ | `tests/unit/core/contracts/test_semantic_envelope_enforcement.py` | ✅ VERIFIED |
| IMP-032 | ORC-SEM-CONF-GATE-001...008 | Confidence gate at semantic phase exit | ✅ 24/24 tests | `core/governance/hooks.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-032 ✅ | `tests/unit/core/orchestrator/test_confidence_gate.py` | ✅ VERIFIED |
| IMP-033 | ORC-SEM-AMB-001...006 | Ambiguity detection schema | ✅ 11/11 tests | `core/contracts/semantic_schema.py` | SD-COVERAGE GAP-033 ✅ | `tests/unit/core/contracts/test_ambiguity_schema.py` | ✅ VERIFIED |
| IMP-034 | GOV-REAS-001...006, GOV-REAS-WAIVERS-001...004 | Minimum reasoning contract | ✅ 44/44 tests | `core/contracts/reasoning_schema.py`, `core/contracts/flow_schema.py`, `core/orchestrator/reasoning_lifecycle.py` | SD-COVERAGE GAP-034 ✅ | `tests/unit/core/orchestrator/test_reasoning_contract.py` | ✅ VERIFIED |
| IMP-035 | ORC-SUFF-GATE-001...008 | Intent sufficiency gate | ✅ 27/27 tests | `core/governance/gates.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-035 ✅ | `tests/unit/core/governance/test_sufficiency_gate.py` | ✅ VERIFIED |
| IMP-036 | INT-DISC-001...010, INT-DISC-019...028, INT-DISC-038...045 | Tool & agent discovery engine | ✅ 17/17 tests | `core/knowledge/discovery_engine.py` | SD-COVERAGE GAP-036 ✅, SD-COMP-LIST ✅ | `tests/unit/core/knowledge/test_discovery_engine.py` | ✅ VERIFIED |
| IMP-037 | INT-DISC-011...018, INT-DISC-046...054 | Discovery registry integration | ✅ 11/11 tests | `core/agents/registry.py`, `core/tools/registry.py`, `core/knowledge/discovery_engine.py` | SD-COVERAGE GAP-036 ✅ | `tests/unit/core/agents/test_registry_discovery.py` | ✅ VERIFIED |
| IMP-038 | INT-DISC-029...037 | Discovery eligibility checks | ✅ 16/16 tests | `core/governance/budgeting.py`, `core/knowledge/discovery_engine.py` | SD-COVERAGE GAP-036 ✅ | `tests/unit/core/knowledge/test_eligibility_checker.py` | ✅ VERIFIED |
| IMP-039 | GOV-DISC-001...005, GOV-DISC-SEL-001...005 | Discovery/selection phase separation | ✅ 39/39 tests | `core/knowledge/discovery_engine.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-036 ✅ | `tests/unit/core/knowledge/test_discovery_selection.py` | ✅ VERIFIED |
| IMP-040 | AGT-DISC-TOOL-001...012 | Tool descriptor contract | ✅ 7/7 tests | `core/contracts/descriptors_schema.py` | SD-COVERAGE GAP-037 ✅, SD-COMP-LIST ✅ | `tests/unit/core/contracts/test_tool_descriptor.py` | ✅ VERIFIED |
| IMP-041 | AGT-DISC-AGT-001...012 | Agent descriptor contract | ✅ 10/10 tests | `core/contracts/descriptors_schema.py` | SD-COVERAGE GAP-038 ✅, SD-COMP-LIST ✅ | `tests/unit/core/contracts/test_agent_descriptor.py` | ✅ VERIFIED |
| IMP-042 | AGT-DISC-VAL-001...006, AGT-DISC-SCHEMA-001...005 | Descriptor validation in registry | ✅ 21/21 tests | `core/agents/registry.py`, `core/tools/registry.py` | SD-COVERAGE GAP-039, GAP-040 ✅ | `tests/unit/core/agents/test_registry_validation.py` | ✅ VERIFIED |
| IMP-043 | GOV-HITL-BIND-001...007, GOV-HITL-DECL-001...005 | HITL binding requirements | ✅ 36/36 tests | `core/governance/hitl_binding.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-041, GAP-042 ✅, SD-COMP-LIST ✅ | `tests/unit/core/governance/test_hitl_binding.py` | ✅ VERIFIED |
| IMP-044 | GOV-SEC-PII-001...005 | Enhanced PII detection | ✅ 32/32 tests | `core/governance/pii_detector.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-043 ✅, SD-COMP-LIST ✅ | `tests/unit/core/governance/test_pii_detector.py` | ✅ VERIFIED |
| IMP-045 | GOV-SEC-CRED-001...005 | Cloud credential patterns | ✅ 30/30 tests | `core/governance/security.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-044 ✅ | `tests/unit/core/governance/test_credential_redaction.py` | ✅ VERIFIED |
| IMP-046 | GOV-SEC-AUTO-001...005 | Automatic redaction on all outputs | ✅ 47/47 tests | `core/governance/security.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-045 ✅ | `tests/unit/core/governance/test_auto_redaction.py` | ✅ VERIFIED |
| IMP-047 | GOV-POL-NOBYPASS-001...005, GOV-POL-BLOCK-001...005 | Policy bypass prevention & blocking | ✅ 33/33 tests | `core/governance/policies.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-046, GAP-047 ✅ | `tests/unit/core/governance/test_policy_nobypass.py` | ✅ VERIFIED |
| IMP-048 | GOV-BUD-HARD-001...005 | Hard budget limits | ✅ 31/31 tests | `core/governance/budgeting.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-048 ✅ | `tests/unit/core/governance/test_hard_budget.py` | ✅ VERIFIED |
| IMP-049 | GOV-GATE-SEM-001...012, GOV-GATE-SUFF-001...006 | Semantic gate implementation | ✅ 33/33 tests | `core/governance/semantic_gate.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-049, GAP-050 ✅, SD-COMP-LIST ✅ | `tests/unit/core/governance/test_semantic_gate.py` | ✅ VERIFIED |
| IMP-050 | GOV-GATE-REJ-001...010 | Gate rejection artifacts | ✅ 38/38 tests | `core/contracts/gate_schema.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-051 ✅, SD-COMP-LIST ✅ | `tests/unit/core/governance/test_gate_rejection.py` | ✅ VERIFIED |
| IMP-051 | GOV-EVID-001...005, GOV-EVID-CONF-001...005, GOV-EVID-TRACE-001...005 | Evidence requirements | ✅ 40/40 tests | `core/governance/evidence_requirements.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-052, GAP-053, GAP-054 ✅, SD-COMP-LIST ✅ | `tests/unit/core/governance/test_evidence_requirements.py` | ✅ VERIFIED |
| IMP-052 | GOV-DEC-RECORD-001...010 | Decision record artifacts | ✅ 47/47 tests | `core/contracts/decision_schema.py`, `core/memory/tracing.py` | SD-COVERAGE GAP-055 ✅, SD-COMP-LIST ✅ | `tests/unit/core/contracts/test_decision_record.py` | ✅ VERIFIED |
| IMP-053 | GOV-SEM-CONF-008...018 | Multi-source confidence aggregation | ✅ 36/36 tests | `core/knowledge/confidence.py` | SD-COVERAGE GAP-056 ✅ | `tests/unit/core/knowledge/test_confidence_aggregation.py` | ✅ VERIFIED |
| IMP-054 | ACC-INV-EXEC-001...015 | Executable invariant tests | ❌ Not started | — | SD-COVERAGE GAP-057 ❌ | — | ❌ MISSING |
| IMP-055 | ACC-CI-INV-001...007 | Invariant CI/CD gate | ❌ Not started | — | SD-COVERAGE GAP-058 ❌ | — | ❌ MISSING |

---

## Gap Detail — Remaining Work

### GAP-057: Executable Invariant Tests (IMP-054)

| Field | Value |
|-------|-------|
| Tech Spec IDs | ACC-INV-EXEC-001...015 |
| Gap Type | Tests only |
| Description | Executable tests that verify all 5 architectural invariants at runtime |
| Severity | Medium |
| What is needed | Add `tests/architecture/test_invariant_enforcement.py` with 15 invariant tests |
| Dependencies | None — all invariants are already enforced in code |
| Estimated effort | 4 hours |

### GAP-058: Invariant CI/CD Gate (IMP-055)

| Field | Value |
|-------|-------|
| Tech Spec IDs | ACC-CI-INV-001...007 |
| Gap Type | CI configuration only |
| Description | CI pipeline stage that runs invariant tests and blocks merge on failure |
| Severity | Low |
| What is needed | Add CI job `invariant-gate` to `.github/workflows/ci.yaml` |
| Dependencies | GAP-057 must be complete first |
| Estimated effort | 1 hour |

---

## Documentation Drift — Corrected

The following documentation was out of sync and has been updated:

| Document | Issue | Fix Applied |
|----------|-------|-------------|
| SD-COVERAGE.md | Gap Register showed GAP-031 to GAP-058 as "❌ Not Started" | Updated to show GAP-031 to GAP-056 as "✅ CLOSED", only GAP-057/058 remain |
| SD-COVERAGE.md | Coverage Summary showed 52-82% coverage | Updated to 100% for ORC, AGT, GOV, INT |
| SD-COVERAGE.md | Version was 1.4 with "Gaps Identified" status | Updated to 1.5 with "Implementation Complete" status |
| SD-COMP-LIST.md | Missing V1.4 governance components | Added: semantic_gate.py, hitl_binding.py, pii_detector.py, evidence_requirements.py |
| SD-COMP-LIST.md | Missing V1.4 contract schemas | Added: descriptors_schema.py, gate_schema.py, decision_schema.py |
| SD-COMP-LIST.md | Missing V1.4 knowledge components | Added: discovery_engine.py |

---

## New Files Added in V1.4 Implementation

### Governance (core/governance/)

| File | IMP Unit | Lines | Purpose |
|------|----------|-------|---------|
| `semantic_gate.py` | IMP-049 | 389 | SemanticGate, SemanticGateResult for envelope validation |
| `hitl_binding.py` | IMP-043 | 697 | HITLBinding, EscalationPath, HITLBindingRegistry |
| `pii_detector.py` | IMP-044 | 598 | PIIDetector, PIIEntity, PIIMatch for NER-based PII detection |
| `evidence_requirements.py` | IMP-051 | 548 | EvidenceValidator, EvidenceRequirement for evidence validation |

### Contracts (core/contracts/)

| File | IMP Unit | Lines | Purpose |
|------|----------|-------|---------|
| `descriptors_schema.py` | IMP-040, IMP-041 | 165 | ToolDescriptor, AgentDescriptor for registry catalogs |
| `gate_schema.py` | IMP-050 | 455 | GateRejectionArtifact, GateRejectionStore for rejection tracing |
| `decision_schema.py` | IMP-052 | 523 | DecisionRecord, DecisionChain, DecisionRecorder |

### Knowledge (core/knowledge/)

| File | IMP Unit | Lines | Purpose |
|------|----------|-------|---------|
| `discovery_engine.py` | IMP-036, IMP-037, IMP-038, IMP-039 | 967 | DiscoveryEngine, ToolCandidate, AgentCandidate, EligibilityChecker |

---

## Recommended Next Actions

1. **IMP-054 (ACC-INV-EXEC)**: Create executable invariant tests
   - File: `tests/architecture/test_invariant_enforcement.py`
   - Tests: 15 tests covering INV-1 through INV-5 enforcement
   - Priority: Medium

2. **IMP-055 (ACC-CI-INV)**: Add CI invariant gate
   - File: `.github/workflows/ci.yaml`
   - Job: `invariant-gate` running after unit tests
   - Priority: Low (depends on IMP-054)

3. **SD-GOV.md Update**: Add architecture diagrams for new governance components
   - SemanticGate integration diagram
   - HITL binding flow diagram
   - PII detector pipeline diagram
   - Priority: Low (documentation)

4. **SD-INT.md Update**: Add discovery engine architecture
   - Discovery/selection phase separation diagram
   - Eligibility checker flow
   - Priority: Low (documentation)

---

## Verification Evidence

### Test Summary (from imp_outcome.md)

| Phase | Tests | Status |
|-------|-------|--------|
| Phase 1: Schema & Contract | 49 | ✅ PASS |
| Phase 2: Core Infrastructure | 58 | ✅ PASS |
| Phase 3: Gate Implementations | 122 | ✅ PASS |
| Phase 4: Governance & Security | 209 | ✅ PASS |
| Phase 5: Reasoning & Evidence | 206 | ✅ PASS |
| **Total** | **644** | ✅ **ALL PASS** |

### File Existence Verification

All new V1.4 files verified to exist in codebase:
- ✅ `core/governance/semantic_gate.py` (389 lines)
- ✅ `core/governance/hitl_binding.py` (697 lines)
- ✅ `core/governance/pii_detector.py` (598 lines)
- ✅ `core/governance/evidence_requirements.py` (548 lines)
- ✅ `core/contracts/descriptors_schema.py` (165 lines)
- ✅ `core/contracts/gate_schema.py` (455 lines)
- ✅ `core/contracts/decision_schema.py` (523 lines)
- ✅ `core/knowledge/discovery_engine.py` (967 lines)

---

## See Also

- [imp_outcome.md](imp_outcome.md) — Implementation outcomes (authoritative)
- [imp_plan.md](imp_plan.md) — Original implementation plan
- [../05_systemdesign/SD-COVERAGE.md](../05_systemdesign/SD-COVERAGE.md) — Updated coverage matrix
- [../05_systemdesign/components/SD-COMP-LIST.md](../05_systemdesign/components/SD-COMP-LIST.md) — Updated component list