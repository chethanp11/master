# BRD: Operational Excellence

> **Document ID**: BRD-OPS  
> **Version**: 1.1  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release  

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-12 | Initial release |
| 1.1 | 2026-01-13 | Added §3.7 Semantic Trace Events, §3.8 Architecture Tests |

---

## Governing Architecture Invariants

The following architecture invariants from [Developer Intent](../00_developer_intent/intent.md) govern this BRD:

| INV | Invariant | Implication for Operations |
|-----|-----------|---------------------------|
| **INV-7** | Reasoning Observability Is as Important as Execution | Traces expose options, confidence, rejections |
| **INV-5** | Iteration Is Orchestrator-Controlled | Iterative state is durable and resumable |

---

## 1. Business Context

### Problem Statement
AI systems are notoriously difficult to operate:
- Workflows fail with opaque errors
- State is lost on process restart
- Debugging requires deep system knowledge
- Performance issues are hard to diagnose
- Quality assurance is inconsistent

### Opportunity
An operational foundation that provides:
- Durable state that survives restarts
- Complete execution traces for debugging
- Performance monitoring and alerting
- Consistent quality through automated testing
- Self-service debugging for operators

### Business Value
- **Reliability**: Workflows survive infrastructure issues
- **Supportability**: Operators can diagnose issues independently
- **Quality**: High test coverage prevents regressions
- **Performance**: SLAs can be monitored and enforced

---

## 2. Stakeholders

| Stakeholder | Role | Primary Concern |
|-------------|------|-----------------|
| **SRE/Ops** | Operates the platform | Reliability, monitoring, alerting |
| **Support Engineer** | Diagnoses issues | Debugging, traceability |
| **QA Engineer** | Ensures quality | Test coverage, validation |
| **Platform Admin** | Manages infrastructure | Performance, capacity |

---

## 3. Business Requirements

> **Source**: [INT-OPS](../00_developer_intent/intent.md#4-operational-excellence-int-ops)

### 3.1 State Persistence

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-001** | Run state must survive process restarts | Derived from: INT-OPS-001 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-002** | In-flight workflows must be resumable after restart | Derived from: INT-OPS-002 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-003** | State must be persisted durably (not just in-memory) | Derived from: INT-OPS-003 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-004** | State storage must support concurrent access | Derived from: INT-OPS-004 | P1 | 2026-01-12 | V1.1 |
| **BRD-OPS-005** | Historical runs must be queryable | Derived from: INT-OPS-005 | P0 | 2026-01-12 | V1.1 |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| State survives restarts | Run lost after process restart |
| State transitions are traced | State changes without event |
| Everything is traced | Action taken without trace record |

### 3.2 Observability

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-010** | Every execution step must be traced | Derived from: INT-OPS-010 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-011** | Traces must include: timestamp, event type, data | Derived from: INT-OPS-011 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-012** | Traces must be queryable by run, step, timeframe | Derived from: INT-OPS-012 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-013** | Large outputs must be stored to files, not inline | Derived from: INT-OPS-013 | P1 | 2026-01-12 | V1.1 |
| **BRD-OPS-014** | Observability data must be organized by product/run | Derived from: INT-OPS-014 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-015** | Dashboards must visualize run status and trends | Derived from: INT-OPS-015 | P2 | 2026-01-12 | V1.1 |
| **BRD-OPS-016** | Reasoning behavior must be observable, not just execution steps | Derived from: — | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-017** | Traces must expose options considered, confidence evolution, rejection reasons | Derived from: — | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-018** | Reasoning traces must be queryable for audit, debugging, and improvement analysis | Derived from: — | P1 | 2026-01-13 | V1.1 |

### 3.3 Performance

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-020** | API responses must complete within 500ms (p95) | Derived from: INT-OPS-020 | P1 | 2026-01-12 | V1.1 |
| **BRD-OPS-021** | Run startup must complete within 2 seconds | Derived from: INT-OPS-021 | P1 | 2026-01-12 | V1.1 |
| **BRD-OPS-022** | Memory backend operations must complete within 100ms | Derived from: INT-OPS-022 | P1 | 2026-01-12 | V1.1 |
| **BRD-OPS-023** | Performance metrics must be measurable | Derived from: INT-OPS-023 | P1 | 2026-01-12 | V1.1 |

### 3.4 Quality Assurance

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-030** | Core modules must have ≥80% test coverage | Derived from: INT-OPS-030 | P1 | 2026-01-12 | V1.1 |
| **BRD-OPS-031** | Critical paths (run lifecycle) must have 100% coverage | Derived from: INT-OPS-031 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-032** | All tests must pass before deployment | Derived from: INT-OPS-032 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-033** | Tests must complete within 10 minutes | Derived from: INT-OPS-033 | P1 | 2026-01-12 | V1.1 |
| **BRD-OPS-034** | Contracts (Pydantic models) must have validation tests | Derived from: INT-OPS-034 | P0 | 2026-01-12 | V1.1 |

### 3.5 Debugging Support

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-040** | Failed runs must include error details and stack traces | Derived from: INT-OPS-040 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-041** | Event timeline must be viewable for any run | Derived from: INT-OPS-041 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-042** | Input/output data must be inspectable | Derived from: INT-OPS-042 | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-043** | LLM calls and responses must be logged | Derived from: INT-OPS-043 | P1 | 2026-01-12 | V1.1 |
| **BRD-OPS-044** | Tool calls and results must be logged | Derived from: INT-OPS-044 | P1 | 2026-01-12 | V1.1 |

### 3.6 Operational Tooling

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-050** | Operators must be able to list all runs | Derived from: — | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-051** | Operators must be able to cancel stuck runs | Derived from: — | P1 | 2026-01-12 | V1.1 |
| **BRD-OPS-052** | Operators must be able to view run details | Derived from: — | P0 | 2026-01-12 | V1.1 |
| **BRD-OPS-053** | Operators must be able to export run data | Derived from: — | P1 | 2026-01-12 | V1.1 |

### 3.7 Semantic Trace Events (Added: 2026-01-13)

> **Source**: [INT-OPS-SEM](../00_developer_intent/intent.md#43-semantic-trace-events-added-2026-01-13)

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-SEM-001** | `semantic_interpretation_started` event must be emitted when phase begins | Derived from: INT-OPS-SEM-001 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-SEM-002** | Started event must include: run_id, product_id, raw_input_length | Derived from: INT-OPS-SEM-002 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-SEM-003** | `semantic_interpretation_completed` event must be emitted when phase succeeds | Derived from: INT-OPS-SEM-003 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-SEM-004** | Completed event must include: envelope_hash, confidence, ambiguity_count, entity_count, next_action | Derived from: INT-OPS-SEM-004 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-SEM-005** | `semantic_validation_completed` event must be emitted after validation | Derived from: INT-OPS-SEM-005 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-SEM-006** | Validation event must include: is_valid, missing_fields, violation_count, revised_confidence | Derived from: INT-OPS-SEM-006 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-SEM-007** | `semantic_stop_issued` event must be emitted on ASK_USER or ABORT | Derived from: INT-OPS-SEM-007 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-SEM-008** | Stop event must include: next_action, question (if ASK_USER), reason (if ABORT), violations | Derived from: INT-OPS-SEM-008 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-SEM-009** | `semantic_interpretation_failed` event must be emitted on exception | Derived from: INT-OPS-SEM-009 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-SEM-010** | Failed event must include: error message | Derived from: INT-OPS-SEM-010 | P1 | 2026-01-13 | V1.1 |

**Event Catalog (New: 2026-01-13)**:
| Event | When | Payload |
|-------|------|---------|
| `semantic_interpretation_started` | Phase begins | `run_id`, `product_id`, `raw_input_length` |
| `semantic_interpretation_completed` | Phase succeeds | `envelope_hash`, `confidence`, `ambiguity_count`, `entity_count`, `next_action` |
| `semantic_validation_completed` | After validate() | `is_valid`, `missing_fields`, `violation_count`, `revised_confidence` |
| `semantic_stop_issued` | ASK_USER or ABORT | `next_action`, `question`, `reason`, `violations` |
| `semantic_interpretation_failed` | Exception thrown | `error` |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Events are structured | Free-form log message instead of event |
| Events include run_id | Event cannot be correlated to run |
| Events have timestamps | Event missing `ts` field |

### 3.8 Architecture Tests (Added: 2026-01-13)

> **Source**: [INT-OPS-ARCH](../00_developer_intent/intent.md#47-architecture-tests-added-2026-01-13)

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-ARCH-001** | Architecture test must verify semantic phase is mandatory | Derived from: INT-OPS-ARCH-001 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-ARCH-002** | Architecture test must verify ASK_USER blocks all step execution | Derived from: INT-OPS-ARCH-002 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-ARCH-003** | Architecture test must verify ABORT blocks all step execution | Derived from: INT-OPS-ARCH-003 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-ARCH-004** | Architecture test must verify product adapters don't import core orchestrator | Derived from: INT-OPS-ARCH-004 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-ARCH-005** | Architecture test must verify core orchestrator doesn't import products | Derived from: INT-OPS-ARCH-005 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-ARCH-006** | Architecture tests must live in `tests/architecture/` directory | Derived from: INT-OPS-ARCH-006 | P1 | 2026-01-13 | V1.1 |
| **BRD-OPS-ARCH-007** | Architecture tests must be run as part of CI pipeline | Derived from: INT-OPS-ARCH-007 | P0 | 2026-01-13 | V1.1 |

**Required Architecture Tests (New: 2026-01-13)**:
| Test | Invariant Verified |
|------|-------------------|
| `test_semantic_phase_is_mandatory` | ORC-SEM-001: Semantic phase runs before any step execution |
| `test_stop_blocks_execution` | ORC-SEM-STOP-001: ASK_USER/ABORT prevent step execution |
| `test_product_adapter_isolated` | PROD-SEM-INT-005/006: No cross-layer imports |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Architecture tests must pass | Test failure ignored |
| Tests verify structure, not behavior | Test only checks runtime values |
| Tests are automated | Manual verification required |

### 3.9 Explainability & Reproducibility (Added: 2026-01-18)

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-060** | Platform must retain reasoning artifacts and execution context to enable post-hoc explainability and reproducibility | Derived from: — | P0 | 2026-01-18 | V1.1 |
| **BRD-OPS-061** | Platform must record the versions, inputs, and hashes required to reproduce outcomes | Derived from: — | P0 | 2026-01-18 | V1.1 |

---

## 4. User Stories

### SRE/Ops Stories
- **US-OPS-001**: As an SRE, I want workflows to survive restarts so that I can perform maintenance without data loss.
- **US-OPS-002**: As an SRE, I want to monitor system health so that I can proactively address issues.
- **US-OPS-003**: As an SRE, I want performance metrics so that I can enforce SLAs.

### Support Engineer Stories
- **US-OPS-010**: As a support engineer, I want complete execution traces so that I can diagnose customer issues.
- **US-OPS-011**: As a support engineer, I want to see exactly what the AI did so that I can explain behavior.
- **US-OPS-012**: As a support engineer, I want to inspect inputs and outputs so that I can identify data issues.

### QA Engineer Stories
- **US-OPS-020**: As a QA engineer, I want high test coverage so that I can be confident in releases.
- **US-OPS-021**: As a QA engineer, I want fast tests so that I can iterate quickly.
- **US-OPS-022**: As a QA engineer, I want contract tests so that API changes don't break integrations.

### Platform Admin Stories
- **US-OPS-030**: As a platform admin, I want to see all runs so that I can manage capacity.
- **US-OPS-031**: As a platform admin, I want to cancel stuck runs so that I can recover from incidents.

---

## 5. Acceptance Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| State durability | Runs recoverable after restart | 100% |
| Trace completeness | Steps with full trace data | 100% |
| Test coverage (core) | Line coverage for core modules | ≥ 80% |
| Test suite duration | Full test suite runtime | < 10 min |
| API latency (p95) | 95th percentile response time | < 500ms |

---

## 6. Techspec Mapping

| BRD ID | Description | Derived Techspec | Ver |
|--------|-------------|------------------|-----|
| BRD-OPS-001 | State persistence | MEM-SQL-001...010 | 1.0 |
| BRD-OPS-002 | Resumable workflows | ORC-RESUME-001...010 | 1.0 |
| BRD-OPS-003 | Durable storage | MEM-BACK-001...010 | 1.0 |
| BRD-OPS-005 | Run queries | MEM-SQL-020...025 | 1.0 |
| BRD-OPS-010 | Step tracing | MEM-TRACE-001...010 | 1.0 |
| BRD-OPS-011 | Trace content | MEM-TRACE-005 (event structure) | 1.0 |
| BRD-OPS-012 | Trace queries | OBS-STORE-010...015 | 1.0 |
| BRD-OPS-013 | File storage | OBS-STORE-020...025 | 1.0 |
| BRD-OPS-014 | Organized storage | OBS-STORE-001...005 | 1.0 |
| BRD-OPS-016 | Reasoning observability | MEM-TRACE-REASON-* | 1.0 |
| BRD-OPS-017 | Reasoning trace content | MEM-TRACE-REASON-010...020 | 1.0 |
| BRD-OPS-018 | Reasoning trace queries | OBS-REASON-QUERY-* | 1.0 |
| BRD-OPS-030 | Test coverage | ACC-COV-001...023 | 1.0 |
| BRD-OPS-031 | Critical path coverage | ACC-COV-020...023 | 1.0 |
| BRD-OPS-032 | CI/CD | ACC-CI-001...005 | 1.0 |
| BRD-OPS-033 | Test performance | ACC-PERF-001...004 | 1.0 |
| BRD-OPS-034 | Contract tests | ACC-VAL-001...004 | 1.0 |
| BRD-OPS-040 | Error details | ORC-ERR-001...010 | 1.0 |
| BRD-OPS-041 | Event timeline | GW-UI-097...099 | 1.0 |
| BRD-OPS-SEM-* | Semantic trace events | MEM-TRACE-SEM-*, OBS-SEM-* | 1.1 |
| BRD-OPS-ARCH-* | Architecture tests | ACC-ARCH-*, TEST-ARCH-* | 1.1 |

---

## 7. Cross-Cutting Requirements

> **Source**: [INT-LIFECYCLE](../00_developer_intent/intent.md#5-developer-intent-lifecycle-int-lifecycle), [INT-FACTORY](../00_developer_intent/intent.md#6-product-factory-model-int-factory)

### 7.1 Intent-to-BRD Traceability

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-LIFE-001** | Every operations intent point must map to at least one BRD requirement | Derived from: INT-LIFECYCLE-020 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-LIFE-002** | BRD requirements must reference source intent | Derived from: INT-LIFECYCLE-021 | P0 | 2026-01-13 | V1.1 |

### 7.2 Product Factory Model

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version |
|----|-------------|---------------------------|----------|------------|---------|
| **BRD-OPS-FAC-001** | Framework MUST own memory and observability; products MUST use them | Derived from: INT-FACTORY-010 | P0 | 2026-01-13 | V1.1 |
| **BRD-OPS-FAC-002** | Products MUST NOT re-implement operational services | Derived from: INT-FACTORY-011 | P0 | 2026-01-13 | V1.1 |

---

## 8. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| SQLite | External | Default persistence backend |
| Filesystem | External | Observability file storage |
| pytest | External | Test framework |

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database corruption | Data loss | Backup strategy, WAL mode |
| Storage exhaustion | System failure | Monitoring, retention policies |
| Test flakiness | CI unreliability | Deterministic tests, retry policy |
| Performance regression | User impact | Benchmarks, alerting |

---

## 9. Observability Directory Structure

```
observability/
├── <product>/
│   └── <run_id>/
│       ├── input/           ← User inputs, uploaded files
│       ├── output/          ← Generated outputs, artifacts
│       ├── runtime/         ← Intermediate state, logs
│       └── events.jsonl     ← Event stream (if file-based)
└── staging/                 ← Temporary upload staging
```

---

## 11. Key Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `run_count` | Active runs | > 100 |
| `run_duration_p95` | 95th percentile run time | > 5 min |
| `error_rate` | Failed runs / total runs | > 5% |
| `api_latency_p95` | 95th percentile API response | > 500ms |
| `storage_usage` | Observability disk usage | > 80% |
| `pending_approvals` | Runs waiting for approval | > 10 |

---

## 12. Framework Laws Governing Operations

> **Source**: [Framework Laws](../00_developer_intent/intent.md#7-framework-laws)

| Law | Implication |
|-----|-------------|
| State transitions are traced | Every state change recorded |
| Governance hooks are mandatory | Operational hooks cannot be bypassed |
| Everything is traced | No action without trace record |

---

## Related Documents

- [Intent.md](../00_developer_intent/intent.md) — Source developer intent
- [Vision.md](../00_developer_intent/Vision.md) — Platform vision and principles
- [BRD-governance.md](BRD-governance.md) — Audit requirements
- [MEM-memory.md](../techspec/MEM-memory.md) — Technical memory specs
- [ACC-acceptance.md](../techspec/ACC-acceptance.md) — Technical acceptance specs
