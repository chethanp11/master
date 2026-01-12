# ADE Implementation Plan

> **Document**: Implementation Plan  
> **Status**: Active  
> **Last Updated**: 2026-01-12

---

## Overview

This plan covers implementation of **ADE Semantic Interpretation** capabilities—6 new modules that transform free-text analyst questions into structured semantic envelopes for flow routing.

### Deliverables

| # | File | Description | Priority |
|---|------|-------------|----------|
| 1 | `products/ade/intents.py` | Intent taxonomy enum and field requirements | P0 |
| 2 | `products/ade/semantic_adapter.py` | ADESemanticAdapter class | P0 |
| 3 | `products/ade/semantic_validation.py` | Validation rules and ValidationResult | P0 |
| 4 | `products/ade/clarifying_questions.py` | Deterministic question templates | P0 |
| 5 | `products/ade/intent_router.py` | Intent-to-flow routing | P0 |
| 6 | `products/ade/observability.py` | ADE trace metadata extension | P0 |

---

## Phase 1: Foundation (Files 1-2)

### 1.1 Intent Taxonomy (`intents.py`)

**Objective**: Define ADE intent types and their field requirements.

**Components**:
- `ADEIntentType` enum with 5 values
- `IntentRequirements` dataclass (required_fields, optional_fields)
- `INTENT_REQUIREMENTS` mapping

**Requirements Covered**: SEM-INTENT-001 through SEM-INTENT-008

**Dependencies**: None (foundation module)

**Test Scenarios**:
- [ ] All 5 intent types are defined
- [ ] Each intent has correct required/optional fields
- [ ] Enum values match expected strings

---

### 1.2 Semantic Adapter (`semantic_adapter.py`)

**Objective**: Interpret free-text input into SemanticEnvelope.

**Components**:
- `ADESemanticAdapter` class
- `interpret(user_input, context)` method
- Keyword/pattern matching for intent classification
- Confidence scoring logic

**Requirements Covered**: SEM-ADAPTER-001 through SEM-ADAPTER-005

**Dependencies**: 
- `intents.py` (ADEIntentType)
- `core/contracts/semantic_envelope_schema.py` (SemanticEnvelope)

**Test Scenarios**:
- [ ] "Show me sales trends" → TREND_ANALYSIS
- [ ] "What anomalies exist?" → ANOMALY_REVIEW
- [ ] "Compare Q1 vs Q2" → COMPARE_PERIODS
- [ ] "Describe this dataset" → DESCRIBE_DATA
- [ ] Ambiguous input → OPEN_ENDED_ANALYSIS with lower confidence

---

## Phase 2: Validation & Questions (Files 3-4)

### 2.1 Semantic Validation (`semantic_validation.py`)

**Objective**: Validate SemanticEnvelope against intent requirements.

**Components**:
- `ValidationResult` Pydantic model
- `validate_semantic_envelope(envelope, intent_type)` function
- Outcome logic: PROCEED / ASK_USER / ABORT
- Confidence adjustment calculation

**Requirements Covered**: SEM-VALIDATE-001 through SEM-VALIDATE-007

**Dependencies**:
- `intents.py` (ADEIntentType, INTENT_REQUIREMENTS)
- `semantic_adapter.py` (SemanticEnvelope)

**Test Scenarios**:
- [ ] Complete envelope → PROCEED, is_valid=True
- [ ] Missing required field → ASK_USER with question
- [ ] Critical failure → ABORT
- [ ] Missing optional field → confidence_adjustment applied

---

### 2.2 Clarifying Questions (`clarifying_questions.py`)

**Objective**: Provide deterministic question templates for missing fields.

**Components**:
- `CLARIFYING_TEMPLATES` dictionary
- `get_clarifying_question(missing_field, intent_type)` function
- Templates for: metrics, time_scope, anomaly_threshold, dataset

**Requirements Covered**: SEM-CLARIFY-001 through SEM-CLARIFY-006

**Dependencies**: None (standalone templates)

**Test Scenarios**:
- [ ] Missing "metrics" → metric focus question
- [ ] Missing "time_scope" → time range question
- [ ] Missing "anomaly_threshold" → anomaly preference question
- [ ] Unknown field → generic fallback question

---

## Phase 3: Routing & Observability (Files 5-6)

### 3.1 Intent Router (`intent_router.py`)

**Objective**: Route validated SemanticEnvelope to appropriate flow.

**Components**:
- `RouteResult` Pydantic model
- `route_intent(envelope)` function
- Routing rules mapping intent → flow

**Routing Table**:

| Intent Type | Flow | Parameters |
|-------------|------|------------|
| DESCRIBE_DATA | visualization | dataset, intent_summary |
| COMPARE_PERIODS | ade_v1 | prompt, dataset, time_scope |
| TREND_ANALYSIS | ade_v1 | prompt, dataset, metrics |
| ANOMALY_REVIEW | ade_v1 | prompt, dataset, metrics |
| OPEN_ENDED_ANALYSIS | visualization | dataset |

**Requirements Covered**: SEM-ROUTER-001 through SEM-ROUTER-005

**Dependencies**:
- `intents.py` (ADEIntentType)
- `semantic_adapter.py` (SemanticEnvelope)

**Test Scenarios**:
- [ ] Each intent type routes to correct flow
- [ ] Parameters are correctly mapped
- [ ] Dataset always included in initial_parameters

---

### 3.2 Semantic Observability (`observability.py`)

**Objective**: Emit ADE-specific trace metadata for semantic interpretation.

**Components**:
- `emit_semantic_trace(envelope, validation_result)` function
- ADE trace fields: ade_intent, ade_confidence, ade_missing_fields, ade_clarifying_question
- Integration with `core.governance.hooks`

**Requirements Covered**: SEM-OBS-001 through SEM-OBS-007

**Dependencies**:
- `core/governance/hooks.py`
- `semantic_adapter.py` (SemanticEnvelope)
- `semantic_validation.py` (ValidationResult)

**Test Scenarios**:
- [ ] Trace includes ade_intent on every event
- [ ] Trace includes ade_confidence
- [ ] ade_missing_fields present only when applicable
- [ ] ade_clarifying_question present only when generated

---

## Phase 4: Integration

### 4.1 Flow Integration

**Objective**: Wire semantic interpretation into ADE flows.

**Changes Required**:
- Update `ade_v1` flow to use ADESemanticAdapter at entry
- Update `visualization` flow for dataset-first semantic handling
- Add validation step before flow execution
- Add clarification HITL step when ASK_USER

**Files Modified**:
- `products/ade/flows/ade_v1.yaml`
- `products/ade/flows/visualization.yaml`

---

### 4.2 Manifest Update

**Objective**: Register new modules in ADE product manifest.

**Changes Required**:
- Add semantic_adapter to module exports
- Add intents to module exports
- Update flow entry points

**Files Modified**:
- `products/ade/manifest.py`

---

## Dependency Graph

```
                    ┌─────────────┐
                    │  intents.py │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
┌──────────────────┐ ┌───────────────┐ ┌─────────────────┐
│ semantic_adapter │ │ semantic_     │ │ intent_router   │
│       .py        │ │ validation.py │ │      .py        │
└────────┬─────────┘ └───────┬───────┘ └─────────────────┘
         │                   │
         │                   │
         │    ┌──────────────┴──────────────┐
         │    │                             │
         ▼    ▼                             ▼
┌────────────────────┐           ┌─────────────────────┐
│ clarifying_        │           │ observability.py    │
│ questions.py       │           │                     │
└────────────────────┘           └─────────────────────┘
```

---

## Success Criteria

| Phase | Criteria | Validation |
|-------|----------|------------|
| 1 | Intent taxonomy complete | Unit tests pass |
| 1 | Semantic adapter classifies correctly | Integration tests pass |
| 2 | Validation returns correct outcomes | Unit tests pass |
| 2 | Clarifying questions are deterministic | No LLM calls verified |
| 3 | Router maps all intents correctly | Integration tests pass |
| 3 | Observability emits ADE fields | Trace inspection |
| 4 | Flows use semantic interpretation | E2E tests pass |

---

## Cross-References

- **BRD**: [BRD-agents.md](../01_brd/BRD-agents.md#8-semantic-interpretation-requirements)
- **Techspec**: [AGENT-agents.md](../02_techspec/AGENT-agents.md#8-adesemantic-adapter-sem-adapter)
