# Dev Prompts Log

- 2026-01-04 17:05:20: going forward save every prompt that is shared here in dev_prompts.md
- 2026-01-04 17:05:20: with date time
- 2026-01-04 17:05:56: create txt files again
- 2026-01-04 17:06:39: components/*.txt
- 2026-01-04 17:16:27: do i have both renderer and templating?
- 2026-01-04 17:22:21: You are Codex. Act as a senior platform engineer working in repo: master/

Objective:
Enforce Master V1 architectural invariants using automated tests.

Task:
Create a new test suite under tests/architecture/ that FAILS if platform laws are violated.

You MUST enforce:
- Products MUST NOT import:
  - core/models/*
  - core/agents/llm_reasoner.py
  - core/memory/*
  - core/orchestrator/*
- Tools MUST NOT import:
  - core/agents/*
  - core/models/*
- Agents MUST NOT import:
  - memory backends
  - tool executors
- UI MUST NOT import:
  - core logic beyond API surface

Implementation rules:
- Use static analysis (AST parsing or ripgrep)
- Fail fast with clear error messages identifying:
  - offending file
  - illegal import
- Tests must be deterministic and fast

Do NOT:
- Modify production code
- Add runtime checks
- Add new framework features

Stop when:
- A regression in imports will reliably fail CI

- 2026-01-04 17:37:18: you missed to add latest prompt to dev_prompts.md. how can i make it permanent rule for codex?
- 2026-01-04 17:43:09: You are Codex. Act as a senior platform engineer working in repo: master/

Objective:
Guarantee that agents can never influence flow control.

Task:
Harden orchestrator control boundaries.

Required changes:
- In StepExecutor:
  - Agents may return DATA ONLY
  - Explicitly forbid returning:
    - next_step
    - retry instructions
    - branching hints
- In contracts:
  - Agent output schema MUST NOT contain control fields
- In governance:
  - Strictly validate agent outputs against schema

Add tests that:
- Fail if agent output contains control semantics
- Prove flow branching is controlled ONLY by orchestrator + policies

Do NOT:
- Add agent-to-agent calls
- Add dynamic flow mutation

Stop when:
- Control is structurally impossible to leak into agents
- 2026-01-04 17:49:31: You are Codex. Act as a senior platform engineer working in repo: master/

Objective:
Finish formalizing USER_INPUT as a first-class orchestration step.

Task:
Complete USER_INPUT support across the framework.

Required changes:
- In flow_schema.py:
  - Add explicit step type: user_input
- In executor.py:
  - Implement semantics:
    - pause execution
    - persist run state
    - resume with schema-validated user input
- Clearly separate:
  - HITL = approval
  - USER_INPUT = data acquisition

Constraints:
- USER_INPUT must be schema-driven
- No prompt-based clarification loops
- No hacks in UI

Add tests for:
- pause/resume correctness
- invalid user input rejection

Stop when:
- Interactive flows are clean, deterministic, and auditable
- 2026-01-04 17:55:54: You are Codex. Act as a senior platform engineer working in repo: master/

Objective:
Ensure governance is enforced at ALL lifecycle boundaries.

Task:
Audit and complete governance hook coverage.

Must enforce at:
- Model invocation
- Tool execution
- User input ingestion
- Output rendering / export

Add explicit enforcement for:
- max steps per run
- max tool calls per run
- max token budget per run (not just per model)

Constraints:
- Use existing governance hooks
- No business logic in UI
- No product overrides of core policy

Add tests proving:
- Violations are blocked consistently
- Limits are enforced deterministically

Stop when:
- Cost, safety, and compliance are predictable by design
- 2026-01-04 18:07:13: You are Codex. Act as a senior platform engineer working in repo: master/

Objective:
Eliminate session bleed and concurrency footguns.

Task:
Harden framework-level concurrency guarantees.

Required checks:
- RunContext MUST be request-scoped
- OrchestratorEngine MUST hold no mutable state
- SQLite backend MUST be WAL-safe
- No singleton state leaks across runs

Add concurrency smoke tests:
- Two parallel runs
- Same product
- Same flow
- No shared state corruption

Constraints:
- Do not add queues or async frameworks
- No UI-layer hacks

Stop when:
- Parallel runs are safe by construction
- 2026-01-04 18:19:34: You are Codex. Act as a senior platform engineer working in repo: master/

Objective:
Prevent silent drift from V1 into V2 behavior.

Task:
Add negative tests asserting forbidden behaviors.

Must assert:
- No agent-to-agent calls
- No dynamic flow mutation
- No autonomous retries without policy
- No hidden state inside products
- No self-modifying flows

Implementation:
- Tests should FAIL if these patterns appear
- Prefer static analysis where possible

Constraints:
- No new features
- No documentation changes
- Tests only

Stop when:
- V1 boundaries are protected by code, not memory
- 2026-01-04 18:21:59: create components txt file again
- 2026-01-04 18:30:22: delete and recreate .txt files
