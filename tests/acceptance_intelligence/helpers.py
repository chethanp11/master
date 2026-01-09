from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Dict, Tuple

from core.agents.registry import AgentRegistry
from core.config.loader import load_settings
from core.config.schema import Settings
from core.governance.security import SecurityRedactor
from core.memory.in_memory import InMemoryBackend
from core.memory.router import MemoryRouter
from core.memory.tracing import Tracer
from core.orchestrator.engine import OrchestratorEngine
from core.tools.registry import ToolRegistry
from core.utils.product_loader import discover_products, register_enabled_products

REGISTRY_TEMPLATE = dedent(
    """\
    from __future__ import annotations

    from core.agents.base import BaseAgent
    from core.contracts.agent_schema import AgentMeta, AgentResult
    from core.contracts.plan_schema import EstimatedCost, PlanProposal, PlanStep
    from core.utils.product_loader import ProductRegistries
    from products.hello_world.agents.simple_agent import build as build_simple_agent
    from products.hello_world.tools.echo_tool import build as build_echo_tool


    class AcceptancePlanAgent(BaseAgent):
        name: str = "acceptance_plan_agent"
        description: str = "Deterministic plan proposal agent for acceptance tests."

        def run(self, step_context):
            payload = step_context.run.payload or {}
            message = str(payload.get("message") or payload.get("prompt") or "no message")
            plan = PlanProposal(
                summary=f"Echo the message {message!r}",
                steps=[
                    PlanStep(
                        step_id="plan_echo",
                        description="Call echo_tool with the current payload.",
                        step_type="tool",
                        tool="echo_tool",
                        requires_approval=False,
                    )
                ],
                required_tools=["echo_tool"],
                approvals=[],
                estimated_cost=EstimatedCost(currency="USD", amount=0.0, tokens=0),
            )
            meta = AgentMeta(agent_name=self.name, tags={"product": step_context.product, "flow": step_context.flow})
            return AgentResult(ok=True, data=plan.model_dump(mode="json"), error=None, meta=meta)


    def build_plan_agent() -> AcceptancePlanAgent:
        return AcceptancePlanAgent()


    def register(registries: ProductRegistries) -> None:
        registries.tool_registry.register(build_echo_tool().name, build_echo_tool)
        registries.agent_registry.register(build_simple_agent().name, build_simple_agent)
        registries.agent_registry.register(build_plan_agent().name, build_plan_agent)
    """
)


def write_registry(path: Path) -> None:
    """Drop the shared registry template into the product directory."""
    path.write_text(REGISTRY_TEMPLATE, encoding="utf-8")


def build_product(
    repo_root: Path,
    *,
    product_name: str,
    flows: Dict[str, str],
) -> Path:
    product_dir = repo_root / "products" / product_name
    flows_dir = product_dir / "flows"
    config_dir = product_dir / "config"
    product_dir.mkdir(parents=True, exist_ok=True)
    flows_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    manifest = f"name: {product_name}\nflows: [{', '.join(flows.keys())}]\n"
    (product_dir / "manifest.yaml").write_text(manifest, encoding="utf-8")
    (config_dir / "product.yaml").write_text(f"name: {product_name}\n", encoding="utf-8")
    for name, content in flows.items():
        (flows_dir / f"{name}.yaml").write_text(dedent(content).lstrip("\n"), encoding="utf-8")

    write_registry(product_dir / "registry.py")
    return product_dir


def build_acceptance_engine(repo_root: Path, product_name: str) -> Tuple[OrchestratorEngine, Settings]:
    """Create an orchestrator wired to a temporary repo layout."""
    settings = load_settings(repo_root=str(repo_root))
    AgentRegistry.clear()
    ToolRegistry.clear()
    catalog = discover_products(settings)
    register_enabled_products(catalog, settings=settings)

    backend = InMemoryBackend()
    memory = MemoryRouter(backend=backend, repo_root=repo_root, observability_root=repo_root / "observability")
    tracer = Tracer(memory=memory, redactor=SecurityRedactor(), mirror_to_log=False)
    engine = OrchestratorEngine.from_settings(settings=settings, memory=memory, tracer=tracer, sleep_fn=lambda _: None)
    return engine, settings
