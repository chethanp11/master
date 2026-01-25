# Implementation Plan — V1.4 Tech Spec Requirements

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  
> **Version**: 1.3  
> **Last Updated**: 2026-01-25  
> **Status**: Ready for Implementation  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.3 | 2026-01-25 | V1.4 Tech Spec implementation plan: 28 GAPs → 25 IMP units covering Semantic Envelope Enforcement, Reasoning Contract, Sufficiency Gate, Discovery, HITL Binding, Enhanced Security, Policy Enforcement, Semantic Gate, Evidence Requirements, Decision Records, Confidence Enhancements, Invariant Tests |
| 1.2 | 2026-01-20 | V1.3 Tech Spec complete: 63 gaps closed via IMP-009 to IMP-030 |
| 1.1 | 2026-01-13 | Initial implementation plan |

---

## 1. Overview

### 1.1 Purpose

This document provides a **deterministic, linear implementation plan** for V1.4 Tech Spec requirements. Each implementation unit (IMP) is directly traceable to:
- Tech Spec requirement IDs (source of truth)
- SD-COVERAGE gap IDs (what needs implementation)

### 1.2 Assumptions

1. V1.3 implementation is complete and stable
2. All code targets `master/` codebase (core/, gateway/, storage/)
3. Products under `products/` are out of scope
4. Python 3.11+ environment with existing dependencies

### 1.3 Entry Criteria

- V1.3 Tech Spec implementation complete (SD-COVERAGE v1.3 GAP COUNT: 0)
- All existing tests passing
- `master` branch stable

### 1.4 Out of Scope

- Product-specific implementations (under `products/`)
- UI/UX changes beyond API contract updates
- Performance optimization (deferred to V1.5)
- External integrations (cloud providers, LLM providers)

---

## 2. Implementation Units

### IMP-031: Semantic Envelope Enforcement Schema

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-031 |
| **Source Tech Spec IDs** | ORC-SEM-ENV-001, ORC-SEM-ENV-002, ORC-SEM-ENV-003, ORC-SEM-ENV-004, ORC-SEM-ENV-005 |
| **Related SD-COVERAGE Gap IDs** | GAP-031 |
| **Target Code Locations** | `core/contracts/semantic_schema.py`, `core/orchestrator/engine.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/contracts/semantic_schema.py`
2. Add `all_constraints_satisfiable: bool` field to `SemanticEnvelope` model
3. Add `envelope_validated: bool = False` field to track validation state
4. Add `bypass_attempt_blocked: bool = False` field for audit
5. Open `core/orchestrator/engine.py`
6. In `_execute_planning_phase()`, add check: if `envelope is None`, raise `SemanticEnvelopeRequiredError`
7. Before planning invocation, validate `envelope.envelope_validated == True`
8. If bypass attempted, emit `envelope_bypass_blocked` trace event
9. Add `semantic_envelope_required` error code to error catalog

**Acceptance Checks:**

- [ ] `SemanticEnvelope` model includes `all_constraints_satisfiable` field
- [ ] Planning phase rejects invocation without valid envelope
- [ ] Bypass attempts emit trace event and fail with correct error code
- [ ] Unit tests in `tests/unit/core/contracts/test_semantic_envelope_enforcement.py`

---

### IMP-032: Confidence Gate at Semantic Phase Exit

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-032 |
| **Source Tech Spec IDs** | ORC-SEM-CONF-GATE-001...008 |
| **Related SD-COVERAGE Gap IDs** | GAP-032 |
| **Target Code Locations** | `core/orchestrator/engine.py`, `core/governance/hooks.py`, `core/memory/tracing.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/governance/hooks.py`
2. Extend `check_semantic_confidence()` to return `GateDecision` with `proceed: bool`, `reason: str`
3. Add parameter for `bypass_allowed: bool = False` (always False per spec)
4. Open `core/orchestrator/engine.py`
5. After semantic interpretation, invoke `check_semantic_confidence(envelope, threshold)`
6. If `effective_confidence < threshold`, transition run to `PAUSED_WAITING_FOR_USER`
7. Generate `ClarificationRequest` with confidence context
8. Open `core/memory/tracing.py`
9. Add `TraceEventType.CONFIDENCE_GATE_EVALUATED` with fields: `threshold`, `effective_confidence`, `decision`
10. Emit trace event on every gate evaluation

**Acceptance Checks:**

- [ ] Confidence gate invoked after semantic phase
- [ ] Low confidence triggers PAUSED_WAITING_FOR_USER
- [ ] No configuration can disable the gate
- [ ] `confidence_gate_evaluated` trace event emitted
- [ ] Unit tests in `tests/unit/core/orchestrator/test_confidence_gate.py`

---

### IMP-033: Ambiguity Detection and Tracking

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-033 |
| **Source Tech Spec IDs** | ORC-SEM-AMB-001...006 |
| **Related SD-COVERAGE Gap IDs** | GAP-033 |
| **Target Code Locations** | `core/contracts/semantic_schema.py`, `core/orchestrator/engine.py`, `core/orchestrator/normalization.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/contracts/semantic_schema.py`
2. Create `Ambiguity` Pydantic model with fields:
   - `ambiguity_id: str`
   - `description: str`
   - `options: List[str]`
   - `source_span: Tuple[int, int]` (start, end position)
   - `resolution_method: Optional[str]`
   - `selected_option: Optional[str]`
3. Update `SemanticEnvelope.ambiguities` from `List[str]` to `List[Ambiguity]`
4. Add `ambiguity_count: int` computed property
5. Open `core/orchestrator/normalization.py`
6. Add `max_allowed_ambiguities` config parameter (default: 3)
7. Open `core/orchestrator/engine.py`
8. After normalization, check `if ambiguity_count > max_allowed_ambiguities`
9. If exceeded, fail with `excessive_ambiguity` error code
10. Include `ambiguity_count` in `semantic_interpretation_completed` trace event

**Acceptance Checks:**

- [ ] `Ambiguity` model defined with all required fields
- [ ] Ambiguities cannot be silently resolved without recording method
- [ ] `ambiguity_count` in trace event
- [ ] Excessive ambiguity blocks execution
- [ ] Unit tests in `tests/unit/core/contracts/test_ambiguity_schema.py`

---

### IMP-034: Minimum Reasoning Contract Enforcement

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-034 |
| **Source Tech Spec IDs** | ORC-REASON-CONTRACT-001...011 |
| **Related SD-COVERAGE Gap IDs** | GAP-034 |
| **Target Code Locations** | `core/orchestrator/reasoning_lifecycle.py`, `core/orchestrator/flow_loader.py`, `core/contracts/reasoning_schema.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/contracts/reasoning_schema.py`
2. Add `ReasoningContract` model with:
   - `mandatory_phases: List[ReasoningPhase]` (INTERPRET, PROPOSE are always required)
   - `critique_waiver: bool = False`
   - `waiver_reason: Optional[str]`
3. Open `core/orchestrator/flow_loader.py`
4. In `validate_flow()`, check that all mandatory reasoning phases are defined
5. If mandatory phases missing, raise `FlowValidationError` with `reasoning_contract_violation`
6. Open `core/orchestrator/reasoning_lifecycle.py`
7. Before each phase transition, validate phase is allowed by contract
8. If `critique_waiver: true` without `waiver_reason`, fail validation
9. If waiver present, emit `critique_phase_waived` trace event with reason
10. Still record confidence even when critique is waived

**Acceptance Checks:**

- [ ] Flow validation fails if mandatory phases missing
- [ ] Critique waiver requires explicit reason
- [ ] `critique_phase_waived` trace event emitted
- [ ] Bypass attempts fail with `reasoning_contract_violation`
- [ ] Unit tests in `tests/unit/core/orchestrator/test_reasoning_contract.py`

---

### IMP-035: Intent Sufficiency Gate

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-035 |
| **Source Tech Spec IDs** | ORC-SUFF-GATE-001...008 |
| **Related SD-COVERAGE Gap IDs** | GAP-035 |
| **Target Code Locations** | `core/orchestrator/engine.py`, `core/knowledge/sufficiency_manager.py`, `core/governance/gates.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/governance/gates.py`
2. Create `IntentSufficiencyGate` class extending `BaseGate`
3. Implement `evaluate(context: RunContext) -> GateResult` method
4. Gate checks `SufficiencyState.gaps.count == 0` or all gaps are non-blocking
5. Open `core/orchestrator/engine.py`
6. Before tool selection phase, invoke `IntentSufficiencyGate.evaluate()`
7. If gate fails, emit `sufficiency_gate_blocked` trace event
8. Transition to `PAUSED_WAITING_FOR_USER` with gap information
9. Add `sufficiency_gate_evaluated` trace event type
10. Include `gap_count`, `blocking_gaps`, `decision` in event payload

**Acceptance Checks:**

- [ ] `IntentSufficiencyGate` class exists
- [ ] Gate evaluated before tool selection
- [ ] Blocking gaps prevent execution
- [ ] Trace events emitted
- [ ] Unit tests in `tests/unit/core/governance/test_sufficiency_gate.py`

---

### IMP-036: Tool & Agent Discovery Engine

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-036 |
| **Source Tech Spec IDs** | INT-DISC-001...010, INT-DISC-019...028, INT-DISC-038...045 |
| **Related SD-COVERAGE Gap IDs** | GAP-036 (partial) |
| **Target Code Locations** | `core/agents/discovery.py` (new), `core/tools/discovery.py` (new), `core/knowledge/discovery_engine.py` (new) |
| **Type of Change** | New file |

**Step-by-Step Instructions:**

1. Create `core/knowledge/discovery_engine.py`
2. Define `DiscoveryEngine` class with methods:
   - `discover_tools(intent: str, context: RunContext) -> List[ToolCandidate]`
   - `discover_agents(intent: str, context: RunContext) -> List[AgentCandidate]`
3. Implement intent-filtered discovery using capability tags
4. Create `ToolCandidate` and `AgentCandidate` dataclasses with `name`, `confidence`, `match_reason`
5. Implement capability matching via `_match_capabilities(intent, descriptor) -> float`
6. Create `core/agents/discovery.py` with agent-specific discovery logic
7. Create `core/tools/discovery.py` with tool-specific discovery logic
8. Integrate with existing `AgentRegistry` and `ToolRegistry`
9. Add `discovery_completed` trace event with candidates list
10. Emit `tool_discovery_started`, `tool_discovery_completed` events

**Acceptance Checks:**

- [ ] `DiscoveryEngine` class exists
- [ ] Intent-filtered discovery returns ranked candidates
- [ ] Capability matching produces confidence scores
- [ ] Trace events emitted
- [ ] Unit tests in `tests/unit/core/knowledge/test_discovery_engine.py`

---

### IMP-037: Discovery Registry Integration

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-037 |
| **Source Tech Spec IDs** | INT-DISC-011...018, INT-DISC-046...054 |
| **Related SD-COVERAGE Gap IDs** | GAP-036 (partial) |
| **Target Code Locations** | `core/agents/registry.py`, `core/tools/registry.py`, `core/knowledge/discovery_engine.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/agents/registry.py`
2. Add `get_all_descriptors() -> List[AgentDescriptor]` method
3. Add `filter_by_capability_tags(tags: List[str]) -> List[str]` method
4. Open `core/tools/registry.py`
5. Add `get_all_descriptors() -> List[ToolDescriptor]` method
6. Add `filter_by_capability_tags(tags: List[str]) -> List[str]` method
7. Open `core/knowledge/discovery_engine.py`
8. Implement `DiscoveryStrategy` abstract base class
9. Create `DefaultDiscoveryStrategy` implementation
10. Add `register_strategy(name: str, strategy: DiscoveryStrategy)` for extensibility
11. Emit `registry_queried` trace event when discovery queries registry

**Acceptance Checks:**

- [ ] Registry exposes descriptor access methods
- [ ] Discovery engine uses strategy pattern
- [ ] Custom strategies can be registered
- [ ] Unit tests in `tests/unit/core/agents/test_registry_discovery.py`

---

### IMP-038: Discovery Eligibility Checks

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-038 |
| **Source Tech Spec IDs** | INT-DISC-029...037 |
| **Related SD-COVERAGE Gap IDs** | GAP-036 (partial) |
| **Target Code Locations** | `core/knowledge/discovery_engine.py`, `core/governance/budgeting.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/knowledge/discovery_engine.py`
2. Add `EligibilityChecker` class with methods:
   - `check_budget_eligibility(candidate, budget: BudgetState) -> bool`
   - `check_confidence_eligibility(candidate, min_confidence: float) -> bool`
   - `check_context_eligibility(candidate, context: RunContext) -> bool`
3. Implement composite `check_eligibility(candidate, context) -> EligibilityResult`
4. Create `EligibilityResult` dataclass with `eligible: bool`, `reasons: List[str]`
5. Filter discovery results through eligibility checks
6. Add `candidate_excluded` trace event for ineligible candidates
7. Open `core/governance/budgeting.py`
8. Add `can_afford_tool(tool_name: str, budget: BudgetState) -> bool` method
9. Add `estimated_cost_by_tool(tool_name: str) -> int` method

**Acceptance Checks:**

- [ ] `EligibilityChecker` class exists
- [ ] Budget-exhausted tools excluded
- [ ] Low-confidence candidates excluded
- [ ] Exclusion reasons traced
- [ ] Unit tests in `tests/unit/core/knowledge/test_eligibility_checker.py`

---

### IMP-039: Discovery Phase Separation

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-039 |
| **Source Tech Spec IDs** | INT-DISC-055...073 |
| **Related SD-COVERAGE Gap IDs** | GAP-036 (partial) |
| **Target Code Locations** | `core/knowledge/discovery_engine.py`, `core/orchestrator/engine.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/knowledge/discovery_engine.py`
2. Separate `discover()` from `select()` as distinct phases
3. `discover()` returns all candidates meeting criteria
4. `select()` chooses final candidates from discovered set
5. Add product domain scoping via `domain_tags` filter
6. Implement deterministic selection with version/hash for reproducibility
7. Open `core/orchestrator/engine.py`
8. Call `discover()` phase first, then `select()` phase
9. Emit separate trace events: `discovery_phase_completed`, `selection_phase_completed`
10. Include `discovery_hash` in selection event for reproducibility

**Acceptance Checks:**

- [ ] Discovery and selection are separate invocations
- [ ] Product domain scoping works via domain_tags
- [ ] Selection is deterministic given same inputs
- [ ] `discovery_hash` in trace for reproducibility
- [ ] Unit tests in `tests/unit/core/knowledge/test_discovery_phases.py`

---

### IMP-040: Tool Descriptor Contract

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-040 |
| **Source Tech Spec IDs** | AGT-DISC-TOOL-001...012 |
| **Related SD-COVERAGE Gap IDs** | GAP-037 |
| **Target Code Locations** | `core/contracts/descriptors_schema.py` (new), `core/tools/base.py` |
| **Type of Change** | New file + Extend existing |

**Step-by-Step Instructions:**

1. Create `core/contracts/descriptors_schema.py`
2. Define `ToolDescriptor` Pydantic model with:
   - `name: str` (globally unique)
   - `description: str` (human-readable)
   - `capability_tags: List[str]`
   - `input_schema: Type[BaseModel]` or JSON Schema reference
   - `output_schema: Type[BaseModel]` or JSON Schema reference
   - `side_effects: bool`
   - `deterministic: bool`
   - `domain_tags: Optional[List[str]]`
   - `version: str` (semantic version)
   - `deprecation: Optional[str]`
3. Set `frozen=True` for immutability
4. Add `model_config = ConfigDict(strict=True)` for strict validation
5. Open `core/tools/base.py`
6. Add abstract `descriptor` property to `BaseTool`
7. Descriptor must be accessible without instantiation (class property)
8. Add JSON serialization method for external tooling

**Acceptance Checks:**

- [ ] `ToolDescriptor` model defined with all fields
- [ ] Model is frozen (immutable)
- [ ] Strict validation mode enabled
- [ ] `BaseTool.descriptor` property exists
- [ ] Unit tests in `tests/unit/core/contracts/test_tool_descriptor.py`

---

### IMP-041: Agent Descriptor Contract

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-041 |
| **Source Tech Spec IDs** | AGT-DISC-AGT-001...012 |
| **Related SD-COVERAGE Gap IDs** | GAP-038 |
| **Target Code Locations** | `core/contracts/descriptors_schema.py`, `core/agents/base.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/contracts/descriptors_schema.py`
2. Define `AgentDescriptor` Pydantic model with:
   - `name: str` (globally unique)
   - `description: str` (human-readable)
   - `capability_tags: List[str]`
   - `input_schema: Type[BaseModel]` reference
   - `output_schema: Type[BaseModel]` reference
   - `reasoning_type: ReasoningType` enum (advisory, critic, ladder, etc.)
   - `domain_tags: List[str]`
   - `version: str`
   - `requires_context_pack: bool`
   - `min_confidence_threshold: Optional[float]`
3. Set `frozen=True` for immutability
4. Open `core/agents/base.py`
5. Add abstract `descriptor` property to `BaseAgent`
6. Descriptor must be accessible without instantiation (class property)

**Acceptance Checks:**

- [ ] `AgentDescriptor` model defined with all fields
- [ ] Model is frozen (immutable)
- [ ] `BaseAgent.descriptor` property exists
- [ ] Unit tests in `tests/unit/core/contracts/test_agent_descriptor.py`

---

### IMP-042: Descriptor Validation in Registry

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-042 |
| **Source Tech Spec IDs** | AGT-DISC-VAL-001...006, AGT-DISC-SCHEMA-001...005 |
| **Related SD-COVERAGE Gap IDs** | GAP-039, GAP-040 |
| **Target Code Locations** | `core/agents/registry.py`, `core/tools/registry.py`, `core/contracts/descriptors_schema.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/agents/registry.py`
2. In `register()` method, validate descriptor against `AgentDescriptor` schema
3. Reject registration if `name` conflicts with existing entity
4. Reject registration if required fields missing or malformed
5. Log validation errors with descriptor name and field details
6. Check descriptor schema version for compatibility
7. Allow optional/experimental fields without validation failure
8. Open `core/tools/registry.py`
9. Apply same validation logic for `ToolDescriptor`
10. Emit `registration_failed` trace event on validation errors

**Acceptance Checks:**

- [ ] Registration validates descriptor schema
- [ ] Name conflicts rejected
- [ ] Missing fields rejected with error details
- [ ] Optional fields don't cause failures
- [ ] Unit tests in `tests/unit/core/agents/test_registry_validation.py`

---

### IMP-043: HITL Binding Requirements

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-043 |
| **Source Tech Spec IDs** | GOV-HITL-BIND-001...007, GOV-HITL-DECL-001...005 |
| **Related SD-COVERAGE Gap IDs** | GAP-041, GAP-042 |
| **Target Code Locations** | `core/governance/hooks.py`, `core/governance/hitl_binding.py` (new), `products/*/manifest.yaml` |
| **Type of Change** | New file + Extend existing |

**Step-by-Step Instructions:**

1. Create `core/governance/hitl_binding.py`
2. Define `HITLBinding` class with:
   - `escalation_paths: Dict[str, EscalationPath]`
   - `immutable: bool = True` (enforced at runtime)
3. Define `EscalationPath` model with trigger conditions
4. Add `is_runtime_modifiable() -> bool` returning False
5. Open `core/governance/hooks.py`
6. Add `check_hitl_binding_immutable()` hook
7. Reject any runtime modification attempts to HITL bindings
8. Emit `hitl_binding_modification_blocked` trace event on attempts
9. Validate HITL conditions at product registration time
10. Store HITL declarations in product manifest schema

**Acceptance Checks:**

- [ ] `HITLBinding` class exists
- [ ] Runtime modifications blocked
- [ ] HITL conditions declared at registration
- [ ] Trace events on modification attempts
- [ ] Unit tests in `tests/unit/core/governance/test_hitl_binding.py`

---

### IMP-044: Enhanced PII Detection

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-044 |
| **Source Tech Spec IDs** | GOV-SEC-PII-001...005 |
| **Related SD-COVERAGE Gap IDs** | GAP-043 |
| **Target Code Locations** | `core/governance/security.py`, `core/governance/pii_detector.py` (new) |
| **Type of Change** | New file + Extend existing |

**Step-by-Step Instructions:**

1. Create `core/governance/pii_detector.py`
2. Define `PIIDetector` class with:
   - `detect_named_entities(text: str) -> List[PIIEntity]`
   - `detect_patterns(text: str) -> List[PIIMatch]`
3. Define `PIIEntity` model with `entity_type`, `value`, `span`, `confidence`
4. Implement NER-based detection (use simple pattern + keyword matching for V1)
5. Add entity types: PERSON, ORGANIZATION, LOCATION, DATE, etc.
6. Open `core/governance/security.py`
7. Integrate `PIIDetector` into `SecurityRedactor`
8. Use NER results to enhance redaction coverage
9. Emit `pii_detected` trace event with entity counts (not values)
10. Add configuration for NER sensitivity levels

**Acceptance Checks:**

- [ ] `PIIDetector` class exists
- [ ] Named entity detection implemented
- [ ] Integration with SecurityRedactor
- [ ] Trace events emitted
- [ ] Unit tests in `tests/unit/core/governance/test_pii_detector.py`

---

### IMP-045: Cloud Credential Patterns

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-045 |
| **Source Tech Spec IDs** | GOV-SEC-CRED-001...005 |
| **Related SD-COVERAGE Gap IDs** | GAP-044 |
| **Target Code Locations** | `core/governance/security.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/governance/security.py`
2. Add AWS credential patterns:
   - `AKIA[0-9A-Z]{16}` (access key ID)
   - `[A-Za-z0-9/+=]{40}` with context for secret key
3. Add GCP credential patterns:
   - Service account JSON structure detection
   - `AIza[0-9A-Za-z\\-_]{35}` (API key)
4. Add Azure credential patterns:
   - Connection strings with AccountKey
   - SAS token patterns
5. Add GitHub patterns:
   - `ghp_[a-zA-Z0-9]{36}` (personal access token)
   - `gho_[a-zA-Z0-9]{36}` (OAuth token)
6. Update `DEFAULT_SENSITIVE_PATTERNS` list
7. Emit `cloud_credential_redacted` trace event with provider type

**Acceptance Checks:**

- [ ] AWS patterns added and tested
- [ ] GCP patterns added and tested
- [ ] Azure patterns added and tested
- [ ] GitHub patterns added and tested
- [ ] Unit tests in `tests/unit/core/governance/test_cloud_credentials.py`

---

### IMP-046: Automatic Redaction Enforcement

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-046 |
| **Source Tech Spec IDs** | GOV-SEC-AUTO-001...005 |
| **Related SD-COVERAGE Gap IDs** | GAP-045 |
| **Target Code Locations** | `core/governance/security.py`, `core/memory/tracing.py`, `gateway/api/routes_run.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/governance/security.py`
2. Create `AutoRedactionEnforcer` class
3. Add `enforce_on_output(data: Any) -> Any` method
4. Apply redaction to all output paths:
   - Trace event payloads
   - API responses
   - Artifact contents
   - Log messages
5. Open `core/memory/tracing.py`
6. Wrap all `emit_event()` calls with auto-redaction
7. Open `gateway/api/routes_run.py`
8. Apply redaction to all response payloads
9. Emit `auto_redaction_applied` trace event when redaction occurs
10. Make auto-redaction non-bypassable

**Acceptance Checks:**

- [ ] `AutoRedactionEnforcer` class exists
- [ ] All output paths covered
- [ ] Cannot be disabled
- [ ] Trace events emitted
- [ ] Integration tests in `tests/integration/test_auto_redaction.py`

---

### IMP-047: Policy Bypass Prevention

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-047 |
| **Source Tech Spec IDs** | GOV-POL-NOBYPASS-001...005, GOV-POL-BLOCK-001...005 |
| **Related SD-COVERAGE Gap IDs** | GAP-046, GAP-047 |
| **Target Code Locations** | `core/governance/policies.py`, `core/governance/hooks.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/governance/policies.py`
2. Remove any `enforce=false` functionality
3. Mark policy methods as final (no override)
4. Add `_bypass_attempted` flag to detect attempts
5. Open `core/governance/hooks.py`
6. In `before_tool`, `before_model` hooks:
   - Remove grace period logic
   - Block immediately on violation
7. Emit `policy_bypass_blocked` trace event on bypass attempts
8. Emit `policy_violation_blocked` trace event on violations
9. Add `POLICY_VIOLATION_IMMEDIATE` error code
10. Ensure no configuration can disable policy checks

**Acceptance Checks:**

- [ ] No bypass configuration exists
- [ ] Violations block immediately
- [ ] Trace events emitted
- [ ] Unit tests in `tests/unit/core/governance/test_policy_enforcement.py`

---

### IMP-048: Hard Budget Limits

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-048 |
| **Source Tech Spec IDs** | GOV-BUD-HARD-001...005 |
| **Related SD-COVERAGE Gap IDs** | GAP-048 |
| **Target Code Locations** | `core/governance/budgeting.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/governance/budgeting.py`
2. Remove any overdraft allowance logic
3. In `consume_budget()`:
   - Pre-check if operation would exceed limit
   - Reject if would exceed (not post-hoc)
4. Add `allow_overdraft: bool = False` (always False, for documentation)
5. Emit `budget_limit_reached` trace event when at limit
6. Emit `budget_operation_rejected` when operation would exceed
7. Add `BUDGET_HARD_LIMIT_EXCEEDED` error code
8. Include `requested_amount`, `remaining_budget`, `limit` in error details

**Acceptance Checks:**

- [ ] No overdraft possible
- [ ] Pre-check before consumption
- [ ] Trace events emitted
- [ ] Unit tests in `tests/unit/core/governance/test_hard_budget.py`

---

### IMP-049: Semantic Gate Implementation

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-049 |
| **Source Tech Spec IDs** | GOV-GATE-SEM-001...012, GOV-GATE-SUFF-001...006 |
| **Related SD-COVERAGE Gap IDs** | GAP-049, GAP-050 |
| **Target Code Locations** | `core/governance/gates.py`, `core/governance/semantic_gate.py` (new) |
| **Type of Change** | New file + Extend existing |

**Step-by-Step Instructions:**

1. Create `core/governance/semantic_gate.py`
2. Define `SemanticGate` class extending `BaseGate`:
   - `validate_envelope_completeness(envelope) -> bool`
   - `validate_confidence_threshold(envelope, threshold) -> bool`
   - `validate_intent_sufficiency(envelope, sufficiency_state) -> bool`
3. Implement `evaluate(context) -> SemanticGateResult`
4. Create `SemanticGateResult` with all validation outcomes
5. Open `core/governance/gates.py`
6. Register `SemanticGate` in `GateRegistry`
7. Add gate evaluation before planning phase
8. Emit `semantic_gate_evaluated` trace event with all inputs
9. On rejection, emit `semantic_gate_rejected` trace event

**Acceptance Checks:**

- [ ] `SemanticGate` class exists
- [ ] Envelope completeness validated
- [ ] Confidence threshold validated
- [ ] Intent sufficiency validated
- [ ] Unit tests in `tests/unit/core/governance/test_semantic_gate.py`

---

### IMP-050: Gate Rejection Artifacts

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-050 |
| **Source Tech Spec IDs** | GOV-GATE-REJ-001...010 |
| **Related SD-COVERAGE Gap IDs** | GAP-051 |
| **Target Code Locations** | `core/contracts/gate_schema.py` (new), `core/governance/gates.py` |
| **Type of Change** | New file + Extend existing |

**Step-by-Step Instructions:**

1. Create `core/contracts/gate_schema.py`
2. Define `GateRejectionArtifact` Pydantic model:
   - `rejection_id: str`
   - `gate_name: str`
   - `rejection_reason: str`
   - `gate_inputs: Dict[str, Any]`
   - `timestamp: datetime`
   - `run_id: str`
   - `recommendations: List[str]`
3. Open `core/governance/gates.py`
4. In `evaluate()` failure path, create `GateRejectionArtifact`
5. Persist artifact via memory backend
6. Emit `gate_rejection_artifact_created` trace event
7. Include full gate inputs in trace event for auditability
8. Add `get_rejection_artifact(rejection_id)` method

**Acceptance Checks:**

- [ ] `GateRejectionArtifact` model defined
- [ ] Artifacts created on rejection
- [ ] Artifacts persisted
- [ ] Full traceability in events
- [ ] Unit tests in `tests/unit/core/contracts/test_gate_rejection.py`

---

### IMP-051: Evidence Requirements

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-051 |
| **Source Tech Spec IDs** | GOV-EVID-001...005, GOV-EVID-CONF-001...005, GOV-EVID-TRACE-001...005 |
| **Related SD-COVERAGE Gap IDs** | GAP-052, GAP-053, GAP-054 |
| **Target Code Locations** | `core/governance/evidence_requirements.py` (new), `core/knowledge/context_pack.py` |
| **Type of Change** | New file + Extend existing |

**Step-by-Step Instructions:**

1. Create `core/governance/evidence_requirements.py`
2. Define `EvidenceRequirement` model with:
   - `requirement_id: str`
   - `description: str`
   - `minimum_confidence: float`
   - `required_sources: List[str]`
3. Define `EvidenceValidator` class:
   - `validate_decision_has_evidence(decision, context_pack) -> bool`
   - `propagate_evidence_confidence(decision) -> float`
   - `check_missing_evidence(decision) -> List[MissingEvidence]`
4. Open `core/knowledge/context_pack.py`
5. Add `get_evidence_for_decision(decision_id) -> List[Evidence]`
6. If evidence missing, trigger clarification request
7. Emit `evidence_validation_completed` trace event
8. Emit `missing_evidence_detected` trace event if gaps found

**Acceptance Checks:**

- [ ] `EvidenceValidator` class exists
- [ ] Decisions require evidence citations
- [ ] Evidence confidence propagates
- [ ] Missing evidence triggers clarification
- [ ] Unit tests in `tests/unit/core/governance/test_evidence_requirements.py`

---

### IMP-052: Decision Record Artifacts

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-052 |
| **Source Tech Spec IDs** | GOV-DEC-RECORD-001...010 |
| **Related SD-COVERAGE Gap IDs** | GAP-055 |
| **Target Code Locations** | `core/contracts/decision_schema.py` (new), `core/orchestrator/reasoning_lifecycle.py` |
| **Type of Change** | New file + Extend existing |

**Step-by-Step Instructions:**

1. Create `core/contracts/decision_schema.py`
2. Define `DecisionRecord` Pydantic model:
   - `decision_id: str`
   - `decision_type: DecisionType` enum
   - `timestamp: datetime`
   - `run_id: str`
   - `phase: ReasoningPhase`
   - `options_considered: List[Option]`
   - `selected_option: Option`
   - `selection_rationale: str`
   - `confidence: float`
   - `evidence_refs: List[str]`
   - `approver: Optional[str]`
3. Open `core/orchestrator/reasoning_lifecycle.py`
4. After each decision point, create `DecisionRecord`
5. Persist decision record via memory backend
6. Emit `decision_recorded` trace event
7. Add `list_decisions(run_id) -> List[DecisionRecord]` to memory API
8. Add `get_decision_chain(run_id) -> List[DecisionRecord]` method

**Acceptance Checks:**

- [ ] `DecisionRecord` model defined
- [ ] All decisions recorded
- [ ] Decisions persisted
- [ ] Decision chain queryable
- [ ] Unit tests in `tests/unit/core/contracts/test_decision_record.py`

---

### IMP-053: Enhanced Confidence Governance

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-053 |
| **Source Tech Spec IDs** | GOV-SEM-CONF-008...018 |
| **Related SD-COVERAGE Gap IDs** | GAP-056 |
| **Target Code Locations** | `core/knowledge/confidence.py`, `core/governance/hooks.py` |
| **Type of Change** | Extend existing module |

**Step-by-Step Instructions:**

1. Open `core/knowledge/confidence.py`
2. Add `ConfidenceAggregationStrategy` enum: MIN, MAX, WEIGHTED, PRODUCT
3. Add `aggregate_multi_source(confidences: List[float], strategy: ConfidenceAggregationStrategy) -> float`
4. Implement each aggregation strategy
5. Add `apply_confidence_decay(confidence: float, iteration: int, decay_rate: float) -> float`
6. Add `CONFIDENCE_FLOOR = 0.5` constant
7. Add `validate_confidence_floor(threshold: float, floor: float) -> float`
8. Open `core/governance/hooks.py`
9. Use aggregation in `check_semantic_confidence()`
10. Apply decay when reasoning iterates
11. Emit `confidence_aggregated` trace event with strategy and sources

**Acceptance Checks:**

- [ ] Multiple aggregation strategies implemented
- [ ] Confidence decay over iterations
- [ ] Confidence floor enforced
- [ ] Trace events emitted
- [ ] Unit tests in `tests/unit/core/knowledge/test_enhanced_confidence.py`

---

### IMP-054: Executable Invariant Tests

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-054 |
| **Source Tech Spec IDs** | ACC-INV-EXEC-001...015 |
| **Related SD-COVERAGE Gap IDs** | GAP-057 |
| **Target Code Locations** | `tests/architecture/test_invariants.py` (new) |
| **Type of Change** | Tests only |

**Step-by-Step Instructions:**

1. Create `tests/architecture/test_invariants.py`
2. Add `@pytest.mark.invariant` marker to all tests
3. Implement `test_products_no_semantic_reimplementation()`:
   - Scan `products/` for semantic logic patterns
   - Assert all semantic imports from `core/`
4. Implement `test_products_no_validation_reimplementation()`:
   - Scan `products/` for validation patterns
   - Assert all validation imports from `core/contracts/`
5. Implement `test_products_no_confidence_reimplementation()`:
   - Scan `products/` for confidence logic
   - Assert all confidence imports from `core/knowledge/`
6. Implement duplication detection tests:
   - Detect SemanticEnvelope, Confidence, Validation class definitions in products
   - Fail if found
7. Verify product imports use `from core.` prefix
8. Add structured error report generation on failure

**Acceptance Checks:**

- [ ] All invariant tests marked with `@pytest.mark.invariant`
- [ ] Product duplication detection works
- [ ] Structured error report on failure
- [ ] Tests pass on clean codebase

---

### IMP-055: Invariant CI/CD Gate

| Field | Value |
|-------|-------|
| **Unit ID** | IMP-055 |
| **Source Tech Spec IDs** | ACC-CI-INV-001...007 |
| **Related SD-COVERAGE Gap IDs** | GAP-058 |
| **Target Code Locations** | `.github/workflows/ci.yaml` or equivalent CI config, `pytest.ini` |
| **Type of Change** | Wiring / integration |

**Step-by-Step Instructions:**

1. Open CI configuration file (`.github/workflows/ci.yaml` or equivalent)
2. Add `invariant-check` job/stage
3. Configure job to run: `pytest -m invariant tests/architecture/`
4. Set job to run before `deploy` stage
5. Ensure job failure sets pipeline status to FAILED
6. Remove any `allow_failure: true` from job config
7. Add artifact upload for test results
8. Open `pytest.ini`
9. Register `invariant` marker: `markers = invariant: marks tests as invariant checks`
10. Add coverage report generation for invariant tests

**Acceptance Checks:**

- [ ] `invariant-check` job exists in CI
- [ ] Job runs before deploy
- [ ] Job failure blocks pipeline
- [ ] Test results uploaded as artifact
- [ ] `pytest.ini` has invariant marker registered

---

## 3. Dependency Order

### 3.1 Implementation Sequence

```
Phase 1: Schema & Contract Additions (Foundation)
├── IMP-040: Tool Descriptor Contract
├── IMP-041: Agent Descriptor Contract
├── IMP-033: Ambiguity Detection Schema
└── IMP-031: Semantic Envelope Enforcement Schema

Phase 2: Core Infrastructure
├── IMP-042: Descriptor Validation in Registry
├── IMP-036: Discovery Engine (depends on IMP-040, IMP-041)
├── IMP-037: Registry Integration (depends on IMP-042)
└── IMP-038: Eligibility Checks (depends on IMP-036)

Phase 3: Gate Implementations
├── IMP-032: Confidence Gate (depends on IMP-031)
├── IMP-035: Sufficiency Gate
├── IMP-049: Semantic Gate (depends on IMP-032, IMP-033)
└── IMP-050: Gate Rejection Artifacts (depends on IMP-049)

Phase 4: Governance Enhancements
├── IMP-043: HITL Binding
├── IMP-044: Enhanced PII Detection
├── IMP-045: Cloud Credential Patterns
├── IMP-046: Automatic Redaction Enforcement (depends on IMP-044, IMP-045)
├── IMP-047: Policy Bypass Prevention
└── IMP-048: Hard Budget Limits

Phase 5: Reasoning & Evidence
├── IMP-034: Reasoning Contract (depends on IMP-032)
├── IMP-039: Discovery Phase Separation (depends on IMP-036, IMP-037)
├── IMP-051: Evidence Requirements
├── IMP-052: Decision Records (depends on IMP-051)
└── IMP-053: Enhanced Confidence (depends on IMP-032)

Phase 6: Testing & CI
├── IMP-054: Invariant Tests
└── IMP-055: CI/CD Gate (depends on IMP-054)
```

### 3.2 Preconditions

| IMP Unit | Preconditions |
|----------|---------------|
| IMP-031 | V1.3 complete |
| IMP-032 | IMP-031 |
| IMP-033 | V1.3 complete |
| IMP-034 | IMP-032 |
| IMP-035 | V1.3 complete |
| IMP-036 | IMP-040, IMP-041 |
| IMP-037 | IMP-042 |
| IMP-038 | IMP-036 |
| IMP-039 | IMP-036, IMP-037 |
| IMP-040 | V1.3 complete |
| IMP-041 | V1.3 complete |
| IMP-042 | V1.3 complete |
| IMP-043 | V1.3 complete |
| IMP-044 | V1.3 complete |
| IMP-045 | V1.3 complete |
| IMP-046 | IMP-044, IMP-045 |
| IMP-047 | V1.3 complete |
| IMP-048 | V1.3 complete |
| IMP-049 | IMP-032, IMP-033 |
| IMP-050 | IMP-049 |
| IMP-051 | V1.3 complete |
| IMP-052 | IMP-051 |
| IMP-053 | IMP-032 |
| IMP-054 | All code units complete |
| IMP-055 | IMP-054 |

---

## 4. Risk & Rollback Notes

### 4.1 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Schema changes break existing tests | Medium | Medium | Run full test suite after each schema change |
| Discovery engine performance impact | Low | Medium | Add performance benchmarks, optimize if needed |
| Gate logic too strict | Medium | High | Configurable thresholds, start with warnings |
| Cloud credential patterns false positives | Medium | Low | Pattern tuning, exemption mechanism |
| CI gate blocks legitimate deploys | Low | High | Manual override with approval trail |

### 4.2 Validation Strategy

1. **After each IMP unit**: Run `pytest tests/unit/` for affected modules
2. **After each phase**: Run `pytest tests/integration/`
3. **Before final merge**: Run full `pytest` suite
4. **Performance check**: Compare test duration before/after

### 4.3 Rollback Strategy

- Each IMP unit modifies specific files listed in "Target Code Locations"
- Git revert for each unit is: `git revert <commit-hash-for-IMP-###>`
- Schema rollback may require database migration (MEM modules)
- Test-only units (IMP-054, IMP-055) can be reverted independently

---

## 5. Final Verification Checklist

### 5.1 Tech Spec ID Coverage

| Tech Spec Range | IMP Units | Status |
|-----------------|-----------|--------|
| ORC-SEM-ENV-001...005 | IMP-031 | ⏳ Planned |
| ORC-SEM-CONF-GATE-001...008 | IMP-032 | ⏳ Planned |
| ORC-SEM-AMB-001...006 | IMP-033 | ⏳ Planned |
| ORC-REASON-CONTRACT-001...011 | IMP-034 | ⏳ Planned |
| ORC-SUFF-GATE-001...008 | IMP-035 | ⏳ Planned |
| INT-DISC-001...073 | IMP-036, IMP-037, IMP-038, IMP-039 | ⏳ Planned |
| AGT-DISC-TOOL-001...012 | IMP-040 | ⏳ Planned |
| AGT-DISC-AGT-001...012 | IMP-041 | ⏳ Planned |
| AGT-DISC-VAL-001...006 | IMP-042 | ⏳ Planned |
| AGT-DISC-SCHEMA-001...005 | IMP-042 | ⏳ Planned |
| GOV-HITL-BIND-001...007 | IMP-043 | ⏳ Planned |
| GOV-HITL-DECL-001...005 | IMP-043 | ⏳ Planned |
| GOV-SEC-PII-001...005 | IMP-044 | ⏳ Planned |
| GOV-SEC-CRED-001...005 | IMP-045 | ⏳ Planned |
| GOV-SEC-AUTO-001...005 | IMP-046 | ⏳ Planned |
| GOV-POL-NOBYPASS-001...005 | IMP-047 | ⏳ Planned |
| GOV-POL-BLOCK-001...005 | IMP-047 | ⏳ Planned |
| GOV-BUD-HARD-001...005 | IMP-048 | ⏳ Planned |
| GOV-GATE-SEM-001...012 | IMP-049 | ⏳ Planned |
| GOV-GATE-SUFF-001...006 | IMP-049 | ⏳ Planned |
| GOV-GATE-REJ-001...010 | IMP-050 | ⏳ Planned |
| GOV-EVID-001...015 | IMP-051 | ⏳ Planned |
| GOV-DEC-RECORD-001...010 | IMP-052 | ⏳ Planned |
| GOV-SEM-CONF-008...018 | IMP-053 | ⏳ Planned |
| ACC-INV-EXEC-001...015 | IMP-054 | ⏳ Planned |
| ACC-CI-INV-001...007 | IMP-055 | ⏳ Planned |

### 5.2 Gap Coverage Verification

- [ ] All 28 SD-COVERAGE gaps (GAP-031 to GAP-058) mapped to IMP units
- [ ] No remaining SD-COVERAGE gaps unplanned
- [ ] No "Clarification Needed" gaps remain

### 5.3 Estimated Effort

| Phase | IMP Units | Estimated Effort |
|-------|-----------|------------------|
| Phase 1 | 4 units | 2 days |
| Phase 2 | 4 units | 3 days |
| Phase 3 | 4 units | 2 days |
| Phase 4 | 6 units | 3 days |
| Phase 5 | 5 units | 3 days |
| Phase 6 | 2 units | 1 day |
| **Total** | **25 units** | **14 days** |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.3 | 2026-01-25 | Platform Team | V1.4 Tech Spec implementation plan (25 IMP units for 155 TSD requirements) |
