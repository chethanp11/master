# ADE Schema Technical Specification

> **Document**: Technical Specification — Schemas  
> **Prefix**: TS-SCHEMA-*  
> **Version**: 1.4  
> **Last Updated**: 2026-01-20

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added context pack requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |
| 1.3 | 2026-01-21 | Added evidence item schema and context pack grounding requirements per gap analysis. |
| 1.4 | 2026-01-20 | Converted all TSD IDs to TS- prefix; added implementation-level technical details (file paths, Pydantic models, field types). |

---

## 1. General Schema Requirements (TS-SCHEMA-GEN)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-GEN-001 | All ADE schemas MUST be Pydantic BaseModel classes with complete type annotations. | Base: `from pydantic import BaseModel`; File: `products/ade/schemas/*.py`; Pattern: `class Schema(BaseModel): field: Type` | MUST | BRD-SCHEMA-001 | — |
| TS-SCHEMA-GEN-002 | All ADE schemas MUST forbid extra fields using model_config = ConfigDict(extra="forbid"). | Implementation: `from pydantic import ConfigDict`; `model_config = ConfigDict(extra="forbid")` in each schema class | MUST | BRD-SCHEMA-002 | — |
| TS-SCHEMA-GEN-003 | All List and Dict fields in ADE schemas MUST use Field(default_factory=...) instead of mutable default arguments. | Pattern: `field: List[str] = Field(default_factory=list)`; Never: `field: List[str] = []` | MUST | BRD-SCHEMA-004 | — |

---

## 2. DecisionPacket Schema (TS-SCHEMA-DP)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-DP-001 | The DecisionPacket schema MUST include required field: question (str). | File: `products/ade/schemas/decision_packet.py`; Field: `question: str` | MUST | BRD-DP-001 | — |
| TS-SCHEMA-DP-002 | The DecisionPacket schema MUST include required field: decision_summary (str). | Field: `decision_summary: str` | MUST | BRD-DP-002 | — |
| TS-SCHEMA-DP-003 | The DecisionPacket schema MUST include required field: confidence_level (str). | Field: `confidence_level: Literal["high", "medium", "low"]` | MUST | BRD-DP-003 | — |
| TS-SCHEMA-DP-004 | The DecisionPacket schema MUST include required field: assumptions (List[str]). | Field: `assumptions: List[str] = Field(default_factory=list)` | MUST | BRD-DP-004 | — |
| TS-SCHEMA-DP-005 | The DecisionPacket schema MUST include required field: limitations (List[str]). | Field: `limitations: List[str] = Field(default_factory=list)` | MUST | BRD-DP-005 | — |
| TS-SCHEMA-DP-006 | The DecisionPacket schema MUST include required field: sections (List[DecisionSection]). | Field: `sections: List[DecisionSection] = Field(default_factory=list)`; Validation: `@field_validator` ensures non-empty | MUST | BRD-DP-006 | — |
| TS-SCHEMA-DP-007 | The DecisionPacket schema MUST include required field: trace_refs (List[Dict[str, Any]]). | Field: `trace_refs: List[Dict[str, Any]] = Field(default_factory=list)`; Keys: `step_id`, `user_inputs` | MUST | BRD-DP-007 | — |
| TS-SCHEMA-DP-008 | The DecisionPacket schema MAY include optional field: reasoning_narrative (Optional[str]). | Field: `reasoning_narrative: Optional[str] = None` | MAY | BRD-DP-002 | — |

---

## 3. DecisionSection Schema (TS-SCHEMA-DS)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-DS-001 | The DecisionSection schema MUST include required field: section_id (str). | File: `products/ade/schemas/decision_section.py`; Field: `section_id: str` | MUST | BRD-DP-006 | — |
| TS-SCHEMA-DS-002 | The DecisionSection schema MUST include required field: title (str). | Field: `title: str` | MUST | BRD-DP-006 | — |
| TS-SCHEMA-DS-003 | The DecisionSection schema MUST include required field: intent (str). | Field: `intent: str` | MUST | BRD-DP-006 | — |
| TS-SCHEMA-DS-004 | The DecisionSection schema MUST include required field: narrative (str). | Field: `narrative: str` | MUST | BRD-DP-006 | — |
| TS-SCHEMA-DS-005 | The DecisionSection schema MUST include required field: claim_strength (str) with allowed values: high, medium, low. | Field: `claim_strength: Literal["high", "medium", "low"]` | MUST | BRD-DP-006 | — |
| TS-SCHEMA-DS-006 | The DecisionSection schema MUST include required field: visuals (List[Dict[str, Any]]). | Field: `visuals: List[Dict[str, Any]] = Field(default_factory=list)` | MUST | BRD-DP-006 | — |
| TS-SCHEMA-DS-007 | The DecisionSection schema MUST include required field: evidence_refs (List[Dict[str, Any]]). | Field: `evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)`; Keys: `dataset_id`, `columns` | MUST | BRD-DP-006, BRD-EVREF-001 | — |
| TS-SCHEMA-DS-008 | The DecisionSection schema MAY include optional field: rejected_alternatives (Optional[List[str]]). | Field: `rejected_alternatives: Optional[List[str]] = None` | MAY | BRD-DP-006 | — |

---

## 4. BusinessReport Schema (TS-SCHEMA-BR)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-BR-001 | The BusinessReport schema MUST include required field: title (str). | File: `products/ade/schemas/business_report.py`; Field: `title: str` | MUST | BRD-BR-001 | — |
| TS-SCHEMA-BR-002 | The BusinessReport schema MUST include required field: generated_at_iso (str) in ISO 8601 format. | Field: `generated_at_iso: str`; Validator: `@field_validator("generated_at_iso") def validate_iso(cls, v): datetime.fromisoformat(v); return v` | MUST | BRD-BR-002 | — |
| TS-SCHEMA-BR-003 | The BusinessReport schema MUST include required field: dataset_id (str). | Field: `dataset_id: str` | MUST | BRD-BR-003 | — |
| TS-SCHEMA-BR-004 | The BusinessReport schema MUST include required field: row_count (int). | Field: `row_count: int = Field(ge=0)` | MUST | BRD-BR-003 | — |
| TS-SCHEMA-BR-005 | The BusinessReport schema MUST include required field: period_labels (List[str]). | Field: `period_labels: List[str] = Field(default_factory=list)` | MUST | BRD-BR-003 | — |
| TS-SCHEMA-BR-006 | The BusinessReport schema MUST include required field: series_count (int). | Field: `series_count: int = Field(ge=0)` | MUST | BRD-BR-003 | — |
| TS-SCHEMA-BR-007 | The BusinessReport schema MUST include required field: executive_summary (List[str]). | Field: `executive_summary: List[str] = Field(default_factory=list)` | MUST | BRD-BR-004 | — |
| TS-SCHEMA-BR-008 | The BusinessReport schema MUST include required field: key_findings (List[Finding]). | Field: `key_findings: List[Finding] = Field(default_factory=list)` | MUST | BRD-BR-005 | — |
| TS-SCHEMA-BR-009 | The BusinessReport schema MUST include required field: visuals (List[VisualSpec]). | Field: `visuals: List[VisualSpec] = Field(default_factory=list)` | MUST | BRD-BR-006 | — |
| TS-SCHEMA-BR-010 | The BusinessReport schema MUST include required field: anomalies (List[AnomalyRow]). | Field: `anomalies: List[AnomalyRow] = Field(default_factory=list)` | MUST | BRD-BR-007 | — |
| TS-SCHEMA-BR-011 | The BusinessReport schema MUST include required field: recommendations (List[str]). | Field: `recommendations: List[str] = Field(default_factory=list)` | MUST | BRD-RPT-006 | — |
| TS-SCHEMA-BR-012 | The BusinessReport schema MUST include required field: appendix (Appendix). | Field: `appendix: Appendix` | MUST | BRD-BR-008 | — |

---

## 5. Finding Schema (TS-SCHEMA-FIND)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-FIND-001 | The Finding schema MUST include required field: headline (str). | File: `products/ade/schemas/finding.py`; Field: `headline: str` | MUST | BRD-BR-005 | — |
| TS-SCHEMA-FIND-002 | The Finding schema MUST include required field: value (str). | Field: `value: str` | MUST | BRD-BR-005 | — |
| TS-SCHEMA-FIND-003 | The Finding schema MUST include required field: context (str). | Field: `context: str` | MUST | BRD-BR-005 | — |
| TS-SCHEMA-FIND-004 | The Finding schema MUST include field evidence_refs using Field(default_factory=list). | Field: `evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)` | MUST | BRD-EVREF-001 | — |

---

## 6. VisualSpec Schema (TS-SCHEMA-VS)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-VS-001 | The VisualSpec schema MUST include required field: kind (Literal["line", "heatmap", "bar"]). | File: `products/ade/schemas/visual_spec.py`; Field: `kind: Literal["line", "heatmap", "bar", "area", "scatter"]` | MUST | BRD-BR-006, BRD-CHART-001 | — |
| TS-SCHEMA-VS-002 | The VisualSpec schema MUST include required field: title (str). | Field: `title: str` | MUST | BRD-BR-006 | — |
| TS-SCHEMA-VS-003 | The VisualSpec schema MUST include field data using Field(default_factory=dict). | Field: `data: Dict[str, Any] = Field(default_factory=dict)` | MUST | BRD-BR-006 | — |
| TS-SCHEMA-VS-004 | The VisualSpec schema MUST include field config using Field(default_factory=dict). | Field: `config: Dict[str, Any] = Field(default_factory=dict)` | MUST | BRD-BR-006 | — |

---

## 7. AnomalyRow Schema (TS-SCHEMA-AR)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-AR-001 | The AnomalyRow schema MUST include required field: rank (int). | File: `products/ade/schemas/anomaly_row.py`; Field: `rank: int = Field(ge=1)` | MUST | BRD-BR-007 | — |
| TS-SCHEMA-AR-002 | The AnomalyRow schema MUST include required field: expense (str). | Field: `expense: str` | MUST | BRD-BR-007 | — |
| TS-SCHEMA-AR-003 | The AnomalyRow schema MUST include required field: period (str). | Field: `period: str` | MUST | BRD-BR-007 | — |
| TS-SCHEMA-AR-004 | The AnomalyRow schema MUST include required field: value (float). | Field: `value: float` | MUST | BRD-BR-007 | — |
| TS-SCHEMA-AR-005 | The AnomalyRow schema MUST include required field: baseline (float). | Field: `baseline: float` | MUST | BRD-BR-007 | — |
| TS-SCHEMA-AR-006 | The AnomalyRow schema MUST include required field: delta (float). | Field: `delta: float` | MUST | BRD-BR-007 | — |
| TS-SCHEMA-AR-007 | The AnomalyRow schema MUST include required field: reason (str). | Field: `reason: str` | MUST | BRD-BR-007, BRD-ANOM-004 | — |
| TS-SCHEMA-AR-008 | The AnomalyRow schema MAY include optional field: delta_pct (Optional[float]). | Field: `delta_pct: Optional[float] = None` | MAY | BRD-BR-007 | — |

---

## 8. IntentFrame Schema (TS-SCHEMA-IF)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-IF-001 | The IntentFrame schema MUST include required field: intent_summary (str). | File: `products/ade/schemas/intent_frame.py`; Field: `intent_summary: str` | MUST | BRD-IF-001 | — |
| TS-SCHEMA-IF-002 | The IntentFrame schema MUST include field: inferred_entities using Field(default_factory=list). | Field: `inferred_entities: List[str] = Field(default_factory=list)` | MUST | BRD-IF-004 | — |
| TS-SCHEMA-IF-003 | The IntentFrame schema MUST include field: inferred_metrics using Field(default_factory=list). | Field: `inferred_metrics: List[str] = Field(default_factory=list)` | MUST | BRD-IF-005 | — |
| TS-SCHEMA-IF-004 | The IntentFrame schema MUST include field: inferred_time_window (Optional[str]) with default None. | Field: `inferred_time_window: Optional[str] = None` | MUST | BRD-IF-004 | — |
| TS-SCHEMA-IF-005 | The IntentFrame schema MUST include field: requested_outputs using Field(default_factory=list). | Field: `requested_outputs: List[str] = Field(default_factory=list)` | MUST | BRD-IF-001 | — |
| TS-SCHEMA-IF-006 | The IntentFrame schema MUST include field: confidence_score (float) with default 0.0 and valid range 0.0-1.0. | Field: `confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)` | MUST | BRD-IF-002 | — |
| TS-SCHEMA-IF-007 | The IntentFrame schema MUST include field: confidence_label (str) with default "low". | Field: `confidence_label: Literal["high", "medium", "low"] = "low"` | MUST | BRD-IF-002 | — |
| TS-SCHEMA-IF-008 | The IntentFrame schema MUST include field: blocking_required (bool) with default False. | Field: `blocking_required: bool = False` | MUST | BRD-IF-003 | — |
| TS-SCHEMA-IF-009 | The IntentFrame schema MUST include field: blocking_questions using Field(default_factory=list). | Field: `blocking_questions: List[str] = Field(default_factory=list)` | MUST | BRD-IF-006 | — |
| TS-SCHEMA-IF-010 | The IntentFrame schema MUST include field: blocking_question (Optional[str]) with default None. | Field: `blocking_question: Optional[str] = None` | MUST | BRD-IF-006 | — |

---

## 9. Validation Requirements (TS-SCHEMA-VAL)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-VAL-001 | All ADE outputs MUST pass Pydantic validation before rendering. | Logic: `schema.model_validate(output)` before `render_*()` calls; Location: `products/ade/tools/assemble_*.py` | MUST | BRD-VAL-001 | — |
| TS-SCHEMA-VAL-002 | Invalid ADE outputs MUST produce clear errors including schema field path and failure reason. | Exception: `pydantic.ValidationError`; Message format: `{field_path}: {error_message}` | MUST | BRD-VAL-002 | — |
| TS-SCHEMA-VAL-003 | ADE validation MUST happen before rendering outputs. | Flow: `assemble_*() -> validate() -> render_*()` | MUST | BRD-VAL-003 | — |

---

## 10. Context Pack Requirements (TS-SCHEMA-CTX)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-CTX-001 | The ADE system MUST construct a Context Pack artifact after ingestion and before planning. | File: `products/ade/schemas/context_pack.py`; Builder: `products/ade/tools/build_context_pack.py`; Step: after `data_reader`, before `planning` | MUST | BRD-CTX-001 | — |
| TS-SCHEMA-CTX-002 | The Context Pack MUST include fields: dataset_profile, coverage, missingness, data_quality_flags, metric_availability. | Schema: `class ContextPack(BaseModel): dataset_profile: DatasetProfile; coverage: Coverage; missingness: Missingness; data_quality_flags: List[str]; metric_availability: Dict[str, bool]` | MUST | BRD-CTX-002 | — |
| TS-SCHEMA-CTX-003 | Context Pack statistics MUST be backed by evidence items referencing dataset_id/columns. | Field: `ContextPack.evidence_items: List[EvidenceItem]`; Required: `evidence_item.dataset_id`, `evidence_item.columns` | MUST | BRD-CTX-003 | — |
| TS-SCHEMA-CTX-004 | ADE advisory reasoning SHOULD reference Context Pack artifacts. | Pattern: `{{artifacts.tool.build_context_pack.output.*}}` in agent prompts | SHOULD | BRD-CTX-004 | — |
| TS-SCHEMA-CTX-005 | ADE reasoning and outputs MUST treat Context Pack artifacts as the sole grounding source; no external data references. | Enforcement: No network calls; All data from `context_pack.data` or `data_reader.output` | MUST | BRD-CTX-005 | — |

---

## 11. Appendix Schema (TS-SCHEMA-APP)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-APP-001 | The Appendix schema MUST include required field: confidence (str). | File: `products/ade/schemas/appendix.py`; Field: `confidence: Literal["high", "medium", "low"]` | MUST | BRD-BR-008 | — |
| TS-SCHEMA-APP-002 | The Appendix schema MUST include field: downgrade_reasons using Field(default_factory=list). | Field: `downgrade_reasons: List[str] = Field(default_factory=list)` | MUST | BRD-BR-008 | — |
| TS-SCHEMA-APP-003 | The Appendix schema MUST include field: trace_refs using Field(default_factory=list). | Field: `trace_refs: List[Dict[str, Any]] = Field(default_factory=list)` | MUST | BRD-BR-008 | — |
| TS-SCHEMA-APP-004 | The Appendix schema MUST include field: assumptions using Field(default_factory=list). | Field: `assumptions: List[str] = Field(default_factory=list)` | MUST | BRD-BR-008 | — |
| TS-SCHEMA-APP-005 | The Appendix schema MUST include field: limitations using Field(default_factory=list). | Field: `limitations: List[str] = Field(default_factory=list)` | MUST | BRD-BR-008 | — |

---

## 12. Evidence Item Schema (TS-SCHEMA-EVITEM)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SCHEMA-EVITEM-001 | Evidence items MUST include a confidence field (float, 0.0-1.0) indicating reliability of the evidence. | File: `products/ade/schemas/evidence.py`; Field: `confidence: float = Field(ge=0.0, le=1.0)` | MUST | BRD-ITEM-003 | — |
| TS-SCHEMA-EVITEM-002 | Evidence items MUST include a values field containing the referenced data values from the source. | Field: `values: Dict[str, Any] = Field(default_factory=dict)` | MUST | BRD-ITEM-006 | — |

---

## Cross-References

- **BRD**: [BRD-data.md](../01_brd/BRD-data.md)
- **System Design**: [schemas.md](../04_systemdesign/schemas.md)
