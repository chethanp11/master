# Developer Intent: Developer & User Experience (INT-EXP)

> **Maps to**: [BRD-experience.md](../02_brd/BRD-experience.md)  
> **Version**: 1.2  
> **Source**: Extracted from [intent.md](intent.md) § 3

---

## Purpose

Define platform-level intent for developer and user experience across API, CLI, UI, and product lifecycle.

## Scope

- Platform-only experience requirements and product lifecycle capabilities.
- Product-specific UX requirements are out of scope.

---

## PLAT-EXP-API — API Experience

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-EXP-001 | Platform SHALL be accessible via HTTP REST API | Integration standard | — | legacy content (intent-experience.md#3.1) | ID NEEDS NORMALIZATION |
| INT-EXP-002 | API responses SHALL follow a consistent envelope format | Predictable parsing | — | legacy content (intent-experience.md#3.1) | ID NEEDS NORMALIZATION |
| INT-EXP-003 | API errors SHALL include machine-readable codes | Automated error handling | — | legacy content (intent-experience.md#3.1) | ID NEEDS NORMALIZATION |
| INT-EXP-004 | API errors SHALL include human-readable messages | Developer debugging | — | legacy content (intent-experience.md#3.1) | ID NEEDS NORMALIZATION |
| INT-EXP-005 | API SHALL support listing products and flows | Discovery | — | legacy content (intent-experience.md#3.1) | ID NEEDS NORMALIZATION |
| INT-EXP-006 | API SHALL support starting, monitoring, and resuming runs | Core functionality | — | legacy content (intent-experience.md#3.1) | ID NEEDS NORMALIZATION |
| INT-EXP-007 | API SHALL enforce payload size limits | Resource protection | — | legacy content (intent-experience.md#3.1) | ID NEEDS NORMALIZATION |

---

## PLAT-EXP-CLI — CLI Experience

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-EXP-010 | Platform SHALL be accessible via command-line interface | Operator standard | — | legacy content (intent-experience.md#3.2) | ID NEEDS NORMALIZATION |
| INT-EXP-011 | CLI output SHALL be valid JSON for scripting | Automation support | — | legacy content (intent-experience.md#3.2) | ID NEEDS NORMALIZATION |
| INT-EXP-012 | CLI SHALL provide commands for all core operations | Feature parity | — | legacy content (intent-experience.md#3.2) | ID NEEDS NORMALIZATION |
| INT-EXP-013 | CLI errors SHALL exit with appropriate status codes | Script integration | — | legacy content (intent-experience.md#3.2) | ID NEEDS NORMALIZATION |
| INT-EXP-014 | CLI SHALL provide helpful guidance on errors | User experience | — | legacy content (intent-experience.md#3.2) | ID NEEDS NORMALIZATION |

---

## PLAT-EXP-UI — UI Experience

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-EXP-020 | Platform SHALL be accessible via web interface | Non-technical users | — | legacy content (intent-experience.md#3.3) | ID NEEDS NORMALIZATION |
| INT-EXP-021 | UI SHALL display available products and flows | Discovery | — | legacy content (intent-experience.md#3.3) | ID NEEDS NORMALIZATION |
| INT-EXP-022 | UI SHALL allow running flows with input | Core functionality | — | legacy content (intent-experience.md#3.3) | ID NEEDS NORMALIZATION |
| INT-EXP-023 | UI SHALL display run status and history | Monitoring | — | legacy content (intent-experience.md#3.3) | ID NEEDS NORMALIZATION |
| INT-EXP-024 | UI SHALL support approval workflows | Human-in-the-loop | — | legacy content (intent-experience.md#3.3) | ID NEEDS NORMALIZATION |
| INT-EXP-025 | UI SHALL support user input collection | Interactive workflows | — | legacy content (intent-experience.md#3.3) | ID NEEDS NORMALIZATION |
| INT-EXP-026 | UI SHALL display execution timeline with events | Debugging support | — | legacy content (intent-experience.md#3.3) | ID NEEDS NORMALIZATION |

---

## PLAT-EXP-PROD — Product System

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-EXP-030 | New products SHALL be creatable from standard structure | Fast onboarding | — | legacy content (intent-experience.md#3.4) | ID NEEDS NORMALIZATION |
| INT-EXP-031 | Products SHALL declare capabilities via manifest | Self-documenting | — | legacy content (intent-experience.md#3.4) | ID NEEDS NORMALIZATION |
| INT-EXP-032 | Products SHALL be auto-discovered without restart | Developer velocity | — | legacy content (intent-experience.md#3.4) | ID NEEDS NORMALIZATION |
| INT-EXP-033 | Products SHALL be independently enableable/disableable | Operational control | — | legacy content (intent-experience.md#3.4) | ID NEEDS NORMALIZATION |
| INT-EXP-034 | Product load errors SHALL NOT crash the platform | Fault isolation | — | legacy content (intent-experience.md#3.4) | ID NEEDS NORMALIZATION |

---

## PLAT-EXP-ISOLATION — Product Isolation

### Intent

| ID | Intent (SHALL) | Rationale | Depends on | Source | Notes |
|----|----------------|-----------|------------|--------|-------|
| INT-EXP-040 | Products SHALL NOT access other products' agents or tools | Security boundary | — | legacy content (intent-experience.md#3.5) | ID NEEDS NORMALIZATION |
| INT-EXP-041 | Products SHALL NOT access other products' data | Data isolation | — | legacy content (intent-experience.md#3.5) | ID NEEDS NORMALIZATION |
| INT-EXP-042 | Product failures SHALL NOT affect other products | Fault isolation | — | legacy content (intent-experience.md#3.5) | ID NEEDS NORMALIZATION |
| INT-EXP-043 | Products SHALL have isolated observability directories | Clean separation | — | legacy content (intent-experience.md#3.5) | ID NEEDS NORMALIZATION |
| — | Products SHALL NOT modify core | Prevent platform corruption | — | legacy content (intent-experience.md#3.5 constraints) | ID NEEDS NORMALIZATION |
| — | Products SHALL be isolated | Prevent cross-product access | — | legacy content (intent-experience.md#3.5 constraints) | ID NEEDS NORMALIZATION |
| — | Products SHALL be fault-isolated | Prevent cascading failures | — | legacy content (intent-experience.md#3.5 constraints) | ID NEEDS NORMALIZATION |

---

## Removed / Quarantined Content (Out of Platform Scope)

- None.

---

## BRD Derivation

This document derives the following in [BRD-experience.md](../02_brd/BRD-experience.md):

- INT-EXP-* → BRD-EXP-*
