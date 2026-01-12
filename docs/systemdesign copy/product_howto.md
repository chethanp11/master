# Product How-To — master/

This document explains **how to build and ship a product** on top of the `master/` platform.  
Products are thin bundles that plug into the shared runtime; **no core changes are needed**.

**Last Updated:** 12 January 2026

---

## 1. Product Principles

- Thin: products only define flows, agents, tools, and config.
- Safe: obey the platform laws (no env reads outside config loader, no persistence outside `core/memory`, no direct tool execution).
- Declarative: flows/policies belong in YAML; behavior is wired via manifests.
- Testable: each product can ship regression suites that run via sqlite when enabled.

## 2. Product Layout

Products live under `products/<product_name>/` with the following required structure:

```
products/<product>/
├── manifest.yaml                  # Metadata + flows + UI/API flags
├── config/
│   └── product.yaml               # Product-specific defaults (required)
├── flows/                         # Flow definitions (YAML)
├── agents/                        # BaseAgent implementations
├── tools/                         # BaseTool implementations
├── registry.py                    # Safe registration hook (ProductRegistries)
└── tests/                         # Optional product-level regression tests
```

```mermaid
flowchart TB
  Manifest[manifest.yaml] --> Loader[Product Loader]
  Config[config/product.yaml] --> Loader
  Registry[registry.py] --> Loader
  Flows[flows/*.yaml] --> Loader
  Decorators[@agent/@tool] --> AutoDiscover[Auto-Discovery]
  AutoDiscover --> Loader
  Loader --> Orchestrator
  Loader --> Gateway
```

There is no scaffolding script; create the product layout manually following this document. The `registry.py` can use auto-discovery or explicit registration.

## 3. Manifest & Config

`manifest.yaml` declares the product catalog entry. Provide:

- `name`, `display_name`, `description`, `version`
- `default_flow`
- `exposed_api` (enabled + allowed_flows)
- `ui_enabled` and `ui` (nav label, panels, icon, category)
- `flows`: optional curated list of flow IDs published by the product

`config/product.yaml` is required and may include:
- `name` (required; defaults to manifest name if omitted)
- `defaults`, `limits`, `flags`, `metadata` (freeform dictionaries)

Product config is surfaced via the product catalog/API and can be injected into agents/tools by the caller; it is not merged into the global Settings loader automatically.

## 4. Flow Definitions

Flows live under `flows/*.yaml`. Each flow defines a sequence of steps referencing registered agents/tools, `human_approval`, `user_input`, and control steps (`branch`, `repeat_until`, `plan_*`, `tool_batch`). Example snippet:

```yaml
id: hello_world
autonomy_level: suggest_only

steps:
  - id: echo
    type: tool
    tool: echo_tool
    backend: local
    params:
      message: "{{payload.keyword}}"
    retry:
      max_attempts: 2
      backoff_seconds: 1
  - id: approval
    type: human_approval
    title: Review the echoed message
    message: Please approve or reject the output.
  - id: summary
    type: agent
    agent: simple_agent
```

The flow loader normalizes step IDs and loads step definitions for the orchestrator to execute.

## 5. Agents & Tools

### Using Decorators (Recommended)

Agents and tools can use decorators for auto-discovery:

```python
# products/<name>/agents/my_agent.py
from core.agents.base import agent, BaseAgent
from core.contracts.agent_schema import AgentResult, StepContext

@agent(
    name="product.my_agent",
    purpose="Describe what this agent does",
    capabilities=["capability_a", "capability_b"],
)
class MyAgent(BaseAgent):
    def run(self, ctx: StepContext) -> AgentResult:
        # Agent implementation
        return AgentResult(ok=True, data={"result": "value"})
```

```python
# products/<name>/tools/my_tool.py
from core.tools.base import tool, BaseTool
from core.contracts.tool_schema import ToolResult

@tool(
    name="product.my_tool",
    description="Describe what this tool does",
    read_only=True,
    side_effect=False,
)
class MyTool(BaseTool):
    def run(self, params: dict, ctx=None) -> ToolResult:
        # Tool implementation
        return ToolResult(ok=True, data={"result": "value"})
```

### Agent Rules

Agents (`BaseAgent`) operate on `StepContext`, inspect payload/artifacts, and return an `AgentResult`. They must not:
- Execute tools directly
- Call vendors/models directly (use `llm_reasoner`)
- Write to disk
- Read environment variables

If a flow needs LLM output, reference the built-in `llm_reasoner` agent in the flow definition.
LLM calls require an explicit reasoning purpose (`INSIGHT`, `PRIORITIZATION`, `EXPLANATION`, `UNCERTAINTY`).

### Tool Rules

Tools (`BaseTool`) perform deterministic actions and return a `ToolResult`. Tool execution always flows through `core/tools/executor.py`, which applies governance hooks and redaction. Retry policy is enforced by the orchestrator on tool steps only.

Tools marked `read_only=True` and `side_effect=False` are eligible for `tool_batch` steps.

## 6. Registration

Every product must provide `products/<name>/registry.py`. Two approaches:

### Option A: Auto-Discovery (Recommended)

```python
from pathlib import Path
from core.utils.product_loader import ProductRegistries, auto_register

def register(registries: ProductRegistries) -> None:
    auto_register(registries, product_path=Path(__file__).parent)
```

This automatically discovers all agents and tools with `@agent` and `@tool` decorators.

### Option B: Explicit Registration

```python
from core.utils.product_loader import ProductRegistries
from products.myproduct.agents.my_agent import MyAgent
from products.myproduct.tools.my_tool import MyTool

def register(registries: ProductRegistries) -> None:
    registries.agent_registry.register("product.my_agent", MyAgent)
    registries.tool_registry.register("product.my_tool", lambda: MyTool())
```

`ProductRegistries` bundles the global `AgentRegistry` and `ToolRegistry` plus settings. The loader imports each registry module, calls `register(...)`, and only then exposes the product's flows to the API/UI. Keep registry imports side-effect-free and idempotent.
Registries accept factories only; do not register shared instances or module-level mutable state.

## 7. Testing & Validation

Product tests belong under `products/<name>/tests/`. Hello World ships `products/hello_world/tests/test_hello_world_flow.py`, which:

- Boots settings via `load_settings(configs_dir=..., secrets_path=...)` to point the sqlite backend into a temp path
- Discovers/registers the hello_world product
- Runs `hello_world`, asserts the run pauses for HITL, resumes with an approval payload, and inspects persisted step outputs (echo + summary)

Use pytest to keep the golden path deterministic (sqlite backend only when enabled, no network).

## 8. Running the Product

Once registered, the gateway exposes:

- `GET /api/products` + `/api/products/{product}/flows` (driven by manifests + discovery)
- `GET /api/runs` and `GET /api/approvals` for run/approval lists
- `GET /api/runs/{run_id}/pending_input` for pending user input prompts
- `POST /api/runs/{run_id}/user_input` to submit user input answers
- `POST /api/run/{product}/{flow}` to start flows (payload or optional `text` field)
- `POST /api/resume_run/{run_id}` to resolve HITL approvals
- CLI commands (`master list-products`, `master run`, `master resume`, `master approvals`)
- Streamlit control center (`gateway/ui/platform_app.py`) that lists products, flows, run history, and approvals

## Recap

- Products ship manifests, configs, flows, agents, tools, registries, and optional tests.
- Use `@agent` and `@tool` decorators for auto-discovery (reduces boilerplate by ~80%).
- The product loader discovers manifests deterministically, registers components safely, and feeds the gateway/orchestrator.
- Tests run via sqlite to prove the golden path (`tool → HITL → agent summary`) behaves under audit-ready persistence.
- All agents/tools are governed by platform policies; no custom governance in products.
