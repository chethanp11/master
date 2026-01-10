# Pydantic Usage Rules

We use Pydantic for strict boundary validation only. Internal plumbing should stay lightweight.

MUST use Pydantic for:
- Tool inputs/outputs
- Agent inputs/outputs
- Run state persisted structures (RunRecord, StepRecord, etc.)
- Trace events that cross module boundaries
- Configs/policies loaded externally

SHOULD NOT use Pydantic for:
- Step-local ephemeral working variables
- Intermediate derived values within a single function scope
- Internal aggregation objects that never cross boundaries
