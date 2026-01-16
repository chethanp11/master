# System Design Documents

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning

> **Last Updated**: 2026-01-12  
> **Status**: V1 Release

---

## Overview

This folder contains **implementation reference documentation** that describes how the MASTER platform works. These documents are the "HOW" layer — written after implementation to serve as reference for engineers working with the codebase.

### Document Hierarchy

```
docs/Framework_Dev_Steps/
├── 01_vision_and_intent/       ← WHY: Vision and intent
├── 02_business_requirements/   ← WHY: Business requirements
├── 03_technical_specifications/← WHAT: Technical requirements  
├── 04_implementation_plan/     ← HOW: Implementation planning
└── 05_system_design/           ← HOW: Implementation reference (this folder)
    ├── README.md               ← Navigation (you are here)
    ├── architecture-overview.md
    ├── component-reference.md
    ├── flows-and-agents-reference.md
    ├── product-guide.md
    ├── governance-reference.md
    └── engineering-standards.md
```

---

## Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| [architecture-overview.md](architecture-overview.md) | High-level architecture, principles, layer diagram, execution flow | All engineers |
| [component-reference.md](component-reference.md) | Deep-dive into each core module | Core contributors |
| [flows-and-agents-reference.md](flows-and-agents-reference.md) | Flow definitions, step types, agent/tool contracts | Product builders |
| [product-guide.md](product-guide.md) | **Start here** to build a new product | Product builders |
| [governance-reference.md](governance-reference.md) | Governance hooks, policies, security, budgets | All engineers |
| [engineering-standards.md](engineering-standards.md) | Coding conventions, patterns, testing | All engineers |

---

## Reading Order

### For New Engineers
1. [architecture-overview.md](architecture-overview.md) — Understand the big picture
2. [product-guide.md](product-guide.md) — Learn how to build products
3. [engineering-standards.md](engineering-standards.md) — Follow conventions

### For Product Builders
1. [product-guide.md](product-guide.md) — Step-by-step product creation
2. [flows-and-agents-reference.md](flows-and-agents-reference.md) — Flow/agent/tool details
3. [governance-reference.md](governance-reference.md) — Understand governance constraints

### For Core Contributors
1. [architecture-overview.md](architecture-overview.md) — System design principles
2. [component-reference.md](component-reference.md) — Module deep-dives
3. [governance-reference.md](governance-reference.md) — Governance internals

---

## Cross-References

| Topic | System Design | BRD | Techspec |
|-------|---------------|-----|----------|
| Orchestration | architecture-overview.md | [BRD-automation.md](../02_business_requirements/BRD-automation.md) | [ORC-orchestration.md](../03_technical_specifications/ORC-orchestration.md) |
| Agents/Tools | flows-and-agents-reference.md | [BRD-automation.md](../02_business_requirements/BRD-automation.md) | [AGT-agents-tools.md](../03_technical_specifications/AGT-agents-tools.md) |
| Governance | governance-reference.md | [BRD-governance.md](../02_business_requirements/BRD-governance.md) | [GOV-governance.md](../03_technical_specifications/GOV-governance.md) |
| Products | product-guide.md | [BRD-experience.md](../02_business_requirements/BRD-experience.md) | [PROD-products.md](../03_technical_specifications/PROD-products.md) |
| Gateway | architecture-overview.md | [BRD-experience.md](../02_business_requirements/BRD-experience.md) | [GW-gateway.md](../03_technical_specifications/GW-gateway.md) |
| Memory | component-reference.md | [BRD-operations.md](../02_business_requirements/BRD-operations.md) | [MEM-memory.md](../03_technical_specifications/MEM-memory.md) |

---

## Document Maintenance

These documents should be updated when:
- Implementation changes significantly
- New modules are added to core
- Architectural decisions are made
- Engineers frequently ask questions not covered

Keep content factual and descriptive — "what is" rather than "what should be". Requirements belong in BRD/techspec.
