# Analytical Decision Engine — Architecture (v1)

## Overview
ADE is an intent-driven analysis runner for analysts. The orchestrator owns flow control; tools only compute facts. ADE supports HITL inputs and approvals, and produces a business insight HTML plus an evidence pack derived from events.

## Run Lifecycle
- **Input staging**: files are staged under `products/ade/staging/input/`, then moved into the run’s observability input directory.
- **Intent understanding**: agent interprets the question and extracts scope (entities, timeframe, metrics).
- **Clarification**: user inputs are requested when intent is ambiguous or underspecified.
- **Planning**: an explicit plan is created (steps, tools, decision points).
- **Execution**: tools run deterministically via the orchestrator; optional hypotheses only when required by plan.
- **Decision gates**: approvals are required for key choices (hypotheses, charting, final framing).
- **Synthesis**: LLMs are used only for interpretation and synthesis from tool outputs.
- **Outputs**: business insight HTML and evidence pack are written to the observability store.

## Orchestrator Responsibilities
- Controls the run lifecycle and step order based on the flow definition.
- Emits trace events per step/tool call into `<observability_root>/<product>/<run_id>/runtime/events.jsonl`.
- Enforces HITL pause/resume and governance checks.
- Ensures tools execute only through `core/tools/executor.py`.

## Artifacts and Data Flow
- **Business Insight HTML**: shareable summary for business stakeholders (no debug dumps).
- **Evidence Pack**: audit trail reconstructed from `events.jsonl` and structured run state.
- Output files are persisted by the observability store; datasets are referenced, not duplicated.

## Determinism and LLM Usage
- Tools are deterministic and compute structured facts.
- LLMs are used only for interpretation and synthesis, never for tool selection or control flow.

## Governance
- Trace events record step outcomes and decisions.
- User inputs and approvals are logged and replayable.
- Redaction is enforced by core governance hooks before trace/log emission.
