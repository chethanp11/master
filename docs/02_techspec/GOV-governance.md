# Governance Technical Specification

> **Document ID**: GOV  
> **Version**: 1.0.0  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-12

---

## 1. Overview

The governance layer enforces policies, security boundaries, and budget limits across all 
platform operations. It operates as a thin evaluation layer that delegates decisions without 
persisting state or performing logging directly.

### 1.1 Implementation References

| Component | File |
|-----------|------|
| Governance Hooks | `core/governance/hooks.py` |
| Policy Engine | `core/governance/policies.py` |
| Security Redactor | `core/governance/security.py` |
| Budget Enforcement | `core/governance/budgeting.py` |
| Unified Gates | `core/governance/gates.py` |
| Policy Config | `configs/policies.yaml` |

---

## 2. Governance Hook Requirements

### 2.1 Hook Architecture

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-HOOK-001** | [V1] Governance hooks MUST be thin evaluation layers that delegate to PolicyEngine and SecurityRedactor without persistence or logging | MUST |
| **GOV-HOOK-002** | [V1] All hook methods MUST return a `HookDecision` dataclass containing: `allowed` (bool), `reason` (str), `scrubbed_payload` (Dict), and `metadata` (Dict) | MUST |
| **GOV-HOOK-003** | [V1] Callers MUST emit trace events; hooks SHALL NOT perform logging directly | MUST |

**Implementation**: `core/governance/hooks.py`

### 2.2 Orchestrator Boundary Hooks

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-HOOK-010** | [V1] `before_step` MUST be invoked before every orchestration step execution | MUST |
| **GOV-HOOK-011** | [V1] `before_step` MUST enforce `max_steps` limit when configured and return `allowed=False` with reason `step_limit_exceeded` when exceeded | MUST |
| **GOV-HOOK-012** | [V1] `before_flow` MUST be invoked before flow execution to validate all branch conditions against the BranchGate | MUST |
| **GOV-HOOK-013** | [V1] `before_flow` MUST be invoked before flow execution to validate all loop stop conditions against the LoopGate | MUST |
| **GOV-HOOK-014** | [V1] `after_run` MUST be invoked before run completion with redacted output | MUST |
| **GOV-HOOK-015** | [V1] `before_autonomy` MUST evaluate autonomy level against PolicyEngine before allowing autonomous operations | MUST |

**Implementation**: `core/governance/hooks.py`

### 2.3 Tool Invocation Hooks

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-HOOK-020** | [V1] `before_tool` MUST be invoked before every tool execution | MUST |
| **GOV-HOOK-021** | [V1] `before_tool` MUST evaluate tool against PolicyEngine allow/block lists | MUST |
| **GOV-HOOK-022** | [V1] `before_tool` MUST consume budget via `BudgetEnforcer` when budget tracking is active and emit `budget_consumed` trace event | MUST |
| **GOV-HOOK-023** | [V1] `before_tool` MUST emit `budget_exceeded` trace event and return `allowed=False` when budget limits are exceeded | MUST |
| **GOV-HOOK-024** | [V1] `before_tool` MUST enforce `max_tool_calls` limit from Settings and track call count in `metadata` | MUST |

**Implementation**: `core/governance/hooks.py`

### 2.4 Model Invocation Hooks

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-HOOK-030** | [V1] `before_model` MUST be invoked before every LLM/model invocation | MUST |
| **GOV-HOOK-031** | [V1] `before_model` MUST detect prompt injection patterns and return `allowed=False` with reason `prompt_injection_detected` when detected | MUST |
| **GOV-HOOK-032** | [V1] These prompt injection patterns MUST be blocked: `"ignore previous instructions"`, `"dump system prompt"`, `"reveal configuration"` | MUST |
| **GOV-HOOK-033** | [V1] `before_model` MUST evaluate model name against PolicyEngine allow/block lists | MUST |
| **GOV-HOOK-034** | [V1] `before_model` MUST enforce `max_tokens_per_call` per-call limit when configured | MUST |
| **GOV-HOOK-035** | [V1] `before_model` MUST enforce `max_tokens_per_run` cumulative limit when configured | MUST |

**Implementation**: `core/governance/hooks.py`

### 2.5 Payload Size Hooks

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-HOOK-040** | [V1] `before_user_input` MUST enforce `max_payload_bytes` limit on user input responses | MUST |
| **GOV-HOOK-041** | [V1] `after_run` MUST enforce `max_payload_bytes` limit on run output | MUST |
| **GOV-HOOK-042** | [V1] `after_run` MUST enforce `max_file_bytes` limit on output files | MUST |

**Implementation**: `core/governance/hooks.py`

### 2.6 Agent Output Validation Hooks

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-HOOK-050** | [V1] `validate_agent_output` MUST detect control field violations using `detect_control_fields` | MUST |
| **GOV-HOOK-051** | [V1] `validate_agent_output` MUST validate payload structure using `validate_payload_structure` | MUST |
| **GOV-HOOK-052** | [V1] Agent output containing control fields MUST be rejected with reason `agent_output_control_fields` | MUST |

**Implementation**: `core/governance/hooks.py`

---

## 3. Policy Engine Requirements

### 3.1 Policy Resolution

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-POL-001** | [V1] PolicyEngine MUST merge per-product overrides with base policy configuration using recursive dictionary merge | MUST |
| **GOV-POL-002** | [V1] Per-product overrides in `products.<name>` SHALL take precedence over base policy values | SHALL |
| **GOV-POL-003** | [V1] All string comparisons for tools and models MUST be case-insensitive (normalized to lowercase) | MUST |

**Implementation**: `core/governance/policies.py`

### 3.2 Autonomy Policy

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-POL-010** | [V1] When `enforce=false`, autonomy checks SHALL return `allowed=True` with reason `policies_disabled` | SHALL |
| **GOV-POL-011** | [V1] `FULL_AUTONOMY` MUST be rejected unless `allow_full_autonomy=true` in policy | MUST |
| **GOV-POL-012** | [V1] Default policy MUST set `allow_full_autonomy: false` | MUST |

**Implementation**: `core/governance/policies.py`

### 3.3 Tool Policy

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-POL-020** | [V1] Tools in `blocked_tools` list MUST be rejected with reason `tool_blocked` | MUST |
| **GOV-POL-021** | [V1] When `allowed_tools` is non-empty, tools not in the allowlist MUST be rejected with reason `tool_not_in_allowlist` | MUST |
| **GOV-POL-022** | [V1] When `allowed_tools` is empty, all tools SHALL be allowed except those explicitly blocked | SHALL |

**Implementation**: `core/governance/policies.py`

### 3.4 Model Policy

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-POL-030** | [V1] Models in `blocked_models` list MUST be rejected with reason `model_blocked` | MUST |
| **GOV-POL-031** | [V1] When `allowed_models` is non-empty, models not in the allowlist MUST be rejected with reason `model_not_in_allowlist` | MUST |
| **GOV-POL-032** | [V1] When `allowed_models` is empty, all models SHALL be allowed except those explicitly blocked | SHALL |

**Implementation**: `core/governance/policies.py`

---

## 4. Security Redaction Requirements

### 4.1 Redaction Configuration

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-SEC-001** | [V1] SecurityRedactor MUST apply key-based redaction for sensitive field names | MUST |
| **GOV-SEC-002** | [V1] SecurityRedactor MUST apply regex pattern-based redaction for inline secrets | MUST |
| **GOV-SEC-003** | [V1] SecurityRedactor MUST include PII patterns by default (`include_pii=True`) | MUST |
| **GOV-SEC-004** | [V1] Redacted values MUST be replaced with the mask string (default: `***REDACTED***`) | MUST |

**Implementation**: `core/governance/security.py`

### 4.2 Sensitive Key Detection

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-SEC-010** | [V1] These keys MUST trigger automatic redaction (case-insensitive substring match): `password`, `passwd`, `secret`, `token`, `api_key`, `apikey` | MUST |
| **GOV-SEC-011** | [V1] These keys MUST trigger automatic redaction: `authorization`, `bearer`, `cookie`, `session` | MUST |
| **GOV-SEC-012** | [V1] These keys MUST trigger automatic redaction: `private_key`, `ssh_key` | MUST |

**Implementation**: `core/governance/security.py`

### 4.3 Pattern-Based Redaction

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-SEC-020** | [V1] API key patterns matching `sk-[A-Za-z0-9_-]{3,}` MUST be redacted | MUST |
| **GOV-SEC-021** | [V1] API key assignments matching `api[_-]?key\s*[:=]\s*\S+` (case-insensitive) MUST be redacted | MUST |
| **GOV-SEC-022** | [V1] Bearer tokens matching `authorization\s*:\s*bearer\s+\S+` (case-insensitive) MUST be redacted | MUST |

**Implementation**: `core/governance/security.py`

### 4.4 PII Pattern Redaction

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-SEC-030** | [V1] Email addresses MUST be redacted | MUST |
| **GOV-SEC-031** | [V1] Credit card/PAN numbers (13-16 digits) MUST be redacted | MUST |
| **GOV-SEC-032** | [V1] Phone numbers (7-15 digits with optional separators) MUST be redacted | MUST |

**Implementation**: `core/governance/security.py`

### 4.5 Text Length Limits

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-SEC-040** | [V1] Text strings MUST be truncated at `max_text_length` (default: 4096 chars) with mask appended | MUST |
| **GOV-SEC-041** | [V1] `max_text_length` MAY be configured via `SecurityRedactor` constructor | MAY |

**Implementation**: `core/governance/security.py`

---

## 5. Budget Enforcement Requirements

### 5.1 Budget Resolution

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-BUD-001** | [V1] Budget MUST be resolved from BudgetPolicy using priority: flow_type override > sensitivity_class override > defaults | MUST |
| **GOV-BUD-002** | [V1] BudgetState MUST be initialized with all counters at zero and `exceeded=False` | MUST |

**Implementation**: `core/governance/budgeting.py`

### 5.2 Budget Limits

| ID | Parameter | Default | Requirement | Level |
|----|-----------|---------|-------------|-------|
| **GOV-BUD-010** | `max_reasoning_passes` | 3 | Maximum reasoning passes MUST be enforced | MUST |
| **GOV-BUD-011** | `max_tool_calls` | 10 | Maximum tool invocations MUST be enforced | MUST |
| **GOV-BUD-012** | `max_parallel_calls` | 5 | Maximum parallel calls MUST be enforced | MUST |
| **GOV-BUD-013** | `max_cost_units` | 20 | Maximum cost units MUST be enforced | MUST |
| **GOV-BUD-014** | `latency_ceiling` | "HIGH" | Latency bucket ceiling MUST be enforced | MUST |

**Implementation**: `core/governance/budgeting.py`

### 5.3 Budget Consumption

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-BUD-020** | [V1] `consume_budget` MUST update BudgetState and return tuple of `(allowed, reason)` | MUST |
| **GOV-BUD-021** | [V1] Latency bucket observations MUST only increase (LOW→MED→HIGH), never decrease | MUST |
| **GOV-BUD-022** | [V1] Violations MUST be accumulated in `violations` list | MUST |

**Implementation**: `core/governance/budgeting.py`

### 5.4 Budget Exceed Actions

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-BUD-030** | [V1] When `action_on_exceed=FAIL`, budget violations MUST return `allowed=False` | MUST |
| **GOV-BUD-031** | [V1] When `action_on_exceed=HITL`, budget violations MUST trigger human-in-the-loop escalation | MUST |
| **GOV-BUD-032** | [V1] When `action_on_exceed=DEGRADE`, system MUST attempt degradation to `degraded_budget` limits | MUST |
| **GOV-BUD-033** | [V1] If degradation is not possible (no `degraded_budget` or already at degraded limits), system MUST return `allowed=False` | MUST |

**Implementation**: `core/governance/budgeting.py`

### 5.5 Reasoning Budget

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-BUD-040** | [V1] ReasoningBudget with `max_passes=3` MUST convert to Budget with `max_reasoning_passes=3` | MUST |
| **GOV-BUD-041** | [V1] ReasoningBudget defaults: `max_passes=3`, `max_tool_calls=5`, `max_parallel_calls=3`, `escalate_on_exceed=false` | MUST |

**Implementation**: `core/governance/budgeting.py`

---

## 6. Gate Validation Requirements

### 6.1 Gate Architecture

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-GATE-001** | [V1] All gates MUST implement the `Gate` protocol with `gate_name` attribute and `evaluate` method | MUST |
| **GOV-GATE-002** | [V1] GateRegistry MUST support registration, lookup, and evaluation of all gates | MUST |
| **GOV-GATE-003** | [V1] Default gates (branch, loop, plan, critic, retrieval) MUST be auto-registered on module import | MUST |

**Implementation**: `core/governance/gates.py`

### 6.2 Branch Gate

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-GATE-010** | [V1] BranchGate MUST validate all branch conditions in FlowDef before execution | MUST |
| **GOV-GATE-011** | [V1] Branch conditions MUST have a `condition` clause; missing clause produces error `branch.{step_id}.missing_condition` | MUST |
| **GOV-GATE-012** | [V1] Condition paths MUST start with `steps` or `artifacts` root | MUST |
| **GOV-GATE-013** | [V1] Steps path format MUST be `steps.<id>.output.<field>` with minimum 4 parts | MUST |
| **GOV-GATE-014** | [V1] Artifact path format MUST have minimum 3 parts | MUST |
| **GOV-GATE-015** | [V1] Referenced step IDs in `then` and `else` MUST exist in flow | MUST |

**Implementation**: `core/governance/gates.py`

### 6.3 Branch Condition Disallowed Segments

| ID | Disallowed Segment | Requirement | Level |
|----|-------------------|-------------|-------|
| **GOV-GATE-020** | `raw_text`, `content`, `prompt` | MUST be blocked in branch conditions | MUST |
| **GOV-GATE-021** | `transcript`, `free_text`, `user_input` | MUST be blocked in branch conditions | MUST |
| **GOV-GATE-022** | `content_ref` | MUST be blocked in branch conditions | MUST |

**Implementation**: `core/governance/gates.py`

### 6.4 Loop Gate

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-GATE-030** | [V1] LoopGate MUST validate all `loop` step conditions | MUST |
| **GOV-GATE-031** | [V1] Loop steps MUST have a `stop_condition`; missing produces error `loop.{step_id}.missing_stop_condition` | MUST |
| **GOV-GATE-032** | [V1] `iteration_step` references MUST point to existing step IDs | MUST |
| **GOV-GATE-033** | [V1] `after_step` references MUST point to existing step IDs | MUST |
| **GOV-GATE-034** | [V1] Stop condition paths MUST pass BranchGate path validation | MUST |

**Implementation**: `core/governance/gates.py`

### 6.5 Plan Gate

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-GATE-040** | [V1] PlanGate MUST validate each step in ActionPlan before execution | MUST |
| **GOV-GATE-041** | [V1] Tool calls MUST be rejected if tool not in `allowed_tools` list (when list is non-empty) | MUST |
| **GOV-GATE-042** | [V1] Tool calls MUST be rejected if tool is not registered in ToolRegistry | MUST |
| **GOV-GATE-043** | [V1] Agent calls MUST be rejected if agent not in `allowed_agents` list (when list is non-empty) | MUST |
| **GOV-GATE-044** | [V1] Agent calls MUST be rejected if agent is not registered in AgentRegistry | MUST |
| **GOV-GATE-045** | [V1] Tools with `has_side_effects=True` descriptor MUST flag step index in `side_effect_indices` | MUST |
| **GOV-GATE-046** | [V1] Each plan step MUST consume budget; budget exceeded triggers rejection or truncation | MUST |

**Implementation**: `core/governance/gates.py`

### 6.6 Plan Gate Result Statuses

| ID | Status | Description | Level |
|----|--------|-------------|-------|
| **GOV-GATE-050** | `APPROVED` | All steps approved, no HITL required | MUST |
| **GOV-GATE-051** | `REQUIRES_HITL` | Approved but human review required for side-effect steps | MUST |
| **GOV-GATE-052** | `TRUNCATED` | Partial approval due to budget (when `allow_partial=True`) | MUST |
| **GOV-GATE-053** | `REJECTED` | Plan cannot be executed | MUST |

**Implementation**: `core/governance/gates.py`

### 6.7 Critic Gate

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-GATE-060** | [V1] CriticGate MUST validate critic recommendations against allowed actions | MUST |
| **GOV-GATE-061** | [V1] `NONE` action MUST always be allowed | MUST |
| **GOV-GATE-062** | [V1] `USER_INPUT` action MUST only be allowed when `allow_user_input=True` | MUST |
| **GOV-GATE-063** | [V1] `HITL` action MUST only be allowed when `allow_hitl=True` | MUST |
| **GOV-GATE-064** | [V1] `FETCH_MORE_EVIDENCE` action MUST only be allowed when `allow_fetch=True` AND `budget_remaining > 0` | MUST |
| **GOV-GATE-065** | [V1] Disallowed recommendations MUST fall back to `NONE` with reason `recommendation_blocked` | MUST |

**Implementation**: `core/governance/gates.py`

### 6.8 Retrieval Gate

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-GATE-070** | [V1] RetrievalGate MUST resolve allowed sources using priority: flow override > product override > global policy > empty | MUST |
| **GOV-GATE-071** | [V1] Sources in `blocked_sources` (global or product-level) MUST be rejected | MUST |
| **GOV-GATE-072** | [V1] Default allowed sources: `runs:current_product`, `trace_events`, `knowledge:approved_docs` | MUST |
| **GOV-GATE-073** | [V1] Default blocked sources: `runs:other_products` | MUST |

**Implementation**: `core/governance/gates.py`

---

## 7. Demo Safety Limit Requirements

| ID | Parameter | Default | Requirement | Level |
|----|-----------|---------|-------------|-------|
| **GOV-DEMO-001** | `max_steps` | 20 | Maximum orchestration steps MUST be enforced | MUST |
| **GOV-DEMO-002** | `max_tool_calls` | 10 | Maximum tool invocations MUST be enforced | MUST |
| **GOV-DEMO-003** | `max_payload_bytes` | 65536 | Maximum payload size MUST be enforced (64KB) | MUST |
| **GOV-DEMO-004** | `max_tokens_per_call` | 512 | Maximum tokens per model call MUST be enforced | MUST |
| **GOV-DEMO-005** | `max_tokens_per_run` | null | Total tokens per run MAY be enforced when configured | MAY |

**Implementation**: `core/governance/hooks.py`, `core/config/schema.py`

---

## 8. Per-Product Override Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-PROD-001** | [V1] Per-product overrides in `products.<name>` MUST be merged with base policies | MUST |
| **GOV-PROD-002** | [V1] Per-product `allowed_tools` MUST restrict tool usage to listed tools only | MUST |
| **GOV-PROD-003** | [V1] Per-product `allowed_models` MUST restrict model usage to listed models only | MUST |
| **GOV-PROD-004** | [V1] Per-product `max_steps` MUST override global `max_steps` limit | MUST |
| **GOV-PROD-005** | [V1] Per-product `retrieval_allowed_sources` MUST override global retrieval policy | MUST |
| **GOV-PROD-006** | [V1] Per-product `retrieval_allowed_sources_by_flow` MUST provide flow-specific source restrictions | MUST |

**Implementation**: `configs/policies.yaml`, `core/governance/policies.py`

---

## 9. Traceability Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-TRACE-001** | [V1] All hook decisions MUST include scrubbed payload suitable for tracing | MUST |
| **GOV-TRACE-002** | [V1] Budget consumption MUST emit `budget_consumed` trace event with state | MUST |
| **GOV-TRACE-003** | [V1] Budget exceeded MUST emit `budget_exceeded` trace event with limit, state, action_taken, and violations | MUST |
| **GOV-TRACE-004** | [V1] HITL escalation MUST emit `hitl_escalation_triggered` trace event with reason and context | MUST |
| **GOV-TRACE-005** | [V1] All redacted payloads MUST be included in `scrubbed_payload` field of HookDecision | MUST |

**Implementation**: `core/governance/hooks.py`

---

## 10. Policy Configuration Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-CFG-001** | [V1] Policy configuration MUST set `enforce: true` by default | MUST |
| **GOV-CFG-002** | [V1] Policy configuration MUST set `allow_full_autonomy: false` by default | MUST |
| **GOV-CFG-003** | [V1] Empty `allowed_tools` list MUST mean all registered tools are allowed | MUST |
| **GOV-CFG-004** | [V1] Empty `allowed_models` list MUST mean all models are allowed | MUST |
| **GOV-CFG-005** | [V1] `retrieval_policy` MUST define both `allowed_sources` and `blocked_sources` | MUST |
| **GOV-CFG-006** | [V1] Product `hello_world` MUST be restricted to `echo_tool` and `gpt-4o-mini` only | MUST |
| **GOV-CFG-007** | [V1] Product `ade` MUST have `allow_full_autonomy: false` | MUST |

**Implementation**: `configs/policies.yaml`

---

## 11. Control Field Validation

### 11.1 Forbidden Control Fields

| ID | Field | Requirement | Level |
|----|-------|-------------|-------|
| **GOV-CTRL-001** | `next_step` | MUST NOT appear in agent output | MUST |
| **GOV-CTRL-002** | `retry` | MUST NOT appear in agent output | MUST |
| **GOV-CTRL-003** | `retry_instructions` | MUST NOT appear in agent output | MUST |
| **GOV-CTRL-004** | `branch` | MUST NOT appear in agent output | MUST |
| **GOV-CTRL-005** | `branching` | MUST NOT appear in agent output | MUST |
| **GOV-CTRL-006** | `branch_hint` | MUST NOT appear in agent output | MUST |
| **GOV-CTRL-007** | `branching_hint` | MUST NOT appear in agent output | MUST |

**Implementation**: `core/governance/hooks.py`

### 11.2 Detection Rules

| ID | Requirement | Level |
|----|-------------|-------|
| **GOV-CTRL-010** | [V1] Control field detection MUST check all nesting levels of the payload | MUST |
| **GOV-CTRL-011** | [V1] Control field detection MUST be case-sensitive | MUST |
| **GOV-CTRL-012** | [V1] Detection MUST return list of all found control fields | MUST |

**Implementation**: `core/governance/hooks.py`

---

## 12. Future Considerations

### 12.1 V1.1 Enhancements

| ID | Feature | Description |
|----|---------|-------------|
| **GOV-FUTURE-001** | Fine-grained permissions | Role-based access control |
| **GOV-FUTURE-002** | Audit logging | Persistent audit trail |
| **GOV-FUTURE-003** | Rate limiting | Per-user/product rate limits |

### 12.2 V2 Features

| ID | Feature | Description |
|----|---------|-------------|
| **GOV-FUTURE-010** | External policy engine | Integration with OPA/Cedar |
| **GOV-FUTURE-011** | Dynamic policies | Runtime policy updates |
| **GOV-FUTURE-012** | Policy versioning | Policy change tracking |

---

## 13. Traceability Matrix

| Requirement | Implementation | Test |
|-------------|----------------|------|
| GOV-HOOK-001 | `core/governance/hooks.py` | `tests/unit/core/governance/test_hooks.py` |
| GOV-POL-020 | `core/governance/policies.py` | `tests/unit/core/governance/test_policies.py` |
| GOV-SEC-010 | `core/governance/security.py` | `tests/unit/core/governance/test_security.py` |
| GOV-BUD-010 | `core/governance/budgeting.py` | `tests/unit/core/governance/test_budgeting.py` |
| GOV-GATE-010 | `core/governance/gates.py` | `tests/unit/core/governance/test_gates.py` |
