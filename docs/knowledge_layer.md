# Knowledge Layer (v1)

The knowledge subsystem provides deterministic local retrieval backed by SQLite.
It consists of four primitives:

1. **Vector Store (`core/knowledge/vector_store.py`)**  
   - File-backed (SQLite) database stored under `storage/vectors/knowledge.sqlite` (configurable).  
   - Chunks are keyed by `(collection, doc_id, chunk_id)` to guarantee idempotent upserts.  
   - Metadata remains filterable (exact-match equality).  
   - Lexical retrieval (`_jaccard`) is the default ranking method while we design future embedding workflows.

2. **Retriever (`core/knowledge/retriever.py`)**  
   - Thin wrapper that constructs `Query` objects (text, top_k, filters, collection) and calls the store.  
   - Returns normalized `Chunk` objects (`chunk_id`, `text`, `source`, `metadata`, optional `score`).

3. **Structured Access (`core/knowledge/structured.py`)**  
   - Loads CSV files (pandas preferred, `csv` fallback).  
   - Provides helper utilities to filter rows and summarize column stats.  
   - No outbound network or text-to-SQL in v1.

4. **Ingestion (`scripts/ingest_knowledge.py`)**  
   - CLI to chunk `.txt/.md/.json/.csv` sources and upsert them into a collection.  
   - Deterministic chunk ids: `doc_id` = normalized absolute path, `chunk_id = f"{doc_id}:::{index}"`.  
   - Metadata includes `source_path`, `chunk_index`, `modified_at`, `file_size`, `tags`, etc.  
   - Summary output lists files processed, skipped, inserted, updated, and cumulative store stats.

## Using the ingestion CLI

```
python scripts/ingest_knowledge.py \
  --db storage/vectors/knowledge.sqlite \
  --collection sandbox \
  --path docs/knowledge \
  --glob "**/*.md" \
  --chunk-size 800 \
  --chunk-overlap 150 \
  --max-bytes 200000
```

You can also ingest explicit files:

```
python scripts/ingest_knowledge.py \
  --db storage/vectors/knowledge.sqlite \
  --collection ops \
  --file docs/runbook.md --file docs/alerts.json
```

The script is idempotent: re-ingesting the same files overwrites the existing `(collection, doc_id, chunk_id)` rows rather than duplicating them.

## Retrieval example

```python
from core.knowledge.base import Query
from core.knowledge.vector_store import SqliteVectorStore
from core.knowledge.retriever import Retriever

store = SqliteVectorStore("storage/vectors/knowledge.sqlite")
retriever = Retriever(store)
chunks = retriever.retrieve(
    query="approval workflow",
    collection="sandbox",
    top_k=3,
    filters={"product": "sandbox"},
)
for chunk in chunks:
    print(chunk.source, chunk.score)
```

## Storage layout

The store lives at the path you pass to the CLI (default recommendation: `storage/vectors/knowledge.sqlite`).  
Each chunk row contains:

| Column       | Description                                 |
|--------------|---------------------------------------------|
| collection   | Logical namespace (`default`, `sandbox`, …) |
| doc_id       | Stable document identifier (normalized path)|
| chunk_id     | Unique per chunk (`doc_id` + index)         |
| text         | Chunk text                                  |
| source       | Source path (`file://…`)                    |
| metadata     | JSON payload (tags, timestamps, etc.)       |
| created_at   | Unix timestamp when first inserted          |
| updated_at   | Last update timestamp                       |

All interactions go through `SqliteVectorStore`, so there are no direct SQLite calls elsewhere in the codebase.
