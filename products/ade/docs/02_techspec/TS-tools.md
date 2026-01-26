# ADE Tool Technical Specification

> **Document**: Technical Specification — Tools  
> **Prefix**: TS-TOOL-*  
> **Version**: 1.5  
> **Last Updated**: 2026-01-21

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added evidence item requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |
| 1.3 | 2026-01-21 | Added tool dependency and anomaly ranking requirements per gap analysis. |
| 1.4 | 2026-01-20 | Converted all TSD IDs to TS- prefix; added implementation-level technical details (file paths, classes, methods, types). |
| 1.5 | 2026-01-21 | Added V1.3 BRD coverage: TS-TOOL-INTENT-001..007 (intent-bound tool selection per BRD-TOOL-006..012). |

---

## 1. General Tool Requirements (TS-TOOL-GEN)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-TOOL-GEN-001 | ADE tools MUST NOT call LLMs directly; all reasoning delegated to agents. | Enforcement: No imports from `core.models.*` in `products/ade/tools/`; CI static check: `grep -r "from core.models" products/ade/tools/` must return empty | MUST | BRD-TOOL-001 | — |
| TS-TOOL-GEN-002 | All tools MUST have descriptors registered in `products/ade/descriptors.py` with `capabilities: List[str]`, `sensitivity: Literal["LOW", "MED", "HIGH"]`, and `cost_hint: Literal["LOW", "MED", "HIGH"]`. | File: `products/ade/descriptors.py`; Class: `ToolDescriptor(BaseModel)`; Registration: `TOOL_DESCRIPTORS: Dict[str, ToolDescriptor]` | MUST | BRD-TOOL-002 | — |
| TS-TOOL-GEN-003 | Tools MUST accurately declare `side_effect: bool` status; only `export_pdf` has `side_effect=True`. | Field: `ToolDescriptor.side_effect: bool`; Validation: `assert TOOL_DESCRIPTORS["export_pdf"].side_effect == True` | MUST | BRD-TOOL-003 | — |
| TS-TOOL-GEN-004 | Tools MUST accurately declare `read_only: bool` status; only `export_pdf` has `read_only=False`. | Field: `ToolDescriptor.read_only: bool`; Validation: `assert all(t.read_only for t in TOOL_DESCRIPTORS.values() if t.name != "export_pdf")` | MUST | BRD-TOOL-002 | — |
| TS-TOOL-GEN-005 | Tools MUST produce deterministic outputs for identical inputs; `f(x) == f(x)` for all tool functions `f`. | Enforcement: No `random` module; No `datetime.now()` in computation logic; Determinism test suite | MUST | BRD-TOOL-002, BRD-TOOL-003 | — |
| TS-TOOL-GEN-006 | Tools MUST produce `evidence_items: List[EvidenceItem]` in output for traceability. | Schema: `products/ade/schemas/evidence.py::EvidenceItem`; Field in output: `output.evidence_items: List[EvidenceItem]` | MUST | BRD-TOOL-005 | — |
| TS-TOOL-GEN-007 | Tools MUST NOT have external network dependencies; all dependencies must be local Python packages version-pinned in `requirements.txt`. | Enforcement: No `requests`, `urllib`, `httpx` imports; No socket connections; CI check: `grep -r "import requests" products/ade/tools/` | MUST | BRD-TOOL-004 | — |

---

## 1.1 Intent-Bound Tool Selection (TS-TOOL-INTENT)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-TOOL-INTENT-001 | ADE MUST bind tool selection directly to declared intent; analytical tools (anomaly detection, aggregation, visualization) SHALL only be invoked if explicitly justified by the resolved intent and constraints. | File: `products/ade/tools/tool_selector.py`; Method: `select_tools(intent: SemanticEnvelope) -> List[ToolSpec]`; Logic: each tool in result must map to `intent.intent_type` or `intent.constraints`; Validation: `assert all(t.justification in intent.dimensions for t in selected_tools)` | MUST | BRD-TOOL-006 | Intent-bound selection |
| TS-TOOL-INTENT-002 | ADE MUST reject tool execution based on mere availability; tools SHALL NOT be selected simply because they exist; every tool invocation SHALL map to an intent dimension and be auditable. | Method: `products/ade/tools/tool_selector.py::_validate_tool_justification(tool: ToolSpec, intent: SemanticEnvelope) -> bool`; Enforcement: No tool selected without `justification: str` field referencing intent dimension; Audit: `ToolInvocationRecord.intent_dimension: str` logged | MUST | BRD-TOOL-007 | No availability-based selection |
| TS-TOOL-INTENT-003 | ADE MUST never hard-code tool lists; ADE SHALL request eligible tools from the platform per run and use only what is surfaced. | Method: `products/ade/tools/tool_discovery.py::discover_eligible_tools(intent: SemanticEnvelope) -> List[str]`; Source: `core.tools.registry.get_available_tools(capabilities=intent.required_capabilities)`; No `HARDCODED_TOOLS` constant allowed | MUST | BRD-TOOL-008 | Dynamic tool discovery |
| TS-TOOL-INTENT-004 | ADE MUST bind tools to intent-derived steps; tools SHALL be invoked because intent demands them, not because they exist or are convenient. | Flow YAML: Each tool step includes `intent_justification: str`; Validation: `core.orchestrator.step_executor.validate_intent_binding(step, intent)` returns error if justification missing or invalid | MUST | BRD-TOOL-009 | Intent-derived binding |
| TS-TOOL-INTENT-005 | ADE MUST declare tool intent at call time; each tool invocation SHALL specify "why this tool" and "what intent dimension it satisfies". | Schema: `ToolInvocation(tool_name: str, inputs: Dict, intent_dimension: str, justification: str)`; Logged to: `core.memory.tracing.emit_tool_invocation()`; Audit: all fields required | MUST | BRD-TOOL-010 | Call-time intent declaration |
| TS-TOOL-INTENT-006 | ADE MUST fail if no eligible tools exist for the resolved intent; if intent cannot be satisfied with available tools, ADE SHALL stop, explain, and ask user. | Method: `products/ade/tools/tool_selector.py::select_tools(intent) -> List[ToolSpec] | TerminalOutcome`; Logic: `if len(eligible_tools) == 0: return TerminalOutcome.ASK_USER(explanation="No tools available to satisfy intent: {intent.intent_type}")` | MUST | BRD-TOOL-011 | Fail on missing tools |
| TS-TOOL-INTENT-007 | ADE MUST never infer permissions; if a tool is not discoverable from the platform, it is not usable; ADE SHALL NOT use fallback logic that bypasses platform discovery. | Enforcement: No `try/except` blocks that fall back to default tools; No `DEFAULT_TOOLS` constant; Only tools from `discover_eligible_tools()` result | MUST | BRD-TOOL-012 | No permission inference |

---

## 2. Data Tools (TS-TOOL-DATA)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-TOOL-DATA-001 | `data_reader` MUST output `DataReaderOutput` with fields: `columns: List[str]`, `rows: int`, `series: List[str]`, `data: List[Dict[str, Any]]`, `x_field: str`, `y_field: str`, `category_field: Optional[str]`. | File: `products/ade/tools/data_reader.py`; Function: `def read_dataset(dataset: str) -> DataReaderOutput`; Schema: `products/ade/schemas/data_reader_output.py` | MUST | BRD-DATA-001, BRD-DATA-002, BRD-DATA-003 | — |
| TS-TOOL-DATA-002 | `data_reader` MUST parse CSV files with: UTF-8 encoding (`encoding="utf-8"`), first row as headers, RFC 4180 quoted field handling, empty values as `None`. | Implementation: `pandas.read_csv(path, encoding="utf-8", quotechar='"', na_values=["", "NA", "null"])`; Validation: `assert df.columns.tolist() == expected_headers` | MUST | BRD-DATA-005, BRD-DATA-006 | — |
| TS-TOOL-DATA-003 | `data_reader` MUST infer field types: `x_field` (datetime/date columns), `y_field` (numeric columns: float64/int64), `category_field` (object/string columns with < 50 unique values). | Method: `_infer_field_types(df: pd.DataFrame) -> Dict[str, str]`; Logic: `x_field = first datetime column; y_field = first numeric column` | MUST | BRD-DATA-004 | — |
| TS-TOOL-DATA-004 | `compute_business_metrics` MUST output `MetricsOutput` with fields: `totals: Dict[str, float]`, `movers: List[MoverItem]`, `anomalies: List[AnomalyItem]`, `evidence_items: List[EvidenceItem]`. | File: `products/ade/tools/compute_metrics.py`; Function: `def compute_business_metrics(data: DataReaderOutput, metric_focus: str) -> MetricsOutput` | MUST | BRD-METRIC-001, BRD-METRIC-003 | — |
| TS-TOOL-DATA-005 | `compute_business_metrics` MUST respect `metric_focus: Literal["mean", "sum", "median", "growth_rate", "anomalies"]` parameter. | Parameter: `metric_focus: str`; Logic: `if metric_focus == "mean": result = df.mean(); elif metric_focus == "sum": result = df.sum(); ...` | MUST | BRD-METRIC-002, BRD-METRIC-004 | — |

---

## 3. Analysis Tools (TS-TOOL-ANALYSIS)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-TOOL-ANALYSIS-001 | `detect_anomalies` MUST use z-score analysis with configurable `threshold: float` (default 2.0). | File: `products/ade/tools/anomaly_detection.py`; Function: `def detect_anomalies(data: DataReaderOutput, threshold: float = 2.0) -> AnomalyOutput`; Formula: `z = (x - mean) / std; is_anomaly = abs(z) > threshold` | MUST | BRD-ANOM-001, BRD-ANOM-002 | — |
| TS-TOOL-ANALYSIS-002 | `detect_anomalies` MUST output `AnomalyOutput` with `anomalies: List[AnomalyRow]` and `evidence_items: List[EvidenceItem]`. | Schema: `products/ade/schemas/anomaly_output.py`; Fields: `anomalies: List[AnomalyRow]`, `evidence_items: List[EvidenceItem]` | MUST | BRD-ANOM-005 | — |
| TS-TOOL-ANALYSIS-003 | Hypothesis tools MUST output `HypothesisResult` with fields: `status: Literal["confirmed", "rejected", "skipped"]`, `reasoning: str`, `evidence_items: List[EvidenceItem]`. | Schema: `products/ade/schemas/hypothesis_result.py`; Used by: `hypothesis_test_data_outage`, `hypothesis_test_seasonality` | MUST | BRD-HYP-004, BRD-HYP-005, BRD-HYP-006 | — |
| TS-TOOL-ANALYSIS-004 | `hypothesis_test_data_outage` MUST check for outage patterns: gaps > 3x median interval, sudden drops > 50% of baseline. | File: `products/ade/tools/hypothesis_outage.py`; Function: `def hypothesis_test_data_outage(data: DataReaderOutput, enabled: bool = True) -> HypothesisResult`; Logic: `if gap > 3 * median_gap or drop > 0.5 * baseline: return confirmed` | MUST | BRD-HYP-001 | — |
| TS-TOOL-ANALYSIS-005 | `hypothesis_test_seasonality` MUST check for seasonal signals using autocorrelation at lags 7, 30, 365 days. | File: `products/ade/tools/hypothesis_seasonality.py`; Function: `def hypothesis_test_seasonality(data: DataReaderOutput, enabled: bool = True) -> HypothesisResult`; Logic: `acf = autocorrelation(data, lags=[7, 30, 365]); if max(acf) > 0.5: return confirmed` | MUST | BRD-HYP-002 | — |
| TS-TOOL-ANALYSIS-006 | Hypothesis tools MUST respect `enabled: bool` parameter; when `enabled=False`, return `HypothesisResult(status="skipped", reasoning="Hypothesis check disabled by user", evidence_items=[])`. | Parameter: `enabled: bool = True`; Logic: `if not enabled: return HypothesisResult(status="skipped", ...)` | MUST | BRD-HYP-003 | — |
| TS-TOOL-ANALYSIS-007 | `driver_analysis` SHOULD identify top-N metric drivers with `contributions: List[DriverContribution]` containing `factor: str`, `contribution_pct: float`, `direction: Literal["positive", "negative"]`. | File: `products/ade/tools/driver_analysis.py`; Function: `def driver_analysis(data: DataReaderOutput, target_metric: str, top_n: int = 5) -> DriverOutput`; Returns: ranked contributions | SHOULD | BRD-DRIVER-001, BRD-DRIVER-002 | — |
| TS-TOOL-ANALYSIS-008 | `detect_anomalies` MUST rank anomalies by severity using `severity_score: float = abs(z_score)` and return list sorted descending by severity. | Field: `AnomalyRow.severity_score: float`; Logic: `sorted(anomalies, key=lambda a: a.severity_score, reverse=True)` | MUST | BRD-ANOM-003 | — |

---

## 4. Visualization Tools (TS-TOOL-VIZ)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-TOOL-VIZ-001 | `build_chart_spec` MUST output `ChartSpec` that is Vega-Lite compatible with `$schema`, `data`, `mark`, `encoding` fields. | File: `products/ade/tools/chart_builder.py`; Function: `def build_chart_spec(data: DataReaderOutput, chart_type: str, x_field: str, y_field: str) -> ChartSpec`; Output: valid Vega-Lite JSON | MUST | BRD-CHART-001, BRD-CHART-007 | — |
| TS-TOOL-VIZ-002 | `build_chart_spec` MUST support chart types: `bar`, `line`, `area`, `scatter` via `chart_type: Literal["bar", "line", "area", "scatter"]`. | Parameter: `chart_type: str`; Mapping: `CHART_TYPE_TO_MARK = {"bar": "bar", "line": "line", "area": "area", "scatter": "point"}` | MUST | BRD-CHART-002, BRD-CHART-003, BRD-CHART-004, BRD-CHART-005 | — |
| TS-TOOL-VIZ-003 | `build_chart_spec` MUST use `fallback_chart_type: str = "bar"` when requested type is incompatible with data shape. | Logic: `if not _is_compatible(chart_type, data): chart_type = fallback_chart_type`; Compatibility: line/area require temporal x-axis | MUST | BRD-CHART-006 | — |
| TS-TOOL-VIZ-004 | `recommend_chart` SHOULD suggest chart type based on data shape using heuristic rules: temporal x → line, categorical x + single y → bar, two numeric → scatter. | File: `products/ade/tools/chart_recommender.py`; Function: `def recommend_chart(data: DataReaderOutput) -> str`; Returns: chart type string | SHOULD | BRD-REC-001, BRD-REC-002 | — |

---

## 5. Assembly Tools (TS-TOOL-ASSEMBLE)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-TOOL-ASSEMBLE-001 | `assemble_decision_packet` MUST output valid `DecisionPacket` that passes `DecisionPacket.model_validate()`. | File: `products/ade/tools/assemble_packet.py`; Function: `def assemble_decision_packet(...) -> DecisionPacket`; Validation: `DecisionPacket.model_validate(output)` | MUST | BRD-PKT-001, BRD-ASM-005 | — |
| TS-TOOL-ASSEMBLE-002 | `assemble_decision_packet` MUST include required sections: `sufficiency: DecisionSection` and `hypotheses: DecisionSection`. | Logic: `sections = [build_sufficiency_section(suff_output), build_hypotheses_section(hyp_results)]`; Validation: `assert len([s for s in sections if s.section_id in ["sufficiency", "hypotheses"]]) >= 2` | MUST | BRD-ASM-004 | — |
| TS-TOOL-ASSEMBLE-003 | `assemble_decision_packet` MUST include `evidence_refs: List[Dict]` in each `DecisionSection` with keys: `dataset_id: str`, `columns: List[str]`. | Schema: `DecisionSection.evidence_refs: List[Dict[str, Any]]`; Required keys: `{"dataset_id": str, "columns": List[str]}` | MUST | BRD-PKT-007 | — |
| TS-TOOL-ASSEMBLE-004 | `assemble_decision_packet` MUST include `trace_refs: List[Dict]` with keys: `step_id: str`, `user_inputs: Dict[str, Any]`. | Schema: `DecisionPacket.trace_refs: List[Dict[str, Any]]`; Built from: `artifacts.user_input.*` and step execution traces | MUST | BRD-PKT-008 | — |
| TS-TOOL-ASSEMBLE-005 | `assemble_business_report` MUST output valid `BusinessReport` that passes `BusinessReport.model_validate()`. | File: `products/ade/tools/assemble_report.py`; Function: `def assemble_business_report(...) -> BusinessReport`; Validation: `BusinessReport.model_validate(output)` | MUST | BRD-RPT-001, BRD-ASM-005 | — |
| TS-TOOL-ASSEMBLE-006 | `assemble_evidence_bundle` MUST aggregate `EvidenceItem` objects from multiple tool outputs with preserved `provenance: str` field. | File: `products/ade/tools/assemble_evidence.py`; Function: `def assemble_evidence_bundle(items: List[EvidenceItem]) -> EvidenceBundle`; Logic: `bundle = EvidenceBundle(items=[...], provenance_map={item.id: item.provenance for item in items})` | MUST | BRD-EVID-001, BRD-EVID-002 | — |
| TS-TOOL-ASSEMBLE-007 | `assemble_insight_card` SHOULD create `InsightCard` with fields: `headline: str`, `value: str`, `context: str`, `evidence_refs: List[Dict]`. | File: `products/ade/tools/assemble_insight.py`; Function: `def assemble_insight_card(finding: Dict, evidence: List[EvidenceItem]) -> InsightCard` | SHOULD | BRD-RPT-003 | — |
| TS-TOOL-ASSEMBLE-008 | `assemble_evidence_bundle` SHOULD deduplicate evidence items by `(dataset_id, columns, values)` tuple to avoid redundancy in outputs. | Method: `assemble_evidence_bundle._deduplicate(items: List[EvidenceItem]) -> List[EvidenceItem]`; Logic: `seen = set(); return [i for i in items if (key := (i.dataset_id, tuple(i.columns), str(i.values))) not in seen and not seen.add(key)]` | SHOULD | BRD-EVID-003 | Deduplication |

---

## 6. Rendering Tools (TS-TOOL-RENDER)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-TOOL-RENDER-001 | `render_business_report_html` MUST produce valid HTML5 with `<!DOCTYPE html>` declaration and all report sections. | File: `products/ade/tools/render_report.py`; Function: `def render_business_report_html(report: BusinessReport) -> str`; Template: `products/ade/templates/business_report.html.jinja2`; Validation: `assert output.startswith("<!DOCTYPE html>")` | MUST | BRD-HTML-001, BRD-HTML-003 | — |
| TS-TOOL-RENDER-002 | `render_decision_packet_html` MUST produce valid HTML5 with all packet sections and visible evidence references. | File: `products/ade/tools/render_packet.py`; Function: `def render_decision_packet_html(packet: DecisionPacket) -> str`; Template: `products/ade/templates/decision_packet.html.jinja2` | MUST | BRD-HTML-002, BRD-HTML-003 | — |
| TS-TOOL-RENDER-003 | `export_pdf` MAY produce multiple output formats: `ade.pdf`, `ade.html`, `ade_stub.json` to `staging/output/`. | File: `products/ade/tools/export_pdf.py`; Function: `def export_pdf(report: BusinessReport, output_dir: str) -> ExportResult`; Outputs: list of written file paths | MAY | BRD-EXP-001 | — |
| TS-TOOL-RENDER-004 | `export_pdf` MUST be the only tool with `side_effect=True`; writes files to `products/ade/staging/output/`. | Field: `TOOL_DESCRIPTORS["export_pdf"].side_effect = True`; Output path: `Path("products/ade/staging/output/")` | MUST | BRD-EXP-003 | — |
| TS-TOOL-RENDER-005 | HTML outputs SHOULD be self-contained with embedded CSS and JavaScript; no external stylesheet or script references. | Template: All CSS inlined via `<style>` tags; All JS inlined via `<script>` tags; Validation: `assert "http://" not in html_output and "https://" not in html_output` (except for Vega-Lite schema URL) | SHOULD | BRD-HTML-004 | Self-contained HTML |
| TS-TOOL-RENDER-006 | When PDF export is enabled, the exported PDF MUST include all report content (executive summary, findings, charts, anomalies, appendix). | Method: `export_pdf._validate_pdf_content(pdf: bytes, report: BusinessReport) -> bool`; Validation: PDF parser checks for all required sections | MUST | BRD-PDF-002 | PDF content completeness |
| TS-TOOL-RENDER-007 | When PDF export is enabled, the exported PDF MUST be printable on standard paper sizes (A4, Letter) with proper margins and pagination. | Config: `products/ade/config/pdf.yaml::print_settings`; Settings: `page_size: "A4"`, `margins: {top: 1in, bottom: 1in, left: 0.75in, right: 0.75in}`, `pagination: true` | MUST | BRD-PDF-003 | PDF printability |

---

## 7. Narrative Tools (TS-TOOL-NARR)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-TOOL-NARR-001 | `build_reasoning_narrative` MUST summarize run events in human-readable format (< 200 words). | File: `products/ade/tools/narrative_builder.py`; Function: `def build_reasoning_narrative(trace_events: List[TraceEvent]) -> str`; Validation: `assert len(output.split()) < 200` | MUST | BRD-RPT-006 | — |

---

## Cross-References

- **BRD**: [BRD-tools.md](../01_brd/BRD-tools.md)
- **System Design**: [agents-and-tools.md](../04_systemdesign/agents-and-tools.md)
