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

## Severity Classification

- **High**: untested error handling, security-related code, data validation, authentication/authorization
- **Medium**: untested business logic, new API endpoints, state transitions
- **Low**: untested display/formatting code, logging, comments-only changes

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
- `severity`: high | medium | low
- `new_test_written`: true if a test was written for this gap
- `test_file`: path to the new test file (if written)
