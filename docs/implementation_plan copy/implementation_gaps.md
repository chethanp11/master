# Implementation Gaps Analysis

**Repository:** master/  
**Analysis Date:** 12 January 2026  
**Baseline:** docs/refactor_plan.md (11 January 2026)

---

## Executive Summary

This document tracks the delta between the planned refactoring (17 phases over 26 weeks) and the actual implementation state. It identifies completed work, partial implementations, and remaining gaps to inform prioritization.

### Overall Status

| Category | Phases | Status |
|----------|--------|--------|
| **Fully Implemented** | 0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16-17 | 15/17 |
| **Partially Implemented** | 1, 3 | 2/17 |
| **Not Implemented** | None | 0/17 |

**Completion Rate:** ~88% of planned work completed

---

## Phase-by-Phase Analysis

### Phase 0: Baseline & Safety Net ✅ COMPLETE

**Goal:** Create acceptance tests to lock current behavior before refactoring.

**Deliverables:**
- [x] Determinism tests (`tests/acceptance_intelligence/test_determinism.py` - 360 lines)
- [x] HITL pause/resume tests (`tests/acceptance_intelligence/test_pause_resume.py` - 510 lines)
- [x] Governance baseline tests (`tests/acceptance_intelligence/test_governance_baseline.py` - 291 lines)
- [x] Trace emission tests (`tests/acceptance_intelligence/test_trace_emission.py` - 464 lines)
- [x] Golden path tests (`tests/acceptance_intelligence/test_golden_paths.py` - 297 lines)

**Evidence:**
- `tests/acceptance_intelligence/` contains 7 test files with comprehensive coverage
- `tests/acceptance_intelligence/golden/` contains expected output fixtures

---

### Phase 1: Contract Consolidation ⚠️ PARTIAL (70%)

**Goal:** Reduce 21 contract files → 14 files (33% reduction)

**Current State:** 17 files in `core/contracts/`

| File | Status | Notes |
|------|--------|-------|
| `action_plan_schema.py` | ✅ Keep | Core contract |
| `advisory_schema.py` | ⚠️ Review | Retained for intelligence; evaluate consolidation |
| `agent_schema.py` | ✅ Keep | Core contract |
| `budget_schema.py` | ✅ Keep | Core contract |
| `context_pack_schema.py` | ✅ Keep | Includes evidence models (merged) |
| `critic_schema.py` | ⚠️ Review | Retained for intelligence; evaluate consolidation |
| `descriptors_schema.py` | ✅ Keep | Enhanced with capabilities, cost hints |
| `flow_schema.py` | ✅ Keep | Core contract |
| `interaction_schema.py` | ✅ New | Consolidates HITL + questions |
| `question_schema.py` | ❌ Delete | Deprecated; re-exports to interaction_schema |
| `reasoning_ladder_schema.py` | ⚠️ Review | Retained for intelligence |
| `reasoning_schema.py` | ✅ Keep | Core contract |
| `retrieval_schema.py` | ✅ Keep | Core contract |
| `run_schema.py` | ✅ Keep | Core contract |
| `tool_schema.py` | ✅ Keep | Core contract |
| `user_input_schema.py` | ✅ Keep | Core contract |

**Gaps:**
1. `question_schema.py` should be deleted (deprecated wrapper exists)
2. Consider consolidating `advisory_schema.py`, `critic_schema.py`, `reasoning_ladder_schema.py` into `intelligence_schema.py`

**Action Items:**
- [ ] Delete `question_schema.py` after confirming no direct imports
- [ ] Evaluate consolidating intelligence-related schemas
- [ ] Target: 14 files (currently 17)

---

### Phase 2: Unused Module Removal ✅ COMPLETE (Revised)

**Goal:** Remove unused tool backends

**Deliverables:**
- [x] Remove `mcp_backend.py` - **REMOVED**
- [x] Remove `remote_backend.py` - **REMOVED**
- [x] `reasoning_ladder.py` - **RETAINED** (plan revised; provides bounded multi-pass pattern)

**Evidence:**
- `core/tools/backends/` contains only `local_backend.py`
- `core/agents/reasoning_ladder.py` exists with bounded interpret→propose→select pattern

**Notes:**
- Original plan marked `reasoning_ladder.py` for removal
- Plan was revised to retain it for intelligence capabilities (Phase 9)
- This is documented as an intentional deviation

---

### Phase 3: Engine Decomposition ⚠️ PARTIAL (50%)

**Goal:** Break `engine.py` (3,083 lines) into focused modules (~400 line coordinator)

**Current State:** `engine.py` still 2,481 lines (reduced from 3,083 but not to target)

| Module | Status | Lines | Target |
|--------|--------|-------|--------|
| `engine.py` | ⚠️ Too large | 2,481 | ~400 |
| `run_lifecycle.py` | ✅ Extracted | 472 | ~300 |
| `plan_executor.py` | ✅ Extracted | 624 | ~350 |
| `loop_executor.py` | ✅ Extracted | 496 | ~150 |
| `user_input_handler.py` | ✅ Extracted | 722 | ~250 |
| `step_runner.py` | ❌ Not created | - | ~400 |
| `hitl_handler.py` | ❌ Not extracted | - | ~200 |

**What's Done:**
- `run_lifecycle.py` - start_run, resume_run, complete_run
- `plan_executor.py` - plan_propose/gate/execute
- `loop_executor.py` - repeat_until handling
- `user_input_handler.py` - user_input pause/resume/validation

**Gaps:**
1. `engine.py` still contains step iteration logic (should be `step_runner.py`)
2. HITL handling not fully extracted to `hitl_handler.py` (separate from `hitl.py`)
3. Significant coupling between engine and extracted modules

**Action Items:**
- [ ] Extract step iteration to `step_runner.py`
- [ ] Extract remaining HITL logic to `hitl_handler.py`
- [ ] Reduce `engine.py` to coordinator role (~400 lines)
- [ ] Review extracted module sizes (some exceed targets)

---

### Phase 4: Governance Consolidation ✅ COMPLETE

**Goal:** Merge 5 gate files into unified `gates.py`

**Deliverables:**
- [x] Unified `gates.py` (749 lines)
- [x] Contains: BranchGate, LoopGate, PlanGate, CriticGate, RetrievalGate
- [x] Gate registry pattern with `resolve_gate()`

**Evidence:**
- `core/governance/gates.py` contains all gate implementations
- Individual gate files removed
- File count reduced from 9 → 5

---

### Phase 5: Registry Unification ✅ COMPLETE

**Goal:** Single generic registry base class

**Deliverables:**
- [x] `core/utils/registry.py` with `ComponentRegistry[T]` (182 lines)
- [x] `AgentRegistry` inherits from `ComponentRegistry[BaseAgent]`
- [x] `ToolRegistry` inherits from `ComponentRegistry[BaseTool]`

**Evidence:**
- `ComponentRegistry` provides: register, resolve, has, list_registered, get_meta
- Both registries share common implementation
- ~100 lines of duplication removed

---

### Phase 6: UI Modularization ✅ COMPLETE

**Goal:** Split `platform_app.py` (1,046 lines) into page modules

**Deliverables:**
- [x] `platform_app.py` reduced to 88 lines (coordinator)
- [x] `pages/home.py` - Product catalog view
- [x] `pages/execution.py` - Run execution view
- [x] `pages/history.py` - Run history view
- [x] `api_client.py` - HTTP client extracted

**Evidence:**
- `gateway/ui/platform_app.py` is slim coordinator
- `gateway/ui/pages/` contains modular page components
- All views work via API calls only (no direct core imports)

---

### Phase 7: Enhanced Descriptors & Evidence ✅ COMPLETE

**Goal:** Build semantic catalog for intelligent tool/agent selection

**Deliverables:**
- [x] `ToolDescriptor` with: capabilities, cost_hint, sensitivity_class
- [x] `AgentDescriptor` with: purpose, capabilities, allowed_step_types
- [x] `EvidenceItem` model with provenance tracking
- [x] `ToolResult` includes evidence field

**Evidence:**
- `core/contracts/descriptors_schema.py` contains enhanced descriptors
- `CostHint` and `SensitivityClass` enums defined
- Evidence provenance tracked in context packs

---

### Phase 8: Context Pack Builder ✅ COMPLETE

**Goal:** Curate LLM inputs deterministically

**Deliverables:**
- [x] `ContextPack` schema with evidence_index
- [x] `ContextPackBuilder` utility
- [x] Deterministic assembly (hash-verified)

**Evidence:**
- `core/contracts/context_pack_schema.py` (167 lines)
- `core/knowledge/context_pack.py` - builder implementation
- `core/knowledge/context_pack_merge.py` - merge logic

---

### Phase 9: Bounded Reasoning & Critic ✅ COMPLETE

**Goal:** Multi-pass reasoning with governance and quality checks

**Deliverables:**
- [x] `ReasoningLadder` with interpret→propose→select pattern
- [x] Budget enforcement (max_passes, max_tool_calls)
- [x] `CriticEvaluator` with structured recommendations
- [x] HITL escalation on budget exceed

**Evidence:**
- `core/agents/reasoning_ladder.py` (439 lines)
- `core/agents/critic_evaluator.py` (261 lines)
- `core/contracts/reasoning_ladder_schema.py` - structured outputs
- `core/contracts/critic_schema.py` - critic recommendations

---

### Phase 10: Parallel Tool Execution ✅ COMPLETE

**Goal:** TOOL_BATCH step type for efficient evidence gathering

**Deliverables:**
- [x] `StepType.TOOL_BATCH` enum value
- [x] `ToolBatchStepDef` schema
- [x] Parallel execution with deterministic merge
- [x] Read-only tool validation

**Evidence:**
- `core/contracts/flow_schema.py` defines TOOL_BATCH step type
- `core/orchestrator/step_executor.py` handles tool_batch execution
- Tests in `tests/core/test_phases_10_12.py`

---

### Phase 11: Missing-Info Question Loop ✅ COMPLETE

**Goal:** Structured information gathering from users

**Deliverables:**
- [x] `QuestionSet` artifact schema
- [x] `Question` model with validation rules
- [x] User input validation before resume
- [x] Answer merge into ContextPack

**Evidence:**
- `core/contracts/question_schema.py` (deprecated wrapper)
- `core/contracts/interaction_schema.py` (new consolidated location)
- `core/orchestrator/user_input_handler.py` (722 lines)

---

### Phase 12: Retrieval Augmentation ✅ COMPLETE

**Goal:** Approved-evidence-only retrieval

**Deliverables:**
- [x] Retrieval policy enforcement
- [x] Source allow/block lists
- [x] Evidence citations with provenance

**Evidence:**
- `core/contracts/retrieval_schema.py` - schemas
- `core/governance/gates.py` - RetrievalGate
- `core/tools/retrieval.py` - implementation

---

### Phase 13: Advisory Agent Set ✅ COMPLETE

**Goal:** Structured intelligence without control-flow authority

**Deliverables:**
- [x] `ToolSelector` - Recommend tools based on descriptors
- [x] `AgentSelector` - Recommend agents for subtasks
- [x] `GapFinder` - Identify missing evidence
- [x] `Summarizer` - Condense evidence into narrative
- [x] `RiskExplainer` - Explain confidence/risk factors

**Evidence:**
- `core/agents/advisory.py` contains all advisory agents
- `core/contracts/advisory_schema.py` defines output schemas
- Advisory agents cannot invoke tools directly (orchestrator-gated)

---

### Phase 14: Product Contract Simplification ✅ COMPLETE

**Goal:** Reduce registry boilerplate with auto-discovery

**Deliverables:**
- [x] `@agent` decorator for auto-registration
- [x] `@tool` decorator for auto-registration
- [x] `auto_discover_agents()` utility
- [x] `auto_discover_tools()` utility
- [x] Simplified `registry.py` pattern

**Evidence:**
- `core/utils/product_loader.py` (499 lines) - discovery utilities
- `core/agents/base.py` - `@agent` decorator
- `core/tools/base.py` - `@tool` decorator
- Products use decorator-based registration

---

### Phase 15: Product Test Consolidation ✅ COMPLETE

**Goal:** Clear test ownership

**Deliverables:**
- [x] Product tests under `products/{name}/tests/`
- [x] Platform tests under `tests/`
- [x] Standard test structure template

**Evidence:**
- `products/ade/tests/` - ADE-specific tests
- `products/hello_world/tests/` - Hello World tests
- `tests/` organized by category (unit, integration, architecture, acceptance)

---

### Phases 16-17: Test Infrastructure Hardening ✅ COMPLETE

**Goal:** Fill critical test gaps

**Deliverables:**
- [x] HITL edge case suite (`tests/core/test_hitl_edge_cases.py`)
- [x] Budget enforcement suite (`tests/core/test_budget_enforcement.py`)
- [x] Product isolation suite (`tests/architecture/test_product_isolation.py`)
- [x] Golden path tests (`tests/acceptance_intelligence/test_golden_paths.py`)
- [x] Expanded invariant tests (`tests/architecture/test_master_v1_invariants.py`)

**Evidence:**
- 348 total tests passing
- Comprehensive coverage of edge cases
- Architecture guardrails enforced via tests

---

## Summary of Remaining Gaps

### High Priority

| Gap | Location | Impact | Effort |
|-----|----------|--------|--------|
| Engine still too large | `core/orchestrator/engine.py` | Maintainability risk | 2-3 weeks |
| Contract file cleanup | `core/contracts/question_schema.py` | Cognitive overhead | 1 day |

### Medium Priority

| Gap | Location | Impact | Effort |
|-----|----------|--------|--------|
| Intelligence schema consolidation | `core/contracts/*.py` | File count reduction | 1 week |
| Extracted module size review | `core/orchestrator/*.py` | Code quality | 1 week |

### Low Priority

| Gap | Location | Impact | Effort |
|-----|----------|--------|--------|
| Documentation updates | `docs/*.md` | Documentation accuracy | 1-2 days |

---

## Implementation vs Documentation Delta

### Features Documented but Not Implemented

| Feature | Documentation | Status |
|---------|--------------|--------|
| SUBFLOW step type | `docs/flows_and_agents.md` mentions rejection | ✅ Correctly not implemented (v1 non-goal) |
| Remote tool backend | Originally in plan | ✅ Correctly removed |
| MCP tool backend | Originally in plan | ✅ Correctly removed |

### Features Implemented but Under-Documented

| Feature | Implementation | Documentation Gap |
|---------|---------------|-------------------|
| `@agent` decorator | `core/agents/base.py` | Partially documented in `product_howto.md` |
| `@tool` decorator | `core/tools/base.py` | Partially documented in `product_howto.md` |
| Unified `ComponentRegistry` | `core/utils/registry.py` | Not in `component_details.md` |
| `gates.py` consolidation | `core/governance/gates.py` | Not fully reflected in docs |

### Documentation Accuracy Issues

| Document | Issue |
|----------|-------|
| `component_details.md` | Lists removed backends (mcp, remote) |
| `core_architecture.md` | References old gate file structure |
| `engineering_standards.md` | Accurate, no issues |
| `flows_and_agents.md` | Mostly accurate |
| `governance_and_policies.md` | References old policy structure |
| `overview.md` | Mostly accurate |
| `product_howto.md` | Missing auto-discovery details |

---

## Recommended Actions

### Immediate (This Sprint)

1. **Delete `question_schema.py`** - It's a deprecated wrapper; update any remaining imports
2. **Update documentation** - Sync docs with actual implementation state

### Short-Term (Next 2 Sprints)

1. **Complete engine decomposition** - Extract `step_runner.py` and slim down `engine.py`
2. **Consolidate intelligence schemas** - Consider single `intelligence_schema.py`

### Long-Term (Backlog)

1. **Performance benchmarks** - Add nightly performance tests
2. **Contract versioning** - Implement schema evolution strategy (noted as missing in original plan)

---

## Metrics

| Metric | Before Refactor | After Refactor | Target | Gap |
|--------|-----------------|----------------|--------|-----|
| Contract files | 21 | 17 | 14 | -3 |
| Engine lines | 3,083 | 2,481 | ~400 | -2,081 |
| Governance files | 9 | 5 | 5 | 0 |
| UI main file lines | 1,046 | 88 | ~150 | ✅ |
| Test count | ~250 | 348 | 300+ | ✅ |
| Tool backends | 3 | 1 | 1 | ✅ |

---

## Appendix: File Inventory

### Core Contracts (17 files)

```
core/contracts/
├── __init__.py
├── action_plan_schema.py
├── advisory_schema.py
├── agent_schema.py
├── budget_schema.py
├── context_pack_schema.py
├── critic_schema.py
├── descriptors_schema.py
├── flow_schema.py
├── interaction_schema.py
├── question_schema.py          # DEPRECATED - delete
├── reasoning_ladder_schema.py
├── reasoning_schema.py
├── retrieval_schema.py
├── run_schema.py
├── tool_schema.py
└── user_input_schema.py
```

### Core Orchestrator (14 files)

```
core/orchestrator/
├── __init__.py
├── _types.py
├── branching.py
├── context.py
├── engine.py                   # 2,481 lines - needs decomposition
├── error_policy.py
├── flow_loader.py
├── hitl.py
├── loop_executor.py
├── looping.py
├── plan_executor.py
├── run_lifecycle.py
├── state.py
├── step_executor.py
├── templating.py
└── user_input_handler.py
```

### Core Governance (5 files)

```
core/governance/
├── __init__.py
├── budgeting.py
├── gates.py                    # Unified (749 lines)
├── hooks.py
├── policies.py
└── security.py
```

### Test Categories

```
tests/
├── acceptance_intelligence/    # Phase 0, 16-17 deliverables
├── architecture/               # Invariant tests
├── core/                       # Core module tests
├── integration/                # End-to-end tests
└── unit/                       # Fast unit tests
```
