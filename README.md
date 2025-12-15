# master — Platform Overview

This README distills the platform knowledge spread across `docs/` into a single reference. Use the linked sections for deeper dives.

## Core Architecture
- `docs/core_architecture.md` explains the runtime layering: orchestrator, agents, tools, memory, knowledge, governance, logging, and the contracts/envelopes that keep every boundary typed.
- `docs/component_details.md` catalogs each subsystem, storage path, and durability guarantees (e.g., `core/memory/router`, `storage/memory`, `gateway/ui/platform_app.py`).

## Product Development
- `docs/product_howto.md` is the definitive HOWTO for building a product pack: manifest/config layout, registry hook, flows/agents/tools, testing, and API exposure.
- `docs/overview.md` highlights the high-level principles (thin products, interface contracts) and the sandbox golden path (`products/sandbox` + Streamlit UI).

## Governance & Standards
- `docs/governance_and_policies.md` documents the policy enforcement model, redaction rules, and governance hooks used by `core/tools/executor.py`, `core/governance/*`, and the gateway/CLI.
- `docs/engineering_standards.md` lists the non-negotiables (boundary rules, result envelopes, tracing) that all engineers must follow.

## Acceptance Checklist
- `docs/v1_acceptance_checklist.md` tracks the staged hardening steps (1–15) and their validation commands; refer here before claiming completion.

## How to Use
1. Read `core_architecture.md` + `component_details.md` to understand the runtime boundaries.
2. Follow `product_howto.md` when adding or updating a product.
3. Consult `governance_and_policies.md` / `engineering_standards.md` before touching tools or persistence.
4. Run through `v1_acceptance_checklist.md` to validate compliance for release.
