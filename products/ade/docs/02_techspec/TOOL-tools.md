# ADE Tool Requirements

> **Document**: Technical Specification — Tools  
> **Prefix**: TOOL-*  
> **Requirements**: ~35

---

## 1. General Tool Requirements (TOOL-GEN)

### TOOL-GEN-001: No LLM Calls
**Priority**: P0  
**Description**: ADE tools MUST NOT call LLMs directly.

**Acceptance Criteria**:
- [ ] No tool imports LLM client libraries
- [ ] No tool makes API calls to LLM services
- [ ] All computation is deterministic

---

### TOOL-GEN-002: Tool Descriptors
**Priority**: P0  
**Description**: All tools MUST have descriptors in `products/ade/descriptors.py`.

**Acceptance Criteria**:
- [ ] ToolDescriptor exists for each tool
- [ ] Descriptor includes capabilities, sensitivity, cost_hint
- [ ] TOOL_DESCRIPTORS map exports all descriptors

---

### TOOL-GEN-003: Side Effect Declaration
**Priority**: P0  
**Description**: Tools MUST accurately declare side_effect status.

| Tool | Side Effect |
|------|-------------|
| export_pdf | Yes |
| (all others) | No |

---

### TOOL-GEN-004: Read-Only Declaration
**Priority**: P0  
**Description**: Tools MUST accurately declare read_only status.

**Acceptance Criteria**:
- [ ] export_pdf: read_only = False
- [ ] All other tools: read_only = True

---

## 2. Data Tools (TOOL-DATA)

### TOOL-DATA-001: data_reader Output
**Priority**: P0  
**Description**: data_reader MUST output standardized structure.

**Output Fields**:
```python
columns: List[str]
rows: List[Dict]
series: Dict
data: Dict
x_field: str
y_field: str
category_field: str
```

---

### TOOL-DATA-002: CSV Parsing
**Priority**: P0  
**Description**: data_reader MUST parse CSV files correctly.

**Acceptance Criteria**:
- [ ] Handles UTF-8 encoding
- [ ] Parses headers correctly
- [ ] Handles quoted fields
- [ ] Handles empty values

---

### TOOL-DATA-003: Field Inference
**Priority**: P1  
**Description**: data_reader MUST infer x_field, y_field, category_field.

**Acceptance Criteria**:
- [ ] Time columns detected as x_field
- [ ] Numeric columns detected as y_field
- [ ] Categorical columns detected as category_field

---

### TOOL-DATA-004: compute_business_metrics Output
**Priority**: P0  
**Description**: compute_business_metrics MUST output metrics structure.

**Output Fields**:
```python
totals: Dict
movers: List
anomalies: List
evidence_items: List[EvidenceItem]
```

---

### TOOL-DATA-005: Metric Focus
**Priority**: P1  
**Description**: compute_business_metrics MUST respect metric_focus parameter.

| metric_focus | Aggregation |
|--------------|-------------|
| mean | Average values |
| sum | Total values |
| median | Median values |
| growth_rate | Period-over-period change |
| anomalies | Outlier detection |

---

## 3. Analysis Tools (TOOL-ANALYSIS)

### TOOL-ANALYSIS-001: detect_anomalies Algorithm
**Priority**: P0  
**Description**: detect_anomalies MUST use z-score analysis.

**Acceptance Criteria**:
- [ ] Z-score threshold is configurable
- [ ] Returns anomalies exceeding threshold
- [ ] Respects min_points parameter

---

### TOOL-ANALYSIS-002: detect_anomalies Output
**Priority**: P0  
**Description**: detect_anomalies MUST output AnomalyRow list.

**Output Fields**:
```python
anomalies: List[AnomalyRow]
evidence_items: List[EvidenceItem]
```

---

### TOOL-ANALYSIS-003: Hypothesis Tool Output
**Priority**: P0  
**Description**: Hypothesis tools MUST output standard structure.

**Output Fields**:
```python
status: str  # "confirmed", "rejected", "skipped"
reasoning: str
evidence_items: List[EvidenceItem]
```

---

### TOOL-ANALYSIS-004: hypothesis_test_data_outage
**Priority**: P1  
**Description**: hypothesis_test_data_outage MUST check for outage patterns.

**Acceptance Criteria**:
- [ ] Detects gaps in time series
- [ ] Detects sudden value drops to zero
- [ ] Returns reasoning for conclusion

---

### TOOL-ANALYSIS-005: hypothesis_test_seasonality
**Priority**: P1  
**Description**: hypothesis_test_seasonality MUST check for seasonal signals.

**Acceptance Criteria**:
- [ ] Detects periodic patterns
- [ ] Identifies seasonal period (weekly, monthly, etc.)
- [ ] Returns reasoning for conclusion

---

### TOOL-ANALYSIS-006: Enabled Parameter
**Priority**: P1  
**Description**: Hypothesis tools MUST respect enabled parameter.

**Acceptance Criteria**:
- [ ] When enabled=False, return status="skipped"
- [ ] When enabled=True, perform analysis
- [ ] Skipped output is still valid structure

---

### TOOL-ANALYSIS-007: driver_analysis
**Priority**: P1  
**Description**: driver_analysis MUST identify key metric drivers.

**Acceptance Criteria**:
- [ ] Returns ranked list of drivers
- [ ] Includes contribution percentages
- [ ] Based on computed metrics

---

## 4. Visualization Tools (TOOL-VIZ)

### TOOL-VIZ-001: build_chart_spec Output
**Priority**: P0  
**Description**: build_chart_spec MUST output Vega-Lite compatible spec.

**Output Fields**:
```python
chart_spec: Dict  # Vega-Lite specification
```

---

### TOOL-VIZ-002: Chart Type Support
**Priority**: P0  
**Description**: build_chart_spec MUST support all chart types.

| chart_type | Support |
|------------|---------|
| bar | Required |
| line | Required |
| area | Required |
| scatter | Required |

---

### TOOL-VIZ-003: Fallback Chart Type
**Priority**: P1  
**Description**: build_chart_spec MUST use fallback when type is incompatible.

**Acceptance Criteria**:
- [ ] fallback_chart_type parameter is respected
- [ ] Default fallback is "bar"
- [ ] Incompatibility is logged

---

### TOOL-VIZ-004: recommend_chart
**Priority**: P2  
**Description**: recommend_chart MUST suggest appropriate chart type.

**Acceptance Criteria**:
- [ ] Considers data shape (time series, categorical, etc.)
- [ ] Returns single recommendation
- [ ] Uses heuristics, not LLM

---

## 5. Assembly Tools (TOOL-ASSEMBLE)

### TOOL-ASSEMBLE-001: assemble_decision_packet Output
**Priority**: P0  
**Description**: assemble_decision_packet MUST output valid DecisionPacket.

**Acceptance Criteria**:
- [ ] Output passes Pydantic validation
- [ ] All required fields populated
- [ ] Sections are well-formed

---

### TOOL-ASSEMBLE-002: Decision Packet Sections
**Priority**: P0  
**Description**: assemble_decision_packet MUST include required sections.

**Required Sections**:
- [ ] sufficiency: Data sufficiency assessment
- [ ] hypotheses: Hypothesis test results

---

### TOOL-ASSEMBLE-003: Evidence References
**Priority**: P0  
**Description**: assemble_decision_packet MUST include evidence_refs in sections.

**Acceptance Criteria**:
- [ ] Each section has evidence_refs list
- [ ] References include dataset_id and columns
- [ ] References are traceable

---

### TOOL-ASSEMBLE-004: Trace References
**Priority**: P0  
**Description**: assemble_decision_packet MUST include trace_refs.

**Acceptance Criteria**:
- [ ] trace_refs includes step_id references
- [ ] trace_refs includes user_inputs
- [ ] All referenced steps are valid

---

### TOOL-ASSEMBLE-005: assemble_business_report Output
**Priority**: P0  
**Description**: assemble_business_report MUST output valid BusinessReport.

**Acceptance Criteria**:
- [ ] Output passes Pydantic validation
- [ ] All required fields populated
- [ ] Executive summary is meaningful

---

### TOOL-ASSEMBLE-006: assemble_evidence_bundle
**Priority**: P1  
**Description**: assemble_evidence_bundle MUST aggregate evidence items.

**Acceptance Criteria**:
- [ ] Combines items from multiple sources
- [ ] Preserves provenance
- [ ] Deduplicates if needed

---

### TOOL-ASSEMBLE-007: assemble_insight_card
**Priority**: P2  
**Description**: assemble_insight_card MUST create InsightCard objects.

**Acceptance Criteria**:
- [ ] Card includes headline, value, context
- [ ] Card includes evidence references
- [ ] Card is self-contained

---

## 6. Rendering Tools (TOOL-RENDER)

### TOOL-RENDER-001: render_business_report_html
**Priority**: P0  
**Description**: render_business_report_html MUST produce valid HTML.

**Acceptance Criteria**:
- [ ] Output is valid HTML5
- [ ] Includes all report sections
- [ ] Charts are rendered (or placeholders)

---

### TOOL-RENDER-002: render_decision_packet_html
**Priority**: P0  
**Description**: render_decision_packet_html MUST produce valid HTML.

**Acceptance Criteria**:
- [ ] Output is valid HTML5
- [ ] Includes all packet sections
- [ ] Evidence references are visible

---

### TOOL-RENDER-003: export_pdf
**Priority**: P2  
**Description**: export_pdf MUST produce multiple output formats.

**Outputs**:
- [ ] ade.pdf: PDF version
- [ ] ade.html: HTML version
- [ ] ade_stub.json: JSON stub

---

### TOOL-RENDER-004: export_pdf Side Effect
**Priority**: P0  
**Description**: export_pdf MUST be the only tool with side_effect=True.

**Acceptance Criteria**:
- [ ] Writes files to filesystem
- [ ] Files written to staging/output/
- [ ] Other tools do not write files

---

## 7. Narrative Tools (TOOL-NARR)

### TOOL-NARR-001: build_reasoning_narrative
**Priority**: P1  
**Description**: build_reasoning_narrative MUST summarize run events.

**Acceptance Criteria**:
- [ ] Narrative is human-readable
- [ ] Summarizes key analysis steps
- [ ] Concise (< 200 words)

---

## Cross-References

- **System Design**: [agents-and-tools.md](../04_systemdesign/agents-and-tools.md)
- **BRD**: [BRD-tools.md](../01_brd/BRD-tools.md)
