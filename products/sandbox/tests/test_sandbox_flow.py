# ==============================
# Sandbox Golden Path Test
# ==============================
from __future__ import annotations

from pathlib import Path

import pytest

from core.config.loader import load_settings
from core.utils.product_loader import discover_products, register_enabled_products
from core.orchestrator.engine import OrchestratorEngine
from core.agents.registry import AgentRegistry
from core.tools.registry import ToolRegistry


@pytest.mark.integration
def test_sandbox_hello_world_end_to_end(tmp_path: Path) -> None:
    """
    Runs:
      echo -> HITL -> summary

    Uses sqlite backend via secrets override.
    """
    repo_root = Path(__file__).resolve().parents[3]
    configs_dir = repo_root / "configs"
    # Create temp secrets to force sqlite path into tmp_path
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir(parents=True, exist_ok=True)
    secrets_path = secrets_dir / "secrets.yaml"
    sqlite_path = tmp_path / "master_test.sqlite"

    secrets_path.write_text(
        "\n".join(
            [
                "# test secrets",
                "secrets:",
                "  db:",
                f"    sqlite_path: '{sqlite_path.as_posix()}'",
                "",
            ]
        ),
        encoding="utf-8",
    )

    # Load settings with injected paths (loader is expected to support this)
    settings = load_settings(configs_dir=str(configs_dir), secrets_path=str(secrets_path))

    # Discover + register products
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        catalog = discover_products(settings, repo_root=repo_root)
        register_enabled_products(catalog, settings=settings)

        engine = OrchestratorEngine.from_settings(settings)

        # Start run (should pause at HITL)
        start = engine.run_flow(product="sandbox", flow="hello_world", payload={"message": "hello"})
        assert start.ok, start.error
        assert start.data and start.data.get("run_id")
        run_id = start.data["run_id"]

        # Run should be pending human
        status1 = engine.get_run(run_id=run_id)
        assert status1.ok, status1.error
        assert status1.data and status1.data.get("run", {}).get("status") in ("PENDING_HUMAN", "pending_human")

        # Resume with approval
        resumed = engine.resume_run(run_id=run_id, approval_payload={"approved": True, "notes": "ok"})
        assert resumed.ok, resumed.error

        # Final status should be completed
        status2 = engine.get_run(run_id=run_id)
        assert status2.ok, status2.error
        assert status2.data and status2.data.get("run", {}).get("status") in ("COMPLETED", "completed")
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
