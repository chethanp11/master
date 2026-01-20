# Implementation Outcomes

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  
> **Plan Version**: 1.2  
> **Plan Date**: 2026-01-20  
> **Last Updated**: 2026-01-20  

---

## Summary

- **Platform**: MASTER
- **Plan version/date**: V1.2 / 2026-01-20
- **Completed units**: 22/22 ✅ COMPLETE
- **Test status**: ✅ All green (699 passed)
- **Notes**: Phase 2 (P0 Core Logic) complete, Phase 3 (P1 Signals & Guards) complete, ALL UNITS COMPLETE

---

## Unit Outcomes

### IMP-012 — Explicit Terminal Outcome Definitions

- **Tech Spec IDs**: ORC-TERM-001, ORC-TERM-002, ORC-TERM-003, ORC-TERM-004, ORC-TERM-005
- **BRD IDs**: BRD-AUTO-052
- **Code changes**:
  - **Added**:
    - `tests/unit/core/contracts/test_terminal_outcomes.py` — 14 unit tests for terminal outcome enums and fields
  - **Modified**:
    - `core/contracts/run_schema.py` — Added `TerminalOutcome` enum (5 values), `OutcomeReason` enum (7 values), and 3 fields to `RunRecord` (`terminal_outcome`, `outcome_reason`, `outcome_explanation`)
    - `core/memory/tracing.py` — Added `TraceEventType.RUN_TERMINAL_OUTCOME` event type
    - `core/orchestrator/run_lifecycle.py` — Added `_set_terminal_outcome()` and `_error_code_to_outcome_reason()` helpers, integrated into `complete_run()` and `fail_run()`
    - `core/memory/base.py` — Added `update_run_terminal_outcome()` method to `MemoryBackend` interface
    - `core/memory/router.py` — Added `update_run_terminal_outcome()` delegation method
    - `core/memory/in_memory.py` — Implemented `update_run_terminal_outcome()` for in-memory backend
    - `core/memory/sqlite_backend.py` — Implemented `update_run_terminal_outcome()` for SQLite backend (stores in summary_json for backwards compatibility)
  - **Deleted**: None
- **Behavior implemented**:
  - `TerminalOutcome` enum with 5 values: COMPLETED, FAILED, CANCELLED, ABORTED, PAUSED_INDEFINITE
  - `OutcomeReason` enum with 7 values: SUCCESS, USER_ABORT, GOVERNANCE_BLOCK, BUDGET_EXCEEDED, MAX_ITERATIONS, VALIDATION_FAILED, UNRECOVERABLE_ERROR
  - `RunRecord` now includes optional `terminal_outcome`, `outcome_reason`, and `outcome_explanation` fields
  - `complete_run()` sets terminal outcome to COMPLETED/SUCCESS with human-readable explanation
  - `fail_run()` maps error code to outcome reason and sets terminal outcome to FAILED
  - `run_terminal_outcome` trace event emitted on run completion/failure
  - Terminal outcome persisted to memory via `update_run_terminal_outcome()` API
- **Tests run**:
  - `pytest tests/unit/core/contracts/test_terminal_outcomes.py -v` → 14 passed
  - `pytest tests/unit/core/contracts/ -v` → 31 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 14 passed in 0.05s ==============================`
  - Trace event verification: `TraceEventType.RUN_TERMINAL_OUTCOME.value == "run_terminal_outcome"`
- **Deviations / decisions**:
  - SQLite backend stores terminal outcome fields in `summary_json` rather than dedicated columns for backwards compatibility with existing schema
  - `_error_code_to_outcome_reason()` uses pattern matching on error code strings to map to outcome reasons
- **Remaining follow-ups**: None

---

### IMP-014 — Hypothesis Structure

- **Tech Spec IDs**: INT-HYP-001, INT-HYP-002, INT-HYP-003, INT-HYP-004, INT-HYP-005
- **BRD IDs**: BRD-AUTO-028
- **Code changes**:
  - **Added**:
    - `core/contracts/hypothesis_schema.py` — NEW: EvidenceRef, Hypothesis, HypothesisSet models with HypothesisSetFrozenError exception
    - `tests/unit/core/contracts/test_hypothesis_schema.py` — 29 unit tests for hypothesis schema
  - **Modified**:
    - `core/contracts/context_pack_schema.py` — Added TYPE_CHECKING import for HypothesisSet, added `all_hypotheses: List[HypothesisSet]` field to ContextPack
  - **Deleted**: None
- **Behavior implemented**:
  - `EvidenceRef` model with id, source_type, confidence (required) + uri, tool_name (optional)
  - `Hypothesis` model with id (UUID auto-generated), description, confidence (0.0-1.0), evidence_refs (max 20)
  - `HypothesisSet` model with hypotheses (max 10), created_at timestamp, optional context_hash, frozen flag
  - `freeze()` method on HypothesisSet makes it immutable
  - `HypothesisSetFrozenError` raised when modifying frozen set
  - `add_hypothesis()` method with frozen check and limit enforcement
  - `get_highest_confidence()` and `get_sorted_by_confidence()` utility methods
  - `all_hypotheses` field on ContextPack for audit trail of hypothesis sets
- **Tests run**:
  - `pytest tests/unit/core/contracts/test_hypothesis_schema.py -v` → 29 passed
  - `pytest tests/unit/core/contracts/ -v` → 60 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 29 passed in 0.08s ==============================`
- **Deviations / decisions**:
  - Added `EvidenceRef` model (not explicitly in plan but required by INT-CP-EVI-001/002)
  - Made both Hypothesis and EvidenceRef models frozen (immutable) for data integrity
  - Used TYPE_CHECKING import in context_pack_schema.py to avoid circular imports
- **Remaining follow-ups**: None

---

### IMP-016 — SufficiencyState Structure

- **Tech Spec IDs**: INT-SUFF-001, INT-SUFF-002, INT-SUFF-003, INT-SUFF-004, INT-SUFF-005
- **BRD IDs**: BRD-AUTO-029
- **Code changes**:
  - **Added**:
    - `core/contracts/sufficiency_schema.py` — NEW: Fact, Unknown, Assumption, Gap models with Priority/Importance enums, SufficiencyState container with utility methods
    - `tests/unit/core/contracts/test_sufficiency_schema.py` — 41 unit tests for sufficiency schema
  - **Modified**:
    - `core/contracts/context_pack_schema.py` — Added TYPE_CHECKING import for SufficiencyState, added `sufficiency_state: Optional[SufficiencyState]` field to ContextPack
  - **Deleted**: None
- **Behavior implemented**:
  - `Priority` enum: CRITICAL, HIGH, MEDIUM, LOW
  - `Importance` enum: REQUIRED, RECOMMENDED, NICE_TO_HAVE
  - `Fact` model with id (UUID), statement, source, confidence (0.0-1.0), established_at timestamp
  - `Unknown` model with id (UUID), description, priority, blocking flag, resolution_attempts counter
  - `Assumption` model with id (UUID), statement, confidence (0.0-1.0), basis description, validated flag
  - `Gap` model with id (UUID), description, importance, suggested_actions (max 10), blocking flag
  - `SufficiencyState` model with facts/unknowns/assumptions/gaps lists, each limited to 50 items
  - `is_sufficient()` method returns True when no blocking unknowns/gaps exist
  - `has_blocking_unknowns()` and `has_blocking_gaps()` query methods
  - `get_blocking_gaps()` and `get_blocking_unknowns()` filter methods
  - `get_high_confidence_facts()` method (threshold ≥ 0.8)
  - `get_unvalidated_assumptions()` filter method
  - `get_summary()` returns dict with counts for all entity types
  - `sufficiency_state` field on ContextPack for tracking evidence sufficiency
- **Tests run**:
  - `pytest tests/unit/core/contracts/test_sufficiency_schema.py -v` → 41 passed
  - `pytest tests/unit/core/contracts/ -v` → 101 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 41 passed in 0.09s ==============================`
  - Full suite: `============================== 101 passed in 0.14s ==============================`
- **Deviations / decisions**:
  - Added `established_at` timestamp to Fact model for temporal tracking
  - Added `resolution_attempts` counter to Unknown model for debugging iteration limits
  - Added `validated` flag to Assumption model for explicit validation tracking
  - Made all entity models frozen (immutable) for data integrity
  - Used TYPE_CHECKING import in context_pack_schema.py to avoid circular imports
- **Remaining follow-ups**: None

---

### IMP-013 — Terminal Outcome Artifacts

- **Tech Spec IDs**: ORC-TERM-ART-001, ORC-TERM-ART-002, ORC-TERM-ART-003, ORC-TERM-ART-004
- **BRD IDs**: BRD-AUTO-052
- **Code changes**:
  - **Added**:
    - `tests/unit/core/contracts/test_terminal_artifacts.py` — 37 unit tests for terminal artifact schemas
  - **Modified**:
    - `core/contracts/run_schema.py` — Added `AbortSource` enum, `CompletedArtifact`, `FailedArtifact`, `AbortedArtifact`, `CancelledArtifact`, `PausedIndefiniteArtifact` schemas, and `terminal_artifact` field to `RunRecord`
    - `core/orchestrator/run_lifecycle.py` — Updated imports, modified `_set_terminal_outcome()` to accept `terminal_artifact` parameter, updated `complete_run()` to create and persist `CompletedArtifact`, updated `fail_run()` to create and persist `FailedArtifact` with new optional parameters (stack_trace, failed_step_id, recovery_attempted)
    - `core/memory/base.py` — Added `terminal_artifact` parameter to `update_run_terminal_outcome()` interface
    - `core/memory/router.py` — Added `terminal_artifact` parameter to `update_run_terminal_outcome()` delegation
    - `core/memory/in_memory.py` — Updated `update_run_terminal_outcome()` to persist `terminal_artifact`
    - `core/memory/sqlite_backend.py` — Updated `update_run_terminal_outcome()` to persist `terminal_artifact` in summary_json
  - **Deleted**: None
- **Behavior implemented**:
  - `CompletedArtifact` schema with `final_output` (required), `output_summary`, `metrics`
  - `FailedArtifact` schema with `error_code`, `error_message` (required), `stack_trace`, `failed_step_id`, `recovery_attempted`
  - `AbortedArtifact` schema with `abort_reason`, `abort_source` (required), `aborted_at_step_id`, `partial_output`
  - `CancelledArtifact` schema with `cancel_reason`, `cancelled_by`, `cancelled_at_step_id` (all optional)
  - `PausedIndefiniteArtifact` schema with `pause_reason` (required), `paused_at_step_id`, `resumable`, `resume_instructions`
  - `AbortSource` enum with USER, SYSTEM, GOVERNANCE values
  - `terminal_artifact: Optional[Dict[str, Any]]` field on `RunRecord`
  - `complete_run()` creates `CompletedArtifact` and persists BEFORE run finalization
  - `fail_run()` creates `FailedArtifact` with error details and persists BEFORE run finalization
  - Memory layer accepts and persists `terminal_artifact` to run record
- **Tests run**:
  - `pytest tests/unit/core/contracts/test_terminal_artifacts.py -v` → 37 passed
  - `pytest tests/unit/core/contracts/ -v` → 138 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 37 passed in 0.07s ==============================`
  - Full suite: `============================== 138 passed in 0.15s ==============================`
- **Deviations / decisions**:
  - Added `CancelledArtifact` and `PausedIndefiniteArtifact` for completeness (covers all 5 terminal outcomes)
  - Extended `fail_run()` with optional `stack_trace`, `failed_step_id`, `recovery_attempted` parameters
  - SQLite backend stores `terminal_artifact` in `summary_json` for backwards compatibility
- **Remaining follow-ups**: None

---
### IMP-015 — Hypothesis Selection

- **Tech Spec IDs**: INT-HYP-SEL-001, INT-HYP-SEL-002, INT-HYP-SEL-003, INT-HYP-SEL-004, INT-HYP-SEL-005
- **BRD IDs**: BRD-AUTO-028
- **Code changes**:
  - **Added**:
    - `core/knowledge/hypothesis_selector.py` — NEW: HypothesisRejection, HypothesisSelectionResult, select_hypothesis(), get_top_hypotheses(), calculate_confidence_gap()
    - `tests/unit/core/knowledge/test_hypothesis_selector.py` — 28 unit tests for hypothesis selection
  - **Modified**:
    - `core/memory/tracing.py` — Added `TraceEventType.HYPOTHESIS_SELECTED` and `TraceEventType.HYPOTHESIS_SELECTION_DEFERRED` event types
  - **Deleted**: None
- **Behavior implemented**:
  - `HypothesisRejection` frozen dataclass with hypothesis_id, reason, confidence, rank
  - `HypothesisSelectionResult` dataclass with selected, alternatives, rejections, margin_used, selection_reason, needs_user_input
  - `to_trace_payload()` method for converting result to trace event payload
  - `select_hypothesis(hypothesis_set, confidence_margin=0.1)` core selection function:
    - Returns exactly one Hypothesis or None (INT-HYP-SEL-001)
    - Prefers highest confidence (INT-HYP-SEL-002)
    - If top 2 within margin, returns None with needs_user_input=True (INT-HYP-SEL-003)
    - Records rejection reasons for each non-selected hypothesis (INT-HYP-SEL-004)
  - `get_top_hypotheses(hypothesis_set, n=3)` utility for presenting options
  - `calculate_confidence_gap(hypothesis_set)` utility for diagnostics
  - Trace event types: `hypothesis_selected`, `hypothesis_selection_deferred`
- **Tests run**:
  - `pytest tests/unit/core/knowledge/test_hypothesis_selector.py -v` → 28 passed
  - `pytest tests/unit/core/ -v` → 204 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 28 passed in 0.07s ==============================`
  - Full suite: `============================== 204 passed in 0.23s ==============================`
- **Deviations / decisions**:
  - Added `HYPOTHESIS_SELECTION_DEFERRED` event type for when user input is needed
  - Added `get_top_hypotheses()` and `calculate_confidence_gap()` utility functions
  - Used dataclass instead of Pydantic for HypothesisRejection (simpler for internal use)
- **Remaining follow-ups**: None

---

### IMP-017 — SufficiencyState Lifecycle

- **Tech Spec IDs**: INT-SUFF-LC-001, INT-SUFF-LC-002, INT-SUFF-LC-003, INT-SUFF-LC-004, INT-SUFF-LC-005
- **BRD IDs**: BRD-AUTO-029
- **Code changes**:
  - **Added**:
    - `core/knowledge/sufficiency_manager.py` — NEW: EvidenceItem dataclass, SufficiencyStateDiff dataclass, SufficiencyManager class, create_sufficiency_manager_from_context(), check_sufficiency_for_proceed() utilities
    - `tests/unit/core/knowledge/test_sufficiency_manager.py` — 36 unit tests for SufficiencyManager lifecycle
  - **Modified**:
    - `core/memory/tracing.py` — Added `TraceEventType.SUFFICIENCY_STATE_UPDATED` and `TraceEventType.SUFFICIENCY_STATE_RESTORED` event types
    - `core/memory/base.py` — Added `persist_sufficiency_state()` and `restore_sufficiency_state()` abstract methods to MemoryBackend
    - `core/memory/router.py` — Added delegation for `persist_sufficiency_state()` and `restore_sufficiency_state()`
    - `core/memory/in_memory.py` — Implemented sufficiency state persistence with `_sufficiency_states` dict storage
    - `core/memory/sqlite_backend.py` — Implemented sufficiency state persistence in `summary_json`
  - **Deleted**: None
- **Behavior implemented**:
  - `EvidenceItem` dataclass with source, description, confidence (default 1.0), evidence_ref, metadata
  - `EvidenceItem.to_fact()` converts evidence to a Fact schema instance
  - `SufficiencyStateDiff` dataclass tracking facts_added, unknowns_resolved, gaps_resolved, assumptions_added, new_unknowns, new_gaps, is_now_sufficient, was_sufficient
  - `SufficiencyStateDiff.has_changes()` and `to_trace_payload()` methods
  - `SufficiencyManager` class with:
    - Constructor accepting `run_id` and optional `initial_state` for restoration
    - `state` and `update_count` properties
    - `update_with_evidence(evidence_list)` adds facts and returns diff (INT-SUFF-LC-001)
    - `resolve_unknown(unknown_id, evidence)` resolves unknown with fact (INT-SUFF-LC-001)
    - `resolve_gap(gap_id, evidence)` resolves gap with fact (INT-SUFF-LC-001)
    - `add_unknown(question, importance, blocking)` adds new unknown
    - `add_gap(description, priority, blocking)` adds new gap
    - `add_assumption(description, confidence, evidence_ref)` adds new assumption
    - `is_sufficient()` checks for blocking unknowns AND gaps (INT-SUFF-LC-005)
    - `has_blocking_issues()` and `get_blocking_issues_summary()` diagnostic methods
    - `to_serializable()` for persistence (INT-SUFF-LC-003)
    - `from_serializable()` classmethod for restoration (INT-SUFF-LC-004)
    - `get_summary()` returns comprehensive state summary with update_count
  - `create_sufficiency_manager_from_context(context_data)` utility function
  - `check_sufficiency_for_proceed(manager)` returns (can_proceed, reason) tuple
  - Trace event types: `sufficiency_state_updated`, `sufficiency_state_restored`
  - Memory layer persistence and restoration methods for sufficiency state
- **Tests run**:
  - `pytest tests/unit/core/knowledge/test_sufficiency_manager.py -v` → 36 passed
  - `pytest tests/unit/core/ -v` → 240 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 36 passed in 0.09s ==============================`
  - Full suite: `============================== 240 passed in 0.24s ==============================`
- **Deviations / decisions**:
  - Used `importance: Importance` enum for Unknown (matches schema) vs `priority: Priority` for Gap
  - `is_sufficient()` implemented locally in manager to check BOTH unknowns and gaps (schema's `is_sufficient()` only checks gaps)
  - Used in-place mutation of SufficiencyState (add_fact, add_unknown, etc. return None)
  - Manager requires `run_id` parameter since SufficiencyState has required `run_id` field
- **Remaining follow-ups**: None

---

### IMP-009 — Reasoning Lifecycle Phases

- **Tech Spec IDs**: ORC-REASON-001, ORC-REASON-002, ORC-REASON-003, ORC-REASON-004, ORC-REASON-005
- **BRD IDs**: BRD-AUTO-047
- **Code changes**:
  - **Added**:
    - `core/orchestrator/reasoning_lifecycle.py` — NEW: ReasoningLifecycle class, PhaseTransitionRecord, VALID_TRANSITIONS map, exceptions (InvalidPhaseTransitionError, RecommendWithoutCritiqueError, ReasoningLifecycleError)
    - `tests/unit/core/orchestrator/test_reasoning_lifecycle.py` — 39 unit tests for reasoning lifecycle
  - **Modified**:
    - `core/contracts/reasoning_schema.py` — Added ReasoningPhase enum (4 values), InterpretOutput, ProposeOutput, CritiqueOutput, RecommendOutput frozen Pydantic models
    - `core/memory/tracing.py` — Added `TraceEventType.REASONING_PHASE_STARTED`, `REASONING_PHASE_COMPLETED`, `REASONING_PHASE_TRANSITION` event types
  - **Deleted**: None
- **Behavior implemented**:
  - `ReasoningPhase` enum with 4 phases: INTERPRET, PROPOSE, CRITIQUE, RECOMMEND (ORC-REASON-001)
  - `ReasoningLifecycle` class with:
    - Constructor accepting `run_id` and `max_iterations` (clamped 1-10)
    - `current_phase`, `iteration`, `is_complete`, `critique_completed` properties
    - `can_transition(to_phase)` checks valid transitions
    - `transition_to(phase)` with validation and record creation (ORC-REASON-002)
    - `set_phase_output(output)` validates type matches phase (ORC-REASON-003)
    - `get_phase_output(phase)`, `has_phase_output(phase)` accessors (ORC-REASON-004)
    - `to_serializable()` and `from_serializable()` for persistence/restoration
    - `get_summary()` for diagnostics
  - `VALID_TRANSITIONS` dict defining allowed phase transitions:
    - None → INTERPRET (initial)
    - INTERPRET → PROPOSE
    - PROPOSE → CRITIQUE
    - CRITIQUE → PROPOSE (loop) or RECOMMEND (terminal)
    - RECOMMEND → (terminal, no transitions)
  - `InvalidPhaseTransitionError` raised on invalid transitions
  - `RecommendWithoutCritiqueError` raised when RECOMMEND attempted without CRITIQUE pass (ORC-REASON-005)
  - `PhaseTransitionRecord` frozen dataclass with from_phase, to_phase, timestamp, iteration, transition_id
  - Phase output schemas (InterpretOutput, ProposeOutput, CritiqueOutput, RecommendOutput) with typed fields
  - Trace event types: `reasoning_phase_started`, `reasoning_phase_completed`, `reasoning_phase_transition`
- **Tests run**:
  - `pytest tests/unit/core/orchestrator/test_reasoning_lifecycle.py -v` → 39 passed
  - `pytest tests/unit/core/ -v` → 279 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 39 passed in 0.08s ==============================`
  - Full suite: `============================== 279 passed in 0.27s ==============================`
- **Deviations / decisions**:
  - Made all phase output schemas frozen (immutable) for data integrity
  - Added `PhaseTransitionRecord` dataclass for audit trail
  - Iteration counter increments when looping from CRITIQUE back to PROPOSE
  - `critique_completed` flag set when CRITIQUE phase output is provided (not on transition)
- **Remaining follow-ups**: None

---

### IMP-010 — Bounded Reasoning Iteration

- **Tech Spec IDs**: ORC-REASON-010, ORC-REASON-011, ORC-REASON-012, ORC-REASON-013, ORC-REASON-014
- **BRD IDs**: BRD-AUTO-047
- **Code changes**:
  - **Added**:
    - Extended `tests/unit/core/orchestrator/test_reasoning_lifecycle.py` — 24 additional unit tests for bounded reasoning iteration (63 total)
  - **Modified**:
    - `core/orchestrator/reasoning_lifecycle.py` — Added `ReasoningTerminationReason` enum (6 values), termination properties (`is_terminated`, `termination_reason`, `final_confidence`, `budget_consumed`, `has_reached_max_iterations`), termination methods (`should_terminate()`, `terminate()`, `check_and_terminate_if_needed()`, `consume_iteration_budget()`, `get_termination_payload()`), updated `to_serializable()`, `from_serializable()`, and `get_summary()` to include termination state
    - `core/memory/tracing.py` — Added `TraceEventType.REASONING_TERMINATED` event type
  - **Deleted**: None
- **Behavior implemented**:
  - `ReasoningTerminationReason` enum with 6 values: SUFFICIENT, MAX_ITERATIONS, BUDGET_EXCEEDED, CONFIDENCE_MET, USER_CANCELLED, ERROR
  - `max_reasoning_iterations` configurable (default 3, max 10, min 1) (ORC-REASON-010)
  - `consume_iteration_budget(amount)` tracks budget consumption per iteration (ORC-REASON-011)
  - `iteration` counter increments on CRITIQUE→PROPOSE loop
  - `has_reached_max_iterations` property detects iteration limit (ORC-REASON-012)
  - `should_terminate()` checks: already terminated, max iterations reached, or reasoning complete
  - `terminate(reason, final_confidence)` sets termination state and returns payload (ORC-REASON-013)
  - `check_and_terminate_if_needed(budget_remaining, confidence_threshold, current_confidence)` auto-terminates on conditions:
    - MAX_ITERATIONS: when iteration >= max_iterations
    - BUDGET_EXCEEDED: when budget_remaining <= 0
    - CONFIDENCE_MET: when current_confidence >= confidence_threshold
  - `get_termination_payload()` returns dict with run_id, iteration_count, reason, final_confidence, budget_consumed, phases_completed, terminated_at (ORC-REASON-014)
  - Termination state serialized/restored via `to_serializable()` / `from_serializable()`
  - `get_summary()` includes is_terminated, termination_reason, final_confidence
  - Trace event type: `reasoning_terminated`
- **Tests run**:
  - `pytest tests/unit/core/orchestrator/test_reasoning_lifecycle.py -v` → 63 passed
  - `pytest tests/unit/core/ -v` → 303 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 63 passed in 0.12s ==============================`
  - Full suite: `============================= 303 passed in 0.34s ==============================`
- **Deviations / decisions**:
  - Priority order for auto-termination: MAX_ITERATIONS > BUDGET_EXCEEDED > CONFIDENCE_MET
  - Default final_confidence is None until termination
  - Termination payload includes `terminated_at` ISO timestamp
  - `should_terminate()` also returns True when reasoning is complete (RECOMMEND phase reached and marked complete)
- **Remaining follow-ups**: None

---

### IMP-011 — Reasoning Phase Events

- **Tech Spec IDs**: ORC-REASON-020, ORC-REASON-021, ORC-REASON-022
- **BRD IDs**: BRD-AUTO-047
- **Code changes**:
  - **Added**:
    - Extended `tests/unit/core/orchestrator/test_reasoning_lifecycle.py` — 8 additional unit tests for phase events (71 total)
  - **Modified**:
    - `core/orchestrator/reasoning_lifecycle.py` — Added `get_phase_started_payload()`, `get_phase_completed_payload()`, `get_phase_failed_payload()` methods for trace event payloads
    - `core/memory/tracing.py` — Added `TraceEventType.REASONING_PHASE_FAILED` event type
  - **Deleted**: None
- **Behavior implemented**:
  - `get_phase_started_payload(input_hash)` returns dict with run_id, phase_name, iteration, input_hash, timestamp (ORC-REASON-020)
  - `get_phase_completed_payload(output_hash, confidence)` returns dict with run_id, phase_name, iteration, output_hash, confidence, timestamp (ORC-REASON-021)
  - `get_phase_failed_payload(error_code, reason)` returns dict with run_id, phase_name, iteration, error_code, reason, timestamp (ORC-REASON-022)
  - Trace event type: `reasoning_phase_failed`
  - All payloads include UTC ISO timestamp
  - Payloads track current phase from lifecycle state
- **Tests run**:
  - `pytest tests/unit/core/orchestrator/test_reasoning_lifecycle.py -v` → 71 passed
  - `pytest tests/unit/core/ -v` → 311 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 71 passed in 0.13s ==============================`
  - Full suite: `============================= 311 passed in 0.27s ==============================`
- **Deviations / decisions**:
  - Payload methods are on ReasoningLifecycle class (callers emit events via Tracer)
  - All timestamps are UTC ISO format for consistency
  - input_hash and output_hash are optional to support callers that don't compute hashes
- **Remaining follow-ups**: None

---

### IMP-018 — Confidence as Runtime Signal

- **Tech Spec IDs**: INT-CONF-001, INT-CONF-002, INT-CONF-003, INT-CONF-004, INT-CONF-005
- **BRD IDs**: BRD-AUTO-049
- **Code changes**:
  - **Added**:
    - `core/knowledge/confidence.py` — NEW: ConfidenceThresholdAction enum, ConfidenceResult dataclass, aggregate_confidence(), get_phase_confidence(), check_confidence_threshold(), aggregate_phase_confidences(), get_confidence_below_threshold_payload()
    - `tests/unit/core/knowledge/test_confidence.py` — 28 unit tests for confidence propagation
  - **Modified**:
    - `core/memory/tracing.py` — Added `TraceEventType.CONFIDENCE_BELOW_THRESHOLD` and `TraceEventType.CONFIDENCE_AGGREGATED` event types
  - **Deleted**: None
- **Behavior implemented**:
  - `ConfidenceThresholdAction` enum with 4 values: CONTINUE, ASK_USER, HITL, ABORT (INT-CONF-004)
  - `ConfidenceResult` dataclass with confidence, component_count, weights_used, is_below_threshold, threshold, recommended_action
  - `aggregate_confidence(confidences, weights)` using weighted product formula: prod(c_i ^ w_i) (INT-CONF-003)
  - `get_phase_confidence(output)` extracts confidence from phase outputs (INT-CONF-002)
  - `check_confidence_threshold(confidence, threshold)` evaluates confidence against threshold, recommends action based on severity (INT-CONF-004)
  - `aggregate_phase_confidences(interpret, propose, critique, recommend, weights)` aggregates all phase confidences (INT-CONF-001)
  - `get_confidence_below_threshold_payload()` generates trace event payload (INT-CONF-005)
  - Trace event types: `confidence_below_threshold`, `confidence_aggregated`
  - Confidence clamped to 0.0-1.0 range, weights normalized to sum to 1.0
  - Recommended action thresholds: >=80% of threshold → ASK_USER, >=50% → HITL, <50% → ABORT
- **Tests run**:
  - `pytest tests/unit/core/knowledge/test_confidence.py -v` → 28 passed
  - `pytest tests/unit/core/ -v` → 339 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 28 passed in 0.06s ==============================`
  - Full suite: `============================= 339 passed in 0.34s ==============================`
- **Deviations / decisions**:
  - Added `CONFIDENCE_AGGREGATED` event type for general aggregation tracking
  - Recommended action escalation based on severity (not just binary below/above)
  - All phase output schemas already had confidence field from IMP-009
  - Zero confidence in any component produces zero aggregate
- **Remaining follow-ups**: None

---

### IMP-019 — Confidence Thresholds

- **Tech Spec IDs**: INT-CONF-THR-001, INT-CONF-THR-002, INT-CONF-THR-003, INT-CONF-THR-004, INT-CONF-THR-005
- **BRD IDs**: BRD-AUTO-049
- **Code changes**:
  - **Added**:
    - Extended `core/knowledge/confidence.py` — Added CONFIDENCE_THRESHOLD_FLOOR constant, resolve_confidence_threshold(), get_threshold_violated_payload(), evaluate_confidence_with_threshold()
    - Extended `tests/unit/core/knowledge/test_confidence.py` — 13 additional tests (41 total)
  - **Modified**:
    - `core/config/schema.py` — Added `reasoning_confidence_threshold` field to PoliciesConfig with floor validation (ge=0.5)
    - `core/memory/tracing.py` — Added `TraceEventType.CONFIDENCE_THRESHOLD_VIOLATED` event type
  - **Deleted**: None
- **Behavior implemented**:
  - `CONFIDENCE_THRESHOLD_FLOOR = 0.5` governance floor constant (INT-CONF-THR-005)
  - `reasoning_confidence_threshold` config field with default 0.7, floor 0.5 (INT-CONF-THR-001)
  - `resolve_confidence_threshold(product_id, global_threshold, by_product)` resolves per-product override with floor enforcement (INT-CONF-THR-002, INT-CONF-THR-005)
  - `evaluate_confidence_with_threshold()` combines resolution and evaluation (INT-CONF-THR-003)
  - `get_threshold_violated_payload()` generates trace event payload with actual, threshold, action, product_id (INT-CONF-THR-004)
  - Trace event type: `confidence_threshold_violated`
  - Deterministic comparison: < means below, >= means at or above
  - Pydantic validation enforces floor at config level
- **Tests run**:
  - `pytest tests/unit/core/knowledge/test_confidence.py -v` → 41 passed
  - `pytest tests/unit/core/ -v` → 352 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 41 passed in 0.08s ==============================`
  - Full suite: `============================= 352 passed in 0.30s ==============================`
- **Deviations / decisions**:
  - Used `reasoning_confidence_threshold` key in by_product dict (not `confidence_threshold`)
  - Floor enforcement at both config validation level and resolution function
  - Did not modify configs/app.yaml or configs/products.yaml (schema defines defaults)
- **Remaining follow-ups**: None

---

### IMP-020 — ContextPack Freeze Requirements

- **Tech Spec IDs**: INT-CP-FREEZE-001, INT-CP-FREEZE-002, INT-CP-FREEZE-003
- **BRD IDs**: BRD-AUTO-051
- **Code changes**:
  - **Added**:
    - `tests/unit/core/contracts/test_context_pack_freeze.py` — 21 unit tests for ContextPack freeze
  - **Modified**:
    - `core/contracts/context_pack_schema.py` — Added ContextPackFrozenError exception, freeze fields (frozen, frozen_at, frozen_hash), freeze() method, mutation guards, utility methods (add_evidence, add_assumption, add_hypothesis_set, set_limit, get_evidence_count, get_freeze_payload)
  - **Deleted**: None
- **Behavior implemented**:
  - `ContextPackFrozenError` exception raised when modifying frozen pack (INT-CP-FREEZE-003)
  - `frozen: bool = False` field on ContextPack (INT-CP-FREEZE-001)
  - `frozen_at: Optional[datetime]` timestamp field (INT-CP-FREEZE-002)
  - `frozen_hash: Optional[str]` SHA-256 hash field (INT-CP-FREEZE-002)
  - `freeze()` method:
    - Sets frozen=True
    - Sets frozen_at to current UTC time
    - Computes and sets frozen_hash (SHA-256 of JSON-serialized content)
    - Returns the hash
    - Raises if already frozen
  - `_check_not_frozen()` internal guard method
  - `add_evidence(entry)` with freeze guard
  - `add_assumption(assumption)` with freeze guard
  - `add_hypothesis_set(hypothesis_set)` with freeze guard
  - `set_limit(key, value)` with freeze guard
  - `get_evidence_count()` utility method
  - `get_freeze_payload(run_id)` for trace event payload
  - Hash is deterministic for same content, different for different content
- **Tests run**:
  - `pytest tests/unit/core/contracts/test_context_pack_freeze.py -v` → 21 passed
  - `pytest tests/unit/core/ -v` → 373 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 21 passed in 0.06s ==============================`
  - Full suite: `============================= 373 passed in 0.33s ==============================`
- **Deviations / decisions**:
  - Used `object.__setattr__` in freeze() to bypass Pydantic immutability after freeze
  - Hash excludes freeze fields to ensure consistency
  - Added mutation helper methods (add_evidence, add_assumption, etc.) that didn't exist before
- **Remaining follow-ups**: None

---

### IMP-021 — ContextPack Freeze Lifecycle

- **Tech Spec IDs**: INT-CP-FREEZE-LC-001, INT-CP-FREEZE-LC-002, INT-CP-FREEZE-LC-003
- **BRD IDs**: BRD-AUTO-051
- **Code changes**:
  - **Added**:
    - `tests/unit/core/contracts/test_context_pack_lifecycle.py` — 22 unit tests for ContextPack freeze lifecycle
  - **Modified**:
    - `core/memory/tracing.py` — Added `TraceEventType.CONTEXT_PACK_FROZEN` event type
    - `core/contracts/context_pack_schema.py` — Added `ContextPackNotFrozenError` exception, updated `__all__` exports
    - `core/memory/base.py` — Added abstract methods `persist_context_pack()` and `restore_context_pack()`
    - `core/memory/router.py` — Added `persist_context_pack()` and `restore_context_pack()` delegation methods
    - `core/memory/in_memory.py` — Added `_context_packs` storage dict, implemented `persist_context_pack()` and `restore_context_pack()`
    - `core/memory/sqlite_backend.py` — Implemented `persist_context_pack()` and `restore_context_pack()` storing in summary_json
  - **Deleted**: None
- **Behavior implemented**:
  - `TraceEventType.CONTEXT_PACK_FROZEN` event type for tracing (INT-CP-FREEZE-LC-001)
  - `ContextPackNotFrozenError` exception for blocking execution on unfrozen pack (INT-CP-FREEZE-LC-003)
  - `persist_context_pack(run_id, context_pack)` method on MemoryBackend (INT-CP-FREEZE-LC-002)
  - `restore_context_pack(run_id)` method on MemoryBackend (INT-CP-FREEZE-LC-002)
  - InMemoryBackend stores context packs in `_context_packs` dict with thread-safe locking
  - SQLiteBackend stores context packs in `summary_json` field for backwards compatibility
  - Full freeze → persist → restore roundtrip verified
  - Multiple runs' context packs are isolated
- **Tests run**:
  - `pytest tests/unit/core/contracts/test_context_pack_lifecycle.py -v` → 22 passed
  - `pytest tests/unit/core/ -q` → 395 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 22 passed in 0.06s ==============================`
  - Full suite: `395 passed in 0.32s`
- **Deviations / decisions**:
  - SQLite backend stores frozen context pack in `summary_json` rather than dedicated column for schema compatibility
  - ContextPackNotFrozenError is distinct from ContextPackFrozenError for precise error handling
- **Remaining follow-ups**: None

---

### IMP-022 — Runtime Self-Modification Prevention Core

- **Tech Spec IDs**: GOV-POL-SELFMOD-001, GOV-POL-SELFMOD-002, GOV-POL-SELFMOD-003
- **BRD IDs**: BRD-GOV-054
- **Code changes**:
  - **Added**:
    - `core/governance/self_modification_guard.py` — NEW file with SelfModificationBlockedError, SelfModificationAttempt, SelfModificationGuard class
    - `tests/unit/core/governance/test_self_modification_guard.py` — 35 unit tests for self-modification prevention
  - **Modified**:
    - `core/memory/tracing.py` — Added `TraceEventType.SELF_MODIFICATION_BLOCKED` event type
  - **Deleted**: None
- **Behavior implemented**:
  - `SelfModificationBlockedError` exception with agent_id, target, reason fields
  - `SelfModificationAttempt` dataclass for tracing attempts
  - `SelfModificationGuard` class with:
    - `check_config_modification(agent_id, target_config)` - blocks config modification (GOV-POL-SELFMOD-001)
    - `check_prompt_modification(agent_id, target_prompt)` - blocks prompt modification (GOV-POL-SELFMOD-001)
    - `check_policy_modification(agent_id, target_policy)` - blocks policy modification (GOV-POL-SELFMOD-001)
    - `check_learning_update(agent_id)` - blocks learning during execution (GOV-POL-SELFMOD-002)
    - `get_blocked_payload()` for trace event payload (GOV-POL-SELFMOD-003)
  - Guard can be disabled or have exempt agents for system use
  - `TraceEventType.SELF_MODIFICATION_BLOCKED` event type defined
  - `get_default_guard()` singleton accessor
- **Tests run**:
  - `pytest tests/unit/core/governance/test_self_modification_guard.py -v` → 35 passed
  - `pytest tests/unit/core/ -q` → 430 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 35 passed in 0.06s ==============================`
  - Full suite: `430 passed in 0.34s`
- **Deviations / decisions**:
  - Guard returns SelfModificationAttempt when not blocked (disabled or exempt) for consistent API
  - Exempt agents feature added for system-level agents that need modification capability
- **Remaining follow-ups**: Integration with before_agent governance hook (IMP-023/IMP-024)

---

### IMP-023 — Frozen Configuration Enforcement

- **Tech Spec IDs**: GOV-POL-SELFMOD-010, GOV-POL-SELFMOD-011, GOV-POL-SELFMOD-012, GOV-POL-SELFMOD-013
- **BRD IDs**: BRD-GOV-054
- **Code changes**:
  - **Added**:
    - `tests/unit/core/governance/test_frozen_config.py` — 37 unit tests for frozen configuration enforcement
  - **Modified**:
    - `core/governance/self_modification_guard.py` — Added ConfigMutationBlockedError exception, FrozenConfig class with validate_* methods and check_mutation()
  - **Deleted**: None
- **Behavior implemented**:
  - `ConfigMutationBlockedError` exception with field, expected_hash, actual_hash fields
  - `FrozenConfig` dataclass with:
    - `frozen_at` timestamp
    - Hash snapshots: policies_hash, agents_hash, tools_hash, budget_hash
    - Full snapshots for validation
    - `create()` factory method for initialization
    - `_compute_hash()` deterministic SHA-256 hashing
    - `validate_policies(current)` - validates policy configuration (GOV-POL-SELFMOD-010)
    - `validate_agents(current)` - validates agent config (GOV-POL-SELFMOD-011)
    - `validate_budget(current)` - validates budget limits (GOV-POL-SELFMOD-012)
    - `validate_tools(current)` - validates tool registry (GOV-POL-SELFMOD-013)
    - `check_mutation()` - combined validation, raises ConfigMutationBlockedError
    - `to_dict()` for serialization
  - Tool validation is order-independent (sorted before hashing)
- **Tests run**:
  - `pytest tests/unit/core/governance/test_frozen_config.py -v` → 37 passed
  - `pytest tests/unit/core/ -q` → 467 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 37 passed in 0.07s ==============================`
  - Full suite: `467 passed in 0.42s`
- **Deviations / decisions**:
  - FrozenConfig stores both hashes (for quick validation) and full snapshots (for detailed comparison)
  - to_dict() excludes full snapshots for efficiency in trace events
- **Remaining follow-ups**: Integration with RunContext at run initialization

---

### IMP-024 — Allowed Runtime Mutations

- **Tech Spec IDs**: GOV-POL-SELFMOD-020, GOV-POL-SELFMOD-021, GOV-POL-SELFMOD-022
- **BRD IDs**: BRD-GOV-054
- **Code changes**:
  - **Added**:
    - `tests/unit/core/governance/test_allowed_mutations.py` — 35 unit tests for allowed runtime mutations
  - **Modified**:
    - `core/governance/self_modification_guard.py` — Added AllowedMutationType class, is_allowed_mutation(), get_allowed_mutation_rationale(), check_mutation_allowed()
  - **Deleted**: None
- **Behavior implemented**:
  - `AllowedMutationType` class with 6 allowed mutation types:
    - BUDGET_CONSUMPTION: Budget tracking for governance (GOV-POL-SELFMOD-020)
    - RUN_ARTIFACTS: Artifact accumulation (GOV-POL-SELFMOD-021)
    - EVIDENCE_ACCUMULATION: Evidence gathering (GOV-POL-SELFMOD-021)
    - RUN_STATUS: Run status transitions (GOV-POL-SELFMOD-022)
    - STEP_STATUS: Step status transitions (GOV-POL-SELFMOD-022)
    - TRACE_EVENTS: Observability events
  - `AllowedMutationType.ALL` frozenset for quick membership check
  - `is_allowed_mutation(mutation_type)` returns True/False
  - `get_allowed_mutation_rationale(mutation_type)` returns documented rationale
  - `check_mutation_allowed(mutation_type)` raises SelfModificationBlockedError if not allowed
  - All disallowed mutations are blocked with informative error message
- **Tests run**:
  - `pytest tests/unit/core/governance/test_allowed_mutations.py -v` → 35 passed
  - `pytest tests/unit/core/ -q` → 502 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 35 passed in 0.06s ==============================`
  - Full suite: `502 passed in 0.41s`
- **Deviations / decisions**:
  - Used class with string constants rather than Enum for simpler string comparison
  - All allowed types have documented rationale for audit/compliance
  - Error message includes list of allowed mutations for developer guidance
- **Remaining follow-ups**: None

---

## IMP-025: Explainability Core

- **Started**: 2025-01-20
- **Completed**: 2025-01-20
- **Status**: ✅ Complete
- **Tech Spec ID(s)**: MEM-EXPLAIN-001, MEM-EXPLAIN-002, MEM-EXPLAIN-003, MEM-EXPLAIN-004, MEM-EXPLAIN-005
- **BRD ID(s)**: BRD-OPS-060
- **Files changed**:
  - **Created**:
    - `core/memory/explainability.py` — Explainability module with dataclasses and explain_run() API
    - `tests/unit/core/memory/test_explainability.py` — 34 unit tests for explainability core
  - **Modified**: None
  - **Deleted**: None
- **Behavior implemented**:
  - `EvidenceRef` dataclass: evidence_id, source_tool, confidence, summary
  - `DecisionPoint` dataclass: decision_id, step_id, phase, decision_type, evidence_refs, source_tools
  - `ReasoningStep` dataclass: step_id, phase, input_summary, output_summary, confidence, decisions
  - `ConfidencePoint` dataclass: phase, confidence, timestamp, reason
  - `ExplanationArtifact` dataclass: run_id, reasoning_chain, evidence_used, decisions_made, confidence_evolution, terminal_outcome
  - `create_evidence_ref(evidence_id, source_tool, confidence, summary)` factory function
  - `create_decision_point(decision_id, step_id, phase, decision_type, evidence_refs, source_tools)` factory function
  - `explain_run(run_id, trace_events)` main API returning populated ExplanationArtifact
  - `get_decision_chain(artifact)` returns chronological decision list
  - `trace_evidence_to_decisions(evidence_id, artifact)` returns decisions using given evidence
- **Tests run**:
  - `pytest tests/unit/core/memory/test_explainability.py -v` → 34 passed
  - `pytest tests/unit/core/ -q` → 536 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 34 passed in 0.05s ==============================`
  - Full suite: `536 passed in 0.44s`
- **Deviations / decisions**:
  - Used plain dataclasses instead of Pydantic for simple structure requirements
  - explain_run() builds artifact from trace events with type-based parsing
  - Phase detection uses step_id pattern matching (retrieval_, reasoning_, etc.)
  - Confidence evolution sorted by timestamp for chronological ordering
- **Remaining follow-ups**: None

---

## IMP-026: Explanation Artifact Structure

- **Started**: 2025-01-20
- **Completed**: 2025-01-20
- **Status**: ✅ Complete
- **Tech Spec ID(s)**: MEM-EXPLAIN-ART-001, MEM-EXPLAIN-ART-002, MEM-EXPLAIN-ART-003
- **BRD ID(s)**: BRD-OPS-060
- **Files changed**:
  - **Created**:
    - `core/contracts/explanation_schema.py` — Pydantic models for explanation artifacts
    - `tests/unit/core/contracts/test_explanation_artifact.py` — 43 unit tests for IMP-026
  - **Modified**:
    - `core/memory/explainability.py` — Added to_pydantic_artifact(), explain_run_pydantic(), updated docstring
  - **Deleted**: None
- **Behavior implemented**:
  - `EvidenceRefModel` Pydantic model with validation (confidence 0-1)
  - `DecisionPointModel` Pydantic model with evidence refs and timestamps
  - `ReasoningStepModel` Pydantic model with step_id, phase, input/output summary, confidence, evidence_refs
  - `ConfidencePointModel` Pydantic model for confidence evolution tracking
  - `TerminalOutcomeSection` Pydantic model with outcome, outcome_reason (OutcomeReason enum), outcome_explanation
  - `ExplanationArtifactModel` Pydantic model with run_id, created_at, reasoning_steps, evidence_used, decisions_made, confidence_evolution, terminal_outcome
  - `get_decision_chain()` method returns chronological decisions
  - `trace_evidence_to_decisions()` method for evidence traceability
  - `dataclass_to_pydantic_*` conversion functions for interoperability
  - `to_pydantic_artifact()` convenience function in explainability.py
  - `explain_run_pydantic()` API returning Pydantic model directly
- **Tests run**:
  - `pytest tests/unit/core/contracts/test_explanation_artifact.py -v` → 43 passed
  - `pytest tests/unit/core/ -q` → 579 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 43 passed in 0.09s ==============================`
  - Full suite: `579 passed in 0.46s`
- **Deviations / decisions**:
  - Used extra="forbid" in all Pydantic models for strict validation
  - Created separate TerminalOutcomeSection model for terminal outcome structure
  - Reused existing OutcomeReason enum from run_schema.py
  - Conversion functions handle both ISO strings and datetime objects for timestamps
- **Remaining follow-ups**: None

---

## IMP-027: Version Tracking for Reproducibility

- **Started**: 2025-01-20
- **Completed**: 2025-01-20
- **Status**: ✅ Complete
- **Tech Spec ID(s)**: MEM-REPRO-001, MEM-REPRO-002, MEM-REPRO-003
- **BRD ID(s)**: BRD-OPS-061
- **Files changed**:
  - **Created**:
    - `tests/unit/core/contracts/test_version_tracking.py` — 28 unit tests for version tracking
  - **Modified**:
    - `core/contracts/run_schema.py` — Added Versions model, added versions field to RunRecord
    - `core/orchestrator/run_lifecycle.py` — Modified start_run() to capture and populate versions
  - **Deleted**: None
- **Behavior implemented**:
  - `Versions` Pydantic model with:
    - `platform_version: str` (default "1.0.0")
    - `flow_version: str` (default "unknown")
    - `python_version: str` (from sys.version_info)
    - `models: Dict[str, str]` (model name → version)
  - `Versions.capture()` factory method that:
    - Captures Python version from sys.version_info
    - Accepts platform_version, flow_version, models as parameters
  - `RunRecord.versions` optional field for version tracking
  - `start_run()` updated with:
    - `platform_version` and `model_versions` parameters
    - Auto-capture of flow_def.version attribute
    - Auto-population of versions in RunRecord
- **Tests run**:
  - `pytest tests/unit/core/contracts/test_version_tracking.py -v` → 28 passed
  - `pytest tests/unit/core/ -q` → 607 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 28 passed in 0.06s ==============================`
  - Full suite: `607 passed in 0.49s`
- **Deviations / decisions**:
  - Used Versions.capture() factory for Python version capture at runtime
  - Flow version extracted from flow_def.version attribute with 'unknown' fallback
  - Version capture at start_run time ensures consistency with run initiation
- **Remaining follow-ups**: None

---

## IMP-028: Input Hashing for Reproducibility

- **Started**: 2025-01-20
- **Completed**: 2025-01-20
- **Status**: ✅ Complete
- **Tech Spec ID(s)**: MEM-REPRO-010, MEM-REPRO-011, MEM-REPRO-012
- **BRD ID(s)**: BRD-OPS-061
- **Files changed**:
  - **Created**:
    - `core/utils/hashing.py` — Canonical JSON serialization and SHA-256 hashing utilities
    - `tests/unit/core/utils/test_input_hashing.py` — 39 unit tests for input hashing
  - **Modified**:
    - `core/contracts/run_schema.py` — Added input_hash field to RunRecord
    - `core/contracts/context_pack_schema.py` — Added content_hash field to ContextPack, updated freeze() method
    - `core/orchestrator/run_lifecycle.py` — Modified start_run() to compute and store input_hash
  - **Deleted**: None
- **Behavior implemented**:
  - `CanonicalJSONEncoder` class for consistent JSON serialization:
    - datetime/date → ISO format strings
    - sets → sorted lists
    - Pydantic models → model_dump()
  - `compute_hash(data, algorithm="sha256")` function:
    - Canonical JSON with sorted keys, minimal separators
    - SHA-256 (default), SHA-512, MD5 supported
    - Returns hex digest
  - `compute_input_hash(payload)` convenience function for run inputs
  - `compute_output_hash(output)` convenience function for run outputs
  - `verify_hash(data, expected_hash)` for hash verification
  - `RunRecord.input_hash` field for run input reproducibility
  - `ContextPack.content_hash` field set during freeze()
  - `start_run()` automatically computes and stores input_hash
- **Tests run**:
  - `pytest tests/unit/core/utils/test_input_hashing.py -v` → 39 passed
  - `pytest tests/unit/core/ -q` → 646 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 39 passed in 0.09s ==============================`
  - Full suite: `646 passed in 0.51s`
- **Deviations / decisions**:
  - Canonical JSON uses sorted keys, minimal separators, ASCII-safe encoding
  - Hash computed at start_run() for consistent timing with run initialization
  - content_hash set same as frozen_hash for consistency (both computed at freeze time)
- **Remaining follow-ups**: None

---

## IMP-029: Output Hashing for Reproducibility

- **Started**: 2025-01-20
- **Completed**: 2025-01-20
- **Status**: ✅ Complete
- **Tech Spec ID(s)**: MEM-REPRO-020, MEM-REPRO-021
- **BRD ID(s)**: BRD-OPS-061
- **Files changed**:
  - **Created**:
    - `tests/unit/core/contracts/test_output_hashing.py` — 16 unit tests for output hashing
  - **Modified**:
    - `core/contracts/run_schema.py` — Added output_hash field to RunRecord
    - `core/orchestrator/run_lifecycle.py` — Modified complete_run() and fail_run() to compute and store output_hash
  - **Deleted**: None
- **Behavior implemented**:
  - `RunRecord.output_hash` field for run output reproducibility
  - `complete_run()` computes output_hash from final output using compute_output_hash()
  - `complete_run()` includes output_hash in run_completed event payload
  - `complete_run()` stores output_hash via memory.update_run_status()
  - `fail_run()` computes output_hash from error_code and error_message
  - `fail_run()` includes output_hash in run_failed event payload
  - `fail_run()` stores output_hash via memory.update_run_status()
- **Tests run**:
  - `pytest tests/unit/core/contracts/test_output_hashing.py -v` → 16 passed
  - `pytest tests/unit/core/ -q` → 662 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 16 passed in 0.06s ==============================`
  - Full suite: `662 passed in 0.52s`
- **Deviations / decisions**:
  - fail_run() hashes error_code and error_message as the output artifact
  - Output hash computed and stored separately from terminal artifact for flexibility
  - Hash included in both event payload and run record for dual traceability
- **Remaining follow-ups**: None

---

## IMP-030: Reproducibility Validation API

- **Started**: 2025-01-20
- **Completed**: 2025-01-20
- **Status**: ✅ Complete
- **Tech Spec ID(s)**: MEM-REPRO-030, MEM-REPRO-031, MEM-REPRO-032
- **BRD ID(s)**: BRD-OPS-061
- **Files changed**:
  - **Created**:
    - `core/memory/reproducibility.py` — Reproducibility validation API with Discrepancy and ReproducibilityResult dataclasses
    - `tests/unit/core/memory/test_reproducibility.py` — 37 unit tests for reproducibility validation
  - **Modified**: None
  - **Deleted**: None
- **Behavior implemented**:
  - `Discrepancy` dataclass with field, expected_hash, actual_hash, details fields
  - `ReproducibilityResult` dataclass with run_id, is_reproducible, discrepancies, verified_fields, skipped_fields, error
  - `validate_reproducibility(run_id)` compares stored vs. recomputed hashes for input and output
  - Returns `is_reproducible` boolean indicating whether all hashes match
  - Returns `discrepancies` list with required fields (field, expected_hash, actual_hash)
  - `validate_input_hash()` helper validates input hash
  - `validate_output_hash()` helper validates output hash
  - `validate_version_consistency()` helper checks version validity
  - `create_reproducibility_snapshot()` utility for capturing reproducibility state
  - Supports loading run from memory or accepting run_record directly
  - Handles missing hashes by marking fields as skipped
- **Tests run**:
  - `pytest tests/unit/core/memory/test_reproducibility.py -v` → 37 passed
  - `pytest tests/unit/core/ -q` → 699 passed (no regressions)
- **Evidence**:
  - Test output: `============================== 37 passed in 0.08s ==============================`
  - Full suite: `699 passed in 0.60s`
- **Deviations / decisions**:
  - API designed to work with either memory interface or direct run_record for flexibility
  - Runs without any hashes are marked as not reproducible with skipped_fields
  - Version consistency check flags "unknown" platform version as discrepancy
  - Summary method provides human-readable status message
- **Remaining follow-ups**: None

---