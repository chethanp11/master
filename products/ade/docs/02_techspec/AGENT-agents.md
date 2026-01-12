# ADE Agent Requirements

> **Document**: Technical Specification — Agents  
> **Prefix**: AGENT-*  
> **Requirements**: ~20

---

## 1. General Agent Requirements (AGENT-GEN)

### AGENT-GEN-001: Agent Descriptors
**Priority**: P0  
**Description**: All agents MUST have descriptors in `products/ade/descriptors.py`.

**Acceptance Criteria**:
- [ ] AgentDescriptor exists for each agent
- [ ] Descriptor includes purpose, capabilities, cost_hint
- [ ] AGENT_DESCRIPTORS map exports all descriptors

---

### AGENT-GEN-002: Cost Hints
**Priority**: P1  
**Description**: Agents MUST have accurate cost hints.

| Agent | Cost Hint |
|-------|-----------|
| intent_agent | MED |
| plan_agent | MED |
| plan_proposal_agent | LOW |
| planning_agent | MED |
| sufficiency_evaluator | LOW |
| dashboard_agent | MED |

---

### AGENT-GEN-003: Step Type Restrictions
**Priority**: P1  
**Description**: Agents MUST only be invoked from allowed step types.

| Agent | Allowed Step Types |
|-------|-------------------|
| plan_proposal_agent | agent, plan_proposal |
| (others) | agent |

---

## 2. intent_agent (AGENT-INTENT)

### AGENT-INTENT-001: Output Schema
**Priority**: P0  
**Description**: intent_agent MUST output IntentFrame schema.

**Fields**:
```python
intent_summary: str
inferred_entities: List[str]
inferred_metrics: List[str]
inferred_time_window: Optional[str]
requested_outputs: List[str]
confidence_score: float
confidence_label: str
blocking_required: bool
blocking_questions: List[str]
blocking_question: Optional[str]
```

---

### AGENT-INTENT-002: Confidence Scoring
**Priority**: P1  
**Description**: intent_agent MUST provide confidence_score (0.0-1.0) and confidence_label.

**Acceptance Criteria**:
- [ ] confidence_score is float between 0.0 and 1.0
- [ ] confidence_label is one of: "low", "medium", "high"
- [ ] Labels map to score ranges: low < 0.4, medium 0.4-0.7, high > 0.7

---

### AGENT-INTENT-003: Blocking Detection
**Priority**: P1  
**Description**: intent_agent MUST detect when clarification is needed.

**Acceptance Criteria**:
- [ ] blocking_required is True when dataset/metric/time window is missing
- [ ] blocking_questions lists specific questions to ask
- [ ] blocking_question contains the primary question

---

### AGENT-INTENT-004: Entity Extraction
**Priority**: P1  
**Description**: intent_agent MUST extract entities from user input.

**Acceptance Criteria**:
- [ ] Dataset names are extracted to inferred_entities
- [ ] Metric names are extracted to inferred_metrics
- [ ] Time windows are extracted to inferred_time_window

---

## 3. plan_agent (AGENT-PLAN)

### AGENT-PLAN-001: Output Schema
**Priority**: P0  
**Description**: plan_agent MUST output PlanSpec schema.

**Acceptance Criteria**:
- [ ] Output is valid PlanSpec
- [ ] Includes tool flags for conditional execution
- [ ] Plan is deterministic

---

### AGENT-PLAN-002: Deterministic Plans
**Priority**: P0  
**Description**: plan_agent MUST produce deterministic plans.

**Acceptance Criteria**:
- [ ] Same inputs produce identical plans
- [ ] No random selection of steps or tools
- [ ] Tool flags are derived from user input

---

## 4. plan_proposal_agent (AGENT-PROPOSAL)

### AGENT-PROPOSAL-001: Output Schema
**Priority**: P0  
**Description**: plan_proposal_agent MUST output PlanProposal.

**Fields**:
```python
proposal_id: str
summary: str
estimated_steps: int
estimated_cost: str  # "LOW", "MED", "HIGH"
requires_approval: bool
```

---

### AGENT-PROPOSAL-002: Approval Requirement
**Priority**: P0  
**Description**: plan_proposal_agent MUST set requires_approval appropriately.

**Acceptance Criteria**:
- [ ] requires_approval is True for non-trivial plans
- [ ] Execution pauses for user decision

---

### AGENT-PROPOSAL-003: Cost Estimation
**Priority**: P1  
**Description**: plan_proposal_agent MUST estimate execution cost.

**Acceptance Criteria**:
- [ ] estimated_cost reflects tool cost hints
- [ ] estimated_steps matches plan step count

---

## 5. planning_agent (AGENT-PLANNING)

### AGENT-PLANNING-001: Dual Role
**Priority**: P1  
**Description**: planning_agent MUST support both intent interpretation and replanning.

**Acceptance Criteria**:
- [ ] Used for intent_interpretation step in visualization flow
- [ ] Used for planning step after sufficiency_eval
- [ ] Context determines behavior

---

### AGENT-PLANNING-002: Replan Notes
**Priority**: P1  
**Description**: planning_agent MUST produce replan notes after rejection.

**Acceptance Criteria**:
- [ ] Notes explain what changed
- [ ] Restart step is identified

---

## 6. sufficiency_evaluator (AGENT-SUFF)

### AGENT-SUFF-001: Output Schema
**Priority**: P0  
**Description**: sufficiency_evaluator MUST output confidence_level and downgrade_reasons.

**Fields**:
```python
confidence_level: str  # "high", "medium", "low"
downgrade_reasons: List[str]
```

---

### AGENT-SUFF-002: Confidence Levels
**Priority**: P0  
**Description**: sufficiency_evaluator MUST use standard confidence levels.

**Acceptance Criteria**:
- [ ] confidence_level is one of: "high", "medium", "low"
- [ ] Level reflects data quality assessment

---

### AGENT-SUFF-003: Downgrade Reasons
**Priority**: P1  
**Description**: sufficiency_evaluator MUST explain confidence downgrades.

**Acceptance Criteria**:
- [ ] downgrade_reasons lists specific issues
- [ ] Reasons are human-readable
- [ ] Empty list when confidence is high

---

### AGENT-SUFF-004: Data Quality Assessment
**Priority**: P1  
**Description**: sufficiency_evaluator MUST assess data quality from data_reader output.

**Acceptance Criteria**:
- [ ] Evaluates row count sufficiency
- [ ] Evaluates column completeness
- [ ] Evaluates data freshness if time column exists

---

## 7. dashboard_agent (AGENT-DASH)

### AGENT-DASH-001: Narrative Output
**Priority**: P1  
**Description**: dashboard_agent MUST produce narrative summary.

**Acceptance Criteria**:
- [ ] Summary is human-readable text
- [ ] Summary reflects dataset characteristics
- [ ] Summary is concise (< 500 words)

---

### AGENT-DASH-002: Dataset Summary Input
**Priority**: P1  
**Description**: dashboard_agent MUST accept dataset summaries as input.

**Acceptance Criteria**:
- [ ] Can process multiple dataset summaries
- [ ] Summarizes key metrics and trends

---

## Cross-References

- **System Design**: [agents-and-tools.md](../04_systemdesign/agents-and-tools.md)
- **BRD**: [BRD-agents.md](../01_brd/BRD-agents.md)
