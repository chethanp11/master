# How to Enhance ADE (v1.1)

> **Last Updated**: 2026-01-17  
> **Version**: 1.1  
> **Audience**: ADE product contributors

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-17 | Initial ADE enhancement workflow |

## Overview

This guide defines the ADE-specific, deterministic doc alignment workflow:

```
Intent → BRD → TechSpec → System Design Coverage → Implementation Plan
```

Only ADE docs under `products/ade/docs/` are in scope.

---

## 1. Product Intent (Source of Truth)

### Where It Lives

```
products/ade/docs/00_product_intent/
├── Vision.md
├── intent-overview-flows.md
├── intent-agents-tools.md
├── intent-data-outputs.md
├── intent-intel-acceptance.md
└── README.md
```

### Rules

- Intent files are the **only source of truth** for meaning.
- Do NOT invent functionality not implied by intent.
- If intent is ambiguous, record a clarification gap.

---

## 2. Intent → BRD Alignment Loop

### Target Files

```
products/ade/docs/01_brd/
├── BRD-overview.md
├── BRD-flows.md
├── BRD-agents.md
├── BRD-tools.md
├── BRD-data.md
├── BRD-outputs.md
├── BRD-COVERAGE.md
└── README.md
```

### Task 1: Update BRD-COVERAGE.md

Update `products/ade/docs/01_brd/BRD-COVERAGE.md` with:

1) Intent requirement list (Intent ID, source file, section)  
2) Mapping to BRD requirement IDs  
3) Coverage status: Covered / Partial / Missing / Clarification Needed  
4) Gap register (only Partial / Missing / Clarification Needed)  
5) “Next BRD edits required” checklist with exact target files  
6) Completion line: `BRD-COVERAGE GAP COUNT: <n>`

### Task 2: Update BRD Docs

For each gap:
- Add or extend BRD sections in the correct BRD file
- Assign BRD IDs (INT-<area>-### → BRD-<area>-###)
- Cross-reference Intent IDs inline

### Iteration Protocol

- Run Task 1 → Task 2 → Task 1 until:
  - `BRD-COVERAGE GAP COUNT: 0`, or
  - remaining gaps are only “Clarification Needed”
- If only clarifications remain, add:
  - “Open Intent Clarifications Required” to BRD-COVERAGE.md

---

## 3. BRD → Tech Spec Alignment Loop

### Target Files

```
products/ade/docs/02_techspec/
├── AGENT-agents.md
├── FLOW-flows.md
├── TOOL-tools.md
├── IO-inputs-outputs.md
├── SCHEMA-schemas.md
└── TS-COVERAGE.md
```

### Hard Rules

- Do NOT edit BRD files unless there is an actual inconsistency/typo.
- Only edit files under `products/ade/docs/02_techspec/` and `TS-COVERAGE.md`.
- Every new/changed requirement must have an explicit ID and map to BRD IDs.
- If a BRD point is ambiguous, add a “Clarification Needed” gap in TS-COVERAGE.

### Task 1: Update TS-COVERAGE.md

`TS-COVERAGE.md` must contain:
1) Coverage matrix table (BRD ID → BRD source → TS coverage links → Status)  
2) Gap register (only uncovered/partial/clarification-needed items)  
3) “Next edits required” checklist with exact TS files/sections  
4) Completion line: `TS-COVERAGE GAP COUNT: <n>`

### Task 2: Update Tech Specs

- Add missing sections/content with BRD IDs inline  
- Keep specs detailed enough to develop code  
- Update TS-COVERAGE to mark coverage with precise location pointers

### Iteration Protocol

- Task 1 → Task 2 → Task 1 until `TS-COVERAGE GAP COUNT: 0`
- Stop only if remaining gaps are “Clarification Needed”

---

## 4. Tech Spec → System Design → Implementation Loop

### Read-Only System Design

```
products/ade/docs/04_systemdesign/
├── architecture.md
├── agents-and-tools.md
├── flows.md
├── inputs-and-outputs.md
├── schemas.md
├── SD-COVERAGE.md
└── README.md
```

**System Design files MUST NOT be edited.**

### Implementation Outputs

```
products/ade/docs/03_implementation_plan/imp_plan.md
```

### Task 1: Update SD-COVERAGE.md

Populate `products/ade/docs/04_systemdesign/SD-COVERAGE.md` with:
1) Coverage matrix (Tech Spec ID → SD reference → Status)  
2) Gap register (Partial/Missing/Clarification Needed only)  
3) Implementation impact for each gap  
4) Completion line: `SD-COVERAGE GAP COUNT: <n>`

### Task 2: Update imp_plan.md

`imp_plan.md` must include:
1) Overview (purpose, assumptions, entry criteria)  
2) Implementation Units (IMP-###) with:
   - Tech Spec IDs
   - SD-COVERAGE gap IDs
   - Target code locations
   - Change type (new/extend/wiring)
   - Step-by-step instructions
   - Acceptance checks  
3) Dependency order  
4) Non-goals  
5) Final verification checklist

### Iteration Protocol

- Task 1 → Task 2 → Task 1  
- Do not mark SD gaps resolved because they appear in the plan  
- Stop when all gaps are in imp_plan.md or only “Clarification Needed” remain  
- If only clarifications remain, add:
  - “Blocking Clarifications Required Before Implementation” to SD-COVERAGE.md

---

## 5. Quality Bar

- Every step is traceable: Intent → BRD → TechSpec → SD-COVERAGE → imp_plan → code
- No vague steps; instructions must be executable and deterministic
- No architectural drift from System Design
- No silent assumptions
