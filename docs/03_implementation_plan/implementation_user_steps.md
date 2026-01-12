# Semantic Interpretation Implementation Steps

> **Feature**: Semantic Interpretation Phase  
> **Format**: Copy-paste prompts for AI-assisted implementation  
> **Last Updated**: 2026-01-12

---

## How to Use This Document

Each step below contains a **prompt** you can copy and paste to implement that part of the feature. Execute steps in order. Each step builds on the previous.

**Prerequisites**:
- Read `implementation_plan.md` for context
- Have the codebase open in VS Code
- Ensure tests pass before starting: `pytest tests/ -v`

---

## Step 1: Create Semantic Schema Contracts

### Prompt 1.1: Create SemanticEnvelope and related models

```
Create the file `core/contracts/semantic_schema.py` with the following Pydantic models:

1. `Entity` model with fields:
   - `type`: str (entity type, e.g., "metric", "date", "filter")
   - `value`: str (extracted value)
   - `confidence`: float (0.0-1.0)
   - `start_pos`: int | None (position in input, optional)
   - `end_pos`: int | None (position in input, optional)

2. `NextAction` enum (str, Enum) with values:
   - CONTINUE = "CONTINUE"
   - ASK_USER = "ASK_USER"
   - ABORT = "ABORT"
   - NEEDS_APPROVAL = "NEEDS_APPROVAL"

3. `SemanticEnvelope` model with fields:
   - `raw_input`: str (original user input)
   - `normalized_input`: str (cleaned/standardized input)
   - `product_id`: str (resolved product identifier)
   - `intent_type`: str (classified intent category)
   - `entities`: list[Entity] (max_items=20)
   - `constraints`: dict[str, Any] (extracted constraints/filters)
   - `confidence`: float (ge=0.0, le=1.0)
   - `ambiguities`: list[str] (max_items=20, unresolved ambiguities)
   - `proposed_next_action`: NextAction (default CONTINUE)

4. `ValidationResult` model with fields:
   - `is_valid`: bool
   - `missing_fields`: list[str] (max_items=20)
   - `violations`: list[str] (max_items=20)
   - `revised_confidence`: float (ge=0.0, le=1.0)
   - `clarifying_question`: str | None (when user input needed)

5. `SemanticContext` model with fields:
   - `raw_input`: str
   - `payload`: dict[str, Any]
   - `product_config`: dict[str, Any]

All models should use `model_config = ConfigDict(extra="forbid")` for strict validation.
Add docstrings explaining each model's purpose.
Export all models in __all__.

Reference requirements: ORC-SEM-010...019, ORC-SEM-020...022, INT-SEM-VAL-001...006
```

### Prompt 1.2: Create unit tests for semantic schema

```
Create `tests/unit/core/contracts/test_semantic_schema.py` with tests for:

1. SemanticEnvelope validation:
   - test_semantic_envelope_valid_minimal
   - test_semantic_envelope_valid_full
   - test_semantic_envelope_confidence_bounds (reject <0 or >1)
   - test_semantic_envelope_entities_max_items (reject >20)
   - test_semantic_envelope_extra_fields_rejected

2. NextAction enum:
   - test_next_action_values
   - test_next_action_serialization

3. ValidationResult:
   - test_validation_result_valid
   - test_validation_result_with_question
   - test_validation_result_confidence_bounds

4. Entity model:
   - test_entity_valid
   - test_entity_confidence_bounds

Use pytest fixtures for common test data.
Reference requirements: ORC-SEM-010...019
```

---

## Step 2: Create Core Normalization Rules

### Prompt 2.1: Implement normalization functions

```
Create `core/orchestrator/normalization.py` with domain-agnostic normalization functions:

1. `normalize_whitespace(text: str) -> str`:
   - Strip leading/trailing whitespace
   - Collapse multiple spaces to single space
   - Normalize newlines

2. `deduplicate_entities(entities: list[Entity]) -> list[Entity]`:
   - Remove duplicates where type AND value match
   - Keep entity with highest confidence when deduping
   - Return sorted list by (type, value)

3. `merge_constraints(constraints: dict) -> dict`:
   - Merge overlapping constraint values deterministically
   - For lists: dedupe and sort
   - For conflicting scalars: keep first encountered
   - Return dict with keys sorted alphabetically

4. `apply_stable_ordering(envelope: SemanticEnvelope) -> SemanticEnvelope`:
   - Sort entities by (type, value)
   - Sort ambiguities alphabetically
   - Sort constraint keys alphabetically
   - Return new envelope with stable ordering

5. `coerce_types(value: Any, target_type: str) -> Any`:
   - Support: "int", "float", "date", "bool"
   - Return original value if coercion fails
   - Used when schema declares expected types

6. `apply_core_normalization(envelope: SemanticEnvelope) -> SemanticEnvelope`:
   - Orchestrates all above functions
   - Returns a fully normalized envelope

IMPORTANT: These functions must NOT contain domain-specific rules.
No rules like "trend requires time axis" - that belongs in product adapters.

Reference requirements: ORC-SEM-030...035
```

### Prompt 2.2: Create unit tests for normalization

```
Create `tests/unit/core/orchestrator/test_normalization.py` with tests:

1. Whitespace normalization:
   - test_normalize_whitespace_trim
   - test_normalize_whitespace_collapse
   - test_normalize_whitespace_newlines

2. Entity deduplication:
   - test_deduplicate_entities_removes_dupes
   - test_deduplicate_entities_keeps_highest_confidence
   - test_deduplicate_entities_stable_sort

3. Constraint merging:
   - test_merge_constraints_dedupes_lists
   - test_merge_constraints_sorts_keys
   - test_merge_constraints_conflict_resolution

4. Stable ordering:
   - test_apply_stable_ordering_entities
   - test_apply_stable_ordering_ambiguities
   - test_apply_stable_ordering_idempotent

5. Type coercion:
   - test_coerce_types_string_to_int
   - test_coerce_types_string_to_date
   - test_coerce_types_invalid_returns_original

Reference requirements: ORC-SEM-030...035
```

---

## Step 3: Create Product Semantic Adapter Interface

### Prompt 3.1: Define the adapter abstract base class

```
Add to `core/contracts/semantic_schema.py` (or create `core/contracts/semantic_adapter.py`):

1. `ProductSemanticAdapter` abstract base class:
   ```python
   from abc import ABC, abstractmethod
   
   class ProductSemanticAdapter(ABC):
       """
       Product-provided semantic interpretation adapter.
       
       Products implement this to customize how user input is interpreted
       and validated for their domain.
       
       IMPORTANT: Implementations must NOT:
       - Import from core/orchestrator/*
       - Call tools or agents directly
       - Access external services
       """
       
       @abstractmethod
       def interpret(self, context: SemanticContext) -> SemanticEnvelope:
           """
           Interpret raw user input into a structured semantic envelope.
           
           Args:
               context: Contains raw_input, payload, product_config
               
           Returns:
               SemanticEnvelope with intent, entities, constraints, confidence
           """
           pass
       
       @abstractmethod  
       def validate(self, envelope: SemanticEnvelope, context: SemanticContext) -> ValidationResult:
           """
           Validate the semantic envelope against domain-specific rules.
           
           Args:
               envelope: Output from interpret()
               context: Original context for reference
               
           Returns:
               ValidationResult with is_valid, violations, revised_confidence
           """
           pass
   ```

2. `DefaultSemanticAdapter` class (non-abstract):
   - `interpret()`: Returns passthrough envelope with confidence=1.0
   - `validate()`: Returns is_valid=True, empty violations

Reference requirements: PROD-SEM-001...005
```

### Prompt 3.2: Create hello_world reference adapter

```
Create `products/hello_world/semantic.py` as a reference implementation:

```python
"""
Semantic adapter for hello_world product.

This is a minimal reference implementation showing how products
can customize semantic interpretation.
"""

from core.contracts.semantic_schema import (
    ProductSemanticAdapter,
    SemanticContext,
    SemanticEnvelope,
    ValidationResult,
    NextAction,
    Entity,
)


class HelloWorldSemanticAdapter(ProductSemanticAdapter):
    """
    Simple semantic adapter for the hello_world demo product.
    
    Recognizes:
    - Greetings (hello, hi, hey)
    - Names (after greeting)
    """
    
    GREETING_PATTERNS = ["hello", "hi", "hey", "greetings"]
    
    def interpret(self, context: SemanticContext) -> SemanticEnvelope:
        raw = context.raw_input.strip().lower()
        entities = []
        intent_type = "unknown"
        confidence = 0.5
        ambiguities = []
        
        # Check for greeting
        for pattern in self.GREETING_PATTERNS:
            if raw.startswith(pattern):
                intent_type = "greeting"
                confidence = 0.9
                
                # Extract name if present (e.g., "hello world")
                remainder = raw[len(pattern):].strip()
                if remainder:
                    entities.append(Entity(
                        type="name",
                        value=remainder,
                        confidence=0.8,
                    ))
                break
        
        if intent_type == "unknown":
            ambiguities.append("Could not determine intent from input")
            confidence = 0.3
        
        return SemanticEnvelope(
            raw_input=context.raw_input,
            normalized_input=raw,
            product_id="hello_world",
            intent_type=intent_type,
            entities=entities,
            constraints={},
            confidence=confidence,
            ambiguities=ambiguities,
            proposed_next_action=NextAction.CONTINUE if confidence > 0.5 else NextAction.ASK_USER,
        )
    
    def validate(self, envelope: SemanticEnvelope, context: SemanticContext) -> ValidationResult:
        violations = []
        revised_confidence = envelope.confidence
        
        # Simple validation: greeting intent should have high confidence
        if envelope.intent_type == "greeting" and envelope.confidence < 0.7:
            violations.append("Greeting confidence too low")
            revised_confidence = 0.6
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            missing_fields=[],
            violations=violations,
            revised_confidence=revised_confidence,
            clarifying_question="What would you like me to help you with?" if violations else None,
        )


# Export for discovery
SemanticAdapter = HelloWorldSemanticAdapter
```

Reference requirements: PROD-SEM-INT-001...006, PROD-SEM-VAL-001...007
```

---

## Step 4: Create Semantic Phase Executor

### Prompt 4.1: Implement SemanticPhase class

```
Create `core/orchestrator/semantic_phase.py`:

```python
"""
Semantic interpretation phase executor.

This module runs before step execution to interpret user intent,
validate the interpretation, and decide whether to proceed.
"""

from typing import Optional
from core.contracts.semantic_schema import (
    SemanticEnvelope,
    SemanticContext,
    ValidationResult,
    NextAction,
    ProductSemanticAdapter,
    DefaultSemanticAdapter,
)
from core.orchestrator.normalization import apply_core_normalization
from core.memory.tracing import Tracer


class SemanticPhaseResult:
    """Result of semantic phase execution."""
    
    def __init__(
        self,
        envelope: SemanticEnvelope,
        validation: ValidationResult,
        next_action: NextAction,
    ):
        self.envelope = envelope
        self.validation = validation
        self.next_action = next_action


class SemanticPhase:
    """
    Executes semantic interpretation before step execution.
    
    This phase:
    1. Calls product adapter to interpret input
    2. Applies core normalization rules
    3. Calls product adapter to validate
    4. Checks confidence thresholds
    5. Determines next action (CONTINUE/ASK_USER/ABORT)
    """
    
    def __init__(
        self,
        tracer: Tracer,
        get_adapter_fn,  # Callable[[str], ProductSemanticAdapter]
        get_threshold_fn,  # Callable[[str], float]
    ):
        self.tracer = tracer
        self.get_adapter = get_adapter_fn
        self.get_threshold = get_threshold_fn
        self.default_adapter = DefaultSemanticAdapter()
    
    async def execute(
        self,
        raw_input: str,
        payload: dict,
        product_id: str,
        skip_semantic: bool = False,
    ) -> SemanticPhaseResult:
        """
        Execute semantic interpretation phase.
        
        Args:
            raw_input: Original user input text
            payload: Full request payload
            product_id: Product identifier
            skip_semantic: If True, return passthrough result
            
        Returns:
            SemanticPhaseResult with envelope, validation, next_action
        """
        # Skip check
        if skip_semantic:
            return self._create_passthrough_result(raw_input, payload, product_id)
        
        # Emit start event
        self.tracer.emit("semantic_interpretation_started", {
            "product_id": product_id,
            "raw_input_length": len(raw_input),
        })
        
        try:
            # Build context
            context = SemanticContext(
                raw_input=raw_input,
                payload=payload,
                product_config={},  # TODO: Get from product catalog
            )
            
            # Get adapter (or default)
            adapter = self._get_adapter_safe(product_id)
            
            # Interpret
            envelope = adapter.interpret(context)
            
            # Apply core normalization
            envelope = apply_core_normalization(envelope)
            
            # Validate
            validation = adapter.validate(envelope, context)
            
            # Confidence check
            threshold = self.get_threshold(product_id)
            next_action = self._determine_next_action(
                envelope, validation, threshold
            )
            
            # Update envelope with final next_action
            envelope.proposed_next_action = next_action
            
            # Emit completion event
            self.tracer.emit("semantic_interpretation_completed", {
                "confidence": envelope.confidence,
                "ambiguity_count": len(envelope.ambiguities),
                "entity_count": len(envelope.entities),
                "next_action": next_action.value,
            })
            
            # Emit validation event
            self.tracer.emit("semantic_validation_completed", {
                "is_valid": validation.is_valid,
                "missing_fields": validation.missing_fields,
                "violation_count": len(validation.violations),
                "revised_confidence": validation.revised_confidence,
            })
            
            # Emit stop event if not continuing
            if next_action != NextAction.CONTINUE:
                self.tracer.emit("semantic_stop_issued", {
                    "next_action": next_action.value,
                    "question": validation.clarifying_question,
                    "violations": validation.violations,
                })
            
            return SemanticPhaseResult(
                envelope=envelope,
                validation=validation,
                next_action=next_action,
            )
            
        except Exception as e:
            self.tracer.emit("semantic_interpretation_failed", {
                "error": str(e),
            })
            raise
    
    def _get_adapter_safe(self, product_id: str) -> ProductSemanticAdapter:
        """Get adapter with fallback to default."""
        try:
            adapter = self.get_adapter(product_id)
            return adapter if adapter else self.default_adapter
        except Exception:
            return self.default_adapter
    
    def _determine_next_action(
        self,
        envelope: SemanticEnvelope,
        validation: ValidationResult,
        threshold: float,
    ) -> NextAction:
        """Determine next action based on confidence and validation."""
        # If validation failed, use its guidance
        if not validation.is_valid:
            if validation.clarifying_question:
                return NextAction.ASK_USER
            return NextAction.ABORT
        
        # Check confidence threshold
        effective_confidence = min(
            envelope.confidence,
            validation.revised_confidence,
        )
        if effective_confidence < threshold:
            return NextAction.ASK_USER
        
        # Use envelope's proposed action
        return envelope.proposed_next_action
    
    def _create_passthrough_result(
        self,
        raw_input: str,
        payload: dict,
        product_id: str,
    ) -> SemanticPhaseResult:
        """Create passthrough result when semantic phase is skipped."""
        envelope = SemanticEnvelope(
            raw_input=raw_input,
            normalized_input=raw_input,
            product_id=product_id,
            intent_type="passthrough",
            entities=[],
            constraints={},
            confidence=1.0,
            ambiguities=[],
            proposed_next_action=NextAction.CONTINUE,
        )
        validation = ValidationResult(
            is_valid=True,
            missing_fields=[],
            violations=[],
            revised_confidence=1.0,
            clarifying_question=None,
        )
        return SemanticPhaseResult(
            envelope=envelope,
            validation=validation,
            next_action=NextAction.CONTINUE,
        )
```

Reference requirements: ORC-SEM-001...004, ORC-SEM-040...043
```

### Prompt 4.2: Create unit tests for semantic phase

```
Create `tests/unit/core/orchestrator/test_semantic_phase.py` with tests:

1. Basic execution:
   - test_semantic_phase_executes_interpret
   - test_semantic_phase_executes_validate
   - test_semantic_phase_applies_normalization

2. Skip behavior:
   - test_semantic_phase_skip_returns_passthrough
   - test_semantic_phase_skip_confidence_is_one

3. Adapter resolution:
   - test_semantic_phase_uses_product_adapter
   - test_semantic_phase_falls_back_to_default

4. Next action determination:
   - test_next_action_continue_when_valid_high_confidence
   - test_next_action_ask_user_when_low_confidence
   - test_next_action_ask_user_when_validation_has_question
   - test_next_action_abort_when_validation_fails_no_question

5. Trace events:
   - test_emits_semantic_interpretation_started
   - test_emits_semantic_interpretation_completed
   - test_emits_semantic_validation_completed
   - test_emits_semantic_stop_issued_on_ask_user
   - test_emits_semantic_stop_issued_on_abort

Use pytest fixtures and mocks for tracer and adapters.
Reference requirements: ORC-SEM-001...004, ORC-SEM-040...043
```

---

## Step 5: Integrate with Orchestrator Engine

### Prompt 5.1: Modify engine.py to call semantic phase

```
Modify `core/orchestrator/engine.py` to integrate the semantic phase:

1. Add import for SemanticPhase and related types

2. Add `semantic_phase` to Engine.__init__():
   ```python
   self.semantic_phase = SemanticPhase(
       tracer=self.tracer,
       get_adapter_fn=self._get_semantic_adapter,
       get_threshold_fn=self._get_confidence_threshold,
   )
   ```

3. Add helper methods:
   ```python
   def _get_semantic_adapter(self, product_id: str):
       # Resolve from product catalog
       pass
   
   def _get_confidence_threshold(self, product_id: str) -> float:
       # Get from settings, with product override
       pass
   ```

4. In run_flow() method, AFTER run initialization but BEFORE step execution:
   ```python
   # Semantic interpretation phase
   semantic_result = await self.semantic_phase.execute(
       raw_input=payload.get("text", str(payload)),
       payload=payload,
       product_id=product_id,
       skip_semantic=flow.config.get("skip_semantic_interpretation", False),
   )
   
   # Store envelope in run context
   run_context.semantic_envelope = semantic_result.envelope
   
   # Handle next action
   if semantic_result.next_action == NextAction.ASK_USER:
       return await self._pause_for_semantic_clarification(
           run_context,
           semantic_result,
       )
   elif semantic_result.next_action == NextAction.ABORT:
       return await self._fail_run_semantic(
           run_context,
           semantic_result,
       )
   elif semantic_result.next_action == NextAction.NEEDS_APPROVAL:
       return await self._request_semantic_approval(
           run_context,
           semantic_result,
       )
   
   # CONTINUE: proceed to step execution
   ```

5. Add helper methods for pause/fail:
   ```python
   async def _pause_for_semantic_clarification(self, run_context, semantic_result):
       # Transition to PAUSED_WAITING_FOR_USER
       # Return structured clarification response
       pass
   
   async def _fail_run_semantic(self, run_context, semantic_result):
       # Transition to FAILED with code "semantic_abort"
       # Return structured error response
       pass
   ```

Reference requirements: ORC-SEM-001, ORC-SEM-STOP-001...007
```

### Prompt 5.2: Update run_schema.py for semantic fields

```
Modify `core/contracts/run_schema.py`:

1. Add import for SemanticEnvelope

2. Add to RunRecord:
   ```python
   semantic_envelope: Optional[SemanticEnvelope] = None
   ```

3. Add new error codes to relevant enum:
   ```python
   SEMANTIC_INTERPRETATION_FAILED = "semantic_interpretation_failed"
   SEMANTIC_ABORT = "semantic_abort"
   ```

4. Ensure SemanticEnvelope is serializable in RunRecord

Reference requirements: ORC-SEM-003, ORC-SEM-004, ORC-SEM-STOP-004
```

---

## Step 6: Add Confidence Threshold Configuration

### Prompt 6.1: Update configs/app.yaml

```
Add to `configs/app.yaml`:

```yaml
# Semantic interpretation settings
semantic:
  # Default confidence threshold (0.0-1.0)
  # Interpretations below this threshold trigger ASK_USER
  default_confidence_threshold: 0.7
  
  # Whether semantic phase is required (can be overridden per flow)
  require_semantic_phase: true
```

Reference requirements: INT-SEM-CONF-003
```

### Prompt 6.2: Update configs/products.yaml

```
Add to `configs/products.yaml`:

```yaml
# Per-product semantic settings
by_product:
  hello_world:
    # More lenient threshold for demo product
    semantic_confidence_threshold: 0.5
  
  ade:
    # Stricter threshold for production product
    semantic_confidence_threshold: 0.8
```

Reference requirements: INT-SEM-CONF-004
```

### Prompt 6.3: Update config loader to read semantic settings

```
Modify `core/config/loader.py` or relevant settings module:

1. Add SemanticSettings model:
   ```python
   class SemanticSettings(BaseModel):
       default_confidence_threshold: float = 0.7
       require_semantic_phase: bool = True
   ```

2. Add to Settings:
   ```python
   semantic: SemanticSettings = SemanticSettings()
   ```

3. Add method to get product-specific threshold:
   ```python
   def get_semantic_threshold(self, product_id: str) -> float:
       product_override = self.products.by_product.get(product_id, {})
       return product_override.get(
           "semantic_confidence_threshold",
           self.semantic.default_confidence_threshold,
       )
   ```

Reference requirements: INT-SEM-CONF-002...004
```

---

## Step 7: Add Governance Hook for Confidence

### Prompt 7.1: Add confidence check hook

```
Add to `core/governance/hooks.py`:

```python
from core.contracts.semantic_schema import SemanticEnvelope, NextAction


def check_semantic_confidence(
    envelope: SemanticEnvelope,
    threshold: float,
) -> tuple[bool, str, NextAction | None]:
    """
    Check if semantic interpretation confidence meets threshold.
    
    Args:
        envelope: Semantic interpretation result
        threshold: Minimum required confidence
        
    Returns:
        Tuple of (allowed, reason, suggested_action)
    """
    if envelope.confidence < threshold:
        return (
            False,
            f"Semantic confidence {envelope.confidence:.2f} below threshold {threshold:.2f}",
            NextAction.ASK_USER,
        )
    return (True, "", None)
```

Reference requirements: INT-SEM-CONF-001
```

---

## Step 8: Update Tracing for Semantic Events

### Prompt 8.1: Add semantic trace event types

```
Modify `core/memory/tracing.py`:

1. Add to TraceEventKind enum (or equivalent):
   ```python
   SEMANTIC_INTERPRETATION_STARTED = "semantic_interpretation_started"
   SEMANTIC_INTERPRETATION_COMPLETED = "semantic_interpretation_completed"
   SEMANTIC_VALIDATION_COMPLETED = "semantic_validation_completed"
   SEMANTIC_STOP_ISSUED = "semantic_stop_issued"
   SEMANTIC_INTERPRETATION_FAILED = "semantic_interpretation_failed"
   ```

2. Ensure Tracer.emit() can handle these event types with proper payload schemas

Reference requirements: ORC-SEM-040...043
```

---

## Step 9: Create Architecture Tests

### Prompt 9.1: Implement mandatory architecture tests

```
Create `tests/architecture/test_semantic_isolation.py`:

```python
"""
Architecture tests for semantic interpretation.

These tests enforce invariants that prevent regression of key behaviors.
They verify:
1. Semantic phase is mandatory
2. Stop actions block execution
3. Product adapters are isolated from core internals

Reference requirements: ACC-SEM-001...005
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch


class TestSemanticPhaseMandatory:
    """Tests that semantic phase always runs before step execution."""
    
    @pytest.mark.asyncio
    async def test_semantic_phase_is_mandatory(self):
        """
        Verifies: ORC-SEM-001, ORC-SEM-003
        
        The orchestrator MUST call semantic phase before any step execution.
        """
        # Setup: Create mock tracer that records events
        events = []
        mock_tracer = Mock()
        mock_tracer.emit = lambda kind, payload: events.append(kind)
        
        # Setup: Create mock semantic phase that returns CONTINUE
        from core.contracts.semantic_schema import (
            SemanticEnvelope, ValidationResult, NextAction
        )
        from core.orchestrator.semantic_phase import SemanticPhase, SemanticPhaseResult
        
        mock_result = SemanticPhaseResult(
            envelope=SemanticEnvelope(
                raw_input="test",
                normalized_input="test",
                product_id="test",
                intent_type="test",
                entities=[],
                constraints={},
                confidence=0.9,
                ambiguities=[],
                proposed_next_action=NextAction.CONTINUE,
            ),
            validation=ValidationResult(
                is_valid=True,
                missing_fields=[],
                violations=[],
                revised_confidence=0.9,
            ),
            next_action=NextAction.CONTINUE,
        )
        
        # TODO: Run a flow through the engine
        # Assert: semantic_interpretation_started appears BEFORE step_started
        
        # Check event order
        semantic_idx = None
        step_idx = None
        for i, event in enumerate(events):
            if event == "semantic_interpretation_started":
                semantic_idx = i
            if event == "step_started" and semantic_idx is None:
                pytest.fail("step_started emitted before semantic_interpretation_started")


class TestStopBlocksExecution:
    """Tests that ASK_USER and ABORT prevent step execution."""
    
    @pytest.mark.asyncio
    async def test_ask_user_blocks_execution(self):
        """
        Verifies: ORC-SEM-STOP-001, ORC-SEM-STOP-002
        
        NextAction=ASK_USER MUST prevent step execution.
        """
        events = []
        
        # TODO: Configure semantic phase to return ASK_USER
        # TODO: Run flow
        # Assert: NO step_started events
        # Assert: run status is PAUSED_WAITING_FOR_USER
        
        assert "step_started" not in events
    
    @pytest.mark.asyncio
    async def test_abort_blocks_execution(self):
        """
        Verifies: ORC-SEM-STOP-004, ORC-SEM-STOP-005
        
        NextAction=ABORT MUST fail the run without step execution.
        """
        events = []
        
        # TODO: Configure semantic phase to return ABORT
        # TODO: Run flow
        # Assert: NO step_started events
        # Assert: run status is FAILED
        # Assert: error code is semantic_abort
        
        assert "step_started" not in events


class TestProductAdapterIsolation:
    """Tests that product adapters don't import core internals and vice versa."""
    
    def test_core_does_not_import_products(self):
        """
        Verifies: PROD-SEM-INT-006, PROD-SEM-VAL-006
        
        Core orchestrator MUST NOT import product domain code.
        """
        core_orchestrator_path = Path("core/orchestrator")
        
        for py_file in core_orchestrator_path.glob("*.py"):
            content = py_file.read_text()
            
            # Check for product imports
            assert "from products" not in content, \
                f"{py_file} imports from products"
            assert "import products" not in content, \
                f"{py_file} imports products"
    
    def test_products_do_not_import_orchestrator_internals(self):
        """
        Verifies: PROD-SEM-INT-005, PROD-SEM-VAL-005
        
        Product adapters MUST NOT import core orchestrator internals.
        """
        products_path = Path("products")
        
        for semantic_file in products_path.glob("*/semantic.py"):
            content = semantic_file.read_text()
            
            # Check for orchestrator internal imports
            assert "from core.orchestrator" not in content, \
                f"{semantic_file} imports core.orchestrator"
            assert "import core.orchestrator" not in content, \
                f"{semantic_file} imports core.orchestrator"
            
            # Allowed imports from core
            # - core.contracts.semantic_schema (the interface)
            # That's it!
    
    def test_adapter_interface_used_via_router(self):
        """
        Verifies: PROD-SEM-005
        
        Adapters MUST be called via ProductRouter, not directly imported.
        """
        # TODO: Verify that semantic_phase.py only calls get_adapter()
        # and doesn't directly import any product adapter classes
        
        semantic_phase_path = Path("core/orchestrator/semantic_phase.py")
        if semantic_phase_path.exists():
            content = semantic_phase_path.read_text()
            assert "from products" not in content
            assert "import products" not in content
```

Reference requirements: ACC-SEM-001...005
```

---

## Step 10: Integration Testing

### Prompt 10.1: Create integration tests for semantic flow

```
Create `tests/integration/test_semantic_flow.py`:

```python
"""
Integration tests for semantic interpretation flow.
"""

import pytest


class TestSemanticFlowIntegration:
    """End-to-end tests for semantic phase in real flows."""
    
    @pytest.mark.asyncio
    async def test_semantic_continue_executes_steps(self):
        """High confidence input proceeds to step execution."""
        # TODO: Run hello_world flow with "hello world"
        # Assert: Run completes successfully
        # Assert: semantic_interpretation_completed event has confidence > 0.7
        pass
    
    @pytest.mark.asyncio
    async def test_semantic_ask_user_pauses_run(self):
        """Low confidence input pauses for clarification."""
        # TODO: Run hello_world flow with ambiguous input
        # Assert: Run status is PAUSED_WAITING_FOR_USER
        # Assert: Response includes clarifying_question
        pass
    
    @pytest.mark.asyncio
    async def test_semantic_resume_after_clarification(self):
        """Run can be resumed after user provides clarification."""
        # TODO: Start run that pauses for clarification
        # TODO: Resume with clarified input
        # Assert: Run completes successfully
        pass
    
    @pytest.mark.asyncio
    async def test_semantic_skip_via_config(self):
        """Semantic phase can be skipped via flow config."""
        # TODO: Run flow with skip_semantic_interpretation: true
        # Assert: No semantic_interpretation_started event
        # Assert: Run proceeds directly to steps
        pass
```

Reference requirements: ORC-SEM-001, ORC-SEM-002
```

---

## Step 11: Final Validation

### Prompt 11.1: Run all tests

```
Run the complete test suite to validate implementation:

```bash
# Run all semantic-related tests
pytest tests/unit/core/contracts/test_semantic_schema.py -v
pytest tests/unit/core/orchestrator/test_normalization.py -v
pytest tests/unit/core/orchestrator/test_semantic_phase.py -v
pytest tests/architecture/test_semantic_isolation.py -v
pytest tests/integration/test_semantic_flow.py -v

# Run full test suite
pytest tests/ -v

# Check coverage
pytest tests/ --cov=core/orchestrator --cov=core/contracts --cov-report=term-missing
```

Expected results:
- All tests pass
- Coverage for semantic modules > 85%
- No import violations in architecture tests
```

### Prompt 11.2: Manual smoke test

```
Perform manual smoke test:

1. Start the platform:
   ```bash
   python -m gateway.cli run hello_world hello_world --payload '{"text": "hello world"}'
   ```
   Expected: Run completes with greeting response

2. Test low confidence:
   ```bash
   python -m gateway.cli run hello_world hello_world --payload '{"text": "xyz123"}'
   ```
   Expected: Run pauses for clarification

3. Check trace events:
   ```bash
   cat observability/hello_world/<run_id>/runtime/events.jsonl | grep semantic
   ```
   Expected: See semantic_interpretation_started, semantic_interpretation_completed
```

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'core.contracts.semantic_schema'`
- Ensure `core/contracts/__init__.py` exports semantic models
- Check PYTHONPATH includes project root

**Issue**: Tests fail with "semantic_interpretation_started not found"
- Verify tracer is properly injected into SemanticPhase
- Check that emit() is being called (add debug logging)

**Issue**: Product adapter not found
- Ensure `products/<name>/semantic.py` exists
- Check that `SemanticAdapter` is exported
- Verify product is enabled in `configs/products.yaml`

**Issue**: Confidence threshold not being applied
- Check `configs/app.yaml` has `semantic.default_confidence_threshold`
- Verify `get_semantic_threshold()` is being called
- Check product-specific override in `configs/products.yaml`

---

## Checklist

- [ ] `core/contracts/semantic_schema.py` created with all models
- [ ] `core/orchestrator/normalization.py` created with rules
- [ ] `core/orchestrator/semantic_phase.py` created
- [ ] `products/hello_world/semantic.py` created as reference
- [ ] `core/orchestrator/engine.py` modified to call semantic phase
- [ ] `configs/app.yaml` updated with semantic settings
- [ ] `configs/products.yaml` updated with per-product thresholds
- [ ] `core/governance/hooks.py` has confidence check
- [ ] `core/memory/tracing.py` has semantic event types
- [ ] Unit tests pass
- [ ] Architecture tests pass
- [ ] Integration tests pass
- [ ] Manual smoke test passes
