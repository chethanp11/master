# ==============================
# Product Loader & Registration
# ==============================
"""
Deterministic discovery + registration for product packs.

Responsibilities (v1):
- Parse products/*/manifest.yaml into ProductMeta objects
- Load product-local config (config/product.yaml)
- Enumerate flows under products/<name>/flows/*.yaml
- Import products/<name>/registry.py safely and call register(registries)
"""

from __future__ import annotations

import importlib.util
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Sequence

import yaml
from pydantic import BaseModel, Field, ValidationError, ConfigDict

from core.agents.registry import AgentRegistry
from core.config.schema import Settings
from core.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


# ==============================
# Manifest + Config Schemas
# ==============================
class UiPanel(BaseModel):
    id: str
    title: str


class UiConfig(BaseModel):
    enabled: bool = True
    nav_label: Optional[str] = None
    panels: List[UiPanel] = Field(default_factory=list)
    icon: Optional[str] = None
    category: Optional[str] = None


class ExposedApi(BaseModel):
    enabled: bool = True
    allowed_flows: List[str] = Field(default_factory=list)


class ProductManifest(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None

    default_flow: Optional[str] = None
    exposed_api: ExposedApi = Field(default_factory=ExposedApi)
    ui_enabled: bool = True
    ui: UiConfig = Field(default_factory=UiConfig)
    flows: List[str] = Field(default_factory=list, description="Optional curated list of flow names")


class ProductConfigModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    defaults: Dict[str, Any] = Field(default_factory=dict)
    limits: Dict[str, Any] = Field(default_factory=dict)
    flags: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ==============================
# Catalog Data Structures
# ==============================
@dataclass(frozen=True)
class ProductMeta:
    name: str
    display_name: str
    description: Optional[str]
    version: Optional[str]
    default_flow: Optional[str]
    expose_api: bool
    ui_enabled: bool
    flows: List[str]
    ui: UiConfig
    root_dir: str
    manifest_path: str
    config_path: str
    registry_path: str
    enabled: bool


@dataclass(frozen=True)
class ProductLoadError:
    product: Optional[str]
    path: str
    message: str


@dataclass(frozen=True)
class ProductRegistries:
    agent_registry: Any
    tool_registry: Any
    settings: Settings


@dataclass
class ProductCatalog:
    products: Dict[str, ProductMeta] = field(default_factory=dict)
    configs: Dict[str, ProductConfigModel] = field(default_factory=dict)
    flows: Dict[str, List[str]] = field(default_factory=dict)
    errors: List[ProductLoadError] = field(default_factory=list)

    def enabled_products(self) -> List[str]:
        return [name for name, meta in self.products.items() if meta.enabled]


# ==============================
# Discovery
# ==============================
def discover_products(settings: Settings, *, repo_root: Optional[Path | str] = None) -> ProductCatalog:
    """
    Discover product manifests/configs/flows under repo_root / products_dir.
    """
    root = Path(repo_root or settings.repo_root_path()).resolve()
    products_root = root / settings.products.products_dir
    catalog = ProductCatalog()

    if not products_root.exists():
        logger.warning("Products directory does not exist: %s", products_root)
        return catalog

    manifest_paths = sorted(products_root.glob("*/manifest.yaml"))

    enabled_allowlist = set(settings.products.enabled or [])
    auto_enable = settings.products.auto_enable or not enabled_allowlist

    for manifest_path in manifest_paths:
        product_root = manifest_path.parent
        try:
            manifest_data = _read_yaml(manifest_path)
        except Exception as exc:
            catalog.errors.append(
                ProductLoadError(product=None, path=str(manifest_path), message=str(exc))
            )
            continue
        if manifest_data is None:
            catalog.errors.append(
                ProductLoadError(product=None, path=str(manifest_path), message="manifest empty or unreadable")
            )
            continue
        try:
            manifest = ProductManifest.model_validate(manifest_data)
        except ValidationError as exc:
            catalog.errors.append(
                ProductLoadError(product=None, path=str(manifest_path), message=str(exc))
            )
            continue

        enabled = auto_enable or manifest.name in enabled_allowlist
        config_path = product_root / "config" / "product.yaml"
        try:
            config_data = _read_yaml(config_path)
        except Exception as exc:
            catalog.errors.append(
                ProductLoadError(product=manifest.name, path=str(config_path), message=str(exc))
            )
            continue
        if config_data is None:
            catalog.errors.append(
                ProductLoadError(
                    product=manifest.name,
                    path=str(config_path),
                    message="Missing product config (config/product.yaml)",
                )
            )
            continue
        if "name" not in config_data:
            config_data["name"] = manifest.name
        try:
            product_config = ProductConfigModel.model_validate(config_data)
        except ValidationError as exc:
            catalog.errors.append(
                ProductLoadError(product=manifest.name, path=str(config_path), message=str(exc))
            )
            continue

        registry_path = product_root / "registry.py"
        if not registry_path.exists():
            catalog.errors.append(
                ProductLoadError(
                    product=manifest.name,
                    path=str(registry_path),
                    message="registry.py is required for every product pack",
                )
            )
            continue

        flow_names = _list_flow_names(product_root / "flows")

        meta = ProductMeta(
            name=manifest.name,
            display_name=manifest.display_name or manifest.name,
            description=manifest.description,
            version=manifest.version,
            default_flow=manifest.default_flow,
            expose_api=bool(manifest.exposed_api.enabled),
            ui_enabled=bool(manifest.ui_enabled and manifest.ui.enabled),
            flows=flow_names or manifest.flows,
            ui=manifest.ui,
            root_dir=str(product_root),
            manifest_path=str(manifest_path),
            config_path=str(config_path),
            registry_path=str(registry_path),
            enabled=enabled,
        )

        catalog.products[manifest.name] = meta
        catalog.configs[manifest.name] = product_config
        catalog.flows[manifest.name] = flow_names

    return catalog


# ==============================
# Registration
# ==============================
def register_enabled_products(
    catalog: ProductCatalog,
    *,
    settings: Settings,
    agent_registry: Any = AgentRegistry,
    tool_registry: Any = ToolRegistry,
) -> List[ProductLoadError]:
    registries = ProductRegistries(
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        settings=settings,
    )
    errors: List[ProductLoadError] = []

    for meta in catalog.products.values():
        if not meta.enabled:
            continue
        try:
            module = _import_registry_module(meta)
            register_fn = getattr(module, "register", None)
            if register_fn is None:
                raise AttributeError("registry.py must define register(registries: ProductRegistries)")
            register_fn(registries)
        except Exception as exc:  # pragma: no cover - error path
            err = ProductLoadError(product=meta.name, path=meta.registry_path, message=str(exc))
            errors.append(err)
            logger.warning("Failed to register product %s: %s", meta.name, exc)

    catalog.errors.extend(errors)
    return errors


# ==============================
# Helpers
# ==============================
def _read_yaml(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return None
    data = yaml.safe_load(raw)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def _list_flow_names(flows_dir: Path) -> List[str]:
    if not flows_dir.exists():
        return []
    names: List[str] = []
    for path in sorted(flows_dir.glob("*")):
        if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}:
            names.append(path.stem)
    return names


def _import_registry_module(meta: ProductMeta) -> ModuleType:
    module_name = f"products.{meta.name}.registry_autoload"
    path = Path(meta.registry_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import registry module for {meta.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
