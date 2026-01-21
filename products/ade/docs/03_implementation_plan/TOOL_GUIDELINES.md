# ADE Tool Development Guidelines

## Overview

This document defines the development guidelines for tools in the Analytical Decision Engine (ADE).
All tools must comply with these guidelines to ensure deterministic behavior, security, and
maintainability.

## TS-TOOL-GEN-007: Network Dependency Restrictions

### Policy

**Tools must not import or use external network libraries.**

The following imports are forbidden in all tool modules:
- `requests`
- `httpx`
- `urllib`
- `urllib3`
- `aiohttp`
- `http.client`
- `socket` (for network operations)

### Rationale

1. **Determinism**: External network calls introduce non-determinism that makes testing and
   reproducibility difficult.

2. **Security**: Tools should not have the ability to make arbitrary network requests, which
   could lead to data exfiltration or uncontrolled API usage.

3. **Cost Control**: Uncontrolled network calls can incur unexpected costs, especially with
   paid APIs.

4. **Isolation**: Tools should operate on data provided through their input parameters, not
   fetch additional data at runtime.

### Enforcement

1. **CI Check**: A static grep check runs on every PR:
   ```bash
   grep -r "import requests\|import urllib\|import httpx" products/ade/tools/
   ```
   The check must return empty (no matches).

2. **Unit Test**: The `test_tool_dependencies.py` test file uses AST parsing to verify no
   forbidden imports exist in tool modules.

3. **Code Review**: Reviewers should verify that no network calls are made, even through
   indirect means.

### Allowed Alternatives

If a tool needs external data:

1. **Pre-fetch at orchestrator level**: Data should be fetched by the orchestrator or a
   dedicated data ingestion step, then passed to tools.

2. **Use framework primitives**: For LLM calls, use the `core.models.router` which is
   governed by budgets and policies.

3. **Local file operations**: Tools may read from local files (within the product boundary)
   that were populated by earlier pipeline steps.

## General Tool Guidelines

### Input/Output

- All tools must define Pydantic schemas for input and output
- Use `ConfigDict(extra="forbid")` to reject unexpected fields
- Document all fields with descriptions

### Side Effects

- Tools marked `read_only=True` must not modify any state
- Tools marked `side_effect=False` must not cause observable effects outside the tool

### Error Handling

- Raise appropriate exceptions with clear messages
- Use `ToolError` with proper `ToolErrorCode` for structured errors
- Never silently ignore errors

### Testing

- Every tool must have corresponding unit tests
- Tests should cover: valid inputs, invalid inputs, edge cases
- Test the standalone function first, then the tool class

### Performance

- Tools should complete in reasonable time (< 30 seconds for most operations)
- Use streaming or chunking for large data operations
- Document expected performance characteristics

## Version Control

This document is versioned with the ADE product. Changes require:
1. Update to this document
2. Corresponding test updates
3. Review and approval
