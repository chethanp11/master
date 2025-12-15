# Visual Insights — Architecture (v1)

## Purpose
`visual_insights` is a product plugin on top of `master/` that turns **CSV + PDF** inputs into **interactive insight cards** and a **PDF export**, with **trace + citations + PII scrubbing** enabled by default.

---

## High-Level Architecture

### Data Flow (v1)
1. **Ingest**: accept CSV + PDF uploads
2. **Profile & Index**
   - CSV → schema + profiling summary
   - PDF → text extraction + chunking + retrieval index
3. **Insight Generation**
   - User selects one of 3 modes (+ optional prompt)
   - System produces Insight Cards (chart + narrative + evidence)
4. **Interact**
   - Filters + drilldowns update cards deterministically
5. **Export**
   - Render current session to PDF (cards + citations + run metadata)
6. **Govern**
   - PII scrubbed logs + trace events throughout

---

## Repository Placement (Product Plugin)

master/
products/
visual_insights/
init.py
product.yaml
configs/
visual_insights.yaml
flows/
v1_flow.py
agents/
insight_planner.py
insight_builder.py
evidence_agent.py
viz_agent.py
tools/
ingest_csv.py
ingest_pdf.py
profile_csv.py
index_pdf.py
retrieve_pdf.py
compute_agg.py
detect_anomalies.py
driver_analysis.py
chart_recommender.py
chart_renderer.py
export_pdf.py
pii_scan.py
contracts/
io.py
insight_card.py
trace_ext.py
tests/
test_golden_path_v1.py

**Rule:** All domain logic lives under `products/visual_insights/`. Core stays product-agnostic.

---

## Runtime Components (Mapped to `master/`)

### 1) Orchestrator (control plane)
- Owns run lifecycle, step execution, and message/context passing.
- Ensures agents remain stateless and do not call tools directly.

**Responsibilities**
- Build plan for selected insight mode
- Execute steps: ingest → profile/index → insight → viz → export
- Emit trace events per step/tool/model call

### 2) Agents (goal-driven, stateless)
Agents are **decision-makers** that output structured intents; they never execute tools.

**Agents in v1**
- `InsightPlannerAgent`
  - Input: user mode + optional prompt + available sources
  - Output: ordered `InsightPlan` (steps + card specs + required transforms)
- `EvidenceAgent`
  - Input: plan step requiring evidence
  - Output: citations (CSV slice refs or PDF spans/pages) + supporting facts
- `InsightBuilderAgent`
  - Input: computed stats + evidence
  - Output: narrative + key takeaways (structured)
- `VizAgent`
  - Input: card spec + data shape
  - Output: chart type choice (from allowed 5) + chart spec request

### 3) Tools (execution boundary)
All real work happens here via `core/tools/executor.py`.

**Tool groups**
- Ingestion
  - `ingest_csv`: parse/store CSV in memory backend, return `DatasetRef`
  - `ingest_pdf`: extract text, store `DocRef`
- Profiling & Indexing
  - `profile_csv`: schema, missingness, distributions, time candidates
  - `index_pdf`: chunk + store chunks + build retrieval index
- Analytics
  - `compute_agg`: groupby/filters/time windows (deterministic)
  - `detect_anomalies`: spikes/drops/changepoints (deterministic rules)
  - `driver_analysis`: top contributors / segment comparisons
- Retrieval
  - `retrieve_pdf`: retrieve top-k chunks + return citations
- Visualization
  - `chart_recommender`: map question/data-shape → allowed chart type
  - `chart_renderer`: generate renderable chart spec (e.g., Vega-Lite/Plotly JSON)
- Governance
  - `pii_scan`: detect PII in text outputs and redact
- Export
  - `export_pdf`: render cards → PDF artifact

---

## Storage & Memory (v1)

All persistence routes through `core/memory/*` backends.

### Stored artifacts
- Raw inputs (CSV bytes, PDF bytes) or controlled references
- Parsed dataset tables (normalized, typed)
- PDF extracted text and chunks
- Retrieval index metadata
- Insight session state:
  - selected sources
  - filters/drilldowns
  - generated cards
  - export history

### Key IDs
- `run_id`: orchestrator run identifier
- `dataset_id`, `doc_id`: stable IDs for uploaded inputs
- `card_id`: unique per Insight Card within a run/session

---

## Contracts (Pydantic at all boundaries)

### Input contracts
- `UploadRequest`
  - files: [CSV|PDF]
  - mode: summarize | answer | anomalies_drivers
  - prompt: optional
  - settings: top_k, max_cards, etc.

### Output contracts
- `InsightCard`
  - `card_id`
  - `title`
  - `chart_type` (line|bar|stacked_bar|scatter|table)
  - `chart_spec` (JSON)
  - `key_metrics` (dict)
  - `narrative` (string)
  - `data_slice` (filters/groupings/time window)
  - `citations` (CSV refs + PDF spans/pages)
  - `assumptions` (list)
  - `confidence` (optional score/label)

### Session state
- `InsightSessionState`
  - sources: datasets/docs
  - active_filters
  - cards[]
  - trace_summary
  - export_refs[]

---

## Insight Modes as Flows (v1)

### Mode A: Summarize Dataset
Steps:
1. ingest_csv + ingest_pdf (if provided)
2. profile_csv / index_pdf
3. planner generates 3–5 card specs
4. compute_agg as needed per card
5. build narratives + evidence
6. render cards

### Mode B: Answer My Question
Steps:
1. ingest + profile/index
2. planner parses intent (structured vs unstructured vs hybrid)
3. if hybrid:
   - compute_agg for CSV evidence
   - retrieve_pdf for textual evidence
4. build answer cards with citations
5. render cards

### Mode C: Find Anomalies + Drivers
Steps:
1. ingest_csv + profile_csv
2. detect_anomalies on candidate measures
3. for each anomaly:
   - compute_agg around time window
   - driver_analysis (dimension contributions / segment compare)
4. build “what changed / why” narratives
5. render cards

---

## UI Architecture (Thin Client)

### UI screens (minimum)
- **Upload & Sources**
  - upload CSV/PDF
  - show detected schema + PDF indexing status
- **Insight Workspace**
  - mode selector + prompt box
  - Insight Card grid
  - global filters
  - per-card drilldowns
- **Evidence & Trace Drawer**
  - show citations (CSV slice / PDF spans)
  - show transforms used (deterministic, human-readable)
  - show run_id + step history
- **Export**
  - generate PDF of current state
  - download link + export metadata

**No business logic in UI:** UI only calls gateway APIs and renders returned specs.

---

## Governance, Trace, and Safety

### Trace events (must be emitted per step)
- ingest_start/end
- profile_start/end
- retrieve_start/end
- compute_start/end
- chart_render_start/end
- export_start/end
- pii_scrub_applied
- errors with sanitized payloads

### Citations policy
- Every narrative statement must be attributable to:
  - a CSV aggregate or row slice reference, and/or
  - a PDF chunk reference with page/span

### PII scrubbing
- Apply before:
  - logging
  - tracing
  - returning narratives to UI
  - embedding/indexing (optional but recommended in v1)

---

## Determinism & Reproducibility

- Use deterministic tool outputs for:
  - profiling
  - aggregation
  - anomaly detection
  - chart recommendation (rule-based mapping)
- Model usage (if any) must be constrained:
  - narrative generation must include citations and pass PII scrub
  - prefer “structured outputs first” to minimize hallucinations
- Store the full plan + transforms in session state so exports reproduce exactly.

---

## v1 Golden Path (E2E Test Target)

Test: `test_golden_path_v1.py`
1. Upload small CSV + small PDF
2. Run each mode:
   - summarize → returns >=3 cards
   - answer → returns >=1 card with citations
   - anomalies+drivers → returns >=2 cards
3. Validate:
   - only allowed chart types used
   - every card has citations
   - trace contains expected step events
4. Export PDF:
   - file generated
   - includes run_id + citations section

---
