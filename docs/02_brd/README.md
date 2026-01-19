# Business Requirements Documents

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  
> **Version**: V1.2  

> **Last Updated**: 2026-01-19  
> **Status**: V1 Release  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |
| V1.2 | 2026-01-19 | Updated BRD table schema guidance and removed user-story-first guidance |

## Overview

This folder contains Business Requirement Documents (BRDs) that define **what** the MASTER platform must achieve from a business perspective. BRDs are the source of truth from which [Technical Specifications](../03_technical_specifications/) are derived.

### Document Hierarchy

```
docs/01_vision_and_intent/   ← Strategic direction
    ↓
docs/02_brd/                 ← Business requirements (this folder)
    ↓
docs/03_technical_specifications/ ← Technical specifications
    ↓
core/, gateway/, products/   ← Implementation
```

---

## Documents

| Document | Theme | Description |
|----------|-------|-------------|
| [Vision.md](../01_vision_and_intent/Vision.md) | Strategy | Mission, audience, value propositions, roadmap |
| [BRD-automation.md](BRD-automation.md) | Intelligent Automation | Agents, tools, reasoning, evidence |
| [BRD-governance.md](BRD-governance.md) | Governance & Compliance | Approval, security, audit, budget |
| [BRD-experience.md](BRD-experience.md) | Developer & User Experience | API, CLI, UI, products |
| [BRD-operations.md](BRD-operations.md) | Operational Excellence | Persistence, observability, quality |

---

## Requirement ID Scheme

```
BRD-<THEME>-<NUMBER>
```

| Prefix | Theme | Techspec Coverage |
|--------|-------|-------------------|
| `BRD-AUTO` | Automation | AGT-*, TOOL-*, INT-*, ORC-RUN-*, ORC-STEP-* |
| `BRD-GOV` | Governance | GOV-*, ORC-PAUSE-*, ORC-RESUME-*, MEM-TRACE-* |
| `BRD-EXP` | Experience | GW-*, PROD-* |
| `BRD-OPS` | Operations | MEM-*, OBS-*, ACC-* |

---

## Priority Definitions

| Priority | Meaning | Timeline |
|----------|---------|----------|
| **P0** | Must-have | V1 release blocker |
| **P1** | Should-have | V1 target, can defer to V1.1 |
| **P2** | Nice-to-have | V1.1 or V2 |

---

## Where to Add Requirements

Use this routing guide to determine which BRD to update:

### BRD-automation.md
- New agent types or capabilities
- Tool integrations
- Reasoning/intelligence features
- Evidence and explainability
- Multi-step task orchestration

### BRD-governance.md
- Approval workflows
- Security & PII handling
- Policy rules (allowed/blocked)
- Budget and cost controls
- Audit requirements

### BRD-experience.md
- New products
- API/CLI/UI features
- Developer onboarding
- Error messaging
- Multi-tenancy & isolation

### BRD-operations.md
- Observability & dashboards
- Persistence & recovery
- Performance & SLAs
- Testing & quality
- Monitoring & alerting

---

## Common Ask Routing

| User Ask | Update In | Techspec Impact |
|----------|-----------|-----------------|
| Add a new product | BRD-experience.md | PROD-* |
| Observability dashboard | BRD-operations.md | OBS-*, MEM-TRACE-* |
| New approval workflow | BRD-governance.md | GOV-*, ORC-PAUSE-* |
| New agent capability | BRD-automation.md | AGT-*, INT-* |
| New tool integration | BRD-automation.md | TOOL-* |
| API rate limiting | BRD-experience.md | GW-API-* |
| PII redaction rules | BRD-governance.md | GOV-SEC-* |
| CLI new command | BRD-experience.md | GW-CLI-* |
| Run history retention | BRD-operations.md | MEM-* |
| Budget/cost controls | BRD-governance.md | GOV-BUD-* |
| Test coverage target | BRD-operations.md | ACC-* |
| UI new page | BRD-experience.md | GW-UI-* |
| Reasoning improvements | BRD-automation.md | INT-RL-*, INT-CRIT-* |
| Multi-tenancy | BRD-experience.md | PROD-ISO-* |
| Platform vision change | Vision.md | — |

---

## How to Add a Requirement

1. **Identify the theme** using the routing guide above
2. **Open the appropriate BRD** document
3. **Add a row** to the Business Requirements table:

```markdown
| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-<THEME>-NNN | <Requirement statement> | INT-<AREA>-NNN | P0/P1/P2 | YYYY-MM-DD | V1.1 | — |
```

4. **Update techspec mapping** once technical requirements are defined

---

## Derivation Process

```
1. Business need identified
       ↓
2. Add requirement to BRD with priority
       ↓
3. Derive technical requirements in techspec
       ↓
4. Update BRD techspec mapping table
       ↓
5. Implement and test
```

---

## Cross-References

- **Technical Specifications**: [docs/techspec/](../techspec/)
- **System Design**: [docs/systemdesign/](../systemdesign/)
- **Implementation Gaps**: [docs/implementationplan/implementation_gaps.md](../implementationplan/implementation_gaps.md)
