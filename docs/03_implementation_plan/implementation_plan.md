# Semantic Interpretation Implementation Plan

> **Feature**: Semantic Interpretation Phase  
> **Version**: V1.0  
> **Status**: Planning  
> **Last Updated**: 2026-01-12

---

## 1. Executive Summary

### 1.1 What We're Building

A **mandatory semantic interpretation phase** that runs before planning/execution for every orchestrator run. This phase:
- Interprets user intent and normalizes input
- Extracts entities and constraints
- Assesses confidence and identifies ambiguities
- Decides whether to proceed, ask for clarification, or abort
- Enables product-specific interpretation via plugin adapters

### 1.2 Why It Matters

| Problem | Solution |
|---------|----------|
| Misunderstood requests proceed to execution | Semantic phase catches ambiguity before any action |
| No way to request clarification mid-flow | `ASK_USER` action pauses and prompts user |
| Products can't customize interpretation | `ProductSemanticAdapter` provides domain hooks |
| Confidence not tracked or enforced | Threshold-based gating prevents low-confidence execution |
| No audit trail for interpretation | Structured trace events capture every decision |

### 1.3 Scope

**In Scope (V1)**:
- Core `SemanticEnvelope` and `ValidationResult` contracts
- `NextAction` enum with CONTINUE/ASK_USER/ABORT
- Orchestrator semantic phase integration
- Product adapter interface (interpret + validate hooks)
- Confidence threshold enforcement
- Deterministic normalization rules
- Trace events for semantic steps
- 3 mandatory architecture tests

**Out of Scope (V1.1+)**:
- ML-based intent classification
- Multi-turn clarification dialogs
- Automatic entity resolution via external APIs
- Learning from user corrections

---

## 2. Architecture Overview

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Orchestrator Engine                          │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐   │
│  │ Run Init     │───▶│ Semantic Phase   │───▶│ Step Execution  │   │
│  └──────────────┘    └────────┬─────────┘    └─────────────────┘   │
│                               │                                      │
│                               ▼                                      │
│                    ┌──────────────────┐                              │
│                    │ NextAction Check │                              │
│                    └────────┬─────────┘                              │
│                             │                                        │
│          ┌─────────────┬────┴────┬──────────────┐                   │
│          ▼             ▼         ▼              ▼                   │
│      CONTINUE      ASK_USER    ABORT    NEEDS_APPROVAL              │
│          │             │         │              │                   │
│          ▼             ▼         ▼              ▼                   │
│      Execute       PAUSED_     FAILED      PENDING_                 │
│       Steps      WAITING_FOR   (abort)      HUMAN                   │
│                     _USER                                            │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Product Semantic Adapter                        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐         ┌──────────────────┐                  │
│  │   interpret()    │         │    validate()    │                  │
│  │                  │         │                  │                  │
│  │ - Extract intent │         │ - Domain rules   │                  │
│  │ - Parse entities │         │ - Missing fields │                  │
│  │ - Set confidence │         │ - Adjust conf.   │                  │
│  └──────────────────┘         └──────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
User Input (raw_input)
       │
       ▼
┌──────────────────┐
│ Core Normalizer  │  ← Trim, dedupe, stable order
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Product Adapter  │  ← interpret(context) → SemanticEnvelope
│   .interpret()   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Product Adapter  │  ← validate(envelope, context) → ValidationResult
│   .validate()    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Confidence Gate  │  ← if confidence < threshold → ASK_USER/ABORT
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ NextAction Check │  ← CONTINUE/ASK_USER/ABORT/NEEDS_APPROVAL
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
 Execute    Pause/Fail
  Steps     with Response
```

---

## 3. Implementation Phases

### Phase 1: Contracts & Schema (Days 1-2)

**Goal**: Define all Pydantic models for semantic interpretation.

| Deliverable | File | Requirements |
|-------------|------|--------------|
| `SemanticEnvelope` | `core/contracts/semantic_schema.py` | ORC-SEM-010...019 |
| `NextAction` enum | `core/contracts/semantic_schema.py` | ORC-SEM-020...022 |
| `ValidationResult` | `core/contracts/semantic_schema.py` | INT-SEM-VAL-001...006 |
| `Entity` model | `core/contracts/semantic_schema.py` | Supporting model |
| `SemanticContext` | `core/contracts/semantic_schema.py` | Input to adapters |

**Key Design Decisions**:
- All models use `ConfigDict(extra="forbid")` for strict validation
- Confidence bounded 0.0-1.0 with `ge=0.0, le=1.0`
- `ambiguities` and `entities` capped at 20 items
- `NextAction` uses string enum for JSON serialization

---

### Phase 2: Core Normalization Rules (Day 3)

**Goal**: Implement domain-agnostic normalization in core.

| Rule | Implementation | Requirements |
|------|----------------|--------------|
| Whitespace trimming | Strip leading/trailing, collapse internal | ORC-SEM-030 |
| Case normalization | Lowercase for matching (preserve original) | ORC-SEM-030 |
| Entity deduplication | Same type+value → single entity | ORC-SEM-031 |
| Constraint merging | Deterministic merge of overlapping constraints | ORC-SEM-032 |
| Stable ordering | Sort entities by (type, value), constraints by key | ORC-SEM-033 |
| Schema coercion | String→int, string→date where schema declares | ORC-SEM-034 |

**What NOT to Include**:
- Domain rules like "trend requires time axis" (ORC-SEM-035)
- Product-specific entity types
- Business logic validation

---

### Phase 3: Product Adapter Interface (Days 4-5)

**Goal**: Define and implement the product plugin interface.

**Interface Definition**:
```python
# core/contracts/semantic_schema.py (or separate file)

class ProductSemanticAdapter(ABC):
    """
    Product-provided semantic interpretation adapter.
    Products implement this to customize interpretation and validation.
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
        Validate the semantic envelope against domain rules.
        
        Args:
            envelope: Output from interpret()
            context: Original context for reference
            
        Returns:
            ValidationResult with is_valid, violations, revised_confidence
        """
        pass
```

**Default Adapter** (for products without custom adapter):
- `interpret()`: Passthrough with basic heuristics
- `validate()`: Always returns `is_valid=True`, confidence unchanged

**Registration**:
- Adapters discovered from `products/<name>/semantic.py`
- Registered via `ProductCatalog` during product load
- Resolved via `ProductRouter.get_semantic_adapter(product_id)`

---

### Phase 4: Orchestrator Integration (Days 6-8)

**Goal**: Integrate semantic phase into orchestrator engine.

**File**: `core/orchestrator/semantic_phase.py`

```python
class SemanticPhase:
    """Executes semantic interpretation before step execution."""
    
    def __init__(self, product_router: ProductRouter, tracer: Tracer):
        self.product_router = product_router
        self.tracer = tracer
    
    async def execute(
        self,
        raw_input: str,
        payload: dict,
        product_id: str,
        flow_config: FlowConfig,
    ) -> SemanticPhaseResult:
        """
        Execute semantic interpretation phase.
        
        Returns:
            SemanticPhaseResult with envelope, validation, and next_action
        """
        # 1. Skip check
        if flow_config.skip_semantic_interpretation:
            return self._create_passthrough_result(raw_input, payload)
        
        # 2. Emit start event
        self.tracer.emit("semantic_interpretation_started", {...})
        
        # 3. Build context
        context = SemanticContext(
            raw_input=raw_input,
            payload=payload,
            product_config=self.product_router.get_config(product_id),
        )
        
        # 4. Get adapter (or default)
        adapter = self.product_router.get_semantic_adapter(product_id)
        
        # 5. Interpret
        envelope = adapter.interpret(context)
        
        # 6. Apply core normalization
        envelope = self._apply_core_normalization(envelope)
        
        # 7. Validate
        validation = adapter.validate(envelope, context)
        
        # 8. Confidence check
        threshold = self._get_confidence_threshold(product_id)
        if envelope.confidence < threshold and validation.is_valid:
            envelope.proposed_next_action = NextAction.ASK_USER
        
        # 9. Emit completion event
        self.tracer.emit("semantic_interpretation_completed", {
            "envelope_hash": hash(envelope),
            "confidence": envelope.confidence,
            "ambiguity_count": len(envelope.ambiguities),
            "next_action": envelope.proposed_next_action,
        })
        
        return SemanticPhaseResult(
            envelope=envelope,
            validation=validation,
            next_action=envelope.proposed_next_action,
        )
```

**Engine Integration** (`core/orchestrator/engine.py`):

```python
class OrchestrationEngine:
    async def run_flow(self, ...):
        # ... existing run init ...
        
        # NEW: Semantic phase (after init, before steps)
        semantic_result = await self.semantic_phase.execute(
            raw_input=payload.get("text", ""),
            payload=payload,
            product_id=product_id,
            flow_config=flow.config,
        )
        
        # Handle next action
        match semantic_result.next_action:
            case NextAction.CONTINUE:
                pass  # Proceed to steps
            case NextAction.ASK_USER:
                return await self._pause_for_clarification(
                    run_context,
                    semantic_result,
                )
            case NextAction.ABORT:
                return await self._fail_run(
                    run_context,
                    code="semantic_abort",
                    reason=semantic_result.validation.violations,
                )
            case NextAction.NEEDS_APPROVAL:
                return await self._request_semantic_approval(
                    run_context,
                    semantic_result,
                )
        
        # ... existing step execution ...
```

---

### Phase 5: Stop/Pause Mechanism (Days 9-10)

**Goal**: Implement structured responses for ASK_USER and ABORT.

**ASK_USER Response**:
```python
class ClarificationResponse(BaseModel):
    """Returned when semantic phase needs user clarification."""
    run_id: str
    status: Literal["PAUSED_WAITING_FOR_USER"]
    clarification_needed: bool = True
    question: str
    ambiguities: list[str]
    original_confidence: float
    context: dict  # What we understood so far
```

**ABORT Response**:
```python
class SemanticAbortError(BaseModel):
    """Returned when semantic phase cannot proceed."""
    run_id: str
    status: Literal["FAILED"]
    error_code: Literal["semantic_abort"]
    reason: str
    violations: list[str]
    ambiguities: list[str]
```

**Trace Events**:
- `semantic_stop_issued` with next_action, question (if ASK_USER), reason (if ABORT)

---

### Phase 6: Confidence Thresholds (Days 11-12)

**Goal**: Implement configurable confidence thresholds.

**Configuration** (`configs/app.yaml`):
```yaml
semantic:
  default_confidence_threshold: 0.7
  require_semantic_phase: true
```

**Per-Product Override** (`configs/products.yaml`):
```yaml
by_product:
  ade:
    semantic_confidence_threshold: 0.8  # Stricter for ADE
  hello_world:
    semantic_confidence_threshold: 0.5  # More lenient for demo
```

**Governance Hook**:
```python
# core/governance/hooks.py

def check_semantic_confidence(
    envelope: SemanticEnvelope,
    threshold: float,
) -> GovernanceDecision:
    """
    Enforce confidence threshold on semantic interpretation.
    """
    if envelope.confidence < threshold:
        return GovernanceDecision(
            allowed=False,
            reason=f"confidence {envelope.confidence} below threshold {threshold}",
            suggested_action=NextAction.ASK_USER,
        )
    return GovernanceDecision(allowed=True)
```

---

### Phase 7: Trace Events (Days 13-14)

**Goal**: Emit structured trace events for semantic steps.

| Event | When | Payload |
|-------|------|---------|
| `semantic_interpretation_started` | Phase begins | `run_id`, `product_id`, `raw_input_length` |
| `semantic_interpretation_completed` | Phase succeeds | `envelope_hash`, `confidence`, `ambiguity_count`, `entity_count`, `next_action` |
| `semantic_validation_completed` | After validate() | `is_valid`, `missing_fields`, `violation_count`, `revised_confidence` |
| `semantic_stop_issued` | ASK_USER or ABORT | `next_action`, `question` (if ASK_USER), `reason` (if ABORT), `violations` |

**Implementation** (`core/memory/tracing.py`):
- Add event types to `TraceEventKind` enum
- Ensure events include `ts`, `run_id`, `step_id` (null for semantic phase)

---

### Phase 8: Architecture Tests (Days 15-16)

**Goal**: Implement 3 mandatory tests that lock behavior.

**File**: `tests/architecture/test_semantic_isolation.py`

```python
import pytest
from pathlib import Path

class TestSemanticIsolation:
    """
    Architecture tests for semantic interpretation.
    These tests prevent regression of key invariants.
    """
    
    def test_semantic_phase_is_mandatory(self):
        """
        Verifies: ORC-SEM-001, ORC-SEM-003
        
        The orchestrator MUST call semantic phase before any step execution.
        """
        # 1. Create a mock flow with steps
        # 2. Run the flow
        # 3. Assert semantic_interpretation_started event emitted BEFORE step_started
        # 4. Assert SemanticEnvelope is populated in run context
        pass
    
    def test_stop_blocks_execution(self):
        """
        Verifies: ORC-SEM-STOP-001, ORC-SEM-STOP-004, ORC-SEM-STOP-007
        
        NextAction=ASK_USER or ABORT MUST prevent step execution.
        """
        # 1. Create adapter that returns ASK_USER
        # 2. Run flow
        # 3. Assert NO step_started events
        # 4. Assert run status is PAUSED_WAITING_FOR_USER
        
        # 5. Create adapter that returns ABORT
        # 6. Run flow
        # 7. Assert NO step_started events
        # 8. Assert run status is FAILED with code semantic_abort
        pass
    
    def test_product_adapter_isolated(self):
        """
        Verifies: PROD-SEM-INT-005, PROD-SEM-INT-006, PROD-SEM-VAL-005, PROD-SEM-VAL-006
        
        Products supply interpret/validate; core never imports product domain code;
        products never import core execution internals.
        """
        # 1. Scan all product semantic.py files
        # 2. Assert NO imports from core/orchestrator/*
        # 3. Scan core/orchestrator/*.py
        # 4. Assert NO imports from products/*
        # 5. Verify adapter interface is called via ProductRouter only
        
        core_orchestrator_files = Path("core/orchestrator").glob("*.py")
        for f in core_orchestrator_files:
            content = f.read_text()
            assert "from products" not in content
            assert "import products" not in content
        
        product_semantic_files = Path("products").glob("*/semantic.py")
        for f in product_semantic_files:
            content = f.read_text()
            assert "from core.orchestrator" not in content
            assert "import core.orchestrator" not in content
        pass
```

---

## 4. File Inventory

### New Files

| File | Purpose | Requirements |
|------|---------|--------------|
| `core/contracts/semantic_schema.py` | Pydantic models for semantic interpretation | ORC-SEM-010...022, INT-SEM-VAL-* |
| `core/orchestrator/semantic_phase.py` | Semantic phase executor | ORC-SEM-001...004, ORC-SEM-030...043 |
| `core/orchestrator/product_router.py` | Route to product adapters | PROD-SEM-005 |
| `products/hello_world/semantic.py` | Reference adapter implementation | PROD-SEM-* |
| `tests/architecture/test_semantic_isolation.py` | Architecture invariant tests | ACC-SEM-* |
| `tests/unit/core/contracts/test_semantic_schema.py` | Schema validation tests | — |
| `tests/unit/core/orchestrator/test_semantic_phase.py` | Phase execution tests | — |

### Modified Files

| File | Changes |
|------|---------|
| `core/orchestrator/engine.py` | Add semantic phase call before step execution |
| `core/orchestrator/run_lifecycle.py` | Add `semantic_envelope` to RunRecord |
| `core/contracts/run_schema.py` | Add `semantic_envelope` field, new error codes |
| `core/governance/hooks.py` | Add `check_semantic_confidence` hook |
| `core/memory/tracing.py` | Add semantic trace event types |
| `configs/app.yaml` | Add `semantic` section with defaults |
| `configs/products.yaml` | Add per-product `semantic_confidence_threshold` |

---

## 5. Testing Strategy

### Unit Tests

| Test File | Coverage |
|-----------|----------|
| `test_semantic_schema.py` | All Pydantic models, validation, bounds |
| `test_semantic_phase.py` | Phase execution, skip logic, normalization |
| `test_product_router.py` | Adapter resolution, default fallback |
| `test_semantic_confidence.py` | Threshold checking, governance hook |

### Integration Tests

| Test File | Scenario |
|-----------|----------|
| `test_semantic_flow.py` | Full flow with semantic phase |
| `test_semantic_pause.py` | ASK_USER pauses correctly |
| `test_semantic_abort.py` | ABORT fails with correct error |
| `test_semantic_resume.py` | Resume after clarification |

### Architecture Tests

| Test | Invariant |
|------|-----------|
| `test_semantic_phase_is_mandatory` | Phase always runs |
| `test_stop_blocks_execution` | ASK_USER/ABORT blocks steps |
| `test_product_adapter_isolated` | No cross-layer imports |

---

## 6. Rollout Plan

### Phase 1: Feature Flag (Week 1)
- Deploy with `semantic.require_semantic_phase: false`
- Run in shadow mode (interpret but don't block)
- Collect metrics on confidence distribution

### Phase 2: Opt-In Products (Week 2)
- Enable for `hello_world` product only
- Validate clarification flow works end-to-end
- Tune confidence thresholds

### Phase 3: All Products (Week 3)
- Enable globally with `require_semantic_phase: true`
- Monitor for unexpected ASK_USER/ABORT rates
- Provide escape hatch via flow config

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Misunderstood task rate | < 5% | User reports after clarification |
| Clarification acceptance | > 80% | Users proceed after ASK_USER |
| False positive rate | < 10% | Unnecessary ASK_USER events |
| Semantic phase latency | < 100ms | P99 execution time |
| Test coverage | 100% | Architecture tests passing |

---

## 8. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Too many ASK_USER pauses | User frustration | Start with low threshold (0.5), tune up |
| Product adapters slow | Run latency | Add timeout, fallback to default |
| Backwards compatibility | Existing flows break | Feature flag, gradual rollout |
| Complex domain rules | Maintenance burden | Keep core minimal, push to products |

---

## 9. Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Pydantic v2 | Library | ✅ Available |
| Tracer | Internal | ✅ Exists |
| ProductCatalog | Internal | ✅ Exists |
| GovernanceHooks | Internal | ✅ Exists |
| User input resume flow | Internal | ✅ Exists |

---

## 10. Timeline Summary

| Week | Phase | Deliverables |
|------|-------|--------------|
| Week 1 | Contracts + Normalization | `semantic_schema.py`, core rules |
| Week 2 | Adapter + Integration | `semantic_phase.py`, engine changes |
| Week 3 | Stop/Pause + Confidence | Response models, thresholds |
| Week 4 | Tests + Rollout | Architecture tests, feature flag |

**Total Effort**: ~16 engineering days

---

## 11. Traceability

| BRD | Techspec | Implementation |
|-----|----------|----------------|
| BRD-AUTO-025 | ORC-SEM-001...004 | `semantic_phase.py` |
| BRD-AUTO-026 | ORC-SEM-030...035 | Core normalization |
| BRD-AUTO-027 | INT-SEM-CONF-* | Confidence thresholds |
| BRD-GOV-025 | ORC-SEM-STOP-* | Stop/pause mechanism |
| BRD-GOV-026 | INT-SEM-CONF-002...004 | Per-product thresholds |
| BRD-GOV-027 | INT-SEM-VAL-006 | Validation blocking |
