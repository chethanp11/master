# ADE Business Requirements Documentation

> **Product**: Analytical Decision Engine (ADE)  
> **Version**: 1.0.0  
> **Last Updated**: 2026-01-12

---

## Document Index

| Document | Description |
|----------|-------------|
| [BRD-overview.md](BRD-overview.md) | Product overview, objectives, scope |
| [BRD-flows.md](BRD-flows.md) | Flow business requirements |
| [BRD-agents.md](BRD-agents.md) | Agent business requirements |
| [BRD-tools.md](BRD-tools.md) | Tool business requirements |
| [BRD-data.md](BRD-data.md) | Data and schema requirements |
| [BRD-outputs.md](BRD-outputs.md) | Output and audit requirements |

---

## Quick Reference

### Product Vision

ADE accepts analyst questions and CSV datasets to produce **audit-ready analytical decisions** with evidence, confidence, and traceability.

### In Scope

- Free-text analyst workflow (`ade_v1`)
- Dataset-first visualization workflow (`visualization`)
- CSV dataset processing
- Business reports and decision packets
- Plan approval workflow

### Out of Scope

- Live database connectors or streaming inputs
- Multi-dataset joins
- Automatic tool discovery or dynamic flow mutation
- BI dashboarding as primary product surface

---

## Traceability

| BRD | Techspec | System Design |
|-----|----------|---------------|
| BRD-overview.md | — | architecture.md |
| BRD-flows.md | FLOW-flows.md | flows.md |
| BRD-agents.md | AGENT-agents.md | agents-and-tools.md |
| BRD-tools.md | TOOL-tools.md | agents-and-tools.md |
| BRD-data.md | SCHEMA-schemas.md, IO-inputs-outputs.md | schemas.md, inputs-and-outputs.md |
| BRD-outputs.md | IO-inputs-outputs.md | inputs-and-outputs.md |
