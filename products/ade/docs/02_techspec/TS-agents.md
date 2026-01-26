# ADE Agent Technical Specification

> **Document**: Technical Specification — Agents & Semantic Interpretation  
> **Prefix**: TS-AGENT-*, TS-SEM-*  
> **Version**: 1.5  
> **Last Updated**: 2026-01-21

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added semantic interpretation requirements |
| 1.2 | 2026-01-20 | Normalized ADE techspec tables to canonical TSD format; removed non-derivable sections; cleaned BRD mappings. |
| 1.3 | 2026-01-21 | Added terminal outcomes, framework escalation, narrative source, confidence config, and validation extensions per gap analysis. |
| 1.4 | 2026-01-20 | Converted all TSD IDs to TS- prefix; added implementation-level technical details (file paths, classes, methods, types). |
| 1.5 | 2026-01-21 | Added V1.3 BRD coverage: TS-AGENT-GEN-004 (agents as specialists), TS-SEM-ADAPTER-006 (intent-derived behavior), TS-AGENT-FRI-006 (platform semantic reliance), TS-AGENT-OUT-018 (reasoning narrative), TS-AGENT-FAIL-001..003 (failure modes). |

---

## 1. General Agent Requirements (TS-AGENT-GEN)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-GEN-001 | All agents MUST have descriptors registered in `products/ade/descriptors.py` with `purpose: str`, `capabilities: List[str]`, and `cost_hint: Literal["LOW", "MED", "HIGH"]` fields. | File: `products/ade/descriptors.py`; Class: `AgentDescriptor(BaseModel)`; Registration: `AGENT_DESCRIPTORS: Dict[str, AgentDescriptor]` | MUST | BRD-CONF-001 | Validate via `assert agent_name in AGENT_DESCRIPTORS` |
| TS-AGENT-GEN-002 | Agents MUST have accurate cost hints: `intent_agent: MED`, `plan_agent: MED`, `plan_proposal_agent: LOW`, `planning_agent: MED`, `sufficiency_evaluator: LOW`, `dashboard_agent: MED`. | File: `products/ade/descriptors.py`; Constant: `AGENT_COST_HINTS: Dict[str, str]` | MUST | BRD-CONF-001 | Used by orchestrator for budget estimation |
| TS-AGENT-GEN-003 | Agents MUST only be invoked from allowed step types: `plan_proposal_agent` from `agent/plan_proposal`; others from `agent` step type. | File: `products/ade/flows/*.yaml`; Field: `step.type`; Validation: `core.orchestrator.step_executor.validate_step_type()` | MUST | BRD-INTEL-002 | Enforced at flow load time |
| TS-AGENT-GEN-004 | ADE MUST treat agents as specialists performing scoped tasks (e.g., "summarize risk signals", "interpret intent"); orchestrator SHALL control sequencing and authority; agents SHALL NOT control flow or make autonomous decisions. | File: `products/ade/agents/*.py`; Pattern: Agents return data only, no flow control; Enforcement: `core.orchestrator.step_executor` calls agents, agents do not call other agents or steps | MUST | BRD-AGENT-001 | Agents are advisory only |

---

## 2. intent_agent (TS-AGENT-INTENT)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-INTENT-001 | `intent_agent` MUST output `IntentFrame` schema with fields: `intent_summary: str`, `inferred_entities: List[str]`, `inferred_metrics: List[str]`, `inferred_time_window: Optional[str]`, `requested_outputs: List[str]`, `confidence_score: float`, `confidence_label: Literal["low", "medium", "high"]`, `blocking_required: bool`, `blocking_questions: List[str]`, `blocking_question: Optional[str]`. | File: `products/ade/agents/intent_agent.py`; Class: `IntentAgent`; Method: `run(user_input: str, context: Dict) -> IntentFrame`; Schema: `products/ade/schemas/intent_frame.py` | MUST | BRD-INTENT-001 | — |
| TS-AGENT-INTENT-002 | `intent_agent` MUST compute `confidence_score: float` in range `[0.0, 1.0]` and derive `confidence_label` using thresholds: `low < 0.4`, `medium in [0.4, 0.7]`, `high > 0.7`. | Method: `IntentAgent._compute_confidence(parsed: Dict) -> Tuple[float, str]`; Config: `products/ade/config/confidence.yaml` | MUST | BRD-INTENT-005 | Configurable thresholds |
| TS-AGENT-INTENT-003 | `intent_agent` MUST detect clarification requirements by setting `blocking_required=True` when `dataset`, `metric`, or `time_window` fields are missing or ambiguous. | Method: `IntentAgent._check_blocking(frame: IntentFrame) -> bool`; Logic: `if not frame.inferred_entities or not frame.inferred_metrics` | MUST | BRD-INTENT-006 | Triggers `ASK_USER` terminal outcome |
| TS-AGENT-INTENT-004 | `intent_agent` MUST extract: dataset names → `inferred_entities: List[str]`, metric names → `inferred_metrics: List[str]`, time windows → `inferred_time_window: Optional[str]`. | Method: `IntentAgent._extract_entities(text: str) -> Dict`; Uses: keyword matching and regex patterns (no LLM) | MUST | BRD-INTENT-002, BRD-INTENT-003, BRD-INTENT-004 | Deterministic extraction |

---

## 3. plan_agent (TS-AGENT-PLAN)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-PLAN-001 | `plan_agent` MUST output valid `PlanSpec` schema with `steps: List[PlanStep]` and `tool_flags: Dict[str, bool]` for conditional execution. | File: `products/ade/agents/plan_agent.py`; Class: `PlanAgent`; Method: `run(intent: IntentFrame) -> PlanSpec`; Schema: `products/ade/schemas/plan_spec.py` | MUST | BRD-PLANGEN-002, BRD-PLANGEN-003 | — |
| TS-AGENT-PLAN-002 | `plan_agent` MUST produce deterministic plans: identical `(intent, context)` inputs MUST produce identical `PlanSpec` outputs with no random selection or shuffling. | Implementation: Use `sorted()` for any list ordering; No `random` module usage; Seed any RNG with `hash(input)` | MUST | BRD-PLANGEN-001, BRD-PLANGEN-004 | Verified by determinism tests |

---

## 4. plan_proposal_agent (TS-AGENT-PROPOSAL)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-PROPOSAL-001 | `plan_proposal_agent` MUST output `PlanProposal` with fields: `proposal_id: str`, `summary: str`, `estimated_steps: int`, `estimated_cost: CostEstimate`, `requires_approval: bool`. | File: `products/ade/agents/plan_proposal_agent.py`; Class: `PlanProposalAgent`; Method: `run(plan: PlanSpec) -> PlanProposal`; Schema: `products/ade/schemas/plan_proposal.py` | MUST | BRD-PROPOSAL-001 | — |
| TS-AGENT-PROPOSAL-002 | `plan_proposal_agent` MUST set `requires_approval=True` for non-trivial plans (step_count > 3 OR estimated_cost.total > budget_threshold) and pause execution for user decision. | Method: `PlanProposalAgent._check_approval_required(plan: PlanSpec) -> bool`; Config: `products/ade/config/governance.yaml::approval_thresholds` | MUST | BRD-PROPOSAL-004 | Integrates with HITL |
| TS-AGENT-PROPOSAL-003 | `plan_proposal_agent` MUST estimate execution cost by summing tool `cost_hint` values from `products/ade/descriptors.py` and multiplying by step count. | Method: `PlanProposalAgent._estimate_cost(steps: List[PlanStep]) -> CostEstimate`; Uses: `TOOL_DESCRIPTORS[tool_name].cost_hint` | MUST | BRD-PROPOSAL-002, BRD-PROPOSAL-003 | Return `CostEstimate(total=sum, breakdown=Dict)` |

---

## 5. planning_agent (TS-AGENT-PLANNING)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-PLANNING-001 | `planning_agent` MUST support both intent interpretation and replanning based on `context.mode: Literal["interpret", "replan"]`. | File: `products/ade/agents/planning_agent.py`; Class: `PlanningAgent`; Method: `run(input: str, context: Dict) -> Union[IntentFrame, ReplanResult]` | MUST | BRD-PLANNING-001, BRD-PLANNING-002 | — |
| TS-AGENT-PLANNING-002 | `planning_agent` MUST produce `ReplanResult` after rejection with fields: `change_summary: str`, `rationale: str`, `restart_step: str`. | Schema: `products/ade/schemas/replan_result.py`; Method: `PlanningAgent._generate_replan(rejection: RejectionReason) -> ReplanResult` | MUST | BRD-PLANNING-002 | Highlight delta from original |

---

## 6. sufficiency_evaluator (TS-AGENT-SUFF)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-SUFF-001 | `sufficiency_evaluator` MUST output `SufficiencyOutput` with fields: `stage: Literal["critique"]`, `confidence_level: Literal["high", "medium", "low"]`, `downgrade_reasons: List[str]`. | File: `products/ade/agents/sufficiency_evaluator.py`; Class: `SufficiencyEvaluator`; Method: `run(data: DataReaderOutput) -> SufficiencyOutput` | MUST | BRD-SUFF-001, BRD-SUFF-002 | — |
| TS-AGENT-SUFF-002 | `sufficiency_evaluator` MUST use standard confidence levels derived from data quality metrics: `high` (coverage > 90%, no missing required columns), `medium` (coverage 70-90%), `low` (coverage < 70% or missing required columns). | Method: `SufficiencyEvaluator._compute_confidence(metrics: Dict) -> str`; Config: `products/ade/config/confidence.yaml::sufficiency_thresholds` | MUST | BRD-SUFF-002 | Configurable thresholds |
| TS-AGENT-SUFF-003 | `sufficiency_evaluator` MUST explain confidence downgrades with human-readable `downgrade_reasons: List[str]` (empty list when confidence is "high"). | Method: `SufficiencyEvaluator._explain_downgrades(metrics: Dict) -> List[str]`; Template: `"Insufficient {field}: {actual} vs required {threshold}"` | MUST | BRD-SUFF-003, BRD-CONF-004 | — |
| TS-AGENT-SUFF-004 | `sufficiency_evaluator` SHOULD evaluate: row count sufficiency (`row_count >= min_rows`), column completeness (`required_cols ⊆ available_cols`), data freshness (`max_date >= cutoff_date`). | Method: `SufficiencyEvaluator._evaluate_quality(data: DataReaderOutput) -> Dict[str, Any]`; Config: `products/ade/config/data_quality.yaml` | SHOULD | BRD-SUFF-004, BRD-SUFF-005, BRD-SUFF-006 | — |

---

## 7. dashboard_agent (TS-AGENT-DASH)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-DASH-001 | `dashboard_agent` MUST produce human-readable narrative summary (< 500 words) via `DashboardOutput.insight: str` reflecting dataset characteristics. | File: `products/ade/agents/dashboard_agent.py`; Class: `DashboardAgent`; Method: `run(metrics: Dict) -> DashboardOutput`; Validation: `assert len(output.insight.split()) < 500` | MUST | BRD-NARR-001, BRD-NARR-002 | — |
| TS-AGENT-DASH-002 | `dashboard_agent` MUST accept dataset summaries as input and produce `DashboardOutput` with fields: `message: str`, `insight: str`, `anomaly_summary: str`, `anomaly_interpretation: str`, `anomaly_count: int`. | Schema: `products/ade/schemas/dashboard_output.py`; Input: `metrics: Dict` from `compute_business_metrics` output | MUST | BRD-NARR-001 | — |

---

## 8. Reasoning Ladder (TS-AGENT-REASON)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-REASON-001 | ADE MUST use multi-stage reasoning ladder: `interpret → propose → critique → finalize` with explicit `stage: str` field in all agent outputs. | Schema field: `stage: Literal["interpret", "propose", "critique", "finalize"]`; Validation: `core.orchestrator.validate_stage_progression()` | MUST | BRD-INTEL-001, BRD-INTEL-002 | — |
| TS-AGENT-REASON-002 | Each reasoning stage MUST be observable in traces with `stage_name: str` in `core.memory.tracing.TraceEvent.metadata`. | File: `products/ade/observability.py`; Method: `emit_stage_trace(stage: str, artifacts: Dict)`; Output: `TraceEvent(metadata={"stage": stage})` | MUST | BRD-INTEL-002 | Stored in observability store |
| TS-AGENT-REASON-003 | Reasoning cycles MUST be bounded by: `max_iterations: int` (default 10), `max_tools: int` (default 20), `max_time_seconds: int` (default 300). | Config: `products/ade/config/governance.yaml::reasoning_limits`; Enforcement: `core.orchestrator.loop_executor.check_bounds()` | MUST | BRD-INTEL-003 | — |
| TS-AGENT-REASON-004 | Reasoning MUST track sufficiency state via `sufficiency_state: Dict[str, List[str]]` with keys: `known`, `unknown`, `blocked`. | Schema: `products/ade/schemas/sufficiency_state.py`; Updated by: `SufficiencyEvaluator.run()` | MUST | BRD-INTEL-004 | — |
| TS-AGENT-REASON-005 | Final outputs MUST include `stop_reason: Literal["sufficient", "budget_exhausted", "missing_inputs", "conflict"]`. | Schema field in: `DecisionPacket.stop_reason`, `BusinessReport.stop_reason`; Set by: `core.orchestrator.run_lifecycle.determine_stop_reason()` | MUST | BRD-INTEL-005 | — |

---

## 9. Critique Requirements (TS-AGENT-CRIT)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-CRIT-001 | A critique stage MUST run before final outputs; final output schemas MUST reference critique via `critique_ref: Optional[str]`. | File: `products/ade/agents/critic_evaluator.py`; Step: must appear before `assemble_*` steps in flow YAML; Schema: `CritiqueOutput` | MUST | BRD-CRIT-001, BRD-CRIT-006 | — |
| TS-AGENT-CRIT-002 | Critique MUST identify evidence gaps via `CritiqueOutput.evidence_gaps: List[str]` listing missing or weak evidence items. | Method: `CriticEvaluator._identify_gaps(evidence: List[EvidenceItem]) -> List[str]` | MUST | BRD-CRIT-002 | — |
| TS-AGENT-CRIT-003 | Critique MUST support confidence downgrade via `CritiqueOutput.revised_confidence: str` and `downgrade_reason: Optional[str]`. | Schema: `products/ade/schemas/critique_output.py`; Logic: if gaps found, downgrade by one level | MUST | BRD-CRIT-003 | — |
| TS-AGENT-CRIT-004 | Critique MUST NOT execute tools or route flows; `CriticEvaluator` class MUST NOT import tool modules or call `orchestrator.execute_step()`. | Enforcement: Static analysis check in CI; Code review requirement | MUST | BRD-CRIT-004 | Advisory only |
| TS-AGENT-CRIT-005 | Blocking critique findings MUST set `CritiqueOutput.blocking_required=True` and trigger `ASK_USER` or `ABORT` terminal outcome. | Method: `CriticEvaluator._check_blocking(gaps: List[str]) -> bool`; Integration: `orchestrator.handle_blocking_critique()` | MUST | BRD-CRIT-005 | — |

---

## 10. Advisory Tool Selection (TS-AGENT-TOOLSEL)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-TOOLSEL-001 | Tool selection MUST be advisory via `PlanSpec.tool_recommendations: List[ToolRecommendation]` with `tool_name: str`, `rationale: str`, `priority: int`. | Schema: `products/ade/schemas/plan_spec.py::ToolRecommendation`; Used by: `plan_agent.run()` | MUST | BRD-TOOLSEL-001 | — |
| TS-AGENT-TOOLSEL-002 | Tool recommendations MAY be ranked via `ToolRecommendation.priority: int` (lower = higher priority) with rationales. | Implementation: `sorted(recommendations, key=lambda r: r.priority)` | MAY | BRD-TOOLSEL-002 | — |
| TS-AGENT-TOOLSEL-003 | Orchestrator MUST remain sole authority for tool execution; agent outputs MUST NOT trigger tool calls directly. | Enforcement: `core.orchestrator.step_executor` is only caller of `tool.run()`; Agents return data only | MUST | BRD-TOOLSEL-003 | — |
| TS-AGENT-TOOLSEL-004 | Advisory tool suggestions MUST NOT force execution; orchestrator MAY ignore recommendations. | Implementation: Recommendations stored in artifacts; flow YAML defines actual execution | MUST | BRD-TOOLSEL-004 | — |

---

## 11. Framework Alignment (TS-AGENT-FRI)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-FRI-001 | Product reasoning MUST use `core.agents.reasoning_ladder` interfaces; no custom reasoning implementations. | Import: `from core.agents.reasoning_ladder import ReasoningLadder`; Usage: `ladder.run_stage(stage_name, input)` | MUST | BRD-CONF-005 | — |
| TS-AGENT-FRI-002 | Product MUST NOT re-implement: orchestrator logic (`core.orchestrator.*`), iteration control (`core.orchestrator.loop_executor`), reasoning ladder semantics (`core.agents.reasoning_ladder`). | Enforcement: No `products/ade/` files may duplicate core module logic; CI static check | MUST | BRD-CONF-005 | — |
| TS-AGENT-FRI-003 | Product MUST NOT bypass framework governance hooks; all agent calls MUST flow through `core.governance.hooks.pre_agent()` and `post_agent()`. | Enforcement: Agent base class calls hooks automatically; direct instantiation prohibited | MUST | BRD-CONF-005 | — |
| TS-AGENT-FRI-004 | Framework gaps MUST be logged in `products/ade/docs/FRAMEWORK_GAPS.md` with BRD ID, gap description, and workaround status. | File: `products/ade/docs/FRAMEWORK_GAPS.md`; Format: Markdown table | MUST | BRD-CONF-005 | — |
| TS-AGENT-FRI-005 | Framework gaps MUST be escalated via `core.governance.hooks.escalate_framework_gap(gap_id: str, description: str)`, not worked around with product-level logic. | Method: `escalate_framework_gap()`; Logged to: `core.memory.observability_store`; Triggers: alert to platform team | MUST | BRD-FRI-005 | — |
| TS-AGENT-FRI-006 | ADE MUST consume platform-provided semantic envelopes and validation outputs; ADE SHALL NOT re-implement semantic parsing, intent extraction, or validation logic inside product code. | Enforcement: `products/ade/semantic_adapter.py` extends `core.knowledge.semantic_adapter.SemanticAdapterBase`; No duplicate parsing logic; Validation from `core.knowledge.validation` | MUST | BRD-FRI-006 | Platform semantic reliance |

---

## 12. No Runtime Learning (TS-AGENT-NRL)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-NRL-001 | Product MUST NOT modify behavior at runtime based on prior runs; no state persistence between runs. | Enforcement: No file writes outside `staging/output/`; No database connections in agents; Stateless function calls | MUST | BRD-CONF-005 | — |
| TS-AGENT-NRL-002 | Product MUST NOT persist learned patterns across runs; no model fine-tuning, no pattern caching. | Enforcement: No ML model updates; No pattern files; Fresh state on each `orchestrator.run()` | MUST | BRD-CONF-005 | — |
| TS-AGENT-NRL-003 | Product evolution MUST follow `intent → BRD → implementation` lifecycle; no autonomous capability changes. | Process: Update BRD first, then Tech Spec, then implementation; Version control all changes | MUST | BRD-CONF-005 | — |
| TS-AGENT-NRL-004 | Identical inputs MUST produce identical outputs across runs; `hash(input) == hash(input')` ⟹ `output == output'`. | Enforcement: Determinism test suite; No `random` without seed; No time-based logic except timestamps | MUST | BRD-PLANGEN-004 | — |

---

## 13. ADESemanticAdapter (TS-SEM-ADAPTER)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SEM-ADAPTER-001 | `ADESemanticAdapter` MUST be implemented in `products/ade/semantic_adapter.py` exporting class `ADESemanticAdapter(SemanticAdapterBase)`. | File: `products/ade/semantic_adapter.py`; Base class: `core.knowledge.semantic_adapter.SemanticAdapterBase` | MUST | BRD-SEM-001 | — |
| TS-SEM-ADAPTER-002 | `ADESemanticAdapter.interpret()` MUST accept `user_input: str` and optional `context: Dict[str, Any]`, returning `SemanticEnvelope`. | Signature: `def interpret(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> SemanticEnvelope` | MUST | BRD-SEM-001 | — |
| TS-SEM-ADAPTER-003 | `SemanticEnvelope` MUST include fields: `intent_type: ADEIntentType`, `requested_outputs: List[str]`, `metrics: List[str]`, `time_scope: Optional[str]`, `constraints: Dict[str, Any]`, `confidence: float`, `raw_input: str`. | Schema: `products/ade/schemas/semantic_envelope.py` | MUST | BRD-SEM-002 | — |
| TS-SEM-ADAPTER-004 | `ADESemanticAdapter` MUST classify input using deterministic keyword/pattern matching (no LLM); use `INTENT_PATTERNS: Dict[ADEIntentType, List[str]]` for classification. | Method: `ADESemanticAdapter._classify_intent(text: str) -> ADEIntentType`; Patterns: regex and keyword lists | MUST | BRD-SEM-002, BRD-SEM-003 | — |
| TS-SEM-ADAPTER-005 | `ADESemanticAdapter` MUST compute `confidence: float` in `[0.0, 1.0]` based on pattern match strength and field completeness. | Method: `ADESemanticAdapter._compute_confidence(matches: Dict) -> float`; Formula: `base_score * completeness_factor` | MUST | BRD-SEM-004 | — |
| TS-SEM-ADAPTER-006 | ADE MUST derive analytical behavior strictly from resolved user intent; analysis types (trend, anomaly, delta) SHALL NOT be assumed unless explicitly specified in the resolved semantic intent. | Enforcement: `ADESemanticAdapter.interpret()` returns only fields present in user input; No default analysis types; Validation: `assert envelope.intent_type in USER_SPECIFIED_INTENTS or envelope.confidence < 0.5` | MUST | BRD-SEM-011 | Intent-only behavior derivation |

---

## 14. ADE Intent Taxonomy (TS-SEM-INTENT)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SEM-INTENT-001 | ADE intent taxonomy MUST be defined in `products/ade/intents.py` exporting `ADEIntentType(Enum)` and `INTENT_REQUIREMENTS: Dict[ADEIntentType, IntentRequirement]`. | File: `products/ade/intents.py`; Enum values: string literals; Requirements: Pydantic model | MUST | BRD-INTENT-TAX-006 | — |
| TS-SEM-INTENT-002 | `ADEIntentType` MUST define values: `DESCRIBE_DATA = "describe_data"`, `COMPARE_PERIODS = "compare_periods"`, `TREND_ANALYSIS = "trend_analysis"`, `ANOMALY_REVIEW = "anomaly_review"`, `OPEN_ENDED_ANALYSIS = "open_ended_analysis"`. | Definition: `class ADEIntentType(str, Enum)` | MUST | BRD-INTENT-TAX-001 to -005 | — |
| TS-SEM-INTENT-003 | `DESCRIBE_DATA` intent MUST require `dataset: str` (required); `metrics: List[str]` and `time_scope: str` are optional. | Entry: `INTENT_REQUIREMENTS[ADEIntentType.DESCRIBE_DATA] = IntentRequirement(required=["dataset"], optional=["metrics", "time_scope"])` | MUST | BRD-INTENT-TAX-001 | — |
| TS-SEM-INTENT-004 | `COMPARE_PERIODS` intent MUST require `dataset: str`, `time_scope: str` (required); `metrics: List[str]` is optional. | Entry: `INTENT_REQUIREMENTS[ADEIntentType.COMPARE_PERIODS] = IntentRequirement(required=["dataset", "time_scope"], optional=["metrics"])` | MUST | BRD-INTENT-TAX-002 | — |
| TS-SEM-INTENT-005 | `TREND_ANALYSIS` intent MUST require `dataset: str`, `metrics: List[str]`, `time_scope: str` (all required). | Entry: `INTENT_REQUIREMENTS[ADEIntentType.TREND_ANALYSIS] = IntentRequirement(required=["dataset", "metrics", "time_scope"])` | MUST | BRD-INTENT-TAX-003 | — |
| TS-SEM-INTENT-006 | `ANOMALY_REVIEW` intent MUST require `dataset: str`, `metrics: List[str]` (required); `time_scope: str` is optional. | Entry: `INTENT_REQUIREMENTS[ADEIntentType.ANOMALY_REVIEW] = IntentRequirement(required=["dataset", "metrics"], optional=["time_scope"])` | MUST | BRD-INTENT-TAX-004 | — |
| TS-SEM-INTENT-007 | `OPEN_ENDED_ANALYSIS` intent MUST require `dataset: str` (required); `metrics: List[str]` and `time_scope: str` are optional. | Entry: `INTENT_REQUIREMENTS[ADEIntentType.OPEN_ENDED_ANALYSIS] = IntentRequirement(required=["dataset"], optional=["metrics", "time_scope"])` | MUST | BRD-INTENT-TAX-005 | — |

---

## 15. Semantic Validation (TS-SEM-VALIDATE)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SEM-VALIDATE-001 | Semantic validation MUST be implemented in `products/ade/semantic_validation.py` exporting `validate_semantic_envelope()` and `ValidationResult`. | File: `products/ade/semantic_validation.py`; Function and class exports | MUST | BRD-SEM-VAL-001 | — |
| TS-SEM-VALIDATE-002 | `validate_semantic_envelope()` MUST accept `envelope: SemanticEnvelope` and `intent_type: ADEIntentType`, returning `ValidationResult`. | Signature: `def validate_semantic_envelope(envelope: SemanticEnvelope, intent_type: ADEIntentType) -> ValidationResult` | MUST | BRD-SEM-VAL-001 | — |
| TS-SEM-VALIDATE-003 | `ValidationResult` MUST include fields: `is_valid: bool`, `missing_fields: List[str]`, `clarifying_question: Optional[str]`, `confidence_adjustment: float`, `outcome: Literal["PROCEED", "ASK_USER", "ABORT"]`. | Schema: `products/ade/schemas/validation_result.py` | MUST | BRD-SEM-VAL-001, BRD-SEM-VAL-002 | — |
| TS-SEM-VALIDATE-004 | Validation MUST return `outcome="ASK_USER"` with `clarifying_question` when `len(missing_fields) > 0` and fields are user-providable. | Logic: `if missing_fields and any(f in USER_PROVIDABLE_FIELDS for f in missing_fields)` | MUST | BRD-SEM-VAL-003 | — |
| TS-SEM-VALIDATE-005 | Validation MUST return `outcome="ABORT"` when critical fields cannot be inferred and no clarification is possible (e.g., no dataset at all). | Logic: `if "dataset" in missing_fields and not context.get("available_datasets")` | MUST | BRD-SEM-VAL-004 | — |
| TS-SEM-VALIDATE-006 | Validation MUST return `outcome="PROCEED"` with `is_valid=True` when all required fields for `intent_type` are present. | Logic: `if all(f in envelope.__dict__ for f in INTENT_REQUIREMENTS[intent_type].required)` | MUST | BRD-SEM-VAL-001 | — |
| TS-SEM-VALIDATE-007 | `ValidationResult.confidence_adjustment: float` MUST be in range `[-1.0, 0.0]` computed as `-0.1 * len(missing_optional_fields)`. | Method: `_compute_adjustment(envelope: SemanticEnvelope, requirements: IntentRequirement) -> float` | MUST | BRD-SEM-VAL-005 | — |
| TS-SEM-VALIDATE-008 | Dataset references MUST be validated against `available_datasets: List[str]` from context before proceeding. | Method: `_validate_dataset_ref(dataset: str, available: List[str]) -> bool`; Error: `ValidationResult(outcome="ASK_USER", clarifying_question="Dataset '{dataset}' not found...")` | MUST | BRD-SEM-VAL-006 | — |
| TS-SEM-VALIDATE-009 | Metric references MUST be validated against dataset schema when known; return `ASK_USER` if metric not in schema columns. | Method: `_validate_metric_ref(metric: str, schema: DatasetSchema) -> bool`; Uses: `products/ade/tools/data_reader.py::get_schema()` | MUST | BRD-SEM-VAL-007 | — |

---

## 16. Clarifying Question Templates (TS-SEM-CLARIFY)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SEM-CLARIFY-001 | Clarifying questions MUST be defined in `products/ade/clarifying_questions.py` exporting `get_clarifying_question()` and `CLARIFYING_TEMPLATES: Dict[str, str]`. | File: `products/ade/clarifying_questions.py` | MUST | BRD-CLARIFY-001, BRD-CLARIFY-002 | — |
| TS-SEM-CLARIFY-002 | `CLARIFYING_TEMPLATES` MUST map missing field names to deterministic question templates. | Type: `Dict[str, str]`; Keys: field names; Values: template strings with `{context}` placeholders | MUST | BRD-CLARIFY-002, BRD-CLARIFY-003 | — |
| TS-SEM-CLARIFY-003 | Template for `metrics` field: `"Which specific metric would you like to focus on? (e.g., revenue, cost, volume)"` | Entry: `CLARIFYING_TEMPLATES["metrics"] = "Which specific metric..."` | MUST | BRD-CLARIFY-004 | — |
| TS-SEM-CLARIFY-004 | Template for `time_scope` field: `"What time period should we analyze? (e.g., last 30 days, Q1 2024, YTD)"` | Entry: `CLARIFYING_TEMPLATES["time_scope"] = "What time period..."` | MUST | BRD-CLARIFY-005 | — |
| TS-SEM-CLARIFY-005 | Template for anomaly threshold: `"What threshold should we use for anomaly detection? (default: 2.0 standard deviations)"` | Entry: `CLARIFYING_TEMPLATES["anomaly_threshold"] = "What threshold..."` | MUST | BRD-CLARIFY-006 | — |
| TS-SEM-CLARIFY-006 | Clarifying questions MUST NOT use LLM for generation; all from predefined `CLARIFYING_TEMPLATES` dictionary. | Enforcement: `get_clarifying_question()` only reads from `CLARIFYING_TEMPLATES`; no model imports | MUST | BRD-CLARIFY-002 | — |

---

## 17. Intent Router (TS-SEM-ROUTER)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SEM-ROUTER-001 | Intent router MUST be implemented in `products/ade/intent_router.py` exporting `route_intent()` and `RouteResult`. | File: `products/ade/intent_router.py` | MUST | BRD-ROUTER-001 | — |
| TS-SEM-ROUTER-002 | `route_intent()` MUST accept `envelope: SemanticEnvelope` and return `RouteResult(flow_name: str, initial_parameters: Dict[str, Any])`. | Signature: `def route_intent(envelope: SemanticEnvelope) -> RouteResult` | MUST | BRD-ROUTER-002 | — |
| TS-SEM-ROUTER-003 | Router MUST use deterministic mapping: `DESCRIBE_DATA → "visualization"`, `COMPARE_PERIODS → "ade_v1"`, `TREND_ANALYSIS → "ade_v1"`, `ANOMALY_REVIEW → "ade_v1"`, `OPEN_ENDED_ANALYSIS → "visualization"`. | Constant: `INTENT_TO_FLOW: Dict[ADEIntentType, str]`; No conditional logic beyond dict lookup | MUST | BRD-ROUTER-003, BRD-ROUTER-004 | — |
| TS-SEM-ROUTER-004 | Router MUST map `SemanticEnvelope` fields to flow parameters with `dataset` always included in `initial_parameters`. | Logic: `initial_parameters = {"dataset": envelope.dataset, **optional_fields}` | MUST | BRD-ROUTER-002 | — |

---

## 18. Semantic Observability (TS-SEM-OBS)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-SEM-OBS-001 | Semantic observability MUST be implemented in `products/ade/observability.py` exporting `emit_semantic_trace()` and integrating with `core.governance.hooks`. | File: `products/ade/observability.py`; Hook: `core.governance.hooks.register_product_hook("ade", emit_semantic_trace)` | MUST | BRD-SEM-OBS-001 | — |
| TS-SEM-OBS-002 | Semantic traces MUST extend core trace events with ADE fields in `metadata.product_specific` namespace. | Structure: `TraceEvent(metadata={"product_specific": {"ade_intent": ..., "ade_confidence": ...}})` | MUST | BRD-SEM-OBS-001 | — |
| TS-SEM-OBS-003 | Trace MUST include `ade_intent: str` field with intent type string on all semantic interpretation events. | Field: `metadata.product_specific.ade_intent = envelope.intent_type.value` | MUST | BRD-SEM-OBS-002 | — |
| TS-SEM-OBS-004 | Trace MUST include `ade_confidence: float` in `[0.0, 1.0]` reflecting final adjusted confidence. | Field: `metadata.product_specific.ade_confidence = validation_result.adjusted_confidence` | MUST | BRD-SEM-OBS-003 | — |
| TS-SEM-OBS-005 | Trace MUST include `ade_missing_fields: List[str]` when validation detects gaps. | Field: `metadata.product_specific.ade_missing_fields = validation_result.missing_fields` | MUST | BRD-SEM-OBS-004 | — |
| TS-SEM-OBS-006 | Trace MUST include `ade_clarifying_question: str` when question is generated. | Field: `metadata.product_specific.ade_clarifying_question = validation_result.clarifying_question` | MUST | BRD-SEM-OBS-005 | — |

---

## 19. Terminal Outcomes (TS-AGENT-TERM)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-TERM-001 | ADE MUST emit explicit terminal outcomes using `TerminalOutcome(Enum)` with values: `SUCCESS = "success"`, `PARTIAL_SUCCESS = "partial_success"`, `ASK_USER = "ask_user"`, `ABORT = "abort"`. | File: `products/ade/schemas/terminal_outcome.py`; Enum: `class TerminalOutcome(str, Enum)` | MUST | BRD-TERM-001 | — |
| TS-AGENT-TERM-002 | `PARTIAL_SUCCESS` outcomes MUST include `PartialSuccessDetails` with fields: `completed_steps: List[str]`, `missing_steps: List[str]`, `reason: str`. | Schema: `products/ade/schemas/terminal_outcome.py::PartialSuccessDetails`; Attached to: `RunResult.partial_details` | MUST | BRD-TERM-002 | — |
| TS-AGENT-TERM-003 | Terminal outcomes MUST include `terminal_artifact: Dict[str, Any]` containing explanations and supporting artifacts. | Field: `RunResult.terminal_artifact = {"explanation": str, "supporting_refs": List[str], "confidence": str}` | MUST | BRD-TERM-003 | — |

---

## 20. Narrative Source Requirements (TS-AGENT-NARR)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-NARR-005 | User-facing explanations MUST be derived from `core.memory.tracing.DecisionRecord` artifacts, not regenerated narratives. | Method: `products/ade/narrative.py::build_explanation(decision_records: List[DecisionRecord]) -> str`; Source: `core.memory.observability_store.get_decision_records(run_id)` | MUST | BRD-NARR-005 | — |

---

## 21. Confidence Configuration (TS-AGENT-CONF)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-CONF-003 | Confidence thresholds MUST be configurable via `products/ade/config/confidence.yaml` with keys: `low_threshold: float`, `high_threshold: float`, `sufficiency_thresholds: Dict`. | File: `products/ade/config/confidence.yaml`; Loaded by: `products/ade/config.py::load_confidence_config()`; Schema: `ConfidenceConfig(BaseModel)` | MUST | BRD-CONF-003 | — |

---

## 22. Failure Mode Requirements (TS-AGENT-FAIL)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-FAIL-001 | ADE MUST fail fast when resolved intent is incompatible with the provided data structure; if the intent cannot be executed on the dataset (e.g., anomaly detection without numeric measures, trend analysis without time field), ADE SHALL halt and explain why. | Method: `products/ade/agents/intent_validator.py::validate_intent_data_compatibility(intent: SemanticEnvelope, data: DataReaderOutput) -> ValidationResult`; Returns: `TerminalOutcome.ABORT` with explanation if incompatible | MUST | BRD-FAIL-001 | Fail-fast on incompatibility |
| TS-AGENT-FAIL-002 | ADE MUST NOT proceed with analysis when required data dimensions are missing; execution SHALL be blocked with structured explanation of the gap. | Method: `products/ade/agents/data_validator.py::validate_required_dimensions(intent: SemanticEnvelope, schema: DatasetSchema) -> ValidationResult`; Returns: `TerminalOutcome.ABORT` or `TerminalOutcome.ASK_USER` with missing dimensions list | MUST | BRD-FAIL-002 | Block on missing dimensions |
| TS-AGENT-FAIL-003 | ADE MUST prohibit time-series or period-over-period analysis without explicit approval; ADE SHALL stop and request clarification before performing any temporal aggregation, trend analysis, or delta computation. | Method: `products/ade/agents/temporal_validator.py::validate_temporal_analysis(intent: SemanticEnvelope, user_approval: bool) -> ValidationResult`; Logic: `if intent.requires_temporal_analysis and not user_approval: return ASK_USER("Please confirm time-based analysis...")` | MUST | BRD-FAIL-003 | Temporal analysis gating |

---

## 23. Reasoning Narrative Requirements (TS-AGENT-NARRATIVE)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-NARRATIVE-001 | ADE MUST declare "Reasoning Narrative" as a required output artifact; every ADE run SHALL produce a coherent, human-readable reasoning narrative explaining why each analysis or decision was made. | File: `products/ade/tools/narrative_builder.py`; Function: `def build_reasoning_narrative(trace_events: List[TraceEvent], decisions: List[DecisionRecord]) -> str`; Output: `reasoning_narrative: str` in `DecisionPacket` and `BusinessReport`; Schema: `DecisionPacket.reasoning_narrative: Optional[str]`; Validation: `assert reasoning_narrative is not None and len(reasoning_narrative) > 0` | MUST | BRD-OUT-018 | Required output artifact |

---

## 24. Reasoning-Presentation Separation (TS-AGENT-SEPARATION)

| TSD ID | Technical Specification | Implementation Details | Level | BRD Mapping | Notes |
|--------|------------------------|------------------------|-------|-------------|-------|
| TS-AGENT-SEPARATION-001 | ADE MUST separate reasoning and business conclusions from HTML or visualization rendering; reasoning artifacts SHALL be generated independently from presentation to ensure auditability and reuse. | Architecture: Reasoning phase produces `ReasoningArtifact` (JSON); Rendering phase consumes `ReasoningArtifact` to produce HTML; Files: `products/ade/tools/reasoning_builder.py` → `products/ade/tools/render_*.py`; No reasoning logic in render modules | MUST | BRD-ALIGN-004 | Separation of concerns |

---

## Cross-References

- **BRD**: [BRD-agents.md](../01_brd/BRD-agents.md)
- **System Design**: [agents-and-tools.md](../04_systemdesign/agents-and-tools.md)
