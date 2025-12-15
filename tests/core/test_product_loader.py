# ==============================
# Tests: Product Loader
# ==============================
from __future__ import annotations

from pathlib import Path
from typing import List

import textwrap

from core.config.schema import Settings
from core.utils.product_loader import (
    ProductCatalog,
    ProductLoadError,
    discover_products,
    register_enabled_products,
)


def _make_settings(repo_root: Path, *, enabled: List[str] | None = None, auto_enable: bool = True) -> Settings:
    data = {
        "app": {"paths": {"repo_root": str(repo_root)}},
        "products": {
            "products_dir": "products",
            "enabled": enabled or [],
            "auto_enable": auto_enable,
        },
    }
    return Settings.model_validate(data)


def _write_product(root: Path, name: str, *, with_registry: bool = True) -> None:
    prod_dir = root / "products" / name
    (prod_dir / "flows").mkdir(parents=True, exist_ok=True)
    (prod_dir / "config").mkdir(parents=True, exist_ok=True)
    (prod_dir / "__init__.py").write_text("", encoding="utf-8")

    (prod_dir / "flows" / "flow_one.yaml").write_text("id: flow_one", encoding="utf-8")

    manifest = textwrap.dedent(
        f"""
        name: "{name}"
        display_name: "{name.title()}"
        description: "Test {name}"
        version: "0.1.0"
        default_flow: "flow_one"
        exposed_api:
          enabled: true
        ui_enabled: true
        ui:
          enabled: true
        """
    ).strip()
    (prod_dir / "manifest.yaml").write_text(manifest, encoding="utf-8")

    config = textwrap.dedent(
        f"""
        name: "{name}"
        defaults:
          autonomy_level: "semi_auto"
        """
    ).strip()
    (prod_dir / "config" / "product.yaml").write_text(config, encoding="utf-8")

    if with_registry:
        registry = textwrap.dedent(
            """
            from core.utils.product_loader import ProductRegistries

            def register(registries: ProductRegistries) -> None:
                registries.agent_registry.register("test_agent", lambda: None)
                registries.tool_registry.register("test_tool", lambda: None)
            """
        ).strip()
        (prod_dir / "registry.py").write_text(registry, encoding="utf-8")


class DummyRegistry:
    def __init__(self) -> None:
        self.names: List[str] = []

    def register(self, name: str, factory) -> None:  # pragma: no cover - simple helper
        self.names.append(name)


def test_discovery_and_registration(tmp_path: Path) -> None:
    _write_product(tmp_path, "alpha")
    settings = _make_settings(tmp_path)

    catalog = discover_products(settings, repo_root=tmp_path)
    assert "alpha" in catalog.products
    assert catalog.flows["alpha"] == ["flow_one"]

    agent_reg = DummyRegistry()
    tool_reg = DummyRegistry()
    errors = register_enabled_products(
        catalog,
        settings=settings,
        agent_registry=agent_reg,
        tool_registry=tool_reg,
    )
    assert not errors
    assert agent_reg.names == ["test_agent"]
    assert tool_reg.names == ["test_tool"]


def test_missing_registry_records_error(tmp_path: Path) -> None:
    _write_product(tmp_path, "bravo", with_registry=False)
    settings = _make_settings(tmp_path)

    catalog = discover_products(settings, repo_root=tmp_path)
    assert "bravo" not in catalog.products
    assert any("registry.py" in err.path for err in catalog.errors)


def test_enabled_filtering(tmp_path: Path) -> None:
    _write_product(tmp_path, "alpha")
    _write_product(tmp_path, "beta")
    settings = _make_settings(tmp_path, enabled=["beta"], auto_enable=False)

    catalog = discover_products(settings, repo_root=tmp_path)
    assert catalog.products["alpha"].enabled is False
    assert catalog.products["beta"].enabled is True
