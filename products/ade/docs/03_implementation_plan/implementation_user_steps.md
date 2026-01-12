# ADE Implementation User Steps

> **Document**: Implementation User Steps  
> **Status**: Active  
> **Last Updated**: 2026-01-12

---

## Overview

Executable prompts for implementing ADE Semantic Interpretation. Each step is a standalone task that can be given to an AI coding assistant.

---

## Step 1: Create Intent Taxonomy

**File**: `products/ade/intents.py`

**Prompt**:
```
Create products/ade/intents.py with:

1. ADEIntentType enum (str, Enum) with values:
   - DESCRIBE_DATA = "describe_data"
   - COMPARE_PERIODS = "compare_periods"  
   - TREND_ANALYSIS = "trend_analysis"
   - ANOMALY_REVIEW = "anomaly_review"
   - OPEN_ENDED_ANALYSIS = "open_ended_analysis"

2. IntentRequirements dataclass with:
   - required_fields: List[str]
   - optional_fields: List[str]

3. INTENT_REQUIREMENTS dict mapping ADEIntentType to IntentRequirements:
   - DESCRIBE_DATA: required=["dataset"], optional=["metrics", "time_scope"]
   - COMPARE_PERIODS: required=["dataset", "time_scope"], optional=["metrics"]
   - TREND_ANALYSIS: required=["dataset", "metrics", "time_scope"], optional=[]
   - ANOMALY_REVIEW: required=["dataset", "metrics"], optional=["time_scope"]
   - OPEN_ENDED_ANALYSIS: required=["dataset"], optional=["metrics", "time_scope"]

Use Pydantic ConfigDict(extra="forbid") on any models.
Reference techspec: SEM-INTENT-001 through SEM-INTENT-008.
```

**Acceptance**:
- [ ] File created at `products/ade/intents.py`
- [ ] ADEIntentType has 5 values
- [ ] INTENT_REQUIREMENTS covers all intents
- [ ] No LLM imports

---

## Step 2: Create Semantic Adapter

**File**: `products/ade/semantic_adapter.py`

**Prompt**:
```
Create products/ade/semantic_adapter.py with ADESemanticAdapter class:

1. Import ADEIntentType from products.ade.intents
2. Import SemanticEnvelope from core.contracts (or define locally if not exists)

3. Implement interpret(self, user_input: str, context: Optional[Dict] = None) -> SemanticEnvelope:
   - Use keyword/pattern matching to classify intent (NO LLM calls)
   - Keywords for each intent:
     * DESCRIBE_DATA: "describe", "summarize", "overview", "what is"
     * COMPARE_PERIODS: "compare", "versus", "vs", "difference between"
     * TREND_ANALYSIS: "trend", "over time", "growth", "decline", "trajectory"
     * ANOMALY_REVIEW: "anomaly", "outlier", "unusual", "spike", "drop"
     * OPEN_ENDED_ANALYSIS: fallback for ambiguous input
   
   - Extract metrics: look for numeric column names or keywords like "revenue", "cost", "volume"
   - Extract time_scope: look for patterns like "Q1", "last 30 days", "2024", "YTD"
   - Compute confidence: higher if intent keywords match strongly, lower if ambiguous

4. Return SemanticEnvelope with:
   - intent_type: str
   - requested_outputs: List[str] 
   - metrics: List[str]
   - time_scope: Optional[str]
   - constraints: Dict[str, Any]
   - confidence: float (0.0-1.0)
   - raw_input: str

Reference techspec: SEM-ADAPTER-001 through SEM-ADAPTER-005.
Classification MUST be deterministic - no LLM calls.
```

**Acceptance**:
- [ ] File created at `products/ade/semantic_adapter.py`
- [ ] ADESemanticAdapter.interpret() returns SemanticEnvelope
- [ ] Intent classification uses patterns only
- [ ] No LLM imports or API calls

---

## Step 3: Create Semantic Validation

**File**: `products/ade/semantic_validation.py`

**Prompt**:
```
Create products/ade/semantic_validation.py with:

1. ValidationResult Pydantic model:
   - is_valid: bool
   - missing_fields: List[str]
   - clarifying_question: Optional[str]
   - confidence_adjustment: float
   - outcome: Literal["PROCEED", "ASK_USER", "ABORT"]
   - Use ConfigDict(extra="forbid")

2. validate_semantic_envelope(envelope: SemanticEnvelope, intent_type: ADEIntentType) -> ValidationResult:
   - Get required fields from INTENT_REQUIREMENTS[intent_type]
   - Check which required fields are missing/empty in envelope
   - Determine outcome:
     * PROCEED: all required fields present, is_valid=True
     * ASK_USER: missing fields that can be clarified (metrics, time_scope)
     * ABORT: critical missing fields (dataset) with no way to clarify
   - Compute confidence_adjustment:
     * 0.0 if all fields present
     * -0.1 to -0.3 for missing optional fields
   - Generate clarifying_question if ASK_USER (import from clarifying_questions)

Reference techspec: SEM-VALIDATE-001 through SEM-VALIDATE-007.
```

**Acceptance**:
- [ ] File created at `products/ade/semantic_validation.py`
- [ ] ValidationResult has all required fields
- [ ] validate_semantic_envelope returns correct outcomes
- [ ] Confidence adjustment calculated correctly

---

## Step 4: Create Clarifying Questions

**File**: `products/ade/clarifying_questions.py`

**Prompt**:
```
Create products/ade/clarifying_questions.py with:

1. CLARIFYING_TEMPLATES dictionary mapping field names to question strings:
   - "metrics": "Which specific metric would you like to focus on? (e.g., revenue, cost, volume)"
   - "time_scope": "What time period should we analyze? (e.g., last 30 days, Q1 2024, YTD)"
   - "anomaly_threshold": "What threshold should we use for anomaly detection? (default: 2.0 standard deviations)"
   - "dataset": "Which dataset would you like to analyze?"
   - "comparison_periods": "Which time periods would you like to compare? (e.g., Q1 vs Q2, 2023 vs 2024)"

2. get_clarifying_question(missing_field: str, intent_type: Optional[ADEIntentType] = None) -> str:
   - Return template from CLARIFYING_TEMPLATES if exists
   - Return generic fallback: f"Please specify the {missing_field} for this analysis."
   - Optionally customize based on intent_type if needed

All questions MUST be from predefined templates - NO LLM generation.

Reference techspec: SEM-CLARIFY-001 through SEM-CLARIFY-006.
```

**Acceptance**:
- [ ] File created at `products/ade/clarifying_questions.py`
- [ ] CLARIFYING_TEMPLATES covers key fields
- [ ] get_clarifying_question returns deterministic strings
- [ ] No LLM imports or API calls

---

## Step 5: Create Intent Router

**File**: `products/ade/intent_router.py`

**Prompt**:
```
Create products/ade/intent_router.py with:

1. RouteResult Pydantic model:
   - flow_name: str
   - initial_parameters: Dict[str, Any]
   - Use ConfigDict(extra="forbid")

2. ROUTING_TABLE constant mapping ADEIntentType to (flow_name, parameter_keys):
   - DESCRIBE_DATA: ("visualization", ["dataset", "intent_summary"])
   - COMPARE_PERIODS: ("ade_v1", ["prompt", "dataset", "time_scope"])
   - TREND_ANALYSIS: ("ade_v1", ["prompt", "dataset", "metrics"])
   - ANOMALY_REVIEW: ("ade_v1", ["prompt", "dataset", "metrics"])
   - OPEN_ENDED_ANALYSIS: ("visualization", ["dataset"])

3. route_intent(envelope: SemanticEnvelope) -> RouteResult:
   - Look up flow_name from ROUTING_TABLE based on envelope.intent_type
   - Build initial_parameters by extracting relevant fields from envelope
   - Always include dataset in parameters
   - For ade_v1 flows, set prompt = envelope.raw_input
   - Return RouteResult

Reference techspec: SEM-ROUTER-001 through SEM-ROUTER-005.
```

**Acceptance**:
- [ ] File created at `products/ade/intent_router.py`
- [ ] RouteResult model defined
- [ ] route_intent returns correct flow for each intent type
- [ ] Parameters correctly mapped from envelope

---

## Step 6: Create Semantic Observability

**File**: `products/ade/observability.py`

**Prompt**:
```
Create products/ade/observability.py with:

1. emit_semantic_trace(envelope: SemanticEnvelope, validation_result: Optional[ValidationResult] = None) -> None:
   - Import emit_event from core.governance.hooks (or stub if not exists)
   - Build trace metadata dict with ADE-specific fields:
     * ade_intent: envelope.intent_type
     * ade_confidence: envelope.confidence (adjusted if validation_result provided)
     * ade_missing_fields: validation_result.missing_fields if non-empty, else omit
     * ade_clarifying_question: validation_result.clarifying_question if present, else omit
   - Emit trace event with event_type="semantic_interpretation"
   - Place ADE fields in metadata.product_specific namespace

2. If core.governance.hooks doesn't exist, create a stub that logs the event.

Reference techspec: SEM-OBS-001 through SEM-OBS-007.
```

**Acceptance**:
- [ ] File created at `products/ade/observability.py`
- [ ] emit_semantic_trace emits all required fields
- [ ] ade_missing_fields only present when applicable
- [ ] ade_clarifying_question only present when generated

---

## Step 7: Integration Tests

**File**: `tests/unit/products/ade/test_semantic_interpretation.py`

**Prompt**:
```
Create tests/unit/products/ade/test_semantic_interpretation.py with:

1. Test ADESemanticAdapter:
   - test_interpret_trend_analysis: "Show me revenue trends over Q1" → TREND_ANALYSIS
   - test_interpret_anomaly_review: "Find anomalies in sales data" → ANOMALY_REVIEW
   - test_interpret_compare_periods: "Compare Q1 vs Q2 revenue" → COMPARE_PERIODS
   - test_interpret_describe_data: "Summarize this dataset" → DESCRIBE_DATA
   - test_interpret_fallback: ambiguous input → OPEN_ENDED_ANALYSIS

2. Test Validation:
   - test_validate_complete_envelope: all fields → PROCEED
   - test_validate_missing_metrics: → ASK_USER with clarifying question
   - test_validate_missing_dataset: → ABORT

3. Test Intent Router:
   - test_route_trend_analysis: → ade_v1 flow
   - test_route_describe_data: → visualization flow

4. Test Clarifying Questions:
   - test_metric_question: deterministic output
   - test_time_scope_question: deterministic output

Use pytest fixtures for common SemanticEnvelope instances.
```

**Acceptance**:
- [ ] Test file created
- [ ] All semantic interpretation modules covered
- [ ] Tests pass with `pytest tests/unit/products/ade/test_semantic_interpretation.py`

---

## Step 8: Wire Into Flows (Optional)

**Files**: `products/ade/flows/ade_v1.yaml`, `products/ade/flows/visualization.yaml`

**Prompt**:
```
Update ADE flows to use semantic interpretation:

1. In ade_v1.yaml:
   - Add semantic_interpretation step before intent_interpretation
   - Step invokes ADESemanticAdapter.interpret()
   - Add validation step after semantic interpretation
   - Add conditional HITL step if validation returns ASK_USER

2. In visualization.yaml:
   - Add semantic_interpretation for dataset-context questions
   - Route to appropriate analysis based on intent

3. Update flow entry points to accept SemanticEnvelope as alternative to raw prompt.

This step is optional and can be done after core modules are tested.
```

**Acceptance**:
- [ ] Flows updated with semantic interpretation steps
- [ ] HITL pause works for ASK_USER outcome
- [ ] E2E test passes with semantic interpretation enabled

---

## Execution Order

```
Step 1 (intents.py)
    ↓
Step 2 (semantic_adapter.py)
    ↓
Step 4 (clarifying_questions.py)  ←── can run in parallel with Step 3
    ↓
Step 3 (semantic_validation.py)
    ↓
Step 5 (intent_router.py)
    ↓
Step 6 (observability.py)
    ↓
Step 7 (tests)
    ↓
Step 8 (flow integration)
```

---

## Cross-References

- **Implementation Plan**: [implementation_plan.md](implementation_plan.md)
- **BRD**: [BRD-agents.md](../01_brd/BRD-agents.md#8-semantic-interpretation-requirements)
- **Techspec**: [AGENT-agents.md](../02_techspec/AGENT-agents.md#8-adesemantic-adapter-sem-adapter)
