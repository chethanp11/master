# Product System Technical Specification

> **Document ID**: PROD  
> **Version**: V1.2  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-13  

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-12 | Initial V1 specification |
| 1.1.0 | 2026-01-13 | Added: §12.3 Semantic Adapter Isolation, §13 Explicit Non-Goals, §16 BRD Requirement Mapping |
| V1.2 | 2026-01-20 | Normalized tables to canonical TSD format; merged/removed non-TSD sections; mapping hygiene |

---

## 1. Overview

The product system provides a modular architecture for packaging domain-specific agents, 
tools, flows, and configurations into self-contained units. Products are auto-discovered 
and registered through a standardized manifest and registry pattern.

## 2. Directory Structure Requirements

### 2.1 Product Directory Layout

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-DIR-001 | Each product MUST reside in `products/<product_name>/` directory | MUST | BRD-EXP-030 | 1.1 | 13 Jan 2026 | — |
| PROD-DIR-002 | Product directory name MUST be lowercase with underscores (snake_case) | MUST | BRD-EXP-030 | 1.1 | 13 Jan 2026 | — |
| PROD-DIR-003 | Product MUST contain a `manifest.yaml` file at root level | MUST | BRD-EXP-030 | 1.1 | 13 Jan 2026 | — |
| PROD-DIR-004 | Product MUST contain a `registry.py` file at root level | MUST | BRD-EXP-030 | 1.1 | 13 Jan 2026 | — |
| PROD-DIR-005 | Product MAY contain a `config/` directory for product-specific configuration | MAY | BRD-EXP-030 | 1.1 | 13 Jan 2026 | — |
| PROD-DIR-006 | Product MAY contain a `data/` directory for sample data | MAY | BRD-EXP-030 | 1.1 | 13 Jan 2026 | — |
| PROD-DIR-007 | Product MAY contain subdirectories for organization (agents, tools, prompts) | MAY | BRD-EXP-030 | 1.1 | 13 Jan 2026 | — |

---

## 3. Manifest Requirements

### 3.1 Core Manifest Schema

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-MAN-001 | Manifest MUST be a valid YAML file | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-002 | Manifest MUST define `name` field (string, lowercase, matches directory) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-003 | Manifest MUST define `display_name` field (string, human-readable) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-004 | Manifest MUST define `version` field (string, semver format) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-005 | Manifest MUST define `description` field (string, product description) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-006 | Manifest MUST define `flows` list (at least one flow) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |


### 3.2 Flow Definition

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-MAN-010 | Each flow MUST define `name` field (unique within product) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-011 | Each flow MUST define `display_name` field | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-012 | Each flow MUST define `entry_point` field (path to flow YAML) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-013 | Each flow MAY define `description` field | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-014 | Each flow MAY define `default: true` (exactly one per product) | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |


### 3.3 API Exposure

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-MAN-020 | Manifest MAY define `exposed_api` section | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-021 | `exposed_api.enabled` MUST be boolean (default: true) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-022 | `exposed_api.require_auth` MAY specify authentication requirement | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-023 | `exposed_api.rate_limit` MAY specify requests per minute limit | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |


### 3.4 UI Configuration

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-MAN-030 | Manifest MAY define `ui` section for Streamlit customization | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-031 | `ui.enabled` MUST be boolean (default: true) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-032 | `ui.intent_driven` MAY enable free-text intent input mode | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-033 | `ui.intent_field` MUST specify payload field for intent (when intent_driven=true) | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-034 | `ui.inputs` MAY define file upload configuration | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-035 | `ui.inputs.enabled` MUST be boolean to enable file uploads | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-036 | `ui.inputs.max_files` MAY limit number of uploadable files | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-037 | `ui.inputs.allowed_extensions` MAY restrict allowed file types | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-038 | `ui.dataset_candidates` MAY define paths to scan for data files | MAY | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |


### 3.5 Manifest Schema Validation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-MAN-040 | Manifest MUST be validated against `ProductManifest` Pydantic model | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-041 | Invalid manifest MUST result in product load failure | MUST | BRD-EXP-031 | 1.1 | 13 Jan 2026 | — |
| PROD-MAN-042 | Validation errors MUST include field path and error message | MUST | BRD-EXP-031, BRD-EXP-052 | 1.1 | 13 Jan 2026 | — |


---

## 4. Registry Requirements

### 4.1 Registry Module

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-REG-001 | Each product MUST have a `registry.py` module | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-REG-002 | Registry module MUST export `AgentRegistry` variable | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-REG-003 | Registry module MUST export `ToolRegistry` variable | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-REG-004 | Registries MUST be Dict[str, Callable] mapping names to factories | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-REG-005 | Registries MUST NOT contain instantiated agents/tools (factories only) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 4.2 Auto-Discovery

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-REG-010 | ProductCatalog MUST auto-discover products in `products/` directory | MUST | BRD-AUTO-ADAPT-007, BRD-EXP-032 | 1.1 | 13 Jan 2026 | — |
| PROD-REG-011 | Discovery MUST skip directories without `manifest.yaml` | MUST | BRD-AUTO-ADAPT-007, BRD-EXP-032 | 1.1 | 13 Jan 2026 | — |
| PROD-REG-012 | Discovery MUST skip directories without `registry.py` | MUST | BRD-AUTO-ADAPT-007, BRD-EXP-032 | 1.1 | 13 Jan 2026 | — |
| PROD-REG-013 | Discovery MUST skip directories starting with `_` or `.` | MUST | BRD-AUTO-ADAPT-007, BRD-EXP-032 | 1.1 | 13 Jan 2026 | — |
| PROD-REG-014 | Discovery MUST respect `products.yaml` enabled/disabled settings | MUST | BRD-AUTO-ADAPT-007, BRD-EXP-032 | 1.1 | 13 Jan 2026 | — |


### 4.3 Registry Pattern

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-REG-020 | Agent factories MUST return subclass of `BaseAgent` | MUST | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |
| PROD-REG-021 | Tool factories MUST return subclass of `BaseTool` | MUST | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |
| PROD-REG-022 | Factory functions MUST accept no arguments or have default values | MUST | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |
| PROD-REG-023 | Factory functions MUST be idempotent (safe to call multiple times) | MUST | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |
| PROD-REG-024 | Factory functions MAY accept configuration Dict as optional argument | MAY | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |


---

## 5. Decorator Requirements

### 5.1 Agent Decorator

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-DEC-001 | `@agent(name="...")` decorator MUST register agent factory | MUST | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |
| PROD-DEC-002 | Decorated class MUST be subclass of `BaseAgent` | MUST | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |
| PROD-DEC-003 | Decorator MUST support `name` parameter for registry key | MUST | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |
| PROD-DEC-004 | Decorator MUST support `description` parameter | MAY | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |
| PROD-DEC-005 | Decorator MUST support `tags` parameter (list of strings) | MAY | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |


### 5.2 Tool Decorator

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-DEC-010 | `@tool(name="...")` decorator MUST register tool factory | MUST | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |
| PROD-DEC-011 | Decorated class MUST be subclass of `BaseTool` | MUST | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |
| PROD-DEC-012 | Decorator MUST support `name` parameter for registry key | MUST | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |
| PROD-DEC-013 | Decorator MAY support `category` parameter for grouping | MAY | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |
| PROD-DEC-014 | Decorator MAY support `requires_approval` parameter | MAY | BRD-EXP-036 | 1.1 | 13 Jan 2026 | — |


---

## 6. Product Catalog Requirements

### 6.1 Catalog Operations

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-CAT-001 | ProductCatalog MUST provide `list_products()` returning all discovered products | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-CAT-002 | ProductCatalog MUST provide `get_product(name)` returning single product | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-CAT-003 | ProductCatalog MUST provide `get_flows(product)` returning product flows | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-CAT-004 | ProductCatalog MUST provide `get_agent_registry(product)` returning agents | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-CAT-005 | ProductCatalog MUST provide `get_tool_registry(product)` returning tools | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 6.2 Product State

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-CAT-010 | Each product MUST have state: `enabled`, `disabled`, `error` | MUST | BRD-EXP-033, BRD-EXP-042 | 1.1 | 13 Jan 2026 | — |
| PROD-CAT-011 | Products disabled in `products.yaml` MUST have state `disabled` | MUST | BRD-EXP-033, BRD-EXP-042 | 1.1 | 13 Jan 2026 | — |
| PROD-CAT-012 | Products that fail to load MUST have state `error` with message | MUST | BRD-EXP-033, BRD-EXP-034, BRD-EXP-042 | 1.1 | 13 Jan 2026 | — |
| PROD-CAT-013 | Error products MUST include `error_path` and `error_message` | MUST | BRD-EXP-033, BRD-EXP-034, BRD-EXP-042 | 1.1 | 13 Jan 2026 | — |


### 6.3 Caching

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-CAT-020 | ProductCatalog MUST cache discovery results | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-CAT-021 | Cache MUST be invalidated on explicit refresh | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-CAT-022 | Registry imports MUST be cached per product | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 7. Product Loader Requirements

### 7.1 Loading Process

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-LOAD-001 | ProductLoader MUST load manifest from `products/<name>/manifest.yaml` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-LOAD-002 | ProductLoader MUST import registry from `products.<name>.registry` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-LOAD-003 | ProductLoader MUST validate manifest against schema | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-LOAD-004 | ProductLoader MUST verify all flow entry_points exist | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-LOAD-005 | ProductLoader MUST raise `ProductLoadError` on failure | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 7.2 Flow Resolution

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-LOAD-010 | Flow entry_point MUST be resolved relative to product directory | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-LOAD-011 | Missing flow file MUST raise `FlowNotFoundError` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-LOAD-012 | Flow YAML MUST be validated against flow schema | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 8. Product Runner Requirements

### 8.1 Execution Context

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-RUN-001 | ProductRunner MUST create isolated execution context per run | MUST | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |
| PROD-RUN-002 | Execution context MUST include product-specific agent registry | MUST | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |
| PROD-RUN-003 | Execution context MUST include product-specific tool registry | MUST | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |
| PROD-RUN-004 | Execution context MUST merge core + product registries | MUST | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |
| PROD-RUN-005 | Product registry entries MUST override core entries with same name | MUST | BRD-EXP-040 | 1.1 | 13 Jan 2026 | — |


### 8.2 Resource Isolation

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-RUN-010 | Each run MUST have isolated observability directory: `observability/<product>/<run_id>/` | MUST | BRD-EXP-041 | 1.1 | 13 Jan 2026 | — |
| PROD-RUN-011 | Product runs MUST NOT access other products' observability directories | MUST | BRD-EXP-041 | 1.1 | 13 Jan 2026 | — |
| PROD-RUN-012 | Product configuration MUST be loaded in isolation from other products | MUST | BRD-EXP-041 | 1.1 | 13 Jan 2026 | — |


---

## 9. Product Semantic Adapter Requirements

### 9.1 Semantic Adapter Interface

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-SEM-001 | Products MAY provide a `ProductSemanticAdapter` class in `products/<name>/semantic.py` | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-002 | If provided, `ProductSemanticAdapter` MUST implement `interpret(context) -> SemanticEnvelope` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-003 | If provided, `ProductSemanticAdapter` MUST implement `validate(envelope, context) -> ValidationResult` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-004 | Products without adapter MUST use core default interpretation (passthrough + heuristics) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-005 | Orchestrator MUST call adapter via product router; adapters MUST NOT import orchestrator internals | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 9.2 Interpret Hook

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-SEM-INT-001 | `interpret(context)` MUST receive: `raw_input`, `payload`, `product_config` | MUST | BRD-AUTO-025, BRD-AUTO-ADAPT-001 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-INT-002 | `interpret` MUST return a fully populated `SemanticEnvelope` | MUST | BRD-AUTO-025, BRD-AUTO-ADAPT-001, BRD-AUTO-ADAPT-002 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-INT-003 | `interpret` MUST set `intent_type` from product-defined intent taxonomy | MUST | BRD-AUTO-025, BRD-AUTO-ADAPT-001, BRD-AUTO-ADAPT-006 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-INT-004 | `interpret` MUST extract domain-specific entities (e.g., chart types, metrics, filters) | MUST | BRD-AUTO-025, BRD-AUTO-ADAPT-001, BRD-AUTO-ADAPT-004, BRD-AUTO-ADAPT-005 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-INT-005 | `interpret` MUST NOT call tools or agents directly | MUST | BRD-AUTO-025, BRD-AUTO-ADAPT-001, BRD-AUTO-ADAPT-008 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-INT-006 | `interpret` MUST NOT import `core/orchestrator/*` internals | MUST | BRD-AUTO-ADAPT-009 | 1.1 | 13 Jan 2026 | — |


### 9.3 Validate Hook

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-SEM-VAL-001 | `validate(envelope, context)` MUST check domain-specific constraints | MUST | BRD-AUTO-026, BRD-AUTO-ADAPT-003 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-VAL-002 | `validate` MUST return `ValidationResult` with all required fields | MUST | BRD-AUTO-026, BRD-AUTO-ADAPT-003 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-VAL-003 | `validate` MAY adjust `revised_confidence` based on validation findings | MAY | BRD-AUTO-026, BRD-AUTO-ADAPT-003 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-VAL-004 | `validate` MAY generate a `clarifying_question` when input is ambiguous | MAY | BRD-AUTO-026, BRD-AUTO-ADAPT-003 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-VAL-005 | `validate` MUST NOT call tools or agents directly | MUST | BRD-AUTO-026, BRD-AUTO-ADAPT-003 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-VAL-006 | `validate` MUST NOT import `core/orchestrator/*` internals | MUST | BRD-GOV-027 | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-VAL-007 | Domain rules (e.g., "trend chart requires time axis") MUST be in product adapter, not core | MUST | BRD-GOV-027 | 1.1 | 13 Jan 2026 | — |


---

## 10. Product Configuration Requirements

### 10.1 Configuration Loading

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-CFG-001 | Product-specific config MUST be loaded from `products/<name>/config/` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-CFG-002 | Product config MUST NOT override global `configs/` settings | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-CFG-003 | Product config MAY provide product-specific model/policy overrides | MAY | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-CFG-004 | Missing product config directory MUST NOT cause load failure | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 11. Products.yaml Requirements

### 11.1 Global Product Settings

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-YAML-001 | `configs/products.yaml` MUST define global product settings | MUST | BRD-EXP-033 | 1.1 | 13 Jan 2026 | — |
| PROD-YAML-002 | Each product MAY have `enabled: true/false` setting | MAY | BRD-EXP-033 | 1.1 | 13 Jan 2026 | — |
| PROD-YAML-003 | Products not listed MUST default to `enabled: true` | MUST | BRD-EXP-033 | 1.1 | 13 Jan 2026 | — |
| PROD-YAML-004 | Products with `enabled: false` MUST be excluded from catalog | MUST | BRD-EXP-033 | 1.1 | 13 Jan 2026 | — |


---

## 12. Example Products

### 12.1 Hello World Product

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-HW-001 | `hello_world` product MUST serve as minimal reference implementation | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-HW-002 | `hello_world` MUST demonstrate: manifest, registry, single flow | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-HW-003 | `hello_world` flow MUST execute without external dependencies | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 12.2 ADE Product

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-ADE-001 | `ade` product MUST demonstrate advanced product patterns | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-ADE-002 | `ade` MUST demonstrate: multi-flow, custom agents, custom tools | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-ADE-003 | `ade` MUST demonstrate: UI configuration, file inputs | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


### 12.3 Semantic Adapter Isolation (Added: 2026-01-13)

> **Source**: BRD-AUTO-ADAPT-001...010, INV-6, INV-10

| TSD ID | Technical Specification | Level | BRD Mapping (BRD ID) | Version | Date added | Notes |
|--------|--------------------------|-------|----------------------|---------|------------|-------|
| PROD-SEM-ISO-001 | Product semantic adapter MUST be imported via dynamic import, not static | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-ISO-002 | Adapter module MUST NOT import `core.orchestrator.*` (enforced by arch test) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-ISO-003 | Adapter MUST NOT hold state between calls; all state in SemanticEnvelope | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-ISO-004 | Adapter MUST NOT call LLM directly; use `advisory_service` if reasoning needed | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-ISO-005 | Adapter MUST NOT access other products' data or configuration | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-ISO-006 | Adapter failures MUST NOT crash orchestrator; return `SemanticEnvelope` with `confidence=0.0` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-ISO-007 | Adapter MUST receive only: `raw_input`, `payload`, `product_config` | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-ISO-008 | Adapter MUST NOT have network access; all external calls via registered tools | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-ISO-009 | Adapter execution timeout MUST be enforced (default: 5s) | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |
| PROD-SEM-ISO-010 | Adapter MUST emit `product_adapter_invoked` trace event | MUST | TBD (Mapping Gap) | 1.1 | 13 Jan 2026 | — |


---

## 13. Explicit Non-Goals (Added: 2026-01-13)

> **Product System MUST NOT**:

| Non-Goal | Rationale | Violation Example |
|----------|-----------|-------------------|
| Cross-product data access | Product isolation is mandatory | Product A reads Product B's files |
| Direct orchestrator import in adapters | Dependency inversion principle | `from core.orchestrator import engine` |
| Stateful adapters | Reproducibility requires statelessness | Adapter caches between runs |
| Direct LLM calls from adapters | Intelligence must go through advisory | Adapter calls OpenAI directly |
| Network access from adapters | Security and auditability | Adapter makes HTTP requests |
| Control flow in adapters | Adapters interpret, don't execute | Adapter calls tools |

---
