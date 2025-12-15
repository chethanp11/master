# ==============================
# API Dependencies / Singletons
# ==============================
from __future__ import annotations

from functools import lru_cache

from core.config.loader import load_settings
from core.utils.product_loader import discover_products, safe_register_all
from core.orchestrator.engine import OrchestratorEngine
from core.memory.router import MemoryRouter
from core.logging.tracing import Tracer


@lru_cache(maxsize=1)
def get_settings():
    settings = load_settings()
    # Product discovery + registration (once)
    reg = discover_products(settings.products.products_dir)
    safe_register_all(reg, enabled_products=settings.products.enabled_products)
    return settings


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
    mem = get_memory_router()
    tracer = get_tracer()
    return OrchestratorEngine.from_settings(settings=settings, memory=mem, tracer=tracer)