# V1 Bloat Audit (Boot Imports)

## Boot Import Graph (FastAPI app)
- `gateway/api/http_app.py`
  - imports `gateway/api/routes_run.py`
    - imports `gateway/api/deps.py`
      - imports `core/config/loader.py`
      - imports `core/utils/product_loader.py`
      - imports `core/orchestrator/engine.py`
        - imports `core/memory/router.py`
          - imports `core/memory/observability_store.py`
          - imports `core/memory/sqlite_backend.py`
      - imports `core/memory/tracing.py`

## Optional Capabilities Imported at Boot
These modules are imported during app boot but represent optional capabilities that should be decoupled:
- None by default (optional backends are now lazy-imported).

## Notes
- `core/memory/observability_store.py` is core V1 (events + outputs); input mirroring is feature-flagged off by default.
- Product discovery and registry load during `get_product_catalog()`; analysis logic remains in products, not core.

## Feature Flags (default OFF)
- `observability_input_mirroring`
- `enable_sqlite_backend`
- `enable_vector_backend`
- `enable_knowledge_index`
