# Implementation Plan: V1.3 Tech Spec Requirements

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  
> **Version**: 1.2  
> **Status**: V1.3 Gap Implementation  
> **Last Updated**: 2026-01-20  
> **Coverage Source**: [SD-COVERAGE.md](../05_systemdesign/SD-COVERAGE.md)  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.2 | 2026-01-20 | Added V1.3 Tech Spec implementation units (IMP-009 to IMP-030) for Hypothesis Management, Sufficiency State, Reasoning Lifecycle, Terminal Outcomes, Self-Modification Prevention, Explainability, Reproducibility |
| 1.1 | 2026-01-13 | Header version normalization |

## 1. Executive Summary

### 1.1 Current State (from SD-COVERAGE)

Tech Specs were updated to V1.3 with 63 new requirements covering Hypothesis Management, Sufficiency State, Reasoning Lifecycle, Terminal Outcomes, Self-Modification Prevention, Explainability, and Reproducibility. This plan covers implementation of all new requirements.

| Component | Total New | Priority | Status |
|-----------|-----------|----------|--------|
| ORC (Reasoning Lifecycle, Terminal Outcomes) | 23 | P0 | Not Started |
| INT (Hypothesis, Sufficiency, Confidence, ContextPack Freeze) | 36 | P0-P1 | Not Started |
| GOV (Self-Modification Prevention) | 10 | P1 | Not Started |
| MEM (Explainability, Reproducibility) | 19 | P1-P2 | Not Started |

### 1.2 Implementation Work Summary

| IMP-ID Range | Feature Area | Gap IDs | Effort | Priority |
|--------------|--------------|---------|--------|----------|
| IMP-009 to IMP-011 | Orchestrator Reasoning Lifecycle | GAP-009...011 | 5d | P0 |
| IMP-012 to IMP-013 | Orchestrator Terminal Outcomes | GAP-012...013 | 3d | P0 |
| IMP-014 to IMP-017 | Intelligence Hypothesis & Sufficiency | GAP-014...017 | 8d | P0 |
| IMP-018 to IMP-021 | Intelligence Confidence & ContextPack | GAP-018...021 | 5d | P1 |
| IMP-022 to IMP-024 | Governance Self-Modification Prevention | GAP-022...024 | 3d | P1 |
| IMP-025 to IMP-026 | Memory Explainability | GAP-025...026 | 3d | P1 |
| IMP-027 to IMP-030 | Memory Reproducibility | GAP-027...030 | 4d | P2 |

**Total Remaining Effort**: ~31 engineering days

---

## 2. Dependency Graph

```
Phase 1 (P0): Foundation
├── IMP-014: Hypothesis Schema (INT-HYP-001...005)
├── IMP-016: SufficiencyState Schema (INT-SUFF-001...005)
└── IMP-012: Terminal Outcome Schema (ORC-TERM-001...005)

Phase 2 (P0): Core Logic
├── IMP-015: Hypothesis Selection (INT-HYP-SEL-001...005)
│   └── depends on: IMP-014
├── IMP-017: SufficiencyState Lifecycle (INT-SUFF-LC-001...005)
│   └── depends on: IMP-016
├── IMP-009: Reasoning Lifecycle Phases (ORC-REASON-001...005)
│   └── depends on: IMP-014, IMP-016
├── IMP-010: Bounded Reasoning Iteration (ORC-REASON-010...015)
│   └── depends on: IMP-009
└── IMP-013: Terminal Outcome Artifacts (ORC-TERM-ART-001...004)
    └── depends on: IMP-012

Phase 3 (P1): Signals & Guards
├── IMP-018: Confidence Propagation (INT-CONF-001...005)
│   └── depends on: IMP-015
├── IMP-019: Confidence Thresholds (INT-CONF-THR-001...005)
│   └── depends on: IMP-018
├── IMP-020: ContextPack Freeze Requirements (INT-CP-FREEZE-001...003)
├── IMP-021: ContextPack Freeze Lifecycle (INT-CP-FREEZE-LC-001...003)
│   └── depends on: IMP-020
├── IMP-022: Self-Modification Prevention Core (GOV-POL-SELFMOD-001...003)
├── IMP-023: Frozen Configuration Enforcement (GOV-POL-SELFMOD-010...013)
│   └── depends on: IMP-022
├── IMP-024: Allowed Runtime Mutations (GOV-POL-SELFMOD-020...022)
│   └── depends on: IMP-022
├── IMP-011: Reasoning Phase Events (ORC-REASON-020...022)
│   └── depends on: IMP-009
├── IMP-025: Explainability Core (MEM-EXPLAIN-001...005)
│   └── depends on: IMP-011
└── IMP-026: Explanation Artifact (MEM-EXPLAIN-ART-001...003)
    └── depends on: IMP-025, IMP-012

Phase 4 (P2): Reproducibility
├── IMP-027: Version Tracking (MEM-REPRO-001...003)
├── IMP-028: Input Hashing (MEM-REPRO-010...012)
│   └── depends on: IMP-020
├── IMP-029: Output Hashing (MEM-REPRO-020...021)
│   └── depends on: IMP-012
└── IMP-030: Reproducibility Validation (MEM-REPRO-030...032)
    └── depends on: IMP-028, IMP-029
```

---

## 3. Implementation Units

### IMP-009: Orchestrator Reasoning Lifecycle Phases

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | ORC-REASON-001, ORC-REASON-002, ORC-REASON-003, ORC-REASON-004, ORC-REASON-005 |
| **Source BRD** | BRD-AUTO-047 |
| **Gap ID** | GAP-009 |
| **Priority** | P0 |
| **Effort** | 2 days |
| **Dependencies** | IMP-014, IMP-016 |

**Target Code Locations**:
- `core/orchestrator/reasoning_lifecycle.py` (NEW)
- `core/contracts/reasoning_schema.py` (MODIFY)
- `core/orchestrator/engine.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `ReasoningPhase` enum with: `INTERPRET`, `PROPOSE`, `CRITIQUE`, `RECOMMEND`
2. Create `ReasoningLifecycle` class in `reasoning_lifecycle.py`:
   - `__init__(self, max_iterations: int = 3)`
   - `current_phase: ReasoningPhase`
   - `transition_to(phase: ReasoningPhase) -> None`
   - `can_transition(from_phase, to_phase) -> bool`
3. Create typed output schemas: `InterpretOutput`, `ProposeOutput`, `CritiqueOutput`, `RecommendOutput`
4. Add `phase_outputs: dict[ReasoningPhase, Any]` to persist outputs
5. Integrate lifecycle control into `engine.py` reasoning step
6. Add invariant: RECOMMEND blocked without CRITIQUE pass

**Acceptance Checks**:
- [ ] `ReasoningPhase` enum exists with 4 phases
- [ ] Phase transitions logged via trace events
- [ ] Each phase produces typed output artifact
- [ ] Phase outputs persisted before transition
- [ ] RECOMMEND blocked without CRITIQUE (test)

---

### IMP-010: Bounded Reasoning Iteration

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | ORC-REASON-010, ORC-REASON-011, ORC-REASON-012, ORC-REASON-013, ORC-REASON-014, ORC-REASON-015 |
| **Source BRD** | BRD-AUTO-048 |
| **Gap ID** | GAP-010 |
| **Priority** | P0 |
| **Effort** | 2 days |
| **Dependencies** | IMP-009 |

**Target Code Locations**:
- `core/orchestrator/reasoning_lifecycle.py` (MODIFY)
- `core/governance/budgeting.py` (MODIFY)
- `core/memory/tracing.py` (MODIFY)

**Step-by-Step Instructions**:
1. Add `max_reasoning_iterations` config (default: 3, max: 10) to `ReasoningLifecycle`
2. Add `iteration_count: int` counter to lifecycle state
3. Integrate `BudgetEnforcer.consume_budget("reasoning")` per iteration
4. Add `ReasoningTerminationReason` enum: `SUFFICIENT`, `MAX_ITERATIONS`, `BUDGET_EXCEEDED`, `CONFIDENCE_MET`
5. Create `reasoning_terminated` trace event with: `iteration_count`, `reason`, `final_confidence`
6. Add termination logic in lifecycle when `iteration_count >= max_reasoning_iterations`

**Acceptance Checks**:
- [ ] `max_reasoning_iterations` configurable (default 3, max 10)
- [ ] Each iteration consumes reasoning budget
- [ ] `iteration_count` tracked and emitted in trace events
- [ ] Deterministic termination at max iterations
- [ ] `reasoning_terminated` event emitted with correct payload

---

### IMP-011: Reasoning Phase Events

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | ORC-REASON-020, ORC-REASON-021, ORC-REASON-022 |
| **Source BRD** | BRD-AUTO-047 |
| **Gap ID** | GAP-011 |
| **Priority** | P0 |
| **Effort** | 1 day |
| **Dependencies** | IMP-009 |

**Target Code Locations**:
- `core/memory/tracing.py` (MODIFY)
- `core/orchestrator/reasoning_lifecycle.py` (MODIFY)

**Step-by-Step Instructions**:
1. Add `TraceEventKind.REASONING_PHASE_STARTED` with payload: `phase_name`, `iteration`, `input_hash`
2. Add `TraceEventKind.REASONING_PHASE_COMPLETED` with payload: `phase_name`, `iteration`, `output_hash`, `confidence`
3. Add `TraceEventKind.REASONING_PHASE_FAILED` with payload: `phase_name`, `iteration`, `error_code`, `reason`
4. Emit events from `ReasoningLifecycle.transition_to()` and exception handlers

**Acceptance Checks**:
- [ ] `reasoning_phase_started` event emitted at phase start
- [ ] `reasoning_phase_completed` event emitted at phase completion
- [ ] `reasoning_phase_failed` event emitted on failure
- [ ] All events include correct payload fields

---

### IMP-012: Explicit Terminal Outcome Definitions

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | ORC-TERM-001, ORC-TERM-002, ORC-TERM-003, ORC-TERM-004, ORC-TERM-005 |
| **Source BRD** | BRD-AUTO-052 |
| **Gap ID** | GAP-012 |
| **Priority** | P0 |
| **Effort** | 1.5 days |
| **Dependencies** | None |

**Target Code Locations**:
- `core/contracts/run_schema.py` (MODIFY)
- `core/orchestrator/run_lifecycle.py` (MODIFY)
- `core/memory/tracing.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `TerminalOutcome` enum: `COMPLETED`, `FAILED`, `CANCELLED`, `ABORTED`, `PAUSED_INDEFINITE`
2. Create `OutcomeReason` enum: `SUCCESS`, `USER_ABORT`, `GOVERNANCE_BLOCK`, `BUDGET_EXCEEDED`, `MAX_ITERATIONS`, `VALIDATION_FAILED`, `UNRECOVERABLE_ERROR`
3. Add `terminal_outcome: TerminalOutcome | None` to `RunRecord`
4. Add `outcome_reason: OutcomeReason | None` to `RunRecord`
5. Add `outcome_explanation: str | None` to `RunRecord` (human-readable)
6. Add `TraceEventKind.RUN_TERMINAL_OUTCOME` with full payload
7. Update `run_lifecycle.py` to set terminal outcome on run completion/failure

**Acceptance Checks**:
- [ ] `TerminalOutcome` and `OutcomeReason` enums exist
- [ ] Every terminal outcome includes reason and explanation
- [ ] `outcome_explanation` is human-readable
- [ ] `run_terminal_outcome` event emitted
- [ ] Terminal outcome persisted in `RunRecord`

---

### IMP-013: Terminal Outcome Artifacts

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | ORC-TERM-ART-001, ORC-TERM-ART-002, ORC-TERM-ART-003, ORC-TERM-ART-004 |
| **Source BRD** | BRD-AUTO-052 |
| **Gap ID** | GAP-013 |
| **Priority** | P0 |
| **Effort** | 1.5 days |
| **Dependencies** | IMP-012 |

**Target Code Locations**:
- `core/contracts/run_schema.py` (MODIFY)
- `core/orchestrator/run_lifecycle.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `CompletedArtifact` schema with final output
2. Create `FailedArtifact` schema: `error_code`, `error_message`, `stack_trace` (optional)
3. Create `AbortedArtifact` schema: `abort_reason`, `abort_source` (user/system/governance)
4. Add `terminal_artifact: dict | None` to `RunRecord`
5. Ensure terminal artifacts persisted BEFORE run record finalized
6. Add validation in `update_run_output` to require artifact for terminal states

**Acceptance Checks**:
- [ ] COMPLETED outcome includes final output artifact
- [ ] FAILED outcome includes error artifact with required fields
- [ ] ABORTED outcome includes abort artifact with source
- [ ] Artifacts persisted before run record finalized

---

### IMP-014: Hypothesis Structure

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | INT-HYP-001, INT-HYP-002, INT-HYP-003, INT-HYP-004, INT-HYP-005 |
| **Source BRD** | BRD-AUTO-028 |
| **Gap ID** | GAP-014 |
| **Priority** | P0 |
| **Effort** | 2 days |
| **Dependencies** | None |

**Target Code Locations**:
- `core/contracts/hypothesis_schema.py` (NEW)
- `core/knowledge/context_pack.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `Hypothesis` Pydantic model:
   - `id: str` (UUID)
   - `description: str`
   - `confidence: float` (0.0-1.0, with ge/le validators)
   - `evidence_refs: list[EvidenceRef]` (max 20 items)
2. Create `HypothesisSet` Pydantic model:
   - `hypotheses: list[Hypothesis]` (max 10)
   - `created_at: datetime`
   - `context_hash: str | None`
   - `frozen: bool = False`
3. Add immutability enforcement: `freeze()` method sets `frozen = True`
4. Raise `HypothesisSetFrozenError` on modification attempts when frozen
5. Add `all_hypotheses: list[HypothesisSet]` to `ContextPack` for audit trail

**Acceptance Checks**:
- [ ] `Hypothesis` model with id, description, confidence, evidence_refs
- [ ] `HypothesisSet` with hypotheses list, created_at, context_hash
- [ ] `HypothesisSet` immutable once frozen
- [ ] All hypotheses retained in audit trail

---

### IMP-015: Hypothesis Selection

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | INT-HYP-SEL-001, INT-HYP-SEL-002, INT-HYP-SEL-003, INT-HYP-SEL-004, INT-HYP-SEL-005 |
| **Source BRD** | BRD-AUTO-028 |
| **Gap ID** | GAP-015 |
| **Priority** | P0 |
| **Effort** | 2 days |
| **Dependencies** | IMP-014 |

**Target Code Locations**:
- `core/knowledge/hypothesis_selector.py` (NEW)
- `core/memory/tracing.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `select_hypothesis(hypothesis_set: HypothesisSet, confidence_margin: float = 0.1) -> Hypothesis | None`
2. Implement selection logic:
   - Sort by confidence descending
   - If top 2 within `confidence_margin`, return `None` (triggers ASK_USER)
   - Otherwise return highest confidence hypothesis
3. Create `TraceEventKind.HYPOTHESIS_SELECTED` with: `selected_id`, `alternatives`, `margin`, `reason`
4. Store rejection reasons for each non-selected hypothesis
5. Emit event on selection

**Acceptance Checks**:
- [ ] `select_hypothesis` returns exactly one Hypothesis or None
- [ ] Selection prefers highest confidence
- [ ] Within-margin triggers ASK_USER (returns None)
- [ ] `hypothesis_selected` event emitted with correct payload
- [ ] Rejected hypotheses recorded with reasons

---

### IMP-016: SufficiencyState Structure

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | INT-SUFF-001, INT-SUFF-002, INT-SUFF-003, INT-SUFF-004, INT-SUFF-005 |
| **Source BRD** | BRD-AUTO-029 |
| **Gap ID** | GAP-016 |
| **Priority** | P0 |
| **Effort** | 2 days |
| **Dependencies** | None |

**Target Code Locations**:
- `core/contracts/sufficiency_schema.py` (NEW)
- `core/knowledge/context_pack.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `Fact` model: `id`, `description`, `evidence_ref`, `confidence`
2. Create `Unknown` model: `id`, `question`, `importance`, `blocking`
3. Create `Assumption` model: `id`, `description`, `confidence`, `evidence_ref`
4. Create `Gap` model: `id`, `description`, `priority`, `blocking`
5. Create `SufficiencyState` Pydantic model:
   - `facts: list[Fact]`
   - `unknowns: list[Unknown]`
   - `assumptions: list[Assumption]`
   - `gaps: list[Gap]`
   - `run_id: str`
   - `updated_at: datetime`
6. Add `sufficiency_state: SufficiencyState | None` to `ContextPack`

**Acceptance Checks**:
- [ ] `SufficiencyState` maintained per run
- [ ] Contains `facts` (verified evidence)
- [ ] Contains `unknowns` (unresolved questions)
- [ ] Contains `assumptions` (with confidence)
- [ ] Contains `gaps` (missing information)

---

### IMP-017: SufficiencyState Lifecycle

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | INT-SUFF-LC-001, INT-SUFF-LC-002, INT-SUFF-LC-003, INT-SUFF-LC-004, INT-SUFF-LC-005 |
| **Source BRD** | BRD-AUTO-029 |
| **Gap ID** | GAP-017 |
| **Priority** | P0 |
| **Effort** | 2 days |
| **Dependencies** | IMP-016 |

**Target Code Locations**:
- `core/knowledge/sufficiency_manager.py` (NEW)
- `core/memory/tracing.py` (MODIFY)
- `core/memory/base.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `SufficiencyManager` class:
   - `update_with_evidence(evidence: list[EvidenceItem]) -> SufficiencyState`
   - `resolve_unknown(unknown_id: str, evidence: EvidenceItem) -> SufficiencyState`
   - `resolve_gap(gap_id: str, evidence: EvidenceItem) -> SufficiencyState`
   - `is_sufficient() -> bool` (returns `len(gaps) == 0` or all gaps non-blocking)
2. Add `TraceEventKind.SUFFICIENCY_STATE_UPDATED` with state diff
3. Add `persist_sufficiency_state(run_id, state)` to `MemoryBackend`
4. Add `restore_sufficiency_state(run_id) -> SufficiencyState | None` for resumption
5. Add check: run proceeds only if sufficient or gaps non-blocking

**Acceptance Checks**:
- [ ] SufficiencyState persisted after each reasoning pass
- [ ] New evidence updates facts and resolves unknowns/gaps
- [ ] `sufficiency_state_updated` event emitted on transitions
- [ ] State restorable from persistence
- [ ] Run proceeds only if gaps.count == 0 or non-blocking

---

### IMP-018: Confidence as Runtime Signal

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | INT-CONF-001, INT-CONF-002, INT-CONF-003, INT-CONF-004, INT-CONF-005 |
| **Source BRD** | BRD-AUTO-049 |
| **Gap ID** | GAP-018 |
| **Priority** | P1 |
| **Effort** | 1.5 days |
| **Dependencies** | IMP-015 |

**Target Code Locations**:
- `core/contracts/reasoning_schema.py` (MODIFY)
- `core/agents/reasoning_ladder.py` (MODIFY)
- `core/memory/tracing.py` (MODIFY)

**Step-by-Step Instructions**:
1. Add `confidence: float` field to all reasoning output schemas (MUST)
2. Create `aggregate_confidence(confidences: list[float], weights: list[float] = None) -> float`
   - Default: weighted product of component confidences
3. Add `confidence` field to all reasoning trace events
4. Create governance action trigger when confidence < threshold:
   - Emit `confidence_below_threshold` event
   - Delegate to governance hook for action (ASK_USER, HITL, ABORT)

**Acceptance Checks**:
- [ ] Confidence flows through all reasoning phases
- [ ] Each reasoning output includes confidence field
- [ ] Aggregated confidence uses weighted product formula
- [ ] Confidence below threshold triggers governance actions
- [ ] Confidence emitted in all reasoning trace events

---

### IMP-019: Confidence Thresholds

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | INT-CONF-THR-001, INT-CONF-THR-002, INT-CONF-THR-003, INT-CONF-THR-004, INT-CONF-THR-005 |
| **Source BRD** | BRD-AUTO-049 |
| **Gap ID** | GAP-019 |
| **Priority** | P1 |
| **Effort** | 1.5 days |
| **Dependencies** | IMP-018 |

**Target Code Locations**:
- `configs/app.yaml` (MODIFY)
- `configs/products.yaml` (MODIFY)
- `core/governance/hooks.py` (MODIFY)

**Step-by-Step Instructions**:
1. Add `confidence_threshold: 0.7` to `configs/app.yaml` (global default)
2. Add per-product threshold in `configs/products.yaml`: `by_product.<product>.confidence_threshold`
3. Implement threshold resolution: per-product overrides global
4. Create `TraceEventKind.CONFIDENCE_THRESHOLD_VIOLATED` with: `actual`, `threshold`, `action`
5. Enforce comparison: `<` means below, `>=` means at or above (deterministic)
6. Add governance floor: products MUST NOT set threshold below 0.5

**Acceptance Checks**:
- [ ] Global confidence threshold configurable (default 0.7)
- [ ] Per-product thresholds override global
- [ ] Threshold comparison deterministic
- [ ] `confidence_threshold_violated` event logged
- [ ] Products cannot lower threshold below 0.5

---

### IMP-020: ContextPack Freeze Requirements

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | INT-CP-FREEZE-001, INT-CP-FREEZE-002, INT-CP-FREEZE-003 |
| **Source BRD** | BRD-AUTO-051 |
| **Gap ID** | GAP-020 |
| **Priority** | P1 |
| **Effort** | 1 day |
| **Dependencies** | None |

**Target Code Locations**:
- `core/knowledge/context_pack.py` (MODIFY)
- `core/contracts/context_pack_schema.py` (MODIFY)

**Step-by-Step Instructions**:
1. Add `frozen: bool = False` to `ContextPack`
2. Add `frozen_at: datetime | None` to `ContextPack`
3. Add `frozen_hash: str | None` (SHA-256 of serialized content)
4. Create `freeze()` method:
   - Sets `frozen = True`
   - Sets `frozen_at = datetime.now(UTC)`
   - Computes and sets `frozen_hash`
5. Create `ContextPackFrozenError` exception
6. Add guard in all mutating methods: raise `ContextPackFrozenError` if frozen

**Acceptance Checks**:
- [ ] ContextPack frozen (immutable) before plan generation
- [ ] Frozen ContextPack has `frozen_at` timestamp
- [ ] Frozen ContextPack has `frozen_hash` (SHA-256)
- [ ] Modification attempts raise `ContextPackFrozenError`

---

### IMP-021: ContextPack Freeze Lifecycle

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | INT-CP-FREEZE-LC-001, INT-CP-FREEZE-LC-002, INT-CP-FREEZE-LC-003 |
| **Source BRD** | BRD-AUTO-051, BRD-OPS-061 |
| **Gap ID** | GAP-021 |
| **Priority** | P1 |
| **Effort** | 1 day |
| **Dependencies** | IMP-020 |

**Target Code Locations**:
- `core/memory/tracing.py` (MODIFY)
- `core/orchestrator/plan_executor.py` (MODIFY)
- `core/memory/base.py` (MODIFY)

**Step-by-Step Instructions**:
1. Add `TraceEventKind.CONTEXT_PACK_FROZEN` with: `run_id`, `frozen_hash`, `evidence_count`
2. Emit event when `ContextPack.freeze()` is called
3. Add `persist_context_pack(run_id, context_pack)` to `MemoryBackend`
4. Add validation in `plan_executor.py`: check `context_pack.frozen == True` before execution
5. Raise `ContextPackNotFrozenError` if plan execution attempted with unfrozen pack

**Acceptance Checks**:
- [ ] `context_pack_frozen` event emitted on freeze
- [ ] Frozen ContextPack persisted for audit/reproducibility
- [ ] Plan executor validates ContextPack is frozen
- [ ] Execution blocked if ContextPack not frozen

---

### IMP-022: Runtime Self-Modification Prevention Core

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | GOV-POL-SELFMOD-001, GOV-POL-SELFMOD-002, GOV-POL-SELFMOD-003 |
| **Source BRD** | BRD-GOV-054 |
| **Gap ID** | GAP-022 |
| **Priority** | P1 |
| **Effort** | 1 day |
| **Dependencies** | None |

**Target Code Locations**:
- `core/governance/self_modification_guard.py` (NEW)
- `core/governance/hooks.py` (MODIFY)
- `core/memory/tracing.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `SelfModificationBlockedError` exception
2. Create `SelfModificationGuard` class:
   - `check_config_modification(agent_id, target_config) -> None` (raises if blocked)
   - `check_prompt_modification(agent_id, target_prompt) -> None` (raises if blocked)
   - `check_policy_modification(agent_id, target_policy) -> None` (raises if blocked)
   - `check_learning_update(agent_id) -> None` (raises if blocked)
3. Add `TraceEventKind.SELF_MODIFICATION_BLOCKED` with: `agent_id`, `target`, `reason`
4. Integrate guard into `before_agent` governance hook

**Acceptance Checks**:
- [ ] Agents prevented from modifying own config/prompts/policies
- [ ] Agents prevented from learning/weight updates during execution
- [ ] Self-modification attempts raise `SelfModificationBlockedError`
- [ ] `self_modification_blocked` trace event emitted

---

### IMP-023: Frozen Configuration Enforcement

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | GOV-POL-SELFMOD-010, GOV-POL-SELFMOD-011, GOV-POL-SELFMOD-012, GOV-POL-SELFMOD-013 |
| **Source BRD** | BRD-GOV-054 |
| **Gap ID** | GAP-023 |
| **Priority** | P1 |
| **Effort** | 1 day |
| **Dependencies** | IMP-022 |

**Target Code Locations**:
- `core/orchestrator/run_lifecycle.py` (MODIFY)
- `core/governance/self_modification_guard.py` (MODIFY)

**Step-by-Step Instructions**:
1. Add `frozen_config: FrozenConfig` to `RunContext` at initialization
2. Create `FrozenConfig` snapshot containing:
   - Policy configurations
   - Agent prompts and system messages
   - Budget and resource limits
   - Tool and agent registry state
3. Mark all snapshot fields as read-only
4. Add validation: compare current config against frozen snapshot
5. Raise `ConfigMutationBlockedError` if mismatch detected during run

**Acceptance Checks**:
- [ ] Policy configurations frozen at run initialization
- [ ] Agent prompts/system messages frozen at run initialization
- [ ] Budget/resource limits frozen (except consumption tracking)
- [ ] Tool/agent registries read-only during run execution

---

### IMP-024: Allowed Runtime Mutations

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | GOV-POL-SELFMOD-020, GOV-POL-SELFMOD-021, GOV-POL-SELFMOD-022 |
| **Source BRD** | BRD-GOV-054 |
| **Gap ID** | GAP-024 |
| **Priority** | P1 |
| **Effort** | 1 day |
| **Dependencies** | IMP-022 |

**Target Code Locations**:
- `core/governance/self_modification_guard.py` (MODIFY)

**Step-by-Step Instructions**:
1. Define allowlist of permitted runtime mutations:
   - Budget consumption counters (via `BudgetEnforcer`)
   - Run artifacts and evidence accumulation
   - Run status and step status transitions (per state machine)
2. Add `is_allowed_mutation(mutation_type: str) -> bool` method
3. Guard checks: if mutation not in allowlist, block; otherwise allow
4. Document each allowed mutation type with rationale

**Acceptance Checks**:
- [ ] Budget consumption counters MAY be updated
- [ ] Run artifacts/evidence MAY be accumulated
- [ ] Run/step status MAY transition per state machine
- [ ] All other mutations blocked

---

### IMP-025: Explainability Core

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | MEM-EXPLAIN-001, MEM-EXPLAIN-002, MEM-EXPLAIN-003, MEM-EXPLAIN-004, MEM-EXPLAIN-005 |
| **Source BRD** | BRD-OPS-060 |
| **Gap ID** | GAP-025 |
| **Priority** | P1 |
| **Effort** | 1.5 days |
| **Dependencies** | IMP-011 |

**Target Code Locations**:
- `core/memory/explainability.py` (NEW)
- `core/memory/base.py` (MODIFY)

**Step-by-Step Instructions**:
1. Ensure all reasoning traces persisted with sufficient detail
2. Create `DecisionPoint` model: `decision_id`, `evidence_refs`, `source_tools`
3. Implement traceability: `decision_id` → `evidence_refs` → source tools
4. Create `explain_run(run_id: str) -> ExplanationArtifact` API
5. `ExplanationArtifact` includes:
   - `reasoning_chain: list[ReasoningStep]`
   - `evidence_used: list[EvidenceRef]`
   - `decisions_made: list[DecisionPoint]`
   - `confidence_evolution: list[tuple[str, float]]` (phase → confidence)

**Acceptance Checks**:
- [ ] All reasoning traces persisted with sufficient detail
- [ ] Each decision point traceable through evidence chain
- [ ] Reasoning chains reconstructable from trace events
- [ ] `explain_run(run_id)` API returns structured artifact
- [ ] Explanation includes required fields

---

### IMP-026: Explanation Artifact Structure

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | MEM-EXPLAIN-ART-001, MEM-EXPLAIN-ART-002, MEM-EXPLAIN-ART-003 |
| **Source BRD** | BRD-OPS-060 |
| **Gap ID** | GAP-026 |
| **Priority** | P1 |
| **Effort** | 1.5 days |
| **Dependencies** | IMP-025, IMP-012 |

**Target Code Locations**:
- `core/contracts/explanation_schema.py` (NEW)
- `core/memory/explainability.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `ExplanationArtifact` Pydantic model:
   - `run_id: str`
   - `created_at: datetime`
   - `reasoning_steps: list[ReasoningStep]`
2. Create `ReasoningStep` model:
   - `step_id: str`
   - `phase: str`
   - `input_summary: str`
   - `output_summary: str`
   - `confidence: float`
   - `evidence_refs: list[EvidenceRef]`
3. Add `terminal_outcome` section:
   - `outcome_reason: OutcomeReason`
   - `outcome_explanation: str`
4. Integrate with `explain_run()` to construct complete artifact

**Acceptance Checks**:
- [ ] `ExplanationArtifact` includes run_id, created_at, reasoning_steps
- [ ] Each reasoning_step has required fields
- [ ] Explanation includes terminal_outcome with reason and explanation

---

### IMP-027: Version Tracking for Reproducibility

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | MEM-REPRO-001, MEM-REPRO-002, MEM-REPRO-003 |
| **Source BRD** | BRD-OPS-061 |
| **Gap ID** | GAP-027 |
| **Priority** | P2 |
| **Effort** | 1 day |
| **Dependencies** | None |

**Target Code Locations**:
- `core/contracts/run_schema.py` (MODIFY)
- `core/orchestrator/run_lifecycle.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `Versions` model:
   - `platform_version: str`
   - `flow_version: str`
   - `python_version: str`
   - `models: dict[str, str]` (model name → version/checkpoint)
2. Add `versions: Versions` to `RunRecord`
3. Populate at run initialization from:
   - `__version__` constant (platform)
   - Flow file hash (flow)
   - `sys.version_info` (Python)
   - Model router metadata (models)

**Acceptance Checks**:
- [ ] `RunRecord` includes `versions` object
- [ ] `versions` includes platform_version, flow_version, python_version
- [ ] `versions` includes model versions dict

---

### IMP-028: Input Hashing for Reproducibility

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | MEM-REPRO-010, MEM-REPRO-011, MEM-REPRO-012 |
| **Source BRD** | BRD-OPS-061 |
| **Gap ID** | GAP-028 |
| **Priority** | P2 |
| **Effort** | 1 day |
| **Dependencies** | IMP-020 |

**Target Code Locations**:
- `core/utils/hashing.py` (NEW or MODIFY)
- `core/contracts/run_schema.py` (MODIFY)
- `core/knowledge/context_pack.py` (MODIFY)

**Step-by-Step Instructions**:
1. Create `compute_hash(data: Any) -> str`:
   - Serialize to canonical JSON (sorted keys, minimal separators)
   - Compute SHA-256
   - Return hex digest
2. Add `input_hash: str` to `RunRecord`
3. Compute and store `input_hash` at run initialization from input payload
4. Add `content_hash: str` to `ContextPack`
5. Compute `content_hash` before freeze

**Acceptance Checks**:
- [ ] All inputs hashed using SHA-256
- [ ] `input_hash` computed from canonical JSON
- [ ] ContextPack includes `content_hash` before freeze

---

### IMP-029: Output Hashing for Reproducibility

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | MEM-REPRO-020, MEM-REPRO-021 |
| **Source BRD** | BRD-OPS-061 |
| **Gap ID** | GAP-029 |
| **Priority** | P2 |
| **Effort** | 1 day |
| **Dependencies** | IMP-012 |

**Target Code Locations**:
- `core/contracts/run_schema.py` (MODIFY)
- `core/orchestrator/run_lifecycle.py` (MODIFY)
- `core/memory/tracing.py` (MODIFY)

**Step-by-Step Instructions**:
1. Add `output_hash: str | None` to `RunRecord`
2. Compute `output_hash` from final output artifact using `compute_hash()`
3. Include `output_hash` in `run_completed` or `run_failed` terminal event
4. Store in `RunRecord` before finalization

**Acceptance Checks**:
- [ ] All outputs hashed using SHA-256
- [ ] `output_hash` recorded in terminal event
- [ ] Hash stored in `RunRecord`

---

### IMP-030: Reproducibility Validation API

| Property | Value |
|----------|-------|
| **Source Tech Spec IDs** | MEM-REPRO-030, MEM-REPRO-031, MEM-REPRO-032 |
| **Source BRD** | BRD-OPS-061 |
| **Gap ID** | GAP-030 |
| **Priority** | P2 |
| **Effort** | 1 day |
| **Dependencies** | IMP-028, IMP-029 |

**Target Code Locations**:
- `core/memory/reproducibility.py` (NEW)

**Step-by-Step Instructions**:
1. Create `validate_reproducibility(run_id: str) -> ReproducibilityResult`:
   - Load `RunRecord` with stored hashes
   - Recompute hashes from stored data
   - Compare stored vs. recomputed
2. Create `ReproducibilityResult` model:
   - `is_reproducible: bool`
   - `discrepancies: list[Discrepancy]`
3. Create `Discrepancy` model:
   - `field: str` (e.g., "input_hash", "output_hash", "content_hash")
   - `expected_hash: str`
   - `actual_hash: str`
4. Expose via API: `GET /api/runs/{run_id}/reproducibility`

**Acceptance Checks**:
- [ ] `validate_reproducibility(run_id)` compares stored vs. recomputed hashes
- [ ] Returns `is_reproducible` boolean
- [ ] Returns `discrepancies` list with required fields

---

## 4. File Inventory

### Files to Create

| File | Purpose | IMP Units |
|------|---------|-----------|
| `core/orchestrator/reasoning_lifecycle.py` | Reasoning lifecycle phases and iteration control | IMP-009, IMP-010 |
| `core/contracts/hypothesis_schema.py` | Hypothesis and HypothesisSet models | IMP-014 |
| `core/knowledge/hypothesis_selector.py` | Hypothesis selection logic | IMP-015 |
| `core/contracts/sufficiency_schema.py` | SufficiencyState model | IMP-016 |
| `core/knowledge/sufficiency_manager.py` | Sufficiency lifecycle management | IMP-017 |
| `core/governance/self_modification_guard.py` | Self-modification prevention | IMP-022, IMP-023, IMP-024 |
| `core/memory/explainability.py` | Explainability API and logic | IMP-025, IMP-026 |
| `core/contracts/explanation_schema.py` | ExplanationArtifact models | IMP-026 |
| `core/memory/reproducibility.py` | Reproducibility validation API | IMP-030 |
| `core/utils/hashing.py` | Canonical JSON hashing utilities | IMP-028, IMP-029 |

### Files to Modify

| File | Changes | IMP Units |
|------|---------|-----------|
| `core/contracts/run_schema.py` | Add terminal outcomes, versions, hashes | IMP-012, IMP-013, IMP-027, IMP-028, IMP-029 |
| `core/contracts/reasoning_schema.py` | Add confidence field to all outputs | IMP-009, IMP-018 |
| `core/orchestrator/engine.py` | Integrate reasoning lifecycle | IMP-009, IMP-010 |
| `core/orchestrator/run_lifecycle.py` | Terminal outcomes, frozen config | IMP-012, IMP-013, IMP-023, IMP-027 |
| `core/orchestrator/plan_executor.py` | ContextPack freeze validation | IMP-021 |
| `core/memory/tracing.py` | New trace event types | IMP-011, IMP-015, IMP-017, IMP-018, IMP-021, IMP-022 |
| `core/memory/base.py` | Persistence APIs for sufficiency, context pack | IMP-017, IMP-021, IMP-025 |
| `core/governance/hooks.py` | Self-modification integration, confidence hooks | IMP-019, IMP-022 |
| `core/governance/budgeting.py` | Reasoning budget integration | IMP-010 |
| `core/knowledge/context_pack.py` | Freeze functionality, hypothesis/sufficiency refs | IMP-014, IMP-016, IMP-020 |
| `core/agents/reasoning_ladder.py` | Confidence propagation | IMP-018 |
| `configs/app.yaml` | Confidence threshold config | IMP-019 |
| `configs/products.yaml` | Per-product threshold config | IMP-019 |

### Test Files to Create

| File | Coverage |
|------|----------|
| `tests/unit/core/orchestrator/test_reasoning_lifecycle.py` | IMP-009, IMP-010, IMP-011 |
| `tests/unit/core/contracts/test_hypothesis_schema.py` | IMP-014 |
| `tests/unit/core/knowledge/test_hypothesis_selector.py` | IMP-015 |
| `tests/unit/core/contracts/test_sufficiency_schema.py` | IMP-016 |
| `tests/unit/core/knowledge/test_sufficiency_manager.py` | IMP-017 |
| `tests/unit/core/contracts/test_terminal_outcomes.py` | IMP-012, IMP-013 |
| `tests/unit/core/governance/test_self_modification_guard.py` | IMP-022, IMP-023, IMP-024 |
| `tests/unit/core/knowledge/test_context_pack_freeze.py` | IMP-020, IMP-021 |
| `tests/unit/core/memory/test_explainability.py` | IMP-025, IMP-026 |
| `tests/unit/core/memory/test_reproducibility.py` | IMP-027, IMP-028, IMP-029, IMP-030 |
| `tests/architecture/test_self_modification_prevention.py` | IMP-022 |

---

## 5. Timeline

### Phase 1: P0 Foundation (Days 1-8)

| Day | IMP Units | Deliverables | Dependencies Met |
|-----|-----------|--------------|------------------|
| 1 | IMP-014 | Hypothesis schema | — |
| 2 | IMP-016 | SufficiencyState schema | — |
| 3 | IMP-012 | Terminal outcome definitions | — |
| 4 | IMP-015 | Hypothesis selection | IMP-014 |
| 5 | IMP-017 | SufficiencyState lifecycle | IMP-016 |
| 6-7 | IMP-009 | Reasoning lifecycle phases | IMP-014, IMP-016 |
| 8 | IMP-010, IMP-013 | Bounded iteration, terminal artifacts | IMP-009, IMP-012 |

### Phase 2: P1 Signals & Guards (Days 9-16)

| Day | IMP Units | Deliverables | Dependencies Met |
|-----|-----------|--------------|------------------|
| 9 | IMP-011 | Reasoning phase events | IMP-009 |
| 10 | IMP-018 | Confidence propagation | IMP-015 |
| 11 | IMP-019 | Confidence thresholds | IMP-018 |
| 12 | IMP-020 | ContextPack freeze | — |
| 13 | IMP-021 | ContextPack freeze lifecycle | IMP-020 |
| 14 | IMP-022 | Self-modification prevention core | — |
| 15 | IMP-023, IMP-024 | Frozen config, allowed mutations | IMP-022 |
| 16 | IMP-025, IMP-026 | Explainability | IMP-011, IMP-012 |

### Phase 3: P2 Reproducibility (Days 17-20)

| Day | IMP Units | Deliverables | Dependencies Met |
|-----|-----------|--------------|------------------|
| 17 | IMP-027 | Version tracking | — |
| 18 | IMP-028 | Input hashing | IMP-020 |
| 19 | IMP-029 | Output hashing | IMP-012 |
| 20 | IMP-030 | Reproducibility validation | IMP-028, IMP-029 |

**Total**: ~20 working days (with parallelization possible in Phase 2)

---

## 6. Validation Criteria

### P0 Validation (Must pass before Phase 2)

- [ ] `Hypothesis` and `HypothesisSet` schemas validate correctly
- [ ] `SufficiencyState` persists and restores correctly
- [ ] Reasoning lifecycle phases execute in order: INTERPRET → PROPOSE → CRITIQUE → RECOMMEND
- [ ] RECOMMEND blocked without passing CRITIQUE
- [ ] Bounded reasoning terminates at max_iterations
- [ ] Terminal outcomes include reason and explanation
- [ ] All terminal artifacts persisted

### P1 Validation (Must pass before Phase 3)

- [ ] Confidence flows through all reasoning phases
- [ ] Confidence thresholds configurable globally and per-product
- [ ] ContextPack freeze prevents modifications
- [ ] Self-modification attempts blocked with exception
- [ ] `explain_run()` returns complete artifact

### P2 Validation (Final acceptance)

- [ ] All inputs/outputs hashed with SHA-256
- [ ] Version information captured in RunRecord
- [ ] `validate_reproducibility()` detects discrepancies

---

## 7. References

- [SD-COVERAGE.md](../05_systemdesign/SD-COVERAGE.md) — Implementation tracking matrix
- [INT-intelligence.md](../03_techspec/INT-intelligence.md) — Intelligence Tech Spec V1.3
- [ORC-orchestration.md](../03_techspec/ORC-orchestration.md) — Orchestration Tech Spec V1.3
- [GOV-governance.md](../03_techspec/GOV-governance.md) — Governance Tech Spec V1.3
- [MEM-memory.md](../03_techspec/MEM-memory.md) — Memory Tech Spec V1.3
