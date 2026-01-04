from __future__ import annotations

# ==============================
# Analytical Decision Engine Orchestrator Flow Test
# ==============================

import shutil
import json
from pathlib import Path

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


@pytest.mark.integration
def test_ade_overview_flow(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "ade.sqlite"
    upload_id = "test_upload"
    upload_dir = repo_root / "products" / "ade" / "staging" / "input"
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_csv = upload_dir / "sample.csv"
    rows = ["date,value"]
    values = [10, 20, 30, 40, 50, 60, 70] * 3
    for idx, value in enumerate(values):
        rows.append(f"2024-01-{idx + 1:02d},{value}")
    sample_csv.write_text("\n".join(rows), encoding="utf-8")

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
            product="ade",
            flow="ade_v1",
            payload={
                "dataset": "sample.csv",
                "upload_id": upload_id,
                "files": [{"name": "sample.csv", "file_type": "csv"}],
                "prompt": "Assess dataset adequacy and highlight key risks.",
            },
        )
        assert started.ok, started.error
        assert started.data and started.data["status"] == "COMPLETED"

        run_id = started.data["run_id"]
        result = engine.get_run(run_id=run_id)
        assert result.ok, result.error
        steps = result.data["steps"]
        read_step = next(s for s in steps if s["step_id"] == "read")
        assert read_step["output"]["data"]["summary"].startswith("Insights for sample.csv")

        assemble_step = next(s for s in steps if s["step_id"] == "assemble_decision_packet")
        packet = assemble_step["output"]["data"]["decision_packet"]
        assert packet["sections"]

        response_path = repo_root / "observability" / "ade" / run_id / "output" / "response.json"
        assert response_path.exists()
        response = json.loads(response_path.read_text(encoding="utf-8"))
        assert "output_files" not in (response.get("result") or {})
        files = response.get("files") or []
        stored_names = [f.get("stored_name") for f in files]
        assert "decision_packet.html" in stored_names
        assert response.get("response_version") == "1.0"
        assert len(set(stored_names)) == len(stored_names)

        html_path = response_path.parent / "decision_packet.html"
        assert html_path.exists()

        events_path = repo_root / "observability" / "ade" / run_id / "runtime" / "events.jsonl"
        events_text = events_path.read_text(encoding="utf-8")
        assert "user_input_requested" not in events_text
        assert "content_base64" not in events_text
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
        shutil.rmtree(upload_dir, ignore_errors=True)
        shutil.rmtree(repo_root / "products" / "ade" / "staging", ignore_errors=True)
        if "run_id" in locals():
            shutil.rmtree(repo_root / "observability" / "ade" / run_id, ignore_errors=True)
