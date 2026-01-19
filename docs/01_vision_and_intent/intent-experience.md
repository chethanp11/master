# Developer Intent: Developer & User Experience (INT-EXP)

> **Maps to**: [BRD-experience.md](../02_brd/BRD-experience.md)  
> **Version**: 1.2  

---

## Purpose

Define platform-level intent for developer and user experience across API, CLI, UI, and product lifecycle.

## Scope

- Platform-only experience requirements and product lifecycle capabilities.
- Product-specific UX requirements are out of scope.

---

## PLAT-EXP-API — API Experience

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-EXP-001 | Platform SHALL be accessible via HTTP REST API — Integration standard | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-002 | API responses SHALL follow a consistent envelope format — Predictable parsing | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-003 | API errors SHALL include machine-readable codes — Automated error handling | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-004 | API errors SHALL include human-readable messages — Developer debugging | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-005 | API SHALL support listing products and flows — Discovery | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-006 | API SHALL support starting, monitoring, and resuming runs — Core functionality | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-007 | API SHALL enforce payload size limits — Resource protection | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-EXP-CLI — CLI Experience

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-EXP-010 | Platform SHALL be accessible via command-line interface — Operator standard | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-011 | CLI output SHALL be valid JSON for scripting — Automation support | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-012 | CLI SHALL provide commands for all core operations — Feature parity | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-013 | CLI errors SHALL exit with appropriate status codes — Script integration | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-014 | CLI SHALL provide helpful guidance on errors — User experience | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-EXP-UI — UI Experience

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-EXP-020 | Platform SHALL be accessible via web interface — Non-technical users | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-021 | UI SHALL display available products and flows — Discovery | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-022 | UI SHALL allow running flows with input — Core functionality | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-023 | UI SHALL display run status and history — Monitoring | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-024 | UI SHALL support approval workflows — Human-in-the-loop | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-025 | UI SHALL support user input collection — Interactive workflows | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-026 | UI SHALL display execution timeline with events — Debugging support | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-EXP-PROD — Product System

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-EXP-030 | New products SHALL be creatable from standard structure — Fast onboarding | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-031 | Products SHALL declare capabilities via manifest — Self-documenting | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-032 | Products SHALL be auto-discovered without restart — Developer velocity | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-033 | Products SHALL be independently enableable/disableable — Operational control | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-034 | Product load errors SHALL NOT crash the platform — Fault isolation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-EXP-ISOLATION — Product Isolation

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-EXP-040 | Products SHALL NOT access other products' agents or tools — Security boundary | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-041 | Products SHALL NOT access other products' data — Data isolation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-042 | Product failures SHALL NOT affect other products — Fault isolation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-043 | Products SHALL have isolated observability directories — Clean separation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-044 | Products SHALL NOT modify core — Prevent platform corruption | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-045 | Products SHALL be isolated — Prevent cross-product access | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-EXP-046 | Products SHALL be fault-isolated — Prevent cascading failures | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## Removed / Quarantined Content (Out of Platform Scope)

- None.

---

## BRD Derivation

This document derives the following in [BRD-experience.md](../02_brd/BRD-experience.md):

- INT-EXP-* → BRD-EXP-*
