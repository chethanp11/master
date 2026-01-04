#!/usr/bin/env python3

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "docs" / "components"
EXTENSIONS = {".py", ".yaml", ".yml"}
EXCLUDE_DIRS: set[str] = set()
EXCLUDE_FILES: set[str] = {".DS_Store"}


def _iter_components(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in EXCLUDE_FILES:
            continue
        if path.parent == root:
            yield path
            continue
        if path.suffix.lower() in EXTENSIONS:
            yield path


def _top_level_dir(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT)
    parts = rel.parts
    return parts[0] if len(parts) > 1 else "root"


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
        if "\x00" in content:
            continue
        if _is_secrets_path(file_path):
            content = _redact_secrets(content)
        lines.append(content.rstrip())
        lines.append("")
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _timestamp() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _is_secrets_path(path: Path) -> bool:
    return "secrets" in path.parts


def _redact_secrets(content: str) -> str:
    redacted_lines: List[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in line:
            redacted_lines.append(line)
            continue
        prefix, _sep, _rest = line.partition(":")
        redacted_lines.append(f"{prefix}: ***REDACTED***")
    return "\n".join(redacted_lines)


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
