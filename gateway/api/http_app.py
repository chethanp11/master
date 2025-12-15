# ==============================
# FastAPI App Factory
# ==============================
from __future__ import annotations

from fastapi import FastAPI

from gateway.api.routes_run import router as run_router


def create_app() -> FastAPI:
    app = FastAPI(title="master", version="0.1.0")
    app.include_router(run_router, prefix="/api")
    return app