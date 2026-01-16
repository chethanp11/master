# Semantic Interpretation - Implementation Prompts

> **Version**: V2.0  
> **Status**: Gap Completion  
> **Last Updated**: 2026-01-16  
> **Source**: [SD-COVERAGE.md](../05_systemdesign/SD-COVERAGE.md), [imp_plan.md](imp_plan.md)

---

## Overview

This document contains copy-paste prompts for implementing the **remaining gaps** in the semantic interpretation feature. Already-implemented items (NextAction enum, skip flag, ASK_USER handling) are excluded.

---

## GAP-001: Complete SemanticEnvelope Fields

### Prompt 1.1: Add Missing Fields

```
Read core/contracts/semantic_schema.py and the ORC-SEM-010 requirement from docs/03_techspecs/ORC-orchestration.md.

Add these missing fields to SemanticEnvelope:
- entities: list[Entity] with max_length=20
- constraints: dict[str, Any] 
- ambiguities: list[str] with max_length=20
- parameters: dict[str, Any]
- interpretation_method: str | None

Add Entity model if not present:
- name: str
- type: str  
- value: Any
- confidence: float (0.0-1.0)

Add field validators for max lengths. Update __init__.py exports.
```

---

## GAP-002: Complete Engine Integration

### Prompt 2.1: Wire Semantic Phase

```
Read core/orchestrator/engine.py and identify where the semantic interpretation phase should run.

Ensure:
1. Semantic phase runs AFTER run initialization but BEFORE step execution
2. SemanticEnvelope is stored in RunRecord
3. NextAction.ABORT triggers proper error handling
4. NextAction.ASK_USER sets run status to PAUSED_WAITING_FOR_USER
5. skip_semantic_interpretation: true bypasses the phase

Reference ORC-SEM-001 from docs/03_techspecs/ORC-orchestration.md.
```

---

## GAP-003: Create Normalization Module

### Prompt 3.1: Create normalization.py

```
Create core/orchestrator/normalization.py implementing:

1. normalize_whitespace(text: str) -> str
   - Collapse multiple spaces/tabs to single space
   - Strip leading/trailing whitespace
   - Normalize line endings
   Reference: ORC-SEM-030

2. deduplicate_entities(entities: list[Entity]) -> list[Entity]
   - Remove duplicates by (name, type) tuple
   - Keep highest confidence instance
   Reference: ORC-SEM-031

3. merge_constraints(constraints: list[dict]) -> dict
   - Merge overlapping constraints
   - Later values override earlier
   Reference: ORC-SEM-032

4. apply_stable_ordering(envelope: SemanticEnvelope) -> SemanticEnvelope
   - Sort entities by name
   - Sort ambiguities alphabetically
   Reference: ORC-SEM-033

5. coerce_types(value: Any, target_type: type) -> Any
   - Coerce value to target type
   - Raise TypeError on failure
   Reference: ORC-SEM-034

6. apply_core_normalization(envelope: SemanticEnvelope) -> SemanticEnvelope
   - Apply all normalizations in order
   - Return normalized copy

Add to core/orchestrator/__init__.py exports.
```

---

## GAP-004: Add Semantic Trace Events

### Prompt 4.1: Add Event Types

```
Read core/memory/tracing.py and add semantic trace event types:

In TraceEventType enum add:
- SEMANTIC_INTERPRETATION_STARTED (ORC-SEM-040)
- SEMANTIC_INTERPRETATION_COMPLETED (ORC-SEM-041)
- SEMANTIC_VALIDATION_COMPLETED (ORC-SEM-042)
- SEMANTIC_STOP_ISSUED (ORC-SEM-043)

Add helper functions:
- emit_semantic_started(run_id, user_input)
- emit_semantic_completed(run_id, envelope, duration_ms)
- emit_semantic_validation(run_id, is_valid, errors)
- emit_semantic_stop(run_id, next_action, reason)
```

---

## GAP-005: Add Confidence Gate Hook

### Prompt 5.1: Create Confidence Gate

```
Read core/governance/hooks.py and add semantic confidence gating:

Add function:
def check_semantic_confidence(
    envelope: SemanticEnvelope,
    threshold: float = 0.7
) -> tuple[bool, str | None]:
    '''
    Check if semantic interpretation meets confidence threshold.
    Returns (passed, reason) tuple.
    '''
    
Logic:
1. If envelope.confidence < threshold, return (False, "Low confidence: {confidence}")
2. If any entity has confidence < 0.5, return (False, "Low entity confidence")
3. Otherwise return (True, None)

Read threshold from configs/app.yaml semantic_confidence_threshold if present.
```

---

## GAP-006: Create hello_world Adapter

### Prompt 6.1: Create Product Adapter

```
Create products/hello_world/semantic.py with:

class HelloWorldSemanticAdapter:
    '''Semantic interpreter for hello_world product.'''
    
    def interpret(self, user_input: str, context: dict) -> SemanticEnvelope:
        '''
        Interpret user input into semantic envelope.
        
        For hello_world, extract:
        - Greeting intent (hello, hi, hey)
        - Name entity if present
        - Language constraint if detected
        '''
        
    def validate(self, envelope: SemanticEnvelope) -> tuple[bool, list[str]]:
        '''Validate envelope for hello_world domain.'''

Register in products/hello_world/__init__.py.
```

---

## GAP-007: Add Unit Tests

### Prompt 7.1: Test SemanticEnvelope

```
Create tests/unit/core/contracts/test_semantic_schema.py:

Test cases:
- test_semantic_envelope_valid_construction
- test_semantic_envelope_max_entities_enforced
- test_semantic_envelope_max_ambiguities_enforced
- test_entity_confidence_bounds
- test_next_action_enum_values
- test_envelope_serialization_roundtrip
```

### Prompt 7.2: Test Normalization

```
Create tests/unit/core/orchestrator/test_normalization.py:

Test cases:
- test_normalize_whitespace_collapses_spaces
- test_normalize_whitespace_handles_tabs
- test_deduplicate_entities_keeps_highest_confidence
- test_merge_constraints_later_wins
- test_stable_ordering_deterministic
- test_coerce_types_success_cases
- test_coerce_types_failure_raises
- test_apply_core_normalization_full_pipeline
```

### Prompt 7.3: Test Engine Integration

```
Create tests/unit/core/orchestrator/test_semantic_phase.py:

Test cases:
- test_semantic_phase_runs_before_steps
- test_semantic_phase_skipped_when_configured
- test_abort_action_stops_run
- test_ask_user_pauses_run
- test_envelope_stored_in_run_record
- test_semantic_errors_handled_gracefully
```

---

## GAP-008: Add Architecture Tests

### Prompt 8.1: Create Isolation Tests

```
Create tests/architecture/test_semantic_isolation.py:

Test architectural invariants:
- test_semantic_schema_no_external_deps
- test_normalization_no_io_operations
- test_semantic_phase_before_step_execution
- test_adapters_implement_required_interface
- test_trace_events_emitted_for_semantic_operations
```

---

## Validation Checklist

After completing all gaps, verify:

- [ ] `pytest tests/unit/core/contracts/test_semantic_schema.py -v` passes
- [ ] `pytest tests/unit/core/orchestrator/test_normalization.py -v` passes
- [ ] `pytest tests/unit/core/orchestrator/test_semantic_phase.py -v` passes
- [ ] `pytest tests/architecture/test_semantic_isolation.py -v` passes
- [ ] hello_world product runs with semantic interpretation enabled
- [ ] SD-COVERAGE.md updated to show all ORC-SEM items as implemented
