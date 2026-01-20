# ADE Input/Output Technical Specification

> **Document**: Technical Specification — Inputs and Outputs  
> **Prefix**: TS-IO-*  
> **Version**: 1.4  
> **Last Updated**: 2026-01-20

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added evidence and artifact requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |
| 1.3 | 2026-01-21 | Added objective expression, output directory, and low-confidence output requirements per gap analysis. |
| 1.4 | 2026-01-20 | Converted all TSD IDs to TS- prefix; added implementation-level technical details (file paths, classes, methods, types). |

---

## 1. Product Objectives (TS-IO-OBJ)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-OBJ-001 | The ADE system MUST include evidence references in 100% of outputs. | Validation: `assert all(section.evidence_refs for section in output.sections)`; Schema: `DecisionSection.evidence_refs: List[Dict]` required | MUST | BRD-OBJ-001 | Maps to OBJ-001 |
| TS-IO-OBJ-002 | The ADE system MUST produce identical outputs for identical inputs. | Enforcement: No `random` imports; No `datetime.now()` in outputs; Determinism test: `f(x) == f(x)` for all functions | MUST | BRD-OBJ-002 | Reproducibility requirement |
| TS-IO-OBJ-003 | The ADE system MUST require explicit user approval for all plans before execution. | File: `products/ade/flows/ade_v1.yaml`; Step: `step_type: hitl`; Form: `viz_preferences` with `required: true` | MUST | BRD-OBJ-003 | — |
| TS-IO-OBJ-004 | The ADE system MUST include confidence_level, assumptions, and limitations in all outputs. | Schema: `BusinessReport.confidence_level: Literal["high", "medium", "low"]`; `BusinessReport.assumptions: List[str]`; `BusinessReport.limitations: List[str]` | MUST | BRD-OBJ-004 | Transparency fields |
| TS-IO-OBJ-005 | The ADE system SHOULD produce a report within 5 minutes of question submission. | Metric: `trace.total_duration_seconds < 300`; Logging: `core.memory.tracing.Tracer` timestamps | SHOULD | BRD-OBJ-005 | Time-to-report target |
| TS-IO-OBJ-006 | The ADE system MUST support at least 4 chart types (bar, line, area, scatter). | Enum: `ChartType = Literal["bar", "line", "area", "scatter"]`; Validation: `assert chart_type in ["bar", "line", "area", "scatter"]` | MUST | BRD-OBJ-006 | — |
| TS-IO-OBJ-007 | The ADE system MUST allow users to toggle hypothesis checks on or off. | Field: `viz_preferences.include_hypothesis_checks: bool`; Tool param: `hypothesis_test_*.enabled: bool` | MUST | BRD-OBJ-007 | — |
| TS-IO-OBJ-008 | Objectives MUST be expressed through explicit goals in configuration, not embedded logic or heuristics. | Config: `products/ade/config/goals.yaml`; No hardcoded objectives in `products/ade/agents/*.py` | MUST | BRD-OBJ-008 | — |

---

## 2. Input Payload Requirements (TS-IO-IN)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-IN-001 | The ADE payload MUST include a dataset field. | Schema: `products/ade/schemas/payload.py::ADEPayload`; Field: `dataset: str` (required); Validation: `pydantic.Field(..., min_length=1)` | MUST | BRD-FMT-001 | Required for both flows |
| TS-IO-IN-002 | The ade_v1 flow MUST accept payload fields: dataset (required), prompt (optional), intent (optional), question (optional), instructions (optional). | Schema: `ADEPayload`; Fields: `dataset: str`, `prompt: Optional[str] = None`, `intent: Optional[str] = None`, `question: Optional[str] = None`, `instructions: Optional[str] = None` | MUST | BRD-V1-001, BRD-V1-003 | — |
| TS-IO-IN-003 | The visualization flow MUST accept payload fields: dataset (required), prompt (optional). | Schema: `VisualizationPayload`; Fields: `dataset: str`, `prompt: Optional[str] = None` | MUST | BRD-VIZ-001 | — |
| TS-IO-IN-004 | The ade_v1 flow MUST accept intent from alternate fields in priority order: prompt, intent, question, instructions. | Method: `_extract_intent(payload: ADEPayload) -> str`; Logic: `return payload.prompt or payload.intent or payload.question or payload.instructions` | MUST | BRD-V1-001, BRD-V1-002 | — |

---

## 3. Dataset Requirements (TS-IO-DATA)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-DATA-001 | The ADE system MUST accept datasets in CSV format with comma delimiter. | Implementation: `pandas.read_csv(path, delimiter=",")`; Validation: `assert path.endswith(".csv")` | MUST | BRD-FMT-001 | — |
| TS-IO-DATA-002 | The ADE system MUST treat the first row of CSV files as the header row. | Implementation: `pandas.read_csv(path, header=0)` (default); Validation: `assert df.columns[0] != 0` | MUST | BRD-FMT-003 | — |
| TS-IO-DATA-003 | The ADE system MUST support UTF-8 encoding for dataset files. | Implementation: `pandas.read_csv(path, encoding="utf-8")`; Fallback: raise `EncodingError` for non-UTF-8 | MUST | BRD-FMT-002 | — |
| TS-IO-DATA-004 | The ADE system MUST read user datasets from products/ade/staging/input/. | Constant: `USER_INPUT_DIR = Path("products/ade/staging/input/")`; Resolution: `USER_INPUT_DIR / f"{dataset}.csv"` | MUST | BRD-LOC-001 | — |
| TS-IO-DATA-005 | The ADE system MUST read built-in datasets from products/ade/data/. | Constant: `BUILTIN_DATA_DIR = Path("products/ade/data/")`; Resolution: `BUILTIN_DATA_DIR / f"{dataset}.csv"` | MUST | BRD-LOC-002 | — |
| TS-IO-DATA-006 | The ADE system MUST provide the branded_cards_transactions dataset as a built-in dataset. | File: `products/ade/data/branded_cards_transactions.csv`; Validation: `assert Path("products/ade/data/branded_cards_transactions.csv").exists()` | MUST | BRD-BUILTIN-001 | — |
| TS-IO-DATA-007 | The ADE system MUST resolve dataset names to file paths using case-sensitive matching. | Logic: `path = data_dir / f"{dataset}.csv"` (no `.lower()`); Error: `DatasetNotFoundError` if not found | MUST | BRD-LOC-003 | — |
| TS-IO-DATA-008 | The ADE system MUST produce a clear error when a dataset file is missing. | Exception: `class DatasetNotFoundError(ADEError): pass`; Message: `f"Dataset '{dataset}' not found in {data_dir}"` | MUST | BRD-LOC-004 | — |

---

## 4. User Input Requirements (TS-IO-USER)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-USER-001 | The viz_preferences user input MUST validate against a schema with properties: chart_type (enum: bar, line, area, scatter), metric_focus (enum: mean, sum, median, growth_rate, anomalies), include_hypothesis_checks (boolean), notes (string). | Schema: `products/ade/schemas/viz_preferences.py::VizPreferences(BaseModel)`; Fields: `chart_type: Literal["bar", "line", "area", "scatter"]`, `metric_focus: Literal["mean", "sum", "median", "growth_rate", "anomalies"]`, `include_hypothesis_checks: bool`, `notes: Optional[str]` | MUST | BRD-PREF-001, BRD-PREF-002, BRD-PREF-003 | — |
| TS-IO-USER-002 | The viz_preferences user input MUST require chart_type and metric_focus fields. | Validation: `pydantic.Field(...)` with no default; Error: `ValidationError` if missing | MUST | BRD-PREF-001, BRD-PREF-002 | — |
| TS-IO-USER-003 | The ade_v1 flow MUST use default values: chart_type=bar, metric_focus=mean, include_hypothesis_checks=true. | Config: `products/ade/flows/ade_v1.yaml`; Defaults: `chart_type: bar`, `metric_focus: mean`, `include_hypothesis_checks: true` | MUST | BRD-PREF-001, BRD-PREF-002 | — |
| TS-IO-USER-004 | The visualization flow MUST use default values: chart_type=bar, metric_focus=anomalies, include_hypothesis_checks=true. | Config: `products/ade/flows/visualization.yaml`; Defaults: `chart_type: bar`, `metric_focus: anomalies`, `include_hypothesis_checks: true` | MUST | BRD-PREF-001, BRD-PREF-002 | — |

---

## 5. Output Requirements (TS-IO-OUT)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-OUT-001 | The ADE system MUST produce business_report.html as a primary output. | File: `products/ade/staging/output/business_report.html`; Generator: `products/ade/tools/render_report.py::render_business_report_html()` | MUST | BRD-OUT-001 | — |
| TS-IO-OUT-002 | The visualization flow MUST produce decision_packet.html as an additional output. | File: `products/ade/staging/output/decision_packet.html`; Generator: `products/ade/tools/render_packet.py::render_decision_packet_html()` | MUST | BRD-OUT-010 | — |
| TS-IO-OUT-003 | The ADE system MUST write outputs to products/ade/staging/output/. | Constant: `OUTPUT_DIR = Path("products/ade/staging/output/")`; Write: `OUTPUT_DIR / filename` | MUST | BRD-LOC-001 | — |
| TS-IO-OUT-004 | The ADE system MUST produce HTML outputs that are valid HTML5 with DOCTYPE declaration. | Validation: `assert output.startswith("<!DOCTYPE html>")`; Template: `products/ade/templates/*.html.jinja2` | MUST | BRD-OUT-002, BRD-OUT-011 | — |
| TS-IO-OUT-005 | The ADE system MUST produce well-formed HTML with no unclosed tags. | Validation: HTML parser with `html.parser` module; No parse errors | MUST | BRD-HTML-003 | — |
| TS-IO-OUT-006 | The export_pdf tool MAY produce ade.pdf, ade.html, and ade_stub.json as optional outputs. | Files: `ade.pdf`, `ade.html`, `ade_stub.json` in `OUTPUT_DIR`; Tool: `products/ade/tools/export_pdf.py::export_pdf()` | MAY | BRD-PDF-001 | — |
| TS-IO-OUT-007 | The ADE system MUST create the output directory if it does not exist before writing outputs. | Logic: `OUTPUT_DIR.mkdir(parents=True, exist_ok=True)` before any write operation | MUST | BRD-LOC-002 | — |

---

## 6. Output Quality Requirements (TS-IO-QUAL)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-QUAL-001 | The ADE system MUST produce non-empty executive summaries that reflect key findings. | Validation: `assert len(report.executive_summary) > 0`; Logic: summary derived from `findings: List[Finding]` | MUST | BRD-QUAL-001, BRD-QUAL-002 | — |
| TS-IO-QUAL-002 | The ADE system MUST produce key findings that include implications and map to evidence. | Schema: `Finding.implications: List[str]`; `Finding.evidence_refs: List[Dict]`; Validation: both non-empty | MUST | BRD-QUAL-001 | — |
| TS-IO-QUAL-003 | The ADE system SHOULD produce recommendations that include concrete actions when present. | Schema: `Recommendation.actions: List[str]`; Guidance: actions should be actionable verb phrases | SHOULD | BRD-QUAL-003 | — |
| TS-IO-QUAL-004 | The ADE system MUST produce narratives in human-readable plain-language text. | Validation: No code blocks; No JSON in narrative; Flesch reading score > 50 | MUST | BRD-NARR-002 | — |
| TS-IO-QUAL-005 | The ADE system MUST render charts using valid Vega-Lite specifications. | Schema: `ChartSpec.$schema: "https://vega.github.io/schema/vega-lite/v5.json"`; Validation: Vega-Lite validator | MUST | BRD-QUAL-010, BRD-CHART-007 | — |
| TS-IO-QUAL-006 | The ADE system MUST render tables with visible column headers and no overflow clipping. | CSS: `table th { visibility: visible; }`; `td { overflow: visible; word-wrap: break-word; }` | MUST | BRD-QUAL-011 | — |
| TS-IO-QUAL-007 | The ADE system MUST produce HTML that renders correctly in Chrome, Firefox, and Safari. | Testing: Playwright/Selenium tests in CI; Browsers: `chromium`, `firefox`, `webkit` | MUST | BRD-QUAL-012 | — |
| TS-IO-QUAL-008 | Low-confidence outputs MUST include a "Next Inputs Needed" section listing data or clarifications required to improve confidence. | Schema: `BusinessReport.next_inputs_needed: List[str]`; Condition: `if report.confidence_level == "low": assert len(report.next_inputs_needed) > 0` | MUST | BRD-QUAL-004 | — |

---

## 7. Version Transparency Requirements (TS-IO-VER)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-VER-001 | The ADE system MUST include product, flow, and schema versions in output metadata. | Schema: `OutputMetadata.product_version: str`, `flow_version: str`, `schema_version: str`; Source: `products/ade/__version__.py` | MUST | BRD-VER-001 | — |
| TS-IO-VER-002 | The ADE system SHOULD record dataset_hash and input_hash in outputs. | Schema: `OutputMetadata.dataset_hash: Optional[str]`, `input_hash: Optional[str]`; Hash: `hashlib.sha256(content).hexdigest()` | SHOULD | BRD-VER-002 | — |
| TS-IO-VER-003 | The ADE system MUST version-pin or disallow non-deterministic dependencies. | File: `requirements.txt`; Format: `package==version` (pinned); CI: `pip-compile` for lock file | MUST | BRD-VER-003 | — |

---

## 8. Decision Authority Boundary (TS-IO-DAB)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-DAB-001 | The ADE system MUST label outputs as recommendations/findings, not decisions. | Template: Use "Finding:", "Recommendation:" labels; Never use "Decision:" | MUST | BRD-DAB-001 | — |
| TS-IO-DAB-002 | The ADE decision packets MUST clarify that human authority is required for final decisions. | Template: Include disclaimer: "This analysis is advisory. Final decisions require human review and approval." | MUST | BRD-DAB-002 | — |
| TS-IO-DAB-003 | The ADE outputs MUST NOT trigger downstream actions without explicit approval. | Enforcement: No HTTP calls; No DB writes; Only file writes to `staging/output/` with `side_effect=True` | MUST | BRD-DAB-003 | — |
| TS-IO-DAB-004 | The ADE system SHOULD use confidence language that avoids implying autonomous decisions. | Language: "suggests", "indicates", "may" instead of "decides", "determines", "will" | SHOULD | BRD-DAB-004 | — |
| TS-IO-DAB-005 | The ADE system MUST present recommendations as advisory. | Template: "Recommended action:" prefix; Disclaimer in report footer | MUST | BRD-DAB-005 | — |

---

## 9. Evidence Requirements (TS-IO-EVID)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-EVID-001 | The ADE system MUST include evidence_refs in all claims (DecisionSection and Finding). | Schema: `DecisionSection.evidence_refs: List[Dict]`; `Finding.evidence_refs: List[Dict]`; Validation: non-empty | MUST | BRD-EVREF-001 | — |
| TS-IO-EVID-002 | The evidence_refs MUST include dataset_id and columns fields. | Schema: `evidence_refs: List[Dict[str, Any]]` with required keys `dataset_id: str`, `columns: List[str]` | MUST | BRD-EVREF-002, BRD-EVREF-003 | — |
| TS-IO-EVID-003 | The DecisionPacket MUST include trace_refs with step_id references and user_inputs. | Schema: `DecisionPacket.trace_refs: List[Dict]` with keys `step_id: str`, `user_inputs: Dict[str, Any]` | MUST | BRD-TRACE-001, BRD-TRACE-002, BRD-TRACE-003 | — |
| TS-IO-EVID-004 | The tools compute_business_metrics, detect_anomalies, hypothesis_test_data_outage, and hypothesis_test_seasonality MUST produce evidence_items. | Schema: Tool outputs include `evidence_items: List[EvidenceItem]`; Validation: non-empty list | MUST | BRD-ITEM-001 | — |

---

## 10. Artifact Reference Requirements (TS-IO-ARTF)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-IO-ARTF-001 | The ADE system MUST support tool output references using syntax {{artifacts.tool.<tool_name>.output.<field>}}. | Parser: `core.orchestrator.normalization.py::resolve_artifact_ref()`; Regex: `r"\{\{artifacts\.tool\.(\w+)\.output\.(\w+)\}\}"` | MUST | BRD-TRACE-002 | — |
| TS-IO-ARTF-002 | The ADE system MUST support user input references using syntax {{artifacts.user_input.<form_id>.values.<field>}}. | Parser: `resolve_artifact_ref()`; Regex: `r"\{\{artifacts\.user_input\.(\w+)\.values\.(\w+)\}\}"` | MUST | BRD-TRACE-003 | — |
| TS-IO-ARTF-003 | The ADE system MUST support agent output references using syntax {{artifacts.agent.<agent_name>.output.<field>}}. | Parser: `resolve_artifact_ref()`; Regex: `r"\{\{artifacts\.agent\.(\w+)\.output\.(\w+)\}\}"` | MUST | BRD-TRACE-002 | — |
| TS-IO-ARTF-004 | The ADE system MUST support payload references using syntax {{payload.<field>}}. | Parser: `resolve_artifact_ref()`; Regex: `r"\{\{payload\.(\w+)\}\}"` | MUST | BRD-V1-001, BRD-VIZ-001 | — |
| TS-IO-ARTF-005 | The ADE system MUST resolve all artifact references at runtime and produce clear errors for missing references. | Exception: `class ArtifactResolutionError(ADEError): pass`; Message: `f"Cannot resolve reference: {ref}"` | MUST | BRD-TRACE-004 | — |

---

## Cross-References

- **BRD**: [BRD-data.md](../01_brd/BRD-data.md), [BRD-outputs.md](../01_brd/BRD-outputs.md), [BRD-overview.md](../01_brd/BRD-overview.md)
- **System Design**: [schemas.md](../04_systemdesign/schemas.md)
