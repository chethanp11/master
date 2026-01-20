# Gateway Technical Specification

> **Document ID**: GW  
> **Version**: V1.2  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-13  

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial V1 specification |
| 1.1.0 | 2026-01-13 | Added: §6.1 Semantic Error Codes, §6.2 Semantic Exit Handling, §8 Explicit Non-Goals, §11 BRD Requirement Mapping |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |

---

## 1. Overview

The gateway layer provides external access to the platform through HTTP API, CLI, and 
Streamlit UI. All three interfaces share the same orchestration engine and follow 
consistent patterns for session isolation and error handling.

## 2. HTTP API Requirements

### 2.1 Server Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-API-001 | The system MUST expose a FastAPI application via a factory function `create_app()` | MUST | BRD-EXP-001 | 1.1 | 13 Jan 2026 | — |
| GW-API-002 | The application MUST include a health check endpoint at `GET /health` | MUST | BRD-EXP-001 | 1.1 | 13 Jan 2026 | — |
| GW-API-003 | The health endpoint MUST return `{"status": "ok"}` when the service is operational | MUST | BRD-EXP-001 | 1.1 | 13 Jan 2026 | — |
| GW-API-004 | All API routes MUST be mounted under the `/api` prefix | MUST | BRD-EXP-001 | 1.1 | 13 Jan 2026 | — |
| GW-API-005 | An ASGI entrypoint named `app` MUST be available at module level for uvicorn | MUST | BRD-EXP-001 | 1.1 | 13 Jan 2026 | — |


### 2.2 Product Endpoints

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-API-010 | `GET /api/products` MUST list all discovered products | MUST | BRD-EXP-005 | 1.1 | 13 Jan 2026 | — |
| GW-API-011 | `GET /api/products/{product}/flows` MUST list flows for a specific product | MUST | BRD-EXP-005 | 1.1 | 13 Jan 2026 | — |
| GW-API-012 | Products endpoint response MUST include: `name`, `display_name`, `description`, `version`, `enabled`, `default_flow`, `ui_enabled`, `flows`, `error`, `error_path`, `error_message`, `ui` | MUST | BRD-EXP-005 | 1.1 | 13 Jan 2026 | — |
| GW-API-013 | Products endpoint MUST return `error=true` for products that failed to load | MUST | BRD-EXP-005 | 1.1 | 13 Jan 2026 | — |
| GW-API-014 | Flows endpoint MUST return 404 with code `product_not_found` for unknown products | MUST | BRD-EXP-005 | 1.1 | 13 Jan 2026 | — |
| GW-API-015 | Flows endpoint MUST return 404 with code `product_disabled` for disabled products | MUST | BRD-EXP-005 | 1.1 | 13 Jan 2026 | — |
| GW-API-016 | Flows endpoint MUST return 503 with code `product_unavailable` for products with load errors | MUST | BRD-EXP-005 | 1.1 | 13 Jan 2026 | — |


### 2.3 Run Endpoints

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-API-020 | `POST /api/products/{product}/flows/{flow}/run` MUST start a new flow execution | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |
| GW-API-021 | `GET /api/runs/{run_id}` MUST return run status and details | MUST | BRD-EXP-006, BRD-OPS-052 | 1.1 | 13 Jan 2026 | — |
| GW-API-022 | `GET /api/runs` MUST list all runs with pagination (`limit`, `offset` parameters) | MUST | BRD-EXP-006, BRD-OPS-050 | 1.1 | 13 Jan 2026 | — |
| GW-API-023 | Run request payload MUST accept `payload` (Dict) and optional `requested_by` (String) fields | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |
| GW-API-024 | Run payload size MUST be limited to 100KB (100 * 1024 bytes) | MUST | BRD-EXP-006, BRD-EXP-007 | 1.1 | 13 Jan 2026 | — |
| GW-API-025 | Requests exceeding payload size limit MUST return 413 with code `payload_too_large` | MUST | BRD-EXP-006, BRD-EXP-007 | 1.1 | 13 Jan 2026 | — |
| GW-API-026 | Unknown flows MUST return 404 with code `flow_not_found` including `available_flows` in details | MUST | BRD-EXP-006, BRD-EXP-053 | 1.1 | 13 Jan 2026 | — |
| GW-API-027 | When `intent` is provided without `payload`, the system MUST map it to an intent field based on product UI configuration | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |


### 2.4 User Input Endpoints

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-API-030 | `GET /api/runs/{run_id}/pending_input` MUST return pending user input prompt | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |
| GW-API-031 | `POST /api/runs/{run_id}/user_input` MUST submit user input response | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |
| GW-API-032 | User input submission MUST accept: `run_id` (required), `form_id`, `answers`, `text`, `values`, `metadata` | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |
| GW-API-033 | When `answers` is provided, system MUST construct form-based response with `form_id`, `schema`, `answers`, `submitted_at` | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |
| GW-API-034 | When `answers` is not provided, system MUST use `FreeTextResponse` schema with `text`, `intent`, `attachments`, `metadata` | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |


### 2.5 Approval Endpoints

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-API-040 | `GET /api/approvals` MUST list pending approvals with pagination (`limit`, `offset`) | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |
| GW-API-041 | `POST /api/runs/{run_id}/resume` MUST resume a paused run with approval decision | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |
| GW-API-042 | Resume request MUST accept: `approved`, `decision`, `comment`, `resolved_by`, `replan` | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |
| GW-API-043 | Decision field MUST default to `"APPROVED"` | MUST | BRD-EXP-006 | 1.1 | 13 Jan 2026 | — |


### 2.6 Output Endpoints

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-API-050 | `GET /api/runs/{run_id}/output/{file_path}` MUST serve output files as FileResponse | MUST | BRD-GOV-043, BRD-OPS-053 | 1.1 | 13 Jan 2026 | — |
| GW-API-051 | Output file paths MUST be validated to prevent path traversal attacks | MUST | BRD-GOV-043, BRD-OPS-053 | 1.1 | 13 Jan 2026 | — |
| GW-API-052 | Invalid output paths MUST return 400 with code `invalid_path` | MUST | BRD-GOV-043, BRD-OPS-053 | 1.1 | 13 Jan 2026 | — |
| GW-API-053 | Missing output files MUST return 404 with code `not_found` | MUST | BRD-GOV-043, BRD-OPS-053 | 1.1 | 13 Jan 2026 | — |


### 2.7 Request/Response Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-API-060 | All successful responses MUST follow envelope: `{"ok": true, "data": {...}, "meta": {...}}` | MUST | BRD-EXP-002 | 1.1 | 13 Jan 2026 | — |
| GW-API-061 | All error responses MUST follow envelope: `{"ok": false, "error": {"code": "...", "message": "...", "details": {...}}}` | MUST | BRD-EXP-002, BRD-EXP-003, BRD-EXP-004 | 1.1 | 13 Jan 2026 | — |
| GW-API-062 | Error codes MUST be lowercase snake_case strings | MUST | BRD-EXP-002, BRD-EXP-003 | 1.1 | 13 Jan 2026 | — |
| GW-API-063 | Meta field MAY include contextual information like `run_id`, `product`, `flow`, `timestamp` | MAY | BRD-EXP-002 | 1.1 | 13 Jan 2026 | — |


### 2.8 Dependency Injection

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-API-070 | Settings MUST be loaded once and cached via `get_settings` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-API-071 | Product catalog MUST be loaded once and cached via `get_product_catalog` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-API-072 | Memory router MUST be a singleton via `get_memory_router` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-API-073 | Tracer MUST be a singleton via `get_tracer` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-API-074 | OrchestratorEngine MUST be instantiated per-request to ensure session isolation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-API-075 | Engine MUST NOT be cached to avoid cross-session state leakage | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 3. CLI Requirements

### 3.1 Command Structure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-CLI-001 | CLI MUST be invocable as `master <command>` | MUST | BRD-EXP-010 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-002 | CLI MUST require a subcommand (no default action) | MUST | BRD-EXP-010 | 1.1 | 13 Jan 2026 | — |


### 3.2 Commands

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-CLI-010 | `products` command MUST list all discovered products with metadata | MUST | BRD-EXP-012 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-011 | `flows <product>` command MUST list flows for specified product | MUST | BRD-EXP-012 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-012 | `run <product> <flow>` command MUST execute a flow | MUST | BRD-EXP-012 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-013 | Run command MUST accept `--payload <json>` OR `--payload-file <path>` (mutually exclusive) | MUST | BRD-EXP-012 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-014 | Run command MAY accept `--requested-by <identifier>` | MAY | BRD-EXP-012 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-015 | `status <run_id>` command MUST return run status | MUST | BRD-EXP-012, BRD-OPS-050, BRD-OPS-052 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-016 | `get <run_id>` command MUST be an alias for status | MUST | BRD-EXP-012, BRD-OPS-052 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-017 | `approvals` command MUST list pending approvals | MUST | BRD-EXP-012 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-018 | `resume --run-id <id>` command MUST resume a paused run | MUST | BRD-EXP-012 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-019 | Resume command MUST accept mutually exclusive `--approve` or `--reject` flags | MUST | BRD-EXP-012 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-020 | Resume command MAY accept `--comment`, `--resolved-by`, `--decision`, `--replan` | MAY | BRD-EXP-012 | 1.1 | 13 Jan 2026 | — |


### 3.3 Output Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-CLI-030 | All CLI output MUST be valid JSON | MUST | BRD-EXP-011 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-031 | JSON output MUST be formatted with 2-space indentation | MUST | BRD-EXP-011, BRD-GOV-043 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-032 | Successful commands MUST return exit code 0 | MUST | BRD-EXP-011, BRD-EXP-013 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-033 | Failed commands MUST return exit code 1 | MUST | BRD-EXP-011, BRD-EXP-013 | 1.1 | 13 Jan 2026 | — |


### 3.4 Error Handling

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-CLI-040 | Invalid JSON payload MUST exit with message "Invalid JSON payload: ..." | MUST | BRD-EXP-014 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-041 | Non-object JSON payload MUST exit with message "JSON payload must be an object." | MUST | BRD-EXP-014 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-042 | Unknown product MUST exit with guidance to run `master products` | MUST | BRD-EXP-014 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-043 | Disabled product MUST exit with guidance to update `configs/products.yaml` | MUST | BRD-EXP-014 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-044 | Product load errors MUST exit with error path and message | MUST | BRD-EXP-014 | 1.1 | 13 Jan 2026 | — |
| GW-CLI-045 | Unknown flow MUST exit listing available flows | MUST | BRD-EXP-014 | 1.1 | 13 Jan 2026 | — |


---

## 4. UI Requirements

### 4.1 Application Structure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-001 | UI MUST be implemented using Streamlit framework | MUST | BRD-EXP-020 | 1.1 | 13 Jan 2026 | — |
| GW-UI-002 | UI MUST use wide layout mode | MUST | BRD-EXP-020 | 1.1 | 13 Jan 2026 | — |
| GW-UI-003 | Page title MUST be "master platform" | MUST | BRD-EXP-020 | 1.1 | 13 Jan 2026 | — |
| GW-UI-004 | UI MUST load settings from repository root | MUST | BRD-EXP-020 | 1.1 | 13 Jan 2026 | — |
| GW-UI-005 | UI MUST communicate with API via HTTP client (no direct core imports) | MUST | BRD-EXP-020 | 1.1 | 13 Jan 2026 | — |


### 4.2 Navigation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-010 | Sidebar MUST display navigation header "Navigation" | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-011 | Sidebar MUST provide radio selection for pages: "Home", "Execution", "History" | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-012 | Sidebar MUST display current API base URL | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.3 Session State

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-020 | Session state MUST maintain `run_history` list | MUST | BRD-EXP-023 | 1.1 | 13 Jan 2026 | — |
| GW-UI-021 | Session state MUST track `last_run_id`, `last_run_status`, `last_run_product`, `last_run_flow` | MUST | BRD-EXP-023 | 1.1 | 13 Jan 2026 | — |
| GW-UI-022 | Run IDs MUST be appended to history when runs are started | MUST | BRD-EXP-023 | 1.1 | 13 Jan 2026 | — |
| GW-UI-023 | Duplicate run IDs in history MUST be deduplicated (move to end) | MUST | BRD-EXP-023 | 1.1 | 13 Jan 2026 | — |


### 4.4 Home Page

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-030 | Home page MUST display product catalog | MUST | BRD-EXP-021 | 1.1 | 13 Jan 2026 | — |
| GW-UI-031 | Products MUST be displayed sorted by name | MUST | BRD-EXP-021 | 1.1 | 13 Jan 2026 | — |
| GW-UI-032 | Each product MUST be shown in collapsible expander with format: "{display_name} ({name})" | MUST | BRD-EXP-021 | 1.1 | 13 Jan 2026 | — |
| GW-UI-033 | Product details MUST show description and available flows | MUST | BRD-EXP-021 | 1.1 | 13 Jan 2026 | — |
| GW-UI-034 | Empty product list MUST show info message "No enabled products were discovered." | MUST | BRD-EXP-021 | 1.1 | 13 Jan 2026 | — |


### 4.5 Execution Page - Run Tab

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-040 | Execution page MUST have three tabs: "▶️ Run", "🔒 Approvals", "❓ User Inputs" | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-050 | Run tab MUST provide product selector dropdown | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-051 | Run tab MUST provide flow selector dropdown (populated from API) | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-052 | Run tab MUST support file uploads when product config enables inputs | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-053 | File uploads MUST respect `max_files`, `allowed_extensions` from product config | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-054 | Run tab MUST support intent-driven mode with text area when product enables intent | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-055 | Run tab MUST support JSON payload editor when intent is disabled | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-056 | "Load Example" button MUST populate example payload for known products | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-057 | Invalid JSON in payload editor MUST display error message | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-058 | Dataset selector MUST be shown when product config defines `dataset_candidates` | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-059 | "Run flow" button MUST be disabled when payload JSON is invalid | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-060 | Successful run MUST display success message with run ID | MUST | BRD-EXP-022 | 1.1 | 13 Jan 2026 | — |
| GW-UI-061 | Run status indicators MUST show when run requires user input or approval | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-062 | "Refresh run status" button MUST update last run status from API | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.6 Execution Page - Approvals Tab

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-070 | Approvals tab MUST list all pending approvals | MUST | BRD-EXP-024 | 1.1 | 13 Jan 2026 | — |
| GW-UI-071 | Each approval MUST display: run_id, product, flow, step_id, type, created_at | MUST | BRD-EXP-024 | 1.1 | 13 Jan 2026 | — |
| GW-UI-072 | Approval details MUST show: summary, instructions, actions, approval_context, intent | MUST | BRD-EXP-024 | 1.1 | 13 Jan 2026 | — |
| GW-UI-073 | Approval context MUST display: reason, step_name, decision_notes, recommended_action | MUST | BRD-EXP-024 | 1.1 | 13 Jan 2026 | — |
| GW-UI-074 | Comment text area MUST be provided for reviewer input | MUST | BRD-EXP-024 | 1.1 | 13 Jan 2026 | — |
| GW-UI-075 | "Approve" button MUST resume run with decision "APPROVED" | MUST | BRD-EXP-024 | 1.1 | 13 Jan 2026 | — |
| GW-UI-076 | "Reject" button MUST resume run with decision "REJECTED" | MUST | BRD-EXP-024 | 1.1 | 13 Jan 2026 | — |
| GW-UI-077 | Raw approval details MUST be viewable in expandable section | MUST | BRD-EXP-024 | 1.1 | 13 Jan 2026 | — |
| GW-UI-078 | Page MUST rerun after approval/rejection to refresh state | MUST | BRD-EXP-024 | 1.1 | 13 Jan 2026 | — |


### 4.7 Execution Page - User Inputs Tab

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-080 | User inputs tab MUST scan recent runs (up to 20) for pending inputs | MUST | BRD-EXP-025 | 1.1 | 13 Jan 2026 | — |
| GW-UI-081 | Runs with status `PAUSED_WAITING_FOR_USER`, `PENDING_USER_INPUT`, `NEEDS_USER_INPUT` MUST be checked for pending input | MUST | BRD-EXP-025 | 1.1 | 13 Jan 2026 | — |
| GW-UI-082 | Each input request MUST display: run_id, title, question | MUST | BRD-EXP-025 | 1.1 | 13 Jan 2026 | — |
| GW-UI-083 | Text area MUST be provided for user response | MUST | BRD-EXP-025 | 1.1 | 13 Jan 2026 | — |
| GW-UI-084 | Submit button MUST be disabled until user provides non-empty response | MUST | BRD-EXP-025 | 1.1 | 13 Jan 2026 | — |
| GW-UI-085 | User input MUST be submitted with `run_id` and `text` containing the response | MUST | BRD-EXP-025 | 1.1 | 13 Jan 2026 | — |
| GW-UI-086 | Submission metadata MUST include `source: "ui_inputs_tab"` | MUST | BRD-EXP-025 | 1.1 | 13 Jan 2026 | — |
| GW-UI-087 | Page MUST rerun after submission to refresh state | MUST | BRD-EXP-025 | 1.1 | 13 Jan 2026 | — |


### 4.8 History Page

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-090 | History page MUST display all runs from session history | MUST | BRD-EXP-026, BRD-OPS-041 | 1.1 | 13 Jan 2026 | — |
| GW-UI-091 | Runs MUST be displayed in reverse chronological order (newest first) | MUST | BRD-EXP-026 | 1.1 | 13 Jan 2026 | — |
| GW-UI-092 | Each run MUST display: run_id (truncated), status with icon, product/flow, created_at | MUST | BRD-EXP-026 | 1.1 | 13 Jan 2026 | — |
| GW-UI-093 | Status icons MUST be displayed: ✅ COMPLETED, 🔄 RUNNING, ⏳ PENDING, ❌ FAILED, ⏸️ PAUSED, ❓ user input, 🔒 approval, 🚫 CANCELLED, ⚠️ ERROR | MUST | BRD-EXP-026 | 1.1 | 13 Jan 2026 | — |
| GW-UI-094 | Run selector dropdown MUST allow selecting a run for detailed view | MUST | BRD-EXP-026 | 1.1 | 13 Jan 2026 | — |
| GW-UI-095 | Run details MUST display metrics: Status, Product, Flow, Created | MUST | BRD-EXP-026 | 1.1 | 13 Jan 2026 | — |
| GW-UI-096 | Raw run data MUST be viewable in expandable section | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-097 | Event timeline MUST be displayed for selected run | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-098 | Each event MUST display: event_type with icon, timestamp, expandable data | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-099 | Event icons MUST be displayed for event types: RUN_STARTED (🚀), RUN_COMPLETED (✅), RUN_FAILED (❌), STEP_STARTED (▶️), STEP_COMPLETED (✔️), STEP_FAILED (⚠️), USER_INPUT_REQUESTED (❓), USER_INPUT_RECEIVED (💬), APPROVAL_REQUESTED (🔒), APPROVAL_GRANTED (✅), APPROVAL_DENIED (🚫), TOOL_CALLED (🔧), TOOL_RESULT (📤), LLM_CALL (🤖), LLM_RESPONSE (💡) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-100 | Empty history MUST show info message directing user to Execution page | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.9 API Client

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-110 | ApiClient MUST wrap all HTTP requests with standardized `ApiResponse` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-111 | ApiResponse MUST include: `ok` (bool), `data` (Optional[Dict]), `error` (Optional[str]) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-112 | Client MUST handle request exceptions gracefully | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-113 | Client MUST parse JSON responses and extract error messages | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-114 | Client MUST detect API-level errors (ok=false in body) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-115 | Default timeout MUST be 15 seconds | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-116 | API base URL MUST be determined from settings or fallback to host:port | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.10 Required Client Methods

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-UI-120 | `get_products()` → `GET /api/products` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-121 | `get_flows(product)` → `GET /api/products/{product}/flows` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-122 | `run_flow(product, flow, payload)` → `POST /api/products/{product}/flows/{flow}/run` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-123 | `get_run(run_id)` → `GET /api/runs/{run_id}` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-124 | `list_runs(limit, offset)` → `GET /api/runs` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-125 | `get_pending_input(run_id)` → `GET /api/runs/{run_id}/pending_input` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-126 | `submit_user_input(run_id, data)` → `POST /api/runs/{run_id}/user_input` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-127 | `get_approvals()` → `GET /api/approvals` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-128 | `resume_run(run_id, data)` → `POST /api/runs/{run_id}/resume` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-UI-129 | `get_run_bundle(run_id)` → `GET /api/runs/{run_id}/bundle` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 5. Session Isolation Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-ISO-001 | Each API request MUST receive a fresh OrchestratorEngine instance | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-ISO-002 | Engine state MUST NOT be shared between requests | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-ISO-003 | Memory router MAY be shared (singleton) as it manages persistence | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-ISO-004 | Product catalog MAY be shared (singleton) as it is read-only | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-ISO-005 | Tracer MAY be shared (singleton) as it manages centralized logging | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 6. Error Handling Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-ERR-001 | API errors MUST use appropriate HTTP status codes: 400 (bad request), 404 (not found), 413 (payload too large), 500 (server error), 503 (service unavailable) | MUST | BRD-EXP-050 | 1.1 | 13 Jan 2026 | — |
| GW-ERR-002 | Error responses MUST include machine-readable `code` field | MUST | BRD-EXP-050 | 1.1 | 13 Jan 2026 | — |
| GW-ERR-003 | Error responses MUST include human-readable `message` field | MUST | BRD-EXP-050 | 1.1 | 13 Jan 2026 | — |
| GW-ERR-004 | Error responses MAY include `details` object with additional context | MAY | BRD-EXP-051 | 1.1 | 13 Jan 2026 | — |
| GW-ERR-005 | Standard error codes MUST include: `product_not_found`, `product_disabled`, `product_unavailable`, `flow_not_found`, `payload_too_large`, `invalid_path`, `not_found`, `unknown_error` | MUST | BRD-EXP-051 | 1.1 | 13 Jan 2026 | — |
| GW-ERR-006 | UI MUST display user-friendly error messages from API responses | MUST | BRD-EXP-052 | 1.1 | 13 Jan 2026 | — |
| GW-ERR-007 | CLI MUST exit with non-zero code on errors | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.1 Semantic Error Codes (Added: 2026-01-13)

> **Source**: BRD-EXP-ERR-001...007, INV-4

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-SEM-ERR-001 | `semantic_interpretation_failed` MUST be returned (500) when semantic phase fails to produce envelope | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-ERR-002 | `semantic_confidence_too_low` MUST be returned (422) when confidence < threshold | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-ERR-003 | `semantic_abort_requested` MUST be returned (422) when orchestrator exits with ABORT | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-ERR-004 | `semantic_clarification_required` MUST be returned (202) when ASK_USER exit | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-ERR-005 | All semantic errors MUST include `envelope_hash` in response details | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-ERR-006 | `semantic_abort_requested` MUST include `AbortArtifact` in response body | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-ERR-007 | `semantic_clarification_required` MUST include `ClarificationRequest` in response body | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.2 Semantic Exit Handling (Added: 2026-01-13)

> **Source**: BRD-EXP-EXIT-001...005, BRD-EXP-ASK-001...004

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-SEM-EXIT-001 | ASK_USER exit MUST return HTTP 202 (Accepted) with pending input URL | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-EXIT-002 | ABORT exit MUST return HTTP 422 (Unprocessable Entity) with reason | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-EXIT-003 | PARTIAL_SUCCESS exit MUST return HTTP 200 with `status=partial_success` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-EXIT-004 | BUDGET_EXCEEDED exit MUST return HTTP 429 (Too Many Requests) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-SEM-EXIT-005 | All semantic exits MUST include `exit_state` field in response | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |

**Semantic Exit Response Schema**:


---

## 7. File Handling Requirements

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| GW-FILE-001 | Uploaded files MUST be staged in `observability/staging` directory | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-FILE-002 | Staging directories MUST be cleared before new uploads | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-FILE-003 | Output files MUST be served from `observability/<product>/<run_id>/output` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-FILE-004 | Run directories MUST include: `output`, `input`, `runtime`, `output` subdirectories | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-FILE-005 | Path traversal attacks MUST be prevented via path resolution validation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| GW-FILE-006 | Dataset candidates MUST be scanned from `products/data` and `products/<product>/data` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


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
