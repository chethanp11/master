#!/usr/bin/env python3
# ==============================
# Memory Schema Migration Utility
# ==============================
"""
Utility script to inspect/apply sqlite memory schema migrations.

Usage:
    python scripts/migrate_memory.py --db-path storage/memory/master.sqlite --apply
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from core.config.loader import load_settings
from core.config.schema import Settings
from core.memory.sqlite_backend import SQLiteBackend

LATEST_VERSION = 1


def _resolve_default_db_path(settings: Settings) -> Path:
    repo_root = settings.repo_root_path()

    def _resolve(path_str: str) -> Path:
        path = Path(path_str)
        return path if path.is_absolute() else (repo_root / path)

    storage_dir = _resolve(settings.app.paths.storage_dir)
    memory_dir = storage_dir / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    db_path = settings.secrets.memory_db_path or str(memory_dir / "master.sqlite")
    db = _resolve(db_path)
    db.parent.mkdir(parents=True, exist_ok=True)
    return db


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Inspect/apply sqlite memory schema migrations.")
    ap.add_argument("--db-path", help="Path to sqlite file. If omitted, derived from settings.", default=None)
    ap.add_argument("--apply", action="store_true", help="Apply pending migrations (idempotent).")
    ap.add_argument("--repo-root", default=None, help="Override repo root for settings resolution.")
    ap.add_argument("--configs-dir", default=None, help="Override configs directory.")
    ap.add_argument("--secrets-file", default=None, help="Override secrets file path.")
    return ap.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)

    settings_kwargs = {
        "repo_root": args.repo_root,
        "configs_dir": args.configs_dir,
        "secrets_file": args.secrets_file,
    }
    # Remove None values
    settings_kwargs = {k: v for k, v in settings_kwargs.items() if v}
    settings, _ = load_settings(include_raw=True, **settings_kwargs)

    db_path = Path(args.db_path) if args.db_path else _resolve_default_db_path(settings)
    backend = SQLiteBackend(db_path=str(db_path), initialize=bool(args.apply))

    current_version = backend.get_schema_version()
    pending = max(0, LATEST_VERSION - current_version)

    print(f"DB path: {db_path}")
    print(f"Current schema version: {current_version}")
    print(f"Latest schema version: {LATEST_VERSION}")
    print(f"Pending migrations: {pending}")

    if args.apply and pending > 0:
        print("Applying migrations...")
        backend.ensure_schema()
        current_version = backend.get_schema_version()
        print(f"Schema updated to version {current_version}")
    elif args.apply:
        print("No migrations to apply.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
