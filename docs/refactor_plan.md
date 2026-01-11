# Architecture Review & Simplification Plan

**Repository:** master/  
**Review Date:** 11 January 2026  
**Reviewer:** Principal Architect

---

## Guiding Constraints (Non-Negotiable)

| Constraint | Implementation Implication |
|------------|---------------------------|
| **Orchestrator remains control plane** | Agents never decide control flow; they only propose |
| **Tools only via ToolExecutor** | All tool calls routed through core executor |
| **LLM calls centralized** | Only via LLM reasoner/router path |
| **Auditability mandatory** | Every feature emits structured trace + artifacts |
| **Enterprise-safe** | Side-effects require HITL; read-only loops allowed under budgets |

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
| `agents/advisory.py` | Advisory agent pattern | **C-SIMPLIFY** | Refactor into bounded advisory agents (selector, gap-finder, summarizer) | Medium |
| `agents/reasoning_ladder.py` | Multi-step reasoning | **C-SIMPLIFY** | Refactor into bounded interpret→propose→select pattern | Medium |
| `agents/critic_evaluator.py` | Output critique | **C-SIMPLIFY** | Refactor into bounded critic with structured recommendations | Medium |

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
| `reasoning_ladder_schema.py` | **C-SIMPLIFY** | Refactor for bounded multi-pass reasoning |
| `critic_schema.py` | **C-SIMPLIFY** | Refactor for structured recommendations |
| `descriptors_schema.py` | **A-CORE** | Expand with capability tags, cost hints, sensitivity class |
| `retrieval_schema.py` | **A-CORE** | Keep |
| `advisory_schema.py` | **C-SIMPLIFY** | Refactor for bounded advisory outputs |

**Contract Consolidation Summary:** 21 files → 14 files (33% reduction)

Note: Reasoning ladder, critic, and advisory schemas retained and simplified for intelligence capabilities rather than removed.

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

### Phase 0: Baseline & Safety Net (1 week)

**Goals:**
- Lock current behavior before touching anything
- Create acceptance tests that prevent regressions
- Enable confident refactoring

**Deliverables:**
- Tests that assert:
  - Deterministic step transitions (same input → same output)
  - Pause/resume correctness for HITL and user_input
  - Governance denies disallowed tools/models
  - Trace emission for every tool/model call
  - Proposal steps do not execute tools directly

**Exit Criteria:**
- All acceptance tests pass on current codebase
- Tests added to CI as blocking gates

---

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

**Note:** `advisory.py`, `critic_evaluator.py`, and `vector_store.py` previously marked for deprecation are now retained for intelligence capabilities (see Phase 7-9).

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

### Phase 7: Enhanced Descriptors & Evidence Model (2 weeks)

**Goals:**
- Build semantic catalog for intelligent tool/agent selection
- Standardize evidence-based reasoning with provenance

**Deliverables:**

**7.1 Expand ToolDescriptor & AgentDescriptor:**
```python
class ToolDescriptor:
    name: str
    description: str
    capabilities: list[str]  # semantic tags
    input_schema_ref: str
    output_schema_ref: str
    read_only: bool
    side_effect: bool
    sensitivity_class: str  # "public" | "internal" | "confidential" | "restricted"
    cost_hint: str  # "low" | "medium" | "high"

class AgentDescriptor:
    name: str
    purpose: str
    capabilities: list[str]
    input_schema_ref: str
    output_schema_ref: str
    cost_hint: str
    allowed_step_types: list[str]  # advisory only
```

**7.2 Introduce EvidenceItem model:**
```python
class EvidenceItem:
    id: str
    type: str  # "table" | "document" | "text" | "metric"
    source: str  # tool name + uri
    timestamp: datetime
    confidence: float
    content_ref: str  # artifact reference
    summary: str
    provenance: dict  # filters, params used
```

**7.3 Update ToolResult contract:**
- Add `evidence: list[EvidenceItem]` field
- Compatibility shim: existing tools auto-wrap output into minimal EvidenceItem

**Exit Criteria:**
- Every registered tool/agent has complete descriptor
- Every tool run yields at least one EvidenceItem
- Trace contains evidence IDs and source mapping

---

### Phase 8: Context Pack Builder (2 weeks)

**Goals:**
- Curate LLM inputs deterministically
- Enable auditable, reproducible reasoning

**Deliverables:**

**8.1 ContextPack schema:**
```python
class ContextPack:
    question: str
    tables_summary: list[TableSummary]  # stats, key rows, column profiles
    documents_summary: list[DocSummary]  # excerpts, metadata
    evidence_index: list[str]  # EvidenceItem references
    assumptions: list[str]  # system-applied
    limits: dict  # data coverage, sampling info
```

**8.2 ContextPackBuilder utility:**
- Takes EvidenceItems + question
- Generates context pack deterministically (no LLM)
- Stores as artifact with hash for reproducibility

**Exit Criteria:**
- Same inputs → same context pack (hash-verified)
- Context pack contains provenance links to all evidence
- LLM calls receive ContextPack, not raw blobs

---

### Phase 9: Bounded Reasoning & Critic Pattern (3 weeks)

**Goals:**
- Enable multi-pass reasoning with governance
- Add critic for quality/completeness checks
- Enforce reasoning budgets

**Deliverables:**

**9.1 ReasoningLadder refactor:**
```python
class ReasoningLadderOutput:
    interpret: InterpretResult  # intent, entities, constraints
    propose: ProposeResult      # candidates, tool_candidates, agent_candidates
    select: SelectResult        # chosen, rationale, evidence_refs
    confidence: float
    assumptions: list[str]
    unknowns: list[str]
```

Each pass:
- Uses same ContextPack
- Yields structured output
- Emits trace events
- Bounded by config budgets

**9.2 Bounded Critic refactor:**
```python
class CriticResult:
    completeness_score: float
    inconsistency_flags: list[str]
    missing_evidence: list[str]
    confidence_adjustment: float
    recommended_action: str  # "NONE" | "USER_INPUT" | "HITL" | "FETCH_MORE_EVIDENCE"
```

Rules:
- Critic cannot call tools; only analyzes artifacts
- Critic cannot produce "execute tool X"; only recommendations
- Orchestrator gates all recommendations via policy

**9.3 Reasoning Budgets (expand existing budgeting.py):**
```python
class ReasoningBudget:
    max_passes: int
    max_tool_calls: int
    max_parallel_calls: int
    max_total_cost_units: float
    max_latency_bucket: str
    policy_by_sensitivity: dict
```

Enforcement:
- Exceeding budgets → deterministic stop or HITL escalation
- No runaway loops

**Exit Criteria:**
- Reasoning ladder bounded by budgets
- Critic output validates; failures are safe
- Budget violations produce deterministic, traceable outcomes

---

### Phase 10: Parallel Read-Only Tool Execution (1 week)

**Goals:**
- Enable efficient evidence gathering
- Maintain determinism and auditability

**Deliverables:**

**10.1 Add TOOL_BATCH step type:**
```yaml
- id: gather_evidence
  type: tool_batch
  tools:
    - tool_a
    - tool_b
    - tool_c
  parallel: true
```

Rules:
- All tools must have `read_only=true` and `side_effect=false`
- Merge strategy: deterministic ordering by tool name
- EvidenceItems appended with stable IDs

**Exit Criteria:**
- Batch rejects any tool not marked read_only
- Deterministic merge order (reproducible)
- Trace contains each tool call as separate event

---

### Phase 11: Missing-Info Question Loop (1 week)

**Goals:**
- Structured information gathering from users
- Validated, schema-driven input

**Deliverables:**

**11.1 QuestionSet artifact:**
```python
class QuestionSet:
    questions: list[Question]
    required_fields: list[str]
    validation_schema: dict
```

**11.2 Flow pattern:**
```yaml
- id: check_completeness
  type: agent
  agent: critic

- id: ask_questions
  type: user_input
  when: "{{artifacts.critic_result.recommended_action}} == 'USER_INPUT'"
  params:
    question_set: "{{artifacts.question_set}}"
```

Rules:
- Invalid user input does not resume flow
- Resume merges validated answers into ContextPack deterministically

**Exit Criteria:**
- User input validated against schema before resume
- Answers appear in ContextPack with provenance

---

### Phase 12: Retrieval Augmentation (1 week)

**Goals:**
- Enable approved-evidence-only retrieval
- Support cross-run learning (within governance)

**Deliverables:**

**12.1 Retrieval tool enhancement:**
- Query prior RunRecords/TraceEvents
- Query approved knowledge sources (per-product whitelist)
- Output as EvidenceItems with citations

**12.2 Policy enforcement:**
```yaml
retrieval_policy:
  allowed_sources:
    - "runs:current_product"
    - "knowledge:approved_docs"
  blocked_sources:
    - "runs:other_products"
```

**Exit Criteria:**
- Retrieval cannot pull from disallowed sources
- Every retrieved item has provenance (run_id, timestamp, artifact_ref)

---

### Phase 13: Advisory Agent Set (2 weeks)

**Goals:**
- Structured intelligence without control-flow authority
- Bank-safe advisory patterns

**Deliverables:**

**13.1 Refactor advisory.py into bounded agents:**

| Agent | Purpose | Output |
|-------|---------|--------|
| `ToolSelector` | Recommend tools based on descriptors + context | `ToolSelectionResult` |
| `AgentSelector` | Recommend agents for subtasks | `AgentSelectionResult` |
| `GapFinder` | Identify missing evidence | `GapAnalysisResult` |
| `Summarizer` | Condense evidence into narrative | `SummaryResult` |
| `RiskExplainer` | Explain confidence/risk factors | `RiskExplanationResult` |

Rules:
- None can invoke ToolExecutor directly
- All outputs are structured; no free-form control
- Orchestrator uses them only via proposal→gate pattern

**Exit Criteria:**
- Advisory agents cannot call tools
- All outputs validate against schemas
- Orchestrator gates all recommendations

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
| Allow agents to control flow | Agents propose; orchestrator decides |
| Allow tools to call tools | Single-level execution only |
| Unbounded loops | All loops must have max_iters and budget caps |
| Raw LLM context | LLM must receive curated ContextPack with evidence |

---

## E.1) Intelligence Upgrade Reconciliation

The following changes from the "Master v2 Intelligence Upgrade Plan" were reviewed and incorporated:

| Change # | Description | Decision | Rationale |
|----------|-------------|----------|-----------|
| 1 | Tool/agent selection with metadata | ✓ Incorporated | Phase 7 + 13: Enables intelligent selection without bypassing governance |
| 2 | Loops and conditional branching | ✓ Already exists | Branching/looping already in orchestrator; enhanced with budget enforcement |
| 3 | Multi-pass reasoning ladder | ✓ Incorporated | Phase 9: Refactored from "remove" to "simplify with bounds" |
| 4 | Proposal → Gate → Execute | ✓ Already exists | plan_propose/gate/execute pattern already implemented |
| 5 | Context Pack Builder | ✓ Incorporated | Phase 8: Critical for auditable, reproducible LLM reasoning |
| 6 | Bounded Critic | ✓ Incorporated | Phase 9: Refactored from "deprecate" to "simplify with bounds" |
| 7 | Reduce schema overuse | ✓ Incorporated | Phase 1: Keep Pydantic at boundaries, lighter types internally |
| 8 | Enhanced descriptors | ✓ Incorporated | Phase 7: Foundation for intelligent selection |
| 9 | Missing-info question loop | ✓ Incorporated | Phase 11: Structured user input gathering |
| 10 | Parallel read-only tools | ✓ Incorporated | Phase 10: New TOOL_BATCH step type |
| 11 | Retrieval augmentation | ✓ Incorporated | Phase 12: Approved-source-only retrieval |
| 12 | Reasoning budgets | ✓ Incorporated | Phase 9: Expanded beyond token limits |
| 13 | Evidence model | ✓ Incorporated | Phase 7: EvidenceItem with provenance |
| 14 | Advisory agent set | ✓ Incorporated | Phase 13: Bounded advisory agents |

**Key Reconciliations:**
- `reasoning_ladder.py`: Changed from E-REMOVE to C-SIMPLIFY (bounded multi-pass pattern is valuable)
- `critic_evaluator.py`: Changed from D-DEPRECATE to C-SIMPLIFY (bounded critic adds value)
- `advisory.py`: Changed from D-DEPRECATE to C-SIMPLIFY (structured advisory agents are useful)

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
| Selecting tools/agents | Policy enforcement |
| Identifying gaps | Budget limits |
| Explaining risks | HITL triggers |

**Pattern: "Reason, then Execute"**
1. Agent reasons → produces structured decision (JSON)
2. Decision stored as proposal artifact
3. Gate validates proposal against governance (allowlists, budgets, sensitivity)
4. Orchestrator executes only approved steps deterministically
5. All execution is traced and auditable

**Pattern: "Bounded Multi-Pass Reasoning"**
1. Interpret pass → structured intent
2. Propose pass → candidates with evidence refs
3. Select pass → chosen action with rationale
4. Each pass bounded by budget (max passes, cost units)
5. Exceeding budget → deterministic stop or HITL escalation

**Pattern: "Evidence-Based Context"**
1. Tools return EvidenceItems with provenance
2. ContextPackBuilder curates evidence deterministically
3. LLM receives ContextPack, not raw data
4. Reasoning cites evidence by ID
5. Audit trail links decisions to source evidence

### Product Isolation Rules

1. Products may only import from `core.agents.base`, `core.tools.base`, `core.contracts.*`, `core.utils.product_loader`
2. No cross-product imports
3. All agents/tools registered explicitly in `registry.py`
4. Architecture tests validate import boundaries

---

## G) Summary: Simplification ROI

### Simplification Phases (Weeks 1-10)

| Phase | Effort | Complexity Reduction | Risk |
|-------|--------|---------------------|------|
| 0. Baseline & Safety Net | 1 week | Acceptance test foundation | Very Low |
| 1. Contract Consolidation | 2 weeks | 21 → 14 files (33%) | Low |
| 2. Unused Module Removal | 1 week | -3 modules | Very Low |
| 3. Engine Decomposition | 3 weeks | 3083 → ~500 lines in main file | Medium |
| 4. Governance Consolidation | 1 week | 9 → 5 files | Low |
| 5. Registry Unification | 1 week | -~100 lines duplication | Low |
| 6. UI Modularization | 1 week | 1046 → ~150 lines in main file | Low |

### Intelligence Enhancement Phases (Weeks 11-22)

| Phase | Effort | Capability Added | Risk |
|-------|--------|-----------------|------|
| 7. Descriptors & Evidence | 2 weeks | Semantic catalog + provenance | Medium |
| 8. Context Pack Builder | 2 weeks | Deterministic LLM input curation | Low |
| 9. Bounded Reasoning & Critic | 3 weeks | Multi-pass reasoning + quality checks | Medium |
| 10. Parallel Tool Execution | 1 week | Efficient read-only batching | Low |
| 11. Missing-Info Loop | 1 week | Structured user input gathering | Low |
| 12. Retrieval Augmentation | 1 week | Approved cross-run learning | Medium |
| 13. Advisory Agent Set | 2 weeks | Structured intelligence layer | Medium |

### Dependency Map

```
Phase 0 (baseline)
    │
    ├── Phase 1 (contracts) ─────────────────────┐
    │       │                                    │
    │       └── Phase 7 (descriptors/evidence) ──┼── Phase 8 (context pack)
    │                   │                        │           │
    ├── Phase 2 (removal)                        │           └── Phase 9 (reasoning/critic)
    │                                            │                   │
    ├── Phase 3 (engine) ────────────────────────┼── Phase 10 (parallel tools)
    │       │                                    │           │
    │       └── Phase 11 (question loop) ────────┘           │
    │                                                        │
    ├── Phase 4 (governance) ── Phase 12 (retrieval) ────────┘
    │
    ├── Phase 5 (registry)
    │
    ├── Phase 6 (UI)
    │
    └── Phase 13 (advisory agents) ← depends on 7, 8, 9
```

**Total: ~22 weeks for simplification + intelligence upgrade while preserving governance and auditability.**
