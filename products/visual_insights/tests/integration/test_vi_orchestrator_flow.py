# ==============================
# Visual Insights Orchestrator Flow Test
# ==============================
from __future__ import annotations

from pathlib import Path

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


@pytest.mark.integration
def test_visual_insights_overview_flow(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "visual_insights.sqlite"

    settings = load_settings(
        repo_root=str(repo_root),
        configs_dir=str(repo_root / "configs"),
        env={
            "MASTER__APP__PATHS__STORAGE_DIR": storage_dir.as_posix(),
            "MASTER__SECRETS__MEMORY_DB_PATH": sqlite_path.as_posix(),
        },
    )

    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        catalog = discover_products(settings, repo_root=repo_root)
        register_enabled_products(catalog, settings=settings)
        engine = OrchestratorEngine.from_settings(settings)

    started = engine.run_flow(
        product="visual_insights",
        flow="visualization",
        payload={"dataset": "sample.csv"},
    )
    assert started.ok, started.error
    assert started.data and started.data["status"] == "PENDING_HUMAN"

    run_id = started.data["run_id"]
    resumed = engine.resume_run(run_id=run_id, approval_payload={"approved": True, "notes": "ok"})
    assert resumed.ok, resumed.error

    result = engine.get_run(run_id=run_id)
    assert result.ok, result.error
    steps = result.data["steps"]
    read_step = next(s for s in steps if s["step_id"] == "read")
    assert read_step["output"]["data"]["summary"].startswith("Insights for sample.csv")

    summarize_step = next(s for s in steps if s["step_id"] == "summarize")
    message = summarize_step["output"]["data"]["message"]
    assert "Dashboard summary" in message
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
