from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.contracts.run_schema import RunStatus
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products


def _stage_sample_csv(repo_root: Path) -> None:
    upload_dir = repo_root / "products" / "ade" / "staging" / "input"
    upload_dir.mkdir(parents=True, exist_ok=True)
    sample_csv = upload_dir / "sample.csv"
    rows = ["date,value"]
    for idx in range(1, 10):
        rows.append(f"2024-01-{idx:02d},{idx * 10}")
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
def test_ade_user_input_pause_resume(tmp_path: Path) -> None:
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
                "prompt": "Summarize sales trend.",
                "files": [{"name": "sample.csv", "file_type": "csv"}],
            },
        )
        assert started.ok, started.error
        assert started.data["status"] == RunStatus.PAUSED_WAITING_FOR_USER.value
        run_id = started.data["run_id"]

        invalid = engine.resume_run(
            run_id=run_id,
            user_input_response={"prompt_id": "clarify_intent", "free_text": ""},
        )
        assert not invalid.ok
        assert invalid.error is not None

        valid = engine.resume_run(
            run_id=run_id,
            user_input_response={
                "prompt_id": "clarify_intent",
                "free_text": "Analyze sample.csv using metric value over last 9 days.",
            },
        )
        assert valid.ok, valid.error
        assert valid.data["status"] == RunStatus.PENDING_HUMAN.value
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
        shutil.rmtree(repo_root / "products" / "ade" / "staging", ignore_errors=True)
        if "run_id" in locals():
            shutil.rmtree(repo_root / "observability" / "ade" / run_id, ignore_errors=True)


@pytest.mark.integration
def test_ade_approval_reject_replan_limit(tmp_path: Path) -> None:
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
                "prompt": "Explain why sales dropped.",
                "files": [{"name": "sample.csv", "file_type": "csv"}],
            },
        )
        assert started.ok, started.error
        run_id = started.data["run_id"]

        valid = engine.resume_run(
            run_id=run_id,
            user_input_response={
                "prompt_id": "clarify_intent",
                "free_text": "Analyze sample.csv using metric value over last 9 days.",
            },
        )
        assert valid.ok, valid.error
        assert valid.data["status"] == RunStatus.PENDING_HUMAN.value

        rejected_once = engine.resume_run(
            run_id=run_id,
            approval_payload={"approved": False},
            decision="REJECTED",
            comment="Adjust plan",
        )
        assert rejected_once.ok, rejected_once.error
        assert rejected_once.data["status"] == RunStatus.PENDING_HUMAN.value

        rejected_twice = engine.resume_run(
            run_id=run_id,
            approval_payload={"approved": False},
            decision="REJECTED",
            comment="Still not right",
        )
        assert rejected_twice.ok, rejected_twice.error
        assert rejected_twice.data["status"] == RunStatus.FAILED.value
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
        shutil.rmtree(repo_root / "products" / "ade" / "staging", ignore_errors=True)
        if "run_id" in locals():
            shutil.rmtree(repo_root / "observability" / "ade" / run_id, ignore_errors=True)
