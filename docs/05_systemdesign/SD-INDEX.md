# System Design Index

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning

> **Last Updated**: 2026-01-16  
> **Status**: V1 Release

---

## One-Line Rule

> **Write System Design as "implemented contracts + behaviors keyed by Tech Spec IDs", not as narrative explanation.**

This single rule is what makes diffs possible.

---

## Trade-off Position

```
                         ↑ Auditability / Diff-ability
                         │
                         │        ★ MASTER Position
                         │        (C) Spec-Driven + Traceable
                         │        "Everything maps to IDs"
                         │
                         │
 (A) Tribal Knowledge    │                          (D) Heavy Process
 "Fast, breaks later"    │                          "Slow, perfect on paper"
                         │
                         │
                         +────────────────────────────────────────────→
                                Delivery Speed / Change Velocity

                         │
                         │
                         │   (B) Narrative Docs
                         │   "Readable, but hard to diff"
                         │
                         ↓
                     Onboarding Ease / Readability
```

MASTER chooses **(C) Spec-Driven + Traceable** — everything maps to requirement IDs, enabling mechanical delta detection.

---

## Document Map

### Core Artifacts

| Document | Purpose | Diff Role |
|----------|---------|-----------|
| [SD-ARCH.md](SD-ARCH.md) | Module boundaries, dependency rules, invariants | Stable reference |
| [SD-COVERAGE.md](SD-COVERAGE.md) | **Tech Spec ID → Implementation mapping** | **Delta detection** |

### Component Docs

| Document | Scope | Tech Spec Source |
|----------|-------|------------------|
| [components/SD-ORC.md](components/SD-ORC.md) | Orchestration engine | `ORC-*` |
| [components/SD-GOV.md](components/SD-GOV.md) | Governance layer | `GOV-*` |
| [components/SD-MEM.md](components/SD-MEM.md) | Memory & persistence | `MEM-*` |
| [components/SD-INT.md](components/SD-INT.md) | Intelligence middleware | `INT-*` |
| [components/SD-TOOLS.md](components/SD-TOOLS.md) | Tool execution | `TOOL-*` |
| [components/SD-GW.md](components/SD-GW.md) | Gateway (API/CLI/UI) | `GW-*` |
| [components/SD-PROD.md](components/SD-PROD.md) | Product contract & isolation | `PROD-*` |

### Reference Docs

| Document | Purpose |
|----------|---------|
| [engineering-standards.md](engineering-standards.md) | Coding conventions, patterns |
| [product-guide.md](product-guide.md) | How to build products |

---

## Golden Path Traces

These trace files demonstrate correct system behavior for key scenarios:

| Scenario | Trace Location | Validates |
|----------|----------------|-----------|
| Simple run completion | `tests/fixtures/traces/simple_run.json` | ORC-RUN-*, ORC-STEP-* |
| HITL approval flow | `tests/fixtures/traces/hitl_approval.json` | GOV-GATE-*, ORC-PAUSE-* |
| Reasoning ladder execution | `tests/fixtures/traces/reasoning.json` | INT-LADDER-*, INT-CRITIC-* |
| Tool invocation | `tests/fixtures/traces/tool_call.json` | TOOL-*, AGT-* |

---

## The Delta Detection Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MECHANICAL PLANNING LOOP                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Parse Tech Specs → extract all requirement IDs                   │
│         │                                                            │
│         ▼                                                            │
│  2. Parse SD-COVERAGE.md → find implemented IDs                      │
│         │                                                            │
│         ▼                                                            │
│  3. DELTA = Tech Spec IDs − Implemented IDs                          │
│         │                                                            │
│         ▼                                                            │
│  4. DELTA becomes:                                                   │
│     • Implementation Plan (what to build)                            │
│     • TST Prompts (test specifications)                              │
│     • Code/Test additions                                            │
│         │                                                            │
│         ▼                                                            │
│  5. After implementation → regenerate SD-COVERAGE                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Design Pattern

> **Requirement IDs must appear in System Design.**

You can't diff Tech Specs vs System Design unless they share a common join key.

**Enforcement**:
1. Every Tech Spec requirement has an ID (e.g., `ORC-RUN-012`)
2. SD-COVERAGE.md references that same ID in a coverage table
3. Component docs link to their coverage sections

---

## Cross-References

| From | To | Join Key |
|------|----|----------|
| Developer Intent | BRD | `INT-*` → `BRD-*` |
| BRD | Tech Spec | `BRD-*` → `ORC-*`, `GOV-*`, etc. |
| Tech Spec | System Design | Requirement ID in SD-COVERAGE |
| System Design | Code | File paths, line numbers |
| Code | Traces | Trace event names |

---

## How-To Guides

| Guide | Purpose |
|-------|---------|
| [../howto/HOWTO-enhance-framework.md](../howto/HOWTO-enhance-framework.md) | End-to-end framework enhancement |
| [../howto/product-howto.md](../howto/product-howto.md) | Building products on MASTER |

---

## Navigation

- **Start here** → [SD-ARCH.md](SD-ARCH.md) for architecture overview
- **Check coverage** → [SD-COVERAGE.md](SD-COVERAGE.md) for implementation status
- **Deep dive** → `components/SD-*.md` for specific components
