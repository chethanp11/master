# ADE BRD Coverage Analysis

> **Document**: BRD Coverage Matrix  
> **Product**: Analytical Decision Engine (ADE)  
> **Version**: 1.1  
> **Last Updated**: 2026-01-17  
> **Status**: V1 Release

> **Purpose**: Trace ADE Developer Intent (INT-*) to ADE BRD requirements and flag gaps.

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-17 | Initial ADE intent-to-BRD coverage matrix |

## Coverage Summary

| Intent File | BRD Document | Coverage | Notes |
|-------------|--------------|----------|-------|
| [intent-overview-flows.md](../00_product_intent/intent-overview-flows.md) | [BRD-overview.md](BRD-overview.md) | ✅ Covered | Objectives, scope, stakeholders, capabilities mapped at section level. |
| [intent-overview-flows.md](../00_product_intent/intent-overview-flows.md) | [BRD-flows.md](BRD-flows.md) | ✅ Covered | Flow, UI, plan approval, determinism mapped to BRD-V1/VIZ/PREF/PLAN/DET/CFG. |
| [intent-agents-tools.md](../00_product_intent/intent-agents-tools.md) | [BRD-agents.md](BRD-agents.md) | ⚠️ Partial | INT-AGT-* lacks explicit BRD coverage; other agent intents map cleanly. |
| [intent-agents-tools.md](../00_product_intent/intent-agents-tools.md) | [BRD-tools.md](BRD-tools.md) | ✅ Covered | Tools, data, analysis, visualization, assembly, rendering mapped. |
| [intent-data-outputs.md](../00_product_intent/intent-data-outputs.md) | [BRD-data.md](BRD-data.md) | ✅ Covered | Data, schemas, evidence, trace refs mapped. |
| [intent-data-outputs.md](../00_product_intent/intent-data-outputs.md) | [BRD-outputs.md](BRD-outputs.md) | ⚠️ Partial | INT-VER-* (version metadata) not present in BRD-outputs. |
| [intent-intel-acceptance.md](../00_product_intent/intent-intel-acceptance.md) | All BRDs | ⚠️ Partial | Several INT-INTEL-* families are not represented in BRDs. |

---

## Coverage Matrix

| Intent Family | Intent IDs | BRD Document | BRD IDs / Sections | Coverage | Notes |
|---------------|------------|--------------|--------------------|----------|-------|
| Overview | INT-OVERVIEW-001..006 | BRD-overview | §1 Vision, §5 Capabilities, §6 Trust/Audit | ✅ | Covered by narrative sections. |
| Objectives | INT-OBJ-001..007 | BRD-overview | §2 Objectives (OBJ-001..007) | ✅ | Objectives map directly. |
| Scope | INT-OVERVIEW-004..006 | BRD-overview | §3 Scope | ✅ | In-scope/out-of-scope covered. |
| Stakeholders | INT-OVERVIEW-* | BRD-overview | §4 Stakeholders | ✅ | Stakeholder mapping covered. |
| Flow overview | INT-FLOWS-001..003 | BRD-flows | §1 Flow Overview | ✅ | Flow list and use cases covered. |
| ade_v1 flow | INT-V1-001..008 | BRD-flows | BRD-V1-001..008 | ✅ | Direct ID alignment. |
| visualization flow | INT-VIZ-001..007 | BRD-flows | BRD-VIZ-001..007 | ✅ | Direct ID alignment. |
| UI preferences | INT-UI-001..003 | BRD-flows | BRD-PREF-001..003 | ✅ | Direct mapping. |
| Plan approval | INT-UI-004..006 | BRD-flows | BRD-PLAN-001..006 | ✅ | Direct mapping. |
| Determinism | INT-DET-001..004 | BRD-flows | BRD-DET-001..004 | ⚠️ Partial | No explicit BRD for "no dynamic flow mutation". |
| Autonomy config | INT-DET-002 | BRD-flows | BRD-CFG-001 | ✅ | Suggest_only autonomy covered. |
| Agent advisory | INT-AGT-001..004 | BRD-agents | — | ❌ Gap | BRD lacks advisory-only requirements. |
| Intent interpretation | INT-INTENT-001..007 | BRD-agents | BRD-INTENT-001..007 | ✅ | Direct mapping. |
| Plan generation | INT-PLAN-001..008 | BRD-agents | BRD-PLANGEN-001..004, BRD-PROPOSAL-001..004 | ✅ | Direct mapping. |
| Data sufficiency | INT-SUFF-001..006 | BRD-agents | BRD-SUFF-001..006 | ✅ | Direct mapping. |
| Narrative | INT-NARR-001..004 | BRD-agents | BRD-NARR-001..003 | ⚠️ Partial | BRD lacks explicit anomaly narrative requirement. |
| Confidence | INT-CONF-001..004 | BRD-agents | BRD-CONF-001..004 | ⚠️ Partial | No BRD for configurable thresholds. |
| Semantic interpretation | INT-SEM-001..010 | BRD-agents | BRD-SEM-001..005, BRD-INTENT-TAX-* | ✅ | Intent taxonomy + envelope covered. |
| Semantic validation | INT-SEM-VAL-001..005 | BRD-agents | BRD-SEM-VAL-001..005 | ✅ | Direct mapping. |
| Semantic observability | INT-SEM-010 | BRD-agents | BRD-SEM-OBS-001..005 | ✅ | Trace metadata covered. |
| Tool determinism | INT-TOOL-001..005 | BRD-tools | BRD-TOOL-001..004 | ⚠️ Partial | Evidence items not explicit in BRD-TOOL-* (covered in BRD-METRIC/ANOM/EVID). |
| Data tools | INT-DATA-001..006 | BRD-tools | BRD-DATA-001..006 | ✅ | Direct mapping. |
| Analysis tools | INT-ANAL-001..007 | BRD-tools | BRD-ANOM-001..005, BRD-HYP-001..006, BRD-DRIVER-001..002 | ✅ | Direct mapping. |
| Visualization tools | INT-VIS-001..004 | BRD-tools | BRD-CHART-001..007, BRD-REC-001..002 | ✅ | Direct mapping. |
| Assembly tools | INT-ASM-001..005 | BRD-tools | BRD-PKT-001..008, BRD-RPT-001..007, BRD-EVID-001..003 | ✅ | Direct mapping. |
| Rendering tools | INT-REND-001..004 | BRD-tools | BRD-HTML-001..004, BRD-EXP-001..003 | ✅ | Direct mapping. |
| Data formats | INT-FMT-001..005 | BRD-data | BRD-FMT-001..005 | ✅ | Direct mapping. |
| Data locations | INT-LOC-001..004 | BRD-data | BRD-LOC-001..004 | ✅ | Direct mapping. |
| Schemas | INT-SCHEMA-001..004 | BRD-data | BRD-SCHEMA-001..004 | ✅ | Direct mapping. |
| DecisionPacket schema | INT-DP-001..007 | BRD-data | BRD-DP-001..007 | ✅ | Direct mapping. |
| BusinessReport schema | INT-BR-001..008 | BRD-data | BRD-BR-001..008 | ✅ | Direct mapping. |
| IntentFrame schema | INT-IF-001..006 | BRD-data | BRD-IF-001..005 | ⚠️ Partial | BRD lacks blocking_questions field requirement. |
| Evidence schema | INT-EV-001..004 | BRD-data | BRD-EVREF-001..004 | ✅ | Direct mapping. |
| Primary outputs | INT-OUT-001..017 | BRD-outputs | BRD-OUT-001..017 | ✅ | Direct mapping. |
| Output location | INT-OUTLOC-001..003 | BRD-outputs | BRD-LOC-001..003 | ✅ | Direct mapping. |
| Audit traceability | INT-AUDIT-001..004 | BRD-outputs | BRD-AUDIT-001..004 | ✅ | Direct mapping. |
| Execution traceability | INT-TRACE-001..004 | BRD-outputs | BRD-AUDIT-010..013 | ✅ | Direct mapping. |
| Transparency | INT-TRANS-001..004 | BRD-outputs | BRD-AUDIT-020..023 | ✅ | Direct mapping. |
| Reproducibility | INT-REPRO-001..004 | BRD-outputs | BRD-REPRO-001..004 | ✅ | Direct mapping. |
| Output quality gates | INT-QUAL-001..004 | BRD-outputs | BRD-QUAL-001..004 | ✅ | Direct mapping. |
| Version transparency | INT-VER-001..003 | BRD-outputs | — | ❌ Gap | No BRD requirement for version metadata. |
| Multi-pass reasoning | INT-INTEL-001..005 | BRD-agents | — | ❌ Gap | No BRD requirements for reasoning ladder. |
| Critique stage | INT-CRIT-001..005 | BRD-agents | — | ❌ Gap | Critique gate not captured in BRD. |
| Context packs | INT-CTX-001..004 | BRD-data/agents | — | ❌ Gap | Context Pack requirements absent in BRD. |
| Advisory tool selection | INT-TOOLSEL-001..004 | BRD-agents/tools | — | ❌ Gap | No BRD coverage for advisory selection. |
| Failure modes | INT-TERM-001..004 | BRD-flows | — | ❌ Gap | Explicit terminal outcomes not in BRD. |
| Plan review detail | INT-REVIEW-001..003 | BRD-flows | BRD-PLAN-001..006 | ⚠️ Partial | Plan detail granularity not in BRD. |
| Safe stopping | INT-STOP-001..002 | BRD-flows | — | ❌ Gap | Safe-exit rules not in BRD. |
| Framework alignment | INT-ALIGN-001..002 | All BRDs | — | ❌ Gap | Framework reliance intent not in BRD. |
| Framework reliance | INT-FRI-001..005 | All BRDs | — | ❌ Gap | No BRD enforcement of framework reliance. |
| Decision authority | INT-DAB-001..005 | BRD-outputs | — | ❌ Gap | Labeling discipline not in BRD. |
| No runtime learning | INT-NRL-001..004 | All BRDs | — | ❌ Gap | No BRD coverage for runtime learning constraints. |

---

## Gap Summary

| Gap Area | Missing Intent IDs | Suggested BRD Target |
|----------|--------------------|----------------------|
| Agent advisory boundary | INT-AGT-001..004 | BRD-agents.md |
| Dynamic flow mutation ban | INT-DET-004 | BRD-flows.md |
| IntentFrame blocking questions | INT-IF-006 | BRD-data.md |
| Version metadata in outputs | INT-VER-001..003 | BRD-outputs.md |
| Multi-pass reasoning ladder | INT-INTEL-001..005 | BRD-agents.md |
| Critique gate | INT-CRIT-001..005 | BRD-agents.md |
| Context pack grounding | INT-CTX-001..004 | BRD-data.md / BRD-agents.md |
| Advisory tool selection | INT-TOOLSEL-001..004 | BRD-tools.md / BRD-agents.md |
| Explicit terminal outcomes | INT-TERM-001..004 | BRD-flows.md |
| Plan review granularity | INT-REVIEW-001..003 | BRD-flows.md |
| Safe stopping rules | INT-STOP-001..002 | BRD-flows.md |
| Framework alignment rules | INT-ALIGN-001..002 | BRD-overview.md |
| Framework reliance invariant | INT-FRI-001..005 | BRD-overview.md |
| Decision authority boundary | INT-DAB-001..005 | BRD-outputs.md |
| No runtime learning | INT-NRL-001..004 | BRD-overview.md |
