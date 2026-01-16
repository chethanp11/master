# BRD: Developer & User Experience

> **Document ID**: BRD-EXP  
> **Version**: 1.1  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-12 | Initial release |
| 1.1 | 2026-01-13 | Added §3.7 Product Factory Model, updated Cross-Cutting Requirements |

---

## Governing Architecture Invariants

The following architecture invariants from [Developer Intent](../00_developer_intent/intent.md) govern this BRD:

| INV | Invariant | Implication for Experience |
|-----|-----------|---------------------------|
| **INV-6** | Platform Laws Are Non-Negotiable | Products are isolated; cannot access other products' resources |
| **INV-8** | Design-Time Intelligence Preferred | Product creation uses AI to derive artifacts from intent |
| **INV-10** | Minimize Product Complexity | Products should be thin, declarative, domain-focused |

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

> **Source**: [INT-EXP](../00_developer_intent/intent.md#3-developer--user-experience-int-exp)

### 3.1 API Experience

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-EXP-001** | Platform must be accessible via HTTP REST API | P0 | INT-EXP-001 | 2026-01-12 |
| **BRD-EXP-002** | API responses must follow consistent envelope format | P0 | INT-EXP-002 | 2026-01-12 |
| **BRD-EXP-003** | API errors must include machine-readable codes | P0 | INT-EXP-003 | 2026-01-12 |
| **BRD-EXP-004** | API errors must include human-readable messages | P0 | INT-EXP-004 | 2026-01-12 |
| **BRD-EXP-005** | API must support listing products and flows | P0 | INT-EXP-005 | 2026-01-12 |
| **BRD-EXP-006** | API must support starting, monitoring, and resuming runs | P0 | INT-EXP-006 | 2026-01-12 |
| **BRD-EXP-007** | API must enforce payload size limits | P1 | INT-EXP-007 | 2026-01-12 |

### 3.2 CLI Experience

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-EXP-010** | Platform must be accessible via command-line interface | P0 | INT-EXP-010 | 2026-01-12 |
| **BRD-EXP-011** | CLI output must be valid JSON for scripting | P0 | INT-EXP-011 | 2026-01-12 |
| **BRD-EXP-012** | CLI must provide commands for all core operations | P0 | INT-EXP-012 | 2026-01-12 |
| **BRD-EXP-013** | CLI errors must exit with appropriate status codes | P0 | INT-EXP-013 | 2026-01-12 |
| **BRD-EXP-014** | CLI must provide helpful guidance on errors | P1 | INT-EXP-014 | 2026-01-12 |

### 3.3 UI Experience

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-EXP-020** | Platform must be accessible via web interface | P0 | INT-EXP-020 | 2026-01-12 |
| **BRD-EXP-021** | UI must display available products and flows | P0 | INT-EXP-021 | 2026-01-12 |
| **BRD-EXP-022** | UI must allow running flows with input | P0 | INT-EXP-022 | 2026-01-12 |
| **BRD-EXP-023** | UI must display run status and history | P0 | INT-EXP-023 | 2026-01-12 |
| **BRD-EXP-024** | UI must support approval workflows | P0 | INT-EXP-024 | 2026-01-12 |
| **BRD-EXP-025** | UI must support user input collection | P0 | INT-EXP-025 | 2026-01-12 |
| **BRD-EXP-026** | UI must display execution timeline with events | P1 | INT-EXP-026 | 2026-01-12 |

### 3.4 Product System

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-EXP-030** | New products must be creatable from standard structure | P0 | INT-EXP-030 | 1.0 | 2026-01-12 |
| **BRD-EXP-031** | Products must declare capabilities via manifest | P0 | INT-EXP-031 | 1.0 | 2026-01-12 |
| **BRD-EXP-032** | Products must be auto-discovered without restart | P1 | INT-EXP-032 | 1.0 | 2026-01-12 |
| **BRD-EXP-033** | Products must be independently enableable/disableable | P0 | INT-EXP-033 | 1.0 | 2026-01-12 |
| **BRD-EXP-034** | Product load errors must not crash the platform | P0 | INT-EXP-034 | 1.0 | 2026-01-12 |
| **BRD-EXP-035** | Products must be shippable in < 1 day | P1 | INT-FACTORY-003 | 1.0 | Added: 2026-01-13 |
| **BRD-EXP-036** | Products must focus on domain logic only, no infrastructure burden | P0 | INT-FACTORY-004 | 1.0 | Added: 2026-01-13 |
| **BRD-EXP-037** | Products must be evolvable via intent updates | P1 | INT-FACTORY-005 | 1.0 | Added: 2026-01-13 |

### 3.5 Product Isolation

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-EXP-040** | Products must not access other products' agents or tools | P0 | INT-EXP-040, INV-6 | 1.0 | 2026-01-12 |
| **BRD-EXP-041** | Products must not access other products' data | P0 | INT-EXP-041, INV-6 | 1.0 | 2026-01-12 |
| **BRD-EXP-042** | Product failures must not affect other products | P0 | INT-EXP-042 | 1.0 | 2026-01-12 |
| **BRD-EXP-043** | Products must have isolated observability directories | P0 | INT-EXP-043 | 1.0 | 2026-01-12 |
| **BRD-EXP-044** | Products cannot modify core framework | P0 | INV-6 | 1.0 | Added: 2026-01-13 |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Products cannot modify core | Product patches orchestrator |
| Products are isolated | Product A reads Product B's data |
| Products are fault-isolated | Product A crash takes down Product B |

### 3.6 Error Experience

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-EXP-050** | Error messages must identify the problem clearly | P0 | — | 2026-01-12 |
| **BRD-EXP-051** | Error messages must suggest remediation steps | P1 | — | 2026-01-12 |
| **BRD-EXP-052** | Validation errors must identify the specific field | P0 | — | 2026-01-12 |
| **BRD-EXP-053** | Not-found errors must suggest available alternatives | P1 | — | 2026-01-12 |

### 3.7 Product Factory Model

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-EXP-060** | Product creation is primarily an intent-driven activity | P0 | INT-FACTORY-001 | 1.0 | Added: 2026-01-13 |
| **BRD-EXP-061** | Code is a generated artifact, not the source of truth | P0 | INT-FACTORY-002 | 1.0 | Added: 2026-01-13 |
| **BRD-EXP-062** | Products define what, framework defines how | P0 | INT-FACTORY-013 | 1.0 | Added: 2026-01-13 |
| **BRD-EXP-063** | Framework provides 90% of functionality, products add 10% | P1 | INT-FACTORY-014 | 1.0 | Added: 2026-01-13 |
| **BRD-EXP-064** | Products are forbidden from re-implementing framework services | P0 | INT-FACTORY-011, INV-10 | 1.0 | Added: 2026-01-13 |

---

## 4. User Stories

### API Developer Stories
- **US-EXP-001**: As an API developer, I want predictable response formats so that I can write robust integration code.
- **US-EXP-002**: As an API developer, I want clear error codes so that I can handle failures programmatically.
- **US-EXP-003**: As an API developer, I want to discover available products so that I don't need out-of-band documentation.

### CLI Operator Stories
- **US-EXP-010**: As a CLI operator, I want JSON output so that I can pipe results to other tools.
- **US-EXP-011**: As a CLI operator, I want helpful error messages so that I can fix issues without documentation.
- **US-EXP-012**: As a CLI operator, I want to script approval workflows so that I can automate operations.

### UI End User Stories
- **US-EXP-020**: As an end user, I want to see what products are available so that I can find the right automation.
- **US-EXP-021**: As an end user, I want to track my workflow progress so that I know when it's complete.
- **US-EXP-022**: As an end user, I want to respond to system questions so that workflows can continue.

### Product Builder Stories
- **US-EXP-030**: As a product builder, I want to create a new product in < 1 day so that I can iterate quickly.
- **US-EXP-031**: As a product builder, I want clear patterns so that I don't reinvent conventions.
- **US-EXP-032**: As a product builder, I want my product isolated so that bugs don't affect others.

---

## 5. Acceptance Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Time-to-first-product | From scaffold to working flow | < 1 day |
| API response consistency | Responses matching envelope schema | 100% |
| CLI scriptability | Commands returning valid JSON | 100% |
| Product isolation | Cross-product access attempts blocked | 100% |
| Error actionability | Errors with remediation guidance | > 80% |

---

## 6. Techspec Mapping

| BRD ID | Description | Derived Techspec |
|--------|-------------|------------------|
| BRD-EXP-001 | HTTP API | GW-API-001...005 |
| BRD-EXP-002 | Response envelope | GW-API-060...063 |
| BRD-EXP-003 | Error codes | GW-ERR-001...007 |
| BRD-EXP-005 | Product/flow listing | GW-API-010...016 |
| BRD-EXP-006 | Run operations | GW-API-020...027, GW-API-030...043 |
| BRD-EXP-010 | CLI interface | GW-CLI-001...002 |
| BRD-EXP-011 | JSON output | GW-CLI-030...033 |
| BRD-EXP-012 | CLI commands | GW-CLI-010...020 |
| BRD-EXP-020 | Web UI | GW-UI-001...005 |
| BRD-EXP-021 | Product display | GW-UI-030...034 |
| BRD-EXP-024 | UI approvals | GW-UI-070...078 |
| BRD-EXP-030 | Product structure | PROD-DIR-001...007 |
| BRD-EXP-031 | Product manifest | PROD-MAN-001...042 |
| BRD-EXP-033 | Product enablement | PROD-YAML-001...004 |
| BRD-EXP-035 | Product scaffolding | PROD-SCAFFOLD-* |
| BRD-EXP-036 | Thin products | PROD-THIN-* |
| BRD-EXP-037 | Intent-driven evolution | PROD-INTENT-* |
| BRD-EXP-040 | Agent/tool isolation | PROD-REG-020...024, PROD-RUN-001...005 |
| BRD-EXP-041 | Data isolation | PROD-RUN-010...012 |
| BRD-EXP-044 | Core protection | PROD-CORE-PROTECT-* |
| BRD-EXP-060 | Intent-driven creation | PROD-FACTORY-001...005 |
| BRD-EXP-061 | Generated artifacts | PROD-FACTORY-010...015 |
| BRD-EXP-062 | What/how separation | PROD-FACTORY-020...025 |
| BRD-EXP-064 | No re-implementation | PROD-FACTORY-030...035 |

---

## 7. Cross-Cutting Requirements

> **Source**: [INT-LIFECYCLE](../00_developer_intent/intent.md#5-developer-intent-lifecycle-int-lifecycle), [INT-FACTORY](../00_developer_intent/intent.md#6-product-factory-model-int-factory)

### 7.1 Intent Ownership

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-EXP-LIFE-001** | Framework Developer owns Framework Developer Intent | P0 | INT-LIFECYCLE-001 | Added: 2026-01-13 |
| **BRD-EXP-LIFE-002** | Product Developer owns Product Developer Intent | P0 | INT-LIFECYCLE-002 | Added: 2026-01-13 |
| **BRD-EXP-LIFE-003** | End Users never modify intent directly | P0 | INT-LIFECYCLE-003 | Added: 2026-01-13 |

### 7.2 Design-Time Intelligence

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-EXP-FAC-001** | AI can derive BRDs from intent | P1 | INT-FACTORY-031, INV-8 | Added: 2026-01-13 |
| **BRD-EXP-FAC-002** | AI can derive specs from BRDs | P1 | INT-FACTORY-032, INV-8 | Added: 2026-01-13 |
| **BRD-EXP-FAC-003** | AI can generate code from specs | P1 | INT-FACTORY-033, INV-8 | Added: 2026-01-13 |
| **BRD-EXP-FAC-004** | AI can generate system design from code | P2 | INT-FACTORY-034 | Added: 2026-01-13 |

### 7.3 Success and Failure Smells

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-EXP-FAC-010** | Success/failure smells must be defined qualitatively | P1 | INT-FACTORY-020 | Added: 2026-01-13 |
| **BRD-EXP-FAC-011** | Smells must be checked during architecture reviews | P1 | INT-FACTORY-021 | Added: 2026-01-13 |
| **BRD-EXP-FAC-012** | Smell detection must trigger design review | P1 | INT-FACTORY-022 | Added: 2026-01-13 |

---

## 8. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| FastAPI | External | HTTP framework |
| Streamlit | External | UI framework |
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

## 10. Product Creation Checklist

For product builders, a new product requires:

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

## 11. Framework Laws Governing Experience

> **Source**: [Framework Laws](../00_developer_intent/intent.md#7-framework-laws)

| Law | Implication |
|-----|-------------|
| Products are isolated | No cross-product resource access |
| Flows are explicit | YAML-defined, no implicit paths |
| Intent precedes BRD | Product requirements derive from intent |

---

## Related Documents

- [Intent.md](../00_developer_intent/intent.md) — Source developer intent
- [Vision.md](../00_developer_intent/Vision.md) — Platform vision and principles
- [BRD-operations.md](BRD-operations.md) — Observability requirements
- [GW-gateway.md](../techspec/GW-gateway.md) — Technical gateway specs
- [PROD-products.md](../techspec/PROD-products.md) — Technical product specs
