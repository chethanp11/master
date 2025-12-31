# ==============================
# Parallel Failure Isolation
# ==============================
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.contracts.tool_schema import ToolError, ToolErrorCode, ToolMeta, ToolResult
from core.memory.router import MemoryRouter
from core.tools.base import BaseTool
from core.tools.registry import ToolRegistry, ToolRegistration
from core.utils.product_loader import discover_products, register_enabled_products


def _register_products():
    settings = load_settings()
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)
    return settings


class PayloadDrivenTool(BaseTool):
    name: str = "echo_tool"

    def run(self, params, ctx):
        fail = bool(ctx.run.payload.get("fail_run"))
        meta = ToolMeta(tool_name=self.name, backend="parallel")
        if fail:
            err = ToolError(
                code=ToolErrorCode.BACKEND_ERROR,
                message="forced failure",
                details={"run_id": ctx.run_id},
            )
            return ToolResult(ok=False, data=None, error=err, meta=meta)
        return ToolResult(ok=True, data={"echo": params.get("message", "")}, error=None, meta=meta)


def _override_echo(tool_cls) -> ToolRegistration | None:
    original = ToolRegistry._tools.get("echo_tool")
    ToolRegistry.register("echo_tool", tool_cls, overwrite=True)
    return original


def _restore_echo(registration: ToolRegistration | None) -> None:
    if registration:
        ToolRegistry._tools["echo_tool"] = registration
    else:
        ToolRegistry._tools.pop("echo_tool", None)


def test_parallel_failure_isolation(orchestrator, trace_sink: List[Dict[str, str]]) -> None:
    _register_products()
    original = _override_echo(lambda: PayloadDrivenTool())
    try:
        def run_task(marker: str, fail: bool):
            payload = {"keyword": f"run-{marker}", "fail_run": fail}
            res = orchestrator.run_flow(product="hello_world", flow="hello_world", payload=payload)
            return res.data["run_id"], fail

        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(run_task, "a", False),
                executor.submit(run_task, "b", False),
                executor.submit(run_task, "c", True),
            ]
            for future in futures:
                results.append(future.result())

        memory = orchestrator.memory  # type: ignore[assignment]
        failed_runs = []
        success_runs = []
        for run_id, is_failed in results:
            bundle = memory.get_run(run_id)
            assert bundle
            if is_failed:
                failed_runs.append(run_id)
                assert bundle.run.status != "COMPLETED"
            else:
                success_runs.append(run_id)
                orchestrator.resume_run(run_id=run_id, approval_payload={"approved": True})
                bundle = memory.get_run(run_id)
                assert bundle.run.status == "COMPLETED"

        assert len(failed_runs) == 1
        assert len(success_runs) == 2

        failure_events = [event for event in trace_sink if event["run_id"] in failed_runs]
        assert failure_events, f"No trace events for failed runs: {failed_runs}"
        assert any(event["kind"] == "tool_call_attempt_failed" for event in failure_events), f"Events: {[e['kind'] for e in failure_events]}"
        assert all(
            event["run_id"] in failed_runs
            for event in failure_events
            if event["kind"] == "tool_call_attempt_failed"
        )

        success_events = [event for event in trace_sink if event["run_id"] in success_runs]
        assert all(event["kind"] != "step_failed" for event in success_events)
        assert success_events
    finally:
        _restore_echo(original)
