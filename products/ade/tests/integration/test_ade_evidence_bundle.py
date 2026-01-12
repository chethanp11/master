from __future__ import annotations

# ==============================
# Integration: ADE Evidence Bundle
# ==============================
"""
Test that the ADE flow correctly assembles evidence bundles
with proper provenance tracking for all tool outputs.

This test validates:
- Evidence items are created by tools
- Each item has tool_step_id, dataset_id, inputs_hash
- Evidence bundle aggregates all items correctly
"""

import shutil
from pathlib import Path

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


@pytest.mark.integration
def test_ade_evidence_bundle_created(tmp_path: Path, ade_product_path: Path) -> None:
    repo_root = ade_product_path.parents[1]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "ade.sqlite"
    upload_id = "test_upload"
    upload_dir = ade_product_path / "staging" / "input"
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_csv = upload_dir / "sample.csv"
    rows = ["Expense,H22024,H2025,H2026", "A,10,12,14", "B,20,22,18"]
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

        result = engine.get_run(run_id=run_id)
        assert result.ok, result.error
        steps = result.data["steps"]
        evidence_step = next(s for s in steps if s["step_id"] == "assemble_evidence_bundle")
        evidence_bundle = evidence_step["output"]["data"]["evidence_bundle"]
        assert evidence_bundle["items"]
        for item in evidence_bundle["items"]:
            assert item.get("tool_step_id")
            assert item.get("dataset_id")
            assert item.get("inputs_hash")
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
        shutil.rmtree(upload_dir, ignore_errors=True)
        if "run_id" in locals():
            shutil.rmtree(repo_root / "observability" / "ade" / run_id, ignore_errors=True)
