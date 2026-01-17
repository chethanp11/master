# ADE Agent Requirements

> **Document**: Technical Specification — Agents & Semantic Interpretation  
> **Prefix**: AGENT-*, SEM-*  
> **Requirements**: ~50

---

## 1. General Agent Requirements (AGENT-GEN)

### AGENT-GEN-001: Agent Descriptors
**Priority**: P0  
**Description**: All agents MUST have descriptors in `products/ade/descriptors.py`.

**Acceptance Criteria**:
- [ ] AgentDescriptor exists for each agent
- [ ] Descriptor includes purpose, capabilities, cost_hint
- [ ] AGENT_DESCRIPTORS map exports all descriptors

---

### AGENT-GEN-002: Cost Hints
**Priority**: P1  
**Description**: Agents MUST have accurate cost hints.

| Agent | Cost Hint |
|-------|-----------|
| intent_agent | MED |
| plan_agent | MED |
| plan_proposal_agent | LOW |
| planning_agent | MED |
| sufficiency_evaluator | LOW |
| dashboard_agent | MED |

---

### AGENT-GEN-003: Step Type Restrictions
**Priority**: P1  
**Description**: Agents MUST only be invoked from allowed step types.

| Agent | Allowed Step Types |
|-------|-------------------|
| plan_proposal_agent | agent, plan_proposal |
| (others) | agent |

---

## 2. intent_agent (AGENT-INTENT)

### AGENT-INTENT-001: Output Schema
**Priority**: P0  
**Description**: intent_agent MUST output IntentFrame schema.

**Fields**:
```python
intent_summary: str
inferred_entities: List[str]
inferred_metrics: List[str]
inferred_time_window: Optional[str]
requested_outputs: List[str]
confidence_score: float
confidence_label: str
blocking_required: bool
blocking_questions: List[str]
blocking_question: Optional[str]
```

---

### AGENT-INTENT-002: Confidence Scoring
**Priority**: P1  
**Description**: intent_agent MUST provide confidence_score (0.0-1.0) and confidence_label.

**Acceptance Criteria**:
- [ ] confidence_score is float between 0.0 and 1.0
- [ ] confidence_label is one of: "low", "medium", "high"
- [ ] Labels map to score ranges: low < 0.4, medium 0.4-0.7, high > 0.7

---

### AGENT-INTENT-003: Blocking Detection
**Priority**: P1  
**Description**: intent_agent MUST detect when clarification is needed.

**Acceptance Criteria**:
- [ ] blocking_required is True when dataset/metric/time window is missing
- [ ] blocking_questions lists specific questions to ask
- [ ] blocking_question contains the primary question

---

### AGENT-INTENT-004: Entity Extraction
**Priority**: P1  
**Description**: intent_agent MUST extract entities from user input.

**Acceptance Criteria**:
- [ ] Dataset names are extracted to inferred_entities
- [ ] Metric names are extracted to inferred_metrics
- [ ] Time windows are extracted to inferred_time_window

---

## 3. plan_agent (AGENT-PLAN)

### AGENT-PLAN-001: Output Schema
**Priority**: P0  
**Description**: plan_agent MUST output PlanSpec schema.

**Acceptance Criteria**:
- [ ] Output is valid PlanSpec
- [ ] Includes tool flags for conditional execution
- [ ] Plan is deterministic

---

### AGENT-PLAN-002: Deterministic Plans
**Priority**: P0  
**Description**: plan_agent MUST produce deterministic plans.

**Acceptance Criteria**:
- [ ] Same inputs produce identical plans
- [ ] No random selection of steps or tools
- [ ] Tool flags are derived from user input

---

## 4. plan_proposal_agent (AGENT-PROPOSAL)

### AGENT-PROPOSAL-001: Output Schema
**Priority**: P0  
**Description**: plan_proposal_agent MUST output PlanProposal.

**Fields**:
```python
proposal_id: str
summary: str
estimated_steps: int
estimated_cost: str  # "LOW", "MED", "HIGH"
requires_approval: bool
```

---

### AGENT-PROPOSAL-002: Approval Requirement
**Priority**: P0  
**Description**: plan_proposal_agent MUST set requires_approval appropriately.

**Acceptance Criteria**:
- [ ] requires_approval is True for non-trivial plans
- [ ] Execution pauses for user decision

---

### AGENT-PROPOSAL-003: Cost Estimation
**Priority**: P1  
**Description**: plan_proposal_agent MUST estimate execution cost.

**Acceptance Criteria**:
- [ ] estimated_cost reflects tool cost hints
- [ ] estimated_steps matches plan step count

---

## 5. planning_agent (AGENT-PLANNING)

### AGENT-PLANNING-001: Dual Role
**Priority**: P1  
**Description**: planning_agent MUST support both intent interpretation and replanning.

**Acceptance Criteria**:
- [ ] Used for intent_interpretation step in visualization flow
- [ ] Used for planning step after sufficiency_eval
- [ ] Context determines behavior

---

### AGENT-PLANNING-002: Replan Notes
**Priority**: P1  
**Description**: planning_agent MUST produce replan notes after rejection.

**Acceptance Criteria**:
- [ ] Notes explain what changed
- [ ] Restart step is identified

---

## 6. sufficiency_evaluator (AGENT-SUFF)

### AGENT-SUFF-001: Output Schema
**Priority**: P0  
**Description**: sufficiency_evaluator MUST output confidence_level and downgrade_reasons.

**Fields**:
```python
confidence_level: str  # "high", "medium", "low"
downgrade_reasons: List[str]
```

---

### AGENT-SUFF-002: Confidence Levels
**Priority**: P0  
**Description**: sufficiency_evaluator MUST use standard confidence levels.

**Acceptance Criteria**:
- [ ] confidence_level is one of: "high", "medium", "low"
- [ ] Level reflects data quality assessment

---

### AGENT-SUFF-003: Downgrade Reasons
**Priority**: P1  
**Description**: sufficiency_evaluator MUST explain confidence downgrades.

**Acceptance Criteria**:
- [ ] downgrade_reasons lists specific issues
- [ ] Reasons are human-readable
- [ ] Empty list when confidence is high

---

### AGENT-SUFF-004: Data Quality Assessment
**Priority**: P1  
**Description**: sufficiency_evaluator MUST assess data quality from data_reader output.

**Acceptance Criteria**:
- [ ] Evaluates row count sufficiency
- [ ] Evaluates column completeness
- [ ] Evaluates data freshness if time column exists

---

## 7. dashboard_agent (AGENT-DASH)

### AGENT-DASH-001: Narrative Output
**Priority**: P1  
**Description**: dashboard_agent MUST produce narrative summary.

**Acceptance Criteria**:
- [ ] Summary is human-readable text
- [ ] Summary reflects dataset characteristics
- [ ] Summary is concise (< 500 words)

---

### AGENT-DASH-002: Dataset Summary Input
**Priority**: P1  
**Description**: dashboard_agent MUST accept dataset summaries as input.

**Acceptance Criteria**:
- [ ] Can process multiple dataset summaries
- [ ] Summarizes key metrics and trends

---

## Agent Advisory Boundary

### BRD-AGT-001: Advisory Only
**Priority**: P0  
**Description**: Agents MUST be advisory only and MUST NOT execute tools or mutate state.

**Acceptance Criteria**:
- [ ] Agents return recommendations only
- [ ] Tool execution always remains with orchestrator
- [ ] Agents do not write to storage or invoke tool backends

---

### BRD-AGT-002: Propose, Never Execute
**Priority**: P0  
**Description**: Agents MUST propose actions without executing them.

**Acceptance Criteria**:
- [ ] Agent outputs include proposed steps or recommendations only
- [ ] No agent step triggers direct tool execution

---

### BRD-AGT-003: Structured Outputs
**Priority**: P0  
**Description**: Agent outputs MUST be structured and schema-validated.

**Acceptance Criteria**:
- [ ] Outputs conform to Pydantic schemas
- [ ] Invalid outputs trigger validation errors

---

### BRD-AGT-004: Auditable Reasoning
**Priority**: P0  
**Description**: Agent reasoning MUST be traceable and auditable.

**Acceptance Criteria**:
- [ ] Trace events capture agent outputs
- [ ] Evidence references included where relevant

---

## Reasoning Ladder

### BRD-INTEL-001: Multi-Stage Reasoning
**Priority**: P0  
**Description**: ADE MUST use multi-stage reasoning (interpret → propose → critique → finalize).

**Acceptance Criteria**:
- [ ] Stages are explicit in agent outputs
- [ ] Outputs include stage identifier

---

### BRD-INTEL-002: Observable Stages
**Priority**: P0  
**Description**: Each reasoning stage MUST be observable in traces.

**Acceptance Criteria**:
- [ ] Trace events include stage name
- [ ] Stage outputs are stored as artifacts

---

### BRD-INTEL-003: Bounded Cycles
**Priority**: P0  
**Description**: Reasoning cycles MUST be bounded by iterations, tools, and time.

**Acceptance Criteria**:
- [ ] Iteration cap enforced
- [ ] Tool call limits enforced
- [ ] Timeouts respected

---

### BRD-INTEL-004: Sufficiency Tracking
**Priority**: P1  
**Description**: Reasoning MUST track sufficiency state across cycles.

**Acceptance Criteria**:
- [ ] Outputs include known/unknown/blocked fields
- [ ] Sufficiency changes are logged

---

### BRD-INTEL-005: Stopping Reason
**Priority**: P1  
**Description**: Final outputs MUST state why reasoning stopped.

**Acceptance Criteria**:
- [ ] Outputs include stop_reason field
- [ ] stop_reason is one of sufficient/budget_exhausted/missing_inputs/conflict

---

## Critique Requirements

### BRD-CRIT-001: Mandatory Critique
**Priority**: P0  
**Description**: A critique stage MUST run before final outputs.

**Acceptance Criteria**:
- [ ] Critique output exists for each run
- [ ] Final output references critique outcome

---

### BRD-CRIT-002: Evidence Checks
**Priority**: P0  
**Description**: Critique MUST identify missing or weak evidence.

**Acceptance Criteria**:
- [ ] Critique lists unsupported claims
- [ ] Evidence gaps are enumerated

---

### BRD-CRIT-003: Confidence Downgrade
**Priority**: P1  
**Description**: Critique MUST be able to downgrade confidence with reasons.

**Acceptance Criteria**:
- [ ] revised_confidence field present
- [ ] downgrade_reason populated when lowered

---

### BRD-CRIT-004: Advisory-Only Critique
**Priority**: P0  
**Description**: Critique MUST NOT execute tools or route flows.

**Acceptance Criteria**:
- [ ] Critique outputs are advisory only
- [ ] No tool invocations from critique stage

---

### BRD-CRIT-005: Blocking Findings
**Priority**: P0  
**Description**: Blocking critique findings MUST trigger clarification or abort.

**Acceptance Criteria**:
- [ ] blocking_required flag emitted
- [ ] Orchestrator transitions to ASK_USER or ABORT

---

## Advisory Tool Selection

### BRD-TOOLSEL-001: Advisory Recommendations
**Priority**: P1  
**Description**: Tool selection MUST be surfaced as advisory recommendations.

**Acceptance Criteria**:
- [ ] Tool recommendations listed explicitly
- [ ] Rationales included when available

---

### BRD-TOOLSEL-002: Ranked Suggestions
**Priority**: P2  
**Description**: Tool recommendations MAY be ranked with rationales.

**Acceptance Criteria**:
- [ ] Ranked list supported

---

### BRD-TOOLSEL-003: Orchestrator Authority
**Priority**: P0  
**Description**: Orchestrator MUST remain the sole authority for tool execution.

**Acceptance Criteria**:
- [ ] Tool execution not triggered by agent output

---

### BRD-TOOLSEL-004: No Forced Execution
**Priority**: P0  
**Description**: Advisory tool suggestions MUST NOT force execution.

**Acceptance Criteria**:
- [ ] Recommendations are optional

---

## Narrative Requirements

### BRD-NARR-004: Anomaly Interpretation
**Priority**: P1  
**Description**: Narrative SHOULD include anomaly interpretation when anomalies are present.

**Acceptance Criteria**:
- [ ] Narrative references anomalies where detected
- [ ] Context provided for anomaly significance

---

## Confidence Requirements

### BRD-CONF-005: Configurable Thresholds
**Priority**: P1  
**Description**: Confidence thresholds MUST be configurable.

**Acceptance Criteria**:
- [ ] Thresholds read from product config
- [ ] Default thresholds documented

---

## Platform Alignment

### BRD-ALIGN-001: Framework Primitives
**Priority**: P0  
**Description**: Product reasoning MUST rely on framework primitives.

**Acceptance Criteria**:
- [ ] No product-level orchestration re-implementation
- [ ] Uses core reasoning ladder interfaces

---

### BRD-ALIGN-002: Escalate Framework Gaps
**Priority**: P0  
**Description**: Requirements needing custom primitives MUST be escalated as framework gaps.

**Acceptance Criteria**:
- [ ] Gaps logged in product docs
- [ ] No workaround implementations in product code

---

## Framework Reliance

### BRD-FRI-001: No Shadow Orchestration
**Priority**: P0  
**Description**: Product MUST NOT re-implement orchestrator logic.

---

### BRD-FRI-002: No Shadow Iteration
**Priority**: P0  
**Description**: Product MUST NOT re-implement iteration control.

---

### BRD-FRI-003: No Shadow Reasoning
**Priority**: P0  
**Description**: Product MUST NOT re-implement reasoning ladder semantics.

---

### BRD-FRI-004: Governance Hooks Required
**Priority**: P0  
**Description**: Product MUST NOT bypass framework governance hooks.

---

### BRD-FRI-005: Escalate Gaps
**Priority**: P0  
**Description**: Framework gaps MUST be escalated, not worked around.

---

## No Runtime Learning

### BRD-NRL-001: No Runtime Behavior Changes
**Priority**: P0  
**Description**: Product MUST NOT modify behavior at runtime based on prior runs.

---

### BRD-NRL-002: No Persisted Learning
**Priority**: P0  
**Description**: Product MUST NOT persist learned patterns across runs.

---

### BRD-NRL-003: Governed Evolution Only
**Priority**: P0  
**Description**: Product evolution MUST follow intent → BRD → implementation lifecycle.

---

### BRD-NRL-004: Run Independence
**Priority**: P0  
**Description**: Identical inputs MUST produce identical outputs across runs.

---

## Cross-References

- **System Design**: [agents-and-tools.md](../04_systemdesign/agents-and-tools.md)
- **BRD**: [BRD-agents.md](../01_brd/BRD-agents.md)

---

# Semantic Interpretation Requirements

> **Prefix**: SEM-*  
> **Requirements**: ~30

---

## 8. ADESemanticAdapter (SEM-ADAPTER)

### SEM-ADAPTER-001: Implementation File
**Priority**: P0  
**Description**: ADESemanticAdapter MUST be implemented in `products/ade/semantic_adapter.py`.

**Acceptance Criteria**:
- [ ] File exists at `products/ade/semantic_adapter.py`
- [ ] Exports `ADESemanticAdapter` class
- [ ] Class conforms to core SemanticAdapter interface

---

### SEM-ADAPTER-002: Input Processing
**Priority**: P0  
**Description**: ADESemanticAdapter MUST process free-text input and return SemanticEnvelope.

**Signature**:
```python
def interpret(self, user_input: str, context: Optional[Dict] = None) -> SemanticEnvelope:
    ...
```

**Acceptance Criteria**:
- [ ] Accepts string user input
- [ ] Optional context dictionary for additional signals
- [ ] Returns valid SemanticEnvelope

---

### SEM-ADAPTER-003: SemanticEnvelope Output
**Priority**: P0  
**Description**: ADESemanticAdapter MUST output core-defined SemanticEnvelope schema.

**SemanticEnvelope Fields**:
```python
intent_type: str           # From ADE intent taxonomy
requested_outputs: List[str]
metrics: List[str]
time_scope: Optional[str]
constraints: Dict[str, Any]
confidence: float          # 0.0 - 1.0
raw_input: str
```

---

### SEM-ADAPTER-004: Intent Classification
**Priority**: P0  
**Description**: ADESemanticAdapter MUST classify input into ADE intent types.

**Acceptance Criteria**:
- [ ] Intent type is one of defined taxonomy values
- [ ] Classification uses keyword/pattern matching (no LLM)
- [ ] Classification is deterministic

---

### SEM-ADAPTER-005: Confidence Scoring
**Priority**: P0  
**Description**: ADESemanticAdapter MUST provide confidence score for interpretation.

**Acceptance Criteria**:
- [ ] confidence is float between 0.0 and 1.0
- [ ] Score reflects certainty of intent classification
- [ ] Score accounts for completeness of extracted fields

---

## 9. ADE Intent Taxonomy (SEM-INTENT)

### SEM-INTENT-001: Implementation File
**Priority**: P0  
**Description**: ADE intent taxonomy MUST be implemented in `products/ade/intents.py`.

**Acceptance Criteria**:
- [ ] File exists at `products/ade/intents.py`
- [ ] Exports `ADEIntentType` enum
- [ ] Exports `INTENT_REQUIREMENTS` mapping

---

### SEM-INTENT-002: Intent Type Enum
**Priority**: P0  
**Description**: ADEIntentType MUST define all supported intent types.

**Enum Values**:
```python
class ADEIntentType(str, Enum):
    DESCRIBE_DATA = "describe_data"
    COMPARE_PERIODS = "compare_periods"
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_REVIEW = "anomaly_review"
    OPEN_ENDED_ANALYSIS = "open_ended_analysis"
```

---

### SEM-INTENT-003: DESCRIBE_DATA Requirements
**Priority**: P0  
**Description**: DESCRIBE_DATA intent MUST have defined field requirements.

| Field | Required | Description |
|-------|----------|-------------|
| dataset | Yes | Dataset to describe |
| metrics | No | Specific metrics to focus on |
| time_scope | No | Optional time period |

---

### SEM-INTENT-004: COMPARE_PERIODS Requirements
**Priority**: P0  
**Description**: COMPARE_PERIODS intent MUST have defined field requirements.

| Field | Required | Description |
|-------|----------|-------------|
| dataset | Yes | Dataset to analyze |
| time_scope | Yes | Time periods to compare |
| metrics | No | Metrics for comparison |

---

### SEM-INTENT-005: TREND_ANALYSIS Requirements
**Priority**: P0  
**Description**: TREND_ANALYSIS intent MUST have defined field requirements.

| Field | Required | Description |
|-------|----------|-------------|
| dataset | Yes | Dataset to analyze |
| metrics | Yes | Metrics to trend |
| time_scope | Yes | Time range for trend |

---

### SEM-INTENT-006: ANOMALY_REVIEW Requirements
**Priority**: P0  
**Description**: ANOMALY_REVIEW intent MUST have defined field requirements.

| Field | Required | Description |
|-------|----------|-------------|
| dataset | Yes | Dataset to analyze |
| metrics | Yes | Metrics to check for anomalies |
| time_scope | No | Optional time scope |

---

### SEM-INTENT-007: OPEN_ENDED_ANALYSIS Requirements
**Priority**: P0  
**Description**: OPEN_ENDED_ANALYSIS intent MUST have defined field requirements.

| Field | Required | Description |
|-------|----------|-------------|
| dataset | Yes | Dataset to explore |
| metrics | No | Optional focus metrics |
| time_scope | No | Optional time scope |

---

### SEM-INTENT-008: Intent Requirements Mapping
**Priority**: P0  
**Description**: INTENT_REQUIREMENTS MUST map intent types to field requirements.

**Structure**:
```python
INTENT_REQUIREMENTS: Dict[ADEIntentType, IntentRequirements] = {
    ADEIntentType.DESCRIBE_DATA: IntentRequirements(
        required_fields=["dataset"],
        optional_fields=["metrics", "time_scope"]
    ),
    # ... other intents
}
```

---

## 10. Semantic Validation (SEM-VALIDATE)

### SEM-VALIDATE-001: Implementation File
**Priority**: P0  
**Description**: Semantic validation MUST be implemented in `products/ade/semantic_validation.py`.

**Acceptance Criteria**:
- [ ] File exists at `products/ade/semantic_validation.py`
- [ ] Exports `validate_semantic_envelope` function
- [ ] Exports `ValidationResult` schema

---

### SEM-VALIDATE-002: Validation Function Signature
**Priority**: P0  
**Description**: validate_semantic_envelope MUST have defined signature.

**Signature**:
```python
def validate_semantic_envelope(
    envelope: SemanticEnvelope,
    intent_type: ADEIntentType
) -> ValidationResult:
    ...
```

---

### SEM-VALIDATE-003: ValidationResult Schema
**Priority**: P0  
**Description**: ValidationResult MUST contain validation outcome fields.

**Fields**:
```python
class ValidationResult(BaseModel):
    is_valid: bool
    missing_fields: List[str]
    clarifying_question: Optional[str]
    confidence_adjustment: float
    outcome: Literal["PROCEED", "ASK_USER", "ABORT"]
```

---

### SEM-VALIDATE-004: ASK_USER Outcome
**Priority**: P0  
**Description**: Validation MUST return ASK_USER when clarification can resolve missing fields.

**Acceptance Criteria**:
- [ ] outcome = "ASK_USER" when missing_fields is non-empty
- [ ] clarifying_question is populated
- [ ] Flow pauses for user response

---

### SEM-VALIDATE-005: ABORT Outcome
**Priority**: P0  
**Description**: Validation MUST return ABORT when analysis cannot proceed.

**Acceptance Criteria**:
- [ ] outcome = "ABORT" when critical fields cannot be inferred
- [ ] No clarifying question is possible
- [ ] Flow terminates gracefully

---

### SEM-VALIDATE-006: PROCEED Outcome
**Priority**: P0  
**Description**: Validation MUST return PROCEED when envelope is complete.

**Acceptance Criteria**:
- [ ] outcome = "PROCEED" when all required fields present
- [ ] is_valid = True
- [ ] missing_fields is empty list

---

### SEM-VALIDATE-007: Confidence Adjustment
**Priority**: P1  
**Description**: ValidationResult MUST compute confidence_adjustment.

**Acceptance Criteria**:
- [ ] confidence_adjustment is float between -1.0 and 0.0
- [ ] Full completeness = 0.0 (no adjustment)
- [ ] Missing optional fields = -0.1 to -0.3
- [ ] Original confidence adjusted by this factor

---

## 11. Clarifying Question Templates (SEM-CLARIFY)

### SEM-CLARIFY-001: Implementation File
**Priority**: P0  
**Description**: Clarifying questions MUST be implemented in `products/ade/clarifying_questions.py`.

**Acceptance Criteria**:
- [ ] File exists at `products/ade/clarifying_questions.py`
- [ ] Exports `get_clarifying_question` function
- [ ] Exports `CLARIFYING_TEMPLATES` dictionary

---

### SEM-CLARIFY-002: Template Structure
**Priority**: P0  
**Description**: CLARIFYING_TEMPLATES MUST map missing fields to question templates.

**Structure**:
```python
CLARIFYING_TEMPLATES: Dict[str, str] = {
    "metrics": "Which specific metric would you like to focus on? (e.g., revenue, cost, volume)",
    "time_scope": "What time period should we analyze? (e.g., last 30 days, Q1 2024)",
    "anomaly_threshold": "What threshold should we use for anomaly detection? (default: 2.0 standard deviations)",
    # ... other fields
}
```

---

### SEM-CLARIFY-003: Metric Focus Template
**Priority**: P1  
**Description**: System MUST provide template for metric focus clarification.

**Template**:
```
"Which specific metric would you like to focus on? (e.g., revenue, cost, volume)"
```

**Acceptance Criteria**:
- [ ] Template is deterministic
- [ ] Provides examples for user guidance
- [ ] Supports customization per intent type

---

### SEM-CLARIFY-004: Time Range Template
**Priority**: P1  
**Description**: System MUST provide template for time range clarification.

**Template**:
```
"What time period should we analyze? (e.g., last 30 days, Q1 2024, YTD)"
```

---

### SEM-CLARIFY-005: Anomaly Preference Template
**Priority**: P1  
**Description**: System MUST provide template for anomaly preference clarification.

**Template**:
```
"What threshold should we use for anomaly detection? (default: 2.0 standard deviations)"
```

---

### SEM-CLARIFY-006: No LLM Generation
**Priority**: P0  
**Description**: Clarifying questions MUST NOT use LLM for generation.

**Acceptance Criteria**:
- [ ] All questions are from predefined templates
- [ ] No API calls to LLM services
- [ ] Questions are deterministic

---

## 12. Intent Router (SEM-ROUTER)

### SEM-ROUTER-001: Implementation File
**Priority**: P0  
**Description**: Intent router MUST be implemented in `products/ade/intent_router.py`.

**Acceptance Criteria**:
- [ ] File exists at `products/ade/intent_router.py`
- [ ] Exports `route_intent` function
- [ ] Exports `RouteResult` schema

---

### SEM-ROUTER-002: Router Function Signature
**Priority**: P0  
**Description**: route_intent MUST have defined signature.

**Signature**:
```python
def route_intent(envelope: SemanticEnvelope) -> RouteResult:
    ...
```

---

### SEM-ROUTER-003: RouteResult Schema
**Priority**: P0  
**Description**: RouteResult MUST contain routing outcome fields.

**Fields**:
```python
class RouteResult(BaseModel):
    flow_name: str
    initial_parameters: Dict[str, Any]
```

---

### SEM-ROUTER-004: Flow Routing Rules
**Priority**: P0  
**Description**: Router MUST use deterministic mapping from intent to flow.

**Routing Rules**:

| Intent Type | Flow Name | Initial Parameters |
|-------------|-----------|-------------------|
| DESCRIBE_DATA | visualization | dataset, intent_summary |
| COMPARE_PERIODS | ade_v1 | prompt, dataset, time_scope |
| TREND_ANALYSIS | ade_v1 | prompt, dataset, metrics |
| ANOMALY_REVIEW | ade_v1 | prompt, dataset, metrics |
| OPEN_ENDED_ANALYSIS | visualization | dataset |

---

### SEM-ROUTER-005: Parameter Mapping
**Priority**: P0  
**Description**: Router MUST map SemanticEnvelope fields to flow parameters.

**Acceptance Criteria**:
- [ ] All required flow parameters are populated
- [ ] Envelope fields are transformed to flow parameter format
- [ ] Dataset is always included in initial_parameters

---

## 13. Semantic Observability (SEM-OBS)

### SEM-OBS-001: Implementation File
**Priority**: P0  
**Description**: Semantic observability MUST be implemented in `products/ade/observability.py`.

**Acceptance Criteria**:
- [ ] File exists at `products/ade/observability.py`
- [ ] Exports `emit_semantic_trace` function
- [ ] Integrates with core observability hooks

---

### SEM-OBS-002: Trace Event Structure
**Priority**: P0  
**Description**: Semantic traces MUST extend core trace events with ADE fields.

**ADE Trace Fields**:
```python
ade_intent: str           # Intent type
ade_confidence: float     # Interpretation confidence
ade_missing_fields: Optional[List[str]]  # Fields requiring clarification
ade_clarifying_question: Optional[str]   # Generated question
```

---

### SEM-OBS-003: ade_intent Field
**Priority**: P0  
**Description**: Trace MUST include ade_intent field with intent type.

**Acceptance Criteria**:
- [ ] ade_intent is string from ADEIntentType enum
- [ ] Field is present on all semantic interpretation events
- [ ] Value matches classified intent

---

### SEM-OBS-004: ade_confidence Field
**Priority**: P0  
**Description**: Trace MUST include ade_confidence field with confidence score.

**Acceptance Criteria**:
- [ ] ade_confidence is float between 0.0 and 1.0
- [ ] Reflects final adjusted confidence
- [ ] Present on all semantic interpretation events

---

### SEM-OBS-005: ade_missing_fields Field
**Priority**: P1  
**Description**: Trace MUST include ade_missing_fields when validation detects gaps.

**Acceptance Criteria**:
- [ ] ade_missing_fields is List[str] of field names
- [ ] Only present when missing_fields is non-empty
- [ ] Omitted when all fields are present

---

### SEM-OBS-006: ade_clarifying_question Field
**Priority**: P1  
**Description**: Trace MUST include ade_clarifying_question when question is generated.

**Acceptance Criteria**:
- [ ] ade_clarifying_question is string with question text
- [ ] Only present when clarifying question is generated
- [ ] Omitted when no clarification needed

---

### SEM-OBS-007: Integration with Core Observability
**Priority**: P0  
**Description**: Semantic observability MUST integrate with core hooks.

**Acceptance Criteria**:
- [ ] Uses `core.governance.hooks` for event emission
- [ ] Follows core trace event schema
- [ ] ADE fields are in metadata.product_specific namespace
