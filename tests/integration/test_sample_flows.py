# ==============================
# Integration Tests: Golden Path (Core + Hello World Product)
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
def test_sample_flow_hello_world(tmp_path: Path, hello_world_test_env: Path) -> None:
    """
    Runs:
      echo -> HITL -> summary

    The hello_world_test_env fixture handles sqlite/secrets overrides so other integration suites can reuse the same storage location.
    """
    repo_root = Path(__file__).resolve().parents[2]
    configs_dir = repo_root / "configs"
    settings = load_settings(configs_dir=str(configs_dir))
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        catalog = discover_products(settings, repo_root=repo_root)
        register_enabled_products(catalog, settings=settings)

        engine = OrchestratorEngine.from_settings(settings)

        started = engine.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "hello"})
        assert started.ok, started.error
        run_id = started.data["run_id"]  # type: ignore[index]

        # Approve
        resumed = engine.resume_run(run_id=run_id, approval_payload={"approved": True, "notes": "ok"})
        assert resumed.ok, resumed.error

        final = engine.get_run(run_id=run_id)
        assert final.ok, final.error
        assert final.data and final.data["run"]["status"] in ("COMPLETED", "completed")
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
