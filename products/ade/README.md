# Visual Insights v1

Visual Insights v1 converts a CSV dataset into a single insight card with a chart, narrative, and export artifacts. The flow is governed end-to-end by the core runtime and includes approvals plus user input for chart configuration.

## v1 Constraints
- Inputs: CSV files only.  
- Flow: `visualization` (fixed step order).  
- Chart types: `line`, `bar`, `stacked_bar`, `scatter`, `table`.  
- Exports: JSON stub plus optional HTML/PDF based on user input.  
- Governance: trace events, citations, and redaction enforced by core hooks.

## Folder Layout
- `config/product.yaml` → feature limits, UI intent/inputs, export settings.  
- `contracts/` → Pydantic models (InsightCard, citations, slices).  
- `flows/` → YAML flows executed by the orchestrator.  
- `agents/` → stateless decision makers used by YAML flows (planning + dashboard).  
- `tools/` → deterministic helpers (anomaly, driver, chart spec, assembly, export).  
- `tests/` → unit + integration coverage for the YAML flow.  
- `docs/` → architecture and requirements for Visual Insights v1.

## Running Tests
- Unit tests: `pytest products/visual_insights/tests/unit/`  
- Integration smoke: `pytest products/visual_insights/tests/integration/test_vi_orchestrator_flow.py`

## Configuration
Edit `products/visual_insights/config/product.yaml` to adjust inputs, max cards, mode defaults, and governance toggles.
