# ==============================
# Knowledge Ingestion Script (v1)
# ==============================
"""
Ingest text files into the local SqliteVectorStore.

Usage examples:
  python scripts/ingest_knowledge.py --db storage/vectors/knowledge.sqlite --path storage/raw --ext .txt
  python scripts/ingest_knowledge.py --db storage/vectors/knowledge.sqlite --file docs/overview.md

Notes:
- This is intentionally minimal for v1.
- Chunking is basic (by characters with overlap).
- Metadata includes source_path and optional tags.
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict, List, Optional, Tuple

from core.knowledge.base import IngestItem
from core.knowledge.vector_store import SqliteVectorStore


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def chunk_text(text: str, *, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    if chunk_size <= 0:
        return [text]
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        j = min(n, i + chunk_size)
        chunks.append(text[i:j])
        if j == n:
            break
        i = max(0, j - overlap)
    return [c.strip() for c in chunks if c.strip()]


def discover_files(root: str, ext: str) -> List[str]:
    out: List[str] = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if ext and not fn.lower().endswith(ext.lower()):
                continue
            out.append(os.path.join(dirpath, fn))
    return out


def build_items(paths: List[str], *, tags: Optional[str], chunk_size: int, overlap: int) -> List[IngestItem]:
    items: List[IngestItem] = []
    tag_list = [t.strip() for t in (tags or "").split(",") if t.strip()]
    for p in paths:
        text = read_text_file(p)
        for idx, chunk in enumerate(chunk_text(text, chunk_size=chunk_size, overlap=overlap)):
            meta: Dict[str, Any] = {
                "source_path": p,
                "source_type": "file",
                "chunk_index": idx,
            }
            if tag_list:
                meta["tags"] = tag_list
            items.append(IngestItem(text=chunk, metadata=meta))
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="Path to SQLite store (e.g., storage/vectors/knowledge.sqlite)")
    ap.add_argument("--path", help="Directory to ingest (recursive)")
    ap.add_argument("--file", help="Single file to ingest")
    ap.add_argument("--ext", default=".txt", help="File extension filter when using --path (default: .txt)")
    ap.add_argument("--tags", default="", help="Comma-separated tags stored in metadata")
    ap.add_argument("--chunk-size", type=int, default=1200, help="Chunk size in chars")
    ap.add_argument("--overlap", type=int, default=200, help="Chunk overlap in chars")
    args = ap.parse_args()

    if not args.path and not args.file:
        raise SystemExit("Provide --path or --file")

    paths: List[str] = []
    if args.file:
        if not os.path.exists(args.file):
            raise SystemExit(f"File not found: {args.file}")
        paths.append(args.file)

    if args.path:
        if not os.path.isdir(args.path):
            raise SystemExit(f"Directory not found: {args.path}")
        paths.extend(discover_files(args.path, args.ext))

    if not paths:
        raise SystemExit("No files found to ingest")

    store = SqliteVectorStore(db_path=args.db)
    items = build_items(paths, tags=args.tags, chunk_size=args.chunk_size, overlap=args.overlap)
    res = store.add_chunks(items)

    print(f"Ingested={res.count} ok={res.ok}")
    if res.errors:
        print("Errors:")
        for e in res.errors[:20]:
            print(f"- {e}")
    st = store.stats()
    print(f"Store total_chunks={st.total_chunks} path={st.store_path}")
    return 0 if res.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())