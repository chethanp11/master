# MASTER — Platform Overview

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning

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
- `docs/01_vision_and_intent/` captures vision plus platform intent requirements.
- `docs/02_brd/` maps business requirements and intent coverage.
- `docs/03_techspec/` defines technical specs and BRD-to-techspec coverage.
- `docs/04_implementation_plan/` tracks implementation plan, gaps, and outcomes.
- `docs/05_systemdesign/` provides architecture and implementation coverage references.
- `docs/howto/product-howto.md` explains how to build and ship products on MASTER.

## Getting started
1. Read the architecture & component docs to understand the runtime boundaries.
2. Follow the product how-to to scaffold `products/<your-product>/`.
3. Write flows (tool → HITL → agent), register agents/tools, and add tests.
4. Use the API/CLI/Streamlit UI to run flows, observe approvals, and resume runs.

## Docs at a glance
- `docs/01_vision_and_intent/Vision.md`: Platform vision and non-negotiable principles.
- `docs/02_brd/README.md`: BRD structure plus links to automation/experience/governance/operations BRDs.
- `docs/03_techspec/README.md`: Technical spec index (`ORC`, `GOV`, `AGT`, `MEM`, `GW`, `PROD`, `INT`, `ACC`) and coverage.
- `docs/03_techspec/TS-COVERAGE.md`: BRD to TechSpec coverage mapping.
- `docs/05_systemdesign/SD-ARCH.md`: Stable architecture boundaries, dependency rules, and invariants.
- `docs/05_systemdesign/SD-COVERAGE.md`: TechSpec ID to implementation mapping for delta detection.
- `docs/howto/product-howto.md`: Product authoring guide (manifest, flows, registry, tests).
