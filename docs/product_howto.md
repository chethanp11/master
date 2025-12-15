# Product How-To — master/

This document explains **how to build a new product** on top of the `master/` agentic platform.

It is written for product teams and prototype builders.
No core changes are required.

---

## 1. What Is a Product?

A product is a **thin, isolated package** that defines:
- Flows
- Agents
- Tools
- Prompts
- Product-level config

A product **does not**:
- Modify core logic
- Implement orchestration
- Handle persistence
- Enforce governance

---

## 2. Product Location

All products live under:

products/<product_name>/

Example:

products/sandbox/

---

## 3. Required Product Structure

products/<product>/
├── flows/
├── agents/
├── tools/
├── prompts/
├── manifest.yaml
├── config/
│   └── product.yaml
├── registry.py
└── tests/

---

## 4. Step-by-Step: Creating a New Product

### Step 1: Scaffold the Product

python scripts/create_product.py sandbox

(Or create the folders manually.)

⸻

### Step 2: Define Product Config

Files:

- products/sandbox/manifest.yaml
- products/sandbox/config/product.yaml

Example `manifest.yaml`:

```
name: sandbox
display_name: "Sandbox"
description: "Demo product"
version: "0.1.0"

default_flow: "hello_world"

exposed_api:
  enabled: true
  allowed_flows:
    - "hello_world"

ui_enabled: true
ui:
  enabled: true
  nav_label: "Sandbox"
  panels:
    - id: "runner"
      title: "Run a Flow"

flows:
  - "hello_world"
```

Example `config/product.yaml`:

```
name: sandbox

defaults:
  autonomy_level: "semi_auto"

limits:
  max_steps: 50

flags:
  enable_tools: true
```


⸻

### Step 3: Create a Flow

File:

products/sandbox/flows/hello_world.yaml

Example:

id: hello_world
autonomy_level: semi_auto

steps:
  - id: generate
    type: agent
    agent: simple_agent

  - id: approve
    type: human_approval
    message: "Approve output?"

  - id: finish
    type: agent
    agent: simple_agent


⸻

### Step 4: Create an Agent

File:

products/sandbox/agents/simple_agent.py

Rules:
	•	Inherit from BaseAgent
	•	Implement run(context)
	•	Return AgentResult

⸻

### Step 5: Register the Agent & Tools

Every product must provide `products/<name>/registry.py` with a safe entrypoint:

```python
from core.utils.product_loader import ProductRegistries
from products.sandbox.agents.simple_agent import build as build_agent
from products.sandbox.tools.echo_tool import build as build_tool

def register(registries: ProductRegistries) -> None:
    registries.agent_registry.register(build_agent().name, build_agent)
    registries.tool_registry.register(build_tool().name, build_tool)
```

The product loader imports this module and calls `register(...)` with sandboxed registries + settings.

⸻

### Step 6: (Optional) Create a Tool

File:

products/sandbox/tools/echo_tool.py

Rules:
	•	Inherit from BaseTool
	•	Define input/output schema
	•	Register via tool registry

⸻

### Step 7: Define Prompts (Optional)

File:

products/sandbox/prompts/simple_agent.yaml

Prompts are resolved by agent name.

⸻

## 5. Running the Product

Run via API

POST /api/run/sandbox/hello_world


⸻

Run via UI

Open:

http://localhost:8000/sandbox


⸻

Run via CLI

python -m gateway.cli run-flow sandbox hello_world


⸻

## 6. Testing a Product

Agent Tests

pytest products/sandbox/tests/test_agents.py


⸻

Flow Tests

pytest products/sandbox/tests/test_flows.py


⸻

## 7. Product Isolation Rules

Products:
	•	Cannot import other products
	•	Cannot import core internals
	•	Cannot bypass governance
	•	Cannot write to storage directly

⸻

## 8. What Product Teams Should NOT Do

❌ Add logic to core
❌ Call tools directly
❌ Read environment variables
❌ Write files or databases
❌ Implement their own approval logic

⸻

## 9. Adding a Second Flow

Just add another YAML file in:

products/<product>/flows/

No code changes required.

⸻

## 10. Promoting a Product

When ready:
	•	Add governance policies
	•	Enable API exposure
	•	Enable UI panels
	•	Run integration tests

⸻

## 11. Product Lifecycle
	1.	Prototype (suggest_only)
	2.	Semi-autonomous (semi_auto + HITL)
	3.	Controlled autonomy (full_auto with policies)
	4.	Platform-ready

⸻

This structure allows teams to build fast, safe, and consistent agentic prototypes without touching the platform core.
