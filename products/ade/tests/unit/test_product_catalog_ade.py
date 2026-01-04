from __future__ import annotations

from pathlib import Path

from core.config.loader import load_settings
from core.utils.product_loader import discover_products


def test_ade_catalog_has_flows() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    settings = load_settings(
        repo_root=str(repo_root),
        configs_dir=str(repo_root / "configs"),
        env={},
    )
    catalog = discover_products(settings, repo_root=repo_root)
    assert "ade" in catalog.products
    assert catalog.flows.get("ade")
