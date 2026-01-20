# Orchestration Engine Technical Specification

> **Document ID**: ORC  
> **Version**: V1.3  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-20  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial release |
| 1.1.0 | 2026-01-13 | Added §3.7 Versioning & Reproducibility, §3.8 Explicit Non-Goals, updated BRD mappings |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |
| V1.3 | 2026-01-20 | Added §15 Orchestrator-Controlled Reasoning (BRD-AUTO-047/048), §16 Explicit Terminal Outcomes (BRD-AUTO-052) |

---

## 1. Overview

The orchestration engine is responsible for executing flows—directed sequences of steps that 
invoke agents, tools, and control structures. This specification defines the requirements for 
run lifecycle management, step execution, pause/resume mechanics, and control flow evaluation.

## 2. Run Lifecycle Requirements

### 2.1 Run Status State Machine

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-RUN-001 | The orchestrator MUST implement a finite state machine with states: `RUNNING`, `PAUSED_WAITING_FOR_USER`, `PENDING_HUMAN`, `COMPLETED`, `FAILED`, `CANCELLED` | MUST | BRD-AUTO-042, BRD-AUTO-STOP-003, BRD-GOV-005 | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-002 | Valid state transitions MUST be enforced: | MUST | BRD-AUTO-042 | 1.1 | 13 Jan 2026 | • `RUNNING` → `PAUSED_WAITING_FOR_USER`, `PENDING_HUMAN`, `COMPLETED`, `FAILED`; • `PAUSED_WAITING_FOR_USER` → `RUNNING`, `CANCELLED`; • `PENDING_HUMAN` → `RUNNING`, `CANCELLED`; • `COMPLETED` → (terminal, no transitions); • `FAILED` → (terminal, no transitions) |
| ORC-RUN-003 | State transitions MUST be validated via `can_transition()` before execution; invalid transitions MUST raise `InvalidTransitionError` | MUST | BRD-AUTO-042 | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-004 | Each state transition MUST emit a `run_state_transition` trace event with `from`, `to`, and `reason` payload fields | MUST | BRD-AUTO-042 | 1.1 | 13 Jan 2026 | — |


### 2.2 Run Initialization

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-RUN-010 | Run initialization MUST generate a unique run ID with format `run_{timestamp}_{uuid8}` | MUST | BRD-AUTO-046 | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-011 | Run initialization MUST create a `RunRecord` with status `RUNNING` | MUST | BRD-AUTO-046 | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-012 | Run initialization MUST pre-create `StepRecord` entries for all steps in the flow | MUST | BRD-AUTO-046 | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-013 | Run initialization MUST initialize metadata counters: `steps_executed=0`, `tool_calls=0`, `tokens_used=0`, `started_at` | MUST | BRD-AUTO-046 | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-014 | Run initialization MUST clear staging area (output only, preserve input) | MUST | BRD-AUTO-046 | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-015 | Run initialization MUST emit `run_started` trace event | MUST | BRD-AUTO-046 | 1.1 | 13 Jan 2026 | — |


### 2.3 Run Input Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-RUN-020 | Payload size MUST be validated against `max_payload_bytes`; runs exceeding the limit MUST be rejected with code `payload_limit_exceeded` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-021 | Flow step count MUST be validated against `max_steps`; flows exceeding the limit MUST be rejected with code `max_steps_exceeded` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 3. Semantic Interpretation Phase Requirements

### 3.1 Mandatory Semantic Phase

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-SEM-001 | The orchestrator MUST execute a `semantic_interpretation` phase before planning/execution for every run | MUST | BRD-AUTO-025, BRD-AUTO-SEM-001 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-002 | The semantic phase MAY be explicitly skipped only if `skip_semantic_interpretation: true` is set in flow config | MAY | BRD-AUTO-025, BRD-AUTO-SEM-001 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-003 | The semantic phase MUST produce a `SemanticEnvelope` result before any step execution | MUST | BRD-AUTO-025, BRD-AUTO-SEM-001 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-004 | If the semantic phase fails, the run MUST transition to `FAILED` with code `semantic_interpretation_failed` | MUST | BRD-AUTO-025, BRD-AUTO-SEM-001, BRD-GOV-027 | 1.1 | 13 Jan 2026 | — |


### 3.2 SemanticEnvelope Contract

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-SEM-010 | `SemanticEnvelope` MUST be a Pydantic model in `core/contracts/semantic_schema.py` | MUST | BRD-AUTO-SEM-002 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-011 | `SemanticEnvelope` MUST include: `raw_input` (original user input) | MUST | BRD-AUTO-SEM-002, BRD-AUTO-SEM-003 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-012 | `SemanticEnvelope` MUST include: `normalized_input` (cleaned/standardized input) | MUST | BRD-AUTO-SEM-002, BRD-AUTO-SEM-003 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-013 | `SemanticEnvelope` MUST include: `product_id` (resolved product identifier) | MUST | BRD-AUTO-SEM-002, BRD-AUTO-SEM-003 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-014 | `SemanticEnvelope` MUST include: `intent_type` (classified intent category) | MUST | BRD-AUTO-SEM-002, BRD-AUTO-SEM-003 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-015 | `SemanticEnvelope` MUST include: `entities` (list of extracted entities with type, value, confidence) | MUST | BRD-AUTO-SEM-002, BRD-AUTO-SEM-003 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-016 | `SemanticEnvelope` MUST include: `constraints` (dict of extracted constraints/filters) | MUST | BRD-AUTO-SEM-002, BRD-AUTO-SEM-003 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-017 | `SemanticEnvelope` MUST include: `confidence` (float 0.0-1.0) | MUST | BRD-AUTO-027, BRD-AUTO-SEM-002, BRD-AUTO-SEM-003, BRD-GOV-060 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-018 | `SemanticEnvelope` MUST include: `ambiguities` (list of unresolved ambiguities) | MUST | BRD-AUTO-027, BRD-AUTO-SEM-002, BRD-AUTO-SEM-003, BRD-GOV-061 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-019 | `SemanticEnvelope` MUST include: `proposed_next_action` (NextAction enum value) | MUST | BRD-AUTO-027, BRD-AUTO-SEM-002 | 1.1 | 13 Jan 2026 | — |


### 3.3 NextAction Enum

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-SEM-020 | `NextAction` enum MUST define: `CONTINUE`, `ASK_USER`, `ABORT` | MUST | BRD-AUTO-027, BRD-AUTO-SEM-004 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-021 | `NextAction` enum MAY define: `NEEDS_APPROVAL` for HITL gate integration | MAY | BRD-AUTO-027, BRD-AUTO-SEM-004 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-022 | `NextAction` MUST be enforced by the engine before step execution proceeds | MUST | BRD-AUTO-027, BRD-AUTO-SEM-004 | 1.1 | 13 Jan 2026 | — |


### 3.4 Orchestrator Stop/Pause Mechanism

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-SEM-STOP-001 | If `NextAction=ASK_USER`, execution MUST NOT proceed to planning/steps | MUST | BRD-AUTO-027, BRD-AUTO-STOP-001, BRD-AUTO-STOP-007, BRD-GOV-025 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-STOP-002 | If `NextAction=ASK_USER`, run MUST transition to `PAUSED_WAITING_FOR_USER` | MUST | BRD-AUTO-027, BRD-AUTO-STOP-001, BRD-AUTO-STOP-003, BRD-GOV-025, BRD-GOV-063, BRD-GOV-CONF-004 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-STOP-003 | If `NextAction=ASK_USER`, a structured response MUST be returned with `clarifying_question` and `ambiguities` | MUST | BRD-AUTO-027, BRD-AUTO-STOP-001, BRD-AUTO-STOP-002, BRD-GOV-025 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-STOP-004 | If `NextAction=ABORT`, run MUST transition to `FAILED` with code `semantic_abort` | MUST | BRD-AUTO-STOP-004, BRD-AUTO-STOP-006 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-STOP-005 | If `NextAction=ABORT`, a structured error MUST include reason and ambiguities | MUST | BRD-AUTO-STOP-004, BRD-AUTO-STOP-005 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-STOP-006 | If `NextAction=NEEDS_APPROVAL`, run MUST transition to `PENDING_HUMAN` with semantic context | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-STOP-007 | Only `NextAction=CONTINUE` permits step execution to proceed | MUST | BRD-AUTO-STOP-007 | 1.1 | 13 Jan 2026 | — |


### 3.5 Deterministic Resolution Rules

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-SEM-030 | Core MUST apply domain-agnostic normalization: whitespace trimming, case normalization | MUST | BRD-AUTO-026, BRD-AUTO-SEM-006 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-031 | Core MUST apply entity deduplication (same type+value → single entity) | MUST | BRD-AUTO-026, BRD-AUTO-SEM-006, BRD-AUTO-SEM-008 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-032 | Core MUST merge overlapping constraints deterministically | MUST | BRD-AUTO-026, BRD-AUTO-SEM-006, BRD-AUTO-SEM-009 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-033 | Core MUST apply stable ordering to entities and constraints | MUST | BRD-AUTO-026, BRD-AUTO-SEM-006, BRD-AUTO-SEM-007, BRD-AUTO-SEM-009 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-034 | Core MUST apply schema coercions (string→int, string→date where schema declares type) | MUST | BRD-AUTO-026, BRD-AUTO-SEM-006, BRD-AUTO-SEM-010 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-035 | Core MUST NOT contain domain-specific rules (e.g., "trend requires time axis") | MUST | BRD-AUTO-026, BRD-AUTO-SEM-006 | 1.1 | 13 Jan 2026 | — |


### 3.6 Semantic Trace Events

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-SEM-040 | Semantic phase MUST emit `semantic_interpretation_started` event at phase start | MUST | BRD-OPS-SEM-001, BRD-OPS-SEM-002 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-041 | Semantic phase MUST emit `semantic_interpretation_completed` event with: envelope_hash, confidence, ambiguity_count, next_action | MUST | BRD-GOV-CONF-007, BRD-OPS-SEM-003, BRD-OPS-SEM-004 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-042 | If validation fails, MUST emit `semantic_validation_completed` event with: is_valid, missing_fields, violations | MUST | BRD-OPS-SEM-005, BRD-OPS-SEM-006 | 1.1 | 13 Jan 2026 | — |
| ORC-SEM-043 | If stop is issued, MUST emit `semantic_stop_issued` event with: next_action, question (if ASK_USER), reason (if ABORT) | MUST | BRD-AUTO-STOP-008, BRD-OPS-SEM-007, BRD-OPS-SEM-008 | 1.1 | 13 Jan 2026 | — |


### 2.4 Run Completion

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-RUN-030 | Run completion MUST transition status to `COMPLETED` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-031 | Run completion MUST persist normalized run output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-032 | Run completion MUST emit `run_completed` trace event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-033 | Run completion MUST export reasoning artifact (Markdown file) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-034 | Run completion MUST write final response to observability storage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-035 | Runs completing without output data MUST transition to `FAILED` with error code `missing_output` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-036 | Run output MUST pass governance validation via `after_run`; denied output MUST fail the run with reason `output_denied` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 2.5 Run Failure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-RUN-040 | Run failure MUST transition status to `FAILED` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-041 | Run failure MUST record error code and message in summary | MUST | BRD-OPS-040 | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-042 | Run failure MUST emit `run_failed` trace event | MUST | BRD-OPS-040 | 1.1 | 13 Jan 2026 | — |
| ORC-RUN-043 | Run failure MUST persist run output with error information | MUST | BRD-OPS-040 | 1.1 | 13 Jan 2026 | — |


---

## 3. Step Execution Requirements


### 3.1 Step Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-STEP-010 | `agent` steps MUST have `agent` field | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-011 | `tool` steps MUST have `tool` field | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-012 | `tool_batch` steps MUST have `tools` field | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-013 | `branch` steps MUST have `if` OR `condition` | MUST | BRD-AUTO-040 | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-014 | `branch` steps MUST have `then`, `condition`, and `else` fields | MUST | BRD-AUTO-040 | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-015 | `loop` steps MUST have `iteration_step`, `stop_condition`, and `max_iters` | MUST | BRD-AUTO-041, BRD-AUTO-045 | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-016 | `tool_batch` steps MUST have `tools` list with 1-20 items | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-017 | `user_input` steps MUST have valid `request` params OR `prompt` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 3.2 Step Lifecycle

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-STEP-020 | Each step execution MUST create `StepRecord` with status `STARTED` and `started_at` timestamp | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-021 | Each step execution MUST call `before_step` for permission check | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-022 | Each step execution MUST emit `step_started` trace event | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-023 | Each step execution MUST execute step logic based on type | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-024 | Each step execution MUST update `StepRecord` with `COMPLETED`/`FAILED` status and `finished_at` timestamp | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-025 | Each step execution MUST emit `step_completed` or `step_failed` trace event | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |
| ORC-STEP-026 | If `before_step` denies execution, the step MUST fail with `before_step_denied` event and run MUST transition to `FAILED` | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |


### 3.3 Step Retry Policy

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-STEP-030 | Tool steps MAY have a `retry_policy` with: | MAY | BRD-AUTO-004 | 1.1 | 13 Jan 2026 | • `max_attempts`: 1-10 attempts (default: 1); • `delay_seconds`: 0-60 seconds delay (default: 0); • `retryable_codes`: Optional list of error codes eligible for retry |
| ORC-STEP-031 | Retry decisions MUST be evaluated via `ErrorPolicy`; failed attempts MUST emit `tool_call_attempt_failed` and `tool_call_retry_scheduled` events | MUST | BRD-AUTO-004 | 1.1 | 13 Jan 2026 | — |


---

## 4. Pause/Resume Requirements

### 4.1 User Input Pause

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-PAUSE-001 | `user_input` steps MUST render params with template context | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-002 | `user_input` steps MUST build `UserInputRequest` from request | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-003 | `user_input` steps MUST create `ApprovalRecord` with type `INPUT` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-004 | `user_input` steps MUST update step status to `PAUSED` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-005 | `user_input` steps MUST transition run to `PAUSED_WAITING_FOR_USER` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-006 | `user_input` steps MUST emit `pending_user_input`, `user_input_requested`, `run_paused` events | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-007 | User input steps with `optional=true` MUST skip pause and continue with empty values | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.2 Human Approval Pause

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-PAUSE-010 | `human_approval` steps MUST build approval payload with context | MUST | BRD-GOV-001, BRD-GOV-002 | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-011 | `human_approval` steps MUST create `ApprovalRecord` via `HITLService` | MUST | BRD-GOV-001, BRD-GOV-002 | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-012 | `human_approval` steps MUST create `ApprovalRecord` with type `APPROVAL` | MUST | BRD-GOV-001, BRD-GOV-002 | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-013 | `human_approval` steps MUST update step status to `PAUSED` | MUST | BRD-GOV-001, BRD-GOV-005 | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-014 | `human_approval` steps MUST transition run to `PENDING_HUMAN` | MUST | BRD-GOV-001, BRD-GOV-005 | 1.1 | 13 Jan 2026 | — |
| ORC-PAUSE-015 | `human_approval` steps MUST emit `pending_human`, `pending_approval`, `run_pending_human` events | MUST | BRD-GOV-001, BRD-GOV-005 | 1.1 | 13 Jan 2026 | — |


### 4.3 Resume from User Input

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-RESUME-001 | Resume from user input MUST validate run is in `PAUSED_WAITING_FOR_USER` or `PENDING_USER_INPUT` status | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-002 | Resume from user input MUST validate response matches pending request (`run_id`, `form_id`) | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-003 | Resume from user input MUST run governance check via `before_user_input` | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-004 | Resume from user input MUST validate input values against request schema | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-005 | Resume from user input MUST merge defaults with provided values | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-006 | Resume from user input MUST store user input artifacts | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-007 | Resume from user input MUST update step status to `COMPLETED` | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-GOV-006, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-008 | Resume from user input MUST transition run to `RUNNING` | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-GOV-006, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-009 | Resume from user input MUST resume execution from next step | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-GOV-006, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-010 | User input validation MUST support: free text mode, choice input mode, question set mode | MUST | BRD-AUTO-042, BRD-AUTO-STOP-009, BRD-GOV-003, BRD-OPS-002 | 1.1 | 13 Jan 2026 | — |


### 4.4 Resume from Approval

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-RESUME-020 | Resume from approval MUST validate run is in `PENDING_HUMAN` status | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-021 | Resume from approval MUST validate approval payload contains `approved` field | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-022 | Resume from approval MUST resolve approval via `HITLService` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-023 | If rejected: transition run to `FAILED` (unless replan enabled) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-024 | If approved: transition run to `RUNNING` and continue | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-025 | Resume MUST emit `run_resumed` or `run_rejected` events | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-026 | Replan after rejection MUST require rejection comment | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-027 | Replan MUST limit to 2 rejections before permanent failure | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-RESUME-028 | Replan MUST re-execute planning step with previous context | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 5. Branch Evaluation Requirements

### 5.1 Condition Expressions

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-BRANCH-001 | Branch conditions MUST support path-based conditions with operators: `==`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `contains`, `not_in` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BRANCH-002 | Branch conditions MUST support composite conditions with `all` (AND) and `any` (OR) groups | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BRANCH-003 | Branch conditions MUST have maximum 20 condition nodes per expression | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BRANCH-004 | Condition paths MUST resolve: `steps.<step_id>.output.<field>` and `artifacts.<key>` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 5.2 Branch Execution

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-BRANCH-010 | Branch evaluation MUST evaluate condition deterministically | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BRANCH-011 | Branch evaluation MUST select `then` step if true, `else` if false | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BRANCH-012 | Branch evaluation MUST emit `branch_evaluated` event with result | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BRANCH-013 | Branch evaluation MUST validate target step exists and is at a later index | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BRANCH-014 | Branch evaluation MUST update run summary with new step index | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BRANCH-015 | Branch target MUST be a later step in the flow; backward jumps MUST fail with `branch_invalid_target` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 6. Loop Evaluation Requirements

### 6.1 Stop Conditions

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-LOOP-001 | Loop stop conditions MUST support: `confidence_threshold`, `no_missing_evidence` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-002 | Loop stop conditions MUST support `all`/`any` groups for composite conditions | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-003 | Loop stop conditions MUST have maximum 20 stop condition nodes | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.2 Loop Execution

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-LOOP-010 | `loop` steps MUST initialize `iteration_count` on first iteration | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-011 | `loop` steps MUST emit `loop_started` event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-012 | `loop` steps MUST check stop condition before each iteration | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-013 | `loop` steps MUST execute iteration step if condition not met | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-014 | `loop` steps MUST increment `iteration_count` counter | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-015 | `loop` steps MUST emit `loop_iteration_started` and `loop_iteration_completed` events | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-016 | `loop` steps MUST terminate when: stop condition met, max_iters reached, or budget exceeded | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.3 Loop Termination

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-LOOP-020 | Loop termination MUST set `reason` with: `STOP_CONDITION_MET`, `MAX_ITERS_REACHED`, `BUDGET_EXCEEDED` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-021 | Loop termination MUST record `finished_at` timestamp | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-022 | Loop termination MUST save loop state to run context | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-023 | Loop termination MUST emit `loop_terminated` event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-024 | Loop termination MUST navigate to `after_step` if specified | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-LOOP-025 | Loop budget MUST be enforced per pass; exceeded budget MAY trigger HITL escalation or fail the step based on action policy | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 7. Plan Execution Requirements

### 7.1 Plan Proposal

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-PLAN-001 | `plan_proposal` steps MUST get plan from `pending_plan` OR execute agent to generate plan | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-002 | `plan_proposal` steps MUST validate plan against `ActionPlan` schema | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-003 | `plan_proposal` steps MUST store plan artifact as `proposed_plan` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-004 | `plan_proposal` steps MUST emit `plan_proposed` event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 7.2 Plan Gate

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-PLAN-010 | `plan_gate` steps MUST load `proposed_plan` artifact | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-011 | `plan_gate` steps MUST execute `PlanGate.evaluate` with allow lists and budget | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-012 | `plan_gate` steps MUST store gate result as `gated_plan` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-013 | `plan_gate` steps MUST emit `plan_gated` event with approval/rejection counts | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 7.3 Plan Execute

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-PLAN-020 | `plan_execute` steps MUST load `gated_plan` artifact | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-021 | If status `REJECTED`: fail step with `plan_rejected` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-022 | If status `REQUIRES_HITL`: pause for approval | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-023 | If status `APPROVED`: execute approved steps sequentially | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-024 | Plan step execution MUST emit `plan_step_started` event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-025 | Plan step execution MUST execute tool or agent call | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-026 | Plan step execution MUST collect evidence and artifacts | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-027 | Plan step execution MUST emit `plan_step_completed` event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-PLAN-028 | Plan step execution MUST fail entire plan if any step fails | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 8. Template Rendering Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-TMPL-001 | Template placeholders MUST use `{{key}}` syntax | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-TMPL-002 | `render_strict` MUST resolve all placeholders or raise `TemplateError` for missing keys | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-TMPL-003 | `render_strict` MUST support nested path resolution (e.g., `{{steps.step1.output.field}}`) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-TMPL-004 | `render_strict` MUST stringify complex values (dict/list) as JSON | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-TMPL-005 | `render_lenient` MUST resolve placeholders leniently (return `None` or empty string for missing) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-TMPL-006 | `render_lenient` MUST preserve non-string values when placeholder is the entire value | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-TMPL-007 | Template rendering MUST recursively render nested dicts and lists | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-TMPL-008 | Artifact paths MUST support dotted keys (e.g., `artifacts.step1.data`) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 9. Tool Batch Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-BATCH-001 | `tool_batch` steps MUST validate all tools are `deterministic` and `read_only` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BATCH-002 | `tool_batch` steps MUST execute up to 20 tools per batch | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BATCH-003 | `tool_batch` steps MUST support parallel or sequential execution | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BATCH-004 | Parallel execution MAY be degraded to sequential if budget `max_parallel_calls` is exceeded | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BATCH-005 | Results MUST be merged with deterministic ordering by tool name | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-BATCH-006 | Evidence items MUST receive stable IDs based on `tool_name` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 10. Context Object Requirements

### 10.1 RunContext

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-CTX-001 | `RunContext` MUST contain: `run_id`, `product`, `flow`, `status`, `input_payload`, `artifacts`, `metadata`, `trace` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-002 | `run_id` MUST be a unique identifier | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-003 | `product` MUST be the product name | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-004 | `flow` MUST be the flow name | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-005 | `status` MUST be the current run status | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-006 | `input_payload` MUST be the initial input payload | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-007 | `artifacts` MUST be the accumulated artifacts dict | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-008 | `metadata` MUST be runtime metadata (counters, budget, loops) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-009 | `trace` MUST be optional trace hook function | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 10.2 StepContext

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-CTX-010 | `StepContext` MUST be derived from `RunContext` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-011 | `StepContext` MUST contain: `step_id`, `step_type`, `backend`, `name`, `status`, `attempt` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-012 | Context `emit` MUST delegate to trace hook with merged payload | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-CTX-013 | `StepContext` MUST provide: `run_id`, `product`, `flow` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 11. Flow Loading Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-FLOW-001 | Flow loader MUST support YAML (`.yaml`, `.yml`) and JSON (`.json`) formats | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-FLOW-002 | Flow loading MUST parse file content | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-FLOW-003 | Flow loading MUST normalize step IDs (fallback to `step_{index}`) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-FLOW-004 | Flow loading MUST validate against `FlowDef` schema | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-FLOW-005 | Flow loading MUST raise `FlowLoadError` for invalid flows | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-FLOW-006 | Flow definitions MUST have `name` (1-80 chars) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-FLOW-007 | Flow definitions MUST have `steps` (non-empty list) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-FLOW-008 | Flow definitions MUST have `autonomy` with default `SUPERVISED` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 12. Error Handling Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-ERR-001 | Step failures MUST update step status to `FAILED` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-ERR-002 | Step failures MUST record error message and type | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-ERR-003 | Step failures MUST transition run to `FAILED` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-ERR-004 | Step failures MUST emit `step_failed` event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-ERR-005 | Step failures MUST persist run output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-ERR-006 | Governance denials MUST fail with appropriate reason codes: `autonomy_denied`, `branch_condition_disallowed`, `loop_condition_disallowed`, `policy_blocked` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-ERR-007 | Free-text input guards MUST block direct tool/agent execution unless explicitly allowed in `allowed_tools` or `allowed_agents` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 13. Observability Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-OBS-001 | The orchestrator MUST emit trace events for: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • Run lifecycle: `run_started`, `run_completed`, `run_failed`, `run_paused`, `run_resumed`; • Step lifecycle: `step_started`, `step_completed`, `step_failed`; • State transitions: `run_state_transition`; • Branches: `branch_evaluated`; • Loops: `loop_started`, `loop_iteration_started`, `loop_iteration_completed`, `loop_terminated`; • Plans: `plan_proposed`, `plan_gated`, `plan_step_started`, `plan_step_completed`; • User input: `user_input_requested`, `user_input_received`, `user_input_accepted`; • Approvals: `pending_human`, `pending_approval`; • Budget: `budget_resolved`, `budget_consumed`, `budget_exceeded` |
| ORC-OBS-002 | All trace events MUST include: `event_id`, `step_id` (if applicable), `run_id`, `product`, `flow`, `kind`, `ts` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 14. Memory/Persistence Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-MEM-001 | Run records MUST be persisted via `MemoryBackend` with: `create_run`, `update_run_status`, `update_run_output`, `get_run_bundle` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-MEM-002 | Step records MUST be persisted via: `create_step`, `update_step` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-MEM-003 | Approval records MUST be managed via `HITLService`: `request_approval`, `resolve_approval` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 15. Orchestrator-Controlled Reasoning Lifecycle (Added: 2026-01-20)

> **Source**: BRD-AUTO-047 (Central reasoning lifecycle), BRD-AUTO-048 (Bounded reasoning iteration)

### 15.1 Reasoning Lifecycle Phases

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-REASON-001 | Orchestrator MUST control reasoning lifecycle with phases: `INTERPRET` → `PROPOSE` → `CRITIQUE` → `RECOMMEND` | MUST | BRD-AUTO-047 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-002 | Phase transitions MUST be explicit and logged via trace events | MUST | BRD-AUTO-047 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-003 | Each phase MUST produce a typed output artifact (`InterpretOutput`, `ProposeOutput`, `CritiqueOutput`, `RecommendOutput`) | MUST | BRD-AUTO-047 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-004 | Phase outputs MUST be persisted before transitioning to next phase | MUST | BRD-AUTO-047 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-005 | Reasoning lifecycle MUST NOT proceed to RECOMMEND without passing CRITIQUE | MUST | BRD-AUTO-047, BRD-AUTO-050 | 1.3 | 20 Jan 2026 | — |


### 15.2 Bounded Reasoning Iteration

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-REASON-010 | Reasoning iterations MUST be bounded by `max_reasoning_iterations` (default: 3, max: 10) | MUST | BRD-AUTO-048 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-011 | Each iteration MUST consume reasoning budget via `BudgetEnforcer` | MUST | BRD-AUTO-048 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-012 | Iteration count MUST be tracked and emitted in all reasoning trace events | MUST | BRD-AUTO-048 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-013 | When `max_reasoning_iterations` is reached, reasoning MUST terminate with deterministic outcome | MUST | BRD-AUTO-048 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-014 | Iteration termination reason MUST be one of: `SUFFICIENT`, `MAX_ITERATIONS`, `BUDGET_EXCEEDED`, `CONFIDENCE_MET` | MUST | BRD-AUTO-048 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-015 | Reasoning termination MUST emit `reasoning_terminated` event with `iteration_count`, `reason`, `final_confidence` | MUST | BRD-AUTO-048 | 1.3 | 20 Jan 2026 | — |


### 15.3 Reasoning Phase Events

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-REASON-020 | Each phase MUST emit `reasoning_phase_started` with `phase_name`, `iteration`, `input_hash` | MUST | BRD-AUTO-047 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-021 | Each phase MUST emit `reasoning_phase_completed` with `phase_name`, `iteration`, `output_hash`, `confidence` | MUST | BRD-AUTO-047 | 1.3 | 20 Jan 2026 | — |
| ORC-REASON-022 | Phase failures MUST emit `reasoning_phase_failed` with `phase_name`, `iteration`, `error_code`, `reason` | MUST | BRD-AUTO-047 | 1.3 | 20 Jan 2026 | — |


---

## 16. Explicit Terminal Outcomes (Added: 2026-01-20)

> **Source**: BRD-AUTO-052 - Explicit terminal outcomes with explanations

### 16.1 Terminal Outcome Definitions

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-TERM-001 | Run MUST terminate with one of explicit outcomes: `COMPLETED`, `FAILED`, `CANCELLED`, `ABORTED`, `PAUSED_INDEFINITE` | MUST | BRD-AUTO-052 | 1.3 | 20 Jan 2026 | — |
| ORC-TERM-002 | Every terminal outcome MUST include `outcome_reason` (enum) and `outcome_explanation` (string) | MUST | BRD-AUTO-052 | 1.3 | 20 Jan 2026 | — |
| ORC-TERM-003 | `outcome_reason` enum MUST include: `SUCCESS`, `USER_ABORT`, `GOVERNANCE_BLOCK`, `BUDGET_EXCEEDED`, `MAX_ITERATIONS`, `VALIDATION_FAILED`, `UNRECOVERABLE_ERROR` | MUST | BRD-AUTO-052 | 1.3 | 20 Jan 2026 | — |
| ORC-TERM-004 | `outcome_explanation` MUST be human-readable and auditable | MUST | BRD-AUTO-052 | 1.3 | 20 Jan 2026 | — |
| ORC-TERM-005 | Terminal outcome MUST be persisted in `RunRecord` and emitted as `run_terminal_outcome` event | MUST | BRD-AUTO-052 | 1.3 | 20 Jan 2026 | — |


### 16.2 Terminal Outcome Artifacts

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-TERM-ART-001 | `COMPLETED` outcome MUST include final output artifact | MUST | BRD-AUTO-052 | 1.3 | 20 Jan 2026 | — |
| ORC-TERM-ART-002 | `FAILED` outcome MUST include error artifact with `error_code`, `error_message`, `stack_trace` (if available) | MUST | BRD-AUTO-052 | 1.3 | 20 Jan 2026 | — |
| ORC-TERM-ART-003 | `ABORTED` outcome MUST include abort artifact with `abort_reason`, `abort_source` (user/system/governance) | MUST | BRD-AUTO-052 | 1.3 | 20 Jan 2026 | — |
| ORC-TERM-ART-004 | All terminal artifacts MUST be persisted before run record is finalized | MUST | BRD-AUTO-052 | 1.3 | 20 Jan 2026 | — |


---

## 17. Versioning & Reproducibility (Added: 2026-01-13)

> **Source**: BRD-AUTO-005, BRD-AUTO-SEM-007, INV-5

### 17.1 Determinism Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-DET-001 | Same flow + payload + config MUST produce identical execution path | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-DET-002 | Semantic envelope MUST be content-hashed for reproducibility | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-DET-003 | Run record MUST capture flow version and config snapshot | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-DET-004 | State transitions MUST be deterministic given same inputs | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-DET-005 | Branch/loop conditions MUST evaluate deterministically | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 17.2 Version Capture

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-VER-001 | `RunRecord` MUST include `flow_version` field | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-VER-002 | `RunRecord` MUST include `config_hash` for reproducibility | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-VER-003 | `SemanticEnvelope` MUST include `envelope_hash` (SHA-256) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| ORC-VER-004 | Model versions used MUST be captured in step metadata | SHOULD | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

**Hash Computation**:


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

