# ==============================
# Integration: Product Discovery
# ==============================
from __future__ import annotations

from core.config.loader import load_settings
from core.utils.product_loader import discover_products


def test_catalog_contains_sandbox() -> None:
    settings = load_settings()
    catalog = discover_products(settings)
    assert "sandbox" in catalog.products
    assert "hello_world" in catalog.flows.get("sandbox", [])
