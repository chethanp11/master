# ADE Product Tests

This directory contains tests specific to the ADE (Analytical Decision Engine) product.

## Test Organization

```
products/ade/tests/
├── conftest.py              # Shared fixtures for ADE tests
├── test_smoke.py            # Quick smoke tests for ADE
├── integration/             # Integration tests (full flow execution)
│   ├── test_ade_evidence_bundle.py    # Evidence bundle assembly
│   ├── test_ade_hitl.py               # Human-in-the-loop workflows
│   ├── test_ade_orchestrator_flow.py  # Full orchestrator flow
│   ├── test_ade_v1.py                 # ADE v1 flow validation
│   ├── test_business_report_html.py   # HTML report generation
│   └── test_business_report_quality.py # Report quality checks
└── unit/                    # Unit tests (isolated component tests)
    ├── test_assemble_decision_packet.py
    ├── test_chart_type_guardrails.py
    ├── test_demo_data_reader.py
    ├── test_detect_anomalies_rules.py
    ├── test_driver_analysis.py
    ├── test_hypothesis_tools.py
    ├── test_product_catalog_ade.py
    ├── test_stub_payload.py
    └── test_sufficiency_evaluator.py
```

## Test Categories

### Unit Tests (`unit/`)
- Test individual tools and agents in isolation
- No external dependencies or full flow execution
- Fast execution, suitable for TDD workflow

### Integration Tests (`integration/`)
- Test complete ADE flows end-to-end
- Require orchestrator and product registration
- Validate real-world scenarios including HITL

## Running Tests

```bash
# Run all ADE tests
pytest products/ade/tests/ -v

# Run only unit tests
pytest products/ade/tests/unit/ -v

# Run only integration tests
pytest products/ade/tests/integration/ -v -m integration

# Run with coverage
pytest products/ade/tests/ --cov=products/ade --cov-report=term-missing
```

## Fixtures

The `conftest.py` provides these fixtures:

| Fixture | Description |
|---------|-------------|
| `ade_product_path` | Path to ADE product root |
| `ade_test_data_path` | Path to ADE data directory |
| `ade_flows_path` | Path to ADE flows directory |
| `ade_staging_path` | Temporary staging directory |
| `sample_csv_data` | Sample CSV content for tests |
| `sample_csv_file` | Sample CSV file in staging |

## Test Data

Test data files should be placed in `products/ade/data/` and accessed
via the `ade_test_data_path` fixture. Do not hardcode paths.

## Adding New Tests

1. **Unit tests**: Add to `unit/` with naming `test_<component>.py`
2. **Integration tests**: Add to `integration/` with `@pytest.mark.integration`
3. Use fixtures from `conftest.py` for consistent setup
4. Follow existing test patterns for consistency
