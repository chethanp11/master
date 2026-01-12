# Product System Technical Specification

> **Document ID**: PROD  
> **Version**: 1.0.0  
> **Status**: V1 Release  
> **Last Updated**: 2026-01-12

---

## 1. Overview

The product system provides a modular architecture for packaging domain-specific agents, 
tools, flows, and configurations into self-contained units. Products are auto-discovered 
and registered through a standardized manifest and registry pattern.

### 1.1 Implementation References

| Component | File |
|-----------|------|
| Product Schema | `core/contracts/flow_schema.py` |
| Product Catalog | `core/orchestrator/product_catalog.py` |
| Product Loader | `core/orchestrator/product_loader.py` |
| Product Runner | `core/orchestrator/product_runner.py` |
| Example: ADE | `products/ade/` |
| Example: Hello World | `products/hello_world/` |

---

## 2. Directory Structure Requirements

### 2.1 Product Directory Layout

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-DIR-001** | [V1] Each product MUST reside in `products/<product_name>/` directory | MUST |
| **PROD-DIR-002** | [V1] Product directory name MUST be lowercase with underscores (snake_case) | MUST |
| **PROD-DIR-003** | [V1] Product MUST contain a `manifest.yaml` file at root level | MUST |
| **PROD-DIR-004** | [V1] Product MUST contain a `registry.py` file at root level | MUST |
| **PROD-DIR-005** | [V1] Product MAY contain a `config/` directory for product-specific configuration | MAY |
| **PROD-DIR-006** | [V1] Product MAY contain a `data/` directory for sample data | MAY |
| **PROD-DIR-007** | [V1] Product MAY contain subdirectories for organization (agents, tools, prompts) | MAY |

**Example Structure**:
```
products/
└── ade/
    ├── manifest.yaml
    ├── registry.py
    ├── __init__.py
    ├── config/
    │   └── settings.yaml
    ├── agents/
    │   ├── __init__.py
    │   ├── planner.py
    │   └── executor.py
    ├── tools/
    │   ├── __init__.py
    │   ├── file_ops.py
    │   └── code_gen.py
    └── prompts/
        └── templates.yaml
```

**Implementation**: `products/*/`

---

## 3. Manifest Requirements

### 3.1 Core Manifest Schema

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-MAN-001** | [V1] Manifest MUST be a valid YAML file | MUST |
| **PROD-MAN-002** | [V1] Manifest MUST define `name` field (string, lowercase, matches directory) | MUST |
| **PROD-MAN-003** | [V1] Manifest MUST define `display_name` field (string, human-readable) | MUST |
| **PROD-MAN-004** | [V1] Manifest MUST define `version` field (string, semver format) | MUST |
| **PROD-MAN-005** | [V1] Manifest MUST define `description` field (string, product description) | MUST |
| **PROD-MAN-006** | [V1] Manifest MUST define `flows` list (at least one flow) | MUST |

**Implementation**: `products/*/manifest.yaml`

### 3.2 Flow Definition

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-MAN-010** | [V1] Each flow MUST define `name` field (unique within product) | MUST |
| **PROD-MAN-011** | [V1] Each flow MUST define `display_name` field | MUST |
| **PROD-MAN-012** | [V1] Each flow MUST define `entry_point` field (path to flow YAML) | MUST |
| **PROD-MAN-013** | [V1] Each flow MAY define `description` field | MAY |
| **PROD-MAN-014** | [V1] Each flow MAY define `default: true` (exactly one per product) | MAY |

**Implementation**: `products/*/manifest.yaml`

### 3.3 API Exposure

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-MAN-020** | [V1] Manifest MAY define `exposed_api` section | MAY |
| **PROD-MAN-021** | [V1] `exposed_api.enabled` MUST be boolean (default: true) | MUST |
| **PROD-MAN-022** | [V1] `exposed_api.require_auth` MAY specify authentication requirement | MAY |
| **PROD-MAN-023** | [V1] `exposed_api.rate_limit` MAY specify requests per minute limit | MAY |

**Implementation**: `products/*/manifest.yaml`

### 3.4 UI Configuration

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-MAN-030** | [V1] Manifest MAY define `ui` section for Streamlit customization | MAY |
| **PROD-MAN-031** | [V1] `ui.enabled` MUST be boolean (default: true) | MUST |
| **PROD-MAN-032** | [V1] `ui.intent_driven` MAY enable free-text intent input mode | MAY |
| **PROD-MAN-033** | [V1] `ui.intent_field` MUST specify payload field for intent (when intent_driven=true) | MUST |
| **PROD-MAN-034** | [V1] `ui.inputs` MAY define file upload configuration | MAY |
| **PROD-MAN-035** | [V1] `ui.inputs.enabled` MUST be boolean to enable file uploads | MUST |
| **PROD-MAN-036** | [V1] `ui.inputs.max_files` MAY limit number of uploadable files | MAY |
| **PROD-MAN-037** | [V1] `ui.inputs.allowed_extensions` MAY restrict allowed file types | MAY |
| **PROD-MAN-038** | [V1] `ui.dataset_candidates` MAY define paths to scan for data files | MAY |

**Implementation**: `products/*/manifest.yaml`

### 3.5 Manifest Schema Validation

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-MAN-040** | [V1] Manifest MUST be validated against `ProductManifest` Pydantic model | MUST |
| **PROD-MAN-041** | [V1] Invalid manifest MUST result in product load failure | MUST |
| **PROD-MAN-042** | [V1] Validation errors MUST include field path and error message | MUST |

**Implementation**: `core/contracts/flow_schema.py`

---

## 4. Registry Requirements

### 4.1 Registry Module

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-REG-001** | [V1] Each product MUST have a `registry.py` module | MUST |
| **PROD-REG-002** | [V1] Registry module MUST export `AgentRegistry` variable | MUST |
| **PROD-REG-003** | [V1] Registry module MUST export `ToolRegistry` variable | MUST |
| **PROD-REG-004** | [V1] Registries MUST be Dict[str, Callable] mapping names to factories | MUST |
| **PROD-REG-005** | [V1] Registries MUST NOT contain instantiated agents/tools (factories only) | MUST |

**Implementation**: `products/*/registry.py`

### 4.2 Auto-Discovery

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-REG-010** | [V1] ProductCatalog MUST auto-discover products in `products/` directory | MUST |
| **PROD-REG-011** | [V1] Discovery MUST skip directories without `manifest.yaml` | MUST |
| **PROD-REG-012** | [V1] Discovery MUST skip directories without `registry.py` | MUST |
| **PROD-REG-013** | [V1] Discovery MUST skip directories starting with `_` or `.` | MUST |
| **PROD-REG-014** | [V1] Discovery MUST respect `products.yaml` enabled/disabled settings | MUST |

**Implementation**: `core/orchestrator/product_catalog.py`

### 4.3 Registry Pattern

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-REG-020** | [V1] Agent factories MUST return subclass of `BaseAgent` | MUST |
| **PROD-REG-021** | [V1] Tool factories MUST return subclass of `BaseTool` | MUST |
| **PROD-REG-022** | [V1] Factory functions MUST accept no arguments or have default values | MUST |
| **PROD-REG-023** | [V1] Factory functions MUST be idempotent (safe to call multiple times) | MUST |
| **PROD-REG-024** | [V1] Factory functions MAY accept configuration Dict as optional argument | MAY |

**Implementation**: `products/*/registry.py`

---

## 5. Decorator Requirements

### 5.1 Agent Decorator

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-DEC-001** | [V1] `@agent(name="...")` decorator MUST register agent factory | MUST |
| **PROD-DEC-002** | [V1] Decorated class MUST be subclass of `BaseAgent` | MUST |
| **PROD-DEC-003** | [V1] Decorator MUST support `name` parameter for registry key | MUST |
| **PROD-DEC-004** | [V1] Decorator MUST support `description` parameter | MAY |
| **PROD-DEC-005** | [V1] Decorator MUST support `tags` parameter (list of strings) | MAY |

**Implementation**: `core/agents/base.py`

### 5.2 Tool Decorator

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-DEC-010** | [V1] `@tool(name="...")` decorator MUST register tool factory | MUST |
| **PROD-DEC-011** | [V1] Decorated class MUST be subclass of `BaseTool` | MUST |
| **PROD-DEC-012** | [V1] Decorator MUST support `name` parameter for registry key | MUST |
| **PROD-DEC-013** | [V1] Decorator MAY support `category` parameter for grouping | MAY |
| **PROD-DEC-014** | [V1] Decorator MAY support `requires_approval` parameter | MAY |

**Implementation**: `core/tools/base.py`

---

## 6. Product Catalog Requirements

### 6.1 Catalog Operations

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-CAT-001** | [V1] ProductCatalog MUST provide `list_products()` returning all discovered products | MUST |
| **PROD-CAT-002** | [V1] ProductCatalog MUST provide `get_product(name)` returning single product | MUST |
| **PROD-CAT-003** | [V1] ProductCatalog MUST provide `get_flows(product)` returning product flows | MUST |
| **PROD-CAT-004** | [V1] ProductCatalog MUST provide `get_agent_registry(product)` returning agents | MUST |
| **PROD-CAT-005** | [V1] ProductCatalog MUST provide `get_tool_registry(product)` returning tools | MUST |

**Implementation**: `core/orchestrator/product_catalog.py`

### 6.2 Product State

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-CAT-010** | [V1] Each product MUST have state: `enabled`, `disabled`, `error` | MUST |
| **PROD-CAT-011** | [V1] Products disabled in `products.yaml` MUST have state `disabled` | MUST |
| **PROD-CAT-012** | [V1] Products that fail to load MUST have state `error` with message | MUST |
| **PROD-CAT-013** | [V1] Error products MUST include `error_path` and `error_message` | MUST |

**Implementation**: `core/orchestrator/product_catalog.py`

### 6.3 Caching

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-CAT-020** | [V1] ProductCatalog MUST cache discovery results | MUST |
| **PROD-CAT-021** | [V1] Cache MUST be invalidated on explicit refresh | MUST |
| **PROD-CAT-022** | [V1] Registry imports MUST be cached per product | MUST |

**Implementation**: `core/orchestrator/product_catalog.py`

---

## 7. Product Loader Requirements

### 7.1 Loading Process

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-LOAD-001** | [V1] ProductLoader MUST load manifest from `products/<name>/manifest.yaml` | MUST |
| **PROD-LOAD-002** | [V1] ProductLoader MUST import registry from `products.<name>.registry` | MUST |
| **PROD-LOAD-003** | [V1] ProductLoader MUST validate manifest against schema | MUST |
| **PROD-LOAD-004** | [V1] ProductLoader MUST verify all flow entry_points exist | MUST |
| **PROD-LOAD-005** | [V1] ProductLoader MUST raise `ProductLoadError` on failure | MUST |

**Implementation**: `core/orchestrator/product_loader.py`

### 7.2 Flow Resolution

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-LOAD-010** | [V1] Flow entry_point MUST be resolved relative to product directory | MUST |
| **PROD-LOAD-011** | [V1] Missing flow file MUST raise `FlowNotFoundError` | MUST |
| **PROD-LOAD-012** | [V1] Flow YAML MUST be validated against flow schema | MUST |

**Implementation**: `core/orchestrator/flow_loader.py`

---

## 8. Product Runner Requirements

### 8.1 Execution Context

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-RUN-001** | [V1] ProductRunner MUST create isolated execution context per run | MUST |
| **PROD-RUN-002** | [V1] Execution context MUST include product-specific agent registry | MUST |
| **PROD-RUN-003** | [V1] Execution context MUST include product-specific tool registry | MUST |
| **PROD-RUN-004** | [V1] Execution context MUST merge core + product registries | MUST |
| **PROD-RUN-005** | [V1] Product registry entries MUST override core entries with same name | MUST |

**Implementation**: `core/orchestrator/product_runner.py`

### 8.2 Resource Isolation

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-RUN-010** | [V1] Each run MUST have isolated observability directory: `observability/<product>/<run_id>/` | MUST |
| **PROD-RUN-011** | [V1] Product runs MUST NOT access other products' observability directories | MUST |
| **PROD-RUN-012** | [V1] Product configuration MUST be loaded in isolation from other products | MUST |

**Implementation**: `core/orchestrator/product_runner.py`, `core/memory/observability_store.py`

---

## 9. Product Configuration Requirements

### 9.1 Configuration Loading

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-CFG-001** | [V1] Product-specific config MUST be loaded from `products/<name>/config/` | MUST |
| **PROD-CFG-002** | [V1] Product config MUST NOT override global `configs/` settings | MUST |
| **PROD-CFG-003** | [V1] Product config MAY provide product-specific model/policy overrides | MAY |
| **PROD-CFG-004** | [V1] Missing product config directory MUST NOT cause load failure | MUST |

**Implementation**: `core/config/loader.py`

---

## 10. Products.yaml Requirements

### 10.1 Global Product Settings

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-YAML-001** | [V1] `configs/products.yaml` MUST define global product settings | MUST |
| **PROD-YAML-002** | [V1] Each product MAY have `enabled: true/false` setting | MAY |
| **PROD-YAML-003** | [V1] Products not listed MUST default to `enabled: true` | MUST |
| **PROD-YAML-004** | [V1] Products with `enabled: false` MUST be excluded from catalog | MUST |

**Implementation**: `configs/products.yaml`, `core/orchestrator/product_catalog.py`

---

## 11. Example Products

### 11.1 Hello World Product

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-HW-001** | [V1] `hello_world` product MUST serve as minimal reference implementation | MUST |
| **PROD-HW-002** | [V1] `hello_world` MUST demonstrate: manifest, registry, single flow | MUST |
| **PROD-HW-003** | [V1] `hello_world` flow MUST execute without external dependencies | MUST |

**Implementation**: `products/hello_world/`

### 11.2 ADE Product

| ID | Requirement | Level |
|----|-------------|-------|
| **PROD-ADE-001** | [V1] `ade` product MUST demonstrate advanced product patterns | MUST |
| **PROD-ADE-002** | [V1] `ade` MUST demonstrate: multi-flow, custom agents, custom tools | MUST |
| **PROD-ADE-003** | [V1] `ade` MUST demonstrate: UI configuration, file inputs | MUST |

**Implementation**: `products/ade/`

---

## 12. Future Considerations

### 12.1 V1.1 Enhancements

| ID | Feature | Description |
|----|---------|-------------|
| **PROD-FUTURE-001** | Hot reload | Reload products without restart |
| **PROD-FUTURE-002** | Product dependencies | Declare inter-product dependencies |
| **PROD-FUTURE-003** | Version constraints | Define min/max platform version |

### 12.2 V2 Features

| ID | Feature | Description |
|----|---------|-------------|
| **PROD-FUTURE-010** | Plugin marketplace | External product installation |
| **PROD-FUTURE-011** | Product templates | Scaffolding for new products |
| **PROD-FUTURE-012** | Multi-tenancy | Per-tenant product isolation |

---

## 13. Traceability Matrix

| Requirement | Implementation | Test |
|-------------|----------------|------|
| PROD-DIR-001 | `products/*/` | `tests/unit/products/test_structure.py` |
| PROD-MAN-001 | `products/*/manifest.yaml` | `tests/unit/products/test_manifest.py` |
| PROD-REG-001 | `products/*/registry.py` | `tests/unit/products/test_registry.py` |
| PROD-CAT-001 | `core/orchestrator/product_catalog.py` | `tests/unit/core/test_product_catalog.py` |
| PROD-LOAD-001 | `core/orchestrator/product_loader.py` | `tests/unit/core/test_product_loader.py` |
| PROD-RUN-001 | `core/orchestrator/product_runner.py` | `tests/unit/core/test_product_runner.py` |
