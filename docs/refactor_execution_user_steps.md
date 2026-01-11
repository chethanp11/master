# Refactor Execution Guide

**Purpose:** Step-by-step instructions for executing [refactor_plan.md](refactor_plan.md) using Claude Opus 4.5 in VS Code Agent Mode.

**Prerequisites:**
- VS Code with GitHub Copilot (Agent Mode enabled)
- All tests passing before starting
- Git branch created for refactoring: `git checkout -b refactor/master-v2`
- Commit after each batch completes successfully

---

## Execution Strategy

### Why Not All At Once?

Implementing all 17 phases in a single prompt would fail because:
1. **Context limits** - Too much code to generate/modify in one session
2. **Risk compounding** - One error cascades into later phases
3. **Verification gaps** - Can't validate intermediate states
4. **Rollback difficulty** - Hard to identify where things broke

### Recommended Approach: 6 Execution Batches

| Batch | Phases | Risk | Duration | Commit Point |
|-------|--------|------|----------|--------------|
| **A** | 0 (Baseline Tests) | Very Low | 1 session | ✓ |
| **B** | 1-2 (Contracts + Removal) | Low | 1-2 sessions | ✓ |
| **C** | 3 (Engine Decomposition) | High | 2-3 sessions | ✓ |
| **D** | 4-6 (Governance, Registry, UI) | Low | 1-2 sessions | ✓ |
| **E** | 7-13 (Intelligence Enhancement) | Medium | 3-4 sessions | ✓ |
| **F** | 14-17 (Product + Tests) | Low | 1-2 sessions | ✓ |

---

## Batch A: Baseline & Safety Net (Phase 0)

### Purpose
Lock in current behavior before any changes. This creates the safety net for all subsequent batches.

### Pre-Prompt Checklist
- [ ] All existing tests pass: `pytest tests/ -v`
- [ ] On clean branch: `git status`

### Prompt 1: Create Acceptance Tests

```
I'm implementing Phase 0 of refactor_plan.md - Baseline & Safety Net.

Create acceptance tests that lock in current platform behavior. These tests must pass BEFORE and AFTER all refactoring.

Create these test files:

1. `tests/acceptance_intelligence/test_determinism.py`:
   - test_same_input_produces_same_output: Run hello_world flow twice with identical input, assert identical artifacts
   - test_step_transitions_are_deterministic: Assert step order matches flow definition
   - test_resume_produces_consistent_result: Pause at HITL, resume, verify final state matches expected

2. `tests/acceptance_intelligence/test_governance_baseline.py`:
   - test_governance_denies_blocked_tools: Configure blocked tool, assert rejection
   - test_governance_denies_blocked_models: Configure blocked model, assert rejection
   - test_proposal_steps_do_not_execute_tools: Run plan_proposal step, verify no tool execution in trace

3. `tests/acceptance_intelligence/test_pause_resume_baseline.py`:
   - test_hitl_pauses_correctly: Assert run status is PENDING_HUMAN after HITL step
   - test_user_input_pauses_correctly: Assert run status is PENDING_USER_INPUT
   - test_resume_is_idempotent: Resume twice, assert same final state

4. `tests/acceptance_intelligence/test_trace_baseline.py`:
   - test_every_tool_call_traced: Run flow with tools, assert trace events for each
   - test_every_model_call_traced: Run flow with LLM, assert trace events
   - test_trace_contains_required_fields: Assert run_id, step_id, timestamp, event_type present

Use existing test fixtures from tests/conftest.py. Use InMemoryBackend and fake providers for determinism.
```

### Verification
```bash
# Run new tests
pytest tests/acceptance_intelligence/ -v

# Run all tests to ensure no regressions
pytest tests/ -v

# Commit if passing
git add tests/acceptance_intelligence/
git commit -m "Phase 0: Add baseline acceptance tests for refactoring safety net"
```

---

## Batch B: Contract Consolidation + Module Removal (Phases 1-2)

### Purpose
Reduce contract file count and remove dead code. Low risk, high clarity improvement.

### Pre-Prompt Checklist
- [ ] Batch A complete and committed
- [ ] All tests passing

### Prompt 2: Contract Consolidation

```
I'm implementing Phase 1 of refactor_plan.md - Contract Consolidation.

Consolidate contract files as specified:

1. Merge `hitl_schema.py` + `question_schema.py` → `interaction_schema.py`:
   - Create core/contracts/interaction_schema.py with all models from both files
   - Add re-exports in original files with deprecation warnings
   - Update all imports across codebase to use new location

2. Merge `plan_schema.py` into `action_plan_schema.py`:
   - Move PlanProposal and related models into action_plan_schema.py
   - Add re-exports in plan_schema.py with deprecation warning
   - Update imports

3. Merge `evidence_schema.py` into `context_pack_schema.py`:
   - Move Evidence, Citation models into context_pack_schema.py
   - Add re-exports with deprecation warning
   - Update imports

4. Merge `branch_schema.py` + `loop_schema.py` into `flow_schema.py`:
   - Move BranchSpec, BranchResult, LoopSpec, LoopResult into flow_schema.py
   - Add re-exports with deprecation warnings
   - Update imports

For deprecation warnings, use this pattern:
```python
import warnings
warnings.warn(
    "Importing from {old_module} is deprecated. Use {new_module} instead.",
    DeprecationWarning,
    stacklevel=2
)
```

Run tests after each merge to catch import errors early.
```

### Prompt 3: Unused Module Removal

```
I'm implementing Phase 2 of refactor_plan.md - Unused Module Removal.

Remove these unused modules:

1. Delete `core/tools/backends/mcp_backend.py`:
   - First verify no imports: grep for "mcp_backend" across codebase
   - Remove from core/tools/backends/__init__.py if exported
   - Delete the file

2. Delete `core/tools/backends/remote_backend.py`:
   - Verify no imports
   - Remove from __init__.py
   - Delete the file

3. Update `core/tools/backends/__init__.py`:
   - Remove any references to deleted backends
   - Keep only local_backend exports

Do NOT delete advisory.py, critic_evaluator.py, reasoning_ladder.py, or vector_store.py - these are retained for intelligence phases.

Run tests after deletions to verify nothing breaks.
```

### Verification
```bash
# Check for import errors
python -c "from core.contracts import *"
python -c "from core.tools.backends import *"

# Run all tests
pytest tests/ -v

# Commit
git add -A
git commit -m "Phases 1-2: Contract consolidation and unused module removal"
```

---

## Batch C: Engine Decomposition (Phase 3)

### Purpose
Break the 3,083-line engine.py into focused modules. HIGH RISK - do incrementally.

### Pre-Prompt Checklist
- [ ] Batches A-B complete and committed
- [ ] All tests passing
- [ ] Read engine.py to understand current structure

### Prompt 4: Extract Run Lifecycle

```
I'm implementing Phase 3 of refactor_plan.md - Engine Decomposition (Part 1 of 4).

Extract run lifecycle management from engine.py into run_lifecycle.py.

Create `core/orchestrator/run_lifecycle.py`:

1. Move these responsibilities from engine.py:
   - Run initialization logic
   - Run completion logic  
   - Run status transitions
   - Run persistence calls

2. The new module should contain:
   - `start_run(engine, flow_def, payload) -> RunRecord`
   - `complete_run(engine, run_record, status, output) -> RunRecord`
   - `fail_run(engine, run_record, error) -> RunRecord`
   - Helper functions for status transitions

3. Update engine.py to import and use these functions.

4. Keep engine.py as the public interface - run_lifecycle.py is internal.

Constraints:
- No circular imports
- All trace events must still emit correctly
- All governance hooks must still be called
- Run tests after extraction

Target: engine.py should lose ~300 lines from this extraction.
```

### Prompt 5: Extract User Input Handler

```
I'm implementing Phase 3 of refactor_plan.md - Engine Decomposition (Part 2 of 4).

Extract user input handling from engine.py into user_input_handler.py.

Create `core/orchestrator/user_input_handler.py`:

1. Move these responsibilities from engine.py:
   - User input step detection and pause
   - User input validation
   - User input response handling
   - Context pack merging with user answers

2. The new module should contain:
   - `pause_for_user_input(engine, run, step, request) -> RunRecord`
   - `validate_user_input(request, response) -> ValidationResult`
   - `apply_user_input(engine, run, response) -> RunRecord`
   - `merge_into_context_pack(context_pack, answers) -> ContextPack`

3. Update engine.py to import and delegate to these functions.

4. Ensure PENDING_USER_INPUT status transitions work correctly.

Target: engine.py should lose ~250 lines from this extraction.
```

### Prompt 6: Extract Plan Executor

```
I'm implementing Phase 3 of refactor_plan.md - Engine Decomposition (Part 3 of 4).

Extract plan execution from engine.py into plan_executor.py.

Create `core/orchestrator/plan_executor.py`:

1. Move these responsibilities from engine.py:
   - plan_propose step handling
   - plan_gate step handling
   - plan_execute step handling
   - Action plan artifact management

2. The new module should contain:
   - `handle_plan_propose(engine, run, step) -> StepResult`
   - `handle_plan_gate(engine, run, step, plan) -> GateResult`
   - `handle_plan_execute(engine, run, step, approved_plan) -> StepResult`
   - Helper functions for plan validation

3. Update engine.py to delegate plan step types to these functions.

4. Ensure HITL triggers for plan approval still work.

Target: engine.py should lose ~350 lines from this extraction.
```

### Prompt 7: Extract HITL Handler + Final Cleanup

```
I'm implementing Phase 3 of refactor_plan.md - Engine Decomposition (Part 4 of 4).

Extract HITL handling and clean up engine.py.

1. Create `core/orchestrator/hitl_handler.py`:
   - Move approval creation, resolution, and state management
   - `create_approval(engine, run, step, context) -> ApprovalRecord`
   - `resolve_approval(engine, run, approval_id, decision) -> RunRecord`
   - `check_pending_approvals(engine, run) -> list[ApprovalRecord]`

2. Create `core/orchestrator/loop_executor.py`:
   - Move repeat_until handling
   - `handle_repeat_until(engine, run, step) -> StepResult`
   - `evaluate_stop_condition(context, condition) -> bool`

3. Clean up engine.py:
   - Should now be ~400-500 lines
   - Should only contain:
     - OrchestratorEngine class definition
     - High-level orchestration methods (run_flow, resume_run)
     - Delegation to extracted modules
   - Remove any dead code or unused private methods

4. Update `core/orchestrator/__init__.py` to export only OrchestratorEngine.

Run full test suite after each extraction step.
```

### Verification
```bash
# Verify engine.py size
wc -l core/orchestrator/engine.py  # Should be ~400-500 lines

# Verify no circular imports
python -c "from core.orchestrator.engine import OrchestratorEngine"

# Run all tests
pytest tests/ -v

# Run acceptance tests specifically
pytest tests/acceptance_intelligence/ -v

# Commit
git add core/orchestrator/
git commit -m "Phase 3: Engine decomposition into focused modules"
```

---

## Batch D: Governance, Registry, UI (Phases 4-6)

### Purpose
Consolidate governance gates, unify registries, modularize UI. Low risk, parallel-safe.

### Pre-Prompt Checklist
- [ ] Batches A-C complete and committed
- [ ] All tests passing

### Prompt 8: Governance Consolidation

```
I'm implementing Phase 4 of refactor_plan.md - Governance Consolidation.

Consolidate gate files into a unified gates.py module.

1. Create `core/governance/gates.py`:
   - Implement a GateRegistry pattern for pluggable gates
   - Move and refactor these into the registry:
     - branch_gate.py → BranchGate class
     - loop_gate.py → LoopGate class
     - plan_gate.py → PlanGate class
     - critic_gate.py → CriticGate class
     - retrieval_policy.py → RetrievalGate class

2. Gate interface:
   ```python
   class Gate(Protocol):
       name: str
       def evaluate(self, context: GateContext) -> GateResult: ...
   
   class GateRegistry:
       def register(self, gate: Gate) -> None: ...
       def get(self, name: str) -> Gate: ...
       def evaluate_all(self, context: GateContext) -> list[GateResult]: ...
   ```

3. Update hooks.py to use GateRegistry instead of direct imports.

4. Keep original files with deprecation warnings and re-exports for backward compatibility.

5. Update tests to use new gate structure.

Target: 5 gate files → 1 gates.py + 5 deprecated stubs
```

### Prompt 9: Registry Unification

```
I'm implementing Phase 5 of refactor_plan.md - Registry Unification.

Create a generic ComponentRegistry base class.

1. Create `core/utils/registry.py`:
   ```python
   from typing import Generic, TypeVar, Callable, Dict
   
   T = TypeVar("T")
   
   class ComponentRegistry(Generic[T]):
       """Generic registry for agents, tools, or other component factories."""
       
       def __init__(self, component_type: str):
           self._component_type = component_type
           self._factories: Dict[str, Callable[..., T]] = {}
       
       def register(self, name: str, factory: Callable[..., T]) -> None: ...
       def get(self, name: str) -> T: ...
       def get_factory(self, name: str) -> Callable[..., T]: ...
       def list_registered(self) -> list[str]: ...
       def has(self, name: str) -> bool: ...
   ```

2. Refactor `core/agents/registry.py`:
   - Make AgentRegistry inherit from ComponentRegistry[BaseAgent]
   - Keep existing API for backward compatibility
   - Add any agent-specific methods as extensions

3. Refactor `core/tools/registry.py`:
   - Make ToolRegistry inherit from ComponentRegistry[BaseTool]
   - Keep existing API for backward compatibility
   - Add any tool-specific methods as extensions

4. Update imports in orchestrator and products.

5. Run all registry-related tests.
```

### Prompt 10: UI Modularization

```
I'm implementing Phase 6 of refactor_plan.md - UI Modularization.

Split platform_app.py (1,046 lines) into page modules.

1. Create directory structure:
   ```
   gateway/ui/
   ├── platform_app.py      # Slim entry point (~150 lines)
   ├── api_client.py        # HTTP client for API calls
   ├── pages/
   │   ├── __init__.py
   │   ├── home.py          # Product catalog view
   │   ├── run.py           # Run execution view
   │   ├── approvals.py     # Pending approvals view
   │   └── history.py       # Run history view
   └── components/
       ├── __init__.py
       ├── run_card.py      # Reusable run display widget
       └── approval_form.py # Approval interaction widget
   ```

2. Create `gateway/ui/api_client.py`:
   - Wrap all HTTP calls to the FastAPI backend
   - Remove any direct core/ imports from UI code
   - Handle errors gracefully with user-friendly messages

3. Extract page modules:
   - Each page is a function that renders its Streamlit content
   - Pages import only from api_client, not from core/
   - Use st.session_state for page state management

4. Slim down platform_app.py:
   - Keep only: app initialization, navigation, page routing
   - Import and call page functions based on navigation state

5. Verify UI still works by running: `streamlit run gateway/ui/platform_app.py`

Target: platform_app.py ≤ 200 lines, no direct core/ imports in UI
```

### Verification
```bash
# Verify governance structure
python -c "from core.governance.gates import GateRegistry"

# Verify registry unification
python -c "from core.utils.registry import ComponentRegistry"
python -c "from core.agents.registry import AgentRegistry"
python -c "from core.tools.registry import ToolRegistry"

# Test UI (manual)
streamlit run gateway/ui/platform_app.py

# Run all tests
pytest tests/ -v

# Commit
git add -A
git commit -m "Phases 4-6: Governance consolidation, registry unification, UI modularization"
```

---

## Batch E: Intelligence Enhancement (Phases 7-13)

### Purpose
Add intelligence capabilities while maintaining governance. Medium risk, done incrementally.

### Pre-Prompt Checklist
- [ ] Batches A-D complete and committed
- [ ] All tests passing

### Prompt 11: Enhanced Descriptors & Evidence Model

```
I'm implementing Phase 7 of refactor_plan.md - Enhanced Descriptors & Evidence Model.

1. Expand `core/contracts/descriptors_schema.py`:
   ```python
   class ToolDescriptor(BaseModel):
       name: str
       description: str
       capabilities: list[str] = []  # semantic tags like ["data_reading", "computation"]
       input_schema_ref: str | None = None
       output_schema_ref: str | None = None
       read_only: bool = True
       side_effect: bool = False
       sensitivity_class: str = "internal"  # "public" | "internal" | "confidential" | "restricted"
       cost_hint: str = "low"  # "low" | "medium" | "high"
   
   class AgentDescriptor(BaseModel):
       name: str
       purpose: str
       capabilities: list[str] = []
       input_schema_ref: str | None = None
       output_schema_ref: str | None = None
       cost_hint: str = "low"
       allowed_step_types: list[str] = []  # e.g., ["advisory"]
   ```

2. Add `EvidenceItem` to `core/contracts/context_pack_schema.py`:
   ```python
   class EvidenceItem(BaseModel):
       id: str
       type: str  # "table" | "document" | "text" | "metric"
       source: str  # tool name + uri
       timestamp: datetime
       confidence: float = 1.0
       content_ref: str | None = None  # artifact reference
       summary: str = ""
       provenance: dict = {}  # filters, params used
   ```

3. Update `core/contracts/tool_schema.py`:
   - Add `evidence: list[EvidenceItem] = []` to ToolResult
   - Add backward-compatible handling for tools that don't return evidence

4. Update registries to require descriptors:
   - AgentRegistry.register() should accept or build AgentDescriptor
   - ToolRegistry.register() should accept or build ToolDescriptor

5. Update existing tools/agents in hello_world and ade products to include basic descriptors.

6. Add tests for descriptor validation and evidence propagation.
```

### Prompt 12: Context Pack Builder Enhancement

```
I'm implementing Phase 8 of refactor_plan.md - Context Pack Builder.

Enhance the ContextPackBuilder for deterministic LLM context curation.

1. Update `core/knowledge/context_pack.py`:
   ```python
   class ContextPackBuilder:
       """Builds deterministic context packs from evidence items."""
       
       def __init__(self, max_tokens: int = 4000):
           self.max_tokens = max_tokens
       
       def build(
           self,
           question: str,
           evidence_items: list[EvidenceItem],
           assumptions: list[str] | None = None,
       ) -> ContextPack:
           """Build context pack deterministically (no LLM calls)."""
           ...
       
       def _summarize_tables(self, items: list[EvidenceItem]) -> list[TableSummary]: ...
       def _summarize_documents(self, items: list[EvidenceItem]) -> list[DocSummary]: ...
       def _build_evidence_index(self, items: list[EvidenceItem]) -> list[str]: ...
       def _compute_hash(self, pack: ContextPack) -> str: ...
   ```

2. Update `core/contracts/context_pack_schema.py`:
   ```python
   class TableSummary(BaseModel):
       source: str
       row_count: int
       columns: list[str]
       sample_rows: list[dict] = []
       statistics: dict = {}
   
   class DocSummary(BaseModel):
       source: str
       title: str
       excerpt: str
       word_count: int
   
   class ContextPack(BaseModel):
       question: str
       tables_summary: list[TableSummary] = []
       documents_summary: list[DocSummary] = []
       evidence_index: list[str] = []  # EvidenceItem IDs
       assumptions: list[str] = []
       limits: dict = {}  # data coverage info
       hash: str = ""  # for reproducibility verification
   ```

3. Update LLM reasoner to use ContextPack:
   - llm_reasoner.py should accept ContextPack instead of raw text
   - Format ContextPack into prompt deterministically

4. Add tests for:
   - Same inputs produce same hash
   - Evidence provenance is preserved
   - Token limits are respected
```

### Prompt 13: Bounded Reasoning & Critic

```
I'm implementing Phase 9 of refactor_plan.md - Bounded Reasoning & Critic Pattern.

1. Refactor `core/agents/reasoning_ladder.py`:
   ```python
   class ReasoningLadder:
       """Bounded multi-pass reasoning with governance."""
       
       def __init__(self, llm_reasoner: LLMReasoner, budget: ReasoningBudget):
           self.llm = llm_reasoner
           self.budget = budget
       
       async def run(self, context_pack: ContextPack) -> ReasoningLadderOutput:
           """Execute interpret → propose → select passes."""
           interpret = await self._interpret_pass(context_pack)
           propose = await self._propose_pass(context_pack, interpret)
           select = await self._select_pass(context_pack, interpret, propose)
           return ReasoningLadderOutput(
               interpret=interpret,
               propose=propose,
               select=select,
               ...
           )
   ```

2. Refactor `core/agents/critic_evaluator.py`:
   ```python
   class CriticEvaluator:
       """Bounded critic for quality/completeness checks."""
       
       def evaluate(self, context_pack: ContextPack, result: Any) -> CriticResult:
           """Analyze without calling tools. Return structured recommendations."""
           return CriticResult(
               completeness_score=...,
               inconsistency_flags=[...],
               missing_evidence=[...],
               confidence_adjustment=...,
               recommended_action="NONE"  # or "USER_INPUT" | "HITL" | "FETCH_MORE_EVIDENCE"
           )
   ```

3. Expand `core/governance/budgeting.py`:
   ```python
   class ReasoningBudget(BaseModel):
       max_passes: int = 3
       max_tool_calls: int = 10
       max_parallel_calls: int = 3
       max_total_cost_units: float = 100.0
       max_latency_bucket: str = "medium"
       escalate_on_exceed: bool = True  # trigger HITL if exceeded
   ```

4. Add governance integration:
   - Budget checks before each reasoning pass
   - HITL escalation when budget exceeded
   - Trace events for budget consumption

5. Add tests for bounded behavior and budget enforcement.
```

### Prompt 14: Parallel Tools, Question Loop, Retrieval

```
I'm implementing Phases 10-12 of refactor_plan.md - Parallel Tools, Question Loop, Retrieval.

Phase 10 - TOOL_BATCH step type:

1. Add to `core/contracts/flow_schema.py`:
   ```python
   class ToolBatchStepDef(BaseModel):
       id: str
       type: Literal["tool_batch"]
       tools: list[str]
       parallel: bool = True
   ```

2. Update step_executor.py to handle tool_batch:
   - Validate all tools are read_only and side_effect=false
   - Execute in parallel if parallel=true
   - Merge results with deterministic ordering (by tool name)
   - Collect all EvidenceItems

Phase 11 - Missing-info question loop:

1. Add to `core/contracts/interaction_schema.py`:
   ```python
   class Question(BaseModel):
       id: str
       text: str
       type: str = "text"  # "text" | "choice" | "number"
       required: bool = True
       choices: list[str] | None = None
       validation: dict = {}
   
   class QuestionSet(BaseModel):
       questions: list[Question]
       context: str = ""
       validation_schema: dict = {}
   ```

2. Update user_input_handler.py to support QuestionSet:
   - Validate answers against QuestionSet schema
   - Merge validated answers into ContextPack

Phase 12 - Retrieval augmentation:

1. Update `core/tools/retrieval.py`:
   - Add query_prior_runs() method
   - Add query_approved_sources() method
   - Return EvidenceItems with full provenance

2. Add retrieval policy to configs/policies.yaml structure:
   ```yaml
   retrieval_policy:
     allowed_sources:
       - "runs:current_product"
       - "knowledge:approved_docs"
     blocked_sources:
       - "runs:other_products"
   ```

3. Update governance hooks to enforce retrieval policy.

Add tests for each new capability.
```

### Prompt 15: Advisory Agent Set

```
I'm implementing Phase 13 of refactor_plan.md - Advisory Agent Set.

Refactor advisory.py into bounded advisory agents.

1. Create `core/agents/advisors/` directory with:
   ```
   core/agents/advisors/
   ├── __init__.py
   ├── base.py           # AdvisoryAgent base class
   ├── tool_selector.py  # ToolSelector agent
   ├── agent_selector.py # AgentSelector agent
   ├── gap_finder.py     # GapFinder agent
   ├── summarizer.py     # Summarizer agent
   └── risk_explainer.py # RiskExplainer agent
   ```

2. Base class in `core/agents/advisors/base.py`:
   ```python
   class AdvisoryAgent(BaseAgent):
       """Base for advisory agents that cannot execute tools."""
       
       def __init__(self):
           super().__init__()
           self._can_execute_tools = False  # Enforced
       
       @abstractmethod
       def advise(self, context: StepContext) -> AdvisoryResult: ...
   ```

3. Implement each advisor:
   - ToolSelector: Recommend tools based on descriptors + context
   - AgentSelector: Recommend agents for subtasks
   - GapFinder: Identify missing evidence in context pack
   - Summarizer: Condense evidence into narrative
   - RiskExplainer: Explain confidence/risk factors

4. Each advisor outputs structured results:
   ```python
   class ToolSelectionResult(BaseModel):
       recommended_tools: list[str]
       rationale: str
       confidence: float
   
   # Similar for other advisors...
   ```

5. Add governance check:
   - Advisors cannot invoke ToolExecutor
   - Architecture test to enforce this

6. Update core/agents/__init__.py to export advisors.

7. Add tests verifying advisors cannot call tools.
```

### Verification
```bash
# Run all tests
pytest tests/ -v

# Run intelligence-specific tests
pytest tests/core/test_reasoning_ladder.py -v
pytest tests/core/test_critic_evaluator.py -v
pytest tests/core/test_tool_batch.py -v
pytest tests/core/test_context_pack_builder.py -v

# Commit
git add -A
git commit -m "Phases 7-13: Intelligence enhancement with governance"
```

---

## Batch F: Product & Test Improvements (Phases 14-17)

### Purpose
Simplify product boilerplate and harden test infrastructure.

### Pre-Prompt Checklist
- [ ] Batches A-E complete and committed
- [ ] All tests passing

### Prompt 16: Product Contract Simplification

```
I'm implementing Phase 14 of refactor_plan.md - Product Contract Simplification.

Add auto-discovery and decorator-based registration for products.

1. Add decorators to `core/agents/base.py`:
   ```python
   def agent(
       name: str,
       purpose: str,
       capabilities: list[str] = None,
       cost_hint: str = "low",
   ):
       """Decorator for agent auto-discovery."""
       def decorator(cls):
           cls._agent_descriptor = AgentDescriptor(
               name=name,
               purpose=purpose,
               capabilities=capabilities or [],
               cost_hint=cost_hint,
           )
           return cls
       return decorator
   ```

2. Add decorators to `core/tools/base.py`:
   ```python
   def tool(
       name: str,
       description: str,
       capabilities: list[str] = None,
       read_only: bool = True,
       side_effect: bool = False,
       sensitivity_class: str = "internal",
       cost_hint: str = "low",
   ):
       """Decorator for tool auto-discovery."""
       ...
   ```

3. Add auto-discovery to `core/utils/product_loader.py`:
   ```python
   def auto_discover_agents(product_path: Path) -> list[tuple[str, Callable]]:
       """Discover all @agent decorated classes in product/agents/."""
       ...
   
   def auto_discover_tools(product_path: Path) -> list[tuple[str, Callable]]:
       """Discover all @tool decorated classes in product/tools/."""
       ...
   
   def auto_register(registries: ProductRegistries, product_path: Path) -> None:
       """Auto-register all discovered agents and tools."""
       for name, factory in auto_discover_agents(product_path):
           registries.agent_registry.register(name, factory)
       for name, factory in auto_discover_tools(product_path):
           registries.tool_registry.register(name, factory)
   ```

4. Update hello_world product to use decorators:
   - Add @agent decorator to simple_agent.py
   - Add @tool decorator to echo_tool.py
   - Simplify registry.py to use auto_register()

5. Update ade product to use decorators (larger refactor):
   - Add decorators to all 6 agents
   - Add decorators to all 17 tools
   - Simplify registry.py from ~85 lines to ~15 lines

6. Add tests for auto-discovery.
```

### Prompt 17: Product Test Consolidation

```
I'm implementing Phase 15 of refactor_plan.md - Product Test Consolidation.

Reorganize tests for clear ownership.

1. Move misplaced ADE tests to product folder:
   - Move tests/integration/test_ade_evidence_bundle.py → products/ade/tests/integration/
   - Move tests/integration/test_business_report_html.py → products/ade/tests/integration/

2. Create standard conftest.py for products:
   ```python
   # products/ade/tests/conftest.py
   import pytest
   from pathlib import Path
   
   @pytest.fixture
   def ade_product_path():
       return Path(__file__).parent.parent
   
   @pytest.fixture
   def ade_test_data_path():
       return Path(__file__).parent.parent / "data"
   ```

3. Update test documentation:
   - Add README.md to tests/ explaining test organization
   - Add README.md to products/ade/tests/ explaining product test scope

4. Update CI configuration (if exists) to run product tests in parallel.

5. Verify all tests still discoverable:
   ```bash
   pytest tests/ --collect-only
   pytest products/*/tests/ --collect-only
   ```
```

### Prompt 18: Test Infrastructure Hardening

```
I'm implementing Phases 16-17 of refactor_plan.md - Test Infrastructure Hardening.

Add comprehensive test suites for critical gaps.

1. Create `tests/core/test_hitl_edge_cases.py`:
   ```python
   def test_double_resume_idempotent():
       """Resuming an already-resumed run is safe."""
       ...
   
   def test_resume_wrong_approval_rejected():
       """Approval for wrong step is rejected."""
       ...
   
   def test_concurrent_approvals_serialized():
       """Multiple approvers on same run are serialized."""
       ...
   ```

2. Create `tests/core/test_budget_enforcement.py`:
   ```python
   def test_max_passes_enforced():
       """Loop terminates at max_passes."""
       ...
   
   def test_max_tool_calls_enforced():
       """Run fails gracefully when budget exceeded."""
       ...
   
   def test_budget_exceeded_triggers_hitl():
       """Budget exceeded with escalation policy pauses for approval."""
       ...
   ```

3. Create `tests/architecture/test_product_isolation.py`:
   ```python
   def test_no_cross_product_imports():
       """No product imports another product."""
       ...
   
   def test_product_cannot_access_other_product_runs():
       """API enforces product isolation."""
       ...
   ```

4. Create `tests/acceptance_intelligence/test_golden_paths.py`:
   ```python
   GOLDEN_PATHS = [
       ("hello_world", "hello_world", {"message": "test"}, "hello_world_expected.json"),
   ]
   
   @pytest.mark.parametrize("product,flow,payload,expected_file", GOLDEN_PATHS)
   def test_golden_path(product, flow, payload, expected_file):
       """Run golden path and compare to stored expected output."""
       ...
   ```

5. Create golden path expected outputs:
   - tests/acceptance_intelligence/golden/hello_world_expected.json

6. Expand architecture invariant tests in tests/architecture/test_master_v1_invariants.py:
   - test_agents_never_call_tools_directly
   - test_tools_never_call_llm_directly
   - test_no_env_reads_outside_config_loader
   - test_no_persistence_outside_memory
```

### Final Verification
```bash
# Run complete test suite
pytest tests/ products/*/tests/ -v

# Check test count increased
pytest tests/ --collect-only | grep "test session starts"

# Verify golden paths
pytest tests/acceptance_intelligence/test_golden_paths.py -v

# Commit
git add -A
git commit -m "Phases 14-17: Product simplification and test hardening"

# Merge to main
git checkout main
git merge refactor/master-v2
git push
```

---

## Troubleshooting

### If Tests Fail After a Batch

1. **Don't proceed to next batch** - fix failures first
2. Check the specific test output for error details
3. Use this prompt to fix:
   ```
   The following tests are failing after implementing Phase X:
   
   [paste test output]
   
   Please fix the issues while maintaining the refactoring goals.
   ```

### If Imports Break

```
After the refactoring, I'm getting import errors:

[paste error]

Please fix the imports while maintaining backward compatibility where specified in refactor_plan.md.
```

### If Performance Degrades

```
After implementing Phase X, I'm seeing performance degradation:

[describe the issue]

Please optimize while maintaining the architectural goals from refactor_plan.md.
```

---

## Post-Refactor Checklist

After all batches complete:

- [ ] All 17 phases implemented
- [ ] All tests passing (including new acceptance tests)
- [ ] engine.py ≤ 500 lines
- [ ] Contract files ≤ 14
- [ ] Governance files ≤ 5
- [ ] platform_app.py ≤ 200 lines
- [ ] Product registry.py files simplified
- [ ] No direct core/ imports in UI
- [ ] Golden path tests passing
- [ ] Architecture invariant tests passing
- [ ] Documentation updated

Final commit:
```bash
git tag v2.0.0-refactored
git push --tags
```
