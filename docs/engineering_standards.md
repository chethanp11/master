# Engineering Standards — master/

This document is the **constitution** of the `master/` platform.  
All code (human-written or AI-generated) **must** comply with these rules.

Violations are considered architectural defects.

---

## 1. Absolute Boundary Rules (Non-Negotiable)

### 1.1 External Vendor Calls
- ❌ **FORBIDDEN**: Calling OpenAI, Anthropic, HuggingFace, DBs, HTTP APIs directly from agents, tools, orchestrator, or products.
- ✅ **ALLOWED ONLY IN**:

core/models/providers/

- All vendor SDK usage must be wrapped behind a provider interface.
- No provider-specific logic outside this layer.

---

### 1.2 Tool Execution
- ❌ **FORBIDDEN**: Agents calling tools directly.
- ❌ **FORBIDDEN**: Tools executing other tools.
- ❌ **FORBIDDEN**: Direct backend calls from orchestrator.

- ✅ **ALLOWED FLOW**:

Agent → ToolExecutor → Governance → Backend → ToolResult

- All tool execution **must** go through:

core/tools/executor.py

---

### 1.3 Persistence & State
- ❌ **FORBIDDEN**: Writing to disk, DBs, or files outside memory backends.
- ❌ **FORBIDDEN**: SQLite / filesystem access outside `core/memory/`.

- ✅ **ALLOWED ONLY IN**:

core/memory/*

- Orchestrator and agents treat memory as a black box.

---

### 1.4 Environment Variables & Config
- ❌ **FORBIDDEN**: Reading environment variables directly (`os.getenv`) outside config loader.
- ❌ **FORBIDDEN**: Hard-coded secrets, URLs, model names, or limits.

- ✅ **ALLOWED ONLY IN**:

config loader (gateway or core/config)

- All runtime values must come from:
- YAML config files
- Environment variables injected via loader
- In-memory config objects

---

## 2. Naming Conventions

### 2.1 Files & Modules
- snake_case for all files and folders
- No abbreviations unless universally understood
- One responsibility per file

Examples:

flow_loader.py
tool_executor.py
sqlite_backend.py

---

### 2.2 Classes
- PascalCase
- One public class per file (unless exception justified)

Examples:

RunContext
BaseAgent
ToolResult

---

### 2.3 Functions
- snake_case
- Verb-first naming

Examples:

load_flow()
execute_step()
validate_policy()

---

### 2.4 Constants & Enums
- UPPER_SNAKE_CASE

Examples:

RUNNING
PENDING_HUMAN
FULL_AUTO

---

## 3. Result Envelope Rules (Critical)

### 3.1 No Raw Returns
- ❌ **FORBIDDEN**: Returning raw strings, dicts, lists, or primitives from:
  - Agents
  - Tools
  - Orchestrator steps

- ✅ **MANDATORY**: Use typed result envelopes.

---

### 3.2 Agent Results
All agents **must** return:

AgentResult

Required fields:
- `success: bool`
- `output: Any`
- `error: AgentError | None`
- `metadata: dict`

---

### 3.3 Tool Results
All tools **must** return:

ToolResult

Required fields:
- `success: bool`
- `data: Any`
- `error: ToolError | None`
- `metadata: dict`

---

### 3.4 Error Objects
Errors are **data**, not control flow.

- ❌ Do not raise exceptions for expected failures.
- ✅ Return structured error objects.

Exceptions are allowed **only** for:
- Programmer errors
- Contract violations
- Corrupted state

---

## 4. Tracing & Observability Rules

### 4.1 Mandatory Tracing
Every significant action **must** emit a trace event:
- Flow start
- Step start/end
- Agent execution
- Tool execution
- HITL pause/resume
- Errors

---

### 4.2 Tracing Flow
All tracing goes through:

core/logging/tracing.py

- ❌ No `print()`
- ❌ No ad-hoc logging
- ❌ No silent failures

---

### 4.3 Sanitization
- All trace payloads **must** be sanitized before persistence.
- PII and secrets are scrubbed via:

core/governance/security.py

---

## 5. Error Handling Rules

### 5.1 Expected Failures
- Use error objects (`AgentError`, `ToolError`)
- Include:
- error code
- human-readable message
- recoverability flag

---

### 5.2 Unexpected Failures
- Raise exceptions
- Must be caught at orchestrator boundary
- Must emit failure trace event
- Must persist failure state

---

### 5.3 Retries & Backoff
- No manual retry loops in agents or tools
- Retry behavior is driven by:
- Flow definition
- Error policy evaluation

---

## 6. Product Code Rules

### 6.1 Product Folder Structure
Each product **must** follow:

products//
├── flows/
├── agents/
├── tools/
├── prompts/
├── config/
└── tests/

---

### 6.2 Product Responsibilities
Products define:
- Business logic
- Domain tools
- Flow sequencing
- Prompt tuning

Products do **not** define:
- Execution mechanics
- Logging
- Persistence
- Governance
- Model invocation logic

---

### 6.3 Imports
- Products may import:
  - Core public contracts
  - Core registries
  - BaseAgent / BaseTool
- Products may **not** import:
  - Orchestrator internals
  - Memory backends
  - Governance internals

---

## 7. Configuration Rules

### 7.1 No Hardcoding
- ❌ Hard-coded model names
- ❌ Hard-coded tool limits
- ❌ Hard-coded retry logic

Everything must be configurable via YAML.

---

### 7.2 Config Precedence
Highest → Lowest:
1. Runtime overrides
2. Product config
3. Global config

---

## 8. Code Generation Rules (AI Safety)

All AI-generated code **must**:
- Follow this document verbatim
- Prefer clarity over cleverness
- Be explicit rather than implicit
- Avoid hidden side effects
- Include docstrings for public interfaces

If unsure:
> **Fail closed, not open.**

---

## 9. Enforcement

- Code review checks against this document
- CI tests validate:
  - Boundary violations
  - Result envelope compliance
  - Missing tracing
- Any exception must be documented in code and approved

---
## 10. Configuration & Secrets Rules (Precedence + What Goes Where)

### 10.1 Config Sources and Precedence (Highest → Lowest)
1. **Runtime overrides** (explicit overrides passed into app startup / CLI)
2. **Environment variables** from `.env` (non-secret flags only)
3. **Product config**: `products/<product>/config/product.yaml`
4. **Global config**: `configs/app.yaml`, `configs/models.yaml`, `configs/policies.yaml`, `configs/logging.yaml`
5. **Code defaults** (last resort; must be safe + minimal)

Rules:
- If the same key exists in multiple layers, **higher layer wins**.
- Code defaults must never contain secrets or environment-specific values.

---

### 10.2 What Goes Where

#### A) `.env` (gitignored)
Use for **non-secret runtime flags** and **local dev knobs**.

Allowed examples:
- ports, host, debug, log level
- local storage paths
- feature flags (enable_ui, enable_api)
- config file locations

Forbidden in `.env`:
- API keys, tokens, passwords
- private endpoints or credentials
- anything that would be escalated as a secret in an enterprise environment

---

#### B) `configs/*.yaml` (checked into git)
Use for **stable, shared platform parameters** and **defaults**.

Examples:
- `configs/app.yaml`:
  - product discovery settings
  - default timeouts, budgets
  - platform-wide limits
- `configs/models.yaml`:
  - model routing defaults (logical names, not secrets)
  - per-use-case model selection rules
- `configs/policies.yaml`:
  - tool allow/deny rules
  - autonomy level constraints
  - approval requirements by tool risk class
- `configs/logging.yaml`:
  - log formats, sinks, retention policies (non-secret)

Rules:
- No secrets inside `configs/*.yaml`
- Use logical model names (e.g., `default`, `fast`, `reasoning`) not raw vendor keys

---

#### C) `secrets/secrets.yaml` (gitignored)
Use for **all secrets**.

Examples:
- vendor API keys (OpenAI, etc.)
- tokens, passwords, private endpoints
- any credential required by tools

Rules:
- Must be gitignored
- Must never be printed/logged
- Must be redacted by `core/governance/security.py`

---

### 10.3 Loading Rules (Enforcement)
- No `os.getenv()` outside the config loader.
- No direct file reads of configs/secrets outside the loader.
- All components receive a **single config object** injected at startup.
- If a secret is missing, fail fast with a clear error (no silent fallbacks).

**This document overrides all other conventions.**