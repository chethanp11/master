# How to Enhance the MASTER Framework

> **Last Updated**: 2026-01-16  
> **Version**: 1.1  
> **Audience**: Framework contributors and maintainers  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |

## Overview

This guide describes the end-to-end process for making changes to the MASTER framework — from capturing developer intent through to validated, documented implementation.

```
Intent → BRD → TechSpec → Implementation → Tests → System Design
```

---

## 1. Developer Intent

### Where It Lives

Developer intent for framework changes lives in:

```
docs/01_vision_and_intent/
├── Vision.md    ← Strategic direction, philosophy, actors
└── intent.md    ← Specific requirements (INT-*, INV-*)
```

### How to Add New Intent

1. **Identify the category** for your change:
   - `INV-*` — Architecture invariants (non-negotiable principles)
   - `INT-AUTO-*` — Intelligent automation (agents, tools, reasoning)
   - `INT-GOV-*` — Governance & compliance
   - `INT-EXP-*` — Developer & user experience
   - `INT-OPS-*` — Operational excellence
   - `INT-LIFECYCLE-*` — Developer intent lifecycle
   - `INT-FACTORY-*` — Product factory model

2. **Add your intent** to the appropriate section in `intent.md`:
   ```markdown
   ### INT-AUTO-XXX: Short Title
   
   - MASTER SHALL <requirement statement>
   - Rationale: <why this matters>
   - Maps to: BRD-AUTO-XXX
   ```

3. **Link to the corresponding BRD** requirement in the table at the top.

---

## 2. Deriving Business Requirements (BRD)

### Where BRDs Live

```
docs/02_business_requirements/
├── README.md
├── BRD-automation.md   ← Agents, tools, reasoning
├── BRD-governance.md   ← Approval, security, audit
├── BRD-experience.md   ← API, CLI, UI, products
└── BRD-operations.md   ← Persistence, observability
```

### How to Derive a BRD from Intent

1. **Map intent to BRD theme**:
   | Intent Prefix | BRD Document |
   |---------------|--------------|
   | `INT-AUTO-*` | BRD-automation.md |
   | `INT-GOV-*` | BRD-governance.md |
   | `INT-EXP-*` | BRD-experience.md |
   | `INT-OPS-*` | BRD-operations.md |

2. **Create the BRD requirement**:
   ```markdown
   ### BRD-AUTO-XXX: Requirement Title
   
   **Priority**: P0 | P1 | P2
   **Source**: INT-AUTO-XXX
   
   **Requirement**: <business-level statement of what the system must do>
   
   **Acceptance Criteria**:
   - [ ] Criterion 1
   - [ ] Criterion 2
   
   **Techspec Coverage**: AGT-XXX, TOOL-XXX
   ```

3. **Assign priority**:
   - **P0**: Must-have for release (blocker)
   - **P1**: Should-have (can defer to next minor)
   - **P2**: Nice-to-have (future)

---

## 3. Creating/Updating Technical Specifications

### Where TechSpecs Live

```
docs/03_technical_specifications/
├── README.md
├── ORC-orchestration.md    ← Orchestration engine
├── AGT-agents-tools.md     ← Agent/tool contracts
├── GOV-governance.md       ← Governance layer
├── MEM-memory.md           ← Memory/persistence
├── INT-intelligence.md     ← Intelligence layer
├── GW-gateway.md           ← Gateway (API/CLI/UI)
├── PROD-products.md        ← Product system
└── ACC-acceptance.md       ← Acceptance criteria
```

### How to Create/Update a TechSpec

1. **Choose the appropriate spec file** based on the domain.

2. **Add a new requirement** with a unique ID:
   ```markdown
   ### AGT-INVOKE-XXX: Requirement Title
   
   **Source**: BRD-AUTO-XXX
   **Status**: V1 | V1.1 | Future
   
   The system SHALL <technical requirement using RFC 2119 language>.
   
   **Implementation**: `core/agents/registry.py:AgentRegistry.invoke()`
   
   **Rationale**: <why this design choice>
   ```

3. **Use RFC 2119 keywords**:
   - `MUST` / `SHALL` — Absolute requirement
   - `MUST NOT` / `SHALL NOT` — Absolute prohibition
   - `SHOULD` — Recommended
   - `MAY` — Optional

4. **Link to implementation** files where the requirement is fulfilled.

---

## 4. Updating SD-COVERAGE

### What is SD-COVERAGE?

[SD-COVERAGE.md](../05_system_design/SD-COVERAGE.md) is the **heart of delta detection**. It maps every Tech Spec requirement ID to its implementation status:

```
Tech Spec IDs − Implemented IDs = Implementation Backlog
```

### Status Legend

| Status | Meaning |
|--------|---------|
| ✅ Implemented | Fully implemented and tested |
| 🟡 Partial | Partially implemented or missing edge cases |
| ❌ Not Implemented | Not yet started |
| 🧪 Experimental | Implemented but not production-ready |
| ⏸️ Deferred | Explicitly moved to future release |

### How to Update SD-COVERAGE

1. **Find the relevant section** in [SD-COVERAGE.md](../05_system_design/SD-COVERAGE.md) (grouped by Tech Spec document).

2. **Update the row** for your requirement:
   ```markdown
   | ORC-RUN-XXX | Your requirement | ✅ Implemented | `core/orchestrator/file.py` | `trace: event.name` | `tests/unit/test_file.py` | Notes |
   ```

3. **Fill in all columns**:
   - **Tech Spec ID**: The requirement ID from techspec
   - **Requirement (short)**: Brief description
   - **Status**: ✅ / 🟡 / ❌ / 🧪 / ⏸️
   - **Implemented In**: File paths with implementation
   - **Trace/Artifact**: Runtime evidence (trace events, artifacts)
   - **Tests**: Test file paths
   - **Notes**: Any caveats or context

4. **Update the summary table** at the top of SD-COVERAGE.md with new counts.

### Finding Gaps (Delta Detection)

```bash
# Count unimplemented requirements
grep -c "❌ Not Implemented" docs/05_system_design/SD-COVERAGE.md

# List partial implementations
grep "🟡 Partial" docs/05_system_design/SD-COVERAGE.md

# Find all requirements needing work
grep -E "❌|🟡" docs/05_system_design/SD-COVERAGE.md
```

### The Mechanical Planning Loop

```
1. Parse Tech Specs → extract all requirement IDs
2. Parse SD-COVERAGE → find implemented IDs
3. DELTA = Tech Spec IDs − Implemented IDs
4. DELTA becomes:
   • Implementation Plan (what to build)
   • TST Prompts (test specifications)
   • Code/Test additions
5. After implementation → update SD-COVERAGE
```

---

## 5. Generating TST Prompts

### What are TST Prompts?

TST (Test Specification Template) prompts are used to generate test cases from techspec requirements.

### How to Generate

1. **Identify testable requirements** in the techspec (look for `SHALL`, `MUST`).

2. **Create test prompt** following this template:
   ```markdown
   ## TST-<PREFIX>-XXX: Test for <Requirement Title>
   
   **Covers**: <TECHSPEC-ID>
   **Type**: unit | integration | architecture | acceptance
   
   **Given**: <precondition>
   **When**: <action>
   **Then**: <expected outcome>
   
   **Edge Cases**:
   - <edge case 1>
   - <edge case 2>
   ```

3. **Map to test categories**:
   | Requirement Type | Test Location |
   |------------------|---------------|
   | Core contracts | `tests/unit/` |
   | Cross-component | `tests/integration/` |
   | Invariants | `tests/architecture/` |
   | End-to-end | `tests/acceptance_intelligence/` |

---

## 6. Validating via Tests and Traces

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/architecture/
pytest tests/acceptance_intelligence/

# Run with coverage
pytest --cov=core --cov-report=html
```

### Validating with Traces

1. **Enable tracing** in your test or run:
   ```python
   from core.memory.tracing import trace_event
   
   trace_event("step_started", {"step_id": "...", "type": "..."})
   ```

2. **Check trace output** in `storage/memory/` or observability store.

3. **Verify trace contains**:
   - All expected events in sequence
   - Required metadata fields
   - No unexpected errors

### Architecture Tests

Architecture tests validate structural invariants:

```bash
pytest tests/architecture/ -v
```

These tests verify:
- Dependency rules (e.g., products don't import from other products)
- Contract compliance
- Layer isolation

---

## 7. Regenerating System Design

### System Design Structure

```
docs/05_system_design/
├── SD-INDEX.md          ← Entry point, delta detection loop
├── SD-ARCH.md           ← Architecture boundaries, invariants
├── SD-COVERAGE.md       ← Tech Spec → Implementation mapping (delta enabler)
├── components/          ← Component-specific docs
│   ├── SD-ORC.md        ← Orchestration
│   ├── SD-GOV.md        ← Governance
│   ├── SD-MEM.md        ← Memory
│   ├── SD-INT.md        ← Intelligence
│   ├── SD-TOOLS.md      ← Tools
│   ├── SD-GW.md         ← Gateway
│   └── SD-PROD.md       ← Products
├── engineering-standards.md
└── product-guide.md
```

### When to Regenerate

Regenerate system design documentation when:
- Implementation changes significantly
- New modules or components are added
- Architectural decisions are made
- Engineers frequently ask undocumented questions

### How to Regenerate

1. **Audit current implementation**:
   ```bash
   # List all modules
   find core/ -name "*.py" -type f | head -20
   
   # Check for new public APIs
   grep -r "def " core/ --include="*.py" | grep -v "__" | grep -v "test"
   ```

2. **Update the appropriate component doc** in `docs/05_system_design/components/`:

   | Component | Document |
   |-----------|----------|
   | Orchestration | `components/SD-ORC.md` |
   | Governance | `components/SD-GOV.md` |
   | Memory | `components/SD-MEM.md` |
   | Intelligence | `components/SD-INT.md` |
   | Tools | `components/SD-TOOLS.md` |
   | Gateway | `components/SD-GW.md` |
   | Products | `components/SD-PROD.md` |

3. **Follow the component doc pattern** (contracts, not narrative):
   - **Scope & Ownership**: What the component owns vs. doesn't own
   - **External Contracts**: Public APIs, schemas, interfaces
   - **Internal State & Lifecycles**: State machines, persistence rules
   - **Governance & Controls**: Enforcement points
   - **Observability**: Trace events emitted, artifacts produced
   - **Tech Spec Coverage**: Link to SD-COVERAGE section
   - **Files**: Source file listing

4. **Update SD-COVERAGE.md** with implementation status for any new requirements.

5. **Update SD-ARCH.md** if architectural boundaries or invariants change.

### Key Principle

> **Write System Design as "implemented contracts + behaviors keyed by Tech Spec IDs", not as narrative explanation.**

This single rule makes diffs possible. Prose rots. Contracts don't.

---

## Quick Reference: Document Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    ENHANCEMENT WORKFLOW                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Add Intent (01_vision_and_intent/intent.md)               │
│         │                                                     │
│         ▼                                                     │
│  2. Derive BRD (02_business_requirements/BRD-*.md)            │
│         │                                                     │
│         ▼                                                     │
│  3. Create TechSpec (03_technical_specifications/*.md)        │
│         │                                                     │
│         ▼                                                     │
│  4. Implement in core/, gateway/, etc.                        │
│         │                                                     │
│         ▼                                                     │
│  5. Write Tests (tests/unit/, integration/, architecture/)    │
│         │                                                     │
│         ▼                                                     │
│  6. Validate (pytest + trace inspection)                      │
│         │                                                     │
│         ▼                                                     │
│  7. Update System Design (05_system_design/*.md)              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## See Also

- [SD-INDEX.md](../05_system_design/SD-INDEX.md) — System design entry point
- [SD-COVERAGE.md](../05_system_design/SD-COVERAGE.md) — Requirement coverage matrix
- [SD-ARCH.md](../05_system_design/SD-ARCH.md) — Architecture boundaries
- [Vision.md](../01_vision_and_intent/Vision.md) — Framework philosophy
- [intent.md](../01_vision_and_intent/intent.md) — Developer intent requirements
- [engineering-standards.md](../05_system_design/engineering-standards.md) — Coding conventions
- [ACC-acceptance.md](../03_technical_specifications/ACC-acceptance.md) — Test acceptance criteria
