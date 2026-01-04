
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


@pytest.mark.integration
def test_ade_v1_flow_deterministic(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "ade.sqlite"
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

        payload = {
            "dataset": "sample.csv",
            "upload_id": "test_upload",
            "files": [{"name": "sample.csv", "file_type": "csv"}],
            "prompt": "Assess dataset adequacy and highlight key risks.",
        }

        first = engine.run_flow(product="ade", flow="ade_v1", payload=payload)
        assert first.ok, first.error
        assert first.data and first.data["status"] == "COMPLETED"

        second = engine.run_flow(product="ade", flow="ade_v1", payload=payload)
        assert second.ok, second.error
        assert second.data and second.data["status"] == "COMPLETED"

        first_run_id = first.data["run_id"]
        second_run_id = second.data["run_id"]

        first_run = engine.get_run(run_id=first_run_id)
        second_run = engine.get_run(run_id=second_run_id)
        assert first_run.ok and second_run.ok

        first_steps = first_run.data["steps"]
        second_steps = second_run.data["steps"]
        assemble_step = next(s for s in first_steps if s["step_id"] == "assemble_decision_packet")
        assemble_step_2 = next(s for s in second_steps if s["step_id"] == "assemble_decision_packet")

        packet = assemble_step["output"]["data"]["decision_packet"]
        packet_2 = assemble_step_2["output"]["data"]["decision_packet"]

        for required_key in (
            "question",
            "decision_summary",
            "confidence_level",
            "assumptions",
            "limitations",
            "sections",
            "trace_refs",
        ):
            assert required_key in packet

        assert packet["sections"]
        assert isinstance(packet["sections"], list)
        assert packet["sections"][0]["section_id"]
        assert packet == packet_2

        response_path = repo_root / "observability" / "ade" / first_run_id / "output" / "response.json"
        assert response_path.exists()
        response = json.loads(response_path.read_text(encoding="utf-8"))
        files = response.get("files") or []
        stored_names = [f.get("stored_name") for f in files]
        assert "decision_packet.html" in stored_names
        html_path = response_path.parent / "decision_packet.html"
        assert html_path.exists()
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
        shutil.rmtree(upload_dir, ignore_errors=True)
        if "first_run_id" in locals():
            shutil.rmtree(repo_root / "observability" / "ade" / first_run_id, ignore_errors=True)
        if "second_run_id" in locals():
            shutil.rmtree(repo_root / "observability" / "ade" / second_run_id, ignore_errors=True)
