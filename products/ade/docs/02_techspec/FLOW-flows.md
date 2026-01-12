# ADE Flow Requirements

> **Document**: Technical Specification — Flows  
> **Prefix**: FLOW-*  
> **Requirements**: ~25

---

## 1. Flow Execution (FLOW-EXEC)

### FLOW-EXEC-001: Deterministic Execution
**Priority**: P0  
**Description**: Flows MUST execute deterministically — same inputs produce same outputs.

**Acceptance Criteria**:
- [ ] Running a flow twice with identical payload produces identical artifacts
- [ ] No random or time-based variations in tool outputs
- [ ] Timestamps are the only allowed variation

---

### FLOW-EXEC-002: Step Sequence
**Priority**: P0  
**Description**: Flow steps MUST execute in the defined sequence.

**Acceptance Criteria**:
- [ ] Steps execute in YAML-defined order
- [ ] No step executes before its dependencies complete
- [ ] Artifact references resolve to prior step outputs

---

### FLOW-EXEC-003: Autonomy Level
**Priority**: P1  
**Description**: All ADE flows MUST use `autonomy_level: "suggest_only"`.

**Acceptance Criteria**:
- [ ] ade_v1 has autonomy_level: suggest_only
- [ ] visualization has autonomy_level: suggest_only
- [ ] Plan approval is required before execution proceeds

---

## 2. ade_v1 Flow (FLOW-V1)

### FLOW-V1-001: Step Count
**Priority**: P1  
**Description**: ade_v1 flow MUST have exactly 13 steps.

**Acceptance Criteria**:
- [ ] Step count matches flow definition
- [ ] All required steps are present

---

### FLOW-V1-002: Required Steps
**Priority**: P0  
**Description**: ade_v1 MUST include the following steps.

| Step ID | Type | Component |
|---------|------|-----------|
| read | tool | data_reader |
| viz_preferences | user_input | — |
| compute_business_metrics | tool | compute_business_metrics |
| sufficiency_eval | agent | sufficiency_evaluator |
| plan_proposal | plan_proposal | plan_proposal_agent |
| compute_anomalies | tool | detect_anomalies |
| build_chart_spec | tool | build_chart_spec |
| hypothesis_data_outage | tool | hypothesis_test_data_outage |
| hypothesis_seasonality | tool | hypothesis_test_seasonality |
| assemble_decision_packet | tool | assemble_decision_packet |
| assemble_evidence_bundle | tool | assemble_evidence_bundle |
| assemble_business_report | tool | assemble_business_report |
| render_business_report_html | tool | render_business_report_html |

---

### FLOW-V1-003: Data Reader First
**Priority**: P0  
**Description**: data_reader MUST execute before any computation steps.

**Acceptance Criteria**:
- [ ] data_reader is step 1
- [ ] All subsequent steps can reference data_reader output

---

### FLOW-V1-004: User Input Before Computation
**Priority**: P1  
**Description**: viz_preferences MUST execute after data_reader and before compute_business_metrics.

**Acceptance Criteria**:
- [ ] User can see dataset summary before selecting preferences
- [ ] Preferences are available for metric computation

---

### FLOW-V1-005: Plan Approval Gate
**Priority**: P0  
**Description**: plan_proposal MUST execute before hypothesis and assembly steps.

**Acceptance Criteria**:
- [ ] Execution pauses at plan_proposal for user approval
- [ ] Rejection triggers appropriate error handling
- [ ] Approval proceeds to remaining steps

---

## 3. visualization Flow (FLOW-VIZ)

### FLOW-VIZ-001: Step Count
**Priority**: P1  
**Description**: visualization flow MUST have exactly 15 steps.

---

### FLOW-VIZ-002: Intent First
**Priority**: P0  
**Description**: visualization flow MUST start with intent_interpretation agent step.

**Acceptance Criteria**:
- [ ] planning_agent executes as first step
- [ ] Intent interpretation happens before data reading

---

### FLOW-VIZ-003: Dual Planning
**Priority**: P1  
**Description**: visualization flow MUST use planning_agent twice.

**Acceptance Criteria**:
- [ ] First use: intent_interpretation (step 1)
- [ ] Second use: planning (step 6, after sufficiency_eval)

---

### FLOW-VIZ-004: Decision Packet HTML
**Priority**: P1  
**Description**: visualization flow MUST render decision_packet.html.

**Acceptance Criteria**:
- [ ] render_decision_packet_html step is present
- [ ] decision_packet.html is produced

---

## 4. User Input Steps (FLOW-INPUT)

### FLOW-INPUT-001: viz_preferences Schema
**Priority**: P0  
**Description**: viz_preferences MUST validate against defined schema.

**Schema**:
```yaml
properties:
  chart_type:
    type: string
    enum: [bar, line, area, scatter]
  metric_focus:
    type: string
    enum: [mean, sum, median, growth_rate, anomalies]
  include_hypothesis_checks:
    type: boolean
  notes:
    type: string
```

---

### FLOW-INPUT-002: Required Fields
**Priority**: P0  
**Description**: viz_preferences MUST require chart_type and metric_focus.

**Acceptance Criteria**:
- [ ] Step fails validation without chart_type
- [ ] Step fails validation without metric_focus
- [ ] include_hypothesis_checks and notes are optional

---

### FLOW-INPUT-003: Default Values
**Priority**: P1  
**Description**: viz_preferences MUST provide sensible defaults.

| Field | ade_v1 Default | visualization Default |
|-------|----------------|----------------------|
| chart_type | bar | bar |
| metric_focus | mean | anomalies |
| include_hypothesis_checks | true | true |
| notes | "" | "" |

---

## 5. Conditional Execution (FLOW-COND)

### FLOW-COND-001: Hypothesis Toggle
**Priority**: P1  
**Description**: Hypothesis tests MUST respect include_hypothesis_checks flag.

**Acceptance Criteria**:
- [ ] When false, hypothesis tools return status: "skipped"
- [ ] When true, hypothesis tools execute normally
- [ ] Skipped tools still produce valid output structure

---

### FLOW-COND-002: Enabled Parameter
**Priority**: P1  
**Description**: Hypothesis tools MUST receive enabled parameter from user input.

```yaml
params:
  enabled: "{{artifacts.user_input.viz_preferences.values.include_hypothesis_checks}}"
```

---

## 6. Error Handling (FLOW-ERR)

### FLOW-ERR-001: Retry Configuration
**Priority**: P1  
**Description**: data_reader step MUST have retry configuration.

```yaml
retry:
  max_attempts: 2
  backoff_seconds: 1
```

---

### FLOW-ERR-002: Fallback Chart Type
**Priority**: P1  
**Description**: build_chart_spec MUST use fallback when user selection is incompatible.

**Acceptance Criteria**:
- [ ] fallback_chart_type: "bar" is configured
- [ ] Incompatible selections fall back gracefully

---

## 7. Artifact References (FLOW-ARTF)

### FLOW-ARTF-001: Tool Output Reference
**Priority**: P0  
**Description**: Tool outputs MUST be referenceable via artifact path.

**Syntax**: `{{artifacts.tool.<tool_name>.output.<field>}}`

---

### FLOW-ARTF-002: User Input Reference
**Priority**: P0  
**Description**: User inputs MUST be referenceable via artifact path.

**Syntax**: `{{artifacts.user_input.<form_id>.values.<field>}}`

---

### FLOW-ARTF-003: Agent Output Reference
**Priority**: P0  
**Description**: Agent outputs MUST be referenceable via artifact path.

**Syntax**: `{{artifacts.agent.<agent_name>.output.<field>}}`

---

### FLOW-ARTF-004: Payload Reference
**Priority**: P0  
**Description**: Payload fields MUST be referenceable directly.

**Syntax**: `{{payload.<field>}}`

---

## Cross-References

- **System Design**: [flows.md](../04_systemdesign/flows.md)
- **BRD**: [BRD-flows.md](../01_brd/BRD-flows.md)
