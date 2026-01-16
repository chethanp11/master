# Agents and Tools Technical Specification

> **Document ID**: AGT / TOOL  
> **Version**: 1.1  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-13  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial release |
| 1.1.0 | 2026-01-13 | Added §2.4 Reasoning & Intelligence Boundaries, §2.5 Explicit Non-Goals, updated BRD mappings |

---

## 1. Overview

This specification defines the contracts, registry patterns, and execution requirements for 
agents and tools in the master platform. Agents are goal-driven reasoning units that produce 
structured outputs; tools are discrete operations that interact with external systems or 
perform computations.

### 1.1 Implementation References

| Component | File |
|-----------|------|
| BaseAgent | `core/agents/base.py` |
| Agent Registry | `core/agents/registry.py` |
| LLMReasoner | `core/agents/llm_reasoner.py` |
| BaseTool | `core/tools/base.py` |
| Tool Registry | `core/tools/registry.py` |
| Tool Executor | `core/tools/executor.py` |
| Local Backend | `core/tools/backends/local_backend.py` |
| ComponentRegistry | `core/utils/registry.py` |
| Agent Schema | `core/contracts/agent_schema.py` |
| Tool Schema | `core/contracts/tool_schema.py` |
| Descriptors | `core/contracts/descriptors_schema.py` |

---

## 2. BaseAgent Contract Requirements

### 2.1 Class Structure

| ID | Requirement | Level |
|----|-------------|-------|
| **AGT-BASE-001** | [V1] All agents MUST extend `BaseAgent` abstract base class | MUST |
| **AGT-BASE-002** | [V1] Every agent MUST provide a stable `name` class attribute used in flows and registries | MUST |
| **AGT-BASE-003** | [V1] Agent names SHOULD use namespaced format `product.agent_name` to avoid collisions | SHOULD |
| **AGT-BASE-004** | [V1] Agents MUST accept `Settings` in constructor for dependency injection | MUST |

**Implementation**: `core/agents/base.py`

### 2.2 Run Method Contract

| ID | Requirement | Level |
|----|-------------|-------|
| **AGT-RUN-001** | [V1] Agents MUST implement abstract method `async run(ctx: StepContext, params: Dict) -> AgentResult` | MUST |
| **AGT-RUN-002** | [V1] Agents MUST return an `AgentResult` envelope (ok/data/error/meta) from the run method | MUST |
| **AGT-RUN-003** | [V1] Agents MUST NOT raise raw exceptions outward; all errors MUST be wrapped in `AgentResult` | MUST |
| **AGT-RUN-004** | [V1] Agents MUST return structured outputs via Pydantic models in `data` | MUST |

**Implementation**: `core/agents/base.py`, `core/contracts/agent_schema.py`

### 2.3 Behavioral Constraints

| ID | Requirement | Level |
|----|-------------|-------|
| **AGT-BEHAV-001** | [V1] Agents MUST be goal-driven, not prompt-driven; agents SHALL NOT rely on prompts for behavior beyond minimal foundational system instructions | MUST |
| **AGT-BEHAV-002** | [V1] Agents MUST NOT call tools directly; tool usage MUST be requested through orchestrator mechanisms via structured tool requests in `AgentResult` | MUST |
| **AGT-BEHAV-003** | [V1] Agents MUST NOT persist state; agents MAY only read/write to orchestrator-managed artifacts/state provided via `StepContext` | MUST |
| **AGT-BEHAV-004** | [V1] Agents MUST NOT read environment variables directly; configuration MUST be injected by the caller | MUST |
| **AGT-BEHAV-005** | [V1] Agents MUST emit trace events via hooks for observability | MUST |

**Implementation**: `core/agents/base.py`

---

## 2.4 Reasoning & Intelligence Boundaries (Added: 2026-01-13)

> **Source**: BRD-AUTO-030...036, INV-1, INV-2, INV-7

### 2.4.1 Agent Reasoning Constraints

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **AGT-REASON-001** | [V1] Agents MUST NOT perform open-ended reasoning; all reasoning MUST be bounded by phase | MUST | 1.1 |
| **AGT-REASON-002** | [V1] Agents MUST NOT make autonomous decisions about execution path | MUST | 1.1 |
| **AGT-REASON-003** | [V1] Agent reasoning outputs MUST be structured artifacts, not free-form text | MUST | 1.1 |
| **AGT-REASON-004** | [V1] Agent reasoning confidence MUST be explicitly computed and bounded 0.0-1.0 | MUST | 1.1 |
| **AGT-REASON-005** | [V1] Agent reasoning traces MUST expose: options_considered, confidence, rejection_reasons | MUST | 1.1 |

**Implementation**: `core/agents/base.py`, `core/agents/advisory.py`

### 2.4.2 Critique Constraints (INV-2)

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **AGT-CRIT-001** | [V1] Critic agents MUST be advisory only; MUST NOT execute tools | MUST | 1.1 |
| **AGT-CRIT-002** | [V1] Critic agents MUST NOT route flows or override policies | MUST | 1.1 |
| **AGT-CRIT-003** | [V1] Critic agents MAY lower confidence or recommend escalation | MAY | 1.1 |
| **AGT-CRIT-004** | [V1] Critic outputs MUST include `confidence_adjustment` bounded -1.0 to 1.0 | MUST | 1.1 |
| **AGT-CRIT-005** | [V1] Critic outputs MUST include `recommended_next_action` from allowed enum | MUST | 1.1 |

**Allowed Critic Actions**:
| Action | Description | Control Effect |
|--------|-------------|----------------|
| `NONE` | No action required | None |
| `USER_INPUT` | Request user clarification | Advisory only |
| `HITL` | Escalate to human | Advisory only |
| `FETCH_MORE_EVIDENCE` | Suggest more evidence | Advisory only |

**Forbidden Critic Actions**:
| Forbidden | Why |
|-----------|-----|
| Execute tools | Violates INV-2 (non-controlling) |
| Route flows | Violates INV-2 (non-controlling) |
| Override policies | Violates INV-6 (laws are explicit) |
| Force decisions | Violates INV-2 (advisory only) |

**Implementation**: `core/agents/critic_evaluator.py`

### 2.4.3 Reasoning Artifact Contract

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **AGT-ARTIFACT-001** | [V1] Every agent invocation MUST produce a structured artifact | MUST | 1.1 |
| **AGT-ARTIFACT-002** | [V1] Artifact MUST include `invocation_id` (UUID) for traceability | MUST | 1.1 |
| **AGT-ARTIFACT-003** | [V1] Artifact MUST include `timestamp` (epoch) for temporal ordering | MUST | 1.1 |
| **AGT-ARTIFACT-004** | [V1] Artifact MUST include `reasoning_trace` with decision path | SHOULD | 1.1 |
| **AGT-ARTIFACT-005** | [V1] Artifacts MUST be immutable once persisted | MUST | 1.1 |

**Implementation**: `core/contracts/agent_schema.py`

---

## 2.5 Explicit Non-Goals (Added: 2026-01-13)

> **Agents and Tools MUST NOT**:

| Non-Goal | Rationale | Violation Example |
|----------|-----------|-------------------|
| Autonomous execution | Violates INV-5, INV-6 | Agent decides to run tool without orchestrator |
| Self-modification | Violates governance | Agent updates own policy or permissions |
| Domain inference | Core is domain-agnostic | Agent infers business rules from patterns |
| Hidden heuristics | Violates auditability | Agent uses undocumented scoring rules |
| Open-ended exploration | Violates bounded reasoning | Agent explores indefinitely without stop condition |
| Direct LLM control | Tools are deterministic | Tool calls LLM to make decision |

---

## 3. AgentResult Schema Requirements

### 3.1 Envelope Structure

| ID | Requirement | Level |
|----|-------------|-------|
| **AGT-ENV-001** | [V1] `AgentResult` (alias for `StepResult`) MUST contain: `ok`, `data`, `error`, `meta` | MUST |
| **AGT-ENV-002** | [V1] When `ok=False`, `data` MUST be `None` | MUST |
| **AGT-ENV-003** | [V1] When `ok=True`, `data` MUST NOT be `None` (required) | MUST |
| **AGT-ENV-004** | [V1] All `AgentResult` fields MUST use `model_config = ConfigDict(extra="forbid")` | MUST |

**Implementation**: `core/contracts/agent_schema.py`

### 3.2 AgentMeta Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **AGT-META-001** | [V1] `AgentMeta` MUST include: `agent_name` (registered agent name) | MUST |
| **AGT-META-002** | [V1] `AgentMeta` MUST include: `role` (enum: PLANNER, EXECUTOR, CRITIC, ROUTER, SUMMARIZER, VALIDATOR, OTHER) | MUST |
| **AGT-META-003** | [V1] `AgentMeta` MUST auto-generate: `invocation_id` (UUID), `timestamp` | MUST |
| **AGT-META-004** | [V1] `AgentMeta` MAY include: `model_used`, `tokens_used`, `latency_ms`, `trace_refs`, `reasoning_trace` | MAY |

**Implementation**: `core/contracts/agent_schema.py`

### 3.3 AgentError Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **AGT-ERR-001** | [V1] `AgentError` MUST include: `code` (enum: INVALID_INPUT, POLICY_BLOCKED, MODEL_ERROR, TIMEOUT, CONTRACT_VIOLATION, UNKNOWN) | MUST |
| **AGT-ERR-002** | [V1] `AgentError` MUST include: `message` (human-readable) | MUST |
| **AGT-ERR-003** | [V1] `AgentError` MAY include: `details`, `trace` (sanitized) | MAY |

**Implementation**: `core/contracts/agent_schema.py`

### 3.4 Output Validation

| ID | Requirement | Level |
|----|-------------|-------|
| **AGT-OUT-001** | [V1] Agent output payloads MUST be objects (dict), not primitives | MUST |
| **AGT-OUT-002** | [V1] Agent output payloads MUST NOT contain control fields at any nesting level: | MUST |
| | • `next_step`, `retry`, `retry_instructions` | |
| | • `branch`, `branching`, `branch_hint`, `branching_hint` | |

**Implementation**: `core/governance/hooks.py`

---

## 4. BaseTool Contract Requirements

### 4.1 Class Structure

| ID | Requirement | Level |
|----|-------------|-------|
| **TOOL-BASE-001** | [V1] All tools MUST extend `BaseTool` abstract base class | MUST |
| **TOOL-BASE-002** | [V1] Every tool MUST provide a stable `name` class attribute used in flows | MUST |
| **TOOL-BASE-003** | [V1] Tools MUST accept `Settings` in constructor | MUST |

**Implementation**: `core/tools/base.py`

### 4.2 Run Method Contract

| ID | Requirement | Level |
|----|-------------|-------|
| **TOOL-RUN-001** | [V1] Tools MUST implement abstract method `async run(ctx: StepContext, params: Dict) -> ToolResult` | MUST |
| **TOOL-RUN-002** | [V1] Tools MUST return a `ToolResult` envelope (ok/data/error/meta/evidence/artifacts) | MUST |
| **TOOL-RUN-003** | [V1] Tools MUST NOT read environment variables directly; config MUST be injected | MUST |

**Implementation**: `core/tools/base.py`, `core/contracts/tool_schema.py`

### 4.3 Execution Constraints

| ID | Requirement | Level |
|----|-------------|-------|
| **TOOL-EXEC-001** | [V1] Tools MUST be executed ONLY through `ToolExecutor` | MUST |
| **TOOL-EXEC-002** | [V1] Tools MUST NOT be called directly by agents or other components | MUST |

**Implementation**: `core/tools/executor.py`

---

## 5. ToolResult Schema Requirements

### 5.1 Envelope Structure

| ID | Requirement | Level |
|----|-------------|-------|
| **TOOL-ENV-001** | [V1] `ToolResult` (alias for `StepResult`) MUST contain: `ok`, `data`, `error`, `meta` | MUST |
| **TOOL-ENV-002** | [V1] `ToolResult` MAY contain: `evidence`, `artifacts` | MAY |
| **TOOL-ENV-003** | [V1] When `ok=False`, `data` MUST be `None` | MUST |
| **TOOL-ENV-004** | [V1] When `ok=True`, `data` MUST NOT be `None` (required) | MUST |

**Implementation**: `core/contracts/tool_schema.py`

### 5.2 ToolMeta Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **TOOL-META-001** | [V1] `ToolMeta` MUST include: `tool_name`, `backend` (local|remote|mcp) | MUST |
| **TOOL-META-002** | [V1] `ToolMeta` MUST auto-generate: `invocation_id` (UUID), `timestamp` | MUST |
| **TOOL-META-003** | [V1] `ToolMeta` MAY include: `latency_ms`, `retries`, `cost_units`, `trace_refs`, `warnings` | MAY |

**Implementation**: `core/contracts/tool_schema.py`

### 5.3 ToolError Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **TOOL-ERR-001** | [V1] `ToolError` MUST include: `code` (enum: INVALID_INPUT, PERMISSION_DENIED, NOT_FOUND, TIMEOUT, RATE_LIMITED, BACKEND_ERROR, CONTRACT_VIOLATION, UNKNOWN, TEMPORARY) | MUST |
| **TOOL-ERR-002** | [V1] `ToolError` MUST include: `message` (human-readable) | MUST |
| **TOOL-ERR-003** | [V1] `ToolError` MAY include: `details`, `trace` (sanitized) | MAY |

**Implementation**: `core/contracts/tool_schema.py`

---

## 6. Registry Pattern Requirements

### 6.1 ComponentRegistry Base

| ID | Requirement | Level |
|----|-------------|-------|
| **REG-BASE-001** | [V1] Registries MUST extend `ComponentRegistry` generic base class | MUST |
| **REG-BASE-002** | [V1] Registries MUST store factories (callables), NOT instances, to avoid shared state | MUST |
| **REG-BASE-003** | [V1] Registries MUST define `_component_type` class attribute for error messages | MUST |
| **REG-BASE-004** | [V1] Registries MUST implement `_validate_factory(factory)` | MUST |

**Implementation**: `core/utils/registry.py`

### 6.2 Name Normalization

| ID | Requirement | Level |
|----|-------------|-------|
| **REG-NORM-001** | [V1] Registry names MUST be normalized: `name.strip().lower()` | MUST |
| **REG-NORM-002** | [V1] Registration and resolution MUST use normalized names consistently | MUST |

**Implementation**: `core/utils/registry.py`

### 6.3 Registration Operations

| ID | Requirement | Level |
|----|-------------|-------|
| **REG-OPS-001** | [V1] `register(name, factory)` MUST raise `RegistryError` if registering an instance instead of factory | MUST |
| **REG-OPS-002** | [V1] `register(name, factory)` MUST raise `RegistryError` if name already registered and `overwrite=False` | MUST |
| **REG-OPS-003** | [V1] `resolve(name)` MUST return a fresh instance by calling the factory | MUST |
| **REG-OPS-004** | [V1] `resolve(name)` MUST raise `RegistryError` if name not registered | MUST |
| **REG-OPS-005** | [V1] `is_registered(name)` MUST return `bool` indicating registration status | MUST |
| **REG-OPS-006** | [V1] `list_all()` MUST return all registered names | MUST |
| **REG-OPS-007** | [V1] `get_factory(name)` MUST return the factory callable | MUST |
| **REG-OPS-008** | [V1] `clear()` MUST remove all registrations | MUST |

**Implementation**: `core/utils/registry.py`

### 6.4 AgentRegistry Extensions

| ID | Requirement | Level |
|----|-------------|-------|
| **REG-AGENT-001** | [V1] `AgentRegistry` MUST store `AgentEntry` with: `name`, `factory`, `descriptor`, `capabilities` | MUST |
| **REG-AGENT-002** | [V1] `AgentRegistry` MUST support `list_by_capability(capability)` | MUST |
| **REG-AGENT-003** | [V1] `AgentRegistry` MUST support `get_descriptor(name)` | MUST |
| **REG-AGENT-004** | [V1] `AgentRegistry` MUST lazily register core agents on first access | MUST |

**Implementation**: `core/agents/registry.py`

### 6.5 ToolRegistry Extensions

| ID | Requirement | Level |
|----|-------------|-------|
| **REG-TOOL-001** | [V1] `ToolRegistry` MUST store `ToolEntry` with: `name`, `factory`, `descriptor`, `capabilities`, `backend` | MUST |
| **REG-TOOL-002** | [V1] `ToolRegistry` MUST support lazy hydration of auto-generated descriptors from tool instances | MUST |
| **REG-TOOL-003** | [V1] `ToolRegistry` MUST support `list_by_capability(capability)` | MUST |
| **REG-TOOL-004** | [V1] `ToolRegistry` MUST support `get_descriptor(name)` | MUST |

**Implementation**: `core/tools/registry.py`

---

## 7. Auto-Discovery Decorator Requirements

### 7.1 Agent Decorator

| ID | Requirement | Level |
|----|-------------|-------|
| **DEC-AGENT-001** | [V1] `@agent` decorator MUST attach `_agent_descriptor` to class | MUST |
| **DEC-AGENT-002** | [V1] `@agent` decorator MUST set `_is_auto_registered = True` on class | MUST |
| **DEC-AGENT-003** | [V1] `@agent` decorator MUST set class `name` attribute if not already set | MUST |
| **DEC-AGENT-004** | [V1] Decorated classes MUST have a `create` function OR be instantiable with no required arguments | MUST |
| **DEC-AGENT-005** | [V1] `cost_hint` MUST be coerced to `CostHint` enum (LOW, MED, HIGH, UNKNOWN) | MUST |
| **DEC-AGENT-006** | [V1] `capabilities` MUST default to `["reasoning"]` if not specified | MUST |

**Implementation**: `core/agents/registry.py`

### 7.2 Tool Decorator

| ID | Requirement | Level |
|----|-------------|-------|
| **DEC-TOOL-001** | [V1] `@tool` decorator MUST attach `_tool_descriptor` to class | MUST |
| **DEC-TOOL-002** | [V1] `@tool` decorator MUST set `_is_auto_registered = True` on class | MUST |
| **DEC-TOOL-003** | [V1] `@tool` decorator MUST set class `name` attribute if not already set | MUST |
| **DEC-TOOL-004** | [V1] Decorated classes MUST have a `create` function OR be instantiable with no required arguments | MUST |
| **DEC-TOOL-005** | [V1] `sensitivity_class` MUST be coerced to `SensitivityClass` enum | MUST |
| **DEC-TOOL-006** | [V1] `cost_hint` MUST be coerced to `CostHint` enum (LOW, MED, HIGH, UNKNOWN) | MUST |
| **DEC-TOOL-007** | [V1] `read_only` MUST default to `True`; `has_side_effects` MUST default to `False` | MUST |

**Implementation**: `core/tools/registry.py`

---

## 8. Descriptor Schema Requirements

### 8.1 AgentDescriptor

| ID | Requirement | Level |
|----|-------------|-------|
| **DESC-AGENT-001** | [V1] `AgentDescriptor` MUST include: `name` | MUST |
| **DESC-AGENT-002** | [V1] `AgentDescriptor` MUST include: `description` (primary purpose) | MUST |
| **DESC-AGENT-003** | [V1] `AgentDescriptor` MUST include: `capabilities` (semantic tags like 'reasoning', 'planning', 'evaluation') | MUST |
| **DESC-AGENT-004** | [V1] `AgentDescriptor` MUST include: `cost_hint` | MUST |
| **DESC-AGENT-005** | [V1] `AgentDescriptor` MUST include: `output_schema` | MUST |
| **DESC-AGENT-006** | [V1] `AgentDescriptor` MAY include: `input_schema`, `examples`, `version`, `tags` | MAY |

**Implementation**: `core/contracts/descriptors_schema.py`

### 8.2 ToolDescriptor

| ID | Requirement | Level |
|----|-------------|-------|
| **DESC-TOOL-001** | [V1] `ToolDescriptor` MUST include: `name`, `description` | MUST |
| **DESC-TOOL-002** | [V1] `ToolDescriptor` MUST include: `capabilities` (semantic tags like 'data_reading', 'computation', 'visualization') | MUST |
| **DESC-TOOL-003** | [V1] `ToolDescriptor` MUST include: `read_only`, `has_side_effects` | MUST |
| **DESC-TOOL-004** | [V1] `ToolDescriptor` MUST include: `sensitivity_class` | MUST |
| **DESC-TOOL-005** | [V1] `ToolDescriptor` MUST include: `cost_hint` | MUST |
| **DESC-TOOL-006** | [V1] `ToolDescriptor` MAY include: `input_schema`, `output_schema`, `examples` | MAY |

**Implementation**: `core/contracts/descriptors_schema.py`

---

## 9. ToolExecutor Governance Flow Requirements

### 9.1 Execution Flow

| ID | Requirement | Level |
|----|-------------|-------|
| **EXEC-FLOW-001** | [V1] ToolExecutor MUST resolve tool from registry before execution | MUST |
| **EXEC-FLOW-002** | [V1] ToolExecutor MUST sanitize parameters via `SecurityRedactor` before governance hooks | MUST |
| **EXEC-FLOW-003** | [V1] ToolExecutor MUST call `before_tool` if hooks configured | MUST |
| **EXEC-FLOW-004** | [V1] ToolExecutor MUST return `ToolResult` with `POLICY_BLOCKED` error if governance denies | MUST |
| **EXEC-FLOW-005** | [V1] ToolExecutor MUST emit `tool_call_blocked` trace event on governance denial | MUST |
| **EXEC-FLOW-006** | [V1] ToolExecutor MUST route execution to appropriate backend (only `local` in v1) | MUST |
| **EXEC-FLOW-007** | [V1] ToolExecutor MUST NEVER raise raw exceptions; all errors MUST be wrapped in `ToolResult` envelope | MUST |

**Implementation**: `core/tools/executor.py`

### 9.2 Result Processing

| ID | Requirement | Level |
|----|-------------|-------|
| **EXEC-RESULT-001** | [V1] ToolExecutor MUST normalize any return value to `ToolResult` via `normalize_tool_result` | MUST |
| **EXEC-RESULT-002** | [V1] ToolExecutor MUST attach evidence to results via `attach_evidence` | MUST |
| **EXEC-RESULT-003** | [V1] ToolExecutor MUST emit `tool_call_completed` trace event with sanitized payload | MUST |
| **EXEC-RESULT-004** | [V1] ToolExecutor MUST strip large fields (`content_base64`, `file_bytes`, `bytes`) from trace payloads | MUST |
| **EXEC-RESULT-005** | [V1] ToolExecutor MUST update `StepContext` with `tokens_used` and `latency_ms` | MUST |

**Implementation**: `core/tools/executor.py`

### 9.3 Local Backend

| ID | Requirement | Level |
|----|-------------|-------|
| **EXEC-LOCAL-001** | [V1] `LocalBackend` MUST execute tool's `run` method in-process | MUST |
| **EXEC-LOCAL-002** | [V1] `LocalBackend` MUST NOT persist state | MUST |
| **EXEC-LOCAL-003** | [V1] `LocalBackend` MUST NOT log sensitive fields; executor handles redaction | MUST |

**Implementation**: `core/tools/backends/local_backend.py`

---

## 10. Evidence Attachment Requirements

### 10.1 Evidence Generation

| ID | Requirement | Level |
|----|-------------|-------|
| **EVID-GEN-001** | [V1] ToolExecutor MUST auto-attach `EvidenceItem` to results if not already present | MUST |
| **EVID-GEN-002** | [V1] Evidence items MUST NOT be attached to `ok=False` errors | MUST |
| **EVID-GEN-003** | [V1] Evidence `id` MUST follow format: `{tool_name}_{timestamp}_{uuid4[:8]}` | MUST |
| **EVID-GEN-004** | [V1] Evidence `confidence` MUST be `0.8` for successful results, `0.5` for errors | MUST |

**Implementation**: `core/tools/executor.py`

### 10.2 Evidence Structure

| ID | Requirement | Level |
|----|-------------|-------|
| **EVID-STRUCT-001** | [V1] `EvidenceItem` MUST include: `id`, `source_type`, `confidence`, `content` | MUST |
| **EVID-STRUCT-002** | [V1] `EvidenceItem` MUST include: `tool_name`, `timestamp`, `provenance` | MUST |
| **EVID-STRUCT-003** | [V1] `provenance` MUST include: `params` (sanitized params) | MUST |
| **EVID-STRUCT-004** | [V1] `provenance` MUST include: `tool`, `uri`, `ref` | MUST |

**Implementation**: `core/contracts/retrieval_schema.py`

### 10.3 Artifact Storage

| ID | Requirement | Level |
|----|-------------|-------|
| **EVID-ARTIFACT-001** | [V1] Evidence payload MUST be stored in `run_context.artifacts` | MUST |
| **EVID-ARTIFACT-002** | [V1] Artifact key MUST follow format: `evidence.{evidence_id}` | MUST |
| **EVID-ARTIFACT-003** | [V1] Artifact URI MUST follow format: `artifact://evidence/{evidence_id}` | MUST |
| **EVID-ARTIFACT-004** | [V1] `ArtifactRef` MUST include: `uri`, `mime_type`, `size_bytes`, `sha256` | MUST |

**Implementation**: `core/contracts/retrieval_schema.py`

---

## 11. StepContext Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **CTX-PROV-001** | [V1] `StepContext` MUST provide access to: `run_id`, `step_id`, `product`, `flow` | MUST |
| **CTX-PROV-002** | [V1] `StepContext` MUST expose `artifacts`, `metadata`, `input_payload` via properties | MUST |
| **CTX-PROV-003** | [V1] `StepContext` MUST support `emit(event_type, payload)` for trace events | MUST |
| **CTX-PROV-004** | [V1] `StepContext` MUST provide: `settings`, `memory`, `tracer` | MUST |

**Implementation**: `core/orchestrator/context.py`

---

## 12. LLM Agent Specific Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **LLM-REQ-001** | [V1] `LLMReasoner` MUST validate params via `LLMReasonerParams` Pydantic model | MUST |
| **LLM-REQ-002** | [V1] `LLMReasoner` MUST call `before_model` pre-flight | MUST |
| **LLM-REQ-003** | [V1] `LLMReasoner` MUST emit `model_call_attempt_started`, `model_call_succeeded`, or `model_call_failed` trace events | MUST |
| **LLM-REQ-004** | [V1] `LLMReasoner` MUST track token usage in `metadata` | MUST |
| **LLM-REQ-005** | [V1] `LLMReasoner` MUST enforce run token budget and emit `model_call_budget_exceeded` if exceeded | MUST |
| **LLM-REQ-006** | [V1] `LLMReasoner` MUST return `POLICY_BLOCKED` error if governance denies model call | MUST |
| **LLM-REQ-007** | [V1] `LLMReasoner` MUST coerce results to `ReasoningOutput` schema for `plan_proposal` step types | MUST |

**Implementation**: `core/agents/llm_reasoner.py`

---

## 13. Future Considerations

### 13.1 V1.1 Enhancements

| ID | Feature | Description |
|----|---------|-------------|
| **AGT-FUTURE-001** | Streaming responses | Support streaming agent output |
| **AGT-FUTURE-002** | Agent composition | Combine multiple agents |
| **TOOL-FUTURE-001** | Remote backend | HTTP-based tool execution |
| **TOOL-FUTURE-002** | MCP backend | Model Context Protocol integration |

### 13.2 V2 Features

| ID | Feature | Description |
|----|---------|-------------|
| **AGT-FUTURE-010** | Multi-agent orchestration | Coordinated agent teams |
| **TOOL-FUTURE-010** | Tool marketplace | External tool discovery |
| **TOOL-FUTURE-011** | Sandboxed execution | Isolated tool environments |

---

## 14. Traceability Matrix

| Requirement | Implementation | Test | BRD Source |
|-------------|----------------|------|------------|
| AGT-BASE-001 | `core/agents/base.py` | `tests/unit/core/agents/test_base.py` | BRD-AUTO-001 |
| AGT-RUN-002 | `core/contracts/agent_schema.py` | `tests/unit/core/contracts/test_agent_schema.py` | BRD-AUTO-002 |
| AGT-BEHAV-001 | `core/agents/base.py` | `tests/unit/core/agents/test_base.py` | BRD-AUTO-005 |
| TOOL-BASE-001 | `core/tools/base.py` | `tests/unit/core/tools/test_base.py` | BRD-AUTO-010 |
| REG-BASE-002 | `core/utils/registry.py` | `tests/unit/core/utils/test_registry.py` | BRD-AUTO-003 |
| EXEC-FLOW-001 | `core/tools/executor.py` | `tests/unit/core/tools/test_executor.py` | BRD-AUTO-014 |
| DEC-AGENT-001 | `core/agents/registry.py` | `tests/unit/core/agents/test_registry.py` | BRD-AUTO-021 |
| AGT-REASON-001 | `core/agents/base.py` | `tests/architecture/test_agent_boundaries.py` | BRD-AUTO-030 |
| AGT-CRIT-001 | `core/agents/critic_evaluator.py` | `tests/unit/core/agents/test_critic_evaluator.py` | BRD-AUTO-031 |
| AGT-ARTIFACT-001 | `core/contracts/agent_schema.py` | `tests/unit/core/contracts/test_agent_schema.py` | BRD-AUTO-036 |

---

## 15. BRD Requirement Mapping

| BRD ID | Description | Techspec IDs | Ver |
|--------|-------------|--------------|-----|
| BRD-AUTO-001 | Multi-step reasoning | AGT-BASE-001...005, AGT-REASON-001...005 | 1.1 |
| BRD-AUTO-002 | Evidence-backed decisions | AGT-RUN-002, EVID-GEN-001...004 | 1.0 |
| BRD-AUTO-003 | Agent composition | REG-AGENT-001...004, AGT-BASE-003 | 1.0 |
| BRD-AUTO-004 | Failure handling | AGT-RUN-003, AGT-ERR-001...003 | 1.0 |
| BRD-AUTO-005 | Deterministic behavior | AGT-BEHAV-001...005 | 1.0 |
| BRD-AUTO-010 | Tool discoverability | DESC-TOOL-001...006 | 1.0 |
| BRD-AUTO-011 | Typed tool interfaces | TOOL-RUN-001...003 | 1.0 |
| BRD-AUTO-012 | Tool isolation testing | TOOL-EXEC-001, EXEC-LOCAL-001...003 | 1.0 |
| BRD-AUTO-013 | Tool evidence | EVID-STRUCT-001...004 | 1.0 |
| BRD-AUTO-014 | Tool observability | EXEC-RESULT-003, OBS-TRACE-* | 1.0 |
| BRD-AUTO-030 | Structured reasoning | AGT-REASON-001...005 | 1.1 |
| BRD-AUTO-031 | Critic evaluation | AGT-CRIT-001...005 | 1.1 |
| BRD-AUTO-034 | Reasoning observability | AGT-REASON-005, AGT-ARTIFACT-004 | 1.1 |
| BRD-AUTO-035 | Reasoning traces | AGT-ARTIFACT-001...005 | 1.1 |
| BRD-AUTO-036 | Reasoning artifacts | AGT-ARTIFACT-001...005 | 1.1 |
