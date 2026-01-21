# ADE Data Schemas

> **Document**: System Design — Schemas  
> **Version**: 1.1.0  
> **Last Updated**: 2026-01-21

---

## 1. Overview

ADE uses Pydantic models for all data structures. All models use `ConfigDict(extra="forbid")` for strict validation.

Location: `products/ade/schemas/`

---

## 2. Core Schemas

### 2.1 DecisionPacket

The primary decision output structure for audit and review.

**Location**: `products/ade/schemas/decision_packet.py`

```python
class DecisionPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: str                      # "finalize"
    question: str                    # Original analyst question
    decision_summary: str            # Summary of the decision
    confidence_level: str            # "high", "medium", "low"
    assumptions: List[str]           # Explicit assumptions made
    limitations: List[str]           # Known limitations
    sections: List[DecisionSection]  # Decision sections with evidence
    trace_refs: List[Dict[str, Any]] # References to execution trace
    reasoning_narrative: Optional[str] = None
    stop_reason: str                 # "sufficient" or "missing_inputs"
    version_metadata: Optional[VersionMetadata] = None
```

**Evidence**:
- `products/ade/schemas/evidence.py` (`TrendEvidence`, `OutlierEvidence`, `DataQualityEvidence`, `HypothesisEvidence`)

**Usage**: Primary output of `assemble_decision_packet` tool.

**Evidence**:
- `products/ade/schemas/decision_packet.py` (`DecisionPacket.stop_reason`, `DecisionPacket.version_metadata`)

---

### 2.2 DecisionSection

A section within a DecisionPacket containing evidence and claims.

**Location**: `products/ade/schemas/decision_section.py`

```python
class DecisionSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: str                  # Unique section identifier
    title: str                       # Section title
    intent: str                      # Section purpose
    narrative: str                   # Explanatory narrative
    claim_strength: str              # "high", "medium", "low"
    visuals: List[Dict[str, Any]]    # Chart specs and tables
    evidence_refs: List[Dict[str, Any]]  # Evidence references
    rejected_alternatives: Optional[List[str]] = None
```

---

### 2.3 BusinessReport

The primary stakeholder report structure.

**Location**: `products/ade/schemas/business_report.py`

```python
class BusinessReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: str = "finalize"
    title: str
    generated_at_iso: str            # ISO timestamp
    dataset_id: str                  # Source dataset
    row_count: int                   # Number of data rows
    period_labels: List[str]         # Time period labels
    series_count: int                # Number of data series
    executive_summary: List[str]     # Summary bullet points
    key_findings: List[Finding]      # Key findings with evidence
    visuals: List[VisualSpec]        # Chart specifications
    anomalies: List[AnomalyRow]      # Detected anomalies
    recommendations: List[str]       # Actionable recommendations
    appendix: Appendix               # Supporting details
    stop_reason: str
    version_metadata: Optional[VersionMetadata] = None
```

---

**Evidence**:
- `products/ade/schemas/business_report.py` (`BusinessReport.stop_reason`, `BusinessReport.version_metadata`)

### 2.4 Finding

A key finding within a BusinessReport.

**Location**: `products/ade/schemas/business_report.py`

```python
class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    headline: str                    # Short headline
    value: str                       # Key value/metric
    context: str                     # Explanatory context
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)
```

---

### 2.5 VisualSpec

Chart specification for rendering.

**Location**: `products/ade/schemas/business_report.py`

```python
class VisualSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["line", "heatmap", "bar"]  # Chart type
    title: str
    data: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
```

---

### 2.6 AnomalyRow

A detected anomaly in the dataset.

**Location**: `products/ade/schemas/business_report.py`

```python
class AnomalyRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int                        # Severity rank
    expense: str                     # Category/expense name
    period: str                      # Time period
    value: float                     # Observed value
    baseline: float                  # Expected baseline
    delta: float                     # Absolute deviation
    delta_pct: Optional[float] = None  # Percentage deviation
    reason: str                      # Explanation
```

---

### 2.7 Appendix

Supporting details for a BusinessReport.

**Location**: `products/ade/schemas/business_report.py`

```python
class Appendix(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confidence: str                  # Overall confidence level
    downgrade_reasons: List[str] = Field(default_factory=list)
    trace_refs: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
```

---

### 2.8 IntentFrame

Parsed user intent from intent_agent.

**Location**: `products/ade/schemas/intent_frame.py`

```python
class IntentFrame(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: str                       # "interpret"
    intent_summary: str              # Summary of user intent
    inferred_entities: List[str] = Field(default_factory=list)
    inferred_metrics: List[str] = Field(default_factory=list)
    inferred_time_window: Optional[str] = None
    requested_outputs: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    confidence_label: str = "low"    # "low", "medium", "high"
    blocking_required: bool = False  # Whether clarification needed
    blocking_questions: List[str] = Field(default_factory=list)
    blocking_question: Optional[str] = None
```

---

**Evidence**:
- `products/ade/schemas/intent_frame.py` (`IntentFrame.stage`)

### 2.9 PlanSpec

Execution plan specification.

**Location**: `products/ade/schemas/plan_spec.py`

```python
class ToolRecommendation(BaseModel):
    tool: str
    rationale: str
    optional: bool = True

class PlanSpec(BaseModel):
    stage: str = "propose"
    plan_summary: str
    tool_flags: Dict[str, bool]
    tool_recommendations: List[ToolRecommendation]
```

**Evidence**:
- `products/ade/schemas/plan_spec.py` (`ToolRecommendation`, `PlanSpec.tool_recommendations`)

---

## 3. Evidence Schemas

### 3.1 Evidence Items

Evidence item with provenance tracking.

**Location**: `products/ade/schemas/evidence.py`

```python
class EvidenceItemBase(BaseModel):
    evidence_id: str
    kind: str
    tool_step_id: str
    dataset_id: str
    created_at_iso: str
    inputs_hash: str
    # TS-SCHEMA-EVITEM-001: confidence field
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    # TS-SCHEMA-EVITEM-002: values field for extracted values
    values: Dict[str, Any] = Field(default_factory=dict)
    # TS-SCHEMA-CTX-004: columns for column references
    columns: List[str] = Field(default_factory=list)

class TrendEvidence(EvidenceItemBase):
    kind: Literal["trend"]
    period_labels: List[str]
    totals: List[Dict[str, Any]]
    means: List[Dict[str, Any]]
    top_movers_abs: List[Dict[str, Any]]
    top_movers_pct: List[Dict[str, Any]]

class OutlierEvidence(EvidenceItemBase):
    kind: Literal["outlier"]
    candidates: List[Dict[str, Any]]
    method: str = "iqr"

class DataQualityEvidence(EvidenceItemBase):
    kind: Literal["data_quality"]
    row_count: int
    deduped_row_count: int
    duplicate_count: int

class HypothesisEvidence(EvidenceItemBase):
    kind: Literal["hypothesis"]
    hypothesis_name: str
    status: str
    reasoning: str
```

---

### 3.2 Citations

Citation references for evidence.

**Location**: `products/ade/schemas/citations.py`

---

## 4. Visualization Schemas

### 4.1 Card / InsightCard

Standalone insight card structure.

**Location**: `products/ade/schemas/card.py`

---

### 4.2 Slices

Data slicing specifications.

**Location**: `products/ade/schemas/slices.py`

---

## 5. Schema Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                     BusinessReport                          │
│  ├── key_findings: List[Finding]                           │
│  ├── visuals: List[VisualSpec]                             │
│  ├── anomalies: List[AnomalyRow]                           │
│  └── appendix: Appendix                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ references
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DecisionPacket                          │
│  ├── sections: List[DecisionSection]                       │
│  │     ├── visuals: List[Dict]                             │
│  │     └── evidence_refs: List[Dict]                       │
│  └── trace_refs: List[Dict]                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ populated by
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     IntentFrame                             │
│  (input from intent_agent)                                  │
└─────────────────────────────────────────────────────────────┘

---

## 6. Context Pack Schema

**Location**: `products/ade/schemas/context_pack.py`

```python
class ContextPack(BaseModel):
    dataset_profile: Dict[str, Any]
    coverage: Dict[str, Any]
    missingness: Dict[str, Any]
    data_quality_flags: List[str]
    metric_availability: List[str]
    evidence_refs: List[Dict[str, Any]]
    # TS-SCHEMA-CTX-004: Evidence items with dataset_id/columns
    evidence_items: List[ContextPackEvidenceItem] = Field(default_factory=list)
    # TS-SCHEMA-CTX-005: Context pack ID for traceability
    context_pack_id: Optional[str] = None
```

**ContextPackEvidenceItem** (TS-SCHEMA-CTX-004):
```python
class ContextPackEvidenceItem(BaseModel):
    dataset_id: str
    columns: List[str] = Field(default_factory=list)
    source: str = ""
    description: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
```

**Evidence**:
- `products/ade/schemas/context_pack.py` (`ContextPack`)

---

## 7. Version Metadata Schema

**Location**: `products/ade/schemas/version_metadata.py`

```python
class VersionMetadata(BaseModel):
    product: str
    product_version: str
    flow_id: str
    flow_version: str
    schema_version: str
    dataset_hash: str
    input_hash: str
    dependency_versions: Dict[str, str]
```

**Evidence**:
- `products/ade/schemas/version_metadata.py` (`VersionMetadata`)
```

---

## 8. Validation Rules

All schemas enforce:

| Rule | Implementation |
|------|----------------|
| **No extra fields** | `ConfigDict(extra="forbid")` |
| **Type checking** | Pydantic type annotations |
| **Default factories** | `Field(default_factory=list)` for lists |
| **Optional fields** | `Optional[T] = None` pattern |
| **Literal constraints** | `Literal["value1", "value2"]` for enums |

---

## 9. Terminal Outcome Schemas (TS-AGENT-TERM-*)

**Location**: `products/ade/schemas/terminal_outcome.py`

### 9.1 TerminalOutcome Enum (TS-AGENT-TERM-001)

```python
class TerminalOutcome(str, Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    ASK_USER = "ask_user"
    ABORT = "abort"
```

### 9.2 PartialSuccessDetails (TS-AGENT-TERM-002)

```python
class PartialSuccessDetails(BaseModel):
    completed_steps: List[str] = Field(default_factory=list)
    missing_steps: List[str] = Field(default_factory=list)
    reason: str = ""
```

### 9.3 TerminalArtifact (TS-AGENT-TERM-003)

```python
class TerminalArtifact(BaseModel):
    explanation: str = ""
    supporting_refs: List[str] = Field(default_factory=list)
    confidence: str = "medium"
```

### 9.4 RunResult

```python
class RunResult(BaseModel):
    run_id: str
    outcome: TerminalOutcome = TerminalOutcome.SUCCESS
    partial_details: Optional[PartialSuccessDetails] = None
    terminal_artifact: Dict[str, Any] = Field(default_factory=dict)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
```

**Evidence**:
- `products/ade/schemas/terminal_outcome.py` (`TerminalOutcome`, `PartialSuccessDetails`, `TerminalArtifact`, `RunResult`)

---

## 10. Confidence Configuration Schema (TS-AGENT-CONF-003)

**Location**: `products/ade/config/confidence.yaml`, `products/ade/utils/confidence.py`

### 10.1 ConfidenceConfig

```python
class ConfidenceConfig(BaseModel):
    low_threshold: float = 0.4
    high_threshold: float = 0.7
    sufficiency_thresholds: SufficiencyThresholds

class SufficiencyThresholds(BaseModel):
    min_rows: int = 30
    critical_rows: int = 15
    min_time_points: int = 12
    max_cv: float = 0.6
    min_non_null_rate: float = 0.7
```

**Evidence**:
- `products/ade/config/confidence.yaml`
- `products/ade/utils/confidence.py` (`ConfidenceConfig`, `SufficiencyThresholds`, `load_confidence_config`)

---

## Cross-References

- [architecture.md](architecture.md) — Component overview
- [agents-and-tools.md](agents-and-tools.md) — Tools that produce these schemas
- [inputs-and-outputs.md](inputs-and-outputs.md) — How schemas flow through the system
