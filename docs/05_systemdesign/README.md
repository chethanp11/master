# System Design Documents

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  
> **Version**: 1.1  

> **Last Updated**: 2026-01-12  
> **Status**: V1 Release  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |

## Overview

This folder contains **implementation reference documentation** that describes how the MASTER platform works. These documents are the "HOW" layer — written after implementation to serve as reference for engineers working with the codebase.

### Document Hierarchy

```
docs/
├── 01_vision_and_intent/       ← WHY: Vision and intent
├── 02_brd/                     ← WHY: Business requirements
├── 03_techspec/                ← WHAT: Technical requirements
├── 04_implementation_plan/     ← HOW: Implementation planning
└── 05_systemdesign/           ← HOW: Implementation reference (this folder)
    ├── README.md               ← Navigation (you are here)
    ├── SD-ARCH.md              ← Architecture boundaries
    ├── SD-COVERAGE.md          ← Requirement coverage matrix
    ├── SD-INDEX.md             ← System design index
    └── components/
        ├── SD-COMP-LIST.md
        ├── SD-GOV.md
        ├── SD-GW.md
        ├── SD-INT.md
        ├── SD-MEM.md
        ├── SD-ORC.md
        ├── SD-PROD.md
        └── SD-TOOLS.md
```

---

## Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| [SD-ARCH.md](SD-ARCH.md) | High-level architecture, boundaries, and invariants | All engineers |
| [SD-COVERAGE.md](SD-COVERAGE.md) | Tech Spec ID → implementation mapping | Core contributors |
| [SD-INDEX.md](SD-INDEX.md) | Navigation, document map, and delta-detection loop | All engineers |
| [components/SD-COMP-LIST.md](components/SD-COMP-LIST.md) | Component inventory and implementation reference | Core contributors |

---

## Reading Order

### For New Engineers
1. [SD-ARCH.md](SD-ARCH.md) — Understand the big picture
2. [SD-INDEX.md](SD-INDEX.md) — Review the doc map and delta-detection loop
3. [components/SD-COMP-LIST.md](components/SD-COMP-LIST.md) — Review component inventory

### For Product Builders
1. `docs/howto/product-howto.md` — Step-by-step product creation
2. [components/SD-PROD.md](components/SD-PROD.md) — Product contract and isolation
3. [components/SD-GOV.md](components/SD-GOV.md) — Governance constraints

### For Core Contributors
1. [SD-ARCH.md](SD-ARCH.md) — System design principles
2. [components/SD-COMP-LIST.md](components/SD-COMP-LIST.md) — Module deep-dives
3. [components/SD-GOV.md](components/SD-GOV.md) — Governance internals

---

## Cross-References

| Topic | System Design | BRD | Techspec |
|-------|---------------|-----|----------|
| Orchestration | SD-ARCH.md / components/SD-ORC.md | [BRD-automation.md](../02_brd/BRD-automation.md) | [ORC-orchestration.md](../03_techspec/ORC-orchestration.md) |
| Agents/Tools | components/SD-TOOLS.md | [BRD-automation.md](../02_brd/BRD-automation.md) | [AGT-agents-tools.md](../03_techspec/AGT-agents-tools.md) |
| Governance | components/SD-GOV.md | [BRD-governance.md](../02_brd/BRD-governance.md) | [GOV-governance.md](../03_techspec/GOV-governance.md) |
| Products | components/SD-PROD.md | [BRD-experience.md](../02_brd/BRD-experience.md) | [PROD-products.md](../03_techspec/PROD-products.md) |
| Gateway | components/SD-GW.md | [BRD-experience.md](../02_brd/BRD-experience.md) | [GW-gateway.md](../03_techspec/GW-gateway.md) |
| Memory | components/SD-MEM.md | [BRD-operations.md](../02_brd/BRD-operations.md) | [MEM-memory.md](../03_techspec/MEM-memory.md) |

---

## Document Maintenance

These documents should be updated when:
- Implementation changes significantly
- New modules are added to core
- Architectural decisions are made
- Engineers frequently ask questions not covered

Keep content factual and descriptive — "what is" rather than "what should be". Requirements belong in BRD/techspec.
