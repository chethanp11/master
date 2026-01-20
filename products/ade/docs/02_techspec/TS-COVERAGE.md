# ADE Tech Spec Coverage Matrix

> **Document**: Tech Spec Coverage (ADE)  
> **Version**: 1.2  
> **Last Updated**: 2026-01-20  
> **Status**: V1.2 Release

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added semantic interpretation coverage |
| 1.2 | 2026-01-20 | Normalized to canonical 6-column coverage matrix; added explicit TSD ID mappings. |

---

## Coverage Matrix

| BRD ID | Business Requirement (from BRD) | Source File | TSD ID | Tech Spec file | Covered |
|--------|--------------------------------|-------------|--------|----------------|---------|
| BRD-OBJ-001 | ADE MUST analyze datasets to answer business questions | BRD-overview.md | IO-OBJ-001 | IO-inputs-outputs.md | ✅ |
| BRD-OBJ-002 | ADE MUST produce evidence-backed recommendations | BRD-overview.md | IO-OBJ-002 | IO-inputs-outputs.md | ✅ |
| BRD-OBJ-003 | ADE MUST visualize key metrics and trends | BRD-overview.md | IO-OBJ-003 | IO-inputs-outputs.md | ✅ |
| BRD-OBJ-004 | ADE MUST identify anomalies in data | BRD-overview.md | IO-OBJ-004 | IO-inputs-outputs.md | ✅ |
| BRD-OBJ-005 | ADE MUST provide confidence levels for findings | BRD-overview.md | IO-OBJ-005 | IO-inputs-outputs.md | ✅ |
| BRD-OBJ-006 | ADE MUST produce self-contained business reports | BRD-overview.md | IO-OBJ-006 | IO-inputs-outputs.md | ✅ |
| BRD-INPUT-001 | System MUST accept business question as text input | BRD-overview.md | IO-INPUT-001 | IO-inputs-outputs.md | ✅ |
| BRD-INPUT-002 | System MUST accept dataset selection | BRD-overview.md | IO-INPUT-002 | IO-inputs-outputs.md | ✅ |
| BRD-INPUT-003 | System MUST accept visualization preferences | BRD-overview.md | IO-INPUT-003 | IO-inputs-outputs.md | ✅ |
| BRD-INPUT-004 | System MUST accept plan approval decision | BRD-overview.md | IO-INPUT-004 | IO-inputs-outputs.md | ✅ |
| BRD-FMT-001 | System MUST support CSV format | BRD-data.md | IO-DATA-001 | IO-inputs-outputs.md | ✅ |
| BRD-FMT-002 | System MUST support UTF-8 encoding | BRD-data.md | IO-DATA-002 | IO-inputs-outputs.md | ✅ |
| BRD-FMT-003 | System MUST support header row with column names | BRD-data.md | IO-DATA-003 | IO-inputs-outputs.md | ✅ |
| BRD-FMT-004 | System MUST support data rows with values | BRD-data.md | IO-DATA-004 | IO-inputs-outputs.md | ✅ |
| BRD-LOC-001 | Datasets MUST be loaded from products/ade/data/ | BRD-data.md | IO-DATA-005 | IO-inputs-outputs.md | ✅ |
| BRD-UI-001 | User MUST provide chart_type selection | BRD-flows.md | IO-UI-001 | IO-inputs-outputs.md | ✅ |
| BRD-UI-002 | User MUST provide metric_focus selection | BRD-flows.md | IO-UI-002 | IO-inputs-outputs.md | ✅ |
| BRD-UI-003 | User MAY toggle hypothesis checks | BRD-flows.md | IO-UI-003 | IO-inputs-outputs.md | ✅ |
| BRD-UI-004 | User MAY provide analysis notes | BRD-flows.md | IO-UI-004 | IO-inputs-outputs.md | ✅ |
| BRD-OUT-001 | ADE MUST output business_report.html | BRD-outputs.md | IO-OUT-001 | IO-inputs-outputs.md | ✅ |
| BRD-OUT-002 | ADE visualization flow MUST output decision_packet.html | BRD-outputs.md | IO-OUT-002 | IO-inputs-outputs.md | ✅ |
| BRD-OUT-003 | All outputs MUST pass Pydantic validation | BRD-outputs.md | IO-OUT-003 | IO-inputs-outputs.md | ✅ |
| BRD-OUT-004 | Outputs MUST include confidence level | BRD-outputs.md | IO-OUT-004 | IO-inputs-outputs.md | ✅ |
| BRD-OUT-005 | Outputs MUST include assumptions and limitations | BRD-outputs.md | IO-OUT-005 | IO-inputs-outputs.md | ✅ |
| BRD-QUAL-001 | Business reports MUST include executive summary | BRD-outputs.md | IO-QUAL-001 | IO-inputs-outputs.md | ✅ |
| BRD-QUAL-002 | Business reports MUST include key findings | BRD-outputs.md | IO-QUAL-002 | IO-inputs-outputs.md | ✅ |
| BRD-QUAL-003 | Business reports MUST include recommendations | BRD-outputs.md | IO-QUAL-003 | IO-inputs-outputs.md | ✅ |
| BRD-VER-001 | Outputs MUST include ADE product version | BRD-outputs.md | IO-VER-001 | IO-inputs-outputs.md | ✅ |
| BRD-VER-002 | Outputs MUST include platform version | BRD-outputs.md | IO-VER-002 | IO-inputs-outputs.md | ✅ |
| BRD-VER-003 | Outputs MUST include generation timestamp | BRD-outputs.md | IO-VER-003 | IO-inputs-outputs.md | ✅ |
| BRD-DAB-001 | ADE MUST NOT make final business decisions | BRD-outputs.md | IO-DAB-001 | IO-inputs-outputs.md | ✅ |
| BRD-DAB-002 | ADE MUST clearly label outputs as recommendations | BRD-outputs.md | IO-DAB-002 | IO-inputs-outputs.md | ✅ |
| BRD-EVREF-001 | Outputs MUST include evidence references | BRD-data.md | IO-EVID-001 | IO-inputs-outputs.md | ✅ |
| BRD-EVREF-002 | Evidence references MUST include dataset_id and columns | BRD-data.md | IO-EVID-002 | IO-inputs-outputs.md | ✅ |
| BRD-TRACE-001 | Outputs MUST include trace references | BRD-data.md | IO-EVID-003 | IO-inputs-outputs.md | ✅ |
| BRD-ARTF-001 | Outputs MUST include artifact references | BRD-data.md | IO-ARTF-001 | IO-inputs-outputs.md | ✅ |
| BRD-SCHEMA-001 | All schemas MUST be Pydantic BaseModel classes | BRD-data.md | SCHEMA-GEN-001 | SCHEMA-schemas.md | ✅ |
| BRD-SCHEMA-002 | All schemas MUST forbid extra fields | BRD-data.md | SCHEMA-GEN-002 | SCHEMA-schemas.md | ✅ |
| BRD-SCHEMA-004 | List/Dict fields MUST use Field(default_factory=...) | BRD-data.md | SCHEMA-GEN-003 | SCHEMA-schemas.md | ✅ |
| BRD-DP-001 | DecisionPacket MUST include question field | BRD-data.md | SCHEMA-DP-001 | SCHEMA-schemas.md | ✅ |
| BRD-DP-002 | DecisionPacket MUST include decision_summary | BRD-data.md | SCHEMA-DP-002 | SCHEMA-schemas.md | ✅ |
| BRD-DP-003 | DecisionPacket MUST include confidence_level | BRD-data.md | SCHEMA-DP-003 | SCHEMA-schemas.md | ✅ |
| BRD-DP-004 | DecisionPacket MUST include assumptions | BRD-data.md | SCHEMA-DP-004 | SCHEMA-schemas.md | ✅ |
| BRD-DP-005 | DecisionPacket MUST include limitations | BRD-data.md | SCHEMA-DP-005 | SCHEMA-schemas.md | ✅ |
| BRD-DP-006 | DecisionPacket MUST include sections | BRD-data.md | SCHEMA-DP-006 | SCHEMA-schemas.md | ✅ |
| BRD-DP-007 | DecisionPacket MUST include trace_refs | BRD-data.md | SCHEMA-DP-007 | SCHEMA-schemas.md | ✅ |
| BRD-BR-001 | BusinessReport MUST include title | BRD-data.md | SCHEMA-BR-001 | SCHEMA-schemas.md | ✅ |
| BRD-BR-002 | BusinessReport MUST include generated_at_iso | BRD-data.md | SCHEMA-BR-002 | SCHEMA-schemas.md | ✅ |
| BRD-BR-003 | BusinessReport MUST include dataset metadata | BRD-data.md | SCHEMA-BR-003 | SCHEMA-schemas.md | ✅ |
| BRD-BR-004 | BusinessReport MUST include executive_summary | BRD-data.md | SCHEMA-BR-007 | SCHEMA-schemas.md | ✅ |
| BRD-BR-005 | BusinessReport MUST include key_findings | BRD-data.md | SCHEMA-BR-008 | SCHEMA-schemas.md | ✅ |
| BRD-BR-006 | BusinessReport MUST include visuals | BRD-data.md | SCHEMA-BR-009 | SCHEMA-schemas.md | ✅ |
| BRD-BR-007 | BusinessReport MUST include anomalies | BRD-data.md | SCHEMA-BR-010 | SCHEMA-schemas.md | ✅ |
| BRD-BR-008 | BusinessReport MUST include appendix | BRD-data.md | SCHEMA-BR-012 | SCHEMA-schemas.md | ✅ |
| BRD-IF-001 | IntentFrame MUST include intent_summary | BRD-data.md | SCHEMA-IF-001 | SCHEMA-schemas.md | ✅ |
| BRD-IF-002 | IntentFrame MUST include confidence_score | BRD-data.md | SCHEMA-IF-006 | SCHEMA-schemas.md | ✅ |
| BRD-IF-003 | IntentFrame MUST include blocking_required | BRD-data.md | SCHEMA-IF-008 | SCHEMA-schemas.md | ✅ |
| BRD-IF-004 | IntentFrame MUST include inferred_entities | BRD-data.md | SCHEMA-IF-002 | SCHEMA-schemas.md | ✅ |
| BRD-IF-005 | IntentFrame MUST include inferred_metrics | BRD-data.md | SCHEMA-IF-003 | SCHEMA-schemas.md | ✅ |
| BRD-IF-006 | IntentFrame MUST include blocking_questions | BRD-data.md | SCHEMA-IF-009 | SCHEMA-schemas.md | ✅ |
| BRD-VAL-001 | Outputs MUST pass Pydantic validation | BRD-data.md | SCHEMA-VAL-001 | SCHEMA-schemas.md | ✅ |
| BRD-VAL-002 | Invalid outputs MUST produce clear errors | BRD-data.md | SCHEMA-VAL-002 | SCHEMA-schemas.md | ✅ |
| BRD-VAL-003 | Validation MUST happen before rendering | BRD-data.md | SCHEMA-VAL-003 | SCHEMA-schemas.md | ✅ |
| BRD-CTX-001 | System MUST construct Context Pack artifact | BRD-data.md | SCHEMA-CTX-001 | SCHEMA-schemas.md | ✅ |
| BRD-CTX-002 | Context Pack MUST include dataset profile fields | BRD-data.md | SCHEMA-CTX-002 | SCHEMA-schemas.md | ✅ |
| BRD-CTX-003 | Context Pack stats MUST be evidence-backed | BRD-data.md | SCHEMA-CTX-003 | SCHEMA-schemas.md | ✅ |
| BRD-CTX-004 | Reasoning SHOULD reference Context Pack | BRD-data.md | SCHEMA-CTX-004 | SCHEMA-schemas.md | ✅ |
| BRD-TOOL-001 | Tools MUST NOT call LLMs directly | BRD-tools.md | TOOL-GEN-001 | TOOL-tools.md | ✅ |
| BRD-TOOL-002 | Tools MUST produce deterministic outputs | BRD-tools.md | TOOL-GEN-005 | TOOL-tools.md | ✅ |
| BRD-TOOL-003 | Same inputs MUST produce same outputs | BRD-tools.md | TOOL-GEN-005 | TOOL-tools.md | ✅ |
| BRD-TOOL-005 | Tools MUST produce evidence items | BRD-tools.md | TOOL-GEN-006 | TOOL-tools.md | ✅ |
| BRD-DATA-001 | System MUST read CSV datasets | BRD-tools.md | TOOL-DATA-001 | TOOL-tools.md | ✅ |
| BRD-DATA-002 | System MUST extract column metadata | BRD-tools.md | TOOL-DATA-001 | TOOL-tools.md | ✅ |
| BRD-DATA-003 | System MUST extract row data | BRD-tools.md | TOOL-DATA-001 | TOOL-tools.md | ✅ |
| BRD-DATA-004 | System MUST infer field types | BRD-tools.md | TOOL-DATA-003 | TOOL-tools.md | ✅ |
| BRD-DATA-005 | System MUST handle UTF-8 encoding | BRD-tools.md | TOOL-DATA-002 | TOOL-tools.md | ✅ |
| BRD-DATA-006 | System MUST handle quoted CSV fields | BRD-tools.md | TOOL-DATA-002 | TOOL-tools.md | ✅ |
| BRD-METRIC-001 | System MUST compute aggregated metrics | BRD-tools.md | TOOL-DATA-004 | TOOL-tools.md | ✅ |
| BRD-METRIC-002 | System MUST support multiple metric types | BRD-tools.md | TOOL-DATA-005 | TOOL-tools.md | ✅ |
| BRD-METRIC-003 | System MUST produce evidence items | BRD-tools.md | TOOL-DATA-004 | TOOL-tools.md | ✅ |
| BRD-METRIC-004 | System MUST respect metric_focus parameter | BRD-tools.md | TOOL-DATA-005 | TOOL-tools.md | ✅ |
| BRD-ANOM-001 | System MUST detect statistical anomalies | BRD-tools.md | TOOL-ANALYSIS-001 | TOOL-tools.md | ✅ |
| BRD-ANOM-002 | System MUST use z-score analysis | BRD-tools.md | TOOL-ANALYSIS-001 | TOOL-tools.md | ✅ |
| BRD-ANOM-005 | System MUST produce evidence items | BRD-tools.md | TOOL-ANALYSIS-002 | TOOL-tools.md | ✅ |
| BRD-HYP-001 | System MUST support data outage hypothesis | BRD-tools.md | TOOL-ANALYSIS-004 | TOOL-tools.md | ✅ |
| BRD-HYP-002 | System MUST support seasonality hypothesis | BRD-tools.md | TOOL-ANALYSIS-005 | TOOL-tools.md | ✅ |
| BRD-HYP-003 | Hypothesis tests MUST be toggleable | BRD-tools.md | TOOL-ANALYSIS-006 | TOOL-tools.md | ✅ |
| BRD-HYP-004 | Tests MUST return status (confirmed/rejected/skipped) | BRD-tools.md | TOOL-ANALYSIS-003 | TOOL-tools.md | ✅ |
| BRD-HYP-005 | Tests MUST provide reasoning | BRD-tools.md | TOOL-ANALYSIS-003 | TOOL-tools.md | ✅ |
| BRD-HYP-006 | Tests MUST produce evidence items | BRD-tools.md | TOOL-ANALYSIS-003 | TOOL-tools.md | ✅ |
| BRD-DRIVER-001 | System SHOULD identify key metric drivers | BRD-tools.md | TOOL-ANALYSIS-007 | TOOL-tools.md | ✅ |
| BRD-DRIVER-002 | Drivers SHOULD be ranked by contribution | BRD-tools.md | TOOL-ANALYSIS-007 | TOOL-tools.md | ✅ |
| BRD-CHART-001 | System MUST build chart specifications | BRD-tools.md | TOOL-VIZ-001 | TOOL-tools.md | ✅ |
| BRD-CHART-002 | System MUST support bar charts | BRD-tools.md | TOOL-VIZ-002 | TOOL-tools.md | ✅ |
| BRD-CHART-003 | System MUST support line charts | BRD-tools.md | TOOL-VIZ-002 | TOOL-tools.md | ✅ |
| BRD-CHART-004 | System MUST support area charts | BRD-tools.md | TOOL-VIZ-002 | TOOL-tools.md | ✅ |
| BRD-CHART-005 | System MUST support scatter charts | BRD-tools.md | TOOL-VIZ-002 | TOOL-tools.md | ✅ |
| BRD-CHART-006 | System MUST use fallback type when needed | BRD-tools.md | TOOL-VIZ-003 | TOOL-tools.md | ✅ |
| BRD-CHART-007 | Specs MUST be Vega-Lite compatible | BRD-tools.md | TOOL-VIZ-001 | TOOL-tools.md | ✅ |
| BRD-REC-001 | System SHOULD recommend chart type | BRD-tools.md | TOOL-VIZ-004 | TOOL-tools.md | ✅ |
| BRD-REC-002 | Recommendations SHOULD consider data shape | BRD-tools.md | TOOL-VIZ-004 | TOOL-tools.md | ✅ |
| BRD-PKT-001 | System MUST assemble decision packets | BRD-tools.md | TOOL-ASSEMBLE-001 | TOOL-tools.md | ✅ |
| BRD-PKT-007 | Packets MUST include evidence references | BRD-tools.md | TOOL-ASSEMBLE-003 | TOOL-tools.md | ✅ |
| BRD-PKT-008 | Packets MUST include trace references | BRD-tools.md | TOOL-ASSEMBLE-004 | TOOL-tools.md | ✅ |
| BRD-RPT-001 | System MUST assemble business reports | BRD-tools.md | TOOL-ASSEMBLE-005 | TOOL-tools.md | ✅ |
| BRD-RPT-006 | Reports MUST include recommendations | BRD-tools.md | TOOL-NARR-001 | TOOL-tools.md | ✅ |
| BRD-EVID-001 | System MUST bundle evidence items | BRD-tools.md | TOOL-ASSEMBLE-006 | TOOL-tools.md | ✅ |
| BRD-EVID-002 | Bundles MUST preserve provenance | BRD-tools.md | TOOL-ASSEMBLE-006 | TOOL-tools.md | ✅ |
| BRD-ASM-004 | Assemblers MUST include all required sections | BRD-tools.md | TOOL-ASSEMBLE-002 | TOOL-tools.md | ✅ |
| BRD-ASM-005 | Assemblers MUST validate outputs against schemas | BRD-tools.md | TOOL-ASSEMBLE-001 | TOOL-tools.md | ✅ |
| BRD-HTML-001 | System MUST render business reports as HTML | BRD-tools.md | TOOL-RENDER-001 | TOOL-tools.md | ✅ |
| BRD-HTML-002 | System MUST render decision packets as HTML | BRD-tools.md | TOOL-RENDER-002 | TOOL-tools.md | ✅ |
| BRD-HTML-003 | HTML MUST be valid HTML5 | BRD-tools.md | TOOL-RENDER-001 | TOOL-tools.md | ✅ |
| BRD-EXP-001 | System MAY export to PDF | BRD-tools.md | TOOL-RENDER-003 | TOOL-tools.md | ✅ |
| BRD-EXP-003 | Exports MUST be written to output location | BRD-tools.md | TOOL-RENDER-004 | TOOL-tools.md | ✅ |
| BRD-INTEL-001 | System MUST use multi-stage reasoning | BRD-agents.md | AGENT-REASON-001 | AGENT-agents.md | ✅ |
| BRD-INTEL-002 | Reasoning MUST have observable stages | BRD-agents.md | AGENT-REASON-002 | AGENT-agents.md | ✅ |
| BRD-INTEL-003 | Reasoning cycles MUST be bounded | BRD-agents.md | AGENT-REASON-003 | AGENT-agents.md | ✅ |
| BRD-INTEL-004 | Reasoning MUST track sufficiency state | BRD-agents.md | AGENT-REASON-004 | AGENT-agents.md | ✅ |
| BRD-INTEL-005 | Final outputs MUST state why reasoning stopped | BRD-agents.md | AGENT-REASON-005 | AGENT-agents.md | ✅ |
| BRD-CRIT-001 | System MUST run critique before finalizing | BRD-agents.md | AGENT-CRIT-001 | AGENT-agents.md | ✅ |
| BRD-CRIT-002 | Critique MUST identify evidence gaps | BRD-agents.md | AGENT-CRIT-002 | AGENT-agents.md | ✅ |
| BRD-CRIT-003 | Critique MUST be able to downgrade confidence | BRD-agents.md | AGENT-CRIT-003 | AGENT-agents.md | ✅ |
| BRD-CRIT-004 | Critique MUST remain advisory | BRD-agents.md | AGENT-CRIT-004 | AGENT-agents.md | ✅ |
| BRD-CRIT-005 | Blocking findings MUST trigger clarification/abort | BRD-agents.md | AGENT-CRIT-005 | AGENT-agents.md | ✅ |
| BRD-CRIT-006 | Critique results MUST be integrated into outcomes | BRD-agents.md | AGENT-CRIT-001 | AGENT-agents.md | ✅ |
| BRD-TOOLSEL-001 | Tool selection MUST be advisory | BRD-agents.md | AGENT-TOOLSEL-001 | AGENT-agents.md | ✅ |
| BRD-TOOLSEL-002 | Tool recommendations MAY be ranked | BRD-agents.md | AGENT-TOOLSEL-002 | AGENT-agents.md | ✅ |
| BRD-TOOLSEL-003 | Orchestrator MUST be sole authority for tool execution | BRD-agents.md | AGENT-TOOLSEL-003 | AGENT-agents.md | ✅ |
| BRD-TOOLSEL-004 | Advisory suggestions MUST NOT force execution | BRD-agents.md | AGENT-TOOLSEL-004 | AGENT-agents.md | ✅ |
| BRD-INTENT-001 | System MUST extract intent summary | BRD-agents.md | AGENT-INTENT-001 | AGENT-agents.md | ✅ |
| BRD-INTENT-002 | System MUST identify datasets | BRD-agents.md | AGENT-INTENT-004 | AGENT-agents.md | ✅ |
| BRD-INTENT-003 | System MUST identify metrics | BRD-agents.md | AGENT-INTENT-004 | AGENT-agents.md | ✅ |
| BRD-INTENT-004 | System MUST identify time window | BRD-agents.md | AGENT-INTENT-004 | AGENT-agents.md | ✅ |
| BRD-INTENT-005 | System MUST provide confidence score | BRD-agents.md | AGENT-INTENT-002 | AGENT-agents.md | ✅ |
| BRD-INTENT-006 | System MUST detect clarification needed | BRD-agents.md | AGENT-INTENT-003 | AGENT-agents.md | ✅ |
| BRD-INTENT-007 | System MUST generate clarifying questions | BRD-agents.md | AGENT-INTENT-003 | AGENT-agents.md | ✅ |
| BRD-PLANNING-001 | System MUST interpret intent from context | BRD-agents.md | AGENT-PLANNING-001 | AGENT-agents.md | ✅ |
| BRD-PLANNING-002 | System MUST support replanning | BRD-agents.md | AGENT-PLANNING-002 | AGENT-agents.md | ✅ |
| BRD-PLANGEN-001 | System MUST produce deterministic plans | BRD-agents.md | AGENT-PLAN-002 | AGENT-agents.md | ✅ |
| BRD-PLANGEN-002 | Plans MUST include required steps | BRD-agents.md | AGENT-PLAN-001 | AGENT-agents.md | ✅ |
| BRD-PLANGEN-003 | Plans MUST include tool flags | BRD-agents.md | AGENT-PLAN-001 | AGENT-agents.md | ✅ |
| BRD-PLANGEN-004 | Same inputs MUST produce same plan | BRD-agents.md | AGENT-PLAN-002 | AGENT-agents.md | ✅ |
| BRD-PROPOSAL-001 | System MUST generate plan summary | BRD-agents.md | AGENT-PROPOSAL-001 | AGENT-agents.md | ✅ |
| BRD-PROPOSAL-002 | System MUST estimate step count | BRD-agents.md | AGENT-PROPOSAL-003 | AGENT-agents.md | ✅ |
| BRD-PROPOSAL-003 | System MUST estimate execution cost | BRD-agents.md | AGENT-PROPOSAL-003 | AGENT-agents.md | ✅ |
| BRD-PROPOSAL-004 | System MUST require approval for non-trivial plans | BRD-agents.md | AGENT-PROPOSAL-002 | AGENT-agents.md | ✅ |
| BRD-SUFF-001 | System MUST assess data sufficiency | BRD-agents.md | AGENT-SUFF-001 | AGENT-agents.md | ✅ |
| BRD-SUFF-002 | System MUST provide confidence level | BRD-agents.md | AGENT-SUFF-002 | AGENT-agents.md | ✅ |
| BRD-SUFF-003 | System MUST explain confidence downgrades | BRD-agents.md | AGENT-SUFF-003 | AGENT-agents.md | ✅ |
| BRD-SUFF-004 | System SHOULD evaluate row count sufficiency | BRD-agents.md | AGENT-SUFF-004 | AGENT-agents.md | ✅ |
| BRD-SUFF-005 | System SHOULD evaluate column completeness | BRD-agents.md | AGENT-SUFF-004 | AGENT-agents.md | ✅ |
| BRD-SUFF-006 | System SHOULD evaluate data freshness | BRD-agents.md | AGENT-SUFF-004 | AGENT-agents.md | ✅ |
| BRD-NARR-001 | System MUST generate dataset summary narratives | BRD-agents.md | AGENT-DASH-001 | AGENT-agents.md | ✅ |
| BRD-NARR-002 | System MUST explain key findings | BRD-agents.md | AGENT-DASH-001 | AGENT-agents.md | ✅ |
| BRD-CONF-001 | Agent outputs MUST include confidence level | BRD-agents.md | AGENT-GEN-001 | AGENT-agents.md | ✅ |
| BRD-CONF-004 | Confidence downgrades MUST be explained | BRD-agents.md | AGENT-SUFF-003 | AGENT-agents.md | ✅ |
| BRD-CONF-005 | System MUST respect platform confidence thresholds | BRD-agents.md | AGENT-FRI-001 | AGENT-agents.md | ✅ |
| BRD-SEM-001 | System MUST interpret free-text questions | BRD-agents.md | SEM-ADAPTER-001 | AGENT-agents.md | ✅ |
| BRD-SEM-002 | Interpretation MUST extract intent and entities | BRD-agents.md | SEM-ADAPTER-003 | AGENT-agents.md | ✅ |
| BRD-SEM-003 | System MUST support all ADE intent types | BRD-agents.md | SEM-ADAPTER-004 | AGENT-agents.md | ✅ |
| BRD-SEM-004 | System MUST classify intent with confidence | BRD-agents.md | SEM-ADAPTER-005 | AGENT-agents.md | ✅ |
| BRD-SEM-005 | Interpretation MUST run before planning | BRD-agents.md | SEM-ADAPTER-001 | AGENT-agents.md | ✅ |
| BRD-INTENT-TAX-001 | System MUST support DESCRIBE_DATA intent | BRD-agents.md | SEM-INTENT-003 | AGENT-agents.md | ✅ |
| BRD-INTENT-TAX-002 | System MUST support COMPARE_PERIODS intent | BRD-agents.md | SEM-INTENT-004 | AGENT-agents.md | ✅ |
| BRD-INTENT-TAX-003 | System MUST support TREND_ANALYSIS intent | BRD-agents.md | SEM-INTENT-005 | AGENT-agents.md | ✅ |
| BRD-INTENT-TAX-004 | System MUST support ANOMALY_REVIEW intent | BRD-agents.md | SEM-INTENT-006 | AGENT-agents.md | ✅ |
| BRD-INTENT-TAX-005 | System MUST support OPEN_ENDED_ANALYSIS intent | BRD-agents.md | SEM-INTENT-007 | AGENT-agents.md | ✅ |
| BRD-INTENT-TAX-006 | Intent types MUST define field requirements | BRD-agents.md | SEM-INTENT-001 | AGENT-agents.md | ✅ |
| BRD-SEM-VAL-001 | System MUST validate semantic output | BRD-agents.md | SEM-VALIDATE-001 | AGENT-agents.md | ✅ |
| BRD-SEM-VAL-002 | Validation MUST identify missing fields | BRD-agents.md | SEM-VALIDATE-003 | AGENT-agents.md | ✅ |
| BRD-SEM-VAL-003 | Validation MUST return ASK_USER when possible | BRD-agents.md | SEM-VALIDATE-004 | AGENT-agents.md | ✅ |
| BRD-SEM-VAL-004 | Validation MUST return ABORT when needed | BRD-agents.md | SEM-VALIDATE-005 | AGENT-agents.md | ✅ |
| BRD-SEM-VAL-005 | Validation MUST compute confidence adjustment | BRD-agents.md | SEM-VALIDATE-007 | AGENT-agents.md | ✅ |
| BRD-CLARIFY-001 | System MUST generate deterministic questions | BRD-agents.md | SEM-CLARIFY-001 | AGENT-agents.md | ✅ |
| BRD-CLARIFY-002 | Questions MUST be templated (no LLM) | BRD-agents.md | SEM-CLARIFY-006 | AGENT-agents.md | ✅ |
| BRD-CLARIFY-003 | Questions MUST target missing fields | BRD-agents.md | SEM-CLARIFY-002 | AGENT-agents.md | ✅ |
| BRD-CLARIFY-004 | System MUST provide metric focus templates | BRD-agents.md | SEM-CLARIFY-003 | AGENT-agents.md | ✅ |
| BRD-CLARIFY-005 | System MUST provide time range templates | BRD-agents.md | SEM-CLARIFY-004 | AGENT-agents.md | ✅ |
| BRD-CLARIFY-006 | System MUST provide anomaly templates | BRD-agents.md | SEM-CLARIFY-005 | AGENT-agents.md | ✅ |
| BRD-ROUTER-001 | System MUST route to appropriate flow | BRD-agents.md | SEM-ROUTER-001 | AGENT-agents.md | ✅ |
| BRD-ROUTER-002 | Router MUST output flow and parameters | BRD-agents.md | SEM-ROUTER-002 | AGENT-agents.md | ✅ |
| BRD-ROUTER-003 | Router MUST use deterministic mapping | BRD-agents.md | SEM-ROUTER-003 | AGENT-agents.md | ✅ |
| BRD-ROUTER-004 | Router MUST support both flow types | BRD-agents.md | SEM-ROUTER-003 | AGENT-agents.md | ✅ |
| BRD-SEM-OBS-001 | System MUST emit trace metadata | BRD-agents.md | SEM-OBS-001 | AGENT-agents.md | ✅ |
| BRD-SEM-OBS-002 | Traces MUST include intent | BRD-agents.md | SEM-OBS-003 | AGENT-agents.md | ✅ |
| BRD-SEM-OBS-003 | Traces MUST include confidence | BRD-agents.md | SEM-OBS-004 | AGENT-agents.md | ✅ |
| BRD-SEM-OBS-004 | Traces MUST include missing fields | BRD-agents.md | SEM-OBS-005 | AGENT-agents.md | ✅ |
| BRD-SEM-OBS-005 | Traces MUST include clarifying questions | BRD-agents.md | SEM-OBS-006 | AGENT-agents.md | ✅ |
| BRD-FLOW-001 | ADE MUST provide two entry points | BRD-flows.md | FLOW-EXEC-003 | FLOW-flows.md | ✅ |
| BRD-FLOW-002 | ade_v1 flow MUST support question-first | BRD-flows.md | FLOW-V1-001 | FLOW-flows.md | ✅ |
| BRD-FLOW-003 | visualization flow MUST support dataset-first | BRD-flows.md | FLOW-VIZ-001 | FLOW-flows.md | ✅ |
| BRD-V1-001 | User MUST enter free-text question | BRD-flows.md | FLOW-ARTF-004 | FLOW-flows.md | ✅ |
| BRD-V1-003 | User MUST select dataset | BRD-flows.md | FLOW-V1-003 | FLOW-flows.md | ✅ |
| BRD-V1-004 | User MUST configure preferences | BRD-flows.md | FLOW-V1-004 | FLOW-flows.md | ✅ |
| BRD-V1-005 | User MUST approve plan | BRD-flows.md | FLOW-V1-005 | FLOW-flows.md | ✅ |
| BRD-V1-006 | System MUST produce business report | BRD-flows.md | FLOW-V1-002 | FLOW-flows.md | ✅ |
| BRD-V1-007 | User SHOULD toggle hypothesis checks | BRD-flows.md | FLOW-COND-001 | FLOW-flows.md | ✅ |
| BRD-VIZ-001 | User MUST select dataset first | BRD-flows.md | FLOW-ARTF-004 | FLOW-flows.md | ✅ |
| BRD-VIZ-002 | System MUST interpret intent | BRD-flows.md | FLOW-VIZ-002 | FLOW-flows.md | ✅ |
| BRD-VIZ-003 | User MUST configure preferences | BRD-flows.md | FLOW-INPUT-001 | FLOW-flows.md | ✅ |
| BRD-VIZ-004 | System MUST evaluate sufficiency | BRD-flows.md | FLOW-VIZ-003 | FLOW-flows.md | ✅ |
| BRD-VIZ-005 | User MUST approve plan | BRD-flows.md | FLOW-V1-005 | FLOW-flows.md | ✅ |
| BRD-VIZ-006 | System MUST produce decision packet | BRD-flows.md | FLOW-VIZ-004 | FLOW-flows.md | ✅ |
| BRD-VIZ-008 | User SHOULD toggle hypothesis checks | BRD-flows.md | FLOW-COND-001 | FLOW-flows.md | ✅ |
| BRD-PREF-001 | User MUST select chart type | BRD-flows.md | FLOW-INPUT-002 | FLOW-flows.md | ✅ |
| BRD-PREF-002 | User MUST select metric focus | BRD-flows.md | FLOW-INPUT-002 | FLOW-flows.md | ✅ |
| BRD-PREF-003 | User SHOULD toggle hypothesis | BRD-flows.md | FLOW-COND-001 | FLOW-flows.md | ✅ |
| BRD-PLAN-001 | System MUST present plan summary | BRD-flows.md | FLOW-V1-005 | FLOW-flows.md | ✅ |
| BRD-PLAN-004 | User MUST be able to approve | BRD-flows.md | FLOW-V1-005 | FLOW-flows.md | ✅ |
| BRD-PLAN-005 | User MUST be able to reject | BRD-flows.md | FLOW-V1-005 | FLOW-flows.md | ✅ |
| BRD-PLAN-007 | Plan summary MUST include objective | BRD-flows.md | FLOW-V1-006 | FLOW-flows.md | ✅ |
| BRD-PLAN-008 | Plan summary MUST include assumptions | BRD-flows.md | FLOW-V1-007 | FLOW-flows.md | ✅ |
| BRD-PLAN-009 | Replan MUST highlight changes | BRD-flows.md | FLOW-V1-008 | FLOW-flows.md | ✅ |
| BRD-DET-001 | Same inputs MUST produce same outputs | BRD-flows.md | FLOW-EXEC-001 | FLOW-flows.md | ✅ |
| BRD-DET-002 | No random variations | BRD-flows.md | FLOW-EXEC-001 | FLOW-flows.md | ✅ |
| BRD-DET-003 | Timestamps are only allowed variation | BRD-flows.md | FLOW-EXEC-001 | FLOW-flows.md | ✅ |
| BRD-CFG-001 | Flows MUST use suggest_only autonomy | BRD-flows.md | FLOW-EXEC-003 | FLOW-flows.md | ✅ |

---

## Gap Register

| BRD ID | Gap Type | Notes |
|--------|----------|-------|
| — | — | No gaps identified. |

---

## Summary

- **Total BRD Requirements**: 210
- **Covered**: 210
- **Gaps**: 0
- **Coverage**: 100%

---

## Cross-References

- **BRD Files**: [01_brd/](../01_brd/)
- **Tech Spec Files**: [02_techspec/](../02_techspec/)
