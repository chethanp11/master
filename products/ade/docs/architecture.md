# Visual Insights — Architecture (v1)

## Decision Chain
- **User input** → file uploads are staged under `products/visual_insights/staging/input/`, then copied into the run’s observability input directory under the configured observability root.  
- **Planning agent** runs first but does not alter control flow (flow order is fixed).  
- **Tools** execute: read → detect anomalies → recommend chart → build chart spec → assemble card.  
- **LLM step** (`llm_reasoner`) generates a narrative summary from tool outputs.  
- **Human approvals** gate visualization and export decisions.  
- **Cards** are emitted as `InsightCard` objects with chart spec, narrative, metrics, and citations.  
- **Export** writes a stub JSON plus optional HTML/PDF files into the run’s observability output directory.

## Orchestrator Responsibilities
- Controls the run lifecycle (plan → read → detect_anomalies → recommend_chart → summarize → llm_review → approval → chart_config → build_chart_spec → assemble_card → approval_export → export).  
- Emits trace events per step/tool call into `<observability_root>/<product>/<run_id>/runtime/events.jsonl`.  
- Ensures agents stay stateless and rely on `core/tools/executor.py` for tool execution.  
- Applies guardrails via contracts and tool validation (chart types limited to the allowed set).

## Contracts & Data Flow
- `InsightCard` → final output with chart_type (line/bar/stacked_bar/scatter/table), key metrics, narrative, assumptions, citations, and optional data slices.  
- Output files are emitted by the export tool and persisted by the observability store.

## Determinism & LLM Usage
- Tooling (anomalies, chart spec, assembly) is deterministic and rule-based in v1.  
- Narrative text is generated via `llm_reasoner`, which routes model calls through `core/models/router.py`.

## Data Governance
- Trace events record each step outcome; export artifacts include the run id in metadata where applicable.  
- Citations in cards reference CSV slices.  
- Redaction is enforced in core governance hooks before trace/log emission.
