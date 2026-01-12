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

Auto-discovery (v2):
- Automatically discover @agent and @tool decorated classes
- Support simplified registry.py that uses auto_register()
"""

from __future__ import annotations


# Public surface for product discovery/registration; keep minimal and stable.
__all__ = [
    "discover_products",
    "register_enabled_products",
    "auto_discover_agents",
    "auto_discover_tools",
    "auto_register",
    "ProductCatalog",
    "ProductMeta",
    "ProductLoadError",
    "ProductRegistries",
]


import importlib.util
import inspect
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Type

import yaml
from pydantic import BaseModel, Field, ValidationError, ConfigDict

from core.agents.registry import AgentRegistry
from core.agents.llm_reasoner import build as build_llm_reasoner
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
    _register_core_agents(agent_registry)
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


def _register_core_agents(agent_registry: Any) -> None:
    has_fn = getattr(agent_registry, "has", None)
    if callable(has_fn):
        if not has_fn("llm_reasoner"):
            agent_registry.register(build_llm_reasoner().name, build_llm_reasoner)


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


# ==============================
# Auto-Discovery Functions
# ==============================


def _import_module_from_path(module_name: str, path: Path) -> ModuleType:
    """Import a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _find_decorated_classes(
    module: ModuleType,
    marker_attr: str,
) -> List[Tuple[str, Type[Any], Any]]:
    """
    Find all classes in a module that have the specified marker attribute.

    Returns list of (name, class, descriptor) tuples.
    """
    results: List[Tuple[str, Type[Any], Any]] = []

    for name, obj in inspect.getmembers(module, inspect.isclass):
        # Skip imported classes (only process classes defined in this module)
        if obj.__module__ != module.__name__:
            continue

        # Check for auto-discovery marker
        if not getattr(obj, "_auto_discover", False):
            continue

        # Get the descriptor
        descriptor = getattr(obj, marker_attr, None)
        if descriptor is None:
            continue

        results.append((descriptor.name, obj, descriptor))

    return results


def _make_factory(cls: Type[Any], module: ModuleType) -> Callable[[], Any]:
    """
    Create a factory function for an agent/tool class.

    Looks for a `build()` function in the module first, then falls back
    to direct instantiation.
    """
    # Check if module has a build() function
    build_fn = getattr(module, "build", None)
    if callable(build_fn):
        return build_fn

    # Fall back to direct instantiation
    def factory() -> Any:
        return cls()

    return factory


def auto_discover_agents(product_path: Path) -> List[Tuple[str, Callable[[], Any], Any]]:
    """
    Discover all @agent decorated classes in product/agents/.

    Args:
        product_path: Path to the product directory (e.g., products/hello_world)

    Returns:
        List of (name, factory_function, descriptor) tuples for each discovered agent.
    """
    agents_dir = product_path / "agents"
    if not agents_dir.exists():
        return []

    results: List[Tuple[str, Callable[[], Any], Any]] = []
    product_name = product_path.name

    for py_file in sorted(agents_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue

        module_name = f"products.{product_name}.agents.{py_file.stem}_autodiscover"
        try:
            module = _import_module_from_path(module_name, py_file)
            for name, cls, descriptor in _find_decorated_classes(module, "_agent_descriptor"):
                factory = _make_factory(cls, module)
                results.append((name, factory, descriptor))
        except Exception as exc:
            logger.warning("Failed to auto-discover agents from %s: %s", py_file, exc)

    return results


def auto_discover_tools(product_path: Path) -> List[Tuple[str, Callable[[], Any], Any]]:
    """
    Discover all @tool decorated classes in product/tools/.

    Args:
        product_path: Path to the product directory (e.g., products/hello_world)

    Returns:
        List of (name, factory_function, descriptor) tuples for each discovered tool.
    """
    tools_dir = product_path / "tools"
    if not tools_dir.exists():
        return []

    results: List[Tuple[str, Callable[[], Any], Any]] = []
    product_name = product_path.name

    for py_file in sorted(tools_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue

        module_name = f"products.{product_name}.tools.{py_file.stem}_autodiscover"
        try:
            module = _import_module_from_path(module_name, py_file)
            for name, cls, descriptor in _find_decorated_classes(module, "_tool_descriptor"):
                factory = _make_factory(cls, module)
                results.append((name, factory, descriptor))
        except Exception as exc:
            logger.warning("Failed to auto-discover tools from %s: %s", py_file, exc)

    return results


def auto_register(registries: ProductRegistries, product_path: Path) -> None:
    """
    Auto-register all discovered agents and tools from a product.

    This function scans the product's agents/ and tools/ directories for
    classes decorated with @agent and @tool, and registers them with the
    appropriate registries.

    Args:
        registries: ProductRegistries containing agent and tool registries
        product_path: Path to the product directory (e.g., products/hello_world)

    Example:
        def register(registries: ProductRegistries) -> None:
            from pathlib import Path
            from core.utils.product_loader import auto_register
            auto_register(registries, Path(__file__).parent)
    """
    # Discover and register agents
    for name, factory, descriptor in auto_discover_agents(product_path):
        try:
            registries.agent_registry.register(name, factory, descriptor=descriptor)
            logger.debug("Auto-registered agent: %s", name)
        except Exception as exc:
            logger.warning("Failed to auto-register agent %s: %s", name, exc)

    # Discover and register tools
    for name, factory, descriptor in auto_discover_tools(product_path):
        try:
            registries.tool_registry.register(name, factory, descriptor=descriptor)
            logger.debug("Auto-registered tool: %s", name)
        except Exception as exc:
            logger.warning("Failed to auto-register tool %s: %s", name, exc)

