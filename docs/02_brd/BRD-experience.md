# BRD: Developer & User Experience

> **Document ID**: BRD-EXP  
> **Version**: V1.2  
> **Last Updated**: 2026-01-19  
> **Status**: V1 Release  

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-12 | Initial release |
| 1.1 | 2026-01-13 | Added §3.7 Product Factory Model, updated Cross-Cutting Requirements |
| V1.2 | 2026-01-19 | Standardized requirement tables, removed TSD-level detail, and aligned intent traceability |

---

## 1. Business Context

### Problem Statement
Platform adoption depends on developer and user experience:
- Developers need multiple ways to interact (API, CLI, UI)
- Building new products should be fast, not weeks of setup
- Products must be isolated to prevent cross-contamination
- Error messages must guide users toward resolution
- Onboarding new team members is slow without clear patterns

### Opportunity
An experience layer that provides:
- Multiple interaction modalities for different personas
- Rapid product development with conventions over configuration
- Strong isolation guarantees for multi-product deployments
- Clear, actionable error messages and documentation
- Self-documenting patterns that reduce onboarding time

### Business Value
- **Developer productivity**: Ship products in days, not weeks
- **User satisfaction**: Right interface for each user type
- **Operational safety**: Product isolation prevents cascading failures
- **Reduced support burden**: Clear errors reduce support tickets

---

## 2. Stakeholders

| Stakeholder | Role | Primary Concern |
|-------------|------|-----------------|
| **API Developer** | Integrates via HTTP API | Clear contracts, predictable responses |
| **CLI Operator** | Runs workflows from terminal | Scriptability, JSON output |
| **UI End User** | Non-technical interaction | Intuitive interface, status visibility |
| **Product Builder** | Creates new products | Fast scaffolding, clear patterns |
| **Platform Admin** | Manages multi-product deployment | Isolation, discovery |

---

## 3. Business Requirements

> **Source**: [intent-experience.md](../01_vision_and_intent/intent-experience.md)

### 3.1 API Experience

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-001** | Platform must be accessible via HTTP REST API | Derived from: INT-EXP-001 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-002** | API responses must follow consistent envelope format | Derived from: INT-EXP-002 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-003** | API errors must include machine-readable codes | Derived from: INT-EXP-003 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-004** | API errors must include human-readable messages | Derived from: INT-EXP-004 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-005** | API must support listing products and flows | Derived from: INT-EXP-005 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-006** | API must support starting, monitoring, and resuming runs | Derived from: INT-EXP-006 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-007** | API must enforce payload size limits | Derived from: INT-EXP-007 | P1 | 2026-01-12 | V1.1 | — |

### 3.2 CLI Experience

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-010** | Platform must be accessible via command-line interface | Derived from: INT-EXP-010 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-011** | CLI output must be valid JSON for scripting | Derived from: INT-EXP-011 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-012** | CLI must provide commands for all core operations | Derived from: INT-EXP-012 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-013** | CLI errors must exit with appropriate status codes | Derived from: INT-EXP-013 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-014** | CLI must provide helpful guidance on errors | Derived from: INT-EXP-014 | P1 | 2026-01-12 | V1.1 | — |

### 3.3 UI Experience

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-020** | Platform must be accessible via web interface | Derived from: INT-EXP-020 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-021** | UI must display available products and flows | Derived from: INT-EXP-021 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-022** | UI must allow running flows with input | Derived from: INT-EXP-022 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-023** | UI must display run status and history | Derived from: INT-EXP-023 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-024** | UI must support approval workflows | Derived from: INT-EXP-024 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-025** | UI must support user input collection | Derived from: INT-EXP-025 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-026** | UI must display execution timeline with events | Derived from: INT-EXP-026 | P1 | 2026-01-12 | V1.1 | — |

### 3.4 Product System

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-030** | New products must be creatable from standard structure | Derived from: INT-EXP-030 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-031** | Products must declare capabilities via manifest | Derived from: INT-EXP-031 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-032** | Products must be auto-discovered without restart | Derived from: INT-EXP-032 | P1 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-033** | Products must be independently enableable/disableable | Derived from: INT-EXP-033 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-034** | Product load errors must not crash the platform | Derived from: INT-EXP-034 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-035** | Products must be shippable in < 1 day | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-036** | Products must focus on domain logic only, no infrastructure burden | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-037** | Products must be evolvable via intent updates | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |

### 3.5 Product Isolation

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-040** | Products must not access other products' agents or tools | Derived from: INT-EXP-040 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-041** | Products must not access other products' data | Derived from: INT-EXP-041 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-042** | Product failures must not affect other products | Derived from: INT-EXP-042 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-043** | Products must have isolated observability directories | Derived from: INT-EXP-043 | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-044** | Products MUST NOT modify core framework | Derived from: INT-EXP-044 | P0 | 2026-01-13 | V1.1 | — |

**Constraints (Non-Negotiable from Intent)**:
| Constraint ID | Constraint Statement | Violation Example | Derived from (Intent ID) |
|---------------|----------------------|-------------------|--------------------------|
| **BRD-EXP-CON-001** | Products MUST NOT modify core | Product patches orchestrator | INT-EXP-044 |
| **BRD-EXP-CON-002** | Products MUST be isolated from other products' resources | Product A reads Product B's data | INT-EXP-045 |
| **BRD-EXP-CON-003** | Products MUST be fault-isolated | Product A crash takes down Product B | INT-EXP-046 |

### 3.6 Error Experience

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-050** | Error messages must identify the problem clearly | Derived from: Intent ID missing | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-051** | Error messages must suggest remediation steps | Derived from: Intent ID missing | P1 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-052** | Validation errors must identify the specific field | Derived from: Intent ID missing | P0 | 2026-01-12 | V1.1 | — |
| **BRD-EXP-053** | Not-found errors must suggest available alternatives | Derived from: Intent ID missing | P1 | 2026-01-12 | V1.1 | — |

### 3.7 Product Factory Model

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-060** | Product creation MUST be primarily an intent-driven activity | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-061** | Code MUST be treated as a generated artifact, not the source of truth | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-062** | Products MUST define what; the framework MUST define how | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-063** | Framework MUST provide 90% of functionality; products MAY add 10% | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-064** | Products MUST NOT re-implement framework services | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |

---

---

## 7. Cross-Cutting Requirements

### 7.1 Intent Ownership

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-LIFE-001** | Framework Developer MUST own Framework Developer Intent | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-LIFE-002** | Product Developer MUST own Product Developer Intent | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-LIFE-003** | End Users MUST NOT modify intent directly | Derived from: Intent ID missing | P0 | 2026-01-13 | V1.1 | — |

### 7.2 Design-Time Intelligence

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-FAC-001** | AI MUST be able to derive BRDs from intent | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-FAC-002** | AI MUST be able to derive specs from BRDs | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-FAC-003** | AI MUST be able to generate code from specs | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-FAC-004** | AI MUST be able to generate system design from code | Derived from: Intent ID missing | P2 | 2026-01-13 | V1.1 | — |

### 7.3 Success and Failure Smells

| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| **BRD-EXP-FAC-010** | Success/failure smells must be defined qualitatively | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-FAC-011** | Smells must be checked during architecture reviews | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |
| **BRD-EXP-FAC-012** | Smell detection must trigger design review | Derived from: Intent ID missing | P1 | 2026-01-13 | V1.1 | — |

---

## 8. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| HTTP API framework | External | Enables API delivery |
| UI framework | External | Enables web interface delivery |
| Product Catalog | Internal | Discovery service |

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API breaking changes | Integration failures | Versioning, deprecation policy |
| UI complexity | User confusion | User testing, progressive disclosure |
| Isolation bypass | Security breach | Strong boundaries, testing |
| Slow product creation | Developer frustration | Templates, scaffolding tools |

---

## 10. Appendix: Technical Details (Removed from BRD)

### Product Creation Checklist (Technical Reference)
```
products/<name>/
├── manifest.yaml     ← Required: Product metadata
├── registry.py       ← Required: Agent/tool registration
├── __init__.py       ← Required: Python package
├── config/           ← Optional: Product-specific config
├── agents/           ← Optional: Custom agents
├── tools/            ← Optional: Custom tools
└── flows/            ← Optional: Flow definitions (or in manifest)
```

Minimum manifest.yaml:
```yaml
name: my_product
display_name: My Product
version: "1.0.0"
description: What this product does
flows:
  - name: main
    display_name: Main Flow
    entry_point: flows/main.yaml
```

---

## Related Documents

- [Vision.md](../01_vision_and_intent/Vision.md) — Platform vision and principles
- [intent-experience.md](../01_vision_and_intent/intent-experience.md) — Source intent
- [BRD-operations.md](BRD-operations.md) — Observability requirements
