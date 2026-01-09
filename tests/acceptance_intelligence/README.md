# Intelligence Acceptance Tests

This suite locks in platform-level invariants for the “intelligence upgrade” workflow samples.

- `test_intelligence_acceptance.py` exercises determinism, pause/resume, governance denial, trace emission, and plan proposal baselines through black-box orchestrator runs.
- Tests live under `tests/acceptance_intelligence` and rely only on helpers defined here.

Run the suite with `pytest tests/acceptance_intelligence` (or target specific tests with `-k`).
