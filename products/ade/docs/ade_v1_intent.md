# ADE - Analyst-Driven Exploration

Solution Document (V1 - Intent-Aligned, Minimal)

## 1. Purpose and Positioning
ADE is an analyst-centric business analysis system, not:
- a BI dashboard
- a fixed analytics pipeline
- an anomaly-only engine

ADE exists to support real analyst thinking, not replace it.

Primary goal:
Enable analysts to ask open-ended business questions, guide reasoning with governance and controls, and produce shareable business insights plus auditable reasoning.

## 2. What ADE Is
ADE is a guided analysis runner where:
1) An analyst starts with a natural language intent
2) The system:
   - interprets intent
   - forms hypotheses when appropriate
   - identifies required data
   - executes tools deterministically
   - synthesizes insights
3) The analyst:
   - clarifies intent when needed
   - provides missing inputs
   - approves or redirects decisions
4) ADE produces:
   - a Business Insight output (HTML)
   - a Reasoning and Evidence Pack (HTML/MD)

ADE is not opinionated about the analysis shape:
- It may produce charts, tables, summaries, comparisons, trends, or plain answers
- No assumption that anomaly detection is required

## 3. Key Design Principle
ADE is intent-driven, not tool-driven.

Tools exist to serve the analysis, not to define it.

An analyst can ask:
- "What were sales for the last 3 quarters?"
- "Why did expenses spike in Q4?"
- "Compare region A vs B"
- "Summarize trends in this dataset"

ADE must not force hypotheses, anomaly checks, or charts unless relevant.

## 4. Analysis Lifecycle
ADE follows an 8-stage analytical reasoning loop:
1) Intent Understanding
   - Parse analyst's business question
   - Identify scope, entities, timeframe, metrics
   - Confidence assessed
2) Clarification (HITL - User Input)
   - Ask questions when intent is ambiguous or underspecified
   - Example questions:
     - "Which metric should we focus on?"
     - "Do you want averages or growth rates?"
     - "Which time window?"
3) Hypothesis Formation (Optional)
   - Only if the intent implies explanation or causality
   - Example hypotheses:
     - seasonality
     - data outage
     - structural change
   - Skipped entirely for factual or descriptive asks
4) Data Identification and Validation
   - Identify datasets (uploaded or registered)
   - Validate sufficiency
   - Request more data if needed
5) Planning
   - Build an explicit analysis plan:
     - steps
     - tools
     - dependencies
     - decision points
   - Plan is transparent and inspectable
6) Execution
   - Deterministic tools run via orchestrator
   - LLMs used only for interpretation and synthesis
   - No autonomous branching
7) Decision and Approval (HITL - Approval)
   - Required for:
     - chart type selection
     - hypothesis inclusion or exclusion
     - final insight framing
   - Analyst may approve, reject, or comment
8) Synthesis and Output
   - Produce final business insight
   - Generate evidence and reasoning pack

## 5. Human-in-the-Loop Model
ADE has two distinct HITL modes:

### A. User Input (Clarification)
Triggered when:
- intent confidence is low
- multiple valid analysis paths exist
- missing parameters

Example:
{
  "question": "Which metric should we focus on?",
  "options": ["mean", "median", "growth_rate"],
  "required": true
}

### B. User Approval (Decision Gate)
Triggered when:
- ADE proposes a decision
- output direction is locked

Examples:
- "Proceed with growth-rate analysis?"
- "Include seasonality hypothesis?"

Both are:
- recorded in events.jsonl
- referenced in evidence output
- replayable for audit

## 6. Output Artifacts

### 6.1 Business Insight Output (Primary)
Audience: Business stakeholders
Format: HTML (V1)

Must include:
- Analysis title and question
- Executive summary (clear, concise)
- Key findings (metrics, deltas, observations)
- Visuals only if helpful
- Referenced datasets (names, columns)
- Assumptions and limitations
- Confidence score plus reasons

Must NOT include:
- step IDs
- raw traces
- debug dumps
- repeated tables

This output must be email-shareable and presentation-ready.

### 6.2 Reasoning and Evidence Pack (Secondary)
Audience: Audit, governance, internal review
Format: HTML or Markdown

Derived from:
- events.jsonl
- structured run state
- approvals and inputs

Includes:
- intent interpretation
- plan and changes
- user inputs and approvals
- hypotheses considered and rejected
- tools executed
- dataset references
- decision rationale

Important: This is not chain-of-thought. It is decision provenance reconstructed from events.

## 7. Observability and Storage
For each run:
observability/
  ade/
    <run_id>/
      events.jsonl          (append-only)
      input/
        <user inputs>       (references only)
      output/
        response.json
        business_insight.html
        evidence_pack.html

Notes:
- Datasets themselves are not duplicated
- Only dataset identifiers are recorded
- Observability is mandatory for ADE runs

## 8. Framework vs Product Responsibility
Framework owns:
- Orchestration
- HITL mechanics (pause/resume)
- Tool execution
- Event emission
- Observability storage
- Governance enforcement

ADE product owns:
- Intent interpretation logic
- Planning heuristics
- Domain tools (analytics, stats)
- Output rendering templates
- Hypothesis logic (optional)

## 9. V1 Scope Control
In scope (V1):
- Single dataset analysis
- Uploaded or registered datasets
- HTML outputs
- Manual approvals and inputs

Out of scope (V1):
- BI dashboards
- Live DB connectors
- Auto-tool discovery
- Multi-dataset joins
- Real-time streaming
- Agent-to-agent autonomy

## 10. Decision on Codebase Direction
Do NOT start fresh. Repurpose ADE, but cut aggressively.

Why:
- Orchestrator and observability already exist
- HITL semantics already present
- Rewrites would reintroduce mistakes

Approach:
- Remove anomaly-first assumptions
- Make hypotheses optional
- Improve outputs
- Reduce flow rigidity

## 11. Success Criteria for ADE V1
ADE V1 is successful if:
- Analyst can ask any reasonable business question
- System pauses appropriately for clarification
- No forced analysis pattern
- Outputs are business-shareable
- Reasoning is auditable
- Codebase feels smaller, not bigger

## Final Call
You are not building analytics automation.
You are building structured analytical thinking at scale.
