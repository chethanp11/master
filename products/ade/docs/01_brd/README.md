# ADE Business Requirements Documentation

> **Product**: Analytical Decision Engine (ADE)  
> **Platform**: MASTER — Managed AI Systems for Trusted Execution & Reasoning  
> **Version**: V1.2  
> **Last Updated**: 2026-01-19

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial release |
| V1.2 | 2026-01-19 | Updated BRD table schema guidance and aligned scope placement |

## Document Index

| Document | Description |
|----------|-------------|
| [BRD-overview.md](BRD-overview.md) | Product overview, objectives, scope |
| [BRD-flows.md](BRD-flows.md) | Flow business requirements |
| [BRD-agents.md](BRD-agents.md) | Agent and semantic interpretation requirements |
| [BRD-tools.md](BRD-tools.md) | Tool business requirements |
| [BRD-data.md](BRD-data.md) | Data and schema requirements |
| [BRD-outputs.md](BRD-outputs.md) | Output and audit requirements |

---

## Quick Reference

### Product Vision

ADE accepts analyst questions and CSV datasets to produce **audit-ready analytical decisions** with evidence, confidence, and traceability.

### Scope

See section 7 for the full scope tables.

---

## How to Add a Requirement

Use the required BRD table structure in each BRD file:

```markdown
| ID | Requirement | Derived from (Intent ID) | Priority | Added Date | Version | Notes |
|----|-------------|---------------------------|----------|------------|---------|-------|
| BRD-<THEME>-NNN | <Requirement statement> | INT-<AREA>-NNN | P0/P1/P2 | YYYY-MM-DD | V1.1 | — |
```

## 7. Scope (From BRD-overview.md)

### 7.1 In Scope

| Category | Items |
|----------|-------|
| **Workflows** | Question-first and dataset-first workflows |
| **Inputs** | Analyst questions and CSV datasets |
| **Outputs** | Business reports and decision packets |
| **User Interactions** | Visualization preferences and plan approval |
| **Analysis** | Anomaly detection, hypothesis testing, metric computation |

### 7.2 Out of Scope

| Category | Exclusion | Rationale |
|----------|-----------|-----------|
| **Data Sources** | Live database connectors | CSV focus for MVP |
| **Data Sources** | Streaming inputs | Batch processing only |
| **Data Operations** | Multi-dataset joins | Single dataset per run |
| **System Behavior** | Dynamic flow mutation | Deterministic flows only |
| **Product Surface** | BI dashboarding | Decision packets are primary |
