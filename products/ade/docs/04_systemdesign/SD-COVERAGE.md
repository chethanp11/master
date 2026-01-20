# ADE System Design Coverage Matrix

> **Document**: System Design Coverage (ADE)  
> **Version**: 1.2  
> **Last Updated**: 2026-01-21  
> **Status**: V1.2 Release — TS- Prefix Normalization Complete

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-13 | Initial release |
| 1.1 | 2026-01-17 | Added semantic interpretation coverage |
| 1.2 | 2026-01-21 | Normalized to TS- prefix format; added 17 new V1.4 Tech Spec IDs; updated gap register with 8 new gaps |

---

## Coverage Matrix

| Tech Spec ID | Tech Spec Source | System Design Reference | Status |
|--------------|------------------|-------------------------|--------|
| TS-AGENT-GEN-001 | TS-agents.md#TS-AGENT-GEN-001 | agents-and-tools.md#agents | Covered |
| TS-AGENT-GEN-002 | TS-agents.md#TS-AGENT-GEN-002 | agents-and-tools.md#agents | Covered |
| TS-AGENT-GEN-003 | TS-agents.md#TS-AGENT-GEN-003 | agents-and-tools.md#agents | Covered |
| TS-AGENT-INTENT-001 | TS-agents.md#TS-AGENT-INTENT-001 | agents-and-tools.md#agents | Covered |
| TS-AGENT-INTENT-002 | TS-agents.md#TS-AGENT-INTENT-002 | agents-and-tools.md#agents | Covered |
| TS-AGENT-INTENT-003 | TS-agents.md#TS-AGENT-INTENT-003 | agents-and-tools.md#agents | Covered |
| TS-AGENT-INTENT-004 | TS-agents.md#TS-AGENT-INTENT-004 | agents-and-tools.md#agents | Covered |
| TS-AGENT-PLAN-001 | TS-agents.md#TS-AGENT-PLAN-001 | agents-and-tools.md#agents | Covered |
| TS-AGENT-PLAN-002 | TS-agents.md#TS-AGENT-PLAN-002 | agents-and-tools.md#agents | Covered |
| TS-AGENT-PROPOSAL-001 | TS-agents.md#TS-AGENT-PROPOSAL-001 | agents-and-tools.md#agents | Covered |
| TS-AGENT-PROPOSAL-002 | TS-agents.md#TS-AGENT-PROPOSAL-002 | agents-and-tools.md#agents | Covered |
| TS-AGENT-PROPOSAL-003 | TS-agents.md#TS-AGENT-PROPOSAL-003 | agents-and-tools.md#agents | Covered |
| TS-AGENT-PLANNING-001 | TS-agents.md#TS-AGENT-PLANNING-001 | agents-and-tools.md#agents | Covered |
| TS-AGENT-PLANNING-002 | TS-agents.md#TS-AGENT-PLANNING-002 | agents-and-tools.md#agents | Covered |
| TS-AGENT-SUFF-001 | TS-agents.md#TS-AGENT-SUFF-001 | agents-and-tools.md#agents | Covered |
| TS-AGENT-SUFF-002 | TS-agents.md#TS-AGENT-SUFF-002 | agents-and-tools.md#agents | Covered |
| TS-AGENT-SUFF-003 | TS-agents.md#TS-AGENT-SUFF-003 | agents-and-tools.md#agents | Covered |
| TS-AGENT-SUFF-004 | TS-agents.md#TS-AGENT-SUFF-004 | agents-and-tools.md#agents | Covered |
| TS-AGENT-DASH-001 | TS-agents.md#TS-AGENT-DASH-001 | agents-and-tools.md#agents | Covered |
| TS-AGENT-DASH-002 | TS-agents.md#TS-AGENT-DASH-002 | agents-and-tools.md#agents | Covered |
| BRD-INTEL-001 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-INTEL-001` | `products/ade/docs/04_systemdesign/schemas.md#2-8-intentframe` | Covered |
| BRD-INTEL-002 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-INTEL-002` | `products/ade/docs/04_systemdesign/schemas.md#2-8-intentframe` | Covered |
| BRD-INTEL-003 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-INTEL-003` | `products/ade/docs/04_systemdesign/flows.md#5-error-handling` | Missing |
| BRD-INTEL-004 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-INTEL-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-5-sufficiency_evaluator` | Covered |
| BRD-INTEL-005 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-INTEL-005` | `products/ade/docs/04_systemdesign/schemas.md#2-1-decisionpacket` | Covered |
| BRD-CRIT-001 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-CRIT-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-6-critic_evaluator` | Covered |
| BRD-CRIT-002 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-CRIT-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-6-critic_evaluator` | Covered |
| BRD-CRIT-003 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-CRIT-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-6-critic_evaluator` | Covered |
| BRD-CRIT-004 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-CRIT-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-6-critic_evaluator` | Covered |
| BRD-CRIT-005 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-CRIT-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-6-critic_evaluator` | Partial |
| BRD-TOOLSEL-001 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-TOOLSEL-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-2-plan_agent` | Covered |
| BRD-TOOLSEL-002 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-TOOLSEL-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-2-plan_agent` | Covered |
| BRD-TOOLSEL-003 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-TOOLSEL-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-2-plan_agent` | Covered |
| BRD-TOOLSEL-004 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-TOOLSEL-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-2-plan_agent` | Covered |
| BRD-NARR-004 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-NARR-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-7-dashboard_agent` | Partial |
| BRD-CONF-005 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-CONF-005` | `products/ade/docs/04_systemdesign/architecture.md#6-configuration` | Covered |
| BRD-ALIGN-001 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-ALIGN-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-ALIGN-002 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-ALIGN-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-FRI-001 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-FRI-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-FRI-002 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-FRI-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-FRI-003 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-FRI-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-FRI-004 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-FRI-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-FRI-005 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-FRI-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-NRL-001 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-NRL-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-NRL-002 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-NRL-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-NRL-003 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-NRL-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| BRD-NRL-004 | `products/ade/docs/02_techspec/AGENT-agents.md#BRD-NRL-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Missing |
| SEM-ADAPTER-001 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ADAPTER-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-ADAPTER-002 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ADAPTER-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-ADAPTER-003 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ADAPTER-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-ADAPTER-004 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ADAPTER-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-ADAPTER-005 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ADAPTER-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-INTENT-001 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-INTENT-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-INTENT-002 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-INTENT-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-INTENT-003 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-INTENT-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-INTENT-004 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-INTENT-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-INTENT-005 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-INTENT-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-INTENT-006 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-INTENT-006` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-INTENT-007 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-INTENT-007` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-INTENT-008 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-INTENT-008` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-VALIDATE-001 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-VALIDATE-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-VALIDATE-002 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-VALIDATE-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-VALIDATE-003 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-VALIDATE-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-VALIDATE-004 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-VALIDATE-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-VALIDATE-005 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-VALIDATE-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-VALIDATE-006 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-VALIDATE-006` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-VALIDATE-007 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-VALIDATE-007` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-CLARIFY-001 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-CLARIFY-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-CLARIFY-002 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-CLARIFY-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-CLARIFY-003 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-CLARIFY-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-CLARIFY-004 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-CLARIFY-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-CLARIFY-005 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-CLARIFY-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-CLARIFY-006 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-CLARIFY-006` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-ROUTER-001 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ROUTER-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-ROUTER-002 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ROUTER-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-ROUTER-003 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ROUTER-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-ROUTER-004 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ROUTER-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-ROUTER-005 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-ROUTER-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-OBS-001 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-OBS-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-OBS-002 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-OBS-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-OBS-003 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-OBS-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-OBS-004 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-OBS-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-OBS-005 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-OBS-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-OBS-006 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-OBS-006` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| SEM-OBS-007 | `products/ade/docs/02_techspec/AGENT-agents.md#SEM-OBS-007` | `products/ade/docs/04_systemdesign/agents-and-tools.md#agents` | Covered |
| FLOW-EXEC-001 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-EXEC-001` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-EXEC-002 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-EXEC-002` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-EXEC-003 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-EXEC-003` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-V1-001 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-V1-001` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-V1-002 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-V1-002` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-V1-003 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-V1-003` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-V1-004 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-V1-004` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-V1-005 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-V1-005` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| BRD-PLAN-007 | `products/ade/docs/02_techspec/FLOW-flows.md#BRD-PLAN-007` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-3-plan_proposal_agent` | Covered |
| BRD-PLAN-008 | `products/ade/docs/02_techspec/FLOW-flows.md#BRD-PLAN-008` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-3-plan_proposal_agent` | Covered |
| BRD-PLAN-009 | `products/ade/docs/02_techspec/FLOW-flows.md#BRD-PLAN-009` | `products/ade/docs/04_systemdesign/agents-and-tools.md#2-4-planning_agent` | Covered |
| FLOW-VIZ-001 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-VIZ-001` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-VIZ-002 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-VIZ-002` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-VIZ-003 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-VIZ-003` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-VIZ-004 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-VIZ-004` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-INPUT-001 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-INPUT-001` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-INPUT-002 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-INPUT-002` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-INPUT-003 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-INPUT-003` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-COND-001 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-COND-001` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-COND-002 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-COND-002` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-ERR-001 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-ERR-001` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-ERR-002 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-ERR-002` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-ARTF-001 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-ARTF-001` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-ARTF-002 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-ARTF-002` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-ARTF-003 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-ARTF-003` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| FLOW-ARTF-004 | `products/ade/docs/02_techspec/FLOW-flows.md#FLOW-ARTF-004` | `products/ade/docs/04_systemdesign/flows.md#flow-overview` | Covered |
| TOOL-GEN-001 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-GEN-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-GEN-002 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-GEN-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-GEN-003 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-GEN-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-GEN-004 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-GEN-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-DATA-001 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-DATA-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-DATA-002 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-DATA-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-DATA-003 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-DATA-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-DATA-004 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-DATA-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-DATA-005 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-DATA-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ANALYSIS-001 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ANALYSIS-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ANALYSIS-002 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ANALYSIS-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ANALYSIS-003 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ANALYSIS-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ANALYSIS-004 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ANALYSIS-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ANALYSIS-005 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ANALYSIS-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ANALYSIS-006 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ANALYSIS-006` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ANALYSIS-007 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ANALYSIS-007` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-VIZ-001 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-VIZ-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-VIZ-002 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-VIZ-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-VIZ-003 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-VIZ-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-VIZ-004 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-VIZ-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ASSEMBLE-001 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ASSEMBLE-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ASSEMBLE-002 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ASSEMBLE-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ASSEMBLE-003 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ASSEMBLE-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ASSEMBLE-004 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ASSEMBLE-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ASSEMBLE-005 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ASSEMBLE-005` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ASSEMBLE-006 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ASSEMBLE-006` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-ASSEMBLE-007 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-ASSEMBLE-007` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-RENDER-001 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-RENDER-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-RENDER-002 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-RENDER-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-RENDER-003 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-RENDER-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-RENDER-004 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-RENDER-004` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| TOOL-NARR-001 | `products/ade/docs/02_techspec/TOOL-tools.md#TOOL-NARR-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#tools` | Covered |
| OBJ-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#OBJ-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Clarification Needed |
| OBJ-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#OBJ-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Clarification Needed |
| OBJ-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#OBJ-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Clarification Needed |
| OBJ-004 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#OBJ-004` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Clarification Needed |
| OBJ-005 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#OBJ-005` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Clarification Needed |
| OBJ-006 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#OBJ-006` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Clarification Needed |
| OBJ-007 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#OBJ-007` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Clarification Needed |
| IO-IN-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-IN-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-IN-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-IN-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-IN-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-IN-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-IN-004 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-IN-004` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-DATA-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-DATA-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-DATA-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-DATA-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-DATA-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-DATA-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-DATA-004 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-DATA-004` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-USER-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-USER-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-USER-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-USER-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-USER-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-USER-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-OUT-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-OUT-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-OUT-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-OUT-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-OUT-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-OUT-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-OUT-004 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-OUT-004` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| BRD-QUAL-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-QUAL-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-2-output-quality-gates` | Partial |
| BRD-QUAL-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-QUAL-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-2-output-quality-gates` | Partial |
| BRD-QUAL-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-QUAL-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-2-output-quality-gates` | Partial |
| BRD-QUAL-004 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-QUAL-004` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-2-output-quality-gates` | Partial |
| BRD-QUAL-010 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-QUAL-010` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-2-output-quality-gates` | Partial |
| BRD-QUAL-011 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-QUAL-011` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-2-output-quality-gates` | Partial |
| BRD-QUAL-012 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-QUAL-012` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-2-output-quality-gates` | Partial |
| BRD-VER-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-VER-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-1-primary-outputs` | Covered |
| BRD-VER-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-VER-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-1-primary-outputs` | Covered |
| BRD-VER-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-VER-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-1-primary-outputs` | Partial |
| BRD-DAB-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-DAB-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-1-primary-outputs` | Covered |
| BRD-DAB-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-DAB-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-1-primary-outputs` | Covered |
| BRD-DAB-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-DAB-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-1-primary-outputs` | Partial |
| BRD-DAB-004 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-DAB-004` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-1-primary-outputs` | Partial |
| BRD-DAB-005 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#BRD-DAB-005` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#5-1-primary-outputs` | Partial |
| IO-EVID-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-EVID-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-EVID-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-EVID-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-EVID-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-EVID-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-EVID-004 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-EVID-004` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-ARTF-001 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-ARTF-001` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-ARTF-002 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-ARTF-002` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-ARTF-003 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-ARTF-003` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-ARTF-004 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-ARTF-004` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| IO-ARTF-005 | `products/ade/docs/02_techspec/IO-inputs-outputs.md#IO-ARTF-005` | `products/ade/docs/04_systemdesign/inputs-and-outputs.md#input-payloads` | Covered |
| SCHEMA-GEN-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-GEN-001` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-GEN-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-GEN-002` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-GEN-003 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-GEN-003` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-DP-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-DP-001` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-DP-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-DP-002` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-DP-003 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-DP-003` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-DS-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-DS-001` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-DS-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-DS-002` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-DS-003 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-DS-003` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-BR-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-BR-001` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-BR-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-BR-002` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-BR-003 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-BR-003` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-FIND-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-FIND-001` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-FIND-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-FIND-002` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-VS-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-VS-001` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-VS-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-VS-002` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-VS-003 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-VS-003` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-AR-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-AR-001` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-AR-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-AR-002` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-IF-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-IF-001` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-IF-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-IF-002` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-IF-003 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-IF-003` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| BRD-IF-006 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#BRD-IF-006` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| BRD-VAL-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#BRD-VAL-001` | `products/ade/docs/04_systemdesign/agents-and-tools.md#3-5-rendering-tools` | Covered |
| BRD-VAL-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#BRD-VAL-002` | `products/ade/docs/04_systemdesign/agents-and-tools.md#3-5-rendering-tools` | Covered |
| BRD-VAL-003 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#BRD-VAL-003` | `products/ade/docs/04_systemdesign/agents-and-tools.md#3-5-rendering-tools` | Covered |
| BRD-CTX-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#BRD-CTX-001` | `products/ade/docs/04_systemdesign/schemas.md#6-context-pack-schema` | Covered |
| BRD-CTX-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#BRD-CTX-002` | `products/ade/docs/04_systemdesign/schemas.md#6-context-pack-schema` | Covered |
| BRD-CTX-003 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#BRD-CTX-003` | `products/ade/docs/04_systemdesign/schemas.md#6-context-pack-schema` | Covered |
| BRD-CTX-004 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#BRD-CTX-004` | `products/ade/docs/04_systemdesign/schemas.md#6-context-pack-schema` | Partial |
| SCHEMA-APP-001 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-APP-001` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |
| SCHEMA-APP-002 | `products/ade/docs/02_techspec/SCHEMA-schemas.md#SCHEMA-APP-002` | `products/ade/docs/04_systemdesign/schemas.md#core-schemas` | Covered |

### New V1.4/V1.5 Tech Spec Requirements

| Tech Spec ID | Tech Spec Source | System Design Reference | Status |
|--------------|------------------|-------------------------|--------|
| TS-AGENT-REASON-001 | TS-agents.md#TS-AGENT-REASON-001 | agents-and-tools.md#reasoning | Covered |
| TS-AGENT-REASON-002 | TS-agents.md#TS-AGENT-REASON-002 | agents-and-tools.md#reasoning | Covered |
| TS-AGENT-REASON-003 | TS-agents.md#TS-AGENT-REASON-003 | — | Missing |
| TS-AGENT-REASON-004 | TS-agents.md#TS-AGENT-REASON-004 | agents-and-tools.md#sufficiency | Covered |
| TS-AGENT-REASON-005 | TS-agents.md#TS-AGENT-REASON-005 | schemas.md#DecisionPacket | Covered |
| TS-AGENT-CRIT-001 | TS-agents.md#TS-AGENT-CRIT-001 | agents-and-tools.md#critic | Covered |
| TS-AGENT-CRIT-002 | TS-agents.md#TS-AGENT-CRIT-002 | agents-and-tools.md#critic | Covered |
| TS-AGENT-CRIT-003 | TS-agents.md#TS-AGENT-CRIT-003 | agents-and-tools.md#critic | Covered |
| TS-AGENT-CRIT-004 | TS-agents.md#TS-AGENT-CRIT-004 | agents-and-tools.md#critic | Covered |
| TS-AGENT-CRIT-005 | TS-agents.md#TS-AGENT-CRIT-005 | — | Missing |
| TS-AGENT-TOOLSEL-001 | TS-agents.md#TS-AGENT-TOOLSEL-001 | agents-and-tools.md#planning | Covered |
| TS-AGENT-TOOLSEL-002 | TS-agents.md#TS-AGENT-TOOLSEL-002 | agents-and-tools.md#planning | Covered |
| TS-AGENT-TOOLSEL-003 | TS-agents.md#TS-AGENT-TOOLSEL-003 | agents-and-tools.md#planning | Covered |
| TS-AGENT-TOOLSEL-004 | TS-agents.md#TS-AGENT-TOOLSEL-004 | agents-and-tools.md#planning | Covered |
| TS-AGENT-FRI-001 | TS-agents.md#TS-AGENT-FRI-001 | — | Missing |
| TS-AGENT-FRI-002 | TS-agents.md#TS-AGENT-FRI-002 | — | Missing |
| TS-AGENT-FRI-003 | TS-agents.md#TS-AGENT-FRI-003 | — | Missing |
| TS-AGENT-FRI-004 | TS-agents.md#TS-AGENT-FRI-004 | — | Missing |
| TS-AGENT-FRI-005 | TS-agents.md#TS-AGENT-FRI-005 | — | Missing |
| TS-AGENT-NRL-001 | TS-agents.md#TS-AGENT-NRL-001 | — | Missing |
| TS-AGENT-NRL-002 | TS-agents.md#TS-AGENT-NRL-002 | — | Missing |
| TS-AGENT-NRL-003 | TS-agents.md#TS-AGENT-NRL-003 | — | Missing |
| TS-AGENT-NRL-004 | TS-agents.md#TS-AGENT-NRL-004 | — | Missing |
| TS-AGENT-TERM-001 | TS-agents.md#TS-AGENT-TERM-001 | — | Missing |
| TS-AGENT-TERM-002 | TS-agents.md#TS-AGENT-TERM-002 | — | Missing |
| TS-AGENT-TERM-003 | TS-agents.md#TS-AGENT-TERM-003 | — | Missing |
| TS-AGENT-NARR-005 | TS-agents.md#TS-AGENT-NARR-005 | — | Missing |
| TS-AGENT-CONF-003 | TS-agents.md#TS-AGENT-CONF-003 | — | Missing |
| TS-SEM-VALIDATE-008 | TS-agents.md#TS-SEM-VALIDATE-008 | — | Missing |
| TS-SEM-VALIDATE-009 | TS-agents.md#TS-SEM-VALIDATE-009 | — | Missing |
| TS-TOOL-GEN-005 | TS-tools.md#TS-TOOL-GEN-005 | agents-and-tools.md#tools | Covered |
| TS-TOOL-GEN-006 | TS-tools.md#TS-TOOL-GEN-006 | agents-and-tools.md#tools | Covered |
| TS-TOOL-GEN-007 | TS-tools.md#TS-TOOL-GEN-007 | — | Missing |
| TS-TOOL-ANALYSIS-008 | TS-tools.md#TS-TOOL-ANALYSIS-008 | — | Missing |
| TS-IO-OBJ-001 | TS-inputs-outputs.md#TS-IO-OBJ-001 | inputs-and-outputs.md | Clarification Needed |
| TS-IO-OBJ-002 | TS-inputs-outputs.md#TS-IO-OBJ-002 | inputs-and-outputs.md | Clarification Needed |
| TS-IO-OBJ-003 | TS-inputs-outputs.md#TS-IO-OBJ-003 | inputs-and-outputs.md | Clarification Needed |
| TS-IO-OBJ-004 | TS-inputs-outputs.md#TS-IO-OBJ-004 | inputs-and-outputs.md | Clarification Needed |
| TS-IO-OBJ-005 | TS-inputs-outputs.md#TS-IO-OBJ-005 | inputs-and-outputs.md | Clarification Needed |
| TS-IO-OBJ-006 | TS-inputs-outputs.md#TS-IO-OBJ-006 | inputs-and-outputs.md | Clarification Needed |
| TS-IO-OBJ-007 | TS-inputs-outputs.md#TS-IO-OBJ-007 | inputs-and-outputs.md | Clarification Needed |
| TS-IO-OBJ-008 | TS-inputs-outputs.md#TS-IO-OBJ-008 | — | Missing |
| TS-IO-DATA-005 | TS-inputs-outputs.md#TS-IO-DATA-005 | inputs-and-outputs.md | Covered |
| TS-IO-DATA-006 | TS-inputs-outputs.md#TS-IO-DATA-006 | inputs-and-outputs.md | Covered |
| TS-IO-DATA-007 | TS-inputs-outputs.md#TS-IO-DATA-007 | inputs-and-outputs.md | Covered |
| TS-IO-DATA-008 | TS-inputs-outputs.md#TS-IO-DATA-008 | inputs-and-outputs.md | Covered |
| TS-IO-USER-004 | TS-inputs-outputs.md#TS-IO-USER-004 | inputs-and-outputs.md | Covered |
| TS-IO-OUT-005 | TS-inputs-outputs.md#TS-IO-OUT-005 | inputs-and-outputs.md | Covered |
| TS-IO-OUT-006 | TS-inputs-outputs.md#TS-IO-OUT-006 | inputs-and-outputs.md | Covered |
| TS-IO-OUT-007 | TS-inputs-outputs.md#TS-IO-OUT-007 | — | Missing |
| TS-IO-QUAL-001 | TS-inputs-outputs.md#TS-IO-QUAL-001 | inputs-and-outputs.md | Partial |
| TS-IO-QUAL-002 | TS-inputs-outputs.md#TS-IO-QUAL-002 | inputs-and-outputs.md | Partial |
| TS-IO-QUAL-003 | TS-inputs-outputs.md#TS-IO-QUAL-003 | inputs-and-outputs.md | Partial |
| TS-IO-QUAL-004 | TS-inputs-outputs.md#TS-IO-QUAL-004 | inputs-and-outputs.md | Partial |
| TS-IO-QUAL-005 | TS-inputs-outputs.md#TS-IO-QUAL-005 | inputs-and-outputs.md | Partial |
| TS-IO-QUAL-006 | TS-inputs-outputs.md#TS-IO-QUAL-006 | inputs-and-outputs.md | Partial |
| TS-IO-QUAL-007 | TS-inputs-outputs.md#TS-IO-QUAL-007 | inputs-and-outputs.md | Partial |
| TS-IO-QUAL-008 | TS-inputs-outputs.md#TS-IO-QUAL-008 | — | Missing |
| TS-IO-VER-001 | TS-inputs-outputs.md#TS-IO-VER-001 | inputs-and-outputs.md | Covered |
| TS-IO-VER-002 | TS-inputs-outputs.md#TS-IO-VER-002 | inputs-and-outputs.md | Covered |
| TS-IO-VER-003 | TS-inputs-outputs.md#TS-IO-VER-003 | inputs-and-outputs.md | Partial |
| TS-IO-DAB-001 | TS-inputs-outputs.md#TS-IO-DAB-001 | inputs-and-outputs.md | Covered |
| TS-IO-DAB-002 | TS-inputs-outputs.md#TS-IO-DAB-002 | inputs-and-outputs.md | Covered |
| TS-IO-DAB-003 | TS-inputs-outputs.md#TS-IO-DAB-003 | inputs-and-outputs.md | Partial |
| TS-IO-DAB-004 | TS-inputs-outputs.md#TS-IO-DAB-004 | inputs-and-outputs.md | Partial |
| TS-IO-DAB-005 | TS-inputs-outputs.md#TS-IO-DAB-005 | inputs-and-outputs.md | Partial |
| TS-FLOW-V1-006 | TS-flows.md#TS-FLOW-V1-006 | flows.md | Partial |
| TS-FLOW-V1-007 | TS-flows.md#TS-FLOW-V1-007 | flows.md | Partial |
| TS-FLOW-V1-008 | TS-flows.md#TS-FLOW-V1-008 | flows.md | Partial |
| TS-FLOW-V1-009 | TS-flows.md#TS-FLOW-V1-009 | — | Missing |
| TS-SCHEMA-DP-004 | TS-schemas.md#TS-SCHEMA-DP-004 | schemas.md | Covered |
| TS-SCHEMA-DP-005 | TS-schemas.md#TS-SCHEMA-DP-005 | schemas.md | Covered |
| TS-SCHEMA-DP-006 | TS-schemas.md#TS-SCHEMA-DP-006 | schemas.md | Covered |
| TS-SCHEMA-DP-007 | TS-schemas.md#TS-SCHEMA-DP-007 | schemas.md | Covered |
| TS-SCHEMA-DP-008 | TS-schemas.md#TS-SCHEMA-DP-008 | schemas.md | Covered |
| TS-SCHEMA-DS-004 | TS-schemas.md#TS-SCHEMA-DS-004 | schemas.md | Covered |
| TS-SCHEMA-DS-005 | TS-schemas.md#TS-SCHEMA-DS-005 | schemas.md | Covered |
| TS-SCHEMA-DS-006 | TS-schemas.md#TS-SCHEMA-DS-006 | schemas.md | Covered |
| TS-SCHEMA-DS-007 | TS-schemas.md#TS-SCHEMA-DS-007 | schemas.md | Covered |
| TS-SCHEMA-DS-008 | TS-schemas.md#TS-SCHEMA-DS-008 | schemas.md | Covered |
| TS-SCHEMA-BR-004 | TS-schemas.md#TS-SCHEMA-BR-004 | schemas.md | Covered |
| TS-SCHEMA-BR-005 | TS-schemas.md#TS-SCHEMA-BR-005 | schemas.md | Covered |
| TS-SCHEMA-BR-006 | TS-schemas.md#TS-SCHEMA-BR-006 | schemas.md | Covered |
| TS-SCHEMA-BR-007 | TS-schemas.md#TS-SCHEMA-BR-007 | schemas.md | Covered |
| TS-SCHEMA-BR-008 | TS-schemas.md#TS-SCHEMA-BR-008 | schemas.md | Covered |
| TS-SCHEMA-BR-009 | TS-schemas.md#TS-SCHEMA-BR-009 | schemas.md | Covered |
| TS-SCHEMA-BR-010 | TS-schemas.md#TS-SCHEMA-BR-010 | schemas.md | Covered |
| TS-SCHEMA-BR-011 | TS-schemas.md#TS-SCHEMA-BR-011 | schemas.md | Covered |
| TS-SCHEMA-BR-012 | TS-schemas.md#TS-SCHEMA-BR-012 | schemas.md | Covered |
| TS-SCHEMA-FIND-003 | TS-schemas.md#TS-SCHEMA-FIND-003 | schemas.md | Covered |
| TS-SCHEMA-FIND-004 | TS-schemas.md#TS-SCHEMA-FIND-004 | schemas.md | Covered |
| TS-SCHEMA-VS-004 | TS-schemas.md#TS-SCHEMA-VS-004 | schemas.md | Covered |
| TS-SCHEMA-AR-003 | TS-schemas.md#TS-SCHEMA-AR-003 | schemas.md | Covered |
| TS-SCHEMA-AR-004 | TS-schemas.md#TS-SCHEMA-AR-004 | schemas.md | Covered |
| TS-SCHEMA-AR-005 | TS-schemas.md#TS-SCHEMA-AR-005 | schemas.md | Covered |
| TS-SCHEMA-AR-006 | TS-schemas.md#TS-SCHEMA-AR-006 | schemas.md | Covered |
| TS-SCHEMA-AR-007 | TS-schemas.md#TS-SCHEMA-AR-007 | schemas.md | Covered |
| TS-SCHEMA-AR-008 | TS-schemas.md#TS-SCHEMA-AR-008 | schemas.md | Covered |
| TS-SCHEMA-IF-004 | TS-schemas.md#TS-SCHEMA-IF-004 | schemas.md | Covered |
| TS-SCHEMA-IF-005 | TS-schemas.md#TS-SCHEMA-IF-005 | schemas.md | Covered |
| TS-SCHEMA-IF-006 | TS-schemas.md#TS-SCHEMA-IF-006 | schemas.md | Covered |
| TS-SCHEMA-IF-007 | TS-schemas.md#TS-SCHEMA-IF-007 | schemas.md | Covered |
| TS-SCHEMA-IF-008 | TS-schemas.md#TS-SCHEMA-IF-008 | schemas.md | Covered |
| TS-SCHEMA-IF-009 | TS-schemas.md#TS-SCHEMA-IF-009 | schemas.md | Covered |
| TS-SCHEMA-IF-010 | TS-schemas.md#TS-SCHEMA-IF-010 | schemas.md | Covered |
| TS-SCHEMA-VAL-001 | TS-schemas.md#TS-SCHEMA-VAL-001 | agents-and-tools.md | Covered |
| TS-SCHEMA-VAL-002 | TS-schemas.md#TS-SCHEMA-VAL-002 | agents-and-tools.md | Covered |
| TS-SCHEMA-VAL-003 | TS-schemas.md#TS-SCHEMA-VAL-003 | agents-and-tools.md | Covered |
| TS-SCHEMA-CTX-001 | TS-schemas.md#TS-SCHEMA-CTX-001 | schemas.md | Covered |
| TS-SCHEMA-CTX-002 | TS-schemas.md#TS-SCHEMA-CTX-002 | schemas.md | Covered |
| TS-SCHEMA-CTX-003 | TS-schemas.md#TS-SCHEMA-CTX-003 | schemas.md | Covered |
| TS-SCHEMA-CTX-004 | TS-schemas.md#TS-SCHEMA-CTX-004 | — | Missing |
| TS-SCHEMA-CTX-005 | TS-schemas.md#TS-SCHEMA-CTX-005 | — | Missing |
| TS-SCHEMA-APP-003 | TS-schemas.md#TS-SCHEMA-APP-003 | schemas.md | Covered |
| TS-SCHEMA-APP-004 | TS-schemas.md#TS-SCHEMA-APP-004 | schemas.md | Covered |
| TS-SCHEMA-APP-005 | TS-schemas.md#TS-SCHEMA-APP-005 | schemas.md | Covered |
| TS-SCHEMA-EVITEM-001 | TS-schemas.md#TS-SCHEMA-EVITEM-001 | — | Missing |
| TS-SCHEMA-EVITEM-002 | TS-schemas.md#TS-SCHEMA-EVITEM-002 | — | Missing |

---

| Gap ID | Tech Spec IDs | Status | Missing in System Design | Why It Matters | Implementation Impact |
|--------|---------------|--------|---------------------------|----------------|-----------------------|
| GAP-001 | TS-IO-OBJ-001..008 | Clarification Needed | Objectives remain unstated in SD | Objectives define success targets for implementation scope. | Clarification required before build |
| GAP-003 | TS-AGENT-REASON-003 | Missing | Bounded cycles (iterations/tools/time) not documented | Limits prevent unbounded reasoning loops. | Code addition required |
| GAP-004 | TS-AGENT-CRIT-005 | Missing | Blocking critique does not stop execution | Missing gate can allow unreviewed outputs. | Code addition required |
| GAP-006 | TS-TOOL-NARR-001 | Partial | Anomaly narrative output exists only in dashboard_agent and is not wired into flows | Narrative completeness is inconsistent. | Wiring / integration only |
| GAP-012 | TS-SCHEMA-CTX-004, TS-SCHEMA-CTX-005 | Missing | Reasoning outputs do not cite context pack artifacts; grounding not enforced | Limits traceability of context grounding. | Wiring / integration only |
| GAP-014 | TS-IO-QUAL-001..008 | Partial | Quality checks do not validate Vega-Lite spec or browser compatibility | Output usability checks are incomplete. | Code extension required |
| GAP-015 | TS-IO-VER-003 | Partial | Dependency pinning not enforced (versions only recorded) | Reproducibility requirements remain incomplete. | Clarification required before build |
| GAP-016 | TS-IO-DAB-003..005 | Partial | Advisory labeling exists but no explicit prevention of downstream actions | Decision boundary remains implicit. | Code extension required |
| GAP-017 | TS-AGENT-FRI-001..002 | Missing | Framework alignment invariants not described | Prevents product re-implementation of core primitives. | Clarification required before build |
| GAP-018 | TS-AGENT-FRI-003..005 | Missing | Framework reliance and escalation invariants not described | Protects thick framework / thin product model. | Code addition required |
| GAP-019 | TS-AGENT-NRL-001..004 | Missing | No runtime learning invariant not described | Guarantees run independence and reproducibility. | Clarification required before build |
| GAP-020 | TS-AGENT-TERM-001..003 | Missing | Terminal outcomes (SUCCESS, PARTIAL_SUCCESS, ASK_USER, ABORT) not designed | Explicit run termination states missing. | Code addition required |
| GAP-021 | TS-AGENT-NARR-005 | Missing | User-facing explanations not sourced from decision records | Narrative traceability gaps. | Code addition required |
| GAP-022 | TS-AGENT-CONF-003 | Missing | Confidence thresholds not externally configurable | Limits operational flexibility. | Code extension required |
| GAP-023 | TS-SEM-VALIDATE-008, TS-SEM-VALIDATE-009 | Missing | Dataset and metric references not validated against available data | Invalid references may pass. | Code addition required |
| GAP-024 | TS-TOOL-GEN-007 | Missing | Tool external network dependency ban not enforced | Reproducibility at risk. | CI/test enforcement required |
| GAP-025 | TS-TOOL-ANALYSIS-008 | Missing | Anomaly severity ranking not documented | Anomaly prioritization unclear. | Code extension required |
| GAP-026 | TS-IO-OUT-007 | Missing | Output directory auto-creation not documented | Output path reliability. | Code addition required |
| GAP-027 | TS-FLOW-V1-006..009 | Partial | Plan summary objective/assumptions/replan/constraints not fully documented | Plan transparency incomplete. | Code extension required |
| GAP-028 | TS-SCHEMA-EVITEM-001, TS-SCHEMA-EVITEM-002 | Missing | Evidence item confidence and values schema not documented | Evidence completeness. | Schema addition required |

---

## Summary

- **Total Tech Spec IDs Tracked**: ~200
- **Covered (✅)**: ~165
- **Partial**: 15
- **Missing/Gaps**: 20 gap IDs covering ~35 TS requirements
- **Coverage**: ~82.5%

---

## SD-COVERAGE GAP COUNT: 20
