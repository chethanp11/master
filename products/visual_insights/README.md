# Visual Insights v1

Visual Insights v1 is a focused, traceable agentic experience that turns CSV + PDF uploads into deterministic insight cards and PDF exports. It prioritizes structured planning and governance-aware tooling so every card is backed by citations, trace events, and PII scrubbing.

## v1 Constraints
- Inputs: CSV and PDF files only (no other formats, connectors, or streams).  
- Insight modes: `summarize_dataset`, `answer_question`, `anomalies_and_drivers`.  
- Chart types: `line`, `bar`, `stacked_bar`, `scatter`, `table`.  
- Export target: PDF output only, driven by the orchestrator’s export step.  
- Governance: trace steps + citations + PII scrub required for every run.

## Folder Layout
- `configs/visual_insights.yaml` → feature limits, mode defaults, export settings.  
- `contracts/` → Pydantic models (UploadRequest, InsightPlan, InsightCard, citations, slices).  
- `flows/` → orchestrator entrypoint + per-step modules wiring agents/tools.  
- `agents/` → stateless decision maker implementations (planner, evidence, builder, viz).  
- `tools/` → deterministic helpers (anomaly, driver, chart spec, assembly).  
- `tests/` → unit + integration coverage (agents-only + golden-path).  
- `docs/` → architecture, API, requirements, runbook for Visual Insights v1.

## Running Tests
- Unit tests: `pytest products/visual_insights/tests/unit/`  
- Integration smoke: `pytest products/visual_insights/tests/integration/test_vi_golden_path_v1.py`

## Configuration
Edit `products/visual_insights/configs/visual_insights.yaml` to adjust inputs, max cards, mode defaults, and governance toggles.
