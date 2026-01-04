from __future__ import annotations

# ==============================
# Tests: Orchestrator (Engine Basic + HITL Pause/Resume)
# ==============================

from pathlib import Path

import pytest

from core.config.loader import load_settings
from core.utils.product_loader import discover_products, register_enabled_products
from core.orchestrator.engine import OrchestratorEngine
from core.agents.registry import AgentRegistry
from core.tools.registry import ToolRegistry


@pytest.mark.integration
def test_engine_runs_and_pauses_on_hitl(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    configs_dir = repo_root / "configs"
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir(parents=True, exist_ok=True)
    secrets_path = secrets_dir / "secrets.yaml"
    sqlite_path = tmp_path / "engine_test.sqlite"

    secrets_path.write_text(
        "\n".join(
            [
                "secrets:",
                "  db:",
                f"    sqlite_path: '{sqlite_path.as_posix()}'",
                "",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(configs_dir=str(configs_dir), secrets_path=str(secrets_path))

    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        catalog = discover_products(settings, repo_root=repo_root)
        register_enabled_products(catalog, settings=settings)

        engine = OrchestratorEngine.from_settings(settings)

        started = engine.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "test"})
        assert started.ok, started.error
        run_id = started.data["run_id"]  # type: ignore[index]

        status = engine.get_run(run_id=run_id)
        assert status.ok, status.error
        assert status.data and status.data["run"]["status"] in ("PENDING_HUMAN", "pending_human")

        resumed = engine.resume_run(run_id=run_id, approval_payload={"approved": True, "notes": "ok"})
        assert resumed.ok, resumed.error

        status2 = engine.get_run(run_id=run_id)
        assert status2.ok, status2.error
        assert status2.data and status2.data["run"]["status"] in ("COMPLETED", "completed")
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
