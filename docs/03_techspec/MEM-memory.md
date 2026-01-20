# Memory and Observability Technical Specification

> **Document ID**: MEM / OBS  
> **Version**: V1.3  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-20  

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial V1 specification |
| 1.1.0 | 2026-01-13 | Added: §12 Semantic Trace Events, §13 Reasoning Observability, §14 Explicit Non-Goals, §17 BRD Requirement Mapping |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |
| V1.3 | 2026-01-20 | Added §13A Explainability (BRD-OPS-060), §13B Reproducibility (BRD-OPS-061) |

---

## 1. Overview

The memory layer provides persistence and retrieval of run records, step records, trace events, 
and approval records. The observability layer writes structured artifacts to disk for debugging, 
auditing, and analysis.

## 2. Data Contract Requirements

### 2.1 RunRecord Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SCHEMA-001 | `RunRecord` MUST contain required fields: | MUST | BRD-AUTO-SEM-005, BRD-OPS-042 | 1.1 | 13 Jan 2026 | • `run_id` (string, auto-generated UUID); • `product` (string, required); • `flow` (string, required, aliased as `flow_id`); • `status` (RunStatus enum, default `RUNNING`); • `autonomy` (optional string); • `started_at` (integer, epoch seconds, auto-generated); • `finished_at` (optional integer, epoch seconds); • `input` (optional dict); • `output` (optional dict); • `summary` (dict, default empty) |


### 2.2 RunStatus Enum

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SCHEMA-002 | `RunStatus` MUST be one of: `RUNNING`, `PAUSED_WAITING_FOR_USER`, `PENDING_HUMAN`, `COMPLETED`, `FAILED`, `CANCELLED`, `ERROR` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 2.3 StepRecord Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SCHEMA-003 | `StepRecord` MUST contain required fields: | MUST | BRD-OPS-042 | 1.1 | 13 Jan 2026 | • `run_id` (string, required); • `step_id` (string, required); • `step_index` (integer, default 0, zero-based); • `name` (string, default empty); • `type` (string, default `tool`, one of `tool`, `agent`, `human_approval`, `subflow`); • `status` (StepStatus enum, default `PENDING`); • `started_at` (optional integer, epoch seconds); • `finished_at` (optional integer, epoch seconds); • `input` (optional dict); • `output` (optional dict); • `error` (optional dict, sanitized); • `meta` (dict, default empty) |


### 2.4 StepStatus Enum

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SCHEMA-004 | `StepStatus` MUST be one of: `PENDING`, `STARTED`, `RUNNING`, `COMPLETED`, `FAILED`, `SKIPPED`, `PAUSED`, `CANCELLED` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 2.5 TraceEvent Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SCHEMA-005 | `TraceEvent` MUST contain required fields: | MUST | BRD-GOV-040, BRD-OPS-011 | 1.1 | 13 Jan 2026 | • `event_id` (string, auto-generated UUID); • `run_id` (string, required); • `step_id` (optional string); • `product` (string, required); • `flow` (string, required); • `kind` (string, default `INFO`, aliased as `event_type`); • `ts` (integer, epoch seconds, auto-generated); • `payload` (dict, default empty, sanitized); • `redacted` (boolean, default false) |


### 2.6 ApprovalRecord Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SCHEMA-006 | `ApprovalRecord` MUST contain required fields: | MUST | BRD-GOV-004 | 1.1 | 13 Jan 2026 | • `approval_id` (string, required); • `run_id` (string, required); • `step_id` (string, required); • `product` (string, required); • `flow` (string, required); • `status` (string, default `PENDING`, one of `PENDING`, `APPROVED`, `REJECTED`); • `requested_by` (optional string); • `requested_at` (integer, required); • `resolved_by` (optional string); • `resolved_at` (optional integer); • `decision` (optional string); • `comment` (optional string); • `context` (dict, default empty, scrubbed for UI display) |


### 2.7 RunBundle Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SCHEMA-007 | `RunBundle` MUST aggregate: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `run` (RunRecord, required); • `steps` (list of StepRecord, default empty); • `events` (list of TraceEvent, default empty); • `approvals` (list of ApprovalRecord, default empty) |


---

## 3. MemoryBackend Interface Requirements

### 3.1 Run Lifecycle Methods

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-API-001 | All `MemoryBackend` implementations MUST implement: | MUST | BRD-AUTO-046, BRD-GOV-041 | 1.1 | 13 Jan 2026 | • `create_run(run: RunRecord) -> None`; • `update_run_status(run_id: str, status: RunStatus, summary: Dict) -> None`; • `update_run_output(run_id: str, output: Dict) -> None` |


### 3.2 Step Lifecycle Methods

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-API-002 | All implementations MUST implement: | MUST | BRD-AUTO-046, BRD-GOV-041 | 1.1 | 13 Jan 2026 | • `create_step(step: StepRecord) -> None`; • `update_step(run_id: str, step_id: str, updates: Dict) -> None` |


### 3.3 Event Persistence Methods

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-API-003 | All implementations MUST implement: | MUST | BRD-AUTO-046 | 1.1 | 13 Jan 2026 | • `add_event(event: TraceEvent) -> None`; • `add_events(events: List[TraceEvent]) -> None` (MAY delegate to `add_event`) |


### 3.4 Approval Lifecycle Methods

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-API-004 | All implementations MUST implement: | MUST | BRD-AUTO-046 | 1.1 | 13 Jan 2026 | • `create_approval(approval: ApprovalRecord) -> None`; • `update_approval(approval_id: str, updates: Dict) -> None` |


### 3.5 Query Methods

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-API-005 | All implementations MUST implement: | MUST | BRD-AUTO-046, BRD-GOV-042, BRD-OPS-005 | 1.1 | 13 Jan 2026 | • `get_run(run_id: str) -> Optional[RunRecord]`; • `get_run_bundle(run_id: str) -> Optional[RunBundle]`; • `list_runs(product: str, limit: int, offset: int) -> List[RunRecord]` |


### 3.6 Schema Management Methods

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-API-006 | Implementations MAY implement: | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `init_schema() -> None` (no-op for in-memory); • `get_schema_version() -> int` (return 0 for in-memory) |


---

## 4. SQLite Backend Requirements

### 4.1 Schema Tables

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SQLITE-001 | SQLiteBackend MUST create `schema_version` table with: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `id` INTEGER PRIMARY KEY with CHECK (id = 1); • `version` INTEGER NOT NULL |


| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SQLITE-002 | SQLiteBackend MUST create `runs` table with columns: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `run_id` TEXT PRIMARY KEY; • `product` TEXT NOT NULL; • `flow` TEXT NOT NULL; • `status` TEXT NOT NULL; • `autonomy` TEXT NOT NULL; • `started_at` INTEGER NOT NULL; • `finished_at` INTEGER nullable; • `input_json` TEXT nullable; • `output_json` TEXT nullable; • `summary_json` TEXT nullable; • Index `idx_runs_product_status` |


| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SQLITE-003 | SQLiteBackend MUST create `steps` table with columns: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `run_id` TEXT NOT NULL; • `step_id` TEXT NOT NULL; • `step_index` INTEGER NOT NULL; • `name` TEXT NOT NULL; • `type` TEXT NOT NULL; • `status` TEXT NOT NULL; • `started_at` INTEGER nullable; • `finished_at` INTEGER nullable; • `input_json` TEXT nullable; • `output_json` TEXT nullable; • `error_json` TEXT nullable; • `meta_json` TEXT nullable; • PRIMARY KEY (`run_id`, `step_id`); • Index `idx_steps_run_id` |


| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SQLITE-004 | SQLiteBackend MUST create `events` table with columns: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `id` INTEGER PRIMARY KEY AUTOINCREMENT; • `run_id` TEXT NOT NULL; • `step_id` TEXT nullable; • `product` TEXT NOT NULL; • `flow` TEXT NOT NULL; • `kind` TEXT NOT NULL; • `ts` INTEGER NOT NULL; • `payload_json` TEXT nullable; • Index `idx_events_run_id` |


| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SQLITE-005 | SQLiteBackend MUST create `approvals` table with columns: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `approval_id` TEXT PRIMARY KEY; • `run_id` TEXT NOT NULL; • `step_id` TEXT NOT NULL; • `product` TEXT NOT NULL; • `flow` TEXT NOT NULL; • `status` TEXT NOT NULL; • `requested_by` TEXT nullable; • `requested_at` INTEGER NOT NULL; • `resolved_by` TEXT nullable; • `resolved_at` INTEGER nullable; • `decision` TEXT nullable; • `comment` TEXT nullable; • `payload_json` TEXT nullable; • Index `idx_approvals_run_id` |


### 4.2 Connection Settings

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SQLITE-006 | SQLite connections MUST use: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `journal_mode=WAL`; • `synchronous=NORMAL`; • `foreign_keys=ON`; • `check_same_thread=False`; • `isolation_level=DEFERRED`; • `busy_timeout` matching the timeout in milliseconds |


### 4.3 Data Handling

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SQLITE-007 | JSON payloads MUST be clamped to `max_json_size` characters | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SQLITE-008 | Run and step creation MUST use `INSERT OR REPLACE` for idempotency | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SQLITE-009 | `finished_at` MUST be set on terminal status (`COMPLETED`, `FAILED`, `CANCELLED`) if not already set | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 5. In-Memory Backend Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-INMEM-001 | InMemoryBackend MUST be thread-safe using `threading.RLock` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-INMEM-002 | InMemoryBackend MUST maintain separate indexes: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `_runs` (keyed by run_id); • `_steps` (keyed by run_id, then step_id); • `_events` (keyed by run_id); • `_approvals` (keyed by approval_id) |
| MEM-INMEM-003 | `get_schema_version()` MUST return `0` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 6. MemoryRouter Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-ROUTER-001 | MemoryRouter MUST delegate all standard `MemoryBackend` operations to the underlying backend | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-ROUTER-002 | When `ObservabilityStore` is provided: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `add_event` MUST also call `obs_store.write_event`; • Router MUST expose observability methods:; - `stage_input_files`; - `stage_output_files`; - `finalize_run_output`; - `mirror_input_to_run`; - `store_user_input`; - `read_user_input`; - `clear_staging`; - `get_run_output_dir`; - `get_run_input_dir` |
| MEM-ROUTER-003 | `from_settings` factory MUST: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | 1. Resolve `db_path` and `observability_dir` from settings; 2. If `db_path` or `use_sqlite` is set → use `SQLiteBackend`; 3. Otherwise → use `InMemoryBackend`; 4. Configure `ObservabilityStore` from `observability_dir` |


---

## 7. ObservabilityStore Requirements

### 7.1 Directory Layout

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| OBS-DIR-001 | The observability directory MUST follow: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| OBS-DIR-002 | Staging directory MUST be at `observability/staging` with: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `input/` for staged input files; • `output/` for staged output files |


### 7.2 Events File Format

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| OBS-EVENTS-001 | Events MUST be written as newline-delimited JSON (JSONL) to `runtime/events.jsonl`: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • One JSON object per line; • Each line is the full `model_dump()` of a TraceEvent; • Lines MUST be appended (not overwritten); • File MUST be flushed after each write |


### 7.3 Response File Format

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| OBS-RESPONSE-001 | The response file MUST: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • Be written atomically via temp file + rename; • Include a `files` array listing all output files; • Each file entry MUST contain: `name`, `path`, `role`, `content_type`, `size`, `sha256` |


### 7.4 File Roles

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| OBS-ROLE-001 | File roles MUST be assigned: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `.pdf` files → `primary`; • `.html` files → `primary`; • Other files → `supplementary` |


### 7.5 Input Mirroring

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| OBS-INPUT-001 | When `mirror_inputs=True`: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `stage_input_files` MUST write `input.json`, `messages.json`, `comments.json`; • `stage_input_files` MUST copy/rename files to staging and record metadata; • `mirror_input_to_run` MUST copy staged files to run's input dir then clear staging |


### 7.6 File Handling

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| OBS-FILE-001 | All JSON writes MUST use atomic write pattern: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | 1. Write to `{path}.tmp`; 2. Rename to `{path}` |
| OBS-FILE-002 | Stored file names MUST be sanitized: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • Strip path components (use basename only); • Replace non-alphanumeric characters (except `._-`) with `_`; • Strip leading/trailing `.` and `_`; • Default to `unnamed_file` if empty after sanitization |
| OBS-FILE-003 | All persisted files MUST have SHA256 hash recorded in metadata | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 8. Tracer Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| OBS-TRACE-001 | Tracer MUST sanitize payloads before persistence via `SecurityRedactor` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| OBS-TRACE-002 | If sanitization modified the payload, `redacted` MUST be set to `True` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| OBS-TRACE-003 | Tracer MUST persist via MemoryBackend only; MUST NOT call SQLite or file I/O directly | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| OBS-TRACE-004 | If `log_to_console=True`, Tracer MUST emit an info-level log with: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `run_id`; • `step_id`; • `kind`; • `ts`; • `payload` (truncated) |
| OBS-TRACE-005 | `from_settings` factory MUST configure: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `redactor` from `SecurityRedactor`; • `log_to_console` from `settings.tracing.log_to_console` |


---

## 9. Run Lifecycle Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-LIFECYCLE-001 | When `create_run` is called, the run MUST have: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • Valid `run_id` (non-empty string); • Valid `product` and `flow`; • `status=RUNNING`; • `started_at` set to current epoch time |
| MEM-LIFECYCLE-002 | When status transitions to `COMPLETED`, `FAILED`, or `CANCELLED`, `finished_at` MUST be set if not already | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-LIFECYCLE-003 | Steps MUST transition through: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | 1. `PENDING` → `STARTED` (set `started_at`); 2. `STARTED` → `COMPLETED` (set `finished_at`); 3. `STARTED` → `PAUSED` (awaiting external input) |
| MEM-LIFECYCLE-004 | When `update_approval` is called: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • If decision starts with "APPROVE" → `status=APPROVED`; • Otherwise → `status=REJECTED`; • `resolved_at` MUST be set to current epoch time |


---

## 10. Error Handling Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-ERR-001 | `MemoryBackendLoadError` MUST contain: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `code` (string, machine-readable); • `message` (string, human-readable); • `to_dict()` method returning `{"code": ..., "message": ...}` |
| MEM-ERR-002 | All orchestrator operations MUST return `RunOperationResult` with: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `ok` (boolean); • `data` (optional dict on success); • `error` (optional `MemoryBackendLoadError` on failure with `code`, `message`, `details`) |


---

## 11. Configuration Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-CONFIG-001 | Settings MUST provide: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `memory.db_path` (default relative path); • `memory.observability_dir` (default relative path) |
| MEM-CONFIG-002 | Settings MUST support feature flags: | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `memory.use_sqlite` (boolean); • `memory.mirror_inputs` (boolean) |
| MEM-CONFIG-003 | Settings MAY provide: | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | • `memory.sqlite_path` (optional custom SQLite path) |


---

## 12. Semantic Trace Events (Added: 2026-01-13)

> **Source**: BRD-OPS-SEM-001...010, INV-7

### 12.1 Required Semantic Events

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-SEM-001 | `semantic_phase_started` MUST be emitted when semantic interpretation begins | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SEM-002 | `semantic_envelope_created` MUST be emitted with full `SemanticEnvelope` in payload | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SEM-003 | `semantic_validation_completed` MUST be emitted with `ValidationResult` in payload | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SEM-004 | `semantic_confidence_checked` MUST be emitted with confidence value and threshold | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SEM-005 | `semantic_phase_completed` MUST be emitted with final `proposed_next_action` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SEM-006 | `semantic_abort_triggered` MUST be emitted if next_action is ABORT | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SEM-007 | `semantic_ask_user_triggered` MUST be emitted if next_action is ASK_USER | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SEM-008 | All semantic events MUST include `envelope_hash` for correlation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SEM-009 | Semantic events MUST NOT be redacted (confidences are not secrets) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-SEM-010 | Semantic events MUST include `product` and `flow` in payload | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 12.2 Semantic Event Payload Schemas

**semantic_envelope_created**:

**semantic_validation_completed**:

**semantic_confidence_checked**:


---

## 13. Reasoning Observability (Added: 2026-01-13)

> **Source**: BRD-OPS-REASON-001...007, INV-7

### 13.1 Reasoning Trace Events

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-REASON-001 | `reasoning_pass_started` MUST be emitted at start of each reasoning pass | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-REASON-002 | `reasoning_pass_completed` MUST be emitted with pass result and exit reason | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-REASON-003 | `critic_evaluation_started` MUST be emitted when critic is invoked | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-REASON-004 | `critic_evaluation_completed` MUST be emitted with recommendation and rationale | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-REASON-005 | `reasoning_ladder_step` MUST be emitted for each ladder rung with level and output | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-REASON-006 | All reasoning events MUST include `pass_number` and `reasoning_budget` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-REASON-007 | Reasoning events MUST NOT include raw LLM prompts (use `prompt_hash` instead) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 13.2 Reasoning Event Payload Schemas

**reasoning_pass_started**:

**reasoning_pass_completed**:

**critic_evaluation_completed**:


### 13.3 Decision Artifact Trace Events

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-DEC-001 | `decision_artifact_created` MUST be emitted when DecisionArtifact is persisted | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-DEC-002 | Event payload MUST include: `decision_id`, `options_count`, `confidence`, `justification_hash` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| MEM-DEC-003 | Event MUST NOT include full `options_considered` (use artifact storage for full data) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 13A. Explainability Requirements (Added: 2026-01-20)

> **Source**: BRD-OPS-060 - Post-hoc explainability

### 13A.1 Explainability Support

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-EXPLAIN-001 | All reasoning traces MUST be persisted with sufficient detail for post-hoc explanation | MUST | BRD-OPS-060 | 1.3 | 20 Jan 2026 | — |
| MEM-EXPLAIN-002 | Each decision point MUST be traceable through `decision_id` → `evidence_refs` → source tools | MUST | BRD-OPS-060 | 1.3 | 20 Jan 2026 | — |
| MEM-EXPLAIN-003 | Reasoning chains MUST be reconstructable from trace events for any completed run | MUST | BRD-OPS-060 | 1.3 | 20 Jan 2026 | — |
| MEM-EXPLAIN-004 | `explain_run(run_id)` API MUST return structured explanation artifact | MUST | BRD-OPS-060 | 1.3 | 20 Jan 2026 | — |
| MEM-EXPLAIN-005 | Explanation artifact MUST include: `reasoning_chain`, `evidence_used`, `decisions_made`, `confidence_evolution` | MUST | BRD-OPS-060 | 1.3 | 20 Jan 2026 | — |


### 13A.2 Explanation Artifact Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-EXPLAIN-ART-001 | `ExplanationArtifact` MUST include `run_id`, `created_at`, `reasoning_steps` (list) | MUST | BRD-OPS-060 | 1.3 | 20 Jan 2026 | — |
| MEM-EXPLAIN-ART-002 | Each `reasoning_step` MUST include: `step_id`, `phase`, `input_summary`, `output_summary`, `confidence`, `evidence_refs` | MUST | BRD-OPS-060 | 1.3 | 20 Jan 2026 | — |
| MEM-EXPLAIN-ART-003 | Explanation MUST include `terminal_outcome` with `outcome_reason` and `outcome_explanation` | MUST | BRD-OPS-060 | 1.3 | 20 Jan 2026 | — |


---

## 13B. Reproducibility Requirements (Added: 2026-01-20)

> **Source**: BRD-OPS-061 - Reproducibility (versions, inputs, hashes)

### 13B.1 Version Recording

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-REPRO-001 | `RunRecord` MUST include `versions` object with platform and dependency versions | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |
| MEM-REPRO-002 | `versions` MUST include: `platform_version`, `flow_version`, `python_version` | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |
| MEM-REPRO-003 | `versions` MUST include model versions used: `models` dict mapping model name to version/checkpoint | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |


### 13B.2 Input Hashing

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-REPRO-010 | All inputs MUST be hashed using SHA-256 and stored as `input_hash` | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |
| MEM-REPRO-011 | `input_hash` MUST be computed from canonical JSON (sorted keys, minimal separators) | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |
| MEM-REPRO-012 | ContextPack MUST include `content_hash` computed before freeze | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |


### 13B.3 Output Hashing

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-REPRO-020 | All outputs MUST be hashed using SHA-256 and stored as `output_hash` | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |
| MEM-REPRO-021 | `output_hash` MUST be recorded in terminal `run_completed` or `run_failed` event | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |


### 13B.4 Reproducibility Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| MEM-REPRO-030 | `validate_reproducibility(run_id)` API MUST compare stored hashes with recomputed values | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |
| MEM-REPRO-031 | Validation MUST return `is_reproducible` boolean and `discrepancies` list | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |
| MEM-REPRO-032 | Discrepancies MUST include: `field`, `expected_hash`, `actual_hash` | MUST | BRD-OPS-061 | 1.3 | 20 Jan 2026 | — |


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
