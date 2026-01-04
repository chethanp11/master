
# Flows and Agents — master/

This document explains **how flows and agents are defined, wired, and executed**
in the `master/` platform.

It is intended for engineers **building products**, not modifying the core runtime.

This document is governed by:
- docs/engineering_standards.md

---

## 1. Core Concepts

### Flow
A **flow** is a declarative definition of:
- *what goal is being pursued*
- *what steps are required*
- *in what order they execute*
- *under what constraints*

```mermaid
sequenceDiagram
  participant User
  participant Gateway as API/CLI/UI
  participant Orchestrator
  participant Agent
  participant ToolExec as ToolExecutor
  participant Tool
  User->>Gateway: run flow
  Gateway->>Orchestrator: run_flow
  Orchestrator->>Agent: run(step)
  Agent-->>Orchestrator: AgentResult
  Orchestrator->>ToolExec: execute tool
  ToolExec->>Tool: run(params)
  Tool-->>ToolExec: ToolResult
  ToolExec-->>Orchestrator: ToolResult
  Orchestrator-->>Gateway: status/result
```

Flows:
- Are defined in YAML or JSON
- Are loaded and validated by the orchestrator
- Contain **no executable logic**
- Describe intent, not implementation

---

### Agent
An **agent** is a unit of goal-driven reasoning.

Agents are:
- Stateless
- Goal-driven (not template-driven)
- Side-effect free

Agents:
- Receive params and constraints from the orchestrator
- Reason and decide
- Return structured outputs (`AgentResult`)
- Do **not** perform IO or execution directly

---

## 2. Flow Location

Flows live under:

products/<product>/flows/

Example:

products/hello_world/flows/hello_world.yaml

---

## 3. Flow Composition Guardrails (V1)

This section defines the V1 flow composition guardrails.

### Core rule: entrypoint composition only

- Flows do not call other flows.
- The orchestrator does not dynamically jump across flow boundaries.
- Products must select which flow to run at the entrypoint (API/CLI/UI).

### Example: multiple flows per product

Product structure:

products/visual_insights/flows/
  visualization.yaml
  data_quality.yaml

Entrypoint selection (pseudo-code):

if request.kind == "data_quality":
    run flow "data_quality"
else:
    run flow "visualization"

### Why

- Keeps execution deterministic and auditable.
- Avoids hidden control flow in YAML.
- Simplifies pause/resume and approvals.

---

## 4. Flow Definition Schema (Conceptual)

```yaml
id: hello_world
description: Simple demo flow

autonomy_level: semi_auto   # suggest_only | semi_auto | full_auto

steps:
  - id: plan
    type: agent
    agent: hello_world.planner
    params:
      instruction: "Generate an execution plan"
    retry:
      max_attempts: 2
      backoff_seconds: 1

  - id: approve
    type: human_approval
    message: "Approve generated plan?"

  - id: execute
    type: agent
    agent: hello_world.executor
    params:
      instruction: "Execute the approved plan"
```

Notes:
- `params` are the primary control inputs to agents and tools
- Retry behavior is declarative and flow-driven

---

## 5. Step Types

### Agent Step

- id: step_name
  type: agent
  agent: product.agent_name
  params:
    instruction: "Describe desired outcome"

Behavior:
- Resolves agent from registry
- Provides StepContext (params, payload, artifacts)
- Executes agent reasoning
- Expects an AgentResult

Agents:
- Do not decide the next step
- Do not call tools directly
- Do not mutate persistent state

---

### Tool Step

- id: call_tool
  type: tool
  tool: product.tool_name

Behavior:
- Executed only by the tool executor
- Subject to governance and policy checks
- Produces a ToolResult

Notes:
- The orchestrator decides whether and when tools run
- Tools are executed only by ToolExecutor

---

### Human Approval Step (HITL)

- id: approve
  type: human_approval
  message: "Approve this output?"

Behavior:
- Pauses execution
- Persists run and step state
- Sets run status to PENDING_APPROVAL (PENDING_HUMAN in storage)
- Requires explicit resume action
- Approval context can be supplied in `params` (reason, decision notes, recommended action)

---

### User Input Step

- id: collect_input
  type: user_input
  params:
    schema_version: "1.0"
    form_id: "chart_config"
    title: "Select chart options"
    mode: choice_input
    schema:
      type: object
      properties:
        chart_type:
          type: string
          enum: [bar, line]
    defaults:
      chart_type: bar
    required: [chart_type]

Behavior:
- Pauses execution
- Sets run status to PENDING_USER_INPUT
- Requires resume with `user_input_response` payload

---

### Plan Proposal Step

- id: propose_plan
  type: plan_proposal
  agent: product.plan_agent

Behavior:
- Invokes a planner agent that returns a structured PlanProposal (JSON)
- Validates proposal against schema
- Emits plan proposal trace events
- Does not execute the plan automatically

---

## 6. Autonomy Levels

Level	Description
suggest_only	Agents reason and suggest; no execution
semi_auto	Tools may execute but require approval
full_auto	Fully autonomous execution

Rules:
- Autonomy level is enforced by governance hooks
- Agents do not override autonomy

---

## 7. Retry and Error Handling

Retries are flow-driven, never agent-driven.

retry:
  max_attempts: 3
  backoff_seconds: 2

Rules:
- Retries occur only on recoverable errors
- Error classification is handled by error policy evaluation
- Agents return structured errors; they do not retry themselves

---

## 8. Agent Location

Agents live under:

products/<product>/agents/

Example:

products/hello_world/agents/simple_agent.py


---

## 9. Agent Contract

All agents must:
- Inherit from BaseAgent
- Implement run(step_context)
- Return AgentResult
- Never raise exceptions for expected failures

Conceptual example:

class SimpleAgent(BaseAgent):
    name = "hello_world.simple"

    def run(self, step_context):
        return AgentResult(
            ok=True,
            data={"message": "Hello world"},
            error=None,
            meta={"agent_name": "hello_world.simple"},
        )


---

## 10. Agent Responsibilities

Agents MAY:
- Read params, constraints, and artifacts
- Reason and decide
- Emit trace events

Agents MUST NOT:
- Execute tools directly
- Call other agents
- Read/write files
- Persist state
- Call models directly (model access is centralized in `core/agents/llm_reasoner.py` via `core/models/router.py`)
- Read environment variables

---

## 11. Agent Registry

Agents are registered at startup:
- Product agents self-register via controlled import
- Registry maps agent_name -> agent class

Resolution:
- Orchestrator resolves agents by name at runtime
- Names should be namespaced (product.agent)

---

## 12. Flow Execution Lifecycle
	1.	Flow loaded and validated
	2.	RunContext initialized
	3.	Step loop begins
	4.	Step executed
	5.	Trace events emitted
	6.	State persisted via memory backend
	7.	HITL pause or continuation
	8.	Completion or failure recorded

Step parameter rendering supports:
- `{{payload.<key>}}`
- `{{artifacts.<key>}}`
Missing values render as `null` for full-token values and as empty strings for inline tokens.

---

## 13. Product Isolation

Rules:
- Flows must not reference agents from other products
- Tools are product-scoped unless explicitly shared
- Core agents/tools may be reused

---

## 14. Testing Flows and Agents

Required:
- Unit test agents independently
- Integration test flows via orchestrator
- Explicitly test HITL paths
- Assert structured outputs and state transitions

---

## 15. Best Practices
- Keep flows declarative and readable
- Express intent via params, not code
- Keep agents small and single-purpose
- Prefer more steps over complex agents
- Use approval gates early for high-risk actions
- Log decisions and intent, not raw data

---

This design keeps flows auditable and deterministic while preserving product isolation.
