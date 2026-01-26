# SD-COMP-LIST: System Component Reference

**Generated:** This document provides a comprehensive listing of all components in the MASTER platform codebase.

---

## Table of Contents

1. [core/agents](#component-coreagents)
2. [core/config](#component-coreconfig)
3. [core/contracts](#component-corecontracts)
4. [core/governance](#component-coregovernance)
5. [core/knowledge](#component-coreknowledge)
6. [core/memory](#component-corememory)
7. [core/models](#component-coremodels)
8. [core/orchestrator](#component-coreorchestrator)
9. [core/tools](#component-coretools)
10. [core/utils](#component-coreutils)
11. [gateway/api](#component-gatewayapi)
12. [gateway/cli](#component-gatewaycli)
13. [gateway/ui](#component-gatewayui)
14. [configs](#component-configs)
15. [scripts](#component-scripts)

---

## Component: core/agents

Agent framework providing bounded intelligent components with governance integration and tracing.

### base.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `BaseAgent` | Abstract base class contract for all agents | All agent implementations, `step_executor.py`, tests | Subclassed by concrete agents; `run()` called by StepExecutor | Every agent step execution |
| `BaseAgent.run()` | Abstract method signature for agent execution | Implemented by all concrete agents | Called with RunContext and input dict | When orchestrator executes an agent step |
| `BaseAgent._inject_config()` | Dependency injection for agent configuration | Called during agent construction | Receives Settings object | At agent instantiation |

### registry.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `AgentRegistry` | Global class-level registry for agent factories | `step_executor.py`, CLI, gateway, tests, product registrations | `register()`, `resolve()`, `list_all()` | App boot (registration), flow execution (resolution) |
| `AgentRegistry.register()` | Register an agent factory under a normalized name | Product `__init__.py` modules, test fixtures | `AgentRegistry.register(name, factory, meta, descriptor)` | During product initialization |
| `AgentRegistry.resolve()` | Get fresh agent instance from factory | `step_executor.py` | `AgentRegistry.resolve(agent_name)` | When executing an agent step |
| `AgentRegistry.get_descriptor()` | Retrieve agent descriptor for governance | `GovernanceHooks`, advisory agents | `AgentRegistry.get_descriptor(name)` | Pre-execution governance checks |
| `AgentRegistry.list_all()` | List all registered agents with metadata | Gateway API, CLI | `AgentRegistry.list_all()` | Admin/debugging endpoints |
| `@agent` decorator | Marks classes for auto-discovery registration | Product agent implementations | `@agent(name="...", purpose="...")` | Class decoration at import time |

### llm_reasoner.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `LlmReasoner` | Core LLM agent with governance hooks + tracing | Registered as `"llm_reasoner"`, used by advisory agents | Subclassed or invoked directly | When flow needs LLM-based reasoning |
| `LlmReasoner.run()` | Execute LLM call with governance wrapper | StepExecutor | `agent.run(run_ctx, inputs)` | Agent step execution |
| `LlmReasoner._build_messages()` | Constructs chat messages from template | Internal | Called by `run()` | Before LLM invocation |
| `LlmReasoner._call_llm()` | Invokes model router with tracing | Internal | Called by `run()` | During LLM execution |

### critic_evaluator.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `CriticEvaluator` | Bounded critic for assessing agent reasoning | Reasoning lifecycle (CRITIQUE phase) | Registered and invoked as agent | When evaluating proposal quality |
| `CriticEvaluator.run()` | Evaluate reasoning with structured output | StepExecutor | `agent.run(run_ctx, {"reasoning": ..., "context_pack": ...})` | CRITIQUE phase of reasoning |
| `CriticOutput` | Pydantic model for critic results | `CriticEvaluator.run()` return | Parsed from LLM response | Result of critique |

### reasoning_ladder.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ReasoningLadder` | Multi-pass reasoning (INTERPRET→PROPOSE→SELECT) | Complex reasoning flows | Registered as agent | When multi-phase reasoning needed |
| `ReasoningLadder.run()` | Execute 3-phase reasoning | StepExecutor | `agent.run(run_ctx, inputs)` | Complex decision making |
| `ReasoningLadderConfig` | Configuration for ladder behavior | ReasoningLadder constructor | Pydantic model with max iterations | Agent initialization |

### advisory.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `AdvisoryAgent` | Base class for bounded advisory agents | `ToolSelector`, `AgentSelector`, `GapFinder`, etc. | Subclassed | Advisory agent implementations |

### advisors/tool_selector.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ToolSelector` | Recommends tools for a given task | Plan proposal phase | `agent.run(run_ctx, {"task": ..., "available_tools": ...})` | When selecting which tool to invoke |
| `ToolSelectorOutput` | Structured recommendations with rationale | Return type of ToolSelector | Pydantic model | Tool selection result |

### advisors/agent_selector.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `AgentSelector` | Recommends agents for a given task | Plan proposal phase | `agent.run(run_ctx, {"task": ..., "available_agents": ...})` | When selecting which agent to invoke |
| `AgentSelectorOutput` | Structured agent recommendations | Return type | Pydantic model | Agent selection result |

### advisors/gap_finder.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `GapFinder` | Identifies missing evidence/information | Sufficiency checking | `agent.run(run_ctx, {"context_pack": ...})` | When assessing evidence completeness |
| `GapFinderOutput` | List of identified gaps with priorities | Return type | Pydantic model | Gap analysis result |

### advisors/summarizer.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `Summarizer` | Generates concise summaries of evidence | Report generation, user explanations | `agent.run(run_ctx, {"content": ...})` | When summarizing for user |
| `SummarizerOutput` | Structured summary with key points | Return type | Pydantic model | Summary result |

### advisors/risk_explainer.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `RiskExplainer` | Explains identified risks to users | Risk reporting | `agent.run(run_ctx, {"risks": ...})` | When explaining detected risks |
| `RiskExplainerOutput` | Risk factors with severity and mitigations | Return type | Pydantic model | Risk explanation result |

---

## Component: core/config

Configuration loading, validation, and schema definitions.

### loader.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `load_settings()` | Main entry point for loading/merging all configs | Gateway API/CLI startup, tests | `settings = load_settings(config_dir)` | Application initialization |
| `_load_yaml()` | Load and parse a YAML file | Internal | Called for each config file | During settings loading |
| `_merge_dicts()` | Deep merge configuration dictionaries | Internal | Merge base + overrides | Config precedence resolution |
| `_apply_env_overrides()` | Apply MASTER__ env var overrides | Internal | Called after YAML loading | Environment-specific config |
| `_hydrate_secrets()` | Inject secrets into provider configs | Internal | After loading secrets.yaml | API key injection |

### schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `Settings` | Top-level Pydantic container for all config | Throughout codebase | Validated from dict | Config validation |
| `AppConfig` | Application-level settings (host, port, debug) | API server, paths | `settings.app` | Server configuration |
| `PoliciesConfig` | Governance limits and per-product overrides | PolicyEngine, GovernanceHooks | `settings.policies` | Policy enforcement |
| `ModelRoutingConfig` | Model selection and routing rules | ModelRouter | `settings.models` | LLM routing |
| `OpenAIConfig` | OpenAI-specific provider settings | OpenAIProvider | `settings.models.openai` | OpenAI API calls |
| `LoggingConfig` | Logging and tracing configuration | Tracer, SecurityRedactor | `settings.logging` | Log/trace setup |
| `ProductsConfig` | Product discovery settings | ProductLoader | `settings.products` | Product enumeration |

---

## Component: core/contracts

Pydantic schema definitions providing stable data contracts across the platform.

### action_plan_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ActionPlanStep` | A step in a plan proposal (pre-execution) | `plan_executor.py`, governance, tests | Pydantic model instantiation | Plan generation |
| `ActionPlanStepApproval` | Approval record for a plan step | Tests | Pydantic model | Plan approval tracking |
| `PlanCost` | Cost estimation for a plan | `plan_executor.py`, governance | Pydantic model | Cost budgeting |
| `ActionPlanProposal` | Complete plan with steps and cost | `plan_executor.py`, governance | Pydantic model | Plan proposal output |
| `ToolCallStep` | Plan step calling a tool | `plan_executor.py`, tests | Pydantic model | Tool step definition |
| `AgentCallStep` | Plan step calling an agent | `plan_executor.py`, governance | Pydantic model | Agent step definition |
| `ActionPlan` | Executable action plan with metadata | `plan_executor.py`, tests | Pydantic model | Plan execution |
| `PlanGateResult` | Result of plan gate evaluation | `plan_executor.py`, governance | Pydantic model | Gate evaluation output |

### agent_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `AgentCategory` | Enum categorizing agent types | Agent registry, tests | Enum access | Agent classification |
| `AgentErrorCode` | Standard error codes for agent failures | All agent implementations | Enum access | Error handling |
| `AgentMeta` | Metadata about agent run (timing, costs) | All agents | Pydantic model | Run metadata |
| `AgentError` | Structured error for agent failures | All agents | Pydantic model | Error reporting |
| `AgentResultEnvelope` | Generic envelope for agent results | Base class for AgentResult | Pydantic model | Result wrapping |
| `detect_control_injection()` | Detects control flow injection attempts | Input validation | Function call | Security check |

### budget_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ExecutionBudget` | Budget for passes, tool calls, cost | Governance, orchestrator | Pydantic model | Budget definition |
| `BoundedReasoningBudget` | Budget with HITL escalation | Reasoning lifecycle | Pydantic model | Reasoning budget |
| `BudgetState` | Runtime state tracking consumption | Budgeting module, governance | Pydantic model | Budget tracking |
| `BudgetPolicy` | Policy defining default and overrides | Settings, governance | Pydantic model | Policy configuration |

### context_pack_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ContextPackFrozenError` | Exception for frozen pack modifications | ContextPack mutations, tests | Exception raise | Write protection |
| `EvidenceSource` | Source provenance (tool, uri, ref) | Evidence tracking | Pydantic model | Provenance |
| `EvidenceItem` | Evidence with type, source, confidence | Knowledge, retrieval | Pydantic model | Evidence storage |
| `TableSummary` | Summary of table evidence | Knowledge, tests | Pydantic model | Table metadata |
| `DocumentSummary` | Summary of document evidence | Knowledge, tests | Pydantic model | Document metadata |
| `ContextPack` | Main evidence container | Knowledge, orchestrator, agents | Pydantic model | Context aggregation |
| `ContextPack.freeze()` | Make context immutable, return hash | Before execution | Method call | Integrity guarantee |
| `ContextPackConfig` | Configuration for context pack building | Knowledge, tests | Pydantic model | Build configuration |

### critic_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `MissingEvidenceRequest` | Request for specific missing evidence | CriticEvaluator, gap finding | Pydantic model | Gap identification |
| `CriticOutput` | Output of critic evaluation | CriticEvaluator, tests | Pydantic model | Critique result |
| `CriticFailure` | Structured failure for critic errors | CriticEvaluator | Pydantic model | Error handling |
| `CriticResultEnvelope` | Envelope for critic output | CriticEvaluator, tests | Pydantic model | Result wrapping |

### flow_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `BranchCondition` | Deterministic condition for branching | `branching.py`, flow definitions | Pydantic model | Branch evaluation |
| `ConfidenceThresholdCondition` | Stop condition based on confidence | `looping.py` | Pydantic model | Loop termination |
| `NoMissingEvidenceCondition` | Stop when no missing evidence | `looping.py` | Pydantic model | Loop termination |
| `StopConditionGroup` | Group of stop conditions with logic | `looping.py` | Pydantic model | Compound conditions |
| `LoopState` | Runtime state for bounded loops | `loop_executor.py` | Pydantic model | Loop tracking |
| `StepType` | Enum for step types (AGENT, TOOL, etc.) | Flow definitions, orchestrator | Enum access | Step classification |
| `FlowAutonomy` | Enum for flow autonomy level | Flow definitions, governance | Enum access | Autonomy control |
| `ExecutionBackend` | Enum for execution backend | Tools, flow definitions | Enum access | Backend selection |
| `RetryPolicy` | Retry policy for steps | `error_policy.py`, flow definitions | Pydantic model | Retry configuration |
| `StepDef` | Declarative step definition | FlowLoader, StepExecutor | Pydantic model | Step specification |
| `ToolBatchItem` | Item in a tool batch | Tool batch execution | Pydantic model | Batch definition |
| `FlowDef` | Declarative flow definition | FlowLoader, orchestrator | Pydantic model | Flow specification |

### hypothesis_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `HypothesisSetFrozenError` | Exception for frozen set modifications | HypothesisSet, tests | Exception raise | Write protection |
| `EvidenceRef` | Reference to supporting evidence | HypothesisSet | Pydantic model | Evidence linking |
| `Hypothesis` | Individual hypothesis with confidence | HypothesisSet, tests | Pydantic model | Hypothesis storage |
| `HypothesisSet` | Collection of hypotheses with freeze | `hypothesis_selector.py`, tests | Pydantic model | Hypothesis management |
| `HypothesisSet.freeze()` | Make set immutable | Before execution | Method call | Integrity guarantee |
| `HypothesisSet.top()` | Get highest confidence hypothesis | Hypothesis selection | Method call | Selection |

### run_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `RunStatus` | Enum for run lifecycle status | Memory backends, orchestrator | Enum access | Status tracking |
| `StepStatus` | Enum for step lifecycle status | Memory backends, orchestrator | Enum access | Step tracking |
| `OutcomeClass` | Enum for terminal outcome | Run finalization | Enum access | Outcome classification |
| `OutcomeReason` | Enum for terminal outcome reason | Run finalization | Enum access | Reason classification |
| `Versions` | Version tracking for reproducibility | RunRecord, tests | Pydantic model | Version capture |
| `ArtifactRef` | Reference to persisted artifact | RunContext, memory, tests | Pydantic model | Artifact linking |
| `TraceEvent` | Single trace event during run | Memory backends, tests | Pydantic model | Event storage |
| `StepRecord` | Persistent record of step execution | Memory backends, tests | Pydantic model | Step persistence |
| `RunRecord` | Persistent record of flow run | Memory backends, orchestrator | Pydantic model | Run persistence |
| `RunError` | Structured error for run operations | Gateway API | Pydantic model | Error reporting |
| `RunResultEnvelope` | Envelope for run results | Gateway API, tests | Pydantic model | Result wrapping |

### semantic_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `SemanticDecision` | Enum for orchestrator control flow | Semantic phase, orchestrator | Enum access | Decision routing |
| `ExtractedEntity` | Extracted entity from user input | Semantic interpretation | Pydantic model | Entity extraction |
| `SemanticEnvelope` | Structured interpretation result | `normalization.py`, orchestrator | Pydantic model | Semantic output |
| `ClarificationNeeded` | Response for user clarification | Semantic phase | Pydantic model | Clarification request |
| `AbortResponse` | Response when run must abort | Semantic phase | Pydantic model | Abort signal |

### sufficiency_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `GapPriority` | Enum for gap priority levels | SufficiencyManager | Enum access | Gap prioritization |
| `UnknownImportance` | Enum for unknown importance | SufficiencyManager | Enum access | Unknown classification |
| `Fact` | Verified evidence with confidence | SufficiencyState, tests | Pydantic model | Fact tracking |
| `Unknown` | Unresolved question | SufficiencyState, tests | Pydantic model | Unknown tracking |
| `Assumption` | Assumed fact with confidence | SufficiencyState, tests | Pydantic model | Assumption tracking |
| `Gap` | Missing information with priority | SufficiencyState, tests | Pydantic model | Gap tracking |
| `SufficiencyState` | Aggregate state tracking | SufficiencyManager, tests | Pydantic model | Sufficiency aggregate |
| `SufficiencyState.is_sufficient()` | Check if no blocking gaps | Sufficiency checking | Method call | Sufficiency evaluation |

### tool_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ToolErrorCode` | Enum for tool error codes | All tool implementations | Enum access | Error classification |
| `ToolMeta` | Metadata about tool execution | All tools | Pydantic model | Execution metadata |
| `ToolError` | Structured error for tool failures | All tools | Pydantic model | Error reporting |
| `ToolResultEnvelope` | Generic envelope for tool results | Base class for ToolResult | Pydantic model | Result wrapping |
| `ToolResult` | Concrete tool result envelope | ToolExecutor, all tools | Pydantic model | Standard result |

### user_input_schema.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `InputChoice` | Option in a choice input | UserInputPrompt | Pydantic model | Choice definition |
| `UserInputPrompt` | Prompt for user input | Gateway API, HITL | Pydantic model | Input prompting |
| `UserInputAnswer` | User's answer to a prompt | Gateway API | Pydantic model | Answer capture |
| `UserInputRequest` | Request for user input | `user_input_handler.py`, HITL | Pydantic model | Input request |
| `UserInputResponse` | User's response to request | `user_input_handler.py` | Pydantic model | Response capture |
| `InputModes` | Constants for input modes | UserInputRequest | Class constants | Mode selection |

### descriptors_schema.py (V1.4)

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ToolDescriptor` | Read-only catalog descriptor for tools | ToolRegistry, DiscoveryEngine | Frozen Pydantic model | Tool discovery |
| `ToolDescriptor.to_json_schema()` | JSON serialization for external tooling | API, external tools | Method call | Schema export |
| `AgentDescriptor` | Read-only catalog descriptor for agents | AgentRegistry, DiscoveryEngine | Frozen Pydantic model | Agent discovery |
| `AgentDescriptor.to_json_schema()` | JSON serialization for external tooling | API, external tools | Method call | Schema export |
| `SensitivityClass` | Enum for sensitivity classification | ToolDescriptor, AgentDescriptor | Enum access | Security classification |
| `CostHint` | Enum for cost estimation hints | ToolDescriptor, AgentDescriptor | Enum access | Cost budgeting |
| `ReasoningType` | Enum for agent reasoning strategy | AgentDescriptor | Enum access | Agent classification |

### gate_schema.py (V1.4)

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `GateRejectionArtifact` | Structured artifact for gate rejection events | GateRegistry, Tracing | Frozen Pydantic model | Rejection tracing |
| `GateRejectionSeverity` | Severity level of gate rejection | GateRejectionArtifact | Enum access | Severity classification |
| `GateRejectionStore` | Storage for gate rejection artifacts | Memory backends | `store.save(artifact)` | Artifact persistence |
| `create_rejection_artifact()` | Factory for rejection artifacts | Gate implementations | Function call | Artifact creation |

### decision_schema.py (V1.4)

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DecisionRecord` | Captures each decision point with full context | Reasoning lifecycle, memory | Frozen Pydantic model | Decision audit |
| `DecisionType` | Enum for decision types | DecisionRecord | Enum access | Decision classification |
| `DecisionChain` | Queryable chain of decisions for a run | Memory backends, explainability | Pydantic model | Decision querying |
| `DecisionRecorder` | Records decisions to memory backend | Reasoning lifecycle | `recorder.record(decision)` | Decision persistence |
| `DecisionRecorder.record()` | Record a decision with evidence | Reasoning phases | Method call | Each decision point |
| `Option` | Single option considered during decision | DecisionRecord.options_considered | Frozen dataclass | Option representation |
| `DECISION_RECORDED` | Trace event type | Tracing | Event kind | Decision emission |

---

## Component: core/governance

Policy enforcement, security, and budget management.

### hooks.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `GovernanceHooks` | Main integration point for orchestrator | OrchestratorEngine, StepExecutor | Injected dependency | All governance checks |
| `GovernanceHooks.before_step()` | Pre-step governance check | StepExecutor | `hooks.before_step(run_ctx, step)` | Before each step |
| `GovernanceHooks.after_step()` | Post-step governance check | StepExecutor | `hooks.after_step(run_ctx, step, result)` | After each step |
| `GovernanceHooks.before_tool_call()` | Pre-tool governance check | ToolExecutor | `hooks.before_tool_call(tool_name, ctx)` | Before tool execution |
| `GovernanceHooks.check_budget()` | Budget availability check | Step/tool execution | `hooks.check_budget(run_ctx)` | Budget enforcement |
| `GovernanceHooks.consume_budget()` | Decrement budget counters | After tool/step | `hooks.consume_budget(run_ctx, cost)` | Budget tracking |

### policies.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `PolicyEngine` | Tool/model allow/deny evaluation | GovernanceHooks | `engine.is_tool_allowed(tool_name, product)` | Policy evaluation |
| `PolicyEngine.is_tool_allowed()` | Check tool against allowlist/blocklist | GovernanceHooks | Boolean return | Tool authorization |
| `PolicyEngine.is_model_allowed()` | Check model against allowlist/blocklist | GovernanceHooks | Boolean return | Model authorization |
| `PolicyEngine.check_autonomy()` | Validate autonomy level permitted | GovernanceHooks | Boolean return | Autonomy check |
| `PolicyEngine.get_effective_limits()` | Resolve limits with product overrides | GovernanceHooks | Returns limit dict | Limit resolution |

### security.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `SecurityRedactor` | PII/secret scrubbing from outputs | Tracer, ToolExecutor | `redactor.redact(text)` | Output sanitization |
| `SecurityRedactor.redact()` | Apply regex patterns to scrub data | Tracing, logging | String return | Before persistence/logging |
| `SecurityRedactor.add_pattern()` | Register additional redaction patterns | Configuration | Method call | Pattern extension |
| `DEFAULT_PATTERNS` | Built-in patterns (API keys, emails) | SecurityRedactor initialization | List constant | Default patterns |

### budgeting.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `init_budget_state()` | Initialize budget state from policy | Run start | `state = init_budget_state(policy, product)` | Run initialization |
| `consume_budget()` | Decrement budget counters | GovernanceHooks | `consume_budget(state, steps=1, tokens=100)` | After resource use |
| `check_budget_available()` | Verify budget not exhausted | GovernanceHooks | Boolean return | Pre-execution check |
| `get_remaining_budget()` | Query remaining resources | Budgeting UI, logging | Returns BudgetState | Budget inspection |

### gates.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `BranchGate` | Evaluates branch conditions | GovernanceHooks | `gate.evaluate(condition, ctx)` | Branch step execution |
| `LoopGate` | Evaluates loop stop conditions | GovernanceHooks | `gate.evaluate(condition, ctx)` | Loop iteration check |
| `PlanGate` | Evaluates action plan against policy | `plan_executor.py` | `gate.evaluate(plan, policy)` | Plan approval |
| `CriticGate` | Evaluates critic output thresholds | Reasoning lifecycle | `gate.evaluate(critic_output)` | Critique threshold |

### self_modification_guard.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `SelfModificationGuard` | Prevents agent self-modification | GovernanceHooks | `guard.check(agent_output)` | Post-agent check |
| `SelfModificationGuard.check()` | Detect code modification attempts | GovernanceHooks | Raises exception on violation | Agent output validation |
| `FORBIDDEN_PATTERNS` | Patterns indicating self-modification | SelfModificationGuard | List constant | Pattern matching |

### semantic_gate.py (V1.4)

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `SemanticGate` | Unified gate for semantic envelope validation | GovernanceHooks, plan_executor | `gate.validate(envelope, sufficiency_state, confidence_threshold)` | Semantic phase exit |
| `SemanticGate.validate()` | Validate envelope completeness, confidence, sufficiency | GovernanceHooks | Returns `SemanticGateResult` | Before plan execution |
| `SemanticGateResult` | Structured result with all validation outcomes | SemanticGate return | Frozen dataclass | Gate evaluation output |
| `SemanticGateResult.to_trace_payload()` | Convert to trace event payload | Tracing | Dict return | Trace emission |

### hitl_binding.py (V1.4)

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `HITLBinding` | Immutable HITL configuration | Product registration, GovernanceHooks | Frozen dataclass | HITL enforcement |
| `EscalationPath` | Trigger conditions and escalation targets | HITLBinding | Frozen dataclass | Escalation routing |
| `EscalationTrigger` | Enum for HITL trigger types | EscalationCondition | Enum access | Trigger matching |
| `EscalationAction` | Enum for escalation actions | EscalationPath | Enum access | Action selection |
| `EscalationCondition` | Condition that triggers HITL escalation | EscalationPath | Frozen dataclass | Trigger evaluation |
| `EscalationCondition.matches()` | Check if condition matches context | Escalation evaluation | Boolean return | Condition matching |
| `HITLBindingRegistry` | Registry for HITL bindings | GovernanceHooks | Singleton registry | Binding lookup |
| `HITLBindingRegistry.register()` | Register immutable HITL binding | Product initialization | Method call | Boot time registration |
| `HITLBindingRegistry.get_binding()` | Get binding for product/trigger | GovernanceHooks | Method call | Escalation lookup |
| `HITLPriority` | Priority levels for escalations | EscalationPath | Enum access | Priority ordering |

### pii_detector.py (V1.4)

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `PIIDetector` | Pattern and NER-based PII detection | SecurityRedactor, GovernanceHooks | `detector.detect(text)` | Output sanitization |
| `PIIDetector.detect()` | Detect all PII entities in text | SecurityRedactor | Returns list of PIIEntity | Before output |
| `PIIDetector.redact()` | Detect and redact PII | SecurityRedactor | Returns redacted text | Output scrubbing |
| `PIIEntity` | Detected PII entity with metadata | PIIDetector return | Frozen dataclass | Entity representation |
| `PIIEntityType` | Enum for PII entity types | PIIEntity | Enum access | Entity classification |
| `PIISensitivity` | Sensitivity level of PII | PIIEntity | Enum access | Sensitivity classification |
| `PIIMatch` | Pattern match representation | PIIDetector internals | Frozen dataclass | Pattern matching |

### evidence_requirements.py (V1.4)

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `EvidenceValidator` | Validates decisions have required evidence | GovernanceHooks, reasoning_lifecycle | `validator.validate(decision, evidence)` | Decision validation |
| `EvidenceValidator.validate()` | Check evidence satisfies requirements | Decision recording | Returns validation result | Before decision commit |
| `EvidenceRequirement` | Model for required evidence per decision type | EvidenceValidator | Frozen dataclass | Requirement definition |
| `EvidenceRequirement.is_satisfied_by()` | Check if requirement satisfied by evidence | EvidenceValidator | Boolean return | Requirement matching |
| `EvidenceType` | Enum for evidence types | EvidenceRequirement | Enum access | Type classification |
| `propagate_evidence_confidence()` | Propagate evidence confidence to decision | Confidence aggregation | Function call | Confidence flow |
| `detect_missing_evidence()` | Detect missing required evidence | Gap analysis | Returns list | HITL trigger |

---

## Component: core/knowledge

Knowledge retrieval, context management, and evidence handling.

### vector_store.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `VectorStoreInterface` | Abstract vector store interface | Implementations, retriever | Abstract base class | Interface definition |
| `VectorStoreInterface.add()` | Add vectors to store | Indexing | Abstract method | Document ingestion |
| `VectorStoreInterface.search()` | Semantic similarity search | Retrieval | Abstract method | Query execution |
| `SqliteVectorStore` | In-memory vector store implementation | Default implementation, tests | `store = SqliteVectorStore()` | Lightweight deployment |
| `SqliteVectorStore.search()` | Search with cosine similarity | Retriever | `store.search(query_vec, top_k)` | Retrieval queries |

### retriever.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `Retriever` | High-level retrieval orchestration | Knowledge tools, agents | `retriever.retrieve(query, filters)` | Evidence gathering |
| `Retriever.retrieve()` | Execute retrieval with filters | Retrieval tool | Returns list of EvidenceItem | Query execution |
| `Retriever.retrieve_batch()` | Batch retrieval for efficiency | Batch operations | Returns list of results | Multiple queries |
| `RetrievalConfig` | Configuration for retrieval | Retriever constructor | Pydantic model | Retriever setup |

### context_pack.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `build_context_pack()` | Compile evidence into ContextPack | Orchestrator, agents | `pack = build_context_pack(evidence_list, config)` | Evidence aggregation |
| `add_evidence()` | Add evidence to existing pack | Context pack mutation | `add_evidence(pack, evidence)` | Evidence addition |
| `summarize_table()` | Generate TableSummary from data | Table evidence processing | Returns TableSummary | Table summarization |
| `summarize_document()` | Generate DocumentSummary from text | Document evidence processing | Returns DocumentSummary | Document summarization |

### context_pack_merge.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `merge_context_packs()` | Combine multiple packs into one | Multi-source aggregation | `merged = merge_context_packs([pack1, pack2])` | Pack consolidation |
| `deduplicate_evidence()` | Remove duplicate evidence items | Merge operations | Internal function | During merge |

### sufficiency_manager.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `SufficiencyManager` | Track facts, unknowns, gaps, assumptions | Reasoning lifecycle | `manager.update(new_evidence)` | Sufficiency tracking |
| `SufficiencyManager.add_fact()` | Record verified evidence | Evidence confirmation | Method call | Fact addition |
| `SufficiencyManager.add_unknown()` | Record unresolved question | Gap analysis | Method call | Unknown addition |
| `SufficiencyManager.add_gap()` | Record missing information | Gap analysis | Method call | Gap addition |
| `SufficiencyManager.is_sufficient()` | Check if sufficient for decision | Sufficiency evaluation | Boolean return | Decision gate |
| `SufficiencyManager.get_blocking_gaps()` | Get high-priority gaps | Gap prioritization | Returns list | Gap resolution |

### hypothesis_selector.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `select_hypothesis()` | Select best hypothesis with audit | Reasoning conclusion | `selected = select_hypothesis(hypothesis_set, ctx)` | Hypothesis selection |
| `rank_hypotheses()` | Rank hypotheses by confidence | Selection process | Returns sorted list | Ranking |
| `record_selection_audit()` | Create audit trail for selection | Explainability | Returns audit record | Audit logging |

### confidence.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `aggregate_confidence()` | Combine multiple confidence scores | Evidence aggregation | `agg = aggregate_confidence([0.8, 0.9])` | Confidence combination |
| `evaluate_against_threshold()` | Compare confidence to threshold | Decision gates | Boolean return | Threshold evaluation |
| `decay_confidence()` | Apply time-based confidence decay | Stale evidence handling | Returns decayed score | Age adjustment |
| `ConfidenceMethod` | Enum for aggregation methods | Configuration | Enum access | Method selection |

### base.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `KnowledgeBase` | Abstract knowledge base interface | Implementations | Abstract base class | Interface definition |
| `KnowledgeBase.query()` | Query knowledge base | Retrieval | Abstract method | Knowledge queries |

### structured.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `StructuredKnowledgeBase` | Structured data knowledge base | Schema-aware queries | Implementation | Structured retrieval |

### discovery_engine.py (V1.4)

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DiscoveryEngine` | Main discovery orchestrator for tools/agents | Reasoning lifecycle, plan_executor | `engine.discover_tools(intent, context)` | Intent-based discovery |
| `DiscoveryEngine.discover_tools()` | Intent-filtered tool discovery | Plan proposal phase | Returns list of ToolCandidate | Tool selection |
| `DiscoveryEngine.discover_agents()` | Intent-filtered agent discovery | Plan proposal phase | Returns list of AgentCandidate | Agent delegation |
| `DiscoveryEngine.select_tool()` | Select best tool from candidates | Plan execution | Returns ToolCandidate | Tool execution |
| `DiscoveryEngine.select_agent()` | Select best agent from candidates | Agent delegation | Returns AgentCandidate | Agent execution |
| `ToolCandidate` | Tool discovered as potentially suitable | DiscoveryEngine return | Frozen dataclass | Candidate representation |
| `AgentCandidate` | Agent discovered as potentially suitable | DiscoveryEngine return | Frozen dataclass | Candidate representation |
| `DiscoveryResult` | Result of discovery phase | DiscoveryEngine.discover_* return | Frozen dataclass | Discovery output |
| `SelectionResult` | Result of selection phase | DiscoveryEngine.select_* return | Frozen dataclass | Selection output |
| `DiscoveryStrategy` | ABC for extensible discovery | Strategy pattern | Abstract base class | Discovery customization |
| `DefaultDiscoveryStrategy` | Default tag-based discovery | DiscoveryEngine default | Strategy implementation | Default discovery |
| `EligibilityChecker` | Check candidate eligibility | Discovery filtering | `checker.check_eligibility(candidate, context)` | Candidate validation |
| `EligibilityResult` | Result of eligibility check | EligibilityChecker return | Dataclass | Eligibility output |
| `match_capabilities()` | Tag-based capability scoring | DiscoveryStrategy | Function call | Capability matching |
| `_compute_discovery_hash()` | Deterministic hash for discovery | DiscoveryResult | Function call | Reproducibility |

---

## Component: core/memory

Persistence, tracing, and observability infrastructure.

### base.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `MemoryBackend` | Abstract persistence interface | Implementations, MemoryRouter | Abstract base class | Interface definition |
| `MemoryBackend.save_run()` | Persist run record | Implementations | Abstract method | Run persistence |
| `MemoryBackend.get_run()` | Retrieve run record | Implementations | Abstract method | Run retrieval |
| `MemoryBackend.list_runs()` | List run records | Implementations | Abstract method | Run listing |
| `MemoryBackend.save_step()` | Persist step record | Implementations | Abstract method | Step persistence |
| `MemoryBackend.save_event()` | Persist trace event | Implementations | Abstract method | Event persistence |

### in_memory.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `InMemoryBackend` | Ephemeral implementation for testing | Tests, development | `backend = InMemoryBackend()` | Test fixtures |
| `InMemoryBackend.save_run()` | Store run in dict | Testing | Dict storage | Test persistence |
| `InMemoryBackend.get_run()` | Retrieve run from dict | Testing | Dict lookup | Test retrieval |
| `InMemoryBackend.clear()` | Reset all storage | Test fixtures | Method call | Test cleanup |

### sqlite_backend.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `SQLiteBackend` | Durable SQLite implementation | Production, persistence | `backend = SQLiteBackend(db_path)` | Production use |
| `SQLiteBackend.save_run()` | Persist run to SQLite | Production | INSERT/UPDATE | Run persistence |
| `SQLiteBackend.get_run()` | Retrieve run from SQLite | Production | SELECT | Run retrieval |
| `SQLiteBackend.list_runs()` | Query runs with filters | Production | SELECT with pagination | Run listing |
| `SQLiteBackend._ensure_schema()` | Create tables if missing | Initialization | DDL execution | First connection |

### router.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `MemoryRouter` | Façade delegating to chosen backend | Orchestrator, gateway | `router = MemoryRouter(backends)` | Backend abstraction |
| `MemoryRouter.save_run()` | Delegate to active backend | Orchestrator | Method delegation | Run persistence |
| `MemoryRouter.get_run()` | Delegate to active backend | Gateway | Method delegation | Run retrieval |
| `MemoryRouter.set_backend()` | Switch active backend | Configuration | Method call | Backend selection |

### tracing.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `Tracer` | Pipeline for trace events | Orchestrator, agents | `tracer.emit(event)` | Event emission |
| `Tracer.emit()` | Process and persist trace event | Throughout codebase | Method call | Event logging |
| `TraceEventKind` | Enum of all trace event types | Event classification | Enum access | Event typing |
| `TracerConfig` | Configuration for tracer behavior | Tracer constructor | Pydantic model | Tracer setup |
| `scrub_trace_event()` | Apply security redaction | Tracer pipeline | Internal function | Pre-persistence |

### observability_store.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ObservabilityStore` | File-based observability storage | Run artifacts, outputs | `store.save(run_id, data)` | Artifact persistence |
| `ObservabilityStore.save()` | Write data to observability dir | Run completion | File write | Output persistence |
| `ObservabilityStore.load()` | Read data from observability dir | History viewing | File read | Output retrieval |
| `ObservabilityStore.get_run_dir()` | Get run-specific directory | File organization | Path return | Directory resolution |

### explainability.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ExplanationArtifact` | Complete explanation for a run | Explainability | Pydantic model | Explanation storage |
| `generate_run_explanation()` | Generate explanation from run data | Run completion | `explanation = generate_run_explanation(run_record, events)` | Post-run |
| `ReasoningStep` | Step in reasoning chain | ExplanationArtifact | Pydantic model | Reasoning trace |
| `EvidenceReference` | Reference to evidence used | ReasoningStep | Pydantic model | Evidence linking |
| `DecisionRecord` | Decision made during reasoning | ReasoningStep | Pydantic model | Decision trace |

### reproducibility.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `capture_versions()` | Record all component versions | Run start | `versions = capture_versions()` | Version capture |
| `verify_reproducibility()` | Check run can be reproduced | Replay validation | Boolean return | Reproducibility check |
| `ReproducibilityReport` | Report on reproducibility status | Verification | Pydantic model | Report generation |

---

## Component: core/models

Model routing and provider abstraction for LLM access.

### router.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ModelRouter` | Centralized model selection | Agents, LLM calls | `router.select(product, purpose)` | Model selection |
| `ModelRouter.select()` | Select model based on rules | LLM invocation | Returns ModelSelection | Pre-LLM call |
| `ModelRouter.call()` | Execute LLM call via provider | Agents | `router.call(messages, model)` | LLM execution |
| `ModelSelection` | Selected provider + model strings | ModelRouter return | Dataclass | Selection result |
| `ModelRoutingRule` | Rule for model selection | Configuration | Pydantic model | Rule definition |

### providers/__init__.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ModelProvider` | Abstract provider interface | Implementations | Abstract base class | Interface definition |
| `ModelProvider.call()` | Execute LLM call | Implementations | Abstract method | LLM invocation |

### providers/openai_provider.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `OpenAIProvider` | Provider adapter for OpenAI API | ModelRouter | `provider.call(request)` | OpenAI calls |
| `OpenAIProvider.call()` | Execute OpenAI API call | ModelRouter | Method call | API invocation |
| `OpenAIRequest` | Request schema for OpenAI | OpenAIProvider | Pydantic model | Request building |
| `OpenAIResponse` | Response schema for OpenAI | OpenAIProvider | Pydantic model | Response parsing |
| `_build_headers()` | Construct API headers | Internal | Header dict | Authentication |
| `_handle_error()` | Error handling for API calls | Internal | Exception handling | Error processing |

---

## Component: core/orchestrator

Flow execution engine and step processing.

### engine.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `OrchestratorEngine` | Main orchestrator entrypoint | Gateway API, CLI, tests | `engine.start_run(product, flow, payload)` | Run orchestration |
| `OrchestratorEngine.start_run()` | Start new flow execution | Gateway API, CLI | Method call | User-initiated run |
| `OrchestratorEngine.get_run()` | Retrieve run state and steps | Gateway API | Method call | Status queries |
| `OrchestratorEngine.get_pending_input()` | Get pending user input prompt | Gateway API | Method call | UI polling |
| `OrchestratorEngine.resume()` | Resume paused run | Gateway API | Method call | User approval/input |
| `OrchestratorEngine.from_settings()` | Factory from Settings | Gateway layer | Classmethod | App startup |
| `_generate_run_id()` | Generate unique run ID | Internal | UUID generation | Run initialization |
| `_compute_payload_size()` | Calculate JSON payload size | Internal | Size check | Payload validation |

### context.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `RunContext` | Request-scoped runtime context | StepExecutor, agents, tools | Dataclass | Run lifetime |
| `RunContext.emit()` | Emit trace events | Throughout orchestrator | `ctx.emit(event_kind, data)` | Event emission |
| `RunContext.build_step_context()` | Create StepContext | StepExecutor | Method call | Step execution |
| `StepContext` | Execution context for single step | Agents, tools | Dataclass | Step lifetime |
| `StepContext.emit()` | Emit step-scoped trace events | Agents, tools | Method call | Step events |
| `TraceEmitter` | Callable type for trace emission | Type annotation | TypeAlias | Type safety |

### flow_loader.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `FlowLoader` | Load and validate FlowDef | OrchestratorEngine, tests | `loader.load(product, flow)` | Flow loading |
| `FlowLoader.load()` | Load flow by product/flow name | Engine | Method call | Run start |
| `FlowLoader.load_from_file()` | Load flow from file path | Tests, tools | Static method | Direct loading |
| `FlowLoader.validate()` | Validate raw dict into FlowDef | Internal | Static method | Post-parse |
| `FlowLoadError` | Exception for load failures | Callers | Exception | Error handling |

### step_executor.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `StepExecutor` | Executes individual steps | OrchestratorEngine | `executor.execute(ctx, step)` | Step execution |
| `StepExecutor.execute()` | Main step dispatcher | Engine step loop | Method call | Each step |
| `StepExecutor._execute_tool()` | Execute tool with retry | Internal | Tool step handling | TOOL step type |
| `StepExecutor._execute_batch()` | Execute tool batch | Internal | Batch handling | TOOL_BATCH type |
| `build_step_context()` | Build StepContext from run | External callers | Function call | Context creation |

### plan_executor.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `handle_plan_propose()` | Handle PLAN_PROPOSE step | StepExecutor | Function call | Plan generation |
| `handle_plan_gate()` | Handle PLAN_GATE step | StepExecutor | Function call | Plan evaluation |
| `handle_plan_execute()` | Handle PLAN_EXECUTE step | StepExecutor | Function call | Plan execution |
| `execute_plan()` | Execute approved plan steps | Internal | Function call | Plan running |
| `store_plan_artifact()` | Store plan in context | Plan handlers | Function call | Plan storage |
| `get_plan_artifact()` | Retrieve plan from context | Plan handlers | Function call | Plan retrieval |

### loop_executor.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `handle_repeat_until()` | Handle REPEAT_UNTIL step | StepExecutor | Function call | Loop execution |
| `get_or_init_loop_state()` | Initialize loop state | Internal | Function call | Loop start |
| `persist_loop_state()` | Save loop state | Internal | Function call | State update |
| `check_and_consume_loop_budget()` | Validate loop budget | Internal | Function call | Each iteration |

### run_lifecycle.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `transition_run_status()` | Validate and execute status transition | Engine | Function call | Status changes |
| `start_run()` | Initialize run record | Engine | Function call | Run start |
| `complete_run()` | Mark run completed | Engine | Function call | Successful completion |
| `fail_run()` | Mark run failed | Engine | Function call | Run failure |
| `write_final_response()` | Write output to observability | Internal | Function call | Run finalization |

### reasoning_lifecycle.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ReasoningLifecycle` | 4-phase reasoning manager | Reasoning agents | Class instantiation | Reasoning run |
| `ReasoningLifecycle.transition()` | Move to new phase | Reasoning flow | Method call | Phase changes |
| `ReasoningLifecycle.set_output()` | Set phase output | Reasoning agents | Method call | Phase completion |
| `ReasoningLifecycle.terminate()` | End reasoning early | Reasoning flow | Method call | Early termination |
| `TerminationReason` | Enum for termination causes | ReasoningLifecycle | Enum access | Termination handling |
| `PhaseTransition` | Transition record | ReasoningLifecycle | Dataclass | Transition logging |

### state.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `RunState` | Finite-state machine states | Transition logic | Enum | State machine |
| `TERMINAL_RUN_STATUSES` | Terminal status set | Status checks | FrozenSet | Status classification |
| `ACTIVE_RUN_STATUSES` | Active status set | Status checks | FrozenSet | Status classification |
| `run_status_to_state()` | Convert RunStatus to RunState | Transitions | Function call | Status conversion |
| `is_valid_transition()` | Check transition validity | run_lifecycle | Function call | Transition validation |

### branching.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `evaluate_condition()` | Evaluate branch condition tree | StepExecutor, gates | `evaluate_condition(cond, ctx)` | Branch evaluation |
| `extract_value()` | Extract value from context by path | Internal | Function call | Value resolution |
| `summarize_condition()` | Human-readable condition summary | Tracing | Function call | Debug output |

### looping.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `evaluate_stop_condition()` | Evaluate loop stop conditions | loop_executor | Function call | Iteration check |
| `summarize_stop_condition()` | Human-readable summary | Tracing | Function call | Debug output |

### normalization.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `normalize_whitespace()` | Collapse whitespace in text | Input normalization | Function call | Text cleanup |
| `deduplicate_entities()` | Remove duplicate entities | Semantic phase | Function call | Entity cleanup |
| `merge_constraints()` | Deep merge constraint dicts | Semantic phase | Function call | Constraint handling |
| `normalize_envelope()` | Full normalization pipeline | Semantic phase | Function call | Before step execution |
| `coerce_value()` | Type coercion (str→int, etc.) | Schema handling | Function call | Type conversion |

### templating.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `render_strict()` | Strict template rendering | Message rendering | `render_strict(template, context)` | Agent prompts |
| `render_messages()` | Render list of message dicts | Agent calls | Function call | LLM message prep |
| `render_lenient()` | Lenient template rendering | Tool params | Function call | Parameter resolution |
| `resolve_path()` | Resolve dot-path in context | Internal | Function call | Value lookup |

### hitl.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `HitlService` | Human-in-the-loop manager | Engine, plan executor | `hitl.create_approval(...)` | HITL handling |
| `HitlService.create_approval()` | Create pending approval | Plan execution, loops | Method call | HITL required |
| `HitlService.resolve()` | Resolve approval with decision | Engine resume | Method call | User decision |
| `generate_approval_id()` | Generate unique approval ID | Internal | Function call | Approval creation |

### user_input_handler.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `validate_user_input()` | Full input validation | Engine resume | `validate_user_input(input, schema)` | Input validation |
| `build_prompt()` | Build UserInputPrompt | Engine | Function call | Prompt display |
| `build_hitl_request()` | Build HitlRequest for input | HITL integration | Function call | HITL request |
| `merge_answers_into_context()` | Merge answers into context pack | Context update | Function call | Context pack update |
| `ValidationResult` | Validation result container | validate_user_input return | Dataclass | Validation output |

### error_policy.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `evaluate_retry()` | Evaluate retry based on policy | StepExecutor | `evaluate_retry(policy, attempt, error)` | After step failure |
| `get_backoff_duration()` | Get backoff time from policy | StepExecutor | Function call | Before retry |
| `RetryDecision` | Result of retry evaluation | evaluate_retry return | Dataclass | Retry logic |

---

## Component: core/tools

Tool framework, registry, and execution infrastructure.

### base.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `BaseTool` | Abstract base class for all tools | All tool implementations | Subclassed | Tool definition |
| `BaseTool.run()` | Abstract method for tool execution | Implementations | Called by executor | Tool execution |
| `BaseTool._inject_config()` | Configuration injection | Construction | Receives Settings | Tool initialization |
| `@tool` decorator | Marks classes for auto-discovery | Product tools | `@tool(name="...", ...)` | Class decoration |

### registry.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ToolRegistry` | Global class-level registry | ToolExecutor, governance, CLI | `ToolRegistry.register(...)` | Tool registration |
| `ToolRegistry.register()` | Register tool factory | Product initialization | Method call | Boot time |
| `ToolRegistry.resolve()` | Get fresh tool instance | ToolExecutor | Method call | Execution time |
| `ToolRegistry.get_descriptor()` | Get tool descriptor | Governance, advisory | Method call | Pre-execution |
| `ToolRegistry.list_all()` | List all registered tools | API endpoints, CLI | Method call | Admin/debug |
| `ToolEntry` | Registration record dataclass | Internal | Dataclass | Registry storage |

### executor.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ToolExecutor` | Central tool execution with governance | StepExecutor, PlanExecutor | `executor.execute(tool, params, ctx)` | Tool execution |
| `ToolExecutor.execute()` | Main tool execution entry | StepExecutor | Method call | Tool steps |
| `ToolExecutor._emit_trace()` | Emit sanitized trace | Internal | After execution | Trace logging |
| `ToolExecutor._redact_result()` | Redact sensitive data | Internal | Before trace | Security |
| `_strip_binary_fields()` | Remove large binary data | Internal | Trace cleanup | Output sanitization |
| `_make_artifact_ref()` | Create artifact reference | Internal | Evidence linking | Provenance |

### retrieval.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `RetrievalPolicy` | Source allow/block control | RetrievalTool | Dataclass | Policy enforcement |
| `search_prior_runs()` | Search previous run records | RetrievalTool | Function call | Retrieval phase |
| `search_approved_sources()` | Search approved knowledge | RetrievalTool | Function call | Retrieval phase |
| `RetrievalTool` | Read-only retrieval tool | Registered as `approved_retrieval` | Tool execution | Evidence gathering |
| `register_retrieval_tool()` | Register retrieval tool | Product initialization | Function call | Boot time |

### backends/local_backend.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `LocalToolBackend` | Executes tools in-process | ToolExecutor | `backend.run(tool, params, ctx)` | Local execution |
| `LocalToolBackend.run()` | Call tool's run method | ToolExecutor | Method call | Tool execution |

---

## Component: core/utils

Utility functions for hashing, discovery, and registry patterns.

### hashing.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `DeterministicEncoder` | JSON encoder for reproducible serialization | hash_json | JSON encoder class | Consistent hashing |
| `hash_json()` | SHA-256 hash of JSON-serializable data | Reproducibility | `hash_json(data)` | Data fingerprinting |
| `hash_input()` | Hash run input payload | run_lifecycle | `hash_input(payload)` | Run initialization |
| `hash_output()` | Hash run output | run_lifecycle | `hash_output(output)` | Run finalization |
| `verify_hash()` | Verify data matches hash | Reproducibility | `verify_hash(data, expected_hash)` | Validation |

### product_loader.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `discover_products()` | Scan and validate products | Gateway startup | `discovery = discover_products(path)` | App initialization |
| `register_products()` | Register agents/tools from products | Gateway startup | `register_products(discovery, ...)` | After discovery |
| `auto_register_product()` | Auto-discover and register | Product `__init__.py` | `auto_register_product(product_path, ...)` | Product registration |
| `_scan_agents()` | Scan for @agent decorated classes | Internal | Returns list | Agent discovery |
| `_scan_tools()` | Scan for @tool decorated classes | Internal | Returns list | Tool discovery |
| `ProductMeta` | Frozen product metadata | Discovery result | Dataclass | Product info |
| `ProductConfig` | Product configuration model | Manifest validation | Pydantic model | Config validation |
| `ProductDiscovery` | Discovery result container | discover_products return | Dataclass | Discovery result |
| `RegistrationContext` | Context for registration | register_products param | Dataclass | Registration context |

### reasoning_exporter.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `export_reasoning_log()` | Convert JSONL to Markdown | Observability | `export_reasoning_log(jsonl_path)` | Post-run export |

### registry.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ComponentFactory` | Type alias for factory callable | Registry classes | TypeAlias | Type annotation |
| `RegistrationRecord` | Registration record dataclass | Registry classes | Dataclass | Registry storage |
| `BaseRegistry` | Generic base class for registries | AgentRegistry, ToolRegistry | Subclassed | Pattern reuse |
| `BaseRegistry.register()` | Register component factory | Subclasses | Method call | Registration |
| `BaseRegistry.resolve()` | Get fresh instance | Subclasses | Method call | Resolution |
| `BaseRegistry.contains()` | Check if registered | Subclasses | Method call | Existence check |
| `BaseRegistry.clear()` | Reset registry | Test fixtures | Method call | Test cleanup |

---

## Component: gateway/api

FastAPI HTTP API for the platform.

### deps.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `get_settings()` | Cached settings singleton | Routes, dependencies | `Depends(get_settings)` | First API request |
| `get_product_discovery()` | Cached product discovery | Routes | `Depends(get_product_discovery)` | Product endpoints |
| `get_memory()` | Cached memory backend | Routes | `Depends(get_memory)` | Run/approval endpoints |
| `get_observability_store()` | Cached observability store | Engine construction | Function call | Engine startup |
| `get_engine()` | Request-scoped engine | Routes | `Depends(get_engine)` | Every run endpoint |

### http_app.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `create_app()` | FastAPI app factory | Tests, main | `app = create_app()` | App startup |
| `health()` | Health check endpoint | Liveness probes | GET /health | Health checks |
| `app` | ASGI application instance | uvicorn | Module-level | Server startup |

### routes_run.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `RunPayload` | Request model for run execution | POST /runs | Pydantic model | Run requests |
| `ResumePayload` | Request model for resume | POST /runs/{id}/resume | Pydantic model | Resume requests |
| `UserInputPayload` | Request model for user input | POST /runs/{id}/user_input | Pydantic model | Input submission |
| `list_products()` | GET /api/products endpoint | API | Route handler | Product listing |
| `list_flows()` | GET /api/products/{}/flows | API | Route handler | Flow listing |
| `list_runs()` | GET /api/runs endpoint | API | Route handler | Run history |
| `list_approvals()` | GET /api/approvals endpoint | API | Route handler | Approval listing |
| `start_run()` | POST /api/products/{}/{}/runs | API | Route handler | Run initiation |
| `get_run()` | GET /api/runs/{id} endpoint | API | Route handler | Run status |
| `get_pending_input()` | GET /api/runs/{id}/pending_input | API | Route handler | Input polling |
| `submit_user_input()` | POST /api/runs/{id}/user_input | API | Route handler | Input submission |
| `resume_run()` | POST /api/runs/{id}/resume | API | Route handler | Run resume |
| `_ok_response()` | Wrap successful responses | All endpoints | Helper function | Response formatting |
| `_validate_product()` | Validate product exists/enabled | Run endpoints | Helper function | Validation |
| `_validate_flow()` | Validate flow exists | Run endpoints | Helper function | Validation |

---

## Component: gateway/cli

Command-line interface for the platform.

### main.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `main()` | CLI entrypoint | Direct execution | `python -m gateway.cli.main` | CLI usage |
| `cmd_list_products()` | List all products | main() dispatch | Function call | `master list-products` |
| `cmd_list_flows()` | List flows for product | main() dispatch | Function call | `master list-flows` |
| `cmd_run()` | Execute a flow | main() dispatch | Function call | `master run` |
| `cmd_status()` | Get run status | main() dispatch | Function call | `master status` |
| `cmd_resume()` | Resume paused run | main() dispatch | Function call | `master resume` |
| `cmd_list_approvals()` | List pending approvals | main() dispatch | Function call | `master list-approvals` |
| `_parse_json()` | Parse JSON string | cmd_run | Helper function | Payload parsing |
| `_load_json()` | Load JSON from stdin/file | cmd_run | Helper function | Payload loading |
| `_validate_product()` | Validate product | Commands | Helper function | Validation |

---

## Component: gateway/ui

Streamlit UI for the platform.

### platform_app.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `main()` | UI entrypoint | Streamlit | Direct execution | UI launch |
| `REPO_ROOT` | Repository root constant | Path resolution | Module constant | Path setup |
| `_resolve_output_dir()` | Resolve observability path | Internal | Helper function | Output paths |

### api_client.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `ApiResponse` | Response wrapper dataclass | All client methods | Dataclass | Response handling |
| `ApiClient` | HTTP client for API | All UI pages | `client.get_products()` | API calls |
| `ApiClient.get_products()` | Fetch products | Home page | Method call | Product listing |
| `ApiClient.get_flows()` | Fetch flows for product | Execution page | Method call | Flow listing |
| `ApiClient.start_run()` | Start flow execution | Execution page | Method call | Run initiation |
| `ApiClient.get_run()` | Get run status | Execution, history | Method call | Status polling |
| `ApiClient.get_pending_input()` | Get pending prompt | Execution page | Method call | Input polling |
| `ApiClient.submit_user_input()` | Submit user input | Execution page | Method call | Input submission |
| `ApiClient.resume_run()` | Resume paused run | Execution page | Method call | Approval handling |
| `ApiClient.get_events()` | Get run events | History page | Method call | Event timeline |
| `_get_api_base_url()` | Resolve API URL | ApiClient init | Helper function | URL setup |
| `pretty_json()` | Format JSON for display | UI pages | Helper function | Display formatting |

### pages/home.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `render_home_page()` | Render home page | platform_app | Function call | Home navigation |
| `_render_product_list()` | Render product cards | render_home_page | Helper function | Product display |

### pages/execution.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `render_execution_page()` | Render execution page with tabs | platform_app | Function call | Execution navigation |
| `_render_run_tab()` | Run tab content | render_execution_page | Helper function | Run UI |
| `_render_approvals_tab()` | Approvals tab content | render_execution_page | Helper function | Approval UI |
| `_render_user_inputs_tab()` | User inputs tab content | render_execution_page | Helper function | Input UI |
| `_render_approval_card()` | Single approval card | _render_approvals_tab | Helper function | Approval card |
| `_render_input_prompt()` | Single input prompt | _render_user_inputs_tab | Helper function | Input form |

### pages/history.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `render_history_page()` | Render history page | platform_app | Function call | History navigation |
| `_render_run_metrics()` | Show run metrics | render_history_page | Helper function | Metrics display |
| `_render_event_timeline()` | Show event timeline | render_history_page | Helper function | Timeline display |
| `_status_icon()` | Map status to emoji | render_history_page | Helper function | Status display |

---

## Component: configs

YAML configuration files defining system behavior.

### app.yaml

| Configuration | Purpose | Where Used | Effect |
|---------------|---------|------------|--------|
| `app.environment` | Environment name (local/stage/prod) | Logging, conditionals | Environment identification |
| `app.debug` | Enable debug mode | Logging, error detail | Verbose output |
| `app.host` | API server bind host | HTTP server | Network binding |
| `app.port` | API server bind port | HTTP server | Port selection |
| `app.default_product` | Default product when unspecified | Gateway | Product fallback |
| `app.default_flow` | Default flow when unspecified | Gateway | Flow fallback |
| `app.gateway_api_base_url` | API URL for UI clients | Streamlit UI | API connection |
| `app.enable_sqlite_memory` | Enable SQLite backend | Memory router | Persistence toggle |
| `app.enable_vector_store` | Enable vector store | Knowledge module | Vector search toggle |
| `paths.repo_root` | Repository root | All path resolution | Base path |
| `paths.configs` | Configs directory | Config loader | Config location |
| `paths.storage` | Storage directory | Memory, observability | Storage location |

### models.yaml

| Configuration | Purpose | Where Used | Effect |
|---------------|---------|------------|--------|
| `models.default_provider` | Default LLM provider | ModelRouter | Provider selection |
| `models.default_model` | Default model name | ModelRouter | Model selection |
| `models.product_overrides` | Per-product model rules | ModelRouter | Product customization |
| `models.purpose_overrides` | Per-purpose model rules | ModelRouter | Purpose-based routing |
| `models.openai.endpoint` | Custom API endpoint | OpenAIProvider | API URL |
| `models.openai.api_key` | API key (prefer secrets) | OpenAIProvider | Authentication |
| `models.openai.timeout_seconds` | Request timeout | OpenAIProvider | Timeout control |

### policies.yaml

| Configuration | Purpose | Where Used | Effect |
|---------------|---------|------------|--------|
| `policies.enabled` | Master policy switch | PolicyEngine | Policy enforcement |
| `policies.allow_full_autonomy` | Allow autonomous operation | PolicyEngine | Autonomy control |
| `policies.tool_allowlist` | Allowed tools | PolicyEngine | Tool filtering |
| `policies.tool_blocklist` | Blocked tools | PolicyEngine | Tool blocking |
| `policies.model_allowlist` | Allowed models | PolicyEngine | Model filtering |
| `policies.model_blocklist` | Blocked models | PolicyEngine | Model blocking |
| `policies.max_tokens_per_request` | Token limit per request | Budgeting | Token control |
| `policies.max_steps` | Max orchestration steps | Budgeting | Step limit |
| `policies.max_tool_calls` | Max tool invocations | Budgeting | Tool call limit |
| `policies.max_payload_bytes` | Max payload size | Engine | Payload limit |
| `policies.retrieval.allowed_sources` | Allowed retrieval sources | RetrievalPolicy | Source control |
| `policies.per_product` | Per-product overrides | PolicyEngine | Product customization |

### logging.yaml

| Configuration | Purpose | Where Used | Effect |
|---------------|---------|------------|--------|
| `logging.level` | Log level | Python logging | Verbosity |
| `logging.console` | Enable console output | Logging config | Console logging |
| `logging.persist_events` | Persist trace events | Tracer | Event storage |
| `logging.redact_sensitive` | Enable redaction | SecurityRedactor | Security scrubbing |
| `logging.redaction_patterns` | Redaction regex patterns | SecurityRedactor | Pattern matching |

### products.yaml

| Configuration | Purpose | Where Used | Effect |
|---------------|---------|------------|--------|
| `products.path` | Products directory | ProductLoader | Product discovery |
| `products.enabled_products` | Explicit product allowlist | ProductLoader | Product filtering |
| `products.enable_all` | Enable all discovered | ProductLoader | Discovery mode |

---

## Component: scripts

Utility scripts for development and data generation.

### generate_component_txt.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `walk_files()` | Recursively yield source files | main() | Generator | File scanning |
| `get_component()` | Get top-level directory name | main() | Function call | File grouping |
| `write_bundle()` | Write component bundle file | main() | Function call | Bundle creation |
| `utc_timestamp()` | Get UTC timestamp | write_bundle() | Function call | Timestamping |
| `is_secrets_file()` | Check if path contains secrets | walk_files() | Function call | Security check |
| `redact_yaml_values()` | Redact sensitive YAML values | write_bundle() | Function call | Secret scrubbing |
| `main()` | Script entrypoint | Direct execution | `python scripts/generate_component_txt.py` | Documentation generation |

### generate_demo_data.py

| Function/Definition | Why It Exists | Where Used | How Used | When Used |
|---------------------|---------------|------------|----------|-----------|
| `generate_amount()` | Generate realistic transaction amounts | generate_rows() | Function call | Amount generation |
| `generate_timestamp()` | Generate timestamps (last 180 days) | generate_rows() | Function call | Time generation |
| `calculate_risk_score()` | Calculate risk score | generate_rows() | Function call | Risk assessment |
| `format_float()` | Format to 2 decimal places | generate_rows() | Function call | Number formatting |
| `generate_rows()` | Generate all transaction rows | main() | Function call | Data generation |
| `assign_fraud_labels()` | Assign fraud labels (~1.5% rate) | main() | Function call | Fraud labeling |
| `write_csv()` | Write data to CSV | main() | Function call | File output |
| `main()` | Script entrypoint | Direct execution | `python scripts/generate_demo_data.py` | Demo data creation |

---

*Document generated from codebase analysis. For implementation details, refer to the source files.*
