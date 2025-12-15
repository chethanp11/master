# ==============================
# Knowledge Ingestion Script (v1)
# ==============================
"""
Ingest text files into the local SqliteVectorStore.

Usage examples:
  python scripts/ingest_knowledge.py --db storage/vectors/knowledge.sqlite --path docs/ --glob "**/*.md"
  python scripts/ingest_knowledge.py --db storage/vectors/knowledge.sqlite --file docs/overview.md --file README.md

Notes:
- This is intentionally minimal for v1.
- Chunking is basic (by characters with overlap).
- Metadata includes source_path and optional tags.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from typing import Dict, List, Optional, Sequence, Tuple

from core.knowledge.base import IngestChunk
from core.knowledge.vector_store import SqliteVectorStore

SUPPORTED_EXTS = {".txt", ".md", ".markdown", ".json", ".csv"}


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_json_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, ensure_ascii=False, indent=2)


def read_csv_file(path: str) -> str:
    return read_text_file(path)


def load_file_text(path: str) -> Tuple[str, str]:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".json"}:
        return read_json_file(path), "application/json"
    if ext in {".csv"}:
        return read_csv_file(path), "text/csv"
    return read_text_file(path), "text/plain"


def chunk_text(text: str, *, chunk_size: int, overlap: int) -> List[str]:
    if chunk_size <= 0:
        return [text]
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        j = min(n, i + chunk_size)
        chunk = text[i:j].strip()
        if chunk:
            chunks.append(chunk)
        if j == n:
            break
        i = max(0, j - overlap)
    return chunks or [text]


def normalize_doc_id(path: str) -> str:
    return os.path.abspath(path).replace(os.sep, "/")


def iter_files(
    *,
    root: Optional[str],
    explicit_files: Sequence[str],
    patterns: Optional[Sequence[str]],
    max_bytes: int,
) -> Tuple[List[str], List[str]]:
    files: List[str] = []
    skipped: List[str] = []

    for p in explicit_files:
        if os.path.isfile(p):
            files.append(os.path.abspath(p))
        else:
            skipped.append(f"{p} (not found)")

    if root:
        if not os.path.isdir(root):
            skipped.append(f"{root} (not a directory)")
        else:
            root_path = os.path.abspath(root)
            matches: List[str] = []
            if patterns:
                for pattern in patterns:
                    glob_pattern = os.path.join(root_path, pattern)
                    matches.extend(glob.glob(glob_pattern, recursive=True))
            else:
                for dirpath, _, filenames in os.walk(root_path):
                    for fn in filenames:
                        matches.append(os.path.join(dirpath, fn))
            for path in matches:
                if not os.path.isfile(path):
                    continue
                ext = os.path.splitext(path)[1].lower()
                if ext not in SUPPORTED_EXTS:
                    continue
                files.append(os.path.abspath(path))

    unique_files = sorted(set(files))
    filtered: List[str] = []
    for path in unique_files:
        try:
            size = os.path.getsize(path)
        except OSError:
            skipped.append(f"{path} (unreadable)")
            continue
        if size > max_bytes:
            skipped.append(f"{path} (>{max_bytes} bytes)")
            continue
        filtered.append(path)
    return filtered, skipped


def build_chunks(
    *,
    paths: List[str],
    collection: str,
    chunk_size: int,
    overlap: int,
    tags: Optional[List[str]],
) -> Tuple[List[IngestChunk], List[str]]:
    items: List[IngestChunk] = []
    errors: List[str] = []
    for path in paths:
        try:
            text, mime_type = load_file_text(path)
        except Exception as exc:
            errors.append(f"{path}: {exc}")
            continue
        doc_id = normalize_doc_id(path)
        stat = os.stat(path)
        file_meta = {
            "source_path": path,
            "source_type": "file",
            "modified_at": int(stat.st_mtime),
            "file_size": stat.st_size,
            "content_type": mime_type,
        }
        if tags:
            file_meta["tags"] = tags

        for idx, chunk in enumerate(chunk_text(text, chunk_size=chunk_size, overlap=overlap)):
            chunk_id = f"{doc_id}:::{idx}"
            meta = dict(file_meta)
            meta["chunk_index"] = idx
            items.append(
                IngestChunk(
                    collection=collection,
                    doc_id=doc_id,
                    chunk_id=chunk_id,
                    text=chunk,
                    source=path,
                    metadata=meta,
                )
            )
    return items, errors


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Ingest local files into the knowledge vector store.")
    ap.add_argument("--db", required=True, help="Path to SQLite store (e.g., storage/vectors/knowledge.sqlite)")
    ap.add_argument("--collection", default="default", help="Collection name (default: default)")
    ap.add_argument("--path", help="Directory to ingest (recursive)")
    ap.add_argument("--glob", action="append", help="Glob pattern relative to --path (can repeat)")
    ap.add_argument("--file", action="append", default=[], help="Specific file to ingest (can repeat)")
    ap.add_argument("--chunk-size", type=int, default=1000, help="Chunk size in characters (default: 1000)")
    ap.add_argument("--chunk-overlap", type=int, default=200, help="Chunk overlap in characters (default: 200)")
    ap.add_argument("--max-bytes", type=int, default=500_000, help="Skip files larger than this many bytes (default: 500k)")
    ap.add_argument("--tags", default="", help="Comma-separated tags stored in metadata")
    return ap.parse_args(argv)


def run_ingest(args: argparse.Namespace) -> int:
    if not args.path and not args.file:
        raise SystemExit("Provide --path or at least one --file")

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    files, skipped = iter_files(
        root=args.path,
        explicit_files=args.file,
        patterns=args.glob,
        max_bytes=args.max_bytes,
    )
    if not files:
        print("No eligible files found.")
        for note in skipped:
            print(f"SKIP: {note}")
        return 1

    chunks, chunk_errors = build_chunks(
        paths=files,
        collection=args.collection,
        chunk_size=args.chunk_size,
        overlap=args.chunk_overlap,
        tags=tags,
    )

    store = SqliteVectorStore(db_path=args.db)
    result = store.upsert(chunks)
    stats = store.stats(collection=args.collection)

    print(f"collection={args.collection}")
    print(f"files_processed={len(files)} skipped={len(skipped)}")
    print(f"chunks_inserted={result.inserted} chunks_updated={result.updated} ok={result.ok}")
    print(f"store_total_chunks={stats.total_chunks} store_path={stats.store_path}")
    if skipped:
        print("Skipped:")
        for msg in skipped[:20]:
            print(f"- {msg}")
    if chunk_errors:
        print("Errors while reading files:")
        for msg in chunk_errors[:20]:
            print(f"- {msg}")
    if result.errors:
        print("Upsert errors:")
        for msg in result.errors[:20]:
            print(f"- {msg}")
    return 0 if result.ok else 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    return run_ingest(args)


if __name__ == "__main__":
    raise SystemExit(main())
