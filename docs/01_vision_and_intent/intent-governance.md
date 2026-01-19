# Developer Intent: Governance & Compliance (INT-GOV)

> **Maps to**: [BRD-governance.md](../02_brd/BRD-governance.md)  
> **Version**: 1.2  

---

## Purpose

Define platform-level governance, security, and compliance intent that constrains all runtime behavior.

## Scope

- Platform-only governance, policy enforcement, and audit requirements.
- Product-specific policy content is out of scope.

---

## PLAT-GOV-HUMAN — Human Oversight

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-GOV-001 | High-risk actions SHALL require human approval before execution — Regulatory compliance, risk mitigation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-002 | Approval requests SHALL include context: what, why, impact — Humans need information to decide | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-003 | Approvers SHALL be able to approve, reject, or request changes — Flexibility in oversight | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-004 | Approval decisions SHALL be recorded with approver identity and timestamp — Complete audit trail | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-005 | Workflows SHALL pause gracefully while awaiting approval — No orphaned or stuck processes | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-006 | Workflows SHALL resume correctly after approval/rejection — Seamless continuation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-GOV-SEC — Security & Privacy

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-GOV-010 | PII SHALL never appear in logs, traces, or persisted data — Privacy regulations | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-011 | Credentials and secrets SHALL be redacted from all outputs — Security best practice | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-012 | Redaction SHALL be automatic, not dependent on developer action — Defense in depth | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-013 | Custom redaction patterns SHALL be configurable per product — Domain-specific sensitivity | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-014 | Redaction failures SHALL halt execution rather than leak data — Fail-safe behavior | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-015 | PII SHALL never appear in logs — Prevent privacy leaks | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-016 | Credentials SHALL never be exposed — Prevent secret leaks | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-017 | Redaction SHALL be automatic — Remove manual redaction dependency | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-GOV-POLICY — Policy Enforcement

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-GOV-020 | Certain tools SHALL be prohibitable by policy — Risk control | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-021 | Certain models SHALL be prohibitable by policy — Compliance with usage agreements | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-022 | Policy violations SHALL block execution, not just warn — Enforceable governance | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-023 | Policies SHALL be configurable per product — Product-specific governance | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-024 | Policy decisions SHALL be logged for audit — Traceability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-025 | Low-confidence interpretations SHALL pause for user clarification — Prevent misguided execution | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-026 | Confidence thresholds SHALL be configurable per product — Domain-appropriate sensitivity | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-027 | Semantic validation failures SHALL block execution — Fail-safe behavior | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-028 | Hooks SHALL NOT be bypassed — Prevent disabling governance | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-029 | Policy violations SHALL block execution — Enforce policy compliance | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-035 | Budgets SHALL be hard limits — Prevent overrun | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-GOV-CONF — Semantic Confidence Governance

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-GOV-CONF-001 | Default confidence threshold SHALL be configurable in `configs/app.yaml` — Platform-wide baseline | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-CONF-002 | Per-product confidence threshold override SHALL be supported in `configs/products.yaml` — Domain-appropriate sensitivity | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-CONF-003 | Default threshold SHALL be 0.7 (adjustable) — Balance usability and safety | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-CONF-004 | Confidence below threshold SHALL trigger ASK_USER — User gets opportunity to clarify | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-CONF-005 | Governance hook `check_semantic_confidence` SHALL enforce thresholds — Enforceable via governance layer | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-CONF-006 | Effective confidence SHALL be minimum of (envelope.confidence, validation.revised_confidence) — Conservative confidence calculation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-CONF-007 | Threshold enforcement SHALL be logged with confidence values — Audit trail for decisions | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-CONF-008 | Threshold SHALL be enforced — Prevent low-confidence execution | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-CONF-009 | Overrides SHALL require explicit config — Prevent implicit threshold changes | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-CONF-010 | Confidence check SHALL be a governance hook — Avoid business-logic-only enforcement | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-GOV-COST — Cost Controls

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-GOV-030 | Each workflow run SHALL have enforceable budget limits — Cost predictability | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-031 | Budget limits SHALL cover: LLM tokens, tool calls, time — Comprehensive control | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-032 | Budget exhaustion SHALL pause or terminate the workflow — Prevent runaway costs | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-033 | Current budget consumption SHALL be trackable in real time — Operational awareness | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-034 | Budget alerts SHALL trigger before limits are reached — Proactive management | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-GOV-AUDIT — Audit & Traceability

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| INT-GOV-040 | Every action SHALL be traceable to: who, what, when, why — Compliance requirement | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-041 | State transitions SHALL be immutable once recorded — Non-repudiation | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-042 | Audit logs SHALL be queryable by run, user, timeframe — Investigation support | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-043 | Audit data SHALL be exportable in standard formats — External audit tools | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |
| INT-GOV-044 | Audit retention period SHALL be configurable — Compliance with data policies | — | 2026-01-13 | V1.1 | ID NEEDS NORMALIZATION |

---

## PLAT-AUD — Decision Records

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-AUD-001 | Platform SHALL generate immutable decision records for every gated action, capturing options considered, evidence used, critique feedback, final choice, and confidence — Ensure auditable decision provenance | PLAT-CTRL-002 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |

---

## PLAT-POL — Runtime Integrity

### Intent

| ID | Intent | Depends on (intent ID) | Added Date | Version | Notes |
|----|--------|----------------------|------------|---------|-------|
| PLAT-POL-001 | Platform SHALL prevent runtime learning or self-modification during execution — Preserve determinism and auditability | PLAT-CTRL-001 | 2026-01-18 | V1.2 | V1.2, 2026-01-18 |

---

## Removed / Quarantined Content (Out of Platform Scope)

- **Summary**: Product-specific configuration examples (explicit product IDs in config examples).  
  **Original**: intent-governance.md § 2.4 (Configuration examples for per-product thresholds).  
  **Reason**: Product-scoped content.

---

## BRD Derivation

This document derives the following in [BRD-governance.md](../02_brd/BRD-governance.md):

- INT-GOV-* → BRD-GOV-*
- INT-GOV-CONF-* → BRD-GOV-CONF-*
