# ADE Data Schemas

> **Document**: System Design — Schemas  
> **Version**: 1.0.0

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

    question: str                    # Original analyst question
    decision_summary: str            # Summary of the decision
    confidence_level: str            # "high", "medium", "low"
    assumptions: List[str]           # Explicit assumptions made
    limitations: List[str]           # Known limitations
    sections: List[DecisionSection]  # Decision sections with evidence
    trace_refs: List[Dict[str, Any]] # References to execution trace
    reasoning_narrative: Optional[str] = None
```

**Usage**: Primary output of `assemble_decision_packet` tool.

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
```

---

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

### 2.9 PlanSpec

Execution plan specification.

**Location**: `products/ade/schemas/plan_spec.py`

Contains deterministic plan specification with tool flags for conditional execution.

---

## 3. Evidence Schemas

### 3.1 Evidence / EvidenceItem

Evidence item with provenance tracking.

**Location**: `products/ade/schemas/evidence.py`

```python
class EvidenceItem(BaseModel):
    evidence_type: str               # "metric", "anomaly", "hypothesis"
    source: str                      # Source tool/step
    value: Any                       # Evidence value
    confidence: float                # Confidence score
    provenance: Dict[str, Any]       # Provenance metadata
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
```

---

## 6. Validation Rules

All schemas enforce:

| Rule | Implementation |
|------|----------------|
| **No extra fields** | `ConfigDict(extra="forbid")` |
| **Type checking** | Pydantic type annotations |
| **Default factories** | `Field(default_factory=list)` for lists |
| **Optional fields** | `Optional[T] = None` pattern |
| **Literal constraints** | `Literal["value1", "value2"]` for enums |

---

## Cross-References

- [architecture.md](architecture.md) — Component overview
- [agents-and-tools.md](agents-and-tools.md) — Tools that produce these schemas
- [inputs-and-outputs.md](inputs-and-outputs.md) — How schemas flow through the system
