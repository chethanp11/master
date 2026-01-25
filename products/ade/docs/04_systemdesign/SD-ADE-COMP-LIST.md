# SD-ADE-COMP-LIST: ADE Component Reference

**Product:** Analytical Decision Engine (ADE)  
**Generated:** This document provides a comprehensive listing of all components in the ADE product.

---

## Table of Contents

1. [Root Files](#component-root-files)
2. [agents](#component-agents)
3. [tools](#component-tools)
4. [schemas](#component-schemas)
5. [utils](#component-utils)
6. [flows](#component-flows)
7. [config](#component-config)

---

## Component: Root Files

Product entry points and metadata.

### __init__.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| Package docstring | Marks directory as Python package | All ADE imports | Implicit import | When any ADE module is imported |

### manifest.yaml

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `id: ade` | Unique product identifier | ProductLoader, gateway | Parsed into ProductMeta | Product discovery at startup |
| `name` | Human-readable display name | UI navigation, API responses | Displayed in sidebar | UI rendering |
| `version` | Semantic versioning | Reproducibility tracking | Embedded in VersionMetadata | Report generation |
| `default_flow: ade_v1` | Fallback flow selection | Gateway when flow unspecified | Passed to OrchestratorEngine | Run initiation |
| `api.enabled` | API exposure control | Gateway routing | Enables /api/products/ade endpoints | Server startup |
| `api.allowed_flows` | API-accessible flows | Gateway validation | `["visualization", "ade_v1"]` | API request handling |
| `ui.enabled` | UI visibility toggle | Streamlit app | Shows/hides product in navigation | UI rendering |
| `ui.panels` | UI panel configuration | Streamlit pages | Configures runner/runs/approvals tabs | UI rendering |
| `flows` | Flow enumeration | FlowLoader, gateway | Lists available flows for product | Product discovery |

### registry.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `register(registries)` | Product registration entrypoint | `core/utils/product_loader.py` | `register(RegistrationContext(...))` | Application startup |
| `auto_register_product()` | Auto-discovers @agent/@tool decorated classes | Internal | Scans agents/ and tools/ directories | Called by register() |

### descriptors.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DATA_READER_DESC` | ToolDescriptor for data_reader | Tool selection, governance | `ToolDescriptor(...)` with capabilities | Planning and cost estimation |
| `BUILD_CHART_SPEC_DESC` | ToolDescriptor for build_chart_spec | Tool selection | Defines visualization capability | Chart building decisions |
| `RECOMMEND_CHART_DESC` | ToolDescriptor for recommend_chart | Tool selection | Recommends chart types | Visualization planning |
| `DETECT_ANOMALIES_DESC` | ToolDescriptor for detect_anomalies | Tool selection | Statistical analysis capability | Anomaly detection |
| `DRIVER_ANALYSIS_DESC` | ToolDescriptor for driver_analysis | Tool selection | Root cause capability | Driver identification |
| `ASSEMBLE_INSIGHT_CARD_DESC` | ToolDescriptor for insight card assembly | Tool selection | Report building capability | Card assembly |
| `ASSEMBLE_DECISION_PACKET_DESC` | ToolDescriptor for packet assembly | Tool selection | Decision support capability | Packet assembly |
| `ASSEMBLE_EVIDENCE_BUNDLE_DESC` | ToolDescriptor for evidence bundling | Tool selection | Evidence aggregation | Bundle creation |
| `BUILD_REASONING_NARRATIVE_DESC` | ToolDescriptor for narrative building | Tool selection | Explanation generation | Narrative creation |
| `COMPUTE_BUSINESS_METRICS_DESC` | ToolDescriptor for metrics computation | Tool selection | Business metrics capability | Metrics calculation |
| `ASSEMBLE_BUSINESS_REPORT_DESC` | ToolDescriptor for report assembly | Tool selection | Report generation | Final report creation |
| `EXPORT_PDF_DESC` | ToolDescriptor for PDF export | Tool selection | Export capability with side_effect=True | PDF generation |
| `RENDER_BUSINESS_REPORT_HTML_DESC` | ToolDescriptor for HTML rendering | Tool selection | HTML generation | Report rendering |
| `RENDER_DECISION_PACKET_HTML_DESC` | ToolDescriptor for packet HTML | Tool selection | HTML generation | Packet rendering |
| `HYPOTHESIS_DATA_OUTAGE_DESC` | ToolDescriptor for outage testing | Tool selection | Hypothesis testing | Data quality check |
| `HYPOTHESIS_SEASONALITY_DESC` | ToolDescriptor for seasonality testing | Tool selection | Pattern detection | Seasonality analysis |
| `DASHBOARD_AGENT_DESC` | AgentDescriptor for dashboard_agent | Agent selection | Visualization coordination | Dashboard generation |
| `INTENT_AGENT_DESC` | AgentDescriptor for intent_agent | Agent selection | NLU capability | Intent parsing |
| `PLAN_AGENT_DESC` | AgentDescriptor for plan_agent | Agent selection | Planning capability | Plan creation |
| `PLAN_PROPOSAL_AGENT_DESC` | AgentDescriptor for plan proposal | Agent selection | Approval workflow | Plan proposal |
| `PLANNING_AGENT_DESC` | AgentDescriptor for planning_agent | Agent selection | Workflow orchestration | High-level planning |
| `SUFFICIENCY_EVALUATOR_DESC` | AgentDescriptor for sufficiency evaluator | Agent selection | Data quality assessment | Sufficiency check |
| `CRITIC_EVALUATOR_DESC` | AgentDescriptor for critic evaluator | Agent selection | Evidence review | Critique evaluation |
| `TOOL_DESCRIPTORS` | Dict mapping tool names to descriptors | Governance, cost estimation | `TOOL_DESCRIPTORS["data_reader"]` | Tool lookup |
| `AGENT_DESCRIPTORS` | Dict mapping agent names to descriptors | Governance, cost estimation | `AGENT_DESCRIPTORS["intent_agent"]` | Agent lookup |

---

## Component: agents

Agent implementations for the ADE analytical pipeline.

### critic_evaluator.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `CriticOutput` | Pydantic model for critique results | CriticEvaluator.run() return | Schema with gaps, confidence, blocking, actions | Critique completion |
| `_extract_confidence_level()` | Extract confidence from payload | Internal | Defaults to "medium" if missing | During critique |
| `_is_valid_plan()` | Check if plan has valid steps | Internal | Validates plan payload | Evidence gap analysis |
| `_build_evidence_gaps()` | Aggregate evidence gaps from inputs | Internal | Combines sufficiency, plan, data issues | Gap identification |
| `CriticEvaluator` | Agent evaluating evidence before outputs | Flow step `critic_eval` | `agent.run(run_ctx, inputs)` | After plan_proposal, before report |
| `create_critic_evaluator()` | Factory function | Agent registry | Returns CriticEvaluator instance | Registry lookup |

### dashboard_agent.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DashboardAgentParams` | Configuration for dashboard generation | DashboardAgent validation | Pydantic model with template | Agent input |
| `DashboardAgentOutput` | Output schema for dashboard | DashboardAgent return | Message, insight, summary, interpretation | Agent output |
| `DashboardAgent` | Creates narrative summary for visual insights | Flow visualization steps | `agent.run(run_ctx, inputs)` | After data/anomaly analysis |
| `create_dashboard_agent()` | Factory function | Agent registry | Returns DashboardAgent instance | Registry lookup |

### intent_agent.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `IntentAgentInput` | Input schema for intent parsing | IntentAgent validation | Pydantic model | Agent input |
| `IntentAgent._classify_question_type()` | Classify question (explain_drop, trend, etc.) | Internal | Keyword matching | Intent classification |
| `IntentAgent._extract_metrics()` | Extract metric names from text | Internal | Keyword matching | Metric extraction |
| `IntentAgent._extract_entities()` | Extract dataset/file references | Internal | Regex patterns | Entity extraction |
| `IntentAgent._extract_time_window()` | Extract time expressions | Internal | Pattern matching | Time parsing |
| `IntentAgent._extract_output_formats()` | Determine output formats requested | Internal | Keyword matching | Format detection |
| `IntentAgent._build_blocking_question()` | Build clarifying question | Internal | Missing field check | When blocking required |
| `IntentAgent` | Interprets analyst intent into IntentFrame | Flow step first position | `agent.run(run_ctx, inputs)` | First step in flow |
| `create_intent_agent()` | Factory function | Agent registry | Returns IntentAgent instance | Registry lookup |

### plan_agent.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `PlanAgentInput` | Input schema with replan notes | PlanAgent validation | Pydantic model | Agent input |
| `PlanAgent._classify_question_type()` | Classify for tool selection | Internal | Same as IntentAgent | Planning |
| `PlanAgent` | Builds deterministic PlanSpec | Flow after intent | `agent.run(run_ctx, inputs)` | After intent interpretation |
| `create_plan_agent()` | Factory function | Agent registry | Returns PlanAgent instance | Registry lookup |

### plan_proposal_agent.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `PlanProposalAgentInput` | Input schema with revision notes | PlanProposalAgent validation | Pydantic model | Agent input |
| `PlanProposalAgent._extract_plan_agent_output()` | Safely get plan agent output | Internal | Artifact extraction | During proposal |
| `PlanProposalAgent` | Generates ActionPlanProposal for approval | Flow step `plan_proposal` | `agent.run(run_ctx, inputs)` | After plan_agent |
| `create_plan_proposal_agent()` | Factory function | Agent registry | Returns PlanProposalAgent instance | Registry lookup |

### planning_agent.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `PlanningAgentInput` | Input with replan_notes and continuation | PlanningAgent validation | Pydantic model | Agent input |
| `PlanningAgent._build_analysis_plan()` | Build analysis plan structure | Internal | Creates baseline, attribution, seasonality | During planning |
| `PlanningAgent._resolve_user_form_input()` | Get user form responses | Internal | Artifact lookup | Preference resolution |
| `PlanningAgent._resolve_viz_preference()` | Get specific viz preference | Internal | Form value extraction | Visualization config |
| `PlanningAgent` | High-level planning with replan support | Flow start or after rejection | `agent.run(run_ctx, inputs)` | Initial or replan scenarios |
| `create_planning_agent()` | Factory function | Agent registry | Returns PlanningAgent instance | Registry lookup |

### sufficiency_evaluator.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `MIN_ROWS` | Minimum rows constant (30) | Sufficiency logic | Threshold check | Row validation |
| `MIN_TIME_POINTS` | Minimum time points (12) | Sufficiency logic | Threshold check | Time series validation |
| `MAX_CV` | Max coefficient of variation (0.6) | Sufficiency logic | Variance stability | Data quality check |
| `SufficiencyOutput` | Output schema with score, level, status | Evaluator return | Pydantic model | Evaluation result |
| `_extract_numeric_values()` | Extract numbers from time series | Internal | Value parsing | Variance calculation |
| `_check_variance_stability()` | Check CV within acceptable range | Internal | `cv <= MAX_CV` | Stability check |
| `evaluate_data_sufficiency()` | Core evaluation logic | SufficiencyEvaluator.run() | Checks rows, time, variance | Main evaluation |
| `SufficiencyEvaluator` | Evaluates data sufficiency without LLM | Flow step `sufficiency_eval` | `agent.run(run_ctx, inputs)` | After data reading |
| `create_sufficiency_evaluator()` | Factory function | Agent registry | Returns SufficiencyEvaluator instance | Registry lookup |

---

## Component: tools

Tool implementations for data processing, analysis, and rendering.

### data_reader.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DataReaderInput` | Input schema with dataset_id | DataReaderTool validation | Pydantic model | Tool input |
| `DataReaderTool` | Reads and parses CSV datasets | Flow step `read` (first) | `tool.run(params, ctx)` | First tool in flow |
| `_resolve_dataset_path()` | Find dataset file path | Internal | Checks data dir, input_dir, staging | Path resolution |
| `_is_numeric()` | Check if string is numeric | Internal | Column classification | Field detection |
| `_clean_cell()` | Clean cell value | Internal | Strip quotes, convert numbers | CSV parsing |
| `_normalize_row()` | Match row to column count | Internal | Handle overflow/underflow | Row processing |
| `_parse_csv()` | Parse CSV file | Internal | Returns (columns, rows, count) | File loading |
| `create_data_reader()` | Factory function | Tool registry | Returns DataReaderTool instance | Registry lookup |

### compute_business_metrics.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ComputeBusinessMetricsInput` | Input schema with data and options | Tool validation | Pydantic model | Tool input |
| `PeriodStats` | Period statistics container | Output structure | Dataclass | Metrics output |
| `ExpenseMover` | Top mover data structure | Output structure | Dataclass | Delta analysis |
| `Anomaly` | Anomaly detection result | Output structure | Dataclass | Outlier output |
| `ComputeBusinessMetricsOutput` | Full metrics output | Tool return | Pydantic model | Metrics result |
| `_to_float()` | Convert to float | Internal | Handle commas, formats | Value parsing |
| `_deduplicate_rows()` | Remove duplicate rows | Internal | Tuple key dedup | Data cleaning |
| `_percentile()` | Calculate percentile | Internal | Linear interpolation | IQR calculation |
| `compute_business_metrics()` | Core metrics computation | Tool run | Totals, means, movers, anomalies | Main logic |
| `ComputeBusinessMetricsTool` | Deterministic metrics computation | Flow step | `tool.run(params, ctx)` | After data reading |
| `create_compute_business_metrics()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### detect_anomalies.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `Point` | Time series point | Input/output | ts + value | Data structure |
| `DetectAnomaliesInput` | Input with series and thresholds | Tool validation | Pydantic model | Tool input |
| `DetectedAnomaly` | Anomaly result with severity | Output | ts, value, zscore, severity_score | Detection output |
| `DetectAnomaliesOutput` | Output with anomalies and summary | Tool return | Pydantic model | Tool result |
| `TableData` | Alternative table input | Nested input | columns + rows | Table-based input |
| `detect_anomalies()` | Z-score anomaly detection | Tool run | Sorts by severity descending | Main logic |
| `DetectAnomaliesTool` | Statistical outlier detection | Flow step `compute_anomalies` | `tool.run(params, ctx)` | Parallel with hypothesis tests |
| `_table_to_series()` | Convert table to series | Internal | Aggregate numeric columns | Table fallback |
| `_detect_anomalies_per_row()` | Per-row anomaly detection | Internal | Non-series path | Table processing |
| `_safe_float()` | Safe float conversion | Internal | Handle parse errors | Value processing |
| `create_detect_anomalies()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### build_chart_spec.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ChartType` | Literal type for valid charts | Type annotation | line, bar, area, etc. | Schema validation |
| `InputChartType` | Input type including "auto" | Input validation | Allows automatic selection | Tool input |
| `TableDataInput` | Table structure validation | Input schema | columns + rows with length check | Data validation |
| `BuildChartSpecInput` | Input schema | Tool validation | Pydantic model | Tool input |
| `BuildChartSpecOutput` | Output with chart_spec | Tool return | chart_spec dict, summary, caveats | Tool result |
| `build_chart_spec()` | Create chart specification | Tool run | Vega-lite style spec | Main logic |
| `BuildChartSpecTool` | Builds visualization specs | Flow step `build_chart_spec` | `tool.run(params, ctx)` | After data processing |
| `create_build_chart_spec()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### recommend_chart.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `RecommendChartInput` | Input with data characteristics | Tool validation | has_time, has_category, etc. | Tool input |
| `RecommendChartOutput` | Output with recommendation | Tool return | chart_type, rationale, caveats | Tool result |
| `recommend_chart()` | Heuristic chart recommendation | Tool run | time→line, xy→scatter, etc. | Main logic |
| `RecommendChartTool` | Recommends chart types | Referenced in planning | `tool.run(params, ctx)` | Before build_chart_spec |
| `create_recommend_chart()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### context_pack_builder.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ContextPackBuilderInput` | Input with dataset info | Tool validation | dataset_id, columns, rows | Tool input |
| `ContextPackBuilderOutput` | Output wrapping ContextPack | Tool return | Pydantic model | Tool result |
| `_compute_missingness()` | Calculate null percentages | Internal | Per-column coverage | Analysis |
| `_identify_numeric_columns()` | Find numeric columns | Internal | Column classification | Schema analysis |
| `_is_numeric()` | Check if parseable as float | Internal | Value testing | Column check |
| `build_context_pack()` | Build dataset profile | Tool run | Quality flags, coverage | Main logic |
| `ContextPackBuilderTool` | Creates dataset context | Flow step `context_pack` | `tool.run(params, ctx)` | Early in flow |
| `create_context_pack_builder()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### assemble_insight_card.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ChartTypeInput` | Literal for valid chart types | Type annotation | line, bar, etc. | Schema validation |
| `AssembleInsightCardInput` | Input with card components | Tool validation | Pydantic model | Tool input |
| `AssembleInsightCardOutput` | Output wrapping InsightCard | Tool return | Pydantic model | Tool result |
| `assemble_insight_card()` | Create insight card | Tool run | Combines spec, metrics, narrative | Main logic |
| `AssembleInsightCardTool` | Assembles visualization cards | Flow step | `tool.run(params, ctx)` | After chart spec |
| `_compute_primary_metric()` | Compute aggregate metric | Internal | sum/mean/median/min/max | Metric calculation |
| `_safe_float()` | Safe float conversion | Internal | Value parsing | Data processing |
| `create_assemble_insight_card()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### assemble_decision_packet.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `AssembleDecisionPacketInput` | Input with sections and metadata | Tool validation | Pydantic model | Tool input |
| `AssembleDecisionPacketOutput` | Output wrapping DecisionPacket | Tool return | Pydantic model | Tool result |
| `assemble_decision_packet()` | Create decision packet | Tool run | Deterministic assembly | Main logic |
| `AssembleDecisionPacketTool` | Assembles structured decisions | Flow step | `tool.run(params, ctx)` | After critique |
| `create_assemble_decision_packet()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### assemble_evidence_bundle.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `AssembleEvidenceBundleInput` | Input with evidence items | Tool validation | Pydantic model | Tool input |
| `AssembleEvidenceBundleOutput` | Output wrapping EvidenceBundle | Tool return | Pydantic model | Tool result |
| `_flatten_items()` | Flatten nested evidence lists | Internal | Recursive flattening | Data processing |
| `assemble_evidence_bundle()` | Aggregate evidence items | Tool run | Bundle with summary stats | Main logic |
| `AssembleEvidenceBundleTool` | Bundles evidence items | Flow step | `tool.run(params, ctx)` | After all analysis |
| `create_assemble_evidence_bundle()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### assemble_business_report.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `AssembleBusinessReportInput` | Input with metrics and packet | Tool validation | Pydantic model | Tool input |
| `AssembleBusinessReportOutput` | Output wrapping BusinessReport | Tool return | Pydantic model | Tool result |
| `_format_number()` | Format with comma separators | Internal | Display formatting | Report building |
| `_rows_to_series()` | Convert rows to chart series | Internal | Visual data prep | Chart building |
| `_validate_visual_spec()` | Validate visual has data | Internal | Quality check | Before return |
| `_ensure_report_quality()` | Validate report completeness | Internal | Summary, findings, evidence | Quality gate |
| `assemble_business_report()` | Create full report | Tool run | Executive summary, visuals, recommendations | Main logic |
| `AssembleBusinessReportTool` | Creates business reports | Flow step near end | `tool.run(params, ctx)` | After packet assembly |
| `create_assemble_business_report()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### render_business_report_html.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `RenderBusinessReportHtmlInput` | Input with report and options | Tool validation | Pydantic model | Tool input |
| `RenderBusinessReportHtmlOutput` | Output with HTML and files | Tool return | html, output_files | Tool result |
| `_escape_html()` | HTML entity escaping | Internal | Safe text rendering | HTML generation |
| `_heatmap_minmax()` | Calculate heatmap color range | Internal | Visual rendering | Color scaling |
| `_render_heatmap_cell()` | Generate styled heatmap cell | Internal | Table rendering | Cell styling |
| `render_business_report_html()` | Generate analyst-ready HTML | Tool run | Plotly charts, responsive CSS | Main logic |
| `RenderBusinessReportHtmlTool` | Renders reports as HTML | Flow step final | `tool.run(params, ctx)` | Last step |
| `create_render_business_report_html()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### render_decision_packet_html.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `RenderDecisionPacketHtmlInput` | Input with packet and options | Tool validation | Pydantic model | Tool input |
| `RenderDecisionPacketHtmlOutput` | Output with HTML and narrative | Tool return | html, output_files, reasoning_narrative | Tool result |
| `_escape()` | HTML entity escaping | Internal | Safe text rendering | HTML generation |
| `_render_table()` | Generate HTML table | Internal | Data display | Table rendering |
| `_render_visual()` | Render chart or table visual | Internal | Section visuals | Visual embedding |
| `_extract_user_inputs()` | Get inputs from trace refs | Internal | Context extraction | Selections display |
| `render_decision_packet_html()` | Generate packet HTML | Tool run | Summary, sections, reasoning | Main logic |
| `RenderDecisionPacketHtmlTool` | Renders packets as HTML | Flow step | `tool.run(params, ctx)` | After packet assembly |
| `create_render_decision_packet_html()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### hypothesis_test_data_outage.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `HypothesisTestDataOutageInput` | Input with series and thresholds | Tool validation | Pydantic model | Tool input |
| `HypothesisTestDataOutageOutput` | Output with status and reasoning | Tool return | hypothesis_name, status, reasoning | Tool result |
| `test_data_outage()` | Test for data outage hypothesis | Tool run | Zero ratio analysis | Main logic |
| `HypothesisTestDataOutageTool` | Detects potential data outages | Flow step | `tool.run(params, ctx)` | Parallel analysis |
| `create_hypothesis_test_data_outage()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### hypothesis_test_seasonality.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `HypothesisTestSeasonalityInput` | Input with series and period | Tool validation | Pydantic model | Tool input |
| `_calculate_seasonality_strength()` | Calculate period bucket CV | Internal | Periodicity detection | Seasonality check |
| `test_seasonality()` | Test for seasonal patterns | Tool run | Bucket variance analysis | Main logic |
| `HypothesisTestSeasonalityTool` | Detects seasonal signals | Flow step | `tool.run(params, ctx)` | Parallel analysis |
| `create_hypothesis_test_seasonality()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### driver_analysis.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `SegmentRow` | Before/after segment comparison | Input structure | segment, before, after | Analysis input |
| `DriverAnalysisInput` | Input with rows and top_k | Tool validation | Pydantic model | Tool input |
| `DriverResult` | Identified driver contribution | Output structure | segment, delta, contribution_pct | Analysis output |
| `DriverAnalysisOutput` | Output with drivers and summary | Tool return | Pydantic model | Tool result |
| `driver_analysis()` | Compute driver contributions | Tool run | Delta and percentage calculation | Main logic |
| `DriverAnalysisTool` | Root cause analysis | Referenced in planning | `tool.run(params, ctx)` | Segment comparison |
| `create_driver_analysis()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### evidence_utils.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `hash_inputs()` | SHA256 hash of parameters | Multiple tools | `hash_inputs({"key": value})` | Evidence creation |
| `now_utc()` | Current UTC timestamp | Multiple tools | `now_utc()` → ISO string | Timestamping |
| `make_evidence_id()` | Deterministic evidence ID | Multiple tools | `make_evidence_id(kind, step, hash)` | Evidence tracking |

### export_pdf.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ExportPdfInput` | Input with cards and format | Tool validation | Pydantic model | Tool input |
| `ExportPdfOutput` | Output with file list | Tool return | output_files with base64 | Tool result |
| `export_pdf()` | Generate PDF/HTML artifacts | Tool run | PIL for PDF, HTML builder | Main logic |
| `ExportPdfTool` | Exports to PDF/HTML (side_effect=True) | Optional final step | `tool.run(params, ctx)` | When export requested |
| `create_export_pdf()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

### export_rendering.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `render_cards_to_pdf_pages()` | Generate PDF pages from cards | export_pdf.py | PIL image generation | PDF creation |
| `_render_chart_on_image()` | Render chart onto PIL image | Internal | Chart type dispatch | Visual rendering |
| `_render_bar_chart()` | Bar chart rendering | Internal | PIL drawing | Bar charts |
| `_render_line_chart()` | Line chart rendering | Internal | PIL drawing | Line charts |
| `_render_scatter_chart()` | Scatter plot rendering | Internal | PIL drawing | Scatter plots |
| `_render_stacked_bar_chart()` | Stacked bar rendering | Internal | PIL drawing | Composition charts |
| `_render_table_image()` | Table as image | Internal | PIL drawing | Table fallback |
| `make_stub_payload()` | Create JSON stub | export_pdf.py | Stub generation | JSON export |
| `_transform_card_to_stub()` | Card to stub format | Internal | Data transformation | Stub building |
| `_extract_columns_rows()` | Extract data from spec | Internal | Data extraction | Insight building |
| `_compute_insights()` | Compute anomaly/trend insights | Internal | Analysis | Card enhancement |
| `generate_interactive_html()` | Generate HTML with JavaScript | export_pdf.py | HTML generation | Export |

### build_reasoning_narrative.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `BuildReasoningNarrativeInput` | Input with run identifiers | Tool validation | Pydantic model | Tool input |
| `BuildReasoningNarrativeOutput` | Output with narrative and steps | Tool return | Pydantic model | Tool result |
| `_load_events()` | Load JSONL events file | Internal | File I/O | Event loading |
| `_summarize_events()` | Parse events into narrative | Internal | Event processing | Summarization |
| `BuildReasoningNarrativeTool` | Generates reasoning summary | Explainability | `tool.run(params, ctx)` | After run completion |
| `create_build_reasoning_narrative()` | Factory function | Tool registry | Returns tool instance | Registry lookup |

---

## Component: schemas

Pydantic schema definitions for ADE data structures.

### business_report.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `Finding` | Key finding with headline and evidence | BusinessReport.findings | Pydantic model | Report assembly |
| `VisualSpec` | Visualization specification | BusinessReport.visuals | Pydantic model | Chart embedding |
| `AnomalyRow` | Anomaly table row | BusinessReport.anomalies | Pydantic model | Anomaly display |
| `Appendix` | Report metadata and limitations | BusinessReport.appendix | Pydantic model | Report metadata |
| `BusinessReport` | Top-level report artifact | assemble_business_report, rendering | Pydantic model | Final output |

### card.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `KeyMetric` | Named metric value | InsightCard.key_metrics | Pydantic model | Metric display |
| `InsightCard` | Complete visualization card | Multiple tools, export | Pydantic model | Visualization |

### citations.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `CsvCitation` | Reference to CSV data | CitationRef | Pydantic model | Data provenance |
| `PdfCitation` | Reference to PDF document | CitationRef | Pydantic model | Document provenance |
| `CitationRef` | Polymorphic citation | InsightCard.citations | Pydantic model | Source linking |

### context_pack.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ContextPackEvidenceItem` | Evidence reference in pack | ContextPack.evidence_refs | Pydantic model | Evidence linking |
| `ContextPack` | Dataset context container | context_pack_builder, evidence | Pydantic model | Context tracking |

### decision_packet.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DecisionPacket` | Top-level decision artifact | assemble_decision_packet, rendering | Pydantic model | Decision output |

### decision_section.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DecisionSection` | Section within decision packet | DecisionPacket.sections | Pydantic model | Section structure |

### evidence.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `EvidenceItemBase` | Base evidence with common fields | Specialized evidence types | Pydantic model | Base class |
| `TrendEvidence` | Evidence for trend analysis | compute_business_metrics | Pydantic model | Trend results |
| `OutlierEvidence` | Evidence for outlier detection | detect_anomalies | Pydantic model | Anomaly results |
| `DataQualityEvidence` | Evidence for data quality | context_pack_builder | Pydantic model | Quality assessment |
| `HypothesisEvidence` | Evidence for hypothesis tests | hypothesis_test_* tools | Pydantic model | Test results |
| `EvidenceItem` | Union type of all evidence | TypeAdapter validation | Type alias | Polymorphic handling |
| `EvidenceBundle` | Container for all evidence | assemble_evidence_bundle | Pydantic model | Evidence aggregation |

### intent_frame.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `IntentFrame` | Structured interpretation of intent | intent_agent, planning | Pydantic model | Intent output |

### plan_spec.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `PlanDecision` | Planning decision with rationale | PlanSpec.decisions | Pydantic model | Decision record |
| `ToolRecommendation` | Tool recommendation | PlanSpec.tool_recommendations | Pydantic model | Tool selection |
| `PlanSpec` | Complete execution plan | plan_agent, planning | Pydantic model | Plan output |

### slices.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `FilterSpec` | Data filter specification | DataSlice.filters | Pydantic model | Filtering |
| `GroupBySpec` | Grouping specification | DataSlice.group_by | Pydantic model | Aggregation |
| `TimeWindow` | Time window specification | DataSlice.time_window | Pydantic model | Time filtering |
| `DataSlice` | Complete slice definition | InsightCard.data_slice | Pydantic model | Data subsetting |

### terminal_outcome.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `TerminalOutcome` | Enum for outcomes (SUCCESS, PARTIAL, etc.) | RunResult.outcome | Enum | Result classification |
| `PartialSuccessDetails` | Details for partial success | RunResult.partial_success_details | Pydantic model | Partial result info |
| `TerminalArtifact` | Terminal artifact with explanation | RunResult typing | Pydantic model | Result artifact |
| `RunResult` | Complete run result | Orchestrator results | Pydantic model | Run output |

### version_metadata.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `VersionMetadata` | Reproducibility metadata | DecisionPacket, BusinessReport | Pydantic model | Version tracking |

---

## Component: utils

Utility functions for validation, formatting, and configuration.

### advisory.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `CONFIDENCE_LABELS` | Maps confidence to advisory prefixes | Tests, report formatting | Dict access | Label lookup |
| `DECISIONAL_TO_ADVISORY` | Decisional→advisory word mapping | apply_advisory_language | Dict iteration | Language transformation |
| `get_advisory_label()` | Get label for confidence level | Report rendering | `get_advisory_label("high")` | Recommendation display |
| `apply_advisory_language()` | Replace decisional terms | Output formatting | `apply_advisory_language(text)` | Output sanitization |
| `format_advisory_header()` | Format headers with labels | Report rendering | `format_advisory_header(title, conf)` | Section headers |
| `format_recommendation_disclaimer()` | Generate disclaimer text | Report rendering | `format_recommendation_disclaimer(conf)` | Report appendix |
| `format_findings_preamble()` | Standard findings preamble | Report rendering | `format_findings_preamble()` | Findings section |
| `detect_decisional_terms()` | Find remaining decisional terms | Validation/linting | `detect_decisional_terms(text)` | Output validation |

### confidence.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DEFAULT_THRESHOLDS` | Default confidence thresholds | Fallback | Dict constant | When config missing |
| `DEFAULT_SUFFICIENCY` | Default sufficiency thresholds | Fallback | Dict constant | When config missing |
| `SufficiencyThresholds` | Pydantic model for thresholds | ConfidenceConfig | Pydantic model | Config validation |
| `ConfidenceConfig` | Complete confidence config | load_confidence_config | Pydantic model | Config container |
| `load_confidence_config()` | Load config from YAML (cached) | Agents, evaluators | `load_confidence_config()` | Startup |
| `load_confidence_thresholds()` | Legacy threshold loading | IntentAgent, tests | `load_confidence_thresholds()` | Confidence labeling |

### narrative.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DecisionRecord` | Decision record dataclass | Narrative building | Dataclass | Decision logging |
| `build_explanation()` | Generate user explanation | Report explainability | `build_explanation(records)` | Post-analysis |
| `build_explanation_from_dicts()` | Convert dicts to records | Dict input | `build_explanation_from_dicts(records)` | Dict source |
| `summarize_records()` | Summary for traceability | Audit logging | `summarize_records(records)` | Trace metadata |

### output.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ensure_output_dir()` | Create output directory | File writes | `ensure_output_dir(path)` | Before file write |
| `get_output_path()` | Get full output path | Path resolution | `get_output_path(filename)` | Path building |
| `get_default_output_dir()` | Get default output directory | Path resolution | `get_default_output_dir()` | Fallback path |

### semantic_validation.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `SemanticValidationResult` | Validation result container | Validation returns | Pydantic model | Validation output |
| `DatasetSchema` | Dataset schema representation | Metric validation | Pydantic model | Schema checking |
| `validate_dataset()` | Validate dataset reference | Semantic parsing | `validate_dataset(name, available)` | Input validation |
| `validate_metric()` | Validate metric reference | Semantic parsing | `validate_metric(metric, schema)` | Input validation |
| `validate_semantic_envelope()` | Full envelope validation | Semantic phase | `validate_semantic_envelope(envelope, ...)` | Input validation |

### validation.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ValidationResult` | Validation result container | All validators | Pydantic model | Validation output |
| `format_pydantic_errors()` | Format Pydantic errors | Error display | `format_pydantic_errors(errors)` | Error handling |
| `validate_output_schema()` | Validate against schema | Output gating | `validate_output_schema(data, schema)` | Before rendering |
| `validate_executive_summary()` | Validate summary presence | Quality check | `validate_executive_summary(report)` | Report validation |
| `validate_findings_have_evidence()` | Check evidence refs | Quality check | `validate_findings_have_evidence(report)` | Report validation |
| `validate_recommendations()` | Check recommendation quality | Quality check | `validate_recommendations(report)` | Report validation |
| `validate_visuals()` | Check visual completeness | Quality check | `validate_visuals(report)` | Report validation |
| `validate_report_quality()` | Run all quality checks | Quality gate | `validate_report_quality(report)` | Before rendering |
| `ValidationGate` | Gate blocking on failure | Rendering pipeline | `gate.check(result)` | Final gate |

### versioning.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `_get_product_version()` | Read product version (cached) | Version building | Internal | Metadata creation |
| `_get_flow_version()` | Read flow version (cached) | Version building | Internal | Metadata creation |
| `_hash_dataset()` | Compute dataset hash | Reproducibility | Internal | Metadata creation |
| `build_version_metadata()` | Build complete metadata | Report/packet assembly | `build_version_metadata(...)` | Output assembly |

---

## Component: flows

YAML flow definitions specifying step sequences.

### ade_v1.yaml

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `id: ade_v1` | Flow identifier | FlowLoader, gateway | Flow lookup | Run initiation |
| `version: 1.0.0` | Flow version | Reproducibility | VersionMetadata | Tracking |
| `autonomy: semi_auto` | Execution autonomy level | Governance | Approval required | HITL control |
| Step: `read` | Load CSV dataset | First step | Tool: data_reader | Flow start |
| Step: `context_pack` | Build dataset profile | After read | Tool: context_pack_builder | Context creation |
| Step: `viz_preferences` | Collect user preferences | User input | Form: chart_type + metric_focus | User interaction |
| Step: `compute_business_metrics` | Calculate metrics | After preferences | Tool: compute_business_metrics | Analysis |
| Step: `sufficiency_eval` | Evaluate data quality | After metrics | Agent: sufficiency_evaluator | Quality check |
| Step: `plan_proposal` | Generate plan proposal | After sufficiency | Agent: plan_proposal_agent | Plan generation |
| Step: `critic_eval` | Evaluate plan | After proposal | Agent: critic_evaluator | Quality gate |
| Step: `compute_anomalies` | Detect anomalies | Parallel | Tool: detect_anomalies | Analysis |
| Step: `build_chart_spec` | Create chart spec | After metrics | Tool: build_chart_spec | Visualization |
| Step: `hypothesis_data_outage` | Test outage hypothesis | Parallel | Tool: hypothesis_test_data_outage | Hypothesis |
| Step: `hypothesis_seasonality` | Test seasonality | Parallel | Tool: hypothesis_test_seasonality | Hypothesis |
| Step: `assemble_decision_packet` | Build decision packet | After critic | Tool: assemble_decision_packet | Assembly |
| Step: `assemble_evidence_bundle` | Bundle evidence | After analysis | Tool: assemble_evidence_bundle | Aggregation |
| Step: `assemble_business_report` | Create report | After bundle | Tool: assemble_business_report | Report creation |
| Step: `render_business_report_html` | Render HTML | Final step | Tool: render_business_report_html | Output |

### visualization.yaml

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `id: visualization` | Flow identifier | FlowLoader, gateway | Flow lookup | Run initiation |
| Step: `intent_interpretation` | Parse user intent | First step | Agent: planning_agent | Intent parsing |
| Step: `read` | Load dataset | After intent | Tool: data_reader | Data loading |
| Step: `context_pack` | Build context | After read | Tool: context_pack_builder | Context creation |
| Step: `sufficiency_eval` | Evaluate data | After context | Agent: sufficiency_evaluator | Quality check |
| Step: `planning` | Create plan | After sufficiency | Agent: planning_agent | Plan creation |
| Step: `plan_proposal` | Propose plan | After planning | Agent: plan_proposal_agent | Proposal |
| Step: `critic_eval` | Evaluate plan | After proposal | Agent: critic_evaluator | Quality gate |
| Step: `compute_business_metrics` | Calculate metrics | After critic | Tool: compute_business_metrics | Analysis |
| Step: `compute_anomalies` | Detect anomalies | Parallel | Tool: detect_anomalies | Analysis |
| Step: `hypothesis_data_outage` | Test outage | Parallel | Tool: hypothesis_test_data_outage | Hypothesis |
| Step: `hypothesis_seasonality` | Test seasonality | Parallel | Tool: hypothesis_test_seasonality | Hypothesis |
| Step: `build_chart_spec` | Create chart | After metrics | Tool: build_chart_spec | Visualization |
| Step: `assemble_decision_packet` | Build packet | After analysis | Tool: assemble_decision_packet | Assembly |
| Step: `assemble_evidence_bundle` | Bundle evidence | After analysis | Tool: assemble_evidence_bundle | Aggregation |
| Step: `assemble_business_report` | Create report | After bundle | Tool: assemble_business_report | Report |
| Step: `render_business_report_html` | Render report HTML | After report | Tool: render_business_report_html | Output |
| Step: `render_decision_packet_html` | Render packet HTML | Final | Tool: render_decision_packet_html | Output |

---

## Component: config

YAML configuration files for ADE product settings.

### product.yaml

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `product: ade` | Product identifier | Product loader | Identification | Discovery |
| `defaults.autonomy` | Default autonomy level | Run initialization | semi_auto | Run setup |
| `defaults.model` | Default LLM model | Model router | gpt-4o-mini | LLM selection |
| `limits.max_steps` | Maximum flow steps | Governance | 50 steps | Budget enforcement |
| `limits.max_tool_calls` | Maximum tool calls | Governance | 50 calls | Budget enforcement |
| `metadata.confidence` | Confidence thresholds | Agent decisions | high: 0.7, medium: 0.4 | Confidence labeling |
| `metadata.outputs` | Required outputs | Quality validation | insight_cards, visual | Output requirements |
| `metadata.file_upload` | Upload settings | File handling | csv, pdf; 25MB max | Input handling |
| `metadata.chart` | Chart settings | Visualization | Allowed types | Chart configuration |
| `metadata.governance` | Governance toggles | Security | Trace, PII redaction | Compliance |

### confidence.yaml

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `low_threshold` | Low confidence boundary | load_confidence_config | 0.4 | Confidence labeling |
| `high_threshold` | High confidence boundary | load_confidence_config | 0.7 | Confidence labeling |
| `sufficiency.min_rows` | Minimum rows for high confidence | SufficiencyEvaluator | 30 | Data evaluation |
| `sufficiency.critical_rows` | Critical row threshold | SufficiencyEvaluator | 15 | Low confidence trigger |
| `sufficiency.min_time_points` | Minimum time series points | SufficiencyEvaluator | 12 | Time series evaluation |
| `sufficiency.max_cv` | Maximum coefficient of variation | SufficiencyEvaluator | 0.6 | Variance stability |
| `sufficiency.min_non_null_rate` | Minimum non-null ratio | SufficiencyEvaluator | 0.7 | Data quality |

### confirm_time_axis.yaml

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `form_id` | Form identifier | USER_INPUT step | confirm_time_axis | User input |
| `title` | Display title | UI rendering | "Confirm time axis" | Form display |
| `question` | Question text | UI rendering | Time bucket confirmation | User prompt |
| `input_mode` | Input type | Form handling | choice_input | Input handling |
| `choices` | Available options | Form rendering | ["yes", "no"] | Option display |

### select_chart_type.yaml

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `form_id` | Form identifier | USER_INPUT step | select_chart_type | User input |
| `title` | Display title | UI rendering | "Select chart type" | Form display |
| `question` | Question text | UI rendering | Chart selection prompt | User prompt |
| `default` | Default selection | Form initialization | "bar" | Pre-selection |
| `choices` | Available options | Form rendering | ["bar", "line", "stacked"] | Option display |

### select_focus_metric.yaml

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `form_id` | Form identifier | USER_INPUT step | select_focus_metric | User input |
| `title` | Display title | UI rendering | "Select focus metric" | Form display |
| `question` | Question text | UI rendering | Metric selection prompt | User prompt |
| `default` | Default selection | Form initialization | "mean" | Pre-selection |
| `choices` | Available options | Form rendering | ["mean", "median", "growth", "outliers"] | Option display |

---

*Document generated from ADE product codebase analysis. For implementation details, refer to the source files.*
