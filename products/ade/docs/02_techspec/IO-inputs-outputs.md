# ADE Input/Output Requirements

> **Document**: Technical Specification — Inputs and Outputs  
> **Prefix**: IO-*  
> **Requirements**: ~20

---

## Product Objectives

### OBJ-001: Evidence References
**Priority**: P0  
**Description**: 100% of outputs MUST include evidence references.

---

### OBJ-002: Reproducibility
**Priority**: P0  
**Description**: Same inputs MUST always produce same outputs.

---

### OBJ-003: Plan Approval
**Priority**: P0  
**Description**: All plans MUST require explicit user approval.

---

### OBJ-004: Transparency Fields
**Priority**: P0  
**Description**: Outputs MUST include confidence_level, assumptions, and limitations.

---

### OBJ-005: Time-to-Report
**Priority**: P1  
**Description**: Time from question to report SHOULD be under 5 minutes.

---

### OBJ-006: Chart Types
**Priority**: P1  
**Description**: At least 4 chart types MUST be available.

---

### OBJ-007: Hypothesis Toggle
**Priority**: P1  
**Description**: Hypothesis checks MUST be toggleable.

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

## 4.1 Output Quality Requirements

### BRD-QUAL-001: Executive Summary Quality
**Priority**: P0  
**Description**: Executive summary MUST be meaningful.

**Acceptance Criteria**:
- [ ] Executive summary is non-empty
- [ ] Summary reflects key findings

---

### BRD-QUAL-002: Actionable Key Findings
**Priority**: P0  
**Description**: Key findings MUST be actionable.

**Acceptance Criteria**:
- [ ] Findings include implications
- [ ] Findings map to evidence

---

### BRD-QUAL-003: Specific Recommendations
**Priority**: P1  
**Description**: Recommendations MUST be specific when present.

**Acceptance Criteria**:
- [ ] Recommendations include concrete actions

---

### BRD-QUAL-004: Human-Readable Narratives
**Priority**: P0  
**Description**: Narratives MUST be human-readable.

**Acceptance Criteria**:
- [ ] Plain-language text
- [ ] Avoids raw data dumps

---

### BRD-QUAL-010: Chart Rendering
**Priority**: P0  
**Description**: Charts MUST render correctly.

**Acceptance Criteria**:
- [ ] Vega-Lite spec validates

---

### BRD-QUAL-011: Table Readability
**Priority**: P0  
**Description**: Tables MUST be readable.

**Acceptance Criteria**:
- [ ] Column headers visible
- [ ] No overflow clipping

---

### BRD-QUAL-012: Browser Compatibility
**Priority**: P0  
**Description**: HTML MUST display in modern browsers.

**Acceptance Criteria**:
- [ ] Renders in Chrome/Firefox/Safari

---

## 4.2 Version Transparency Requirements

### BRD-VER-001: Output Version Metadata
**Priority**: P0  
**Description**: Outputs MUST include product, flow, and schema versions.

**Acceptance Criteria**:
- [ ] Version metadata present in output payload

---

### BRD-VER-002: Input Hashing
**Priority**: P1  
**Description**: Outputs MUST record dataset hash and input parameter hash.

**Acceptance Criteria**:
- [ ] dataset_hash present
- [ ] input_hash present

---

### BRD-VER-003: Dependency Pinning
**Priority**: P0  
**Description**: Non-deterministic dependencies MUST be version-pinned or disallowed.

**Acceptance Criteria**:
- [ ] Dependency versions recorded
- [ ] Non-pinned dependencies rejected

---

## 4.3 Decision Authority Boundary

### BRD-DAB-001: Recommendation Labeling
**Priority**: P0  
**Description**: Outputs MUST be labeled as recommendations/findings, not decisions.

**Acceptance Criteria**:
- [ ] Output labels avoid \"decision\" language

---

### BRD-DAB-002: Human Authority
**Priority**: P0  
**Description**: Decision packets MUST clarify human authority for final decisions.

**Acceptance Criteria**:
- [ ] Human authority statement included

---

### BRD-DAB-003: No Automatic Actions
**Priority**: P0  
**Description**: Outputs MUST NOT trigger downstream actions without explicit approval.

**Acceptance Criteria**:
- [ ] Outputs marked as advisory-only

---

### BRD-DAB-004: Confidence Language
**Priority**: P1  
**Description**: Confidence language MUST avoid implying autonomous decisions.

**Acceptance Criteria**:
- [ ] Language uses recommendation framing

---

### BRD-DAB-005: Advisory Presentation
**Priority**: P0  
**Description**: Recommendations MUST be presented as advisory.

**Acceptance Criteria**:
- [ ] Recommendation section labeled advisory

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
