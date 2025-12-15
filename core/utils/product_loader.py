# ==============================
# Product Loader
# ==============================
"""
Discovers products and loads their manifests safely.

Responsibilities (v1):
- Discover products/*/manifest.yaml
- Parse manifest and build a product registry (metadata)
- Provide an explicit "register_product(product_name)" that imports a product's
  registration module (if declared) to bind agents/tools to registries.

Safety goals:
- Discovery must NOT import product code (no side effects).
- Registration import is explicit and controlled, and should only execute
  registry registration (no network calls, no persistence, no env reads).

Notes:
- This module does not enforce governance policies; it provides metadata and safe loading.
"""

from __future__ import annotations

import glob
import importlib
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError


class UiPanel(BaseModel):
    id: str
    title: str


class UiConfig(BaseModel):
    enabled: bool = True
    nav_label: Optional[str] = None
    panels: List[UiPanel] = Field(default_factory=list)


class ExposedApi(BaseModel):
    enabled: bool = True
    allowed_flows: List[str] = Field(default_factory=list)


class Entrypoints(BaseModel):
    register_module: Optional[str] = None


class ProductManifest(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None

    default_flow: Optional[str] = None
    exposed_api: ExposedApi = Field(default_factory=ExposedApi)
    ui: UiConfig = Field(default_factory=UiConfig)
    entrypoints: Entrypoints = Field(default_factory=Entrypoints)
    assets: Dict[str, Any] = Field(default_factory=dict)


@dataclass(frozen=True)
class ProductInfo:
    name: str
    root_dir: str
    manifest_path: str
    manifest: ProductManifest


class ProductRegistry:
    def __init__(self) -> None:
        self._products: Dict[str, ProductInfo] = {}

    def add(self, info: ProductInfo) -> None:
        if info.name in self._products:
            raise ValueError(f"Duplicate product name discovered: {info.name}")
        self._products[info.name] = info

    def get(self, name: str) -> Optional[ProductInfo]:
        return self._products.get(name)

    def list(self) -> List[ProductInfo]:
        return sorted(self._products.values(), key=lambda p: p.name)


def discover_products(products_dir: str) -> ProductRegistry:
    """
    Discover products from products_dir by scanning for */manifest.yaml.
    Does NOT import product code.
    """
    reg = ProductRegistry()
    pattern = os.path.join(products_dir, "*", "manifest.yaml")
    for manifest_path in glob.glob(pattern):
        root_dir = os.path.dirname(manifest_path)
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            manifest = ProductManifest.model_validate(raw)
            info = ProductInfo(
                name=manifest.name,
                root_dir=root_dir,
                manifest_path=manifest_path,
                manifest=manifest,
            )
            reg.add(info)
        except (OSError, ValidationError) as e:
            logger.warning("Skipping product manifest %s: %s", manifest_path, e)
            continue
    return reg


def register_product(product: ProductInfo) -> None:
    """
    Explicitly import and execute product registration module (if configured).
    The module should only register agents/tools via registries.
    """
    mod = product.manifest.entrypoints.register_module
    if not mod:
        return
    importlib.import_module(mod)


def safe_register_all(registry: ProductRegistry, enabled_products: Optional[List[str]] = None) -> None:
    """
    Register all enabled products.

    enabled_products:
      - None => register all discovered products
      - list => register only those listed (missing entries are ignored)
    """
    if enabled_products is None:
        for p in registry.list():
            register_product(p)
        return

    enabled_set = set(enabled_products)
    for p in registry.list():
        if p.name in enabled_set:
            register_product(p)
logger = logging.getLogger(__name__)
