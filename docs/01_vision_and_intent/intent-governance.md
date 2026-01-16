# Developer Intent: Governance & Compliance (INT-GOV)

> **Maps to**: [BRD-governance.md](../02_brd/BRD-governance.md)  
> **Version**: 1.1  
>
> **Source**: Extracted from [intent.md](intent.md) § 2  

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-13 | Header version normalization |

## 2.1 Human Oversight

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-001** | High-risk actions must require human approval before execution | Regulatory compliance, risk mitigation |
| **INT-GOV-002** | Approval requests must include context: what, why, impact | Humans need information to decide |
| **INT-GOV-003** | Approvers must be able to approve, reject, or request changes | Flexibility in oversight |
| **INT-GOV-004** | Approval decisions must be recorded with approver identity and timestamp | Complete audit trail |
| **INT-GOV-005** | Workflows must pause gracefully while awaiting approval | No orphaned or stuck processes |
| **INT-GOV-006** | Workflows must resume correctly after approval/rejection | Seamless continuation |

---

## 2.2 Security & Privacy

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-010** | PII must never appear in logs, traces, or persisted data | Privacy regulations (GDPR, SOC 2) |
| **INT-GOV-011** | Credentials and secrets must be redacted from all outputs | Security best practice |
| **INT-GOV-012** | Redaction must be automatic—not dependent on developer action | Defense in depth; humans forget |
| **INT-GOV-013** | Custom redaction patterns must be configurable per product | Domain-specific sensitivity |
| **INT-GOV-014** | Redaction failures must halt execution rather than leak data | Fail-safe, not fail-open |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| PII never in logs | SSN appears in trace event |
| Credentials never exposed | API key in error message |
| Redaction is automatic | Developer must call redact() |

---

## 2.3 Policy Enforcement

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-020** | Certain tools must be prohibitable by policy | Risk control |
| **INT-GOV-021** | Certain models must be prohibitable by policy | Compliance with usage agreements |
| **INT-GOV-022** | Policy violations must block execution—not just warn | Enforceable governance |
| **INT-GOV-023** | Policies must be configurable per product | Product-specific governance |
| **INT-GOV-024** | Policy decisions must be logged for audit | Traceability |
| **INT-GOV-025** | Low-confidence interpretations must pause for user clarification | Prevents misguided execution |
| **INT-GOV-026** | Confidence thresholds must be configurable per product | Domain-appropriate sensitivity |
| **INT-GOV-027** | Semantic validation failures must block execution | Fail-safe behavior |

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Hooks cannot be bypassed | Developer disables governance |
| Policy violations block | Warning logged but execution continues |
| Budgets are hard limits | Limit exceeded but run continues |

---

## 2.4 Semantic Confidence Governance (Added: 2026-01-13)

> **Intent**: Confidence thresholds and governance hooks for semantic interpretation.

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-CONF-001** | Default confidence threshold must be configurable in `configs/app.yaml` | Platform-wide baseline |
| **INT-GOV-CONF-002** | Per-product confidence threshold override must be supported in `configs/products.yaml` | Domain-appropriate sensitivity |
| **INT-GOV-CONF-003** | Default threshold must be 0.7 (adjustable) | Balance between usability and safety |
| **INT-GOV-CONF-004** | Confidence below threshold must trigger ASK_USER (not silent failure) | User gets opportunity to clarify |
| **INT-GOV-CONF-005** | Governance hook `check_semantic_confidence` must enforce thresholds | Enforceable via governance layer |
| **INT-GOV-CONF-006** | Effective confidence is minimum of (envelope.confidence, validation.revised_confidence) | Conservative confidence calculation |
| **INT-GOV-CONF-007** | Threshold enforcement must be logged with confidence values | Audit trail for threshold decisions |

### Configuration (New: 2026-01-13)

**Platform Default** (`configs/app.yaml`):
```yaml
semantic:
  default_confidence_threshold: 0.7
  require_semantic_phase: true
```

**Per-Product Override** (`configs/products.yaml`):
```yaml
by_product:
  ade:
    semantic_confidence_threshold: 0.8  # Stricter for production
  hello_world:
    semantic_confidence_threshold: 0.5  # More lenient for demo
```

### Constraints (Non-Negotiable)

| Constraint | Violation Example |
|------------|-------------------|
| Threshold is enforced | Low confidence proceeds without check |
| Override requires explicit config | Implicit threshold changes |
| Confidence check is governance hook | Check embedded in business logic |

---

## 2.5 Cost Controls

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-030** | Each workflow run must have enforceable budget limits | Cost predictability |
| **INT-GOV-031** | Budget limits must cover: LLM tokens, tool calls, time | Comprehensive control |
| **INT-GOV-032** | Budget exhaustion must pause/terminate the workflow | Prevent runaway costs |
| **INT-GOV-033** | Current budget consumption must be trackable in real-time | Operational awareness |
| **INT-GOV-034** | Budget alerts must trigger before limits are reached | Proactive management |

---

## 2.6 Audit & Traceability

### Intent

| ID | Intent | Rationale |
|----|--------|-----------|
| **INT-GOV-040** | Every action must be traceable to: who, what, when, why | Compliance requirement |
| **INT-GOV-041** | State transitions must be immutable once recorded | Non-repudiation |
| **INT-GOV-042** | Audit logs must be queryable by run, user, timeframe | Investigation support |
| **INT-GOV-043** | Audit data must be exportable in standard formats | External audit tools |
| **INT-GOV-044** | Audit retention period must be configurable | Compliance with data policies |

---

## BRD Derivation

This document derives the following in [BRD-governance.md](../02_brd/BRD-governance.md):

- INT-GOV-* → BRD-GOV-*
- INT-GOV-CONF-* → BRD-GOV-CONF-*
