# Visual Insights API (v1)

## Function-level API
- `run_visual_insights_v1(upload_request: UploadRequest, ctx: dict) -> RunResponse`  
  - Entrypoint called by orchestrator/gateway.  
  - `ctx` is used for run/session IDs and optional mode overrides.  
- `export_pdf(export_request: ExportRequest) -> bytes` (placeholder: orchestrator handles export via tools).

## UploadRequest
Fields:
```json
{
  "files": [
    {"file_id": "csv_1", "file_type": "csv", "name": "data.csv"},
    {"file_id": "pdf_1", "file_type": "pdf", "name": "context.pdf"}
  ],
  "mode": "summarize_dataset",
  "prompt": "What drove the spike?"
}
```

## RunResponse
Fields:
```json
{
  "run_id": "run_visual_insights_v1",
  "session_id": "session_visual_insights_v1",
  "cards": [
    {
      "card_id": "card_1",
      "title": "Revenue trend",
      "chart_type": "line",
      "chart_spec": {"type": "line"},
      "key_metrics": [{"name": "revenue", "value": 12345}],
      "narrative": "Revenue increased steadily",
      "citations": [{"type": "csv", "csv": {"dataset_id": "csv_1", "columns": ["value"], "filters": []}}]
    }
  ],
  "trace_steps": [
    "ingest:start", "ingest:end",
    "profile_index:start", "profile_index:end",
    "plan:start", "plan:end",
    "compute:start", "compute:end",
    "evidence:start", "evidence:end",
    "render:start", "render:end",
    "export:start", "export:end"
  ]
}
```

## Modes & Chart Types
- Modes: `summarize_dataset`, `answer_question`, `anomalies_and_drivers`.  
- Chart types allowed in `InsightCard`: `line`, `bar`, `stacked_bar`, `scatter`, `table`.

## ExportRequest
Fields:
```json
{
  "run_id": "run_visual_insights_v1",
  "format": "pdf"
}
```

