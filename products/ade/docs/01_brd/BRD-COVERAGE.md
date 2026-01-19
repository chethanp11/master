# ADE BRD Coverage Analysis

> **Document**: BRD Coverage Matrix  
> **Product**: Analytical Decision Engine (ADE)  
> **Version**: 1.1  
> **Last Updated**: 2026-01-17  
> **Status**: V1 Release

> **Purpose**: Trace ADE Developer Intent (INT-*) to ADE BRD requirements and flag gaps.

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-17 | Initial ADE intent-to-BRD coverage matrix |
| 1.1 | 2026-01-17 | Updated coverage after BRD gap fill |

## Coverage Summary

| Intent File | BRD Document | Coverage | Notes |
|-------------|--------------|----------|-------|
| [intent-overview-flows.md](../00_product_intent/intent-overview-flows.md) | [BRD-overview.md](BRD-overview.md) | ✅ Covered | Coverage derived from BRD derived-from mappings. |
| [intent-overview-flows.md](../00_product_intent/intent-overview-flows.md) | [BRD-flows.md](BRD-flows.md) | ✅ Covered | Coverage derived from BRD derived-from mappings. |
| [intent-agents-tools.md](../00_product_intent/intent-agents-tools.md) | [BRD-agents.md](BRD-agents.md) | ✅ Covered | Coverage derived from BRD derived-from mappings. |
| [intent-agents-tools.md](../00_product_intent/intent-agents-tools.md) | [BRD-tools.md](BRD-tools.md) | ✅ Covered | Coverage derived from BRD derived-from mappings. |
| [intent-data-outputs.md](../00_product_intent/intent-data-outputs.md) | [BRD-data.md](BRD-data.md) | ✅ Covered | Coverage derived from BRD derived-from mappings. |
| [intent-data-outputs.md](../00_product_intent/intent-data-outputs.md) | [BRD-outputs.md](BRD-outputs.md) | ✅ Covered | Coverage derived from BRD derived-from mappings. |
| [intent-intel-acceptance.md](../00_product_intent/intent-intel-acceptance.md) | All BRDs | ✅ Covered | Coverage derived from BRD derived-from mappings. |

---

## Coverage Matrix

### intent-overview-flows.md

| Intent ID | Intent | Source File | Section | BRD ID | Covered |
|-----------|--------|-------------|---------|--------|---------|
| INT-DET-001 | Flows must be deterministic — Reproducibility | intent-overview-flows.md | Intent | BRD-DET-001 | Covered |
| INT-DET-002 | Flows must use suggest_only autonomy — Framework compliance | intent-overview-flows.md | Intent | BRD-CFG-001 | Covered |
| INT-DET-003 | Same inputs must produce same execution — Audit requirement | intent-overview-flows.md | Intent | BRD-DET-001 | Covered |
| INT-FLOWS-001 | Provide two entry points for different analyst use cases — Flexibility for different workflows | intent-overview-flows.md | Intent | BRD-FLOW-001 | Covered |
| INT-FLOWS-002 | ade_v1 flow: analyst has a question to answer — Question-first workflow | intent-overview-flows.md | Intent | BRD-FLOW-002 | Covered |
| INT-FLOWS-003 | visualization flow: analyst has a dataset to explore — Dataset-first workflow | intent-overview-flows.md | Intent | BRD-FLOW-003 | Covered |
| INT-OBJ-001 | 100% of outputs must include evidence references — Evidence-based requirement | intent-overview-flows.md | Intent | BRD-OBJ-001 | Covered |
| INT-OBJ-002 | Same inputs must always produce same outputs — Reproducibility requirement | intent-overview-flows.md | Intent | BRD-OBJ-002 | Covered |
| INT-OBJ-003 | All plans must require explicit user approval — Human-in-the-loop requirement | intent-overview-flows.md | Intent | BRD-OBJ-003 | Covered |
| INT-OBJ-004 | All outputs must include confidence_level, assumptions, limitations — Transparency requirement | intent-overview-flows.md | Intent | BRD-OBJ-004 | Covered |
| INT-OBJ-005 | Time from question to report should be < 5 minutes — Usability target | intent-overview-flows.md | Intent | BRD-OBJ-005 | Covered |
| INT-OBJ-006 | 4+ chart types must be available — Visualization richness | intent-overview-flows.md | Intent | BRD-CHART-002, BRD-CHART-003, BRD-CHART-004, BRD-CHART-005, BRD-OBJ-006 | Covered |
| INT-OBJ-007 | Hypothesis checks must be toggleable — Analysis flexibility | intent-overview-flows.md | Intent | BRD-OBJ-007 | Covered |
| INT-OBJ-008 | Objectives and success criteria SHALL be expressed through schemas and goals, not embedded logic or heuristics — Keep objectives explicit and auditable | intent-overview-flows.md | Intent | BRD-OBJ-008 | Covered |
| INT-OVERVIEW-001 | Transform analyst questions into structured, audit-ready outputs — Core product value proposition | intent-overview-flows.md | Intent | BRD-OVERVIEW-001 | Covered |
| INT-OVERVIEW-002 | Every claim must be traceable to source data — Trust requires evidence | intent-overview-flows.md | Intent | BRD-OVERVIEW-002 | Covered |
| INT-OVERVIEW-003 | Same inputs must always produce same outputs — Audit and reproducibility requirement | intent-overview-flows.md | Intent | BRD-OVERVIEW-003 | Covered |
| INT-OVERVIEW-004 | Confidence, assumptions, and limitations must be explicit — Transparency requirement | intent-overview-flows.md | Intent | BRD-OVERVIEW-004 | Covered |
| INT-OVERVIEW-005 | Plans must require human approval before execution — Human oversight by design | intent-overview-flows.md | Intent | BRD-OVERVIEW-005 | Covered |
| INT-OVERVIEW-006 | Analyst questions must be semantically interpreted — Enable natural language interaction | intent-overview-flows.md | Intent | BRD-OVERVIEW-006 | Covered |
| INT-UI-001 | Visualization preferences must include chart_type — User control | intent-overview-flows.md | Intent | BRD-PREF-001 | Covered |
| INT-UI-002 | Visualization preferences must include metric_focus — Analysis direction | intent-overview-flows.md | Intent | BRD-METRIC-004, BRD-PREF-002 | Covered |
| INT-UI-003 | Visualization preferences must include hypothesis_enabled flag — Optional analysis | intent-overview-flows.md | Intent | BRD-PREF-003, BRD-VIZ-008 | Covered |
| INT-UI-004 | Plan approval must show plan summary — Informed decision | intent-overview-flows.md | Intent | BRD-PLAN-001 | Covered |
| INT-UI-005 | Plan approval must allow approve/reject — Human control | intent-overview-flows.md | Intent | BRD-PLAN-004, BRD-PLAN-005 | Covered |
| INT-UI-006 | Rejection must trigger replanning — Recovery path | intent-overview-flows.md | Intent | BRD-PLAN-006, BRD-PLANNING-002 | Covered |
| INT-V1-001 | User must be able to enter free-text questions — Natural language interaction | intent-overview-flows.md | Intent | BRD-V1-001 | Covered |
| INT-V1-002 | System must interpret intent from question — Semantic understanding | intent-overview-flows.md | Intent | BRD-V1-002 | Covered |
| INT-V1-003 | User must select dataset for analysis — Data source specification | intent-overview-flows.md | Intent | BRD-V1-003 | Covered |
| INT-V1-004 | User must configure visualization preferences — Customization | intent-overview-flows.md | Intent | BRD-V1-004 | Covered |
| INT-V1-005 | User must approve plan before execution — Human oversight | intent-overview-flows.md | Intent | BRD-V1-005 | Covered |
| INT-V1-006 | System must produce business report — Primary output | intent-overview-flows.md | Intent | BRD-V1-006 | Covered |
| INT-V1-007 | User should be able to enable/disable hypothesis checks — Analysis flexibility | intent-overview-flows.md | Intent | BRD-V1-007 | Covered |
| INT-V1-008 | User should be able to add notes to analysis — Documentation | intent-overview-flows.md | Intent | BRD-PREF-004, BRD-V1-008 | Covered |
| INT-VIZ-001 | User must select dataset first — Dataset-first workflow | intent-overview-flows.md | Intent | BRD-VIZ-001 | Covered |
| INT-VIZ-002 | System must interpret intent from dataset context — Intelligent interpretation | intent-overview-flows.md | Intent | BRD-PLANNING-001, BRD-VIZ-002 | Covered |
| INT-VIZ-003 | User must provide visualization preferences — Explicit preferences | intent-overview-flows.md | Intent | BRD-VIZ-003 | Covered |
| INT-VIZ-004 | System must check data sufficiency — Quality gate | intent-overview-flows.md | Intent | BRD-VIZ-004 | Covered |
| INT-VIZ-005 | User must approve plan before execution — Human oversight | intent-overview-flows.md | Intent | BRD-VIZ-005 | Covered |
| INT-VIZ-006 | System must produce decision packet — Primary output | intent-overview-flows.md | Intent | BRD-VIZ-006 | Covered |
| INT-VIZ-007 | System must also produce business report — Secondary output | intent-overview-flows.md | Intent | BRD-VIZ-007 | Covered |

### intent-agents-tools.md

| Intent ID | Intent | Source File | Section | BRD ID | Covered |
|-----------|--------|-------------|---------|--------|---------|
| INT-ANAL-001 | Detect statistical anomalies — Insight discovery | intent-agents-tools.md | Intent | BRD-ANOM-001, BRD-METRIC-001 | Covered |
| INT-ANAL-002 | Use z-score analysis — Standard methodology | intent-agents-tools.md | Intent | BRD-ANOM-002 | Covered |
| INT-ANAL-003 | Rank anomalies by severity — Prioritization | intent-agents-tools.md | Intent | BRD-ANOM-003 | Covered |
| INT-ANAL-004 | Explain anomaly reasons — Interpretation | intent-agents-tools.md | Intent | BRD-ANOM-004 | Covered |
| INT-ANAL-005 | Support hypothesis testing — Deeper analysis | intent-agents-tools.md | Intent | BRD-HYP-001, BRD-HYP-002, BRD-HYP-004, BRD-HYP-005, BRD-METRIC-002 | Covered |
| INT-ANAL-006 | Make hypothesis tests toggleable — User control | intent-agents-tools.md | Intent | BRD-HYP-003 | Covered |
| INT-ANAL-007 | Identify key metric drivers — Root cause analysis | intent-agents-tools.md | Intent | BRD-DRIVER-001, BRD-DRIVER-002 | Covered |
| INT-ASM-001 | Assemble decision packets — Primary output | intent-agents-tools.md | Intent | BRD-PKT-001 | Covered |
| INT-ASM-002 | Assemble business reports — Primary output | intent-agents-tools.md | Intent | BRD-RPT-001 | Covered |
| INT-ASM-003 | Bundle evidence items — Traceability | intent-agents-tools.md | Intent | BRD-EVID-001, BRD-EVID-003 | Covered |
| INT-ASM-004 | Include all required sections — Completeness | intent-agents-tools.md | Intent | BRD-ASM-004 | Covered |
| INT-ASM-005 | Validate against schemas — Data integrity | intent-agents-tools.md | Intent | BRD-ASM-005 | Covered |
| INT-CONF-001 | All agent outputs must include confidence level — Uncertainty transparency | intent-agents-tools.md | Intent | BRD-CONF-001 | Covered |
| INT-CONF-002 | Low confidence must trigger user clarification — Human intervention | intent-agents-tools.md | Intent | BRD-CONF-002 | Covered |
| INT-CONF-003 | Confidence thresholds must be configurable — Product flexibility | intent-agents-tools.md | Intent | BRD-CONF-003 | Covered |
| INT-CONF-004 | Confidence downgrades must be explained — Transparency | intent-agents-tools.md | Intent | BRD-CONF-004 | Covered |
| INT-CONF-005 | ADE SHALL respect platform-defined confidence thresholds and gates when requesting execution, escalation, or human input — Align product gating with platform policy | intent-agents-tools.md | Intent | BRD-CONF-005 | Covered |
| INT-DATA-001 | Read CSV datasets — Data source support | intent-agents-tools.md | Intent | BRD-DATA-001 | Covered |
| INT-DATA-002 | Extract column metadata — Schema understanding | intent-agents-tools.md | Intent | BRD-DATA-002 | Covered |
| INT-DATA-003 | Extract row data — Data access | intent-agents-tools.md | Intent | BRD-DATA-003 | Covered |
| INT-DATA-004 | Infer field types (x, y, category) — Smart defaults | intent-agents-tools.md | Intent | BRD-DATA-004 | Covered |
| INT-DATA-005 | Handle UTF-8 encoding — International support | intent-agents-tools.md | Intent | BRD-DATA-005 | Covered |
| INT-DATA-006 | Handle quoted CSV fields — Format robustness | intent-agents-tools.md | Intent | BRD-DATA-006 | Covered |
| INT-INTENT-001 | Extract intent summary from user question — Structured understanding | intent-agents-tools.md | Intent | BRD-INTENT-001 | Covered |
| INT-INTENT-002 | Identify referenced datasets — Data source identification | intent-agents-tools.md | Intent | BRD-INTENT-002 | Covered |
| INT-INTENT-003 | Identify referenced metrics — Analysis focus | intent-agents-tools.md | Intent | BRD-INTENT-003 | Covered |
| INT-INTENT-004 | Identify time window constraints — Temporal scoping | intent-agents-tools.md | Intent | BRD-INTENT-004 | Covered |
| INT-INTENT-005 | Provide confidence score (0-1) — Uncertainty quantification | intent-agents-tools.md | Intent | BRD-INTENT-005 | Covered |
| INT-INTENT-006 | Detect when clarification is needed — Avoid misinterpretation | intent-agents-tools.md | Intent | BRD-INTENT-006 | Covered |
| INT-INTENT-007 | Generate clarifying questions — User guidance | intent-agents-tools.md | Intent | BRD-INTENT-007 | Covered |
| INT-NARR-001 | Generate dataset summary narratives — Human readability | intent-agents-tools.md | Intent | BRD-NARR-001 | Covered |
| INT-NARR-002 | Explain key findings in plain language — Accessibility | intent-agents-tools.md | Intent | BRD-NARR-002 | Covered |
| INT-NARR-003 | Summarize anomalies with context — Interpretation | intent-agents-tools.md | Intent | BRD-NARR-003 | Covered |
| INT-NARR-004 | Provide recommendations — Actionability | intent-agents-tools.md | Intent | BRD-NARR-004, BRD-RPT-006 | Covered |
| INT-NARR-005 | User-facing explanations SHALL be derived from platform decision records, not regenerated narratives — Preserve decision provenance | intent-agents-tools.md | Intent | BRD-NARR-005 | Covered |
| INT-PLAN-001 | Produce deterministic plans — Reproducibility | intent-agents-tools.md | Intent | BRD-PLANGEN-001 | Covered |
| INT-PLAN-002 | Include all required analysis steps — Completeness | intent-agents-tools.md | Intent | BRD-PLANGEN-002 | Covered |
| INT-PLAN-003 | Include tool flags for conditional execution — Flexibility | intent-agents-tools.md | Intent | BRD-PLANGEN-003 | Covered |
| INT-PLAN-004 | Same inputs must produce same plan — Determinism | intent-agents-tools.md | Intent | BRD-PLANGEN-004 | Covered |
| INT-PLAN-005 | Generate human-readable plan summary — Informed approval | intent-agents-tools.md | Intent | BRD-PLAN-001, BRD-PROPOSAL-001 | Covered |
| INT-PLAN-006 | Estimate step count — User visibility | intent-agents-tools.md | Intent | BRD-PLAN-002, BRD-PROPOSAL-002 | Covered |
| INT-PLAN-007 | Estimate execution cost — Cost transparency | intent-agents-tools.md | Intent | BRD-PLAN-003, BRD-PROPOSAL-003 | Covered |
| INT-PLAN-008 | Require approval for non-trivial plans — Human oversight | intent-agents-tools.md | Intent | BRD-PROPOSAL-004 | Covered |
| INT-REND-001 | Render HTML outputs — Web-compatible output | intent-agents-tools.md | Intent | BRD-HTML-001, BRD-HTML-002 | Covered |
| INT-REND-002 | Produce valid HTML5 — Standards compliance | intent-agents-tools.md | Intent | BRD-HTML-003 | Covered |
| INT-REND-003 | Embed visualizations — Self-contained output | intent-agents-tools.md | Intent | BRD-HTML-004 | Covered |
| INT-REND-004 | Support PDF export — Alternative format | intent-agents-tools.md | Intent | BRD-EXP-001, BRD-PDF-001, BRD-PDF-002, BRD-PDF-003 | Covered |
| INT-SUFF-001 | Assess data sufficiency before analysis — Quality gate | intent-agents-tools.md | Intent | BRD-SUFF-001 | Covered |
| INT-SUFF-002 | Provide confidence level (high/medium/low) — Uncertainty communication | intent-agents-tools.md | Intent | BRD-CL-001, BRD-CL-002, BRD-SUFF-002 | Covered |
| INT-SUFF-003 | Explain confidence downgrades — Transparency | intent-agents-tools.md | Intent | BRD-SUFF-003 | Covered |
| INT-SUFF-004 | Evaluate row count sufficiency — Statistical validity | intent-agents-tools.md | Intent | BRD-SUFF-004 | Covered |
| INT-SUFF-005 | Evaluate column completeness — Data quality | intent-agents-tools.md | Intent | BRD-SUFF-005 | Covered |
| INT-SUFF-006 | Evaluate data freshness — Temporal relevance | intent-agents-tools.md | Intent | BRD-SUFF-006 | Covered |
| INT-TOOL-001 | Tools perform factual computation only — Determinism | intent-agents-tools.md | Intent | BRD-TOOL-004 | Covered |
| INT-TOOL-002 | Tools must NOT call LLMs directly — Reproducibility | intent-agents-tools.md | Intent | BRD-DET-004, BRD-TOOL-001 | Covered |
| INT-TOOL-003 | Tools must produce deterministic outputs — Audit requirement | intent-agents-tools.md | Intent | BRD-TOOL-002 | Covered |
| INT-TOOL-004 | Same inputs must produce same outputs — Reproducibility | intent-agents-tools.md | Intent | BRD-TOOL-003 | Covered |
| INT-TOOL-005 | Tools must produce evidence items — Traceability | intent-agents-tools.md | Intent | BRD-ANOM-005, BRD-HYP-006, BRD-ITEM-001, BRD-METRIC-003, BRD-TOOL-005 | Covered |
| INT-VIS-001 | Build chart specifications — Visual output | intent-agents-tools.md | Intent | BRD-CHART-001 | Covered |
| INT-VIS-002 | Support multiple chart types — Flexibility | intent-agents-tools.md | Intent | BRD-CHART-002, BRD-CHART-003, BRD-CHART-004, BRD-CHART-005, BRD-CHART-006 | Covered |
| INT-VIS-003 | Recommend appropriate chart types — Smart defaults | intent-agents-tools.md | Intent | BRD-REC-001, BRD-REC-002 | Covered |
| INT-VIS-004 | Use Vega-Lite compatible specs — Standard format | intent-agents-tools.md | Intent | BRD-CHART-007 | Covered |

### intent-data-outputs.md

| Intent ID | Intent | Source File | Section | BRD ID | Covered |
|-----------|--------|-------------|---------|--------|---------|
| INT-AUDIT-001 | All claims traceable to evidence — Trust requirement | intent-data-outputs.md | Intent | BRD-AUDIT-001, BRD-EVREF-001, BRD-PKT-007 | Covered |
| INT-AUDIT-002 | Evidence includes dataset references — Data source | intent-data-outputs.md | Intent | BRD-AUDIT-002, BRD-EVREF-002 | Covered |
| INT-AUDIT-003 | Evidence includes column references — Specificity | intent-data-outputs.md | Intent | BRD-AUDIT-003, BRD-EVREF-003 | Covered |
| INT-AUDIT-004 | Evidence verifiable against source data — Audit requirement | intent-data-outputs.md | Intent | BRD-AUDIT-004, BRD-EVREF-004 | Covered |
| INT-BR-001 | Include title — Identification | intent-data-outputs.md | Intent | BRD-BR-001 | Covered |
| INT-BR-002 | Include timestamp — Temporal reference | intent-data-outputs.md | Intent | BRD-BR-002 | Covered |
| INT-BR-003 | Include dataset_id — Data source | intent-data-outputs.md | Intent | BRD-BR-003 | Covered |
| INT-BR-004 | Include executive_summary — Key takeaways | intent-data-outputs.md | Intent | BRD-BR-004, BRD-RPT-002 | Covered |
| INT-BR-005 | Include key_findings — Detailed insights | intent-data-outputs.md | Intent | BRD-BR-005, BRD-RPT-003 | Covered |
| INT-BR-006 | Include visuals — Visual communication | intent-data-outputs.md | Intent | BRD-BR-006, BRD-RPT-004 | Covered |
| INT-BR-007 | Include anomalies — Issue identification | intent-data-outputs.md | Intent | BRD-BR-007, BRD-RPT-005 | Covered |
| INT-BR-008 | Include appendix — Supporting detail | intent-data-outputs.md | Intent | BRD-BR-008, BRD-RPT-007 | Covered |
| INT-DP-001 | Include question — Context | intent-data-outputs.md | Intent | BRD-DP-001, BRD-PKT-002 | Covered |
| INT-DP-002 | Include decision_summary — Primary output | intent-data-outputs.md | Intent | BRD-DP-002, BRD-PKT-003 | Covered |
| INT-DP-003 | Include confidence_level — Uncertainty | intent-data-outputs.md | Intent | BRD-CL-003, BRD-DP-003, BRD-PKT-004 | Covered |
| INT-DP-004 | Include assumptions — Transparency | intent-data-outputs.md | Intent | BRD-DP-004, BRD-PKT-005 | Covered |
| INT-DP-005 | Include limitations — Transparency | intent-data-outputs.md | Intent | BRD-DP-005, BRD-PKT-006 | Covered |
| INT-DP-006 | Include sections — Structure | intent-data-outputs.md | Intent | BRD-DP-006, BRD-PKT-007 | Covered |
| INT-DP-007 | Include trace_refs — Audit trail | intent-data-outputs.md | Intent | BRD-DP-007, BRD-PKT-008 | Covered |
| INT-EV-001 | Evidence includes dataset_id — Data source | intent-data-outputs.md | Intent | BRD-ITEM-004 | Covered |
| INT-EV-002 | Evidence includes columns — Specific fields | intent-data-outputs.md | Intent | BRD-ITEM-005 | Covered |
| INT-EV-003 | Evidence includes values — Actual data | intent-data-outputs.md | Intent | BRD-ITEM-006 | Covered |
| INT-EV-004 | Evidence is verifiable — Audit requirement | intent-data-outputs.md | Intent | BRD-EVID-002, BRD-ITEM-002, BRD-ITEM-003 | Covered |
| INT-FMT-001 | Accept CSV format — Standard format | intent-data-outputs.md | Intent | BRD-FMT-001 | Covered |
| INT-FMT-002 | Support UTF-8 encoding — International support | intent-data-outputs.md | Intent | BRD-FMT-002 | Covered |
| INT-FMT-003 | Parse standard CSV headers — Schema extraction | intent-data-outputs.md | Intent | BRD-FMT-003 | Covered |
| INT-FMT-004 | Handle quoted fields — Format robustness | intent-data-outputs.md | Intent | BRD-FMT-004 | Covered |
| INT-FMT-005 | Handle empty values — Data quality | intent-data-outputs.md | Intent | BRD-FMT-005 | Covered |
| INT-IF-001 | Include intent_summary — Interpretation | intent-data-outputs.md | Intent | BRD-IF-001 | Covered |
| INT-IF-002 | Include confidence_score — Uncertainty | intent-data-outputs.md | Intent | BRD-IF-002 | Covered |
| INT-IF-003 | Include blocking_required — Flow control | intent-data-outputs.md | Intent | BRD-IF-003 | Covered |
| INT-IF-004 | Include inferred_entities — Extraction | intent-data-outputs.md | Intent | BRD-IF-004 | Covered |
| INT-IF-005 | Include inferred_metrics — Extraction | intent-data-outputs.md | Intent | BRD-IF-005 | Covered |
| INT-IF-006 | Include blocking_questions — User guidance | intent-data-outputs.md | Intent | BRD-IF-006 | Covered |
| INT-LOC-001 | User datasets in staging/input/ — User data isolation | intent-data-outputs.md | Location Rules | BRD-LOC-001 | Covered |
| INT-LOC-002 | Built-in datasets in data/ — Product data | intent-data-outputs.md | Location Rules | BRD-BUILTIN-001, BRD-BUILTIN-002, BRD-LOC-002 | Covered |
| INT-LOC-003 | Dataset names resolve to file paths — Abstraction | intent-data-outputs.md | Location Rules | BRD-LOC-003 | Covered |
| INT-LOC-004 | Missing datasets produce clear errors — User guidance | intent-data-outputs.md | Location Rules | BRD-LOC-004 | Covered |
| INT-OUT-001 | Produce business_report.html — Primary output | intent-data-outputs.md | Business Report | BRD-HTML-001, BRD-OUT-001 | Covered |
| INT-OUT-002 | Report must be valid HTML5 — Standards | intent-data-outputs.md | Business Report | BRD-OUT-002, BRD-QUAL-012 | Covered |
| INT-OUT-003 | Include executive summary — Key takeaways | intent-data-outputs.md | Business Report | BRD-OUT-003 | Covered |
| INT-OUT-004 | Include key findings — Detailed insights | intent-data-outputs.md | Business Report | BRD-OUT-004 | Covered |
| INT-OUT-005 | Include visualizations — Visual communication | intent-data-outputs.md | Business Report | BRD-OUT-005, BRD-QUAL-010 | Covered |
| INT-OUT-006 | Include anomaly table — Issue identification | intent-data-outputs.md | Business Report | BRD-OUT-006, BRD-QUAL-011 | Covered |
| INT-OUT-007 | Include recommendations — Actionability | intent-data-outputs.md | Business Report | BRD-OUT-007, BRD-RPT-006 | Covered |
| INT-OUT-008 | Include appendix — Supporting detail | intent-data-outputs.md | Business Report | BRD-OUT-008 | Covered |
| INT-OUT-010 | Produce decision_packet.html — Primary output (viz flow) | intent-data-outputs.md | Decision Packet | BRD-HTML-002, BRD-OUT-010 | Covered |
| INT-OUT-011 | Packet must be valid HTML5 — Standards | intent-data-outputs.md | Decision Packet | BRD-OUT-011, BRD-QUAL-012 | Covered |
| INT-OUT-012 | Include question — Context | intent-data-outputs.md | Decision Packet | BRD-OUT-012 | Covered |
| INT-OUT-013 | Include decision summary — Primary output | intent-data-outputs.md | Decision Packet | BRD-OUT-013 | Covered |
| INT-OUT-014 | Include confidence level — Uncertainty | intent-data-outputs.md | Decision Packet | BRD-OUT-014 | Covered |
| INT-OUT-015 | Include evidence sections — Traceability | intent-data-outputs.md | Decision Packet | BRD-OUT-015 | Covered |
| INT-OUT-016 | Include assumptions — Transparency | intent-data-outputs.md | Decision Packet | BRD-OUT-016 | Covered |
| INT-OUT-017 | Include limitations — Transparency | intent-data-outputs.md | Decision Packet | BRD-OUT-017 | Covered |
| INT-OUTLOC-001 | Outputs written to staging/output/ — Organization | intent-data-outputs.md | 6.2 Output Location Intent | BRD-EXP-003, BRD-LOC-001 | Covered |
| INT-OUTLOC-002 | Create directory if missing — Robustness | intent-data-outputs.md | 6.2 Output Location Intent | BRD-LOC-002 | Covered |
| INT-OUTLOC-003 | Consistent file naming — Predictability | intent-data-outputs.md | 6.2 Output Location Intent | BRD-LOC-003 | Covered |
| INT-REPRO-001 | Same inputs produce same outputs — Audit requirement | intent-data-outputs.md | Intent | BRD-REPRO-001 | Covered |
| INT-REPRO-002 | Timestamps are only allowed variation — Practical necessity | intent-data-outputs.md | Intent | BRD-DET-003, BRD-REPRO-002 | Covered |
| INT-REPRO-003 | No random or non-deterministic operations — Reproducibility | intent-data-outputs.md | Intent | BRD-DET-002, BRD-REPRO-003 | Covered |
| INT-REPRO-004 | Outputs can be regenerated from inputs — Verification | intent-data-outputs.md | Intent | BRD-REPRO-004 | Covered |
| INT-SCHEMA-001 | All data structures use Pydantic models — Type safety | intent-data-outputs.md | General Schema Intent | BRD-SCHEMA-001, BRD-VAL-001 | Covered |
| INT-SCHEMA-002 | Schemas reject unknown fields — Data integrity | intent-data-outputs.md | General Schema Intent | BRD-SCHEMA-002, BRD-VAL-002 | Covered |
| INT-SCHEMA-003 | Schemas validate types — Error prevention | intent-data-outputs.md | General Schema Intent | BRD-SCHEMA-003, BRD-VAL-001, BRD-VAL-003 | Covered |
| INT-SCHEMA-004 | Use default factories for collections — Safe initialization | intent-data-outputs.md | General Schema Intent | BRD-SCHEMA-004 | Covered |
| INT-TRACE-001 | Outputs include trace_refs — Audit trail | intent-data-outputs.md | Intent | BRD-AUDIT-010, BRD-PKT-008, BRD-TRACE-001 | Covered |
| INT-TRACE-002 | trace_refs link to execution steps — Step traceability | intent-data-outputs.md | Intent | BRD-AUDIT-011, BRD-TRACE-002 | Covered |
| INT-TRACE-003 | trace_refs include user inputs — Input traceability | intent-data-outputs.md | Intent | BRD-AUDIT-012, BRD-TRACE-003 | Covered |
| INT-TRACE-004 | Execution must be reproducible — Audit requirement | intent-data-outputs.md | Intent | BRD-AUDIT-013, BRD-TRACE-004 | Covered |
| INT-TRANS-001 | Outputs include explicit assumptions — Transparency | intent-data-outputs.md | Intent | BRD-AUDIT-020 | Covered |
| INT-TRANS-002 | Outputs include explicit limitations — Transparency | intent-data-outputs.md | Intent | BRD-AUDIT-021 | Covered |
| INT-TRANS-003 | Confidence levels must be explained — Understanding | intent-data-outputs.md | Intent | BRD-AUDIT-022, BRD-CL-004 | Covered |
| INT-TRANS-004 | Downgrade reasons must be documented — Transparency | intent-data-outputs.md | Intent | BRD-AUDIT-023 | Covered |

### intent-intel-acceptance.md

| Intent ID | Intent | Source File | Section | BRD ID | Covered |
|-----------|--------|-------------|---------|--------|---------|
| INT-ALIGN-001 | All reasoning, iteration, critique, and governance patterns SHALL rely on framework-provided primitives — Framework leverage | intent-intel-acceptance.md | Intent | BRD-ALIGN-001 | Covered |
| INT-ALIGN-002 | If a product needs to re-implement these mechanisms, it indicates a framework gap—not a product feature — Gap detection | intent-intel-acceptance.md | Intent | BRD-ALIGN-002 | Covered |
| INT-ALIGN-003 | ADE SHALL consume platform-provided reasoning outputs without altering their structure or semantics — Preserve platform meaning | intent-intel-acceptance.md | Intent | BRD-ALIGN-003 | Covered |
| INT-CRIT-001 | Product SHALL execute a critique stage before finalizing any decision or report — Quality gate | intent-intel-acceptance.md | Intent | BRD-CRIT-001 | Covered |
| INT-CRIT-002 | Critique SHALL identify missing evidence, weak evidence, unsupported claims, and overreach — Evidence validation | intent-intel-acceptance.md | Intent | BRD-CRIT-002 | Covered |
| INT-CRIT-003 | Critique SHALL be able to downgrade confidence and record downgrade reasons — Honest uncertainty | intent-intel-acceptance.md | Intent | BRD-CRIT-003 | Covered |
| INT-CRIT-004 | Critique SHALL NEVER execute tools, route flows, or override orchestrator policies — Advisory boundary | intent-intel-acceptance.md | Intent | BRD-CRIT-004 | Covered |
| INT-CRIT-005 | Blocking critique findings SHALL force either user clarification (HITL) or a safe abort — Safe escalation | intent-intel-acceptance.md | Intent | BRD-CRIT-005 | Covered |
| INT-CRIT-006 | Critique results SHALL be integrated into outcomes, allowing confidence downgrades or blocking gaps to influence final results — Make critique actionable | intent-intel-acceptance.md | Intent | BRD-CRIT-006 | Covered |
| INT-CTX-001 | Product SHALL construct a Context Pack after ingestion and before planning or reasoning — Grounding first | intent-intel-acceptance.md | Intent | BRD-CTX-001 | Covered |
| INT-CTX-002 | Context Packs SHALL include dataset profile, coverage, missingness, data quality flags, and metric availability — Comprehensive context | intent-intel-acceptance.md | Intent | BRD-CTX-002 | Covered |
| INT-CTX-003 | All computed statistics SHALL be backed by Evidence Items included in the Context Pack — Evidence-backed | intent-intel-acceptance.md | Intent | BRD-CTX-003 | Covered |
| INT-CTX-004 | Advisory reasoning SHALL reference Context Pack artifacts, not ungrounded free text — Grounded reasoning | intent-intel-acceptance.md | Intent | BRD-CTX-004 | Covered |
| INT-CTX-005 | ADE reasoning and outputs SHALL treat Context Pack artifacts as the sole grounding source — Prevent ungrounded conclusions | intent-intel-acceptance.md | Intent | BRD-CTX-005 | Covered |
| INT-DAB-001 | ADE SHALL produce decision-support artifacts, not autonomous decisions — Human authority preserved | intent-intel-acceptance.md | Intent | BRD-DAB-005 | Covered |
| INT-DAB-002 | Final business decisions SHALL always remain with a human or downstream governed system — Accountability clarity | intent-intel-acceptance.md | Intent | BRD-DAB-002 | Covered |
| INT-DAB-003 | DecisionPackets represent recommendations with evidence and confidence, not authoritative outcomes — Semantic precision | intent-intel-acceptance.md | Intent | BRD-DAB-004 | Covered |
| INT-DAB-004 | ADE outputs SHALL be labeled as "recommendations" or "findings", never as "decisions" or "actions" — Language discipline | intent-intel-acceptance.md | Intent | BRD-DAB-001 | Covered |
| INT-DAB-005 | No ADE output SHALL trigger downstream actions without explicit human or system approval — Action boundary | intent-intel-acceptance.md | Intent | BRD-DAB-003 | Covered |
| INT-FRI-001 | Product SHALL NOT re-implement orchestration logic already provided by MASTER framework — No shadow orchestration | intent-intel-acceptance.md | Intent | BRD-FRI-001 | Covered |
| INT-FRI-002 | Product SHALL NOT re-implement iteration control already provided by MASTER framework — No shadow loops | intent-intel-acceptance.md | Intent | BRD-FRI-002 | Covered |
| INT-FRI-003 | Product SHALL NOT re-implement reasoning ladder semantics already provided by MASTER framework — No shadow reasoning | intent-intel-acceptance.md | Intent | BRD-FRI-003 | Covered |
| INT-FRI-004 | Product SHALL NOT bypass framework governance hooks — Governance integrity | intent-intel-acceptance.md | Intent | BRD-FRI-004 | Covered |
| INT-FRI-005 | Any product requirement that cannot be satisfied using existing framework primitives SHALL be treated as a framework gap and escalated, not worked around — Gap escalation | intent-intel-acceptance.md | Intent | BRD-FRI-005 | Covered |
| INT-INTEL-001 | Product SHALL reason using a multi-stage reasoning ladder rather than single-pass analysis — Depth over speed | intent-intel-acceptance.md | Intent | BRD-INTEL-001 | Covered |
| INT-INTEL-002 | Reasoning SHALL progress through explicit stages: interpretation, proposal, gated execution, critique, and finalization — Structured reasoning | intent-intel-acceptance.md | Intent | BRD-INTEL-002 | Covered |
| INT-INTEL-003 | Each reasoning cycle SHALL be bounded by explicit limits (iterations, tools, tokens, time) — Governance enforcement | intent-intel-acceptance.md | Intent | BRD-INTEL-003 | Covered |
| INT-INTEL-004 | System SHALL track sufficiency state across cycles (what is known, unknown, blocked) — State awareness | intent-intel-acceptance.md | Intent | BRD-INTEL-004 | Covered |
| INT-INTEL-005 | Final outputs SHALL explicitly state why reasoning stopped (sufficient, budget exhausted, missing inputs, or conflict) — Transparency | intent-intel-acceptance.md | Intent | BRD-INTEL-005 | Covered |
| INT-NRL-001 | ADE SHALL NOT modify its behavior, thresholds, or logic at runtime based on prior executions — No implicit adaptation | intent-intel-acceptance.md | Intent | BRD-NRL-001 | Covered |
| INT-NRL-002 | ADE SHALL NOT persist learned patterns, weights, or preferences across runs — No hidden state | intent-intel-acceptance.md | Intent | BRD-NRL-002 | Covered |
| INT-NRL-003 | All learning and evolution SHALL occur through the governed intent → BRD → implementation lifecycle — Governed evolution only | intent-intel-acceptance.md | Intent | BRD-NRL-003 | Covered |
| INT-NRL-004 | Run N SHALL produce identical outputs to Run 1 given identical inputs — Run independence | intent-intel-acceptance.md | Intent | BRD-NRL-004 | Covered |
| INT-QUAL-001 | All key findings or assertions SHALL be backed by at least one evidence reference — Evidence requirement | intent-intel-acceptance.md | Intent | BRD-QUAL-001 | Covered |
| INT-QUAL-002 | Executive summaries SHALL include scope, key result, confidence, and primary limitation — Completeness | intent-intel-acceptance.md | Intent | BRD-QUAL-002 | Covered |
| INT-QUAL-003 | Recommendations SHALL only be emitted when evidence-supported; otherwise they SHALL be omitted — No speculation | intent-intel-acceptance.md | Intent | BRD-QUAL-003 | Covered |
| INT-QUAL-004 | Low-confidence outputs SHALL include a "Next Inputs Needed" section — User guidance | intent-intel-acceptance.md | Intent | BRD-QUAL-004 | Covered |
| INT-REVIEW-001 | Plan proposals SHALL clearly present objective, steps, expected evidence, assumptions, risks, and estimated runtime — Informed consent | intent-intel-acceptance.md | Intent | BRD-PLAN-007, BRD-PLAN-008 | Covered |
| INT-REVIEW-002 | Users SHALL be able to approve plans with constraints (time window, iteration caps, disabled tests) — User control | intent-intel-acceptance.md | Intent | BRD-PLAN-010 | Covered |
| INT-REVIEW-003 | Replans after rejection SHALL explicitly show what changed and why — Transparency | intent-intel-acceptance.md | Intent | BRD-PLAN-009 | Covered |
| INT-SEM-001 | ADE SHALL provide a ProductSemanticAdapter that interprets analyst questions into structured semantic envelopes — Domain-specific interpretation | intent-intel-acceptance.md | Intent | BRD-SEM-001 | Covered |
| INT-SEM-002 | Semantic interpretation SHALL extract intent_type (DESCRIBE_DATA, COMPARE_PERIODS, TREND_ANALYSIS, ANOMALY_REVIEW, OPEN_ENDED_ANALYSIS) — Intent classification | intent-intel-acceptance.md | Intent | BRD-INTENT-TAX-001, BRD-INTENT-TAX-002, BRD-INTENT-TAX-003, BRD-INTENT-TAX-004, BRD-INTENT-TAX-005, BRD-SEM-002, BRD-SEM-003 | Covered |
| INT-SEM-003 | Semantic interpretation SHALL extract entities: metrics, time_windows, dataset_references, filter_conditions — Entity extraction | intent-intel-acceptance.md | Intent | BRD-SEM-002 | Covered |
| INT-SEM-004 | Semantic interpretation SHALL produce confidence score (0.0-1.0) indicating interpretation certainty — Uncertainty quantification | intent-intel-acceptance.md | Intent | BRD-SEM-004, BRD-SEM-VAL-005 | Covered |
| INT-SEM-005 | Low confidence (< 0.8 for ADE) SHALL trigger ASK_USER next action — Clarification threshold | intent-intel-acceptance.md | Intent | BRD-SEM-VAL-003 | Covered |
| INT-SEM-006 | Semantic validation SHALL check for required fields based on intent_type — Domain validation | intent-intel-acceptance.md | Intent | BRD-INTENT-TAX-006, BRD-SEM-VAL-002 | Covered |
| INT-SEM-007 | Missing required fields SHALL generate clarifying_questions — User guidance | intent-intel-acceptance.md | Intent | BRD-CLARIFY-001, BRD-CLARIFY-002, BRD-CLARIFY-003, BRD-CLARIFY-004, BRD-CLARIFY-005, BRD-CLARIFY-006 | Covered |
| INT-SEM-008 | Ambiguous inputs SHALL be captured in ambiguities list — Transparency | intent-intel-acceptance.md | Intent | BRD-SEM-VAL-004 | Covered |
| INT-SEM-009 | Semantic interpretation SHALL run BEFORE planning phase — Correct ordering | intent-intel-acceptance.md | Intent | BRD-ROUTER-001, BRD-ROUTER-002, BRD-ROUTER-003, BRD-ROUTER-004, BRD-SEM-005 | Covered |
| INT-SEM-010 | Semantic interpretation SHALL be traced with structured events — Observability | intent-intel-acceptance.md | Intent | BRD-SEM-OBS-001, BRD-SEM-OBS-002, BRD-SEM-OBS-003, BRD-SEM-OBS-004, BRD-SEM-OBS-005 | Covered |
| INT-SEM-VAL-001 | TREND_ANALYSIS without time_axis SHALL trigger clarifying question — Missing required field | intent-intel-acceptance.md | Validation Rules | BRD-SEM-VAL-001, BRD-SEM-VAL-003 | Covered |
| INT-SEM-VAL-002 | COMPARE_PERIODS with single time_window SHALL trigger clarifying question — Insufficient data | intent-intel-acceptance.md | Validation Rules | BRD-SEM-VAL-001, BRD-SEM-VAL-003 | Covered |
| INT-SEM-VAL-003 | Dataset references SHALL be validated against available datasets — Data availability | intent-intel-acceptance.md | Validation Rules | BRD-SEM-VAL-006 | Covered |
| INT-SEM-VAL-004 | Metric references SHALL be validated against dataset schema when known — Schema validation | intent-intel-acceptance.md | Validation Rules | BRD-SEM-VAL-007 | Covered |
| INT-SEM-VAL-005 | Validation failures SHALL produce violations list with specific field references — Actionable errors | intent-intel-acceptance.md | Validation Rules | BRD-SEM-VAL-002 | Covered |
| INT-TERM-001 | ADE SHALL emit explicit terminal outcomes: SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT — Consistent termination semantics | intent-intel-acceptance.md | Intent | BRD-TERM-001 | Covered |
| INT-TERM-002 | PARTIAL_SUCCESS outcomes SHALL state what was completed, what is missing, and why — Clear incomplete results | intent-intel-acceptance.md | Intent | BRD-TERM-002 | Covered |
| INT-TERM-003 | Terminal outcomes SHALL include required explanations and supporting artifacts — Audit-ready termination | intent-intel-acceptance.md | Intent | BRD-TERM-003 | Covered |
| INT-TOOLSEL-001 | Tool choice SHALL be surfaced as an advisory recommendation, not embedded silently in plans — Transparency | intent-intel-acceptance.md | Intent | BRD-TOOLSEL-001 | Covered |
| INT-TOOLSEL-002 | System MAY produce ranked tool suggestions with rationales and exclusions — Informed choice | intent-intel-acceptance.md | Intent | BRD-TOOLSEL-002 | Covered |
| INT-TOOLSEL-003 | Orchestrator SHALL remain the sole authority to approve or reject tool execution based on policy and budgets — Governance boundary | intent-intel-acceptance.md | Intent | BRD-TOOLSEL-003 | Covered |
| INT-TOOLSEL-004 | Advisory tool suggestions SHALL NOT force execution — Advisory only | intent-intel-acceptance.md | Intent | BRD-TOOLSEL-004 | Covered |
| INT-VER-001 | Every output SHALL include product version, flow version, schema version, and tool versions — Version tracking | intent-intel-acceptance.md | Intent | BRD-VER-001 | Covered |
| INT-VER-002 | Outputs SHALL record dataset hash (or checksum) and input parameter hash — Input traceability | intent-intel-acceptance.md | Intent | BRD-VER-002 | Covered |
| INT-VER-003 | Non-deterministic dependencies SHALL be disallowed or explicitly version-pinned — Reproducibility | intent-intel-acceptance.md | Intent | BRD-VER-003 | Covered |

## Gap Summary

| Gap Area | Missing Intent IDs | Suggested BRD Target |
|----------|--------------------|----------------------|
| None | — | — |

### Next BRD Edits Required

- [ ] None.

### Completion Line

BRD-COVERAGE GAP COUNT: 0
