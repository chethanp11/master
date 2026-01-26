# ADE Implementation Plan

> **Document**: Implementation Plan  
> **Version**: 2.0  
> **Last Updated**: 2026-01-21  
> **Status**: V2.0 Release — TechSpec → SystemDesign Alignment Complete

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-17 | Initial release with 15 IMP units |
| 1.1 | 2026-01-20 | Added IMP-016..025 for V1.4 Tech Spec coverage |
| 1.2 | 2026-01-21 | Updated status for 21 completed IMP units |
| 2.0 | 2026-01-21 | TechSpec V1.5/V1.6 → SystemDesign V1.4 alignment complete; 21 new TSD IDs verified covered; no new implementation required |

---

## 1. Overview

### 1.1 Purpose

This document defines the deterministic implementation plan for ADE (Analytical Decision Engine) based on the alignment between:
- **Tech Specs (Source of Truth)**: `products/ade/docs/02_techspec/*.md` (V1.5/V1.6)
- **System Design (Reference Architecture)**: `products/ade/docs/04_systemdesign/*.md` (V1.1.0)
- **SD-COVERAGE (Gap Analysis)**: `products/ade/docs/04_systemdesign/SD-COVERAGE.md` (V1.4)

### 1.2 Alignment Status

| Layer | Version | Gap Count | Status |
|-------|---------|-----------|--------|
| BRD → TechSpec | TS-COVERAGE V1.6 | 0 | ✅ Complete |
| TechSpec → SystemDesign | SD-COVERAGE V1.4 | 0 | ✅ Complete |

### 1.3 Assumptions

1. All V1.5/V1.6 TSD IDs have corresponding coverage in System Design V1.1.0
2. System Design files are read-only reference architecture (MUST NOT be edited)
3. All implementation changes are strictly inside `products/ade/`

### 1.4 Entry Criteria

- TS-COVERAGE GAP COUNT: 0 ✅
- SD-COVERAGE GAP COUNT: 0 ✅
- All BRD requirements have TSD mappings ✅
- All TSD IDs have SD coverage ✅

---

## 2. V1.5/V1.6 TSD Coverage Summary

The following 21 new TSD IDs were added in Tech Spec V1.5/V1.6 and verified against System Design:

### 2.1 Agent Requirements (TS-agents.md V1.5)

| TSD ID | Description | SD Reference | Status |
|--------|-------------|--------------|--------|
| TS-AGENT-GEN-004 | Agents as specialists | agents-and-tools.md#agents | ✅ Covered |
| TS-SEM-ADAPTER-006 | Intent-derived behavior | agents-and-tools.md#semantic-adapter | ✅ Covered |
| TS-AGENT-FRI-006 | Platform semantic reliance | architecture.md#10-framework-alignment | ✅ Covered |
| TS-AGENT-FAIL-001 | Fail-fast on incompatibility | agents-and-tools.md#failure-modes | ✅ Covered |
| TS-AGENT-FAIL-002 | Block on missing dimensions | agents-and-tools.md#failure-modes | ✅ Covered |
| TS-AGENT-FAIL-003 | Temporal analysis gating | agents-and-tools.md#failure-modes | ✅ Covered |
| TS-AGENT-NARRATIVE-001 | Reasoning narrative artifact | agents-and-tools.md#6-1-narrative-builder | ✅ Covered |
| TS-AGENT-SEPARATION-001 | Reasoning-presentation separation | architecture.md#8-trust-and-audit | ✅ Covered |

### 2.2 Tool Requirements (TS-tools.md V1.5)

| TSD ID | Description | SD Reference | Status |
|--------|-------------|--------------|--------|
| TS-TOOL-INTENT-001 | Intent-bound tool selection | agents-and-tools.md#intent-bound-tool-selection | ✅ Covered |
| TS-TOOL-INTENT-002 | No availability-based selection | agents-and-tools.md#intent-bound-tool-selection | ✅ Covered |
| TS-TOOL-INTENT-003 | Dynamic tool discovery | agents-and-tools.md#intent-bound-tool-selection | ✅ Covered |
| TS-TOOL-INTENT-004 | Intent-derived binding | agents-and-tools.md#intent-bound-tool-selection | ✅ Covered |
| TS-TOOL-INTENT-005 | Call-time intent declaration | agents-and-tools.md#intent-bound-tool-selection | ✅ Covered |
| TS-TOOL-INTENT-006 | Fail on missing tools | agents-and-tools.md#intent-bound-tool-selection | ✅ Covered |
| TS-TOOL-INTENT-007 | No permission inference | agents-and-tools.md#intent-bound-tool-selection | ✅ Covered |
| TS-TOOL-ASSEMBLE-008 | Evidence deduplication | agents-and-tools.md#5-assembly-tools | ✅ Covered |
| TS-TOOL-RENDER-005 | Self-contained HTML | agents-and-tools.md#6-rendering-tools | ✅ Covered |
| TS-TOOL-RENDER-006 | PDF content completeness | agents-and-tools.md#6-rendering-tools | ✅ Covered |
| TS-TOOL-RENDER-007 | PDF printability | agents-and-tools.md#6-rendering-tools | ✅ Covered |

### 2.3 I/O Requirements (TS-inputs-outputs.md V1.5)

| TSD ID | Description | SD Reference | Status |
|--------|-------------|--------------|--------|
| TS-IO-OBJ-009 | Analysis-agnostic extensibility | inputs-and-outputs.md#1-input-payloads | ✅ Covered |
| TS-IO-DATA-009 | Transaction-level default | inputs-and-outputs.md#2-datasets | ✅ Covered |

---

## 3. Completed Implementation Units (V1.0-V1.2)

The following 25 IMP units from previous versions remain complete:

| IMP ID | TSD IDs | Description | Status |
|--------|---------|-------------|--------|
| IMP-001 | TS-IO-OBJ-001..008 | Clarification records | ✅ Complete |
| IMP-002 | TS-AGENT-REASON-001, 002 | Multi-stage reasoning ladder | ✅ Complete |
| IMP-003 | TS-AGENT-REASON-003 | Bounded reasoning cycles | ✅ Complete |
| IMP-004 | TS-AGENT-CRIT-005 | Blocking critique findings | ✅ Complete |
| IMP-005 | TS-AGENT-CRIT-001..004 | Critique integration | ✅ Complete |
| IMP-006 | TS-TOOL-NARR-001 | Anomaly interpretation wiring | ✅ Complete |
| IMP-007 | TS-AGENT-DASH-001, 002 | Dashboard agent outputs | ✅ Complete |
| IMP-008 | TS-FLOW-V1-001..005 | ade_v1 flow steps | ✅ Complete |
| IMP-009 | TS-FLOW-VIZ-001..004 | Visualization flow steps | ✅ Complete |
| IMP-010 | TS-TOOL-DATA-001..005 | Data tools | ✅ Complete |
| IMP-011 | TS-TOOL-ANALYSIS-001..007 | Analysis tools | ✅ Complete |
| IMP-012 | TS-TOOL-VIZ-001..004 | Visualization tools | ✅ Complete |
| IMP-013 | TS-IO-QUAL-001..008 | Quality validation | ✅ Complete |
| IMP-014 | TS-IO-VER-001..003 | Version metadata | ✅ Complete |
| IMP-015 | TS-IO-DAB-001..005 | Advisory boundary | ✅ Complete |
| IMP-016 | TS-AGENT-FRI-001..005, TS-AGENT-NRL-001..004 | Framework alignment | ✅ Complete |
| IMP-017 | TS-AGENT-TERM-001..003 | Terminal outcomes | ✅ Complete |
| IMP-018 | TS-AGENT-NARR-005 | Narrative from decision records | ✅ Complete |
| IMP-019 | TS-AGENT-CONF-003 | Confidence configuration | ✅ Complete |
| IMP-020 | TS-SEM-VALIDATE-008, 009 | Semantic validation | ✅ Complete |
| IMP-021 | TS-TOOL-GEN-007 | Tool dependency checks | ✅ Complete |
| IMP-022 | TS-TOOL-ANALYSIS-008 | Anomaly severity scoring | ✅ Complete |
| IMP-023 | TS-IO-OUT-007 | Output directory utilities | ✅ Complete |
| IMP-024 | TS-FLOW-V1-006..009 | Plan detail metadata | ✅ Complete |
| IMP-025 | TS-SCHEMA-CTX-004, 005, TS-SCHEMA-EVITEM-001, 002 | Context pack and evidence schemas | ✅ Complete |

---

## 4. New Implementation Requirements

### 4.1 Current Status

Based on the TechSpec V1.5/V1.6 → SystemDesign V1.4 alignment:

| Analysis | Result |
|----------|--------|
| New TSD IDs identified | 21 |
| TSD IDs with SD coverage | 21 |
| TSD IDs missing SD coverage | 0 |
| New implementation required | **None** |

### 4.2 Justification

All 21 new V1.5/V1.6 TSD IDs are already covered by the existing System Design reference architecture:

1. **Agent specialist pattern** (TS-AGENT-GEN-004) - Covered by agents-and-tools.md agent descriptions
2. **Intent-derived behavior** (TS-SEM-ADAPTER-006) - Covered by semantic adapter section
3. **Platform semantic reliance** (TS-AGENT-FRI-006) - Covered by framework alignment section
4. **Failure modes** (TS-AGENT-FAIL-001..003) - Covered by flow error handling
5. **Reasoning narrative** (TS-AGENT-NARRATIVE-001) - Covered by narrative builder section
6. **Reasoning-presentation separation** (TS-AGENT-SEPARATION-001) - Covered by trust/audit section
7. **Intent-bound tool selection** (TS-TOOL-INTENT-001..007) - Covered by tool selection section
8. **Evidence deduplication** (TS-TOOL-ASSEMBLE-008) - Covered by assembly tools section
9. **HTML/PDF rendering** (TS-TOOL-RENDER-005..007) - Covered by rendering tools section
10. **I/O extensibility** (TS-IO-OBJ-009, TS-IO-DATA-009) - Covered by I/O sections

---

## 5. Dependency Order

No new implementation units required. Existing dependency order for completed units:

```
IMP-001 (clarification records)
    ↓
IMP-002..003 (reasoning ladder)
    ↓
IMP-004..005 (critique)
    ↓
IMP-006..007 (narrative/dashboard)
    ↓
IMP-008..009 (flows)
    ↓
IMP-010..012 (tools)
    ↓
IMP-013..015 (quality/version/advisory)
    ↓
IMP-016..025 (framework/terminal/schema)
```

---

## 6. Non-Goals

1. **System Design modifications** - SD files are read-only reference
2. **New IMP units** - All TSD IDs have SD coverage
3. **Framework-level changes** - All ADE work stays in `products/ade/`
4. **imp_outcome.md updates** - Excluded per user instructions
5. **imp_gaps.md updates** - Excluded per user instructions

---

## 7. Final Verification Checklist

| Check | Status |
|-------|--------|
| TS-COVERAGE GAP COUNT = 0 | ✅ Verified |
| SD-COVERAGE GAP COUNT = 0 | ✅ Verified |
| All V1.5/V1.6 TSD IDs tracked in SD-COVERAGE | ✅ Verified (21 IDs) |
| No new implementation units required | ✅ Confirmed |
| System Design files unmodified | ✅ Confirmed |
| Changes limited to `products/ade/` | ✅ Confirmed |

---

## 8. Cross-References

- **BRD**: [products/ade/docs/01_brd/](../01_brd/)
- **Tech Specs**: [products/ade/docs/02_techspec/](../02_techspec/)
- **System Design**: [products/ade/docs/04_systemdesign/](../04_systemdesign/)
- **TS-COVERAGE**: [TS-COVERAGE.md](../02_techspec/TS-COVERAGE.md) (V1.6)
- **SD-COVERAGE**: [SD-COVERAGE.md](../04_systemdesign/SD-COVERAGE.md) (V1.4)

---

## IMP-PLAN GAP COUNT: 0
