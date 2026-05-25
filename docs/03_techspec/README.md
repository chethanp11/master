# Technical Specifications Index

> **Document ID**: TS-README  
> **Version**: V1.2  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-13  

## Purpose

This directory contains the formal technical requirements for the MASTER agentic platform.
Requirements use RFC 2119 language (MUST, SHALL, SHOULD, MAY) to indicate obligation levels.

Each specification document includes:
- **Requirement IDs** for traceability (e.g., `ORC-001`, `GOV-HOOK-010`)
- **Canonical TSD tables** with BRD mappings
- **RFC 2119 language** for obligation levels

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |

## Specification Documents

| Document | Prefix | Description | Requirements |
|----------|--------|-------------|--------------|
| [ORC-orchestration.md](ORC-orchestration.md) | `ORC-*` | Orchestration engine, run lifecycle, step execution | ~60 |
| [AGT-agents-tools.md](AGT-agents-tools.md) | `AGT-*`, `TOOL-*` | Agent/tool contracts, registries, decorators | ~85 |
| [GOV-governance.md](GOV-governance.md) | `GOV-*` | Governance hooks, policies, security, gates | ~120 |
| [MEM-memory.md](MEM-memory.md) | `MEM-*` | Memory backend, persistence, observability | ~45 |
| [INT-intelligence.md](INT-intelligence.md) | `INT-*` | Advisory agents, reasoning ladder, critic | ~105 |
| [GW-gateway.md](GW-gateway.md) | `GW-*` | HTTP API, CLI, Streamlit UI | ~130 |
| [PROD-products.md](PROD-products.md) | `PROD-*` | Product structure, isolation, auto-discovery | ~55 |
| [ACC-acceptance.md](ACC-acceptance.md) | `ACC-*` | Test categories, coverage targets, validation | ~30 |

**Total Requirements**: ~630

---

## Requirement ID Scheme

Each requirement has a unique identifier following this pattern:

`<PREFIX>-<CATEGORY>-<NUMBER>`

| Prefix | Domain |
|--------|--------|
| `ORC` | Orchestration engine |
| `AGT` | Agent contracts |
| `TOOL` | Tool contracts |
| `REG` | Registry system |
| `GOV` | Governance layer |
| `MEM` | Memory/persistence |
| `OBS` | Observability |
| `INT` | Intelligence layer |
| `GW` | Gateway (API/CLI/UI) |
| `PROD` | Product system |
| `ACC` | Acceptance criteria |

---

## RFC 2119 Keywords

These specifications use RFC 2119 terminology:

| Keyword | Meaning |
|---------|---------|
| **MUST** / **SHALL** | Absolute requirement; non-compliance is a defect |
| **MUST NOT** / **SHALL NOT** | Absolute prohibition |
| **SHOULD** | Recommended; deviation requires justification |
| **SHOULD NOT** | Discouraged; usage requires justification |
| **MAY** | Optional; implementation choice |

---

## Requirements Table Format

All technical specifications use the canonical TSD table structure:

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| ORC-RUN-001 | The orchestrator MUST generate a unique run ID | MUST | BRD-OPS-001 | 1.1 | 13 Jan 2026 | — |

---

## Architecture Invariants

Cross-cutting rules that span multiple specifications:

| ID | Invariant |
|----|-----------|
| `INV-001` | No circular imports between core modules |
| `INV-002` | Products MUST NOT import from other products |
| `INV-003` | Registries store factories, not instances |
| `INV-004` | All errors wrapped in result envelopes |
| `INV-005` | Governance hooks MUST NOT persist or log |
| `INV-006` | Context packs MUST be deterministic |
| `INV-007` | All trace events include run_id and timestamp |

---

## Validation

Requirements are validated through:

1. **Unit Tests** — Individual component behavior
2. **Integration Tests** — Cross-module interactions
3. **Architecture Tests** — Structural invariants
4. **Acceptance Tests** — End-to-end scenarios

Current coverage: **348+ tests passing**

---

## Change History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial specification extraction from implementation |

---

## References

- [../05_systemdesign/SD-ARCH.md](../05_systemdesign/SD-ARCH.md) — High-level architecture
- [../05_systemdesign/SD-INDEX.md](../05_systemdesign/SD-INDEX.md) — System design navigation and component map
- [../howto/HOWTO-enhance-framework.md](../howto/HOWTO-enhance-framework.md) — Development workflow and implementation loop
- [../04_implementation_plan/imp_gaps.md](../04_implementation_plan/imp_gaps.md) — Gap analysis
