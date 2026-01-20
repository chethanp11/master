# Governance Technical Specification

> **Document ID**: GOV  
> **Version**: V1.2  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-13  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial release |
| 1.1.0 | 2026-01-13 | Added §12 Semantic Confidence Governance, §13 Decision Artifact Requirements, §14 Explicit Non-Goals, updated BRD mappings |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |

---

## 1. Overview

The governance layer enforces policies, security boundaries, and budget limits across all 
platform operations. It operates as a thin evaluation layer that delegates decisions without 
persisting state or performing logging directly.

## 2. Governance Hook Requirements

### 2.1 Hook Architecture

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-HOOK-001 | Governance hooks MUST be thin evaluation layers that delegate to PolicyEngine and SecurityRedactor without persistence or logging | MUST | BRD-GOV-051 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-002 | All hook methods MUST return a `HookDecision` dataclass containing: `allowed` (bool), `reason` (str), `scrubbed_payload` (Dict), and `metadata` (Dict) | MUST | BRD-GOV-022, BRD-GOV-052 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-003 | Callers MUST emit trace events; hooks SHALL NOT perform logging directly | MUST | BRD-GOV-024, BRD-GOV-053 | 1.1 | 13 Jan 2026 | — |


### 2.2 Orchestrator Boundary Hooks

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-HOOK-010 | `before_step` MUST be invoked before every orchestration step execution | MUST | BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-011 | `before_step` MUST enforce `max_steps` limit when configured and return `allowed=False` with reason `step_limit_exceeded` when exceeded | MUST | BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-012 | `before_flow` MUST be invoked before flow execution to validate all branch conditions against the BranchGate | MUST | BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-013 | `before_flow` MUST be invoked before flow execution to validate all loop stop conditions against the LoopGate | MUST | BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-014 | `after_run` MUST be invoked before run completion with redacted output | MUST | BRD-GOV-014, BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-015 | `before_autonomy` MUST evaluate autonomy level against PolicyEngine before allowing autonomous operations | MUST | BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |


### 2.3 Tool Invocation Hooks

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-HOOK-020 | `before_tool` MUST be invoked before every tool execution | MUST | BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-021 | `before_tool` MUST evaluate tool against PolicyEngine allow/block lists | MUST | BRD-GOV-020, BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-022 | `before_tool` MUST consume budget via `BudgetEnforcer` when budget tracking is active and emit `budget_consumed` trace event | MUST | BRD-GOV-034, BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-023 | `before_tool` MUST emit `budget_exceeded` trace event and return `allowed=False` when budget limits are exceeded | MUST | BRD-GOV-034, BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-024 | `before_tool` MUST enforce `max_tool_calls` limit from Settings and track call count in `metadata` | MUST | BRD-GOV-050 | 1.1 | 13 Jan 2026 | — |


### 2.4 Model Invocation Hooks

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-HOOK-030 | `before_model` MUST be invoked before every LLM/model invocation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-031 | `before_model` MUST detect prompt injection patterns and return `allowed=False` with reason `prompt_injection_detected` when detected | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-032 | These prompt injection patterns MUST be blocked: `"ignore previous instructions"`, `"dump system prompt"`, `"reveal configuration"` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-033 | `before_model` MUST evaluate model name against PolicyEngine allow/block lists | MUST | BRD-GOV-021 | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-034 | `before_model` MUST enforce `max_tokens_per_call` per-call limit when configured | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-035 | `before_model` MUST enforce `max_tokens_per_run` cumulative limit when configured | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 2.5 Payload Size Hooks

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-HOOK-040 | `before_user_input` MUST enforce `max_payload_bytes` limit on user input responses | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-041 | `after_run` MUST enforce `max_payload_bytes` limit on run output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-042 | `after_run` MUST enforce `max_file_bytes` limit on output files | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 2.6 Agent Output Validation Hooks

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-HOOK-050 | `validate_agent_output` MUST detect control field violations using `detect_control_fields` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-051 | `validate_agent_output` MUST validate payload structure using `validate_payload_structure` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-HOOK-052 | Agent output containing control fields MUST be rejected with reason `agent_output_control_fields` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 3. Policy Engine Requirements

### 3.1 Policy Resolution

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-POL-001 | PolicyEngine MUST merge per-product overrides with base policy configuration using recursive dictionary merge | MUST | BRD-GOV-023 | 1.1 | 13 Jan 2026 | — |
| GOV-POL-002 | Per-product overrides in `products.<name>` SHALL take precedence over base policy values | SHALL | BRD-GOV-023 | 1.1 | 13 Jan 2026 | — |
| GOV-POL-003 | All string comparisons for tools and models MUST be case-insensitive (normalized to lowercase) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 3.2 Autonomy Policy

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-POL-010 | When `enforce=false`, autonomy checks SHALL return `allowed=True` with reason `policies_disabled` | SHALL | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-POL-011 | `FULL_AUTONOMY` MUST be rejected unless `allow_full_autonomy=true` in policy | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-POL-012 | Default policy MUST set `allow_full_autonomy: false` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 3.3 Tool Policy

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-POL-020 | Tools in `blocked_tools` list MUST be rejected with reason `tool_blocked` | MUST | BRD-GOV-020 | 1.1 | 13 Jan 2026 | — |
| GOV-POL-021 | When `allowed_tools` is non-empty, tools not in the allowlist MUST be rejected with reason `tool_not_in_allowlist` | MUST | BRD-GOV-020 | 1.1 | 13 Jan 2026 | — |
| GOV-POL-022 | When `allowed_tools` is empty, all tools SHALL be allowed except those explicitly blocked | SHALL | BRD-GOV-020 | 1.1 | 13 Jan 2026 | — |


### 3.4 Model Policy

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-POL-030 | Models in `blocked_models` list MUST be rejected with reason `model_blocked` | MUST | BRD-GOV-021 | 1.1 | 13 Jan 2026 | — |
| GOV-POL-031 | When `allowed_models` is non-empty, models not in the allowlist MUST be rejected with reason `model_not_in_allowlist` | MUST | BRD-GOV-021 | 1.1 | 13 Jan 2026 | — |
| GOV-POL-032 | When `allowed_models` is empty, all models SHALL be allowed except those explicitly blocked | SHALL | BRD-GOV-021 | 1.1 | 13 Jan 2026 | — |


---

## 4. Security Redaction Requirements

### 4.1 Redaction Configuration

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-SEC-001 | SecurityRedactor MUST apply key-based redaction for sensitive field names | MUST | BRD-GOV-012, BRD-GOV-013 | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-002 | SecurityRedactor MUST apply regex pattern-based redaction for inline secrets | MUST | BRD-GOV-012 | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-003 | SecurityRedactor MUST include PII patterns by default (`include_pii=True`) | MUST | BRD-GOV-012 | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-004 | Redacted values MUST be replaced with the mask string (default: `***REDACTED***`) | MUST | BRD-GOV-012 | 1.1 | 13 Jan 2026 | — |


### 4.2 Sensitive Key Detection

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-SEC-010 | These keys MUST trigger automatic redaction (case-insensitive substring match): `password`, `passwd`, `secret`, `token`, `api_key`, `apikey` | MUST | BRD-GOV-011 | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-011 | These keys MUST trigger automatic redaction: `authorization`, `bearer`, `cookie`, `session` | MUST | BRD-GOV-011 | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-012 | These keys MUST trigger automatic redaction: `private_key`, `ssh_key` | MUST | BRD-GOV-011 | 1.1 | 13 Jan 2026 | — |


### 4.3 Pattern-Based Redaction

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-SEC-020 | API key patterns matching `sk-[A-Za-z0-9_-]{3,}` MUST be redacted | MUST | BRD-GOV-011 | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-021 | API key assignments matching `api[_-]?key\s*[:=]\s*\S+` (case-insensitive) MUST be redacted | MUST | BRD-GOV-011 | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-022 | Bearer tokens matching `authorization\s*:\s*bearer\s+\S+` (case-insensitive) MUST be redacted | MUST | BRD-GOV-011 | 1.1 | 13 Jan 2026 | — |


### 4.4 PII Pattern Redaction

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-SEC-030 | Email addresses MUST be redacted | MUST | BRD-GOV-010 | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-031 | Credit card/PAN numbers (13-16 digits) MUST be redacted | MUST | BRD-GOV-010 | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-032 | Phone numbers (7-15 digits with optional separators) MUST be redacted | MUST | BRD-GOV-010 | 1.1 | 13 Jan 2026 | — |


### 4.5 Text Length Limits

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-SEC-040 | Text strings MUST be truncated at `max_text_length` (default: 4096 chars) with mask appended | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-SEC-041 | `max_text_length` MAY be configured via `SecurityRedactor` constructor | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 5. Budget Enforcement Requirements

### 5.1 Budget Resolution

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-BUD-001 | Budget MUST be resolved from BudgetPolicy using priority: flow_type override > sensitivity_class override > defaults | MUST | BRD-GOV-030 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-002 | BudgetState MUST be initialized with all counters at zero and `exceeded=False` | MUST | BRD-GOV-030 | 1.1 | 13 Jan 2026 | — |


### 5.2 Budget Limits

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-BUD-010 | Maximum reasoning passes MUST be enforced | MUST | BRD-GOV-030, BRD-GOV-031 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-011 | Maximum tool invocations MUST be enforced | MUST | BRD-GOV-030, BRD-GOV-031 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-012 | Maximum parallel calls MUST be enforced | MUST | BRD-GOV-030, BRD-GOV-031 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-013 | Maximum cost units MUST be enforced | MUST | BRD-GOV-030, BRD-GOV-031 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-014 | Latency bucket ceiling MUST be enforced | MUST | BRD-GOV-030, BRD-GOV-031 | 1.1 | 13 Jan 2026 | — |


### 5.3 Budget Consumption

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-BUD-020 | `consume_budget` MUST update BudgetState and return tuple of `(allowed, reason)` | MUST | BRD-GOV-033 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-021 | Latency bucket observations MUST only increase (LOW→MED→HIGH), never decrease | MUST | BRD-GOV-033 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-022 | Violations MUST be accumulated in `violations` list | MUST | BRD-GOV-033 | 1.1 | 13 Jan 2026 | — |


### 5.4 Budget Exceed Actions

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-BUD-030 | When `action_on_exceed=FAIL`, budget violations MUST return `allowed=False` | MUST | BRD-GOV-032 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-031 | When `action_on_exceed=HITL`, budget violations MUST trigger human-in-the-loop escalation | MUST | BRD-GOV-032 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-032 | When `action_on_exceed=DEGRADE`, system MUST attempt degradation to `degraded_budget` limits | MUST | BRD-GOV-032 | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-033 | If degradation is not possible (no `degraded_budget` or already at degraded limits), system MUST return `allowed=False` | MUST | BRD-GOV-032 | 1.1 | 13 Jan 2026 | — |


### 5.5 Reasoning Budget

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-BUD-040 | ReasoningBudget with `max_passes=3` MUST convert to Budget with `max_reasoning_passes=3` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-BUD-041 | ReasoningBudget defaults: `max_passes=3`, `max_tool_calls=5`, `max_parallel_calls=3`, `escalate_on_exceed=false` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 6. Gate Validation Requirements

### 6.1 Gate Architecture

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-GATE-001 | All gates MUST implement the `Gate` protocol with `gate_name` attribute and `evaluate` method | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-002 | GateRegistry MUST support registration, lookup, and evaluation of all gates | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-003 | Default gates (branch, loop, plan, critic, retrieval) MUST be auto-registered on module import | MUST | BRD-AUTO-044 | 1.1 | 13 Jan 2026 | — |


### 6.2 Branch Gate

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-GATE-010 | BranchGate MUST validate all branch conditions in FlowDef before execution | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-011 | Branch conditions MUST have a `condition` clause; missing clause produces error `branch.{step_id}.missing_condition` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-012 | Condition paths MUST start with `steps` or `artifacts` root | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-013 | Steps path format MUST be `steps.<id>.output.<field>` with minimum 4 parts | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-014 | Artifact path format MUST have minimum 3 parts | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-015 | Referenced step IDs in `then` and `else` MUST exist in flow | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.3 Branch Condition Disallowed Segments

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-GATE-020 | MUST be blocked in branch conditions | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-021 | MUST be blocked in branch conditions | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-022 | MUST be blocked in branch conditions | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.4 Loop Gate

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-GATE-030 | LoopGate MUST validate all `loop` step conditions | MUST | BRD-AUTO-041, BRD-AUTO-045 | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-031 | Loop steps MUST have a `stop_condition`; missing produces error `loop.{step_id}.missing_stop_condition` | MUST | BRD-AUTO-041, BRD-AUTO-045 | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-032 | `iteration_step` references MUST point to existing step IDs | MUST | BRD-AUTO-041, BRD-AUTO-045 | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-033 | `after_step` references MUST point to existing step IDs | MUST | BRD-AUTO-041, BRD-AUTO-045 | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-034 | Stop condition paths MUST pass BranchGate path validation | MUST | BRD-AUTO-041, BRD-AUTO-045 | 1.1 | 13 Jan 2026 | — |


### 6.5 Plan Gate

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-GATE-040 | PlanGate MUST validate each step in ActionPlan before execution | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-041 | Tool calls MUST be rejected if tool not in `allowed_tools` list (when list is non-empty) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-042 | Tool calls MUST be rejected if tool is not registered in ToolRegistry | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-043 | Agent calls MUST be rejected if agent not in `allowed_agents` list (when list is non-empty) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-044 | Agent calls MUST be rejected if agent is not registered in AgentRegistry | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-045 | Tools with `has_side_effects=True` descriptor MUST flag step index in `side_effect_indices` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-046 | Each plan step MUST consume budget; budget exceeded triggers rejection or truncation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.6 Plan Gate Result Statuses

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-GATE-050 | PlanGate MUST return status `APPROVED` when all steps are approved and no HITL review is required | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-051 | PlanGate MUST return status `REQUIRES_HITL` when side-effect steps require human review | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-052 | PlanGate MUST return status `TRUNCATED` when partial approval is granted due to budget and `allow_partial=True` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-053 | PlanGate MUST return status `REJECTED` when the plan cannot be executed | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.7 Critic Gate

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-GATE-060 | CriticGate MUST validate critic recommendations against allowed actions | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-061 | `NONE` action MUST always be allowed | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-062 | `USER_INPUT` action MUST only be allowed when `allow_user_input=True` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-063 | `HITL` action MUST only be allowed when `allow_hitl=True` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-064 | `FETCH_MORE_EVIDENCE` action MUST only be allowed when `allow_fetch=True` AND `budget_remaining > 0` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-065 | Disallowed recommendations MUST fall back to `NONE` with reason `recommendation_blocked` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.8 Retrieval Gate

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-GATE-070 | RetrievalGate MUST resolve allowed sources using priority: flow override > product override > global policy > empty | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-071 | Sources in `blocked_sources` (global or product-level) MUST be rejected | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-072 | Default allowed sources: `runs:current_product`, `trace_events`, `knowledge:approved_docs` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-GATE-073 | Default blocked sources: `runs:other_products` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 7. Demo Safety Limit Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-DEMO-001 | Maximum orchestration steps MUST be enforced | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEMO-002 | Maximum tool invocations MUST be enforced | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEMO-003 | Maximum payload size MUST be enforced (64KB) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEMO-004 | Maximum tokens per model call MUST be enforced | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEMO-005 | Total tokens per run MAY be enforced when configured | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 8. Per-Product Override Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-PROD-001 | Per-product overrides in `products.<name>` MUST be merged with base policies | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-PROD-002 | Per-product `allowed_tools` MUST restrict tool usage to listed tools only | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-PROD-003 | Per-product `allowed_models` MUST restrict model usage to listed models only | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-PROD-004 | Per-product `max_steps` MUST override global `max_steps` limit | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-PROD-005 | Per-product `retrieval_allowed_sources` MUST override global retrieval policy | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-PROD-006 | Per-product `retrieval_allowed_sources_by_flow` MUST provide flow-specific source restrictions | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 9. Traceability Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-TRACE-001 | All hook decisions MUST include scrubbed payload suitable for tracing | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-TRACE-002 | Budget consumption MUST emit `budget_consumed` trace event with state | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-TRACE-003 | Budget exceeded MUST emit `budget_exceeded` trace event with limit, state, action_taken, and violations | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-TRACE-004 | HITL escalation MUST emit `hitl_escalation_triggered` trace event with reason and context | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-TRACE-005 | All redacted payloads MUST be included in `scrubbed_payload` field of HookDecision | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 10. Policy Configuration Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-CFG-001 | Policy configuration MUST set `enforce: true` by default | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CFG-002 | Policy configuration MUST set `allow_full_autonomy: false` by default | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CFG-003 | Empty `allowed_tools` list MUST mean all registered tools are allowed | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CFG-004 | Empty `allowed_models` list MUST mean all models are allowed | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CFG-005 | `retrieval_policy` MUST define both `allowed_sources` and `blocked_sources` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CFG-006 | Product `hello_world` MUST be restricted to `echo_tool` and `gpt-4o-mini` only | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CFG-007 | Product `ade` MUST have `allow_full_autonomy: false` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 11. Control Field Validation

### 11.1 Forbidden Control Fields

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-CTRL-001 | MUST NOT appear in agent output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CTRL-002 | MUST NOT appear in agent output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CTRL-003 | MUST NOT appear in agent output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CTRL-004 | MUST NOT appear in agent output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CTRL-005 | MUST NOT appear in agent output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CTRL-006 | MUST NOT appear in agent output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CTRL-007 | MUST NOT appear in agent output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 11.2 Detection Rules

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-CTRL-010 | Control field detection MUST check all nesting levels of the payload | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CTRL-011 | Control field detection MUST be case-sensitive | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-CTRL-012 | Detection MUST return list of all found control fields | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 12. Semantic Confidence Governance (Added: 2026-01-13)

> **Source**: BRD-GOV-CONF-001...007, INV-3

### 12.1 Confidence Threshold Enforcement

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-SEM-CONF-001 | `check_semantic_confidence` hook MUST be called after semantic interpretation | MUST | BRD-GOV-CONF-001 | 1.1 | 13 Jan 2026 | — |
| GOV-SEM-CONF-002 | Default confidence threshold MUST be `0.7` | MUST | BRD-GOV-026, BRD-GOV-CONF-002 | 1.1 | 13 Jan 2026 | — |
| GOV-SEM-CONF-003 | Threshold MUST be configurable in `configs/app.yaml` under `semantic.default_confidence_threshold` | MUST | BRD-GOV-CONF-003 | 1.1 | 13 Jan 2026 | — |
| GOV-SEM-CONF-004 | Per-product override MUST be supported in `configs/products.yaml` under `by_product.<product>.semantic_confidence_threshold` | MUST | BRD-GOV-063, BRD-GOV-CONF-004 | 1.1 | 13 Jan 2026 | — |
| GOV-SEM-CONF-005 | Effective confidence = `min(envelope.confidence, validation.revised_confidence)` | MUST | BRD-GOV-CONF-005 | 1.1 | 13 Jan 2026 | — |
| GOV-SEM-CONF-006 | If effective confidence < threshold, hook MUST return `allowed=False` with `reason=confidence_below_threshold` | MUST | BRD-GOV-CONF-006 | 1.1 | 13 Jan 2026 | — |
| GOV-SEM-CONF-007 | Confidence check MUST emit `semantic_confidence_checked` trace event | MUST | BRD-GOV-CONF-007 | 1.1 | 13 Jan 2026 | — |


### 12.2 Confidence Hook Signature


### 12.3 Configuration Schema

**Platform Default** (`configs/app.yaml`):

**Per-Product Override** (`configs/products.yaml`):

---

## 13. Decision Artifact Requirements (Added: 2026-01-13)

> **Source**: BRD-GOV-045...047, INV-4

### 13.1 Decision Artifact Structure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-DEC-001 | Every gated decision MUST produce a `DecisionArtifact` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-002 | `DecisionArtifact` MUST include: `decision_id` (UUID) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-003 | `DecisionArtifact` MUST include: `options_considered` (list of alternatives) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-004 | `DecisionArtifact` MUST include: `evidence_refs` (list of supporting evidence) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-005 | `DecisionArtifact` MUST include: `critique_input` (critic evaluation if applicable) | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-006 | `DecisionArtifact` MUST include: `choice` (selected option) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-007 | `DecisionArtifact` MUST include: `justification` (reasoning for choice) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-008 | `DecisionArtifact` MUST include: `confidence` (0.0-1.0) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-009 | `DecisionArtifact` MUST be immutable once persisted | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

**DecisionArtifact Schema**:


### 13.2 Artifact Persistence

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GOV-DEC-PERS-001 | Decision artifacts MUST be stored in `run_context.artifacts` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-PERS-002 | Artifact key MUST be `decision.{decision_id}` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-PERS-003 | Artifact creation MUST emit `decision_artifact_created` trace event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GOV-DEC-PERS-004 | Artifacts MUST NOT be modified after creation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 14. Explicit Non-Goals (Added: 2026-01-13)

> **Governance MUST NOT**:

| Non-Goal | Rationale | Violation Example |
|----------|-----------|-------------------|
| Bypassable hooks | Violates INV-6 | Developer flag disables governance |
| Soft limits | Budget exhaustion must be enforced | Warning logged but run continues |
| Agent-controlled policies | Violates INV-2 | Agent modifies its own permissions |
| Hidden policy decisions | Violates auditability | Policy check without trace event |
| Runtime policy modification | Governance is config-driven | Code changes policy at runtime |
| Probabilistic enforcement | Governance is deterministic | Random sampling of policy checks |

---
