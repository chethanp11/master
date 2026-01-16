# Developer Intent: Operational Excellence (INT-OPS)

> **Maps to**: [BRD-operations.md](../02_brd/BRD-operations.md)
>
> **Source**: Extracted from [intent.md](intent.md) § 4

---

## 4.1 State Persistence

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-001** | Run state must survive process restarts | Reliability |
| **INT-OPS-002** | In-flight workflows must be resumable after restart | No lost work |
| **INT-OPS-003** | State must be persisted durably (not just in-memory) | Data safety |
| **INT-OPS-004** | State storage must support concurrent access | Scalability |
| **INT-OPS-005** | Historical runs must be queryable | Audit, debugging |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| State survives restarts | Run lost after process restart |
| State transitions are traced | State changes without event |
| Everything is traced | Action taken without trace record |

---

## 4.2 Observability

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-010** | Every execution step must be traced | Debugging |
| **INT-OPS-011** | Traces must include: timestamp, event type, data | Complete picture |
| **INT-OPS-012** | Traces must be queryable by run, step, timeframe | Investigation |
| **INT-OPS-013** | Large outputs must be stored to files, not inline | Storage efficiency |
| **INT-OPS-014** | Observability data must be organized by product/run | Multi-tenancy |
| **INT-OPS-015** | Dashboards must visualize run status and trends | Operations monitoring |

---

## 4.3 Semantic Trace Events (Added: 2026-01-13)

> **Intent**: Structured trace events for semantic interpretation phase.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-SEM-001** | `semantic_interpretation_started` event must be emitted when phase begins | Track phase lifecycle |
| **INT-OPS-SEM-002** | Started event must include: run_id, product_id, raw_input_length | Context for debugging |
| **INT-OPS-SEM-003** | `semantic_interpretation_completed` event must be emitted when phase succeeds | Track successful interpretation |
| **INT-OPS-SEM-004** | Completed event must include: envelope_hash, confidence, ambiguity_count, entity_count, next_action | Interpretation metrics |
| **INT-OPS-SEM-005** | `semantic_validation_completed` event must be emitted after validation | Track validation outcome |
| **INT-OPS-SEM-006** | Validation event must include: is_valid, missing_fields, violation_count, revised_confidence | Validation metrics |
| **INT-OPS-SEM-007** | `semantic_stop_issued` event must be emitted on ASK_USER or ABORT | Track stop decisions |
| **INT-OPS-SEM-008** | Stop event must include: next_action, question (if ASK_USER), reason (if ABORT), violations | Stop context |
| **INT-OPS-SEM-009** | `semantic_interpretation_failed` event must be emitted on exception | Error visibility |
| **INT-OPS-SEM-010** | Failed event must include: error message | Debugging information |

### Event Catalog (New: 2026-01-13)

| Event | When | Payload |
|-------|------|---------|
| `semantic_interpretation_started` | Phase begins | `run_id`, `product_id`, `raw_input_length` |
| `semantic_interpretation_completed` | Phase succeeds | `envelope_hash`, `confidence`, `ambiguity_count`, `entity_count`, `next_action` |
| `semantic_validation_completed` | After validate() | `is_valid`, `missing_fields`, `violation_count`, `revised_confidence` |
| `semantic_stop_issued` | ASK_USER or ABORT | `next_action`, `question`, `reason`, `violations` |
| `semantic_interpretation_failed` | Exception thrown | `error` |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Events are structured | Free-form log message instead of event |
| Events include run_id | Event cannot be correlated to run |
| Events have timestamps | Event missing `ts` field |

---

## 4.4 Performance

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-020** | API responses must complete within 500ms (p95) | User experience |
| **INT-OPS-021** | Run startup must complete within 2 seconds | Responsiveness |
| **INT-OPS-022** | Memory backend operations must complete within 100ms | System responsiveness |
| **INT-OPS-023** | Performance metrics must be measurable | SLA monitoring |

---

## 4.5 Quality Assurance

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-030** | Core modules must have ≥80% test coverage | Quality baseline |
| **INT-OPS-031** | Critical paths (run lifecycle) must have 100% coverage | Risk mitigation |
| **INT-OPS-032** | All tests must pass before deployment | Quality gate |
| **INT-OPS-033** | Tests must complete within 10 minutes | Developer velocity |
| **INT-OPS-034** | Contracts (Pydantic models) must have validation tests | Interface stability |

---

## 4.6 Debugging Support

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-040** | Failed runs must include error details and stack traces | Root cause analysis |
| **INT-OPS-041** | Event timeline must be viewable for any run | Execution understanding |
| **INT-OPS-042** | Input/output data must be inspectable | Data debugging |
| **INT-OPS-043** | LLM calls and responses must be logged | AI debugging |
| **INT-OPS-044** | Tool calls and results must be logged | Integration debugging |

---

## 4.7 Architecture Tests (Added: 2026-01-13)

> **Intent**: Mandatory tests that lock critical semantic behavior.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-OPS-ARCH-001** | Architecture test must verify semantic phase is mandatory | Prevent regression of mandatory phase |
| **INT-OPS-ARCH-002** | Architecture test must verify ASK_USER blocks all step execution | Lock stop behavior |
| **INT-OPS-ARCH-003** | Architecture test must verify ABORT blocks all step execution | Lock abort behavior |
| **INT-OPS-ARCH-004** | Architecture test must verify product adapters don't import core orchestrator | Enforce isolation |
| **INT-OPS-ARCH-005** | Architecture test must verify core orchestrator doesn't import products | Enforce isolation |
| **INT-OPS-ARCH-006** | Architecture tests must live in `tests/architecture/` directory | Clear test organization |
| **INT-OPS-ARCH-007** | Architecture tests must be run as part of CI pipeline | Continuous enforcement |

### Required Architecture Tests (New: 2026-01-13)

| Test | Invariant Verified |
|------|-------------------|
| `test_semantic_phase_is_mandatory` | ORC-SEM-001: Semantic phase runs before any step execution |
| `test_stop_blocks_execution` | ORC-SEM-STOP-001: ASK_USER/ABORT prevent step execution |
| `test_product_adapter_isolated` | PROD-SEM-INT-005/006: No cross-layer imports |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Architecture tests must pass | Test failure ignored |
| Tests verify structure, not behavior | Test only checks runtime values |
| Tests are automated | Manual verification required |

---

## BRD Derivation

This document derives the following in [BRD-operations.md](../02_brd/BRD-operations.md):

- INT-OPS-* → BRD-OPS-*
- INT-OPS-SEM-* → BRD-OPS-SEM-*
- INT-OPS-ARCH-* → BRD-OPS-ARCH-*
