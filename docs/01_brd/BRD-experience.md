# BRD: Developer & User Experience

> **Document ID**: BRD-EXP  
> **Last Updated**: 2026-01-12  
> **Status**: V1 Release

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

### 3.1 API Experience

| ID | Requirement | Priority | Rationale |
|----|-------------|----------|-----------|
| **BRD-EXP-001** | Platform must be accessible via HTTP REST API | P0 | Integration standard |
| **BRD-EXP-002** | API responses must follow consistent envelope format | P0 | Predictable parsing |
| **BRD-EXP-003** | API errors must include machine-readable codes | P0 | Automated error handling |
| **BRD-EXP-004** | API errors must include human-readable messages | P0 | Developer debugging |
| **BRD-EXP-005** | API must support listing products and flows | P0 | Discovery |
| **BRD-EXP-006** | API must support starting, monitoring, and resuming runs | P0 | Core functionality |
| **BRD-EXP-007** | API must enforce payload size limits | P1 | Resource protection |

### 3.2 CLI Experience

| ID | Requirement | Priority | Rationale |
|----|-------------|----------|-----------|
| **BRD-EXP-010** | Platform must be accessible via command-line interface | P0 | Operator standard |
| **BRD-EXP-011** | CLI output must be valid JSON for scripting | P0 | Automation support |
| **BRD-EXP-012** | CLI must provide commands for all core operations | P0 | Feature parity |
| **BRD-EXP-013** | CLI errors must exit with appropriate status codes | P0 | Script integration |
| **BRD-EXP-014** | CLI must provide helpful guidance on errors | P1 | User experience |

### 3.3 UI Experience

| ID | Requirement | Priority | Rationale |
|----|-------------|----------|-----------|
| **BRD-EXP-020** | Platform must be accessible via web interface | P0 | Non-technical users |
| **BRD-EXP-021** | UI must display available products and flows | P0 | Discovery |
| **BRD-EXP-022** | UI must allow running flows with input | P0 | Core functionality |
| **BRD-EXP-023** | UI must display run status and history | P0 | Monitoring |
| **BRD-EXP-024** | UI must support approval workflows | P0 | Human-in-the-loop |
| **BRD-EXP-025** | UI must support user input collection | P0 | Interactive workflows |
| **BRD-EXP-026** | UI must display execution timeline with events | P1 | Debugging support |

### 3.4 Product System

| ID | Requirement | Priority | Rationale |
|----|-------------|----------|-----------|
| **BRD-EXP-030** | New products must be creatable from standard structure | P0 | Fast onboarding |
| **BRD-EXP-031** | Products must declare capabilities via manifest | P0 | Self-documenting |
| **BRD-EXP-032** | Products must be auto-discovered without restart | P1 | Developer velocity |
| **BRD-EXP-033** | Products must be independently enableable/disableable | P0 | Operational control |
| **BRD-EXP-034** | Product load errors must not crash the platform | P0 | Fault isolation |

### 3.5 Product Isolation

| ID | Requirement | Priority | Rationale |
|----|-------------|----------|-----------|
| **BRD-EXP-040** | Products must not access other products' agents or tools | P0 | Security boundary |
| **BRD-EXP-041** | Products must not access other products' data | P0 | Data isolation |
| **BRD-EXP-042** | Product failures must not affect other products | P0 | Fault isolation |
| **BRD-EXP-043** | Products must have isolated observability directories | P0 | Clean separation |

### 3.6 Error Experience

| ID | Requirement | Priority | Rationale |
|----|-------------|----------|-----------|
| **BRD-EXP-050** | Error messages must identify the problem clearly | P0 | User experience |
| **BRD-EXP-051** | Error messages must suggest remediation steps | P1 | Self-service |
| **BRD-EXP-052** | Validation errors must identify the specific field | P0 | Developer productivity |
| **BRD-EXP-053** | Not-found errors must suggest available alternatives | P1 | Discovery |

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
| BRD-EXP-040 | Agent/tool isolation | PROD-REG-020...024, PROD-RUN-001...005 |
| BRD-EXP-041 | Data isolation | PROD-RUN-010...012 |

---

## 7. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| FastAPI | External | HTTP framework |
| Streamlit | External | UI framework |
| Product Catalog | Internal | Discovery service |

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API breaking changes | Integration failures | Versioning, deprecation policy |
| UI complexity | User confusion | User testing, progressive disclosure |
| Isolation bypass | Security breach | Strong boundaries, testing |
| Slow product creation | Developer frustration | Templates, scaffolding tools |

---

## 9. Product Creation Checklist

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

## Related Documents

- [Vision.md](Vision.md) — Platform vision and principles
- [BRD-operations.md](BRD-operations.md) — Observability requirements
- [GW-gateway.md](../techspec/GW-gateway.md) — Technical gateway specs
- [PROD-products.md](../techspec/PROD-products.md) — Technical product specs
