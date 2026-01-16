# Orchestration Engine Technical Specification

> **Document ID**: ORC  
> **Version**: 1.1.0  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-13

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial release |
| 1.1.0 | 2026-01-13 | Added §3.7 Versioning & Reproducibility, §3.8 Explicit Non-Goals, updated BRD mappings |

---

## 1. Overview

The orchestration engine is responsible for executing flows—directed sequences of steps that 
invoke agents, tools, and control structures. This specification defines the requirements for 
run lifecycle management, step execution, pause/resume mechanics, and control flow evaluation.

### 1.1 Implementation References

| Component | File | Lines |
|-----------|------|-------|
| Main Engine | `core/orchestrator/engine.py` | Full file |
| Run Lifecycle | `core/orchestrator/run_lifecycle.py` | Full file |
| Step Executor | `core/orchestrator/step_executor.py` | Full file |
| Flow Loader | `core/orchestrator/flow_loader.py` | Full file |
| Branching | `core/orchestrator/branching.py` | Full file |
| Looping | `core/orchestrator/looping.py` | Full file |
| Plan Executor | `core/orchestrator/plan_executor.py` | Full file |
| Loop Executor | `core/orchestrator/loop_executor.py` | Full file |
| User Input Handler | `core/orchestrator/user_input_handler.py` | Full file |
| HITL Service | `core/orchestrator/hitl.py` | Full file |
| Templating | `core/orchestrator/templating.py` | Full file |
| Context Objects | `core/orchestrator/context.py` | Full file |
| State Helpers | `core/orchestrator/state.py` | Full file |

---

## 2. Run Lifecycle Requirements

### 2.1 Run Status State Machine

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-RUN-001** | [V1] The orchestrator MUST implement a finite state machine with states: `RUNNING`, `PAUSED_WAITING_FOR_USER`, `PENDING_HUMAN`, `COMPLETED`, `FAILED`, `CANCELLED` | MUST |
| **ORC-RUN-002** | [V1] Valid state transitions MUST be enforced: | MUST |
| | • `RUNNING` → `PAUSED_WAITING_FOR_USER`, `PENDING_HUMAN`, `COMPLETED`, `FAILED` | |
| | • `PAUSED_WAITING_FOR_USER` → `RUNNING`, `CANCELLED` | |
| | • `PENDING_HUMAN` → `RUNNING`, `CANCELLED` | |
| | • `COMPLETED` → (terminal, no transitions) | |
| | • `FAILED` → (terminal, no transitions) | |
| **ORC-RUN-003** | [V1] State transitions MUST be validated via `can_transition()` before execution; invalid transitions MUST raise `InvalidTransitionError` | MUST |
| **ORC-RUN-004** | [V1] Each state transition MUST emit a `run_state_transition` trace event with `from`, `to`, and `reason` payload fields | MUST |

**Implementation**: `core/orchestrator/state.py`, `core/contracts/run_schema.py`

### 2.2 Run Initialization

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-RUN-010** | [V1] Run initialization MUST generate a unique run ID with format `run_{timestamp}_{uuid8}` | MUST |
| **ORC-RUN-011** | [V1] Run initialization MUST create a `RunRecord` with status `RUNNING` | MUST |
| **ORC-RUN-012** | [V1] Run initialization MUST pre-create `StepRecord` entries for all steps in the flow | MUST |
| **ORC-RUN-013** | [V1] Run initialization MUST initialize metadata counters: `steps_executed=0`, `tool_calls=0`, `tokens_used=0`, `started_at` | MUST |
| **ORC-RUN-014** | [V1] Run initialization MUST clear staging area (output only, preserve input) | MUST |
| **ORC-RUN-015** | [V1] Run initialization MUST emit `run_started` trace event | MUST |

**Implementation**: `core/orchestrator/run_lifecycle.py`

### 2.3 Run Input Validation

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-RUN-020** | [V1] Payload size MUST be validated against `max_payload_bytes`; runs exceeding the limit MUST be rejected with code `payload_limit_exceeded` | MUST |
| **ORC-RUN-021** | [V1] Flow step count MUST be validated against `max_steps`; flows exceeding the limit MUST be rejected with code `max_steps_exceeded` | MUST |

**Implementation**: `core/orchestrator/engine.py`, `core/governance/hooks.py`

---

## 3. Semantic Interpretation Phase Requirements

### 3.1 Mandatory Semantic Phase

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-SEM-001** | [V1] The orchestrator MUST execute a `semantic_interpretation` phase before planning/execution for every run | MUST |
| **ORC-SEM-002** | [V1] The semantic phase MAY be explicitly skipped only if `skip_semantic_interpretation: true` is set in flow config | MAY |
| **ORC-SEM-003** | [V1] The semantic phase MUST produce a `SemanticEnvelope` result before any step execution | MUST |
| **ORC-SEM-004** | [V1] If the semantic phase fails, the run MUST transition to `FAILED` with code `semantic_interpretation_failed` | MUST |

**Implementation**: `core/orchestrator/engine.py`, `core/orchestrator/semantic_phase.py`

### 3.2 SemanticEnvelope Contract

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-SEM-010** | [V1] `SemanticEnvelope` MUST be a Pydantic model in `core/contracts/semantic_schema.py` | MUST |
| **ORC-SEM-011** | [V1] `SemanticEnvelope` MUST include: `raw_input` (original user input) | MUST |
| **ORC-SEM-012** | [V1] `SemanticEnvelope` MUST include: `normalized_input` (cleaned/standardized input) | MUST |
| **ORC-SEM-013** | [V1] `SemanticEnvelope` MUST include: `product_id` (resolved product identifier) | MUST |
| **ORC-SEM-014** | [V1] `SemanticEnvelope` MUST include: `intent_type` (classified intent category) | MUST |
| **ORC-SEM-015** | [V1] `SemanticEnvelope` MUST include: `entities` (list of extracted entities with type, value, confidence) | MUST |
| **ORC-SEM-016** | [V1] `SemanticEnvelope` MUST include: `constraints` (dict of extracted constraints/filters) | MUST |
| **ORC-SEM-017** | [V1] `SemanticEnvelope` MUST include: `confidence` (float 0.0-1.0) | MUST |
| **ORC-SEM-018** | [V1] `SemanticEnvelope` MUST include: `ambiguities` (list of unresolved ambiguities) | MUST |
| **ORC-SEM-019** | [V1] `SemanticEnvelope` MUST include: `proposed_next_action` (NextAction enum value) | MUST |

**Implementation**: `core/contracts/semantic_schema.py`

### 3.3 NextAction Enum

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-SEM-020** | [V1] `NextAction` enum MUST define: `CONTINUE`, `ASK_USER`, `ABORT` | MUST |
| **ORC-SEM-021** | [V1] `NextAction` enum MAY define: `NEEDS_APPROVAL` for HITL gate integration | MAY |
| **ORC-SEM-022** | [V1] `NextAction` MUST be enforced by the engine before step execution proceeds | MUST |

**Implementation**: `core/contracts/semantic_schema.py`

### 3.4 Orchestrator Stop/Pause Mechanism

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-SEM-STOP-001** | [V1] If `NextAction=ASK_USER`, execution MUST NOT proceed to planning/steps | MUST |
| **ORC-SEM-STOP-002** | [V1] If `NextAction=ASK_USER`, run MUST transition to `PAUSED_WAITING_FOR_USER` | MUST |
| **ORC-SEM-STOP-003** | [V1] If `NextAction=ASK_USER`, a structured response MUST be returned with `clarifying_question` and `ambiguities` | MUST |
| **ORC-SEM-STOP-004** | [V1] If `NextAction=ABORT`, run MUST transition to `FAILED` with code `semantic_abort` | MUST |
| **ORC-SEM-STOP-005** | [V1] If `NextAction=ABORT`, a structured error MUST include reason and ambiguities | MUST |
| **ORC-SEM-STOP-006** | [V1] If `NextAction=NEEDS_APPROVAL`, run MUST transition to `PENDING_HUMAN` with semantic context | MAY |
| **ORC-SEM-STOP-007** | [V1] Only `NextAction=CONTINUE` permits step execution to proceed | MUST |

**Implementation**: `core/orchestrator/engine.py`, `core/orchestrator/semantic_phase.py`

### 3.5 Deterministic Resolution Rules

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-SEM-030** | [V1] Core MUST apply domain-agnostic normalization: whitespace trimming, case normalization | MUST |
| **ORC-SEM-031** | [V1] Core MUST apply entity deduplication (same type+value → single entity) | MUST |
| **ORC-SEM-032** | [V1] Core MUST merge overlapping constraints deterministically | MUST |
| **ORC-SEM-033** | [V1] Core MUST apply stable ordering to entities and constraints | MUST |
| **ORC-SEM-034** | [V1] Core MUST apply schema coercions (string→int, string→date where schema declares type) | MUST |
| **ORC-SEM-035** | [V1] Core MUST NOT contain domain-specific rules (e.g., "trend requires time axis") | MUST |

**Implementation**: `core/orchestrator/semantic_phase.py`

### 3.6 Semantic Trace Events

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-SEM-040** | [V1] Semantic phase MUST emit `semantic_interpretation_started` event at phase start | MUST |
| **ORC-SEM-041** | [V1] Semantic phase MUST emit `semantic_interpretation_completed` event with: envelope_hash, confidence, ambiguity_count, next_action | MUST |
| **ORC-SEM-042** | [V1] If validation fails, MUST emit `semantic_validation_completed` event with: is_valid, missing_fields, violations | MUST |
| **ORC-SEM-043** | [V1] If stop is issued, MUST emit `semantic_stop_issued` event with: next_action, question (if ASK_USER), reason (if ABORT) | MUST |

**Implementation**: `core/memory/tracing.py`, `core/orchestrator/semantic_phase.py`

### 2.4 Run Completion

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-RUN-030** | [V1] Run completion MUST transition status to `COMPLETED` | MUST |
| **ORC-RUN-031** | [V1] Run completion MUST persist normalized run output | MUST |
| **ORC-RUN-032** | [V1] Run completion MUST emit `run_completed` trace event | MUST |
| **ORC-RUN-033** | [V1] Run completion MUST export reasoning artifact (Markdown file) | MUST |
| **ORC-RUN-034** | [V1] Run completion MUST write final response to observability storage | MUST |
| **ORC-RUN-035** | [V1] Runs completing without output data MUST transition to `FAILED` with error code `missing_output` | MUST |
| **ORC-RUN-036** | [V1] Run output MUST pass governance validation via `after_run`; denied output MUST fail the run with reason `output_denied` | MUST |

**Implementation**: `core/orchestrator/run_lifecycle.py`

### 2.5 Run Failure

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-RUN-040** | [V1] Run failure MUST transition status to `FAILED` | MUST |
| **ORC-RUN-041** | [V1] Run failure MUST record error code and message in summary | MUST |
| **ORC-RUN-042** | [V1] Run failure MUST emit `run_failed` trace event | MUST |
| **ORC-RUN-043** | [V1] Run failure MUST persist run output with error information | MUST |

**Implementation**: `core/orchestrator/run_lifecycle.py`

---

## 3. Step Execution Requirements

### 3.1 Step Types

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-STEP-001** | [V1] The orchestrator MUST support these step types: | MUST |

| Type | Description | V1 Status |
|------|-------------|-----------|
| `agent` | Execute an agent | ✅ Implemented |
| `tool` | Execute a single tool | ✅ Implemented |
| `tool_batch` | Execute multiple read-only tools | ✅ Implemented |
| `human_approval` | Pause for HITL approval | ✅ Implemented |
| `user_input` | Pause for user input | ✅ Implemented |
| `propose_plan` | Propose an action plan | ✅ Implemented |
| `plan_proposal` | New-style plan proposal | ✅ Implemented |
| `plan_gate` | Evaluate plan against governance | ✅ Implemented |
| `plan_execute` | Execute approved plan | ✅ Implemented |
| `branch` | Conditional branching | ✅ Implemented |
| `loop` | Bounded loop execution | ✅ Implemented |
| `subflow` | Nested flow execution | ❌ Deferred to V2 |

### 3.2 Step Validation

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-STEP-010** | [V1] `agent` steps MUST have `agent` field | MUST |
| **ORC-STEP-011** | [V1] `tool` steps MUST have `tool` field | MUST |
| **ORC-STEP-012** | [V1] `tool_batch` steps MUST have `tools` field | MUST |
| **ORC-STEP-013** | [V1] `branch` steps MUST have `if` OR `condition` | MUST |
| **ORC-STEP-014** | [V1] `branch` steps MUST have `then`, `condition`, and `else` fields | MUST |
| **ORC-STEP-015** | [V1] `loop` steps MUST have `iteration_step`, `stop_condition`, and `max_iters` | MUST |
| **ORC-STEP-016** | [V1] `tool_batch` steps MUST have `tools` list with 1-20 items | MUST |
| **ORC-STEP-017** | [V1] `user_input` steps MUST have valid `request` params OR `prompt` | MUST |

**Implementation**: `core/contracts/flow_schema.py`, `core/orchestrator/flow_loader.py`

### 3.3 Step Lifecycle

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-STEP-020** | [V1] Each step execution MUST create `StepRecord` with status `STARTED` and `started_at` timestamp | MUST |
| **ORC-STEP-021** | [V1] Each step execution MUST call `before_step` for permission check | MUST |
| **ORC-STEP-022** | [V1] Each step execution MUST emit `step_started` trace event | MUST |
| **ORC-STEP-023** | [V1] Each step execution MUST execute step logic based on type | MUST |
| **ORC-STEP-024** | [V1] Each step execution MUST update `StepRecord` with `COMPLETED`/`FAILED` status and `finished_at` timestamp | MUST |
| **ORC-STEP-025** | [V1] Each step execution MUST emit `step_completed` or `step_failed` trace event | MUST |
| **ORC-STEP-026** | [V1] If `before_step` denies execution, the step MUST fail with `before_step_denied` event and run MUST transition to `FAILED` | MUST |

**Implementation**: `core/orchestrator/step_executor.py`

### 3.4 Step Retry Policy

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-STEP-030** | [V1] Tool steps MAY have a `retry_policy` with: | MAY |
| | • `max_attempts`: 1-10 attempts (default: 1) | |
| | • `delay_seconds`: 0-60 seconds delay (default: 0) | |
| | • `retryable_codes`: Optional list of error codes eligible for retry | |
| **ORC-STEP-031** | [V1] Retry decisions MUST be evaluated via `ErrorPolicy`; failed attempts MUST emit `tool_call_attempt_failed` and `tool_call_retry_scheduled` events | MUST |

**Implementation**: `core/orchestrator/error_policy.py`

---

## 4. Pause/Resume Requirements

### 4.1 User Input Pause

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-PAUSE-001** | [V1] `user_input` steps MUST render params with template context | MUST |
| **ORC-PAUSE-002** | [V1] `user_input` steps MUST build `UserInputRequest` from request | MUST |
| **ORC-PAUSE-003** | [V1] `user_input` steps MUST create `ApprovalRecord` with type `INPUT` | MUST |
| **ORC-PAUSE-004** | [V1] `user_input` steps MUST update step status to `PAUSED` | MUST |
| **ORC-PAUSE-005** | [V1] `user_input` steps MUST transition run to `PAUSED_WAITING_FOR_USER` | MUST |
| **ORC-PAUSE-006** | [V1] `user_input` steps MUST emit `pending_user_input`, `user_input_requested`, `run_paused` events | MUST |
| **ORC-PAUSE-007** | [V1] User input steps with `optional=true` MUST skip pause and continue with empty values | MUST |

**Implementation**: `core/orchestrator/user_input_handler.py`

### 4.2 Human Approval Pause

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-PAUSE-010** | [V1] `human_approval` steps MUST build approval payload with context | MUST |
| **ORC-PAUSE-011** | [V1] `human_approval` steps MUST create `ApprovalRecord` via `HITLService` | MUST |
| **ORC-PAUSE-012** | [V1] `human_approval` steps MUST create `ApprovalRecord` with type `APPROVAL` | MUST |
| **ORC-PAUSE-013** | [V1] `human_approval` steps MUST update step status to `PAUSED` | MUST |
| **ORC-PAUSE-014** | [V1] `human_approval` steps MUST transition run to `PENDING_HUMAN` | MUST |
| **ORC-PAUSE-015** | [V1] `human_approval` steps MUST emit `pending_human`, `pending_approval`, `run_pending_human` events | MUST |

**Implementation**: `core/orchestrator/hitl.py`

### 4.3 Resume from User Input

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-RESUME-001** | [V1] Resume from user input MUST validate run is in `PAUSED_WAITING_FOR_USER` or `PENDING_USER_INPUT` status | MUST |
| **ORC-RESUME-002** | [V1] Resume from user input MUST validate response matches pending request (`run_id`, `form_id`) | MUST |
| **ORC-RESUME-003** | [V1] Resume from user input MUST run governance check via `before_user_input` | MUST |
| **ORC-RESUME-004** | [V1] Resume from user input MUST validate input values against request schema | MUST |
| **ORC-RESUME-005** | [V1] Resume from user input MUST merge defaults with provided values | MUST |
| **ORC-RESUME-006** | [V1] Resume from user input MUST store user input artifacts | MUST |
| **ORC-RESUME-007** | [V1] Resume from user input MUST update step status to `COMPLETED` | MUST |
| **ORC-RESUME-008** | [V1] Resume from user input MUST transition run to `RUNNING` | MUST |
| **ORC-RESUME-009** | [V1] Resume from user input MUST resume execution from next step | MUST |
| **ORC-RESUME-010** | [V1] User input validation MUST support: free text mode, choice input mode, question set mode | MUST |

**Implementation**: `core/orchestrator/user_input_handler.py`

### 4.4 Resume from Approval

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-RESUME-020** | [V1] Resume from approval MUST validate run is in `PENDING_HUMAN` status | MUST |
| **ORC-RESUME-021** | [V1] Resume from approval MUST validate approval payload contains `approved` field | MUST |
| **ORC-RESUME-022** | [V1] Resume from approval MUST resolve approval via `HITLService` | MUST |
| **ORC-RESUME-023** | [V1] If rejected: transition run to `FAILED` (unless replan enabled) | MUST |
| **ORC-RESUME-024** | [V1] If approved: transition run to `RUNNING` and continue | MUST |
| **ORC-RESUME-025** | [V1] Resume MUST emit `run_resumed` or `run_rejected` events | MUST |
| **ORC-RESUME-026** | [V1] Replan after rejection MUST require rejection comment | MUST |
| **ORC-RESUME-027** | [V1] Replan MUST limit to 2 rejections before permanent failure | MUST |
| **ORC-RESUME-028** | [V1] Replan MUST re-execute planning step with previous context | MUST |

**Implementation**: `core/orchestrator/hitl.py`

---

## 5. Branch Evaluation Requirements

### 5.1 Condition Expressions

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-BRANCH-001** | [V1] Branch conditions MUST support path-based conditions with operators: `==`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `contains`, `not_in` | MUST |
| **ORC-BRANCH-002** | [V1] Branch conditions MUST support composite conditions with `all` (AND) and `any` (OR) groups | MUST |
| **ORC-BRANCH-003** | [V1] Branch conditions MUST have maximum 20 condition nodes per expression | MUST |
| **ORC-BRANCH-004** | [V1] Condition paths MUST resolve: `steps.<step_id>.output.<field>` and `artifacts.<key>` | MUST |

**Implementation**: `core/orchestrator/branching.py`

### 5.2 Branch Execution

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-BRANCH-010** | [V1] Branch evaluation MUST evaluate condition deterministically | MUST |
| **ORC-BRANCH-011** | [V1] Branch evaluation MUST select `then` step if true, `else` if false | MUST |
| **ORC-BRANCH-012** | [V1] Branch evaluation MUST emit `branch_evaluated` event with result | MUST |
| **ORC-BRANCH-013** | [V1] Branch evaluation MUST validate target step exists and is at a later index | MUST |
| **ORC-BRANCH-014** | [V1] Branch evaluation MUST update run summary with new step index | MUST |
| **ORC-BRANCH-015** | [V1] Branch target MUST be a later step in the flow; backward jumps MUST fail with `branch_invalid_target` | MUST |

**Implementation**: `core/orchestrator/branching.py`

---

## 6. Loop Evaluation Requirements

### 6.1 Stop Conditions

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-LOOP-001** | [V1] Loop stop conditions MUST support: `confidence_threshold`, `no_missing_evidence` | MUST |
| **ORC-LOOP-002** | [V1] Loop stop conditions MUST support `all`/`any` groups for composite conditions | MUST |
| **ORC-LOOP-003** | [V1] Loop stop conditions MUST have maximum 20 stop condition nodes | MUST |

**Implementation**: `core/orchestrator/looping.py`

### 6.2 Loop Execution

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-LOOP-010** | [V1] `loop` steps MUST initialize `iteration_count` on first iteration | MUST |
| **ORC-LOOP-011** | [V1] `loop` steps MUST emit `loop_started` event | MUST |
| **ORC-LOOP-012** | [V1] `loop` steps MUST check stop condition before each iteration | MUST |
| **ORC-LOOP-013** | [V1] `loop` steps MUST execute iteration step if condition not met | MUST |
| **ORC-LOOP-014** | [V1] `loop` steps MUST increment `iteration_count` counter | MUST |
| **ORC-LOOP-015** | [V1] `loop` steps MUST emit `loop_iteration_started` and `loop_iteration_completed` events | MUST |
| **ORC-LOOP-016** | [V1] `loop` steps MUST terminate when: stop condition met, max_iters reached, or budget exceeded | MUST |

**Implementation**: `core/orchestrator/loop_executor.py`

### 6.3 Loop Termination

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-LOOP-020** | [V1] Loop termination MUST set `reason` with: `STOP_CONDITION_MET`, `MAX_ITERS_REACHED`, `BUDGET_EXCEEDED` | MUST |
| **ORC-LOOP-021** | [V1] Loop termination MUST record `finished_at` timestamp | MUST |
| **ORC-LOOP-022** | [V1] Loop termination MUST save loop state to run context | MUST |
| **ORC-LOOP-023** | [V1] Loop termination MUST emit `loop_terminated` event | MUST |
| **ORC-LOOP-024** | [V1] Loop termination MUST navigate to `after_step` if specified | MUST |
| **ORC-LOOP-025** | [V1] Loop budget MUST be enforced per pass; exceeded budget MAY trigger HITL escalation or fail the step based on action policy | MAY |

**Implementation**: `core/orchestrator/loop_executor.py`

---

## 7. Plan Execution Requirements

### 7.1 Plan Proposal

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-PLAN-001** | [V1] `plan_proposal` steps MUST get plan from `pending_plan` OR execute agent to generate plan | MUST |
| **ORC-PLAN-002** | [V1] `plan_proposal` steps MUST validate plan against `ActionPlan` schema | MUST |
| **ORC-PLAN-003** | [V1] `plan_proposal` steps MUST store plan artifact as `proposed_plan` | MUST |
| **ORC-PLAN-004** | [V1] `plan_proposal` steps MUST emit `plan_proposed` event | MUST |

**Implementation**: `core/orchestrator/plan_executor.py`

### 7.2 Plan Gate

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-PLAN-010** | [V1] `plan_gate` steps MUST load `proposed_plan` artifact | MUST |
| **ORC-PLAN-011** | [V1] `plan_gate` steps MUST execute `PlanGate.evaluate` with allow lists and budget | MUST |
| **ORC-PLAN-012** | [V1] `plan_gate` steps MUST store gate result as `gated_plan` | MUST |
| **ORC-PLAN-013** | [V1] `plan_gate` steps MUST emit `plan_gated` event with approval/rejection counts | MUST |

**Implementation**: `core/orchestrator/plan_executor.py`, `core/governance/gates.py`

### 7.3 Plan Execute

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-PLAN-020** | [V1] `plan_execute` steps MUST load `gated_plan` artifact | MUST |
| **ORC-PLAN-021** | [V1] If status `REJECTED`: fail step with `plan_rejected` | MUST |
| **ORC-PLAN-022** | [V1] If status `REQUIRES_HITL`: pause for approval | MUST |
| **ORC-PLAN-023** | [V1] If status `APPROVED`: execute approved steps sequentially | MUST |
| **ORC-PLAN-024** | [V1] Plan step execution MUST emit `plan_step_started` event | MUST |
| **ORC-PLAN-025** | [V1] Plan step execution MUST execute tool or agent call | MUST |
| **ORC-PLAN-026** | [V1] Plan step execution MUST collect evidence and artifacts | MUST |
| **ORC-PLAN-027** | [V1] Plan step execution MUST emit `plan_step_completed` event | MUST |
| **ORC-PLAN-028** | [V1] Plan step execution MUST fail entire plan if any step fails | MUST |

**Implementation**: `core/orchestrator/plan_executor.py`

---

## 8. Template Rendering Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-TMPL-001** | [V1] Template placeholders MUST use `{{key}}` syntax | MUST |
| **ORC-TMPL-002** | [V1] `render_strict` MUST resolve all placeholders or raise `TemplateError` for missing keys | MUST |
| **ORC-TMPL-003** | [V1] `render_strict` MUST support nested path resolution (e.g., `{{steps.step1.output.field}}`) | MUST |
| **ORC-TMPL-004** | [V1] `render_strict` MUST stringify complex values (dict/list) as JSON | MUST |
| **ORC-TMPL-005** | [V1] `render_lenient` MUST resolve placeholders leniently (return `None` or empty string for missing) | MUST |
| **ORC-TMPL-006** | [V1] `render_lenient` MUST preserve non-string values when placeholder is the entire value | MUST |
| **ORC-TMPL-007** | [V1] Template rendering MUST recursively render nested dicts and lists | MUST |
| **ORC-TMPL-008** | [V1] Artifact paths MUST support dotted keys (e.g., `artifacts.step1.data`) | MUST |

**Implementation**: `core/orchestrator/templating.py`

---

## 9. Tool Batch Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-BATCH-001** | [V1] `tool_batch` steps MUST validate all tools are `deterministic` and `read_only` | MUST |
| **ORC-BATCH-002** | [V1] `tool_batch` steps MUST execute up to 20 tools per batch | MUST |
| **ORC-BATCH-003** | [V1] `tool_batch` steps MUST support parallel or sequential execution | MUST |
| **ORC-BATCH-004** | [V1] Parallel execution MAY be degraded to sequential if budget `max_parallel_calls` is exceeded | MAY |
| **ORC-BATCH-005** | [V1] Results MUST be merged with deterministic ordering by tool name | MUST |
| **ORC-BATCH-006** | [V1] Evidence items MUST receive stable IDs based on `tool_name` | MUST |

**Implementation**: `core/orchestrator/step_executor.py`

---

## 10. Context Object Requirements

### 10.1 RunContext

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-CTX-001** | [V1] `RunContext` MUST contain: `run_id`, `product`, `flow`, `status`, `input_payload`, `artifacts`, `metadata`, `trace` | MUST |
| **ORC-CTX-002** | [V1] `run_id` MUST be a unique identifier | MUST |
| **ORC-CTX-003** | [V1] `product` MUST be the product name | MUST |
| **ORC-CTX-004** | [V1] `flow` MUST be the flow name | MUST |
| **ORC-CTX-005** | [V1] `status` MUST be the current run status | MUST |
| **ORC-CTX-006** | [V1] `input_payload` MUST be the initial input payload | MUST |
| **ORC-CTX-007** | [V1] `artifacts` MUST be the accumulated artifacts dict | MUST |
| **ORC-CTX-008** | [V1] `metadata` MUST be runtime metadata (counters, budget, loops) | MUST |
| **ORC-CTX-009** | [V1] `trace` MUST be optional trace hook function | MUST |

**Implementation**: `core/orchestrator/context.py`

### 10.2 StepContext

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-CTX-010** | [V1] `StepContext` MUST be derived from `RunContext` | MUST |
| **ORC-CTX-011** | [V1] `StepContext` MUST contain: `step_id`, `step_type`, `backend`, `name`, `status`, `attempt` | MUST |
| **ORC-CTX-012** | [V1] Context `emit` MUST delegate to trace hook with merged payload | MUST |
| **ORC-CTX-013** | [V1] `StepContext` MUST provide: `run_id`, `product`, `flow` | MUST |

**Implementation**: `core/orchestrator/context.py`

---

## 11. Flow Loading Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-FLOW-001** | [V1] Flow loader MUST support YAML (`.yaml`, `.yml`) and JSON (`.json`) formats | MUST |
| **ORC-FLOW-002** | [V1] Flow loading MUST parse file content | MUST |
| **ORC-FLOW-003** | [V1] Flow loading MUST normalize step IDs (fallback to `step_{index}`) | MUST |
| **ORC-FLOW-004** | [V1] Flow loading MUST validate against `FlowDef` schema | MUST |
| **ORC-FLOW-005** | [V1] Flow loading MUST raise `FlowLoadError` for invalid flows | MUST |
| **ORC-FLOW-006** | [V1] Flow definitions MUST have `name` (1-80 chars) | MUST |
| **ORC-FLOW-007** | [V1] Flow definitions MUST have `steps` (non-empty list) | MUST |
| **ORC-FLOW-008** | [V1] Flow definitions MUST have `autonomy` with default `SUPERVISED` | MUST |

**Implementation**: `core/orchestrator/flow_loader.py`

---

## 12. Error Handling Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-ERR-001** | [V1] Step failures MUST update step status to `FAILED` | MUST |
| **ORC-ERR-002** | [V1] Step failures MUST record error message and type | MUST |
| **ORC-ERR-003** | [V1] Step failures MUST transition run to `FAILED` | MUST |
| **ORC-ERR-004** | [V1] Step failures MUST emit `step_failed` event | MUST |
| **ORC-ERR-005** | [V1] Step failures MUST persist run output | MUST |
| **ORC-ERR-006** | [V1] Governance denials MUST fail with appropriate reason codes: `autonomy_denied`, `branch_condition_disallowed`, `loop_condition_disallowed`, `policy_blocked` | MUST |
| **ORC-ERR-007** | [V1] Free-text input guards MUST block direct tool/agent execution unless explicitly allowed in `allowed_tools` or `allowed_agents` | MUST |

**Implementation**: `core/orchestrator/step_executor.py`, `core/governance/hooks.py`

---

## 13. Observability Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-OBS-001** | [V1] The orchestrator MUST emit trace events for: | MUST |
| | • Run lifecycle: `run_started`, `run_completed`, `run_failed`, `run_paused`, `run_resumed` | |
| | • Step lifecycle: `step_started`, `step_completed`, `step_failed` | |
| | • State transitions: `run_state_transition` | |
| | • Branches: `branch_evaluated` | |
| | • Loops: `loop_started`, `loop_iteration_started`, `loop_iteration_completed`, `loop_terminated` | |
| | • Plans: `plan_proposed`, `plan_gated`, `plan_step_started`, `plan_step_completed` | |
| | • User input: `user_input_requested`, `user_input_received`, `user_input_accepted` | |
| | • Approvals: `pending_human`, `pending_approval` | |
| | • Budget: `budget_resolved`, `budget_consumed`, `budget_exceeded` | |
| **ORC-OBS-002** | [V1] All trace events MUST include: `event_id`, `step_id` (if applicable), `run_id`, `product`, `flow`, `kind`, `ts` | MUST |

**Implementation**: `core/memory/tracing.py`

---

## 14. Memory/Persistence Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **ORC-MEM-001** | [V1] Run records MUST be persisted via `MemoryBackend` with: `create_run`, `update_run_status`, `update_run_output`, `get_run_bundle` | MUST |
| **ORC-MEM-002** | [V1] Step records MUST be persisted via: `create_step`, `update_step` | MUST |
| **ORC-MEM-003** | [V1] Approval records MUST be managed via `HITLService`: `request_approval`, `resolve_approval` | MUST |

**Implementation**: `core/memory/router.py`, `core/orchestrator/hitl.py`

---

## 15. Future Considerations

### 15.1 V1.1 Enhancements

| ID | Feature | Description |
|----|---------|-------------|
| **ORC-FUTURE-001** | Parallel step execution | Execute independent steps concurrently |
| **ORC-FUTURE-002** | Step dependencies | Explicit DAG-based step dependencies |
| **ORC-FUTURE-003** | Checkpoint/rollback | Save and restore run state |

### 15.2 V2 Features

| ID | Feature | Description |
|----|---------|-------------|
| **ORC-FUTURE-010** | Subflow execution | Nested flow execution (`subflow` step type) |
| **ORC-FUTURE-011** | Distributed execution | Multi-node orchestration |
| **ORC-FUTURE-012** | Event-driven triggers | Start flows from external events |

---

## 16. Traceability Matrix

| Requirement | Implementation | Test |
|-------------|----------------|------|
| ORC-RUN-001 | `core/contracts/run_schema.py` | `tests/unit/core/contracts/test_run_schema.py` |
| ORC-RUN-010 | `core/orchestrator/run_lifecycle.py` | `tests/unit/core/orchestrator/test_run_lifecycle.py` |
| ORC-STEP-001 | `core/contracts/flow_schema.py` | `tests/unit/core/contracts/test_flow_schema.py` |
| ORC-PAUSE-001 | `core/orchestrator/user_input_handler.py` | `tests/integration/test_user_input_flow.py` |
| ORC-BRANCH-001 | `core/orchestrator/branching.py` | `tests/unit/core/orchestrator/test_branching.py` |
| ORC-LOOP-010 | `core/orchestrator/loop_executor.py` | `tests/unit/core/orchestrator/test_loop_executor.py` |
| ORC-PLAN-001 | `core/orchestrator/plan_executor.py` | `tests/unit/core/orchestrator/test_plan_executor.py` |
| ORC-SEM-001 | `core/orchestrator/semantic_phase.py` | `tests/architecture/test_semantic_isolation.py` |
| ORC-SEM-010 | `core/contracts/semantic_schema.py` | `tests/unit/core/contracts/test_semantic_schema.py` |
| ORC-SEM-STOP-001 | `core/orchestrator/engine.py` | `tests/architecture/test_semantic_isolation.py` |

---

## 17. Versioning & Reproducibility (Added: 2026-01-13)

> **Source**: BRD-AUTO-005, BRD-AUTO-SEM-007, INV-5

### 17.1 Determinism Requirements

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **ORC-DET-001** | [V1] Same flow + payload + config MUST produce identical execution path | MUST | 1.1 |
| **ORC-DET-002** | [V1] Semantic envelope MUST be content-hashed for reproducibility | MUST | 1.1 |
| **ORC-DET-003** | [V1] Run record MUST capture flow version and config snapshot | MUST | 1.1 |
| **ORC-DET-004** | [V1] State transitions MUST be deterministic given same inputs | MUST | 1.1 |
| **ORC-DET-005** | [V1] Branch/loop conditions MUST evaluate deterministically | MUST | 1.1 |

**Implementation**: `core/orchestrator/engine.py`, `core/orchestrator/semantic_phase.py`

### 17.2 Version Capture

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **ORC-VER-001** | [V1] `RunRecord` MUST include `flow_version` field | MUST | 1.1 |
| **ORC-VER-002** | [V1] `RunRecord` MUST include `config_hash` for reproducibility | MUST | 1.1 |
| **ORC-VER-003** | [V1] `SemanticEnvelope` MUST include `envelope_hash` (SHA-256) | MUST | 1.1 |
| **ORC-VER-004** | [V1] Model versions used MUST be captured in step metadata | SHOULD | 1.1 |

**Hash Computation**:
```python
def compute_envelope_hash(envelope: SemanticEnvelope) -> str:
    """Compute deterministic hash of semantic envelope."""
    payload = envelope.model_dump(exclude={"envelope_hash"})
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()
```

**Implementation**: `core/orchestrator/semantic_phase.py`, `core/contracts/run_schema.py`

---

## 18. Explicit Non-Goals (Added: 2026-01-13)

> **The Orchestrator MUST NOT**:

| Non-Goal | Rationale | Violation Example |
|----------|-----------|-------------------|
| Agent-controlled execution | Violates INV-5, INV-6 | Agent decides next step |
| Implicit state changes | Violates auditability | State changes without trace event |
| Self-modifying flows | Violates determinism | Flow modifies itself at runtime |
| Unbounded iteration | Violates INV-5 | Loop without max_iters |
| Hidden branching logic | Violates explicit flows | Undocumented conditional paths |
| Autonomous tool invocation | Violates governance | Tool runs without before_tool hook |

---

## 19. BRD Requirement Mapping (Added: 2026-01-13)

| BRD ID | Description | Techspec IDs | Ver |
|--------|-------------|--------------|-----|
| BRD-AUTO-SEM-001 | Mandatory semantic phase | ORC-SEM-001...004 | 1.1 |
| BRD-AUTO-SEM-002 | Structured envelope | ORC-SEM-010...019 | 1.1 |
| BRD-AUTO-SEM-004 | NextAction determination | ORC-SEM-020...022 | 1.1 |
| BRD-AUTO-SEM-006 | Domain-agnostic normalization | ORC-SEM-030...035 | 1.1 |
| BRD-AUTO-SEM-007 | Deterministic normalization | ORC-DET-001...005 | 1.1 |
| BRD-AUTO-STOP-001 | ASK_USER pause | ORC-SEM-STOP-001...003 | 1.1 |
| BRD-AUTO-STOP-004 | ABORT failure | ORC-SEM-STOP-004...005 | 1.1 |
| BRD-AUTO-STOP-007 | Stop blocks steps | ORC-SEM-STOP-007 | 1.1 |
| BRD-AUTO-040 | Workflow patterns | ORC-STEP-001, ORC-BRANCH-*, ORC-LOOP-* | 1.0 |
| BRD-AUTO-044 | Governed iteration | ORC-LOOP-010...016 | 1.0 |
| BRD-AUTO-045 | Stop conditions | ORC-LOOP-020...025 | 1.0 |
| BRD-AUTO-046 | Durable iteration | ORC-LOOP-022, ORC-CTX-007 | 1.0 |
| BRD-OPS-001 | State persistence | ORC-RUN-010...015 | 1.0 |
| BRD-OPS-002 | Resumable workflows | ORC-RESUME-001...028 | 1.0 |
| BRD-OPS-SEM-001 | Semantic trace events | ORC-SEM-040...043 | 1.1 |
