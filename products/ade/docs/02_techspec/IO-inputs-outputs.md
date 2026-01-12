# ADE Input/Output Requirements

> **Document**: Technical Specification — Inputs and Outputs  
> **Prefix**: IO-*  
> **Requirements**: ~20

---

## 1. Input Payload Requirements (IO-IN)

### IO-IN-001: Dataset Required
**Priority**: P0  
**Description**: Payload MUST include dataset field.

**Acceptance Criteria**:
- [ ] dataset is required for both flows
- [ ] Missing dataset causes validation error
- [ ] Dataset name maps to CSV file

---

### IO-IN-002: ade_v1 Payload Schema
**Priority**: P0  
**Description**: ade_v1 MUST accept defined payload fields.

**Fields**:
```json
{
  "dataset": "required",
  "prompt": "optional",
  "intent": "optional",
  "question": "optional",
  "instructions": "optional"
}
```

---

### IO-IN-003: visualization Payload Schema
**Priority**: P0  
**Description**: visualization MUST accept defined payload fields.

**Fields**:
```json
{
  "dataset": "required",
  "prompt": "optional"
}
```

---

### IO-IN-004: Alternate Intent Fields
**Priority**: P1  
**Description**: ade_v1 MUST accept intent from multiple fields.

**Priority Order**:
1. `prompt` (primary)
2. `intent`
3. `question`
4. `instructions`

---

## 2. Dataset Requirements (IO-DATA)

### IO-DATA-001: CSV Format
**Priority**: P0  
**Description**: Datasets MUST be CSV format.

**Acceptance Criteria**:
- [ ] Standard CSV with comma delimiter
- [ ] First row is header
- [ ] UTF-8 encoding

---

### IO-DATA-002: Dataset Location
**Priority**: P0  
**Description**: Datasets MUST be in defined locations.

**Locations**:
- [ ] `products/ade/staging/input/` (user datasets)
- [ ] `products/ade/data/` (built-in datasets)

---

### IO-DATA-003: Built-in Dataset
**Priority**: P1  
**Description**: branded_cards_transactions MUST be available.

**Location**: `products/ade/data/branded_cards_transactions.csv`

---

### IO-DATA-004: Dataset Name Resolution
**Priority**: P0  
**Description**: Dataset names MUST resolve to file paths.

**Acceptance Criteria**:
- [ ] Name without extension maps to .csv file
- [ ] Case-sensitive matching
- [ ] Missing file causes clear error

---

## 3. User Input Requirements (IO-USER)

### IO-USER-001: viz_preferences Validation
**Priority**: P0  
**Description**: viz_preferences MUST validate against schema.

**Schema Properties**:
```json
{
  "chart_type": {"type": "string", "enum": ["bar", "line", "area", "scatter"]},
  "metric_focus": {"type": "string", "enum": ["mean", "sum", "median", "growth_rate", "anomalies"]},
  "include_hypothesis_checks": {"type": "boolean"},
  "notes": {"type": "string"}
}
```

---

### IO-USER-002: Required User Fields
**Priority**: P0  
**Description**: chart_type and metric_focus MUST be required.

**Acceptance Criteria**:
- [ ] Missing chart_type fails validation
- [ ] Missing metric_focus fails validation
- [ ] Defaults are applied if not provided

---

### IO-USER-003: Default Values
**Priority**: P1  
**Description**: User inputs MUST have defaults.

| Flow | chart_type | metric_focus | include_hypothesis_checks |
|------|------------|--------------|---------------------------|
| ade_v1 | bar | mean | true |
| visualization | bar | anomalies | true |

---

## 4. Output Requirements (IO-OUT)

### IO-OUT-001: Primary Outputs
**Priority**: P0  
**Description**: Flows MUST produce primary outputs.

**Required Outputs**:
- [ ] business_report.html
- [ ] decision_packet.html (visualization flow only)

---

### IO-OUT-002: Output Location
**Priority**: P0  
**Description**: Outputs MUST be written to staging/output/.

**Location**: `products/ade/staging/output/`

---

### IO-OUT-003: Valid HTML
**Priority**: P0  
**Description**: HTML outputs MUST be valid HTML5.

**Acceptance Criteria**:
- [ ] DOCTYPE declaration present
- [ ] Well-formed HTML structure
- [ ] No unclosed tags

---

### IO-OUT-004: Optional Exports
**Priority**: P2  
**Description**: export_pdf MAY produce additional outputs.

**Optional Outputs**:
- [ ] ade.pdf
- [ ] ade.html
- [ ] ade_stub.json

---

## 5. Evidence Requirements (IO-EVID)

### IO-EVID-001: Evidence References Required
**Priority**: P0  
**Description**: All claims MUST have evidence_refs.

**Acceptance Criteria**:
- [ ] DecisionSection has evidence_refs
- [ ] Finding has evidence_refs
- [ ] References are traceable

---

### IO-EVID-002: Evidence Reference Structure
**Priority**: P0  
**Description**: evidence_refs MUST include required fields.

**Required Fields**:
```python
{
  "dataset_id": str,
  "columns": List[str]
}
```

---

### IO-EVID-003: Trace References Required
**Priority**: P0  
**Description**: DecisionPacket MUST include trace_refs.

**Acceptance Criteria**:
- [ ] trace_refs includes step_id references
- [ ] trace_refs includes user_inputs
- [ ] All referenced steps exist

---

### IO-EVID-004: Evidence Items
**Priority**: P1  
**Description**: Tools MUST produce evidence_items.

**Tools Producing Evidence Items**:
- [ ] compute_business_metrics
- [ ] detect_anomalies
- [ ] hypothesis_test_data_outage
- [ ] hypothesis_test_seasonality

---

## 6. Artifact Reference Requirements (IO-ARTF)

### IO-ARTF-001: Tool Output Syntax
**Priority**: P0  
**Description**: Tool outputs MUST be referenceable.

**Syntax**: `{{artifacts.tool.<tool_name>.output.<field>}}`

---

### IO-ARTF-002: User Input Syntax
**Priority**: P0  
**Description**: User inputs MUST be referenceable.

**Syntax**: `{{artifacts.user_input.<form_id>.values.<field>}}`

---

### IO-ARTF-003: Agent Output Syntax
**Priority**: P0  
**Description**: Agent outputs MUST be referenceable.

**Syntax**: `{{artifacts.agent.<agent_name>.output.<field>}}`

---

### IO-ARTF-004: Payload Syntax
**Priority**: P0  
**Description**: Payload fields MUST be referenceable.

**Syntax**: `{{payload.<field>}}`

---

### IO-ARTF-005: Reference Resolution
**Priority**: P0  
**Description**: All artifact references MUST resolve at runtime.

**Acceptance Criteria**:
- [ ] Missing references cause clear errors
- [ ] Resolved values are correct types
- [ ] Nested references are supported

---

## Cross-References

- **System Design**: [inputs-and-outputs.md](../04_systemdesign/inputs-and-outputs.md)
- **BRD**: [BRD-data.md](../01_brd/BRD-data.md), [BRD-outputs.md](../01_brd/BRD-outputs.md)
