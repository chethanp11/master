# System Design: Spec Coverage Matrix

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  
> **Version**: 1.1  

> **Last Updated**: 2026-01-16  
> **Status**: V1 Release  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |

## Purpose

This document is the **heart of delta detection**. It maps every Tech Spec requirement ID to its implementation status, enabling mechanical planning:

```
Tech Spec IDs − Implemented IDs = Implementation Backlog
```

---

## Status Legend

| Status | Meaning |
|--------|---------|
| ✅ Implemented | Fully implemented and tested |
| 🟡 Partial | Partially implemented or missing edge cases |
| ❌ Not Implemented | Not yet started |
| 🧪 Experimental | Implemented but not production-ready |
| ⏸️ Deferred | Explicitly moved to future release |

---

## Coverage Summary

| Tech Spec | Total | ✅ | 🟡 | ❌ | Coverage |
|-----------|-------|-----|-----|-----|----------|
| [ORC-orchestration.md](#orchestration-orc) | ~115 | 113 | 0 | 2 | 98% |
| [AGT-agents-tools.md](#agents--tools-agt-tool) | ~50 | 45 | 3 | 2 | 90% |
| [GOV-governance.md](#governance-gov) | ~65 | 63 | 0 | 2 | 97% |
| [MEM-memory.md](#memory-mem) | ~45 | 43 | 2 | 0 | 96% |
| [INT-intelligence.md](#intelligence-int) | ~55 | 48 | 5 | 2 | 87% |
| [GW-gateway.md](#gateway-gw) | ~75 | 70 | 3 | 2 | 93% |
| [PROD-products.md](#products-prod) | ~50 | 47 | 1 | 2 | 94% |
| [ACC-acceptance.md](#acceptance-acc) | ~15 | 15 | 0 | 0 | 100% |

---

## Orchestration (ORC)

> Source: [../03_techspecs/ORC-orchestration.md](../03_techspecs/ORC-orchestration.md)

### Run Lifecycle (ORC-RUN)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| ORC-RUN-001 | Run status state machine (RUNNING, PAUSED, PENDING_HUMAN, etc.) | ✅ Implemented | `core/contracts/run_schema.py` | `trace: run_state_transition` | `tests/unit/core/test_run_schema.py` | RunStatus enum |
| ORC-RUN-002 | Valid state transitions enforced | ✅ Implemented | `core/orchestrator/state.py` | `trace: run_state_transition` | `tests/unit/core/test_state.py` | |
| ORC-RUN-003 | `can_transition()` validation | ✅ Implemented | `core/orchestrator/state.py` | — | `tests/unit/core/test_state.py` | InvalidTransitionError |
| ORC-RUN-004 | State transition trace events | ✅ Implemented | `core/orchestrator/run_lifecycle.py` | `trace: run_state_transition` | `tests/unit/core/test_run_lifecycle.py` | |
| ORC-RUN-010 | Run ID format `run_{timestamp}_{uuid8}` | ✅ Implemented | `core/orchestrator/run_lifecycle.py` | `trace: run_started` | `tests/unit/core/test_run_lifecycle.py` | |
| ORC-RUN-011 | RunRecord created with status RUNNING | ✅ Implemented | `core/orchestrator/run_lifecycle.py` | — | `tests/unit/core/test_run_lifecycle.py` | |
| ORC-RUN-012 | Pre-create StepRecords for all steps | ✅ Implemented | `core/orchestrator/run_lifecycle.py` | — | `tests/unit/core/test_run_lifecycle.py` | |
| ORC-RUN-013 | Initialize metadata counters | ✅ Implemented | `core/orchestrator/run_lifecycle.py` | — | `tests/unit/core/test_run_lifecycle.py` | |
| ORC-RUN-015 | `run_started` trace event | ✅ Implemented | `core/orchestrator/run_lifecycle.py` | `trace: run_started` | `tests/unit/core/test_run_lifecycle.py` | |
| ORC-RUN-020 | Payload size validation | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | 100KB limit |
| ORC-RUN-030 | Run completion → COMPLETED status | ✅ Implemented | `core/orchestrator/run_lifecycle.py` | `trace: run_completed` | `tests/integration/test_run_complete.py` | |
| ORC-RUN-040 | Run failure → FAILED status | ✅ Implemented | `core/orchestrator/run_lifecycle.py` | `trace: run_failed` | `tests/unit/core/test_run_lifecycle.py` | |

### Semantic Interpretation (ORC-SEM)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| ORC-SEM-001 | Semantic interpretation phase before planning | ✅ Implemented | `core/orchestrator/engine.py` | `trace: semantic_interpretation_started` | `tests/unit/core/orchestrator/test_semantic_phase.py` | Full lifecycle |
| ORC-SEM-002 | Skip with `skip_semantic_interpretation: true` | ✅ Implemented | `core/orchestrator/engine.py` | `trace: semantic_interpretation_skipped` | `tests/unit/core/orchestrator/test_semantic_phase.py` | Flow config option |
| ORC-SEM-010 | SemanticEnvelope Pydantic model | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | Full schema |
| ORC-SEM-011 | normalized_input field | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-012 | product_id field | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-013 | intent_type field | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-014 | entities list with Entity model | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-015 | constraints dict | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-016 | confidence float 0.0-1.0 | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-017 | ambiguities list | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-018 | proposed_next_action field | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-019 | parameters dict + interpretation_method | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-020 | NextAction enum (CONTINUE, ASK_USER, ABORT, NEEDS_APPROVAL) | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-030 | normalize_whitespace() | ✅ Implemented | `core/orchestrator/normalization.py` | — | `tests/unit/core/orchestrator/test_normalization.py` | |
| ORC-SEM-031 | deduplicate_entities() | ✅ Implemented | `core/orchestrator/normalization.py` | — | `tests/unit/core/orchestrator/test_normalization.py` | |
| ORC-SEM-032 | merge_constraints() | ✅ Implemented | `core/orchestrator/normalization.py` | — | `tests/unit/core/orchestrator/test_normalization.py` | |
| ORC-SEM-033 | apply_stable_ordering() | ✅ Implemented | `core/orchestrator/normalization.py` | — | `tests/unit/core/orchestrator/test_normalization.py` | |
| ORC-SEM-034 | coerce_types() | ✅ Implemented | `core/orchestrator/normalization.py` | — | `tests/unit/core/orchestrator/test_normalization.py` | |
| ORC-SEM-035 | apply_core_normalization() | ✅ Implemented | `core/orchestrator/normalization.py` | — | `tests/unit/core/orchestrator/test_normalization.py` | |
| ORC-SEM-040 | SEMANTIC_INTERPRETATION_STARTED trace | ✅ Implemented | `core/memory/tracing.py` | `trace: semantic_interpretation_started` | `tests/unit/core/orchestrator/test_semantic_phase.py` | |
| ORC-SEM-041 | SEMANTIC_INTERPRETATION_COMPLETED trace | ✅ Implemented | `core/memory/tracing.py` | `trace: semantic_interpretation_completed` | `tests/unit/core/orchestrator/test_semantic_phase.py` | |
| ORC-SEM-042 | SEMANTIC_VALIDATION_COMPLETED trace | ✅ Implemented | `core/memory/tracing.py` | `trace: semantic_validation_completed` | `tests/unit/core/orchestrator/test_semantic_phase.py` | |
| ORC-SEM-043 | SEMANTIC_STOP_ISSUED trace | ✅ Implemented | `core/memory/tracing.py` | `trace: semantic_stop_issued` | `tests/unit/core/orchestrator/test_semantic_phase.py` | |
| ORC-SEM-050 | check_semantic_confidence() hook | ✅ Implemented | `core/governance/hooks.py` | — | `tests/unit/core/governance/test_semantic_hooks.py` | |
| ORC-SEM-STOP-002 | ASK_USER → PAUSED_WAITING_FOR_USER | ✅ Implemented | `core/orchestrator/engine.py` | `trace: run_paused` | `tests/unit/core/orchestrator/test_semantic_phase.py` | |
| ORC-SEM-STOP-003 | ClarificationResponse model | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |
| ORC-SEM-STOP-005 | AbortResponse model | ✅ Implemented | `core/contracts/semantic_schema.py` | — | `tests/unit/core/contracts/test_semantic_schema.py` | |

### Step Execution (ORC-STEP)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| ORC-STEP-001 | Step types: agent, tool, tool_batch, human_approval, user_input, etc. | ✅ Implemented | `core/orchestrator/step_executor.py` | `trace: step_started` | `tests/unit/core/test_step_executor.py` | |
| ORC-STEP-010 | `agent` steps require `agent` field | ✅ Implemented | `core/contracts/flow_schema.py` | — | `tests/unit/core/test_flow_schema.py` | |
| ORC-STEP-011 | `tool` steps require `tool` field | ✅ Implemented | `core/contracts/flow_schema.py` | — | `tests/unit/core/test_flow_schema.py` | |
| ORC-STEP-020 | StepRecord with STARTED status | ✅ Implemented | `core/orchestrator/step_executor.py` | `trace: step_started` | `tests/unit/core/test_step_executor.py` | |
| ORC-STEP-021 | `before_step` permission check | ✅ Implemented | `core/orchestrator/step_executor.py` | `trace: before_step` | `tests/unit/core/test_step_executor.py` | |
| ORC-STEP-030 | Step retry policy | ✅ Implemented | `core/orchestrator/error_policy.py` | `trace: tool_call_retry_scheduled` | `tests/unit/core/test_error_policy.py` | |

### Pause/Resume (ORC-PAUSE, ORC-RESUME)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| ORC-PAUSE-001 | User input template rendering | ✅ Implemented | `core/orchestrator/user_input_handler.py` | — | `tests/unit/core/test_user_input.py` | |
| ORC-PAUSE-003 | ApprovalRecord with type INPUT | ✅ Implemented | `core/orchestrator/user_input_handler.py` | `trace: pending_user_input` | `tests/integration/test_user_input.py` | |
| ORC-PAUSE-005 | Run → PAUSED_WAITING_FOR_USER | ✅ Implemented | `core/orchestrator/user_input_handler.py` | `trace: run_paused` | `tests/integration/test_user_input.py` | |
| ORC-PAUSE-010 | Human approval payload | ✅ Implemented | `core/orchestrator/hitl.py` | `trace: pending_human` | `tests/integration/test_hitl.py` | |
| ORC-PAUSE-014 | Run → PENDING_HUMAN | ✅ Implemented | `core/orchestrator/hitl.py` | `trace: run_pending_human` | `tests/integration/test_hitl.py` | |
| ORC-RESUME-001 | Validate run in PAUSED_WAITING_FOR_USER | ✅ Implemented | `core/orchestrator/user_input_handler.py` | — | `tests/integration/test_resume.py` | |
| ORC-RESUME-020 | Validate run in PENDING_HUMAN | ✅ Implemented | `core/orchestrator/hitl.py` | — | `tests/integration/test_hitl.py` | |
| ORC-RESUME-022 | HITLService resolve approval | ✅ Implemented | `core/orchestrator/hitl.py` | `trace: run_resumed` | `tests/integration/test_hitl.py` | |

### Branching & Looping (ORC-BRANCH, ORC-LOOP)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| ORC-BRANCH-001 | Path-based conditions with operators | ✅ Implemented | `core/orchestrator/branching.py` | `trace: branch_evaluated` | `tests/unit/core/test_branching.py` | |
| ORC-BRANCH-002 | Composite conditions (all/any) | ✅ Implemented | `core/orchestrator/branching.py` | — | `tests/unit/core/test_branching.py` | |
| ORC-BRANCH-010 | Deterministic evaluation | ✅ Implemented | `core/orchestrator/branching.py` | `trace: branch_evaluated` | `tests/unit/core/test_branching.py` | |
| ORC-LOOP-001 | Stop conditions (confidence_threshold, etc.) | ✅ Implemented | `core/orchestrator/looping.py` | — | `tests/unit/core/test_looping.py` | |
| ORC-LOOP-010 | Initialize iteration_count | ✅ Implemented | `core/orchestrator/loop_executor.py` | `trace: loop_started` | `tests/unit/core/test_loop_executor.py` | |
| ORC-LOOP-016 | Terminate on stop/max_iters/budget | ✅ Implemented | `core/orchestrator/loop_executor.py` | `trace: loop_terminated` | `tests/unit/core/test_loop_executor.py` | |

### Plan Execution (ORC-PLAN)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| ORC-PLAN-001 | Plan from pending_plan or agent | ✅ Implemented | `core/orchestrator/plan_executor.py` | `trace: plan_proposed` | `tests/unit/core/test_plan_executor.py` | |
| ORC-PLAN-002 | Validate against ActionPlan schema | ✅ Implemented | `core/contracts/action_plan_schema.py` | — | `tests/unit/core/test_action_plan.py` | |

---

## Agents & Tools (AGT, TOOL)

> Source: [../03_techspecs/AGT-agents-tools.md](../03_techspecs/AGT-agents-tools.md)

### BaseAgent Contract (AGT-BASE)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| AGT-BASE-001 | Agents extend BaseAgent | ✅ Implemented | `core/agents/base.py` | — | `tests/unit/core/test_agent_base.py` | |
| AGT-BASE-002 | Agent `name` class attribute | ✅ Implemented | `core/agents/base.py` | — | `tests/unit/core/test_agent_registry.py` | |
| AGT-BASE-003 | Namespaced format `product.agent_name` | ✅ Implemented | `core/agents/registry.py` | — | `tests/unit/core/test_namespace.py` | |
| AGT-BASE-004 | Accept Settings in constructor | ✅ Implemented | `core/agents/base.py` | — | `tests/unit/core/test_agent_base.py` | |

### Agent Run Method (AGT-RUN)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| AGT-RUN-001 | `async run(ctx, params) -> AgentResult` | ✅ Implemented | `core/agents/base.py` | `trace: agent_invocation` | `tests/unit/core/test_agent_base.py` | |
| AGT-RUN-002 | Return AgentResult envelope | ✅ Implemented | `core/contracts/agent_schema.py` | — | `tests/unit/core/test_agent_schema.py` | |
| AGT-RUN-003 | No raw exceptions outward | ✅ Implemented | `core/agents/base.py` | — | `tests/unit/core/test_agent_base.py` | |

### Agent Behavioral Constraints (AGT-BEHAV)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| AGT-BEHAV-001 | Goal-driven, not prompt-driven | ✅ Implemented | `core/agents/base.py` | — | `tests/architecture/test_agent_advisory.py` | INV-1 |
| AGT-BEHAV-002 | No direct tool calls | ✅ Implemented | `core/agents/base.py` | — | `tests/architecture/test_agent_advisory.py` | INV-1 |
| AGT-BEHAV-003 | No state persistence | ✅ Implemented | `core/agents/base.py` | — | `tests/architecture/test_agent_advisory.py` | |
| AGT-BEHAV-005 | Emit trace events via hooks | ✅ Implemented | `core/agents/base.py` | `trace: agent_invocation` | `tests/unit/core/test_tracing.py` | |

### Agent Reasoning (AGT-REASON)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| AGT-REASON-001 | Bounded reasoning by phase | ✅ Implemented | `core/agents/reasoning_ladder.py` | — | `tests/unit/core/test_reasoning_ladder.py` | |
| AGT-REASON-004 | Confidence bounded 0.0-1.0 | ✅ Implemented | `core/contracts/advisory_schema.py` | — | `tests/unit/core/test_advisory_schema.py` | |
| AGT-REASON-005 | Expose options_considered, confidence | ✅ Implemented | `core/agents/advisory.py` | `artifact: advisory` | `tests/unit/core/test_advisory.py` | |

### Critic Constraints (AGT-CRIT)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| AGT-CRIT-001 | Critic is advisory only | ✅ Implemented | `core/agents/critic_evaluator.py` | — | `tests/unit/core/test_critic.py` | INV-2 |
| AGT-CRIT-002 | No flow routing or policy override | ✅ Implemented | `core/agents/critic_evaluator.py` | — | `tests/architecture/test_agent_advisory.py` | |
| AGT-CRIT-004 | `confidence_adjustment` bounded -1.0 to 1.0 | ✅ Implemented | `core/contracts/critic_schema.py` | — | `tests/unit/core/test_critic_schema.py` | |

### AgentResult Schema (AGT-ENV)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| AGT-ENV-001 | AgentResult: ok, data, error, meta | ✅ Implemented | `core/contracts/agent_schema.py` | — | `tests/unit/core/test_agent_schema.py` | |
| AGT-META-001 | AgentMeta includes agent_name | ✅ Implemented | `core/contracts/agent_schema.py` | — | `tests/unit/core/test_agent_schema.py` | |
| AGT-META-002 | AgentMeta includes role enum | ✅ Implemented | `core/contracts/agent_schema.py` | — | `tests/unit/core/test_agent_schema.py` | |

### Tool Contracts (TOOL)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| PROD-DEC-010 | `@tool` decorator registers factory | ✅ Implemented | `core/tools/base.py` | — | `tests/unit/core/test_tool_registry.py` | |
| PROD-DEC-011 | Tool extends BaseTool | ✅ Implemented | `core/tools/base.py` | — | `tests/unit/core/test_tool_base.py` | |
| — | Tool returns ToolResult | ✅ Implemented | `core/contracts/tool_schema.py` | `artifact: tool_result` | `tests/unit/core/test_tool_result.py` | |
| — | Tool execution deterministic | ✅ Implemented | `core/tools/executor.py` | — | `tests/architecture/test_determinism.py` | INV-4 |
| — | Tool errors captured in result | ✅ Implemented | `core/tools/executor.py` | `trace: tool_error` | `tests/unit/core/test_tool_errors.py` | |

---

## Governance (GOV)

> Source: [../03_techspecs/GOV-governance.md](../03_techspecs/GOV-governance.md)

### Hook Architecture (GOV-HOOK)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GOV-HOOK-001 | Thin evaluation layers, no persistence | ✅ Implemented | `core/governance/hooks.py` | — | `tests/unit/core/test_hooks.py` | |
| GOV-HOOK-002 | Return HookDecision dataclass | ✅ Implemented | `core/governance/hooks.py` | — | `tests/unit/core/test_hooks.py` | allowed, reason, scrubbed_payload |
| GOV-HOOK-003 | Callers emit trace, not hooks | ✅ Implemented | `core/governance/hooks.py` | — | `tests/unit/core/test_hooks.py` | |
| GOV-HOOK-010 | `before_step` before every step | ✅ Implemented | `core/governance/hooks.py` | `trace: before_step` | `tests/unit/core/test_hooks.py` | |
| GOV-HOOK-011 | `before_step` enforces max_steps | ✅ Implemented | `core/governance/hooks.py` | — | `tests/unit/core/test_hooks.py` | |
| GOV-HOOK-012 | `before_flow` validates branch conditions | ✅ Implemented | `core/governance/hooks.py` | — | `tests/unit/core/test_hooks.py` | |
| GOV-HOOK-020 | `before_tool` before every tool | ✅ Implemented | `core/governance/hooks.py` | `trace: before_tool` | `tests/unit/core/test_hooks.py` | |
| GOV-HOOK-021 | `before_tool` evaluates allow/block lists | ✅ Implemented | `core/governance/hooks.py` | — | `tests/unit/core/test_policy_lists.py` | |
| GOV-HOOK-022 | `before_tool` consumes budget | ✅ Implemented | `core/governance/hooks.py` | `trace: budget_consumed` | `tests/unit/core/test_budgeting.py` | |
| GOV-HOOK-030 | `before_model` before every LLM call | ✅ Implemented | `core/governance/hooks.py` | `trace: before_model` | `tests/unit/core/test_hooks.py` | |
| GOV-HOOK-031 | Detect prompt injection | ✅ Implemented | `core/governance/hooks.py` | — | `tests/unit/core/test_prompt_injection.py` | |
| GOV-HOOK-050 | `validate_agent_output` detects control fields | ✅ Implemented | `core/governance/hooks.py` | — | `tests/unit/core/test_output_validation.py` | |

### Policy Engine (GOV-POL)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GOV-POL-001 | Merge per-product overrides | ✅ Implemented | `core/governance/policies.py` | — | `tests/unit/core/test_policies.py` | |
| GOV-POL-003 | Case-insensitive string comparisons | ✅ Implemented | `core/governance/policies.py` | — | `tests/unit/core/test_policies.py` | |
| GOV-POL-010 | `enforce=false` allows all | ✅ Implemented | `core/governance/policies.py` | — | `tests/unit/core/test_policies.py` | |
| GOV-POL-020 | Blocked tools rejected | ✅ Implemented | `core/governance/policies.py` | `trace: policy_blocked` | `tests/unit/core/test_policy_lists.py` | |
| GOV-POL-030 | Blocked models rejected | ✅ Implemented | `core/governance/policies.py` | `trace: model_blocked` | `tests/unit/core/test_policy_lists.py` | |

### Security Redaction (GOV-SEC)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GOV-SEC-001 | Key-based redaction | ✅ Implemented | `core/governance/security.py` | `trace: pii_redacted` | `tests/unit/core/test_security.py` | |
| GOV-SEC-002 | Regex pattern-based redaction | ✅ Implemented | `core/governance/security.py` | — | `tests/unit/core/test_security.py` | |
| GOV-SEC-003 | PII patterns by default | ✅ Implemented | `core/governance/security.py` | — | `tests/unit/core/test_pii_redaction.py` | |
| GOV-SEC-010 | Redact password, secret, token, api_key | ✅ Implemented | `core/governance/security.py` | — | `tests/unit/core/test_security.py` | |
| GOV-SEC-020 | Redact `sk-*` API key patterns | ✅ Implemented | `core/governance/security.py` | — | `tests/unit/core/test_security.py` | |
| GOV-SEC-030 | Redact email addresses | ✅ Implemented | `core/governance/security.py` | — | `tests/unit/core/test_pii_redaction.py` | |
| GOV-SEC-031 | Redact credit card numbers | ✅ Implemented | `core/governance/security.py` | — | `tests/unit/core/test_pii_redaction.py` | |

### Budget Enforcement (GOV-BUD)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| — | Token budget tracked per run | ✅ Implemented | `core/governance/budgeting.py` | `trace: budget_updated` | `tests/unit/core/test_budgeting.py` | |
| — | Budget exceeded halts run | ✅ Implemented | `core/governance/budgeting.py` | `trace: budget_exceeded` | `tests/integration/test_budget_halt.py` | |

### Gates (GOV-GATE)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| — | GateRegistry with BaseGate ABC | ✅ Implemented | `core/governance/gates.py` | — | `tests/unit/core/test_gates.py` | |
| — | Gate returns GateResult | ✅ Implemented | `core/governance/gates.py` | `trace: gate_evaluated` | `tests/unit/core/test_gates.py` | |
| — | Gate failure pauses run | ✅ Implemented | `core/governance/gates.py` | `trace: gate_paused` | `tests/integration/test_gate_pause.py` | |

---

## Memory (MEM)

> Source: [../03_techspecs/MEM-memory.md](../03_techspecs/MEM-memory.md)

### Data Schemas (MEM-SCHEMA)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| MEM-SCHEMA-001 | RunRecord required fields | ✅ Implemented | `core/contracts/run_schema.py` | — | `tests/unit/core/test_run_schema.py` | run_id, product, flow, status |
| MEM-SCHEMA-002 | RunStatus enum | ✅ Implemented | `core/contracts/run_schema.py` | — | `tests/unit/core/test_run_schema.py` | RUNNING, PAUSED, etc. |
| MEM-SCHEMA-003 | StepRecord required fields | ✅ Implemented | `core/contracts/run_schema.py` | — | `tests/unit/core/test_run_schema.py` | run_id, step_id, status |
| MEM-SCHEMA-004 | StepStatus enum | ✅ Implemented | `core/contracts/run_schema.py` | — | `tests/unit/core/test_run_schema.py` | PENDING, STARTED, etc. |
| MEM-SCHEMA-005 | TraceEvent required fields | ✅ Implemented | `core/contracts/run_schema.py` | — | `tests/unit/core/test_run_schema.py` | event_id, run_id, kind |
| MEM-SCHEMA-006 | ApprovalRecord required fields | ✅ Implemented | `core/contracts/run_schema.py` | — | `tests/unit/core/test_run_schema.py` | approval_id, status |
| MEM-SCHEMA-007 | RunBundle aggregates records | ✅ Implemented | `core/contracts/run_schema.py` | — | `tests/unit/core/test_run_schema.py` | |

### MemoryBackend Interface (MEM-API)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| MEM-API-001 | Run lifecycle methods | ✅ Implemented | `core/memory/base.py` | — | `tests/unit/core/test_memory_backend.py` | create_run, update_run_status |
| MEM-API-002 | Step lifecycle methods | ✅ Implemented | `core/memory/base.py` | — | `tests/unit/core/test_memory_backend.py` | create_step, update_step |
| MEM-API-003 | Event persistence methods | ✅ Implemented | `core/memory/base.py` | — | `tests/unit/core/test_memory_backend.py` | add_event, add_events |
| MEM-API-004 | Approval lifecycle methods | ✅ Implemented | `core/memory/base.py` | — | `tests/unit/core/test_memory_backend.py` | create_approval, update_approval |
| MEM-API-005 | Query methods | ✅ Implemented | `core/memory/base.py` | — | `tests/unit/core/test_memory_backend.py` | get_run, get_run_bundle, list_runs |

### Backend Implementations (MEM-BACK)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| — | Pluggable backend interface | ✅ Implemented | `core/memory/base.py` | — | `tests/unit/core/test_memory_backend.py` | MemoryBackend ABC |
| — | In-memory backend for testing | ✅ Implemented | `core/memory/in_memory.py` | — | `tests/unit/core/test_in_memory.py` | |
| — | SQLite backend for persistence | ✅ Implemented | `core/memory/sqlite_backend.py` | — | `tests/integration/test_sqlite_backend.py` | |

### Tracing (MEM-TRACE)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| — | All events have timestamp | ✅ Implemented | `core/memory/tracing.py` | — | `tests/unit/core/test_tracing.py` | Auto-generated ts |
| — | Events linked to run ID | ✅ Implemented | `core/memory/tracing.py` | — | `tests/unit/core/test_tracing.py` | |
| — | Trace exportable as JSON | ✅ Implemented | `core/memory/tracing.py` | `artifact: trace.json` | `tests/unit/core/test_trace_export.py` | |
| — | SecurityRedactor applied to payloads | ✅ Implemented | `core/memory/tracing.py` | — | `tests/unit/core/test_tracing.py` | |

---

## Intelligence (INT)

> Source: [../03_techspecs/INT-intelligence.md](../03_techspecs/INT-intelligence.md)

### Advisory Agents (INT-ADV)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| INT-ADV-001 | Inherit from BaseAdvisoryAgent | ✅ Implemented | `core/agents/advisory.py` | — | `tests/unit/core/test_advisory.py` | |
| INT-ADV-002 | JSON-only responses, no control directives | ✅ Implemented | `core/agents/advisory.py` | — | `tests/unit/core/test_advisory.py` | |
| INT-ADV-003 | No direct tool calls | ✅ Implemented | `core/agents/advisory.py` | — | `tests/architecture/test_agent_advisory.py` | |
| INT-ADV-004 | Define output_schema | ✅ Implemented | `core/agents/advisory.py` | — | `tests/unit/core/test_advisory.py` | |
| INT-ADV-006 | Pass through governance hooks | ✅ Implemented | `core/agents/advisory.py` | `trace: before_model` | `tests/unit/core/test_advisory.py` | |
| INT-ADV-007 | Emit `model_call_attempt_started` | ✅ Implemented | `core/agents/advisory.py` | `trace: model_call_attempt_started` | `tests/unit/core/test_advisory.py` | |

### ToolSelector (INT-TS)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| INT-TS-001 | Return ToolSelectorOutput | ✅ Implemented | `core/agents/advisory.py` | `artifact: tool_selection` | `tests/unit/core/test_advisory.py` | |
| INT-TS-002 | selected_tools max 10 | ✅ Implemented | `core/contracts/advisory_schema.py` | — | `tests/unit/core/test_advisory_schema.py` | |
| INT-TS-004 | SelectedTool: name, rationale, confidence | ✅ Implemented | `core/contracts/advisory_schema.py` | — | `tests/unit/core/test_advisory_schema.py` | |

### Reasoning Ladder (INT-RL)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| INT-RL-001 | Three passes: interpret → propose → select | ✅ Implemented | `core/agents/reasoning_ladder.py` | `trace: ladder_phase` | `tests/unit/core/test_reasoning_ladder.py` | |
| INT-RL-002 | max_passes >= 3 | ✅ Implemented | `core/agents/reasoning_ladder.py` | — | `tests/unit/core/test_reasoning_ladder.py` | |
| INT-RL-003 | Budget consumed before each pass | ✅ Implemented | `core/agents/reasoning_ladder.py` | `trace: budget_consumed` | `tests/unit/core/test_reasoning_ladder.py` | |
| INT-RL-INT-001 | InterpretOutput: intent, entities, constraints | ✅ Implemented | `core/contracts/reasoning_ladder_schema.py` | — | `tests/unit/core/test_reasoning_schema.py` | |
| INT-RL-PRO-001 | ProposeOutput: tool_candidates, agent_candidates | ✅ Implemented | `core/contracts/reasoning_ladder_schema.py` | — | `tests/unit/core/test_reasoning_schema.py` | |
| INT-RL-SEL-001 | SelectOutput: final_selection, confidence | ✅ Implemented | `core/contracts/reasoning_ladder_schema.py` | — | `tests/unit/core/test_reasoning_schema.py` | |
| INT-RL-BUD-001 | consume_budget before each pass | ✅ Implemented | `core/agents/reasoning_ladder.py` | `trace: budget_consumed` | `tests/unit/core/test_reasoning_ladder.py` | |

### Critic Evaluator (INT-CRIT)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| INT-CRIT-001 | No direct tool calls | ✅ Implemented | `core/agents/critic_evaluator.py` | — | `tests/unit/core/test_critic.py` | |
| INT-CRIT-002 | Return CriticResult | ✅ Implemented | `core/agents/critic_evaluator.py` | `artifact: critique` | `tests/unit/core/test_critic.py` | |
| INT-CRIT-003 | Emit `critic_evaluator_started` | ✅ Implemented | `core/agents/critic_evaluator.py` | `trace: critic_evaluator_started` | `tests/unit/core/test_critic.py` | |
| INT-CRIT-004 | Emit `critic_evaluator_completed` | ✅ Implemented | `core/agents/critic_evaluator.py` | `trace: critic_evaluator_completed` | `tests/unit/core/test_critic.py` | |

### Critic Output Schema (INT-CRIT-OUT)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| — | completeness_score 0.0-1.0 | ✅ Implemented | `core/contracts/critic_schema.py` | — | `tests/unit/core/test_critic_schema.py` | |
| — | confidence_adjustment -1.0 to 1.0 | ✅ Implemented | `core/contracts/critic_schema.py` | — | `tests/unit/core/test_critic_schema.py` | |
| — | recommended_next_action enum | ✅ Implemented | `core/contracts/critic_schema.py` | — | `tests/unit/core/test_critic_schema.py` | |

---

## Gateway (GW)

> Source: [../03_techspecs/GW-gateway.md](../03_techspecs/GW-gateway.md)

### HTTP API Server (GW-API)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GW-API-001 | FastAPI `create_app()` factory | ✅ Implemented | `gateway/api/http_app.py` | — | `tests/integration/test_api.py` | |
| GW-API-002 | Health check at GET /health | ✅ Implemented | `gateway/api/http_app.py` | — | `tests/integration/test_api.py` | |
| GW-API-004 | Routes under /api prefix | ✅ Implemented | `gateway/api/http_app.py` | — | `tests/integration/test_api.py` | |
| GW-API-005 | ASGI entrypoint `app` | ✅ Implemented | `gateway/api/http_app.py` | — | — | |

### Product Endpoints (GW-API-01x)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GW-API-010 | GET /api/products lists products | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |
| GW-API-011 | GET /api/products/{product}/flows | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |
| GW-API-014 | 404 for unknown product | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |

### Run Endpoints (GW-API-02x)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GW-API-020 | POST /api/products/{product}/flows/{flow}/run | ✅ Implemented | `gateway/api/routes_run.py` | `trace: api_run_started` | `tests/integration/test_api.py` | |
| GW-API-021 | GET /api/runs/{run_id} | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |
| GW-API-024 | Payload size limit 100KB | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |
| GW-API-025 | 413 for payload_too_large | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |

### User Input & Approval Endpoints (GW-API-03x, 04x)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GW-API-030 | GET /api/runs/{run_id}/pending_input | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |
| GW-API-031 | POST /api/runs/{run_id}/user_input | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |
| GW-API-040 | GET /api/approvals | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |
| GW-API-041 | POST /api/runs/{run_id}/resume | ✅ Implemented | `gateway/api/routes_run.py` | `trace: api_resumed` | `tests/integration/test_api.py` | |

### Response Schema (GW-API-06x)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GW-API-060 | Success: `{ok: true, data, meta}` | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |
| GW-API-061 | Error: `{ok: false, error: {code, message}}` | ✅ Implemented | `gateway/api/routes_run.py` | — | `tests/integration/test_api.py` | |

### Dependency Injection (GW-API-07x)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GW-API-070 | Settings singleton via get_settings | ✅ Implemented | `gateway/api/deps.py` | — | — | |
| GW-API-071 | ProductCatalog singleton | ✅ Implemented | `gateway/api/deps.py` | — | — | |
| GW-API-074 | Engine per-request (session isolation) | ✅ Implemented | `gateway/api/deps.py` | — | — | |

### CLI (GW-CLI)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| GW-CLI-001 | Invocable as `master <command>` | ✅ Implemented | `gateway/cli/main.py` | — | `tests/integration/test_cli.py` | argparse |
| GW-CLI-010 | `products` command lists products | ✅ Implemented | `gateway/cli/main.py` | — | `tests/integration/test_cli.py` | |
| GW-CLI-012 | `run <product> <flow>` command | ✅ Implemented | `gateway/cli/main.py` | — | `tests/integration/test_cli.py` | |
| GW-CLI-015 | `status <run_id>` command | ✅ Implemented | `gateway/cli/main.py` | — | `tests/integration/test_cli.py` | |
| GW-CLI-017 | `approvals` command | ✅ Implemented | `gateway/cli/main.py` | — | `tests/integration/test_cli.py` | |
| GW-CLI-018 | `resume --run-id` command | ✅ Implemented | `gateway/cli/main.py` | — | `tests/integration/test_cli.py` | |
| GW-CLI-030 | JSON output | ✅ Implemented | `gateway/cli/main.py` | — | `tests/integration/test_cli.py` | |
| GW-CLI-032 | Exit code 0 on success | ✅ Implemented | `gateway/cli/main.py` | — | `tests/integration/test_cli.py` | |

### UI (GW-UI)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| — | Streamlit platform_app.py | ✅ Implemented | `gateway/ui/platform_app.py` | — | — | |
| — | Modular pages/ structure | ✅ Implemented | `gateway/ui/pages/` | — | — | |
| — | API client for backend calls | ✅ Implemented | `gateway/ui/api_client.py` | — | — | |

---

## Products (PROD)

> Source: [../03_techspecs/PROD-products.md](../03_techspecs/PROD-products.md)

### Directory Structure (PROD-DIR)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| PROD-DIR-001 | Products in `products/<name>/` | ✅ Implemented | `products/` | — | `tests/architecture/test_product_structure.py` | |
| PROD-DIR-002 | Snake_case directory names | ✅ Implemented | `products/` | — | `tests/architecture/test_product_structure.py` | |
| PROD-DIR-003 | `manifest.yaml` required | ✅ Implemented | `products/*/manifest.yaml` | — | `tests/unit/test_product_discovery.py` | |
| PROD-DIR-004 | `registry.py` required | ✅ Implemented | `products/*/registry.py` | — | `tests/unit/test_product_discovery.py` | |

### Manifest Schema (PROD-MAN)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| PROD-MAN-001 | Valid YAML file | ✅ Implemented | `core/utils/product_loader.py` | — | `tests/unit/test_product_loader.py` | |
| PROD-MAN-002 | `name` field required | ✅ Implemented | `core/utils/product_loader.py` | — | `tests/unit/test_product_loader.py` | |
| PROD-MAN-003 | `display_name` field | ✅ Implemented | `core/utils/product_loader.py` | — | `tests/unit/test_product_loader.py` | |
| PROD-MAN-006 | `flows` list required | ✅ Implemented | `core/utils/product_loader.py` | — | `tests/unit/test_product_loader.py` | |
| PROD-MAN-020 | `exposed_api` section | ✅ Implemented | `core/utils/product_loader.py` | — | `tests/unit/test_product_loader.py` | |
| PROD-MAN-030 | `ui` section for Streamlit | ✅ Implemented | `core/utils/product_loader.py` | — | `tests/unit/test_product_loader.py` | |
| PROD-MAN-040 | Validate against ProductManifest | ✅ Implemented | `core/utils/product_loader.py` | — | `tests/unit/test_product_loader.py` | Pydantic |

### Registry Pattern (PROD-REG)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| PROD-REG-001 | `registry.py` module required | ✅ Implemented | `products/*/registry.py` | — | `tests/unit/test_product_discovery.py` | |
| PROD-REG-004 | Registries are Dict[str, Callable] | ✅ Implemented | `core/utils/product_loader.py` | — | `tests/unit/test_product_loader.py` | Factory pattern |
| PROD-REG-005 | Factories only (no instances) | ✅ Implemented | `products/*/registry.py` | — | `tests/architecture/test_product_isolation.py` | |
| PROD-REG-010 | Auto-discovery in products/ | ✅ Implemented | `core/utils/product_loader.py` | `trace: product_discovered` | `tests/unit/test_product_discovery.py` | |
| PROD-REG-011 | Skip dirs without manifest.yaml | ✅ Implemented | `core/utils/product_loader.py` | — | `tests/unit/test_product_discovery.py` | |

### Decorator Pattern (PROD-DEC)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| PROD-DEC-001 | `@agent(name="...")` decorator | ✅ Implemented | `core/agents/base.py` | — | `tests/unit/core/test_agent_decorator.py` | |
| PROD-DEC-010 | `@tool(name="...")` decorator | ✅ Implemented | `core/tools/base.py` | — | `tests/unit/core/test_tool_decorator.py` | |

### Product Isolation (PROD-ISO)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| — | Products cannot import each other | ✅ Implemented | — | — | `tests/architecture/test_product_isolation.py` | INV-5 |
| — | Separate agent/tool namespaces | ✅ Implemented | `core/agents/registry.py` | — | `tests/unit/core/test_namespace_isolation.py` | |

---

## Acceptance (ACC)

> Source: [../03_techspecs/ACC-acceptance.md](../03_techspecs/ACC-acceptance.md)

| Tech Spec ID | Requirement (short) | Status | Implemented In | Trace/Artifact | Tests | Notes |
|--------------|---------------------|--------|----------------|----------------|-------|-------|
| ACC-001 | Unit tests for all core modules | ✅ Implemented | `tests/unit/` | — | — | |
| ACC-002 | Integration tests for cross-module flows | ✅ Implemented | `tests/integration/` | — | — | |
| ACC-003 | Architecture tests for invariants | ✅ Implemented | `tests/architecture/` | — | — | |
| ACC-004 | Acceptance tests for end-to-end flows | ✅ Implemented | `tests/acceptance_intelligence/` | — | — | |

---

## Delta Detection

### Finding Unimplemented Requirements

```bash
# Count unimplemented requirements
grep -c "❌ Not Implemented" docs/05_systemdesign/SD-COVERAGE.md

# List partial implementations
grep "🟡 Partial" docs/05_systemdesign/SD-COVERAGE.md
```

### Generating Implementation Plan

1. Extract all `❌ Not Implemented` and `🟡 Partial` rows
2. Group by component (ORC, GOV, etc.)
3. Create TST prompts for each requirement
4. Prioritize by dependency order

---

## Maintenance

### After Implementation

1. Update status from `❌` → `🟡` → `✅`
2. Add file paths in "Implemented In"
3. Add trace event names in "Trace/Artifact"
4. Link to tests in "Tests" column

### Adding New Requirements

1. Add requirement to Tech Spec with new ID
2. Add row to this coverage matrix with `❌ Not Implemented`
3. Plan implementation
4. Update status as work progresses

---

## See Also

- [SD-INDEX.md](SD-INDEX.md) — Navigation and delta detection loop
- [SD-ARCH.md](SD-ARCH.md) — Architecture boundaries and invariants
- [../howto/HOWTO-enhance-framework.md](../howto/HOWTO-enhance-framework.md) — Enhancement workflow
