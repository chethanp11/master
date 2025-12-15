

# Engineering Standards — master/

This document is the **constitution** of the `master/` platform.  
All code (human-written or AI-generated) **must** comply with these rules.

Violations are considered **architectural defects**, not style issues.

This document overrides all other conventions.

---

## 1. Absolute Boundary Rules (Non-Negotiable)

### 1.1 External Vendor Calls
- ❌ **FORBIDDEN**: Calling OpenAI, Anthropic, HuggingFace, vector DBs, HTTP APIs, or any external services directly from:
  - agents
  - tools
  - orchestrator
  - products

- ✅ **ALLOWED ONLY IN**:

core/models/providers/

Rules:
- All vendor SDK usage must be wrapped behind a provider interface.
- No provider-specific logic outside this layer.
- Model selection is done via logical names (never vendor IDs).

---

### 1.2 Tool Execution
- ❌ **FORBIDDEN**: Agents calling tools directly.
- ❌ **FORBIDDEN**: Tools executing other tools.
- ❌ **FORBIDDEN**: Direct backend calls from orchestrator.

- ✅ **MANDATORY FLOW**:

Agent → ToolExecutor → Governance → Backend → ToolResult

Rules:
- All tool execution **must** go through:

core/tools/executor.py

- Tool backends are implementation details, never invoked directly.

---

### 1.3 Persistence & State
- ❌ **FORBIDDEN**: Writing to disk, DBs, or files outside memory backends.
- ❌ **FORBIDDEN**: SQLite, filesystem, or vector store access outside `core/memory/`.

- ✅ **ALLOWED ONLY IN**:

core/memory/*

Rules:
- Orchestrator and agents treat memory as a black box.
- Memory access is always via interfaces, never concrete backends.

---

### 1.4 Environment Variables & Config
- ❌ **FORBIDDEN**: Reading environment variables directly (`os.getenv`) outside the config loader.
- ❌ **FORBIDDEN**: Hard-coded secrets, URLs, model names, limits, or timeouts.

- ✅ **ALLOWED ONLY IN**:

core/config/loader.py
gateway/api/deps.py

Rules:
- All runtime values come from:
  - YAML config files
  - Environment variables injected via loader
  - In-memory config objects
- No component owns configuration.

---

## 2. Core Execution Philosophy (Foundational)

### 2.1 Goal-Driven, Not Prompt-Driven
- **Agents are strictly GOAL-DRIVEN.**
- Prompts are **not** a control mechanism.

Rules:
- ❌ No product logic embedded in prompts.
- ❌ No prompt engineering as a system behavior lever.
- ✅ Agents receive:
  - explicit goals
  - constraints
  - expected outputs
  - allowed tools
  from the orchestrator.

Prompts (if present at all):
- Are **foundational system instructions only**
- Live in core
- Must not encode business logic or branching behavior

---

### 2.2 Orchestrator Is the Control Plane
- The orchestrator owns:
  - flow execution
  - step sequencing
  - retries and backoff
  - tool authorization
  - HITL pauses and resumes
  - state transitions

Rules:
- ❌ Agents do not decide workflow.
- ❌ Agents do not call other agents.
- ❌ Agents do not schedule tools.
- ✅ Agents return structured intent; orchestrator decides execution.

---

## 3. Naming Conventions

### 3.1 Files & Modules
- `snake_case`
- No abbreviations unless universally understood
- One responsibility per file

Examples:

flow_loader.py
tool_executor.py
sqlite_backend.py

---

### 3.2 Classes
- `PascalCase`
- One public class per file unless explicitly justified

Examples:

RunContext
BaseAgent
ToolResult

---

### 3.3 Functions
- `snake_case`
- Verb-first naming

Examples:

load_flow()
execute_step()
validate_policy()

---

### 3.4 Constants & Enums
- `UPPER_SNAKE_CASE`

Examples:

RUNNING
PENDING_HUMAN
FULL_AUTO

---

## 4. Result Envelope Rules (Critical)

### 4.1 No Raw Returns
- ❌ **FORBIDDEN**: Returning raw strings, dicts, lists, or primitives from:
  - agents
  - tools
  - orchestrator steps

- ✅ **MANDATORY**: Typed result envelopes everywhere.

---

### 4.2 Agent Results
All agents **must** return `AgentResult`.

Required fields:
- `success: bool`
- `output: Any`
- `error: AgentError | None`
- `metadata: dict`

---

### 4.3 Tool Results
All tools **must** return `ToolResult`.

Required fields:
- `success: bool`
- `data: Any`
- `error: ToolError | None`
- `metadata: dict`

---

### 4.4 Error Objects
Errors are **data**, not control flow.

Rules:
- ❌ Do not raise exceptions for expected failures.
- ✅ Return structured error objects.

Exceptions are allowed **only** for:
- programmer errors
- contract violations
- corrupted state

---

## 5. Tracing & Observability Rules

### 5.1 Mandatory Tracing
Every significant action **must** emit a trace event:
- flow start/end
- step start/end
- agent execution
- tool execution
- HITL pause/resume
- errors and retries

---

### 5.2 Tracing Flow
All tracing goes through:

core/logging/tracing.py

Rules:
- ❌ No `print()`
- ❌ No ad-hoc logging
- ❌ No silent failures

---

### 5.3 Sanitization
- All trace payloads **must** be sanitized before persistence.
- PII and secrets are scrubbed via:

core/governance/security.py

---

## 6. Error Handling Rules

### 6.1 Expected Failures
- Use structured error objects (`AgentError`, `ToolError`)
- Include:
  - error code
  - human-readable message
  - recoverability flag

---

### 6.2 Unexpected Failures
- Raise exceptions
- Must be caught at orchestrator boundary
- Must emit failure trace event
- Must persist failure state

---

### 6.3 Retries & Backoff
- ❌ No manual retry loops in agents or tools
- Retry behavior is driven by:
  - flow definition
  - error policy evaluation

---

## 7. Product Code Rules

### 7.1 Product Folder Structure
Each product **must** follow:
```
products//
├── flows/
├── agents/
├── tools/
├── prompts/
├── config/
└── tests/
```
---

### 7.2 Product Responsibilities
Products define:
- domain goals
- domain tools
- flow sequencing
- schemas and constraints

Products **do NOT** define:
- execution mechanics
- orchestration logic
- logging
- persistence
- governance
- model invocation logic
- prompt-based behavior control

---

### 7.3 Prompts in Products
Rules:
- Prompts are **optional**
- Prompts must NOT encode logic
- Prompts must NOT replace goals or flows
- Prompts may only provide:
  - formatting hints
  - domain vocabulary
  - stylistic guidance (if required)

---

### 7.4 Imports
- Products may import:
  - core public contracts
  - core registries
  - BaseAgent / BaseTool

- Products may **not** import:
  - orchestrator internals
  - memory backends
  - governance internals
  - logging internals

---

## 8. Configuration Rules

### 8.1 No Hardcoding
- ❌ Hard-coded model names
- ❌ Hard-coded tool limits
- ❌ Hard-coded retry logic

Everything must be configurable via YAML.

---

### 8.2 Config Precedence
Highest → Lowest:
1. Runtime overrides
2. Product config
3. Global config
4. Code defaults (safe only)

---

## 9. Code Generation Rules (AI Safety)

All AI-generated code **must**:
- Follow this document verbatim
- Prefer clarity over cleverness
- Be explicit rather than implicit
- Avoid hidden side effects
- Include docstrings for public interfaces

If unsure:
> **Fail closed, not open.**

---

## 10. Configuration & Secrets Rules

### 10.1 Config Sources and Precedence (Highest → Lowest)
1. Runtime overrides
2. `.env` (non-secret flags only)
3. Product config (`products/<product>/config/product.yaml`)
4. Global config (`configs/*.yaml`)
5. Code defaults (safe, minimal)

---

### 10.2 What Goes Where

#### A) `.env` (gitignored)
Use for **non-secret runtime flags only**:
- ports, debug, log level
- feature flags
- local paths

❌ Never store secrets.

---

#### B) `configs/*.yaml` (checked into git)
Use for **shared platform defaults**:
- discovery rules
- model routing logic (logical names)
- policy defaults
- logging config

❌ Never store secrets.

---

#### C) `secrets/secrets.yaml` (gitignored)
Use for **all secrets**:
- API keys
- tokens
- credentials

Rules:
- Must never be logged
- Must be redacted by governance
- Missing secrets fail fast

---

### 10.3 Loading Rules
- No `os.getenv()` outside config loader
- No direct file reads of configs/secrets outside loader
- One validated config object injected everywhere

---

## 11. Enforcement

- Code reviews enforce this document
- CI validates:
  - boundary violations
  - envelope compliance
  - missing tracing
- Any exception must be documented and approved

**This document is binding.**

