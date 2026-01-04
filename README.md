# master — Platform Overview

`master/` is a product-agnostic platform that provides a shared orchestrator, governance, memory, and UI while keeping product logic isolated under `products/`.  
Products supply manifests, flows, agents, and tools; the platform executes flows, applies governance, handles HITL/user-input pauses, and persists run state.

## Why this platform helps
- **Single runtime control plane:** Orchestrator, tool executor, memory router, and governance hooks are centralized so flows execute consistently across products.
- **Product isolation:** Products only live under `products/<name>` and never touch core code, yet they get shared features (API, CLI, UI, tracing, HITL) for free.
- **Safety by design:** Policies, redaction, and contract envelopes enforce structured results and governance checks before tool/model execution and trace emission.
- **Golden path ready:** Hello World demonstrates the echo → HITL → summary flow; you can reuse the same test/style for your product, and the Streamlit UI + API expose every flow automatically.

## Advantages at a glance
1. **Audit-ready execution:** Runs/steps/approvals/trace events persist via `core/memory/sqlite_backend.py` and file-backed observability.
2. **Plug-and-play products:** Loader discovers `manifest.yaml`, loads `config/product.yaml`, registers agents/tools, and wires them into API/UI.
3. **Unified tooling:** CLI commands and the Streamlit control center share the same orchestrator and contracts.
4. **Config-first control:** YAML configs and the loader centralize app/policy/logging settings and secrets.

## Thought process & docs map
- `docs/core_architecture.md` describes orchestrator/memory/governance/logging layers and the contracts that keep them typed.
- `docs/component_details.md` catalogs each package path plus storage, gateway, and product subsystems.
- `docs/product_howto.md` walks you through manifest/config, flows, registry hooks, and regression testing.
- `docs/overview.md` presents the high-level principles and the hello_world golden path.
- `docs/governance_and_policies.md` plus `docs/engineering_standards.md` enumerate the safety rules that every commit must respect.

## Getting started
1. Read the architecture & component docs to understand the runtime boundaries.
2. Follow the product how-to to scaffold `products/<your-product>/`.
3. Write flows (tool → HITL → agent), register agents/tools, and add tests.
4. Use the API/CLI/Streamlit UI to run flows, observe approvals, and resume runs.

## Docs at a glance
- `docs/core_architecture.md`: Deep dive into orchestrator, memory, governance, observability, and contract layers.
- `docs/component_details.md`: Component catalog mapping code paths to responsibilities, storage, gateways, and tests.
- `docs/overview.md`: High-level principles and the hello_world golden-path demo with UI/API interaction notes.
- `docs/product_howto.md`: Step-by-step guide to scaffolding manifests, flows, agents/tools, registration, and regression testing.
- `docs/governance_and_policies.md`: Policy enforcement story, redaction rules, hooks, and governance artifacts.
- `docs/engineering_standards.md`: Platform laws letting you know what you must never break (env reads, persistence, envelope rules).
