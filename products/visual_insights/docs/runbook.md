# Visual Insights Runbook (v1)

## Prerequisites
- macOS or Linux with Python 3.10+ installed. `python -m venv .venv && source .venv/bin/activate`.  
- `pip install -r requirements.txt` (root project requirements).  
- Use a clean checkout of `master/` so `products/visual_insights` imports resolve.

## Running Tests
- Unit suite: `pytest products/visual_insights/tests/unit/`.  
- Integration smoke: `pytest products/visual_insights/tests/integration/test_vi_golden_path_v1.py`.

## Troubleshooting
- **Import errors**: ensure `products/visual_insights/__init__.py` exists and Python path includes the repo root; rerun `pip install -e .` if needed.  
- **Missing citations errors**: check that `render_step` always supplies at least one `CitationRef`. Guardrail violations raise `ValueError` before the response returns.  
- **Unsupported chart types**: cards must use `line`, `bar`, `stacked_bar`, `scatter`, or `table`; non-compliant chart specs are rejected by the flow guardrail validator.  
- **PDF indexing placeholder**: PDF ingestion currently tracks only `DocRef` placeholders; treat any missing extracted text as a known limitation until `retrieve_pdf` tool is wired.

## Workflow Tips
- Start from `products/visual_insights/tests/integration/test_vi_golden_path_v1.py` to understand a golden run.  
- Update `configs/visual_insights.yaml` for limits (max cards, top_k, chunk size).  
- Keep UI/CLI store minimal logic; orchestration + governance live under `flows/` and `core/`.
