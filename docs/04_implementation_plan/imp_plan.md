# Semantic Interpretation Implementation Plan

> **Feature**: Semantic Interpretation Phase (Gap Completion)  
> **Version**: 1.1  
> **Status**: In Progress  
> **Last Updated**: 2026-01-16  
> **Coverage Source**: [SD-COVERAGE.md](../05_systemdesign/SD-COVERAGE.md)  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |

## 1. Executive Summary

### 1.1 Current State (from SD-COVERAGE)

The semantic interpretation feature is **partially implemented**. This plan focuses on completing the remaining gaps.

| Component | Status | Notes |
|-----------|--------|-------|
| NextAction enum | Done | CONTINUE, ASK_USER, ABORT |
| Skip semantic flag | Done | `skip_semantic_interpretation: true` |
| ASK_USER pause handling | Done | -> PAUSED_WAITING_FOR_USER |
| SemanticEnvelope schema | Partial | Missing fields per spec |
| Engine integration | Partial | Phase exists but incomplete |
| Core normalization | Not Started | normalization.py needed |
| Trace events | Not Started | Semantic events needed |
| Product adapters | Not Started | hello_world adapter needed |
| Confidence gates | Not Started | Governance hook needed |
| Unit tests | Not Started | Test coverage needed |

### 1.2 Remaining Work

| Gap ID | Requirement | Effort | Priority |
|--------|-------------|--------|----------|
| GAP-001 | Complete SemanticEnvelope fields | 0.5d | P0 |
| GAP-002 | Complete engine integration | 1d | P0 |
| GAP-003 | Create normalization.py | 1d | P1 |
| GAP-004 | Add semantic trace events | 0.5d | P1 |
| GAP-005 | Add confidence gate hook | 0.5d | P1 |
| GAP-006 | Create hello_world adapter | 0.5d | P1 |
| GAP-007 | Add unit tests | 1d | P2 |
| GAP-008 | Add architecture tests | 0.5d | P2 |

**Total Remaining Effort**: ~5.5 engineering days

---

## 2. Architecture Overview

The semantic phase sits between run initialization and step execution:

1. **Run Init** -> already implemented
2. **Semantic Phase** -> GAP-001, GAP-002 (complete integration)
3. **Core Normalizer** -> GAP-003 (normalization.py)
4. **Product Adapter** -> GAP-006 (hello_world/semantic.py)
5. **Confidence Gate** -> GAP-005 (governance/hooks.py)
6. **NextAction Check** -> already implemented
7. **Step Execution / Pause** -> already implemented

---

## 3. Gap Implementation Plan

### Phase 1: Complete Schema & Engine (P0) - Days 1-2

**GAP-001: Complete SemanticEnvelope**

File: `core/contracts/semantic_schema.py`

Add missing fields to existing model:
- `entities: list[Entity]` (max 20)
- `constraints: dict[str, Any]`
- `ambiguities: list[str]` (max 20)
- `parameters: dict[str, Any]`
- `interpretation_method: str | None`

**GAP-002: Complete Engine Integration**

File: `core/orchestrator/engine.py`

Ensure semantic phase runs BEFORE step execution with proper error handling and envelope storage in RunRecord.

---

### Phase 2: Normalization & Tracing (P1) - Days 3-4

**GAP-003: Create Core Normalization**

File: `core/orchestrator/normalization.py` (NEW)

Functions:
- `normalize_whitespace(text)` - ORC-SEM-030
- `deduplicate_entities(entities)` - ORC-SEM-031
- `merge_constraints(constraints)` - ORC-SEM-032
- `apply_stable_ordering(envelope)` - ORC-SEM-033
- `coerce_types(value, target)` - ORC-SEM-034
- `apply_core_normalization(envelope)` - orchestrates all

**GAP-004: Add Semantic Trace Events**

File: `core/memory/tracing.py`

Add event types:
- SEMANTIC_INTERPRETATION_STARTED
- SEMANTIC_INTERPRETATION_COMPLETED
- SEMANTIC_VALIDATION_COMPLETED
- SEMANTIC_STOP_ISSUED

**GAP-005: Add Confidence Gate Hook**

File: `core/governance/hooks.py`

Add `check_semantic_confidence(envelope, threshold)` function.

---

### Phase 3: Product Adapter (P1) - Day 4

**GAP-006: Create hello_world Adapter**

File: `products/hello_world/semantic.py` (NEW)

Implement `HelloWorldSemanticAdapter` with `interpret()` and `validate()` methods.

---

### Phase 4: Tests (P2) - Days 5-6

**GAP-007: Unit Tests**
- `test_semantic_schema.py`
- `test_normalization.py`
- `test_semantic_phase.py`

**GAP-008: Architecture Tests**

File: `tests/architecture/test_semantic_isolation.py`

---

## 4. File Inventory

### Files to Modify

| File | Change |
|------|--------|
| `core/contracts/semantic_schema.py` | Add missing fields |
| `core/orchestrator/engine.py` | Complete integration |
| `core/governance/hooks.py` | Add confidence hook |
| `core/memory/tracing.py` | Add event types |
| `configs/app.yaml` | Add threshold config |

### Files to Create

| File | Purpose |
|------|---------|
| `core/orchestrator/normalization.py` | Normalization rules |
| `products/hello_world/semantic.py` | Reference adapter |
| `tests/unit/core/orchestrator/test_normalization.py` | Tests |
| `tests/unit/core/orchestrator/test_semantic_phase.py` | Tests |
| `tests/architecture/test_semantic_isolation.py` | Invariant tests |

---

## 5. Validation Criteria

- [ ] SemanticEnvelope has all required fields (ORC-SEM-010)
- [ ] Engine calls semantic phase before steps (ORC-SEM-001)
- [ ] normalization.py implements ORC-SEM-030...034
- [ ] Trace events emitted (ORC-SEM-040...043)
- [ ] Confidence gate blocks low-confidence runs
- [ ] hello_world adapter works end-to-end
- [ ] All tests pass

---

## 6. Timeline

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | GAP-001, GAP-002 | Schema, engine integration |
| 2 | GAP-002 continued | Engine tests passing |
| 3 | GAP-003, GAP-004 | normalization.py, trace events |
| 4 | GAP-005, GAP-006 | Confidence gate, adapter |
| 5 | GAP-007 | Unit tests |
| 6 | GAP-008 | Architecture tests |

**Total**: 5.5 days

---

## 7. References

- [SD-COVERAGE.md](../05_systemdesign/SD-COVERAGE.md)
- [ORC-orchestration.md](../03_techspecs/ORC-orchestration.md)
- [SD-ORC.md](../05_systemdesign/SD-ORC.md)
