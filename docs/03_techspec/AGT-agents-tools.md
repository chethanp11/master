# Agents and Tools Technical Specification

> **Document ID**: AGT / TOOL  
> **Version**: V1.3  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-25  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial release |
| 1.1.0 | 2026-01-13 | Added §2.4 Reasoning & Intelligence Boundaries, §2.5 Explicit Non-Goals, updated BRD mappings |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |
| V1.3 | 2026-01-25 | Added §13 Discovery Descriptor Requirements (BRD-AUTO-DISC-001-008) |

---

## 1. Overview

This specification defines the contracts, registry patterns, and execution requirements for 
agents and tools in the master platform. Agents are goal-driven reasoning units that produce 
structured outputs; tools are discrete operations that interact with external systems or 
perform computations.

## 2. BaseAgent Contract Requirements

### 2.1 Class Structure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-BASE-001 | All agents MUST extend `BaseAgent` abstract base class | MUST | BRD-AUTO-001 | 1.1 | 13 Jan 2026 | — |
| AGT-BASE-002 | Every agent MUST provide a stable `name` class attribute used in flows and registries | MUST | BRD-AUTO-001 | 1.1 | 13 Jan 2026 | — |
| AGT-BASE-003 | Agent names SHOULD use namespaced format `product.agent_name` to avoid collisions | SHOULD | BRD-AUTO-001 | 1.1 | 13 Jan 2026 | — |
| AGT-BASE-004 | Agents MUST accept `Settings` in constructor for dependency injection | MUST | BRD-AUTO-001 | 1.1 | 13 Jan 2026 | — |


### 2.2 Run Method Contract

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-RUN-001 | Agents MUST implement abstract method `async run(ctx: StepContext, params: Dict) -> AgentResult` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-RUN-002 | Agents MUST return an `AgentResult` envelope (ok/data/error/meta) from the run method | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-RUN-003 | Agents MUST NOT raise raw exceptions outward; all errors MUST be wrapped in `AgentResult` | MUST | BRD-AUTO-004 | 1.1 | 13 Jan 2026 | — |
| AGT-RUN-004 | Agents MUST return structured outputs via Pydantic models in `data` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 2.3 Behavioral Constraints

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-BEHAV-001 | Agents MUST be goal-driven, not prompt-driven; agents SHALL NOT rely on prompts for behavior beyond minimal foundational system instructions | MUST | BRD-AUTO-005 | 1.1 | 13 Jan 2026 | — |
| AGT-BEHAV-002 | Agents MUST NOT call tools directly; tool usage MUST be requested through orchestrator mechanisms via structured tool requests in `AgentResult` | MUST | BRD-AUTO-003, BRD-AUTO-005 | 1.1 | 13 Jan 2026 | — |
| AGT-BEHAV-003 | Agents MUST NOT persist state; agents MAY only read/write to orchestrator-managed artifacts/state provided via `StepContext` | MUST | BRD-AUTO-005 | 1.1 | 13 Jan 2026 | — |
| AGT-BEHAV-004 | Agents MUST NOT read environment variables directly; configuration MUST be injected by the caller | MUST | BRD-AUTO-005 | 1.1 | 13 Jan 2026 | — |
| AGT-BEHAV-005 | Agents MUST emit trace events via hooks for observability | MUST | BRD-AUTO-005 | 1.1 | 13 Jan 2026 | — |


---

## 2.4 Reasoning & Intelligence Boundaries (Added: 2026-01-13)

> **Source**: BRD-AUTO-030...036, INV-1, INV-2, INV-7

### 2.4.1 Agent Reasoning Constraints

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-REASON-001 | Agents MUST NOT perform open-ended reasoning; all reasoning MUST be bounded by phase | MUST | BRD-AUTO-005 | 1.1 | 13 Jan 2026 | — |
| AGT-REASON-002 | Agents MUST NOT make autonomous decisions about execution path | MUST | BRD-AUTO-005 | 1.1 | 13 Jan 2026 | — |
| AGT-REASON-003 | Agent reasoning outputs MUST be structured artifacts, not free-form text | MUST | BRD-AUTO-005 | 1.1 | 13 Jan 2026 | — |
| AGT-REASON-004 | Agent reasoning confidence MUST be explicitly computed and bounded 0.0-1.0 | MUST | BRD-AUTO-005 | 1.1 | 13 Jan 2026 | — |
| AGT-REASON-005 | Agent reasoning traces MUST expose: options_considered, confidence, rejection_reasons | MUST | BRD-AUTO-005, BRD-AUTO-034 | 1.1 | 13 Jan 2026 | — |


### 2.4.2 Critique Constraints (INV-2)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-CRIT-001 | Critic agents MUST be advisory only; MUST NOT execute tools | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| AGT-CRIT-002 | Critic agents MUST NOT route flows or override policies | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| AGT-CRIT-003 | Critic agents MAY lower confidence or recommend escalation | MAY | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| AGT-CRIT-004 | Critic outputs MUST include `confidence_adjustment` bounded -1.0 to 1.0 | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| AGT-CRIT-005 | Critic outputs MUST include `recommended_next_action` from allowed enum | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| AGT-CRIT-006 | Critic outputs MUST restrict `recommended_next_action` to: `NONE`, `USER_INPUT`, `HITL`, `FETCH_MORE_EVIDENCE` | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |
| AGT-CRIT-007 | Critic outputs MUST NOT include control actions (execute tools, route flows, override policies, force decisions) | MUST | BRD-AUTO-031 | 1.1 | 13 Jan 2026 | — |


### 2.4.3 Reasoning Artifact Contract

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-ARTIFACT-001 | Every agent invocation MUST produce a structured artifact | MUST | BRD-AUTO-002, BRD-AUTO-036, BRD-GOV-045 | 1.1 | 13 Jan 2026 | — |
| AGT-ARTIFACT-002 | Artifact MUST include `invocation_id` (UUID) for traceability | MUST | BRD-AUTO-002, BRD-AUTO-036, BRD-GOV-045 | 1.1 | 13 Jan 2026 | — |
| AGT-ARTIFACT-003 | Artifact MUST include `timestamp` (epoch) for temporal ordering | MUST | BRD-AUTO-002, BRD-AUTO-036, BRD-GOV-045 | 1.1 | 13 Jan 2026 | — |
| AGT-ARTIFACT-004 | Artifact MUST include `reasoning_trace` with decision path | SHOULD | BRD-AUTO-002, BRD-AUTO-035, BRD-AUTO-036, BRD-GOV-045, BRD-GOV-046 | 1.1 | 13 Jan 2026 | — |
| AGT-ARTIFACT-005 | Artifacts MUST be immutable once persisted | MUST | BRD-AUTO-002, BRD-AUTO-036, BRD-GOV-045, BRD-GOV-047 | 1.1 | 13 Jan 2026 | — |


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

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-ENV-001 | `AgentResult` (alias for `StepResult`) MUST contain: `ok`, `data`, `error`, `meta` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-ENV-002 | When `ok=False`, `data` MUST be `None` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-ENV-003 | When `ok=True`, `data` MUST NOT be `None` (required) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-ENV-004 | All `AgentResult` fields MUST use `model_config = ConfigDict(extra="forbid")` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 3.2 AgentMeta Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-META-001 | `AgentMeta` MUST include: `agent_name` (registered agent name) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-META-002 | `AgentMeta` MUST include: `role` (enum: PLANNER, EXECUTOR, CRITIC, ROUTER, SUMMARIZER, VALIDATOR, OTHER) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-META-003 | `AgentMeta` MUST auto-generate: `invocation_id` (UUID), `timestamp` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-META-004 | `AgentMeta` MAY include: `model_used`, `tokens_used`, `latency_ms`, `trace_refs`, `reasoning_trace` | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 3.3 AgentError Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-ERR-001 | `AgentError` MUST include: `code` (enum: INVALID_INPUT, POLICY_BLOCKED, MODEL_ERROR, TIMEOUT, CONTRACT_VIOLATION, UNKNOWN) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-ERR-002 | `AgentError` MUST include: `message` (human-readable) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-ERR-003 | `AgentError` MAY include: `details`, `trace` (sanitized) | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 3.4 Output Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-OUT-001 | Agent output payloads MUST be objects (dict), not primitives | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| AGT-OUT-002 | Agent output payloads MUST NOT contain control fields at any nesting level: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `next_step`, `retry`, `retry_instructions`; • `branch`, `branching`, `branch_hint`, `branching_hint` |


---

## 4. BaseTool Contract Requirements

### 4.1 Class Structure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| TOOL-BASE-001 | All tools MUST extend `BaseTool` abstract base class | MUST | BRD-AUTO-010 | 1.1 | 13 Jan 2026 | — |
| TOOL-BASE-002 | Every tool MUST provide a stable `name` class attribute used in flows | MUST | BRD-AUTO-010 | 1.1 | 13 Jan 2026 | — |
| TOOL-BASE-003 | Tools MUST accept `Settings` in constructor | MUST | BRD-AUTO-010 | 1.1 | 13 Jan 2026 | — |


### 4.2 Run Method Contract

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| TOOL-RUN-001 | Tools MUST implement abstract method `async run(ctx: StepContext, params: Dict) -> ToolResult` | MUST | BRD-AUTO-011 | 1.1 | 13 Jan 2026 | — |
| TOOL-RUN-002 | Tools MUST return a `ToolResult` envelope (ok/data/error/meta/evidence/artifacts) | MUST | BRD-AUTO-011 | 1.1 | 13 Jan 2026 | — |
| TOOL-RUN-003 | Tools MUST NOT read environment variables directly; config MUST be injected | MUST | BRD-AUTO-011 | 1.1 | 13 Jan 2026 | — |


### 4.3 Execution Constraints

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| TOOL-EXEC-001 | Tools MUST be executed ONLY through `ToolExecutor` | MUST | BRD-AUTO-012 | 1.1 | 13 Jan 2026 | — |
| TOOL-EXEC-002 | Tools MUST NOT be called directly by agents or other components | MUST | BRD-AUTO-012 | 1.1 | 13 Jan 2026 | — |


---

## 5. ToolResult Schema Requirements

### 5.1 Envelope Structure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| TOOL-ENV-001 | `ToolResult` (alias for `StepResult`) MUST contain: `ok`, `data`, `error`, `meta` | MUST | BRD-AUTO-011 | 1.1 | 13 Jan 2026 | — |
| TOOL-ENV-002 | `ToolResult` MAY contain: `evidence`, `artifacts` | MAY | BRD-AUTO-011, BRD-AUTO-013 | 1.1 | 13 Jan 2026 | — |
| TOOL-ENV-003 | When `ok=False`, `data` MUST be `None` | MUST | BRD-AUTO-011 | 1.1 | 13 Jan 2026 | — |
| TOOL-ENV-004 | When `ok=True`, `data` MUST NOT be `None` (required) | MUST | BRD-AUTO-011 | 1.1 | 13 Jan 2026 | — |


### 5.2 ToolMeta Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| TOOL-META-001 | `ToolMeta` MUST include: `tool_name`, `backend` (local/remote) | MUST | BRD-AUTO-014 | 1.1 | 13 Jan 2026 | — |
| TOOL-META-002 | `ToolMeta` MUST auto-generate: `invocation_id` (UUID), `timestamp` | MUST | BRD-AUTO-014 | 1.1 | 13 Jan 2026 | — |
| TOOL-META-003 | `ToolMeta` MAY include: `latency_ms`, `retries`, `cost_units`, `trace_refs`, `warnings` | MAY | BRD-AUTO-014 | 1.1 | 13 Jan 2026 | — |


### 5.3 ToolError Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| TOOL-ERR-001 | `ToolError` MUST include: `code` (enum: INVALID_INPUT, PERMISSION_DENIED, NOT_FOUND, TIMEOUT, RATE_LIMITED, BACKEND_ERROR, CONTRACT_VIOLATION, UNKNOWN, TEMPORARY) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| TOOL-ERR-002 | `ToolError` MUST include: `message` (human-readable) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| TOOL-ERR-003 | `ToolError` MAY include: `details`, `trace` (sanitized) | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 6. Registry Pattern Requirements

### 6.1 ComponentRegistry Base

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| REG-BASE-001 | Registries MUST extend `ComponentRegistry` generic base class | MUST | BRD-AUTO-010 | 1.1 | 13 Jan 2026 | — |
| REG-BASE-002 | Registries MUST store factories (callables), NOT instances, to avoid shared state | MUST | BRD-AUTO-010 | 1.1 | 13 Jan 2026 | — |
| REG-BASE-003 | Registries MUST define `_component_type` class attribute for error messages | MUST | BRD-AUTO-010 | 1.1 | 13 Jan 2026 | — |
| REG-BASE-004 | Registries MUST implement `_validate_factory(factory)` | MUST | BRD-AUTO-010 | 1.1 | 13 Jan 2026 | — |


### 6.2 Name Normalization

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| REG-NORM-001 | Registry names MUST be normalized: `name.strip().lower()` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-NORM-002 | Registration and resolution MUST use normalized names consistently | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.3 Registration Operations

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| REG-OPS-001 | `register(name, factory)` MUST raise `RegistryError` if registering an instance instead of factory | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-OPS-002 | `register(name, factory)` MUST raise `RegistryError` if name already registered and `overwrite=False` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-OPS-003 | `resolve(name)` MUST return a fresh instance by calling the factory | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-OPS-004 | `resolve(name)` MUST raise `RegistryError` if name not registered | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-OPS-005 | `is_registered(name)` MUST return `bool` indicating registration status | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-OPS-006 | `list_all()` MUST return all registered names | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-OPS-007 | `get_factory(name)` MUST return the factory callable | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-OPS-008 | `clear()` MUST remove all registrations | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.4 AgentRegistry Extensions

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| REG-AGENT-001 | `AgentRegistry` MUST store `AgentEntry` with: `name`, `factory`, `descriptor`, `capabilities` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-AGENT-002 | `AgentRegistry` MUST support `list_by_capability(capability)` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-AGENT-003 | `AgentRegistry` MUST support `get_descriptor(name)` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-AGENT-004 | `AgentRegistry` MUST lazily register core agents on first access | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.5 ToolRegistry Extensions

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| REG-TOOL-001 | `ToolRegistry` MUST store `ToolEntry` with: `name`, `factory`, `descriptor`, `capabilities`, `backend` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-TOOL-002 | `ToolRegistry` MUST support lazy hydration of auto-generated descriptors from tool instances | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-TOOL-003 | `ToolRegistry` MUST support `list_by_capability(capability)` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| REG-TOOL-004 | `ToolRegistry` MUST support `get_descriptor(name)` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 7. Auto-Discovery Decorator Requirements

### 7.1 Agent Decorator

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| DEC-AGENT-001 | `@agent` decorator MUST attach `_agent_descriptor` to class | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-AGENT-002 | `@agent` decorator MUST set `_is_auto_registered = True` on class | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-AGENT-003 | `@agent` decorator MUST set class `name` attribute if not already set | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-AGENT-004 | Decorated classes MUST have a `create` function OR be instantiable with no required arguments | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-AGENT-005 | `cost_hint` MUST be coerced to `CostHint` enum (LOW, MED, HIGH, UNKNOWN) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-AGENT-006 | `capabilities` MUST default to `["reasoning"]` if not specified | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 7.2 Tool Decorator

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| DEC-TOOL-001 | `@tool` decorator MUST attach `_tool_descriptor` to class | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-TOOL-002 | `@tool` decorator MUST set `_is_auto_registered = True` on class | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-TOOL-003 | `@tool` decorator MUST set class `name` attribute if not already set | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-TOOL-004 | Decorated classes MUST have a `create` function OR be instantiable with no required arguments | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-TOOL-005 | `sensitivity_class` MUST be coerced to `SensitivityClass` enum | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-TOOL-006 | `cost_hint` MUST be coerced to `CostHint` enum (LOW, MED, HIGH, UNKNOWN) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DEC-TOOL-007 | `read_only` MUST default to `True`; `has_side_effects` MUST default to `False` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 8. Descriptor Schema Requirements

### 8.1 AgentDescriptor

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| DESC-AGENT-001 | `AgentDescriptor` MUST include: `name` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-AGENT-002 | `AgentDescriptor` MUST include: `description` (primary purpose) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-AGENT-003 | `AgentDescriptor` MUST include: `capabilities` (semantic tags like 'reasoning', 'planning', 'evaluation') | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-AGENT-004 | `AgentDescriptor` MUST include: `cost_hint` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-AGENT-005 | `AgentDescriptor` MUST include: `output_schema` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-AGENT-006 | `AgentDescriptor` MAY include: `input_schema`, `examples`, `version`, `tags` | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 8.2 ToolDescriptor

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| DESC-TOOL-001 | `ToolDescriptor` MUST include: `name`, `description` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-TOOL-002 | `ToolDescriptor` MUST include: `capabilities` (semantic tags like 'data_reading', 'computation', 'visualization') | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-TOOL-003 | `ToolDescriptor` MUST include: `read_only`, `has_side_effects` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-TOOL-004 | `ToolDescriptor` MUST include: `sensitivity_class` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-TOOL-005 | `ToolDescriptor` MUST include: `cost_hint` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| DESC-TOOL-006 | `ToolDescriptor` MAY include: `input_schema`, `output_schema`, `examples` | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 9. ToolExecutor Governance Flow Requirements

### 9.1 Execution Flow

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| EXEC-FLOW-001 | ToolExecutor MUST resolve tool from registry before execution | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-FLOW-002 | ToolExecutor MUST sanitize parameters via `SecurityRedactor` before governance hooks | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-FLOW-003 | ToolExecutor MUST call `before_tool` if hooks configured | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-FLOW-004 | ToolExecutor MUST return `ToolResult` with `POLICY_BLOCKED` error if governance denies | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-FLOW-005 | ToolExecutor MUST emit `tool_call_blocked` trace event on governance denial | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-FLOW-006 | ToolExecutor MUST route execution to appropriate backend (only `local` in v1) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-FLOW-007 | ToolExecutor MUST NEVER raise raw exceptions; all errors MUST be wrapped in `ToolResult` envelope | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 9.2 Result Processing

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| EXEC-RESULT-001 | ToolExecutor MUST normalize any return value to `ToolResult` via `normalize_tool_result` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-RESULT-002 | ToolExecutor MUST attach evidence to results via `attach_evidence` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-RESULT-003 | ToolExecutor MUST emit `tool_call_completed` trace event with sanitized payload | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-RESULT-004 | ToolExecutor MUST strip large fields (`content_base64`, `file_bytes`, `bytes`) from trace payloads | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-RESULT-005 | ToolExecutor MUST update `StepContext` with `tokens_used` and `latency_ms` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 9.3 Local Backend

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| EXEC-LOCAL-001 | `LocalBackend` MUST execute tool's `run` method in-process | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-LOCAL-002 | `LocalBackend` MUST NOT persist state | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EXEC-LOCAL-003 | `LocalBackend` MUST NOT log sensitive fields; executor handles redaction | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 10. Evidence Attachment Requirements

### 10.1 Evidence Generation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| EVID-GEN-001 | ToolExecutor MUST auto-attach `EvidenceItem` to results if not already present | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EVID-GEN-002 | Evidence items MUST NOT be attached to `ok=False` errors | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EVID-GEN-003 | Evidence `id` MUST follow format: `{tool_name}_{timestamp}_{uuid4[:8]}` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EVID-GEN-004 | Evidence `confidence` MUST be `0.8` for successful results, `0.5` for errors | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 10.2 Evidence Structure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| EVID-STRUCT-001 | `EvidenceItem` MUST include: `id`, `source_type`, `confidence`, `content` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EVID-STRUCT-002 | `EvidenceItem` MUST include: `tool_name`, `timestamp`, `provenance` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EVID-STRUCT-003 | `provenance` MUST include: `params` (sanitized params) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EVID-STRUCT-004 | `provenance` MUST include: `tool`, `uri`, `ref` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 10.3 Artifact Storage

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| EVID-ARTIFACT-001 | Evidence payload MUST be stored in `run_context.artifacts` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EVID-ARTIFACT-002 | Artifact key MUST follow format: `evidence.{evidence_id}` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EVID-ARTIFACT-003 | Artifact URI MUST follow format: `artifact://evidence/{evidence_id}` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| EVID-ARTIFACT-004 | `ArtifactRef` MUST include: `uri`, `mime_type`, `size_bytes`, `sha256` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 11. StepContext Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| CTX-PROV-001 | `StepContext` MUST provide access to: `run_id`, `step_id`, `product`, `flow` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| CTX-PROV-002 | `StepContext` MUST expose `artifacts`, `metadata`, `input_payload` via properties | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| CTX-PROV-003 | `StepContext` MUST support `emit(event_type, payload)` for trace events | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| CTX-PROV-004 | `StepContext` MUST provide: `settings`, `memory`, `tracer` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 12. LLM Agent Specific Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| LLM-REQ-001 | `LLMReasoner` MUST validate params via `LLMReasonerParams` Pydantic model | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| LLM-REQ-002 | `LLMReasoner` MUST call `before_model` pre-flight | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| LLM-REQ-003 | `LLMReasoner` MUST emit `model_call_attempt_started`, `model_call_succeeded`, or `model_call_failed` trace events | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| LLM-REQ-004 | `LLMReasoner` MUST track token usage in `metadata` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| LLM-REQ-005 | `LLMReasoner` MUST enforce run token budget and emit `model_call_budget_exceeded` if exceeded | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| LLM-REQ-006 | `LLMReasoner` MUST return `POLICY_BLOCKED` error if governance denies model call | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| LLM-REQ-007 | `LLMReasoner` MUST coerce results to `ReasoningOutput` schema for `plan_proposal` step types | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

---

## 13. Discovery Descriptor Requirements

This section defines the explicit capability descriptor contracts that tools and agents MUST implement to support dynamic discovery by the orchestration engine. These descriptors are the foundation for intent-filtered, eligibility-checked discovery as specified in BRD-AUTO-DISC-001-008.

### 13.1 Tool Descriptor Contract

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-DISC-TOOL-001 | Every tool class MUST expose a `descriptor` property returning `ToolDescriptor` schema | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Enables registry population |
| AGT-DISC-TOOL-002 | `ToolDescriptor.name` MUST be a globally unique identifier string | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Registry key constraint |
| AGT-DISC-TOOL-003 | `ToolDescriptor.description` MUST contain human-readable capability summary | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Used for intent matching |
| AGT-DISC-TOOL-004 | `ToolDescriptor.capability_tags` MUST be a list of semantic capability labels | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Enables tag-based filtering |
| AGT-DISC-TOOL-005 | `ToolDescriptor.input_schema` MUST reference a Pydantic model or JSON Schema for input validation | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Contract enforcement |
| AGT-DISC-TOOL-006 | `ToolDescriptor.output_schema` MUST reference a Pydantic model or JSON Schema for output validation | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Contract enforcement |
| AGT-DISC-TOOL-007 | `ToolDescriptor.side_effects` MUST declare boolean or enum indicating mutation capability | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Governance filtering |
| AGT-DISC-TOOL-008 | `ToolDescriptor.deterministic` MUST declare boolean indicating determinism guarantee | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Reproducibility support |
| AGT-DISC-TOOL-009 | `ToolDescriptor.domain_tags` SHOULD contain product/domain scope labels | SHOULD | BRD-AUTO-DISC-001, BRD-AUTO-DISC-007 | 1.3 | 25 Jan 2026 | Product-controlled exposure |
| AGT-DISC-TOOL-010 | `ToolDescriptor.version` MUST contain semantic version string | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Versioned discovery |
| AGT-DISC-TOOL-011 | `ToolDescriptor.deprecation` SHOULD contain deprecation notice if tool is deprecated | SHOULD | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Lifecycle management |
| AGT-DISC-TOOL-012 | Tool descriptor MUST be accessible without instantiating tool execution context | MUST | BRD-AUTO-DISC-002 | 1.3 | 25 Jan 2026 | Registry scalability |

### 13.2 Agent Descriptor Contract

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-DISC-AGT-001 | Every agent class MUST expose a `descriptor` property returning `AgentDescriptor` schema | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Enables registry population |
| AGT-DISC-AGT-002 | `AgentDescriptor.name` MUST be a globally unique identifier string | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Registry key constraint |
| AGT-DISC-AGT-003 | `AgentDescriptor.description` MUST contain human-readable capability summary | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Used for intent matching |
| AGT-DISC-AGT-004 | `AgentDescriptor.capability_tags` MUST be a list of semantic capability labels | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Enables tag-based filtering |
| AGT-DISC-AGT-005 | `AgentDescriptor.input_schema` MUST reference input contract for agent invocation | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Contract enforcement |
| AGT-DISC-AGT-006 | `AgentDescriptor.output_schema` MUST reference output contract for agent results | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Contract enforcement |
| AGT-DISC-AGT-007 | `AgentDescriptor.reasoning_type` MUST declare reasoning mode enum (advisory, critic, ladder, etc.) | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Discovery categorization |
| AGT-DISC-AGT-008 | `AgentDescriptor.domain_tags` MUST contain product/domain scope labels | MUST | BRD-AUTO-DISC-001, BRD-AUTO-DISC-007 | 1.3 | 25 Jan 2026 | Product-controlled exposure |
| AGT-DISC-AGT-009 | `AgentDescriptor.version` MUST contain semantic version string | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Versioned discovery |
| AGT-DISC-AGT-010 | `AgentDescriptor.requires_context_pack` MUST declare boolean for context pack dependency | MUST | BRD-AUTO-DISC-001, BRD-AUTO-DISC-004 | 1.3 | 25 Jan 2026 | Eligibility pre-check |
| AGT-DISC-AGT-011 | `AgentDescriptor.min_confidence_threshold` SHOULD declare minimum input confidence | SHOULD | BRD-AUTO-DISC-001, BRD-AUTO-DISC-004 | 1.3 | 25 Jan 2026 | Eligibility pre-check |
| AGT-DISC-AGT-012 | Agent descriptor MUST be accessible without instantiating agent execution context | MUST | BRD-AUTO-DISC-002 | 1.3 | 25 Jan 2026 | Registry scalability |

### 13.3 Descriptor Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-DISC-VAL-001 | Registry MUST validate all descriptors against Pydantic schema on registration | MUST | BRD-AUTO-DISC-002 | 1.3 | 25 Jan 2026 | Schema enforcement |
| AGT-DISC-VAL-002 | Registration MUST fail if `name` conflicts with existing registered entity | MUST | BRD-AUTO-DISC-002 | 1.3 | 25 Jan 2026 | Uniqueness constraint |
| AGT-DISC-VAL-003 | Registration MUST fail if required descriptor fields are missing or malformed | MUST | BRD-AUTO-DISC-002 | 1.3 | 25 Jan 2026 | Contract enforcement |
| AGT-DISC-VAL-004 | Registry MUST log validation errors with descriptor name and field details | MUST | BRD-AUTO-DISC-002 | 1.3 | 25 Jan 2026 | Debuggability |
| AGT-DISC-VAL-005 | Descriptor schema version MUST be checked for compatibility on registration | MUST | BRD-AUTO-DISC-008 | 1.3 | 25 Jan 2026 | Extensibility support |
| AGT-DISC-VAL-006 | Optional/experimental descriptor fields MUST NOT cause validation failure | MUST | BRD-AUTO-DISC-008 | 1.3 | 25 Jan 2026 | Forward compatibility |

### 13.4 Descriptor Schema Definition

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| AGT-DISC-SCHEMA-001 | `ToolDescriptor` Pydantic model MUST be defined in `core/contracts/descriptors_schema.py` | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Canonical location |
| AGT-DISC-SCHEMA-002 | `AgentDescriptor` Pydantic model MUST be defined in `core/contracts/descriptors_schema.py` | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Canonical location |
| AGT-DISC-SCHEMA-003 | Descriptor models MUST use strict Pydantic validation mode | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Type safety |
| AGT-DISC-SCHEMA-004 | Descriptor models MUST be frozen (immutable after creation) | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Registry consistency |
| AGT-DISC-SCHEMA-005 | Descriptor models MUST support JSON serialization for external tooling | MUST | BRD-AUTO-DISC-001 | 1.3 | 25 Jan 2026 | Interoperability |

---
