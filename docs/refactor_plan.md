# Architecture Review & Simplification Plan

**Repository:** master/  
**Review Date:** 11 January 2026  
**Reviewer:** Principal Architect

---

## A) Architectural Diagnosis

### What Works ✓

| Strength | Evidence |
|----------|----------|
| **Clear core/product separation** | Products only define flows, agents, tools; no orchestration leakage |
| **Strong contract discipline** | Pydantic models at all boundaries; typed envelopes for agent/tool results |
| **Governance centralization** | All policy checks flow through `core/governance/hooks.py` |
| **HITL as first-class primitive** | Pause/resume model is clean; approvals are audited |
| **Deterministic replay design** | Run/step snapshots enable state reconstruction |
| **Model isolation** | LLM calls only via `core/models/router.py` → providers |

### What Is Over-Engineered ⚠️

| Issue | Location | Impact |
|-------|----------|--------|
| **21 contract files** for ~40 models | `core/contracts/` | Cognitive overhead; hard to navigate |
| **9 governance files** with thin gates | `core/governance/` | 5 gate files averaging 60 lines each |
| **Reasoning ladder abstraction** | `core/agents/reasoning_ladder.py` | Unused by any product; adds indirection |
| **Multiple memory backends** | sqlite + in_memory + tracing | Only sqlite used in practice |
| **Tool backend abstraction** | local/mcp/remote | Only local used; remote explicitly disabled |

### What Is Fragile ⚠️

| Issue | Risk |
|-------|------|
| **engine.py (3,083 lines)** | Single point of failure; changes risk regression across all flows |
| **Step type proliferation** | 10+ step types with different handlers complicate testing |
| **Plan execution complexity** | `plan_propose` → `plan_gate` → `plan_execute` chain is intricate |
| **User input ↔ context pack merge** | Multi-step validation/merge logic spread across modules |

### What Is Missing 🔴

| Gap | Impact |
|-----|--------|
| **Auto-discovery for product agents/tools** | Verbose `registry.py` boilerplate |
| **Contract versioning strategy** | No schema evolution plan |
| **Structured error taxonomy** | Errors are data but lack classification (retriable, fatal, user-fixable) |
| **Observability query interface** | Artifacts written but no standard query path |

### Top 5 Root Causes of Complexity

1. **Engine monolith**: `engine.py` accumulated responsibilities incrementally
2. **Contract explosion**: New features added new schema files instead of extending existing ones
3. **Gate proliferation**: Each governance concern got its own module instead of pluggable registry
4. **Abstraction anticipation**: Built for hypothetical needs (remote tools, MCP, vector stores) not actual usage
5. **Missing consolidation cycles**: Technical debt accumulated without dedicated simplification sprints

---

## B) Component Value Audit

### Core Orchestrator

| Component | Purpose | Decision | Action | Risk |
|-----------|---------|----------|--------|------|
| `orchestrator/engine.py` | Flow execution, state management, HITL | **C-SIMPLIFY** | Split into 4-5 focused modules | High |
| `orchestrator/step_executor.py` | Tool/agent step dispatch | **A-CORE** | Keep as-is | — |
| `orchestrator/branching.py` | Branch condition evaluation | **A-CORE** | Keep | — |
| `orchestrator/looping.py` | Loop condition evaluation | **A-CORE** | Keep | — |
| `orchestrator/templating.py` | Param/message rendering | **A-CORE** | Keep | — |
| `orchestrator/hitl.py` | Approval creation/resolution | **B-CONSOLIDATE** | Merge into engine's extracted HITL module | Low |
| `orchestrator/flow_loader.py` | YAML → FlowDef parsing | **A-CORE** | Keep | — |
| `orchestrator/context.py` | RunContext/StepContext | **A-CORE** | Keep | — |
| `orchestrator/state.py` | Status helpers | **B-CONSOLIDATE** | Inline into context.py | Low |
| `orchestrator/error_policy.py` | Retry/backoff definitions | **A-CORE** | Keep | — |

### Core Agents

| Component | Purpose | Decision | Action | Risk |
|-----------|---------|----------|--------|------|
| `agents/base.py` | BaseAgent contract | **A-CORE** | Keep | — |
| `agents/registry.py` | Agent registration/lookup | **C-SIMPLIFY** | Unify with tool registry base class | Low |
| `agents/llm_reasoner.py` | LLM invocation wrapper | **A-CORE** | Keep | — |
| `agents/advisory.py` | Advisory agent pattern | **D-DEPRECATE** | Feature-flag out; remove after audit | Low |
| `agents/reasoning_ladder.py` | Multi-step reasoning | **E-REMOVE** | Delete; no product references | Very low |
| `agents/critic_evaluator.py` | Output critique | **D-DEPRECATE** | Feature-flag; remove if unused after 90 days | Low |

### Core Tools

| Component | Purpose | Decision | Action | Risk |
|-----------|---------|----------|--------|------|
| `tools/base.py` | BaseTool contract | **A-CORE** | Keep | — |
| `tools/registry.py` | Tool registration/lookup | **C-SIMPLIFY** | Unify with agent registry | Low |
| `tools/executor.py` | Tool execution + governance | **A-CORE** | Keep | — |
| `tools/retrieval.py` | Retrieval tool impl | **A-CORE** | Keep | — |
| `tools/backends/local_backend.py` | Local tool execution | **A-CORE** | Keep | — |
| `tools/backends/mcp_backend.py` | MCP protocol backend | **E-REMOVE** | Delete; unused and disabled | Very low |
| `tools/backends/remote_backend.py` | Remote tool calls | **E-REMOVE** | Delete; unused and disabled | Very low |

### Core Governance

| Component | Purpose | Decision | Action | Risk |
|-----------|---------|----------|--------|------|
| `governance/hooks.py` | Governance hook orchestration | **C-SIMPLIFY** | Reduce from 359 lines; extract hook registry | Medium |
| `governance/policies.py` | Policy loading/evaluation | **A-CORE** | Keep | — |
| `governance/security.py` | Redaction, injection checks | **A-CORE** | Keep | — |
| `governance/budgeting.py` | Budget enforcement | **A-CORE** | Keep | — |
| `governance/branch_gate.py` | Branch condition validation | **B-CONSOLIDATE** | Merge into unified `gates.py` | Low |
| `governance/loop_gate.py` | Loop condition validation | **B-CONSOLIDATE** | Merge into `gates.py` | Low |
| `governance/plan_gate.py` | Plan step validation | **B-CONSOLIDATE** | Merge into `gates.py` | Low |
| `governance/critic_gate.py` | Critic output validation | **B-CONSOLIDATE** | Merge into `gates.py` | Low |
| `governance/retrieval_policy.py` | Retrieval source filtering | **B-CONSOLIDATE** | Merge into `gates.py` | Low |

### Core Memory

| Component | Purpose | Decision | Action | Risk |
|-----------|---------|----------|--------|------|
| `memory/base.py` | Memory interface | **A-CORE** | Keep | — |
| `memory/router.py` | Backend routing | **A-CORE** | Keep | — |
| `memory/sqlite_backend.py` | SQLite persistence | **A-CORE** | Keep | — |
| `memory/in_memory.py` | In-memory backend | **C-SIMPLIFY** | Keep for tests; mark as test-only | Low |
| `memory/observability_store.py` | Artifact file storage | **A-CORE** | Keep | — |
| `memory/tracing.py` | Trace event emission | **A-CORE** | Keep | — |

### Core Knowledge

| Component | Purpose | Decision | Action | Risk |
|-----------|---------|----------|--------|------|
| `knowledge/base.py` | Knowledge interface | **A-CORE** | Keep | — |
| `knowledge/retriever.py` | Document retrieval | **A-CORE** | Keep | — |
| `knowledge/context_pack.py` | Context assembly | **A-CORE** | Keep | — |
| `knowledge/context_pack_merge.py` | Context merging | **B-CONSOLIDATE** | Merge into context_pack.py | Low |
| `knowledge/vector_store.py` | Vector DB interface | **D-DEPRECATE** | Feature-flag; evaluate need | Low |
| `knowledge/structured.py` | Structured knowledge | **C-SIMPLIFY** | Audit usage; simplify or remove | Low |

### Contracts Consolidation

| Contract File | Decision | Action |
|---------------|----------|--------|
| `run_schema.py` | **A-CORE** | Keep |
| `flow_schema.py` | **A-CORE** | Keep |
| `agent_schema.py` | **A-CORE** | Keep |
| `tool_schema.py` | **A-CORE** | Keep |
| `user_input_schema.py` | **A-CORE** | Keep |
| `hitl_schema.py` + `question_schema.py` | **B-CONSOLIDATE** | Merge → `interaction_schema.py` |
| `budget_schema.py` | **A-CORE** | Keep |
| `action_plan_schema.py` | **A-CORE** | Keep |
| `plan_schema.py` | **B-CONSOLIDATE** | Merge into action_plan_schema.py |
| `context_pack_schema.py` | **A-CORE** | Keep |
| `evidence_schema.py` | **B-CONSOLIDATE** | Merge into context_pack_schema.py |
| `branch_schema.py` + `loop_schema.py` | **B-CONSOLIDATE** | Merge into flow_schema.py |
| `reasoning_schema.py` | **A-CORE** | Keep |
| `reasoning_ladder_schema.py` | **E-REMOVE** | Delete with reasoning_ladder.py |
| `critic_schema.py` | **D-DEPRECATE** | Remove with critic_evaluator |
| `descriptors_schema.py` | **A-CORE** | Keep |
| `retrieval_schema.py` | **A-CORE** | Keep |
| `advisory_schema.py` | **D-DEPRECATE** | Remove with advisory.py |

**Contract Consolidation Summary:** 21 files → 12 files (43% reduction)

### Gateway

| Component | Decision | Action |
|-----------|----------|--------|
| `api/http_app.py` | **A-CORE** | Keep |
| `api/routes_run.py` | **A-CORE** | Keep |
| `api/deps.py` | **A-CORE** | Keep |
| `cli/main.py` | **A-CORE** | Keep |
| `ui/platform_app.py` (1046 lines) | **C-SIMPLIFY** | Split into page modules |

---

## C) Simplification-Oriented Refactor Plan

### Phase 1: Contract Consolidation (2 weeks)

**Goals:**
- Reduce cognitive load navigating contracts
- Establish clear schema groupings
- Remove unused schemas

**Actions:**

| Remove/Merge | Into | Migration |
|--------------|------|-----------|
| `reasoning_ladder_schema.py` | Delete | No references |
| `critic_schema.py` | Delete or deprecate | Update imports to raise deprecation |
| `advisory_schema.py` | Delete or deprecate | Update imports |
| `hitl_schema.py` + `question_schema.py` | `interaction_schema.py` | Re-export from new location |
| `plan_schema.py` | `action_plan_schema.py` | Re-export |
| `evidence_schema.py` | `context_pack_schema.py` | Re-export |
| `branch_schema.py` + `loop_schema.py` | `flow_schema.py` | Re-export |

**Exit Criteria:**
- Contract file count ≤ 12
- All imports resolve
- All tests pass

---

### Phase 2: Unused Module Removal (1 week)

**Goals:**
- Remove dead code
- Reduce maintenance surface
- Clarify what's actually used

**Actions:**

| Remove | Justification |
|--------|---------------|
| `reasoning_ladder.py` | Zero product usage |
| `mcp_backend.py` | Disabled in executor |
| `remote_backend.py` | Disabled in executor |

| Deprecate (feature-flag) | Review after 90 days |
|--------------------------|---------------------|
| `advisory.py` | No active usage |
| `critic_evaluator.py` | No active usage |
| `vector_store.py` | No active usage |

**Exit Criteria:**
- Deleted modules have no import references
- Deprecated modules raise warnings on import
- CI passes with feature flags off

---

### Phase 3: Engine Decomposition (3 weeks)

**Goals:**
- Break `engine.py` (3,083 lines) into focused modules
- Each module owns one responsibility
- Enable parallel development and safer changes

**Proposed Module Structure:**

```
core/orchestrator/
├── engine.py              # Slim coordinator (~400 lines)
├── run_lifecycle.py       # start_run, resume_run, complete_run (~300 lines)
├── step_runner.py         # step iteration, artifact management (~400 lines)
├── user_input_handler.py  # user_input pause/resume/validation (~250 lines)
├── plan_executor.py       # plan_propose/gate/execute (~350 lines)
├── loop_executor.py       # repeat_until handling (~150 lines)
├── hitl_handler.py        # approval creation/resolution (~200 lines)
├── step_executor.py       # (existing) tool/agent dispatch
├── branching.py           # (existing)
├── looping.py             # (existing)
├── templating.py          # (existing)
├── context.py             # (existing)
├── flow_loader.py         # (existing)
└── error_policy.py        # (existing)
```

**Before → After Responsibility Map:**

| Responsibility | Before (engine.py) | After |
|----------------|-------------------|-------|
| Run start/resume/complete | `_execute_run`, `_resume_from_pending` | `run_lifecycle.py` |
| Step iteration | `_execute_steps`, `_run_step` | `step_runner.py` |
| User input handling | `_pause_for_user_input`, `_handle_user_input_response` | `user_input_handler.py` |
| Plan execution | `_handle_plan_propose`, `_handle_plan_gate`, `_handle_plan_execute` | `plan_executor.py` |
| Loop handling | `_handle_repeat_until` | `loop_executor.py` |
| HITL approvals | `_create_approval`, approval resolution | `hitl_handler.py` |
| Tool/agent dispatch | (already in step_executor.py) | Keep |

**Invariants (must never happen):**
- Extracted modules must not import each other circularly
- `engine.py` remains the only public entry point
- No governance bypass in extracted modules
- Trace events emitted consistently across modules

**Exit Criteria:**
- `engine.py` ≤ 500 lines
- Each extracted module ≤ 400 lines
- All existing tests pass
- New unit tests for each extracted module

---

### Phase 4: Governance Consolidation (1 week)

**Goals:**
- Consolidate 5 gate files into unified module
- Reduce governance module count
- Maintain enforcement rigor

**Actions:**

| Merge | Into | Pattern |
|-------|------|---------|
| `branch_gate.py`, `loop_gate.py`, `plan_gate.py`, `critic_gate.py`, `retrieval_policy.py` | `gates.py` | Registry pattern |

**Resulting Structure:**
```
core/governance/
├── hooks.py        # Hook orchestration (~250 lines)
├── policies.py     # Policy loading
├── security.py     # Redaction, injection
├── budgeting.py    # Budget enforcement
└── gates.py        # All gates (~300 lines)
```

**Exit Criteria:**
- Governance file count: 9 → 5
- All governance tests pass
- Hook behavior unchanged

---

### Phase 5: Registry Unification (1 week)

**Goals:**
- Single generic registry implementation
- Reduce code duplication
- Simplify product registration

**Actions:**

Create `core/utils/registry.py`:
```python
class ComponentRegistry[T]:
    """Generic registry for agents, tools, or other factories."""
    def register(self, name: str, factory: Callable[..., T]) -> None: ...
    def get(self, name: str) -> T: ...
    def list_registered(self) -> list[str]: ...
```

| Refactor | Action |
|----------|--------|
| `agents/registry.py` | Inherit from `ComponentRegistry[BaseAgent]` |
| `tools/registry.py` | Inherit from `ComponentRegistry[BaseTool]` |

**Exit Criteria:**
- Both registries share base implementation
- Registration API unchanged
- Tests pass

---

### Phase 6: UI Modularization (1 week)

**Goals:**
- Split `platform_app.py` (1,046 lines)
- Remove direct core imports
- Establish page-based structure

**Proposed Structure:**
```
gateway/ui/
├── platform_app.py      # App entry, routing (~150 lines)
├── pages/
│   ├── home.py          # Product catalog view
│   ├── run.py           # Run execution view
│   ├── approvals.py     # Pending approvals view
│   └── history.py       # Run history view
├── components/
│   ├── run_card.py      # Reusable run display
│   └── approval_form.py # Approval interaction
└── api_client.py        # HTTP client for API calls
```

**Exit Criteria:**
- `platform_app.py` ≤ 200 lines
- All views work via API calls only
- No direct `core/` imports in UI

---

## D) Target End-State Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Gateway Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────┐   │
│  │   CLI    │  │   API    │  │    UI (Streamlit pages)      │   │
│  │          │  │ FastAPI  │  │    → calls API only          │   │
│  └────┬─────┘  └────┬─────┘  └──────────────────────────────┘   │
└───────┼─────────────┼───────────────────────────────────────────┘
        │             │
        └──────┬──────┘
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestrator Layer                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ engine.py (coordinator)                                   │  │
│  │   → run_lifecycle.py    (start/resume/complete)           │  │
│  │   → step_runner.py      (iteration, artifacts)            │  │
│  │   → user_input_handler  (user_input pause/resume)         │  │
│  │   → hitl_handler        (approvals)                       │  │
│  │   → plan_executor       (action plans)                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                  │
│  ┌──────────────────┐ ┌────────────┐ ┌──────────────────────┐   │
│  │  Step Executor   │ │ Governance │ │       Memory         │   │
│  │  (tool/agent     │ │ (hooks,    │ │  (router, sqlite,    │   │
│  │   dispatch)      │ │  gates,    │ │   observability)     │   │
│  │                  │ │  policies) │ │                      │   │
│  └────────┬─────────┘ └────────────┘ └──────────────────────┘   │
│           │                                                     │
│   ┌───────┴───────┐                                             │
│   ▼               ▼                                             │
│ ┌─────────┐  ┌──────────┐                                       │
│ │ Agents  │  │  Tools   │                                       │
│ │Registry │  │ Executor │                                       │
│ └─────────┘  └──────────┘                                       │
└─────────────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Intelligence Layer                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ LLM Reasoner → Model Router → Providers                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Product Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │  hello_world/   │  │      ade/       │  ...more products     │
│  │  ├─ manifest    │  │  ├─ manifest    │                       │
│  │  ├─ config/     │  │  ├─ config/     │                       │
│  │  ├─ flows/      │  │  ├─ flows/      │                       │
│  │  ├─ agents/     │  │  ├─ agents/     │                       │
│  │  ├─ tools/      │  │  ├─ tools/      │                       │
│  │  └─ registry.py │  │  └─ registry.py │                       │
│  └─────────────────┘  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

### Product Boundary Contract (Minimal)

**Required files:**
```
products/{name}/
├── manifest.yaml      # name, version, default_flow, ui config
├── config/product.yaml # product-specific settings
├── registry.py        # register(registries) → agents + tools
└── flows/{flow}.yaml  # at least one flow
```

**Forbidden:**
- Direct imports from `core/models/providers/`
- Direct imports from `core/memory/*_backend.py`
- Direct tool execution (must go through executor)
- Direct model calls (must go through llm_reasoner)

---

## E) Non-Goals (Explicit)

| Do NOT | Reason |
|--------|--------|
| Rewrite the orchestrator | Extraction preserves working code; rewrite risks regression |
| Replace FastAPI | Current API layer is clean; no benefit to switching |
| Replace Streamlit | Works for internal/demo UI; custom UI is additive |
| Add GraphQL | REST is sufficient; GraphQL adds complexity |
| Add event sourcing | Current snapshot model works; event sourcing is overkill |
| Add microservices | Single deployable is a strength; splitting adds operational cost |

---

## F) Decision Principles ("Architectural Laws")

### When to Add an Abstraction

✓ Add when:
- Multiple products need the same capability
- External dependency isolation is required
- Contract enforcement is needed at a boundary

✗ Do NOT add when:
- Only one use case exists today
- "We might need it later" is the only justification

### When to Delete Instead of Extend

✓ Delete when:
- Module has zero imports after grep search
- Feature flag has been off for 90+ days
- Complexity cost exceeds value delivered

### Control vs Intelligence

| Trust Model (Reasoning) | Enforce Determinism (Execution) |
|-------------------------|--------------------------------|
| Interpreting user intent | Tool invocation |
| Planning action sequences | Step ordering |
| Summarizing results | Artifact persistence |
| Generating hypotheses | Approval state transitions |

**Pattern: "Reason, then Execute"**
1. Agent reasons → produces structured decision (JSON)
2. Orchestrator validates against governance
3. Orchestrator executes deterministically
4. All execution is traced and auditable

### Product Isolation Rules

1. Products may only import from `core.agents.base`, `core.tools.base`, `core.contracts.*`, `core.utils.product_loader`
2. No cross-product imports
3. All agents/tools registered explicitly in `registry.py`
4. Architecture tests validate import boundaries

---

## G) Summary: Simplification ROI

| Phase | Effort | Complexity Reduction | Risk |
|-------|--------|---------------------|------|
| 1. Contract Consolidation | 2 weeks | 21 → 12 files (43%) | Low |
| 2. Unused Module Removal | 1 week | -5 modules | Very Low |
| 3. Engine Decomposition | 3 weeks | 3083 → ~500 lines in main file | Medium |
| 4. Governance Consolidation | 1 week | 9 → 5 files | Low |
| 5. Registry Unification | 1 week | -~100 lines duplication | Low |
| 6. UI Modularization | 1 week | 1046 → ~150 lines in main file | Low |

**Total: ~9 weeks for 40-50% reduction in surface complexity while preserving all capabilities.**
