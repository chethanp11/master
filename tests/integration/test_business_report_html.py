from __future__ import annotations

# ==============================
# Integration: Business Report HTML
# ==============================

import json
import shutil
from pathlib import Path

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


@pytest.mark.integration
def test_business_report_html_generated(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "ade.sqlite"
    upload_id = "test_upload"
    upload_dir = repo_root / "products" / "ade" / "staging" / "input"
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_csv = upload_dir / "sample.csv"
    rows = [
        "Expense,H22024,H2025,H2026",
        "A,10,12,14",
        "B,20,22,18",
        "A,10,12,14",
    ]
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
                "prompt": "Summarize key trends and highlight anomalies.",
            },
        )
        assert started.ok, started.error
        assert started.data["status"] == "PAUSED_WAITING_FOR_USER"
        run_id = started.data["run_id"]

        user_input = engine.resume_run(
            run_id=run_id,
            user_input_response={
                "form_id": "viz_preferences",
                "values": {
                    "chart_type": "line",
                    "metric_focus": "mean",
                    "include_hypothesis_checks": True,
                    "notes": "",
                },
            },
        )
        assert user_input.ok, user_input.error
        assert user_input.data["status"] == "PENDING_HUMAN"

        approved = engine.resume_run(run_id=run_id, approval_payload={"approved": True}, decision="APPROVED")
        assert approved.ok, approved.error
        assert approved.data["status"] == "COMPLETED"

        response_path = repo_root / "observability" / "ade" / run_id / "output" / "response.json"
        response = json.loads(response_path.read_text(encoding="utf-8"))
        files = response.get("files") or []
        stored_names = [f.get("stored_name") for f in files]
        assert "business_report.html" in stored_names

        html_path = response_path.parent / "business_report.html"
        html = html_path.read_text(encoding="utf-8")
        assert "Executive summary" in html
        assert "primary-chart" in html or "Plotly.newPlot" in html
        assert "<details>" in html
        assert html.count("row-label\">A") == 1
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
        shutil.rmtree(upload_dir, ignore_errors=True)
        if "run_id" in locals():
            shutil.rmtree(repo_root / "observability" / "ade" / run_id, ignore_errors=True)
