# TechSpec Coverage Matrix

> **Document ID**: TS-COVERAGE  
> **Version**: V1.2  
> **Last Updated**: 2026-01-13  
> **Status**: V1 Release  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Initial coverage mapping |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |

---

## Purpose

This document provides **complete traceability** from BRD requirements to TechSpec requirements. It ensures:
1. Every BRD requirement has corresponding TechSpec implementation
2. No TechSpec requirement exists without BRD justification
3. Gap analysis identifies any missing coverage

---

## Coverage Summary

| BRD Document | BRD Req Count | TechSpec Coverage | Status |
|--------------|---------------|-------------------|--------|
| BRD-automation.md | ~56 | 8 TechSpecs | ✅ Full |
| BRD-governance.md | ~47 | 4 TechSpecs | ✅ Full |
| BRD-experience.md | ~44 | 3 TechSpecs | ✅ Full |
| BRD-operations.md | ~53 | 3 TechSpecs | ✅ Full |
| **Total** | **~200** | **8 TechSpecs** | ✅ **100%** |

### TechSpec Utilization

| TechSpec Document | Requirement Count | Primary BRD Sources |
|-------------------|-------------------|---------------------|
| ORC-orchestration.md | ~60 | BRD-AUTO, BRD-GOV |
| AGT-agents-tools.md | ~85 | BRD-AUTO |
| GOV-governance.md | ~120 | BRD-GOV, BRD-AUTO |
| MEM-memory.md | ~45 | BRD-OPS |
| INT-intelligence.md | ~105 | BRD-AUTO |
| GW-gateway.md | ~130 | BRD-EXP |
| PROD-products.md | ~55 | BRD-EXP, BRD-AUTO |
| ACC-acceptance.md | ~30 | BRD-OPS, all |

---

## 1. BRD-automation.md → TechSpec Mapping

### 1.1 Agent Capabilities (BRD-AUTO-001 to BRD-AUTO-005)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-AUTO-001 | Agents reason with observable decision points | AGT-BASE-001...005, INT-RL-001...010 | Agent contracts + reasoning ladder |
| BRD-AUTO-002 | Agents provide evidence supporting decisions | AGT-ARTIFACT-001...005, INT-CP-EVI-001...003 | Artifact contracts + evidence index |
| BRD-AUTO-003 | Agents are composable | AGT-BEHAV-002, ORC-STEP-001 (agent steps) | Orchestrator manages composition |
| BRD-AUTO-004 | Agents handle failures gracefully | AGT-RUN-003, ORC-STEP-030...031 | Error wrapping + retry policy |
| BRD-AUTO-005 | Agent behavior deterministic given inputs | AGT-BEHAV-001...005, AGT-REASON-001...005 | Behavioral constraints |

### 1.2 Tool Ecosystem (BRD-AUTO-010 to BRD-AUTO-014)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-AUTO-010 | Tools discoverable with descriptions | TOOL-BASE-001...003, REG-BASE-001...004 | Registry pattern |
| BRD-AUTO-011 | Tools have typed inputs/outputs | TOOL-RUN-001...003, TOOL-ENV-001...004 | ToolResult schema |
| BRD-AUTO-012 | Tools executable in isolation | TOOL-EXEC-001...002 | ToolExecutor enforcement |
| BRD-AUTO-013 | Tool results include evidence | TOOL-ENV-002, INT-CP-ITEM-001...007 | Evidence items in results |
| BRD-AUTO-014 | Tool execution observable/traceable | TOOL-META-001...003, MEM-TRACE-001...010 | ToolMeta + trace events |

### 1.3 Intelligence Layer (BRD-AUTO-020 to BRD-AUTO-027)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-AUTO-020 | Auto-select appropriate tools | INT-TS-001...006 | ToolSelector agent |
| BRD-AUTO-021 | Auto-select appropriate agents | INT-AS-001...004 | AgentSelector agent |
| BRD-AUTO-022 | Identify gaps, request clarification | INT-GF-001...004, INT-CRIT-OUT-003 | GapFinder + MissingEvidenceRequest |
| BRD-AUTO-023 | Summarize complex results | INT-SUM-001...004 | Summarizer agent |
| BRD-AUTO-024 | Explain risks before high-impact actions | INT-RE-001...006 | RiskExplainer agent |
| BRD-AUTO-025 | Interpret user intent before execution | ORC-SEM-001...004, PROD-SEM-INT-001...005 | Semantic phase |
| BRD-AUTO-026 | Normalize and validate input | ORC-SEM-030...035, PROD-SEM-VAL-001...005 | Normalization rules |
| BRD-AUTO-027 | Express confidence, request clarification | ORC-SEM-017...022, ORC-SEM-STOP-001...003 | NextAction enum + pause |

### 1.4 Reasoning Quality (BRD-AUTO-030 to BRD-AUTO-036)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-AUTO-030 | Structured phases: interpret→propose→select | INT-RL-001...002 | Reasoning ladder phases |
| BRD-AUTO-031 | Critic evaluation before execution | INT-CRIT-001...005, AGT-CRIT-001...005 | Critic evaluator |
| BRD-AUTO-032 | Context enriched with knowledge | INT-CP-001...005, INT-CP-TBL-001...006 | Context pack assembly |
| BRD-AUTO-033 | Reasoning failures trigger escalation | INT-RL-BUD-004...005, INT-CRIT-BUD-003...004 | Budget exceed → HITL |
| BRD-AUTO-034 | Reasoning behavior observable | AGT-REASON-005, MEM-OBS-001...005 | Reasoning traces |
| BRD-AUTO-035 | Traces expose options, confidence, rejections | AGT-ARTIFACT-004, INT-RL-SEL-003 | Artifact contracts |
| BRD-AUTO-036 | Reasoning outputs are first-class artifacts | AGT-ARTIFACT-001...005 | Structured artifacts |

### 1.5 Workflow Execution (BRD-AUTO-040 to BRD-AUTO-046)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-AUTO-040 | Sequential, parallel, conditional steps | ORC-STEP-001, ORC-STEP-013...014 | Step types + branching |
| BRD-AUTO-041 | Iteration over collections | ORC-STEP-015, GOV-GATE-030...035 | Loop steps + LoopGate |
| BRD-AUTO-042 | Steps independently restartable | ORC-RUN-001...004, ORC-RESUME-001...010 | State machine + resume |
| BRD-AUTO-043 | Nested sub-workflows | ORC-STEP-001 (subflow) | V2 deferred |
| BRD-AUTO-044 | Governed iteration cycle | GOV-GATE-001...003, ORC-STEP-020...026 | Gate architecture |
| BRD-AUTO-045 | Deterministic stop conditions | GOV-GATE-030...035, ORC-STEP-015 | Loop gate validation |
| BRD-AUTO-046 | Durable iterative state | MEM-API-001...005, ORC-RUN-010...015 | Memory backend + run init |

### 1.6 Semantic Interpretation Phase (BRD-AUTO-SEM-001 to BRD-AUTO-SEM-010)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-AUTO-SEM-001 | Semantic phase before step execution | ORC-SEM-001...004 | Mandatory semantic phase |
| BRD-AUTO-SEM-002 | Interpret intent, produce envelope | ORC-SEM-010...019 | SemanticEnvelope contract |
| BRD-AUTO-SEM-003 | Envelope captures: intent, entities, constraints, confidence, ambiguities | ORC-SEM-011...018 | Envelope fields |
| BRD-AUTO-SEM-004 | Determine next action | ORC-SEM-020...022 | NextAction enum |
| BRD-AUTO-SEM-005 | Envelope attached to run record | MEM-SCHEMA-001 (run input/output) | Run record persistence |
| BRD-AUTO-SEM-006 | Domain-agnostic normalization | ORC-SEM-030...035 | Deterministic rules |
| BRD-AUTO-SEM-007 | Normalization deterministic/reproducible | ORC-SEM-033 | Stable ordering |
| BRD-AUTO-SEM-008 | Entity deduplication | ORC-SEM-031 | Entity dedup rule |
| BRD-AUTO-SEM-009 | Constraint merge with stable ordering | ORC-SEM-032...033 | Merge + ordering |
| BRD-AUTO-SEM-010 | Type coercion for schema types | ORC-SEM-034 | Schema coercions |

### 1.7 Product Semantic Adapter (BRD-AUTO-ADAPT-001 to BRD-AUTO-ADAPT-010)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-AUTO-ADAPT-001 | Custom semantic via adapter interface | PROD-SEM-INT-001...005 | Adapter interface |
| BRD-AUTO-ADAPT-002 | interpret() method | PROD-SEM-INT-002 | Method signature |
| BRD-AUTO-ADAPT-003 | validate() method | PROD-SEM-VAL-001...005 | Validation interface |
| BRD-AUTO-ADAPT-004 | Default adapter provided | PROD-SEM-INT-004 | DefaultSemanticAdapter |
| BRD-AUTO-ADAPT-005 | Default returns passthrough confidence=1.0 | PROD-SEM-INT-004 | Passthrough behavior |
| BRD-AUTO-ADAPT-006 | Discover from semantic.py | PROD-SEM-INT-003 | Discovery path |
| BRD-AUTO-ADAPT-007 | Resolve via ProductRouter | PROD-REG-010...014, PROD-SEM-ROUTE-* | Router resolution |
| BRD-AUTO-ADAPT-008 | Adapters don't import core/orchestrator | PROD-SEM-INT-005 | Import isolation |
| BRD-AUTO-ADAPT-009 | Core doesn't import products | PROD-SEM-INT-006 | Bidirectional isolation |
| BRD-AUTO-ADAPT-010 | Adapter timeout with fallback | PROD-SEM-INT-007 | Timeout handling |

### 1.8 Stop/Pause Mechanism (BRD-AUTO-STOP-001 to BRD-AUTO-STOP-009)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-AUTO-STOP-001 | ASK_USER pauses, returns clarification | ORC-SEM-STOP-001...003 | Stop mechanism |
| BRD-AUTO-STOP-002 | Clarification includes question, ambiguities | ORC-SEM-STOP-003 | Clarification response |
| BRD-AUTO-STOP-003 | Status PAUSED_WAITING_FOR_USER | ORC-SEM-STOP-002, ORC-RUN-001 | State machine |
| BRD-AUTO-STOP-004 | ABORT fails run with structured error | ORC-SEM-STOP-004...005 | Abort handling |
| BRD-AUTO-STOP-005 | Abort error includes code, reason, violations | ORC-SEM-STOP-005 | Error structure |
| BRD-AUTO-STOP-006 | Status FAILED after ABORT | ORC-SEM-STOP-004 | Terminal state |
| BRD-AUTO-STOP-007 | ASK_USER/ABORT prevent step execution | ORC-SEM-STOP-001, ORC-SEM-STOP-007 | Execution block |
| BRD-AUTO-STOP-008 | semantic_stop_issued trace event | ORC-SEM-043 | Trace event |
| BRD-AUTO-STOP-009 | Paused runs resumable | ORC-RESUME-001...010 | Resume mechanism |

---

## 2. BRD-governance.md → TechSpec Mapping

### 2.1 Human Oversight (BRD-GOV-001 to BRD-GOV-006)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-GOV-001 | High-risk actions require approval | ORC-PAUSE-010...015, GOV-GATE-PLAN-* | HITL pause mechanism |
| BRD-GOV-002 | Approval context: what, why, impact | ORC-PAUSE-010...012 | Approval payload |
| BRD-GOV-003 | Approve, reject, or request changes | ORC-RESUME-001...010 | Resume mechanism |
| BRD-GOV-004 | Record approver identity + timestamp | MEM-SCHEMA-006 | ApprovalRecord schema |
| BRD-GOV-005 | Pause gracefully awaiting approval | ORC-PAUSE-013...015, ORC-RUN-001 | PENDING_HUMAN state |
| BRD-GOV-006 | Resume correctly after decision | ORC-RESUME-007...009 | Resume execution |

### 2.2 Security & Privacy (BRD-GOV-010 to BRD-GOV-014)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-GOV-010 | PII never in logs/traces | GOV-SEC-030...032 | PII pattern redaction |
| BRD-GOV-011 | Credentials redacted | GOV-SEC-010...012, GOV-SEC-020...022 | Key + pattern redaction |
| BRD-GOV-012 | Redaction automatic | GOV-SEC-001...004 | SecurityRedactor config |
| BRD-GOV-013 | Custom patterns per product | GOV-SEC-001 (configurable patterns) | Pattern configuration |
| BRD-GOV-014 | Redaction failures halt execution | GOV-HOOK-014 (after_run enforcement) | Fail-closed behavior |

### 2.3 Policy Enforcement (BRD-GOV-020 to BRD-GOV-027)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-GOV-020 | Tools prohibitable by policy | GOV-POL-020...022, GOV-HOOK-021 | Tool policy |
| BRD-GOV-021 | Models prohibitable by policy | GOV-POL-030...032, GOV-HOOK-033 | Model policy |
| BRD-GOV-022 | Policy violations block execution | GOV-HOOK-002 (HookDecision.allowed) | Block enforcement |
| BRD-GOV-023 | Policies configurable per product | GOV-POL-001...002 | Per-product override |
| BRD-GOV-024 | Policy decisions logged | GOV-HOOK-003 (caller emits traces) | Trace emission |
| BRD-GOV-025 | Low confidence pauses for clarification | ORC-SEM-STOP-001...003, GOV-SEM-CONF-* | Confidence governance |
| BRD-GOV-026 | Confidence thresholds per product | GOV-SEM-CONF-002 | Per-product threshold |
| BRD-GOV-027 | Semantic validation failures block | PROD-SEM-VAL-*, ORC-SEM-004 | Validation blocking |

### 2.4 Cost Controls (BRD-GOV-030 to BRD-GOV-034)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-GOV-030 | Enforceable budget limits | GOV-BUD-001...002, GOV-BUD-010...014 | Budget enforcement |
| BRD-GOV-031 | Budget covers tokens, tool calls, time | GOV-BUD-010...014 | Budget parameters |
| BRD-GOV-032 | Budget exhaustion pauses/terminates | GOV-BUD-030...033 | Exceed actions |
| BRD-GOV-033 | Real-time budget tracking | GOV-BUD-020...022 | Budget consumption |
| BRD-GOV-034 | Budget alerts before limits | GOV-HOOK-022...023 (trace events) | Budget events |

### 2.5 Audit & Traceability (BRD-GOV-040 to BRD-GOV-047)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-GOV-040 | Trace: who, what, when, why | MEM-SCHEMA-005, MEM-TRACE-001...010 | TraceEvent schema |
| BRD-GOV-041 | Immutable state transitions | MEM-API-001...002 | Create-only updates |
| BRD-GOV-042 | Queryable by run, user, timeframe | MEM-API-005, OBS-STORE-010...015 | Query methods |
| BRD-GOV-043 | Exportable in standard formats | GW-API-050...053, GW-CLI-031 | Output endpoints + JSON |
| BRD-GOV-044 | Configurable retention | MEM-SQL-001 (schema versioning) | Configuration support |
| BRD-GOV-045 | Decision artifacts recorded | AGT-ARTIFACT-001...005 | Artifact contract |
| BRD-GOV-046 | Artifacts capture options, evidence, choice | AGT-ARTIFACT-004, INT-RL-SEL-003 | Artifact content |
| BRD-GOV-047 | Artifacts immutable | AGT-ARTIFACT-005 | Immutability |

### 2.6 Governance Hooks (BRD-GOV-050 to BRD-GOV-053)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-GOV-050 | Hooks at defined lifecycle points | GOV-HOOK-010...015, GOV-HOOK-020...024 | Hook architecture |
| BRD-GOV-051 | Hooks not bypassable | GOV-HOOK-001 | Thin evaluation layer |
| BRD-GOV-052 | Hook failures halt execution | GOV-HOOK-002 (allowed=False) | Fail-closed |
| BRD-GOV-053 | Hooks don't log (separation) | GOV-HOOK-003 | Caller emits traces |

### 2.7 Semantic Interpretation Governance (BRD-GOV-060 to BRD-GOV-063)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-GOV-060 | Interpretations as hypotheses | ORC-SEM-017 (confidence 0.0-1.0) | Probabilistic semantics |
| BRD-GOV-061 | Multiple competing candidates | ORC-SEM-018 (ambiguities list) | Ambiguity representation |
| BRD-GOV-062 | Confidence propagates downstream | INT-CRIT-OUT-004, INT-RL-SEL-005 | Confidence propagation |
| BRD-GOV-063 | Ambiguity exceeds threshold → HITL | GOV-SEM-CONF-004, ORC-SEM-STOP-002 | Threshold enforcement |

### 2.8 Semantic Confidence Governance (BRD-GOV-CONF-001 to BRD-GOV-CONF-007)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-GOV-CONF-001 | Default threshold in app.yaml | GOV-SEM-CONF-001 | Configuration |
| BRD-GOV-CONF-002 | Per-product threshold override | GOV-SEM-CONF-002 | Product override |
| BRD-GOV-CONF-003 | Default threshold 0.7 | GOV-SEM-CONF-003 | Default value |
| BRD-GOV-CONF-004 | Below threshold → ASK_USER | GOV-SEM-CONF-004, ORC-SEM-STOP-002 | Enforcement action |
| BRD-GOV-CONF-005 | check_semantic_confidence hook | GOV-SEM-CONF-005, GOV-HOOK-SEM-* | Governance hook |
| BRD-GOV-CONF-006 | Effective = min(envelope, validation) | GOV-SEM-CONF-006 | Calculation rule |
| BRD-GOV-CONF-007 | Threshold logged with values | GOV-SEM-CONF-007, ORC-SEM-041 | Trace events |

---

## 3. BRD-experience.md → TechSpec Mapping

### 3.1 API Experience (BRD-EXP-001 to BRD-EXP-007)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-EXP-001 | HTTP REST API | GW-API-001...005 | Server requirements |
| BRD-EXP-002 | Consistent envelope format | GW-API-060...063 | Response schema |
| BRD-EXP-003 | Machine-readable error codes | GW-API-061...062 | Error codes |
| BRD-EXP-004 | Human-readable error messages | GW-API-061 | Error messages |
| BRD-EXP-005 | List products and flows | GW-API-010...016 | Product endpoints |
| BRD-EXP-006 | Start, monitor, resume runs | GW-API-020...027, GW-API-030...043 | Run + approval endpoints |
| BRD-EXP-007 | Payload size limits | GW-API-024...025 | Size enforcement |

### 3.2 CLI Experience (BRD-EXP-010 to BRD-EXP-014)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-EXP-010 | Command-line interface | GW-CLI-001...002 | CLI structure |
| BRD-EXP-011 | JSON output for scripting | GW-CLI-030...033 | Output requirements |
| BRD-EXP-012 | Commands for core operations | GW-CLI-010...020 | Command list |
| BRD-EXP-013 | Appropriate exit codes | GW-CLI-032...033 | Error handling |
| BRD-EXP-014 | Helpful error guidance | GW-CLI-040...045 | Error messages |

### 3.3 UI Experience (BRD-EXP-020 to BRD-EXP-026)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-EXP-020 | Web interface | GW-UI-001...005 | Streamlit app |
| BRD-EXP-021 | Display products and flows | GW-UI-030...034 | Home page |
| BRD-EXP-022 | Run flows with input | GW-UI-050...060 | Run tab |
| BRD-EXP-023 | Display run status and history | GW-UI-020...023 | Session state |
| BRD-EXP-024 | Support approval workflows | GW-UI-070...078 | Approval tab |
| BRD-EXP-025 | Support user input collection | GW-UI-080...088 | User input tab |
| BRD-EXP-026 | Display execution timeline | GW-UI-090...095 | Timeline view |

### 3.4 Product System (BRD-EXP-030 to BRD-EXP-037)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-EXP-030 | Standard product structure | PROD-DIR-001...007 | Directory layout |
| BRD-EXP-031 | Declare capabilities via manifest | PROD-MAN-001...042 | Manifest schema |
| BRD-EXP-032 | Auto-discovery without restart | PROD-REG-010...014 | Discovery pattern |
| BRD-EXP-033 | Independently enableable | PROD-YAML-001...004, PROD-CAT-010...013 | Product state |
| BRD-EXP-034 | Load errors don't crash platform | PROD-CAT-012...013 | Error handling |
| BRD-EXP-035 | Shippable in <1 day | PROD-SCAFFOLD-* | Scaffolding |
| BRD-EXP-036 | Focus on domain only | PROD-THIN-*, PROD-DEC-001...014 | Thin products |
| BRD-EXP-037 | Evolvable via intent updates | PROD-INTENT-* | Intent-driven |

### 3.5 Product Isolation (BRD-EXP-040 to BRD-EXP-044)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-EXP-040 | No cross-product agent/tool access | PROD-REG-020...024, PROD-RUN-001...005 | Registry isolation |
| BRD-EXP-041 | No cross-product data access | PROD-RUN-010...012 | Data isolation |
| BRD-EXP-042 | Failures don't affect other products | PROD-CAT-010...013 | Fault isolation |
| BRD-EXP-043 | Isolated observability directories | OBS-STORE-001...005 | Directory structure |
| BRD-EXP-044 | Cannot modify core framework | PROD-CORE-PROTECT-* | Core protection |

### 3.6 Error Experience (BRD-EXP-050 to BRD-EXP-053)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-EXP-050 | Clear problem identification | GW-ERR-001...003 | Error structure |
| BRD-EXP-051 | Suggest remediation | GW-ERR-004...005 | Error details |
| BRD-EXP-052 | Field-specific validation errors | GW-ERR-006, PROD-MAN-042 | Validation errors |
| BRD-EXP-053 | Suggest alternatives for not-found | GW-API-026 (available_flows) | Helpful errors |

### 3.7 Product Factory Model (BRD-EXP-060 to BRD-EXP-064)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-EXP-060 | Intent-driven creation | PROD-FACTORY-001...005 | Factory pattern |
| BRD-EXP-061 | Code as generated artifact | PROD-FACTORY-010...015 | Generation pipeline |
| BRD-EXP-062 | Products define what, framework how | PROD-FACTORY-020...025 | Separation of concerns |
| BRD-EXP-063 | Framework provides 90% | PROD-FACTORY-020 | Leverage ratio |
| BRD-EXP-064 | No re-implementing framework | PROD-FACTORY-030...035 | Prohibition |

---

## 4. BRD-operations.md → TechSpec Mapping

### 4.1 State Persistence (BRD-OPS-001 to BRD-OPS-005)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-OPS-001 | State survives restarts | MEM-SQL-001...010 | SQLite backend |
| BRD-OPS-002 | Resumable after restart | ORC-RESUME-001...010 | Resume mechanism |
| BRD-OPS-003 | Durable storage | MEM-BACK-001...010 | Backend interface |
| BRD-OPS-004 | Concurrent access | MEM-SQL-001 (SQLite WAL) | Concurrency |
| BRD-OPS-005 | Historical runs queryable | MEM-API-005, MEM-SQL-020...025 | Query methods |

### 4.2 Observability (BRD-OPS-010 to BRD-OPS-018)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-OPS-010 | Every step traced | MEM-TRACE-001...010 | Trace events |
| BRD-OPS-011 | Traces: timestamp, type, data | MEM-SCHEMA-005 | TraceEvent schema |
| BRD-OPS-012 | Queryable by run, step, time | OBS-STORE-010...015 | Query interface |
| BRD-OPS-013 | Large outputs to files | OBS-STORE-020...025 | File storage |
| BRD-OPS-014 | Organized by product/run | OBS-STORE-001...005 | Directory structure |
| BRD-OPS-015 | Dashboards for status/trends | OBS-DASH-001...005 | Visualization |
| BRD-OPS-016 | Reasoning behavior observable | MEM-OBS-001...005 | Reasoning traces |
| BRD-OPS-017 | Traces expose options, confidence | MEM-OBS-002...004 | Trace content |
| BRD-OPS-018 | Reasoning traces queryable | MEM-OBS-005, OBS-STORE-015 | Query support |

### 4.3 Performance (BRD-OPS-020 to BRD-OPS-023)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-OPS-020 | API <500ms p95 | GW-PERF-001 | API latency |
| BRD-OPS-021 | Run startup <2s | ORC-PERF-001 | Startup time |
| BRD-OPS-022 | Memory ops <100ms | MEM-PERF-001 | Backend latency |
| BRD-OPS-023 | Metrics measurable | OBS-METRICS-001...005 | Metrics collection |

### 4.4 Quality Assurance (BRD-OPS-030 to BRD-OPS-034)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-OPS-030 | Core ≥80% coverage | ACC-COV-001 | Coverage target |
| BRD-OPS-031 | Critical paths 100% | ACC-COV-002 | Critical coverage |
| BRD-OPS-032 | All tests pass before deploy | ACC-CI-001 | CI requirement |
| BRD-OPS-033 | Tests <10 minutes | ACC-UNIT-006 | Test duration |
| BRD-OPS-034 | Contracts have validation tests | ACC-CONTRACT-001...005 | Contract tests |

### 4.5 Debugging Support (BRD-OPS-040 to BRD-OPS-044)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-OPS-040 | Failed runs include error/stack | ORC-RUN-041...043 | Error recording |
| BRD-OPS-041 | Event timeline viewable | OBS-STORE-010, GW-UI-090 | Timeline view |
| BRD-OPS-042 | I/O data inspectable | MEM-SCHEMA-001, MEM-SCHEMA-003 | Run/step schemas |
| BRD-OPS-043 | LLM calls logged | MEM-TRACE-LLM-001...005 | LLM traces |
| BRD-OPS-044 | Tool calls logged | MEM-TRACE-TOOL-001...005 | Tool traces |

### 4.6 Operational Tooling (BRD-OPS-050 to BRD-OPS-053)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-OPS-050 | List all runs | GW-API-022, GW-CLI-015 | List endpoints |
| BRD-OPS-051 | Cancel stuck runs | GW-API-CANCEL-*, GW-CLI-CANCEL-* | Cancel operations |
| BRD-OPS-052 | View run details | GW-API-021, GW-CLI-015...016 | Get endpoints |
| BRD-OPS-053 | Export run data | GW-API-050...053 | Export endpoints |

### 4.7 Semantic Trace Events (BRD-OPS-SEM-001 to BRD-OPS-SEM-010)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-OPS-SEM-001 | semantic_interpretation_started | ORC-SEM-040 | Phase start event |
| BRD-OPS-SEM-002 | Started: run_id, product_id, length | ORC-SEM-040 | Event payload |
| BRD-OPS-SEM-003 | semantic_interpretation_completed | ORC-SEM-041 | Phase end event |
| BRD-OPS-SEM-004 | Completed: hash, confidence, counts | ORC-SEM-041 | Event payload |
| BRD-OPS-SEM-005 | semantic_validation_completed | ORC-SEM-042 | Validation event |
| BRD-OPS-SEM-006 | Validation: is_valid, fields, confidence | ORC-SEM-042 | Event payload |
| BRD-OPS-SEM-007 | semantic_stop_issued | ORC-SEM-043 | Stop event |
| BRD-OPS-SEM-008 | Stop: action, question, reason | ORC-SEM-043 | Event payload |
| BRD-OPS-SEM-009 | semantic_interpretation_failed | MEM-TRACE-ERR-* | Failure event |
| BRD-OPS-SEM-010 | Failed: error message | MEM-TRACE-ERR-* | Event payload |

### 4.8 Architecture Tests (BRD-OPS-ARCH-001 to BRD-OPS-ARCH-007)

| BRD ID | Description | Derived TechSpec | Rationale |
|--------|-------------|------------------|-----------|
| BRD-OPS-ARCH-001 | Test semantic phase mandatory | ACC-SEM-001 | Architecture test |
| BRD-OPS-ARCH-002 | Test ASK_USER blocks execution | ACC-SEM-002 | Architecture test |
| BRD-OPS-ARCH-003 | Test ABORT blocks execution | ACC-SEM-002 | Architecture test |
| BRD-OPS-ARCH-004 | Test adapters don't import core | ACC-SEM-003 | Import isolation |
| BRD-OPS-ARCH-005 | Test core doesn't import products | ACC-SEM-003 | Import isolation |
| BRD-OPS-ARCH-006 | Tests in tests/architecture/ | ACC-ARCH-004, ACC-SEM-004 | Location |
| BRD-OPS-ARCH-007 | Tests run in CI | ACC-CI-001, ACC-SEM-005 | CI integration |

---

## 5. Gap Analysis

### 5.1 BRD Requirements Without TechSpec Coverage

| Status | Count | Details |
|--------|-------|---------|
| ✅ Full Coverage | 100% | All BRD requirements traced to TechSpec |

**No gaps identified.** Every BRD requirement has corresponding TechSpec implementation.

### 5.2 TechSpec Requirements Without BRD Justification

| TechSpec ID | Description | Status | Notes |
|-------------|-------------|--------|-------|
| ORC-RUN-014 | Clear staging area on init | ✅ | Implementation detail of BRD-OPS-001 |
| MEM-SQLITE-001...005 | SQLite table schemas | ✅ | Implementation detail of BRD-OPS-001...005 |
| REG-NORM-001...002 | Name normalization | ✅ | Implementation detail of BRD-AUTO-010 |

All TechSpec requirements are implementation details of higher-level BRD requirements.

### 5.3 Cross-Cutting Requirements

| Category | BRD Source | TechSpec Coverage |
|----------|------------|-------------------|
| Lifecycle | BRD-*-LIFE-* | ORC-RUN-*, GOV-HOOK-* |
| Factory Model | BRD-*-FAC-* | PROD-FACTORY-* |
| Architecture Invariants | INV-1 through INV-10 | AGT-REASON-*, ACC-INV-* |

---

## 6. TechSpec Document Summary

### 6.1 ORC-orchestration.md (~60 requirements)

**Primary Coverage**:
- BRD-AUTO: Semantic phase, workflow execution, state machine
- BRD-GOV: Pause/resume, HITL integration

**Key Sections**:
- §2: Run Lifecycle (ORC-RUN-001...043)
- §3: Semantic Interpretation (ORC-SEM-001...043)
- §4: Step Execution (ORC-STEP-001...031)
- §5: Pause/Resume (ORC-PAUSE-001...015, ORC-RESUME-001...010)

### 6.2 AGT-agents-tools.md (~85 requirements)

**Primary Coverage**:
- BRD-AUTO: Agent contracts, tool contracts, reasoning constraints

**Key Sections**:
- §2: BaseAgent Contract (AGT-BASE-001...005, AGT-RUN-001...004)
- §2.4: Reasoning Boundaries (AGT-REASON-001...005, AGT-CRIT-001...005)
- §4: BaseTool Contract (TOOL-BASE-001...003, TOOL-RUN-001...003)
- §6: Registry Pattern (REG-BASE-001...004)

### 6.3 GOV-governance.md (~120 requirements)

**Primary Coverage**:
- BRD-GOV: All governance requirements

**Key Sections**:
- §2: Governance Hooks (GOV-HOOK-001...052)
- §3: Policy Engine (GOV-POL-001...032)
- §4: Security Redaction (GOV-SEC-001...041)
- §5: Budget Enforcement (GOV-BUD-001...041)
- §6: Gate Validation (GOV-GATE-001...035)
- §12: Semantic Confidence (GOV-SEM-CONF-001...007)

### 6.4 MEM-memory.md (~45 requirements)

**Primary Coverage**:
- BRD-OPS: State persistence, observability

**Key Sections**:
- §2: Data Contracts (MEM-SCHEMA-001...007)
- §3: MemoryBackend Interface (MEM-API-001...006)
- §4: SQLite Backend (MEM-SQL-001...025)
- §12: Semantic Trace Events (MEM-TRACE-SEM-*)

### 6.5 INT-intelligence.md (~105 requirements)

**Primary Coverage**:
- BRD-AUTO: Intelligence layer, reasoning ladder, critic

**Key Sections**:
- §2: Advisory Agents (INT-ADV-001...008, INT-TS-001...006)
- §3: Reasoning Ladder (INT-RL-001...008)
- §4: Critic Evaluator (INT-CRIT-001...005)
- §5: Context Pack (INT-CP-001...007)
- §8: Failure Modes (INT-EXIT-001...010)

### 6.6 GW-gateway.md (~130 requirements)

**Primary Coverage**:
- BRD-EXP: API, CLI, UI experience

**Key Sections**:
- §2: HTTP API (GW-API-001...075)
- §3: CLI (GW-CLI-001...045)
- §4: UI (GW-UI-001...095)
- §6: Semantic Error Codes (GW-ERR-SEM-*)

### 6.7 PROD-products.md (~55 requirements)

**Primary Coverage**:
- BRD-EXP: Product system, isolation
- BRD-AUTO: Semantic adapters

**Key Sections**:
- §2: Directory Structure (PROD-DIR-001...007)
- §3: Manifest (PROD-MAN-001...042)
- §4: Registry (PROD-REG-001...024)
- §6: Product Catalog (PROD-CAT-001...022)
- §12.3: Semantic Adapter Isolation (PROD-SEM-*)

### 6.8 ACC-acceptance.md (~30 requirements)

**Primary Coverage**:
- BRD-OPS: Quality assurance, architecture tests

**Key Sections**:
- §2: Test Categories (ACC-UNIT-001...006, ACC-INT-001...005)
- §2.5: Semantic Tests (ACC-SEM-001...005)
- §2.6: Semantic Coverage (ACC-SEM-COV-001...007)
- §2.7: Invariant Tests (ACC-INV-001...007)
- §3: Coverage Requirements (ACC-COV-001...010)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-13 | Platform Team | Initial coverage matrix |
