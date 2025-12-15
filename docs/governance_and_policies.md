# Governance and Policies — master/

This document defines the **governance model** for the `master/` agentic platform.

Governance exists to ensure:
- Safety
- Auditability
- Consistency
- Enterprise compliance
- Controlled autonomy

All enforcement is **centralized in core**.  
Products cannot bypass governance.

---

## 1. Governance Scope

Governance applies to:
- Flows
- Steps
- Agents
- Tools
- Models
- Autonomy levels
- Human-in-the-loop behavior
- Logging and persistence

No product code may implement its own governance logic.

---

## 2. Policy Configuration

Policies are defined in:

configs/policies.yaml

Policies are **data-driven**, not code-driven.

---

## 3. Policy Types

### 3.1 Tool Policies

Control which tools can be executed.

Example:
```yaml
tools:
  echo_tool:
    risk: low
  db_write_tool:
    risk: high
    require_human_approval: true
```
Enforced:
	•	Before tool execution
	•	By core.governance.hooks.before_tool_call

---

### 3.2 Flow Policies

Control flow-level behavior.

Example:

flows:
  hello_world:
    max_steps: 10
    allow_autonomy: semi_auto

Enforced:
	•	At flow start
	•	During step evaluation

⸻

### 3.3 Autonomy Policies

Limit autonomy per product or flow.

autonomy:
  default: suggest_only
  allowed:
    - suggest_only
    - semi_auto

full_auto requires explicit policy enablement.

⸻

### 3.4 Product Policies

Apply constraints per product.

products:
  agentaura:
    allowed_tools:
      - echo_tool
    blocked_models:
      - gpt-4o


⸻

### 3.5 Model Policies

Control model usage.

models:
  gpt-4o:
    max_tokens: 8000
    allow_external: false


⸻

## 4. Human-in-the-Loop (HITL)

### 4.1 When HITL is Required

HITL is triggered when:
	•	A step type is human_approval
	•	A tool policy requires approval
	•	A governance hook raises RequireHumanApproval

⸻

### 4.2 HITL Behavior

When HITL is triggered:
	•	Execution pauses
	•	Run state → PENDING_HUMAN
	•	Context is persisted
	•	Approval request is created

⸻

### 4.3 Resume Flow

Resumption occurs via:

POST /api/resume_run/{run_id}

Only permitted when:
	•	Run is in PENDING_HUMAN
	•	Approval decision exists

⸻

## 5. Governance Hooks

Hooks are extension points executed by the runtime.

### 5.1 Available Hooks

Hook Name	Trigger
before_flow_start	Flow initialization
before_step	Step execution
before_tool_call	Tool invocation
after_step	Step completion
before_flow_complete	Finalization


⸻

### 5.2 Hook Responsibilities

Hooks may:
	•	Allow execution
	•	Deny execution
	•	Require human approval
	•	Modify context metadata
	•	Emit trace events

Hooks may NOT:
	•	Execute tools
	•	Modify flow structure

⸻

## 6. Security and Redaction

### 6.1 PII Scrubbing

All logs and traces are scrubbed for:
	•	API keys
	•	Tokens
	•	Secrets
	•	PII patterns (emails, IDs)

Implemented in:

core/governance/security.py

Scrubbing occurs:
	•	Before persistence
	•	Before log emission
	•	Before UI rendering

⸻

### 6.2 Redaction Rules

Redacted values appear as:

[REDACTED]

No raw secrets may be written to disk.

⸻

## 7. Auditability

Every run must record:
	•	Who triggered it
	•	Which flow
	•	Which steps
	•	Which tools
	•	Approval decisions
	•	Final outcome

Stored in:

storage/memory/


⸻

## 8. Policy Violations

When a policy is violated:
	•	Execution stops
	•	Run status → FAILED
	•	Error is recorded as a structured governance error
	•	No partial state is committed

⸻

## 9. Governance Error Types

Error Type	Description
PolicyViolation	Disallowed action
AutonomyViolation	Exceeded autonomy
ToolBlocked	Tool not permitted
ModelBlocked	Model not permitted
ApprovalRequired	HITL required


⸻

## 10. Product Developer Rules

Product teams:
	•	Must define flows within allowed autonomy
	•	Must request new tool approvals centrally
	•	Must not hardcode policy logic
	•	Must test policy paths

⸻

## 11. Non-Negotiable Rules
	•	Governance cannot be bypassed
	•	Policies are evaluated at runtime
	•	Hooks are mandatory
	•	Violations are final

⸻

This governance model ensures safe autonomy without sacrificing speed or flexibility.

