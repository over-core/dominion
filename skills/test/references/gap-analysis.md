# Gap Analysis

Identify test coverage gaps in phase changes.

## Identify Changed Files

1. Read all SUMMARY.md files from `.dominion/phases/{N}/summaries/`
2. Collect the "Files Changed" sections — build a complete list of modified files
3. Cross-reference with git diff if summaries are incomplete

## Find Corresponding Tests

For each changed source file, find its test file using language conventions:
- Rust: `src/foo.rs` → `tests/foo.rs` or `src/foo.rs` (inline `#[cfg(test)]`)
- Python: `src/foo.py` → `tests/test_foo.py` or `tests/foo_test.py`
- JavaScript/TypeScript: `src/foo.ts` → `src/foo.test.ts` or `__tests__/foo.test.ts`
- Go: `foo.go` → `foo_test.go`

## Check Coverage

For each changed file:
1. Does a corresponding test file exist?
2. If yes, do the tests cover the new/modified code paths?
3. Use Grep to check if new functions/methods have test cases

## HRBT-Based Severity

Replace static severity heuristics with risk-based classification from Researcher's HRBT matrix:

1. Read `.dominion/phases/{N}/research.toml` — find HRBT risk entries per component
2. For each gap, determine the component's HRBT risk level:
   - **High risk** (HRBT): untested code in high-risk components — severity "high" regardless of code type
   - **Medium risk** (HRBT): untested code in medium-risk components — severity "medium"
   - **Low risk** (HRBT): untested code in low-risk components — severity "low"
3. If no HRBT data available, fall back to static heuristics:
   - High: security-related code, data validation, authentication/authorization, error handling
   - Medium: business logic, API endpoints, state transitions
   - Low: display/formatting, logging, comments-only changes

## Test Layer Classification

For each gap, identify which test layer is missing:
- `unit` — isolated function/method testing
- `integration` — module boundary / service interaction testing
- `property` — invariant-based generative testing
- `adversarial` — malformed input, resource exhaustion, race conditions

## Fragility Assessment

After identifying gaps, assess existing test suite health:
1. **Flaky tests**: tests that fail non-deterministically — grep for `sleep`, `setTimeout`, time-dependent assertions, shared mutable state between tests
2. **Brittle tests**: tests that break on implementation change but behavior is preserved — tests asserting on internal implementation details rather than behavior
3. **Test independence**: verify no test depends on execution order or shared state — look for global setup, shared database state, test coupling
4. **Flag**: report fragile tests in test-report.toml `[[fragility]]` entries with type (flaky/brittle) and description

## Write New Tests

For high and medium severity gaps:
- Write new tests that cover the gap
- Place tests in the appropriate test file following project conventions
- Run the new tests to verify they pass

For low severity gaps:
- Document but do not write tests

## Output

For each gap:
- `id`: G1, G2, ... (sequential)
- `description`: what is not covered
- `severity`: high | medium | low (from HRBT risk classification)
- `risk_level`: high | medium | low (HRBT source)
- `test_layer`: unit | integration | property | adversarial (which layer is missing)
- `new_test_written`: true if a test was written for this gap
- `test_file`: path to the new test file (if written)
