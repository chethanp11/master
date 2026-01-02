#!/usr/bin/env python3
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "docs" / "components"
EXTENSIONS = {".py", ".yaml", ".yml"}
EXCLUDE_DIRS = {"secrets"}


def _iter_components(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in EXTENSIONS:
            yield path


def _top_level_dir(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT)
    parts = rel.parts
    return parts[0] if parts else ""


def _write_bundle(name: str, files: List[Path]) -> None:
    if not files:
        return
    output_path = OUTPUT_DIR / f"{name}.txt"
    timestamp = _timestamp()
    lines: List[str] = []
    lines.append(f"# captured_at: {timestamp}")
    lines.append("")
    for file_path in sorted(files):
        rel = file_path.relative_to(REPO_ROOT)
        lines.append(f"# {rel}")
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        lines.append(content.rstrip())
        lines.append("")
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _timestamp() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bundles: dict[str, List[Path]] = {}
    for component in _iter_components(REPO_ROOT):
        top = _top_level_dir(component)
        if not top or top.startswith(".") or top in EXCLUDE_DIRS:
            continue
        bundles.setdefault(top, []).append(component)
    for name, files in sorted(bundles.items()):
        _write_bundle(name, files)
    print(f"Wrote {len(bundles)} component bundle(s) to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
