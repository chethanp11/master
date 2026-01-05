from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


def _stage_sample_csv(repo_root: Path) -> None:
    upload_dir = repo_root / "products" / "ade" / "staging" / "input"
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_csv = upload_dir / "sample.csv"
    rows = ["Expense,H22024,H2025,H2026"]
    rows.append("A,10,20,30")
    rows.append("B,5,10,15")
    sample_csv.write_text("\n".join(rows), encoding="utf-8")


def _build_engine(tmp_path: Path, repo_root: Path) -> OrchestratorEngine:
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "ade.sqlite"
    settings = load_settings(
        repo_root=str(repo_root),
        configs_dir=str(repo_root / "configs"),
        env={
            "MASTER__APP__PATHS__STORAGE_DIR": storage_dir.as_posix(),
            "MASTER__SECRETS__MEMORY_DB_PATH": sqlite_path.as_posix(),
        },
    )
    catalog = discover_products(settings, repo_root=repo_root)
    register_enabled_products(catalog, settings=settings)
    return OrchestratorEngine.from_settings(settings)


@pytest.mark.integration
def test_business_report_quality_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        _stage_sample_csv(repo_root)
        engine = _build_engine(tmp_path, repo_root)

        started = engine.run_flow(
            product="ade",
            flow="ade_v1",
            payload={
                "dataset": "sample.csv",
                "prompt": "Summarize spend trend.",
                "files": [{"name": "sample.csv", "file_type": "csv"}],
            },
        )
        run_id = started.data["run_id"]
        engine.resume_run(
            run_id=run_id,
            user_input_response={
                "prompt_id": "clarify_intent",
                "free_text": "Analyze sample.csv using metric H2026 over H2024-H2026.",
            },
        )
        engine.resume_run(run_id=run_id, approval_payload={"approved": True}, decision="APPROVED")

        response_path = repo_root / "observability" / "ade" / run_id / "output" / "response.json"
        response = json.loads(response_path.read_text(encoding="utf-8"))
        files = {item.get("stored_name") for item in (response.get("files") or [])}
        assert "business_report.html" in files

        report_path = response_path.parent / "business_report.html"
        html = report_path.read_text(encoding="utf-8")
        assert "Executive summary" in html
        assert "What changed?" in html
        assert "So what?" in html
        assert "What next?" in html
        assert "primary-chart" in html
        assert html.count("Expense by period heatmap") == 1
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
        shutil.rmtree(repo_root / "products" / "ade" / "staging", ignore_errors=True)
        if "run_id" in locals():
            shutil.rmtree(repo_root / "observability" / "ade" / run_id, ignore_errors=True)
