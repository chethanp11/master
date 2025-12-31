# ==============================
# Integration: Gateway API Runs
# ==============================
from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient

from core.agents.registry import AgentRegistry
from core.tools.registry import ToolRegistry
from gateway.api.http_app import create_app
import gateway.api.deps as deps


def _reset_deps() -> None:
    deps.get_engine.cache_clear()
    deps.get_settings.cache_clear()
    deps.get_memory_router.cache_clear()
    deps.get_tracer.cache_clear()
    deps.get_product_catalog.cache_clear()


@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    sqlite_path = tmp_path / "api.sqlite"
    storage_dir = tmp_path / "storage"
    monkeypatch.setenv("MASTER__APP__PATHS__REPO_ROOT", repo_root.as_posix())
    monkeypatch.setenv("MASTER__APP__PATHS__STORAGE_DIR", storage_dir.as_posix())
    monkeypatch.setenv("MASTER__SECRETS__MEMORY_DB_PATH", sqlite_path.as_posix())
    AgentRegistry.clear()
    ToolRegistry.clear()
    _reset_deps()
    client = TestClient(create_app())
    yield client
    client.close()
    AgentRegistry.clear()
    ToolRegistry.clear()
    _reset_deps()


def _start_hello_world_run(api_client: TestClient, payload: Optional[Dict[str, Any]] = None) -> str:
    req_payload = payload or {"keyword": "API"}
    started = api_client.post("/api/run/hello_world/hello_world", json={"payload": req_payload}).json()
    assert started["ok"] is True
    assert started["data"]["status"] == "PENDING_HUMAN"
    return started["data"]["run_id"]


@pytest.mark.integration
def test_gateway_api_run_resume_flow(api_client: TestClient) -> None:
    products = api_client.get("/api/products").json()
    assert products["ok"] is True
    hello_world = next((p for p in products["data"]["products"] if p["name"] == "hello_world"), None)
    assert hello_world is not None
    assert "hello_world" in hello_world["flows"]

    flows = api_client.get("/api/products/hello_world/flows").json()
    assert flows["ok"] is True
    assert "hello_world" in flows["data"]["flows"]

    run_id = _start_hello_world_run(api_client)

    pending = api_client.get(f"/api/run/{run_id}").json()
    assert pending["ok"] is True
    assert pending["data"]["run"]["status"] == "PENDING_HUMAN"

    resumed = api_client.post(
        f"/api/resume_run/{run_id}",
        json={"decision": "APPROVED", "approval_payload": {"approved": True, "notes": "ok"}},
    ).json()
    assert resumed["ok"] is True
    assert resumed["data"]["status"] == "COMPLETED"

    final = api_client.get(f"/api/run/{run_id}").json()
    assert final["ok"] is True
    assert final["data"]["run"]["status"] == "COMPLETED"


@pytest.mark.integration
def test_gateway_api_resume_rejection_marks_failed(api_client: TestClient) -> None:
    run_id = _start_hello_world_run(api_client)

    resumed = api_client.post(
        f"/api/resume_run/{run_id}",
        json={"decision": "APPROVED", "approval_payload": {"approved": False, "notes": "reject"}},
    ).json()
    assert resumed["ok"] is True
    assert resumed["data"]["status"] == "FAILED"

    final = api_client.get(f"/api/run/{run_id}").json()
    assert final["ok"] is True
    assert final["data"]["run"]["status"] == "FAILED"


@pytest.mark.integration
def test_gateway_api_missing_approval_field_is_rejected(api_client: TestClient) -> None:
    run_id = _start_hello_world_run(api_client)
    resp = api_client.post(
        f"/api/resume_run/{run_id}",
        json={"decision": "APPROVED", "approval_payload": {"notes": "missing approved flag"}},
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["detail"]["error"]["code"] == "missing_approval_field"


@pytest.mark.integration
def test_gateway_api_trace_cleanliness(api_client: TestClient) -> None:
    run_id = _start_hello_world_run(api_client, payload={"keyword": "safe", "api_key": "sk-secret"})
    resumed = api_client.post(
        f"/api/resume_run/{run_id}",
        json={"decision": "APPROVED", "approval_payload": {"approved": True}},
    ).json()
    assert resumed["ok"] is True
    final = api_client.get(f"/api/run/{run_id}").json()
    serialized_steps = json.dumps(final["data"].get("steps", []))
    assert "api_key" not in serialized_steps
