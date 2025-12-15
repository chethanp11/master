# master — Platform Overview

`master/` is a product-agnostic agentic platform that gives teams a shared runtime, governance, and UI while letting each product ship domain logic in isolation.  
The core orchestrator, memory, and governance layers are battle-tested; your product only needs to supply manifests, flows, agents, and tools. The platform handles agent/tool execution, retries, HITL approvals, auditing, and persistence for you.

## Why this platform helps
- **Single source of runtime truth:** The orchestrator, tool executor, memory router, and governance hooks are centralized, so every flow is executed consistently and auditable across products.
- **Product isolation:** Products only live under `products/<name>` and never touch core code, yet they get shared features (API, CLI, UI, tracing, HITL) for free.
- **Safety by design:** Policies, redaction, and contract envelopes force every agent/tool/run to return structured results and obey governance before emitting traces/logs.
- **Golden path ready:** Sandbox demonstrates the echo → HITL → summary flow; you can reuse the same test/style for your product, and the Streamlit UI + API expose every flow automatically.

## Advantages at a glance
1. **Audit-ready execution:** Runs/steps/approvals/trace events land in sqlite via `core/memory/sqlite_backend.py`, so any crash or restart can resume seamlessly.
2. **Plug-and-play products:** Product loader discovers `manifest.yaml`, loads `config/product.yaml`, registers agents/tools, and wires them into the API/UI without extra wiring.
3. **Unified tooling:** CLI commands (`master run`, `master resume`, `master approvals`) and the Streamlit control center (`gateway/ui/platform_app.py`) share the same orchestrator and contracts.
4. **Config-first flexibility:** YAML-based configs (`configs/*.yaml`) and secrets loader keep environment dependencies centralized; defaults, products, policies, and logging are all injectable via the loader.

## Thought process & docs map
- `docs/core_architecture.md` describes orchestrator/memory/governance/logging layers and the contracts that keep them typed.
- `docs/component_details.md` catalogs each package path plus storage, gateway, and product subsystems.
- `docs/product_howto.md` walks you through manifest/config, flows, registry hooks, and regression testing.
- `docs/overview.md` presents the high-level principles and the sandbox golden path.
- `docs/governance_and_policies.md` plus `docs/engineering_standards.md` enumerate the safety rules that every commit must respect.
- `docs/v1_acceptance_checklist.md` records the staged hardening steps (1–15) and their validation commands — use it to confirm compliance before releases.

## Getting started
1. Read the architecture & component docs to understand the runtime boundaries.
2. Follow the product how-to to scaffold `products/<your-product>/`.
3. Write flows (tool → HITL → agent), register agents/tools, and add tests.
4. Use the API/CLI/Streamlit UI to run flows, observe approvals, and resume runs.

## Docs at a glance
- `docs/core_architecture.md`: Deep dive into orchestrator, memory, governance, logging, knowledge, and contract layers.
- `docs/component_details.md`: Component catalog mapping code paths to responsibilities, storage, gateways, and tests.
- `docs/overview.md`: High-level principles and the sandbox golden-path demo with UI/API interaction notes.
- `docs/product_howto.md`: Step-by-step guide to scaffolding manifests, flows, agents/tools, registration, and regression testing.
- `docs/governance_and_policies.md`: Policy enforcement story, redaction rules, hooks, and governance artifacts.
- `docs/engineering_standards.md`: Platform laws letting you know what you must never break (env reads, persistence, envelope rules).
- `docs/v1_acceptance_checklist.md`: Staged hardening checklist (steps 1–15) with validation commands for compliance.
