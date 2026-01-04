from __future__ import annotations

# ==============================
# Hello World Golden Path Test
# ==============================

import json
from pathlib import Path

import pytest

from core.config.loader import load_settings
from core.utils.product_loader import discover_products, register_enabled_products
from core.orchestrator.engine import OrchestratorEngine
from core.agents.registry import AgentRegistry
from core.tools.registry import ToolRegistry


@pytest.mark.integration
def test_hello_world_end_to_end(tmp_path: Path) -> None:
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
        start = engine.run_flow(product="hello_world", flow="hello_world", payload={"keyword": "hello"})
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

        steps = status2.data["steps"]
        assert steps, "Expected persisted steps for hello_world run"
        echo_step = next((s for s in steps if s["step_id"] == "echo"), None)
        assert echo_step is not None
        echo_output = echo_step["output"]
        assert echo_output and echo_output["data"]["echo"] == "hello"
        assert "timestamp" in echo_output["data"]

        summary_step = next((s for s in steps if s["step_id"] == "summary"), None)
        assert summary_step is not None
        summary_output = summary_step["output"]
        assert summary_output and summary_output.get("ok") is True
        summary_data = summary_output["data"]
        assert summary_data["details"]["message"] == "hello"
        assert summary_data["details"]["approved"] is True
        assert "summary" in summary_data

        observability_root = repo_root / "observability" / "hello_world" / run_id
        input_path = observability_root / "input" / "input.json"
        events_path = observability_root / "runtime" / "events.jsonl"
        response_path = observability_root / "output" / "response.json"
        assert input_path.exists()
        assert events_path.exists()
        assert response_path.exists()
        response = json.loads(response_path.read_text(encoding="utf-8"))
        assert response["status"] == "COMPLETED"
        assert response["result"] is not None
        events = events_path.read_text(encoding="utf-8").splitlines()
        assert any('"output_written"' in line for line in events)
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
