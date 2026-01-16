# Gateway Technical Specification

> **Document ID**: GW  
> **Version**: 1.1.0  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-13

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial V1 specification |
| 1.1.0 | 2026-01-13 | Added: §6.1 Semantic Error Codes, §6.2 Semantic Exit Handling, §8 Explicit Non-Goals, §11 BRD Requirement Mapping |

---

## 1. Overview

The gateway layer provides external access to the platform through HTTP API, CLI, and 
Streamlit UI. All three interfaces share the same orchestration engine and follow 
consistent patterns for session isolation and error handling.

### 1.1 Implementation References

| Component | File |
|-----------|------|
| HTTP App | `gateway/api/http_app.py` |
| API Routes | `gateway/api/routes_run.py` |
| Dependencies | `gateway/api/deps.py` |
| CLI | `gateway/cli/main.py` |
| UI Entry | `gateway/ui/platform_app.py` |
| API Client | `gateway/ui/api_client.py` |
| UI Pages | `gateway/ui/pages/*.py` |

---

## 2. HTTP API Requirements

### 2.1 Server Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-API-001** | [V1] The system MUST expose a FastAPI application via a factory function `create_app()` | MUST |
| **GW-API-002** | [V1] The application MUST include a health check endpoint at `GET /health` | MUST |
| **GW-API-003** | [V1] The health endpoint MUST return `{"status": "ok"}` when the service is operational | MUST |
| **GW-API-004** | [V1] All API routes MUST be mounted under the `/api` prefix | MUST |
| **GW-API-005** | [V1] An ASGI entrypoint named `app` MUST be available at module level for uvicorn | MUST |

**Implementation**: `gateway/api/http_app.py`

### 2.2 Product Endpoints

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-API-010** | [V1] `GET /api/products` MUST list all discovered products | MUST |
| **GW-API-011** | [V1] `GET /api/products/{product}/flows` MUST list flows for a specific product | MUST |
| **GW-API-012** | [V1] Products endpoint response MUST include: `name`, `display_name`, `description`, `version`, `enabled`, `default_flow`, `ui_enabled`, `flows`, `error`, `error_path`, `error_message`, `ui` | MUST |
| **GW-API-013** | [V1] Products endpoint MUST return `error=true` for products that failed to load | MUST |
| **GW-API-014** | [V1] Flows endpoint MUST return 404 with code `product_not_found` for unknown products | MUST |
| **GW-API-015** | [V1] Flows endpoint MUST return 404 with code `product_disabled` for disabled products | MUST |
| **GW-API-016** | [V1] Flows endpoint MUST return 503 with code `product_unavailable` for products with load errors | MUST |

**Implementation**: `gateway/api/routes_run.py`

### 2.3 Run Endpoints

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-API-020** | [V1] `POST /api/products/{product}/flows/{flow}/run` MUST start a new flow execution | MUST |
| **GW-API-021** | [V1] `GET /api/runs/{run_id}` MUST return run status and details | MUST |
| **GW-API-022** | [V1] `GET /api/runs` MUST list all runs with pagination (`limit`, `offset` parameters) | MUST |
| **GW-API-023** | [V1] Run request payload MUST accept `payload` (Dict) and optional `requested_by` (String) fields | MUST |
| **GW-API-024** | [V1] Run payload size MUST be limited to 100KB (100 * 1024 bytes) | MUST |
| **GW-API-025** | [V1] Requests exceeding payload size limit MUST return 413 with code `payload_too_large` | MUST |
| **GW-API-026** | [V1] Unknown flows MUST return 404 with code `flow_not_found` including `available_flows` in details | MUST |
| **GW-API-027** | [V1] When `intent` is provided without `payload`, the system MUST map it to an intent field based on product UI configuration | MUST |

**Implementation**: `gateway/api/routes_run.py`

### 2.4 User Input Endpoints

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-API-030** | [V1] `GET /api/runs/{run_id}/pending_input` MUST return pending user input prompt | MUST |
| **GW-API-031** | [V1] `POST /api/runs/{run_id}/user_input` MUST submit user input response | MUST |
| **GW-API-032** | [V1] User input submission MUST accept: `run_id` (required), `form_id`, `answers`, `text`, `values`, `metadata` | MUST |
| **GW-API-033** | [V1] When `answers` is provided, system MUST construct form-based response with `form_id`, `schema`, `answers`, `submitted_at` | MUST |
| **GW-API-034** | [V1] When `answers` is not provided, system MUST use `FreeTextResponse` schema with `text`, `intent`, `attachments`, `metadata` | MUST |

**Implementation**: `gateway/api/routes_run.py`

### 2.5 Approval Endpoints

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-API-040** | [V1] `GET /api/approvals` MUST list pending approvals with pagination (`limit`, `offset`) | MUST |
| **GW-API-041** | [V1] `POST /api/runs/{run_id}/resume` MUST resume a paused run with approval decision | MUST |
| **GW-API-042** | [V1] Resume request MUST accept: `approved`, `decision`, `comment`, `resolved_by`, `replan` | MUST |
| **GW-API-043** | [V1] Decision field MUST default to `"APPROVED"` | MUST |

**Implementation**: `gateway/api/routes_run.py`

### 2.6 Output Endpoints

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-API-050** | [V1] `GET /api/runs/{run_id}/output/{file_path}` MUST serve output files as FileResponse | MUST |
| **GW-API-051** | [V1] Output file paths MUST be validated to prevent path traversal attacks | MUST |
| **GW-API-052** | [V1] Invalid output paths MUST return 400 with code `invalid_path` | MUST |
| **GW-API-053** | [V1] Missing output files MUST return 404 with code `not_found` | MUST |

**Implementation**: `gateway/api/routes_run.py`

### 2.7 Request/Response Schema

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-API-060** | [V1] All successful responses MUST follow envelope: `{"ok": true, "data": {...}, "meta": {...}}` | MUST |
| **GW-API-061** | [V1] All error responses MUST follow envelope: `{"ok": false, "error": {"code": "...", "message": "...", "details": {...}}}` | MUST |
| **GW-API-062** | [V1] Error codes MUST be lowercase snake_case strings | MUST |
| **GW-API-063** | [V1] Meta field MAY include contextual information like `run_id`, `product`, `flow`, `timestamp` | MAY |

**Implementation**: `gateway/api/routes_run.py`

### 2.8 Dependency Injection

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-API-070** | [V1] Settings MUST be loaded once and cached via `get_settings` | MUST |
| **GW-API-071** | [V1] Product catalog MUST be loaded once and cached via `get_product_catalog` | MUST |
| **GW-API-072** | [V1] Memory router MUST be a singleton via `get_memory_router` | MUST |
| **GW-API-073** | [V1] Tracer MUST be a singleton via `get_tracer` | MUST |
| **GW-API-074** | [V1] OrchestratorEngine MUST be instantiated per-request to ensure session isolation | MUST |
| **GW-API-075** | [V1] Engine MUST NOT be cached to avoid cross-session state leakage | MUST |

**Implementation**: `gateway/api/deps.py`

---

## 3. CLI Requirements

### 3.1 Command Structure

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-CLI-001** | [V1] CLI MUST be invocable as `master <command>` | MUST |
| **GW-CLI-002** | [V1] CLI MUST require a subcommand (no default action) | MUST |

**Implementation**: `gateway/cli/main.py`

### 3.2 Commands

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-CLI-010** | [V1] `products` command MUST list all discovered products with metadata | MUST |
| **GW-CLI-011** | [V1] `flows <product>` command MUST list flows for specified product | MUST |
| **GW-CLI-012** | [V1] `run <product> <flow>` command MUST execute a flow | MUST |
| **GW-CLI-013** | [V1] Run command MUST accept `--payload <json>` OR `--payload-file <path>` (mutually exclusive) | MUST |
| **GW-CLI-014** | [V1] Run command MAY accept `--requested-by <identifier>` | MAY |
| **GW-CLI-015** | [V1] `status <run_id>` command MUST return run status | MUST |
| **GW-CLI-016** | [V1] `get <run_id>` command MUST be an alias for status | MUST |
| **GW-CLI-017** | [V1] `approvals` command MUST list pending approvals | MUST |
| **GW-CLI-018** | [V1] `resume --run-id <id>` command MUST resume a paused run | MUST |
| **GW-CLI-019** | [V1] Resume command MUST accept mutually exclusive `--approve` or `--reject` flags | MUST |
| **GW-CLI-020** | [V1] Resume command MAY accept `--comment`, `--resolved-by`, `--decision`, `--replan` | MAY |

**Implementation**: `gateway/cli/main.py`

### 3.3 Output Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-CLI-030** | [V1] All CLI output MUST be valid JSON | MUST |
| **GW-CLI-031** | [V1] JSON output MUST be formatted with 2-space indentation | MUST |
| **GW-CLI-032** | [V1] Successful commands MUST return exit code 0 | MUST |
| **GW-CLI-033** | [V1] Failed commands MUST return exit code 1 | MUST |

**Implementation**: `gateway/cli/main.py`

### 3.4 Error Handling

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-CLI-040** | [V1] Invalid JSON payload MUST exit with message "Invalid JSON payload: ..." | MUST |
| **GW-CLI-041** | [V1] Non-object JSON payload MUST exit with message "JSON payload must be an object." | MUST |
| **GW-CLI-042** | [V1] Unknown product MUST exit with guidance to run `master products` | MUST |
| **GW-CLI-043** | [V1] Disabled product MUST exit with guidance to update `configs/products.yaml` | MUST |
| **GW-CLI-044** | [V1] Product load errors MUST exit with error path and message | MUST |
| **GW-CLI-045** | [V1] Unknown flow MUST exit listing available flows | MUST |

**Implementation**: `gateway/cli/main.py`

---

## 4. UI Requirements

### 4.1 Application Structure

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-001** | [V1] UI MUST be implemented using Streamlit framework | MUST |
| **GW-UI-002** | [V1] UI MUST use wide layout mode | MUST |
| **GW-UI-003** | [V1] Page title MUST be "master platform" | MUST |
| **GW-UI-004** | [V1] UI MUST load settings from repository root | MUST |
| **GW-UI-005** | [V1] UI MUST communicate with API via HTTP client (no direct core imports) | MUST |

**Implementation**: `gateway/ui/platform_app.py`

### 4.2 Navigation

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-010** | [V1] Sidebar MUST display navigation header "Navigation" | MUST |
| **GW-UI-011** | [V1] Sidebar MUST provide radio selection for pages: "Home", "Execution", "History" | MUST |
| **GW-UI-012** | [V1] Sidebar MUST display current API base URL | MUST |

**Implementation**: `gateway/ui/platform_app.py`

### 4.3 Session State

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-020** | [V1] Session state MUST maintain `run_history` list | MUST |
| **GW-UI-021** | [V1] Session state MUST track `last_run_id`, `last_run_status`, `last_run_product`, `last_run_flow` | MUST |
| **GW-UI-022** | [V1] Run IDs MUST be appended to history when runs are started | MUST |
| **GW-UI-023** | [V1] Duplicate run IDs in history MUST be deduplicated (move to end) | MUST |

**Implementation**: `gateway/ui/platform_app.py`

### 4.4 Home Page

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-030** | [V1] Home page MUST display product catalog | MUST |
| **GW-UI-031** | [V1] Products MUST be displayed sorted by name | MUST |
| **GW-UI-032** | [V1] Each product MUST be shown in collapsible expander with format: "{display_name} ({name})" | MUST |
| **GW-UI-033** | [V1] Product details MUST show description and available flows | MUST |
| **GW-UI-034** | [V1] Empty product list MUST show info message "No enabled products were discovered." | MUST |

**Implementation**: `gateway/ui/pages/home.py`

### 4.5 Execution Page - Run Tab

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-040** | [V1] Execution page MUST have three tabs: "▶️ Run", "🔒 Approvals", "❓ User Inputs" | MUST |
| **GW-UI-050** | [V1] Run tab MUST provide product selector dropdown | MUST |
| **GW-UI-051** | [V1] Run tab MUST provide flow selector dropdown (populated from API) | MUST |
| **GW-UI-052** | [V1] Run tab MUST support file uploads when product config enables inputs | MUST |
| **GW-UI-053** | [V1] File uploads MUST respect `max_files`, `allowed_extensions` from product config | MUST |
| **GW-UI-054** | [V1] Run tab MUST support intent-driven mode with text area when product enables intent | MUST |
| **GW-UI-055** | [V1] Run tab MUST support JSON payload editor when intent is disabled | MUST |
| **GW-UI-056** | [V1] "Load Example" button MUST populate example payload for known products | MUST |
| **GW-UI-057** | [V1] Invalid JSON in payload editor MUST display error message | MUST |
| **GW-UI-058** | [V1] Dataset selector MUST be shown when product config defines `dataset_candidates` | MUST |
| **GW-UI-059** | [V1] "Run flow" button MUST be disabled when payload JSON is invalid | MUST |
| **GW-UI-060** | [V1] Successful run MUST display success message with run ID | MUST |
| **GW-UI-061** | [V1] Run status indicators MUST show when run requires user input or approval | MUST |
| **GW-UI-062** | [V1] "Refresh run status" button MUST update last run status from API | MUST |

**Implementation**: `gateway/ui/pages/execution.py`

### 4.6 Execution Page - Approvals Tab

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-070** | [V1] Approvals tab MUST list all pending approvals | MUST |
| **GW-UI-071** | [V1] Each approval MUST display: run_id, product, flow, step_id, type, created_at | MUST |
| **GW-UI-072** | [V1] Approval details MUST show: summary, instructions, actions, approval_context, intent | MUST |
| **GW-UI-073** | [V1] Approval context MUST display: reason, step_name, decision_notes, recommended_action | MUST |
| **GW-UI-074** | [V1] Comment text area MUST be provided for reviewer input | MUST |
| **GW-UI-075** | [V1] "Approve" button MUST resume run with decision "APPROVED" | MUST |
| **GW-UI-076** | [V1] "Reject" button MUST resume run with decision "REJECTED" | MUST |
| **GW-UI-077** | [V1] Raw approval details MUST be viewable in expandable section | MUST |
| **GW-UI-078** | [V1] Page MUST rerun after approval/rejection to refresh state | MUST |

**Implementation**: `gateway/ui/pages/execution.py`

### 4.7 Execution Page - User Inputs Tab

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-080** | [V1] User inputs tab MUST scan recent runs (up to 20) for pending inputs | MUST |
| **GW-UI-081** | [V1] Runs with status `PAUSED_WAITING_FOR_USER`, `PENDING_USER_INPUT`, `NEEDS_USER_INPUT` MUST be checked for pending input | MUST |
| **GW-UI-082** | [V1] Each input request MUST display: run_id, title, question | MUST |
| **GW-UI-083** | [V1] Text area MUST be provided for user response | MUST |
| **GW-UI-084** | [V1] Submit button MUST be disabled until user provides non-empty response | MUST |
| **GW-UI-085** | [V1] User input MUST be submitted with `run_id` and `text` containing the response | MUST |
| **GW-UI-086** | [V1] Submission metadata MUST include `source: "ui_inputs_tab"` | MUST |
| **GW-UI-087** | [V1] Page MUST rerun after submission to refresh state | MUST |

**Implementation**: `gateway/ui/pages/execution.py`

### 4.8 History Page

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-090** | [V1] History page MUST display all runs from session history | MUST |
| **GW-UI-091** | [V1] Runs MUST be displayed in reverse chronological order (newest first) | MUST |
| **GW-UI-092** | [V1] Each run MUST display: run_id (truncated), status with icon, product/flow, created_at | MUST |
| **GW-UI-093** | [V1] Status icons MUST be displayed: ✅ COMPLETED, 🔄 RUNNING, ⏳ PENDING, ❌ FAILED, ⏸️ PAUSED, ❓ user input, 🔒 approval, 🚫 CANCELLED, ⚠️ ERROR | MUST |
| **GW-UI-094** | [V1] Run selector dropdown MUST allow selecting a run for detailed view | MUST |
| **GW-UI-095** | [V1] Run details MUST display metrics: Status, Product, Flow, Created | MUST |
| **GW-UI-096** | [V1] Raw run data MUST be viewable in expandable section | MUST |
| **GW-UI-097** | [V1] Event timeline MUST be displayed for selected run | MUST |
| **GW-UI-098** | [V1] Each event MUST display: event_type with icon, timestamp, expandable data | MUST |
| **GW-UI-099** | [V1] Event icons MUST be displayed for event types: RUN_STARTED (🚀), RUN_COMPLETED (✅), RUN_FAILED (❌), STEP_STARTED (▶️), STEP_COMPLETED (✔️), STEP_FAILED (⚠️), USER_INPUT_REQUESTED (❓), USER_INPUT_RECEIVED (💬), APPROVAL_REQUESTED (🔒), APPROVAL_GRANTED (✅), APPROVAL_DENIED (🚫), TOOL_CALLED (🔧), TOOL_RESULT (📤), LLM_CALL (🤖), LLM_RESPONSE (💡) | MUST |
| **GW-UI-100** | [V1] Empty history MUST show info message directing user to Execution page | MUST |

**Implementation**: `gateway/ui/pages/history.py`

### 4.9 API Client

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-110** | [V1] ApiClient MUST wrap all HTTP requests with standardized `ApiResponse` | MUST |
| **GW-UI-111** | [V1] ApiResponse MUST include: `ok` (bool), `data` (Optional[Dict]), `error` (Optional[str]) | MUST |
| **GW-UI-112** | [V1] Client MUST handle request exceptions gracefully | MUST |
| **GW-UI-113** | [V1] Client MUST parse JSON responses and extract error messages | MUST |
| **GW-UI-114** | [V1] Client MUST detect API-level errors (ok=false in body) | MUST |
| **GW-UI-115** | [V1] Default timeout MUST be 15 seconds | MUST |
| **GW-UI-116** | [V1] API base URL MUST be determined from settings or fallback to host:port | MUST |

**Implementation**: `gateway/ui/api_client.py`

### 4.10 Required Client Methods

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-UI-120** | [V1] `get_products()` → `GET /api/products` | MUST |
| **GW-UI-121** | [V1] `get_flows(product)` → `GET /api/products/{product}/flows` | MUST |
| **GW-UI-122** | [V1] `run_flow(product, flow, payload)` → `POST /api/products/{product}/flows/{flow}/run` | MUST |
| **GW-UI-123** | [V1] `get_run(run_id)` → `GET /api/runs/{run_id}` | MUST |
| **GW-UI-124** | [V1] `list_runs(limit, offset)` → `GET /api/runs` | MUST |
| **GW-UI-125** | [V1] `get_pending_input(run_id)` → `GET /api/runs/{run_id}/pending_input` | MUST |
| **GW-UI-126** | [V1] `submit_user_input(run_id, data)` → `POST /api/runs/{run_id}/user_input` | MUST |
| **GW-UI-127** | [V1] `get_approvals()` → `GET /api/approvals` | MUST |
| **GW-UI-128** | [V1] `resume_run(run_id, data)` → `POST /api/runs/{run_id}/resume` | MUST |
| **GW-UI-129** | [V1] `get_run_bundle(run_id)` → `GET /api/runs/{run_id}/bundle` | MUST |

**Implementation**: `gateway/ui/api_client.py`

---

## 5. Session Isolation Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-ISO-001** | [V1] Each API request MUST receive a fresh OrchestratorEngine instance | MUST |
| **GW-ISO-002** | [V1] Engine state MUST NOT be shared between requests | MUST |
| **GW-ISO-003** | [V1] Memory router MAY be shared (singleton) as it manages persistence | MAY |
| **GW-ISO-004** | [V1] Product catalog MAY be shared (singleton) as it is read-only | MAY |
| **GW-ISO-005** | [V1] Tracer MAY be shared (singleton) as it manages centralized logging | MAY |

**Implementation**: `gateway/api/deps.py`

---

## 6. Error Handling Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-ERR-001** | [V1] API errors MUST use appropriate HTTP status codes: 400 (bad request), 404 (not found), 413 (payload too large), 500 (server error), 503 (service unavailable) | MUST |
| **GW-ERR-002** | [V1] Error responses MUST include machine-readable `code` field | MUST |
| **GW-ERR-003** | [V1] Error responses MUST include human-readable `message` field | MUST |
| **GW-ERR-004** | [V1] Error responses MAY include `details` object with additional context | MAY |
| **GW-ERR-005** | [V1] Standard error codes MUST include: `product_not_found`, `product_disabled`, `product_unavailable`, `flow_not_found`, `payload_too_large`, `invalid_path`, `not_found`, `unknown_error` | MUST |
| **GW-ERR-006** | [V1] UI MUST display user-friendly error messages from API responses | MUST |
| **GW-ERR-007** | [V1] CLI MUST exit with non-zero code on errors | MUST |

**Implementation**: `gateway/api/routes_run.py`, `gateway/cli/main.py`

### 6.1 Semantic Error Codes (Added: 2026-01-13)

> **Source**: BRD-EXP-ERR-001...007, INV-4

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **GW-SEM-ERR-001** | [V1] `semantic_interpretation_failed` MUST be returned (500) when semantic phase fails to produce envelope | MUST | 1.1 |
| **GW-SEM-ERR-002** | [V1] `semantic_confidence_too_low` MUST be returned (422) when confidence < threshold | MUST | 1.1 |
| **GW-SEM-ERR-003** | [V1] `semantic_abort_requested` MUST be returned (422) when orchestrator exits with ABORT | MUST | 1.1 |
| **GW-SEM-ERR-004** | [V1] `semantic_clarification_required` MUST be returned (202) when ASK_USER exit | MUST | 1.1 |
| **GW-SEM-ERR-005** | [V1] All semantic errors MUST include `envelope_hash` in response details | MUST | 1.1 |
| **GW-SEM-ERR-006** | [V1] `semantic_abort_requested` MUST include `AbortArtifact` in response body | MUST | 1.1 |
| **GW-SEM-ERR-007** | [V1] `semantic_clarification_required` MUST include `ClarificationRequest` in response body | MUST | 1.1 |

**Implementation**: `gateway/api/routes_run.py`

### 6.2 Semantic Exit Handling (Added: 2026-01-13)

> **Source**: BRD-EXP-EXIT-001...005, BRD-EXP-ASK-001...004

| ID | Requirement | Level | Ver |
|----|-------------|-------|-----|
| **GW-SEM-EXIT-001** | [V1] ASK_USER exit MUST return HTTP 202 (Accepted) with pending input URL | MUST | 1.1 |
| **GW-SEM-EXIT-002** | [V1] ABORT exit MUST return HTTP 422 (Unprocessable Entity) with reason | MUST | 1.1 |
| **GW-SEM-EXIT-003** | [V1] PARTIAL_SUCCESS exit MUST return HTTP 200 with `status=partial_success` | MUST | 1.1 |
| **GW-SEM-EXIT-004** | [V1] BUDGET_EXCEEDED exit MUST return HTTP 429 (Too Many Requests) | MUST | 1.1 |
| **GW-SEM-EXIT-005** | [V1] All semantic exits MUST include `exit_state` field in response | MUST | 1.1 |

**Semantic Exit Response Schema**:
```json
{
    "run_id": "uuid",
    "status": "running|paused|completed|failed|partial_success",
    "exit_state": "SUCCESS|PARTIAL_SUCCESS|ASK_USER|ABORT|BUDGET_EXCEEDED",
    "semantic": {
        "envelope_hash": "sha256",
        "confidence": 0.85,
        "proposed_next_action": "CONTINUE|ASK_USER|ABORT"
    },
    "clarification_request": { ... },  // if ASK_USER
    "abort_artifact": { ... }           // if ABORT
}
```

**Implementation**: `gateway/api/routes_run.py`

---

## 7. File Handling Requirements

| ID | Requirement | Level |
|----|-------------|-------|
| **GW-FILE-001** | [V1] Uploaded files MUST be staged in `observability/staging` directory | MUST |
| **GW-FILE-002** | [V1] Staging directories MUST be cleared before new uploads | MUST |
| **GW-FILE-003** | [V1] Output files MUST be served from `observability/<product>/<run_id>/output` | MUST |
| **GW-FILE-004** | [V1] Run directories MUST include: `output`, `input`, `runtime`, `output` subdirectories | MUST |
| **GW-FILE-005** | [V1] Path traversal attacks MUST be prevented via path resolution validation | MUST |
| **GW-FILE-006** | [V1] Dataset candidates MUST be scanned from `products/data` and `products/<product>/data` | MUST |

**Implementation**: `gateway/api/routes_run.py`, `core/memory/observability_store.py`

---

## 8. Explicit Non-Goals (Added: 2026-01-13)

> **Gateway MUST NOT**:

| Non-Goal | Rationale | Violation Example |
|----------|-----------|-------------------|
| Silent error suppression | All errors must be surfaced | API catches exception, returns 200 |
| Direct orchestrator state mutation | Gateway is read-only for state | API endpoint modifies run_context |
| Exposing raw LLM responses | Privacy and security | API returns full prompt/completion |
| Cross-product data exposure | Product isolation enforced | List runs shows all products |
| Bypassing governance | Gateway respects all policies | API endpoint skips approval check |
| Client-controlled confidence | Confidence is server-determined | API accepts confidence in request |

---

## 9. Future Considerations

### 9.1 V1.1 Enhancements

| ID | Feature | Description |
|----|---------|-------------|
| **GW-FUTURE-001** | WebSocket streaming | Real-time event streaming |
| **GW-FUTURE-002** | API versioning | `/api/v1/` prefix |
| **GW-FUTURE-003** | Rate limiting | Per-client rate limits |

### 9.2 V2 Features

| ID | Feature | Description |
|----|---------|-------------|
| **GW-FUTURE-010** | Authentication | JWT/OAuth2 authentication |
| **GW-FUTURE-011** | Multi-tenancy | Tenant isolation |
| **GW-FUTURE-012** | GraphQL | Alternative API interface |

---

## 10. Traceability Matrix

| Requirement | Implementation | Test | BRD Source |
|-------------|----------------|------|------------|
| GW-API-001 | `gateway/api/http_app.py` | `tests/integration/test_http_app.py` | BRD-EXP-010 |
| GW-API-020 | `gateway/api/routes_run.py` | `tests/integration/test_routes_run.py` | BRD-EXP-020 |
| GW-CLI-001 | `gateway/cli/main.py` | `tests/integration/test_cli.py` | BRD-EXP-030 |
| GW-UI-001 | `gateway/ui/platform_app.py` | `tests/integration/test_ui.py` | BRD-EXP-040 |
| GW-ISO-001 | `gateway/api/deps.py` | `tests/unit/gateway/test_deps.py` | BRD-EXP-050 |
| GW-SEM-ERR-001...007 | `gateway/api/routes_run.py` | `tests/integration/test_semantic_errors.py` | BRD-EXP-ERR-001...007 |
| GW-SEM-EXIT-001...005 | `gateway/api/routes_run.py` | `tests/integration/test_semantic_exits.py` | BRD-EXP-EXIT-001...005 |

---

## 11. BRD Requirement Mapping (Added: 2026-01-13)

| BRD Requirement | Techspec Requirement(s) | Status |
|-----------------|-------------------------|--------|
| BRD-EXP-ERR-001 | GW-SEM-ERR-001 | Mapped |
| BRD-EXP-ERR-002 | GW-SEM-ERR-002 | Mapped |
| BRD-EXP-ERR-003 | GW-SEM-ERR-003 | Mapped |
| BRD-EXP-ERR-004 | GW-SEM-ERR-004 | Mapped |
| BRD-EXP-ERR-005 | GW-SEM-ERR-005 | Mapped |
| BRD-EXP-ERR-006 | GW-SEM-ERR-006 | Mapped |
| BRD-EXP-ERR-007 | GW-SEM-ERR-007 | Mapped |
| BRD-EXP-EXIT-001 | GW-SEM-EXIT-001 | Mapped |
| BRD-EXP-EXIT-002 | GW-SEM-EXIT-002 | Mapped |
| BRD-EXP-EXIT-003 | GW-SEM-EXIT-003 | Mapped |
| BRD-EXP-EXIT-004 | GW-SEM-EXIT-004 | Mapped |
| BRD-EXP-EXIT-005 | GW-SEM-EXIT-005 | Mapped |
| BRD-EXP-ASK-001 | GW-SEM-EXIT-001, GW-API-030 | Mapped |
| BRD-EXP-ASK-002 | GW-SEM-ERR-007 | Mapped |
| BRD-EXP-ASK-003 | GW-API-031 | Existing |
| BRD-EXP-ASK-004 | GW-API-032, GW-API-033 | Existing |
| BRD-EXP-010...050 | GW-API-*, GW-CLI-*, GW-UI-* | Existing |