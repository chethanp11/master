# ADE Schema Requirements

> **Document**: Technical Specification — Schemas  
> **Prefix**: SCHEMA-*  
> **Requirements**: ~20

---

## 1. General Schema Requirements (SCHEMA-GEN)

### SCHEMA-GEN-001: Pydantic Models
**Priority**: P0  
**Description**: All schemas MUST be Pydantic BaseModel classes.

**Acceptance Criteria**:
- [ ] All schemas inherit from BaseModel
- [ ] Type annotations are complete
- [ ] Models are importable

---

### SCHEMA-GEN-002: Extra Fields Forbidden
**Priority**: P0  
**Description**: All schemas MUST forbid extra fields.

**Acceptance Criteria**:
- [ ] `model_config = ConfigDict(extra="forbid")` on all models
- [ ] Unknown fields cause validation errors

---

### SCHEMA-GEN-003: Default Factories
**Priority**: P1  
**Description**: List and Dict fields MUST use Field(default_factory=...).

**Acceptance Criteria**:
- [ ] No mutable default arguments
- [ ] Lists use `default_factory=list`
- [ ] Dicts use `default_factory=dict`

---

## 2. DecisionPacket Schema (SCHEMA-DP)

### SCHEMA-DP-001: Required Fields
**Priority**: P0  
**Description**: DecisionPacket MUST have all required fields.

**Required Fields**:
```python
question: str
decision_summary: str
confidence_level: str
assumptions: List[str]
limitations: List[str]
sections: List[DecisionSection]
trace_refs: List[Dict[str, Any]]
```

---

### SCHEMA-DP-002: Optional Fields
**Priority**: P1  
**Description**: DecisionPacket MAY have optional fields.

**Optional Fields**:
```python
reasoning_narrative: Optional[str] = None
```

---

### SCHEMA-DP-003: Sections List
**Priority**: P0  
**Description**: DecisionPacket.sections MUST be List[DecisionSection].

**Acceptance Criteria**:
- [ ] Each section is valid DecisionSection
- [ ] Sections are ordered

---

## 3. DecisionSection Schema (SCHEMA-DS)

### SCHEMA-DS-001: Required Fields
**Priority**: P0  
**Description**: DecisionSection MUST have all required fields.

**Required Fields**:
```python
section_id: str
title: str
intent: str
narrative: str
claim_strength: str
visuals: List[Dict[str, Any]]
evidence_refs: List[Dict[str, Any]]
```

---

### SCHEMA-DS-002: Optional Fields
**Priority**: P1  
**Description**: DecisionSection MAY have optional fields.

**Optional Fields**:
```python
rejected_alternatives: Optional[List[str]] = None
```

---

### SCHEMA-DS-003: Claim Strength Values
**Priority**: P1  
**Description**: claim_strength MUST be standard value.

**Allowed Values**: "high", "medium", "low"

---

## 4. BusinessReport Schema (SCHEMA-BR)

### SCHEMA-BR-001: Required Fields
**Priority**: P0  
**Description**: BusinessReport MUST have all required fields.

**Required Fields**:
```python
title: str
generated_at_iso: str
dataset_id: str
row_count: int
period_labels: List[str]
series_count: int
executive_summary: List[str]
key_findings: List[Finding]
visuals: List[VisualSpec]
anomalies: List[AnomalyRow]
recommendations: List[str]
appendix: Appendix
```

---

### SCHEMA-BR-002: ISO Timestamp
**Priority**: P1  
**Description**: generated_at_iso MUST be valid ISO 8601 timestamp.

**Acceptance Criteria**:
- [ ] Format: YYYY-MM-DDTHH:MM:SSZ
- [ ] Timezone-aware or UTC

---

### SCHEMA-BR-003: Nested Schemas
**Priority**: P0  
**Description**: BusinessReport MUST use proper nested schemas.

**Nested Types**:
- [ ] key_findings: List[Finding]
- [ ] visuals: List[VisualSpec]
- [ ] anomalies: List[AnomalyRow]
- [ ] appendix: Appendix

---

## 5. Finding Schema (SCHEMA-FIND)

### SCHEMA-FIND-001: Required Fields
**Priority**: P0  
**Description**: Finding MUST have all required fields.

**Required Fields**:
```python
headline: str
value: str
context: str
```

---

### SCHEMA-FIND-002: Evidence References
**Priority**: P1  
**Description**: Finding.evidence_refs MUST use default_factory.

```python
evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)
```

---

## 6. VisualSpec Schema (SCHEMA-VS)

### SCHEMA-VS-001: Required Fields
**Priority**: P0  
**Description**: VisualSpec MUST have all required fields.

**Required Fields**:
```python
kind: Literal["line", "heatmap", "bar"]
title: str
```

---

### SCHEMA-VS-002: Kind Literal
**Priority**: P0  
**Description**: VisualSpec.kind MUST be Literal type.

**Allowed Values**: "line", "heatmap", "bar"

---

### SCHEMA-VS-003: Optional Data Fields
**Priority**: P1  
**Description**: VisualSpec.data and config MUST have defaults.

```python
data: Dict[str, Any] = Field(default_factory=dict)
config: Dict[str, Any] = Field(default_factory=dict)
```

---

## 7. AnomalyRow Schema (SCHEMA-AR)

### SCHEMA-AR-001: Required Fields
**Priority**: P0  
**Description**: AnomalyRow MUST have all required fields.

**Required Fields**:
```python
rank: int
expense: str
period: str
value: float
baseline: float
delta: float
reason: str
```

---

### SCHEMA-AR-002: Optional Fields
**Priority**: P1  
**Description**: AnomalyRow.delta_pct is optional.

```python
delta_pct: Optional[float] = None
```

---

## 8. IntentFrame Schema (SCHEMA-IF)

### SCHEMA-IF-001: Required Fields
**Priority**: P0  
**Description**: IntentFrame MUST have intent_summary as required.

**Required Fields**:
```python
intent_summary: str
```

---

### SCHEMA-IF-002: Default Values
**Priority**: P1  
**Description**: IntentFrame fields MUST have sensible defaults.

```python
inferred_entities: List[str] = Field(default_factory=list)
inferred_metrics: List[str] = Field(default_factory=list)
inferred_time_window: Optional[str] = None
requested_outputs: List[str] = Field(default_factory=list)
confidence_score: float = 0.0
confidence_label: str = "low"
blocking_required: bool = False
blocking_questions: List[str] = Field(default_factory=list)
blocking_question: Optional[str] = None
```

---

### SCHEMA-IF-003: Confidence Score Range
**Priority**: P1  
**Description**: confidence_score MUST be 0.0-1.0.

**Acceptance Criteria**:
- [ ] Values < 0.0 are invalid
- [ ] Values > 1.0 are invalid
- [ ] Default is 0.0

---

## 9. Appendix Schema (SCHEMA-APP)

### SCHEMA-APP-001: Required Fields
**Priority**: P0  
**Description**: Appendix MUST have confidence as required.

**Required Fields**:
```python
confidence: str
```

---

### SCHEMA-APP-002: Default Factories
**Priority**: P1  
**Description**: Appendix list fields MUST use default_factory.

```python
downgrade_reasons: List[str] = Field(default_factory=list)
trace_refs: List[Dict[str, Any]] = Field(default_factory=list)
assumptions: List[str] = Field(default_factory=list)
limitations: List[str] = Field(default_factory=list)
```

---

## Cross-References

- **System Design**: [schemas.md](../04_systemdesign/schemas.md)
- **BRD**: [BRD-data.md](../01_brd/BRD-data.md)
