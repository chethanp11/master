# ==============================
# Observability Writer
# ==============================
"""
Append-only observability writer for runtime events and artifacts.

Files:
- observability/<product>/<run_id>/runtime/events.jsonl
- observability/<product>/<run_id>/output/*
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ObservabilityWriter:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.root = repo_root / "observability"

    def _run_dir(self, *, product: str, run_id: str) -> Path:
        return self.root / product / run_id

    def _ensure_dirs(self, *, product: str, run_id: str) -> Dict[str, Path]:
        base = self._run_dir(product=product, run_id=run_id)
        paths = {
            "base": base,
            "input": base / "input",
            "runtime": base / "runtime",
            "output": base / "output",
        }
        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
        return paths

    def append_event(self, *, product: str, run_id: str, payload: Dict[str, Any]) -> Path:
        paths = self._ensure_dirs(product=product, run_id=run_id)
        runtime_path = paths["runtime"] / "events.jsonl"
        line = json.dumps(payload, ensure_ascii=False)
        runtime_path.open("a", encoding="utf-8").write(line + "\n")
        return runtime_path

    def output_path(self, *, product: str, run_id: str, name: str) -> Path:
        paths = self._ensure_dirs(product=product, run_id=run_id)
        return paths["output"] / name

    def input_path(self, *, product: str, run_id: str, name: str) -> Path:
        paths = self._ensure_dirs(product=product, run_id=run_id)
        return paths["input"] / name
