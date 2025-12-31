# Visual Insights — Architecture (v1)

## Decision Chain
- **User upload** → `UploadRequest` containing CSV/PDF `FileRef`s and selected `InsightMode`.  
- **Planner agent** (`InsightPlannerAgent`) produces an `InsightPlan` (card specs + required tools).  
- **Tools** execute: ingest → profile → analytics (aggregate/anomaly/driver) → retrievals → chart spec → assembly.  
- **Viz agent** (`VizAgent`) picks one of five allowed chart types before cards are rendered.  
- **Cards** come back as `InsightCard` objects that include chart spec, narrative template, metrics, and citations.  
- **Export** step renders cards into a governance-ready PDF artifact.

## Orchestrator Responsibilities
- Controls the run lifecycle (ingest → profile → plan → compute → evidence → render → export).  
- Emits trace markers (`ingest:start`, `plan:end`, etc.) so each step/tool call is auditable.  
- Ensures agents stay stateless and rely on `core/tools/executor.py` for any execution.  
- Applies guardrails before returning `RunResponse`: citations present and chart types limited to the allowed five.

## Contracts & Data Flow
- `UploadRequest` → describes files, mode, optional prompt.  
- `InsightPlan` → ordered `PlanStep`s and `CardSpec`s (intent + preferred chart).  
- `InsightCard` → final output with chart_type (line/bar/stacked_bar/scatter/table), key metrics, narrative, assumptions, citations, and optional data slices.  
- `RunResponse` → includes cards + `trace_steps`.

## Determinism & Optional LLMs
- All tooling (anomalies, driver analysis, chart spec, assembly) is deterministic and rule-based in v1.  
- Narrative text is templated; actual language generation (LLMs) is optional and can be layered in later, but core guards (citations, PII scrub) remain enforced.

## Data Governance
- Trace events record each step outcome; exported PDFs reference `run_id` and trace metadata.  
- Citations always cite CSV slices or PDF page spans.  
- PII scrubbing happens inside tool outputs before narratives/logs/traces leave the system.  
