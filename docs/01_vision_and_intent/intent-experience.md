# Developer Intent: Developer & User Experience (INT-EXP)

> **Maps to**: [BRD-experience.md](../02_brd/BRD-experience.md)  
> **Version**: 1.1  
>
> **Source**: Extracted from [intent.md](intent.md) § 3  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |

## 3.1 API Experience

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-001** | Platform must be accessible via HTTP REST API | Integration standard |
| **INT-EXP-002** | API responses must follow consistent envelope format | Predictable parsing |
| **INT-EXP-003** | API errors must include machine-readable codes | Automated error handling |
| **INT-EXP-004** | API errors must include human-readable messages | Developer debugging |
| **INT-EXP-005** | API must support listing products and flows | Discovery |
| **INT-EXP-006** | API must support starting, monitoring, and resuming runs | Core functionality |
| **INT-EXP-007** | API must enforce payload size limits | Resource protection |

---

## 3.2 CLI Experience

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-010** | Platform must be accessible via command-line interface | Operator standard |
| **INT-EXP-011** | CLI output must be valid JSON for scripting | Automation support |
| **INT-EXP-012** | CLI must provide commands for all core operations | Feature parity |
| **INT-EXP-013** | CLI errors must exit with appropriate status codes | Script integration |
| **INT-EXP-014** | CLI must provide helpful guidance on errors | User experience |

---

## 3.3 UI Experience

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-020** | Platform must be accessible via web interface | Non-technical users |
| **INT-EXP-021** | UI must display available products and flows | Discovery |
| **INT-EXP-022** | UI must allow running flows with input | Core functionality |
| **INT-EXP-023** | UI must display run status and history | Monitoring |
| **INT-EXP-024** | UI must support approval workflows | Human-in-the-loop |
| **INT-EXP-025** | UI must support user input collection | Interactive workflows |
| **INT-EXP-026** | UI must display execution timeline with events | Debugging support |

---

## 3.4 Product System

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-030** | New products must be creatable from standard structure | Fast onboarding |
| **INT-EXP-031** | Products must declare capabilities via manifest | Self-documenting |
| **INT-EXP-032** | Products must be auto-discovered without restart | Developer velocity |
| **INT-EXP-033** | Products must be independently enableable/disableable | Operational control |
| **INT-EXP-034** | Product load errors must not crash the platform | Fault isolation |

---

## 3.5 Product Isolation

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-EXP-040** | Products must not access other products' agents or tools | Security boundary |
| **INT-EXP-041** | Products must not access other products' data | Data isolation |
| **INT-EXP-042** | Product failures must not affect other products | Fault isolation |
| **INT-EXP-043** | Products must have isolated observability directories | Clean separation |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Products cannot modify core | Product patches orchestrator |
| Products are isolated | Product A reads Product B's data |
| Products are fault-isolated | Product A crash takes down Product B |

---

## BRD Derivation

This document derives the following in [BRD-experience.md](../02_brd/BRD-experience.md):

- INT-EXP-* → BRD-EXP-*
