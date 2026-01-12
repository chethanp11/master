"""
Golden Path Tests

These tests run flows against stored expected outputs to catch regressions.
Each golden path test:
1. Runs a flow with a specific payload
2. Compares outputs to stored expected.json files
3. Fails if outputs drift from expected

To update golden files after intentional changes:
    pytest tests/acceptance_intelligence/test_golden_paths.py --update-golden
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.contracts.run_schema import RunStatus
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products
from tests.acceptance_intelligence import test_helpers as helpers


GOLDEN_DIR = Path(__file__).parent / "golden"

# Golden path definitions: (product, flow, payload, expected_file)
GOLDEN_PATHS: List[Tuple[str, str, Dict[str, Any], str]] = [
    (
        "hello_world",
        "hello_world",
        {"keyword": "golden_test"},
        "hello_world_expected.json",
    ),
]


def _normalize_output(output: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize output by removing non-deterministic fields."""
    if not output:
        return {}

    normalized = {}
    for key, value in output.items():
        # Skip timestamp fields and IDs
        if key in ("timestamp", "ts", "created_at", "updated_at", "run_id", "event_id",
                   "ended_at", "started_at", "id", "latency_ms"):
            continue
        # Skip evidence IDs and URIs (contain UUIDs)
        if key in ("evidence", "artifacts", "content_ref", "source"):
            continue
        # Recursively normalize nested dicts
        if isinstance(value, dict):
            normalized[key] = _normalize_output(value)
        elif isinstance(value, list):
            # Skip lists that contain evidence items
            if key == "evidence":
                continue
            normalized[key] = [
                _normalize_output(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            normalized[key] = value

    return normalized


def _extract_golden_data(bundle: Any) -> Dict[str, Any]:
    """Extract comparable data from a run bundle."""
    data = {
        "status": bundle.run.status.value if hasattr(bundle.run.status, "value") else str(bundle.run.status),
        "product": bundle.run.product,
        "flow": bundle.run.flow,
        "steps": [],
    }

    for step in bundle.steps:
        step_data = {
            "step_id": step.step_id,
            "type": step.type,
            "status": step.status.value if hasattr(step.status, "value") else str(step.status),
        }
        if step.output:
            step_data["output"] = _normalize_output(step.output)
        data["steps"].append(step_data)

    return data


def _load_expected(filename: str) -> Optional[Dict[str, Any]]:
    """Load expected output from golden file."""
    path = GOLDEN_DIR / filename
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save_expected(filename: str, data: Dict[str, Any]) -> None:
    """Save expected output to golden file."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    path = GOLDEN_DIR / filename
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _compare_golden(actual: Dict[str, Any], expected: Dict[str, Any]) -> List[str]:
    """Compare actual output to expected, return list of differences."""
    differences: List[str] = []

    # Compare top-level fields
    for key in ["status", "product", "flow"]:
        if actual.get(key) != expected.get(key):
            differences.append(f"Field '{key}': expected {expected.get(key)!r}, got {actual.get(key)!r}")

    # Compare steps
    actual_steps = actual.get("steps", [])
    expected_steps = expected.get("steps", [])

    if len(actual_steps) != len(expected_steps):
        differences.append(f"Step count: expected {len(expected_steps)}, got {len(actual_steps)}")
    else:
        for i, (act_step, exp_step) in enumerate(zip(actual_steps, expected_steps)):
            for key in ["step_id", "type", "status"]:
                if act_step.get(key) != exp_step.get(key):
                    differences.append(
                        f"Step {i} '{key}': expected {exp_step.get(key)!r}, got {act_step.get(key)!r}"
                    )

            # Compare outputs (normalized)
            act_output = _normalize_output(act_step.get("output", {}))
            exp_output = _normalize_output(exp_step.get("output", {}))

            # Check critical output fields - ok field
            act_ok = act_output.get("ok")
            exp_ok = exp_output.get("ok")
            if act_ok != exp_ok:
                differences.append(
                    f"Step {i} output.ok: expected {exp_ok}, got {act_ok}"
                )

            # Compare data structure - check key data fields exist
            act_data = act_output.get("data", {})
            exp_data = exp_output.get("data", {})

            if isinstance(act_data, dict) and isinstance(exp_data, dict):
                # Check critical data fields match
                for data_key in exp_data:
                    if data_key not in act_data:
                        differences.append(f"Step {i} output.data missing key: {data_key}")
                    elif act_data[data_key] != exp_data[data_key]:
                        # Only flag differences for non-timestamp fields
                        if data_key not in ("timestamp", "ts", "created_at"):
                            differences.append(
                                f"Step {i} output.data[{data_key}]: expected {exp_data[data_key]!r}, got {act_data[data_key]!r}"
                            )

    return differences


@pytest.fixture
def update_golden(request) -> bool:
    """Check if --update-golden flag was passed."""
    return request.config.getoption("--update-golden", default=False)


def pytest_addoption(parser):
    """Add --update-golden option to pytest."""
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Update golden files with actual outputs",
    )


class TestGoldenPaths:
    """Run golden path tests comparing outputs to stored expected files."""

    @pytest.mark.parametrize("product,flow,payload,expected_file", GOLDEN_PATHS)
    def test_golden_path(
        self,
        orchestrator,
        trace_sink: List[dict],
        product: str,
        flow: str,
        payload: Dict[str, Any],
        expected_file: str,
    ) -> None:
        """Run golden path and compare to stored expected output."""
        # Register products
        settings = load_settings()
        AgentRegistry.clear()
        ToolRegistry.clear()
        catalog = discover_products(settings)
        register_enabled_products(catalog, settings=settings)

        trace_sink.clear()

        # Run the flow
        started = orchestrator.run_flow(product=product, flow=flow, payload=payload)
        assert started.ok, f"Failed to start flow: {started.error}"
        run_id = started.data["run_id"]

        # For flows with HITL, approve and continue
        bundle = orchestrator.memory.get_run(run_id)
        if bundle.run.status == RunStatus.PENDING_HUMAN:
            resumed = orchestrator.resume_run(
                run_id=run_id,
                approval_payload={"approved": True},
                decision="APPROVED",
            )
            assert resumed.ok, f"Failed to resume: {resumed.error}"
            bundle = orchestrator.memory.get_run(run_id)

        # Extract actual data
        actual = _extract_golden_data(bundle)

        # Load expected
        expected = _load_expected(expected_file)

        if expected is None:
            # First run - save the golden file
            _save_expected(expected_file, actual)
            pytest.skip(f"Created golden file: {expected_file}")
            return

        # Compare
        differences = _compare_golden(actual, expected)

        if differences:
            # Format nice error message
            diff_msg = "\n".join(f"  - {d}" for d in differences)
            pytest.fail(
                f"Golden path mismatch for {product}/{flow}:\n{diff_msg}\n\n"
                f"Run with --update-golden to update expected output."
            )


class TestGoldenPathIntegrity:
    """Tests to verify golden file integrity."""

    def test_all_golden_files_exist(self) -> None:
        """All referenced golden files exist."""
        missing: List[str] = []
        for _, _, _, expected_file in GOLDEN_PATHS:
            path = GOLDEN_DIR / expected_file
            if not path.exists():
                missing.append(expected_file)

        # Skip if files don't exist yet (they'll be created on first run)
        if missing:
            pytest.skip(f"Golden files not yet created: {missing}")

    def test_golden_files_are_valid_json(self) -> None:
        """All golden files contain valid JSON."""
        invalid: List[Tuple[str, str]] = []

        if not GOLDEN_DIR.exists():
            pytest.skip("Golden directory does not exist")

        for json_file in GOLDEN_DIR.glob("*.json"):
            try:
                json.loads(json_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                invalid.append((json_file.name, str(e)))

        assert not invalid, (
            f"Invalid JSON in golden files:\n"
            + "\n".join(f"  {f}: {e}" for f, e in invalid)
        )

    def test_golden_files_have_required_fields(self) -> None:
        """All golden files have required fields."""
        missing_fields: List[Tuple[str, List[str]]] = []
        required = {"status", "product", "flow", "steps"}

        if not GOLDEN_DIR.exists():
            pytest.skip("Golden directory does not exist")

        for json_file in GOLDEN_DIR.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                missing = required - set(data.keys())
                if missing:
                    missing_fields.append((json_file.name, list(missing)))
            except json.JSONDecodeError:
                continue  # Already caught by other test

        assert not missing_fields, (
            f"Golden files missing required fields:\n"
            + "\n".join(f"  {f}: {m}" for f, m in missing_fields)
        )
