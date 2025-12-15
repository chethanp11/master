# Visual Insights — Requirements (v1)

## 1. Objective
Visual Insights enables users to upload **CSV (structured)** and **PDF (unstructured)** data, ask natural-language questions, and receive **clear, visual, and explainable insights**.  
The product is designed to be deterministic, auditable, and enterprise-ready from day one.

---

## 2. In-Scope (v1 Hard Limits)

### 2.1 Supported Inputs
- CSV files (tabular structured data)
- PDF files (unstructured text)

_No other file formats or live data sources are supported in v1._

---

### 2.2 Insight Modes
Exactly **three** insight modes are supported:

1. **Summarize Dataset**
   - Automatic overview of key metrics, dimensions, and trends

2. **Answer My Question**
   - User-provided natural language question answered using CSV and/or PDF evidence

3. **Find Anomalies + Drivers**
   - Detection of significant changes or outliers and explanation of contributing factors

---

### 2.3 Visual Output Types
Insights may use **only** the following chart types:

- Line
- Bar
- Stacked Bar
- Scatter
- Table

No additional visualization types are allowed in v1.

---

### 2.4 Export
- Export format: **PDF only**
- Export captures the current insight session state

---

## 3. User Workflow (v1)

1. Upload one or more CSV and/or PDF files
2. System parses and profiles inputs
3. User selects an insight mode and optionally provides a prompt
4. System generates one or more **Insight Cards**
5. User applies filters or drilldowns
6. User exports the session as a PDF

---

## 4. Insight Card Requirements

Each Insight Card **must** include:

- Title
- One approved visualization (chart or table)
- Key metrics or figures
- Narrative explanation (“what happened / why it matters”)
- Data slice description (filters, groupings, time window)
- Source citations (CSV references and/or PDF page spans)
- Assumptions or confidence notes (if applicable)

Insight Cards must be deterministic and reproducible.

---

## 5. Functional Requirements by Mode

### 5.1 Summarize Dataset
- Identify key measures, dimensions, and time columns
- Surface high-level trends, distributions, and notable patterns
- Generate **3–5 Insight Cards** by default

---

### 5.2 Answer My Question
- Accept free-form natural language input
- Resolve intent against:
  - Structured CSV data
  - Unstructured PDF content (via retrieval)
- Return one or more Insight Cards that directly answer the question
- Clearly state assumptions where interpretation is required

---

### 5.3 Find Anomalies + Drivers
- Detect anomalies such as spikes, drops, or sudden changes
- Perform driver analysis to explain contributing factors
- Include before/after or segment comparison where relevant
- Generate anomaly visualization plus supporting breakdowns

---

## 6. Governance & Trust Requirements (Mandatory)

### 6.1 Traceability
- Every run must emit structured trace events for:
  - Ingestion
  - Profiling / indexing
  - Planning
  - Computation
  - Rendering
  - Export
- Each exported PDF must reference a unique run identifier

---

### 6.2 Citations
- Every Insight Card must include citations:
  - CSV-based insights reference dataset and column slices
  - PDF-based insights reference document ID, page number, and text span

Insights without citations must not be rendered.

---

### 6.3 PII Scrubbing
- Detect common PII (names, emails, phone numbers, IDs)
- Redact PII from:
  - Narratives
  - Logs
  - Trace payloads
- Raw data remains accessible only via controlled memory backends

---

## 7. Non-Functional Requirements

- **Deterministic**: Same inputs and prompts produce the same outputs
- **Explainable**: Every insight is backed by data and citations
- **Isolated**: Each session is independent
- **Thin UI**: No business logic in the UI layer
- **Config-driven**: Limits and defaults come from product config

---

## 8. Explicitly Out of Scope (v1)

- Excel, database, or API connectors
- Real-time or streaming data
- Additional chart types (maps, heatmaps, networks)
- PowerPoint, image, or HTML exports
- User-customizable chart styling
- Cross-session dashboards or persistence beyond a single run

---

## 9. v1 Success Criteria

- Users can generate meaningful insights from CSV and/or PDF data in under one minute
- Every Insight Card is traceable, cited, and PII-safe
- Exported PDFs are reproducible and audit-ready
- Product behavior aligns strictly with defined v1 limits

---