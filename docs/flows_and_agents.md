# Flows and Agents — master/

This document explains **how flows and agents are defined, wired, and executed** in the `master/` platform.

It is intended for engineers **building products**, not modifying the core runtime.

---

## 1. Core Concepts

### Flow
A **flow** is a declarative definition of *what steps to execute* and *in what order*.

- Defined in YAML or JSON
- Loaded and validated by the orchestrator
- Drives execution without embedding logic in code

### Agent
An **agent** is a unit of reasoning.

- Stateless
- Deterministic for a given context
- Returns structured output (`AgentResult`)
- Does **not** perform IO directly

---

## 2. Flow Structure

Flows live in:

products//flows/

Example:

hello_world.yaml

---

## 3. Flow Definition Schema (Conceptual)

```yaml
id: hello_world
description: Simple demo flow

autonomy_level: semi_auto   # suggest_only | semi_auto | full_auto

steps:
  - id: plan
    type: agent
    agent: simple_planner
    retry:
      max_attempts: 2
      backoff_seconds: 1

  - id: approve
    type: human_approval
    message: "Approve generated plan?"

  - id: execute
    type: agent
    agent: simple_executor


⸻

4. Step Types

4.1 Agent Step

- id: step_name
  type: agent
  agent: agent_name

	•	Executes an agent registered in the product
	•	Receives RunContext
	•	Returns AgentResult

⸻

4.2 Tool Step (Optional)

- id: call_tool
  type: tool
  tool: tool_name

	•	Executes via tool executor
	•	Subject to governance checks

⸻

4.3 Human Approval Step (HITL)

- id: approve
  type: human_approval
  message: "Approve this output?"

	•	Pauses execution
	•	Persists state
	•	Sets run status to PENDING_HUMAN
	•	Requires explicit resume call

⸻

5. Autonomy Levels

Level	Description
suggest_only	Generates output but does not execute tools
semi_auto	Executes tools but requires approvals
full_auto	Fully autonomous execution

Autonomy is enforced by governance hooks.

⸻

6. Retry and Error Handling

Retries are flow-driven, not agent-driven.

retry:
  max_attempts: 3
  backoff_seconds: 2

	•	Retries occur only on recoverable errors
	•	Error evaluation handled by error policy engine

⸻

7. Agent Definition

Agents live in:

products/<product>/agents/

Example:

simple_agent.py


⸻

8. Agent Contract

All agents must:
	•	Inherit from BaseAgent
	•	Implement run(context)
	•	Return AgentResult
	•	Never raise for expected failures

Example (conceptual):

class SimpleAgent(BaseAgent):
    def run(self, context):
        return AgentResult(
            success=True,
            output="Hello world",
            metadata={}
        )


⸻

9. Agent Responsibilities

Agents may:
	•	Read context
	•	Reason
	•	Request tool execution (via context signals)
	•	Format outputs

Agents may NOT:
	•	Execute tools directly
	•	Read/write files
	•	Persist state
	•	Call models directly

⸻

10. Agent Registry

Agents are registered at startup:
	•	Product agents register themselves
	•	Registry maps agent_name → class

The orchestrator resolves agents by name at runtime.

⸻

11. Flow Execution Lifecycle
	1.	Flow loaded and validated
	2.	RunContext initialized
	3.	Step loop begins
	4.	Step executed
	5.	Traces emitted
	6.	State persisted
	7.	HITL pause or continue
	8.	Completion or failure

⸻

12. Flow Composition Patterns

12.1 Linear Flow

Plan → Execute → Finish


⸻

12.2 Looping Flow

Plan → Execute → Critic → Plan (on failure)

(Requires conditional support)

⸻

12.3 Approval Gate

Generate → Approve → Execute


⸻

13. Product Isolation
	•	Flows cannot reference agents from other products
	•	Tools are product-scoped unless explicitly shared
	•	Prompts are product-specific by default

⸻

14. Testing Flows and Agents
	•	Unit test agents independently
	•	Integration test flows via orchestrator
	•	HITL paths must be tested explicitly

⸻

15. Best Practices
	•	Keep flows declarative
	•	Keep agents small
	•	Prefer more steps over complex agents
	•	Use approval gates early
	•	Log intent, not raw data

⸻

This design ensures flows remain readable, auditable, and change-safe.

