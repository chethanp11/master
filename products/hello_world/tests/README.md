# Hello World Product Tests

This directory contains tests specific to the hello_world reference product.

## Test Organization

```
products/hello_world/tests/
├── conftest.py              # Shared fixtures for hello_world tests
└── test_hello_world_flow.py # Flow execution tests
```

## Purpose

The hello_world product serves as a reference implementation demonstrating:
- Minimal product structure
- Basic agent and tool registration
- Simple flow execution

Tests here validate that the reference implementation works correctly
and can serve as a template for new products.

## Running Tests

```bash
# Run all hello_world tests
pytest products/hello_world/tests/ -v

# Run with coverage
pytest products/hello_world/tests/ --cov=products/hello_world --cov-report=term-missing
```

## Fixtures

The `conftest.py` provides these fixtures:

| Fixture | Description |
|---------|-------------|
| `hello_world_product_path` | Path to hello_world product root |
| `hello_world_flows_path` | Path to hello_world flows directory |
| `hello_world_staging_path` | Temporary staging directory |

## Adding New Tests

1. Follow the existing test patterns
2. Use fixtures from `conftest.py` for consistent setup
3. Keep tests simple - this is a reference implementation
