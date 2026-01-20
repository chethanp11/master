# BRD: Governance & Compliance

> **Document ID**: BRD-GOV  
> **Version**: 1.2  
> **Last Updated**: 2026-01-13

> **MASTER** — Managed AI Systems for Trusted Execution & Reasoning  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-12 | Initial release |
| 1.1 | 2026-01-13 | Added §3.8 Semantic Confidence Governance with INT-GOV-CONF-* requirements |

---

## Governing Architecture Invariants

The following architecture invariants from [Developer Intent](../00_developer_intent/intent.md) govern this BRD:

| INV | Invariant | Implication for Governance |
|-----|-----------|---------------------------|
| **INV-3** | Semantic Interpretation Is Probabilistic | Ambiguity is first-class state; HITL required when uncertain |
| **INV-4** | Decisions Must Be Explainable and Auditable | Decision artifacts with evidence, immutable once recorded |
| **INV-6** | Platform Laws Are Explicit and Non-Negotiable | Governance hooks non-bypassable at all lifecycle points |
| **INV-9** | Feedback Feeds Intent, Not Direct Code Changes | Governance lifecycle preserved even for urgent fixes |

---

## 1. Business Context

### Problem Statement
AI automation creates significant risk without proper governance:
- Autonomous agents can take actions with serious consequences
- Sensitive data (PII, credentials) can leak into logs and traces
- Runaway processes can consume unbounded resources
- Compliance auditors require complete action traceability
- Organizations need assurance that AI operates within boundaries

### Opportunity
A governance framework that provides:
- Configurable human-in-the-loop approval for high-risk actions
- Automatic redaction of sensitive data from all outputs
- Enforceable policies on tools, models, and behaviors
- Complete audit trails for compliance requirements
- Resource controls to prevent cost overruns

### Business Value
- **Regulatory compliance**: Meet audit and compliance requirements automatically
- **Risk mitigation**: Prevent unauthorized or harmful actions
- **Cost control**: Budget enforcement prevents runaway expenses
- **Trust**: Stakeholders can verify AI operates within boundaries

---

## 2. Stakeholders

| Stakeholder | Role | Primary Concern |
|-------------|------|-----------------|
| **Compliance Officer** | Ensures regulatory adherence | Audit trails, policy enforcement |
| **Security Engineer** | Protects sensitive data | PII redaction, credential safety |
| **Risk Manager** | Manages operational risk | Human oversight, approval workflows |
| **Finance** | Controls operational costs | Budget limits, usage tracking |
| **Auditor** | Verifies compliance | Complete traceability, evidence |

---

## 3. Business Requirements

> **Source**: [INT-GOV](../00_developer_intent/intent.md#2-governance--compliance-int-gov)

### 3.1 Human Oversight

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-GOV-001** | High-risk actions must require human approval before execution | P0 | INT-GOV-001 | 2026-01-12 |
| **BRD-GOV-002** | Approval requests must include context: what, why, impact | P0 | INT-GOV-002 | 2026-01-12 |
| **BRD-GOV-003** | Approvers must be able to approve, reject, or request changes | P0 | INT-GOV-003 | 2026-01-12 |
| **BRD-GOV-004** | Approval decisions must be recorded with approver identity and timestamp | P0 | INT-GOV-004 | 2026-01-12 |
| **BRD-GOV-005** | Workflows must pause gracefully while awaiting approval | P0 | INT-GOV-005 | 2026-01-12 |
| **BRD-GOV-006** | Workflows must resume correctly after approval/rejection | P0 | INT-GOV-006 | 2026-01-12 |

### 3.2 Security & Privacy

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-GOV-010** | PII must never appear in logs, traces, or persisted data | P0 | INT-GOV-010 | 2026-01-12 |
| **BRD-GOV-011** | Credentials and secrets must be redacted from all outputs | P0 | INT-GOV-011 | 2026-01-12 |
| **BRD-GOV-012** | Redaction must be automatic—not dependent on developer action | P0 | INT-GOV-012 | 2026-01-12 |
| **BRD-GOV-013** | Custom redaction patterns must be configurable per product | P1 | INT-GOV-013 | 2026-01-12 |
| **BRD-GOV-014** | Redaction failures must halt execution rather than leak data | P0 | INT-GOV-014 | 2026-01-12 |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| PII never in logs | SSN appears in trace event |
| Credentials never exposed | API key in error message |
| Redaction is automatic | Developer must call redact() |

### 3.3 Policy Enforcement

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-GOV-020** | Certain tools must be prohibitable by policy | P0 | INT-GOV-020 | 2026-01-12 |
| **BRD-GOV-021** | Certain models must be prohibitable by policy | P0 | INT-GOV-021 | 2026-01-12 |
| **BRD-GOV-022** | Policy violations must block execution—not just warn | P0 | INT-GOV-022 | 2026-01-12 |
| **BRD-GOV-023** | Policies must be configurable per product | P1 | INT-GOV-023 | 2026-01-12 |
| **BRD-GOV-024** | Policy decisions must be logged for audit | P0 | INT-GOV-024 | 2026-01-12 |
| **BRD-GOV-025** | Low-confidence interpretations must pause for user clarification | P0 | INT-GOV-025, INV-3 | 2026-01-12 |
| **BRD-GOV-026** | Confidence thresholds must be configurable per product | P1 | INT-GOV-026 | 2026-01-12 |
| **BRD-GOV-027** | Semantic validation failures must block execution | P0 | INT-GOV-027 | 2026-01-12 |

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Hooks cannot be bypassed | Developer disables governance |
| Policy violations block | Warning logged but execution continues |
| Budgets are hard limits | Limit exceeded but run continues |

### 3.4 Cost Controls

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-GOV-030** | Each workflow run must have enforceable budget limits | P0 | INT-GOV-030 | 2026-01-12 |
| **BRD-GOV-031** | Budget limits must cover: LLM tokens, tool calls, time | P0 | INT-GOV-031 | 2026-01-12 |
| **BRD-GOV-032** | Budget exhaustion must pause/terminate the workflow | P0 | INT-GOV-032 | 2026-01-12 |
| **BRD-GOV-033** | Current budget consumption must be trackable in real-time | P1 | INT-GOV-033 | 2026-01-12 |
| **BRD-GOV-034** | Budget alerts must trigger before limits are reached | P1 | INT-GOV-034 | 2026-01-12 |

### 3.5 Audit & Traceability

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-GOV-040** | Every action must be traceable to: who, what, when, why | P0 | INT-GOV-040 | 2026-01-12 |
| **BRD-GOV-041** | State transitions must be immutable once recorded | P0 | INT-GOV-041 | 2026-01-12 |
| **BRD-GOV-042** | Audit logs must be queryable by run, user, timeframe | P0 | INT-GOV-042 | 2026-01-12 |
| **BRD-GOV-043** | Audit data must be exportable in standard formats | P1 | INT-GOV-043 | 2026-01-12 |
| **BRD-GOV-044** | Audit retention period must be configurable | P1 | INT-GOV-044 | 2026-01-12 |
| **BRD-GOV-045** | Gated/consequential decisions must be recorded as decision artifacts | P0 | PLAT-AUD-001, INV-4 | Added: 2026-01-13 |
| **BRD-GOV-046** | Decision artifacts must capture: options considered, evidence, critique input, choice, justification, confidence | P0 | PLAT-AUD-001, INV-4 | Added: 2026-01-13 |
| **BRD-GOV-047** | Decision artifacts must be immutable once recorded | P0 | PLAT-AUD-001, INV-4 | Added: 2026-01-13 |

### 3.6 Governance Hooks

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-GOV-050** | Governance hooks must execute at defined lifecycle points | P0 | INV-6 | 2026-01-12 |
| **BRD-GOV-051** | Hooks must not be bypassable by agents or tools | P0 | INV-6 | 2026-01-12 |
| **BRD-GOV-052** | Hook failures must halt execution (fail-closed) | P0 | INV-6 | 2026-01-12 |
| **BRD-GOV-053** | Hooks must not perform logging (separation of concerns) | P0 | INV-6 | 2026-01-12 |
| **BRD-GOV-054** | Runtime execution must prevent learning or self-modification during execution | P0 | PLAT-POL-001 | 1.2 | Added: 2026-01-18 |

### 3.7 Semantic Interpretation Governance

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-GOV-060** | All semantic interpretations must be treated as hypotheses with confidence, not facts | P0 | INV-3 | 1.0 | Added: 2026-01-13 |
| **BRD-GOV-061** | System must represent interpretation as multiple competing candidates where ambiguity exists | P1 | INV-3 | 1.0 | Added: 2026-01-13 |
| **BRD-GOV-062** | Confidence and ambiguity must propagate into downstream artifacts, decisions, and outputs | P0 | INV-3 | 1.0 | Added: 2026-01-13 |
| **BRD-GOV-063** | When ambiguity exceeds policy thresholds, execution must require HITL or halt safely | P0 | INV-3 | 1.0 | Added: 2026-01-13 |

### 3.8 Semantic Confidence Governance (Added: 2026-01-13)

> **Source**: [INT-GOV-CONF](../00_developer_intent/intent.md#24-semantic-confidence-governance-added-2026-01-13)

| ID | Requirement | Priority | Source | Ver | Date |
|----|-------------|----------|--------|-----|------|
| **BRD-GOV-CONF-001** | Default confidence threshold must be configurable in `configs/app.yaml` | P0 | INT-GOV-CONF-001 | 1.1 | Added: 2026-01-13 |
| **BRD-GOV-CONF-002** | Per-product confidence threshold override must be supported in `configs/products.yaml` | P0 | INT-GOV-CONF-002 | 1.1 | Added: 2026-01-13 |
| **BRD-GOV-CONF-003** | Default threshold must be 0.7 (adjustable) | P1 | INT-GOV-CONF-003 | 1.1 | Added: 2026-01-13 |
| **BRD-GOV-CONF-004** | Confidence below threshold must trigger ASK_USER (not silent failure) | P0 | INT-GOV-CONF-004 | 1.1 | Added: 2026-01-13 |
| **BRD-GOV-CONF-005** | Governance hook `check_semantic_confidence` must enforce thresholds | P0 | INT-GOV-CONF-005 | 1.1 | Added: 2026-01-13 |
| **BRD-GOV-CONF-006** | Effective confidence is minimum of (envelope.confidence, validation.revised_confidence) | P0 | INT-GOV-CONF-006 | 1.1 | Added: 2026-01-13 |
| **BRD-GOV-CONF-007** | Threshold enforcement must be logged with confidence values | P1 | INT-GOV-CONF-007 | 1.1 | Added: 2026-01-13 |

**Configuration (New: 2026-01-13)**:

Platform Default (`configs/app.yaml`):
```yaml
semantic:
  default_confidence_threshold: 0.7
  require_semantic_phase: true
```

Per-Product Override (`configs/products.yaml`):
```yaml
by_product:
  ade:
    semantic_confidence_threshold: 0.8  # Stricter for production
  hello_world:
    semantic_confidence_threshold: 0.5  # More lenient for demo
```

**Constraints (Non-Negotiable from Intent)**:
| Constraint | Violation Example |
|------------|-------------------|
| Threshold is enforced | Low confidence proceeds without check |
| Override requires explicit config | Implicit threshold changes |
| Confidence check is governance hook | Check embedded in business logic |

---

## 4. User Stories

### Compliance Officer Stories
- **US-GOV-001**: As a compliance officer, I want all high-risk actions to require human approval so that we meet regulatory requirements.
- **US-GOV-002**: As a compliance officer, I want complete audit trails so that I can respond to auditor requests.
- **US-GOV-003**: As a compliance officer, I want PII automatically redacted so that we comply with privacy regulations.

### Security Engineer Stories
- **US-GOV-010**: As a security engineer, I want credentials never to appear in logs so that secrets remain protected.
- **US-GOV-011**: As a security engineer, I want to prohibit certain tools so that risky operations are blocked.
- **US-GOV-012**: As a security engineer, I want redaction to fail-closed so that leaks are impossible.

### Risk Manager Stories
- **US-GOV-020**: As a risk manager, I want to review high-risk actions before execution so that I can prevent harmful outcomes.
- **US-GOV-021**: As a risk manager, I want to see what the system plans to do so that I can make informed decisions.

### Finance Stories
- **US-GOV-030**: As a finance stakeholder, I want budget limits on workflows so that costs are predictable.
- **US-GOV-031**: As a finance stakeholder, I want to track usage in real-time so that I can manage budgets proactively.

---

## 5. Acceptance Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| PII leakage incidents | PII detected in logs/outputs | 0 |
| Policy enforcement rate | Policy violations blocked | 100% |
| Approval response capture | Approvals recorded with identity | 100% |
| Budget enforcement | Runs stopped at budget limit | 100% |
| Audit completeness | Actions with full trace | 100% |

---

## 6. Techspec Mapping

| BRD ID | Description | Derived Techspec | Ver |
|--------|-------------|------------------|-----|
| BRD-GOV-001 | Human approval | ORC-PAUSE-010...015, GOV-GATE-PLAN-* | 1.0 |
| BRD-GOV-002 | Approval context | ORC-PAUSE-012 (summary, instructions) | 1.0 |
| BRD-GOV-025 | Confidence-based pause | ORC-SEM-STOP-*, INT-SEM-CONF-* | 1.0 |
| BRD-GOV-026 | Confidence thresholds | INT-SEM-CONF-010...020 | 1.0 |
| BRD-GOV-027 | Semantic validation blocking | PROD-SEM-VAL-* | 1.0 |
| BRD-GOV-003 | Approval decisions | ORC-RESUME-001...010 | 1.0 |
| BRD-GOV-004 | Approval audit | ORC-RESUME-004 (resolved_by, decision) | 1.0 |
| BRD-GOV-005 | Graceful pause | ORC-RUN-015...018 (PAUSED states) | 1.0 |
| BRD-GOV-010 | PII redaction | GOV-SEC-030...035 | 1.0 |
| BRD-GOV-011 | Credential redaction | GOV-SEC-030 (keys, tokens) | 1.0 |
| BRD-GOV-012 | Automatic redaction | GOV-HOOK-010...015 | 1.0 |
| BRD-GOV-020 | Tool prohibition | GOV-POL-020...022 | 1.0 |
| BRD-GOV-021 | Model prohibition | GOV-POL-030...032 | 1.0 |
| BRD-GOV-022 | Policy blocking | GOV-HOOK-001 (non-bypassable) | 1.0 |
| BRD-GOV-030 | Budget limits | GOV-BUD-010...014 | 1.0 |
| BRD-GOV-031 | Budget types | GOV-BUD-011 (tokens, calls, time) | 1.0 |
| BRD-GOV-032 | Budget enforcement | GOV-HOOK-022...024 | 1.0 |
| BRD-GOV-040 | Action traceability | MEM-TRACE-001...010 | 1.0 |
| BRD-GOV-041 | Immutable state | ORC-RUN-004 (traced transitions) | 1.0 |
| BRD-GOV-045 | Decision artifacts | GOV-DEC-ARTIFACT-* | 1.0 |
| BRD-GOV-046 | Decision artifact content | GOV-DEC-CONTENT-* | 1.0 |
| BRD-GOV-047 | Artifact immutability | GOV-DEC-IMMUT-* | 1.0 |
| BRD-GOV-050 | Governance hooks | GOV-HOOK-001...005 | 1.0 |
| BRD-GOV-060 | Semantic hypothesis | INT-SEM-PROB-* | 1.0 |
| BRD-GOV-061 | Multiple candidates | INT-SEM-CAND-* | 1.0 |
| BRD-GOV-062 | Confidence propagation | INT-SEM-PROP-* | 1.0 |
| BRD-GOV-063 | Ambiguity escalation | INT-SEM-ESC-* | 1.0 |
| BRD-GOV-CONF-* | Semantic confidence governance | GOV-SEM-CONF-*, GOV-HOOK-SEM-* | 1.1 |

---

## 7. Cross-Cutting Requirements

> **Source**: [INT-LIFECYCLE](../00_developer_intent/intent.md#5-developer-intent-lifecycle-int-lifecycle), [INT-FACTORY](../00_developer_intent/intent.md#6-product-factory-model-int-factory)

### 7.1 Intent-to-BRD Traceability

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-GOV-LIFE-001** | Every governance intent point must map to at least one BRD requirement | P0 | INT-LIFECYCLE-020 | Added: 2026-01-13 |
| **BRD-GOV-LIFE-002** | BRD requirements must reference source intent | P0 | INT-LIFECYCLE-021 | Added: 2026-01-13 |
| **BRD-GOV-LIFE-003** | Intent updates must be versioned and reviewed | P0 | INT-LIFECYCLE-004 | Added: 2026-01-13 |

### 7.2 User Feedback Handling

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-GOV-LIFE-010** | User feedback is not Developer Intent | P0 | INT-LIFECYCLE-010 | Added: 2026-01-13 |
| **BRD-GOV-LIFE-011** | Feedback must be captured in structured format | P1 | INT-LIFECYCLE-011 | Added: 2026-01-13 |
| **BRD-GOV-LIFE-012** | Feedback must be reviewed before promotion to intent | P0 | INT-LIFECYCLE-012, INV-9 | Added: 2026-01-13 |
| **BRD-GOV-LIFE-013** | Bugs and enhancements follow governed lifecycle even when urgent | P0 | INV-9 | Added: 2026-01-13 |

### 7.3 Product Factory Model

| ID | Requirement | Priority | Source | Date |
|----|-------------|----------|--------|------|
| **BRD-GOV-FAC-001** | Products are forbidden from re-implementing governance services | P0 | INT-FACTORY-011 | Added: 2026-01-13 |
| **BRD-GOV-FAC-002** | Framework owns governance; products define what, framework defines how | P0 | INT-FACTORY-010, INT-FACTORY-013 | Added: 2026-01-13 |

---

## 8. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Memory Backend | Internal | Stores audit data |
| Tracer | Internal | Records events |
| Policy Configuration | Config | `configs/policies.yaml` |
| Security Patterns | Config | Redaction patterns |

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Approval bottleneck | Workflow delays | Clear SLAs, escalation paths |
| Over-aggressive redaction | Data loss | Configurable patterns, testing |
| Policy misconfiguration | Blocked legitimate actions | Validation, staging environment |
| Budget gaming | Exceeded costs | Hard limits, no soft caps |

---

## 10. Compliance Mapping

| Regulation | Relevant BRD Requirements |
|------------|--------------------------|
| **GDPR** | BRD-GOV-010 (PII), BRD-GOV-040 (audit), BRD-GOV-044 (retention) |
| **SOC 2** | BRD-GOV-001 (approval), BRD-GOV-040 (traceability), BRD-GOV-051 (controls) |
| **HIPAA** | BRD-GOV-010 (PHI), BRD-GOV-012 (automatic), BRD-GOV-014 (fail-safe) |
| **PCI-DSS** | BRD-GOV-011 (credentials), BRD-GOV-041 (immutable logs) |

---

## 11. Framework Laws Governing Governance

> **Source**: [Framework Laws](../00_developer_intent/intent.md#7-framework-laws)

| Law | Implication |
|-----|-------------|
| Governance hooks are mandatory | Every lifecycle point has mandatory hooks |
| Budgets are enforced | Hard limits, no soft caps |
| PII is never logged | Automatic redaction, fail-closed |
| Intent precedes BRD | Governance requirements derive from intent |
| Feedback is not intent | User feedback goes through review before promotion |

---

## Related Documents

- [Intent.md](../00_developer_intent/intent.md) — Source developer intent
- [Vision.md](../00_developer_intent/Vision.md) — Platform vision and principles
- [BRD-automation.md](BRD-automation.md) — Agent capabilities requiring governance
- [GOV-governance.md](../techspec/GOV-governance.md) — Technical governance specs
- [ORC-orchestration.md](../techspec/ORC-orchestration.md) — Pause/resume specs
