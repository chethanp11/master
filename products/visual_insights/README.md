# Visual Insights v1

Visual Insights is an agentic dashboard for CSV and PDF data.
It supports three engagement modes—explore, monitor, explain—and can render five default chart types.
The product focuses on traceability: every operation emits traces, citations, and PII scrubbing metadata.
PDF export is available via the orchestrator’s render/export primitives.

Structure:
- `configs/` holds Visual Insights-specific settings.
- `contracts/` defines shared dataclasses for IO, modes, refs, slices, etc.
- `flows/` wires the V1 flow + modular steps.
- `agents/` and `tools/` provide domain logic (planning, evidence, cards).
- `tests/` contains unit/integration guards.
- `docs/` sketches architecture, requirements, API surface, and runbook notes.
