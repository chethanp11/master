# ==============================
# API Dependencies / Singletons
# ==============================
from __future__ import annotations

from functools import lru_cache

from core.config.loader import load_settings
from core.utils.product_loader import discover_products, register_enabled_products, ProductCatalog
from core.orchestrator.engine import OrchestratorEngine
from core.memory.router import MemoryRouter
from core.logging.tracing import Tracer


@lru_cache(maxsize=1)
def get_settings():
    return load_settings()


@lru_cache(maxsize=1)
def get_product_catalog() -> ProductCatalog:
    settings = get_settings()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)
    return catalog


@lru_cache(maxsize=1)
def get_memory_router() -> MemoryRouter:
    settings = get_settings()
    return MemoryRouter.from_settings(settings)


@lru_cache(maxsize=1)
def get_tracer() -> Tracer:
    settings = get_settings()
    mem = get_memory_router()
    return Tracer.from_settings(settings=settings, memory=mem)


@lru_cache(maxsize=1)
def get_engine() -> OrchestratorEngine:
    settings = get_settings()
    get_product_catalog()  # ensure products are registered once
    mem = get_memory_router()
    tracer = get_tracer()
    return OrchestratorEngine.from_settings(settings=settings, memory=mem, tracer=tracer)
