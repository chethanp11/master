# Test Organization

This directory contains the core test suite for the master framework.
Product-specific tests live in their respective product directories.

## Directory Structure

```
tests/
├── conftest.py              # Shared fixtures for core tests
├── acceptance_intelligence/ # Intelligence capability acceptance tests
├── architecture/            # Architecture invariant tests
├── core/                    # Core framework tests
├── integration/             # Core integration tests
└── unit/                    # Core unit tests

products/*/tests/            # Product-specific tests
├── conftest.py              # Product fixtures
├── integration/             # Product integration tests
└── unit/                    # Product unit tests
```

## Test Categories

### Core Tests (`tests/`)

Tests for the core framework components:

| Directory | Purpose |
|-----------|---------|
| `acceptance_intelligence/` | Validate intelligence capabilities work end-to-end |
| `architecture/` | Enforce architectural invariants and guardrails |
| `core/` | Test core modules (orchestrator, memory, governance) |
| `integration/` | Cross-module integration scenarios |
| `unit/` | Isolated unit tests for utilities and helpers |

### Product Tests (`products/*/tests/`)

Each product has its own test directory following the same structure:
- `unit/` - Isolated component tests
- `integration/` - Full product flow tests

Products maintain ownership of their test suites, enabling:
- Clear responsibility boundaries
- Parallel test execution by product
- Independent test evolution

## Running Tests

```bash
# Run all core tests
pytest tests/ -v

# Run all product tests
pytest products/*/tests/ -v

# Run everything
pytest tests/ products/*/tests/ -v

# Run only unit tests (fast)
pytest tests/unit/ products/*/tests/unit/ -v

# Run only integration tests
pytest -m integration -v

# Run tests for a specific product
pytest products/ade/tests/ -v

# Collect tests without running (verify discovery)
pytest tests/ --collect-only
pytest products/*/tests/ --collect-only
```

## Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.integration` | Integration tests (may be slower) |
| `@pytest.mark.slow` | Particularly slow tests |
| `@pytest.mark.acceptance` | Acceptance/behavior tests |

## Test Ownership

| Test Location | Owner | Scope |
|---------------|-------|-------|
| `tests/` | Core team | Framework behavior, architectural invariants |
| `products/ade/tests/` | ADE team | ADE-specific flows, tools, agents |
| `products/hello_world/tests/` | Core team | Reference implementation tests |

## CI Configuration

Tests run in parallel by category:
1. **Core unit tests** - Fast, run first
2. **Core integration tests** - Medium speed
3. **Product tests** - Run in parallel per product
4. **Architecture tests** - Blocking guardrails

## Adding Tests

### For Core Changes
Add tests to `tests/` following existing patterns.

### For Product Changes
Add tests to `products/<name>/tests/`:
1. Use the product's `conftest.py` fixtures
2. Follow the product's test conventions
3. Mark integration tests with `@pytest.mark.integration`

## Best Practices

1. **Isolation**: Tests should not depend on external state
2. **Speed**: Prefer unit tests; use integration tests sparingly
3. **Clarity**: Test names should describe the scenario
4. **Fixtures**: Use shared fixtures from conftest.py
5. **Cleanup**: Always clean up resources (files, DB entries)
6. **Determinism**: Tests must produce the same result every run
