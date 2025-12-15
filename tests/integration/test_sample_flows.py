# ==============================
# Integration Tests: Golden Path (Core + Sandbox Product)
# ==============================
from __future__ import annotations

from pathlib import Path

import pytest

from core.config.loader import load_settings
from core.utils.product_loader import discover_products, safe_register_all
from core.orchestrator.engine import OrchestratorEngine


@pytest.mark.integration
def test_sample_flow_sandbox_hello_world(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    configs_dir = repo_root / "configs"
    products_dir = repo_root / "products"

    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir(parents=True, exist_ok=True)
    secrets_path = secrets_dir / "secrets.yaml"
    sqlite_path = tmp_path / "it.sqlite"

    secrets_path.write_text(
        "\n".join(
            [
                "secrets:",
                "  db:",
                f"    sqlite_path: '{sqlite_path.as_posix()}'",
                "",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(configs_dir=str(configs_dir), secrets_path=str(secrets_path))
    reg = discover_products(str(products_dir))
    safe_register_all(reg, enabled_products=["sandbox"])

    engine = OrchestratorEngine.from_settings(settings)

    started = engine.run_flow(product="sandbox", flow="hello_world", payload={"message": "hello"})
    assert started.ok, started.error
    run_id = started.data["run_id"]  # type: ignore[index]

    # Approve
    resumed = engine.resume_run(run_id=run_id, approval_payload={"approved": True, "notes": "ok"})
    assert resumed.ok, resumed.error

    final = engine.get_run(run_id=run_id)
    assert final.ok, final.error
    assert final.data and final.data["run"]["status"] in ("COMPLETED", "completed")