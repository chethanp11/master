from __future__ import annotations

# ==============================
# Integration: CLI Runs
# ==============================

import json
from pathlib import Path
from typing import List, Tuple

import pytest

from core.agents.registry import AgentRegistry
from core.tools.registry import ToolRegistry
from gateway.cli import main as cli_main


def _run_cli(args: List[str], capsys) -> Tuple[int, dict]:
    code = cli_main.main(args)
    captured = capsys.readouterr()
    output = captured.out.strip()
    data = json.loads(output) if output else {}
    return code, data


@pytest.mark.integration
def test_cli_run_resume_flow(tmp_path, monkeypatch, capsys) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "cli.sqlite"
    monkeypatch.setenv("MASTER__APP__PATHS__REPO_ROOT", repo_root.as_posix())
    monkeypatch.setenv("MASTER__APP__PATHS__STORAGE_DIR", storage_dir.as_posix())
    monkeypatch.setenv("MASTER__SECRETS__MEMORY_DB_PATH", sqlite_path.as_posix())

    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        code, products = _run_cli(["list-products"], capsys)
        assert code == 0
        assert "hello_world" in products["products"]

        code, flows = _run_cli(["list-flows", "--product", "hello_world"], capsys)
        assert code == 0
        assert "hello_world" in flows["flows"]

        code, started = _run_cli(
            [
                "run",
                "--product",
                "hello_world",
                "--flow",
                "hello_world",
                "--payload",
                '{"keyword":"CLI"}',
            ],
            capsys,
        )
        assert code == 0
        assert started["ok"] is True
        run_id = started["data"]["run_id"]
        assert started["data"]["status"] == "PENDING_HUMAN"

        code, pending = _run_cli(["status", "--run-id", run_id], capsys)
        assert code == 0
        assert pending["ok"] is True
        assert pending["data"]["run"]["status"] == "PENDING_HUMAN"

        code, approvals = _run_cli(["approvals"], capsys)
        assert code == 0
        assert approvals["approvals"], "Expected at least one pending approval"

        code, resumed = _run_cli(
            [
                "resume",
                "--run-id",
                run_id,
                "--approve",
                "--payload",
                '{"approved": true}',
            ],
            capsys,
        )
        assert code == 0
        assert resumed["ok"] is True

        code, final = _run_cli(["status", "--run-id", run_id], capsys)
        assert code == 0
        assert final["data"]["run"]["status"] == "COMPLETED"
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()


@pytest.mark.integration
def test_cli_resume_rejection_marks_failed(tmp_path, monkeypatch, capsys) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "cli.sqlite"
    monkeypatch.setenv("MASTER__APP__PATHS__REPO_ROOT", repo_root.as_posix())
    monkeypatch.setenv("MASTER__APP__PATHS__STORAGE_DIR", storage_dir.as_posix())
    monkeypatch.setenv("MASTER__SECRETS__MEMORY_DB_PATH", sqlite_path.as_posix())

    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        _, _ = _run_cli(["list-products"], capsys)
        _, _ = _run_cli(["list-flows", "--product", "hello_world"], capsys)

        _, started = _run_cli(
            [
                "run",
                "--product",
                "hello_world",
                "--flow",
                "hello_world",
                "--payload",
                '{"keyword":"CLI"}',
            ],
            capsys,
        )
        run_id = started["data"]["run_id"]

        _, rejection = _run_cli(
            [
                "resume",
                "--run-id",
                run_id,
                "--reject",
                "--payload",
                '{"approved": false}',
            ],
            capsys,
        )
        assert rejection["ok"] is True
        assert rejection["data"]["status"] == "FAILED"

        _, final = _run_cli(["status", "--run-id", run_id], capsys)
        assert final["data"]["run"]["status"] == "FAILED"
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()


@pytest.mark.integration
def test_cli_resume_missing_payload_fails(tmp_path, monkeypatch, capsys) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    storage_dir = tmp_path / "storage"
    sqlite_path = tmp_path / "cli.sqlite"
    monkeypatch.setenv("MASTER__APP__PATHS__REPO_ROOT", repo_root.as_posix())
    monkeypatch.setenv("MASTER__APP__PATHS__STORAGE_DIR", storage_dir.as_posix())
    monkeypatch.setenv("MASTER__SECRETS__MEMORY_DB_PATH", sqlite_path.as_posix())

    AgentRegistry.clear()
    ToolRegistry.clear()
    try:
        _, _ = _run_cli(["list-products"], capsys)
        _, _ = _run_cli(["list-flows", "--product", "hello_world"], capsys)

        _, started = _run_cli(
            [
                "run",
                "--product",
                "hello_world",
                "--flow",
                "hello_world",
                "--payload",
                '{"keyword":"CLI"}',
            ],
            capsys,
        )
        run_id = started["data"]["run_id"]

        code, failure = _run_cli(
            [
                "resume",
                "--run-id",
                run_id,
                "--approve",
            ],
            capsys,
        )
        assert code != 0
        assert failure["ok"] is False
        assert failure["error"]["code"] == "missing_approval_field"
    finally:
        AgentRegistry.clear()
        ToolRegistry.clear()
