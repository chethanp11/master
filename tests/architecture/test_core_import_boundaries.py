from __future__ import annotations

import re
from pathlib import Path


def test_core_does_not_import_products_modules() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    core_root = repo_root / "core"
    pattern = re.compile(r"\b(from|import)\s+products\b")

    offenders = []
    for path in core_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if pattern.search(text):
            offenders.append(path)

    assert not offenders, f"Core must not import products modules: {offenders}"
