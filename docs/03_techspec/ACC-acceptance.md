# Acceptance Criteria Technical Specification

> **Document ID**: ACC  
> **Version**: V1.3  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-25  

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial V1 specification |
| 1.1.0 | 2026-01-13 | Added: §2.6 Semantic Phase Coverage, §2.7 Architecture Invariant Tests, §12.1 Explicit Non-Goals, §16 BRD Requirement Mapping |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |
| V1.3 | 2026-01-25 | Added: §2.8 Executable Invariant Enforcement (BRD-INV-027-030), §7.3 Invariant CI/CD Gate |

---

## 1. Overview

This specification defines acceptance criteria for the master agentic platform. All 
requirements in other techspec documents are considered accepted when corresponding 
tests pass at the specified coverage levels.

## 2. Test Categories

### 2.1 Unit Tests

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-UNIT-001 | Unit tests MUST test individual functions/methods in isolation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-UNIT-002 | Unit tests MUST mock all external dependencies | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-UNIT-003 | Unit tests MUST be located in `tests/unit/` directory | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-UNIT-004 | Unit test files MUST follow pattern `test_<module>.py` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-UNIT-005 | Unit test functions MUST follow pattern `test_<behavior>` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-UNIT-006 | Unit tests MUST complete within 1 second per test | SHOULD | BRD-OPS-033 | 1.1 | 13 Jan 2026 | — |


### 2.2 Integration Tests

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-INT-001 | Integration tests MUST test component interactions | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INT-002 | Integration tests MAY use real dependencies (DB, filesystem) | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INT-003 | Integration tests MUST be located in `tests/integration/` directory | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INT-004 | Integration tests MUST clean up resources after execution | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INT-005 | Integration tests SHOULD use test fixtures for setup/teardown | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 2.3 Architecture Tests

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-ARCH-001 | Architecture tests MUST verify layer boundaries | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-ARCH-002 | Architecture tests MUST verify import restrictions | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-ARCH-003 | Architecture tests MUST verify contract compliance | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-ARCH-004 | Architecture tests MUST be located in `tests/architecture/` directory | MUST | BRD-OPS-ARCH-006 | 1.1 | 13 Jan 2026 | — |


### 2.5 Semantic Interpretation Tests

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-SEM-001 | `test_semantic_phase_is_mandatory` MUST verify pipeline always calls semantic phase before step execution | MUST | BRD-OPS-ARCH-001 | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-002 | `test_stop_blocks_execution` MUST verify `ASK_USER`/`ABORT` prevents planning/tool execution | MUST | BRD-OPS-ARCH-002, BRD-OPS-ARCH-003 | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-003 | `test_product_adapter_isolated` MUST verify: products supply interpret/validate; core never imports product domain code; products never import core execution internals | MUST | BRD-OPS-ARCH-004, BRD-OPS-ARCH-005 | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-004 | Semantic tests MUST be located in `tests/architecture/test_semantic_isolation.py` | MUST | BRD-OPS-ARCH-006 | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-005 | Semantic tests MUST use mock products to verify adapter interface contract | MUST | BRD-OPS-ARCH-007 | 1.1 | 13 Jan 2026 | — |

### 2.4 Acceptance/Intelligence Tests

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-AI-001 | Acceptance tests MUST verify end-to-end behavior | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-AI-002 | Acceptance tests MUST cover critical user journeys | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-AI-003 | Acceptance tests MUST be located in `tests/acceptance_intelligence/` directory | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-AI-004 | Acceptance tests SHOULD use real product flows | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 2.6 Semantic Phase Coverage Tests (Added: 2026-01-13)

> **Source**: BRD-OPS-ARCH-001...007, INV-1, INV-3

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-SEM-COV-001 | `test_semantic_envelope_all_fields` MUST verify all SemanticEnvelope fields are populated | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-COV-002 | `test_confidence_threshold_enforced` MUST verify low confidence blocks execution | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-COV-003 | `test_ask_user_produces_clarification` MUST verify ClarificationRequest is generated | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-COV-004 | `test_abort_produces_artifact` MUST verify AbortArtifact is generated | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-COV-005 | `test_semantic_events_emitted` MUST verify all required trace events are emitted | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-COV-006 | `test_entity_extraction_coverage` MUST verify entities are extracted correctly | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEM-COV-007 | `test_ambiguity_detection_coverage` MUST verify ambiguities are detected | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

### 2.7 Architecture Invariant Tests (Added: 2026-01-13)

> **Source**: BRD-OPS-ARCH-001...007, INV-1...INV-10

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-INV-001 | `test_inv1_reasoning_as_primitive` MUST verify agents provide reasoning, not truth | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INV-002 | `test_inv2_critic_non_controlling` MUST verify critics suggest, don't command | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INV-003 | `test_inv3_probabilistic_semantics` MUST verify all interpretations have confidence | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INV-004 | `test_inv4_auditable_decisions` MUST verify all decisions produce artifacts | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INV-005 | `test_inv5_orchestrator_control` MUST verify iteration is orchestrator-owned | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INV-006 | `test_inv6_explicit_platform_laws` MUST verify governance cannot be bypassed | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-INV-007 | `test_inv7_reasoning_observability` MUST verify all reasoning is traced | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

### 2.8 Executable Invariant Enforcement (Added: 2026-01-25)

> **Source**: BRD-INV-027, BRD-INV-028, BRD-INV-029, BRD-INV-030

This section defines TSD requirements ensuring platform invariants are executable, enforced via automated tests, and block CI/CD on failure.

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-INV-EXEC-001 | Architecture tests MUST exist for each platform invariant (INV-1 through INV-10+) | MUST | BRD-INV-027 | 1.3 | 25 Jan 2026 | Invariants as code |
| ACC-INV-EXEC-002 | Invariant tests MUST be located in `tests/architecture/test_invariants.py` | MUST | BRD-INV-027 | 1.3 | 25 Jan 2026 | Canonical location |
| ACC-INV-EXEC-003 | Invariant tests MUST be marked with `@pytest.mark.invariant` | MUST | BRD-INV-027 | 1.3 | 25 Jan 2026 | CI gate filtering |
| ACC-INV-EXEC-004 | Invariant tests MUST run on every CI build (not optional) | MUST | BRD-INV-027, BRD-INV-030 | 1.3 | 25 Jan 2026 | Blocking gate |
| ACC-INV-EXEC-005 | Invariant test failure MUST block merge/deployment | MUST | BRD-INV-030 | 1.3 | 25 Jan 2026 | No bypass allowed |
| ACC-INV-EXEC-006 | Invariant tests MUST NOT be skipped without P0 approval | MUST | BRD-INV-030 | 1.3 | 25 Jan 2026 | Skip requires escalation |
| ACC-INV-EXEC-007 | `test_products_no_semantic_reimplementation` MUST verify products import semantic logic from `core/` | MUST | BRD-INV-028 | 1.3 | 25 Jan 2026 | No product duplication |
| ACC-INV-EXEC-008 | `test_products_no_validation_reimplementation` MUST verify products import validation from `core/contracts/` | MUST | BRD-INV-028 | 1.3 | 25 Jan 2026 | No product duplication |
| ACC-INV-EXEC-009 | `test_products_no_confidence_reimplementation` MUST verify products import confidence logic from `core/knowledge/` | MUST | BRD-INV-028 | 1.3 | 25 Jan 2026 | No product duplication |
| ACC-INV-EXEC-010 | Duplication detection test MUST scan product directories for semantic/validation patterns | MUST | BRD-INV-029 | 1.3 | 25 Jan 2026 | Automated detection |
| ACC-INV-EXEC-011 | Duplication detection test MUST fail if product defines own SemanticEnvelope, Confidence, or Validation classes | MUST | BRD-INV-029 | 1.3 | 25 Jan 2026 | Pattern blocklist |
| ACC-INV-EXEC-012 | Duplication detection test MUST verify product imports use `from core.` prefix | MUST | BRD-INV-029 | 1.3 | 25 Jan 2026 | Import verification |
| ACC-INV-EXEC-013 | CI/CD pipeline MUST include dedicated "invariant-check" stage | MUST | BRD-INV-030 | 1.3 | 25 Jan 2026 | Explicit gate stage |
| ACC-INV-EXEC-014 | Invariant-check stage MUST run before integration/deployment stages | MUST | BRD-INV-030 | 1.3 | 25 Jan 2026 | Fail-fast ordering |
| ACC-INV-EXEC-015 | Invariant failures MUST produce structured error report with violation details | MUST | BRD-INV-030 | 1.3 | 25 Jan 2026 | Actionable diagnostics |

---

## 3. Coverage Requirements

### 3.1 Overall Coverage

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-COV-001 | Overall line coverage MUST be ≥80% | MUST | BRD-OPS-030 | 1.1 | 13 Jan 2026 | — |
| ACC-COV-002 | Overall branch coverage SHOULD be ≥70% | SHOULD | BRD-OPS-031 | 1.1 | 13 Jan 2026 | — |
| ACC-COV-003 | Coverage reports MUST be generated on CI runs | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-004 | Coverage MUST NOT decrease without justification | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

### 3.2 Module-Specific Coverage

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-COV-010 | Module `core/orchestrator/` MUST maintain ≥85% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-011 | Module `core/agents/` MUST maintain ≥80% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-012 | Module `core/tools/` MUST maintain ≥80% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-013 | Module `core/governance/` MUST maintain ≥85% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-014 | Module `core/memory/` MUST maintain ≥80% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-015 | Module `core/knowledge/` SHOULD maintain ≥75% coverage | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-016 | Module `core/contracts/` MUST maintain ≥90% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-017 | Module `gateway/api/` MUST maintain ≥80% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-018 | Module `gateway/cli/` SHOULD maintain ≥75% coverage | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-019 | Module `gateway/ui/` SHOULD maintain ≥60% coverage | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

### 3.3 Critical Path Coverage

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-COV-020 | Run lifecycle (start → complete) MUST have 100% path coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-021 | Error handling paths MUST have ≥90% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-022 | Security-sensitive code MUST have 100% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-COV-023 | Governance hooks MUST have 100% coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

---

## 4. Test Fixture Requirements

### 4.1 Common Fixtures

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-FIX-001 | `conftest.py` MUST provide `mock_settings` fixture | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-FIX-002 | `conftest.py` MUST provide `mock_memory_backend` fixture | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-FIX-003 | `conftest.py` MUST provide `mock_tracer` fixture | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-FIX-004 | `conftest.py` MUST provide `temp_observability_dir` fixture | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-FIX-005 | `conftest.py` MUST provide `sample_run_context` fixture | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-FIX-006 | `conftest.py` MUST provide `sample_flow` fixture | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.2 Fixture Isolation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-FIX-010 | Fixtures MUST NOT share mutable state between tests | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-FIX-011 | Database fixtures MUST use separate test databases | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-FIX-012 | File fixtures MUST use temporary directories | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-FIX-013 | All fixtures MUST clean up resources on teardown | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 5. Validation Requirements

### 5.1 Contract Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-VAL-001 | All Pydantic models MUST have validation tests | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-VAL-002 | Schema validation tests MUST cover valid inputs | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-VAL-003 | Schema validation tests MUST cover invalid inputs | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-VAL-004 | Schema validation tests MUST verify error messages | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 5.2 API Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-VAL-010 | All API endpoints MUST have request validation tests | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-VAL-011 | All API endpoints MUST have response validation tests | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-VAL-012 | API error responses MUST match error schema | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-VAL-013 | API validation MUST test boundary conditions | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 6. Performance Requirements

### 6.1 Test Performance

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-PERF-001 | Full test suite MUST complete within 10 minutes | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-PERF-002 | Unit test suite MUST complete within 2 minutes | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-PERF-003 | Integration test suite MUST complete within 5 minutes | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-PERF-004 | Individual tests MUST NOT exceed 30 seconds | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

### 6.2 Benchmarks

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-PERF-010 | Critical operations SHOULD have benchmark tests | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-PERF-011 | Benchmark results SHOULD be tracked over time | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-PERF-012 | Performance regressions SHOULD fail CI | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

---

## 7. CI/CD Requirements

### 7.1 Continuous Integration

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-CI-001 | All tests MUST pass before merge | MUST | BRD-OPS-032, BRD-OPS-ARCH-007 | 1.1 | 13 Jan 2026 | — |
| ACC-CI-002 | Tests MUST run on Python 3.11+ | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-CI-003 | Tests MUST run on both Linux and macOS | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-CI-004 | Type checking (mypy/pyright) MUST pass | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-CI-005 | Linting (ruff) MUST pass | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

### 7.2 Test Execution

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-CI-010 | Tests MUST be run via pytest | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-CI-011 | Test markers MUST be used for categorization | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-CI-012 | Slow tests MUST be marked with `@pytest.mark.slow` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-CI-013 | Tests requiring external services MUST be marked with `@pytest.mark.integration` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

### 7.3 Invariant CI/CD Gate (Added: 2026-01-25)

> **Source**: BRD-INV-027, BRD-INV-030

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-CI-INV-001 | CI pipeline MUST include `invariant-check` job/stage | MUST | BRD-INV-030 | 1.3 | 25 Jan 2026 | Dedicated gate |
| ACC-CI-INV-002 | `invariant-check` job MUST run `pytest -m invariant tests/architecture/` | MUST | BRD-INV-027 | 1.3 | 25 Jan 2026 | Marker-based execution |
| ACC-CI-INV-003 | `invariant-check` job MUST execute before `deploy` stage | MUST | BRD-INV-030 | 1.3 | 25 Jan 2026 | Fail-fast ordering |
| ACC-CI-INV-004 | `invariant-check` failure MUST set pipeline status to FAILED | MUST | BRD-INV-030 | 1.3 | 25 Jan 2026 | Blocking behavior |
| ACC-CI-INV-005 | `invariant-check` job MUST NOT have `allow_failure: true` | MUST | BRD-INV-030 | 1.3 | 25 Jan 2026 | No soft failure |
| ACC-CI-INV-006 | `invariant-check` results MUST be uploaded as CI artifact | MUST | BRD-INV-027 | 1.3 | 25 Jan 2026 | Audit trail |
| ACC-CI-INV-007 | Invariant test coverage report MUST be included in CI summary | SHOULD | BRD-INV-027 | 1.3 | 25 Jan 2026 | Visibility |


---

## 8. Security Testing Requirements

### 8.1 Security Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-SEC-001 | Redaction logic MUST have dedicated tests | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEC-002 | Path traversal prevention MUST be tested | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEC-003 | Input sanitization MUST be tested | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEC-004 | Payload size limits MUST be tested | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-SEC-005 | Sensitive data MUST NOT appear in test logs | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 9. Documentation Testing

### 9.1 Documentation Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-DOC-001 | README examples SHOULD be executable | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-DOC-002 | API documentation SHOULD match implementation | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-DOC-003 | Configuration examples SHOULD be valid | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

---

## 10. Requirement Traceability

### 10.1 Traceability Rules

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-TRACE-001 | Each techspec requirement MUST have corresponding test(s) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-TRACE-002 | Test docstrings SHOULD reference requirement IDs | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-TRACE-003 | Traceability matrix MUST be maintained in `TS-COVERAGE.md` for techspec-to-BRD coverage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

---

## 11. Test Data Requirements

### 11.1 Test Data Management

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ACC-DATA-001 | Test data MUST be version controlled | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-DATA-002 | Test data MUST NOT contain sensitive information | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-DATA-003 | Test data SHOULD be minimal but representative | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ACC-DATA-004 | Large test datasets SHOULD use fixtures, not files | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

---

## 12. Explicit Non-Goals (Added: 2026-01-13)

> **Acceptance Tests MUST NOT**:

| Non-Goal | Rationale | Violation Example |
|----------|-----------|-------------------|
| Flaky tests | Tests must be deterministic | Test passes 90% of time |
| External dependencies in unit tests | Unit tests must be isolated | Unit test calls OpenAI API |
| Shared mutable state | Tests must be independent | Test A modifies global used by Test B |
| Skipped critical tests | Critical paths must be tested | `@pytest.mark.skip` on governance test |
| Mocked governance in integration tests | Governance must be tested end-to-end | Integration test stubs all hooks |
| Performance as acceptance | Performance is SLO, not acceptance | Test fails if >500ms |

---
