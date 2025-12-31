# Visual Insights — Architecture (v1)

## Decision Chain
- **User input** → dataset is staged under `observability/<product>/<run_id>/input/`.  
- **Planning agent** selects the next step when a replan is requested.  
- **Tools** execute: read → detect anomalies → recommend chart → build chart spec → assemble card.  
- **Human approvals** gate visualization and export decisions.  
- **Cards** are emitted as `InsightCard` objects with chart spec, narrative, metrics, and citations.  
- **Export** writes a PDF and a JSON stub to `observability/<product>/<run_id>/output/`.

## Orchestrator Responsibilities
- Controls the run lifecycle (plan → read → detect_anomalies → recommend_chart → summarize → approval → build_chart_spec → assemble_card → approval_export → export).  
- Emits trace events per step/tool call into `observability/.../runtime/events.jsonl`.  
- Ensures agents stay stateless and rely on `core/tools/executor.py` for execution.  
- Applies guardrails via contracts and tool validation (chart types limited to the allowed set).

## Contracts & Data Flow
- `InsightCard` → final output with chart_type (line/bar/stacked_bar/scatter/table), key metrics, narrative, assumptions, citations, and optional data slices.  
- `response.json` → emitted on completion with run/step/approval records and artifacts.

## Determinism & Optional LLMs
- All tooling (anomalies, driver analysis, chart spec, assembly) is deterministic and rule-based in v1.  
- Narrative text is templated; actual language generation (LLMs) is optional and can be layered in later, but core guards (citations, PII scrub) remain enforced.

## Data Governance
- Trace events record each step outcome; exported PDFs reference `run_id` and trace metadata.  
- Citations always cite CSV slices or PDF page spans.  
- PII scrubbing happens inside tool outputs before narratives/logs/traces leave the system.  
