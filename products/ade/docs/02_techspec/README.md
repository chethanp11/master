# ADE Technical Specification

> **Product**: Analytical Decision Engine (ADE)  
> **Version**: 1.0.0  
> **Last Updated**: 2026-01-12  
> **Total Requirements**: ~120

---

## Document Index

| Document | Prefix | Description | Req Count |
|----------|--------|-------------|-----------|
| [FLOW-flows.md](FLOW-flows.md) | FLOW-* | Flow execution requirements | ~25 |
| [AGENT-agents.md](AGENT-agents.md) | AGENT-* | Agent behavior requirements | ~20 |
| [TOOL-tools.md](TOOL-tools.md) | TOOL-* | Tool implementation requirements | ~35 |
| [SCHEMA-schemas.md](SCHEMA-schemas.md) | SCHEMA-* | Data schema requirements | ~20 |
| [IO-inputs-outputs.md](IO-inputs-outputs.md) | IO-* | Input/output requirements | ~20 |

---

## Requirement ID Convention

```
<PREFIX>-<CATEGORY>-<NUMBER>
```

| Prefix | Domain |
|--------|--------|
| FLOW | Flow execution |
| AGENT | Agent behavior |
| TOOL | Tool implementation |
| SCHEMA | Data schemas |
| IO | Inputs and outputs |

---

## Quick Reference

### Critical Requirements

| ID | Description | Priority |
|----|-------------|----------|
| FLOW-EXEC-001 | Flows must execute deterministically | P0 |
| TOOL-PURE-001 | Tools must not call LLMs directly | P0 |
| SCHEMA-VALID-001 | All outputs must pass Pydantic validation | P0 |
| IO-EVID-001 | All claims must have evidence_refs | P0 |

### Traceability

| System Design | Techspec |
|---------------|----------|
| [architecture.md](../04_systemdesign/architecture.md) | FLOW-*, AGENT-*, TOOL-* |
| [flows.md](../04_systemdesign/flows.md) | FLOW-* |
| [agents-and-tools.md](../04_systemdesign/agents-and-tools.md) | AGENT-*, TOOL-* |
| [schemas.md](../04_systemdesign/schemas.md) | SCHEMA-* |
| [inputs-and-outputs.md](../04_systemdesign/inputs-and-outputs.md) | IO-* |
