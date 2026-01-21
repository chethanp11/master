# ADE Clarification Records

> **Purpose**: Document enforcement decisions for requirements that cannot be fully automated in code.  
> **Created**: 2026-01-21  
> **Related Plan**: imp_plan.md v1.2  

---

## IMP-001: Objectives Enforcement Clarification

**Tech Spec IDs**: TS-IO-OBJ-001 through TS-IO-OBJ-008 (mapped from OBJ-001..OBJ-007 plus OBJ-008)

### Objective Enforcement Classification

| Objective ID | Tech Spec ID | Requirement Summary | Enforcement Type | Enforcement Mechanism |
|--------------|--------------|---------------------|------------------|----------------------|
| OBJ-001 | TS-IO-OBJ-001 | Include evidence references in 100% of outputs | **Runtime + Test** | Schema validation (`evidence_refs` required field); Unit test asserting non-empty evidence refs |
| OBJ-002 | TS-IO-OBJ-002 | Identical inputs → identical outputs | **Test** | Determinism test: `f(x) == f(x)` for all functions; CI/CD check for no `random` imports without seed |
| OBJ-003 | TS-IO-OBJ-003 | Explicit user approval for all plans | **Runtime (Flow)** | HITL step in flow YAML with `required: true`; Orchestrator enforces pause at approval step |
| OBJ-004 | TS-IO-OBJ-004 | Include confidence_level, assumptions, limitations in outputs | **Runtime + Test** | Schema required fields; Unit tests validating presence |
| OBJ-005 | TS-IO-OBJ-005 | Report within 5 minutes | **Reporting** | Tracing via `core.memory.tracing.Tracer`; Metrics dashboard (not blocking); Warning log if exceeded |
| OBJ-006 | TS-IO-OBJ-006 | Support at least 4 chart types | **Test** | Unit test for `ChartType` enum containing bar, line, area, scatter |
| OBJ-007 | TS-IO-OBJ-007 | Allow toggle for hypothesis checks | **Runtime (Config)** | `viz_preferences.include_hypothesis_checks: bool` in user input; Conditional tool execution |
| OBJ-008 | TS-IO-OBJ-008 | Objectives via config, not hardcoded | **Test + Review** | Config file `goals.yaml` present; No hardcoded objectives in agent code; Code review policy |

### Decision Rationale

1. **OBJ-001, OBJ-003, OBJ-004, OBJ-007**: These are structural requirements that can be enforced at runtime via schema validation and flow structure. No additional implementation needed beyond existing schema definitions.

2. **OBJ-002, OBJ-006, OBJ-008**: These are behavioral/architectural constraints best enforced through automated tests and CI checks. Determinism is verified by running the same input twice and comparing outputs.

3. **OBJ-005**: Performance requirement cannot block execution. Implemented as observability/reporting with warnings. Not a hard gate.

### Acceptance Confirmation

- ✅ Each objective has a defined enforcement mechanism (test, runtime, reporting, or review).
- ✅ Runtime enforcement is structural (schema, flow YAML) and does not require additional code changes.
- ✅ Test enforcement will be validated by running existing test suite (`pytest products/ade/tests/`).

---

## IMP-016: Alignment/Reliance/No-Learning Constraints Clarification

**Tech Spec IDs**: 
- TS-AGENT-FRI-001 through TS-AGENT-FRI-005 (Framework Alignment)
- TS-AGENT-NRL-001 through TS-AGENT-NRL-004 (No Runtime Learning)

### Constraint Enforcement Classification

| Constraint ID | Tech Spec ID | Requirement Summary | Enforcement Type | Enforcement Mechanism |
|---------------|--------------|---------------------|------------------|----------------------|
| FRI-001 | TS-AGENT-FRI-001 | Use `core.agents.reasoning_ladder` interfaces | **Static Analysis + Review** | CI grep check for prohibited imports; Code review policy |
| FRI-002 | TS-AGENT-FRI-002 | No re-implementation of core modules | **Static Analysis + Review** | CI check: no duplicate logic in `products/ade/`; Code review |
| FRI-003 | TS-AGENT-FRI-003 | No bypass of governance hooks | **Runtime** | Agent base class enforces hooks; Direct instantiation prohibited (abstract base) |
| FRI-004 | TS-AGENT-FRI-004 | Log framework gaps in FRAMEWORK_GAPS.md | **Documentation** | Manual process; File exists and is maintained |
| FRI-005 | TS-AGENT-FRI-005 | Escalate gaps via `escalate_framework_gap()` | **Runtime** | Call `core.governance.hooks.escalate_framework_gap()` when gaps detected |
| NRL-001 | TS-AGENT-NRL-001 | No runtime behavior modification | **Static Analysis + Test** | No file writes outside `staging/output/`; No DB connections in agents; Stateless test |
| NRL-002 | TS-AGENT-NRL-002 | No persistent learned patterns | **Static Analysis + Test** | No ML model files; No pattern caches; Fresh state verified in tests |
| NRL-003 | TS-AGENT-NRL-003 | Evolution follows BRD lifecycle | **Process/Review** | Version control; PR review required; BRD-first policy documented |
| NRL-004 | TS-AGENT-NRL-004 | Identical inputs → identical outputs | **Test** | Same as OBJ-002; Determinism test suite |

### Decision Rationale

1. **FRI-001, FRI-002, NRL-001, NRL-002**: Static analysis is the primary enforcement mechanism. CI will include grep-based checks to detect prohibited patterns (e.g., importing `core.orchestrator` and re-defining its logic, writing to files outside output directory, importing ML libraries for runtime learning).

2. **FRI-003, FRI-005**: Runtime enforcement via base class design. All agents must extend `AgentBase` which calls governance hooks automatically. Gap escalation is a method call; presence verified by integration tests.

3. **FRI-004**: Documentation requirement. Verified by file existence check in CI: `test -f products/ade/docs/FRAMEWORK_GAPS.md`.

4. **NRL-003**: Process requirement. Enforced via PR workflow and documented policy. Cannot be automated beyond requiring BRD linkage in PR descriptions.

5. **NRL-004**: Same as OBJ-002. Determinism test already covers this.

### Static Analysis Checks to Implement (IMP-021)

The following checks will be added as part of IMP-021 (Phase 7):

```bash
# No network imports in tools
grep -r "import requests\|import urllib\|import httpx" products/ade/tools/ → must be empty

# No ML model training
grep -r "\.fit\(\|\.train\(\|model\.save\(" products/ade/ → must be empty

# No file writes outside staging/output
# Verified by unit tests mocking file system
```

### Acceptance Confirmation

- ✅ Each alignment/reliance/no-learning constraint has a defined enforcement mechanism.
- ✅ Runtime enforcement is structural (base class design, hook calls).
- ✅ Static analysis checks are documented and will be implemented in IMP-021.
- ✅ Process/documentation requirements are acknowledged as review-based.

---

## Summary

| IMP Unit | Clarification Complete | Enforcement Mechanisms Defined | Linked Tech Spec IDs |
|----------|----------------------|-------------------------------|---------------------|
| IMP-001 | ✅ Yes | ✅ 8 objectives classified | TS-IO-OBJ-001..008 |
| IMP-016 | ✅ Yes | ✅ 10 constraints classified | TS-AGENT-FRI-001..005, TS-AGENT-NRL-001..004 |

---

## Linked Artifacts

- **Implementation Plan**: `products/ade/docs/03_implementation_plan/imp_plan.md`
- **Tech Spec (I/O)**: `products/ade/docs/02_techspec/TS-inputs-outputs.md`
- **Tech Spec (Agents)**: `products/ade/docs/02_techspec/TS-agents.md`
- **FRAMEWORK_GAPS.md**: `products/ade/docs/FRAMEWORK_GAPS.md` (to be created if not exists)
