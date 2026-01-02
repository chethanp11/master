# ==============================
# Testing Fixtures
# ==============================
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.config.schema import Settings
from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.governance.hooks import GovernanceHooks
from core.governance.security import SecurityRedactor
from core.memory.tracing import Tracer
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.models.providers.openai_provider import OpenAIRequest, OpenAIResponse
from core.orchestrator.engine import OrchestratorEngine
from gateway.api.http_app import create_app
from gateway.api import deps as gateway_deps


@pytest.fixture
def trace_sink() -> List[Dict[str, Any]]:
    """Collects emitted trace events without touching production logging."""
    return []


class _CollectingTracer(Tracer):
    def __init__(self, *, sink: List[Dict[str, Any]], **kwargs: Any) -> None:
        self._sink = sink
        super().__init__(**kwargs)

    def emit(self, event: Any) -> None:  # type: ignore[override]
        super().emit(event)
        payload = event.model_dump()
        if "event_type" not in payload:
            payload["event_type"] = payload.get("kind")
        self._sink.append(payload)


@pytest.fixture
def memory_backend() -> InMemoryBackend:
    """In-memory memory backend for deterministic persistence during tests."""
    return InMemoryBackend()


@pytest.fixture
def fake_model_provider() -> Callable[[OpenAIRequest], OpenAIResponse]:
    """Deterministic stub matching the OpenAI provider interface."""

    def _provider(request: OpenAIRequest) -> OpenAIResponse:
        return OpenAIResponse(
            ok=True,
            model=request.model,
            content=f"stub response for {request.model}",
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            meta={"stub": True},
        )

    return _provider


class FakeToolBackend:
    def __init__(self, *, behavior: str = "success") -> None:
        self.behavior = behavior
        self.calls = 0

    def run(self, tool: Any, params: Dict[str, Any], ctx: Any) -> ToolResult:
        self.calls += 1
        meta = ToolMeta(tool_name=getattr(tool, "name", tool.__class__.__name__), backend="fake")
        if self.behavior == "always_timeout":
            err = ToolError(
                code=ToolErrorCode.TIMEOUT,
                message="timeout",
                details={"params": params},
            )
            return ToolResult(ok=False, data=None, error=err, meta=meta)
        if self.behavior == "fail_once_then_success" and self.calls == 1:
            err = ToolError(
                code=ToolErrorCode.BACKEND_ERROR,
                message="simulated transient failure",
                details={"params": params},
            )
            return ToolResult(ok=False, data=None, error=err, meta=meta)
        return ToolResult.ok(data={"result": "ok"}, meta=meta)


@pytest.fixture
def fake_tool_backend() -> FakeToolBackend:
    return FakeToolBackend()


@pytest.fixture
def orchestrator(memory_backend: InMemoryBackend, trace_sink: List[Dict[str, Any]]) -> OrchestratorEngine:
    """Engine wired to deterministic in-memory helpers."""
    settings = Settings()
    memory_router = MemoryRouter(backend=memory_backend)
    tracer = _CollectingTracer(memory=memory_backend, redactor=SecurityRedactor(), sink=trace_sink)
    engine = OrchestratorEngine.from_settings(
        settings=settings,
        memory=memory_router,
        tracer=tracer,
        sleep_fn=lambda _: None,
    )
    return engine


@pytest.fixture
def app_client(orchestrator: OrchestratorEngine) -> TestClient:
    """FastAPI test client wired to the provided orchestrator."""
    gateway_deps.get_engine.cache_clear()
    gateway_deps.get_settings.cache_clear()
    gateway_deps.get_memory_router.cache_clear()
    gateway_deps.get_tracer.cache_clear()
    gateway_deps.get_product_catalog.cache_clear()
    app = create_app()
    app.dependency_overrides[gateway_deps.get_engine] = lambda: orchestrator
    client = TestClient(app)
    return client
