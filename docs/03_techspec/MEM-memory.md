# Memory and Observability Technical Specification

> **Document ID**: MEM / OBS  
> **Version**: 1.1.0  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-13

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial V1 specification |
| 1.1.0 | 2026-01-13 | Added: §12 Semantic Trace Events, §13 Reasoning Observability, §14 Explicit Non-Goals, §17 BRD Requirement Mapping |

---

## 1. Overview

The memory layer provides persistence and retrieval of run records, step records, trace events, 
and approval records. The observability layer writes structured artifacts to disk for debugging, 
auditing, and analysis.

### 1.1 Implementation References

| Component | File |
|-----------|------|
| Memory Interfaces | `core/memory/base.py` |
| Memory Router | `core/memory/router.py` |
| SQLite Backend | `core/memory/sqlite_backend.py` |
| In-Memory Backend | `core/memory/in_memory.py` |
| Observability Store | `core/memory/observability_store.py` |
| Tracer | `core/memory/tracing.py` |
| Run Schema | `core/contracts/run_schema.py` |

---

## 2. Data Contract Requirements

### 2.1 RunRecord Schema

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SCHEMA-001** | [V1] `RunRecord` MUST contain required fields: | MUST |
| | • `run_id` (string, auto-generated UUID) | |
| | • `product` (string, required) | |
| | • `flow` (string, required, aliased as `flow_id`) | |
| | • `status` (RunStatus enum, default `RUNNING`) | |
| | • `autonomy` (optional string) | |
| | • `started_at` (integer, epoch seconds, auto-generated) | |
| | • `finished_at` (optional integer, epoch seconds) | |
| | • `input` (optional dict) | |
| | • `output` (optional dict) | |
| | • `summary` (dict, default empty) | |

**Implementation**: `core/contracts/run_schema.py`

### 2.2 RunStatus Enum

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SCHEMA-002** | [V1] `RunStatus` MUST be one of: `RUNNING`, `PAUSED_WAITING_FOR_USER`, `PENDING_HUMAN`, `COMPLETED`, `FAILED`, `CANCELLED`, `ERROR` | MUST |

**Implementation**: `core/contracts/run_schema.py`

### 2.3 StepRecord Schema

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SCHEMA-003** | [V1] `StepRecord` MUST contain required fields: | MUST |
| | • `run_id` (string, required) | |
| | • `step_id` (string, required) | |
| | • `step_index` (integer, default 0, zero-based) | |
| | • `name` (string, default empty) | |
| | • `type` (string, default `tool`, one of `tool|agent|human_approval|subflow`) | |
| | • `status` (StepStatus enum, default `PENDING`) | |
| | • `started_at` (optional integer, epoch seconds) | |
| | • `finished_at` (optional integer, epoch seconds) | |
| | • `input` (optional dict) | |
| | • `output` (optional dict) | |
| | • `error` (optional dict, sanitized) | |
| | • `meta` (dict, default empty) | |

**Implementation**: `core/contracts/run_schema.py`

### 2.4 StepStatus Enum

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SCHEMA-004** | [V1] `StepStatus` MUST be one of: `PENDING`, `STARTED`, `RUNNING`, `COMPLETED`, `FAILED`, `SKIPPED`, `PAUSED`, `CANCELLED` | MUST |

**Implementation**: `core/contracts/run_schema.py`

### 2.5 TraceEvent Schema

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SCHEMA-005** | [V1] `TraceEvent` MUST contain required fields: | MUST |
| | • `event_id` (string, auto-generated UUID) | |
| | • `run_id` (string, required) | |
| | • `step_id` (optional string) | |
| | • `product` (string, required) | |
| | • `flow` (string, required) | |
| | • `kind` (string, default `INFO`, aliased as `event_type`) | |
| | • `ts` (integer, epoch seconds, auto-generated) | |
| | • `payload` (dict, default empty, sanitized) | |
| | • `redacted` (boolean, default false) | |

**Implementation**: `core/contracts/run_schema.py`

### 2.6 ApprovalRecord Schema

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SCHEMA-006** | [V1] `ApprovalRecord` MUST contain required fields: | MUST |
| | • `approval_id` (string, required) | |
| | • `run_id` (string, required) | |
| | • `step_id` (string, required) | |
| | • `product` (string, required) | |
| | • `flow` (string, required) | |
| | • `status` (string, default `PENDING`, one of `PENDING|APPROVED|REJECTED`) | |
| | • `requested_by` (optional string) | |
| | • `requested_at` (integer, required) | |
| | • `resolved_by` (optional string) | |
| | • `resolved_at` (optional integer) | |
| | • `decision` (optional string) | |
| | • `comment` (optional string) | |
| | • `context` (dict, default empty, scrubbed for UI display) | |

**Implementation**: `core/contracts/run_schema.py`

### 2.7 RunBundle Schema

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SCHEMA-007** | [V1] `RunBundle` MUST aggregate: | MUST |
| | • `run` (RunRecord, required) | |
| | • `steps` (list of StepRecord, default empty) | |
| | • `events` (list of TraceEvent, default empty) | |
| | • `approvals` (list of ApprovalRecord, default empty) | |

**Implementation**: `core/contracts/run_schema.py`

---

## 3. MemoryBackend Interface Requirements

### 3.1 Run Lifecycle Methods

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-API-001** | [V1] All `MemoryBackend` implementations MUST implement: | MUST |
| | • `create_run(run: RunRecord) -> None` | |
| | • `update_run_status(run_id: str, status: RunStatus, summary: Dict) -> None` | |
| | • `update_run_output(run_id: str, output: Dict) -> None` | |

**Implementation**: `core/memory/base.py`

### 3.2 Step Lifecycle Methods

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-API-002** | [V1] All implementations MUST implement: | MUST |
| | • `create_step(step: StepRecord) -> None` | |
| | • `update_step(run_id: str, step_id: str, updates: Dict) -> None` | |

**Implementation**: `core/memory/base.py`

### 3.3 Event Persistence Methods

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-API-003** | [V1] All implementations MUST implement: | MUST |
| | • `add_event(event: TraceEvent) -> None` | |
| | • `add_events(events: List[TraceEvent]) -> None` (MAY delegate to `add_event`) | |

**Implementation**: `core/memory/base.py`

### 3.4 Approval Lifecycle Methods

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-API-004** | [V1] All implementations MUST implement: | MUST |
| | • `create_approval(approval: ApprovalRecord) -> None` | |
| | • `update_approval(approval_id: str, updates: Dict) -> None` | |

**Implementation**: `core/memory/base.py`

### 3.5 Query Methods

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-API-005** | [V1] All implementations MUST implement: | MUST |
| | • `get_run(run_id: str) -> Optional[RunRecord]` | |
| | • `get_run_bundle(run_id: str) -> Optional[RunBundle]` | |
| | • `list_runs(product: str, limit: int, offset: int) -> List[RunRecord]` | |

**Implementation**: `core/memory/base.py`

### 3.6 Schema Management Methods

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-API-006** | [V1] Implementations MAY implement: | MAY |
| | • `init_schema() -> None` (no-op for in-memory) | |
| | • `get_schema_version() -> int` (return 0 for in-memory) | |

**Implementation**: `core/memory/base.py`

---

## 4. SQLite Backend Requirements

### 4.1 Schema Tables

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SQLITE-001** | [V1] SQLiteBackend MUST create `schema_version` table with: | MUST |
| | • `id` INTEGER PRIMARY KEY with CHECK (id = 1) | |
| | • `version` INTEGER NOT NULL | |

**Implementation**: `core/memory/sqlite_backend.py`

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SQLITE-002** | [V1] SQLiteBackend MUST create `runs` table with columns: | MUST |

| Column | Type | Constraint |
|--------|------|------------|
| run_id | TEXT | PRIMARY KEY |
| product | TEXT | NOT NULL |
| flow | TEXT | NOT NULL |
| status | TEXT | NOT NULL |
| autonomy | TEXT | NOT NULL |
| started_at | INTEGER | NOT NULL |
| finished_at | INTEGER | nullable |
| input_json | TEXT | nullable |
| output_json | TEXT | nullable |
| summary_json | TEXT | nullable |

Index: `idx_runs_product_status`

**Implementation**: `core/memory/sqlite_backend.py`

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SQLITE-003** | [V1] SQLiteBackend MUST create `steps` table with columns: | MUST |

| Column | Type | Constraint |
|--------|------|------------|
| run_id | TEXT | NOT NULL |
| step_id | TEXT | NOT NULL |
| step_index | INTEGER | NOT NULL |
| name | TEXT | NOT NULL |
| type | TEXT | NOT NULL |
| status | TEXT | NOT NULL |
| started_at | INTEGER | nullable |
| finished_at | INTEGER | nullable |
| input_json | TEXT | nullable |
| output_json | TEXT | nullable |
| error_json | TEXT | nullable |
| meta_json | TEXT | nullable |

PRIMARY KEY: `(run_id, step_id)`  
Index: `idx_steps_run_id`

**Implementation**: `core/memory/sqlite_backend.py`

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SQLITE-004** | [V1] SQLiteBackend MUST create `events` table with columns: | MUST |

| Column | Type | Constraint |
|--------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| run_id | TEXT | NOT NULL |
| step_id | TEXT | nullable |
| product | TEXT | NOT NULL |
| flow | TEXT | NOT NULL |
| kind | TEXT | NOT NULL |
| ts | INTEGER | NOT NULL |
| payload_json | TEXT | nullable |

Index: `idx_events_run_id`

**Implementation**: `core/memory/sqlite_backend.py`

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SQLITE-005** | [V1] SQLiteBackend MUST create `approvals` table with columns: | MUST |

| Column | Type | Constraint |
|--------|------|------------|
| approval_id | TEXT | PRIMARY KEY |
| run_id | TEXT | NOT NULL |
| step_id | TEXT | NOT NULL |
| product | TEXT | NOT NULL |
| flow | TEXT | NOT NULL |
| status | TEXT | NOT NULL |
| requested_by | TEXT | nullable |
| requested_at | INTEGER | NOT NULL |
| resolved_by | TEXT | nullable |
| resolved_at | INTEGER | nullable |
| decision | TEXT | nullable |
| comment | TEXT | nullable |
| payload_json | TEXT | nullable |

Index: `idx_approvals_run_id`

**Implementation**: `core/memory/sqlite_backend.py`

### 4.2 Connection Settings

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SQLITE-006** | [V1] SQLite connections MUST use: | MUST |
| | • `journal_mode=WAL` | |
| | • `synchronous=NORMAL` | |
| | • `foreign_keys=ON` | |
| | • `check_same_thread=False` | |
| | • `isolation_level=DEFERRED` | |
| | • `busy_timeout` matching the timeout in milliseconds | |

**Implementation**: `core/memory/sqlite_backend.py`

### 4.3 Data Handling

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-SQLITE-007** | [V1] JSON payloads MUST be clamped to `max_json_size` characters | MUST |
| **MEM-SQLITE-008** | [V1] Run and step creation MUST use `INSERT OR REPLACE` for idempotency | MUST |
| **MEM-SQLITE-009** | [V1] `finished_at` MUST be set on terminal status (`COMPLETED`, `FAILED`, `CANCELLED`) if not already set | MUST |

**Implementation**: `core/memory/sqlite_backend.py`

---

## 5. In-Memory Backend Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-INMEM-001** | [V1] InMemoryBackend MUST be thread-safe using `threading.RLock` | MUST |
| **MEM-INMEM-002** | [V1] InMemoryBackend MUST maintain separate indexes: | MUST |
| | • `_runs` (keyed by run_id) | |
| | • `_steps` (keyed by run_id, then step_id) | |
| | • `_events` (keyed by run_id) | |
| | • `_approvals` (keyed by approval_id) | |
| **MEM-INMEM-003** | [V1] `get_schema_version()` MUST return `0` | MUST |

**Implementation**: `core/memory/in_memory.py`

---

## 6. MemoryRouter Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-ROUTER-001** | [V1] MemoryRouter MUST delegate all standard `MemoryBackend` operations to the underlying backend | MUST |
| **MEM-ROUTER-002** | [V1] When `ObservabilityStore` is provided: | MUST |
| | • `add_event` MUST also call `obs_store.write_event` | |
| | • Router MUST expose observability methods: | |
| |   - `stage_input_files` | |
| |   - `stage_output_files` | |
| |   - `finalize_run_output` | |
| |   - `mirror_input_to_run` | |
| |   - `store_user_input` | |
| |   - `read_user_input` | |
| |   - `clear_staging` | |
| |   - `get_run_output_dir` | |
| |   - `get_run_input_dir` | |
| **MEM-ROUTER-003** | [V1] `from_settings` factory MUST: | MUST |
| | 1. Resolve `db_path` and `observability_dir` from settings | |
| | 2. If `db_path` or `use_sqlite` is set → use `SQLiteBackend` | |
| | 3. Otherwise → use `InMemoryBackend` | |
| | 4. Configure `ObservabilityStore` from `observability_dir` | |

**Implementation**: `core/memory/router.py`

---

## 7. ObservabilityStore Requirements

### 7.1 Directory Layout

| ID | Requirement | Level |
|----|-------------|-------|
| **OBS-DIR-001** | [V1] The observability directory MUST follow: | MUST |
```
observability/<product>/<run_id>/
├── input/
│   ├── input.json
│   ├── messages.json
│   ├── comments.json
│   └── attachments.json
├── runtime/
│   ├── events.jsonl
│   └── user_input/<form_id>.json
└── output/
    ├── response.json
    └── <output files>
```

**Implementation**: `core/memory/observability_store.py`

| ID | Requirement | Level |
|----|-------------|-------|
| **OBS-DIR-002** | [V1] Staging directory MUST be at `observability/staging` with: | MUST |
| | • `input/` for staged input files | |
| | • `output/` for staged output files | |

**Implementation**: `core/memory/observability_store.py`

### 7.2 Events File Format

| ID | Requirement | Level |
|----|-------------|-------|
| **OBS-EVENTS-001** | [V1] Events MUST be written as newline-delimited JSON (JSONL) to `runtime/events.jsonl`: | MUST |
| | • One JSON object per line | |
| | • Each line is the full `model_dump()` of a TraceEvent | |
| | • Lines MUST be appended (not overwritten) | |
| | • File MUST be flushed after each write | |

**Implementation**: `core/memory/observability_store.py`

### 7.3 Response File Format

| ID | Requirement | Level |
|----|-------------|-------|
| **OBS-RESPONSE-001** | [V1] The response file MUST: | MUST |
| | • Be written atomically via temp file + rename | |
| | • Include a `files` array listing all output files | |
| | • Each file entry MUST contain: `name`, `path`, `role`, `content_type`, `size`, `sha256` | |

**Implementation**: `core/memory/observability_store.py`

### 7.4 File Roles

| ID | Requirement | Level |
|----|-------------|-------|
| **OBS-ROLE-001** | [V1] File roles MUST be assigned: | MUST |
| | • `.pdf` files → `primary` | |
| | • `.html` files → `primary` | |
| | • Other files → `supplementary` | |

**Implementation**: `core/memory/observability_store.py`

### 7.5 Input Mirroring

| ID | Requirement | Level |
|----|-------------|-------|
| **OBS-INPUT-001** | [V1] When `mirror_inputs=True`: | MUST |
| | • `stage_input_files` MUST write `input.json`, `messages.json`, `comments.json` | |
| | • `stage_input_files` MUST copy/rename files to staging and record metadata | |
| | • `mirror_input_to_run` MUST copy staged files to run's input dir then clear staging | |

**Implementation**: `core/memory/observability_store.py`

### 7.6 File Handling

| ID | Requirement | Level |
|----|-------------|-------|
| **OBS-FILE-001** | [V1] All JSON writes MUST use atomic write pattern: | MUST |
| | 1. Write to `{path}.tmp` | |
| | 2. Rename to `{path}` | |
| **OBS-FILE-002** | [V1] Stored file names MUST be sanitized: | MUST |
| | • Strip path components (use basename only) | |
| | • Replace non-alphanumeric characters (except `._-`) with `_` | |
| | • Strip leading/trailing `.` and `_` | |
| | • Default to `unnamed_file` if empty after sanitization | |
| **OBS-FILE-003** | [V1] All persisted files MUST have SHA256 hash recorded in metadata | MUST |

**Implementation**: `core/memory/observability_store.py`

---

## 8. Tracer Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **OBS-TRACE-001** | [V1] Tracer MUST sanitize payloads before persistence via `SecurityRedactor` | MUST |
| **OBS-TRACE-002** | [V1] If sanitization modified the payload, `redacted` MUST be set to `True` | MUST |
| **OBS-TRACE-003** | [V1] Tracer MUST persist via MemoryBackend only; MUST NOT call SQLite or file I/O directly | MUST |
| **OBS-TRACE-004** | [V1] If `log_to_console=True`, Tracer MUST emit an info-level log with: | MUST |
| | • `run_id` | |
| | • `step_id` | |
| | • `kind` | |
| | • `ts` | |
| | • `payload` (truncated) | |
| **OBS-TRACE-005** | [V1] `from_settings` factory MUST configure: | MUST |
| | • `redactor` from `SecurityRedactor` | |
| | • `log_to_console` from `settings.tracing.log_to_console` | |

**Implementation**: `core/memory/tracing.py`

---

## 9. Run Lifecycle Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-LIFECYCLE-001** | [V1] When `create_run` is called, the run MUST have: | MUST |
| | • Valid `run_id` (non-empty string) | |
| | • Valid `product` and `flow` | |
| | • `status=RUNNING` | |
| | • `started_at` set to current epoch time | |
| **MEM-LIFECYCLE-002** | [V1] When status transitions to `COMPLETED`, `FAILED`, or `CANCELLED`, `finished_at` MUST be set if not already | MUST |
| **MEM-LIFECYCLE-003** | [V1] Steps MUST transition through: | MUST |
| | 1. `PENDING` → `STARTED` (set `started_at`) | |
| | 2. `STARTED` → `COMPLETED` (set `finished_at`) | |
| | 3. `STARTED` → `PAUSED` (awaiting external input) | |
| **MEM-LIFECYCLE-004** | [V1] When `update_approval` is called: | MUST |
| | • If decision starts with "APPROVE" → `status=APPROVED` | |
| | • Otherwise → `status=REJECTED` | |
| | • `resolved_at` MUST be set to current epoch time | |

**Implementation**: `core/memory/sqlite_backend.py`, `core/memory/in_memory.py`

---

## 10. Error Handling Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-ERR-001** | [V1] `MemoryBackendLoadError` MUST contain: | MUST |
| | • `code` (string, machine-readable) | |
| | • `message` (string, human-readable) | |
| | • `to_dict()` method returning `{"code": ..., "message": ...}` | |
| **MEM-ERR-002** | [V1] All orchestrator operations MUST return `RunOperationResult` with: | MUST |
| | • `ok` (boolean) | |
| | • `data` (optional dict on success) | |
| | • `error` (optional `MemoryBackendLoadError` on failure with `code`, `message`, `details`) | |

**Implementation**: `core/memory/base.py`

---

## 11. Configuration Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **MEM-CONFIG-001** | [V1] Settings MUST provide: | MUST |
| | • `memory.db_path` (default relative path) | |
| | • `memory.observability_dir` (default relative path) | |
| **MEM-CONFIG-002** | [V1] Settings MUST support feature flags: | MUST |
| | • `memory.use_sqlite` (boolean) | |
| | • `memory.mirror_inputs` (boolean) | |
| **MEM-CONFIG-003** | [V1] Settings MAY provide: | MAY |
| | • `memory.sqlite_path` (optional custom SQLite path) | |

**Implementation**: `core/config/schema.py`

---

## 12. Semantic Trace Events (Added: 2026-01-13)

> **Source**: BRD-OPS-SEM-001...010, INV-7

### 12.1 Required Semantic Events

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **MEM-SEM-001** | [V1] `semantic_phase_started` MUST be emitted when semantic interpretation begins | MUST | 1.1 |
| **MEM-SEM-002** | [V1] `semantic_envelope_created` MUST be emitted with full `SemanticEnvelope` in payload | MUST | 1.1 |
| **MEM-SEM-003** | [V1] `semantic_validation_completed` MUST be emitted with `ValidationResult` in payload | MUST | 1.1 |
| **MEM-SEM-004** | [V1] `semantic_confidence_checked` MUST be emitted with confidence value and threshold | MUST | 1.1 |
| **MEM-SEM-005** | [V1] `semantic_phase_completed` MUST be emitted with final `proposed_next_action` | MUST | 1.1 |
| **MEM-SEM-006** | [V1] `semantic_abort_triggered` MUST be emitted if next_action is ABORT | MUST | 1.1 |
| **MEM-SEM-007** | [V1] `semantic_ask_user_triggered` MUST be emitted if next_action is ASK_USER | MUST | 1.1 |
| **MEM-SEM-008** | [V1] All semantic events MUST include `envelope_hash` for correlation | MUST | 1.1 |
| **MEM-SEM-009** | [V1] Semantic events MUST NOT be redacted (confidences are not secrets) | MUST | 1.1 |
| **MEM-SEM-010** | [V1] Semantic events MUST include `product` and `flow` in payload | MUST | 1.1 |

**Implementation**: `core/memory/tracing.py`

### 12.2 Semantic Event Payload Schemas

**semantic_envelope_created**:
```python
{
    "envelope_hash": str,  # SHA256 of normalized_input
    "product": str,
    "flow": str,
    "intent_type": str,
    "confidence": float,
    "entity_count": int,
    "ambiguity_count": int,
    "proposed_next_action": str  # CONTINUE|ASK_USER|ABORT|NEEDS_APPROVAL
}
```

**semantic_validation_completed**:
```python
{
    "envelope_hash": str,
    "valid": bool,
    "revised_confidence": Optional[float],
    "correction_count": int,
    "clarification_requested": bool
}
```

**semantic_confidence_checked**:
```python
{
    "envelope_hash": str,
    "effective_confidence": float,
    "threshold": float,
    "passed": bool,
    "source": str  # "platform_default" | "product_override"
}
```

**Implementation**: `core/memory/tracing.py`

---

## 13. Reasoning Observability (Added: 2026-01-13)

> **Source**: BRD-OPS-REASON-001...007, INV-7

### 13.1 Reasoning Trace Events

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **MEM-REASON-001** | [V1] `reasoning_pass_started` MUST be emitted at start of each reasoning pass | MUST | 1.1 |
| **MEM-REASON-002** | [V1] `reasoning_pass_completed` MUST be emitted with pass result and exit reason | MUST | 1.1 |
| **MEM-REASON-003** | [V1] `critic_evaluation_started` MUST be emitted when critic is invoked | MUST | 1.1 |
| **MEM-REASON-004** | [V1] `critic_evaluation_completed` MUST be emitted with recommendation and rationale | MUST | 1.1 |
| **MEM-REASON-005** | [V1] `reasoning_ladder_step` MUST be emitted for each ladder rung with level and output | MUST | 1.1 |
| **MEM-REASON-006** | [V1] All reasoning events MUST include `pass_number` and `reasoning_budget` | MUST | 1.1 |
| **MEM-REASON-007** | [V1] Reasoning events MUST NOT include raw LLM prompts (use `prompt_hash` instead) | MUST | 1.1 |

**Implementation**: `core/memory/tracing.py`

### 13.2 Reasoning Event Payload Schemas

**reasoning_pass_started**:
```python
{
    "pass_number": int,
    "max_passes": int,
    "agent": str,
    "tool_budget_remaining": int
}
```

**reasoning_pass_completed**:
```python
{
    "pass_number": int,
    "exit_reason": str,  # DONE|NEED_MORE|ESCALATE
    "tools_used": int,
    "confidence_achieved": float
}
```

**critic_evaluation_completed**:
```python
{
    "recommendation": str,  # NONE|USER_INPUT|HITL|FETCH_MORE_EVIDENCE
    "rationale_hash": str,  # SHA256 of rationale text
    "strengths_count": int,
    "gaps_count": int,
    "confidence": float
}
```

**Implementation**: `core/memory/tracing.py`

### 13.3 Decision Artifact Trace Events

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **MEM-DEC-001** | [V1] `decision_artifact_created` MUST be emitted when DecisionArtifact is persisted | MUST | 1.1 |
| **MEM-DEC-002** | [V1] Event payload MUST include: `decision_id`, `options_count`, `confidence`, `justification_hash` | MUST | 1.1 |
| **MEM-DEC-003** | [V1] Event MUST NOT include full `options_considered` (use artifact storage for full data) | MUST | 1.1 |

**Implementation**: `core/memory/tracing.py`

---

## 14. Explicit Non-Goals (Added: 2026-01-13)

> **Memory/Observability MUST NOT**:

| Non-Goal | Rationale | Violation Example |
|----------|-----------|-------------------|
| Mutable trace events | Traces are immutable audit records | Event updated after creation |
| Hidden events | All significant events must be traced | Decision made without trace |
| Raw LLM content in events | Privacy and size concerns | Full prompt in payload |
| Cross-product queries without isolation | Product isolation must be enforced | Query returns other products' data |
| Synchronous event blocking | Events must not slow execution | Event persistence blocks run |
| Agent-controlled event filtering | Agents cannot hide their traces | Agent deletes own events |

---

## 15. Future Considerations

### 15.1 V1.1 Enhancements

| ID | Feature | Description |
|----|---------|-------------|
| **MEM-FUTURE-001** | Run archival | Archive old runs to cold storage |
| **MEM-FUTURE-002** | Event streaming | Real-time event push via WebSocket |
| **MEM-FUTURE-003** | Metrics aggregation | Roll up trace events into metrics |

### 15.2 V2 Features

| ID | Feature | Description |
|----|---------|-------------|
| **MEM-FUTURE-010** | PostgreSQL backend | Enterprise-grade persistence |
| **MEM-FUTURE-011** | Distributed tracing | OpenTelemetry integration |
| **MEM-FUTURE-012** | Multi-region | Cross-region data replication |

---

## 16. Traceability Matrix

| Requirement | Implementation | Test | BRD Source |
|-------------|----------------|------|------------|
| MEM-SCHEMA-001 | `core/contracts/run_schema.py` | `tests/unit/core/contracts/test_run_schema.py` | BRD-OPS-010 |
| MEM-API-001 | `core/memory/base.py` | `tests/unit/core/memory/test_base.py` | BRD-OPS-020 |
| MEM-SQLITE-002 | `core/memory/sqlite_backend.py` | `tests/unit/core/memory/test_sqlite_backend.py` | BRD-OPS-030 |
| MEM-INMEM-001 | `core/memory/in_memory.py` | `tests/unit/core/memory/test_in_memory.py` | BRD-OPS-030 |
| OBS-DIR-001 | `core/memory/observability_store.py` | `tests/unit/core/memory/test_observability_store.py` | BRD-OPS-040 |
| OBS-TRACE-001 | `core/memory/tracing.py` | `tests/unit/core/memory/test_tracing.py` | BRD-OPS-040 |
| MEM-SEM-001...010 | `core/memory/tracing.py` | `tests/unit/core/memory/test_semantic_events.py` | BRD-OPS-SEM-001...010 |
| MEM-REASON-001...007 | `core/memory/tracing.py` | `tests/unit/core/memory/test_reasoning_events.py` | BRD-OPS-REASON-001...007 |
| MEM-DEC-001...003 | `core/memory/tracing.py` | `tests/unit/core/memory/test_decision_events.py` | BRD-GOV-045...047 |

---

## 17. BRD Requirement Mapping (Added: 2026-01-13)

| BRD Requirement | Techspec Requirement(s) | Status |
|-----------------|-------------------------|--------|
| BRD-OPS-SEM-001 | MEM-SEM-001 | Mapped |
| BRD-OPS-SEM-002 | MEM-SEM-002 | Mapped |
| BRD-OPS-SEM-003 | MEM-SEM-003 | Mapped |
| BRD-OPS-SEM-004 | MEM-SEM-004 | Mapped |
| BRD-OPS-SEM-005 | MEM-SEM-005 | Mapped |
| BRD-OPS-SEM-006 | MEM-SEM-006, MEM-SEM-007 | Mapped |
| BRD-OPS-SEM-007 | MEM-SEM-008 | Mapped |
| BRD-OPS-SEM-008 | MEM-SEM-009 | Mapped |
| BRD-OPS-SEM-009 | MEM-SEM-010 | Mapped |
| BRD-OPS-SEM-010 | MEM-SEM-002 (entity_count) | Mapped |
| BRD-OPS-REASON-001 | MEM-REASON-001 | Mapped |
| BRD-OPS-REASON-002 | MEM-REASON-002 | Mapped |
| BRD-OPS-REASON-003 | MEM-REASON-003, MEM-REASON-004 | Mapped |
| BRD-OPS-REASON-004 | MEM-REASON-005 | Mapped |
| BRD-OPS-REASON-005 | MEM-REASON-006 | Mapped |
| BRD-OPS-REASON-006 | MEM-REASON-007 | Mapped |
| BRD-OPS-REASON-007 | MEM-DEC-001...003 | Mapped |
| BRD-OPS-010...049 | MEM-SCHEMA-001...MEM-CONFIG-003 | Existing |