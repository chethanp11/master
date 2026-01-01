# ==============================
# Visual Insights Orchestrator Flow Test
# ==============================
from __future__ import annotations

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
def test_visual_insights_overview_flow(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "visual_insights.sqlite"
    upload_id = "test_upload"
    upload_dir = repo_root / "products" / "visual_insights" / "staging" / "input"
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_csv = upload_dir / "sample.csv"
    sample_csv.write_text("col_a,col_b\n1,2\n3,4\n", encoding="utf-8")

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
            payload={
                "dataset": "sample.csv",
                "upload_id": upload_id,
                "files": [{"name": "sample.csv", "file_type": "csv"}],
            },
        )
        assert started.ok, started.error
        assert started.data and started.data["status"] == "PENDING_HUMAN"

        run_id = started.data["run_id"]
        resumed = engine.resume_run(run_id=run_id, approval_payload={"approved": True, "notes": "ok"})
        assert resumed.ok, resumed.error

        resumed_export = engine.resume_run(run_id=run_id, approval_payload={"approved": True, "notes": "ok"})
        assert resumed_export.ok, resumed_export.error

        result = engine.get_run(run_id=run_id)
        assert result.ok, result.error
        steps = result.data["steps"]
        read_step = next(s for s in steps if s["step_id"] == "read")
        assert read_step["output"]["data"]["summary"].startswith("Insights for sample.csv")

        summarize_step = next(s for s in steps if s["step_id"] == "summarize")
        message = summarize_step["output"]["data"]["message"]
        assert "Dashboard summary" in message

        response_path = repo_root / "observability" / "visual_insights" / run_id / "output" / "response.json"
        assert response_path.exists()
        response = json.loads(response_path.read_text(encoding="utf-8"))
        assert "output_files" not in (response.get("result") or {})
        files = response.get("files") or []
        stored_names = [f.get("stored_name") for f in files]
        assert "visualization.pdf" in stored_names
        assert "visualization_stub.json" in stored_names
        stub_entry = next((f for f in files if f.get("stored_name") == "visualization_stub.json"), None)
        assert stub_entry is not None
        assert stub_entry.get("content_type") == "application/json"
        assert stub_entry.get("role") == "supporting"
        pdf_entry = next((f for f in files if f.get("stored_name") == "visualization.pdf"), None)
        assert pdf_entry is not None
        assert pdf_entry.get("role") == "primary"
        assert response.get("response_version") == "1.0"
        assert len(set(stored_names)) == len(stored_names)
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
        shutil.rmtree(upload_dir, ignore_errors=True)
        shutil.rmtree(repo_root / "products" / "visual_insights" / "staging", ignore_errors=True)
        if "run_id" in locals():
            shutil.rmtree(repo_root / "observability" / "visual_insights" / run_id, ignore_errors=True)
