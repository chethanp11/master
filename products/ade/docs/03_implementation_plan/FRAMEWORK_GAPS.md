# ADE Framework Gaps

> **Purpose**: Log framework gaps that impact ADE product implementation, per TS-AGENT-FRI-004.  
> **Last Updated**: 2026-01-21  
> **Status**: Active tracking document  

---

## Gap Register

| Gap ID | BRD ID | Tech Spec ID | Gap Description | Workaround Status | Resolution |
|--------|--------|--------------|-----------------|-------------------|------------|
| — | — | — | No gaps currently logged. | — | — |

---

## Process

When a framework gap is identified:

1. Add entry to the table above with a unique Gap ID (FG-001, FG-002, ...).
2. Reference the BRD requirement and Tech Spec ID that the gap impacts.
3. Call `core.governance.hooks.escalate_framework_gap(gap_id, description)` at runtime.
4. Document workaround if any, or mark as "Blocked" if no workaround exists.
5. Track resolution via platform team engagement.

---

## Escalation API

```python
from core.governance.hooks import escalate_framework_gap

# Example usage
escalate_framework_gap(
    gap_id="FG-001",
    description="core.orchestrator does not support conditional step skipping based on agent output"
)
```

---

## Notes

- This document is maintained as part of the ADE product codebase.
- Gap escalation events are logged to `core.memory.observability_store` for platform team visibility.
- Workarounds must not duplicate core module logic (per TS-AGENT-FRI-002).
