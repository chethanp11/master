# ADE Schema Technical Specification

> **Document**: Technical Specification — Schemas  
> **Prefix**: SCHEMA-*  
> **Version**: 1.2  
> **Last Updated**: 2026-01-20

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added context pack requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |

---

## 1. General Schema Requirements (SCHEMA-GEN)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-GEN-001 | All ADE schemas MUST be Pydantic BaseModel classes with complete type annotations. | MUST | BRD-SCHEMA-001 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-GEN-002 | All ADE schemas MUST forbid extra fields using model_config = ConfigDict(extra="forbid"). | MUST | BRD-SCHEMA-002 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-GEN-003 | All List and Dict fields in ADE schemas MUST use Field(default_factory=...) instead of mutable default arguments. | MUST | BRD-SCHEMA-004 | 1.1 | 13 Jan 2026 | — |

---

## 2. DecisionPacket Schema (SCHEMA-DP)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-DP-001 | The DecisionPacket schema MUST include required field: question (str). | MUST | BRD-DP-001 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DP-002 | The DecisionPacket schema MUST include required field: decision_summary (str). | MUST | BRD-DP-002 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DP-003 | The DecisionPacket schema MUST include required field: confidence_level (str). | MUST | BRD-DP-003 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DP-004 | The DecisionPacket schema MUST include required field: assumptions (List[str]). | MUST | BRD-DP-004 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DP-005 | The DecisionPacket schema MUST include required field: limitations (List[str]). | MUST | BRD-DP-005 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DP-006 | The DecisionPacket schema MUST include required field: sections (List[DecisionSection]). | MUST | BRD-DP-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DP-007 | The DecisionPacket schema MUST include required field: trace_refs (List[Dict[str, Any]]). | MUST | BRD-DP-007 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DP-008 | The DecisionPacket schema MAY include optional field: reasoning_narrative (Optional[str]). | MAY | BRD-DP-002 | 1.1 | 13 Jan 2026 | — |

---

## 3. DecisionSection Schema (SCHEMA-DS)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-DS-001 | The DecisionSection schema MUST include required field: section_id (str). | MUST | BRD-DP-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DS-002 | The DecisionSection schema MUST include required field: title (str). | MUST | BRD-DP-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DS-003 | The DecisionSection schema MUST include required field: intent (str). | MUST | BRD-DP-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DS-004 | The DecisionSection schema MUST include required field: narrative (str). | MUST | BRD-DP-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DS-005 | The DecisionSection schema MUST include required field: claim_strength (str) with allowed values: high, medium, low. | MUST | BRD-DP-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DS-006 | The DecisionSection schema MUST include required field: visuals (List[Dict[str, Any]]). | MUST | BRD-DP-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DS-007 | The DecisionSection schema MUST include required field: evidence_refs (List[Dict[str, Any]]). | MUST | BRD-DP-006, BRD-EVREF-001 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-DS-008 | The DecisionSection schema MAY include optional field: rejected_alternatives (Optional[List[str]]). | MAY | BRD-DP-006 | 1.1 | 13 Jan 2026 | — |

---

## 4. BusinessReport Schema (SCHEMA-BR)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-BR-001 | The BusinessReport schema MUST include required field: title (str). | MUST | BRD-BR-001 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-002 | The BusinessReport schema MUST include required field: generated_at_iso (str) in ISO 8601 format. | MUST | BRD-BR-002 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-003 | The BusinessReport schema MUST include required field: dataset_id (str). | MUST | BRD-BR-003 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-004 | The BusinessReport schema MUST include required field: row_count (int). | MUST | BRD-BR-003 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-005 | The BusinessReport schema MUST include required field: period_labels (List[str]). | MUST | BRD-BR-003 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-006 | The BusinessReport schema MUST include required field: series_count (int). | MUST | BRD-BR-003 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-007 | The BusinessReport schema MUST include required field: executive_summary (List[str]). | MUST | BRD-BR-004 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-008 | The BusinessReport schema MUST include required field: key_findings (List[Finding]). | MUST | BRD-BR-005 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-009 | The BusinessReport schema MUST include required field: visuals (List[VisualSpec]). | MUST | BRD-BR-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-010 | The BusinessReport schema MUST include required field: anomalies (List[AnomalyRow]). | MUST | BRD-BR-007 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-011 | The BusinessReport schema MUST include required field: recommendations (List[str]). | MUST | BRD-RPT-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-BR-012 | The BusinessReport schema MUST include required field: appendix (Appendix). | MUST | BRD-BR-008 | 1.1 | 13 Jan 2026 | — |

---

## 5. Finding Schema (SCHEMA-FIND)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-FIND-001 | The Finding schema MUST include required field: headline (str). | MUST | BRD-BR-005 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-FIND-002 | The Finding schema MUST include required field: value (str). | MUST | BRD-BR-005 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-FIND-003 | The Finding schema MUST include required field: context (str). | MUST | BRD-BR-005 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-FIND-004 | The Finding schema MUST include field evidence_refs using Field(default_factory=list). | MUST | BRD-EVREF-001 | 1.1 | 13 Jan 2026 | — |

---

## 6. VisualSpec Schema (SCHEMA-VS)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-VS-001 | The VisualSpec schema MUST include required field: kind (Literal["line", "heatmap", "bar"]). | MUST | BRD-BR-006, BRD-CHART-001 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-VS-002 | The VisualSpec schema MUST include required field: title (str). | MUST | BRD-BR-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-VS-003 | The VisualSpec schema MUST include field data using Field(default_factory=dict). | MUST | BRD-BR-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-VS-004 | The VisualSpec schema MUST include field config using Field(default_factory=dict). | MUST | BRD-BR-006 | 1.1 | 13 Jan 2026 | — |

---

## 7. AnomalyRow Schema (SCHEMA-AR)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-AR-001 | The AnomalyRow schema MUST include required field: rank (int). | MUST | BRD-BR-007 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-AR-002 | The AnomalyRow schema MUST include required field: expense (str). | MUST | BRD-BR-007 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-AR-003 | The AnomalyRow schema MUST include required field: period (str). | MUST | BRD-BR-007 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-AR-004 | The AnomalyRow schema MUST include required field: value (float). | MUST | BRD-BR-007 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-AR-005 | The AnomalyRow schema MUST include required field: baseline (float). | MUST | BRD-BR-007 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-AR-006 | The AnomalyRow schema MUST include required field: delta (float). | MUST | BRD-BR-007 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-AR-007 | The AnomalyRow schema MUST include required field: reason (str). | MUST | BRD-BR-007, BRD-ANOM-004 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-AR-008 | The AnomalyRow schema MAY include optional field: delta_pct (Optional[float]). | MAY | BRD-BR-007 | 1.1 | 13 Jan 2026 | — |

---

## 8. IntentFrame Schema (SCHEMA-IF)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-IF-001 | The IntentFrame schema MUST include required field: intent_summary (str). | MUST | BRD-IF-001 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-IF-002 | The IntentFrame schema MUST include field: inferred_entities using Field(default_factory=list). | MUST | BRD-IF-004 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-IF-003 | The IntentFrame schema MUST include field: inferred_metrics using Field(default_factory=list). | MUST | BRD-IF-005 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-IF-004 | The IntentFrame schema MUST include field: inferred_time_window (Optional[str]) with default None. | MUST | BRD-IF-004 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-IF-005 | The IntentFrame schema MUST include field: requested_outputs using Field(default_factory=list). | MUST | BRD-IF-001 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-IF-006 | The IntentFrame schema MUST include field: confidence_score (float) with default 0.0 and valid range 0.0-1.0. | MUST | BRD-IF-002 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-IF-007 | The IntentFrame schema MUST include field: confidence_label (str) with default "low". | MUST | BRD-IF-002 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-IF-008 | The IntentFrame schema MUST include field: blocking_required (bool) with default False. | MUST | BRD-IF-003 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-IF-009 | The IntentFrame schema MUST include field: blocking_questions using Field(default_factory=list). | MUST | BRD-IF-006 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-IF-010 | The IntentFrame schema MUST include field: blocking_question (Optional[str]) with default None. | MUST | BRD-IF-006 | 1.1 | 13 Jan 2026 | — |

---

## 9. Validation Requirements (SCHEMA-VAL)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-VAL-001 | All ADE outputs MUST pass Pydantic validation before rendering. | MUST | BRD-VAL-001 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-VAL-002 | Invalid ADE outputs MUST produce clear errors including schema field path and failure reason. | MUST | BRD-VAL-002 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-VAL-003 | ADE validation MUST happen before rendering outputs. | MUST | BRD-VAL-003 | 1.1 | 13 Jan 2026 | — |

---

## 10. Context Pack Requirements (SCHEMA-CTX)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-CTX-001 | The ADE system MUST construct a Context Pack artifact after ingestion and before planning. | MUST | BRD-CTX-001 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-CTX-002 | The Context Pack MUST include fields: dataset_profile, coverage, missingness, data_quality_flags, metric_availability. | MUST | BRD-CTX-002 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-CTX-003 | Context Pack statistics MUST be backed by evidence items referencing dataset_id/columns. | MUST | BRD-CTX-003 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-CTX-004 | ADE advisory reasoning SHOULD reference Context Pack artifacts. | SHOULD | BRD-CTX-004 | 1.1 | 13 Jan 2026 | — |

---

## 11. Appendix Schema (SCHEMA-APP)

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|------------------------|-------|---------------------|---------|------------|-------|
| SCHEMA-APP-001 | The Appendix schema MUST include required field: confidence (str). | MUST | BRD-BR-008 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-APP-002 | The Appendix schema MUST include field: downgrade_reasons using Field(default_factory=list). | MUST | BRD-BR-008 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-APP-003 | The Appendix schema MUST include field: trace_refs using Field(default_factory=list). | MUST | BRD-BR-008 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-APP-004 | The Appendix schema MUST include field: assumptions using Field(default_factory=list). | MUST | BRD-BR-008 | 1.1 | 13 Jan 2026 | — |
| SCHEMA-APP-005 | The Appendix schema MUST include field: limitations using Field(default_factory=list). | MUST | BRD-BR-008 | 1.1 | 13 Jan 2026 | — |

---

## Cross-References

- **BRD**: [BRD-data.md](../01_brd/BRD-data.md)
